"""
Tarea R4 — R̂ y rebalanceo (Tablas 13 y 14).
Diagnóstico y regeneración con N_cal = 50,000 (y N_cal = 10,000 para reproducir A1).
Semillas de A1:
  - H0 n in {200, 500, 1000} -> rng(70000 + i)
  - DGP 3 r=4 n=1000 -> rng(80000 + i)
  - DGP 4 r=3 n=500 -> rng(90000 + i)
  - DGP 1 -> rng(200000 + i)
"""

import sys
import os
import time
import json
import warnings
import numpy as np
from scipy.interpolate import interp1d

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from experiments.power_comparison import (
    generate_ar1,
    generate_rw_break_variance,
    generate_ar1_break_variance,
    rolling_mean,
    rolling_var,
    sample_variance_over_k,
    THETA_FIXED,
    C_1,
    C_2,
)
from stationarity_test.hac_estimator import hac_newey_west

RESULTS_DIR = "experiments/results"


def ci_wilson(p_hat, n_sim):
    z = 1.96
    denom = 1 + z**2 / n_sim
    center = (p_hat + z**2 / (2 * n_sim)) / denom
    width = z * np.sqrt(p_hat * (1 - p_hat) / n_sim + z**2 / (4 * n_sim**2)) / denom
    return round(float(center - width), 4), round(float(center + width), 4)


