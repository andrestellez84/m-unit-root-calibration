"""
Auditoria A7 - diagnostico del tamano nominal del bootstrap DF-GLS a n=200.

Hallazgo que se diagnostica: en la calibracion del Bloque 1 (paseo aleatorio
homoscedastico, familia 70, 5000 series, B = 399, worker con semilla) boot_adf
rechaza al 5% nominal 294/5000 = 0.0588, IC que excluye 0.05. En la celda de
control de A6 (dgp3 n=200 r=1.0, 2000 series, B = 999, sin semilla) rechazo
90/2000 = 0.0450. Diferencias: B, trayectorias y semilla del remuestreo.

Diseno (tres patas sobre las MISMAS 2000 trayectorias de A6)
------------------------------------------------------------
  A6            publicado: B de A6, sin semilla (leido de wild_bootstrap_r_audit6.json)
  seeded_B_A6   worker con semilla, el B de A6
  seeded_B399   worker con semilla, B = 399 (el de A7)
Las dos patas con semilla usan las MISMAS semillas de R por serie (familia 94):
numeros aleatorios comunes, contraste pareado de B.
Configuracion del contraste identica a A6 y A7: boot_adf AWB, intercepto, QD,
min_lag = max_lag = 0, rechazo p < 0.05.

Lecturas registradas en este archivo ANTES de correr
----------------------------------------------------
L1 reproduccion de A6: la tasa seeded_B_A6 cae en el IC Clopper-Pearson 95% de A6.
L2 efecto de B: McNemar exacto pareado seeded_B399 vs seeded_B_A6. "B es la causa"
   si p < 0.05 y la tasa con B = 399 es mayor.
L3 efecto de las trayectorias: contraste de dos muestras (z, bilateral) entre la
   calibracion de A7 (familia 70, B = 399) y seeded_B399 (trayectorias de A6,
   B = 399). Mismo procedimiento, trayectorias independientes de la misma ley.
L4 nominal: si cada IC contiene 0.05.
Veredicto:
  "efecto_de_B"      si L2 declara a B causa.
  "no_diagnosticada" en otro caso. Se reportan las tres patas, L2 y L3, y el
                     numero de intervalos nominales examinados en la calibracion
                     (con cuantos excluyen 0.05), para que la lectura de
                     multiplicidad quede declarada. No se atribuye otra causa.

Uso: python experiments/audit7_bootstrap_size_diag.py --cores 14 --max-seconds 3600
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.stats import binomtest, norm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_dgp5_runner as RUN                            # noqa: E402
import audit7_dgp5_analysis as A                            # noqa: E402
from audit6_wild_bootstrap_sweep import (generate_dgp3_series,  # noqa: E402
                                         dgp3_seed_base)
from power_comparison import generate_rw_break_variance      # noqa: E402

OUT = os.path.join(C.RESULTS, "bootstrap_size_diag_n200_audit7.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit7_bootstrap_size_diag")
A6_JSON = os.path.join(C.RESULTS, "wild_bootstrap_r_audit6.json")
N, R_BREAK = 200, 1.0
N_SIM = D.SIZE_DIAG_N_SIM
ALPHA = 0.05
DIAG_ALPHA = 0.05
PAIRING_CHECK = 50
NOMINAL_PROCS = ("p_boot_dfgls", "p_R050_nominal", "p_dfgls", "p_adf", "p_pp")


def tag(B):
    return "sizediag_dgp3_n%d_r%.1f_B%d" % (N, R_BREAK, B)


def r_seed_base():
    return C.seed_base(D.FAM_SIZE_DIAG, 0)


def make_batch_fn(B, cores):
    def batch_fn(indices):
        if list(indices) != list(range(indices[0], indices[0] + len(indices))):
            raise ValueError("indices no contiguos")
        i0 = indices[0]
        mat = generate_dgp3_series(N, R_BREAK, len(indices), i0=i0)
        p, timing = RUN.run_bootstrap_matrix(tag(B), mat, i0, RUN.r_seed_start(r_seed_base(), i0),
                                             cores, B, tmp_dir=CKPT)
        C.atomic_write_json(os.path.join(CKPT, "%s_i%06d_k%05d.timing.json"
                                         % (tag(B), i0, len(indices))), timing)
        return [[v] for v in p]
    return batch_fn


def summary(k, n):
    lo, hi = C.clopper_pearson(k, n)
    return {"rejections": int(k), "n": int(n), "rate": k / n, "ci_lower": lo, "ci_upper": hi,
            "ci_contains_nominal": bool(lo <= ALPHA <= hi)}


def two_sample(k1, n1, k2, n2):
    pp = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (k1 / n1 - k2 / n2) / se if se > 0 else 0.0
    return {"z": z, "p_value": float(2 * norm.sf(abs(z)))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=3600.0)
    a = ap.parse_args()
    resume = ("python experiments/audit7_bootstrap_size_diag.py --cores %d --max-seconds %.0f"
              % (a.cores, a.max_seconds))

    with open(A6_JSON, encoding="utf-8") as f:
        a6 = json.load(f)["dgp3"][str(N)]["%.1f" % R_BREAK]
    if int(a6["N_sim"]) != N_SIM:
        raise SystemExit("A6 tiene N_sim=%s, el diagnostico espera %d" % (a6["N_sim"], N_SIM))
    B_A6, B_A7 = int(a6["B"]), int(D.DGP5_B)

    sb = dgp3_seed_base(N, R_BREAK)
    mat = generate_dgp3_series(N, R_BREAK, PAIRING_CHECK)
    worst = max(float(np.max(np.abs(mat[:, i] - generate_rw_break_variance(
        n=N, ratio=R_BREAK, rng=np.random.default_rng(sb + i))))) for i in range(PAIRING_CHECK))
    print("=" * 78)
    print("  A7 - diagnostico del tamano del bootstrap a n=%d: trayectorias de A6 (dgp3 r=%.1f)" % (N, R_BREAK))
    print("  A6: %d/%d = %.4f  B=%d  | patas con semilla: B=%d y B=%d | pareo max|diff|=%.1e"
          % (a6["adf"]["rejections"], N_SIM, a6["adf"]["rate"], B_A6, B_A6, B_A7, worst))
    print("=" * 78, flush=True)
    if worst != 0.0:
        raise SystemExit(3)

    t0 = time.time()
    p = {}
    for B in (B_A7, B_A6):
        print("\n[PATA] B=%d" % B, flush=True)
        try:
            rows, _ = C.run_cell_batched(tag(B), N_SIM, make_batch_fn(B, a.cores), CKPT, a.cores,
                                         t0, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc)
            return 2
        p[B] = np.array([r[0] for r in rows], dtype=float)

    rej = {B: np.nan_to_num(v, nan=1.0) < ALPHA for B, v in p.items()}
    legs = {"A6_unseeded_B%d" % B_A6: summary(int(a6["adf"]["rejections"]), N_SIM),
            "seeded_B%d" % B_A6: summary(int(rej[B_A6].sum()), N_SIM),
            "seeded_B%d" % B_A7: summary(int(rej[B_A7].sum()), N_SIM)}

    L1 = bool(a6["adf"]["ci_lower"] <= legs["seeded_B%d" % B_A6]["rate"] <= a6["adf"]["ci_upper"])
    only399 = int((rej[B_A7] & ~rej[B_A6]).sum())
    only999 = int((~rej[B_A7] & rej[B_A6]).sum())
    p_mc = float(binomtest(min(only399, only999), only399 + only999, 0.5).pvalue) \
        if only399 + only999 > 0 else 1.0
    L2_cause = bool(p_mc < DIAG_ALPHA and legs["seeded_B%d" % B_A7]["rate"] > legs["seeded_B%d" % B_A6]["rate"])

    cal, why = A.load_rows(RUN.CKPT, D.cal_tag(N), D.N_CAL)
    if cal is None:
        raise SystemExit("calibracion de A7 n=%d ausente: %s" % (N, why))
    k_cal = int((np.nan_to_num(cal[:, RUN.IDX["p_boot_dfgls"]], nan=1.0) < ALPHA).sum())
    legs["A7_calibration_family70_B%d" % B_A7] = summary(k_cal, cal.shape[0])
    L3 = two_sample(k_cal, cal.shape[0], int(rej[B_A7].sum()), N_SIM)

    intervals = {}
    for n in D.CAL_N_ACTIVE:
        rows, _ = A.load_rows(RUN.CKPT, D.cal_tag(n), D.N_CAL)
        for col in NOMINAL_PROCS:
            k = int((np.nan_to_num(rows[:, RUN.IDX[col]], nan=1.0) < ALPHA).sum())
            intervals["n%d_%s" % (n, col)] = summary(k, rows.shape[0])
    excluding = sorted(k for k, v in intervals.items() if not v["ci_contains_nominal"])

    verdict = "efecto_de_B" if L2_cause else "no_diagnosticada"
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="dgp3_rw_homoscedastic_n200", n_sim=N_SIM,
            seed_formula=("trayectorias: 300000 + n*100 + int(r*10) + i (A6); semilla de R de la "
                          "serie i: (94*10^8 + i) mod M, comun a las dos patas"),
            extra_code_files=[RUN.WORKER_R]),
        "finding_diagnosed": "tamano nominal de boot_adf a n=200 en la calibracion de A7 frente a A6",
        "test_configuration": {"function": "bootUR::boot_adf", "bootstrap": "AWB",
                               "deterministics": "intercept", "detrend": "QD",
                               "min_lag": 0, "max_lag": 0, "rejection": "p < 0.05", "cores": a.cores},
        "trajectory_pairing_max_abs_diff": worst,
        "legs": legs,
        "L1_seeded_reproduces_A6_within_ci": L1,
        "L2_B_effect_paired": {"only_B%d" % B_A7: only399, "only_B%d" % B_A6: only999,
                               "mcnemar_p": p_mc, "B_is_cause": L2_cause},
        "L3_trajectory_effect_two_sample_A7cal_vs_A6traj_B%d" % B_A7: L3,
        "calibration_nominal_intervals_examined": {"count": len(intervals),
                                                   "excluding_nominal": excluding,
                                                   "intervals": intervals},
        "verdict": verdict,
        "elapsed_sec": round(time.time() - t0, 1),
    })
    print("\n%-34s %s" % ("pata", "tasa  [IC 95%]"))
    for k, v in legs.items():
        print("%-34s %.4f [%.4f, %.4f]%s" % (k, v["rate"], v["ci_lower"], v["ci_upper"],
                                             "" if v["ci_contains_nominal"] else "  excluye 0.05"))
    print("L1 con semilla reproduce A6: %s" % L1)
    print("L2 B=%d vs B=%d pareado: solo %d / solo %d  McNemar p=%.4f  B causa: %s"
          % (B_A7, B_A6, only399, only999, p_mc, L2_cause))
    print("L3 calibracion A7 vs trayectorias A6 (B=%d): z=%.2f p=%.4f" % (B_A7, L3["z"], L3["p_value"]))
    print("intervalos nominales examinados: %d, excluyen 0.05: %s" % (len(intervals), excluding))
    print("VEREDICTO: %s -> %s" % (verdict, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
