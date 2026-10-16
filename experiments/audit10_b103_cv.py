"""
Auditoria A10 - B10.3.6 (condicional): B9.7 con el theta final.

Solo si el theta de B10.1 != 0.1. La tabla de valores criticos de B9.7 (familia
107, N_cal = 100 000, los cinco theta, seis n, cuatro alpha, dos casos) se
reemite desde sus checkpoints marcando el theta final (misma semilla del EE
bootstrap que B9.7, de modo que la tabla coincide con la de A9). Auditoria de
semilla cruzada restringida a las 12 celdas (caso, n) del theta final: las 6 de
mayor EE (maximo sobre alpha); calibracion independiente de A9 (cvx de la
familia 107) si existe para ese (caso, n); si no, nueva en la familia 113
(celda cvx_<caso>_n<n>, N_cal = 100 000).

Salidas: b103_cv_audit10.json y critical_values_audit10.csv.
"""
import argparse
import csv
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_design as D                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b97_critical_values as B97                           # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B10.3"]
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b103_cv")
OUT = os.path.join(C.RESULTS, "b103_cv_audit10.json")
OUT_CSV = os.path.join(C.RESULTS, "critical_values_audit10.csv")
K_AUDIT = 6


def final_theta():
    return C.read_json("b101_theta_audit10.json")["primary_theta"]


def a9_rows(tag):
    parts = []
    for i0 in range(0, D9.N_CV, B97.CHUNK):
        p = os.path.join(B97.CKPT, "%s_i%06d.npz" % (tag, i0))
        if not os.path.exists(p):
            return None
        with np.load(p) as z:
            parts.append(z["rows"])
    return np.vstack(parts)


def _new_rows(case, n, idx):
    det = D9.CASE_DET[case]
    out = []
    for i in idx:
        y = D.cvx_path(case, n, i)
        s2 = hac_sigma_sq(y)
        out.append([s2] + [E.rmgls(y, n, t, s2, det) for t in E.THETAS])
    return out


