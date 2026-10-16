"""
Auditoria A7 - control del bootstrap sin semilla de A6.

El worker con el que A6 produjo las celdas de DGP 3 a n=200 (commit 62c0772,
checkpoint bootur_dgp3_n200_r4.00.json) no fijaba la semilla de R y no guardaba
los p-valores por serie. Pregunta: la tasa publicada de la celda n=200, r=4.0 es
una estimacion valida aunque no sea reproducible serie a serie?

Replica de su configuracion con el worker con semilla:
  trayectorias  generador de A6 (audit6_wild_bootstrap_sweep.generate_dgp3_series),
                seed_base 300000 + n*100 + int(r*10), i = 0..N-1. Se vuelve a
                comprobar la identidad con power_comparison.py sobre 50 series.
  contraste     bootUR::boot_adf, AWB, deterministics = "intercept", detrend = "QD",
                min_lag = max_lag = 0, con el B que A6 registro para la celda
  rechazo       p < 0.05 estricto, como el worker de A6
  semillas de R (familia 93)*10^8 + i, via audit7_bootstrap_worker.R

Criterio registrado en este archivo ANTES de correr
---------------------------------------------------
  DENTRO del error Monte Carlo  <=>  la tasa con semilla cae en el IC de
  Clopper-Pearson al 95% que A6 publico para la celda (leido de su JSON).
  Se reporta tambien la cota de dos muestras |d| <= z_0.975 sqrt(2 pbar(1-pbar)/N),
  conservadora porque las trayectorias son comunes y las dos tasas estan
  positivamente correlacionadas.
  FUERA -> exit 3: se detiene todo y se reporta.

Ademas, el primer lote se recalcula al final fuera del checkpoint: sus p-valores
deben ser identicos (determinismo del worker con semilla sobre B = 1999).

Uso: python experiments/audit7_seed_control_a6.py --cores 14 --max-seconds 3600
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.stats import norm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_dgp5_runner as RUN                            # noqa: E402
from audit6_wild_bootstrap_sweep import (generate_dgp3_series,  # noqa: E402
                                         dgp3_seed_base)
from power_comparison import generate_rw_break_variance      # noqa: E402

OUT = os.path.join(C.RESULTS, "bootstrap_seed_control_a6_audit7.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit7_seed_control_a6")
A6_JSON = os.path.join(C.RESULTS, "wild_bootstrap_r_audit6.json")
A6_WORKER_COMMIT = "62c0772"
N, R_BREAK = 200, 4.0
N_SIM = D.SEED_CONTROL_N_SIM
ALPHA = 0.05
PAIRING_CHECK = 50
TAG = "seedctl_dgp3_n%d_r%.1f" % (N, R_BREAK)


def r_seed_base():
    return C.seed_base(D.FAM_SEED_CONTROL, 0)


def make_batch_fn(cores, B, sidecar=True):
    def batch_fn(indices):
        if list(indices) != list(range(indices[0], indices[0] + len(indices))):
            raise ValueError("indices no contiguos")
        i0 = indices[0]
        mat = generate_dgp3_series(N, R_BREAK, len(indices), i0=i0)
        p, timing = RUN.run_bootstrap_matrix(TAG, mat, i0, RUN.r_seed_start(r_seed_base(), i0),
                                             cores, B, tmp_dir=CKPT)
        if sidecar:
            C.atomic_write_json(os.path.join(CKPT, "%s_i%06d_k%05d.timing.json"
                                             % (TAG, i0, len(indices))), timing)
        return [[v] for v in p]
    return batch_fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=3600.0)
    a = ap.parse_args()
    resume = ("python experiments/audit7_seed_control_a6.py --cores %d --max-seconds %.0f"
              % (a.cores, a.max_seconds))

    with open(A6_JSON, encoding="utf-8") as f:
        a6 = json.load(f)["dgp3"][str(N)]["%.1f" % R_BREAK]
    ref = a6["adf"]
    B = int(a6["B"])
    if int(a6["N_sim"]) != N_SIM:
        raise SystemExit("A6 tiene N_sim=%s, el control espera %d" % (a6["N_sim"], N_SIM))

    sb = dgp3_seed_base(N, R_BREAK)
    worst = 0.0
    mat = generate_dgp3_series(N, R_BREAK, PAIRING_CHECK)
    for i in range(PAIRING_CHECK):
        y = generate_rw_break_variance(n=N, ratio=R_BREAK, rng=np.random.default_rng(sb + i))
        worst = max(worst, float(np.max(np.abs(mat[:, i] - y))))
    print("=" * 78)
    print("  A7 - control del bootstrap sin semilla de A6: dgp3 n=%d r=%.1f B=%d N=%d cores=%d"
          % (N, R_BREAK, B, N_SIM, a.cores))
    print("  A6: %d/%d = %.4f  IC [%.4f, %.4f]" % (ref["rejections"], N_SIM, ref["rate"],
                                                 ref["ci_lower"], ref["ci_upper"]))
    print("  pareo de trayectorias con power_comparison.py: max|diff| = %.3e sobre %d series"
          % (worst, PAIRING_CHECK))
    print("=" * 78)
    if worst != 0.0:
        raise SystemExit(3)

    t0 = time.time()
    try:
        rows, info = C.run_cell_batched(TAG, N_SIM, make_batch_fn(a.cores, B), CKPT, a.cores,
                                        t0, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc)
        return 2
    p = np.array([r[0] for r in rows], dtype=float)
    n_nan = int(np.isnan(p).sum())
    k = int((np.nan_to_num(p, nan=1.0) < ALPHA).sum())
    rate = k / N_SIM
    lo, hi = C.clopper_pearson(k, N_SIM)
    inside = bool(ref["ci_lower"] <= rate <= ref["ci_upper"])
    pbar = (k + int(ref["rejections"])) / (2.0 * N_SIM)
    z = float(norm.ppf(0.975))
    bound = z * math.sqrt(2.0 * pbar * (1.0 - pbar) / N_SIM)
    diff = rate - float(ref["rate"])

    probe_k = C.PROBE_SERIES
    again = np.array([r[0] for r in make_batch_fn(a.cores, B, sidecar=False)(list(range(probe_k)))])
    rerun_identical = bool(np.array_equal(again, p[:probe_k], equal_nan=True))

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="dgp3_rw_variance_break", n_sim=N_SIM,
            seed_formula=("trayectorias: 300000 + n*100 + int(r*10) + i (A6); "
                          "semilla de R de la serie i: (93*10^8 + i) mod M"),
            extra_code_files=[RUN.WORKER_R]),
        "question": "tasa de A6 sin semilla de R frente a la misma celda con semilla",
        "a6_reference": {"source": "wild_bootstrap_r_audit6.json", "worker_commit": A6_WORKER_COMMIT,
                         "n": N, "r": R_BREAK, "B": B, "n_sim": N_SIM, "adf": ref},
        "test_configuration": {"function": "bootUR::boot_adf", "bootstrap": "AWB",
                               "deterministics": "intercept", "detrend": "QD",
                               "min_lag": 0, "max_lag": 0, "B": B, "rejection": "p < 0.05",
                               "cores": a.cores},
        "trajectory_pairing_max_abs_diff": worst,
        "r_seed_base": r_seed_base(), "r_seed_modulus": RUN.R_SEED_MODULUS,
        "seeded": {"rejections": k, "n": N_SIM, "rate": rate, "ci_lower": lo, "ci_upper": hi,
                   "nan_pvalues": n_nan},
        "criterion": {"rule": "tasa con semilla dentro del IC Clopper-Pearson 95% de A6",
                      "inside_a6_ci": inside,
                      "difference_seeded_minus_a6": diff,
                      "two_sample_bound_conservative": bound,
                      "inside_two_sample_bound": bool(abs(diff) <= bound)},
        "determinism_first_batch_rerun_identical": rerun_identical,
        "cell_elapsed_sec": info["elapsed_sec"],
        "verdict": "DENTRO" if inside else "FUERA",
    })
    print("\n  con semilla: %d/%d = %.4f  IC [%.4f, %.4f]  NaN=%d" % (k, N_SIM, rate, lo, hi, n_nan))
    print("  diferencia %.4f  cota de dos muestras %.4f  -> %s" % (diff, bound,
                                                                 "dentro" if abs(diff) <= bound else "fuera"))
    print("  primer lote recalculado identico: %s" % rerun_identical)
    print("  VEREDICTO: %s del IC de A6  -> %s" % ("DENTRO" if inside else "FUERA", OUT))
    return 0 if (inside and rerun_identical) else 3


if __name__ == "__main__":
    sys.exit(main())
