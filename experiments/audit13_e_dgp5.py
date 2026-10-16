"""
Auditoria A13 - B13.E(2): DGP 5 a n = 200 con theta = 0 (tab:dgp5).

B10.3.2 (audit10_b103_dgp5) con theta = 0. Trayectorias de A7 (familia 60),
regeneradas con sus semillas; sin aleatoriedad nueva. RM-GLS theta = 0 (sigma_hat
HAC) se calcula sobre las trayectorias de A7 y sobre su celda de calibracion
(N_cal = 5000); umbral igualado = cuantil 5 % en esa celda. Nivel nominal: ECDF de
la nula de A10 (N_cal = 500 000) con theta = 0. Columnas de A7 sin cambios.

Paso 0 (protocol_audit13.md, lectura 10), max |Delta| = 0:
  (a) componentes g1/g2 (R = 0.5) frente a los checkpoints de A7, 50 series por
      celda (como A10);
  (b) RM-GLS theta = 0.02 recalculado con esta rutina en las 50 primeras series de
      cada celda y de la celda de calibracion frente a la cache de A10
      (audit10_b103/dgp5_gls_t0.02_<celda>.npz).
Tambien se reproduce la tabla de A10 (theta = 0.02) desde esa cache con esta
rutina de analisis: tasas igualadas y nominales de la primaria frente a
b103_dgp5_audit10.json.

Salida: experiments/results/e_dgp5_audit13.json.
"""
import argparse
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
import audit10_b103_dgp5 as B103D                                  # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import cdf_from_null_stats  # noqa: E402

CKPT = os.path.join(C.CKPT_ROOT, "audit13_dgp5")
CKPT_A10 = os.path.join(C.CKPT_ROOT, "audit10_b103")
OUT = os.path.join(C.RESULTS, "e_dgp5_audit13.json")
N = B103D.N
PASO0 = B103D.PASO0


def a10_cache(tag):
    with np.load(os.path.join(CKPT_A10, "dgp5_%s_%s.npz" % (C.PRIM_V13, tag))) as z:
        return z["stat"]


def paso0_v13(kind, rho, r, tag):
    import audit7_dgp5_runner as RUN
    mine = np.array(B103D._stats(kind, rho, r, RUN.cell_seed_base(kind, N, rho, r), range(PASO0), C.THETA_V13))
    return float(np.max(np.abs(mine - a10_cache(tag)[:PASO0])))


