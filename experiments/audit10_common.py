"""
Auditoria A10 - infraestructura comun.

Reutiliza la de A9 (audit9_common, que a su vez envuelve audit8_common) sin
modificarla: semillas SeedSequence(familia, spawn_key=(celda, i)) (identico a
SeedSequence(familia).spawn(...)[celda].spawn(...)[i], verificado en B10.0),
Wilson, McNemar exacto, region exacta binomial, ejecucion por lotes con
checkpoint atomico y tope de 4 h por bloque. Cambian el manifiesto
(manifest_audit10.json), la carpeta de logs, las familias (110-115; 116-119
reservadas para enmiendas) y el conjunto de modulos cuyo sha256 se registra en
la procedencia (audit10_*, audit9_*, audit8_* y produccion).
"""
import datetime
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for _p in (HERE, os.path.join(REPO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit9_common as C9                                        # noqa: E402

C8 = C9.C8
RESULTS = C9.RESULTS
CKPT_ROOT = C9.CKPT_ROOT
MANIFEST = os.path.join(RESULTS, "manifest_audit10.json")
LOGS = os.path.join(RESULTS, "logs_audit10")

ALPHA = C9.ALPHA
BLOCK_MAX_SECONDS = 4 * 3600
FAMILY = {"B10.0": 110, "B10.1": 111, "B10.2": 112, "B10.3": 113, "B10.4": 114, "B10.5": 115,
          "AMEND1": 116, "AMEND2": 117, "AMEND3": 118, "AMEND4": 119}
PRIOR_A9_FAMILIES = tuple(range(100, 110))

BudgetExhausted = C9.BudgetExhausted
atomic_write_json = C9.atomic_write_json
sha256_file = C9.sha256_file
git = C9.git
rep_seedseq = C9.rep_seedseq
rep_rng = C9.rep_rng
wilson = C9.wilson
exact_region = C9.exact_region
rate_record = C9.rate_record
mcnemar_exact = C9.mcnemar_exact
diff_independent = C9.diff_independent
mean_with_se = C9.mean_with_se
plain = C9.plain
rel = C9.rel
versions = C9.versions
read_json = C9.read_json
run_cell = C9.run_cell
paired_diff = C9.paired_diff
load_rows = C9.load_rows
load_prefix = C9.load_prefix


def code_files():
    files = (glob.glob(os.path.join(HERE, "audit10_*.py")) + glob.glob(os.path.join(HERE, "audit9_*.py"))
             + glob.glob(os.path.join(HERE, "audit8_*.py"))
             + glob.glob(os.path.join(HERE, "make_figures_audit10.py"))
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


def rate_pooled(parts, region):
    """Tasa agregada de varias muestras independientes (vectores de rechazo) con Wilson y region exacta."""
    x = np.concatenate([np.asarray(p, dtype=bool) for p in parts])
    return rate_record(x, region)
