"""
Tarea R6 — Cerrar T8 (tamaño adaptativo) y T10 (costos y benchmarks).
"""

import sys
import os
import time
import json
import platform
try:
    import psutil
except ImportError:
    psutil = None
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from stationarity_test.empirical_eigenvalues import (
    build_null_cdf_adaptive,
    build_null_cdf,
)
from stationarity_test.statistic import compute_statistic
from statsmodels.tsa.stattools import adfuller, kpss
from arch.unitroot import PhillipsPerron, DFGLS

RESULTS_DIR = "experiments/results"


def ci_wilson(p_hat, n_sim):
    z = 1.96
    denom = 1 + z**2 / n_sim
    center = (p_hat + z**2 / (2 * n_sim)) / denom
    width = z * np.sqrt(p_hat * (1 - p_hat) / n_sim + z**2 / (4 * n_sim**2)) / denom
    return round(float(center - width), 4), round(float(center + width), 4)


def run_r6():
    t_start = time.time()
    print("=" * 70)
    print("  Tarea R6: Cerrar T8 (Tamaño Adaptativo) y T10 (Costos y Benchmarks)")
    print("=" * 70)

    # ==================================================================
    # R6.1: verify_adaptive_size (T8)
    # ==================================================================
    print("\n--- R6.1: Verificación de Tamaño Adaptativo (§6.1) ---")
    grid_r61 = [
        (150, 10000), (150, 50000),
        (200, 10000), (200, 50000),
        (250, 10000), (250, 50000),
        (300, 10000), (300, 50000),
    ]

    r61_rows = []
    N_TEST = 5000

    for n, n_cal in grid_r61:
        t0 = time.time()
        cdf_func = build_null_cdf_adaptive(
            (0.1, 0.1), n, N_cal=n_cal, seed=42, use_cache=False
        )
        t_cal = time.time() - t0

        rng = np.random.default_rng(9999)
        rej_count = 0
        for _ in range(N_TEST):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            res = compute_statistic(Y, (0.1, 0.1), R=0.5, eps=1e-3, andrews_pilot="alpha1")
            g1, g2 = res["g1_std"], res["g2_std"]
            denom = g1**2 + g2**2
            r_hat = g2**2 / denom if denom > 1e-12 else 0.5
            stat = np.sqrt((1.0 - r_hat)**2 * g1**2 + r_hat**2 * g2**2)
            p = float(cdf_func(stat))
            if p < 0.05:
                rej_count += 1

        rate = rej_count / N_TEST
        ci_l, ci_u = ci_wilson(rate, N_TEST)
        r61_rows.append({
            "n": n,
            "N_cal": n_cal,
            "rejection_rate": rate,
            "ci_lower": ci_l,
            "ci_upper": ci_u,
            "in_exact_band": 0.0440 <= rate <= 0.0562,
            "t_cal_sec": round(t_cal, 2),
        })
        print(f"  n={n:3d}, N_cal={n_cal:5d}: rate={rate:.4f} [{ci_l:.4f}, {ci_u:.4f}] "
              f"in_band={'YES' if 0.0440 <= rate <= 0.0562 else 'NO'} ({t_cal:.1f}s)")

    df_r61 = pd.DataFrame(r61_rows)
    csv_path = os.path.join(RESULTS_DIR, "adaptive_size_audit5b.csv")
    df_r61.to_csv(csv_path, index=False)
    print(f"Resultados T8 guardados en: {csv_path}")

    # Check origin of 0.0518
    match_0518 = [r for r in r61_rows if abs(r["rejection_rate"] - 0.0518) < 1e-4]
    print(f"\nOrigen de 0.0518 en §6.1:")
    if match_0518:
        for m in match_0518:
            print(f"  Encontrado en: n={m['n']}, N_cal={m['N_cal']}")
    else:
        print("  Ninguna de las configuraciones probadas dio exactamente 0.0518.")

    # ==================================================================
    # R6.2: Benchmarks y Costos (T10)
    # ==================================================================
    print("\n--- R6.2: Costos Computacionales y Benchmarks ---")

    # 1. Calibraciones (3 repeticiones, use_cache=False)
    print("  Midiendo build_null_cdf(theta=(0.1,0.1), R=0.5, n=1000, N_cal=50000, seed=42)...")
    cal_50k_times = []
    for rep in range(3):
        t0 = time.perf_counter()
        build_null_cdf((0.1, 0.1), 0.5, 1000, N_cal=50000, seed=42, use_cache=False)
        dt = time.perf_counter() - t0
        cal_50k_times.append(dt)
        print(f"    Rep {rep + 1}: {dt:.3f} s")

    print("  Midiendo build_null_cdf con N_cal=10000...")
    cal_10k_times = []
    for rep in range(3):
        t0 = time.perf_counter()
        build_null_cdf((0.1, 0.1), 0.5, 1000, N_cal=10000, seed=42, use_cache=False)
        dt = time.perf_counter() - t0
        cal_10k_times.append(dt)
        print(f"    Rep {rep + 1}: {dt:.3f} s")

    # 2. Precalentar JIT
    print("\n  Precalentando JIT numba...")
    dummy = np.random.default_rng(0).standard_normal(201).cumsum()
    compute_statistic(dummy, (0.1, 0.1), 0.5, eps=1e-3)
    adfuller(dummy, autolag="AIC")
    PhillipsPerron(dummy)
    DFGLS(dummy, trend="c")
    kpss(dummy, regression="c", nlags="auto")

    # 3. Costo por serie en 200 series
    n_series_grid = [200, 500, 1000, 5000, 20000]
    N_SERIES = 200
    timing_results = {}

    print(f"\n  Midiendo costo por serie sobre {N_SERIES} series independientes:")
    print(f"{'n':>6s} | {'Propuesto (ms)':>16s} | {'ADF (ms)':>12s} | {'PP (ms)':>12s} | {'DF-GLS (ms)':>12s} | {'KPSS (ms)':>12s} | {'Ratio Prop/ADF':>14s}")
    print("-" * 95)

    for n in n_series_grid:
        # Precompute CDF once
        cdf_test = build_null_cdf((0.1, 0.1), 0.5, n, N_cal=10000, seed=42)

        rng = np.random.default_rng(123)
        series_list = [rng.standard_normal(n + 1).cumsum() for _ in range(N_SERIES)]

        t_prop, t_adf, t_pp, t_dfgls, t_kpss = [], [], [], [], []

        for Y in series_list:
            # Proposed
            t0 = time.perf_counter()
            res = compute_statistic(Y, (0.1, 0.1), 0.5, eps=1e-3, andrews_pilot="alpha1")
            _ = cdf_test(res["statistic"])
            t_prop.append((time.perf_counter() - t0) * 1000.0)

            # ADF
            t0 = time.perf_counter()
            _ = adfuller(Y, autolag="AIC")
            t_adf.append((time.perf_counter() - t0) * 1000.0)

            # PP
            t0 = time.perf_counter()
            _ = PhillipsPerron(Y).pvalue
            t_pp.append((time.perf_counter() - t0) * 1000.0)

            # DF-GLS
            t0 = time.perf_counter()
            _ = DFGLS(Y, trend="c").pvalue
            t_dfgls.append((time.perf_counter() - t0) * 1000.0)

            # KPSS
            t0 = time.perf_counter()
            _ = kpss(Y, regression="c", nlags="auto")
            t_kpss.append((time.perf_counter() - t0) * 1000.0)

        def get_stats(arr):
            q25, med, q75 = np.percentile(arr, [25, 50, 75])
            return {"median": float(med), "iqr": float(q75 - q25)}

        st_prop = get_stats(t_prop)
        st_adf = get_stats(t_adf)
        st_pp = get_stats(t_pp)
        st_dfgls = get_stats(t_dfgls)
        st_kpss = get_stats(t_kpss)
        ratio_adf = st_prop["median"] / st_adf["median"]

        timing_results[str(n)] = {
            "proposed": st_prop,
            "adf": st_adf,
            "pp": st_pp,
            "dfgls": st_dfgls,
            "kpss": st_kpss,
            "ratio_prop_adf": round(ratio_adf, 4),
        }

        print(f"{n:6d} | {st_prop['median']:7.3f} (±{st_prop['iqr']:5.3f}) | "
              f"{st_adf['median']:6.3f} (±{st_adf['iqr']:5.3f}) | "
              f"{st_pp['median']:6.3f} (±{st_pp['iqr']:5.3f}) | "
              f"{st_dfgls['median']:6.3f} (±{st_dfgls['iqr']:5.3f}) | "
              f"{st_kpss['median']:6.3f} (±{st_kpss['iqr']:5.3f}) | "
              f"{ratio_adf:14.4f}")

    # 4. Extrapolación Tabla B
    # 5 thetas x 3 R x 6 n = 90 cells with N_cal = 100,000
    mean_cal_50k = float(np.mean(cal_50k_times))
    cal_100k_est_sec = mean_cal_50k * 2.0
    table_b_total_sec = 90 * cal_100k_est_sec
    table_b_total_min = table_b_total_sec / 60.0

    print(f"\nExtrapolación Tabla B (90 celdas, N_cal=100,000):")
    print(f"  Tiempo estimado por celda (100k): {cal_100k_est_sec:.2f} s")
    print(f"  Tiempo total estimado (90 celdas): {table_b_total_sec:.1f} s (~{table_b_total_min:.1f} min)")

    # 5. Hardware specs
    hw_info = {
        "os": platform.platform(),
        "processor": platform.processor(),
        "cpu_count_physical": psutil.cpu_count(logical=False) if psutil else os.cpu_count(),
        "cpu_count_logical": psutil.cpu_count(logical=True) if psutil else os.cpu_count(),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2) if psutil else None,
        "python_version": platform.python_version(),
    }
    print(f"\nHardware Info: {hw_info}")

    full_output = {
        "calibration_times": {
            "Ncal_50k_reps_sec": cal_50k_times,
            "Ncal_50k_mean_sec": mean_cal_50k,
            "Ncal_10k_reps_sec": cal_10k_times,
            "Ncal_10k_mean_sec": float(np.mean(cal_10k_times)),
        },
        "per_series_timing_ms": timing_results,
        "table_b_extrapolation": {
            "cells": 90,
            "N_cal": 100000,
            "est_per_cell_sec": cal_100k_est_sec,
            "est_total_sec": table_b_total_sec,
            "est_total_min": table_b_total_min,
        },
        "hardware": hw_info,
    }

    out_path = os.path.join(RESULTS_DIR, "tarea6_benchmarks_audit5b.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)
    print(f"Resultados T10 guardados en: {out_path}")

    print(f"\nTarea R6 completada en {time.time() - t_start:.1f}s.")


if __name__ == "__main__":
    run_r6()
