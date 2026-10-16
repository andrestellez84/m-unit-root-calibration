"""
Auditoria A10 - B10.2: identidad del estadistico con theta = 0.

Notacion del proyecto: Y_0, ..., Y_n; sigma2 = sigma_hat^2_HAC de diff(Y) (rutina
de produccion); u_k = residuo GLS (caso c: Y_k - mu_GLS con a = 1 + cbar/n,
cbar = -7; caso ct: detrend QD con a = 1 + cbar/(n + 1), cbar = -13.5,
t = 1, ..., n + 1). Implementacion independiente de u_k (ecuaciones normales
propias, sin llamar a produccion).

  (i)  RM-GLS(theta = 0) de produccion frente a
       [ (n + 1)^{-1} sum_{k=0}^{n} u_k^2 / (n sigma2) ]^{1/2}.
  (ii) MSB_HAC = [ n^{-2} sum_{k=0}^{n-1} u_k^2 / sigma2 ]^{1/2} (forma de
       Ng-Perron con T = n incrementos) y la relacion exacta
       RM-GLS(0)^2 = n/(n + 1) MSB_HAC^2 + u_n^2 / (n (n + 1) sigma2).
  Informacion: MSB de A8 (audit8_unitroot.np_statistics, a = 1 + cbar/T,
  T = n + 1) con s2_AR sustituido por sigma2.
  (3)  RM-GLS con tau = round(theta n) (acotado a [2, n/2]) frente a tau = 0,
       theta in {0.005, 0.002}, n = 1000.

1000 series por (caso, n), n in {200, 1000}, familia 112 (celdas id_<caso>_n<n>).
Salida: experiments/results/b102_identity_audit10.json.
"""
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_design as D                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B10.2"]
OUT = os.path.join(C.RESULTS, "b102_identity_audit10.json")
THRESHOLD = 1e-12
CBAR = {"c": -7.0, "ct": -13.5}
SMALL_THETAS = (0.005, 0.002)
SMALL_N = 1000


def gls_residual(Y, det):
    """Residuo GLS independiente (ecuaciones normales explicitas)."""
    Y = np.asarray(Y, dtype=np.float64)
    T = Y.size
    n = T - 1
    a = 1.0 + CBAR[det] / (n if det == "c" else T)
    if det == "c":
        Z = np.ones((T, 1))
    else:
        Z = np.column_stack([np.ones(T), np.arange(1.0, T + 1.0)])
    yq = np.concatenate([Y[:1], Y[1:] - a * Y[:-1]])
    zq = np.vstack([Z[:1], Z[1:] - a * Z[:-1]])
    beta = np.linalg.solve(zq.T @ zq, zq.T @ yq)
    return Y - Z @ beta


def relative(a, b):
    return abs(a - b) / abs(b)


def one_cell(case, n):
    det = D.CASE_DET[case]
    r_i, r_ii, r_a8, share_end = [], [], [], []
    small = {str(t): [] for t in SMALL_THETAS}
    taus = {str(t): E.taus(t, n)[0] for t in SMALL_THETAS}
    for i in range(D.N_ID):
        y = D.id_path(case, n, i)
        s2 = hac_sigma_sq(y)
        prod = E.rmgls(y, n, 0.0, s2, det)
        u = gls_residual(y, det)
        rm_ind = math.sqrt(float(u @ u) / (n + 1) / (n * s2))
        msb_hac = math.sqrt(float(u[:-1] @ u[:-1]) / n ** 2 / s2)
        end = u[-1] ** 2 / (n * (n + 1) * s2)
        rel_form = math.sqrt(n / (n + 1) * msb_hac ** 2 + end)
        r_i.append(relative(prod, rm_ind))
        r_ii.append(relative(prod, rel_form))
        share_end.append(end / prod ** 2)
        npr = U.np_statistics(y, det)
        msb_a8_hac = npr["MSB"] * math.sqrt(npr["s2_ar"] / s2)
        r_a8.append(relative(msb_a8_hac, msb_hac))
        if n == SMALL_N:
            for t in SMALL_THETAS:
                small[str(t)].append(relative(E.rmgls(y, n, t, s2, det), prod))

    def summ(x):
        x = np.asarray(x)
        return {"max": float(x.max()), "mean": float(x.mean()), "median": float(np.median(x))}
    out = {"case": case, "n": n, "reps": D.N_ID,
           "i_production_vs_same_convention": summ(r_i),
           "ii_production_vs_exact_relation_with_msb_hac": summ(r_ii),
           "endpoint_term_share_of_rm2": summ(share_end),
           "factor_sqrt_n_over_n_plus_1": math.sqrt(n / (n + 1)),
           "info_msb_a8_with_sigma_hac_vs_msb_hac": summ(r_a8)}
    if n == SMALL_N:
        out["small_theta_vs_theta0"] = {t: dict(summ(v), tau=taus[t]) for t, v in small.items()}
    out["pass"] = bool(max(r_i) <= THRESHOLD and max(r_ii) <= THRESHOLD)
    return out


def main():
    t0 = time.time()
    cells = {"%s|%d" % (case, n): one_cell(case, n) for case in D.CASES for n in D.ID_N}
    worst_i = max(v["i_production_vs_same_convention"]["max"] for v in cells.values())
    worst_ii = max(v["ii_production_vs_exact_relation_with_msb_hac"]["max"] for v in cells.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"n": list(D.ID_N), "reps": D.N_ID, "threshold": THRESHOLD, "cbar": CBAR,
                      "small_thetas": list(SMALL_THETAS), "small_n": SMALL_N,
                      "rule": "protocol_audit10.md, lectura 9"},
           "relation": {
               "same_convention": "RM-GLS(0) = [ (n+1)^{-1} sum_{k=0}^{n} u_k^2 / (n sigma2) ]^{1/2}",
               "exact_relation": "RM-GLS(0)^2 = n/(n+1) MSB_HAC^2 + u_n^2 / (n (n+1) sigma2),  "
                                 "MSB_HAC = [ n^{-2} sum_{k=0}^{n-1} u_k^2 / sigma2 ]^{1/2}"},
           "cells": cells, "worst_i": worst_i, "worst_ii": worst_ii,
           "pass": bool(worst_i <= THRESHOLD and worst_ii <= THRESHOLD),
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for k, v in cells.items():
        print(k, v["pass"], v["i_production_vs_same_convention"]["max"],
              v["ii_production_vs_exact_relation_with_msb_hac"]["max"],
              v["info_msb_a8_with_sigma_hac_vs_msb_hac"], v.get("small_theta_vs_theta0"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
