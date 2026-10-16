"""
Auditoria A13 - B13.E(1): tab:calib (B10.3.3) con theta = 0.

Sin simular. El mismo calculo que audit10_b103_finite sobre las mismas filas: las
independientes de B9.2 (N = 20 000 por n, familia 102), las de n = 20 000 de B9.4
(familia 104) y la calibracion de mayor N_cal disponible en cada n (500 000 de
A10 en n <= 1000; 50 000 de A9 en 2000 y 5000). Se calcula para theta = 0 y
theta = 0.02.

Paso 0 (protocol_audit13.md, lectura 3): la salida con theta = 0.02 coincide hoja a
hoja con b103_finite_audit10.json (cases), max |Delta| = 0.

Salida: experiments/results/e_calib_audit13.json.
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

import audit13_common as C                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402
import audit9_b94_finite_sample as B94                             # noqa: E402
import audit10_b103_finite as B103F                                # noqa: E402

OUT = os.path.join(C.RESULTS, "e_calib_audit13.json")


def compute(prim, big, cals, rejectors, region, thr):
    JB = {c: i for i, c in enumerate(B94.BIG_COLS)}
    scols = E.columns(**B92.SIZE_FLAGS)
    J = E.index(scols)
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
    return res


def leaf_diff(a, b, path=""):
    """max |a - b| sobre hojas numericas comunes; cuenta hojas y diferencias de estructura."""
    if isinstance(a, dict) and isinstance(b, dict):
        worst, n, miss = 0.0, 0, 0
        for k in set(a) | set(b):
            if k not in a or k not in b:
                miss += 1
                continue
            w, m, x = leaf_diff(a[k], b[k], path + "." + str(k))
            worst, n, miss = max(worst, w), n + m, miss + x
        return worst, n, miss
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return 0.0, 0, 1
        worst, n, miss = 0.0, 0, 0
        for x, y in zip(a, b):
            w, m, z = leaf_diff(x, y, path)
            worst, n, miss = max(worst, w), n + m, miss + z
        return worst, n, miss
    if isinstance(a, bool) or isinstance(b, bool):
        return (0.0 if a == b else float("inf")), 1, 0
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)), 1, 0
    return (0.0 if a == b else float("inf")), 1, 0


def main():
    t0 = time.time()
    big, _ = C.load_rows(B94.CKPT, "big_n%d" % D9.N_BIG_N, D9.N_BIG)
    region = C.exact_region(D9.N_INDEP)
    thr = B94.KS_C * math.sqrt(2.0 / D9.N_INDEP)
    cals = {n: B103F.best_calibration(n) for n in D9.N_ALL}
    rejectors = {(n, case): E.rejector(cals[n][0], cals[n][1], case) for n in D9.N_ALL for case in E.CASES}
    res = {t: compute(t, big, cals, rejectors, region, thr) for t in (C.PRIM, C.PRIM_V13)}
    ref = C.read_json("b103_finite_audit10.json")
    worst, leaves, miss = leaf_diff(res[C.PRIM_V13], ref["cases"])
    out = {"provenance": C.provenance(__file__, seed_family=None),
           "config": {"theta": C.THETA, "reference_theta": C.THETA_V13, "N_big": D9.N_BIG, "n_big": D9.N_BIG_N,
                      "N_indep": D9.N_INDEP, "ks_threshold": thr, "ks_rule": ref["config"]["ks_rule"],
                      "published_cv": ref["config"]["published_cv"],
                      "calibration_by_n": {str(n): cals[n][2] for n in D9.N_ALL},
                      "reading": "protocol_audit13.md, lecturas 3 y 6"},
           "exact_region_20000": region,
           "paso0": {"v13_vs_b103_finite_max_abs_diff": worst, "leaves_compared": leaves, "structure_mismatches": miss,
                     "passes": worst == 0 and miss == 0},
           "cases_by_theta": res, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("Paso 0", out["paso0"])
    for case in E.CASES:
        print(case, {n: (round(v["cv_at_n"], 4), round(v["size_with_cv_at_n"]["rate"], 4), round(v["size_with_cv_n20000"]["rate"], 4))
                     for n, v in res[C.PRIM][case]["approximation_cost"].items()}, "q20000", round(res[C.PRIM][case]["cv_n20000"], 4))
    return 0 if out["paso0"]["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
