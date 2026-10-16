"""
Auditoria A12 - calibraciones nuevas (familia 136) y Paso 0 de las de A10.

1. Columnas Perron-Qu (kpq, s2ar_pq, glsbp_t0, mzt_pq, msb_pq, dfgls_pq, dfgls_pq_p) de
   los dos casos sobre 500 000 paseos gaussianos (Y_0 = 0) por n in {100, 200, 500,
   1000, 2000}, celda cal_n<n> (protocolo_audit12, lectura 8).
2. Paso 0 de la reutilizacion de A10 (N_cal = 500 000, semilla 42, n in {100, 200,
   500, 1000}): las 50 primeras filas recalculadas con audit12_unitroot.np_part frente a
   audit10_cal/cal_n<n>.npz, max |Delta| = 0.

Uso: python experiments/audit12_cal.py --run --cores 14 [--n 100 200 ...]; --paso0
Salida (con --paso0): experiments/results/cal_paso0_audit12.json. Checkpoints en
checkpoints/audit12_cal.
"""
import argparse
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
import audit12_design as D                                         # noqa: E402
import audit12_unitroot as P                                       # noqa: E402
import audit12_runner as R                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402

FAM = C.FAMILY["CAL"]
CKPT = os.path.join(C.CKPT_ROOT, "audit12_cal")
OUT_PASO0 = os.path.join(C.RESULTS, "cal_paso0_audit12.json")
A10_CAL = os.path.join(C.CKPT_ROOT, "audit10_cal")
A10_N = (100, 200, 500, 1000)
PASO0 = 50
PQ_COLS = P.pq_cols()


def pq_row(n):
    def f(i):
        return P.row_pq(D.cal_path(n, i), n)
    return f


def load_pq(n):
    rows, el = R.load_cell(CKPT, "cal_n%d" % n, D.N_CAL)
    return rows, PQ_COLS, el


def load_a10(n):
    with np.load(os.path.join(A10_CAL, "cal_n%d.npz" % n)) as z:
        return z["rows"], tuple(str(c) for c in z["cols"])


def paso0():
    out = {}
    for n in A10_N:
        rows, cols = load_a10(n)
        J = {c: i for i, c in enumerate(cols)}
        rng = np.random.default_rng(E.CAL_SEED)
        ys = [P.null_path(("ma", 0.0), n, rng) for _ in range(PASO0)]
        for det in ("c", "ct"):
            worst = {}
            new = [P.np_part(y, n, det) for y in ys]
            for c in ("s2", "gls_t0", "gls_t0.02", "glsb_t0", "dfgls", "mzt", "msb", "k", "s2ar", "adf", "pp"):
                ref = rows[:PASO0, J["s2" if c == "s2" else "%s|%s" % (det, c)]]
                a = np.array([d[c] for d in new])
                dd = np.where(np.isnan(a) & np.isnan(ref), 0.0, np.abs(a - ref))
                worst[c] = float(np.max(np.where(np.isnan(dd), np.inf, dd)))
            out["%d|%s" % (n, det)] = {"by_column": worst, "max_abs_diff": max(worst.values())}
        del rows
    worst = max(v["max_abs_diff"] for v in out.values())
    res = {"provenance": C.provenance(__file__, seed_family=None), "reps": PASO0, "cells": out, "max_abs_diff": worst,
           "passes": worst == 0.0, "source": "checkpoints/audit10_cal/cal_n<n>.npz (semilla 42)"}
    C.write_result(OUT_PASO0, res, __file__)
    print("Paso 0 A10", worst)
    return 0 if res["passes"] else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--paso0", action="store_true")
    ap.add_argument("--n", type=int, nargs="*", default=list(D.CAL_N))
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    rc = 0
    if a.paso0:
        rc = paso0()
    if a.run:
        t_block = time.time()
        resume = "python experiments/audit12_cal.py --run --cores %d --n %s" % (a.cores, " ".join(str(n) for n in a.n))
        R.warm(a.cores)
        try:
            for n in a.n:
                print("[CAL] n=%d" % n, flush=True)
                R.run_cell("cal_n%d" % n, D.N_CAL, pq_row(n), len(PQ_COLS), CKPT, a.cores, t_block, a.max_seconds,
                           resume, per_core=500 if n <= 500 else 200, log=lambda s: print(s, flush=True))
        except C.BudgetExhausted as exc:
            print("[TOPE] %s" % exc, flush=True)
            return 2
        print("calibracion: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
