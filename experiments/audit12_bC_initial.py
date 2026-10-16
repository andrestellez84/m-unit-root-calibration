"""
Auditoria A12 - B12.C: condicion inicial (familia 132).

DGP 1 constante, n = 200, rho in {0.90, 0.95, 0.97}; u_0 = alpha / sqrt(1 - rho^2) con
alpha in {0, 1, 2, 4} (signo positivo) y una variante con u_0 = z_0 / sqrt(1 - rho^2),
z_0 ~ N(0, 1) de la celda c_u0_rho<rho>. Pareo (lectura 14): e_1..e_n de la celda
c_rho<rho>, comunes a las cinco variantes de u_0. y_t = u_t, u_t = rho u_{t-1} + e_t.
Fila completa de B12.A (audit12_unitroot.row_a, caso c) por variante; procedimientos
al cv iid de n = 200 (A10 N_cal = 500 000 para el lado NP, familia 136 para (b')).
Potencia y McNemar exacto frente a DF-GLS (MAIC-GLS, cv simulado).

Uso: python experiments/audit12_bC_initial.py --run --cores 14 ; --analyze
Salida: experiments/results/bC_initial_audit12.json.
"""
import argparse
import math
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
import audit12_bA_ma as A                                          # noqa: E402

FAM = C.FAMILY["C"]
CKPT = os.path.join(C.CKPT_ROOT, "audit12_bC")
OUT = os.path.join(C.RESULTS, "bC_initial_audit12.json")
VARIANTS = tuple("alpha%g" % a for a in D.C_ALPHA) + ("random",)
PROCS = ("gls_t0", "gls_t0.02", "glsb_t0", "glsbp_t0", "dfgls", "mzt", "msb", "adf", "pp")
REF = "dfgls"
NC = len(P.COLS_A)


def paths(rho, i):
    e = D.c_innov_rng(rho, i).standard_normal(D.C_N)
    z0 = D.c_u0_rng(rho, i).standard_normal()
    s = 1.0 / math.sqrt(1.0 - rho * rho)
    out = []
    for u0 in [a * s for a in D.C_ALPHA] + [z0 * s]:
        y = np.empty(D.C_N + 1)
        y[0] = u0
        for t in range(D.C_N):
            y[t + 1] = rho * y[t] + e[t]
        out.append(y)
    return out


def row_fn(rho):
    def f(i):
        r = []
        for y in paths(rho, i):
            r += P.row_a(y, D.C_N, "c")
        return r
    return f


def tag(rho):
    return "c_rho%s" % D.rtag(rho)


def run(cores, max_seconds):
    t_block = time.time()
    resume = "python experiments/audit12_bC_initial.py --run --cores %d" % cores
    R.warm(cores)
    try:
        for rho in D.C_RHO:
            print("[CELDA] %s" % tag(rho), flush=True)
            R.run_cell(tag(rho), D.N_C, row_fn(rho), NC * len(VARIANTS), CKPT, cores, t_block, max_seconds, resume,
                       per_core=50, log=lambda s: print(s, flush=True))
    except C.BudgetExhausted as exc:
        print("[TOPE] %s" % exc, flush=True)
        return 2
    return 0


def analyze():
    t0 = time.time()
    rule = A.iid_rules((D.C_N,))[(D.C_N, "c")]
    res = {}
    for rho in D.C_RHO:
        R_all, el = R.load_cell(CKPT, tag(rho), D.N_C)
        for vi, v in enumerate(VARIANTS):
            rows = R_all[:, vi * NC:(vi + 1) * NC]
            rej = {p: A.reject_iid(rule, rows, p) for p in PROCS}
            res["%s|%s" % (D.rtag(rho), v)] = {
                "rho": rho, "variant": v, "alpha": None if v == "random" else D.C_ALPHA[vi],
                "power": {p: C.rate_record(x) for p, x in rej.items()},
                "mcnemar_vs_dfgls": {p: C.mcnemar_exact(rej[p], rej[REF]) for p in PROCS if p != REF},
                "diff_vs_dfgls": {p: C.paired_diff(rej[p], rej[REF]) for p in PROCS if p != REF},
                "nan": {p: int(np.sum(~np.isfinite(rows[:, A.J[p]]))) for p in PROCS}, "elapsed_sec": el}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"n": D.C_N, "rho": list(D.C_RHO), "alpha": list(D.C_ALPHA), "variants": list(VARIANTS), "N": D.N_C,
                      "procs": list(PROCS), "reference": REF, "case": "c",
                      "u0": "alpha / sqrt(1 - rho^2); random: z_0 / sqrt(1 - rho^2), z_0 ~ N(0, 1)",
                      "pairing": "e_1..e_n comunes a las cinco variantes de cada rho (celda c_rho<rho>)",
                      "cv": "iid n = 200 (A10 N_cal = 500 000; (b'): familia 136)",
                      "calibration_source": rule["source"]},
           "cells": res, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for k, v in res.items():
        print(k, {p: round(x["rate"], 3) for p, x in v["power"].items()})
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    if a.run:
        rc = run(a.cores, a.max_seconds)
        if rc:
            return rc
    if a.analyze:
        return analyze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
