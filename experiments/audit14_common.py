"""
Auditoria A14 - infraestructura comun (protocol_audit14.md, lectura 1).

Reutiliza la de A13 (audit13_common, que envuelve audit10_common) sin modificarla.
Cambian el manifiesto (manifest_audit14.json), la carpeta de logs, la de tabulares,
la familia reservada (150, sin uso) y el conjunto de modulos cuyo sha256 se registra
en la procedencia. Lee paper_latex_v15.zip sin extraerlo.
"""
import datetime
import glob
import io
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C13                                       # noqa: E402
import audit13_q_common as Q13                                     # noqa: E402

REPO = C13.REPO
RESULTS = C13.RESULTS
CKPT_ROOT = C13.CKPT_ROOT
MANIFEST = os.path.join(RESULTS, "manifest_audit14.json")
LOGS = os.path.join(RESULTS, "logs_audit14")
TABLES = os.path.join(RESULTS, "tables_audit14")
TABLES_A13 = C13.TABLES
PAPER_FIGURES = C13.PAPER_FIGURES
MANUSCRIPT_V15 = os.path.join(os.path.dirname(REPO), "paper_latex_v15.zip")
MANUSCRIPT_V14 = Q13.MANUSCRIPT_V14
PREFIX = "v15/"
TEXT_FILES = Q13.TEXT_FILES
PROTOCOL = "experiments/protocol_audit14.md"

ALPHA = C13.ALPHA
PP = C13.PP
PRIM = C13.PRIM
PRIM_V13 = C13.PRIM_V13
FAMILY = {"RESERVED": 150}
PRIOR_FAMILIES = tuple(range(90, 150))

sha256_file = C13.sha256_file
git = C13.git
plain = C13.plain
rel = C13.rel
versions = C13.versions
read_json = C13.read_json
atomic_write_json = C13.C10.atomic_write_json
utc_now = C13.C8.C7.utc_now


def code_files():
    pats = ("audit14_*.py", "audit13_*.py", "audit12_common.py", "audit10_*.py", "audit9_*.py", "audit8_*.py")
    files = [f for p in pats for f in glob.glob(os.path.join(HERE, p))]
    files += glob.glob(os.path.join(REPO, "src", "stationarity_test", "*.py"))
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
           "code_all_committed": all(v["git_state"] == "committed" for v in code.values())}
    rec.update(extra)
    return rec


def register_outputs(script, outputs, prov=None):
    import json
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
            "versions": prov["versions"], "registered_utc": utc_now()}
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


def have(name):
    return os.path.exists(os.path.join(RESULTS, name))


def committed(path):
    """Commit que anadio un archivo del repositorio y sha256 en disco y en HEAD (audit12_b120_inventory.committed)."""
    import audit12_b120_inventory as B120
    return B120.committed(path)


def last_commit(path):
    """Ultimo commit que toco un archivo (None si no esta en git) y su fecha."""
    log = git("log", "-1", "--format=%H %cI", "--", path).strip()
    tracked = bool(git("ls-files", "--", path).strip())
    h, t = (log.split(" ", 1) if log else (None, None))
    return {"path": path, "tracked": tracked, "last_commit": h, "last_commit_time": t}


class V15(Q13.V14):
    """El v15 dentro del zip: archivos de texto (.tex, .md) y binarios por ruta relativa a v15/."""

    def __init__(self, path=MANUSCRIPT_V15, prefix=PREFIX):
        with open(path, "rb") as f:
            self.raw = f.read()
        self.path = path
        self.z = zipfile.ZipFile(io.BytesIO(self.raw))
        self.files = {n[len(prefix):]: self.z.read(n).decode("utf-8") for n in self.z.namelist()
                      if n.endswith((".tex", ".md"))}
        self.binary = {n[len(prefix):]: self.z.read(n) for n in self.z.namelist() if not n.endswith("/")}
