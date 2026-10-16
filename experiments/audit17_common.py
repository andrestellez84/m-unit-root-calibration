"""
Auditoria A17 (enmienda 7) - infraestructura comun.

Reutiliza la de A16 (audit16_common) sin modificarla. Cambian el manifiesto (manifest_audit17.json), la lista de codigo
de la procedencia (anade audit17_*.py) y la entrada del manuscrito (paper_latex_v18.zip). Sin familias nuevas: E7.1
reutiliza los caminos de E6.4 (familia 160).
"""
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C16                                       # noqa: E402

REPO = C16.REPO
RESULTS = C16.RESULTS
MANIFEST = os.path.join(RESULTS, "manifest_audit17.json")
PROTOCOL = "experiments/protocol_audit15_amend7.md"
ALPHA = C16.ALPHA
PP = C16.PP
ZIP_V18 = os.path.join(C16.DESKTOP, "paper_latex_v18.zip")
ZIP_V17 = C16.ZIP_V17
ZIP_V16 = C16.ZIP_V16
BOOTUR_SRC = C16.BOOTUR_SRC

sha256_file = C16.sha256_file
git = C16.git
plain = C16.plain
rel = C16.rel
versions = C16.versions
read_json = C16.read_json
atomic_write_json = C16.atomic_write_json
utc_now = C16.utc_now
assistant = C16.assistant
have = C16.have
Manuscript = C16.Manuscript
v16 = C16.v16
v17 = C16.v17


def v18():
    return Manuscript(ZIP_V18)


def code_files():
    files = C16.code_files() + glob.glob(os.path.join(HERE, "audit17_*.py"))
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
