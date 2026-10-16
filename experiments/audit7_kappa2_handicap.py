"""
Auditoria A7 - Bloque 1 (opcion D): handicap de kappa_2 por persistencia.

Pregunta: si la persistencia deprime la potencia de kappa_2, la union queda con
handicap justo donde vive la prediccion 1 y el test propuesto podria ganar por
un artefacto del comparador. Se mide, no se supone. kappa_2 no lleva bootstrap.

Diseno
------
Para cada celda (n, rho, r) con r > 1 de la rejilla de DGP 5:
  AR  : AR(1) rho con quiebre de varianza r            (celda de DGP 5)
  RW  : paseo aleatorio con el MISMO quiebre r           (DGP 3)
Ambas series usan la MISMA semilla (seed_base de la celda de DGP 5). Como
generate_ar1_break_variance y generate_rw_break_variance extraen las
innovaciones en el mismo orden, las innovaciones son identicas y lo unico que
cambia es rho: la persistencia queda aislada exactamente. Es un solape de
semillas DELIBERADO (numeros aleatorios comunes) para un contraste pareado.

kappa_2 se evalua al valor critico simulado de su n (kappa2_simcv_audit7.json).

Alcance: n=200 es lo requerido (3 rho x r in {2,3,4}); se anaden n=500 con la
misma rejilla y las celdas de confirmacion n=1000, porque la lectura honesta de
respaldo descansa en esos n y su premisa es que alli no hay handicap.
Segunda enmienda: se anade la extension de quiebres debiles (r in
D.DGP5_RATIOS_WEAK, n in {200, 500}) con el mismo criterio; el handicap de la
extension se declara por n sobre RO.EXTENSION_P1 y se registra aparte. Las
celdas ya calculadas se leen de sus checkpoints sin cambios.

Criterio registrado en la enmienda ANTES de medir
--------------------------------------------------
Handicap en una celda si, a la vez:
  (i)  McNemar exacto sobre los pares discordantes da p < 0.05 con la potencia
       bajo RW por encima de la potencia bajo AR, y
  (ii) el deficit relativo (pot_RW - pot_AR) / pot_RW es >= 0.10.
Handicap DECLARADO para un n si ocurre en al menos una celda del interior de la
prediccion 1: rho in {0.93, 0.95}, r in {2, 3}.

Uso:
  python experiments/audit7_kappa2_handicap.py --cores 14 --max-seconds 1800
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed
from scipy.stats import binomtest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_readout as RO                                 # noqa: E402
from audit7_kappa2 import KAPPA2_CRITICAL, kappa2_on_adf_residuals  # noqa: E402
from power_comparison import generate_rw_break_variance      # noqa: E402

OUT = os.path.join(C.RESULTS, "kappa2_handicap_audit7.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit7_kappa2_handicap")
SIMCV = os.path.join(C.RESULTS, "kappa2_simcv_audit7.json")
N_SIM = D.DGP5_N_SIM
RATIOS = (2.0, 3.0, 4.0)
# Criterio tomado de audit7_readout.py, la misma fuente que cita la enmienda
INTERIOR = RO.INTERIOR_P1
MCNEMAR_ALPHA = RO.HANDICAP_ALPHA
REL_SHORTFALL_MIN = RO.HANDICAP_REL_SHORTFALL_MIN


def cells():
    out = [(200, rho, r, "requerido") for rho in D.DGP5_RHOS for r in RATIOS]
    out += [(500, rho, r, "extension") for rho in D.DGP5_RHOS for r in RATIOS]
    out += [(n, rho, r, "extension") for (n, rho, r) in D.DGP5_CONFIRM]
    out += [(n, rho, r, "extension_enmienda2") for (n, rho, r) in D.dgp5_cells_weak()]
    return out


def cell_key(n, rho, r):
    return "n%d_rho%.2f_r%s" % (n, rho, D.fmt_r(r))


def generate(kind, n, rho, r, rng):
    if kind == "ar":
        return D.generate_dgp5(n, rho, r, rng)
    return generate_rw_break_variance(n=n, ratio=r, rng=rng)


def _rows(kind, n, rho, r, sb, indices):
    out = []
    for i in indices:
        k2, lag, _ = kappa2_on_adf_residuals(generate(kind, n, rho, r, np.random.default_rng(sb + i)))
        out.append([k2, float(lag)])
    return out


def make_batch_fn(kind, n, rho, r, sb, cores):
    def batch_fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(
            delayed(_rows)(kind, n, rho, r, sb, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return batch_fn


def innovation_pairing_proof(n, rho, r, sb, n_check=50):
    """AR y RW con la misma semilla deben tener innovaciones identicas."""
    worst = 0.0
    for i in range(n_check):
        y_ar = generate("ar", n, rho, r, np.random.default_rng(sb + i))
        y_rw = generate("rw", n, rho, r, np.random.default_rng(sb + i))
        e_ar = y_ar[1:] - rho * y_ar[:-1]
        e_rw = np.diff(y_rw)
        worst = max(worst, float(np.max(np.abs(e_ar - e_rw))))
    return worst


def power(values, cv):
    k = int((values > cv).sum())
    lo, hi = C.clopper_pearson(k, values.size)
    return {"rejections": k, "n": int(values.size), "rate": k / values.size,
            "ci_lower": lo, "ci_upper": hi}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=1800.0)
    a = ap.parse_args()
    resume = ("python experiments/audit7_kappa2_handicap.py --cores %d --max-seconds %.0f"
              % (a.cores, a.max_seconds))

    with open(SIMCV, encoding="utf-8") as f:
        simcv = json.load(f)
    cv_sim = {int(n): c["simulated_critical_values"]["0.05"] for n, c in simcv["cells"].items()}

    print("=" * 78)
    print("  A7 / Bloque 1 - handicap de kappa_2 por persistencia (N_sim=%d)" % N_SIM)
    print("  valores criticos simulados: %s" % {n: round(v, 4) for n, v in cv_sim.items()})
    print("=" * 78)

    t_block = time.time()
    Parallel(n_jobs=a.cores, backend="loky")(          # calentamiento del pool
        delayed(_rows)("ar", 200, 0.93, 2.0, C.seed_base(D.FAM_DGP5, 999), [0])
        for _ in range(a.cores))

    results, proofs = {}, {}
    for (n, rho, r, scope) in cells():
        sb = D.dgp5_seed_base(n, rho, r)
        proof = innovation_pairing_proof(n, rho, r, sb)
        proofs[cell_key(n, rho, r)] = proof
        if proof > 1e-9:
            raise SystemExit("innovaciones AR/RW no pareadas en %s: %.3e"
                             % (cell_key(n, rho, r), proof))
        vals = {}
        for kind in ("ar", "rw"):
            tag = "k2h_%s_%s" % (kind, cell_key(n, rho, r))
            print("\n[CELDA] %s  seed_base=%d" % (tag, sb))
            try:
                rows, info = C.run_cell_batched(tag, N_SIM, make_batch_fn(kind, n, rho, r, sb, a.cores),
                                                CKPT, a.cores, t_block, a.max_seconds, resume)
            except C.BudgetExhausted as exc:
                print("  [TOPE] %s" % exc)
                return 2
            v = np.array([row[0] for row in rows])
            if np.isnan(v).any():
                raise SystemExit("%s: %d NaN" % (tag, np.isnan(v).sum()))
            vals[kind] = v

        cv = cv_sim[n]
        rej_ar, rej_rw = vals["ar"] > cv, vals["rw"] > cv
        b = int((rej_ar & ~rej_rw).sum())            # rechaza AR, no RW
        c = int((~rej_ar & rej_rw).sum())            # rechaza RW, no AR
        p_mc = float(binomtest(min(b, c), b + c, 0.5).pvalue) if b + c > 0 else 1.0
        p_ar, p_rw = power(vals["ar"], cv), power(vals["rw"], cv)
        diff = p_rw["rate"] - p_ar["rate"]
        rel = diff / p_rw["rate"] if p_rw["rate"] > 0 else 0.0
        handicap = bool(p_mc < MCNEMAR_ALPHA and diff > 0 and rel >= REL_SHORTFALL_MIN)
        key = cell_key(n, rho, r)
        results[key] = {
            "n": n, "rho": rho, "r": r, "scope": scope,
            "interior_prediction_1": (rho, r) in INTERIOR,
            "extension_prediction_1": (rho, r) in RO.EXTENSION_P1,
            "shared_seed_base": sb, "simulated_cv": cv,
            "power_ar_break": p_ar, "power_rw_break": p_rw,
            "power_nominal_1.358": {"ar": power(vals["ar"], KAPPA2_CRITICAL[0.05]),
                                    "rw": power(vals["rw"], KAPPA2_CRITICAL[0.05])},
            "diff_rw_minus_ar": diff, "relative_shortfall": rel,
            "mcnemar": {"ar_only": b, "rw_only": c, "p_value": p_mc},
            "handicap_cell": handicap}
        print("  potencia AR=%.4f  RW=%.4f  deficit=%.4f (rel %.1f%%)  McNemar p=%.2e  -> %s%s"
              % (p_ar["rate"], p_rw["rate"], diff, 100 * rel, p_mc,
                 "HANDICAP" if handicap else "sin handicap",
                 "  [interior]" if (rho, r) in INTERIOR else ""))

    declared = {}
    for n in sorted({v["n"] for v in results.values()}):
        inner = [k for k, v in results.items() if v["n"] == n and v["interior_prediction_1"]]
        hits = [k for k in inner if results[k]["handicap_cell"]]
        declared[str(n)] = {"interior_cells": inner, "handicap_cells": hits,
                            "handicap_declared": bool(hits)}
    declared_ext = {}
    for n in sorted({v["n"] for v in results.values() if v["extension_prediction_1"]}):
        inner = [k for k, v in results.items() if v["n"] == n and v["extension_prediction_1"]]
        hits = [k for k in inner if results[k]["handicap_cell"]]
        declared_ext[str(n)] = {"extension_cells": inner, "handicap_cells": hits,
                                "handicap_declared": bool(hits)}

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="kappa2_persistence_handicap", n_sim=N_SIM,
            seed_formula=("AR: seed_base de la celda de DGP 5 (60*10^8 + idx*10^5); "
                          "RW: la MISMA semilla, pareo deliberado de innovaciones"),
            critical_values_source="kappa2_simcv_audit7.json"),
        "criterion": {"mcnemar_alpha": MCNEMAR_ALPHA,
                      "relative_shortfall_min": REL_SHORTFALL_MIN,
                      "interior_prediction_1": sorted([list(x) for x in INTERIOR]),
                      "declared_if": "handicap en al menos una celda del interior de ese n",
                      "extension_prediction_1": sorted([list(x) for x in RO.EXTENSION_P1]),
                      "declared_if_extension": "handicap en al menos una celda de la extension de ese n"},
        "innovation_pairing_max_abs_diff": proofs,
        "declared_by_n": declared,
        "declared_by_n_extension": declared_ext,
        "cells": results,
        "block_elapsed_sec": round(time.time() - t_block, 1),
    })
    print("\n" + "=" * 78)
    for n, d in declared.items():
        print("  n=%s: handicap %s  %s" % (n, "DECLARADO" if d["handicap_declared"] else "no declarado",
                                          d["handicap_cells"]))
    for n, d in declared_ext.items():
        print("  n=%s extension: handicap %s  %s" % (n, "DECLARADO" if d["handicap_declared"] else "no declarado",
                                                    d["handicap_cells"]))
    print("  %s" % OUT)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
