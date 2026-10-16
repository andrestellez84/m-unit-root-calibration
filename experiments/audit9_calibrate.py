"""
Auditoria A9 - calibracion bajo la Ec. (3) sobre los caminos de produccion (semilla 42).

Una muestra por n (N_cal = 50000) con todas las columnas del motor para los dos
casos deterministas; KPSS y ZA en n in {200, 500, 1000}; P_T de ERS en n = 2000.
Checkpoint por trozo (npz) y reanudacion; tope de 4 h.

Uso: python experiments/audit9_calibrate.py --n 200 500 1000 --cores 14
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit9_common as C                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402

CKPT = os.path.join(C.CKPT_ROOT, "audit9_cal")


def load(n):
    import numpy as np
    with np.load(os.path.join(CKPT, "cal_n%d.npz" % n)) as z:
        return z["rows"], tuple(str(c) for c in z["cols"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", required=True)
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    resume = "python experiments/audit9_calibrate.py --n %s --cores %d" % (" ".join(map(str, a.n)), a.cores)
    t_block = time.time()
    E.warm(a.cores)
    for n in a.n:
        t0 = time.time()
        try:
            rows, cols = E.calibration(n, a.cores, CKPT, t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
        print("[CAL] n=%d %s filas x %d columnas en %.0f s" % (n, rows.shape[0], rows.shape[1], time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
