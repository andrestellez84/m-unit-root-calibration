"""
Auditoria A12 - B12.0: inventario, protocolo, mapa de semillas y test de convencion.

Sin computo pesado. Registra:
  1. sha256 (disco y commiteado) y commit de protocol_audit12.md y de
     prediccion_ma_audit12.md (la prediccion debe ser anterior al protocolo).
  2. sha256 de los JSON reutilizados (lista del encargo y los que usan B12.A-F) y de
     las muestras de calibracion y carpetas de checkpoints que se reutilizan.
  3. Equivalencia SeedSequence(familia).spawn <-> spawn_key = (celda, i) en las celdas
     nuevas y colisiones de los streams de A12 (130, 132, 136, 137) frente a A8-A11
     (familias 90-129), semillas enteras de A5-A7 y la 42 de produccion.
  4. Test de convencion (lectura 2): con psi = 0 el generador MA y la fila nueva
     reproducen (a) las 50 primeras trayectorias de a1_dm_n200_s1 y a1_ct_n200_s1
     (familia 111, B10.1) y (b) las 50 primeras filas de la calibracion de A10 a
     n = 200 (semilla 42): trayectoria y columnas comunes, max |Delta| = 0.

Salida: experiments/results/b120_inventory_audit12.json.
"""
import datetime
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
import audit12_design as D                                         # noqa: E402
import audit12_unitroot as P                                       # noqa: E402
import audit11_design as D11                                       # noqa: E402
import audit10_design as D10                                       # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_b0_inventory as INV8                                 # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit10_b100_protocol as B100                               # noqa: E402

OUT = os.path.join(C.RESULTS, "b120_inventory_audit12.json")
PROTOCOL = "experiments/protocol_audit12.md"
PREDICTION = "experiments/prediccion_ma_audit12.md"
REUSED_JSON = ("b101_theta_audit10.json", "b103_equalized_audit10.json", "b92_theta_audit9.json",
               "b93_attribution_audit9.json", "b97_critical_values_audit9.json", "t3_anchor_audit11.json",
               "b94_finite_sample_audit9.json", "b91_equalized_audit9.json")
REUSED_NPZ = tuple("audit10_cal/cal_n%d.npz" % n for n in (100, 200, 500, 1000)) + ("audit9_cal/cal_n2000.npz",)
REUSED_CKPT = ("audit9_b91", "audit9_b92", "audit9_b94", "audit10_b101")
SPAWN_CHECK_REPS = 3
PASO0 = 50
CONV_COLS = ("s2", "gls_t0", "gls_t0.02", "glsb_t0", "dfgls", "dfgls_p", "mzt", "msb", "k", "s2ar", "adf", "adf_p",
             "pp", "pp_p")


