"""
Auditoria A7 - Bloque 1 (compuerta): kappa_2 con valor critico SIMULADO.

Decision 2 de la especificacion revisada. La compuerta nominal fallo en 6 de 6
celdas por conservadurismo de muestra finita (kappa2_validation_audit7.json).
En lugar de retirar kappa_2 se le aplica la misma metodologia que la Definicion 1
aplica al estadistico propuesto: la ley nula se calibra por simulacion.

1. Valor critico simulado: cuantil 0.95 de kappa_2 sobre N_cal = 5000 replicas
   del paseo aleatorio gaussiano homoscedastico (el conjunto de calibracion del
   Bloque 1, familia 70), para cada n in {200, 500, 1000}.
2. Verificacion en muestra: el tamano sobre ese mismo conjunto debe ser 0.05
   exacto por construccion.
3. Verificacion FUERA de muestra (compuerta): sobre la segunda nula del Bloque
   1a, AR(1) rho=0.93 homoscedastico (familia 91, checkpoints commiteados), el
   tamano al valor critico simulado debe caer en [0.0440, 0.0562] en las tres n.
   Si falla, el proceso se detiene y se avisa antes de seguir.
4. Comprobacion adicional, no compuerta: el paseo aleatorio independiente del
   Bloque 1a (familia 91) al mismo valor critico.

Uso:
  python experiments/audit7_kappa2_simcv.py --cores 14 --max-seconds 14400
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                  # noqa: E402
import audit7_design as D                                  # noqa: E402
from audit7_kappa2 import KAPPA2_CRITICAL, kappa2_on_adf_residuals  # noqa: E402

OUT = os.path.join(C.RESULTS, "kappa2_simcv_audit7.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit7_calibration_kappa2")
VALID_CKPT = os.path.join(C.CKPT_ROOT, "audit7_kappa2_validation")
GATE_REGION = (0.0440, 0.0562)


def _kappa2_indices(n, sb, indices):
    rows = []
    for i in indices:
        y = D.generate_calibration(n, np.random.default_rng(sb + i))
        k2, lag, T = kappa2_on_adf_residuals(y)
        rows.append([k2, float(lag), float(T)])
    return rows


def make_batch_fn(n, sb, cores):
    def batch_fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(
            delayed(_kappa2_indices)(n, sb, p) for p in parts)
        by_idx = {}
        for p, r in zip(parts, res):
            by_idx.update(zip(p, r))
        return [by_idx[i] for i in indices]
    return batch_fn


def load_validation_values(null, n):
    """kappa_2 por serie de los checkpoints commiteados del Bloque 1a."""
    files = sorted(glob.glob(os.path.join(VALID_CKPT, "%s_n%d_i*_k*.json" % (null, n))))
    chunks = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if d.get("complete") is not True:
            raise RuntimeError("lote incompleto en %s" % f)
        chunks.append(d)
    chunks.sort(key=lambda d: d["i0"])
    vals, expected_i0 = [], 0
    for d in chunks:
        if d["i0"] != expected_i0:
            raise RuntimeError("%s_n%d: hueco de lotes en i0=%d" % (null, n, expected_i0))
        vals.extend(r[0] for r in d["rows"])
        expected_i0 += d["k"]
    return np.asarray(vals, dtype=float), {
        os.path.relpath(f, C.REPO).replace(os.sep, "/"): C._sha256_file(f) for f in files}


def rate_above(values, cv):
    ok = values[~np.isnan(values)]
    k = int((ok > cv).sum())
    lo, hi = C.clopper_pearson(k, values.size)
    return {"rejections": k, "n": int(values.size), "rate": k / values.size,
            "ci_lower": lo, "ci_upper": hi, "nan": int(np.isnan(values).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.DEFAULT_MAX_SECONDS)
    a = ap.parse_args()
    resume = ("python experiments/audit7_kappa2_simcv.py --cores %d --max-seconds %.0f"
              % (a.cores, a.max_seconds))

    bases = D.all_seed_bases()
    overlap = C.seed_overlap_report(bases, D.N_CAL)
    if overlap["exact_collisions"] or overlap["overlapping_pairs"]:
        raise SystemExit("semillas solapadas en el diseno del Bloque 1: %s" % overlap)

    print("=" * 78)
    print("  A7 / Bloque 1 - compuerta de kappa_2 con valor critico simulado")
    print("  N_cal=%d  cores=%d  region fuera de muestra [%.4f, %.4f]"
          % ((D.N_CAL, a.cores) + GATE_REGION))
    print("=" * 78)

    t_block = time.time()
    Parallel(n_jobs=a.cores, backend="loky")(          # calentamiento del pool
        delayed(_kappa2_indices)(200, C.seed_base(D.FAM_CALIBRATION, 999), [0])
        for _ in range(a.cores))

    cells, source_files = {}, {}
    for n in D.CAL_N_GRID:
        tag, sb = D.cal_tag(n), D.cal_seed_base(n)
        print("\n[CALIBRACION] %s  seed_base=%d" % (tag, sb))
        try:
            rows, info = C.run_cell_batched(tag, D.N_CAL, make_batch_fn(n, sb, a.cores),
                                            CKPT, a.cores, t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc)
            return 2
        cal = np.array([r[0] for r in rows])
        if np.isnan(cal).any():
            raise SystemExit("%s: %d valores NaN en la calibracion" % (tag, np.isnan(cal).sum()))
        cv = {lvl: float(np.quantile(cal, 1.0 - lvl)) for lvl in sorted(KAPPA2_CRITICAL)}
        in_sample = rate_above(cal, cv[0.05])

        ar, f_ar = load_validation_values("ar093", n)
        rw, f_rw = load_validation_values("rw", n)
        source_files.update(f_ar)
        source_files.update(f_rw)
        if ar.size != D.N_CAL or rw.size != D.N_CAL:
            raise SystemExit("n=%d: tamanos inesperados AR=%d RW=%d" % (n, ar.size, rw.size))
        ar_sim = rate_above(ar, cv[0.05])
        rw_sim = rate_above(rw, cv[0.05])
        ar_sim["in_gate_region"] = bool(GATE_REGION[0] <= ar_sim["rate"] <= GATE_REGION[1])

        cells[str(n)] = {
            "n": n, "calibration_seed_base": sb, "n_cal": D.N_CAL,
            "simulated_critical_values": {"%.2f" % k: v for k, v in cv.items()},
            "asymptotic_critical_values": {"%.2f" % k: v for k, v in KAPPA2_CRITICAL.items()},
            "in_sample_size_at_simulated_cv": in_sample,
            "out_of_sample_ar093_at_simulated_cv": ar_sim,
            "out_of_sample_rw_family91_at_simulated_cv": rw_sim,
            "nominal_rates_at_1.358": {
                "calibration_rw": rate_above(cal, KAPPA2_CRITICAL[0.05]),
                "ar093_family91": rate_above(ar, KAPPA2_CRITICAL[0.05]),
                "rw_family91": rate_above(rw, KAPPA2_CRITICAL[0.05])},
            **info}
        print("  valor critico simulado 5%%: %.4f  (asintotico 1.358)" % cv[0.05])
        print("  en muestra (RW calibracion): %.4f  (%d/%d)"
              % (in_sample["rate"], in_sample["rejections"], in_sample["n"]))
        print("  FUERA de muestra AR(0.93):   %.4f  IC [%.4f, %.4f]  -> %s"
              % (ar_sim["rate"], ar_sim["ci_lower"], ar_sim["ci_upper"],
                 "DENTRO" if ar_sim["in_gate_region"] else "FUERA"))
        print("  fuera de muestra RW fam. 91: %.4f  IC [%.4f, %.4f]  (informativo)"
              % (rw_sim["rate"], rw_sim["ci_lower"], rw_sim["ci_upper"]))

    exact = all(c["in_sample_size_at_simulated_cv"]["rejections"] == round(0.05 * D.N_CAL)
                for c in cells.values())
    failed = [n for n, c in cells.items()
              if not c["out_of_sample_ar093_at_simulated_cv"]["in_gate_region"]]
    verdict = "PASA" if (not failed and exact) else "FALLA"

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="kappa2_simulated_critical_value", n_sim=D.N_CAL,
            seed_formula="70*10^8 + n_idx*10^5 (calibracion); AR y RW de contraste: familia 91",
            null="paseo aleatorio gaussiano homoscedastico (nula compuesta)",
            quantile_method="numpy.quantile, interpolacion lineal, nivel 1-alpha",
            source_checkpoints=source_files),
        "gate": {"region": list(GATE_REGION), "failed_n": failed,
                 "in_sample_exact_0.05_all_n": exact, "verdict": verdict},
        "seed_overlap_block1_design": overlap,
        "cells": cells,
        "block_elapsed_sec": round(time.time() - t_block, 1),
    })
    print("\n" + "=" * 78)
    print("  COMPUERTA kappa_2 (valor critico simulado): %s   fuera: %s   exacto en muestra: %s"
          % (verdict, failed, exact))
    print("  %s" % OUT)
    print("=" * 78)
    return 0 if verdict == "PASA" else 3


if __name__ == "__main__":
    sys.exit(main())
