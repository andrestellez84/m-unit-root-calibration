"""
Auditoria A11 - T0: registro del protocolo y mapa de semillas.

Sin computo de resultados. Registra:
  1. sha256 de experiments/protocol_audit11.md (disco y contenido commiteado) y el
     commit que lo introdujo.
  2. sha256 del manuscrito de referencia (paper_latex_v12.zip, fuera del repo) y de
     los .tex de paper/ (v11), que no se tocan.
  3. Equivalencia de SeedSequence(familia).spawn(celdas)[c].spawn(reps)[i] con
     SeedSequence(familia, spawn_key=(c, i)) en las celdas nuevas (primeras replicas).
  4. Colision de semillas: streams de A11 (familias 123 y 124) frente a los previos
     (A8 90-98, A9 100-107, A10 110-115, semillas enteras de A5-A7 y la 42).

Salida: experiments/results/t0_protocol_audit11.json.
"""
import argparse
import glob
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402
import audit11_design as D                                         # noqa: E402
import audit10_design as D10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_b0_inventory as INV8                                 # noqa: E402

OUT = os.path.join(C.RESULTS, "t0_protocol_audit11.json")
PROTOCOL = "experiments/protocol_audit11.md"
SPAWN_CHECK_REPS = 3


def spawn_equivalence():
    worst, checked = 0, 0
    for fam, cells in D.CELLS.items():
        if not cells:
            continue
        kids = np.random.SeedSequence(fam).spawn(len(cells))
        for ci, name in enumerate(cells):
            grand = kids[ci].spawn(min(D.cell_reps(fam, name), SPAWN_CHECK_REPS))
            for i, g in enumerate(grand):
                worst = max(worst, int(np.any(g.generate_state(4) != C.rep_seedseq(fam, ci, i).generate_state(4))))
                checked += 1
    return {"reps_checked_per_cell": SPAWN_CHECK_REPS, "streams_checked": checked, "mismatches": worst,
            "equivalent": worst == 0}


def family_words(cells, reps_fn, family):
    words = [INV8.state_words(C.rep_seedseq(family, ci, i) for i in range(reps_fn(family, name)))
             for ci, name in enumerate(cells)]
    return np.concatenate(words) if words else np.array([], dtype=np.uint64)


def seed_map():
    t0 = time.time()
    blocks = INV8.prior_seed_blocks()
    prior_ints = np.unique(np.concatenate([np.arange(b, b + n, dtype=np.int64) for _, b, n in blocks]
                                          + [np.array([42], dtype=np.int64),
                                             np.arange(200000 + 200 * 100 + 30, 200000 + 1000 * 100 + 50 + 5000,
                                                       dtype=np.int64)]))
    prior = [INV8.state_words(np.random.SeedSequence(int(s)) for s in prior_ints)]
    fams = {}
    for mod in (D8, D9, D10):
        for fam, cells in mod.CELLS.items():
            w = family_words(cells, mod.cell_reps, fam)
            fams[str(fam)] = int(w.size)
            prior.append(w)
    prior = np.concatenate(prior)
    new, all_new = {}, []
    for fam, cells in D.CELLS.items():
        w = family_words(cells, D.cell_reps, fam)
        new[str(fam)] = {"cells": len(cells), "replicate_streams": int(w.size), "distinct": int(np.unique(w).size)}
        all_new.append(w)
    all_new = np.concatenate(all_new)
    return {"method": "palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8-A10)",
            "prior_integer_seeds": int(prior_ints.size), "prior_family_streams": fams,
            "prior_streams_total": int(prior.size), "new_families": new, "new_streams_total": int(all_new.size),
            "collisions_new_vs_prior": int(np.intersect1d(all_new, prior).size),
            "collisions_within_new": int(all_new.size - np.unique(all_new).size),
            "families_without_cells": [f for f, c in D.CELLS.items() if not c],
            "elapsed_sec": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript-zip", default=os.path.join(os.path.dirname(C.REPO), "paper_latex_v12.zip"))
    a = ap.parse_args()
    prot_path = os.path.join(C.REPO, PROTOCOL)
    commit = C.git("log", "--diff-filter=A", "--format=%H", "--", PROTOCOL).strip().splitlines()
    protocol = {"path": PROTOCOL, "sha256_disk": C.sha256_file(prot_path),
                "sha256_committed": C.C8.git_blob_sha256(PROTOCOL), "commit_added": commit[-1] if commit else None,
                "commit_last": C.git("log", "-1", "--format=%H", "--", PROTOCOL).strip()}
    manuscript = {"zip": os.path.basename(a.manuscript_zip), "zip_sha256": C.sha256_file(a.manuscript_zip),
                  "zip_bytes": os.path.getsize(a.manuscript_zip),
                  "paper_tex_v11": {C.rel(p): C.sha256_file(p) for p in sorted(glob.glob(os.path.join(C.REPO, "paper", "*.tex")))}}
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["T0"]), "protocol": protocol,
           "manuscript": manuscript, "spawn_equivalence": spawn_equivalence(), "seed_map": seed_map(),
           "families": C.FAMILY}
    C.write_result(OUT, out, __file__)
    print(protocol)
    print(out["spawn_equivalence"])
    print({k: v for k, v in out["seed_map"].items() if k != "prior_family_streams"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
