"""
Tarea R5 — Datos reales: barrido completo de 3 configuraciones y DF-GLS.
Configuraciones:
  1. _repro: pilot alpha2, N_cal 10,000 (debe coincidir bit a bit con pre-registro)
  2. _a1_10k: pilot alpha1, N_cal 10,000
  3. _a1_50k: pilot alpha1, N_cal 50,000
"""

import sys
import os
import time
import json
import subprocess
import numpy as np
import pandas as pd

RESULTS_DIR = "experiments/results"
CHECKPOINTS_DIR = os.path.join(RESULTS_DIR, "checkpoints")
DATA_DIR = os.path.join("experiments", "data")

INDICES = ["SP500", "FTSE", "NIKKEI", "DAX"]
WINDOW_SIZES = [150, 200, 250, 300]
CONTROL_PERIODS = ["C1_1993", "C2_2005", "C3_2017"]

EVENTS = {
    "E1_BlackMonday": "1987-10-19",
    "E2_AsianCrisis": "1997-07-02",
    "E3_RussianCrisis": "1998-08-17",
    "E4_DotCom": "2000-03-10",
    "E5_Subprime": "2008-09-15",
    "E6_COVID": "2020-02-20",
}
EXCLUSIONS = {
    ("FTSE", "E1_BlackMonday"),
    ("DAX", "E1_BlackMonday"),
}


def run_cmd(cmd):
    print(f"\n>> Executing: {' '.join(cmd)}")
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("STDOUT:\n", res.stdout)
        print("STDERR:\n", res.stderr)
        raise RuntimeError(f"Command failed with return code {res.returncode}")
    print(f">> Done in {time.time() - t0:.1f}s")
    return res.stdout


