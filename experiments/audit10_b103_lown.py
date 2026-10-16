"""
Auditoria A10 - B10.3.7 (condicional): tamano gaussiano en el dominio bajo.

Solo si el theta de B10.1 != 0.1. n in {60, 100, 150}, N = 50 000 por (caso, n)
(familia 113, celdas low_<caso>_n<n>, hijos distintos por caso); calibracion de
N_cal = 500 000 en los caminos de produccion (audit10_engine.calibration, con
reutilizacion de A9 donde el troceo lo permite). Tasas de la primaria final y de
theta = 0.1 (y, como informacion, del resto de columnas), Wilson y region exacta
de N = 50 000.

Modos: --run (calibraciones y celdas, reanudable), --analyze.
Salida: experiments/results/b103_lown_audit10.json.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_design as D                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_engine as E                                          # noqa: E402

FAM = C.FAMILY["B10.3"]
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b103")
OUT = os.path.join(C.RESULTS, "b103_lown_audit10.json")
PROCS = tuple(E.tname(t) for t in E.THETAS) + ("rm_t0.1", "msbhac", "glsb_t0", "adf", "dfgls", "mzt", "msb")


def final_theta():
    return C.read_json("b101_theta_audit10.json")["primary_theta"]


def cell_flags(case):
    return {"cases": (D.CASE_DET[case],), "adfpp": True, "kpss": False, "za": False, "pt": False}


def run(a):
    if final_theta() == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    resume = "python experiments/audit10_b103_lown.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for n in D.LOW_N:
            t0 = time.time()
            _, _, info = E10.calibration(n, a.cores, t_block, a.max_seconds, resume, log=lambda *x: print(*x, flush=True))
            print("[CAL] n=%d lista: %.1f min, %s" % (n, (time.time() - t0) / 60, info), flush=True)
        for case in D.CASES:
            for n in D.LOW_N:
                tag = "low_%s_n%d" % (case, n)
                print("\n[CELDA] %s" % tag, flush=True)
                C.run_cell(tag, D.N_LOW, E.make_batch_fn(lambda i, cs=case, nn=n: D.low_path(cs, nn, i), n, a.cores,
                                                         **cell_flags(case)),
                           CKPT, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def analyze(a):
    t0 = time.time()
    theta = final_theta()
    region = C.exact_region(D.N_LOW)
    import audit10_b101_theta as B101
    qbig = B101.big_quantiles()
    cal, cells = {}, {}
    for n in D.LOW_N:
        rows, cols, info = E10.load_cal(n)
        cal[str(n)] = dict(info, N_cal=int(rows.shape[0]))
        for case in D.CASES:
            det = D.CASE_DET[case]
            rej, qs = E.rejector(rows, cols, det)
            srows, _ = C.load_rows(CKPT, "low_%s_n%d" % (case, n), D.N_LOW)
            scols = E.columns(**cell_flags(case))
            J = E.index(scols)
            cells["%s|%d" % (case, n)] = {
                "case": case, "n": n, "sim_thresholds": qs,
                "rates": {p: C.rate_record(rej(srows, scols, p), region) for p in PROCS},
                "size_with_cv_n20000": {t: dict(C.rate_record(srows[:, J["%s|%s" % (det, t)]] < qbig[(det, t)], region),
                                                cv_n20000=qbig[(det, t)]) for t in B101.THETA_PROCS},
                "msb_published_cv": dict(C.rate_record(E.reject_published(srows, scols, det, "msb"), region),
                                         cv=E.MSB_CV5_PUBLISHED[det])}
        del rows
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "primary": E.tname(theta), "reference": E.tname(0.1), "n": list(D.LOW_N),
                      "N": D.N_LOW, "N_cal": E10.N_CAL, "rule": "protocol_audit10.md, lectura 10 (3.7)"},
           "exact_region_50000": region, "calibration": cal, "cells": cells,
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for k, v in cells.items():
        print(k, {p: round(v["rates"][p]["rate"], 4) for p in (E.tname(theta), E.tname(0.1))})
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
