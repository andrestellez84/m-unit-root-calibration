"""
Auditoria A9 - B9.3: de donde viene la ganancia en muestra finita (solo analisis).

A tau = 0 y anclaje GLS, tres variantes sobre las mismas trayectorias:
  (a) escala sigma_hat HAC (Bartlett, Andrews alpha(1)) + valores criticos simulados
      (columna gls_t0, nula hac de produccion);
  (b) escala s2_AR con MAIC + valores criticos simulados (columna glsb_t0; la misma
      muestra de calibracion, con s2_AR en cada camino);
  (c) s2_AR con MAIC + valores criticos asintoticos de Ng-Perron: MSB-GLS estandar
      (columna msb con 0.233 / 0.168).
Control de convencion: MSB-GLS con valor critico simulado (msb sim).

Regla de atribucion (protocolo): (a) - (b) = estimador de escala; (b) - (c) =
calibracion. Diferencias pareadas con su EE, por celda y en media por n.

Evaluacion: tamano gaussiano (independientes de B9.2, n in {100, 200, 500, 1000},
ambos casos); las 22 celdas de mala especificacion (Delta frente a la gaussiana
independiente del mismo n y caso); DGP 1 (demeaned) y caso con tendencia (filas de
B9.1); potencia local c in {5, 10, 15, 20} (filas de B9.2), ambos casos.
"""
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402

FAM = C.FAMILY["B9.3"]
OUT = os.path.join(C.RESULTS, "b93_attribution_audit9.json")
SIZE_N = (100, 200, 500, 1000)
LP_C = (5.0, 10.0, 15.0, 20.0)
VARIANTS = ("a", "b", "c", "msb_sim")


def variants(rej, rows, cols, case):
    return {"a": rej(rows, cols, "gls_t0"), "b": rej(rows, cols, "glsb_t0"),
            "c": E.reject_asy(rows, cols, case, "msb"), "msb_sim": rej(rows, cols, "msb")}


def diffs(v):
    return {"a_minus_b": C.paired_diff(v["a"], v["b"]), "b_minus_c": C.paired_diff(v["b"], v["c"]),
            "b_minus_msb_sim": C.paired_diff(v["b"], v["msb_sim"])}


def rates(v, region):
    return {k: C.rate_record(x, region) for k, x in v.items()}


def combine(d_mis, d_g):
    return {"delta": d_mis["delta"] - d_g["delta"], "se": math.sqrt(d_mis["se"] ** 2 + d_g["se"] ** 2)}


def by_n(cells, key):
    out = {}
    for n in sorted({c["n"] for c in cells.values()}):
        ks = [k for k, c in cells.items() if c["n"] == n]
        out[str(n)] = {"cells": ks, **{d: C.mean_with_se([cells[k][key][d] for k in ks])
                                       for d in ("a_minus_b", "b_minus_c", "b_minus_msb_sim")}}
    return out


def analyze():
    t0 = time.time()
    rejectors, _ = B91.rejectors_for(D.N_ALL, E.CASES)
    region20, region5 = C.exact_region(D.N_INDEP), C.exact_region(D.N_SIM)
    scols = E.columns(**B92.SIZE_FLAGS)
    # tamano gaussiano (y referencia de Delta en todos los n de las celdas mal especificadas)
    gauss, gv = {}, {}
    for n in D.N_ALL:
        rows, _ = C.load_rows(B92.CKPT, "indep_n%d" % n, D.N_INDEP)
        for case in E.CASES:
            v = variants(rejectors[(n, case)][0], rows, scols, case)
            gv[(n, case)] = v
            if n in SIZE_N:
                gauss["%s|%d" % (case, n)] = {"n": n, "case": case, "rates": rates(v, region20), "diffs": diffs(v)}
    # mala especificacion
    mis = {}
    for k, s in D.misspec_cells().items():
        n = s["n"]
        rows, _ = C.load_rows(B92.CKPT, k, D.N_SIM)
        for case in E.CASES:
            v = variants(rejectors[(n, case)][0], rows, scols, case)
            dm, dg = diffs(v), diffs(gv[(n, case)])
            mis["%s|%s" % (case, k)] = {"cell": k, "n": n, "case": case, "rates": rates(v, region5),
                                        "delta_vs_gauss": {x: C.diff_independent(C.rate_record(v[x]), C.rate_record(gv[(n, case)][x]))
                                                           for x in VARIANTS},
                                        "diffs_of_delta": {d: combine(dm[d], dg[d]) for d in dm}}
    # DGP 1 y tendencia (filas de B9.1)
    pw = {}
    for k, spec in B91.cells().items():
        if not k.startswith(("dgp1_", "ct_power_")):
            continue
        n = spec["n"]
        case = "ct" if k.startswith("ct_") else "c"
        rows, _ = C.load_rows(B91.CKPT, k, D.N_SIM)
        v = variants(rejectors[(n, case)][0], rows, E.columns(**B91.flags_for(k)), case)
        pw[k] = {"n": n, "case": case, "rho": spec["rho"], "rates": rates(v, region5), "diffs": diffs(v)}
    # potencia local
    lp = {}
    for case in D.LP_CASES:
        det = D.CASE_DET[case]
        rej = rejectors[(D.N_LP, det)][0]
        cols = E.columns(cases=(det,), **B92.LP_FLAGS)
        for c in LP_C:
            rows, _ = C.load_rows(B92.CKPT, "lp_%s_c%s" % (case, D.cname(c)), D.N_POWER)
            v = variants(rej, rows, cols, det)
            lp["%s|%s" % (case, D.cname(c))] = {"case": case, "c": c, "n": D.N_LP,
                                               "power": {x: float(y.mean()) for x, y in v.items()}, "diffs": diffs(v)}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"a": "gls_t0 (sigma_hat HAC) + nula hac simulada", "b": "glsb_t0 (s2_AR MAIC) + nula simulada con s2_AR",
                      "c": "MSB-GLS (MAIC) + valor asintotico de Ng-Perron", "control": "MSB-GLS + valor simulado",
                      "rule": "(a) - (b) = escala; (b) - (c) = calibracion (protocolo)",
                      "se": "pareado: sd(d_i)/sqrt(N); en Delta, cuadratura con la parte gaussiana; medias por n con sqrt(sum se^2)/k",
                      "size_n": list(SIZE_N), "local_c": list(LP_C)},
           "exact_region_20000": region20, "exact_region_5000": region5,
           "gaussian_size": gauss, "gaussian_size_by_n": {case: {str(n): gauss["%s|%d" % (case, n)]["diffs"] for n in SIZE_N}
                                                          for case in E.CASES},
           "misspec": mis,
           "misspec_by_n": {case: by_n({k: v for k, v in mis.items() if v["case"] == case}, "diffs_of_delta")
                            for case in E.CASES},
           "power": pw,
           "power_by_n": {case: by_n({k: v for k, v in pw.items() if v["case"] == case}, "diffs") for case in E.CASES},
           "local_power": lp, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for case in E.CASES:
        print(case, {n: (round(d["a_minus_b"]["delta"] * 100, 2), round(d["b_minus_c"]["delta"] * 100, 2))
                     for n, d in out["gaussian_size_by_n"][case].items()})
    return 0


if __name__ == "__main__":
    sys.exit(analyze())
