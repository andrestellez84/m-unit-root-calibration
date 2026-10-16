"""
Auditoria A15 - B15.1: bootstrap de MZ_t-GLS bajo correlacion serial (protocol_audit15.md, 1.1-1.11;
enmiendas 1-3; prediccion 14cbca7). Autorizado por la enmienda 3 (E3.4) si pasan E3.1-E3.2.

Brazos sobre los mismos caminos: (i) asintotico NP2001; (ii) valor iid de b1_critical_audit14.json;
(iii) «SB (bootUR)»; (iv) AWB de def:awb; (v') «SWB (bootUR)» (solo si su Paso 0 paso). R replicas,
p = (1 + #{T* <= T})/(R + 1); rechazo con p <= 0.05. Tamano: celdas de A12 (familia 152);
potencia: n = 200, c y ct, rho in {0.90, 0.95}, errores iid y MA(-0.5) (familia 153). Potencia
ajustada: umbral = cuantil 5 % del p-valor (o de MZ_t-GLS para (i) y (ii)) en la celda nula del
mismo error, n = 200 y caso. Desenlace segun 14cbca7.
Configuracion (R, celdas, brazos) desde probes_audit15.json (chosen_configuration).

Salida: experiments/results/b1_boot_audit15.json.
"""
import argparse
import math
import os
import sys
import time
from functools import partial

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_design as D                                         # noqa: E402
import audit15_boot_engine as BE                                   # noqa: E402
import audit12_runner as R12                                       # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit9_engine as E9                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_boot_audit15.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit15_b1")
FS, FP = C.FAMILY["SIZE1"], C.FAMILY["POWER1"]
DC = {"c": 1, "ct": 2}
COLS = ["mzt", "k", "p_iii", "p_iv", "p_v_prime"]
BOOT_ARMS = ("iii", "iv", "v_prime")
ARM_LABEL = {"i": "(i) asintotico NP2001", "ii": "(ii) iid A14", "iii": "(iii) SB (bootUR)", "iv": "(iv) AWB",
             "v_prime": "(v') SWB (bootUR)"}
RED_ERR = ("ma_m0p8", "ma_0p5", "ar_0p5")
D_MARGIN = 0.005                 # prediccion 14cbca7: D <= D(ii) - 0.005
M_MARGIN = 0.010                 # M <= M(ii) - 0.010
COST_PP = 1.0                    # potencia ajustada >= (ii) - 1.0 pp


def arm_rng(fam, cell, i, a):
    return np.random.default_rng(np.random.SeedSequence(fam, spawn_key=(cell, i, a)))


def row(fam, cell, err, n, case, rho, R, arms, i):
    rng = C.rep_rng(fam, cell, i)
    y = P12.null_path(err, n, rng) if rho is None else P12.alt_path(err, n, rho, rng)
    T = len(y)
    ct = case == "ct"
    cbar = BE.CBAR_NP[case]
    kmax = U.kmax_rule(T)
    pmax = BE.kmax_rule(T)
    dc = DC[case]
    cqd = BE.CQD_BOOTUR[dc - 1]
    mzt, _, k = BE.mzt_gls(y, ct, cbar, kmax)
    out = [mzt, float(k), float("nan"), float("nan"), float("nan")]
    if "iii" in arms:
        g = arm_rng(fam, cell, i, D.ARMS["iii"])
        l = BE.bootur_block_length(T)
        out[2] = BE.pvalue_sb(y, ct, cbar, kmax, pmax, dc, cqd, g.integers(0, T - l + 1, size=(R, T)))[0]
    if "iv" in arms:
        g = arm_rng(fam, cell, i, D.ARMS["iv"])
        gam, _ = E9.awb_gamma(T - 1)
        out[3] = BE.pvalue_awb(y, ct, cbar, kmax, gam, g.standard_normal((R, T - 1)))[0]
    if "v_prime" in arms:
        g = arm_rng(fam, cell, i, D.ARMS["v_prime"])
        out[4] = BE.pvalue_swb(y, ct, cbar, kmax, pmax, dc, cqd, g.standard_normal((R, T)))[0]
    return out


