"""
Auditoria A10 - B10.0: registro del protocolo, inventario de A9 reutilizado y mapa de semillas.

Sin computo de resultados. Registra:
  1. sha256 de experiments/protocol_audit10.md (disco y contenido commiteado) y el
     commit que lo introdujo.
  2. Inventario de los JSON de A9 que A10 reutiliza (sha256, bytes, mtime) y de
     las carpetas de checkpoints de A9 (numero de archivos y sha256 agregado).
  3. Equivalencia del esquema SeedSequence(familia).spawn(celdas)[c].spawn(reps)[i]
     con SeedSequence(familia, spawn_key=(c, i)) en todas las celdas nuevas
     (primeras replicas de cada celda).
  4. Colision de semillas: streams de A10 (familias 110-115) frente a todos los
     previos: los de A9 (familias 100-107, mapa de audit9_b90_protocol, que ya
     incluye A8 90-98, semillas enteras de A5-A7 y la semilla 42 de produccion).

Salida: experiments/results/b100_protocol_audit10.json.
"""
import datetime
import glob
import hashlib
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_design as D                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_b0_inventory as INV8                                 # noqa: E402

OUT = os.path.join(C.RESULTS, "b100_protocol_audit10.json")
PROTOCOL = "experiments/protocol_audit10.md"
A9_JSON = ("b90_protocol_audit9.json", "b91_equalized_audit9.json", "b92_budget_audit9.json",
           "b92_theta_audit9.json", "b93_attribution_audit9.json", "b94_finite_sample_audit9.json",
           "b95_awb_audit9.json", "b95_budget_audit9.json", "b96_application_audit9.json",
           "b97_critical_values_audit9.json", "figures_audit9.json", "manifest_audit9.json")
A9_CKPT = ("audit9_cal", "audit9_b91", "audit9_b92", "audit9_b94", "audit9_b95", "audit9_b96", "audit9_b97")
SPAWN_CHECK_REPS = 3


def file_record(path):
    return {"sha256": C.sha256_file(path), "bytes": os.path.getsize(path),
            "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc).isoformat()}


def ckpt_record(d):
    files = sorted(f for f in glob.glob(os.path.join(C.CKPT_ROOT, d, "*")) if os.path.isfile(f))
    h = hashlib.sha256()
    for f in files:
        h.update(C.sha256_file(f).encode())
    return {"files": len(files), "aggregate_sha256": h.hexdigest(),
            "bytes": int(sum(os.path.getsize(f) for f in files)),
            "last_mtime_utc": max((datetime.datetime.fromtimestamp(os.path.getmtime(f), datetime.timezone.utc).isoformat()
                                   for f in files), default=None)}


def spawn_equivalence():
    worst, checked = 0, 0
    for fam, cells in D.CELLS.items():
        if not cells:
            continue
        kids = np.random.SeedSequence(fam).spawn(len(cells))
        for ci, name in enumerate(cells):
            reps = D.cell_reps(fam, name)
            grand = kids[ci].spawn(min(reps, SPAWN_CHECK_REPS))
            for i, g in enumerate(grand):
                a = g.generate_state(4)
                b = C.rep_seedseq(fam, ci, i).generate_state(4)
                worst = max(worst, int(np.any(a != b)))
                checked += 1
    return {"reps_checked_per_cell": SPAWN_CHECK_REPS, "streams_checked": checked, "mismatches": worst,
            "equivalent": worst == 0}


def family_words(cells, reps_fn, family):
    words = []
    for ci, name in enumerate(cells):
        words.append(INV8.state_words(C.rep_seedseq(family, ci, i) for i in range(reps_fn(family, name))))
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
    for fam, cells in D8.CELLS.items():
        w = family_words(cells, D8.cell_reps, fam)
        fams[str(fam)] = int(w.size)
        prior.append(w)
    for fam, cells in D9.CELLS.items():
        w = family_words(cells, D9.cell_reps, fam)
        fams[str(fam)] = int(w.size)
        prior.append(w)
    prior = np.concatenate(prior)
    new, all_new = {}, []
    for fam, cells in D.CELLS.items():
        w = family_words(cells, D.cell_reps, fam)
        new[str(fam)] = {"cells": len(cells), "replicate_streams": int(w.size), "distinct": int(np.unique(w).size)}
        all_new.append(w)
    all_new = np.concatenate(all_new)
    return {"method": "palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8 y A9)",
            "prior_integer_seeds": int(prior_ints.size), "prior_family_streams": fams,
            "prior_streams_total": int(prior.size),
            "new_families": new, "new_streams_total": int(all_new.size),
            "collisions_new_vs_prior": int(np.intersect1d(all_new, prior).size),
            "collisions_within_new": int(all_new.size - np.unique(all_new).size),
            "families_without_cells": [f for f, c in D.CELLS.items() if not c],
            "elapsed_sec": round(time.time() - t0, 1)}


def main():
    prot_path = os.path.join(C.REPO, PROTOCOL)
    commit = C.git("log", "--diff-filter=A", "--format=%H", "--", PROTOCOL).strip().splitlines()
    protocol = {"path": PROTOCOL, "sha256_disk": C.sha256_file(prot_path),
                "sha256_committed": C.C8.git_blob_sha256(PROTOCOL), "commit_added": commit[-1] if commit else None,
                "commit_last": C.git("log", "-1", "--format=%H", "--", PROTOCOL).strip()}
    inv = {n: file_record(os.path.join(C.RESULTS, n)) for n in A9_JSON}
    ck = {d: ckpt_record(d) for d in A9_CKPT}
    spawn = spawn_equivalence()
    seeds = seed_map()
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["B10.0"]), "protocol": protocol,
           "a9_inventory": inv, "a9_checkpoints": ck, "spawn_equivalence": spawn, "seed_map": seeds,
           "families": C.FAMILY}
    C.write_result(OUT, out, __file__)
    print(protocol)
    print(spawn)
    print({k: v for k, v in seeds.items() if k != "prior_family_streams"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
