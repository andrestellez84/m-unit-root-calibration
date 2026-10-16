"""
Auditoria A7 - Bloque 3.1: tamano bajo H0 con innovaciones GARCH(1,1).

Paseo aleatorio Y_t = Y_{t-1} + eps_t con eps_t GARCH(1,1):
    h_t = omega + alpha * e_{t-1}^2 + beta * h_{t-1},   e_t = sqrt(h_t) z_t
Las innovaciones se dividen por la raiz de la varianza incondicional
omega / (1 - alpha - beta), de modo que su varianza incondicional es 1. Arranque en
la varianza incondicional y BURN observaciones descartadas. omega = 0.05 en todas.

Configuraciones:
  --set base  alpha = 0.10, beta = 0.85 (persistencia 0.95), z ~ N(0, 1).
              Salida garch_size_audit7.json. Semillas: familia 80, celda = indice de n
              (decision 4: sustituye 800000 + n*100, cuyo bloque de n=1000 empieza en
              900000, la base de la familia de colas pesadas).
  --set ext   tres configuraciones adicionales, semillas de la familia 81 (nueva y
              disjunta), celda = indice_config * 3 + indice de n:
                p099     alpha = 0.05, beta = 0.94 (persistencia 0.99), z ~ N(0, 1)
                p098     alpha = 0.08, beta = 0.90 (persistencia 0.98), z ~ N(0, 1)
                p095_t5  alpha = 0.10, beta = 0.85 (persistencia 0.95), z ~ t(5) / sqrt(5/3)
              Salida garch_size_ext_audit7.json. Antes de escribirla, Paso 0: el
              generador y las columnas refactorizados reproducen las primeras
              PASO0_SERIES filas de cada celda base guardadas en sus checkpoints
              (max |delta| = 0 exigido; si no, no se escribe nada).
  --set ext_large  p099 y p095_t5 en n in {2000, 5000}, semillas de la familia 82
              (nueva y disjunta), celda = indice_config * 2 + indice de n.
              Salida garch_size_ext_large_audit7.json. Paso 0: reproduce las primeras
              PASO0_SERIES filas de las celdas base y de las celdas p099 y p095_t5 de
              --set ext guardadas en sus checkpoints (max |delta| = 0 exigido).

Columnas, como la tabla de robustez vigente (size_robustness_heavy_tails_audit5b.json):
test propuesto con R in {0.25, 0.50, 0.75}, piloto alpha(1) y la nula GAUSSIANA sin
recalibrar (N_cal = 50000, seed 42); ADF (AIC), PP, DF-GLS (trend="c") y KPSS
(regression="c", nlags="auto") sobre el paseo aleatorio.
n in {200, 500, 1000}, N_sim = 5000.

Checkpoint por lote (audit7_common.run_cell_batched).

Uso: python experiments/audit7_garch_size.py --set ext --cores 14 --max-seconds 14400
"""
import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402
from power_comparison import C_1, C_2                            # noqa: E402
from stationarity_test.utils import (rolling_mean, rolling_var,  # noqa: E402
                                     sample_variance_over_k)
from stationarity_test.hac_estimator import hac_newey_west       # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf  # noqa: E402
from statsmodels.tsa.stattools import adfuller, kpss             # noqa: E402
from arch.unitroot import DFGLS, PhillipsPerron                  # noqa: E402

OUT = os.path.join(C.RESULTS, "garch_size_audit7.json")
OUT_EXT = os.path.join(C.RESULTS, "garch_size_ext_audit7.json")
OUT_EXT_LARGE = os.path.join(C.RESULTS, "garch_size_ext_large_audit7.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit7_garch")
CKPT_EXT = os.path.join(C.CKPT_ROOT, "audit7_garch_ext")
CKPT_EXT_LARGE = os.path.join(C.CKPT_ROOT, "audit7_garch_ext_large")
FAM_GARCH = 80
FAM_GARCH_EXT = 81
FAM_GARCH_EXT_LARGE = 82
OMEGA, ALPHA_G, BETA_G = 0.05, 0.10, 0.85
UNC_VAR = OMEGA / (1.0 - ALPHA_G - BETA_G)
T_DF = 5
BURN = 500
N_GRID = (200, 500, 1000)
N_SIM = 5000
N_CAL = 50000
CAL_SEED = 42
THETA = (0.1, 0.1)
R_CONFIGS = {"R025": 0.25, "R050": 0.50, "R075": 0.75}
PILOT = "alpha1"
ALPHA = 0.05
COLUMNS = ["g1_std", "g2_std", "p_adf", "p_pp", "p_dfgls", "p_kpss", "eps_var"]
IDX = {c: i for i, c in enumerate(COLUMNS)}
PASO0_SERIES = 50