def design(chosen):
    reduced = chosen in ("red2_R199_18cells", "red3_R199_18cells_no_iv")
    size = []
    for e in P12.ERRORS:
        for n in D.A_N:
            for c in D.CASES:
                name = D.size_cell(e, n, c)
                tag = P12.err_tag(e)
                keep = (not reduced) or tag in RED_ERR or (n == D.POW1_N and e in D.POW1_ERR)
                if keep:
                    size.append((name, e, n, c))
    power = [(D.pow1_cell(e, r, c), e, r, c) for e in D.POW1_ERR for r in D.POW1_RHO for c in D.CASES]
    return size, power


def settings(probe, gate_v):
    chosen = probe["b15_1"]["chosen_configuration"]
    R = D.R if chosen == "full" else 199
    arms = [a for a in BOOT_ARMS if (a != "v_prime" or gate_v) and not (chosen == "red3_R199_18cells_no_iv" and a == "iv")]
    return chosen, R, arms


def run(cores, t_block, max_seconds, chosen, R, arms):
    size, power = design(chosen)
    for name, e, n, c in size:
        R12.run_cell("sz1_" + name, D.N_SIZE1, partial(row, FS, D.cell_index(FS, name), e, n, c, None, R, tuple(arms)), len(COLS), CKPT,
                     cores, t_block, max_seconds, "python experiments/audit15_b1_boot.py", per_core=25)
    for name, e, r, c in power:
        R12.run_cell(name, D.N_POW1, partial(row, FP, D.cell_index(FP, name), e, D.POW1_N, c, r, R, tuple(arms)), len(COLS), CKPT,
                     cores, t_block, max_seconds, "python experiments/audit15_b1_boot.py", per_core=25)
    return size, power


def decisions(rows, n, case, arms, q_iid):
    mzt = np.nan_to_num(rows[:, 0], nan=np.inf)
    dec = {"i": mzt < U.NP_CV5[case]["MZt"], "ii": mzt < q_iid[(n, case)]}
    for a in arms:
        dec[a] = rows[:, COLS.index("p_" + a)] <= C.ALPHA
    return dec


