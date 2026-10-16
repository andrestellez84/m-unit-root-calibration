"""
Auditoria A10 - B10.3.1 (condicional): potencia a tamano igualado con el theta final.

Solo si el theta de B10.1 != 0.1 (protocol_audit10.md, CONDICION B10.3).
Filas: checkpoints de B9.1 (DGP 1, DGP 2, potencia con tendencia; trayectorias de
B5 de A8, Paso 0 ya hecho en A9 y repetido aqui) y de B9.2 (DGP 3). Contienen las
columnas de los cinco theta: no se simula ninguna trayectoria.
Umbrales simulados: calibracion de N_cal = 500 000 de B10.1 (n in {200, 500,
1000}) en las columnas que contiene; KPSS y ZA (sin columna en la calibracion de
500 000) con la de A9 (N_cal = 50 000). La fuente se declara por procedimiento.
Primaria de las McNemar: RM-GLS con el theta final. E1 y E2 se recalculan como
informacion.

Salida: experiments/results/b103_equalized_audit10.json.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402

FAM = C.FAMILY["B10.3"]
OUT = os.path.join(C.RESULTS, "b103_equalized_audit10.json")
N3 = (200, 500, 1000)


def final_theta():
    b = C.read_json("b101_theta_audit10.json")
    return b["primary_theta"]


def combined_rejectors(ns=N3, cases=E.CASES):
    """Rechazo con la calibracion de 500 000 si la columna existe; si no, la de A9 (50 000)."""
    out, src = {}, {}
    for n in ns:
        rows10, cols10, _ = E10.load_cal(n)
        rows9, cols9 = B91.CAL.load(n)
        for case in cases:
            r10, q10 = E.rejector(rows10, cols10, case)
            r9, q9 = E.rejector(rows9, cols9, case)
            have10 = {c.split("|", 1)[1] for c in cols10 if c.startswith(case + "|")}

            def rej(rows, cols, p, r10=r10, r9=r9, have10=have10):
                return r10(rows, cols, p) if p in have10 else r9(rows, cols, p)
            qs = dict(q9)
            qs.update(q10)
            out[(n, case)] = (rej, qs)
            src["%s|%d" % (case, n)] = {"N_cal_500000": sorted(have10 & set(E.RM_LIKE + E.SIM_LOWER)),
                                        "N_cal_50000_a9": sorted(set(E.SIM_LOWER) - have10)}
        del rows10, rows9
    return out, src


def main():
    t0 = time.time()
    theta = final_theta()
    prim = E.tname(theta)
    if theta == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    B91.PRIMARY = prim
    region = C.exact_region(D9.N_SIM)
    rejectors, src = combined_rejectors()
    a8 = C.read_json("b5_power_audit8.json")
    thetas = tuple(E.tname(t) for t in E.THETAS) + ("glsb_t0",)
    res, _ = B91.analyze_cells(list(B91.cells()), rejectors, region, a8, extra_procs=thetas)
    saved = B91.CKPT
    try:
        B91.CKPT = B92.CKPT
        d3, _ = B91.analyze_cells(B92.dgp3_cells(), rejectors, region, a8, extra_procs=thetas)
    finally:
        B91.CKPT = saved
    e1, e2 = B91.e_rules(res)
    res.update(d3)
    worst = max(v["paso0"]["max_abs_diff"] for v in res.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "primary": prim, "N_sim": D9.N_SIM, "N_cal": E10.N_CAL,
                      "trajectories": "B5 de A8 (familia 95): filas de audit9_b91 (DGP 1, DGP 2, tendencia) y "
                                      "audit9_b92 (DGP 3)",
                      "rule_sim": "RM-like: p = F_null(stat) < 0.05; resto: stat < cuantil 5% bajo la Ec. (3)",
                      "calibration_source": src},
           "exact_region_5000": region, "paso0_worst": worst, "cells": res,
           "E1_informative": e1, "E2_informative": e2,
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("theta", theta, "Paso 0 peor", worst, "E1", e1["wins"], e1["wins_with_mcnemar"], "E2", e2["wins"],
          e2["wins_with_mcnemar"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