def run_r5():
    t_start = time.time()
    print("=" * 70)
    print("  Tarea R5: Barrido de validación en datos reales (3 configuraciones)")
    print("=" * 70)

    configs = [
        {"name": "repro", "pilot": "alpha2", "n_cal": 10000, "suffix": "_repro"},
        {"name": "a1_10k", "pilot": "alpha1", "n_cal": 10000, "suffix": "_a1_10k"},
        {"name": "a1_50k", "pilot": "alpha1", "n_cal": 50000, "suffix": "_a1_50k"},
    ]

    for cfg in configs:
        suf = cfg["suffix"]
        pilot = cfg["pilot"]
        n_cal = str(cfg["n_cal"])
        print(f"\n{'#' * 70}")
        print(f"  Configuración: {cfg['name']} (pilot={pilot}, N_cal={n_cal}, suffix={suf})")
        print(f"{'#' * 70}")

        # 1. Run real_data_validation.py
        cmd_val = [
            "python", "-u", "experiments/real_data_validation.py",
            "--pilot", pilot,
            "--n-cal", n_cal,
            "--suffix", suf,
        ]
        run_cmd(cmd_val)

        # 2. Run extend_realdata_dfgls.py
        cmd_dfgls = [
            "python", "-u", "experiments/extend_realdata_dfgls.py",
            "--suffix", suf,
        ]
        run_cmd(cmd_dfgls)

    # ------------------------------------------------------------------
    # Verificación Criterio Duro para _repro vs pre-registro restaurado
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  VERIFICACIÓN CRITERIO DURO: _repro vs real_data_results.json (pre-registro)")
    print("=" * 70)

    with open(os.path.join(RESULTS_DIR, "real_data_results.json"), "r", encoding="utf-8") as f:
        data_orig = json.load(f)
    with open(os.path.join(RESULTS_DIR, "real_data_results_repro.json"), "r", encoding="utf-8") as f:
        data_repro = json.load(f)

    # Compare 48 control rates
    orig_cps = {f"{cp['index']}_D{cp['D']}": cp for cp in data_orig["checkpoints"]}
    repro_cps = {f"{cp['index']}_D{cp['D']}": cp for cp in data_repro["checkpoints"]}

    diffs_found = []
    ours_repro_list = []
    ours_orig_list = []

    for key, cp_orig in orig_cps.items():
        cp_rep = repro_cps[key]
        for pid in CONTROL_PERIODS:
            r_orig = cp_orig["false_positive_rates"][pid]["ours"]
            r_rep = cp_rep["false_positive_rates"][pid]["ours"]
            ours_orig_list.append(r_orig)
            ours_repro_list.append(r_rep)
            if abs(r_orig - r_rep) > 1e-6:
                diffs_found.append((key, pid, r_orig, r_rep))

    mean_orig = float(np.mean(ours_orig_list))
    max_orig = float(np.max(ours_orig_list))
    mean_rep = float(np.mean(ours_repro_list))
    max_rep = float(np.max(ours_repro_list))

    print(f"Pre-registro original: media={mean_orig:.5f}, max={max_orig:.4f}")
    print(f"Reproducción (_repro): media={mean_rep:.5f}, max={max_rep:.4f}")

    if diffs_found:
        print(f"ALERTA: {len(diffs_found)} discrepancias encontradas:")
        for d in diffs_found:
            print(f"  {d[0]} {d[1]}: orig={d[2]:.4f}, repro={d[3]:.4f}")
        raise RuntimeError("Fallo criterio duro: _repro no coincide bit a bit con el pre-registro.")
    else:
        print("CRITERIO DURO CUMPLIDO: Las 48 celdas coinciden bit a bit.")

    # ------------------------------------------------------------------
    # Extracción de métricas para las 3 configuraciones
    # ------------------------------------------------------------------
    summary_comparison = {}
    for cfg in configs:
        suf = cfg["suffix"]
        name = cfg["name"]
        with open(os.path.join(RESULTS_DIR, f"real_data_results{suf}.json"), "r", encoding="utf-8") as f:
            d = json.load(f)

        cps = d["checkpoints"]

        # 48 FP rates
        fp_ours, fp_adf, fp_pp, fp_dfgls, fp_kpss = [], [], [], [], []
        latencies_ours = []
        latencies_adf = []
        latencies_pp = []
        latencies_dfgls = []
        latencies_kpss = []

        for cp in cps:
            for pid in CONTROL_PERIODS:
                rates = cp["false_positive_rates"].get(pid, {})
                if rates:
                    if rates.get("ours") is not None: fp_ours.append(rates["ours"])
                    if rates.get("adf") is not None: fp_adf.append(rates["adf"])
                    if rates.get("pp") is not None: fp_pp.append(rates["pp"])
                    if rates.get("dfgls") is not None: fp_dfgls.append(rates["dfgls"])
                    if rates.get("kpss") is not None: fp_kpss.append(rates["kpss"])

            for eid, lat in cp.get("latencies", {}).items():
                if isinstance(lat, dict) and lat.get("excluded"): continue
                if lat is None: continue
                if lat.get("ours") is not None: latencies_ours.append(lat["ours"])
                if lat.get("adf") is not None: latencies_adf.append(lat["adf"])
                if lat.get("pp") is not None: latencies_pp.append(lat["pp"])
                if lat.get("dfgls") is not None: latencies_dfgls.append(lat["dfgls"])
                if lat.get("kpss") is not None: latencies_kpss.append(lat["kpss"])

        # Adverse cells
        adverse_cells = {}
        target_keys = [
            ("SP500", 150, "C1_1993"),
            ("NIKKEI", 200, "C2_2005"),
            ("NIKKEI", 300, "C2_2005"),
        ]
        for cp in cps:
            for idx, D, pid in target_keys:
                if cp["index"] == idx and cp["D"] == D:
                    rates = cp["false_positive_rates"].get(pid, {})
                    adverse_cells[f"{idx}_D{D}_{pid}"] = {
                        "ours": rates.get("ours"),
                        "adf": rates.get("adf"),
                        "pp": rates.get("pp"),
                        "dfgls": rates.get("dfgls"),
                        "kpss": rates.get("kpss"),
                    }

        summary_comparison[name] = {
            "mean_fp": {
                "ours": float(np.mean(fp_ours)),
                "adf": float(np.mean(fp_adf)),
                "pp": float(np.mean(fp_pp)),
                "dfgls": float(np.mean(fp_dfgls)) if fp_dfgls else None,
                "kpss": float(np.mean(fp_kpss)),
            },
            "max_fp": {
                "ours": float(np.max(fp_ours)),
                "adf": float(np.max(fp_adf)),
                "pp": float(np.max(fp_pp)),
                "dfgls": float(np.max(fp_dfgls)) if fp_dfgls else None,
                "kpss": float(np.max(fp_kpss)),
            },
            "detections": {
                "ours": len(latencies_ours),
                "adf": len(latencies_adf),
                "pp": len(latencies_pp),
                "dfgls": len(latencies_dfgls),
                "kpss": len(latencies_kpss),
            },
            "mean_latency": {
                "ours": float(np.mean(latencies_ours)) if latencies_ours else None,
                "adf": float(np.mean(latencies_adf)) if latencies_adf else None,
                "pp": float(np.mean(latencies_pp)) if latencies_pp else None,
                "dfgls": float(np.mean(latencies_dfgls)) if latencies_dfgls else None,
                "kpss": float(np.mean(latencies_kpss)) if latencies_kpss else None,
            },
            "adverse_cells": adverse_cells,
        }

    # DKW table
    dkw_table = {}
    for N in [1000, 10000, 50000, 100000]:
        eps = float(np.sqrt(np.log(2.0 / 0.05) / (2.0 * N)))
        dkw_table[str(N)] = round(eps, 4)

    full_output = {
        "summary": summary_comparison,
        "dkw_bounds": dkw_table,
    }

    comp_path = os.path.join(RESULTS_DIR, "real_data_comparison_audit5b.json")
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    print("\n" + "=" * 70)
    print("  RESUMEN COMPARATIVO DATOS REALES")
    print("=" * 70)
    print(f"{'Métrica':<25s} {'_repro':<15s} {'_a1_10k':<15s} {'_a1_50k':<15s}")
    print("-" * 70)
    for metric in ["ours", "adf", "pp", "dfgls", "kpss"]:
        v_rep = summary_comparison["repro"]["mean_fp"].get(metric)
        v_10k = summary_comparison["a1_10k"]["mean_fp"].get(metric)
        v_50k = summary_comparison["a1_50k"]["mean_fp"].get(metric)
        s_rep = f"{v_rep:.5f}" if v_rep is not None else "N/A"
        s_10k = f"{v_10k:.5f}" if v_10k is not None else "N/A"
        s_50k = f"{v_50k:.5f}" if v_50k is not None else "N/A"
        print(f"FP medio {metric:<16s} {s_rep:<15s} {s_10k:<15s} {s_50k:<15s}")

    for metric in ["ours", "adf", "pp", "dfgls", "kpss"]:
        v_rep = summary_comparison["repro"]["max_fp"].get(metric)
        v_10k = summary_comparison["a1_10k"]["max_fp"].get(metric)
        v_50k = summary_comparison["a1_50k"]["max_fp"].get(metric)
        s_rep = f"{v_rep:.4f}" if v_rep is not None else "N/A"
        s_10k = f"{v_10k:.4f}" if v_10k is not None else "N/A"
        s_50k = f"{v_50k:.4f}" if v_50k is not None else "N/A"
        print(f"FP max {metric:<18s} {s_rep:<15s} {s_10k:<15s} {s_50k:<15s}")

    print(f"\nTarea R5 completada en {time.time() - t_start:.1f}s.")


if __name__ == "__main__":
    run_r5()
