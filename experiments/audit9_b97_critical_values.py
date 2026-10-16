"""
Auditoria A9 - B9.7 (1): valores criticos finales de RM-GLS.

theta in {0, 0.02, 0.05, 0.1, 0.2} (el primario de B9.2 y los cuatro restantes como
sensibilidad), n in {100, 200, 500, 1000, 2000, 5000}, alpha in {0.01, 0.025,
0.05, 0.10}, casos demeaned y con tendencia, calibracion hac (sigma_hat HAC en
cada camino), cola inferior, N_cal = 100000 por (caso, n) (familia 107, celda
cv_<caso>_n<n>, un hijo por replica). EE del cuantil por bootstrap (200
remuestreos). Auditoria de semilla cruzada sobre el 10% de las 60 celdas
(theta, n, caso) de mayor error estandar (maximo sobre alpha), con calibraciones
independientes (cvx_<caso>_n<n>).

Checkpoints en npz por trozo de 20000 replicas.
Salidas: b97_critical_values_audit9.json y critical_values_audit9.csv.
Uso: python experiments/audit9_b97_critical_values.py --cores 14
"""
import argparse
import csv
import math
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B9.7"]
CKPT = os.path.join(C.CKPT_ROOT, "audit9_b97")
OUT = os.path.join(C.RESULTS, "b97_critical_values_audit9.json")
OUT_CSV = os.path.join(C.RESULTS, "critical_values_audit9.csv")
CHUNK = 20000
ALPHAS = (0.01, 0.025, 0.05, 0.10)
BOOT = 200
AUDIT_SHARE = 0.10
COLS = ("s2",) + tuple(E.tname(t) for t in E.THETAS)


def rows_for(case, n, cross, idx):
    det = D.CASE_DET[case]
    out = []
    for i in idx:
        y = D.cv_path(case, n, i, cross)
        s2 = hac_sigma_sq(y)
        out.append([s2] + [E.rmgls(y, n, t, s2, det) for t in E.THETAS])
    return out