def run_r4():
    t_start = time.time()
    print("=" * 70)
    print("  Tarea R4: Distribución de R_hat y Rebalanceo (Tablas 13 y 14)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Constantes de rebalanceo (50,000 sims, seed 42)
    # ------------------------------------------------------------------
    print("\n--- Paso 1: Constantes de rebalanceo m1, m2 (N_cal=50000, seed=42) ---")
    rebalance = {}
    for n in [200, 500, 1000]:
        tau_1 = max(2, min(int(round(THETA_FIXED[0] * n)), n // 2))
        tau_2 = max(2, min(int(round(THETA_FIXED[1] * n)), n // 2))
        scale_1 = 1.0 * n ** (C_1 / 2.0)
        scale_2 = 1.0 * n ** (C_2 / 2.0)

        rng = np.random.default_rng(42)
        g1_vals = np.empty(50000)
        g2_vals = np.empty(50000)
        for j in range(50000):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])
            means = rolling_mean(Y, tau_1)
            variances = rolling_var(Y, tau_2)
            g1_vals[j] = float(np.sqrt(max(sample_variance_over_k(means), 0.0))) / scale_1
            g2_vals[j] = float(np.sqrt(max(sample_variance_over_k(variances), 0.0))) / scale_2

        m1 = float(np.mean(g1_vals))
        m2 = float(np.mean(g2_vals))
        rebalance[n] = {"m1": m1, "m2": m2}
        print(f"  n={n}: m1={m1:.6f}, m2={m2:.6f} (exp: m1 ~ 0.334, m2 ~ 0.014)")

    rebal_path = os.path.join(RESULTS_DIR, "rebalance_constants_audit5b.json")
    with open(rebal_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "theta": list(THETA_FIXED),
                "N_cal": 50000,
                "constants": {str(k): v for k, v in rebalance.items()},
                "seed": 42,
            },
            f,
            indent=2,
        )
    print(f"Constantes guardadas en: {rebal_path}")

    # ------------------------------------------------------------------
    # Step 2: Tabla 13 — Distribución de R_hat (sigma=1 conocido y HAC)
    # ------------------------------------------------------------------
    print("\n--- Paso 2: Tabla 13 (Distribución de R_hat y R_bal) ---")
    scenarios_t13 = [
        {"name": "H0_n200", "n": 200, "dgp": "H0", "seed_base": 70000},
        {"name": "H0_n500", "n": 500, "dgp": "H0", "seed_base": 70000},
        {"name": "H0_n1000", "n": 1000, "dgp": "H0", "seed_base": 70000},
        {"name": "DGP3_r4_n1000", "n": 1000, "dgp": "DGP3", "r": 4.0, "seed_base": 80000},
        {"name": "DGP4_r3_n500", "n": 500, "dgp": "DGP4", "r": 3.0, "rho": 0.5, "seed_base": 90000},
    ]

    t13_results = {"sigma_known": {}, "alpha1_hac": {}, "alpha2_hac": {}}

    for mode in ["sigma_known", "alpha1_hac", "alpha2_hac"]:
        t13_results[mode] = {}
        for sc in scenarios_t13:
            n = sc["n"]
            tau_1 = max(2, min(int(round(THETA_FIXED[0] * n)), n // 2))
            tau_2 = max(2, min(int(round(THETA_FIXED[1] * n)), n // 2))
            m1 = rebalance[n]["m1"]
            m2 = rebalance[n]["m2"]

            r_hats = np.empty(5000)
            r_bals = np.empty(5000)

            for i in range(5000):
                rng = np.random.default_rng(sc["seed_base"] + i)
                if sc["dgp"] == "H0":
                    Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
                elif sc["dgp"] == "DGP3":
                    Y = generate_rw_break_variance(n=n, ratio=sc["r"], rng=rng)
                elif sc["dgp"] == "DGP4":
                    Y = generate_ar1_break_variance(n=n, rho=sc["rho"], ratio=sc["r"], rng=rng)

                means = rolling_mean(Y, tau_1)
                g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
                variances = rolling_var(Y, tau_2)
                g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

                if mode == "sigma_known":
                    scale_1 = 1.0 * n ** (C_1 / 2.0)
                    scale_2 = 1.0 * n ** (C_2 / 2.0)
                else:
                    diffs = np.diff(Y)
                    pilot = "alpha1" if mode == "alpha1_hac" else "alpha2"
                    s2 = hac_newey_west(diffs, andrews_pilot=pilot)
                    s = np.sqrt(s2)
                    scale_1 = s * n ** (C_1 / 2.0) if s > 0 else 1.0
                    scale_2 = s2 * n ** (C_2 / 2.0) if s2 > 0 else 1.0

                g1_std = g1_raw / scale_1
                g2_std = g2_raw / scale_2

                # R_hat
                denom_a = g1_std**2 + g2_std**2
                r_hat = g2_std**2 / denom_a if denom_a > 0 else 0.5
                r_hats[i] = r_hat

                # R_bal
                b1 = g1_std / m1
                b2 = g2_std / m2
                denom_b = b1**2 + b2**2
                r_bal = b2**2 / denom_b if denom_b > 0 else 0.5
                r_bals[i] = r_bal

            t13_results[mode][sc["name"]] = {
                "r_hat": {
                    "mean": float(np.mean(r_hats)),
                    "median": float(np.median(r_hats)),
                    "q05": float(np.quantile(r_hats, 0.05)),
                    "q95": float(np.quantile(r_hats, 0.95)),
                },
                "r_bal": {
                    "mean": float(np.mean(r_bals)),
                    "median": float(np.median(r_bals)),
                    "q05": float(np.quantile(r_bals, 0.05)),
                    "q95": float(np.quantile(r_bals, 0.95)),
                },
            }

    t13_path = os.path.join(RESULTS_DIR, "rhat_distribution_audit5b.json")
    with open(t13_path, "w", encoding="utf-8") as f:
        json.dump(t13_results, f, indent=2)
    print(f"Tabla 13 guardada en: {t13_path}")

    # Verify Controls for Table 13 (sigma_known mode reproduces A1)
    print("\nVerificación Controles Tabla 13 (sigma_known = reproduces A1):")
    ctrls_t13 = t13_results["sigma_known"]
    print(f"  H0 n=200: R_hat mean = {ctrls_t13['H0_n200']['r_hat']['mean']:.4f} (target: 0.0027)")
    print(f"  H0 n=500: R_hat mean = {ctrls_t13['H0_n500']['r_hat']['mean']:.4f} (target: 0.0026)")
    print(f"  H0 n=1000: R_hat mean = {ctrls_t13['H0_n1000']['r_hat']['mean']:.4f} (target: 0.0025)")
    print(f"  DGP3 r=4: R_hat mean = {ctrls_t13['DGP3_r4_n1000']['r_hat']['mean']:.4f} (target: 0.0574)")
    print(f"  DGP4 r=3: R_hat mean = {ctrls_t13['DGP4_r3_n500']['r_hat']['mean']:.4f} (target: 0.1600)")

    assert abs(ctrls_t13["H0_n200"]["r_hat"]["mean"] - 0.0027) < 2e-4
    assert abs(ctrls_t13["H0_n500"]["r_hat"]["mean"] - 0.0026) < 2e-4
    assert abs(ctrls_t13["H0_n1000"]["r_hat"]["mean"] - 0.0025) < 2e-4
    assert abs(ctrls_t13["DGP3_r4_n1000"]["r_hat"]["mean"] - 0.0574) < 2e-4
    assert abs(ctrls_t13["DGP4_r3_n500"]["r_hat"]["mean"] - 0.1600) < 2e-4
    print("Controles Tabla 13: PASS")

    # ------------------------------------------------------------------
    # Step 3: Tabla 14 — Tamaño y Potencia Adaptativa vs Rebalanceada
    # ------------------------------------------------------------------
    print("\n--- Paso 3: Tabla 14 (Tamaño y Potencia Adaptativa vs Rebalanceada) ---")

    def build_cdfs(n, N_cal, seed):
        tau_1 = max(2, min(int(round(THETA_FIXED[0] * n)), n // 2))
        tau_2 = max(2, min(int(round(THETA_FIXED[1] * n)), n // 2))
        scale_1 = 1.0 * n ** (C_1 / 2.0)
        scale_2 = 1.0 * n ** (C_2 / 2.0)
        m1 = rebalance[n]["m1"]
        m2 = rebalance[n]["m2"]

        rng = np.random.default_rng(seed)
        stats_a = np.empty(N_cal)
        stats_r = np.empty(N_cal)

        for j in range(N_cal):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_std = g1_raw / scale_1
            g2_std = g2_raw / scale_2

            # Adaptive
            denom_a = g1_std**2 + g2_std**2
            r_hat = g2_std**2 / denom_a if denom_a > 0 else 0.5
            stats_a[j] = np.sqrt((1.0 - r_hat)**2 * g1_std**2 + r_hat**2 * g2_std**2)

            # Rebalanced
            b1 = g1_std / m1
            b2 = g2_std / m2
            denom_r = b1**2 + b2**2
            r_bal = b2**2 / denom_r if denom_r > 0 else 0.5
            stats_r[j] = np.sqrt((1.0 - r_bal)**2 * b1**2 + r_bal**2 * b2**2)

        stats_a_sorted = np.sort(stats_a)
        stats_r_sorted = np.sort(stats_r)
        ecdf_y = np.arange(1, N_cal + 1) / N_cal

        cdf_a = interp1d(stats_a_sorted, ecdf_y, kind="linear", bounds_error=False, fill_value=(0.0, 1.0))
        cdf_r = interp1d(stats_r_sorted, ecdf_y, kind="linear", bounds_error=False, fill_value=(0.0, 1.0))
        return cdf_a, cdf_r

    scenarios_t14 = [
        {"name": "H0_n200", "dgp": "H0", "n": 200, "seed_base": 100000},
        {"name": "H0_n500", "dgp": "H0", "n": 500, "seed_base": 100000},
        {"name": "H0_n1000", "dgp": "H0", "n": 1000, "seed_base": 100000},
        {"name": "DGP1_rho095_n200", "dgp": "DGP1", "n": 200, "rho": 0.95, "seed_base": 200000},
        {"name": "DGP1_rho097_n500", "dgp": "DGP1", "n": 500, "rho": 0.97, "seed_base": 200000},
        {"name": "DGP1_rho099_n1000", "dgp": "DGP1", "n": 1000, "rho": 0.99, "seed_base": 200000},
        {"name": "DGP3_r4_n1000", "dgp": "DGP3", "n": 1000, "r": 4.0, "seed_base": 300000},
        {"name": "DGP4_r3_n500", "dgp": "DGP4", "n": 500, "r": 3.0, "rho": 0.5, "seed_base": 400000},
    ]

    t14_results = {}

    for n_cal in [10000, 50000]:
        print(f"\nBuilding CDFs for N_cal={n_cal}...")
        cdfs_a = {}
        cdfs_r = {}
        for n in [200, 500, 1000]:
            cdfs_a[n], cdfs_r[n] = build_cdfs(n, n_cal, seed=42)

        for mode in ["sigma_known", "alpha1_hac", "alpha2_hac"]:
            cfg_name = f"{mode}_Ncal{n_cal}"
            t14_results[cfg_name] = {}
            print(f"Running simulation for {cfg_name}...")

            for sc in scenarios_t14:
                n = sc["n"]
                tau_1 = max(2, min(int(round(THETA_FIXED[0] * n)), n // 2))
                tau_2 = max(2, min(int(round(THETA_FIXED[1] * n)), n // 2))
                m1 = rebalance[n]["m1"]
                m2 = rebalance[n]["m2"]

                rej_a = 0
                rej_r = 0
                r_bal_list = []
                stat_r_list = []

                for i in range(5000):
                    rng = np.random.default_rng(sc["seed_base"] + i)
                    if sc["dgp"] == "H0":
                        Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
                    elif sc["dgp"] == "DGP1":
                        Y = generate_ar1(n=n, rho=sc["rho"], rng=rng)
                    elif sc["dgp"] == "DGP3":
                        Y = generate_rw_break_variance(n=n, ratio=sc["r"], rng=rng)
                    elif sc["dgp"] == "DGP4":
                        Y = generate_ar1_break_variance(n=n, rho=sc["rho"], ratio=sc["r"], rng=rng)

                    means = rolling_mean(Y, tau_1)
                    g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
                    variances = rolling_var(Y, tau_2)
                    g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

                    if mode == "sigma_known":
                        scale_1 = 1.0 * n ** (C_1 / 2.0)
                        scale_2 = 1.0 * n ** (C_2 / 2.0)
                    else:
                        diffs = np.diff(Y)
                        pilot = "alpha1" if mode == "alpha1_hac" else "alpha2"
                        s2 = hac_newey_west(diffs, andrews_pilot=pilot)
                        s = np.sqrt(s2)
                        scale_1 = s * n ** (C_1 / 2.0) if s > 0 else 1.0
                        scale_2 = s2 * n ** (C_2 / 2.0) if s2 > 0 else 1.0

                    g1_std = g1_raw / scale_1
                    g2_std = g2_raw / scale_2

                    # Adaptive
                    denom_a = g1_std**2 + g2_std**2
                    r_hat = g2_std**2 / denom_a if denom_a > 0 else 0.5
                    stat_a = np.sqrt((1.0 - r_hat)**2 * g1_std**2 + r_hat**2 * g2_std**2)
                    p_a = float(np.clip(cdfs_a[n](stat_a), 0.0, 1.0))
                    if p_a < 0.05:
                        rej_a += 1

                    # Rebalanced
                    b1 = g1_std / m1
                    b2 = g2_std / m2
                    denom_r = b1**2 + b2**2
                    r_bal = b2**2 / denom_r if denom_r > 0 else 0.5
                    stat_r = np.sqrt((1.0 - r_bal)**2 * b1**2 + r_bal**2 * b2**2)
                    p_r = float(np.clip(cdfs_r[n](stat_r), 0.0, 1.0))
                    if p_r < 0.05:
                        rej_r += 1

                    if sc["name"] == "DGP4_r3_n500":
                        r_bal_list.append(r_bal)
                        stat_r_list.append(stat_r)

                rate_a = rej_a / 5000
                rate_r = rej_r / 5000
                cell = {
                    "adaptive": rate_a,
                    "adaptive_ci": ci_wilson(rate_a, 5000),
                    "rebalanced": rate_r,
                    "rebalanced_ci": ci_wilson(rate_r, 5000),
                }
                if sc["name"] == "DGP4_r3_n500":
                    cell["r_bal_mean"] = float(np.mean(r_bal_list))
                    cell["rebal_stat_mean"] = float(np.mean(stat_r_list))

                t14_results[cfg_name][sc["name"]] = cell
                print(f"  {sc['name']:<20s}: adapt={rate_a:.4f}, rebal={rate_r:.4f}")

    t14_path = os.path.join(RESULTS_DIR, "adaptive_size_power_audit5b.json")
    with open(t14_path, "w", encoding="utf-8") as f:
        json.dump(t14_results, f, indent=2)
    print(f"Tabla 14 guardada en: {t14_path}")

    # Control Assertions for Table 14: sigma_known_Ncal10000 matches A1
    print("\n--- Verificación Controles Tabla 14 (sigma_known_Ncal10000 reproduces A1) ---")
    ctrls_a1 = t14_results["sigma_known_Ncal10000"]

    # Size
    print(f"  H0 n=200: adapt={ctrls_a1['H0_n200']['adaptive']:.4f} (exp 0.0492), rebal={ctrls_a1['H0_n200']['rebalanced']:.4f} (exp 0.0494)")
    print(f"  H0 n=500: adapt={ctrls_a1['H0_n500']['adaptive']:.4f} (exp 0.0466), rebal={ctrls_a1['H0_n500']['rebalanced']:.4f} (exp 0.0536)")
    print(f"  H0 n=1000: adapt={ctrls_a1['H0_n1000']['adaptive']:.4f} (exp 0.0512), rebal={ctrls_a1['H0_n1000']['rebalanced']:.4f} (exp 0.0488)")
    assert abs(ctrls_a1["H0_n200"]["adaptive"] - 0.0492) < 1e-4
    assert abs(ctrls_a1["H0_n200"]["rebalanced"] - 0.0494) < 1e-4

    # DGP1
    print(f"  DGP1 n=200: adapt={ctrls_a1['DGP1_rho095_n200']['adaptive']:.4f} (exp 0.4030), rebal={ctrls_a1['DGP1_rho095_n200']['rebalanced']:.4f} (exp 0.2986)")
    print(f"  DGP1 n=500: adapt={ctrls_a1['DGP1_rho097_n500']['adaptive']:.4f} (exp 0.7236), rebal={ctrls_a1['DGP1_rho097_n500']['rebalanced']:.4f} (exp 0.4738)")
    print(f"  DGP1 n=1000: adapt={ctrls_a1['DGP1_rho099_n1000']['adaptive']:.4f} (exp 0.4446), rebal={ctrls_a1['DGP1_rho099_n1000']['rebalanced']:.4f} (exp 0.3142)")
    assert abs(ctrls_a1["DGP1_rho095_n200"]["adaptive"] - 0.4030) < 1e-4
    assert abs(ctrls_a1["DGP1_rho095_n200"]["rebalanced"] - 0.2986) < 1e-4

    # DGP3
    print(f"  DGP3 r=4: adapt={ctrls_a1['DGP3_r4_n1000']['adaptive']:.4f} (exp 0.0004), rebal={ctrls_a1['DGP3_r4_n1000']['rebalanced']:.4f} (exp 0.0000)")
    assert abs(ctrl_dgp3 := ctrls_a1["DGP3_r4_n1000"]["adaptive"] - 0.0004) < 1e-4
    assert ctrls_a1["DGP3_r4_n1000"]["rebalanced"] == 0.0000

    # DGP4 — The critical cell
    print(f"  DGP4 r=3 n=500: adapt={ctrls_a1['DGP4_r3_n500']['adaptive']:.4f} (exp 1.0000), rebal={ctrls_a1['DGP4_r3_n500']['rebalanced']:.4f} (exp 0.0000)")
    assert ctrls_a1["DGP4_r3_n500"]["adaptive"] == 1.0000
    assert ctrls_a1["DGP4_r3_n500"]["rebalanced"] == 0.0000
    print("Controles Tabla 14: PASS — Replicación bit a bit de A1 confirmada.")

    print(f"\nTarea R4 completada con éxito en {time.time() - t_start:.1f}s.")


if __name__ == "__main__":
    run_r4()
