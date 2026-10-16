"""
Auditoria A9 - B9.1: potencia a tamano igualado sobre las trayectorias de B5 (A8).

Celdas (familia 95 de A8, N_sim = 5000): DGP 1 (21), DGP 2 (18) y potencia con
tendencia (12, B5.ct.3). Cada fila se recalcula con el motor de A9 (todas las
columnas); Paso 0: las primeras 50 filas frente a los checkpoints de B5 en las
columnas comunes (max |delta| = 0).

Reglas: tasa "asy" = la convencion de A8 (p-valor asintotico; MZt y MSB con los
valores de Ng-Perron; KPSS rechaza la estacionariedad); tasa "sim" = valor
critico simulado bajo la Ec. (3) al mismo n y caso, sobre los caminos de
produccion (audit9_calibrate.py, N_cal = 50000). RM, RM-GLS y MSB-HAC usan su
nula hac de produccion (la misma en las dos columnas). AWB: se arrastra de
b5_power_audit8.json sin recalcular. McNemar exacto de la primaria (RM-GLS,
theta = 0.1) frente a cada comparador en la version simulada.

Uso:
  python experiments/audit9_b91_equalized.py --run --cores 14
  python experiments/audit9_b91_equalized.py --analyze
"""
import argparse
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
import audit9_calibrate as CAL                                     # noqa: E402

FAM = C.FAMILY["B9.1"]
CKPT = os.path.join(C.CKPT_ROOT, "audit9_b91")
CKPT_A8 = os.path.join(C.CKPT_ROOT, "audit8_b5")
OUT = os.path.join(C.RESULTS, "b91_equalized_audit9.json")
PASO0 = 50
PRIMARY = "gls_t0.1"
E1_MIN_WIN, E1_MIN_SIG = 8, 6
E2_RHOS = (0.8, 0.85, 0.9, 0.93)
E2_MIN_SIG = 3
MCN_P = 0.05


def flags_for(name):
    if name.startswith("dgp1"):
        return {"cases": ("c",), "adfpp": True, "kpss": True}
    if name.startswith("dgp2"):
        return {"cases": ("c",), "adfpp": True, "za": True}
    if name.startswith("dgp3"):
        return {"cases": ("c",), "adfpp": True}
    return {"cases": ("ct",), "adfpp": True}


def cells():
    B5, all_cells = D.b5()
    names = [k for k in all_cells if k.startswith(("dgp1_", "dgp2_", "ct_power_"))]
    return {k: all_cells[k] for k in names}


PROCS = {"c": ("gls_t0.1", "rm_t0.1", "msbhac", "adf", "pp", "dfgls", "mzt", "msb"),
         "ct": ("gls_t0.1", "rm_t0.1", "msbhac", "adf", "pp", "dfgls", "mzt", "msb")}
ASY = ("adf", "pp", "dfgls", "mzt", "msb", "kpss", "za")
A8_COLS_DM = {"rm": "c|rm_t0.1", "rmgls": "c|gls_t0.1", "adf_p": "c|adf_p", "pp_p": "c|pp_p", "dfgls_p": "c|dfgls_p",
              "dfgls_k": "c|k", "mzt": "c|mzt", "msb": "c|msb", "kpss_p": "c|kpss_p", "za_p": "c|za_p"}
A8_COLS_CT = {"rm": "ct|rm_t0.1", "rmgls": "ct|gls_t0.1", "adf_stat": "ct|adf", "adf_p": "ct|adf_p", "pp_stat": "ct|pp",
              "pp_p": "ct|pp_p", "dfgls_stat": "ct|dfgls", "dfgls_p": "ct|dfgls_p", "mzt": "ct|mzt", "msb": "ct|msb"}


