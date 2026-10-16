import os
import sys
import json
import subprocess
import math
import argparse

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compare-only', action='store_true')
    args = parser.parse_args()

    if not args.compare_only:
        # 1. Regenerate
        # run_cmd("python experiments/size_robustness_heavy_tails.py") # DONE
        # run_cmd("python experiments/power_comparison.py SIZE") # DONE
        # run_cmd("python experiments/power_comparison.py DGP1") # DONE
        run_cmd("python experiments/power_comparison.py DGP2")
        run_cmd("python experiments/power_comparison.py DGP34")
        run_cmd("python experiments/extend_dgp1_dfgls.py")
        run_cmd("python experiments/extend_dgp23_dfgls.py")
    
    # 2. Compare
    print("Regeneration complete. Comparing...")
    
    out_lines = []
    out_lines.append("## Tarea C: Comparación de Experimentos Sintéticos (Antes vs Después)")
    
    # helper for mc error
    def mc_err(p, n=5000):
        # 1.96 * sqrt(p*(1-p)/n)
        return 1.96 * math.sqrt(p * (1 - p) / n) * 100
    
    # DGP1
    with open("experiments/results_old_audit4/power_comparison_dgp1.json") as f:
        old_dgp1 = json.load(f)['dgp1']
    with open("experiments/results/power_comparison_dgp1.json") as f:
        new_dgp1 = json.load(f)['dgp1']
        
    out_lines.append("\n### DGP 1 (AR(1) alternatives)")
    out_lines.append("| n | rho | Test | Antiguo (%) | Nuevo (%) | Diff (pp) | MC Err | ¿Significativo? |")
    out_lines.append("|---|---|---|---|---|---|---|---|")
    
    tests = ['ours_R050', 'adf', 'pp', 'kpss_rej', 'dfgls']
    test_names = {'ours_R050': 'Propuesto (R=0.5)', 'adf': 'ADF', 'pp': 'PP', 'kpss_rej': 'KPSS', 'dfgls': 'DF-GLS'}
    
    def compare_dgp(old_dgp, new_dgp, name, param_name="rho"):
        out = [f"### {name}"]
        out.append(f"| n | {param_name} | Test | Antiguo (%) | Nuevo (%) | Diff (pp) | MC Err | ¿Significativo? |")
        out.append(f"|---|---|---|---|---|---|---|---|")
        for n in sorted(old_dgp.keys(), key=int):
            for param in sorted(old_dgp[n].keys(), key=float):
                for t in tests:
                    v_old = old_dgp[n][param].get(t, None)
                    v_new = new_dgp[n][param].get(t, None)
                    if v_old is not None and v_new is not None:
                        diff = (v_new - v_old) * 100
                        err = mc_err((v_new + v_old)/2)
                        sig = "**SÍ**" if abs(diff) > err else "No"
                        out.append(f"| {n} | {param} | {test_names[t]} | {v_old*100:.1f} | {v_new*100:.1f} | {diff:+.1f} | ±{err:.1f} | {sig} |")
        return "\n".join(out)
        
    out_lines.append(compare_dgp(old_dgp1, new_dgp1, "DGP 1 (AR(1) alternatives)"))
    
    with open("experiments/results_old_audit4/power_comparison_dgp2.json") as f:
        old_dgp2 = json.load(f)['dgp2']
    with open("experiments/results/power_comparison_dgp2.json") as f:
        new_dgp2 = json.load(f)['dgp2']
    out_lines.append("\n" + compare_dgp(old_dgp2, new_dgp2, "DGP 2 (Mean Break)", "break_ratio"))
    
    with open("experiments/results_old_audit4/power_comparison_dgp3.json") as f:
        old_dgp3 = json.load(f)['dgp3']
    with open("experiments/results/power_comparison_dgp3.json") as f:
        new_dgp3 = json.load(f)['dgp3']
    out_lines.append("\n" + compare_dgp(old_dgp3, new_dgp3, "DGP 3 (Variance Break)", "break_ratio"))
    
    with open("experiments/results_old_audit4/power_comparison_dgp4.json") as f:
        old_dgp4 = json.load(f)['dgp4']
    with open("experiments/results/power_comparison_dgp4.json") as f:
        new_dgp4 = json.load(f)['dgp4']
    out_lines.append("\n" + compare_dgp(old_dgp4, new_dgp4, "DGP 4 (Trend)", "slope"))
    
    # Size
    with open("experiments/results_old_audit4/power_comparison_size.json") as f:
        old_sz = json.load(f)['size']
    with open("experiments/results/power_comparison_size.json") as f:
        new_sz = json.load(f)['size']
    out_lines.append("\n### Verificación de Tamaño (H0)")
    out_lines.append("| n | Test | Antiguo (%) | Nuevo (%) | Diff (pp) | MC Err | ¿Significativo? |")
    out_lines.append("|---|---|---|---|---|---|---|")
    for n in sorted(old_sz.keys(), key=int):
        for t in tests:
            if t == 'dfgls': continue
            v_old = old_sz[n].get(t, None)
            v_new = new_sz[n].get(t, None)
            if v_old is not None and v_new is not None:
                diff = (v_new - v_old) * 100
                err = mc_err((v_new + v_old)/2)
                sig = "**SÍ**" if abs(diff) > err else "No"
                out_lines.append(f"| {n} | {test_names[t]} | {v_old*100:.2f} | {v_new*100:.2f} | {diff:+.2f} | ±{err:.1f} | {sig} |")
                
    # Heavy tails
    with open("experiments/results_old_audit4/size_robustness_heavy_tails.json") as f:
        old_ht = json.load(f)
    with open("experiments/results/size_robustness_heavy_tails.json") as f:
        new_ht = json.load(f)
    out_lines.append("\n### Robustez de Tamaño (Colas Pesadas)")
    out_lines.append("| Dist | n | Test | Antiguo (%) | Nuevo (%) | Diff (pp) | MC Err | ¿Significativo? |")
    out_lines.append("|---|---|---|---|---|---|---|---|")
    old_ht_res = old_ht.get('results', old_ht)
    new_ht_res = new_ht.get('results', new_ht)
    for dist in old_ht_res.keys():
        if dist in ['completed_at', 'alpha', 'N_sim', 'description', 'distributions', 'config']: continue
        for n in sorted(old_ht_res[dist].keys(), key=int):
            for t in ['ours', 'adf', 'pp', 'kpss']:
                v_old = old_ht_res[dist][n].get(t, None)
                v_new = new_ht_res[dist][n].get(t, None)
                if v_old is not None and v_new is not None:
                    diff = (v_new - v_old) * 100
                    err = mc_err((v_new + v_old)/2)
                    sig = "**SÍ**" if abs(diff) > err else "No"
                    out_lines.append(f"| {dist} | {n} | {t.upper()} | {v_old*100:.2f} | {v_new*100:.2f} | {diff:+.2f} | ±{err:.1f} | {sig} |")

    with open("experiments/results/comparacion_audit4.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
        
    # Append to main audit 4 report
    with open("experiments/results/resultados_auditoria_4.md", "a", encoding="utf-8") as f:
        f.write("\n\n" + "\n".join(out_lines))

if __name__ == "__main__":
    main()