CONFIGS = {
    "base": {"alpha": ALPHA_G, "beta": BETA_G, "innovations": "normal"},
    "p099": {"alpha": 0.05, "beta": 0.94, "innovations": "normal"},
    "p098": {"alpha": 0.08, "beta": 0.90, "innovations": "normal"},
    "p095_t5": {"alpha": 0.10, "beta": 0.85, "innovations": "t%d" % T_DF},
}
EXT_KEYS = ("p099", "p098", "p095_t5")
LARGE_KEYS = ("p099", "p095_t5")
N_GRID_LARGE = (2000, 5000)
SETS = {"base": {"keys": ("base",), "n_grid": N_GRID, "ckpt": CKPT},
        "ext": {"keys": EXT_KEYS, "n_grid": N_GRID, "ckpt": CKPT_EXT},
        "ext_large": {"keys": LARGE_KEYS, "n_grid": N_GRID_LARGE, "ckpt": CKPT_EXT_LARGE}}


def seed_base(n):
    return C.seed_base(FAM_GARCH, N_GRID.index(n))


def seed_base_ext(key, n):
    return C.seed_base(FAM_GARCH_EXT, EXT_KEYS.index(key) * len(N_GRID) + N_GRID.index(n))


def seed_base_ext_large(key, n):
    return C.seed_base(FAM_GARCH_EXT_LARGE, LARGE_KEYS.index(key) * len(N_GRID_LARGE) + N_GRID_LARGE.index(n))


def cell_seed_base(key, n):
    if key == "base":
        return seed_base(n)
    return seed_base_ext_large(key, n) if n in N_GRID_LARGE else seed_base_ext(key, n)


def cell_tag(key, n):
    return "garch_n%d" % n if key == "base" else "garch_%s_n%d" % (key, n)


def unconditional_variance(key):
    cfg = CONFIGS[key]
    return OMEGA / (1.0 - cfg["alpha"] - cfg["beta"])


def z_fourth_moment(key):
    # E[z^4]: 3 para N(0,1); para t(nu) estandarizada, 3 (nu - 2) / (nu - 4)
    return 3.0 if CONFIGS[key]["innovations"] == "normal" else 3.0 * (T_DF - 2) / (T_DF - 4)


def garch_innovations(key, n, rng):
    cfg = CONFIGS[key]
    a, b = cfg["alpha"], cfg["beta"]
    unc = unconditional_variance(key)
    if cfg["innovations"] == "normal":
        z = rng.standard_normal(BURN + n)
    else:
        z = rng.standard_t(T_DF, BURN + n) * np.sqrt((T_DF - 2.0) / T_DF)
    e = np.empty(BURN + n)
    h_prev, e2_prev = unc, unc
    for t in range(BURN + n):
        h = OMEGA + a * e2_prev + b * h_prev
        e[t] = np.sqrt(h) * z[t]
        h_prev, e2_prev = h, e[t] ** 2
    return e[BURN:] / np.sqrt(unc)


def generate(key, n, sb, i):
    eps = garch_innovations(key, n, np.random.default_rng(sb + i))
    Y = np.empty(n + 1)
    Y[0] = 0.0
    Y[1:] = np.cumsum(eps)
    return Y, eps


def _p(fn):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return float(fn())
    except Exception:
        return float("nan")


