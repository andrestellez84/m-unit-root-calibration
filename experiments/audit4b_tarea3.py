import json

def load_results(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    old_res = load_results("experiments/results/real_data_results.json")['checkpoints']
    new_res = load_results("experiments/results/real_data_results_audit4.json")['checkpoints']
    
    old_map = {(c['index'], c['D']): c for c in old_res}
    new_map = {(c['index'], c['D']): c for c in new_res}
    
    tests = ['ours', 'adf', 'pp', 'kpss', 'dfgls']
    periods = ['C1_1993', 'C2_2005', 'C3_2017']
    
    # Actually, in the old json the periods were 'C1_Calm90s', etc.
    # But in new_res they are 'C1_1993', 'C2_2005', 'C3_2017'.
    # Let's check old_res keys.
    sample_old_fpr = list(old_map.values())[0]['false_positive_rates']
    sample_new_fpr = list(new_map.values())[0]['false_positive_rates']
    
    old_period_keys = list(sample_old_fpr.keys())
    new_period_keys = list(sample_new_fpr.keys())
    
    period_mapping = dict(zip(old_period_keys, new_period_keys))
    
    changes = []
    
    # Store rates to compute mean and max
    ours_old_rates = []
    ours_new_rates = []
    
    for p_old, p_new in period_mapping.items():
        for idx in ['SP500', 'FTSE', 'NIKKEI', 'DAX']:
            for D in [150, 200, 250, 300]:
                if (idx, D) not in old_map or (idx, D) not in new_map:
                    continue
                o = old_map[(idx, D)]['false_positive_rates'].get(p_old, {})
                n = new_map[(idx, D)]['false_positive_rates'].get(p_new, {})
                
                if not isinstance(o, dict) or not isinstance(n, dict):
                    continue
                    
                v_old = o.get('ours')
                v_new = n.get('ours')
                
                if v_old is not None and v_new is not None:
                    ours_old_rates.append(v_old)
                    ours_new_rates.append(v_new)
                    diff = (v_new - v_old)
                    if abs(diff) > 0.005:
                        changes.append((p_new, idx, D, v_old, v_new, diff))
                        
                # Sanity check controls
                for t in ['adf', 'pp', 'kpss', 'dfgls']:
                    # Note kpss and dfgls might not be present in old
                    vo = o.get(t)
                    vn = n.get(t)
                    if vo is not None and vn is not None:
                        if abs(vo - vn) > 1e-4:
                            print(f"WARNING: Control {t} changed in {p_new} {idx} {D}: {vo} -> {vn}")
                            
    mean_old = sum(ours_old_rates) / len(ours_old_rates) if ours_old_rates else 0
    mean_new = sum(ours_new_rates) / len(ours_new_rates) if ours_new_rates else 0
    max_old = max(ours_old_rates) if ours_old_rates else 0
    max_new = max(ours_new_rates) if ours_new_rates else 0
    
    out = [
        "## 3. Falsos Positivos en Datos Reales",
        f"- Celdas analizadas: {len(ours_old_rates)}",
        f"- Tasa media (Antiguo): {mean_old*100:.2f}% | Tasa media (Nuevo): {mean_new*100:.2f}%",
        f"- Tasa máxima (Antiguo): {max_old*100:.2f}% | Tasa máxima (Nuevo): {max_new*100:.2f}%",
        f"- Celdas con cambio > 0.5 pp: {len(changes)}",
        ""
    ]
    
    if changes:
        out.extend([
            "| Periodo | Índice | D | Antiguo (%) | Nuevo (%) | Diff (pp) |",
            "|---|---|---|---|---|---|"
        ])
        for p, idx, D, vo, vn, diff in changes:
            out.append(f"| {p} | {idx} | {D} | {vo*100:.2f} | {vn*100:.2f} | {diff*100:+.2f} |")
            
    with open("experiments/results/audit4b_tarea3.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    main()
