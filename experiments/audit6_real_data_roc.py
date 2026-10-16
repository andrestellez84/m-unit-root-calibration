"""
Auditoría A6 — Componente 2: Detección a Igualada Tasa de Falsa Alarma (ARL0, ARL1, ROC y AUC).

Métricas:
  1. Calibración a FPR igualada: Umbral c_alpha* ajustado en ventanas de control
     para igualar la tasa de falsa alarma a alpha* = 0.0277 (media de Ours) y alpha* = 0.0500.
  2. ARL0 (Average Run Length bajo H0): Longitudes de racha reales entre episodios de alarma
     agrupando rechazos contiguos (gap <= 5 días).
  3. ARL1 (Latencia media de detección): Días de negociación hasta la primera alarma post-evento
     en las 6 crisis pre-registradas (ventana de búsqueda = 120 días).
  4. ROC Operativa de Monitoreo y AUC: Evaluación no paramétrica barriendo umbrales continuos,
     con H0 definida por las ventanas de control y H1 definida por el calendario de eventos.
"""

import os
import sys
import time
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
INDICES = ["SP500", "FTSE", "NIKKEI", "DAX"]
WINDOW_SIZES = [150, 200, 250, 300]

CONTROL_PERIODS = {
    "C1_1993": ("1993-01-01", "1993-12-31"),
    "C2_2005": ("2005-01-01", "2005-12-31"),
    "C3_2017": ("2017-01-01", "2017-12-31"),
}

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

LATENCY_MAX_WINDOW = 120
CLUSTER_GAP_TOLERANCE = 5  # Días de tolerancia para agrupar alarmas contiguas


def load_all_rolling_data():
    """Load the 16 rolling analysis files."""
    datasets = {}
    for idx in INDICES:
        datasets[idx] = {}
        for D in WINDOW_SIZES:
            path = os.path.join(RESULTS_DIR, f"rolling_{idx}_D{D}.json")
            with open(path, "r", encoding="utf-8") as f:
                datasets[idx][D] = json.load(f)
    return datasets


def extract_period_mask(dates: list[str], start_date: str, end_date: str) -> np.ndarray:
    """Boolean mask for dates in [start_date, end_date]."""
    arr = np.array(dates)
    return (arr >= start_date) & (arr <= end_date)


def extract_post_event_mask(dates: list[str], event_date: str, max_days: int = 120) -> tuple[np.ndarray, int]:
    """Boolean mask for the max_days trading days following an event."""
    arr = np.array(dates)
    indices = np.where(arr >= event_date)[0]
    if len(indices) == 0:
        return np.zeros(len(dates), dtype=bool), -1
    start_idx = indices[0]
    end_idx = min(start_idx + max_days, len(dates))
    mask = np.zeros(len(dates), dtype=bool)
    mask[start_idx:end_idx] = True
    return mask, start_idx


def compute_empirical_fpr(p_vals: np.ndarray, threshold: float, is_kpss: bool = False) -> float:
    """Compute empirical false positive rate under a given threshold."""
    valid = p_vals[~np.isnan(p_vals)]
    if len(valid) == 0:
        return 0.0
    if is_kpss:
        rejections = np.sum(valid < threshold)  # KPSS rejects stationarity when p < alpha
    else:
        rejections = np.sum(valid < threshold)
    return float(rejections / len(valid))


def calibrate_threshold_for_target_fpr(control_pvals: np.ndarray, target_fpr: float, is_kpss: bool = False) -> float:
    """Find the threshold c_alpha* such that FPR(c_alpha*) <= target_fpr."""
    valid = control_pvals[~np.isnan(control_pvals)]
    if len(valid) == 0:
        return 0.05
    # For lower-tail rejections (p < threshold), threshold is the target_fpr-th quantile
    return float(np.quantile(valid, target_fpr))


