"""
Auditoria A9 - B9.5: calibracion por bootstrap salvaje autorregresivo del propio estadistico (CARO, 8 h).

Estadistico: la primaria de B9.2 (RM-GLS con el theta elegido, caso demeaned).
Remuestreo (protocolo, lectura 13): AWB de bootUR 1.0.5 con sus valores por
defecto, B = 399, residuos bajo la nula con intercepto y retardo 0; el estadistico
se recalcula por completo en cada remuestra; semilla de cada serie
SeedSequence(105, spawn_key = (celda, i)). N_sim = 2000: las primeras 2000
trayectorias de cada celda de origen.

Celdas: DGP 3 r in {1, 2, 4} x n in {200, 500} (B5 de A8); GARCH de n = 200 (A7);
DGP 1 rho in {0.95, 0.99} x n in {200, 500} (B5 de A8); nula gaussiana n = 200 y
500 (independientes de B9.2).

Presupuesto: sonda de 14 series a n = 200 y a n = 500, extrapolacion al total y
detencion si excede 8 h.
Regla (INFORMATIVA): protocol_audit9.md, REGLA B9.5.

Modos: --budget, --run, --analyze.
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

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402

FAM = C.FAMILY["B9.5"]
CKPT = os.path.join(C.CKPT_ROOT, "audit9_b95")
OUT = os.path.join(C.RESULTS, "b95_awb_audit9.json")
OUT_BUDGET = os.path.join(C.RESULTS, "b95_budget_audit9.json")
BUDGET_HOURS = 8.0
PROBE_CELLS = {200: "indep_n200", 500: "indep_n500"}
RULE_I_MIN = 4
RULE_II_PP = 3.0


def primary_theta():
    return C.read_json("b92_theta_audit9.json")["primary_theta"]


def cell_n(cell):
    return int(cell.rsplit("_n", 1)[1])


def awb_rows(cell, src, idx, theta):
    n = cell_n(cell)
    out = []
    for i in idx:
        y = D.awb_source_path(cell, src, i)
        p, s = E.awb_pvalue(y, n, theta, "c", D.B_AWB, D.awb_rng(cell, i))
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
    theta = primary_theta()
    E.warm(a.cores)
    t_block = time.time()
    sps = {}
    for n, cell in PROBE_CELLS.items():
        src = dict(D.AWB_CELLS)[cell]
        _, info = C.C8.C7.run_cell_batched(cell, D.N_AWB, batch_fn(cell, src, theta, a.cores), CKPT, a.cores, t_block,
                                           1e12, "", log=lambda *x: None, probe_only=True)
        sps[n] = info["probe_sec_per_series"]
    counts = {n: sum(1 for c, _ in D.AWB_CELLS if cell_n(c) == n) for n in PROBE_CELLS}
    proj = sum(sps[n] * D.N_AWB * counts[n] for n in PROBE_CELLS)
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "budget_hours": BUDGET_HOURS, "theta": theta,
           "probe_sec_per_series": {str(k): v for k, v in sps.items()}, "cells_per_n": {str(k): v for k, v in counts.items()},
           "projected_total_hours": proj / 3600, "within_budget": bool(proj / 3600 <= BUDGET_HOURS),
           "rule": "sonda de 14 series a n = 200 y n = 500; proyeccion = sonda x 2000 x celdas de ese n"}
    C.write_result(OUT_BUDGET, out, __file__)
    print("B9.5 proyeccion %.2f h: %s" % (proj / 3600, out["within_budget"]))
    return 0 if out["within_budget"] else 3


def run(a):
    if not C.read_json(os.path.basename(OUT_BUDGET))["within_budget"]:
        print("presupuesto excedido: no se lanza B9.5")
        return 3
    theta = primary_theta()
    resume = "python experiments/audit9_b95_awb.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for cell, src in D.AWB_CELLS:
            print("\n[CELDA] %s" % cell, flush=True)
            C.run_cell(cell, D.N_AWB, batch_fn(cell, src, theta, a.cores), CKPT, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    return 0


def sim_rows(cell, src):
    """Filas de la calibracion simulada de la primaria sobre las mismas trayectorias (B9.1 / B9.2)."""
    if cell.startswith("dgp1_"):
        return C.load_rows(B91.CKPT, cell, D.N_SIM)[0][:D.N_AWB], E.columns(**B91.flags_for(cell))
    if cell.startswith("dgp3_"):
        return C.load_rows(B92.CKPT, cell, D.N_SIM)[0][:D.N_AWB], E.columns(**B91.flags_for(cell))
    reps = D.N_INDEP if src == "indep" else D.N_SIM
    return C.load_rows(B92.CKPT, cell, reps)[0][:D.N_AWB], E.columns(**B92.SIZE_FLAGS)


def analyze(a):
    t0 = time.time()
    theta = primary_theta()
    prim = E.tname(theta)
    region = C.exact_region(D.N_AWB)
    rejectors, _ = B91.rejectors_for((200, 500), ("c",))
    res = {}
    for cell, src in D.AWB_CELLS:
        n = cell_n(cell)
        rows, _ = C.load_rows(CKPT, cell, D.N_AWB)
        p = rows[:, 0]
        srows, scols = sim_rows(cell, src)
        r_sim = rejectors[(n, "c")][0](srows, scols, prim)
        r_awb = p < C.ALPHA
        stat_diff = float(np.max(np.abs(rows[:, 1] - srows[:, E.index(scols)["c|%s" % prim]])))
        res[cell] = {"n": n, "source": src, "awb": C.rate_record(r_awb, region), "sim": C.rate_record(r_sim, region),
                     "mcnemar_awb_vs_sim": C.mcnemar_exact(r_awb, r_sim),
                     "power_loss_pp": (r_sim.mean() - r_awb.mean()) * 100,
                     "max_abs_diff_stat_vs_rows": stat_diff}
    dgp3 = [c for c in res if c.startswith("dgp3_")]
    dgp1 = [c for c in res if c.startswith("dgp1_")]
    n_in = sum(res[c]["awb"]["in_region"] for c in dgp3)
    loss_ok = all(res[c]["power_loss_pp"] <= RULE_II_PP for c in dgp1)
    g, l = E.awb_gamma(200)
    g5, l5 = E.awb_gamma(500)
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"theta": theta, "statistic": prim, "B": D.B_AWB, "N_sim": D.N_AWB, "residuals": "dY - media(dY), retardo 0",
                      "ar_AWB": {"200": {"l": l, "gamma": g}, "500": {"l": l5, "gamma": g5}},
                      "bootUR_default": "block_length = round(1.75 T^(1/3)), ar_AWB = 0.01^(1/block_length) (check_inputs, bootUR 1.0.5)",
                      "pvalue": "#{stat* <= stat} / B", "seed": "SeedSequence(105, spawn_key = (celda, i))"},
           "exact_region_2000": region, "cells": res,
           "rule": {"i_in_region_dgp3": n_in, "i_of": len(dgp3), "i_min": RULE_I_MIN, "i_holds": bool(n_in >= RULE_I_MIN),
                    "ii_power_loss_pp": {c: res[c]["power_loss_pp"] for c in dgp1}, "ii_threshold_pp": RULE_II_PP,
                    "ii_holds": bool(loss_ok), "recommend_awb": bool(n_in >= RULE_I_MIN and loss_ok)},
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print({c: (round(v["awb"]["rate"], 4), round(v["sim"]["rate"], 4)) for c, v in res.items()})
    print("regla", out["rule"])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
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
