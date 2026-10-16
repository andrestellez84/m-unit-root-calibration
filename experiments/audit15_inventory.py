"""
Auditoria A15 - B15.I: inventario de semillas antes de B15.1 (protocol_audit15.md, lectura G1;
enmienda 2, seccion 3). Sin computo de estadisticos.

Colisiones (palabra 0 de SeedSequence.generate_state(uint64), metodo de A8-A13) de todos los
streams de A15 (trayectorias (celda, i) y streams por brazo (celda, i, a) de 151-158) frente a los
de las familias previas con streams (disenos de A8-A13), las semillas enteras de A5-A7 y la 42.
Registra tambien los commits y sha256 del protocolo, las enmiendas y la prediccion, y los archivos
descargados (tamano y sha256).

Salida: experiments/results/inventory_audit15.json.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_design as D                                         # noqa: E402
import audit13_design as D13                                       # noqa: E402
import audit12_design as D12                                       # noqa: E402
import audit11_design as D11                                       # noqa: E402
import audit10_design as D10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_b0_inventory as INV8                                 # noqa: E402
import audit12_b120_inventory as B120                              # noqa: E402

OUT = os.path.join(C.RESULTS, "inventory_audit15.json")
DOCS = ("experiments/protocol_audit15.md", "experiments/protocol_audit15_amend1.md", "experiments/protocol_audit15_amend2.md",
        "experiments/prediccion_boot_audit15.md", "experiments/protocol_audit15_amend3.md")
EXTERNAL = {"bootUR_1.0.5.tar.gz": "https://cran.r-project.org/src/contrib/bootUR_1.0.5.tar.gz",
            "HARRecommendations.pdf": "https://ebenlazarus.github.io/HARRecommendations.pdf"}


def words(ss_iter):
    return INV8.state_words(ss_iter)


def new_words():
    per, allw = {}, []
    for fam, cells in D.CELLS.items():
        if not cells:
            per[str(fam)] = {"cells": 0, "path_streams": 0, "arm_streams": 0}
            continue
        wp, wa = [], []
        for ci, name in enumerate(cells):
            reps = D.cell_reps(fam, name)
            wp.append(words(np.random.SeedSequence(fam, spawn_key=(ci, i)) for i in range(reps)))
            for a in D.arm_keys(fam, name):
                wa.append(words(np.random.SeedSequence(fam, spawn_key=(ci, i, a)) for i in range(reps)))
        wp = np.concatenate(wp)
        wa = np.concatenate(wa) if wa else np.array([], dtype=np.uint64)
        per[str(fam)] = {"cells": len(cells), "path_streams": int(wp.size), "arm_streams": int(wa.size)}
        allw += [wp, wa]
    return per, np.concatenate(allw)


def prior_words():
    blocks = INV8.prior_seed_blocks()
    ints = np.unique(np.concatenate([np.arange(b, b + n, dtype=np.int64) for _, b, n in blocks]
                                    + [np.array([42], dtype=np.int64),
                                       np.arange(200000 + 200 * 100 + 30, 200000 + 1000 * 100 + 50 + 5000, dtype=np.int64)]))
    prior = [words(np.random.SeedSequence(int(s)) for s in ints)]
    fams = {}
    for mod in (D8, D9, D10, D11, D12, D13):
        for fam, cells in mod.CELLS.items():
            w = B120.family_words(cells, mod.cell_reps, fam)
            fams[str(fam)] = int(w.size)
            prior.append(w)
    return int(ints.size), fams, np.concatenate(prior)


def main():
    t0 = time.time()
    docs = {p: C.committed(p) for p in DOCS}
    ext = {}
    for name, url in EXTERNAL.items():
        p = os.path.join(HERE, "external_audit15", name)
        ext[name] = {"url": url, "local": C.rel(p), "bytes": os.path.getsize(p) if os.path.exists(p) else None,
                     "sha256": C.sha256_file(p) if os.path.exists(p) else None, "committed": False}
    n_ints, fams, prior = prior_words()
    per, new = new_words()
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit15.md, G1; enmienda 2, seccion 3",
           "documents": docs, "external_files": ext,
           "families": {"assigned": C.FAMILY, "reserved_unused": C.RESERVED_UNUSED,
                        "overlap_with_prior_range": sorted(set(C.FAMILY.values()) & set(C.PRIOR_FAMILIES) - {C.RESERVED_UNUSED})},
           "seed_map": {"method": "palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8-A13)",
                        "prior_families": sorted(int(f) for f in fams), "prior_family_streams": fams,
                        "prior_integer_seeds": n_ints, "prior_streams_total": int(prior.size),
                        "new_families": per, "new_streams_total": int(new.size),
                        "collisions_new_vs_prior": int(np.intersect1d(new, prior).size),
                        "collisions_within_new": int(new.size - np.unique(new).size)},
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    sm = out["seed_map"]
    print({k: v for k, v in sm.items() if k not in ("prior_family_streams", "new_families")})
    print(per)
    print({p: (d["commit_added"] or "")[:7] for p, d in docs.items()})
    ok = sm["collisions_new_vs_prior"] == 0 and sm["collisions_within_new"] == 0 and not out["families"]["overlap_with_prior_range"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
