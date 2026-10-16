"""
Auditoría A6 — Componente 3: Robustez de Tamaño DKW y Tabla Maestra de Desviaciones alpha(1) vs alpha(2).

Contenido:
  1. Límites exactos de la desigualdad de Dvoretzky-Kiefer-Wolfowitz (DKW).
  2. Tabla comparativa de tamaño empírico para N_cal in {10,000, 50,000} confirmando epsilon_DKW.
  3. Tabla maestra unificada de desviaciones alpha(1) vs alpha(2) a través de los 4 dominios experimentales:
     - Tamaño bajo H0 (Tabla 1)
     - Colas pesadas (Tabla 2: t3, t5, Pareto)
     - Quiebre de varianza (DGP 3 y DGP 4)
     - Aplicación empírica en datos reales (48 celdas de control, 13 detecciones, latencia).
"""

import os
import sys
import json
import numpy as np
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def compute_dkw_bound(N_cal: int, gamma: float = 0.05) -> float:
    """
    Dvoretzky-Kiefer-Wolfowitz (DKW) uniform error bound:
    P(sup_x |F_N(x) - F(x)| > epsilon) <= 2 * exp(-2 * N * epsilon^2) = gamma
    => epsilon = sqrt(ln(2 / gamma) / (2 * N))
    """
    return float(np.sqrt(np.log(2.0 / gamma) / (2.0 * N_cal)))


def build_size_robustness_table():
    """Build size robustness comparison for N_cal=10k vs 50k from audit5b results."""
    csv_path = os.path.join(RESULTS_DIR, "adaptive_size_audit5b.csv")
    df = pd.read_csv(csv_path)

    # Group by n
    table_rows = []
    n_vals = sorted(df["n"].unique())

    for n in n_vals:
        sub = df[df["n"] == n]
        row_10k = sub[sub["N_cal"] == 10000].iloc[0]
        row_50k = sub[sub["N_cal"] == 50000].iloc[0]

        rate_10k = float(row_10k["rejection_rate"])
        rate_50k = float(row_50k["rejection_rate"])
        delta = abs(rate_10k - rate_50k)

        table_rows.append({
            "n": int(n),
            "rate_10k": rate_10k,
            "ci_10k": [float(row_10k["ci_lower"]), float(row_10k["ci_upper"])],
            "rate_50k": rate_50k,
            "ci_50k": [float(row_50k["ci_lower"]), float(row_50k["ci_upper"])],
            "delta": float(round(delta, 4)),
            "dkw_bound_10k": 0.0136,
            "dkw_bound_50k": 0.0061,
            "satisfies_dkw": bool(delta <= 0.0136),
        })

    return table_rows


