"""
Auditoria A10 - B10.3.4 (condicional): sonda AWB con el theta final (CARO, 8 h).

Solo si el theta de B10.1 != 0.1. Igual que B9.5 de A9 (audit9_b95_awb) salvo:
theta = el de B10.1; semillas de remuestreo SeedSequence(113, spawn_key =
(awb_<celda>, i)); la columna simulada rechaza con la nula de N_cal = 500 000 de
B10.1. Mismas trayectorias de origen (primeras 2000 de cada celda), B = 399,
AWB de bootUR 1.0.5 con sus valores por defecto, regla de recomendacion de A9
(protocol_audit9.md, REGLA B9.5) con la region exacta de N = 2000.

Modos: --budget (sonda de 14 series a n = 200 y 500; se detiene si excede 8 h),
--run, --analyze.
Salidas: b103_awb_budget_audit10.json, b103_awb_audit10.json.
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
import audit10_design as D                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b95_awb as B95                                       # noqa: E402

FAM = C.FAMILY["B10.3"]
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b103_awb")
OUT = os.path.join(C.RESULTS, "b103_awb_audit10.json")
OUT_BUDGET = os.path.join(C.RESULTS, "b103_awb_budget_audit10.json")
BUDGET_HOURS = 8.0


def final_theta():
    return C.read_json("b101_theta_audit10.json")["primary_theta"]


def awb_rows(cell, src, idx, theta):
    n = B95.cell_n(cell)
    out = []
    for i in idx:
        y = D9.awb_source_path(cell, src, i)
        p, s = E.awb_pvalue(y, n, theta, "c", D9.B_AWB, D.awb_rng(cell, i))
        out.append([p, s])
    return out


def batch_fn(cell, src, theta, cores):
    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(awb_rows)(cell, src, p, theta) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def budget(a):
    theta = final_theta()
    E.warm(a.cores)
    t_block = time.time()
    sps = {}
    for n, cell in B95.PROBE_CELLS.items():
        src = dict(D9.AWB_CELLS)[cell]
        _, info = C.C8.C7.run_cell_batched(cell, D9.N_AWB, batch_fn(cell, src, theta, a.cores), CKPT, a.cores, t_block,
                                           1e12, "", log=lambda *x: None, probe_only=True)
        sps[n] = info["probe_sec_per_series"]
    counts = {n: sum(1 for c, _ in D9.AWB_CELLS if B95.cell_n(c) == n) for n in B95.PROBE_CELLS}
    proj = sum(sps[n] * D9.N_AWB * counts[n] for n in B95.PROBE_CELLS)
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "budget_hours": BUDGET_HOURS, "theta": theta,
           "probe_sec_per_series": {str(k): v for k, v in sps.items()}, "cells_per_n": {str(k): v for k, v in counts.items()},
           "projected_total_hours": proj / 3600, "within_budget": bool(proj / 3600 <= BUDGET_HOURS),
           "rule": "sonda de 14 series a n = 200 y n = 500; proyeccion = sonda x 2000 x celdas de ese n"}
    C.write_result(OUT_BUDGET, out, __file__)
    print("B10.3.4 proyeccion %.2f h: %s" % (proj / 3600, out["within_budget"]))
    return 0 if out["within_budget"] else 3


def run(a):
    if not C.read_json(os.path.basename(OUT_BUDGET))["within_budget"]:
        print("presupuesto excedido: no se lanza B10.3.4")
        return 3
    theta = final_theta()
    resume = "python experiments/audit10_b103_awb.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for cell, src in D9.AWB_CELLS:
            print("\n[CELDA] %s" % cell, flush=True)
            C.run_cell(cell, D9.N_AWB, batch_fn(cell, src, theta, a.cores), CKPT, a.cores, t_block,
                       BUDGET_HOURS * 3600, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def analyze(a):
    t0 = time.time()
    theta = final_theta()
    prim = E.tname(theta)
    region = C.exact_region(D9.N_AWB)
    rej = {}
    for n in (200, 500):
        rows, cols, _ = E10.load_cal(n)
        rej[n] = E.rejector(rows, cols, "c")[0]
        del rows
    res = {}
    for cell, src in D9.AWB_CELLS:
        n = B95.cell_n(cell)
        rows, _ = C.load_rows(CKPT, cell, D9.N_AWB)
        p = rows[:, 0]
        srows, scols = B95.sim_rows(cell, src)
        r_sim = rej[n](srows, scols, prim)
        r_awb = p < C.ALPHA
        stat_diff = float(np.max(np.abs(rows[:, 1] - srows[:, E.index(scols)["c|%s" % prim]])))
        res[cell] = {"n": n, "source": src, "awb": C.rate_record(r_awb, region), "sim": C.rate_record(r_sim, region),
                     "mcnemar_awb_vs_sim": C.mcnemar_exact(r_awb, r_sim),
                     "power_loss_pp": (r_sim.mean() - r_awb.mean()) * 100,
                     "max_abs_diff_stat_vs_rows": stat_diff}
    dgp3 = [c for c in res if c.startswith("dgp3_")]
    dgp1 = [c for c in res if c.startswith("dgp1_")]
    n_in = sum(res[c]["awb"]["in_region"] for c in dgp3)
    loss_ok = all(res[c]["power_loss_pp"] <= B95.RULE_II_PP for c in dgp1)
    g, l = E.awb_gamma(200)
    g5, l5 = E.awb_gamma(500)
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "statistic": prim, "B": D9.B_AWB, "N_sim": D9.N_AWB,
                      "residuals": "dY - media(dY), retardo 0", "ar_AWB": {"200": {"l": l, "gamma": g}, "500": {"l": l5, "gamma": g5}},
                      "pvalue": "#{stat* <= stat} / B", "seed": "SeedSequence(113, spawn_key = (awb_<celda>, i))",
                      "sim_calibration": "B10.1, N_cal = %d" % E10.N_CAL},
           "exact_region_2000": region, "cells": res,
           "rule": {"i_in_region_dgp3": n_in, "i_of": len(dgp3), "i_min": B95.RULE_I_MIN,
                    "i_holds": bool(n_in >= B95.RULE_I_MIN),
                    "ii_power_loss_pp": {c: res[c]["power_loss_pp"] for c in dgp1}, "ii_threshold_pp": B95.RULE_II_PP,
                    "ii_holds": bool(loss_ok), "recommend_awb": bool(n_in >= B95.RULE_I_MIN and loss_ok)},
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print({c: (round(v["awb"]["rate"], 4), round(v["sim"]["rate"], 4)) for c, v in res.items()})
    print("regla", out["rule"])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--budget", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if final_theta() == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    if a.budget:
        return budget(a)
    if a.analyze:
        return analyze(a)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
