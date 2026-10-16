"""
Auditoria A8 - infraestructura comun.

- Semillas: numpy.random.SeedSequence(family, spawn_key=(cell,)) es el hijo de la
  celda (identico a SeedSequence(family).spawn(n)[cell]); la replica i de la celda
  es SeedSequence(family, spawn_key=(cell, i)) (identico a
  cell_ss.spawn(N)[i]). Las semillas de remuestreo de R se derivan de
  SeedSequence(family, spawn_key=(cell, i, R_STREAM)).
- Ejecucion por lotes con checkpoint atomico y tope por bloque: se reutiliza
  audit7_common.run_cell_batched (sonda de 14 series, lotes completos marcados
  complete=true, reanudacion por lote).
- Intervalos: Wilson para tasas; McNemar exacto; test de signo exacto; region
  exacta de aceptacion binomial calculada a partir de N.
- Procedencia: cada script registra en manifest_audit8.json el sha256 del script
  y de los modulos audit8_* y de produccion, commit, versiones y el sha256/mtime
  de cada salida.
"""
import datetime
import hashlib
import importlib.metadata as md
import json
import math
import os
import platform
import subprocess
import sys

import numpy as np
from scipy.stats import binom, binomtest, norm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for _p in (HERE, os.path.join(REPO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit7_common as C7                                        # noqa: E402

RESULTS = os.path.join(HERE, "results")
CKPT_ROOT = os.path.join(RESULTS, "checkpoints")
MANIFEST = os.path.join(RESULTS, "manifest_audit8.json")
LOGS = os.path.join(RESULTS, "logs_audit8")

ALPHA = 0.05
BLOCK_MAX_SECONDS = 4 * 3600          # regla 2 del encargo (el tope de 8 h del autor es mas laxo)
R_STREAM = 1                          # tercer elemento del spawn_key para semillas de R
PACKAGES = ("numpy", "scipy", "numba", "statsmodels", "arch", "pandas", "joblib", "matplotlib", "pytest")

FAMILY = {"B0": 90, "B1": 91, "B2": 92, "B3": 93, "B4": 94, "B5": 95, "B6": 96, "B7": 97, "B8": 98, "AMEND": 99}

BudgetExhausted = C7.BudgetExhausted
atomic_write_json = C7.atomic_write_json
sha256_file = C7._sha256_file
git = C7._git


# ---------------------------------------------------------------------------
# Semillas
# ---------------------------------------------------------------------------
def cell_seedseq(family, cell):
    return np.random.SeedSequence(int(family), spawn_key=(int(cell),))


def rep_seedseq(family, cell, i):
    return np.random.SeedSequence(int(family), spawn_key=(int(cell), int(i)))


def rep_rng(family, cell, i):
    return np.random.default_rng(rep_seedseq(family, cell, i))


def r_seed(family, cell, i):
    """Semilla entera para set.seed de R, derivada del mismo SeedSequence."""
    ss = np.random.SeedSequence(int(family), spawn_key=(int(cell), int(i), R_STREAM))
    return int(ss.generate_state(1, dtype=np.uint32)[0] % (2 ** 31 - 1))


def pcg_state_word(seed_like):
    """Primera palabra del estado inicial de PCG64: identifica el stream efectivo."""
    return int(np.random.PCG64(seed_like).state["state"]["state"])


# ---------------------------------------------------------------------------
# Estadistica
# ---------------------------------------------------------------------------
def wilson(k, n, level=0.95):
    if n == 0:
        return float("nan"), float("nan")
    z = norm.ppf(0.5 + level / 2)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(centre - half), float(centre + half)


def exact_region(n, p=ALPHA, level=0.95):
    """Region central exacta de la tasa observada bajo tasa verdadera p."""
    lo = binom.ppf((1 - level) / 2, n, p) / n
    hi = binom.ppf(1 - (1 - level) / 2, n, p) / n
    return [float(lo), float(hi)]


def rate_record(mask, region=None):
    mask = np.asarray(mask, dtype=bool)
    k, n = int(mask.sum()), int(mask.size)
    lo, hi = wilson(k, n)
    rec = {"rate": k / n, "rejections": k, "n": n, "wilson_lower": lo, "wilson_upper": hi,
           "se": math.sqrt((k / n) * (1 - k / n) / n)}
    if region is not None:
        rec["in_region"] = bool(region[0] <= rec["rate"] <= region[1])
    return rec


def mcnemar_exact(a, b):
    """a, b: rechazos por replica de dos procedimientos sobre las mismas trayectorias."""
    a, b = np.asarray(a, dtype=bool), np.asarray(b, dtype=bool)
    only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
    m = only_a + only_b
    p = 1.0 if m == 0 else float(binomtest(only_a, m, 0.5).pvalue)
    return {"only_first": only_a, "only_second": only_b, "discordant": m, "p_value": p}


def sign_test(b_total, c_total):
    m = b_total + c_total
    return {"b": int(b_total), "c": int(c_total),
            "p_value": 1.0 if m == 0 else float(binomtest(int(b_total), int(m), 0.5).pvalue)}


def diff_independent(r1, r2):
    """Diferencia de proporciones independientes (tasa1 - tasa2) con su error estandar."""
    d = r1["rate"] - r2["rate"]
    se = math.sqrt(r1["se"] ** 2 + r2["se"] ** 2)
    return {"delta": d, "se": se}


def mean_with_se(deltas):
    """Media de diferencias independientes con EE = sqrt(sum se^2)/k."""
    k = len(deltas)
    return {"mean": float(sum(x["delta"] for x in deltas) / k),
            "se": float(math.sqrt(sum(x["se"] ** 2 for x in deltas)) / k), "k": k}


# ---------------------------------------------------------------------------
# Procedencia
# ---------------------------------------------------------------------------
def code_files():
    import glob
    files = glob.glob(os.path.join(HERE, "audit8_*.py")) + glob.glob(os.path.join(HERE, "audit8_*.R")) \
        + glob.glob(os.path.join(HERE, "make_figures_audit8.py")) \
        + glob.glob(os.path.join(REPO, "src", "stationarity_test", "*.py"))
    return sorted(set(os.path.abspath(f) for f in files))


def rel(p):
    return os.path.relpath(os.path.abspath(p), REPO).replace(os.sep, "/")


def versions():
    out = {"python": sys.version.split()[0], "platform": platform.platform()}
    for p in PACKAGES:
        try:
            out[p] = md.version(p)
        except md.PackageNotFoundError:
            out[p] = None
    return out


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
           "worktree_dirty": bool(dirty), "dirty_files": dirty, "generated_utc": C7.utc_now(),
           "seed_family": seed_family, "versions": versions(), "code": code,
           "code_all_committed": all(v["git_state"] == "committed" for v in code.values())}
    rec.update(extra)
    return rec


def plain(o):
    """Convierte tipos de numpy a tipos nativos de JSON (recursivo)."""
    if isinstance(o, dict):
        return {str(k): plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [plain(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return plain(o.tolist())
    return o


def write_result(path, obj, script):
    """Escribe un JSON de resultados y registra la salida en manifest_audit8.json."""
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
            "versions": prov["versions"], "registered_utc": C7.utc_now()}
    man["updated_utc"] = C7.utc_now()
    atomic_write_json(MANIFEST, man)


def read_json(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return json.load(f)


def git_blob_sha256(path, rev="HEAD"):
    """sha256 del contenido commiteado (independiente de la conversion de fin de linea)."""
    data = subprocess.run(["git", "show", "%s:%s" % (rev, path)], cwd=REPO, capture_output=True).stdout
    return hashlib.sha256(data).hexdigest()


def run_cell(tag, n_sim, batch_fn, ckpt_dir, cores, t_block, max_seconds, resume, log=print, k_batch=None):
    return C7.run_cell_batched(tag, n_sim, batch_fn, ckpt_dir, cores, t_block, max_seconds, resume,
                               log=log, k_batch_override=k_batch)
