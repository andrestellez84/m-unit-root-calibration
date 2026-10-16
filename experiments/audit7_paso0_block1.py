"""
Auditoria A7 - Bloque 1, Paso 0 (regla 5): apareamiento demostrado.

1. Generadores: para cada celda de DGP 5 y de calibracion se regeneran 50
   series con la funcion que usa el runner (la que tambien escribe el .bin del
   bootstrap) y con las funciones de power_comparison.py llamadas directamente
   con default_rng(seed_base + i). Exigido: max|diff| = 0.
2. Componentes: el runner calcula g1_std y g2_std por el mismo camino que
   run_experiment_cell de power_comparison.py (columnas publicadas de R = 0.50);
   A5 evaluo el adaptativo con compute_statistic. Se comparan ambos caminos y el
   estadistico R = 0.50 sobre 50 series por n.
3. Semillas: solape entre todas las celdas del diseno del Bloque 1, incluida la
   extension de la segunda enmienda.
4. Semillas de R del bootstrap: la serie i de una celda usa (seed_base + i) mod M
   en audit7_bootstrap_worker.R. Rangos disjuntos entre todas las celdas con
   bootstrap (tambien las retiradas y la celda de control de A6), sin vuelta
   del modulo dentro de una celda, y la semilla de un lote desplazado coincide
   con la del indice global.

Pasa o falla, va a la seccion de diffs del reporte.

Uso: python experiments/audit7_paso0_block1.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_dgp5_runner as RUN                            # noqa: E402
from power_comparison import (generate_ar1_break_variance,  # noqa: E402
                              generate_rw_break_variance)
from stationarity_test.statistic import compute_statistic   # noqa: E402

OUT = os.path.join(C.RESULTS, "paso0_block1_audit7.json")
N_CHECK = 50
COMPONENT_TOL = 1e-12


def main():
    gen = {}
    worst_gen = 0.0
    for (n, rho, r) in D.dgp5_cells():
        sb = D.dgp5_seed_base(n, rho, r)
        d = max(float(np.max(np.abs(
            RUN.generate("dgp5", n, rho, r, sb, i)
            - generate_ar1_break_variance(n=n, rho=rho, ratio=r, rng=np.random.default_rng(sb + i)))))
            for i in range(N_CHECK))
        gen[D.dgp5_tag(n, rho, r)] = {"seed_base": sb, "max_abs_diff": d}
        worst_gen = max(worst_gen, d)
    for n in D.CAL_N_GRID:
        sb = D.cal_seed_base(n)
        d = max(float(np.max(np.abs(
            RUN.generate("cal", n, None, None, sb, i)
            - generate_rw_break_variance(n=n, ratio=1.0, rng=np.random.default_rng(sb + i)))))
            for i in range(N_CHECK))
        gen[D.cal_tag(n)] = {"seed_base": sb, "max_abs_diff": d}
        worst_gen = max(worst_gen, d)

    comp, worst_comp = {}, 0.0
    for n in D.CAL_N_GRID:
        sb = D.cal_seed_base(n)
        dg1 = dg2 = dst = 0.0
        for i in range(N_CHECK):
            Y = RUN.generate("cal", n, None, None, sb, i)
            g1, g2 = RUN.components(Y)
            ref = compute_statistic(Y, RUN.THETA, 0.5, andrews_pilot=RUN.PILOT)
            dg1 = max(dg1, abs(g1 - ref["g1_std"]))
            dg2 = max(dg2, abs(g2 - ref["g2_std"]))
            dst = max(dst, abs(np.sqrt(0.25 * g1 ** 2 + 0.25 * g2 ** 2) - ref["statistic"]))
        comp["n%d" % n] = {"max_abs_diff_g1_std": dg1, "max_abs_diff_g2_std": dg2,
                           "max_abs_diff_stat_R050": dst}
        worst_comp = max(worst_comp, dg1, dg2, dst)

    overlap = C.seed_overlap_report(D.all_seed_bases(), D.N_CAL)

    M = RUN.R_SEED_MODULUS
    boot_jobs = {D.cal_tag(n): (D.cal_seed_base(n), D.N_CAL) for n in D.CAL_N_GRID}
    boot_jobs.update({D.dgp5_tag(*c): (D.dgp5_seed_base(*c), D.DGP5_N_SIM) for c in D.dgp5_cells()})
    boot_jobs["seed_control_a6"] = (C.seed_base(D.FAM_SEED_CONTROL, 0), D.SEED_CONTROL_N_SIM)
    # Las dos patas del diagnostico (B=399 y B=999) comparten a proposito estas semillas
    # (numeros aleatorios comunes); se cuentan una vez.
    boot_jobs["size_diag_a6_dgp3_n200_r1"] = (C.seed_base(D.FAM_SIZE_DIAG, 0), D.SIZE_DIAG_N_SIM)
    iv = sorted((RUN.r_seed_start(sb, 0), RUN.r_seed_start(sb, 0) + N - 1, tag)
                for tag, (sb, N) in boot_jobs.items())
    wraps = [t for lo, hi, t in iv if hi >= M]
    r_overlaps = [[a[2], b[2]] for a, b in zip(iv, iv[1:]) if b[0] <= a[1]]
    shift_ok = all(RUN.r_seed_start(sb, i) == (RUN.r_seed_start(sb, 0) + i) % M
                   for (sb, N) in boot_jobs.values() for i in (1, N // 2, N - 1))
    r_seeds = {"modulus": M, "n_cells": len(iv), "wrap_around_cells": wraps,
               "overlapping_pairs": r_overlaps,
               "min_gap_between_cells": int(min(b[0] - a[1] - 1 for a, b in zip(iv, iv[1:]))),
               "batch_shift_consistent": bool(shift_ok),
               "ranges": {t: [int(lo), int(hi)] for lo, hi, t in iv}}

    ok = (worst_gen == 0.0 and worst_comp <= COMPONENT_TOL
          and overlap["exact_collisions"] == 0 and overlap["overlapping_pairs"] == 0
          and not wraps and not r_overlaps and shift_ok)

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="block1_pairing_proof", n_sim=N_CHECK,
            seed_formula="las del diseno del Bloque 1 (audit7_design.py)"),
        "generators": {"n_series_per_cell": N_CHECK, "worst_max_abs_diff": worst_gen,
                       "cells": gen},
        "components_vs_compute_statistic": {"tolerance": COMPONENT_TOL,
                                            "worst_max_abs_diff": worst_comp, "by_n": comp},
        "seed_overlap_block1": overlap,
        "r_bootstrap_seeds": r_seeds,
        "verdict": "PASA" if ok else "FALLA",
    })
    print("generadores: %d celdas, peor max|diff| = %.3e" % (len(gen), worst_gen))
    for k, v in comp.items():
        print("componentes %s: g1 %.2e  g2 %.2e  estadistico %.2e"
              % (k, v["max_abs_diff_g1_std"], v["max_abs_diff_g2_std"], v["max_abs_diff_stat_R050"]))
    print("semillas: %d celdas, %d colisiones, %d pares solapados"
          % (overlap["n_cells"], overlap["exact_collisions"], overlap["overlapping_pairs"]))
    print("semillas de R: %d celdas, %d solapes, %d con vuelta del modulo, hueco minimo %d, "
          "desplazamiento de lote %s" % (r_seeds["n_cells"], len(r_overlaps), len(wraps),
                                         r_seeds["min_gap_between_cells"], shift_ok))
    print("PASO 0 BLOQUE 1: %s   -> %s" % ("PASA" if ok else "FALLA", OUT))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
