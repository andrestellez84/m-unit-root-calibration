"""
Auditoria A7 - Bloque 1a: validacion de kappa_2 contra su ley nula.

Es la compuerta que falto con Lee-Strazicich en A6: ningun comparador nuevo se
usa sin demostrar antes que reproduce su tamano nominal.

Nulas de "sin quiebre de varianza", 5000 replicas, n in {200, 500, 1000}:
  (i)  rw     : paseo aleatorio gaussiano homoscedastico
  (ii) ar093  : AR(1) estacionario, rho = 0.93, homoscedastico

Criterio: el tamano empirico al valor critico 1.358 debe caer en la region
binomial [0.0440, 0.0562] en las seis celdas. Si falla en MAS DE UNA celda,
kappa_2 se retira.

Semillas: familia 91, seed_base = 91*10^8 + indice_celda*10^5, con
indice_celda = 3*indice_nula + indice_n. Disjuncion demostrada en el JSON.

Uso:
  python experiments/audit7_kappa2_validation.py --n-sim 5000 --cores 14 \
      --max-seconds 14400
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                  # noqa: E402
from audit7_kappa2 import KAPPA2_CRITICAL, kappa2_on_adf_residuals  # noqa: E402

OUT = os.path.join(C.RESULTS, "kappa2_validation_audit7.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit7_kappa2_validation")
SEED_FAMILY = 91
NULLS = ("rw", "ar093")
N_GRID = (200, 500, 1000)
GATE_REGION = (0.0440, 0.0562)          # region fijada en la especificacion
MAX_FAILED_CELLS = 1


def generate(null, n, rng):
    eps = rng.standard_normal(n)
    y = np.empty(n + 1)
    y[0] = 0.0
    if null == "rw":
        np.cumsum(eps, out=y[1:])
    elif null == "ar093":
        for t in range(n):
            y[t + 1] = 0.93 * y[t] + eps[t]
    else:
        raise ValueError(null)
    return y


def _eval_indices(null, n, sb, indices):
    rows = []
    for i in indices:
        y = generate(null, n, np.random.default_rng(sb + i))
        k2, lag, T = kappa2_on_adf_residuals(y)
        rows.append([k2, float(lag), float(T)])
    return rows


def make_batch_fn(null, n, sb, cores):
    def batch_fn(indices):
        parts = [indices[j::cores] for j in range(cores)]
        parts = [p for p in parts if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(
            delayed(_eval_indices)(null, n, sb, p) for p in parts)
        by_idx = {}
        for p, r in zip(parts, res):
            for i, row in zip(p, r):
                by_idx[i] = row
        return [by_idx[i] for i in indices]
    return batch_fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sim", type=int, default=5000)
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.DEFAULT_MAX_SECONDS)
    a = ap.parse_args()
    resume = ("python experiments/audit7_kappa2_validation.py --n-sim %d "
              "--cores %d --max-seconds %.0f" % (a.n_sim, a.cores, a.max_seconds))

    cells = [(null, n) for null in NULLS for n in N_GRID]
    bases = {"%s_n%d" % (null, n): C.seed_base(SEED_FAMILY, NULLS.index(null) * 3
                                               + N_GRID.index(n))
             for null, n in cells}
    overlap = C.seed_overlap_report(bases, a.n_sim)
    if overlap["exact_collisions"] or overlap["overlapping_pairs"]:
        raise SystemExit("semillas solapadas: %s" % overlap)

    acc_exact = C.binomial_acceptance_region(a.n_sim)
    print("=" * 76)
    print("  A7 / Bloque 1a - validacion de kappa_2")
    print("  N_sim=%d  cores=%d  tope=%.2f h" % (a.n_sim, a.cores, a.max_seconds / 3600))
    print("  region de la compuerta: [%.4f, %.4f]   (exacta binomial: [%.4f, %.4f])"
          % (GATE_REGION + acc_exact))
    print("  semillas: %d celdas, %d bases distintas, %d pares solapados"
          % (overlap["n_cells"], overlap["distinct_seed_bases"],
             overlap["overlapping_pairs"]))
    print("=" * 76)

    t_block = time.time()
    # Calentamiento del pool de loky. Sin esto la sonda de la primera celda
    # cronometra el arranque de 14 procesos y la importacion de statsmodels:
    # en la primera corrida proyecto 0.37 h para una celda que tardo segundos.
    Parallel(n_jobs=a.cores, backend="loky")(
        delayed(_eval_indices)("rw", 200, C.seed_base(SEED_FAMILY, 99), [0])
        for _ in range(a.cores))
    out_cells, stopped = {}, None
    for null, n in cells:
        tag = "%s_n%d" % (null, n)
        sb = bases[tag]
        print("\n[CELDA] %s  seed_base=%d" % (tag, sb))
        try:
            rows, info = C.run_cell_batched(
                tag, a.n_sim, make_batch_fn(null, n, sb, a.cores), CKPT,
                a.cores, t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            stopped = str(exc)
            print("  [TOPE] " + stopped)
            break
        k2 = np.array([r[0] for r in rows])
        lags = np.array([r[1] for r in rows])
        nan = int(np.isnan(k2).sum())
        ok = k2[~np.isnan(k2)]
        rec = {"null": null, "n": n, "n_sim": a.n_sim, "seed_base": sb,
               "nan_statistics": nan, "mean_adf_lag": float(lags.mean()),
               "kappa2_quantiles": {q: float(np.quantile(ok, float(q)))
                                    for q in ("0.90", "0.95", "0.99")},
               "levels": {}}
        for lvl, cv in sorted(KAPPA2_CRITICAL.items()):
            rej = int((ok > cv).sum())            # NaN cuenta como no rechazo
            lo, hi = C.clopper_pearson(rej, a.n_sim)
            rec["levels"]["%.2f" % lvl] = {"critical_value": cv, "rejections": rej,
                                           "rate": rej / a.n_sim,
                                           "ci_lower": lo, "ci_upper": hi}
        r5 = rec["levels"]["0.05"]["rate"]
        rec["in_gate_region"] = bool(GATE_REGION[0] <= r5 <= GATE_REGION[1])
        rec.update(info)
        out_cells[tag] = rec
        print("  tamano 5%%: %.4f  IC [%.4f, %.4f]  -> %s   | 10%%: %.4f  1%%: %.4f"
              "  | q95 kappa2=%.3f (vc 1.358)  NaN=%d  rezago ADF medio %.2f"
              % (r5, rec["levels"]["0.05"]["ci_lower"], rec["levels"]["0.05"]["ci_upper"],
                 "DENTRO" if rec["in_gate_region"] else "FUERA",
                 rec["levels"]["0.10"]["rate"], rec["levels"]["0.01"]["rate"],
                 rec["kappa2_quantiles"]["0.95"], nan, rec["mean_adf_lag"]))

    failed = [t for t, r in out_cells.items() if not r["in_gate_region"]]
    complete = (len(out_cells) == len(cells)) and stopped is None
    if complete:
        verdict = "PASA" if len(failed) <= MAX_FAILED_CELLS else "FALLA"
    else:
        verdict = "INCOMPLETA"

    result = {
        "provenance": C.provenance(
            dgp="kappa2_null_validation", n_sim=a.n_sim,
            seed_formula="91*10^8 + (3*null_idx + n_idx)*10^5; rng=default_rng(seed_base+i)",
            nulls={"rw": "paseo aleatorio gaussiano homoscedastico",
                   "ar093": "AR(1) rho=0.93 gaussiano homoscedastico"},
            statistic="kappa_2 sobre residuos MCO de ADF(c, AIC)",
            hac="Bartlett, L=floor(4*(T/100)^(2/9))"),
        "gate": {"region": list(GATE_REGION),
                 "exact_binomial_region": list(acc_exact),
                 "max_failed_cells": MAX_FAILED_CELLS,
                 "failed_cells": failed, "verdict": verdict,
                 "complete": complete},
        "seed_overlap": overlap,
        "cells": out_cells,
        "block_elapsed_sec": round(time.time() - t_block, 1),
    }
    if stopped:
        result["stopped"] = stopped
    C.atomic_write_json(OUT, result)

    print("\n" + "=" * 76)
    print("  COMPUERTA kappa_2: %s   celdas fuera: %d %s"
          % (verdict, len(failed), failed))
    print("  %s" % OUT)
    print("=" * 76)
    return 0 if verdict == "PASA" else (3 if verdict == "FALLA" else 2)


if __name__ == "__main__":
    sys.exit(main())
