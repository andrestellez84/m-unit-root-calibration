"""
Auditoria A7 - Bloque 1: presupuesto por sondas, antes de lanzar.

Las sondas se corren SOLO sobre las celdas de calibracion (paseo aleatorio), no
sobre DGP 5, para no ver resultados de DGP 5 antes de tiempo. El costo por serie
del bootstrap depende de n y no de rho o r, asi que la sonda de calibracion a un
n mide el costo de las celdas de DGP 5 a ese n.

Cada sonda descompone el tiempo en:
  - costo estacionario del bootstrap por serie (medido dentro del worker de R),
  - arranque del cluster de R por lote (pared del worker menos tiempo interno),
  - costo de los procedimientos en Python por serie (pool ya caliente).
La sonda de pared de 14 series incluye el arranque y sobreestima; por eso la
proyeccion usa los componentes, y el numero de lotes se reconstruye con la misma
regla que run_cell_batched para cargar el arranque de R en cada lote.

Las sondas quedan como primer lote de las celdas de calibracion y se reutilizan.

Uso: python experiments/audit7_block1_budget.py --cores 14
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_dgp5_runner as RUN                            # noqa: E402

OUT = os.path.join(C.RESULTS, "block1_budget_audit7.json")
BLOCK_CAP = 4 * 3600
ADAPTNULL_PROBE = 14 * 14


def k_batch_rule(probe_wall_sps):
    k = int(max(C.PROBE_SERIES, math.floor(C.TARGET_BATCH_SEC / max(probe_wall_sps, 1e-6))))
    return max(C.PROBE_SERIES, (k // C.PROBE_SERIES) * C.PROBE_SERIES)


def _adaptnull_components(n, indices):
    for i in indices:
        RUN.components(RUN.generate("adaptnull", n, None, None, RUN.ADAPT_NULL_SEED, i))
    return len(indices)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()

    t0 = time.time()
    RUN.warm_pool(a.cores, D.CAL_N_GRID)
    per_n = {}
    for n in D.CAL_N_GRID:
        tag, sb = D.cal_tag(n), D.cal_seed_base(n)
        print("\n[SONDA] %s" % tag)
        _, info = C.run_cell_batched(tag, D.N_CAL, RUN.make_batch_fn("cal", n, None, None, sb,
                                                                      a.cores, D.DGP5_B),
                                     RUN.CKPT, a.cores, time.time(), 1e12, "", probe_only=True)
        tpath = os.path.join(RUN.CKPT, "%s_i%06d_k%05d.timing.json" % (tag, 0, C.PROBE_SERIES))
        with open(tpath, encoding="utf-8") as f:
            tm = json.load(f)
        boot_sps = tm["r_internal_sec_per_series"]
        r_startup = max(tm["r_wall_sec"] - tm["r_internal_sec"], 0.0)
        py_sps = tm["py_wall_sec"] / tm["k"]
        steady = boot_sps + py_sps
        k_batch = k_batch_rule(info["probe_sec_per_series"])

        idx = list(range(ADAPTNULL_PROBE))
        parts = [idx[j::a.cores] for j in range(a.cores)]
        t1 = time.time()
        Parallel(n_jobs=a.cores, backend="loky")(delayed(_adaptnull_components)(n, p) for p in parts)
        adapt_sps = (time.time() - t1) / ADAPTNULL_PROBE

        def cell_sec(N):
            batches = 1 + math.ceil(max(N - C.PROBE_SERIES, 0) / k_batch)
            return N * steady + batches * r_startup, batches

        cal_sec, cal_batches = cell_sec(D.N_CAL)
        dgp5_cell_sec, dgp5_batches = cell_sec(D.DGP5_N_SIM)
        per_n[str(n)] = {
            "probe_wall_sec_per_series": info["probe_sec_per_series"],
            "bootstrap_steady_sec_per_series": boot_sps,
            "r_cluster_startup_sec_per_batch": r_startup,
            "python_sec_per_series": py_sps,
            "steady_total_sec_per_series": steady,
            "k_batch_used_by_runner": k_batch,
            "calibration_cell_sec": cal_sec, "calibration_batches": cal_batches,
            "dgp5_cell_sec": dgp5_cell_sec, "dgp5_batches_per_cell": dgp5_batches,
            "adaptnull_sec_per_series": adapt_sps,
            "adaptnull_cell_sec": adapt_sps * RUN.ADAPT_NULL_N,
        }
        print("  bootstrap %.3f s/serie | arranque R %.1f s/lote | python %.3f s/serie | "
              "lote %d | calibracion %.2f h | celda DGP5 %.2f h | nula adaptativa %.2f h"
              % (boot_sps, r_startup, py_sps, k_batch, cal_sec / 3600, dgp5_cell_sec / 3600,
                 adapt_sps * RUN.ADAPT_NULL_N / 3600))

    jobs = [("adaptnull n=%d" % n, per_n[str(n)]["adaptnull_cell_sec"]) for n in D.CAL_N_GRID]
    jobs += [("cal n=%d" % n, per_n[str(n)]["calibration_cell_sec"]) for n in D.CAL_N_GRID]
    cells = D.dgp5_cells()
    first = [c for c in cells if abs(c[1] - 0.93) < 1e-9]
    rest = [c for c in cells if abs(c[1] - 0.93) >= 1e-9]
    jobs += [(D.dgp5_tag(*c), per_n[str(c[0])]["dgp5_cell_sec"]) for c in first + rest]
    total = sum(s for _, s in jobs)

    blocks, cur, cur_s = [], [], 0.0
    for name, s in jobs:
        if cur and cur_s + s > BLOCK_CAP:
            blocks.append({"jobs": cur, "sec": cur_s})
            cur, cur_s = [], 0.0
        cur.append(name)
        cur_s += s
    if cur:
        blocks.append({"jobs": cur, "sec": cur_s})
    oversized = [name for name, s in jobs if s > BLOCK_CAP]

    subtotal = {
        "nulas_nominales_adaptativo": sum(per_n[str(n)]["adaptnull_cell_sec"] for n in D.CAL_N_GRID),
        "calibracion": sum(per_n[str(n)]["calibration_cell_sec"] for n in D.CAL_N_GRID),
        "dgp5_n200": sum(per_n["200"]["dgp5_cell_sec"] for c in cells if c[0] == 200),
        "dgp5_n500": sum(per_n["500"]["dgp5_cell_sec"] for c in cells if c[0] == 500),
        "dgp5_n1000": sum(per_n["1000"]["dgp5_cell_sec"] for c in cells if c[0] == 1000),
        "rho_0.93_primero": sum(per_n[str(c[0])]["dgp5_cell_sec"] for c in first),
    }
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="block1_budget", n_sim=None,
                                   seed_formula="sondas sobre la calibracion (familia 70)",
                                   extra_code_files=[RUN.WORKER_R]),
        "block_cap_sec": BLOCK_CAP, "per_n": per_n, "subtotals_sec": subtotal,
        "total_sec": total, "exceeds_10h": total > 10 * 3600,
        "order": "nulas adaptativas, calibraciones, DGP 5 con rho=0.93 primero",
        "blocks": blocks, "jobs_longer_than_block_cap": oversized,
        "probes_elapsed_sec": round(time.time() - t0, 1),
    })
    print("\nTOTAL proyectado: %.2f h  (%s 10 h)" % (total / 3600, "supera" if total > 36000 else "no supera"))
    for k, v in subtotal.items():
        print("  %-28s %.2f h" % (k, v / 3600))
    for i, b in enumerate(blocks, 1):
        print("  bloque %d: %.2f h  (%d trabajos)" % (i, b["sec"] / 3600, len(b["jobs"])))
    if oversized:
        print("  trabajos que superan 4 h por si solos (los parte el tope entre lotes): %s" % oversized)
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
