"""
Auditoria A7 - Bloque 1a (diagnostico): descomposicion del infra-dimensionamiento
de kappa_2.

Una comprobacion previa mostro que kappa_2 rechaza menos del 5% al valor critico
1.358 incluso sobre ruido iid gaussiano (0.029 a T=200, 0.039 a T=2000). Antes
de atribuir la discrepancia a nada, se aisla cada fuente posible anadiendo un
ingrediente del estadistico a la vez. Todas las variantes usan el mismo puente
de sumas parciales y comparan su supremo con el mismo valor critico:

  V1  incrementos N(0,1), varianza CONOCIDA (=1)
        -> aisla la discretizacion del supremo del puente browniano
  V2  incrementos e_t^2 con e_t ~ N(0,1), varianza CONOCIDA (=2)
        -> anade la asimetria de los incrementos chi-cuadrado
  V3  como V2 pero con varianza ESTIMADA por la varianza muestral (L = 0)
        -> anade la estimacion de escala
  V4  kappa_2 completo: varianza de largo plazo Bartlett, L = floor(4(T/100)^{2/9})
        -> anade los rezagos del HAC

Si V1 ya esta por debajo de 0.05, parte del infra-dimensionamiento es propio de
la ley asintotica usada a muestra finita y no un error de implementacion.

Semillas: familia 92, seed_base = 92*10^8 + indice_celda*10^5; cada bloque de
replicas usa default_rng(seed_base + indice_de_bloque).
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                               # noqa: E402
from audit7_kappa2 import (KAPPA2_CRITICAL, bartlett_long_run_variance,  # noqa: E402
                           newey_west_bandwidth)

OUT = os.path.join(C.RESULTS, "kappa2_diagnosis_audit7.json")
SEED_FAMILY = 92
T_GRID = (200, 500, 1000, 5000)
VARIANTS = ("V1_normal_known_var", "V2_chisq_known_var",
            "V3_chisq_sample_var", "V4_kappa2_full")
REPS = 20000
CHUNK = 1000


def sup_bridge(inc, scale):
    """max_k |S_k - (k/T) S_T| / sqrt(T * scale), fila a fila.

    scale se aplana a un vector de una entrada por fila. En la primera version
    V3 y V4 pasaban escalas de forma (R, 1) contra maximos de forma (R,), y
    numpy difundia el cociente a una matriz R x R que mezclaba el maximo de
    cada fila con la varianza de todas las demas.
    """
    R, T = inc.shape
    S = np.cumsum(inc, axis=1)
    k = np.arange(1, T + 1, dtype=float)
    D = S - (k / T) * S[:, -1:]
    scale = np.broadcast_to(np.asarray(scale, dtype=float).reshape(-1), (R,))
    out = np.max(np.abs(D), axis=1) / np.sqrt(T * scale)
    if out.shape != (R,):
        raise RuntimeError("sup_bridge: forma %s, esperaba (%d,)" % (out.shape, R))
    return out


def run_variant(variant, T, sb):
    stats = []
    for b in range(REPS // CHUNK):
        rng = np.random.default_rng(sb + b)
        z = rng.standard_normal((CHUNK, T))
        if variant == "V1_normal_known_var":
            stats.append(sup_bridge(z, 1.0))
        elif variant == "V2_chisq_known_var":
            stats.append(sup_bridge(z * z, 2.0))
        elif variant == "V3_chisq_sample_var":
            u = z * z
            stats.append(sup_bridge(u, u.var(axis=1, keepdims=True)))
        elif variant == "V4_kappa2_full":
            u = z * z
            L = newey_west_bandwidth(T)
            uc = u - u.mean(axis=1, keepdims=True)
            lrv = np.array([bartlett_long_run_variance(row, L) for row in uc])
            stats.append(sup_bridge(u, lrv[:, None]))
    return np.concatenate(stats)


def main():
    cells = [(v, T) for v in VARIANTS for T in T_GRID]
    bases = {"%s_T%d" % (v, T): C.seed_base(SEED_FAMILY, i) for i, (v, T) in enumerate(cells)}
    overlap = C.seed_overlap_report(bases, REPS // CHUNK)
    if overlap["exact_collisions"] or overlap["overlapping_pairs"]:
        raise SystemExit("semillas solapadas: %s" % overlap)

    t0 = time.time()
    res = {}
    print("%-22s %6s %8s %8s %8s %8s" % ("variante", "T", "media", "P>1.224", "P>1.358", "P>1.628"))
    for (v, T) in cells:
        tag = "%s_T%d" % (v, T)
        s = run_variant(v, T, bases[tag])
        rec = {"variant": v, "T": T, "reps": int(s.size), "seed_base": bases[tag],
               "mean": float(s.mean()),
               "mc_se_rate_at_5pct": float(np.sqrt(0.05 * 0.95 / s.size)),
               "rates": {"%.2f" % lvl: float(np.mean(s > cv))
                         for lvl, cv in sorted(KAPPA2_CRITICAL.items())},
               "quantile_0.95": float(np.quantile(s, 0.95))}
        if v == "V4_kappa2_full":
            rec["hac_bandwidth"] = newey_west_bandwidth(T)
        res[tag] = rec
        print("%-22s %6d %8.4f %8.4f %8.4f %8.4f   q95=%.3f"
              % (v, T, rec["mean"], rec["rates"]["0.10"], rec["rates"]["0.05"],
                 rec["rates"]["0.01"], rec["quantile_0.95"]))

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="kappa2_bridge_decomposition", n_sim=REPS,
            seed_formula="92*10^8 + cell_idx*10^5; bloque b usa default_rng(seed_base+b)",
            reference={"E_sup_abs_brownian_bridge": "sqrt(pi/2)*ln(2) = 0.8687",
                       "critical_values": {str(k): v for k, v in KAPPA2_CRITICAL.items()}}),
        "seed_overlap": overlap,
        "cells": res,
        "elapsed_sec": round(time.time() - t0, 1),
    })
    print("\nescrito %s (%.1f s)" % (OUT, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
