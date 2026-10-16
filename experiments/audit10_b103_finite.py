"""
Auditoria A10 - B10.3.3 (condicional): B9.4 completo con el theta final.

Solo si el theta de B10.1 != 0.1. Sin simular: las filas de n = 20 000
(audit9_b94, familia 104) y las trayectorias independientes de cada n (audit9_b92,
familia 102, N = 20 000) contienen los cinco theta.

1. KS de dos muestras frente a n = 20 000 (umbral 1.358 sqrt(2 / 20 000)).
2. Coste de aproximar: tamano en cada n con el cuantil 5% de n = 20 000 frente al
   de la calibracion en n; calibracion de mayor N_cal disponible en cada n
   (500 000 de B10.1 en 200, 500, 1000 y de B10.3.7 en 60, 100, 150; 50 000 de
   A9 en 2000 y 5000). DF-GLS y MSB-GLS: valores publicados frente a simulados.
3. E[stat^2] con sigma = 1 y con sigma_hat HAC.

Salida: experiments/results/b103_finite_audit10.json.
"""
import math
import os
import sys
import time

import numpy as np
from scipy.stats import ks_2samp

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402
import audit9_b94_finite_sample as B94                             # noqa: E402

FAM = C.FAMILY["B10.3"]
OUT = os.path.join(C.RESULTS, "b103_finite_audit10.json")


def final_theta():
    return C.read_json("b101_theta_audit10.json")["primary_theta"]


def best_calibration(n):
    p = os.path.join(E10.CKPT_CAL, "cal_n%d.npz" % n)
    if os.path.exists(p):
        rows, cols, _ = E10.load_cal(n)
        return rows, cols, "audit10_cal (N_cal = %d)" % rows.shape[0]
    rows, cols = B91.CAL.load(n)
    return rows, cols, "audit9_cal (N_cal = %d)" % rows.shape[0]


def main():
    t0 = time.time()
    theta = final_theta()
    if theta == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    prim = E.tname(theta)
    big, _ = C.load_rows(B94.CKPT, "big_n%d" % D9.N_BIG_N, D9.N_BIG)
    JB = {c: i for i, c in enumerate(B94.BIG_COLS)}
    scols = E.columns(**B92.SIZE_FLAGS)
    J = E.index(scols)
    region = C.exact_region(D9.N_INDEP)
    thr = B94.KS_C * math.sqrt(2.0 / D9.N_INDEP)
    cals = {n: best_calibration(n) for n in D9.N_ALL}
    rejectors = {(n, case): E.rejector(cals[n][0], cals[n][1], case) for n in D9.N_ALL for case in E.CASES}
    res = {}
    for case in E.CASES:
        xb = big[:, JB["%s|%s" % (case, prim)]]
        q_big = float(np.quantile(xb, C.ALPHA))
        ks, cost, cost_sym, mom = {}, {}, {}, {}
        for n in D9.N_ALL:
            rows, _ = C.load_rows(B92.CKPT, "indep_n%d" % n, D9.N_INDEP)
            x = rows[:, J["%s|%s" % (case, prim)]]
            s2 = rows[:, J["s2"]]
            rej, qs = rejectors[(n, case)]
            if n in B94.KS_N:
                r = ks_2samp(x, xb)
                ks[str(n)] = {"D": float(r.statistic), "p_value": float(r.pvalue), "threshold": thr,
                              "below_threshold": bool(r.statistic < thr), "N_each": [int(x.size), int(xb.size)]}
            crow, ccols, csrc = cals[n]
            q_n = float(np.quantile(crow[:, E.index(ccols)["%s|%s" % (case, prim)]], C.ALPHA))
            cost[str(n)] = {"cv_n20000": q_big, "cv_at_n": q_n, "calibration": csrc,
                            "size_with_cv_n20000": C.rate_record(x < q_big, region),
                            "size_with_cv_at_n": C.rate_record(rej(rows, scols, prim), region)}
            cost_sym[str(n)] = {p: {"size_published_asymptotic": C.rate_record(E.reject_published(rows, scols, case, p), region),
                                    "size_simulated_at_n": C.rate_record(rej(rows, scols, p), region),
                                    "published_cv": (E.DFGLS_CV5_PUBLISHED if p == "dfgls" else E.MSB_CV5_PUBLISHED)[case],
                                    "simulated_cv": qs[p], "calibration": csrc}
                                for p in ("dfgls", "msb")}
            one = x * np.sqrt(s2)
            mom[str(n)] = {"E_stat2_sigma1": float(np.mean(one ** 2)), "se_sigma1": float(np.std(one ** 2, ddof=1) / math.sqrt(one.size)),
                           "E_stat2_hac": float(np.mean(x ** 2)), "se_hac": float(np.std(x ** 2, ddof=1) / math.sqrt(x.size))}
        one_b = xb * np.sqrt(big[:, JB["s2"]])
        mom[str(D9.N_BIG_N)] = {"E_stat2_sigma1": float(np.mean(one_b ** 2)),
                                "se_sigma1": float(np.std(one_b ** 2, ddof=1) / math.sqrt(one_b.size)),
                                "E_stat2_hac": float(np.mean(xb ** 2)),
                                "se_hac": float(np.std(xb ** 2, ddof=1) / math.sqrt(xb.size))}
        res[case] = {"cv_n20000": q_big, "ks": ks, "approximation_cost": cost, "approximation_cost_comparators": cost_sym,
                     "moments": mom}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "statistic": prim, "N_big": D9.N_BIG, "n_big": D9.N_BIG_N, "N_indep": D9.N_INDEP,
                      "ks_threshold": thr, "ks_rule": "D < 1.358 sqrt(2/20000)",
                      "published_cv": {"dfgls": E.DFGLS_CV5_PUBLISHED, "msb": E.MSB_CV5_PUBLISHED},
                      "calibration_by_n": {str(n): cals[n][2] for n in D9.N_ALL}},
           "exact_region_20000": region, "cases": res, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for case in E.CASES:
        print(case, {n: (round(v["size_with_cv_n20000"]["rate"], 4), round(v["size_with_cv_at_n"]["rate"], 4))
                     for n, v in res[case]["approximation_cost"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