def compute_clustered_arl0(dates: list[str], p_vals: np.ndarray, threshold: float, gap_tolerance: int = 5) -> tuple[float, int, list[int]]:
    """
    Compute actual run lengths between alarm clusters in control periods.

    Clustering rule:
      An alarm cluster starts on the first date where p_t < threshold.
      It ends when no alarm occurs for more than `gap_tolerance` trading days.
      Run length is the number of trading days between consecutive cluster onsets.
    """
    is_alarm = np.array([p is not None and not np.isnan(p) and p < threshold for p in p_vals])
    alarm_indices = np.where(is_alarm)[0]

    if len(alarm_indices) == 0:
        # No false alarms: run length spans the entire control sample
        return float(len(dates)), 0, [len(dates)]

    # Group into clusters
    clusters = []
    current_cluster = [alarm_indices[0]]

    for idx in alarm_indices[1:]:
        if idx - current_cluster[-1] <= gap_tolerance:
            current_cluster.append(idx)
        else:
            clusters.append(current_cluster)
            current_cluster = [idx]
    clusters.append(current_cluster)

    # Inter-cluster run lengths (in trading days)
    run_lengths = []
    # Run before first cluster
    run_lengths.append(clusters[0][0])
    # Runs between clusters (from end of cluster i to start of cluster i+1)
    for c_prev, c_next in zip(clusters[:-1], clusters[1:]):
        run_lengths.append(c_next[0] - c_prev[-1])
    # Run after last cluster to end of sample
    run_lengths.append(len(dates) - 1 - clusters[-1][-1])

    mean_run_length = float(np.mean(run_lengths)) if len(run_lengths) > 0 else float(len(dates))
    return mean_run_length, len(clusters), run_lengths


def compute_event_latency(dates: list[str], p_vals: np.ndarray, event_date: str, threshold: float, max_days: int = 120) -> int:
    """
    Compute trading days from event date to first rejection under threshold.
    Capped at max_days if no detection occurs.
    """
    arr = np.array(dates)
    indices = np.where(arr >= event_date)[0]
    if len(indices) == 0:
        return max_days
    start_idx = indices[0]
    end_idx = min(start_idx + max_days, len(dates))

    for offset, j in enumerate(range(start_idx, end_idx)):
        p = p_vals[j]
        if p is not None and not np.isnan(p) and p < threshold:
            return offset
    return max_days