def row(key, n, sb, i):
    Y, eps = generate(key, n, sb, i)
    tau_1 = max(2, min(int(round(THETA[0] * n)), n // 2))
    tau_2 = max(2, min(int(round(THETA[1] * n)), n // 2))
    g1_raw = float(np.sqrt(max(sample_variance_over_k(rolling_mean(Y, tau_1)), 0.0)))
    g2_raw = float(np.sqrt(max(sample_variance_over_k(rolling_var(Y, tau_2)), 0.0)))
    s2 = hac_newey_west(np.diff(Y), andrews_pilot=PILOT)
    s = np.sqrt(s2)
    g1 = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
    g2 = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0
    return [float(g1), float(g2),
            _p(lambda: adfuller(Y, autolag="AIC")[1]),
            _p(lambda: PhillipsPerron(Y).pvalue),
            _p(lambda: DFGLS(Y, trend="c").pvalue),
            _p(lambda: kpss(Y, regression="c", nlags="auto")[1]),
            float(np.var(eps))]


def _rows(key, n, sb, indices):
    return [row(key, n, sb, i) for i in indices]


def make_batch_fn(key, n, sb, cores):
    def batch_fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(key, n, sb, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return batch_fn


def rate(mask):
    mask = np.asarray(mask, dtype=bool)
    k = int(mask.sum())
    lo, hi = C.clopper_pearson(k, mask.size)
    return {"rate": k / mask.size, "rejections": k, "n": int(mask.size), "ci_lower": lo, "ci_upper": hi}


def checkpoint_rows(ckpt, key, n, k):
    """Primeras k filas de una celda guardadas en disco (lotes completos)."""
    tag = cell_tag(key, n)
    chunks = []
    for name in os.listdir(ckpt):
        if name.startswith(tag + "_i") and name.endswith(".json"):
            with open(os.path.join(ckpt, name), encoding="utf-8") as f:
                d = json.load(f)
            if d.get("complete") is True:
                chunks.append(d)
    rows = []
    for c in sorted(chunks, key=lambda c: c["i0"]):
        if c["i0"] != len(rows):
            raise RuntimeError("%s: checkpoints no contiguos en i0=%d" % (tag, c["i0"]))
        rows.extend(c["rows"])
        if len(rows) >= k:
            break
    if len(rows) < k:
        raise RuntimeError("%s: %d filas en checkpoints, se necesitan %d" % (tag, len(rows), k))
    return np.asarray(rows[:k], dtype=float)


def reproduce_cells(targets, cores):
    """targets: [(ckpt, key, n)]. Filas recalculadas frente a las guardadas, max |delta|."""
    worst, by_cell = 0.0, {}
    for ckpt, key, n in targets:
        ref = checkpoint_rows(ckpt, key, n, PASO0_SERIES)
        new = np.asarray(make_batch_fn(key, n, cell_seed_base(key, n), cores)(list(range(PASO0_SERIES))), dtype=float)
        nan_mismatch = int((np.isnan(ref) != np.isnan(new)).sum())
        d = np.where(np.isnan(ref) & np.isnan(new), 0.0, np.abs(ref - new))
        m = float(np.nanmax(d)) if nan_mismatch == 0 else float("inf")
        by_cell[cell_tag(key, n)] = {"checkpoint_dir": os.path.basename(ckpt), "series": PASO0_SERIES,
                                     "max_abs_diff": m, "nan_pattern_mismatches": nan_mismatch}
        worst = max(worst, m)
    return by_cell, worst


def paso0_base_reproduction(cores):
    by_cell, worst = reproduce_cells([(CKPT, "base", n) for n in N_GRID], cores)
    return {"description": "generador y columnas refactorizados (config base) frente a las filas de los checkpoints "
                           "de audit7_garch producidos por la version anterior del script",
            "columns": COLUMNS, "by_n": {str(n): by_cell[cell_tag("base", n)] for n in N_GRID},
            "worst_max_abs_diff": worst, "passed": worst == 0.0}


def paso0_large_reproduction(cores):
    targets = [(CKPT, "base", n) for n in N_GRID] + [(CKPT_EXT, k, n) for k in LARGE_KEYS for n in N_GRID]
    by_cell, worst = reproduce_cells(targets, cores)
    return {"description": "script con --set ext_large frente a las filas de los checkpoints de la configuracion base "
                           "y de las celdas de --set ext de las mismas dos configuraciones",
            "columns": COLUMNS, "by_cell": by_cell, "worst_max_abs_diff": worst, "passed": worst == 0.0}


def null_cdfs(n_grid):
    return {n: {k: build_null_cdf(THETA, v, n, N_cal=N_CAL, seed=CAL_SEED, use_cache=False)
                for k, v in R_CONFIGS.items()} for n in n_grid}


def analyze(key, rows_by_n, cdfs, region):
    cells = {}
    for n in rows_by_n:
        R, info = rows_by_n[n]
        g1, g2 = R[:, IDX["g1_std"]], R[:, IDX["g2_std"]]
        rej = {"ours_%s" % k: np.clip(cdfs[n][k](np.sqrt((1 - v) ** 2 * g1 ** 2 + v ** 2 * g2 ** 2)), 0, 1) < ALPHA
               for k, v in R_CONFIGS.items()}
        nan = {}
        for name in ("adf", "pp", "dfgls", "kpss"):
            col = R[:, IDX["p_" + name]]
            nan[name] = int(np.isnan(col).sum())
            rej[name] = np.nan_to_num(col, nan=1.0) < ALPHA
        rates = {k: rate(v) for k, v in rej.items()}
        cells[str(n)] = {"n": n, "seed_base": cell_seed_base(key, n), "rejection_rates": rates,
                         "in_exact_acceptance_region": {k: bool(region[0] <= v["rate"] <= region[1])
                                                        for k, v in rates.items() if k != "kpss"},
                         "nan_counts": nan,
                         "innovation_variance_mean": float(np.mean(R[:, IDX["eps_var"]])),
                         "cell_elapsed_sec": info["elapsed_sec"]}
    return cells


def garch_record(key):
    cfg = CONFIGS[key]
    return {"omega": OMEGA, "alpha": cfg["alpha"], "beta": cfg["beta"], "persistence": cfg["alpha"] + cfg["beta"],
            "unconditional_variance_before_scaling": unconditional_variance(key), "burn_in": BURN,
            "z": "N(0,1)" if cfg["innovations"] == "normal" else "t(%d) * sqrt((%d-2)/%d)" % (T_DF, T_DF, T_DF),
            "z_fourth_moment": z_fourth_moment(key),
            "fourth_moment_condition_E_z4_alpha2_plus_2alpha_beta_plus_beta2":
                z_fourth_moment(key) * cfg["alpha"] ** 2 + 2 * cfg["alpha"] * cfg["beta"] + cfg["beta"] ** 2}


CONFIG_RECORD = {"theta": list(THETA), "R": R_CONFIGS, "pilot": PILOT,
                 "null_cdf": "gaussiana sin recalibrar", "N_cal": N_CAL, "cal_seed": CAL_SEED,
                 "alpha": ALPHA, "N_sim": N_SIM,
                 "kpss_note": "KPSS contrasta estacionariedad: sobre el paseo aleatorio su tasa es potencia, no tamano"}


def run_config(key, set_name, a, t_block, resume):
    ckpt = SETS[set_name]["ckpt"]
    rows_by_n = {}
    for n in SETS[set_name]["n_grid"]:
        tg, sb = cell_tag(key, n), cell_seed_base(key, n)
        print("\n[CELDA] %s  seed_base=%d" % (tg, sb), flush=True)
        rows, info = C.run_cell_batched(tg, N_SIM, make_batch_fn(key, n, sb, a.cores), ckpt, a.cores,
                                        t_block, a.max_seconds, resume)
        rows_by_n[n] = (np.asarray(rows, dtype=float), info)
        print("  [COMPLETA] %s en %.0f s" % (tg, info["elapsed_sec"]), flush=True)
    return rows_by_n


def print_cells(label, cells):
    for n, c in cells.items():
        r = c["rejection_rates"]
        print("  %-8s n=%-4s R025=%.4f R050=%.4f R075=%.4f ADF=%.4f PP=%.4f DF-GLS=%.4f KPSS=%.4f  var(eps)=%.3f"
              % (label, n, r["ours_R025"]["rate"], r["ours_R050"]["rate"], r["ours_R075"]["rate"], r["adf"]["rate"],
                 r["pp"]["rate"], r["dfgls"]["rate"], r["kpss"]["rate"], c["innovation_variance_mean"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=tuple(SETS), default="ext")
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.DEFAULT_MAX_SECONDS)
    ap.add_argument("--calibration-probe", type=int, default=0,
                    help="solo mide build_null_cdf con este N_cal en cada n del set y sale")
    a = ap.parse_args()
    resume = "python experiments/audit7_garch_size.py --set %s --cores %d --max-seconds %.0f" % (a.set, a.cores, a.max_seconds)
    keys, n_grid = SETS[a.set]["keys"], SETS[a.set]["n_grid"]
    print("=" * 78)
    print("  A7 / Bloque 3.1 - tamano bajo GARCH(1,1), set %s, configuraciones %s, n=%s, N_sim=%d"
          % (a.set, list(keys), list(n_grid), N_SIM))
    print("=" * 78, flush=True)

    if a.calibration_probe:
        for n in n_grid:
            t0 = time.time()
            build_null_cdf(THETA, R_CONFIGS["R050"], n, N_cal=a.calibration_probe, seed=CAL_SEED, use_cache=False)
            el = time.time() - t0
            print("  sonda de calibracion n=%d N_cal=%d: %.2f s -> %.4f s/serie; %d x %d series: %.0f s"
                  % (n, a.calibration_probe, el, el / a.calibration_probe, len(R_CONFIGS), N_CAL,
                     el / a.calibration_probe * N_CAL * len(R_CONFIGS)), flush=True)
        return 0

    Parallel(n_jobs=a.cores, backend="loky")(delayed(_rows)(k, n, 1, [0]) for k in keys for n in n_grid
                                             for _ in range(a.cores // 3 + 1))

    paso0 = None
    if a.set != "base":
        paso0 = paso0_base_reproduction(a.cores) if a.set == "ext" else paso0_large_reproduction(a.cores)
        print("Paso 0 (script vs checkpoints): peor max|delta| = %r  -> %s"
              % (paso0["worst_max_abs_diff"], "PASA" if paso0["passed"] else "FALLA"), flush=True)
        if not paso0["passed"]:
            print(json.dumps(paso0, indent=1))
            return 3

    t_block = time.time()
    rows = {}
    for key in keys:
        try:
            rows[key] = run_config(key, a.set, a, t_block, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc)
            return 2

    region = C.binomial_acceptance_region(N_SIM)
    t_cal = time.time()
    cdfs = null_cdfs(n_grid)
    cal_sec = time.time() - t_cal
    print("  calibracion de la nula: %.0f s" % cal_sec, flush=True)
    if a.set == "base":
        cells = analyze("base", rows["base"], cdfs, region)
        C.atomic_write_json(OUT, {
            "provenance": C.provenance(dgp="rw_garch11_innovations", n_sim=N_SIM,
                                       seed_formula="80*10^8 + n_idx*10^5 + i"),
            "garch": {k: v for k, v in garch_record("base").items() if not k.startswith(("z_", "fourth"))},
            "config": CONFIG_RECORD,
            "exact_acceptance_region": list(region),
            "cells": cells})
        print_cells("base", cells)
        print(OUT)
        return 0

    configs = {}
    for key in keys:
        configs[key] = {"garch": garch_record(key), "seed_cell_index_offset": keys.index(key) * len(n_grid),
                        "cells": analyze(key, rows[key], cdfs, region)}
        print_cells(key, configs[key]["cells"])
    if a.set == "ext":
        C.atomic_write_json(OUT_EXT, {
            "provenance": C.provenance(dgp="rw_garch11_innovations_ext", n_sim=N_SIM,
                                       seed_formula="81*10^8 + (config_idx*3 + n_idx)*10^5 + i; config_idx: %s" % list(EXT_KEYS)),
            "base_results_file": os.path.basename(OUT),
            "config_order": list(EXT_KEYS),
            "config": CONFIG_RECORD,
            "exact_acceptance_region": list(region),
            "paso0_base_reproduction": paso0,
            "configs": configs})
        print(OUT_EXT)
        return 0
    C.atomic_write_json(OUT_EXT_LARGE, {
        "provenance": C.provenance(dgp="rw_garch11_innovations_ext_large", n_sim=N_SIM,
                                   seed_formula="82*10^8 + (config_idx*2 + n_idx)*10^5 + i; config_idx: %s; n: %s"
                                                % (list(LARGE_KEYS), list(N_GRID_LARGE))),
        "smaller_n_results_file": os.path.basename(OUT_EXT),
        "config_order": list(LARGE_KEYS),
        "n_grid": list(N_GRID_LARGE),
        "config": CONFIG_RECORD,
        "exact_acceptance_region": list(region),
        "calibration_elapsed_sec": round(cal_sec, 1),
        "paso0_reproduction": paso0,
        "configs": configs})
    print(OUT_EXT_LARGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
