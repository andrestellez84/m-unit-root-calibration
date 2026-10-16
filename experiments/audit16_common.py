"""
Auditoria A16 (enmienda 6) - infraestructura comun.

Reutiliza la de A15 (audit15_common) sin modificarla. Cambian el manifiesto (manifest_audit16.json),
la carpeta de tabulares (tables_audit16), la familia de semillas (160, control de invariancia de E6.4)
y la lista de codigo de la procedencia, que anade audit16_*.py. Entradas del manuscrito: zips del v16
y del v17 en el escritorio, leidos sin extraerlos al repositorio.
"""
import datetime
import glob
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C15                                       # noqa: E402

REPO = C15.REPO
RESULTS = C15.RESULTS
MANIFEST = os.path.join(RESULTS, "manifest_audit16.json")
TABLES = os.path.join(RESULTS, "tables_audit16")
PROTOCOL = "experiments/protocol_audit15_amend6.md"
ALPHA = C15.ALPHA
PP = C15.PP
FAMILY = {"INVAR": 160}
PRIOR_FAMILIES = tuple(range(90, 160))
DESKTOP = os.path.dirname(REPO)
ZIP_V16 = os.path.join(DESKTOP, "paper_latex_v16.zip")
ZIP_V17 = os.path.join(DESKTOP, "paper_latex_v17.zip")
BOOTUR_SRC = os.path.join(HERE, "external_audit15", "src_bootUR", "bootUR")

sha256_file = C15.sha256_file
git = C15.git
plain = C15.plain
rel = C15.rel
versions = C15.versions
read_json = C15.read_json
atomic_write_json = C15.atomic_write_json
utc_now = C15.utc_now
assistant = C15.assistant
have = C15.have
rep_seedseq = C15.rep_seedseq


def code_files():
    files = C15.code_files() + glob.glob(os.path.join(HERE, "audit16_*.py"))
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


class Manuscript:
    """Archivos .tex/.md de un zip del manuscrito, leidos en memoria (sin extraerlos al repositorio)."""

    def __init__(self, path):
        self.path = path
        self.sha256 = sha256_file(path)
        self.files = {}
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.endswith((".tex", ".md", ".bib")):
                    self.files[n.split("/", 1)[1] if "/" in n else n] = z.read(n).decode("utf-8")
            self.names = [n.split("/", 1)[1] if "/" in n else n for n in z.namelist()]

    def read_bytes(self, name):
        with zipfile.ZipFile(self.path) as z:
            for n in z.namelist():
                if (n.split("/", 1)[1] if "/" in n else n) == name:
                    return z.read(n)
        raise KeyError(name)

    def lines(self, name):
        return self.files[name].splitlines()


def v16():
    return Manuscript(ZIP_V16)


def v17():
    return Manuscript(ZIP_V17)
