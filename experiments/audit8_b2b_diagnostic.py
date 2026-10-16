"""
Auditoria A8 - diagnostico de la compuerta B2b (DURA), que no paso.

No cambia la compuerta ni continua la auditoria. Registra:

D1  Tamano gaussiano de RM (R = 0, theta = 0.1, calibracion hac con la nula de
    B2, seed = 42, N_cal = 50000) sobre 20000 paseos aleatorios gaussianos
    independientes de los publicados (familia 92, celdas diag_gauss_n*),
    n in {200, 500, 1000}.
D2  Tamano sobre las trayectorias publicadas de n = 200 con una calibracion hac
    independiente (N_cal = 50000, familia 92, celda diag_cal_n200).
D3  Construccion: el estadistico de los datos y el de los caminos de calibracion
    son la misma funcion (rm_core.path_statistic con sigma_hat HAC) sobre caminos
    de la misma ley; se registra la igualdad de la funcion en los dos lados.
D4  Tasas publicadas de R = 0.5 a n in {60, 100, 150} (small_n_size_audit5.json):
    reproduccion con la nula de N_cal = 10000 y seed = 42 (la que
    compute_statistic deja en la cache de build_null_cdf, cuya clave no incluye
    N_cal) frente a la de N_cal = 50000.
D5  Las trayectorias gaussianas publicadas usan default_rng(0 + i) en todos los
    n: la serie i de n = 200 es el prefijo de la serie i de n = 500 y 1000.

Salida: experiments/results/b2b_diagnostic_audit8.json.
Uso: python experiments/audit8_b2b_diagnostic.py --cores 14
"""
import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf, cdf_from_null_stats  # noqa: E402

OUT = os.path.join(C.RESULTS, "b2b_diagnostic_audit8.json")
FAM = C.FAMILY["B2"]
DIAG_N = (200, 500, 1000)
DIAG_REPS = 20000
SMALL_N = (60, 100, 150)
SMALL_NCAL = (10000, 50000)


def rm_hac_stat(Y, n):
    t1, t2 = B2.taus(0.1, n, "theta")
    return path_statistic(Y, n, t1, t2, 0.0, hac_sigma_sq(Y), B2.C1, B2.C2, need_g2=False)[0]


def _stats(n, cell, idx):
    return [rm_hac_stat(D.gauss_rw(n, C.rep_rng(FAM, cell, i)), n) for i in idx]


def par(fn, cores, reps, *args):
    parts = [list(range(reps))[j::cores] for j in range(cores)]
    out = Parallel(n_jobs=cores)(delayed(fn)(*args, p) for p in parts)
    by = {}
    for p, r in zip(parts, out):
        by.update(zip(p, r))
    return np.array([by[i] for i in range(reps)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    c_hac = B2.NULL_COLS.index(("R0_t0.1", "hac"))
    out = {"D1_independent_paths": {}, "D2_independent_calibration": {}, "D4_small_n_published": {}}
    for n in DIAG_N:
        null = B2.rm_null(n, a.cores)[:, c_hac]
        s = par(_stats, a.cores, DIAG_REPS, n, D.cell_index(FAM, "diag_gauss_n%d" % n))
        rej = np.clip(cdf_from_null_stats(null)(s), 0.0, 1.0) < C.ALPHA
        out["D1_independent_paths"][str(n)] = C.rate_record(rej, C.exact_region(DIAG_REPS))
        print("D1 n=%d" % n, out["D1_independent_paths"][str(n)], flush=True)
    rows200, _ = B2.load_rows("gauss_n200", D.N_SIM)
    null_ind = par(_stats, a.cores, D.N_CAL, 200, D.cell_index(FAM, "diag_cal_n200"))
    rej = np.clip(cdf_from_null_stats(null_ind)(rows200[:, B2.IDX["stat_R0_t0.1"]]), 0.0, 1.0) < C.ALPHA
    null42 = B2.rm_null(200, a.cores)[:, c_hac]
    out["D2_independent_calibration"] = {
        "published_paths_rate_independent_cal": C.rate_record(rej, C.exact_region(D.N_SIM)),
        "q05_seed42": float(np.quantile(null42, C.ALPHA)), "q05_independent": float(np.quantile(null_ind, C.ALPHA)),
        "published_paths_rate_seed42_cal": C.read_json("b2_size_audit8.json")["B2b"]["gaussian_size"]["200"]["hac"]}
    print("D2", out["D2_independent_calibration"], flush=True)
    out["D3_construction"] = {"data_statistic": "rm_core.path_statistic(Y, n, tau, tau, R=0, s2=hac_newey_west(diff Y))",
                              "calibration_statistic": "rm_core.path_statistic sobre caminos cumsum(N(0,1)) con Y_0 = 0 y el mismo s2",
                              "data_paths": "power_comparison.generate_ar1(rho = 1), Y_0 = 0, innovaciones N(0, 1)",
                              "same_function": True}
    small = C.read_json("small_n_size_audit5.json")
    for n in SMALL_N:
        rows, _ = B2.load_rows("gauss_n%d" % n, D.N_SIM)
        stat = rows[:, B2.IDX["stat_R0.5_t0.1"]]
        pub = next(c for c in small if c["n"] == n and c["theta"] == 0.1)["ours_R050"]
        rates = {}
        for ncal in SMALL_NCAL:
            cdf = build_null_cdf((0.1, 0.1), 0.5, n, N_cal=ncal, seed=D.CAL_SEED_PUBLISHED, use_cache=False)
            rates[str(ncal)] = float((np.clip(cdf(stat), 0.0, 1.0) < C.ALPHA).mean())
        out["D4_small_n_published"][str(n)] = {"published": pub, "reproduced_by_N_cal": rates,
                                                "matches": {k: abs(v - pub) < 5e-5 for k, v in rates.items()}}
        print("D4 n=%d" % n, out["D4_small_n_published"][str(n)], flush=True)
    out["D4_code"] = {"file": "experiments/audit5_tarea3.py",
                      "note": "compute_statistic(..., R = 0.5) en simulate_components llama a null_cdf -> build_null_cdf con "
                              "N_cal = 10000 y use_cache = True; la llamada posterior build_null_cdf(N_cal = 50000) usa la "
                              "misma clave de cache (theta, R, n)"}
    g = [D.reused_gauss(n, 7) for n in (200, 500, 1000)]
    out["D5_nested_paths"] = {"series_checked": 7, "n200_is_prefix_of_n500": bool(np.array_equal(g[0], g[1][:201])),
                              "n200_is_prefix_of_n1000": bool(np.array_equal(g[0], g[2][:201]))}
    out["provenance"] = C.provenance(__file__, seed_family=FAM)
    out["elapsed_sec"] = round(time.time() - t0, 1)
    C.write_result(OUT, out, __file__)
    print(out["D5_nested_paths"])
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
