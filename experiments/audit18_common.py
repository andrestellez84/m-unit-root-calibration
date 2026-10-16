"""
Auditoria A18 (enmienda 8) - infraestructura comun.

Reutiliza la de A17 (audit17_common) sin modificarla. Cambian el manifiesto (manifest_audit18.json), la lista de codigo de la
procedencia (anade audit18_*.py) y la entrada (paper_latex_v18b.zip). Anade la limpieza de fechas de los PDF (lectura E8.3).
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit17_common as C17                                       # noqa: E402

REPO = C17.REPO
RESULTS = C17.RESULTS
MANIFEST = os.path.join(RESULTS, "manifest_audit18.json")
PROTOCOL = "experiments/protocol_audit15_amend8.md"
ZIP_V18 = C17.ZIP_V18
ZIP_V18B = os.path.join(C17.C16.DESKTOP, "paper_latex_v18b.zip")
DATE_KEYS = ("CreationDate", "ModDate")
DATE_RE = re.compile(rb"D:\d{8}")
RASTER_DPI = 72

sha256_file = C17.sha256_file
git = C17.git
plain = C17.plain
rel = C17.rel
versions = C17.versions
read_json = C17.read_json
atomic_write_json = C17.atomic_write_json
utc_now = C17.utc_now
assistant = C17.assistant
have = C17.have
Manuscript = C17.Manuscript
v18 = C17.v18


def v18b():
    return Manuscript(ZIP_V18B)


def pdfinfo_exe():
    import audit16_supplement as S16
    return os.path.join(os.path.dirname(S16.PDFLATEX), "pdfinfo.exe")


def code_files():
    files = C17.code_files() + glob.glob(os.path.join(HERE, "audit18_*.py"))
    return sorted(set(os.path.abspath(f) for f in files))


def provenance(script, seed_family=None, **extra):
    tracked = set(git("ls-files").splitlines())
    modified = set(git("diff", "--name-only", "HEAD").splitlines())
    code = {}
    for f in code_files():
        r = rel(f)
        code[r] = {"sha256": sha256_file(f),
                   "git_state": "untracked" if r not in tracked else ("modified" if r in modified else "committed")}
    dirty = [l for l in git("status", "--porcelain", "--untracked-files=no").splitlines() if "__pycache__" not in l]
    rec = {"script": rel(script), "script_sha256": sha256_file(script), "commit": git("rev-parse", "HEAD"),
           "worktree_dirty": bool(dirty), "dirty_files": dirty, "generated_utc": utc_now(),
           "seed_family": seed_family, "versions": versions(), "code": code,
           "code_all_committed": all(v["git_state"] == "committed" for v in code.values()),
           "assistant": assistant()}
    rec.update(extra)
    return rec


def register_outputs(script, outputs, prov=None):
    man = {"entries": {}}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            man = json.load(f)
    prov = prov or provenance(script)
    for out in outputs:
        man["entries"][rel(out)] = {
            "sha256": sha256_file(out), "bytes": os.path.getsize(out),
            "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(out), datetime.timezone.utc).isoformat(),
            "script": prov["script"], "script_sha256": prov["script_sha256"], "commit": prov["commit"],
            "worktree_dirty": prov["worktree_dirty"], "code_all_committed": prov["code_all_committed"],
            "versions": prov["versions"], "assistant": prov.get("assistant"), "registered_utc": utc_now()}
    man["updated_utc"] = utc_now()
    atomic_write_json(MANIFEST, man)


def write_result(path, obj, script):
    obj = plain(obj)
    atomic_write_json(path, obj)
    register_outputs(script, [path], obj.get("provenance"))


def write_text(path, text, script, prov=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)
    register_outputs(script, [path], prov)


def pdfinfo(path):
    r = subprocess.run([pdfinfo_exe(), path], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def pdf_snapshot(path):
    import fitz
    with fitz.open(path) as d:
        return {"meta": {k: v for k, v in (d.metadata or {}).items() if v}, "xmp": d.get_xml_metadata(),
                "contents": [p.read_contents() for p in d], "pixels": [p.get_pixmap(dpi=RASTER_DPI).samples for p in d]}


def strip_pdf_dates(path):
    """E8.3: quita /CreationDate y /ModDate del Info (y el XMP si lo hay); conserva el contenido. Devuelve el registro."""
    import fitz
    before = pdf_snapshot(path)
    sha_before = sha256_file(path)
    d = fitz.open(path)
    kind, val = d.xref_get_key(-1, "Info")
    removed = []
    if kind == "xref":
        x = int(val.split()[0])
        src = d.xref_object(x, compressed=True)
        removed = [k for k in DATE_KEYS if ("/" + k) in src]
        new = re.sub(r"/(?:%s)\s*(?:\([^)]*\)|<[^>]*>|null)" % "|".join(DATE_KEYS), "", src)
        if new != src:
            d.update_object(x, new)
    had_xmp = bool(d.get_xml_metadata())
    if had_xmp:
        d.del_xml_metadata()
    tmp = path + ".tmp.pdf"
    d.save(tmp, garbage=1, deflate=False, no_new_id=True)
    d.close()
    os.replace(tmp, path)
    after = pdf_snapshot(path)
    raw = open(path, "rb").read()
    info = pdfinfo(path)
    return {"sha256_before": sha_before, "sha256_after": sha256_file(path), "removed_keys": removed, "had_xmp": had_xmp,
            "meta_before": before["meta"], "meta_after": after["meta"],
            "content_streams_equal": before["contents"] == after["contents"], "raster_equal": before["pixels"] == after["pixels"],
            "raw_has_date_key": any(k.encode() in raw for k in DATE_KEYS), "raw_has_date_value": DATE_RE.search(raw) is not None,
            "pdfinfo_date_lines": [l for l in info.splitlines() if "Date" in l],
            "ok": before["contents"] == after["contents"] and before["pixels"] == after["pixels"] and not any(k.encode() in raw for k in DATE_KEYS)
            and DATE_RE.search(raw) is None and not [l for l in info.splitlines() if "Date" in l]}


def check_pdf_dates(path):
    raw = open(path, "rb").read()
    info = pdfinfo(path)
    return {"raw_has_date_key": any(k.encode() in raw for k in DATE_KEYS), "raw_has_date_value": DATE_RE.search(raw) is not None,
            "pdfinfo_date_lines": [l for l in info.splitlines() if "Date" in l]}