def cell_rows(case, n, cross, cores, t_block, max_seconds, resume):
    tag = "%s_%s_n%d" % ("cvx" if cross else "cv", case, n)
    os.makedirs(CKPT, exist_ok=True)
    parts = []
    for i0 in range(0, D.N_CV, CHUNK):
        p = os.path.join(CKPT, "%s_i%06d.npz" % (tag, i0))
        if os.path.exists(p):
            with np.load(p) as z:
                if bool(z["complete"]) and z["rows"].shape == (min(CHUNK, D.N_CV - i0), len(COLS)):
                    parts.append(z["rows"])
                    continue
        if time.time() - t_block > max_seconds:
            raise C.BudgetExhausted("%s: tope antes de i0=%d.\nREANUDAR CON:\n  %s" % (tag, i0, resume))
        t0 = time.time()
        idx = list(range(i0, min(i0 + CHUNK, D.N_CV)))
        split = [idx[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(rows_for)(case, n, cross, s) for s in split)
        rows = np.zeros((len(idx), len(COLS)))
        for s, r in zip(split, res):
            rows[np.array(s) - i0] = r
        tmp = p + ".tmp.npz"
        np.savez(tmp, rows=rows, complete=True, elapsed=time.time() - t0)
        os.replace(tmp, p)
        print("    %s i0=%d  %.1f s" % (tag, i0, time.time() - t0), flush=True)
        parts.append(rows)
    return np.vstack(parts)


def quantiles_with_se(x, ss):
    q = np.quantile(x, ALPHAS)
    rng = np.random.default_rng(ss)
    bs = np.array([np.quantile(x[rng.integers(0, len(x), len(x))], ALPHAS) for _ in range(BOOT)])
    return q, bs.std(axis=0, ddof=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    resume = "python experiments/audit9_b97_critical_values.py --cores %d" % a.cores
    t_block = time.time()
    theta_p = C.read_json("b92_theta_audit9.json")["primary_theta"]
    E.warm(a.cores)
    data = {}
    try:
        for case in D.LP_CASES:
            for n in D.B7_N:
                print("[CELDA] cv_%s_n%d" % (case, n), flush=True)
                data[(case, n)] = cell_rows(case, n, False, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    table, csv_rows = {}, []
    for (case, n), R in data.items():
        cell = D.cell_index(FAM, "cv_%s_n%d" % (case, n))
        for th in E.THETAS:
            col = COLS.index(E.tname(th))
            q, se = quantiles_with_se(R[:, col], C.rep_seedseq(FAM, cell, D.N_CV + col))
            key = "%s|%g|%d" % (case, th, n)
            table[key] = {"case": case, "theta": th, "n": n, "primary": th == theta_p,
                          "cv": {"%g" % al: float(v) for al, v in zip(ALPHAS, q)},
                          "se": {"%g" % al: float(v) for al, v in zip(ALPHAS, se)}, "max_se": float(np.max(se))}
            for al, v, s in zip(ALPHAS, q, se):
                csv_rows.append({"case": case, "theta": th, "primary": th == theta_p, "n": n, "alpha": al,
                                 "critical_value": float(v), "se": float(s), "N_cal": D.N_CV, "calibration": "hac",
                                 "anchor": "gls", "tail": "lower", "seed_family": FAM, "cell": "cv_%s_n%d" % (case, n)})
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        wr.writeheader()
        wr.writerows(csv_rows)
    k_audit = max(1, int(math.ceil(AUDIT_SHARE * len(table))))
    chosen = sorted(table, key=lambda k: -table[k]["max_se"])[:k_audit]
    audit = {"share": AUDIT_SHARE, "ranking": "maximo sobre alpha del EE bootstrap del cuantil", "cells": chosen, "by_cell": {}}
    try:
        xdata = {}
        for k in chosen:
            v = table[k]
            if (v["case"], v["n"]) not in xdata:
                print("[AUDITORIA] cvx_%s_n%d" % (v["case"], v["n"]), flush=True)
                xdata[(v["case"], v["n"])] = cell_rows(v["case"], v["n"], True, a.cores, t_block, a.max_seconds, resume)
            qx = np.quantile(xdata[(v["case"], v["n"])][:, COLS.index(E.tname(v["theta"]))], ALPHAS)
            dev = {"%g" % al: float(x - v["cv"]["%g" % al]) for al, x in zip(ALPHAS, qx)}
            audit["by_cell"][k] = {"cv_independent": {"%g" % al: float(x) for al, x in zip(ALPHAS, qx)}, "deviation": dev,
                                   "max_abs_deviation": max(abs(x) for x in dev.values()),
                                   "max_abs_deviation_in_se": max(abs(dev["%g" % al]) / v["se"]["%g" % al] for al in ALPHAS)}
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    audit["max_abs_deviation"] = max(v["max_abs_deviation"] for v in audit["by_cell"].values())
    audit["max_abs_deviation_in_se"] = max(v["max_abs_deviation_in_se"] for v in audit["by_cell"].values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "primary_theta": theta_p,
           "config": {"N_cal": D.N_CV, "thetas": list(E.THETAS), "alphas": list(ALPHAS), "n": list(D.B7_N),
                      "calibration": "hac", "anchor": "gls", "R": 0.0, "tail": "inferior (rechazo si estadistico < valor critico)",
                      "bootstrap_se": BOOT},
           "table": table, "csv": C.rel(OUT_CSV), "csv_sha256": C.sha256_file(OUT_CSV), "cross_seed_audit": audit,
           "elapsed_sec": round(time.time() - t_block, 1)}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, [OUT_CSV], out["provenance"])
    print("auditoria cruzada max |dev| %.5f (%.2f EE)" % (audit["max_abs_deviation"], audit["max_abs_deviation_in_se"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