def table(stat_by_tag, cal_stat, cdf_prim, cells_spec, AN, B, cal, a7_rows):
    import audit7_dgp5_runner as RUN
    I = RUN.IDX
    thr = float(np.quantile(-cal_stat, AN.CAL_QUANTILE))
    out = {}
    for tag, (rho, r) in cells_spec.items():
        rows = a7_rows[tag]
        sm = AN.rejections_size_matched(rows, B, cal)
        ps = stat_by_tag[tag]
        sm["primary"] = -ps > thr
        out[tag] = {"rho": rho, "r": r,
                    "size_matched": {k: C.rate_record(sm[k]) for k in ("primary", "proposed_R050", "proposed_adaptive",
                                                                       "union_joint", "bootstrap_dfgls")},
                    "nominal_hac": {"primary_hac": C.rate_record(np.clip(cdf_prim(ps), 0, 1) < C.ALPHA)},
                    "g2_share_R050_median": float(np.median(rows[:, I["g2_share_R050"]])),
                    "mcnemar_primary_vs_R050": C.mcnemar_exact(sm["primary"], sm["proposed_R050"]),
                    "mcnemar_primary_vs_bootstrap": C.mcnemar_exact(sm["primary"], sm["bootstrap_dfgls"])}
    return out, thr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    import audit7_design as D7
    import audit7_dgp5_runner as RUN
    import audit7_dgp5_analysis as AN
    B = D7.DGP5_B
    I = RUN.IDX

    def a7(tag, n_sim):
        rows, why = AN.load_rows(RUN.CKPT, tag, n_sim)
        if rows is None:
            raise KeyError("checkpoints de A7 no disponibles para %s: %s" % (tag, why))
        return rows

    E.warm(a.cores)
    cal_tag = D7.cal_tag(N)
    cal = AN.calibrate(a7(cal_tag, D7.N_CAL), B)
    spec = {D7.dgp5_tag(nn, rho, r): (rho, r) for (nn, rho, r) in D7.dgp5_cells() if nn == N}
    rows = {tag: a7(tag, D7.DGP5_N_SIM) for tag in spec}
    saved = B103D.CKPT
    try:
        B103D.CKPT = CKPT                                 # la cache nueva no toca la carpeta de A10
        cal_stat0, _ = B103D.gls_stats("cal", None, None, D7.N_CAL, C.THETA, a.cores)
        stat0 = {tag: B103D.gls_stats("dgp5", rho, r, D7.DGP5_N_SIM, C.THETA, a.cores)[0] for tag, (rho, r) in spec.items()}
    finally:
        B103D.CKPT = saved
    worst_a = 0.0
    for tag, (rho, r) in spec.items():
        sb = RUN.cell_seed_base("dgp5", N, rho, r)
        for i in range(PASO0):
            y = RUN.generate("dgp5", N, rho, r, sb, i)
            t1, t2 = B2.taus(0.1, N, "theta")
            _, g1, g2 = path_statistic(y, N, t1, t2, 0.5, hac_sigma_sq(y), B2.C1, B2.C2)
            worst_a = max(worst_a, abs(g1 - rows[tag][i, I["g1_std"]]), abs(g2 - rows[tag][i, I["g2_std"]]))
    p0b = {cal_tag: paso0_v13("cal", None, None, cal_tag)}
    p0b.update({tag: paso0_v13("dgp5", rho, r, tag) for tag, (rho, r) in spec.items()})
    rows10, cols10, _ = E10.load_cal(N)
    J10 = E.index(cols10)
    cdf = {t: cdf_from_null_stats(rows10[:, J10["c|%s" % t]]) for t in (C.PRIM, C.PRIM_V13)}
    del rows10
    cells0, thr0 = table(stat0, cal_stat0, cdf[C.PRIM], spec, AN, B, cal, rows)
    cells2, thr2 = table({tag: a10_cache(tag) for tag in spec}, a10_cache(cal_tag), cdf[C.PRIM_V13], spec, AN, B, cal, rows)
    ref = C.read_json("b103_dgp5_audit10.json")
    rep = 0.0
    for tag, v in ref["cells"].items():
        for k, rr in v["size_matched"].items():
            rep = max(rep, abs(cells2[tag]["size_matched"][k]["rate"] - rr["rate"]))
        rep = max(rep, abs(cells2[tag]["nominal_hac"]["primary_hac"]["rate"] - v["nominal_hac"]["primary_hac"]["rate"]),
                  abs(cells2[tag]["mcnemar_primary_vs_R050"]["p_value"] - v["mcnemar_primary_vs_R050"]["p_value"]),
                  abs(cells2[tag]["mcnemar_primary_vs_bootstrap"]["p_value"] - v["mcnemar_primary_vs_bootstrap"]["p_value"]))
    rep = max(rep, abs(thr2 - ref["threshold_primary"]))
    out = {"provenance": C.provenance(__file__, seed_family=None),
           "config": {"theta": C.THETA, "primary": C.PRIM, "n": N, "B": B, "N_sim": D7.DGP5_N_SIM,
                      "N_cal_equalized": D7.N_CAL, "N_cal_nominal_primary": E10.N_CAL,
                      "trajectories": "A7 (familia 60), regeneradas con sus semillas",
                      "reading": "protocol_audit13.md, lectura 10"},
           "calibration_cell": cal_tag, "threshold_primary": thr0, "threshold_v13": thr2,
           "a7_thresholds": cal["thresholds"], "a7_joint_alpha_star": cal["joint_union_alpha_star"],
           "paso0": {"reps": PASO0, "a_components_max_abs_diff": worst_a, "b_v13_vs_a10_cache": p0b,
                     "b_max_abs_diff": max(p0b.values()), "c_v13_table_vs_b103_max_abs_diff": rep,
                     "passes": worst_a == 0 and max(p0b.values()) == 0 and rep == 0},
           "a7_source_sha256": C.sha256_file(os.path.join(C.RESULTS, "dgp5_mixed_audit7.json")),
           "cells": cells0, "cells_v13": cells2, "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("Paso 0", out["paso0"]["a_components_max_abs_diff"], out["paso0"]["b_max_abs_diff"],
          out["paso0"]["c_v13_table_vs_b103_max_abs_diff"])
    for tag, v in cells0.items():
        print(tag, round(v["size_matched"]["primary"]["rate"], 4), round(cells2[tag]["size_matched"]["primary"]["rate"], 4))
    return 0 if out["paso0"]["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
