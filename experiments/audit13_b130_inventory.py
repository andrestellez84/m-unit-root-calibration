"""
Auditoria A13 - B13.0: inventario, protocolo y mapa de semillas.

Sin computo pesado. Registra:
  1. sha256 (disco y commiteado) y commit de protocol_audit13.md.
  2. sha256 del manuscrito de referencia (paper_latex_v13.zip), de los JSON que
     B13.E y B13.T leen y agregado de las carpetas de checkpoints reutilizadas.
  3. Equivalencia SeedSequence(familia).spawn <-> spawn_key = (celda, i) en las
     celdas nuevas y colisiones de los streams de A13 (141-143) frente a A8-A12
     (familias 90-137), semillas enteras de A5-A7 y la 42 de produccion (metodo de
     A8-A12: palabra 0 de generate_state).

Salida: experiments/results/b130_inventory_audit13.json.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_design as D                                         # noqa: E402
import audit12_design as D12                                       # noqa: E402
import audit11_design as D11                                       # noqa: E402
import audit10_design as D10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_b0_inventory as INV8                                 # noqa: E402
import audit10_b100_protocol as B100                               # noqa: E402
import audit12_b120_inventory as B120                              # noqa: E402

OUT = os.path.join(C.RESULTS, "b130_inventory_audit13.json")
PROTOCOL = "experiments/protocol_audit13.md"
REUSED_JSON = ("b101_theta_audit10.json", "b103_equalized_audit10.json", "b103_finite_audit10.json",
               "b103_lown_audit10.json", "b103_cv_audit10.json", "b103_awb_audit10.json", "b103_dgp5_audit10.json",
               "b103_application_audit10.json", "b92_theta_audit9.json", "b97_critical_values_audit9.json",
               "b95_awb_audit9.json", "b96_application_audit9.json", "b5_power_audit8.json", "b3_comparators_audit8.json",
               "dgp5_mixed_audit7.json", "bA_ma_audit12.json", "bC_initial_audit12.json", "figures_audit11.json")
REUSED_CKPT = ("audit10_cal", "audit9_cal", "audit9_b91", "audit9_b92", "audit9_b94", "audit9_b95", "audit10_b103",
               "audit10_b103_app", "audit8_b5", "audit8_b6", "audit7_block1")
SPAWN_CHECK_REPS = 3


def spawn_equivalence():
    worst, checked = 0, 0
    for fam, cells in D.CELLS.items():
        if not cells:
            continue
        kids = np.random.SeedSequence(fam).spawn(len(cells))
        for ci, name in enumerate(cells):
            for i, g in enumerate(kids[ci].spawn(min(D.cell_reps(fam, name), SPAWN_CHECK_REPS))):
                worst = max(worst, int(np.any(g.generate_state(4) != C.rep_seedseq(fam, ci, i).generate_state(4))))
                checked += 1
    return {"reps_checked_per_cell": SPAWN_CHECK_REPS, "streams_checked": checked, "mismatches": worst,
            "equivalent": worst == 0}


def seed_map():
    t0 = time.time()
    blocks = INV8.prior_seed_blocks()
    prior_ints = np.unique(np.concatenate([np.arange(b, b + n, dtype=np.int64) for _, b, n in blocks]
                                          + [np.array([42], dtype=np.int64),
                                             np.arange(200000 + 200 * 100 + 30, 200000 + 1000 * 100 + 50 + 5000,
                                                       dtype=np.int64)]))
    prior = [INV8.state_words(np.random.SeedSequence(int(s)) for s in prior_ints)]
    fams = {}
    for mod in (D8, D9, D10, D11, D12):
        for fam, cells in mod.CELLS.items():
            w = B120.family_words(cells, mod.cell_reps, fam)
            fams[str(fam)] = int(w.size)
            prior.append(w)
    prior = np.concatenate(prior)
    new, all_new = {}, []
    for fam, cells in D.CELLS.items():
        w = B120.family_words(cells, D.cell_reps, fam)
        new[str(fam)] = {"cells": len(cells), "replicate_streams": int(w.size), "distinct": int(np.unique(w).size)}
        all_new.append(w)
    all_new = np.concatenate(all_new)
    prior_fams = sorted(int(f) for f in fams)
    return {"method": "palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8-A12)",
            "prior_families": prior_fams, "prior_families_cover_90_137": all(f in C.PRIOR_FAMILIES for f in prior_fams),
            "prior_integer_seeds": int(prior_ints.size), "prior_family_streams": fams,
            "prior_streams_total": int(prior.size), "new_families": new, "new_streams_total": int(all_new.size),
            "collisions_new_vs_prior": int(np.intersect1d(all_new, prior).size),
            "collisions_within_new": int(all_new.size - np.unique(all_new).size),
            "families_without_cells": [f for f, c in D.CELLS.items() if not c], "elapsed_sec": round(time.time() - t0, 1)}


def main():
    t0 = time.time()
    prot = B120.committed(PROTOCOL)
    reused = {n: B120.file_record(os.path.join(C.RESULTS, n)) for n in REUSED_JSON}
    ck = {d: B100.ckpt_record(d) for d in REUSED_CKPT}
    out = {"provenance": C.provenance(__file__, seed_family=None), "protocol": prot,
           "manuscript": dict(B120.file_record(C.MANUSCRIPT), path=os.path.basename(C.MANUSCRIPT)),
           "reused_json": reused, "reused_checkpoints": ck, "spawn_equivalence": spawn_equivalence(),
           "seed_map": seed_map(), "families": C.FAMILY, "cells": {str(k): list(v) for k, v in D.CELLS.items()}}
    out["elapsed_sec"] = round(time.time() - t0, 1)
    C.write_result(OUT, out, __file__)
    sm = out["seed_map"]
    ok = (prot["sha256_disk"] == prot["sha256_committed"] and out["spawn_equivalence"]["equivalent"]
          and sm["collisions_new_vs_prior"] == 0 and sm["collisions_within_new"] == 0)
    print("protocolo", prot)
    print({k: v for k, v in sm.items() if k != "prior_family_streams"})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
