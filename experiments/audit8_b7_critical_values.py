"""
Auditoria A8 - B7: valores criticos y verificacion de la teoria para la primaria.

1. Tabla de valores criticos (cola inferior) de RM y RM-GLS (R = 0), demeaned y
   con tendencia (QD), calibracion hac, N_cal = 100000 por (caso, n) (familia 97,
   celda cv_<caso>_n<n>, un hijo por replica), theta in {0.05, 0.10, 0.15, 0.20,
   0.30} x n in {100, 200, 500, 1000, 2000, 5000} x alpha in {0.01, 0.025, 0.05,
   0.10}; error estandar del cuantil por bootstrap sobre la muestra de
   calibracion. CSV legible por maquina. Auditoria de semilla cruzada sobre el
   10% de las celdas (theta, n, caso) de la primaria con mayor error estandar
   relativo, con calibraciones independientes (celda cvx_<caso>_n<n>).
2. Verificacion de la teoria del limite (primaria RM demeaned):
   - E[F_1^theta] en forma cerrada (audit3_phase1_audit3.py) frente a la traza del
     espectro (compute_eigenvalues); Paso 0 frente a los valores de A3 en
     theta = 0.1;
   - E[[g1_std]^2] / E[F_1^theta] con sigma = 1 y con sigma_hat, por n;
   - KS de una muestra entre [g1_std]^2 (sigma = 1) y la CDF de Davies del
     espectro (davies_cdf), por n, frente a 1.358 / sqrt(N).
   Si la primaria es RM-GLS, el punto 2 se sustituye por 2-bis (tamano simulado
   a n = 20000 frente a los n de la rejilla y E[[g1_GLS]^2] por n).

Checkpoints en npz por bloque de 20000 replicas (las 100000 filas por celda no
caben en JSON).
Salidas: b7_critical_values_audit8.json y critical_values_audit8.csv.
Uso: python experiments/audit8_b7_critical_values.py --cores 14 --max-seconds 14400
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

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.kl_eigenvalues import compute_eigenvalues   # noqa: E402
from stationarity_test.davies import davies_cdf                    # noqa: E402

FAM = C.FAMILY["B7"]
CKPT = os.path.join(C.CKPT_ROOT, "audit8_b7")
OUT = os.path.join(C.RESULTS, "b7_critical_values_audit8.json")
OUT_CSV = os.path.join(C.RESULTS, "critical_values_audit8.csv")
N_CAL = 100000
CHUNK = 20000
THETAS = (0.05, 0.10, 0.15, 0.20, 0.30)
ALPHAS = (0.01, 0.025, 0.05, 0.10)
CASES = {"dm": "c", "ct": "ct"}
ANCHORS = ("mean", "gls")
BOOT = 200
AUDIT_SHARE = 0.10
N_KS = 10000
DAVIES_GRID = 400
KS_CONST = 1.358
THEORY_THETA = 0.1
EIG_K = 200
EIG_EPS = 1e-8
COLS = (tuple("%s_t%g" % (a, t) for a in ANCHORS for t in THETAS)
        + ("g1std_sigma1", "g1std_hac", "gls_sigma1"))
N_GLS_BIG = 20000
N_BIG = 20000


def closed_EF1(theta):
    """E[F_1^theta] en forma cerrada (audit3_phase1_audit3.py, linea de E_F1_closed)."""
    return (10 - 40 * theta + 55 * theta ** 2 - 26 * theta ** 3) / (60 * (1 - theta) ** 2)


def rows_for(case, n, cell, idx):
    det = CASES[case]
    out = []
    for i in idx:
        y = D.gauss_rw(n, C.rep_rng(FAM, cell, i))
        s2 = hac_sigma_sq(y)
        r = []
        for an in ANCHORS:
            for th in THETAS:
                t1, t2 = B2.taus(th, n, "theta")
                r.append(path_statistic(y, n, t1, t2, 0.0, s2, B2.C1, B2.C2, deterministics=det, anchor=an, need_g2=False)[0])
        t1, t2 = B2.taus(THEORY_THETA, n, "theta")
        r.append(path_statistic(y, n, t1, t2, 0.0, 1.0, B2.C1, B2.C2, deterministics=det, need_g2=False)[1])
        r.append(path_statistic(y, n, t1, t2, 0.0, s2, B2.C1, B2.C2, deterministics=det, need_g2=False)[1])
        r.append(path_statistic(y, n, t1, t2, 0.0, 1.0, B2.C1, B2.C2, deterministics=det, anchor="gls", need_g2=False)[1])
        out.append(r)
    return out


def cell_rows(tag, case, n, cores, t_block, max_seconds, resume, reps=None):
    cell = D.cell_index(FAM, tag)
    reps = N_CAL if reps is None else reps
    os.makedirs(CKPT, exist_ok=True)
    parts_all = []
    for i0 in range(0, reps, CHUNK):
        p = os.path.join(CKPT, "%s_i%06d.npz" % (tag, i0))
        if os.path.exists(p):
            with np.load(p) as z:
                if bool(z["complete"]) and z["rows"].shape == (min(CHUNK, reps - i0), len(COLS)):
                    parts_all.append(z["rows"])
                    continue
        if time.time() - t_block > max_seconds:
            raise C.BudgetExhausted("%s: tope de bloque alcanzado antes de i0=%d.\nREANUDAR CON:\n  %s" % (tag, i0, resume))
        t0 = time.time()
        idx = list(range(i0, min(i0 + CHUNK, reps)))
        split = [idx[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores)(delayed(rows_for)(case, n, cell, s) for s in split)
        rows = np.zeros((len(idx), len(COLS)))
        for s, r in zip(split, res):
            rows[np.array(s) - i0] = r
        tmp = p + ".tmp.npz"
        np.savez(tmp, rows=rows, complete=True)
        os.replace(tmp, p)
        print("    %s i0=%d  %.1f s" % (tag, i0, time.time() - t0), flush=True)
        parts_all.append(rows)
    return np.vstack(parts_all)


def _davies(v, eig):
    return davies_cdf(v, eig)[0]


def quantiles_with_se(x, seed_ss):
    q = np.quantile(x, ALPHAS)
    rng = np.random.default_rng(seed_ss)
    bs = np.array([np.quantile(x[rng.integers(0, len(x), len(x))], ALPHAS) for _ in range(BOOT)])
    return q, bs.std(axis=0, ddof=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    resume = "python experiments/audit8_b7_critical_values.py --cores %d --max-seconds %.0f" % (a.cores, a.max_seconds)
    t_block = time.time()
    b4 = C.read_json("b4_local_power_audit8.json")
    gls = bool(b4["gls_rule"]["adopt_gls"])
    prim_anchor = "gls" if gls else "mean"
    anchors_report = ("gls", "mean") if gls else ("mean",)
    data = {}
    try:
        for case in CASES:
            for n in D.B7_N:
                tag = "cv_%s_n%d" % (case, n)
                print("[CELDA] %s" % tag, flush=True)
                data[(case, n)] = cell_rows(tag, case, n, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    table, csv_rows = {}, []
    for (case, n), R in data.items():
        for an in anchors_report:
            for th in THETAS:
                col = COLS.index("%s_t%g" % (an, th))
                ss = C.rep_seedseq(FAM, D.cell_index(FAM, "cv_%s_n%d" % (case, n)), N_CAL + col)
                q, se = quantiles_with_se(R[:, col], ss)
                key = "%s|%s|%g|%d" % (case, an, th, n)
                table[key] = {"case": case, "anchor": an, "theta": th, "n": n,
                              "cv": {"%g" % al: float(v) for al, v in zip(ALPHAS, q)},
                              "se": {"%g" % al: float(v) for al, v in zip(ALPHAS, se)},
                              "max_rel_se": float(np.max(se / np.abs(q)))}
                for al, v, s in zip(ALPHAS, q, se):
                    csv_rows.append({"case": case, "anchor": an, "theta": th, "n": n, "alpha": al, "critical_value": float(v),
                                     "se": float(s), "N_cal": N_CAL, "calibration": "hac", "R": 0.0,
                                     "seed_family": FAM, "cell": "cv_%s_n%d" % (case, n)})
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        wr.writeheader()
        wr.writerows(csv_rows)
    # auditoria de semilla cruzada
    prim_keys = [k for k, v in table.items() if v["anchor"] == prim_anchor]
    k_audit = max(1, int(math.ceil(AUDIT_SHARE * len(prim_keys))))
    chosen = sorted(prim_keys, key=lambda k: -table[k]["max_rel_se"])[:k_audit]
    audit = {"share": AUDIT_SHARE, "cells": chosen, "by_cell": {}}
    try:
        xdata = {}
        for k in chosen:
            v = table[k]
            tag = "cvx_%s_n%d" % (v["case"], v["n"])
            if (v["case"], v["n"]) not in xdata:
                print("[AUDITORIA] %s" % tag, flush=True)
                xdata[(v["case"], v["n"])] = cell_rows(tag, v["case"], v["n"], a.cores, t_block, a.max_seconds, resume)
            col = COLS.index("%s_t%g" % (v["anchor"], v["theta"]))
            qx = np.quantile(xdata[(v["case"], v["n"])][:, col], ALPHAS)
            dev = {"%g" % al: float(x - v["cv"]["%g" % al]) for al, x in zip(ALPHAS, qx)}
            audit["by_cell"][k] = {"cv_independent": {"%g" % al: float(x) for al, x in zip(ALPHAS, qx)},
                                   "deviation": dev, "max_abs_deviation": max(abs(x) for x in dev.values()),
                                   "max_abs_deviation_in_se": max(abs(dev["%g" % al]) / v["se"]["%g" % al] for al in ALPHAS)}
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    audit["max_abs_deviation"] = max(v["max_abs_deviation"] for v in audit["by_cell"].values())
    # teoria
    theory = {}
    if not gls:
        a3 = {r["theta"]: r for r in C.read_json("audit3_phase1_audit3.json")["trace_results"]}
        tr = {}
        for th in THETAS:
            eig, tb = compute_eigenvalues(th, component=1, K=EIG_K, eps=EIG_EPS)
            total = float(np.sum(eig) + tb)
            tr["%g" % th] = {"closed_form": closed_EF1(th), "trace": total,
                             "rel_error": abs(total - closed_EF1(th)) / closed_EF1(th)}
        p0 = {"theta": THEORY_THETA, "a3_trace": a3[THEORY_THETA]["total"], "a3_closed": a3[THEORY_THETA]["closed"],
              "trace_now": tr["%g" % THEORY_THETA]["trace"],
              "abs_diff_trace": abs(tr["%g" % THEORY_THETA]["trace"] - a3[THEORY_THETA]["total"]),
              "abs_diff_closed": abs(tr["%g" % THEORY_THETA]["closed_form"] - a3[THEORY_THETA]["closed"])}
        eig, _ = compute_eigenvalues(THEORY_THETA, component=1, K=EIG_K, eps=EIG_EPS)
        ef1 = closed_EF1(THEORY_THETA)
        mom, ks = {}, {}
        pooled = np.concatenate([data[("dm", n)][:N_KS, COLS.index("g1std_sigma1")] ** 2 for n in D.B7_N])
        grid = np.unique(np.concatenate([np.quantile(pooled, np.linspace(0.0, 1.0, DAVIES_GRID)), [pooled.min(), pooled.max()]]))
        F_grid = np.array(Parallel(n_jobs=a.cores)(delayed(_davies)(float(v), eig) for v in grid))
        for n in D.B7_N:
            R = data[("dm", n)]
            g1 = R[:, COLS.index("g1std_sigma1")] ** 2
            gh = R[:, COLS.index("g1std_hac")] ** 2
            mom[str(n)] = {"ratio_sigma1": float(g1.mean() / ef1), "se_sigma1": float(g1.std(ddof=1) / math.sqrt(len(g1)) / ef1),
                           "ratio_hac": float(gh.mean() / ef1), "se_hac": float(gh.std(ddof=1) / math.sqrt(len(gh)) / ef1)}
            x = np.sort(g1[:N_KS])
            F = np.interp(x, grid, F_grid)
            ecdf_hi = np.arange(1, N_KS + 1) / N_KS
            ecdf_lo = np.arange(0, N_KS) / N_KS
            Dks = float(max(np.max(ecdf_hi - F), np.max(F - ecdf_lo)))
            ks[str(n)] = {"N": N_KS, "D": Dks, "threshold": KS_CONST / math.sqrt(N_KS),
                          "below_threshold": bool(Dks <= KS_CONST / math.sqrt(N_KS))}
            print("  teoria n=%d  razon %.4f / %.4f  KS %.4f" % (n, mom[str(n)]["ratio_sigma1"], mom[str(n)]["ratio_hac"], Dks), flush=True)
        theory = {"variant": "RM demeaned", "trace_vs_closed": tr, "paso0_a3": p0, "EF1_theta": ef1,
                  "moment_ratio": mom, "ks_davies": ks, "eig_K": EIG_K,
                  "davies_evaluation": "davies_cdf en %d puntos (cuantiles de la muestra agrupada) e interpolacion lineal; "
                                       "el espectro no depende de n" % len(grid),
                  "davies_grid_max_step": float(np.max(np.diff(F_grid)))}
    else:
        from scipy.stats import ks_2samp
        col = COLS.index("gls_t0.1")
        try:
            big = cell_rows("gls_n%d" % N_BIG, "dm", N_BIG, a.cores, t_block, a.max_seconds, resume,
                            reps=N_GLS_BIG)[:, col]
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
        ks, sizes, mom = {}, {}, {}
        for n in D.B7_N:
            x = data[("dm", n)][:, col]
            k = ks_2samp(x[:N_BIG], big)
            thr = KS_CONST * math.sqrt((N_BIG + N_BIG) / (N_BIG * N_BIG))
            ks[str(n)] = {"D": float(k.statistic), "p_value": float(k.pvalue), "threshold": thr,
                          "below_threshold": bool(k.statistic <= thr), "N_each": N_BIG}
            q = float(np.quantile(x, C.ALPHA))
            sizes[str(n)] = {"cv_at_n": q, "size_at_n20000_with_that_cv": float((big < q).mean())}
            g = data[("dm", n)][:, COLS.index("gls_sigma1")] ** 2
            mom[str(n)] = {"E_g1gls2_sigma1": float(g.mean()), "se": float(g.std(ddof=1) / math.sqrt(len(g))),
                           "E_g1gls2_hac": float((x ** 2).mean())}
        gbig = big ** 2
        theory = {"variant": "2-bis (RM-GLS)", "n_big": N_BIG, "N": N_BIG,
                  "note": "solo se reporta; no se deriva teoria",
                  "ks_two_sample_vs_n20000": ks, "size_at_n20000_with_cv_of_each_n": sizes,
                  "moment_E_g1gls2_by_n": mom,
                  "moment_at_n20000": {"E_stat2_hac": float(gbig.mean()),
                                       "se": float(gbig.std(ddof=1) / math.sqrt(len(gbig)))}}
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "primary_is_gls": gls,
           "config": {"N_cal": N_CAL, "thetas": THETAS, "alphas": ALPHAS, "n": D.B7_N, "calibration": "hac", "R": 0.0,
                      "tail": "inferior (rechazo si estadistico <= valor critico)", "bootstrap_se": BOOT},
           "table": table, "csv": C.rel(OUT_CSV), "csv_sha256": C.sha256_file(OUT_CSV),
           "cross_seed_audit": audit, "theory": theory, "elapsed_sec": round(time.time() - t_block, 1)}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, [OUT_CSV], out["provenance"])
    print("auditoria cruzada max |dev| %.5f" % audit["max_abs_deviation"])
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
