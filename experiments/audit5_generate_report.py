import os
import json
import hashlib
from datetime import datetime
import pandas as pd

def sha256(path):
    if not os.path.exists(path): return "N/A"
    with open(path, 'rb') as f: return hashlib.sha256(f.read()).hexdigest()

def mtime(path):
    if not os.path.exists(path): return "N/A"
    return datetime.fromtimestamp(os.path.getmtime(path)).isoformat()

def generate_report():
    out = ["# Auditoría A5 - Pre-submission\n"]
    out.append("## Metadatos de la corrida\n")
    
    files = [
        "experiments/results/size_audit5.json",
        "experiments/results/size_robustness_heavy_tails_audit5.json",
        "experiments/results/small_n_size_audit5.json",
        "experiments/results/small_n_ks_audit5.csv",
        "experiments/results/power_comparison_dgp34_alpha1_audit5.json",
        "experiments/results/power_comparison_dgp34_alpha2_audit5.json",
        "experiments/results/rebalance_constants_audit5.json",
        "experiments/results/rhat_distribution_audit5.json",
        "experiments/results/adaptive_size_power_audit5.json",
        "experiments/results/validation_results_audit5_alpha1.json",
        "experiments/results/validation_results_audit5_alpha2.json",
        "experiments/results/adaptive_size_audit5.csv"
    ]
    
    out.append("| Archivo | SHA256 | Mtime |")
    out.append("|---|---|---|")
    for f in files:
        out.append(f"| {os.path.basename(f)} | {sha256(f)} | {mtime(f)} |")
    out.append("\n")

    # Table 1: Size
    out.append("## Tabla 1: Tamaño Empírico bajo H0 (T1)\n")
    if os.path.exists("experiments/results/size_audit5.json"):
        with open("experiments/results/size_audit5.json") as f:
            d = json.load(f)
        out.append("| n | Pilot | R=0.25 | R=0.50 | R=0.75 | DF-GLS | KPSS |")
        out.append("|---|---|---|---|---|---|---|")
        for pilot in ["alpha1", "alpha2"]:
            if pilot not in d: continue
            for n in ["200", "500", "1000"]:
                if n not in d[pilot]: continue
                r = d[pilot][n]
                out.append(f"| {n} | {pilot} | {r.get('ours_R025', 'N/A')} | {r.get('ours_R050', 'N/A')} | {r.get('ours_R075', 'N/A')} | {r.get('dfgls', 'N/A')} | {r.get('kpss_rw', 'N/A')} |")
    out.append("\n")

    # Table 2: Heavy Tails
    out.append("## Tabla 2: Colas Pesadas (T2)\n")
    if os.path.exists("experiments/results/size_robustness_heavy_tails_audit5.json"):
        with open("experiments/results/size_robustness_heavy_tails_audit5.json") as f:
            d = json.load(f)
        out.append("| n | Distribución | Pilot | R=0.25 | R=0.50 | R=0.75 | DF-GLS |")
        out.append("|---|---|---|---|---|---|---|")
        for dist_name, dof_list in [("student-t", [3, 4]), ("chisquare", [3, 5])]:
            for dof in dof_list:
                for pilot in ["alpha1", "alpha2"]:
                    for n in ["200", "500", "1000"]:
                        if pilot in d and str(dof) in d[pilot] and n in d[pilot][str(dof)]:
                            r = d[pilot][str(dof)][n]
                            out.append(f"| {n} | {dist_name}({dof}) | {pilot} | {r.get('ours_R025', 'N/A')} | {r.get('ours_R050', 'N/A')} | {r.get('ours_R075', 'N/A')} | {r.get('dfgls', 'N/A')} |")
    out.append("\n")

    # DGP3 and 4 Power
    out.append("## Potencia DGP3 y DGP4 (T4)\n")
    out.append("| DGP | n | r | Pilot | R=0.25 | R=0.50 | R=0.75 | DF-GLS | KPSS |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for pilot in ["alpha1", "alpha2"]:
        fp = f"experiments/results/power_comparison_dgp34_{pilot}_audit5.json"
        if os.path.exists(fp):
            with open(fp) as f:
                d = json.load(f)
            for dgp in ["dgp3", "dgp4"]:
                if dgp not in d: continue
                for n in ["200", "500", "1000"]:
                    if n not in d[dgp]: continue
                    for r_val, res in d[dgp][n].items():
                        out.append(f"| {dgp.upper()} | {n} | {r_val} | {pilot} | {res.get('ours_R025', 'N/A')} | {res.get('ours_R050', 'N/A')} | {res.get('ours_R075', 'N/A')} | {res.get('dfgls', 'N/A')} | {res.get('kpss_rej', 'N/A')} |")
    out.append("\n")

    # T5: R_hat distribution
    out.append("## Tabla 13: Distribución del Ponderador R_hat (T5)\n")
    if os.path.exists("experiments/results/rhat_distribution_audit5.json"):
        with open("experiments/results/rhat_distribution_audit5.json") as f:
            d = json.load(f)
        out.append("| Scenario | Pilot | R_hat Mean | Median | q05-q95 | R_bal Mean | Median | q05-q95 |")
        out.append("|---|---|---|---|---|---|---|---|")
        for pilot in ["alpha1", "alpha2"]:
            if pilot not in d: continue
            for sc, res in d[pilot].items():
                rhat = res.get('r_hat', {})
                rbal = res.get('r_bal', {})
                out.append(f"| {sc} | {pilot} | {rhat.get('mean', 'N/A'):.3f} | {rhat.get('median', 'N/A'):.3f} | [{rhat.get('q05', 'N/A'):.3f}, {rhat.get('q95', 'N/A'):.3f}] | {rbal.get('mean', 'N/A'):.3f} | {rbal.get('median', 'N/A'):.3f} | [{rbal.get('q05', 'N/A'):.3f}, {rbal.get('q95', 'N/A'):.3f}] |")
    out.append("\n")

    # T6: Adaptive Size and Power
    out.append("## Tabla 14: Tamaño y Potencia Adaptativa (T6)\n")
    if os.path.exists("experiments/results/adaptive_size_power_audit5.json"):
        with open("experiments/results/adaptive_size_power_audit5.json") as f:
            d = json.load(f)
        out.append("| Scenario | Pilot | R_hat | R_bal |")
        out.append("|---|---|---|---|")
        for pilot in ["alpha1", "alpha2"]:
            if pilot not in d: continue
            for sc, res in d[pilot].items():
                out.append(f"| {sc} | {pilot} | {res.get('R_hat', 'N/A')} | {res.get('R_bal', 'N/A')} |")
    out.append("\n")

    # T7: Real Data Validation
    out.append("## Tabla 16: Tasas de Falsos Positivos Datos Reales (T7)\n")
    for pilot in ["alpha1", "alpha2"]:
        fp_path = f"experiments/results/validation_results_audit5_{pilot}.json"
        if os.path.exists(fp_path):
            with open(fp_path) as f:
                d = json.load(f)
            fp_rates = d.get("fp_rates", {})
            out.append(f"### Pilot: {pilot}\n")
            out.append("| Period | Index | D | Ours | ADF | PP | DF-GLS | KPSS |")
            out.append("|---|---|---|---|---|---|---|---|")
            for k, row in fp_rates.items():
                parts = k.split("_") # C1_1993_SP500_150
                if len(parts) >= 4:
                    period = f"{parts[0]}_{parts[1]}"
                    idx = parts[2]
                    D = parts[3]
                    out.append(f"| {period} | {idx} | {D} | {row.get('ours', 'N/A'):.3f} | {row.get('adf', 'N/A'):.3f} | {row.get('pp', 'N/A'):.3f} | {row.get('dfgls', 'N/A'):.3f} | {row.get('kpss', 'N/A'):.3f} |")
    out.append("\n")

    # T10: Tiempos de ejecucion
    out.append("## Tiempos de Ejecución (T10)\n")
    out.append("Ver archivo: `experiments/results/tarea10_audit5.log`\n")
    
    # Write output
    with open("experiments/results/resultados_auditoria_5.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    
    print("Report generated at experiments/results/resultados_auditoria_5.md")

if __name__ == "__main__":
    generate_report()
