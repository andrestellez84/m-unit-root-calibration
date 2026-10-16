import json
import pandas as pd

def mc_err(p):
    return 1.96 * ((p * (1 - p)) / 5000)**0.5 * 100

def main():
    with open("experiments/results_old_audit4/power_comparison_size.json") as f:
        old_sz = json.load(f)['size']
    with open("experiments/results/power_comparison_size.json") as f:
        new_sz = json.load(f)['size']
        
    with open("experiments/results_old_audit4/power_comparison_dgp1.json") as f:
        old_dgp1 = json.load(f)['dgp1']
    with open("experiments/results/power_comparison_dgp1.json") as f:
        new_dgp1 = json.load(f)['dgp1']
        
    # Map old keys to new keys where needed
    # new_sz keys: 'ours_R050', 'adf', 'pp', 'kpss_rej', 'kpss_size'
    # old_sz keys: 'ours', 'adf', 'pp', 'kpss'
    
    tests = [
        ('Propuesto (R=0.5)', 'ours', 'ours_R050'),
        ('ADF', 'adf', 'adf'),
        ('PP', 'pp', 'pp'),
        ('KPSS', 'kpss', 'kpss_rej'),
        ('DF-GLS', 'dfgls', 'dfgls')
    ]
    
    ns = ["200", "500", "1000"]
    
    out_lines = [
        "## 2. Verificación de Tamaño (H0), Filas Completas",
        "| n | Test | Antiguo (%) | Nuevo (%) | Diff (pp) | MC Err | ¿Significativo? |",
        "|---|---|---|---|---|---|---|"
    ]
    
    for n in ns:
        for t_name, old_key, new_key in tests:
            if t_name == 'DF-GLS':
                # DF-GLS size is in DGP1 with rho=1.0
                v_old = old_dgp1[n]["1.0"].get('dfgls')
                v_new = new_dgp1[n]["1.0"].get('dfgls')
            else:
                v_old = old_sz[n].get(old_key)
                v_new = new_sz[n].get(new_key)
                
            if v_old is not None and v_new is not None:
                diff = (v_new - v_old) * 100
                err = mc_err((v_new + v_old)/2)
                sig = "**SÍ**" if abs(diff) > err else "No"
                out_lines.append(f"| {n} | {t_name} | {v_old*100:.2f} | {v_new*100:.2f} | {diff:+.2f} | ±{err:.1f} | {sig} |")
                
    with open("experiments/results/audit4b_tarea2.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

if __name__ == "__main__":
    main()
