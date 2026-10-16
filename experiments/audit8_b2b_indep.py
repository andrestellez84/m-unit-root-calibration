"""
Auditoria A8 - B2b segun la enmienda 2: referencia gaussiana independiente.

- 20000 paseos aleatorios gaussianos por n (familia 92, celda indep_gauss_n<n>,
  un hijo de SeedSequence por n: no anidados), n in {60, 100, 150, 200, 500,
  1000, 2000, 5000}, con la misma fila por replica que B2 (todos los
  procedimientos) y las mismas calibraciones (RM: semilla 42, N_cal = 50000;
  comparadores sim: familia 92).
- Compuerta B2b (DURA, enmienda 2): tamano de RM hac (R = 0, theta = 0.1) dentro
  de la region exacta para N = 20000 en n = 200, 500 y 1000.
- Tasas gaussianas de todos los procedimientos con esta referencia; Delta
  pareado de las 22 celdas mal especificadas recalculado frente a ella y, en
  tabla aparte, frente a la referencia publicada de B2.

Salida: experiments/results/b2b_indep_audit8.json.
Uso:
  python experiments/audit8_b2b_indep.py --cores 14 --max-seconds 14400
  python experiments/audit8_b2b_indep.py --analyze
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "b2b_indep_audit8.json")
FAM = C.FAMILY["B2"]
GATE_N = (200, 500, 1000)
GATE_PROC = "rm_R0_t0.1_hac"
PROCS = ("rm_R0_t0.1_one", "rm_R0_t0.1_hac", "rm_R0.5_t0.1_one", "rm_R0.5_t0.1_hac",
         "adf_asy", "adf_sim", "pp_asy", "pp_sim", "dfgls_asy", "dfgls_sim",
         "mzt_asy", "mzt_sim", "msb_asy", "msb_sim", "rm_msbhac_hac",
         "rm_R0_t0.02_hac", "rm_R0_t0.05_hac", "rm_R0_t0.2_hac", "rm_rmgls_hac", "dfglsaic_asy")


def run(a):
    resume = "python experiments/audit8_b2b_indep.py --cores %d --max-seconds %.0f" % (a.cores, a.max_seconds)
    t_block = time.time()
    for name, spec in sorted(D.indep_cells().items(), key=lambda kv: kv[1]["n"]):
        print("\n[CELDA] %s" % name, flush=True)
        try:
            _, info = C.run_cell(name, D.N_INDEP, B2.make_batch_fn("cell", name, spec, a.cores), B2.CKPT, a.cores,
                                 t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
        print("  [COMPLETA] %s en %.0f s" % (name, info["elapsed_sec"]), flush=True)
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def load_rejections():
    """Rechazos de las celdas de B2 y de las independientes (todas las columnas)."""
    null_all = {n: B2.rm_null(n, 1) for n in D.N_ALL}
    sim_all = {n: B2.load_rows("cal_dm_n%d" % n, D.N_CAL)[0] for n in D.N_ALL}
    cells = dict(B2.cell_order())
    rej, elapsed = {}, {}
    for k, s in cells.items():
        rows, _ = B2.load_rows(k, D.N_SIM)
        rej[k] = B2.rejections(rows, null_all, sim_all, s["n"])
    indep = D.indep_cells()
    for k, s in indep.items():
        rows, elapsed[k] = B2.load_rows(k, D.N_INDEP)
        rej[k] = B2.rejections(rows, null_all, sim_all, s["n"])
    return cells, indep, rej, elapsed


def analyze(a):
    t0 = time.time()
    cells, indep, rej, elapsed = load_rejections()
    reg5, reg20 = C.exact_region(D.N_SIM), C.exact_region(D.N_INDEP)
    by_n_ind = {s["n"]: k for k, s in indep.items()}
    by_n_pub = {s["n"]: k for k, s in cells.items() if s["kind"] == "gauss"}
    misspec = [k for k, s in cells.items() if s["kind"] != "gauss"]
    gauss_indep = {str(n): {p: C.rate_record(rej[k][p], reg20) for p in PROCS} for n, k in sorted(by_n_ind.items())}
    gauss_pub = {str(n): {p: C.rate_record(rej[k][p], reg5) for p in PROCS} for n, k in sorted(by_n_pub.items())}
    mis = {k: {p: C.rate_record(rej[k][p], reg5) for p in PROCS} for k in misspec}
    delta = {"independent": {}, "published": {}}
    for k in misspec:
        n = str(cells[k]["n"])
        delta["independent"][k] = {p: C.diff_independent(mis[k][p], gauss_indep[n][p]) for p in PROCS}
        delta["published"][k] = {p: C.diff_independent(mis[k][p], gauss_pub[n][p]) for p in PROCS}
    by_n = {ref: {} for ref in delta}
    for ref in delta:
        for n in sorted({cells[k]["n"] for k in misspec}):
            ks = [k for k in misspec if cells[k]["n"] == n]
            by_n[ref][str(n)] = {"cells": ks, **{p: C.mean_with_se([delta[ref][k][p] for k in ks]) for p in PROCS}}
    gate_sizes = {str(n): gauss_indep[str(n)][GATE_PROC] for n in GATE_N}
    gate = {"verdict": "PASA" if all(v["in_region"] for v in gate_sizes.values()) else "FALLA",
            "procedure": GATE_PROC, "N": D.N_INDEP, "region": reg20, "sizes": gate_sizes,
            "reported_other_n": {n: v[GATE_PROC] for n, v in gauss_indep.items() if int(n) not in GATE_N}}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "amendment": "experiments/protocol_audit8_amend2.md",
           "config": {"N_indep": D.N_INDEP, "N_sim_misspec": D.N_SIM, "procedures": PROCS,
                      "delta_note": "Delta = tasa mal especificada (N = 5000) - tasa gaussiana; EE de diferencia de "
                                    "proporciones independientes con el N de cada lado"},
           "exact_region_20000": reg20, "exact_region_5000": reg5,
           "gate": gate, "gaussian_rates_independent": gauss_indep, "gaussian_rates_published": gauss_pub,
           "misspec_rates": mis, "paired_delta": delta, "mean_delta_by_n": by_n,
           "cells_elapsed_sec": elapsed, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("B2b (enmienda 2):", gate["verdict"], {n: (v["rate"], v["in_region"]) for n, v in gate_sizes.items()})
    print({n: round(v[GATE_PROC]["rate"], 4) for n, v in gauss_indep.items()})
    print(OUT)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    return analyze(a) if a.analyze else run(a)


if __name__ == "__main__":
    sys.exit(main())
