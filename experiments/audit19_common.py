"""
Auditoria A19 - infraestructura comun (protocol_audit19.md).

Reutiliza la de A18 (audit18_common) sin modificarla. Cambian el manifiesto (manifest_audit19.json), la lista de codigo de la
procedencia (anade audit19_*.py y make_figures_audit19.py) y la entrada (paper_latex_v25.zip).
"""
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit18_common as C18                                       # noqa: E402

REPO = C18.REPO
RESULTS = C18.RESULTS
FIGURES = os.path.join(HERE, "figures")
MANIFEST = os.path.join(RESULTS, "manifest_audit19.json")
PROTOCOL = "experiments/protocol_audit19.md"
ZIP_V25 = os.path.join(C18.C17.C16.DESKTOP, "paper_latex_v25.zip")
ZIP_V25_SHA256 = "7e5273a76bc2fa163290fcb588d6354a3f2deed738cbbfdf4c98e10a6d913728"
ALPHA = C18.C17.ALPHA

sha256_file = C18.sha256_file
git = C18.git
plain = C18.plain
rel = C18.rel
versions = C18.versions
read_json = C18.read_json
atomic_write_json = C18.atomic_write_json
utc_now = C18.utc_now
assistant = C18.assistant
Manuscript = C18.Manuscript
strip_pdf_dates = C18.strip_pdf_dates
check_pdf_dates = C18.check_pdf_dates


def v25():
    m = Manuscript(ZIP_V25)
    if m.sha256 != ZIP_V25_SHA256:
        raise SystemExit("paper_latex_v25.zip no es el registrado en el protocolo (E0): %s" % m.sha256)
    return m


def code_files():
    files = C18.code_files() + glob.glob(os.path.join(HERE, "audit19_*.py")) + [os.path.join(HERE, "make_figures_audit19.py")]
    return sorted(set(os.path.abspath(f) for f in files if os.path.exists(f)))


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
           "protocol": PROTOCOL, "assistant": assistant()}
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
