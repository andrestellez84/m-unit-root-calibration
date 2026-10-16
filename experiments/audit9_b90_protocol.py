"""
Auditoria A9 - B9.0: registro del protocolo, inventario de A8 reutilizado y mapa de semillas.

Sin computo de resultados. Registra:
  1. sha256 de experiments/protocol_audit9.md (disco y contenido commiteado) y el
     commit que lo introdujo.
  2. Inventario de los JSON de A8 que A9 reutiliza (sha256, bytes, mtime) y de las
     carpetas de checkpoints de A8 de las que se regeneran trayectorias (numero de
     lotes y sha256 agregado de sus sha256 ordenados).
  3. Colision de semillas: los streams de A9 (familias 100-107, cada replica de
     cada celda) frente a todos los previos: familias de A8 (90-98, celdas y
     replicas actuales de audit8_design), semillas enteras de A5-A7 (mapa de
     paso0_pairing_audit7.json) y extras (semilla 42 de produccion,
     audit5_tarea2). Metodo de A8: palabra 0 de SeedSequence.generate_state.

Salida: experiments/results/b90_protocol_audit9.json.
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

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_b0_inventory as INV8                                 # noqa: E402

OUT = os.path.join(C.RESULTS, "b90_protocol_audit9.json")
PROTOCOL = "experiments/protocol_audit9.md"
A8_JSON = ("b2_size_audit8.json", "b2b_indep_audit8.json", "b3_comparators_audit8.json", "b4_local_power_audit8.json",
           "b5_power_audit8.json", "b5_budget_audit8.json", "b6_application_audit8.json",
           "b7_critical_values_audit8.json", "deviation_table_audit8.json", "manifest_audit8.json",
           "garch_size_audit7.json", "garch_size_ext_audit7.json", "garch_size_ext_large_audit7.json")
A8_CKPT = ("audit8_b2", "audit8_b5", "audit8_b6")


def file_record(path):
    return {"sha256": C.sha256_file(path), "bytes": os.path.getsize(path),
            "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc).isoformat()}


def ckpt_record(d):
    files = sorted(glob.glob(os.path.join(C.CKPT_ROOT, d, "*.json")))
    h = hashlib.sha256()
    for f in files:
        h.update(C.sha256_file(f).encode())
    return {"json_batches": len(files), "aggregate_sha256": h.hexdigest(),
            "last_mtime_utc": max((datetime.datetime.fromtimestamp(os.path.getmtime(f), datetime.timezone.utc).isoformat()
                                   for f in files), default=None)}


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
    a8 = {}
    for fam, cells in D8.CELLS.items():
        w = family_words(cells, D8.cell_reps, fam)
        a8[str(fam)] = int(w.size)
        prior.append(w)
    prior = np.concatenate(prior)
    new, all_new = {}, []
    for fam, cells in D.CELLS.items():
        w = family_words(cells, D.cell_reps, fam)
        new[str(fam)] = {"cells": len(cells), "replicate_streams": int(w.size), "distinct": int(np.unique(w).size)}
        all_new.append(w)
    all_new = np.concatenate(all_new)
    return {"method": "palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8)",
            "prior_integer_seeds": int(prior_ints.size), "prior_a8_family_streams": a8,
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
    inv = {n: file_record(os.path.join(C.RESULTS, n)) for n in A8_JSON}
    ck = {d: ckpt_record(d) for d in A8_CKPT}
    seeds = seed_map()
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["B9.0"]), "protocol": protocol,
           "a8_inventory": inv, "a8_checkpoints": ck, "seed_map": seeds,
           "families": C.FAMILY}
    C.write_result(OUT, out, __file__)
    print(protocol)
    print({k: v for k, v in seeds.items() if k != "prior_a8_family_streams"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