def compute_roc_and_auc(control_pvals: np.ndarray, crisis_pvals: np.ndarray, n_points: int = 200) -> tuple[list[float], list[float], float]:
    """
    Compute empirical ROC curve (FPR vs TPR) and AUC by sweeping thresholds.
    """
    clean_ctrl = control_pvals[~np.isnan(control_pvals)]
    clean_crisis = crisis_pvals[~np.isnan(crisis_pvals)]

    if len(clean_ctrl) == 0 or len(clean_crisis) == 0:
        return [0.0, 1.0], [0.0, 1.0], 0.5

    # Evaluation grid from 0 to 1 with logarithmic spacing near 0
    grid_low = np.logspace(-4, -1, n_points // 2)
    grid_high = np.linspace(0.1, 1.0, n_points // 2)
    thresholds = np.unique(np.concatenate(([0.0], grid_low, grid_high, [1.0])))
    thresholds = np.sort(thresholds)

    fpr_list = []
    tpr_list = []

    for th in thresholds:
        fpr = np.mean(clean_ctrl < th)
        tpr = np.mean(clean_crisis < th)
        fpr_list.append(float(fpr))
        tpr_list.append(float(tpr))

    # Ensure monotonic curve for trapezoidal rule
    fpr_arr = np.array(fpr_list)
    tpr_arr = np.array(tpr_list)
    sort_idx = np.lexsort((tpr_arr, fpr_arr))
    fpr_sorted = fpr_arr[sort_idx]
    tpr_sorted = tpr_arr[sort_idx]

    auc = float(np.trapezoid(tpr_sorted, fpr_sorted))
    return fpr_sorted.tolist(), tpr_sorted.tolist(), float(round(auc, 4))


def run_full_real_data_roc_analysis():
    print("=" * 70)
    print("  Auditoría A6 — Componente 2: Métricas a Tasa de Falsa Alarma Igualada")
    print("  y ROC Operativa de Monitoreo")
    print("=" * 70)

    datasets = load_all_rolling_data()
    methods = ["ours", "adf", "pp", "dfgls", "kpss"]
    method_pkeys = {
        "ours": "p_ours",
        "adf": "p_adf",
        "pp": "p_pp",
        "dfgls": "p_dfgls",
        "kpss": "p_kpss",
    }

    # Aggregate pooled control windows and pooled crisis windows across all 16 series
    pooled_control_pvals = {m: [] for m in methods}
    pooled_crisis_pvals = {m: [] for m in methods}

    for idx in INDICES:
        for D in WINDOW_SIZES:
            r = datasets[idx][D]
            dates = r["dates"]

            # Control masks
            for c_name, (c_start, c_end) in CONTROL_PERIODS.items():
                c_mask = extract_period_mask(dates, c_start, c_end)
                for m in methods:
                    p_arr = np.array([np.nan if x is None else float(x) for x in r[method_pkeys[m]]])
                    pooled_control_pvals[m].extend(p_arr[c_mask].tolist())

            # Crisis masks
            for e_name, e_date in EVENTS.items():
                if (idx, e_name) in EXCLUSIONS:
                    continue
                e_mask, _ = extract_post_event_mask(dates, e_date, LATENCY_MAX_WINDOW)
                for m in methods:
                    p_arr = np.array([np.nan if x is None else float(x) for x in r[method_pkeys[m]]])
                    pooled_crisis_pvals[m].extend(p_arr[e_mask].tolist())

    for m in methods:
        pooled_control_pvals[m] = np.array(pooled_control_pvals[m])
        pooled_crisis_pvals[m] = np.array(pooled_crisis_pvals[m])

    # 1. Uncalibrated (Nominal alpha = 0.05) metrics
    print("\n--- 1. Métricas con Umbral Nominal alpha = 0.05 ---")
    nominal_thresholds = {m: 0.05 for m in methods}
    uncalibrated_summary = {}

    for m in methods:
        fpr = float(np.mean(pooled_control_pvals[m] < 0.05))
        uncalibrated_summary[m] = {"nominal_alpha": 0.05, "empirical_fpr": float(round(fpr, 4))}
        print(f"  {m.upper():6s}: Empirical FPR en Control = {fpr:.4f}")

    # Baseline Ours FPR to match
    ours_mean_fpr = uncalibrated_summary["ours"]["empirical_fpr"]  # ≈ 0.0277

    # 2. Calibrated Thresholds to Equalize FPR at alpha* = 0.0277 and alpha* = 0.0500
    print(f"\n--- 2. Calibración a FPR Igualada (Targets: alpha*={ours_mean_fpr:.4f} y alpha*=0.0500) ---")
    calibrated_thresholds_ours = {}
    calibrated_thresholds_0500 = {}

    for m in methods:
        c_th_ours = calibrate_threshold_for_target_fpr(pooled_control_pvals[m], ours_mean_fpr, is_kpss=(m == "kpss"))
        c_th_0500 = calibrate_threshold_for_target_fpr(pooled_control_pvals[m], 0.0500, is_kpss=(m == "kpss"))
        calibrated_thresholds_ours[m] = c_th_ours
        calibrated_thresholds_0500[m] = c_th_0500
        print(f"  {m.upper():6s}: Umbral c* (FPR={ours_mean_fpr:.4f}) = {c_th_ours:.6f} | c* (FPR=0.050) = {c_th_0500:.6f}")

    # 3. Compute ARL0 and ARL1 under Nominal and Matched Thresholds
    print("\n--- 3. Cómputo de ARL0 (inter-alarm run length) y ARL1 (latencia) ---")
    eval_regimes = {
        "nominal_005": nominal_thresholds,
        f"matched_ours_{ours_mean_fpr:.4f}": calibrated_thresholds_ours,
        "matched_0050": calibrated_thresholds_0500,
    }

    regime_results = {}

    for regime_name, thresholds in eval_regimes.items():
        regime_results[regime_name] = {"thresholds": thresholds, "arl0": {}, "arl1": {}, "clusters_count": {}}

        for m in methods:
            th = thresholds[m]
            # Run lengths across all 48 control series (4 indices x 4 windows x 3 periods)
            all_ctrl_runs = []
            total_clusters = 0

            for idx in INDICES:
                for D in WINDOW_SIZES:
                    r = datasets[idx][D]
                    dates = r["dates"]
                    p_arr = np.array([np.nan if x is None else float(x) for x in r[method_pkeys[m]]])

                    for c_name, (c_start, c_end) in CONTROL_PERIODS.items():
                        c_mask = extract_period_mask(dates, c_start, c_end)
                        c_dates = np.array(dates)[c_mask].tolist()
                        c_pvals = p_arr[c_mask]

                        arl0_cell, n_clust, runs = compute_clustered_arl0(c_dates, c_pvals, th, gap_tolerance=CLUSTER_GAP_TOLERANCE)
                        all_ctrl_runs.extend(runs)
                        total_clusters += n_clust

            mean_arl0 = float(np.mean(all_ctrl_runs)) if len(all_ctrl_runs) > 0 else float(len(c_dates))

            # Latencies across all valid crisis events (13 to 24 valid combinations)
            latencies = []
            for idx in INDICES:
                for D in WINDOW_SIZES:
                    r = datasets[idx][D]
                    dates = r["dates"]
                    p_arr = np.array([np.nan if x is None else float(x) for x in r[method_pkeys[m]]])

                    for e_name, e_date in EVENTS.items():
                        if (idx, e_name) in EXCLUSIONS:
                            continue
                        lat = compute_event_latency(dates, p_arr, e_date, th, max_days=LATENCY_MAX_WINDOW)
                        latencies.append(lat)

            mean_arl1 = float(np.mean(latencies))

            regime_results[regime_name]["arl0"][m] = float(round(mean_arl0, 2))
            regime_results[regime_name]["arl1"][m] = float(round(mean_arl1, 2))
            regime_results[regime_name]["clusters_count"][m] = int(total_clusters)

            print(
                f"  [{regime_name:18s}] {m.upper():6s} (th={th:.5f}): "
                f"ARL0 = {mean_arl0:6.1f} días ({total_clusters:3d} alarmas) | "
                f"ARL1 = {mean_arl1:5.1f} días"
            )

    # 4. ROC Operativa de Monitoreo and AUC per Procedure
    print("\n--- 4. Curvas ROC Operativa de Monitoreo y AUC ---")
    roc_results = {}
    for m in methods:
        fprs, tprs, auc = compute_roc_and_auc(pooled_control_pvals[m], pooled_crisis_pvals[m])
        # Downsample ROC points for compact storage (keep ~50 points)
        step = max(len(fprs) // 50, 1)
        sampled_fpr = fprs[::step]
        sampled_tpr = tprs[::step]
        if fprs[-1] not in sampled_fpr:
            sampled_fpr.append(fprs[-1])
            sampled_tpr.append(tprs[-1])

        roc_results[m] = {
            "auc": auc,
            "sampled_fpr": [float(round(x, 4)) for x in sampled_fpr],
            "sampled_tpr": [float(round(x, 4)) for x in sampled_tpr],
        }
        print(f"  {m.upper():6s}: AUC = {auc:.4f}")

    payload = {
        "metadata": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "indices": INDICES,
            "window_sizes": WINDOW_SIZES,
            "control_periods": CONTROL_PERIODS,
            "events": EVENTS,
            # ordenado: EXCLUSIONS es un conjunto y su orden de iteracion no
            # es estable entre corridas, lo que hacia fallar el control de
            # regresion por una permutacion cosmetica de metadatos.
            "exclusions": sorted([list(x) for x in EXCLUSIONS]),
            "clustering_gap_tolerance": CLUSTER_GAP_TOLERANCE,
            "latency_max_window": LATENCY_MAX_WINDOW,
            "definition_note": (
                "La curva ROC se etiqueta explícitamente como 'ROC operativa de monitoreo'. "
                "La clase positiva H1 se define operacionalmente por el calendario de eventos históricos "
                "pre-registrados (E1-E6), no por la hipótesis de estacionariedad subyacente. En §6.3 se "
                "sostiene que el proceso de precios preserva su raíz unitaria en crisis y lo que se detecta "
                "es la perturbación estructural del régimen estocástico."
            ),
        },
        "uncalibrated_summary": uncalibrated_summary,
        "regime_results": regime_results,
        "roc_results": roc_results,
    }

    out_file = os.path.join(RESULTS_DIR, "real_data_arl_roc_audit6.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\n======================================================================")
    print(f"  Resultados de ARL y ROC guardados en: {out_file}")
    print(f"======================================================================\n")
    return payload


if __name__ == "__main__":
    run_full_real_data_roc_analysis()
