"""
Auditoria A9 - infraestructura comun.

Reutiliza la de A8 (audit8_common) sin modificarla: mismas semillas
SeedSequence(familia, spawn_key=(celda, i)), Wilson, McNemar exacto, region
exacta binomial, ejecucion por lotes con checkpoint atomico y tope de 4 h por
bloque. Cambian el manifiesto (manifest_audit9.json), la carpeta de logs, las
familias (100-107; 108-109 reservadas para enmiendas) y el conjunto de modulos
cuyo sha256 se registra en la procedencia (audit9_*, audit8_* y produccion).
"""
import datetime
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for _p in (HERE, os.path.join(REPO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit8_common as C8                                        # noqa: E402

RESULTS = C8.RESULTS
CKPT_ROOT = C8.CKPT_ROOT
MANIFEST = os.path.join(RESULTS, "manifest_audit9.json")
LOGS = os.path.join(RESULTS, "logs_audit9")

ALPHA = C8.ALPHA
BLOCK_MAX_SECONDS = 4 * 3600
FAMILY = {"B9.0": 100, "B9.1": 101, "B9.2": 102, "B9.3": 103, "B9.4": 104, "B9.5": 105, "B9.6": 106,
          "B9.7": 107, "AMEND1": 108, "AMEND2": 109}
PRIOR_A8_FAMILIES = tuple(range(90, 100))

BudgetExhausted = C8.BudgetExhausted
atomic_write_json = C8.atomic_write_json
sha256_file = C8.sha256_file
git = C8.git
rep_seedseq = C8.rep_seedseq
rep_rng = C8.rep_rng
wilson = C8.wilson
exact_region = C8.exact_region
rate_record = C8.rate_record
mcnemar_exact = C8.mcnemar_exact
diff_independent = C8.diff_independent
mean_with_se = C8.mean_with_se
plain = C8.plain
rel = C8.rel
versions = C8.versions
read_json = C8.read_json
run_cell = C8.run_cell


def paired_diff(a, b):
    """Diferencia pareada de tasas (a - b) sobre las mismas trayectorias, con EE de la media de a_i - b_i."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    d = a - b
    n = d.size
    return {"delta": float(d.mean()), "se": float(d.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan"), "n": n}


def code_files():
    files = (glob.glob(os.path.join(HERE, "audit9_*.py")) + glob.glob(os.path.join(HERE, "audit8_*.py"))
             + glob.glob(os.path.join(HERE, "make_figures_audit9.py"))
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


def load_rows(ckpt_dir, tag, n_sim):
    """Filas completas de una celda a partir de sus lotes (A8: audit8_b2_size.load_rows)."""
    chunks = []
    for p in glob.glob(os.path.join(ckpt_dir, "%s_i*_k*.json" % tag)):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d["tag"] == tag:
            chunks.append(d)
    chunks.sort(key=lambda d: d["i0"])
    rows, pos = [], 0
    for d in chunks:
        if d["i0"] != pos:
            continue
        rows.extend(d["rows"])
        pos += d["k"]
    if len(rows) < n_sim:
        raise KeyError("%s: %d filas, se esperaban %d" % (tag, len(rows), n_sim))
    return np.asarray(rows[:n_sim], dtype=float), sum(d["elapsed_sec"] for d in chunks)


def load_prefix(ckpt_dir, tag, k):
    """Primeras k filas de una celda (Paso 0), sin exigir la celda completa."""
    chunks = []
    for p in glob.glob(os.path.join(ckpt_dir, "%s_i*_k*.json" % tag)):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d["tag"] == tag:
            chunks.append(d)
    chunks.sort(key=lambda d: d["i0"])
    rows, pos = [], 0
    for d in chunks:
        if d["i0"] != pos:
            break
        rows.extend(d["rows"])
        pos += d["k"]
        if len(rows) >= k:
            break
    return np.asarray(rows[:k], dtype=float)
