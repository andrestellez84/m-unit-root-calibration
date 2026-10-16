"""
Auditoria A13 - B13.E(2): AWB con theta = 0 sobre las trayectorias de B9.5 (tab:awb).

B10.3.4 (audit10_b103_awb) con theta = 0: mismas trayectorias de origen (las 2000
primeras de cada celda de B9.5), B = 399, AWB de bootUR 1.0.5 con sus valores por
defecto, residuos dY - media(dY), remuestreo SeedSequence(142, spawn_key =
(awb_<celda>, i)). Columna simulada: RM-GLS theta = 0 con la calibracion de A10
(N_cal = 500 000). Regla B9.5 recalculada (informativa).

Presupuesto (protocol_audit13.md, lectura 9): 8 h. Sonda de 14 series a n = 200 y
n = 500; proyeccion = s/serie x 2000 x celdas de ese n; si supera 8 h no se lanza.
En la corrida, tope de 8 h con checkpoint por lote (se detiene y reporta).
Paso 0: el estadistico observado de cada serie coincide con la fila de B9.1/B9.2
(max |Delta| = 0).

Modos: --budget, --run, --analyze.
Salidas: e_awb_budget_audit13.json, e_awb_audit13.json.
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

import audit13_common as C                                         # noqa: E402
import audit13_design as D                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b95_awb as B95                                       # noqa: E402

FAM = C.FAMILY["AWB"]
CKPT = os.path.join(C.CKPT_ROOT, "audit13_awb")
OUT = os.path.join(C.RESULTS, "e_awb_audit13.json")
OUT_BUDGET = os.path.join(C.RESULTS, "e_awb_budget_audit13.json")
BUDGET_HOURS = 8.0


def awb_rows(cell, src, idx):
    n = B95.cell_n(cell)
    out = []
    for i in idx:
        y = D9.awb_source_path(cell, src, i)
        p, s = E.awb_pvalue(y, n, C.THETA, "c", D9.B_AWB, D.awb_rng(cell, i))
        out.append([p, s])
    return out


def batch_fn(cell, src, cores):
    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(awb_rows)(cell, src, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def budget(a):
    E.warm(a.cores)
    t_block = time.time()
    sps = {}
    for n, cell in B95.PROBE_CELLS.items():
        src = dict(D9.AWB_CELLS)[cell]
        _, info = C.C8.C7.run_cell_batched(cell, D9.N_AWB, batch_fn(cell, src, a.cores), CKPT, a.cores, t_block,
                                           1e12, "", log=lambda *x: None, probe_only=True)
        sps[n] = info["probe_sec_per_series"]
    counts = {n: sum(1 for c, _ in D9.AWB_CELLS if B95.cell_n(c) == n) for n in B95.PROBE_CELLS}
    proj = sum(sps[n] * D9.N_AWB * counts[n] for n in B95.PROBE_CELLS)
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "budget_hours": BUDGET_HOURS, "theta": C.THETA,
           "probe_sec_per_series": {str(k): v for k, v in sps.items()}, "cells_per_n": {str(k): v for k, v in counts.items()},
           "projected_total_hours": proj / 3600, "within_budget": bool(proj / 3600 <= BUDGET_HOURS),
           "rule": "sonda de 14 series a n = 200 y n = 500; proyeccion = sonda x 2000 x celdas de ese n; "
                   "no se lanza si supera el presupuesto"}
    C.write_result(OUT_BUDGET, out, __file__)
    print("AWB theta = 0: proyeccion %.2f h: %s" % (proj / 3600, out["within_budget"]))
    return 0 if out["within_budget"] else 3


def run(a):
    if not C.read_json(os.path.basename(OUT_BUDGET))["within_budget"]:
        print("presupuesto excedido: no se lanza")
        return 3
    resume = "python experiments/audit13_e_awb.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for cell, src in D9.AWB_CELLS:
            print("\n[CELDA] %s" % cell, flush=True)
            C.run_cell(cell, D9.N_AWB, batch_fn(cell, src, a.cores), CKPT, a.cores, t_block, BUDGET_HOURS * 3600, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def analyze(a):
    t0 = time.time()
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
        r_sim = rej[n](srows, scols, C.PRIM)
        r_v13 = rej[n](srows, scols, C.PRIM_V13)
        r_awb = p < C.ALPHA
        res[cell] = {"n": n, "source": src, "awb": C.rate_record(r_awb, region), "sim": C.rate_record(r_sim, region),
                     "sim_v13": C.rate_record(r_v13, region),
                     "mcnemar_awb_vs_sim": C.mcnemar_exact(r_awb, r_sim),
                     "power_loss_pp": (r_sim.mean() - r_awb.mean()) * C.PP,
                     "max_abs_diff_stat_vs_rows": float(np.max(np.abs(rows[:, 1] - srows[:, E.index(scols)["c|%s" % C.PRIM]])))}
    dgp3 = [c for c in res if c.startswith("dgp3_")]
    dgp1 = [c for c in res if c.startswith("dgp1_")]
    n_in = sum(res[c]["awb"]["in_region"] for c in dgp3)
    loss_ok = all(res[c]["power_loss_pp"] <= B95.RULE_II_PP for c in dgp1)
    g, l = E.awb_gamma(200)
    g5, l5 = E.awb_gamma(500)
    ref = C.read_json("b103_awb_audit10.json")
    v13_sim = max(abs(res[c]["sim_v13"]["rate"] - ref["cells"][c]["sim"]["rate"]) for c in res)
    p0 = max(v["max_abs_diff_stat_vs_rows"] for v in res.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": C.THETA, "statistic": C.PRIM, "B": D9.B_AWB, "N_sim": D9.N_AWB,
                      "residuals": "dY - media(dY), retardo 0", "ar_AWB": {"200": {"l": l, "gamma": g}, "500": {"l": l5, "gamma": g5}},
                      "pvalue": "#{stat* <= stat} / B", "seed": "SeedSequence(142, spawn_key = (awb_<celda>, i))",
                      "sim_calibration": "A10, N_cal = %d" % E10.N_CAL, "reading": "protocol_audit13.md, lectura 9"},
           "exact_region_2000": region, "cells": res,
           "paso0": {"stat_vs_rows_max_abs_diff": p0, "sim_v13_vs_b103_awb_max_abs_diff": v13_sim,
                     "passes": p0 == 0 and v13_sim == 0},
           "rule": {"i_in_region_dgp3": n_in, "i_of": len(dgp3), "i_min": B95.RULE_I_MIN,
                    "i_holds": bool(n_in >= B95.RULE_I_MIN),
                    "ii_power_loss_pp": {c: res[c]["power_loss_pp"] for c in dgp1}, "ii_threshold_pp": B95.RULE_II_PP,
                    "ii_holds": bool(loss_ok), "recommend_awb": bool(n_in >= B95.RULE_I_MIN and loss_ok)},
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print({c: (round(v["awb"]["rate"], 4), round(v["sim"]["rate"], 4)) for c, v in res.items()})
    print("regla", out["rule"], "Paso 0", out["paso0"])
    return 0 if out["paso0"]["passes"] else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--budget", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.budget:
        return budget(a)
    if a.analyze:
        return analyze(a)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