def build_dual_pilot_deviation_table():
    """Build unified alpha(1) vs alpha(2) deviation table across all domains."""
    # 1. H0 Size (size_audit5.json)
    with open(os.path.join(RESULTS_DIR, "size_audit5.json"), "r", encoding="utf-8") as f:
        size_data = json.load(f)

    h0_size_diffs = []
    for n_str in ["200", "500", "1000"]:
        r_a1 = size_data["alpha1"][n_str]["ours_R050"]
        r_a2 = size_data["alpha2"][n_str]["ours_R050"]
        h0_size_diffs.append({
            "n": int(n_str),
            "alpha1": r_a1,
            "alpha2": r_a2,
            "diff": float(round(abs(r_a1 - r_a2), 4)),
            "rel_diff_pct": float(round(abs(r_a1 - r_a2) / r_a1 * 100, 2)) if r_a1 > 0 else 0.0,
        })

    # 2. Heavy Tails (size_robustness_heavy_tails_audit5b.json)
    with open(os.path.join(RESULTS_DIR, "size_robustness_heavy_tails_audit5b.json"), "r", encoding="utf-8") as f:
        ht_data = json.load(f)

    ht_diffs = []
    for dist in ht_data["alpha1"].keys():
        for n_str in ["200", "500", "1000"]:
            r_a1 = ht_data["alpha1"][dist][n_str]["ours_R050"]
            r_a2 = ht_data["alpha2"][dist][n_str]["ours_R050"]
            ht_diffs.append({
                "dist": dist,
                "n": int(n_str),
                "alpha1": r_a1,
                "alpha2": r_a2,
                "diff": float(round(abs(r_a1 - r_a2), 4)),
            })

    # 3. DGP 3 and DGP 4 (power_comparison_dgp34_alpha{1,2}_audit5b.json)
    with open(os.path.join(RESULTS_DIR, "power_comparison_dgp34_alpha1_audit5b.json"), "r", encoding="utf-8") as f:
        dgp34_a1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, "power_comparison_dgp34_alpha2_audit5b.json"), "r", encoding="utf-8") as f:
        dgp34_a2 = json.load(f)

    dgp3_diffs = []
    for n_str in ["200", "500", "1000"]:
        for r_str in ["1.0", "1.5", "2.0", "2.5", "3.0", "4.0"]:
            r_a1 = dgp34_a1["dgp3"][n_str][r_str]["ours_R050"]
            r_a2 = dgp34_a2["dgp3"][n_str][r_str]["ours_R050"]
            dgp3_diffs.append({
                "n": int(n_str),
                "ratio": float(r_str),
                "alpha1": r_a1,
                "alpha2": r_a2,
                "diff": float(round(abs(r_a1 - r_a2), 4)),
            })

    dgp4_diffs = []
    for n_str in ["200", "500", "1000"]:
        for r_str in ["1.0", "1.5", "2.0", "2.5", "3.0", "4.0"]:
            c_a1 = dgp34_a1["dgp4"][n_str][r_str]
            c_a2 = dgp34_a2["dgp4"][n_str][r_str]
            dgp4_diffs.append({
                "n": int(n_str),
                "ratio": float(r_str),
                "alpha1_power": c_a1["ours_R050"],
                "alpha2_power": c_a2["ours_R050"],
                "alpha1_Eg1": c_a1["E_g1_std"],
                "alpha2_Eg1": c_a2["E_g1_std"],
                "alpha1_Eg2": c_a1["E_g2_std"],
                "alpha2_Eg2": c_a2["E_g2_std"],
            })

    # 4. Real Data Application (real_data_comparison_audit5b.json)
    with open(os.path.join(RESULTS_DIR, "real_data_comparison_audit5b.json"), "r", encoding="utf-8") as f:
        rd_comp = json.load(f)["summary"]

    real_data_summary = {
        "alpha1_10k": {
            "mean_fp": rd_comp["a1_10k"]["mean_fp"]["ours"],
            "max_fp": rd_comp["a1_10k"]["max_fp"]["ours"],
            "detections": rd_comp["a1_10k"]["detections"]["ours"],
            "mean_latency": rd_comp["a1_10k"]["mean_latency"]["ours"],
        },
        "alpha2_10k_repro": {
            "mean_fp": rd_comp["repro"]["mean_fp"]["ours"],
            "max_fp": rd_comp["repro"]["max_fp"]["ours"],
            "detections": rd_comp["repro"]["detections"]["ours"],
            "mean_latency": rd_comp["repro"]["mean_latency"]["ours"],
        },
        "alpha1_50k": {
            "mean_fp": rd_comp["a1_50k"]["mean_fp"]["ours"],
            "max_fp": rd_comp["a1_50k"]["max_fp"]["ours"],
            "detections": rd_comp["a1_50k"]["detections"]["ours"],
            "mean_latency": rd_comp["a1_50k"]["mean_latency"]["ours"],
        },
    }

    return {
        "h0_size": h0_size_diffs,
        "heavy_tails": ht_diffs,
        "dgp3_variance_break": dgp3_diffs,
        "dgp4_ar1_variance_break": dgp4_diffs,
        "real_data": real_data_summary,
    }


def main():
    print("=" * 70)
    print("  Auditoría A6 — Componente 3: Robustez DKW y Desviaciones Dual-Pilot")
    print("=" * 70)

    # 1. DKW bounds
    dkw_10k = compute_dkw_bound(10000)
    dkw_50k = compute_dkw_bound(50000)
    dkw_100k = compute_dkw_bound(100000)

    print(f"  Limite DKW (N=10,000):  epsilon = {dkw_10k:.6f} (~ 0.0136)")
    print(f"  Limite DKW (N=50,000):  epsilon = {dkw_50k:.6f} (~ 0.0061)")
    print(f"  Limite DKW (N=100,000): epsilon = {dkw_100k:.6f} (~ 0.0043)")

    # 2. Size robustness table
    size_rob_table = build_size_robustness_table()
    print("\n--- Tabla de Robustez de Tamaño N_cal=10k vs 50k ---")
    for r in size_rob_table:
        print(f"  n={r['n']:3d}: 10k={r['rate_10k']:.4f} | 50k={r['rate_50k']:.4f} | Delta={r['delta']:.4f} (DKW <= {r['dkw_bound_10k']}: {r['satisfies_dkw']})")

    # 3. Dual pilot deviations
    deviations = build_dual_pilot_deviation_table()

    payload = {
        "metadata": {
            "timestamp_utc": "2026-09-06T18:00:00Z",
            "dkw_bounds": {
                "N_10000": {"epsilon_exact": float(dkw_10k), "reported": 0.0136},
                "N_50000": {"epsilon_exact": float(dkw_50k), "reported": 0.0061},
                "N_100000": {"epsilon_exact": float(dkw_100k), "reported": 0.0043},
            },
        },
        "size_robustness_table": size_rob_table,
        "pilot_deviations": deviations,
    }

    out_file = os.path.join(RESULTS_DIR, "size_robustness_dkw_audit6.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\n======================================================================")
    print(f"  Resultados de DKW y Desviaciones guardados en: {out_file}")
    print(f"======================================================================\n")
    return payload


if __name__ == "__main__":
    main()