def analyze(size, power, arms, R, chosen):
    q14 = C.read_json("b1_critical_audit14.json")["values"]
    q_iid = {(v["n"], v["case"]): v["critical_value"] for v in q14 if v["stat"] == "mzt" and v["alpha"] == C.ALPHA}
    all_arms = ["i", "ii"] + list(arms)
    region = C.exact_region(D.N_SIZE1)
    cells, raw = {}, {}
    for name, e, n, c in size:
        rows, el = R12.load_cell(CKPT, "sz1_" + name, D.N_SIZE1)
        raw[name] = rows
        dec = decisions(rows, n, c, arms, q_iid)
        cells[name] = {"err_tag": P12.err_tag(e), "n": n, "case": c,
                       "rates": {a: C.C14.C13.rate_record(dec[a], region) for a in all_arms}, "elapsed_sec": el}
    nz = [k for k, v in cells.items() if v["err_tag"] != "ma_0"]
    iid = [k for k, v in cells.items() if v["err_tag"] == "ma_0"]
    summ = {}
    for a in all_arms:
        dev = {k: abs(cells[k]["rates"][a]["rate"] - C.ALPHA) for k in nz}
        summ[a] = {"D": float(np.mean(list(dev.values()))), "M": float(max(dev.values())), "argmax": max(dev, key=dev.get),
                   "cells": len(nz), "iid_in_region": sum(1 for k in iid if cells[k]["rates"][a]["in_region"]), "iid_cells": len(iid)}
    pw = {}
    for name, e, r, c in power:
        rows, el = R12.load_cell(CKPT, name, D.N_POW1)
        null = D.size_cell(e, D.POW1_N, c)
        nrows = raw[null]
        dec_raw = decisions(rows, D.POW1_N, c, arms, q_iid)
        adj = {}
        thr = {}
        for a in ["i", "ii"]:
            thr[a] = float(np.quantile(np.nan_to_num(nrows[:, 0], nan=np.inf), C.ALPHA))
            adj[a] = np.nan_to_num(rows[:, 0], nan=np.inf) <= thr[a]
        for a in arms:
            j = COLS.index("p_" + a)
            thr[a] = float(np.quantile(nrows[:, j], C.ALPHA))
            adj[a] = rows[:, j] <= thr[a]
        rec = {"err_tag": P12.err_tag(e), "rho": r, "case": c, "null_cell": null, "thresholds": thr,
               "raw": {a: C.C14.C13.rate_record(dec_raw[a]) for a in all_arms},
               "adjusted": {a: C.C14.C13.rate_record(adj[a]) for a in all_arms}, "vs_ii": {}}
        for a in arms:
            mc = C.mcnemar_exact(adj[a], adj["ii"])
            dpp = (float(adj[a].mean()) - float(adj["ii"].mean())) * C.PP
            rec["vs_ii"][a] = {"diff_pp": dpp, "mcnemar": mc, "no_cost": dpp >= -COST_PP or mc["p_value"] >= C.ALPHA}
        pw[name] = rec
    pred = {}
    for a in arms:
        dom = (summ[a]["D"] <= summ["ii"]["D"] - D_MARGIN and summ[a]["M"] <= summ["ii"]["M"] - M_MARGIN
               and summ[a]["iid_in_region"] == summ[a]["iid_cells"])
        nocost = all(v["vs_ii"][a]["no_cost"] for v in pw.values())
        pred[a] = {"dominates_size": dom, "no_cost": nocost, "outcome": ("A" if nocost else "C") if dom else "B",
                   "D": summ[a]["D"], "M": summ[a]["M"], "D_ii": summ["ii"]["D"], "M_ii": summ["ii"]["M"]}
    evaluated = [a for a in ("iii", "v_prime") if a in arms]
    outs = [pred[a]["outcome"] for a in evaluated]
    overall = "A" if "A" in outs else ("C" if "C" in outs else "B")
    return {"size": cells, "size_summary": summ, "power": pw, "prediction": {"by_arm": pred, "evaluated_arms": evaluated,
                                                                              "overall": overall, "order": "A > C > B"},
            "exact_region": region}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=min(os.cpu_count() or 1, 16))
    ap.add_argument("--max-hours", type=float, default=48)
    a = ap.parse_args()
    probe = C.read_json("probes_audit15.json")
    gate = C.read_json("b1_paso0_v2_audit15.json")["gate"]
    if not gate["iii_SB_bootUR"] or not probe["b15_1"].get("executed") or not probe["b15_1"]["chosen_configuration"]:
        print("B15.1 no autorizado (enmienda 3, E3.4)")
        return 4
    chosen, R, arms = settings(probe, gate["v_prime_SWB_bootUR"])
    if chosen != "full":
        print("configuracion reducida %s: requiere informar al autor antes de lanzar (E3.4)" % chosen)
        return 5
    t0 = time.time()
    R12.warm(a.cores)
    size, power = run(a.cores, t0, a.max_hours * 3600, chosen, R, arms)
    res = analyze(size, power, arms, R, chosen)
    out = {"provenance": C.provenance(__file__, seed_family=[FS, FP]),
           "reading": "protocol_audit15.md, 1.1-1.11; enmiendas 1-3; prediccion 14cbca7",
           "config": {"chosen_configuration": chosen, "R": R, "boot_arms": arms, "arm_labels": ARM_LABEL, "N_size": D.N_SIZE1,
                      "N_power": D.N_POW1, "pvalue": "(1 + #{T* <= T})/(R + 1); rechazo p <= 0.05",
                      "v_prime_excluded": "v_prime" not in arms, "cores": a.cores},
           **res, "elapsed_sec": time.time() - t0}
    C.write_result(OUT, out, __file__)
    for k, v in res["size_summary"].items():
        print("%-8s D = %.4f  M = %.4f (%s)  iid en region %d/%d" % (k, v["D"], v["M"], v["argmax"], v["iid_in_region"], v["iid_cells"]))
    print("prediccion:", {k: v["outcome"] for k, v in res["prediction"]["by_arm"].items()}, "global", res["prediction"]["overall"])
    print("%.0f s" % out["elapsed_sec"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
