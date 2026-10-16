"""
Tarea R2 — DGP 3 y DGP 4, comparación pareada real.
Evaluates run_dgp3 and run_dgp4 under alpha1 and alpha2 with identical seeds.
N_cal = 50,000, seed 42. N_sim = 5,000, theta = (0.1, 0.1), n in {200, 500, 1000}.
"""

import sys
import os
import time
import json
import hashlib
import numpy as np

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from experiments.power_comparison import (
    precalibrate_cdfs,
    run_dgp3,
    run_dgp4,
    THETA_FIXED,
    R_CONFIGS,
    N_GRID,
    DGP3_RATIOS,
    DGP4_RATIOS,
)

RESULTS_DIR = "experiments/results"


def run_r2():
    t_start = time.time()
    print("=" * 70)
    print("  Tarea R2: DGP 3 y DGP 4 — Comparación pareada real (alpha1 vs alpha2)")
    print(f"  N_sim=5000, N_cal=50000, n in {N_GRID}")
    print("=" * 70)

    # Step 1: Precompute null CDFs once (N_cal=50000, seed=42)
    t0 = time.time()
    cdf_cache = precalibrate_cdfs(
        theta=THETA_FIXED,
        r_values=R_CONFIGS,
        n_grid=N_GRID,
        N_cal=50000,
    )
    print(f"CDF cache precalibrated in {time.time() - t0:.1f}s\n")

    outputs = {}

    for pilot in ["alpha1", "alpha2"]:
        print(f"\n{'#' * 70}")
        print(f"  RUNNING PILOT: {pilot}")
        print(f"{'#' * 70}")
        t_pilot = time.time()

        dgp3_res = run_dgp3(cdf_cache, pilot=pilot)
        dgp4_res = run_dgp4(cdf_cache, pilot=pilot)

        combined = {
            "metadata": {
                "pilot": pilot,
                "theta": list(THETA_FIXED),
                "N_cal": 50000,
                "cal_seed": 42,
                "N_sim": 5000,
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "dgp3": dgp3_res,
            "dgp4": dgp4_res,
        }

        out_path = os.path.join(RESULTS_DIR, f"power_comparison_dgp34_{pilot}_audit5b.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2)

        print(f"\nSaved {pilot} results to {out_path} ({time.time() - t_pilot:.1f}s)")
        outputs[pilot] = out_path

    # Step 2: Automatic MD5 Inequality Assertion
    path_a1 = outputs["alpha1"]
    path_a2 = outputs["alpha2"]
    h1 = hashlib.md5(open(path_a1, "rb").read()).hexdigest()
    h2 = hashlib.md5(open(path_a2, "rb").read()).hexdigest()

    print(f"\nMD5 alpha1: {h1}")
    print(f"MD5 alpha2: {h2}")
    assert h1 != h2, f"FALLO: las dos ramas produjeron el mismo archivo ({h1})"
    print("Assertion PASS: Los archivos son distintos (h1 != h2)\n")

    # Step 3: Verification of Controls
    with open(path_a1, "r", encoding="utf-8") as f:
        data_a1 = json.load(f)
    with open(path_a2, "r", encoding="utf-8") as f:
        data_a2 = json.load(f)

    # Controls alpha1
    ctrl_a1_g1 = data_a1["dgp4"]["200"]["1.0"]["E_g1_std"]
    ctrl_a1_g2 = data_a1["dgp4"]["200"]["1.0"]["E_g2_std"]
    print(f"[Control alpha1 n=200 r=1.0] E[g1]={ctrl_a1_g1:.18f} (exp: 0.041430173768439445)")
    print(f"[Control alpha1 n=200 r=1.0] E[g2]={ctrl_a1_g2:.18f} (exp: 0.004679906883529837)")
    assert abs(ctrl_a1_g1 - 0.041430173768439445) < 1e-12
    assert abs(ctrl_a1_g2 - 0.004679906883529837) < 1e-12

    ctrl_a1_1000_g1 = data_a1["dgp4"]["1000"]["4.0"]["E_g1_std"]
    ctrl_a1_1000_g2 = data_a1["dgp4"]["1000"]["4.0"]["E_g2_std"]
    print(f"[Control alpha1 n=1000 r=4.0] E[g1]={ctrl_a1_1000_g1:.5f} (exp: 0.01059)")
    print(f"[Control alpha1 n=1000 r=4.0] E[g2]={ctrl_a1_1000_g2:.5f} (exp: 0.00383)")
    assert abs(ctrl_a1_1000_g1 - 0.01059) < 1e-4
    assert abs(ctrl_a1_1000_g2 - 0.00383) < 1e-4

    # Controls alpha2
    ctrl_a2_g1 = data_a2["dgp4"]["200"]["1.0"]["E_g1_std"]
    ctrl_a2_g2 = data_a2["dgp4"]["200"]["1.0"]["E_g2_std"]
    print(f"[Control alpha2 n=200 r=1.0] E[g1]={ctrl_a2_g1:.5f} (exp: ~0.03735)")
    print(f"[Control alpha2 n=200 r=1.0] E[g2]={ctrl_a2_g2:.5f} (exp: ~0.00380)")
    assert abs(ctrl_a2_g1 - 0.03735) < 5e-4
    assert abs(ctrl_a2_g2 - 0.00380) < 5e-4

    # Amplifications
    amp_a1 = data_a1["dgp4"]["1000"]["4.0"]["E_g2_std"] / data_a1["dgp4"]["1000"]["1.0"]["E_g2_std"]
    amp_a2 = data_a2["dgp4"]["1000"]["4.0"]["E_g2_std"] / data_a2["dgp4"]["1000"]["1.0"]["E_g2_std"]
    print(f"[Amplificacion n=1000 r=4.0] alpha1={amp_a1:.2f}x (exp: 5.21x), alpha2={amp_a2:.2f}x (exp: 5.17x)")

    # Print summary tables
    print("\n" + "=" * 70)
    print("  TABLA COMPLETA DGP 3 (alpha1 vs alpha2)")
    print("=" * 70)
    print(f"{'n':>5s} {'r':>4s} {'Pilot':>7s} {'R50':>7s} {'R25':>7s} {'R75':>7s} {'ADF':>7s} {'PP':>7s} {'KPSS':>7s}")
    print("-" * 65)
    for n in N_GRID:
        for r in DGP3_RATIOS:
            r_str = f"{r:.1f}" if f"{r:.1f}" in data_a1["dgp3"][str(n)] else str(r)
            row_a1 = data_a1["dgp3"][str(n)][r_str]
            row_a2 = data_a2["dgp3"][str(n)][r_str]
            print(f"{n:5d} {r:4.1f}  alpha1 {row_a1['ours_R050']:7.4f} {row_a1['ours_R025']:7.4f} {row_a1['ours_R075']:7.4f} {row_a1['adf']:7.4f} {row_a1['pp']:7.4f} {row_a1['kpss_rej']:7.4f}")
            print(f"{n:5d} {r:4.1f}  alpha2 {row_a2['ours_R050']:7.4f} {row_a2['ours_R025']:7.4f} {row_a2['ours_R075']:7.4f} {row_a2['adf']:7.4f} {row_a2['pp']:7.4f} {row_a2['kpss_rej']:7.4f}")

    print("\n" + "=" * 70)
    print("  TABLA COMPLETA DGP 4 (alpha1 vs alpha2)")
    print("=" * 70)
    print(f"{'n':>5s} {'r':>4s} {'Pilot':>7s} {'R50':>7s} {'R25':>7s} {'R75':>7s} {'ADF':>7s} {'PP':>7s} {'KPSS':>7s} {'E[g1]':>8s} {'E[g2]':>8s} {'sd(g1)':>8s} {'sd(g2)':>8s} {'Amp(g2)':>8s}")
    print("-" * 115)
    for n in N_GRID:
        e_g2_base_a1 = data_a1["dgp4"][str(n)]["1.0"]["E_g2_std"]
        e_g2_base_a2 = data_a2["dgp4"][str(n)]["1.0"]["E_g2_std"]
        for r in DGP4_RATIOS:
            r_str = f"{r:.1f}" if f"{r:.1f}" in data_a1["dgp4"][str(n)] else str(r)
            row_a1 = data_a1["dgp4"][str(n)][r_str]
            row_a2 = data_a2["dgp4"][str(n)][r_str]
            amp1 = row_a1["E_g2_std"] / e_g2_base_a1
            amp2 = row_a2["E_g2_std"] / e_g2_base_a2
            print(f"{n:5d} {r:4.1f}  alpha1 {row_a1['ours_R050']:7.4f} {row_a1['ours_R025']:7.4f} {row_a1['ours_R075']:7.4f} {row_a1['adf']:7.4f} {row_a1['pp']:7.4f} {row_a1['kpss_rej']:7.4f} {row_a1['E_g1_std']:8.5f} {row_a1['E_g2_std']:8.5f} {row_a1['std_g1']:8.5f} {row_a1['std_g2']:8.5f} {amp1:7.2f}x")
            print(f"{n:5d} {r:4.1f}  alpha2 {row_a2['ours_R050']:7.4f} {row_a2['ours_R025']:7.4f} {row_a2['ours_R075']:7.4f} {row_a2['adf']:7.4f} {row_a2['pp']:7.4f} {row_a2['kpss_rej']:7.4f} {row_a2['E_g1_std']:8.5f} {row_a2['E_g2_std']:8.5f} {row_a2['std_g1']:8.5f} {row_a2['std_g2']:8.5f} {amp2:7.2f}x")

    print(f"\nTarea R2 total time: {time.time() - t_start:.1f}s")


if __name__ == "__main__":
    run_r2()