def run_cells(names, cores, t_block, max_seconds, resume, ckpt=CKPT):
    for name in names:
        spec = D.b5_spec(name)
        n = spec["n"]
        fl = flags_for(name)
        print("\n[CELDA] %s" % name, flush=True)
        C.run_cell(name, D.N_SIM, E.make_batch_fn(lambda i, nm=name: D.b5_path(nm, i), n, cores, **fl),
                   ckpt, cores, t_block, max_seconds, resume)


def run(a):
    resume = "python experiments/audit9_b91_equalized.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for n in D.N3:
            E.calibration(n, a.cores, CAL.CKPT, t_block, a.max_seconds, resume)
            print("[CAL] n=%d lista" % n, flush=True)
        run_cells(list(cells()), a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def paso0(name, rows, cols):
    import audit8_b5_power as B5
    ref = C.load_prefix(CKPT_A8, name, PASO0)
    J = E.index(cols)
    if name.startswith("ct_"):
        mapping, idx = A8_COLS_CT, B5.ICT
    else:
        mapping, idx = A8_COLS_DM, B5.IDM
    worst = {}
    for a8c, mine in mapping.items():
        if mine not in J:
            continue
        x, y = ref[:, idx[a8c]], rows[:PASO0, J[mine]]
        both_nan = np.isnan(x) & np.isnan(y)
        d = np.where(both_nan, 0.0, np.abs(x - y))
        worst[a8c] = float(np.nanmax(np.where(np.isnan(d), np.inf, d)))
    return {"reps": int(ref.shape[0]), "max_abs_diff_by_column": worst, "max_abs_diff": max(worst.values())}


def analyze_cells(names, rejectors, region, a8_power, extra_procs=()):
    out, rejs = {}, {}
    for name in names:
        spec = D.b5_spec(name)
        n = spec["n"]
        case = "ct" if name.startswith("ct_") else "c"
        rows, _ = C.load_rows(CKPT, name, D.N_SIM)
        cols = E.columns(**flags_for(name))
        rej, _ = rejectors[(n, case)]
        procs = list(PROCS[case]) + [p for p in extra_procs if p in E.RM_LIKE]
        if name.startswith("dgp1"):
            procs.append("kpss")
        if name.startswith("dgp2"):
            procs.append("za")
        sim = {p: rej(rows, cols, p) for p in procs}
        asy = {p: E.reject_asy(rows, cols, case, p) for p in procs if p in ASY}
        rec = {"n": n, "case": case, "rates_sim": {p: C.rate_record(v, region) for p, v in sim.items()},
               "rates_asy": {p: C.rate_record(v, region) for p, v in asy.items()},
               "mcnemar_primary_vs_sim": {p: C.mcnemar_exact(sim[PRIMARY], v) for p, v in sim.items() if p != PRIMARY},
               "nan": {c: int(np.isnan(rows[:, i]).sum()) for i, c in enumerate(cols)},
               "paso0": paso0(name, rows, cols)}
        for k in ("rho", "delta", "r"):
            if k in spec:
                rec[k] = spec[k]
        blk = "ct" if name.startswith("ct_") else name.split("_")[0]
        src = a8_power.get(blk, {}).get(name, {}) if blk != "ct" else a8_power["ct"]["power"].get(name, {})
        rec["a8_rates"] = {p: v["rate"] for p, v in src.get("rates", {}).items()}
        if "awb" in src.get("rates", {}):
            rec["awb_carried_from_a8"] = src["rates"]["awb"]
        out[name] = rec
        rejs[name] = sim
    return out, rejs


def rejectors_for(ns, cases):
    out, thr = {}, {}
    for n in ns:
        rows, cols = CAL.load(n)
        for case in cases:
            rej, qs = E.rejector(rows, cols, case)
            out[(n, case)] = (rej, qs)
            thr["%s|%d" % (case, n)] = qs
    return out, thr


def e_rules(res):
    ct = {k: v for k, v in res.items() if k.startswith("ct_power")}
    e1_cells = {}
    for k, v in ct.items():
        pr = v["rates_sim"][PRIMARY]["rate"]
        win = all(pr > v["rates_sim"][c]["rate"] for c in ("dfgls", "mzt"))
        sig = win and all(v["mcnemar_primary_vs_sim"][c]["p_value"] < MCN_P for c in ("dfgls", "mzt"))
        e1_cells[k] = {"wins_both": win, "wins_both_mcnemar": sig,
                       "primary": pr, "dfgls_sim": v["rates_sim"]["dfgls"]["rate"], "mzt_sim": v["rates_sim"]["mzt"]["rate"],
                       "p_dfgls": v["mcnemar_primary_vs_sim"]["dfgls"]["p_value"],
                       "p_mzt": v["mcnemar_primary_vs_sim"]["mzt"]["p_value"]}
    n_win = sum(c["wins_both"] for c in e1_cells.values())
    n_sig = sum(c["wins_both_mcnemar"] for c in e1_cells.values())
    e1 = {"cells": e1_cells, "wins": n_win, "wins_with_mcnemar": n_sig, "of": len(e1_cells),
          "thresholds": [E1_MIN_WIN, E1_MIN_SIG], "holds": bool(n_win >= E1_MIN_WIN and n_sig >= E1_MIN_SIG)}
    e2_cells = {}
    for rho in E2_RHOS:
        k = "dgp1_rho%s_n200" % ("%g" % rho).replace(".", "p")
        v = res[k]
        pr, dg = v["rates_sim"][PRIMARY]["rate"], v["rates_sim"]["dfgls"]["rate"]
        p = v["mcnemar_primary_vs_sim"]["dfgls"]["p_value"]
        e2_cells[k] = {"rho": rho, "primary": pr, "dfgls_sim": dg, "p": p, "wins": pr > dg, "wins_sig": pr > dg and p < MCN_P}
    wins = sum(c["wins"] for c in e2_cells.values())
    sig = sum(c["wins_sig"] for c in e2_cells.values())
    e2 = {"cells": e2_cells, "wins": wins, "wins_with_mcnemar": sig, "of": len(e2_cells),
          "holds": bool(wins == len(e2_cells) and sig >= E2_MIN_SIG),
          "holds_alternative_reading": bool(sig >= E2_MIN_SIG),
          "reading": "supera en las cuatro rho y con McNemar p < 0.05 (primaria mayor) en al menos 3 (protocolo, lectura 6)"}
    return e1, e2


def analyze(a):
    t0 = time.time()
    region = C.exact_region(D.N_SIM)
    rejectors, thr = rejectors_for(D.N3, ("c", "ct"))
    ctrl = {}
    for n in D.N3:
        rows, cols = CAL.load(n)
        ctrl[str(n)] = E.production_control(n, rows, cols)
        print("control de produccion n=%d %s" % (n, ctrl[str(n)]), flush=True)
    a8 = C.read_json("b5_power_audit8.json")
    res, _ = analyze_cells(list(cells()), rejectors, region, a8)
    e1, e2 = e_rules(res)
    worst_p0 = max(v["paso0"]["max_abs_diff"] for v in res.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"N_sim": D.N_SIM, "N_cal": E.N_CAL, "cal_seed": E.CAL_SEED, "primary": PRIMARY,
                      "trajectories": "B5 de A8 (familia 95), regeneradas con audit8_b5_power.path",
                      "rule_sim": "RM-like: p = F_null(stat) < 0.05 (nula hac de produccion); resto: stat < cuantil 5% bajo la Ec. (3)",
                      "rule_asy": "convencion de A8", "awb": "arrastrado de b5_power_audit8.json sin recalcular"},
           "exact_region_5000": region, "sim_thresholds": thr, "production_control": ctrl,
           "paso0_worst": worst_p0, "cells": res, "E1": e1, "E2": e2,
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("Paso 0 peor", worst_p0)
    print("E1", e1["wins"], e1["wins_with_mcnemar"], e1["holds"], "E2", e2["wins"], e2["wins_with_mcnemar"], e2["holds"])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        return analyze(a)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
