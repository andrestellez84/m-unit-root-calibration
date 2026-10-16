"""
Auditoria A10 - B10.3.2 (condicional): DGP 5 a n = 200 con la primaria final.

Solo si el theta de B10.1 != 0.1. Trayectorias de A7 (familia 60), regeneradas
con sus semillas; Paso 0 de las componentes g1/g2 (R = 0.5) frente a los
checkpoints de A7. Columnas de A7 (R = 0.5, R adaptativo, union conjunta,
bootstrap DF-GLS) y sus umbrales a tamano igualado: los de A7 (celda de
calibracion de A7, N_cal = 5000). La primaria final (RM-GLS, theta final,
sigma_hat HAC) se calcula nueva sobre las trayectorias de A7 y sobre la celda de
calibracion de A7; umbral igualado = cuantil 5% en esa celda (como A8). Nivel
nominal: la primaria con la ECDF de la nula hac de B10.1 (n = 200, N_cal = 500 000);
R = 0.5 con la nula hac de A8. Control: la misma rutina con theta = 0.1 frente a
la cache de A8 (audit8_b5/dgp5_gls_<celda>.npz) en las primeras 50 series.
Cuota mediana de g2: la de A7 (R = 0.5).

Salida: experiments/results/b103_dgp5_audit10.json.
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

import audit10_common as C                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import cdf_from_null_stats  # noqa: E402

FAM = C.FAMILY["B10.3"]
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b103")
CKPT_A8 = os.path.join(C.CKPT_ROOT, "audit8_b5")
OUT = os.path.join(C.RESULTS, "b103_dgp5_audit10.json")
N = 200
PASO0 = 50


def final_theta():
    return C.read_json("b101_theta_audit10.json")["primary_theta"]


def _stats(kind, rho, r, sb, idx, theta):
    import audit7_dgp5_runner as RUN
    out = []
    for i in idx:
        y = RUN.generate(kind, N, rho, r, sb, i)
        out.append(E.rmgls(y, N, theta, hac_sigma_sq(y), "c"))
    return out


def gls_stats(kind, rho, r, reps, theta, cores):
    import audit7_design as D7
    import audit7_dgp5_runner as RUN
    tag = D7.cal_tag(N) if kind == "cal" else D7.dgp5_tag(N, rho, r)
    os.makedirs(CKPT, exist_ok=True)
    p = os.path.join(CKPT, "dgp5_%s_%s.npz" % (E.tname(theta), tag))
    if os.path.exists(p):
        with np.load(p) as z:
            if bool(z["complete"]) and z["stat"].shape == (reps,):
                return z["stat"], tag
    sb = RUN.cell_seed_base(kind, N, rho, r)
    parts = [list(range(reps))[j::cores] for j in range(cores)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(_stats)(kind, rho, r, sb, pp, theta) for pp in parts)
    stat = np.zeros(reps)
    for pp, rr in zip(parts, res):
        stat[np.array(pp)] = rr
    np.savez(p + ".tmp.npz", stat=stat, complete=True)
    os.replace(p + ".tmp.npz", p)
    return stat, tag


def a8_control(kind, rho, r, tag):
    """theta = 0.1 con esta rutina frente a la cache de RM-GLS de A8 (primeras PASO0 series)."""
    import audit7_dgp5_runner as RUN
    p = os.path.join(CKPT_A8, "dgp5_gls_%s.npz" % tag)
    if not os.path.exists(p):
        return None
    with np.load(p) as z:
        ref = z["stat"][:PASO0]
    mine = np.array(_stats(kind, rho, r, RUN.cell_seed_base(kind, N, rho, r), range(PASO0), 0.1))
    return float(np.max(np.abs(mine - ref)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    theta = final_theta()
    if theta == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    import audit7_design as D7
    import audit7_dgp5_runner as RUN
    import audit7_dgp5_analysis as AN
    B = D7.DGP5_B
    I = RUN.IDX

    def a7_rows(tag, n_sim):
        rows, why = AN.load_rows(RUN.CKPT, tag, n_sim)
        if rows is None:
            raise KeyError("checkpoints de A7 no disponibles para %s: %s" % (tag, why))
        return rows

    E.warm(a.cores)
    cal_rows = a7_rows(D7.cal_tag(N), D7.N_CAL)
    cal = AN.calibrate(cal_rows, B)
    cal_stat, cal_tag = gls_stats("cal", None, None, D7.N_CAL, theta, a.cores)
    thr = float(np.quantile(-cal_stat, AN.CAL_QUANTILE))
    rows10, cols10, _ = E10.load_cal(N)
    cdf_prim = cdf_from_null_stats(rows10[:, E.index(cols10)["c|%s" % E.tname(theta)]])
    del rows10
    null8 = B2.rm_null(N, a.cores)
    cdf_05 = cdf_from_null_stats(null8[:, B2.NULL_COLS.index(("R0.5_t0.1", "hac"))])
    controls = {cal_tag: a8_control("cal", None, None, cal_tag)}
    worst = 0.0
    cells = {}
    for (nn, rho, r) in D7.dgp5_cells():
        if nn != N:
            continue
        tag = D7.dgp5_tag(nn, rho, r)
        rows = a7_rows(tag, D7.DGP5_N_SIM)
        sb = RUN.cell_seed_base("dgp5", nn, rho, r)
        for i in range(PASO0):
            y = RUN.generate("dgp5", nn, rho, r, sb, i)
            t1, t2 = B2.taus(0.1, nn, "theta")
            _, g1, g2 = path_statistic(y, nn, t1, t2, 0.5, hac_sigma_sq(y), B2.C1, B2.C2)
            worst = max(worst, abs(g1 - rows[i, I["g1_std"]]), abs(g2 - rows[i, I["g2_std"]]))
        sm = AN.rejections_size_matched(rows, B, cal)
        ps, _ = gls_stats("dgp5", rho, r, D7.DGP5_N_SIM, theta, a.cores)
        controls[tag] = a8_control("dgp5", rho, r, tag)
        sm["primary"] = -ps > thr
        nom = {"primary_hac": np.clip(cdf_prim(ps), 0, 1) < C.ALPHA,
               "r05_hac": np.clip(cdf_05(rows[:, I["stat_R050"]]), 0, 1) < C.ALPHA}
        cells[tag] = {"rho": rho, "r": r,
                      "size_matched": {k: C.rate_record(sm[k]) for k in ("primary", "proposed_R050", "proposed_adaptive",
                                                                         "union_joint", "bootstrap_dfgls")},
                      "nominal_hac": {k: C.rate_record(v) for k, v in nom.items()},
                      "g2_share_R050_median": float(np.median(rows[:, I["g2_share_R050"]])),
                      "mcnemar_primary_vs_R050": C.mcnemar_exact(sm["primary"], sm["proposed_R050"]),
                      "mcnemar_primary_vs_bootstrap": C.mcnemar_exact(sm["primary"], sm["bootstrap_dfgls"])}
    a7 = C.read_json("dgp5_mixed_audit7.json")
    ctrl_vals = [v for v in controls.values() if v is not None]
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "primary": E.tname(theta), "n": N, "B": B, "N_sim": D7.DGP5_N_SIM,
                      "N_cal_equalized": D7.N_CAL, "N_cal_nominal_primary": E10.N_CAL,
                      "rule": "protocol_audit10.md, lectura 10 (3.2)"},
           "calibration_cell": cal_tag, "threshold_primary": thr, "a7_thresholds": cal["thresholds"],
           "a7_joint_alpha_star": cal["joint_union_alpha_star"],
           "paso0": {"reps": PASO0, "max_abs_diff_components": worst},
           "control_theta01_vs_a8": {"by_cell": controls, "max_abs_diff": max(ctrl_vals) if ctrl_vals else None},
           "a7_source_sha256": C.sha256_file(os.path.join(C.RESULTS, "dgp5_mixed_audit7.json")),
           "a7_generated_utc": a7["provenance"]["generated_utc"], "cells": cells,
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("celdas", len(cells), "Paso 0", worst, "control A8", out["control_theta01_vs_a8"]["max_abs_diff"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
