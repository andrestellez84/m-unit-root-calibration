"""
Tarea R3 — Colas pesadas: regenerando la Tabla 2 con semillas originales.
seed_base = 900000 + n*100 + df*10.
Innovaciones t(5) y t(3) reescaladas a varianza unitaria.
N_cal = 50,000, seed 42. N_sim = 5,000.
R in {0.25, 0.50, 0.75}, DF-GLS, ADF, PP, KPSS.
Both pilots: alpha1 and alpha2.
"""

import sys
import os
import time
import json
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*InterpolationWarning.*")

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from experiments.size_robustness_heavy_tails import (
    generate_rw_heavy,
    run_adf,
    run_pp,
    run_kpss_test,
    DISTRIBUTIONS,
    ci_wilson,
    THETA,
    C_1,
    C_2,
    N_GRID,
)
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.empirical_eigenvalues import build_null_cdf
from arch.unitroot import DFGLS

RESULTS_DIR = "experiments/results"
R_VALS = {
    "R025": 0.25,
    "R050": 0.50,
    "R075": 0.75,
}


def run_dfgls(Y):
    try:
        return DFGLS(Y, trend="c").pvalue
    except Exception:
        return 1.0


def run_r3():
    t_start = time.time()
    print("=" * 70)
    print("  Tarea R3: Colas Pesadas (Tabla 2) — Regeneración exacta con semillas del paper")
    print(f"  N_sim=5000, N_cal=50000, n in {N_GRID}")
    print("=" * 70)

    # Precalculate Gaussian CDFs for each (R, n)
    print("\nPrecalibrating null CDFs (N_cal=50000, seed=42)...")
    cdfs = {}
    for r_name, r_val in R_VALS.items():
        for n in N_GRID:
            t0 = time.time()
            cdfs[(r_name, n)] = build_null_cdf(THETA, r_val, n, N_cal=50000, seed=42)
            print(f"  R={r_val:.2f}, n={n}: {time.time() - t0:.1f}s")

    results = {
        "metadata": {
            "N_cal": 50000,
            "cal_seed": 42,
            "N_sim": 5000,
            "seed_formula": "900000 + n*100 + df*10",
            "alpha": 0.05,
            "exact_acceptance_interval": [0.0440, 0.0562],
        },
        "alpha1": {},
        "alpha2": {},
    }

    for dist_name, dist_params in DISTRIBUTIONS.items():
        df = dist_params["df"]
        scale = dist_params["scale"]
        print(f"\n{'=' * 70}")
        print(f"  Distribution: {dist_name} (df={df}, scale={scale:.4f})")
        print(f"{'=' * 70}")

        results["alpha1"][dist_name] = {}
        results["alpha2"][dist_name] = {}

        for n in N_GRID:
            t0 = time.time()
            seed_base = 900000 + n * 100 + df * 10
            tau_1 = max(2, min(int(round(THETA[0] * n)), n // 2))
            tau_2 = max(2, min(int(round(THETA[1] * n)), n // 2))

            rejs = {
                "alpha1": {r_name: 0 for r_name in R_VALS},
                "alpha2": {r_name: 0 for r_name in R_VALS},
                "adf": 0,
                "pp": 0,
                "kpss": 0,
                "dfgls": 0,
            }

            for i in range(5000):
                rng = np.random.default_rng(seed_base + i)
                Y = generate_rw_heavy(n, df, scale, rng)

                # Baselines
                if run_adf(Y) < 0.05:
                    rejs["adf"] += 1
                if run_pp(Y) < 0.05:
                    rejs["pp"] += 1
                if run_kpss_test(Y) < 0.05:
                    rejs["kpss"] += 1
                if run_dfgls(Y) < 0.05:
                    rejs["dfgls"] += 1

                # Our tests
                means = rolling_mean(Y, tau_1)
                g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
                variances = rolling_var(Y, tau_2)
                g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))
                diffs = np.diff(Y)

                for pilot in ["alpha1", "alpha2"]:
                    s2 = hac_newey_west(diffs, andrews_pilot=pilot)
                    s = np.sqrt(s2)
                    g1s = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
                    g2s = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0

                    for r_name, r_val in R_VALS.items():
                        stat = np.sqrt((1.0 - r_val) ** 2 * g1s ** 2 + r_val ** 2 * g2s ** 2)
                        cdf_func = cdfs[(r_name, n)]
                        p = float(np.clip(cdf_func(stat), 0.0, 1.0))
                        if p < 0.05:
                            rejs[pilot][r_name] += 1

            for pilot in ["alpha1", "alpha2"]:
                cell = {
                    "ours_R025": rejs[pilot]["R025"] / 5000,
                    "ours_R025_ci": ci_wilson(rejs[pilot]["R025"] / 5000, 5000),
                    "ours_R050": rejs[pilot]["R050"] / 5000,
                    "ours_R050_ci": ci_wilson(rejs[pilot]["R050"] / 5000, 5000),
                    "ours_R075": rejs[pilot]["R075"] / 5000,
                    "ours_R075_ci": ci_wilson(rejs[pilot]["R075"] / 5000, 5000),
                    "adf": rejs["adf"] / 5000,
                    "adf_ci": ci_wilson(rejs["adf"] / 5000, 5000),
                    "pp": rejs["pp"] / 5000,
                    "pp_ci": ci_wilson(rejs["pp"] / 5000, 5000),
                    "dfgls": rejs["dfgls"] / 5000,
                    "dfgls_ci": ci_wilson(rejs["dfgls"] / 5000, 5000),
                    "kpss": rejs["kpss"] / 5000,
                    "kpss_ci": ci_wilson(rejs["kpss"] / 5000, 5000),
                }
                results[pilot][dist_name][str(n)] = cell

            print(f"  n={n} ({time.time() - t0:.1f}s): "
                  f"ADF={rejs['adf']/5000:.4f}, DFGLS={rejs['dfgls']/5000:.4f} | "
                  f"a1 R50={rejs['alpha1']['R050']/5000:.4f}, a2 R50={rejs['alpha2']['R050']/5000:.4f}")

    out_path = os.path.join(RESULTS_DIR, "size_robustness_heavy_tails_audit5b.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {out_path}")

    # Control Assertions
    print("\n" + "=" * 70)
    print("  VERIFICACIÓN DE CONTROLES (Tabla 2)")
    print("=" * 70)

    # 1. ADF t(5) n=200
    adf_t5_200 = results["alpha1"]["t5"]["200"]["adf"]
    print(f"ADF t(5) n=200: {adf_t5_200:.4f} (target: 0.0628)")
    assert abs(adf_t5_200 - 0.0628) < 1e-6, f"Fallo en semilla: ADF t(5) n=200 dio {adf_t5_200}"

    # 2. Controls alpha1 R=0.5: t(5): 0.0368 / 0.0456 / 0.0518
    t5_a1_200 = results["alpha1"]["t5"]["200"]["ours_R050"]
    t5_a1_500 = results["alpha1"]["t5"]["500"]["ours_R050"]
    t5_a1_1000 = results["alpha1"]["t5"]["1000"]["ours_R050"]
    print(f"alpha1 t(5) R=0.5: {t5_a1_200:.4f} / {t5_a1_500:.4f} / {t5_a1_1000:.4f} (target: 0.0368 / 0.0456 / 0.0518)")
    assert abs(t5_a1_200 - 0.0368) < 1e-6
    assert abs(t5_a1_500 - 0.0456) < 1e-6
    assert abs(t5_a1_1000 - 0.0518) < 1e-6

    # 3. Controls alpha1 R=0.5: t(3): 0.0404 / 0.0464 / 0.0530
    t3_a1_200 = results["alpha1"]["t3"]["200"]["ours_R050"]
    t3_a1_500 = results["alpha1"]["t3"]["500"]["ours_R050"]
    t3_a1_1000 = results["alpha1"]["t3"]["1000"]["ours_R050"]
    print(f"alpha1 t(3) R=0.5: {t3_a1_200:.4f} / {t3_a1_500:.4f} / {t3_a1_1000:.4f} (target: 0.0404 / 0.0464 / 0.0530)")
    assert abs(t3_a1_200 - 0.0404) < 1e-6
    assert abs(t3_a1_500 - 0.0464) < 1e-6
    assert abs(t3_a1_1000 - 0.0530) < 1e-6

    # 4. Celda en negrita que cambia: t(5) n=500 alpha2 da 0.0464 vs 0.0456
    t5_a2_500 = results["alpha2"]["t5"]["500"]["ours_R050"]
    print(f"alpha2 t(5) n=500 R=0.5: {t5_a2_500:.4f} (target: 0.0464)")
    assert abs(t5_a2_500 - 0.0464) < 1e-6

    print("\nTODOS LOS CONTROLES DE LA TAREA R3 PASARON A LA PERFECCIÓN.")
    print(f"Tarea R3 total time: {time.time() - t_start:.1f}s")


if __name__ == "__main__":
    run_r3()
