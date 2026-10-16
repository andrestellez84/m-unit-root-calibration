"""
Auditoria A11 - infraestructura comun.

Reutiliza la de A10 (audit10_common, que envuelve audit9_common y audit8_common)
sin modificarla: semillas SeedSequence(familia, spawn_key=(celda, i)), Wilson,
escritura atomica y checkpoint. Cambian el manifiesto (manifest_audit11.json), la
carpeta de logs, las familias (120-125; 126-129 reservadas para enmiendas) y el
conjunto de modulos cuyo sha256 se registra en la procedencia.
"""
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for _p in (HERE, os.path.join(REPO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit10_common as C10                                      # noqa: E402

C9 = C10.C9
C8 = C10.C8
RESULTS = C10.RESULTS
CKPT_ROOT = C10.CKPT_ROOT
MANIFEST = os.path.join(RESULTS, "manifest_audit11.json")
LOGS = os.path.join(RESULTS, "logs_audit11")
FIGURES = os.path.join(HERE, "figures")
PAPER_FIGURES = os.path.join(REPO, "paper", "figures")

ALPHA = C10.ALPHA
BLOCK_MAX_SECONDS = 4 * 3600
FAMILY = {"T0": 120, "T1": 121, "T2": 122, "T3": 123, "T4": 124, "T5": 125,
          "AMEND1": 126, "AMEND2": 127, "AMEND3": 128, "AMEND4": 129}

BudgetExhausted = C10.BudgetExhausted
atomic_write_json = C10.atomic_write_json
sha256_file = C10.sha256_file
git = C10.git
rep_seedseq = C10.rep_seedseq
rep_rng = C10.rep_rng
wilson = C10.wilson
plain = C10.plain
rel = C10.rel
versions = C10.versions
read_json = C10.read_json


def code_files():
    files = (glob.glob(os.path.join(HERE, "audit11_*.py")) + glob.glob(os.path.join(HERE, "make_figures_audit11.py"))
             + glob.glob(os.path.join(HERE, "make_figures_audit10.py")) + glob.glob(os.path.join(HERE, "make_figures_audit9.py"))
             + glob.glob(os.path.join(HERE, "audit10_common.py")) + glob.glob(os.path.join(HERE, "audit9_common.py"))
             + glob.glob(os.path.join(HERE, "audit9_engine.py")) + glob.glob(os.path.join(HERE, "audit8_common.py"))
             + glob.glob(os.path.join(HERE, "audit8_design.py"))
             + glob.glob(os.path.join(REPO, "src", "stationarity_test", "*.py")))
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
           "worktree_dirty": bool(dirty), "dirty_files": dirty, "generated_utc": C8.C7.utc_now(),
           "seed_family": seed_family, "versions": versions(), "code": code,
           "code_all_committed": all(v["git_state"] == "committed" for v in code.values())}
    rec.update(extra)
    return rec


def write_result(path, obj, script):
    obj = plain(obj)
    atomic_write_json(path, obj)
    register_outputs(script, [path], obj.get("provenance"))


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
            "versions": prov["versions"], "registered_utc": C8.C7.utc_now()}
    man["updated_utc"] = C8.C7.utc_now()
    atomic_write_json(MANIFEST, man)