def file_record(path):
    return {"sha256": C.sha256_file(path), "bytes": os.path.getsize(path),
            "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc).isoformat()}


def committed(path):
    log = C.git("log", "--diff-filter=A", "--format=%H %cI", "--", path).strip().splitlines()
    first = log[-1].split() if log else [None, None]
    return {"path": path, "sha256_disk": C.sha256_file(os.path.join(C.REPO, path)),
            "sha256_committed": C.C8.git_blob_sha256(path), "commit_added": first[0], "commit_time": first[1]}


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
    for mod in (D8, D9, D10, D11):
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
    return {"method": "palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8-A11)",
            "prior_families": sorted(int(f) for f in fams), "prior_integer_seeds": int(prior_ints.size),
            "prior_family_streams": fams, "prior_streams_total": int(prior.size), "new_families": new,
            "new_streams_total": int(all_new.size),
            "collisions_new_vs_prior": int(np.intersect1d(all_new, prior).size),
            "collisions_within_new": int(all_new.size - np.unique(all_new).size),
            "families_without_cells": [f for f, c in D.CELLS.items() if not c], "elapsed_sec": round(time.time() - t0, 1)}


def diff_cols(new, ref):
    worst = {}
    for c in CONV_COLS:
        a, b = np.asarray(new[c]), np.asarray(ref[c])
        both = np.isnan(a) & np.isnan(b)
        d = np.where(both, 0.0, np.abs(a - b))
        worst[c] = float(np.max(np.where(np.isnan(d), np.inf, d)))
    return worst


def convention():
    import audit10_b101_theta as B101
    out = {}
    for case, det in (("dm", "c"), ("ct", "ct")):
        tag = "a1_%s_n200_s1" % case
        ref = C.load_prefix(B101.CKPT, tag, PASO0)
        J = E.index(E.columns(cases=(det,), adfpp=True))
        path_worst, new = 0.0, {c: [] for c in CONV_COLS}
        for i in range(PASO0):
            ci = D10.cell_index(111, tag)
            y = P.null_path(("ma", 0.0), 200, C.rep_rng(111, ci, i))
            path_worst = max(path_worst, float(np.max(np.abs(y - D10.a1_path(case, 200, 1, i)))))
            d = P.np_part(y, 200, det)
            for c in CONV_COLS:
                new[c].append(d[c])
        refd = {c: ref[:, J["s2" if c == "s2" else "%s|%s" % (det, c)]] for c in CONV_COLS}
        w = diff_cols(new, refd)
        out["b101|" + tag] = {"paths": PASO0, "path_max_abs_diff": path_worst, "by_column": w, "max_abs_diff": max(w.values())}
    with np.load(os.path.join(C.CKPT_ROOT, "audit10_cal", "cal_n200.npz")) as z:
        rows, cols = z["rows"][:PASO0], [str(c) for c in z["cols"]]
    J = {c: i for i, c in enumerate(cols)}
    rng = np.random.default_rng(E.CAL_SEED)
    ys = [P.null_path(("ma", 0.0), 200, rng) for _ in range(PASO0)]
    for det in ("c", "ct"):
        new = {c: [] for c in CONV_COLS}
        for y in ys:
            d = P.np_part(y, 200, det)
            for c in CONV_COLS:
                new[c].append(d[c])
        refd = {c: rows[:, J["s2" if c == "s2" else "%s|%s" % (det, c)]] for c in CONV_COLS}
        w = diff_cols(new, refd)
        out["cal_n200|%s" % det] = {"paths": PASO0, "by_column": w, "max_abs_diff": max(w.values())}
    worst = max(v["max_abs_diff"] for v in out.values())
    return {"reading": "familia 110 sin trayectorias; se usan a1_*_n200_s1 (familia 111) y la calibracion de A10 n = 200 (semilla 42)",
            "cells": out, "max_abs_diff": worst, "passes": worst == 0.0}


def main():
    t0 = time.time()
    prot, pred = committed(PROTOCOL), committed(PREDICTION)
    reused = {n: file_record(os.path.join(C.RESULTS, n)) for n in REUSED_JSON}
    npz = {p: file_record(os.path.join(C.CKPT_ROOT, p)) for p in REUSED_NPZ}
    ck = {d: B100.ckpt_record(d) for d in REUSED_CKPT}
    conv = convention()
    out = {"provenance": C.provenance(__file__, seed_family=None), "protocol": prot, "prediction": pred,
           "prediction_before_protocol": pred["commit_time"] <= prot["commit_time"] and pred["commit_added"] != prot["commit_added"],
           "reused_json": reused, "reused_npz": npz, "reused_checkpoints": ck,
           "spawn_equivalence": spawn_equivalence(), "convention_test": conv, "seed_map": seed_map(),
           "families": C.FAMILY, "elapsed_sec": None}
    out["elapsed_sec"] = round(time.time() - t0, 1)
    C.write_result(OUT, out, __file__)
    print("protocolo", prot)
    print("prediccion", pred, "antes:", out["prediction_before_protocol"])
    print("convencion", conv["max_abs_diff"], conv["passes"])
    print({k: v for k, v in out["seed_map"].items() if k not in ("prior_family_streams",)})
    return 0 if conv["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
