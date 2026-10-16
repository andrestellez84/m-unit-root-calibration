"""
Auditoria A6 - Paso 0 de pareo para DGP1 y DGP3.

Demuestra que los generadores inline de audit6_wild_bootstrap_sweep.py producen
trayectorias BIT-A-BIT identicas a las de experiments/power_comparison.py bajo
las formulas de semilla documentadas en power_comparison.py:408 (DGP1) y :496 (DGP3).

Sin esto, las columnas del bootstrap no son comparables celda-a-celda con las
columnas de ADF/PP/DF-GLS/test propuesto ya publicadas.
"""
import os, sys, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments.power_comparison import generate_ar1, generate_rw_break_variance
from experiments.audit6_wild_bootstrap_sweep import (
    generate_dgp1_series, generate_dgp3_series,
)

N_CHECK = 50
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results",
                   "paso0_pairing_audit6.json")

report = {"n_series_checked_per_cell": N_CHECK, "dgp1": {}, "dgp3": {}, "all_pass": True}

print("=" * 72)
print("  PASO 0: pareo bit-a-bit de semillas, DGP1 y DGP3")
print("=" * 72)

# ---- DGP 1: AR(1), seed_base = 100000 + n*100 + int(rho*100)
print("\n--- DGP 1  (power_comparison.py:408) ---")
for n in (200, 500, 1000):
    for rho in (0.95, 0.97, 0.99):
        seed_base = 100000 + n * 100 + int(rho * 100)
        mat = generate_dgp1_series(n, rho, N_CHECK)          # del sweep
        ref = np.column_stack([                               # de power_comparison
            generate_ar1(n=n, rho=rho, rng=np.random.default_rng(seed_base + i))
            for i in range(N_CHECK)
        ])
        identical = bool(np.array_equal(mat, ref))
        max_abs = float(np.max(np.abs(mat - ref)))
        report["dgp1"][f"n{n}_rho{rho:.2f}"] = {
            "seed_base": seed_base, "bitwise_identical": identical, "max_abs_diff": max_abs}
        report["all_pass"] &= identical
        print(f"  n={n:<5} rho={rho:.2f}  seed_base={seed_base:<7} "
              f"identical={identical}  max|diff|={max_abs:.3e}")

# ---- DGP 3: RW con quiebre de varianza, seed_base = 300000 + n*100 + int(r*10)
print("\n--- DGP 3  (power_comparison.py:496) ---")
for n in (200, 1000):
    for r in (1.0, 2.0, 3.0, 4.0):
        seed_base = 300000 + n * 100 + int(r * 10)
        mat = generate_dgp3_series(n, r, N_CHECK)
        ref = np.column_stack([
            generate_rw_break_variance(n=n, ratio=r, rng=np.random.default_rng(seed_base + i))
            for i in range(N_CHECK)
        ])
        identical = bool(np.array_equal(mat, ref))
        max_abs = float(np.max(np.abs(mat - ref)))
        report["dgp3"][f"n{n}_r{r:.1f}"] = {
            "seed_base": seed_base, "bitwise_identical": identical, "max_abs_diff": max_abs}
        report["all_pass"] &= identical
        print(f"  n={n:<5} r={r:.1f}    seed_base={seed_base:<7} "
              f"identical={identical}  max|diff|={max_abs:.3e}")

# ---- Solapamiento de bloques de semillas (numeros aleatorios comunes)
print("\n--- Solapamiento de bloques de semillas (N_sim=2000) ---")
overlaps = {}
for label, base_fn, params, n_grid in (
    ("dgp1", lambda n, p: 100000 + n * 100 + int(p * 100), (0.95, 0.97, 0.99), (200, 500, 1000)),
    ("dgp3", lambda n, p: 300000 + n * 100 + int(p * 10), (1.0, 2.0, 3.0, 4.0), (200, 1000)),
):
    for n in n_grid:
        bases = sorted(base_fn(n, p) for p in params)
        gaps = [bases[i + 1] - bases[i] for i in range(len(bases) - 1)]
        ov = [2000 - g for g in gaps if g < 2000]
        overlaps[f"{label}_n{n}"] = {"seed_bases": bases, "gaps": gaps,
                                     "overlapping_draws": ov}
        print(f"  {label} n={n:<5} bases={bases} gaps={gaps} -> "
              f"solape={ov if ov else 'ninguno'} de 2000")
report["seed_block_overlap"] = overlaps

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("\n" + "=" * 72)
print(f"  VEREDICTO PASO 0: {'PASS' if report['all_pass'] else 'FAIL'}")
print(f"  Guardado en {OUT}")
print("=" * 72)
sys.exit(0 if report["all_pass"] else 1)
