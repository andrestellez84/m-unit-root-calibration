"""
Auditoria A8 - B3: comparadores de tamano que faltan (CARO; presupuesto 30 h).

Los estadisticos sin bootstrap (MZt-GLS y MSB-GLS asy/sim, MSB-HAC hac, RM hac
con theta in {0.02, 0.05, 0.2}, RM-GLS hac) se calcularon en la pasada de B2
sobre las mismas trayectorias; aqui se analizan. Este script anade el bootstrap
AWB de DF-GLS (bootUR::boot_adf, AWB, QD, intercepto, lag 0, B = 399).

Alcance (enmienda 2): solo n <= 1000. Primeras 2000 trayectorias de las 18
celdas mal especificadas con n <= 1000 y de las gaussianas independientes de la
familia 92 (indep_gauss_n200/500/1000), mas 5000 trayectorias gaussianas nuevas a
n = 200 (familia 93). Semilla de remuestreo por serie derivada de
SeedSequence(93, (celda, i, 1)). La referencia gaussiana de las tasas y de los
Delta de todos los procedimientos es la independiente de la familia 92
(N = 20000; para AWB, sus primeras 2000).

Modos:
  --budget   regla de presupuesto: una celda completa (gaussiana n = 1000,
             2000 series) y una sonda de 14 series por cada otro n; extrapola el
             coste total y lo escribe en b3_budget_audit8.json y en el log. Si
             supera 30 h, el bloque no se lanza.
  --run      bootstrap de todas las celdas (checkpoint por lote; tope por bloque).
  --analyze  tablas, Delta pareado, D1-D3 y entrada G3 de B4. Con
             --no-bootstrap analiza solo las columnas sin bootstrap.

Salidas: b3_budget_audit8.json, b3_comparators_audit8.json.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
from audit6_wild_bootstrap_sweep import find_rscript               # noqa: E402

FAM = C.FAMILY["B3"]
CKPT = os.path.join(C.CKPT_ROOT, "audit8_b3")
OUT = os.path.join(C.RESULTS, "b3_comparators_audit8.json")
OUT_BUDGET = os.path.join(C.RESULTS, "b3_budget_audit8.json")
WORKER = os.path.join(HERE, "audit8_bootstrap_worker.R")
B_BOOT = 399
BUDGET_HOURS = 30.0
BUDGET_FULL_CELL = "indep_gauss_n1000"
EXTRA = "boot_gauss_n200_N5000"
GATE_PP = 0.30
SE_MULT = 2.0
D_N = (200, 500)


def boot_cells():
    cells = D.size_cells()
    out = [(k, s, D.N_SIM_BOOT) for k, s in cells.items() if s["kind"] != "gauss" and s["n"] <= D.N_BOOT_MAX]
    out += [(k, s, D.N_SIM_BOOT) for k, s in D.indep_cells().items() if 200 <= s["n"] <= D.N_BOOT_MAX]
    out.append((EXTRA, {"kind": "gauss_new93", "n": 200, "reused": False, "source": "familia 93"}, D.N_SIM))
    return out


def rseed_cell(name):
    return D.cell_index(FAM, "rseed_" + name)


def path(name, spec, i):
    if name == EXTRA:
        return D.new_gauss(FAM, EXTRA, 200, i)
    return D.size_path(name, spec, i)


def run_boot(name, spec, indices, cores):
    n = spec["n"]
    mat = np.column_stack([path(name, spec, i) for i in indices])
    seeds = np.array([C.r_seed(FAM, rseed_cell(name), i) for i in indices], dtype=np.int32)
    os.makedirs(CKPT, exist_ok=True)
    stem = os.path.join(CKPT, "_tmp_%s_i%06d" % (name, indices[0]))
    binp, seedp, outj = stem + ".bin", stem + ".seeds", stem + ".json"
    mat.T.astype(np.float64).tofile(binp)
    seeds.tofile(seedp)
    exp5 = ",".join("%.6f" % v for v in mat[:5, 0])
    try:
        r = subprocess.run([find_rscript(), WORKER, binp, str(n), str(len(indices)), str(B_BOOT), str(cores),
                            outj, exp5, seedp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("worker de R fallo:\n%s" % (r.stdout + r.stderr)[-3000:])
        with open(outj, encoding="utf-8") as f:
            d = json.load(f)
    finally:
        for p in (binp, seedp, outj):
            if os.path.exists(p):
                os.remove(p)
    return [[float("nan") if v is None else float(v)] for v in d["p_adf"]]


def batch_fn_for(name, spec, cores):
    return lambda indices: run_boot(name, spec, indices, cores)


def budget(a):
    resume = "python experiments/audit8_b3_comparators.py --budget --cores %d" % a.cores
    t_block = time.time()
    cells = {k: (s, N) for k, s, N in boot_cells()}
    s, N = cells[BUDGET_FULL_CELL]
    print("[PRESUPUESTO] celda completa %s (%d series)" % (BUDGET_FULL_CELL, N), flush=True)
    rows, info = C.run_cell("boot_" + BUDGET_FULL_CELL, N, batch_fn_for(BUDGET_FULL_CELL, s, a.cores), CKPT,
                            a.cores, t_block, a.max_seconds, resume)
    sps = {s["n"]: info["elapsed_sec"] / N}
    measured = {str(s["n"]): {"cell": BUDGET_FULL_CELL, "series": N, "elapsed_sec": info["elapsed_sec"],
                              "sec_per_series": sps[s["n"]], "kind": "celda completa"}}
    for n in sorted({sp["n"] for sp, _ in cells.values()} - {s["n"]}):
        name = "indep_gauss_n%d" % n
        sp, NN = cells[name]
        print("[PRESUPUESTO] sonda %s" % name, flush=True)
        _, pinfo = C.C7.run_cell_batched("boot_" + name, NN, batch_fn_for(name, sp, a.cores), CKPT, a.cores,
                                         t_block, a.max_seconds, resume, probe_only=True)
        sps[n] = pinfo["probe_sec_per_series"]
        measured[str(n)] = {"cell": name, "series": C.C7.PROBE_SERIES, "sec_per_series": sps[n], "kind": "sonda"}
    per_cell = {k: {"n": sp["n"], "series": NN, "projected_sec": NN * sps[sp["n"]]} for k, (sp, NN) in cells.items()}
    total = sum(v["projected_sec"] for v in per_cell.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "B": B_BOOT, "cores": a.cores,
           "budget_hours": BUDGET_HOURS, "measured": measured, "per_cell": per_cell,
           "projected_total_hours": total / 3600, "within_budget": total / 3600 <= BUDGET_HOURS,
           "rule": "una celda completa (la gaussiana de n = 1000, la mayor que cabe en un bloque de 4 h) y sondas de "
                   "14 series en los demas n; coste de cada celda = series x segundos por serie medidos a su n"}
    C.write_result(OUT_BUDGET, out, __file__)
    print("[PRESUPUESTO] proyeccion total %.1f h frente a %.0f h -> %s" % (
        total / 3600, BUDGET_HOURS, "dentro" if out["within_budget"] else "EXCEDE: no se lanza"), flush=True)
    for n, m in sorted(measured.items(), key=lambda kv: int(kv[0])):
        print("  n=%s  %.3f s/serie (%s)" % (n, m["sec_per_series"], m["kind"]), flush=True)
    return 0 if out["within_budget"] else 5


def run(a):
    bud = C.read_json(os.path.basename(OUT_BUDGET))
    if not bud["within_budget"]:
        print("presupuesto excedido: no se lanza")
        return 5
    resume = "python experiments/audit8_b3_comparators.py --run --cores %d --max-seconds %.0f" % (a.cores, a.max_seconds)
    t_block = time.time()
    for name, spec, N in sorted(boot_cells(), key=lambda x: (x[1]["n"], x[0])):
        print("\n[CELDA] boot_%s" % name, flush=True)
        try:
            C.run_cell("boot_" + name, N, batch_fn_for(name, spec, a.cores), CKPT, a.cores, t_block,
                       a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def load_rows_b3(tag, N):
    saved = B2.CKPT
    try:
        B2.CKPT = CKPT
        return B2.load_rows(tag, N)
    finally:
        B2.CKPT = saved


def paired_se(a_m, b_m, a_g, b_g):
    """EE de (Delta_A - Delta_B) con A, B pareados dentro de cada celda y celdas independientes."""
    def v(a, b):
        d = a.astype(float) - b.astype(float)
        return d.var(ddof=0) / len(d)
    return math.sqrt(v(a_m, b_m) + v(a_g, b_g))


def analyze(a):
    import audit8_b2b_indep as BI
    t0 = time.time()
    cells, indep, rej, _ = BI.load_rejections()
    region5, region2, region20 = C.exact_region(D.N_SIM), C.exact_region(D.N_SIM_BOOT), C.exact_region(D.N_INDEP)
    boot, boot_elapsed = {}, {}
    if not a.no_bootstrap:
        for name, spec, N in boot_cells():
            p, el = load_rows_b3("boot_" + name, N)
            boot[name] = {"p": p[:, 0], "nan": int(np.isnan(p[:, 0]).sum())}
            boot_elapsed[name] = el
            if name in rej:
                rej[name]["awb"] = np.nan_to_num(p[:, 0], nan=1.0) < C.ALPHA
    procs = ["rm_R0_t0.1_hac", "adf_sim", "dfgls_asy", "dfgls_sim", "mzt_asy", "mzt_sim", "msb_asy", "msb_sim",
             "rm_msbhac_hac", "rm_R0_t0.02_hac", "rm_R0_t0.05_hac", "rm_R0_t0.2_hac", "rm_rmgls_hac"]
    misspec = [k for k, s in cells.items() if s["kind"] != "gauss"]
    garch = [k for k, s in cells.items() if s["kind"] == "garch"]
    gauss_by_n = {s["n"]: k for k, s in indep.items()}

    def mask(k, p):
        m = rej[k][p]
        return m[:D.N_SIM_BOOT] if p == "awb" else m

    def region_for(k, p):
        if p == "awb":
            return region2
        return region20 if k in indep else region5

    def has(k, p):
        return p != "awb" or "awb" in rej[k]

    all_procs = procs + (["awb"] if boot else [])
    rate_cells = misspec + [gauss_by_n[n] for n in D.N_MAIN]
    rates = {k: {p: C.rate_record(mask(k, p), region_for(k, p)) for p in all_procs if has(k, p)} for k in rate_cells}
    deltas = {k: {p: C.diff_independent(rates[k][p], rates[gauss_by_n[cells[k]["n"]]][p])
                  for p in all_procs if p in rates[k]} for k in misspec}
    ns = sorted({cells[k]["n"] for k in misspec})
    by_n = {}
    for n in ns:
        ks = [k for k in misspec if cells[k]["n"] == n]
        by_n[str(n)] = {p: C.mean_with_se([deltas[k][p] for k in ks]) for p in all_procs if all(p in deltas[k] for k in ks)}
    in_region = {p: {"garch": sum(rates[k][p]["in_region"] for k in garch if p in rates[k]),
                     "garch_cells": sum(1 for k in garch if p in rates[k]),
                     "heavy": sum(rates[k][p]["in_region"] for k in misspec if cells[k]["kind"] == "heavy" and p in rates[k])}
                 for p in all_procs}
    prim = "rm_R0_t0.1_hac"
    d1_comp = ["adf_sim", "dfgls_sim", "msb_sim", "mzt_sim", "rm_msbhac_hac"]
    d1 = {}
    for n in D_N:
        ks = [k for k in misspec if cells[k]["n"] == n]
        g = gauss_by_n[n]
        d1[str(n)] = {}
        for c in d1_comp:
            diff = by_n[str(n)][prim]["mean"] - by_n[str(n)][c]["mean"]
            se = math.sqrt(sum(paired_se(mask(k, prim), mask(k, c), mask(g, prim), mask(g, c)) ** 2 for k in ks)) / len(ks)
            d1[str(n)][c] = {"mean_delta_primary": by_n[str(n)][prim]["mean"], "mean_delta_comparator": by_n[str(n)][c]["mean"],
                             "difference": diff, "se_difference": se, "holds": bool(diff < -SE_MULT * se)}
    d1_yes = all(v["holds"] for n in d1.values() for v in n.values())
    d2 = {str(n): {"mean_delta_primary": by_n[str(n)][prim]["mean"], "mean_delta_msbhac": by_n[str(n)]["rm_msbhac_hac"]["mean"],
                   "abs_diff_pp": abs(by_n[str(n)][prim]["mean"] - by_n[str(n)]["rm_msbhac_hac"]["mean"]) * 100}
          for n in ns}
    d2_yes = all(v["abs_diff_pp"] <= GATE_PP for v in d2.values())
    d3 = None
    if boot:
        garch_b = [k for k in garch if "awb" in rates[k]]
        small = [k for k in misspec if cells[k]["n"] <= 500]
        mb = C.mean_with_se([deltas[k]["awb"] for k in small])
        mp = C.mean_with_se([deltas[k][prim] for k in small])
        cnt_b = sum(rates[k]["awb"]["in_region"] for k in garch_b)
        cnt_p = sum(rates[k][prim]["in_region"] for k in garch_b)
        d3 = {"garch_cells_compared": garch_b, "garch_in_region_awb": cnt_b, "garch_in_region_primary": cnt_p,
              "mean_delta_awb_n_le_500": mb, "mean_delta_primary_n_le_500": mp,
              "holds": bool(cnt_b >= cnt_p and abs(mb["mean"]) < abs(mp["mean"]))}
    g3_cells = [k for k in garch if cells[k]["n"] <= 500]
    g3 = {"cells": g3_cells, "mean_delta_rmgls": C.mean_with_se([deltas[k]["rm_rmgls_hac"] for k in g3_cells]),
          "mean_delta_rm": C.mean_with_se([deltas[k][prim] for k in g3_cells])}
    g3["excess_pp"] = (g3["mean_delta_rmgls"]["mean"] - g3["mean_delta_rm"]["mean"]) * 100
    literal = C.exact_region(D.N_SIM)
    g2 = {}
    for n in (200, 500, 1000):
        r = dict(rates[gauss_by_n[n]]["rm_rmgls_hac"])
        r["in_protocol_interval"] = bool(literal[0] <= r["rate"] <= literal[1])
        g2[str(n)] = r
    boot_size = None
    if boot:
        p = boot[EXTRA]["p"]
        boot_size = C.rate_record(np.nan_to_num(p, nan=1.0) < C.ALPHA, C.exact_region(len(p)))
        boot_size["nan"] = boot[EXTRA]["nan"]
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "amendment": "experiments/protocol_audit8_amend2.md",
           "bootstrap_included": bool(boot), "B": B_BOOT, "bootstrap_n_max": D.N_BOOT_MAX,
           "exact_region_5000": region5, "exact_region_2000": region2, "exact_region_20000": region20,
           "g2_protocol_interval": literal,
           "gaussian_reference": "indep_gauss_n* (familia 92, N = 20000; AWB: primeras 2000)",
           "procedures": all_procs, "rates": rates, "paired_delta": deltas, "mean_delta_by_n": by_n,
           "count_in_region": in_region,
           "D1": {"by_n": d1, "holds": d1_yes}, "D2": {"by_n": d2, "holds": d2_yes}, "D3": d3,
           "G2_rmgls_gaussian_size": g2, "G3_input": g3, "bootstrap_size_n200_N5000": boot_size,
           "bootstrap_nan": {k: v["nan"] for k, v in boot.items()}, "bootstrap_elapsed_sec": boot_elapsed,
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("D1", d1_yes, "D2", d2_yes, "D3", None if d3 is None else d3["holds"])
    print("G2", {k: (v["rate"], v["in_protocol_interval"]) for k, v in g2.items()}, "G3 exceso pp", g3["excess_pp"])
    print(OUT)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--budget", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--no-bootstrap", action="store_true")
    a = ap.parse_args()
    if a.budget:
        return budget(a)
    if a.run:
        return run(a)
    return analyze(a)


if __name__ == "__main__":
    sys.exit(main())
