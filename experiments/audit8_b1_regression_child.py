"""
A8 / B1 - proceso hijo de la regresion pre/post.

Se ejecuta con PYTHONPATH apuntando a un paquete stationarity_test concreto (el
del commit anterior a B1, extraido con git archive, o el del arbol actual) y
escribe en --out las filas de la configuracion publicada sobre las 100 series de
la celda "regression" de la familia 91. Solo usa la API anterior a B1 (defaults).

Filas por serie: statistic y p_value de compute_statistic con defaults para
R in {0.25, 0.5, 0.75} (deterministics "c") y R = 0.5 con deterministics "ct";
p-valor de la configuracion de las tablas publicadas (build_null_cdf con
N_cal = 50000, seed = 42) para R in {0.25, 0.5, 0.75}. Ademas, sha256 de la
muestra nula ordenada (R = 0.5, n = 200, N_cal = 50000, seed = 42).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

REGRESSION_N = (200, 500, 1000)
N_SERIES = 100
RHO_ALT = 0.93


def series(i, cell_index, family):
    n = REGRESSION_N[i % len(REGRESSION_N)]
    rng = np.random.default_rng(np.random.SeedSequence(family, spawn_key=(cell_index, i)))
    eps = rng.standard_normal(n)
    Y = np.empty(n + 1)
    Y[0] = 0.0
    rho = 1.0 if i % 2 == 0 else RHO_ALT
    for t in range(n):
        Y[t + 1] = rho * Y[t] + eps[t]
    return Y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--family", type=int, required=True)
    ap.add_argument("--cell", type=int, required=True)
    a = ap.parse_args()
    import stationarity_test
    from stationarity_test.statistic import compute_statistic
    from stationarity_test.empirical_eigenvalues import build_null_cdf, _simulate_null_statistics
    theta = (0.1, 0.1)
    Rs = (0.25, 0.5, 0.75)
    cdfs = {(R, n): build_null_cdf(theta, R, n, N_cal=50000, seed=42, use_cache=False) for R in Rs for n in REGRESSION_N}
    rows = []
    for i in range(N_SERIES):
        Y = series(i, a.cell, a.family)
        n = len(Y) - 1
        r = {"i": i, "n": n}
        for R in Rs:
            res = compute_statistic(Y, theta, R)
            r["stat_R%g" % R] = res["statistic"]
            r["p_default_R%g" % R] = res["p_value"]
            r["p_published_R%g" % R] = float(np.clip(cdfs[(R, n)](res["statistic"]), 0.0, 1.0))
        res = compute_statistic(Y, theta, 0.5, deterministics="ct")
        r["stat_ct_R0.5"] = res["statistic"]
        r["p_default_ct_R0.5"] = res["p_value"]
        rows.append(r)
    null = np.sort(_simulate_null_statistics(theta, 0.5, 200, 50000, 42))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"module_file": os.path.abspath(stationarity_test.__file__), "rows": rows,
                   "null_R0.5_n200_sha256": hashlib.sha256(null.tobytes()).hexdigest()}, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
