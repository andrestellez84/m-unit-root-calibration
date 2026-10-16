"""
Auditoria A13 - B13.E(1): tab:dgp1, tab:ctpower, tab:dgp2 y tab:dgp3 con theta = 0.

Sin simular. Repite el analisis de B10.3.1 (audit10_b103_equalized) sobre las
mismas filas (checkpoints de B9.1 y B9.2, trayectorias de B5 de A8, familia 95) y
con los mismos umbrales (calibracion de 500 000 de A10; KPSS y ZA con la de A9),
cambiando solo la primaria de las McNemar a RM-GLS theta = 0.

Paso 0 (protocol_audit13.md, lectura 3):
  (a) el de B9.1 frente a B5 de A8, que analyze_cells repite en cada celda;
  (b) todas las tasas (simuladas y asintoticas) de todas las columnas coinciden con
      las de b103_equalized_audit10.json (max |Delta| = 0);
  (c) el mismo codigo con la primaria theta = 0.02 reproduce las McNemar publicadas
      (mcnemar_primary_vs_sim) de b103_equalized_audit10.json (max |Delta| = 0).

Salida: experiments/results/e_equalized_audit13.json.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402
import audit10_b103_equalized as B103                              # noqa: E402

OUT = os.path.join(C.RESULTS, "e_equalized_audit13.json")


def analyze(primary, rejectors, region, a8):
    B91.PRIMARY = primary
    thetas = tuple(E.tname(t) for t in E.THETAS) + ("glsb_t0",)
    res, _ = B91.analyze_cells(list(B91.cells()), rejectors, region, a8, extra_procs=thetas)
    saved = B91.CKPT
    try:
        B91.CKPT = B92.CKPT
        d3, _ = B91.analyze_cells(B92.dgp3_cells(), rejectors, region, a8, extra_procs=thetas)
    finally:
        B91.CKPT = saved
    res.update(d3)
    return res


def max_rate_diff(mine, ref):
    worst, n = 0.0, 0
    for k, v in ref["cells"].items():
        for block in ("rates_sim", "rates_asy"):
            for p, r in v[block].items():
                worst = max(worst, abs(mine[k][block][p]["rate"] - r["rate"]))
                n += 1
    return worst, n


def max_mcnemar_diff(mine, ref):
    worst, n = 0.0, 0
    for k, v in ref["cells"].items():
        for p, r in v["mcnemar_primary_vs_sim"].items():
            m = mine[k]["mcnemar_primary_vs_sim"][p]
            worst = max(worst, abs(m["p_value"] - r["p_value"]), abs(m["only_first"] - r["only_first"]),
                        abs(m["only_second"] - r["only_second"]))
            n += 1
    return worst, n


def main():
    t0 = time.time()
    ref = C.read_json("b103_equalized_audit10.json")
    region = C.exact_region(D9.N_SIM)
    rejectors, src = B103.combined_rejectors()
    a8 = C.read_json("b5_power_audit8.json")
    res0 = analyze(C.PRIM, rejectors, region, a8)
    res2 = analyze(C.PRIM_V13, rejectors, region, a8)
    rd, nr = max_rate_diff(res0, ref)
    md, nm = max_mcnemar_diff(res2, ref)
    worst_a = max(v["paso0"]["max_abs_diff"] for v in res0.values())
    out = {"provenance": C.provenance(__file__, seed_family=None),
           "config": {"theta": C.THETA, "primary": C.PRIM, "reference": C.PRIM_V13, "N_sim": D9.N_SIM,
                      "trajectories": ref["config"]["trajectories"], "rule_sim": ref["config"]["rule_sim"],
                      "calibration_source": src, "reading": "protocol_audit13.md, lecturas 3 y 5"},
           "exact_region_5000": region,
           "paso0": {"a_vs_a8_b5_worst": worst_a, "b_rates_vs_b103_max_abs_diff": rd, "b_rates_compared": nr,
                     "c_mcnemar_v13_vs_b103_max_abs_diff": md, "c_mcnemar_compared": nm,
                     "passes": worst_a == 0 and rd == 0 and md == 0},
           "cells": res0, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("Paso 0", out["paso0"])
    return 0 if out["paso0"]["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
