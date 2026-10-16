"""
Auditoria A9 - B9.4: que compra la calibracion de muestra finita (theta primario de B9.2).

1. Muestra de 20000 replicas a n = 20000 (familia 104; las mismas para los dos
   casos) y KS de dos muestras frente a las 20000 trayectorias independientes de
   cada n in {60, 100, 200, 500, 1000, 2000, 5000} (B9.2), con umbral
   1.358 sqrt(2 / 20000).
2. Coste de aproximar: tamano en cada n (trayectorias independientes) con el
   cuantil 5% de la muestra de n = 20000 frente al de la calibracion en n (nula
   hac de produccion). Simetrico para DF-GLS (MAIC) y MSB-GLS: valores criticos
   asintoticos publicados (ERS 1996; Ng-Perron 2001) frente a los simulados en n.
3. E[stat^2] por n con sigma = 1 (stat * sigma_hat) y con sigma_hat HAC.

Uso:
  python experiments/audit9_b94_finite_sample.py --run --cores 14
  python experiments/audit9_b94_finite_sample.py --analyze
"""
import argparse
import math
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed
from scipy.stats import ks_2samp

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B9.4"]
CKPT = os.path.join(C.CKPT_ROOT, "audit9_b94")
OUT = os.path.join(C.RESULTS, "b94_finite_sample_audit9.json")
KS_N = (60, 100, 200, 500, 1000, 2000, 5000)
KS_C = 1.358
BIG_COLS = ("s2",) + tuple("%s|%s" % (case, E.tname(t)) for case in E.CASES for t in E.THETAS)


def big_row(i):
    y = D.big_path(i)
    n = D.N_BIG_N
    s2 = hac_sigma_sq(y)
    return [float(s2)] + [float(E.rmgls(y, n, t, s2, case)) for case in E.CASES for t in E.THETAS]


def batch_fn(cores):
    def _rows(idx):
        return [big_row(i) for i in idx]

    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def run(a):
    resume = "python experiments/audit9_b94_finite_sample.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        C.run_cell("big_n%d" % D.N_BIG_N, D.N_BIG, batch_fn(a.cores), CKPT, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    return 0


def analyze(a):
    t0 = time.time()
    b92 = C.read_json("b92_theta_audit9.json")
    theta = b92["primary_theta"]
    prim = E.tname(theta)
    big, _ = C.load_rows(CKPT, "big_n%d" % D.N_BIG_N, D.N_BIG)
    JB = {c: i for i, c in enumerate(BIG_COLS)}
    rejectors, _ = B91.rejectors_for(D.N_ALL, E.CASES)
    scols = E.columns(**B92.SIZE_FLAGS)
    J = E.index(scols)
    region = C.exact_region(D.N_INDEP)
    thr = KS_C * math.sqrt(2.0 / D.N_INDEP)
    res = {}
    for case in E.CASES:
        xb = big[:, JB["%s|%s" % (case, prim)]]
        q_big = float(np.quantile(xb, C.ALPHA))
        ks, cost, cost_sym, mom = {}, {}, {}, {}
        for n in D.N_ALL:
            rows, _ = C.load_rows(B92.CKPT, "indep_n%d" % n, D.N_INDEP)
            x = rows[:, J["%s|%s" % (case, prim)]]
            s2 = rows[:, J["s2"]]
            rej = rejectors[(n, case)][0]
            if n in KS_N:
                r = ks_2samp(x, xb)
                ks[str(n)] = {"D": float(r.statistic), "p_value": float(r.pvalue), "threshold": thr,
                              "below_threshold": bool(r.statistic < thr), "N_each": [int(x.size), int(xb.size)]}
            cal_rows, cal_cols = B91.CAL.load(n)
            q_n = float(np.quantile(cal_rows[:, E.index(cal_cols)["%s|%s" % (case, prim)]], C.ALPHA))
            cost[str(n)] = {"cv_n20000": q_big, "cv_at_n": q_n,
                            "size_with_cv_n20000": C.rate_record(x < q_big, region),
                            "size_with_cv_at_n": C.rate_record(rej(rows, scols, prim), region)}
            cost_sym[str(n)] = {p: {"size_published_asymptotic": C.rate_record(E.reject_published(rows, scols, case, p), region),
                                    "size_simulated_at_n": C.rate_record(rej(rows, scols, p), region),
                                    "published_cv": (E.DFGLS_CV5_PUBLISHED if p == "dfgls" else E.MSB_CV5_PUBLISHED)[case],
                                    "simulated_cv": rejectors[(n, case)][1][p]}
                                for p in ("dfgls", "msb")}
            one = x * np.sqrt(s2)
            mom[str(n)] = {"E_stat2_sigma1": float(np.mean(one ** 2)), "se_sigma1": float(np.std(one ** 2, ddof=1) / math.sqrt(one.size)),
                           "E_stat2_hac": float(np.mean(x ** 2)), "se_hac": float(np.std(x ** 2, ddof=1) / math.sqrt(x.size))}
        one_b = xb * np.sqrt(big[:, JB["s2"]])
        mom[str(D.N_BIG_N)] = {"E_stat2_sigma1": float(np.mean(one_b ** 2)),
                               "se_sigma1": float(np.std(one_b ** 2, ddof=1) / math.sqrt(one_b.size)),
                               "E_stat2_hac": float(np.mean(xb ** 2)),
                               "se_hac": float(np.std(xb ** 2, ddof=1) / math.sqrt(xb.size))}
        res[case] = {"cv_n20000": q_big, "ks": ks, "approximation_cost": cost, "approximation_cost_comparators": cost_sym,
                     "moments": mom}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "statistic": prim, "N_big": D.N_BIG, "n_big": D.N_BIG_N, "N_indep": D.N_INDEP,
                      "ks_threshold": thr, "ks_rule": "D < 1.358 sqrt(2/20000)",
                      "published_cv": {"dfgls": E.DFGLS_CV5_PUBLISHED, "msb": E.MSB_CV5_PUBLISHED}},
           "exact_region_20000": region, "cases": res, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for case in E.CASES:
        print(case, {n: (round(v["size_with_cv_n20000"]["rate"], 4), round(v["size_with_cv_at_n"]["rate"], 4))
                     for n, v in res[case]["approximation_cost"].items()})
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    return analyze(a) if a.analyze else run(a)


if __name__ == "__main__":
    sys.exit(main())
