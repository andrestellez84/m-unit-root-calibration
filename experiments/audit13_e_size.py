"""
Auditoria A13 - B13.E(1): tab:size con theta = 0.

n in {200, 500, 1000}: tasa agregada de B10.1 (b101_theta_audit10.json,
cells.<caso|n>.rates.gls_t0.pooled, N = 100 000), sin simular.
n in {60, 100, 150}: 50 000 caminos nuevos por (caso, n), familia 141 (celdas
size_<caso>_n<n>, hijos distintos por caso), paseo gaussiano de A8. Fila ligera
por camino: s2 y RM-GLS con theta = 0 y 0.02 en el caso de la celda (rutinas de
audit9_engine). Paso 0: la fila ligera coincide con audit9_engine.row en los 50
primeros caminos de cada celda (max |Delta| = 0). Rechazo RM-like con la
calibracion de A10 (N_cal = 500 000); tamano con el cuantil 5 % de n = 20 000
(B9.4) para la figura. Informativo: la tasa theta = 0 de B10.3.7 (familia 113) y la
diferencia pareada theta = 0 - theta = 0.02 sobre sus caminos.

Modos: --run (celdas, reanudable), --analyze.
Salida: experiments/results/e_size_audit13.json.
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

import audit13_common as C                                         # noqa: E402
import audit13_design as D                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_engine as E                                          # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["TAB"]
CKPT = os.path.join(C.CKPT_ROOT, "audit13_size")
OUT = os.path.join(C.RESULTS, "e_size_audit13.json")
THETAS = (C.THETA, C.THETA_V13)
LARGE_N = (200, 500, 1000)


def light_cols(det):
    return ("s2",) + tuple("%s|%s" % (det, C.tname(t)) for t in THETAS)


def light_row(y, n, det):
    y = np.asarray(y, dtype=np.float64)
    s2 = hac_sigma_sq(y)
    return [s2] + [E.rmgls(y, n, t, s2, det) for t in THETAS]


def batch_fn(case, n, cores):
    det = D.CASE_DET[case]

    def _rows(idx):
        return [light_row(D.size_path(case, n, i), n, det) for i in idx]

    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def paso0(case, n):
    det = D.CASE_DET[case]
    full = E.columns(cases=(det,), adfpp=False)
    J = E.index(full)
    worst = 0.0
    for i in range(D.PASO0):
        y = D.size_path(case, n, i)
        ref = E.row(y, n, cases=(det,), adfpp=False)
        mine = light_row(y, n, det)
        worst = max(worst, max(abs(a - ref[J[c]]) for a, c in zip(mine, light_cols(det))))
    return worst


def run(a):
    resume = "python experiments/audit13_e_size.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for case in D.CASES:
            for n in D.LOW_N:
                tag = "size_%s_n%d" % (case, n)
                print("\n[CELDA] %s" % tag, flush=True)
                C.run_cell(tag, D.N_LOW, batch_fn(case, n, a.cores), CKPT, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def analyze(a):
    t0 = time.time()
    import audit10_b101_theta as B101
    qbig = B101.big_quantiles()
    b101 = C.read_json("b101_theta_audit10.json")
    low = C.read_json("b103_lown_audit10.json")
    region_low = C.exact_region(D.N_LOW)
    cells, p0, cal = {}, {}, {}
    for n in D.LOW_N:
        rows, cols, info = E10.load_cal(n)
        cal[str(n)] = dict(info, N_cal=int(rows.shape[0]), source="audit10_cal/cal_n%d.npz" % n)
        for case in D.CASES:
            det = D.CASE_DET[case]
            rej, _ = E.rejector(rows, cols, det)
            tag = "size_%s_n%d" % (case, n)
            srows, _ = C.load_rows(CKPT, tag, D.N_LOW)
            scols = light_cols(det)
            J = E.index(scols)
            p0[tag] = paso0(case, n)
            r = {t: rej(srows, scols, t) for t in (C.PRIM, C.PRIM_V13)}
            lk = "%s|%d" % (case, n)
            cells[lk] = {"case": case, "n": n, "source": "familia 141, celda %s" % tag, "N": int(srows.shape[0]),
                         "rates": {t: C.rate_record(v, region_low) for t, v in r.items()},
                         "size_with_cv_n20000": {t: dict(C.rate_record(srows[:, J["%s|%s" % (det, t)]] < qbig[(det, t)],
                                                                         region_low), cv_n20000=qbig[(det, t)])
                                                 for t in (C.PRIM, C.PRIM_V13)},
                         "paired_theta0_minus_v13": C.paired_diff(r[C.PRIM], r[C.PRIM_V13]),
                         "a10_lown": {"theta0": low["cells"][lk]["rates"][C.PRIM],
                                      "v13": low["cells"][lk]["rates"][C.PRIM_V13],
                                      "source": "b103_lown_audit10.json cells.%s.rates" % lk}}
        del rows
    for n in LARGE_N:
        for case in D.CASES:
            lk = "%s|%d" % (case, n)
            c = b101["cells"][lk]
            cells[lk] = {"case": case, "n": n, "source": "b101_theta_audit10.json cells.%s.rates.<theta>.pooled" % lk,
                         "N": c["rates"][C.PRIM]["pooled"]["n"],
                         "rates": {t: c["rates"][t]["pooled"] for t in (C.PRIM, C.PRIM_V13)},
                         "size_with_cv_n20000": {t: c["size_with_cv_n20000"][t] for t in (C.PRIM, C.PRIM_V13)}}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": C.THETA, "reference_theta": C.THETA_V13, "low_n": list(D.LOW_N), "N_low": D.N_LOW,
                      "large_n": list(LARGE_N), "rule": "RM-like: p = F_null(stat) < 0.05, calibracion de A10 (N_cal = 500 000)",
                      "reading": "protocol_audit13.md, lectura 4"},
           "exact_region_50000": region_low, "exact_region_100000": C.exact_region(2 * D.N_LOW),
           "calibration": cal, "paso0": {"by_cell": p0, "reps": D.PASO0, "max_abs_diff": max(p0.values())},
           "cells": cells, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for k, v in cells.items():
        print(k, {t: round(x["rate"], 4) for t, x in v["rates"].items()})
    print("Paso 0", out["paso0"]["max_abs_diff"])
    return 0 if out["paso0"]["max_abs_diff"] == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=4 * 3600)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    rc = run(a) if a.run else 0
    if rc == 0 and a.analyze:
        rc = analyze(a)
    return rc


if __name__ == "__main__":
    sys.exit(main())