def new_cvx(case, n, cores, t_block, max_seconds, resume):
    tag = "cvx_%s_n%d" % (case, n)
    os.makedirs(CKPT, exist_ok=True)
    parts = []
    for i0 in range(0, D.N_CV, B97.CHUNK):
        p = os.path.join(CKPT, "%s_i%06d.npz" % (tag, i0))
        if os.path.exists(p):
            with np.load(p) as z:
                if bool(z["complete"]):
                    parts.append(z["rows"])
                    continue
        if time.time() - t_block > max_seconds:
            raise C.BudgetExhausted("%s: tope antes de i0=%d.\nREANUDAR CON:\n  %s" % (tag, i0, resume))
        t0 = time.time()
        idx = list(range(i0, min(i0 + B97.CHUNK, D.N_CV)))
        split = [idx[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(_new_rows)(case, n, s) for s in split)
        rows = np.zeros((len(idx), len(B97.COLS)))
        for s, r in zip(split, res):
            rows[np.array(s) - i0] = r
        np.savez(p + ".tmp.npz", rows=rows, complete=True, elapsed=time.time() - t0)
        os.replace(p + ".tmp.npz", p)
        print("    %s i0=%d  %.1f s" % (tag, i0, time.time() - t0), flush=True)
        parts.append(rows)
    return np.vstack(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    t_block = time.time()
    theta = final_theta()
    if theta == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    resume = "python experiments/audit10_b103_cv.py --cores %d" % a.cores
    table, csv_rows = {}, []
    for case in D9.LP_CASES:
        for n in D9.B7_N:
            R = a9_rows("cv_%s_n%d" % (case, n))
            if R is None:
                raise KeyError("checkpoints de B9.7 no disponibles: cv_%s_n%d" % (case, n))
            cell = D9.cell_index(B97.FAM, "cv_%s_n%d" % (case, n))
            for th in E.THETAS:
                col = B97.COLS.index(E.tname(th))
                q, se = B97.quantiles_with_se(R[:, col], C.rep_seedseq(B97.FAM, cell, D9.N_CV + col))
                key = "%s|%g|%d" % (case, th, n)
                table[key] = {"case": case, "theta": th, "n": n, "primary": th == theta,
                              "cv": {"%g" % al: float(v) for al, v in zip(B97.ALPHAS, q)},
                              "se": {"%g" % al: float(v) for al, v in zip(B97.ALPHAS, se)}, "max_se": float(np.max(se))}
                for al, v, s in zip(B97.ALPHAS, q, se):
                    csv_rows.append({"case": case, "theta": th, "primary": th == theta, "n": n, "alpha": al,
                                     "critical_value": float(v), "se": float(s), "N_cal": D9.N_CV, "calibration": "hac",
                                     "anchor": "gls", "tail": "lower", "seed_family": B97.FAM,
                                     "cell": "cv_%s_n%d" % (case, n)})
    a9 = C.read_json("b97_critical_values_audit9.json")["table"]
    max_diff_vs_a9 = max(abs(table[k]["cv"][al] - a9[k]["cv"][al]) for k in table for al in table[k]["cv"])
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        wr.writeheader()
        wr.writerows(csv_rows)
    mine = [k for k in table if table[k]["theta"] == theta]
    chosen = sorted(mine, key=lambda k: -table[k]["max_se"])[:K_AUDIT]
    audit = {"k": K_AUDIT, "of": len(mine), "ranking": "maximo sobre alpha del EE bootstrap del cuantil",
             "cells": chosen, "by_cell": {}}
    try:
        for k in chosen:
            v = table[k]
            tag = "cvx_%s_n%d" % (v["case"], v["n"])
            X = a9_rows(tag)
            src = "audit9_b97 (familia 107)"
            if X is None:
                print("[AUDITORIA] %s nueva (familia 113)" % tag, flush=True)
                E.warm(a.cores)
                X = new_cvx(v["case"], v["n"], a.cores, t_block, a.max_seconds, resume)
                src = "audit10_b103_cv (familia 113)"
            qx = np.quantile(X[:, B97.COLS.index(E.tname(theta))], B97.ALPHAS)
            dev = {"%g" % al: float(x - v["cv"]["%g" % al]) for al, x in zip(B97.ALPHAS, qx)}
            audit["by_cell"][k] = {"source": src, "cv_independent": {"%g" % al: float(x) for al, x in zip(B97.ALPHAS, qx)},
                                   "deviation": dev, "max_abs_deviation": max(abs(x) for x in dev.values()),
                                   "max_abs_deviation_in_se": max(abs(dev[al]) / v["se"][al] for al in dev)}
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    audit["max_abs_deviation"] = max(v["max_abs_deviation"] for v in audit["by_cell"].values())
    audit["max_abs_deviation_in_se"] = max(v["max_abs_deviation_in_se"] for v in audit["by_cell"].values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "primary_theta": theta,
           "config": {"N_cal": D9.N_CV, "thetas": list(E.THETAS), "alphas": list(B97.ALPHAS), "n": list(D9.B7_N),
                      "calibration": "hac", "anchor": "gls", "R": 0.0, "tail": "inferior", "bootstrap_se": B97.BOOT,
                      "source_rows": "checkpoints de B9.7 (familia 107)"},
           "table": table, "max_abs_diff_vs_a9_table": max_diff_vs_a9,
           "csv": C.rel(OUT_CSV), "csv_sha256": C.sha256_file(OUT_CSV), "cross_seed_audit": audit,
           "elapsed_sec": round(time.time() - t_block, 1)}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, [OUT_CSV], out["provenance"])
    print("tabla frente a A9: %.3g; auditoria max |dev| %.5f (%.2f EE)" % (max_diff_vs_a9, audit["max_abs_deviation"],
                                                                           audit["max_abs_deviation_in_se"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
