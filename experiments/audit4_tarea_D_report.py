import json
import pandas as pd

def load_results(path):
    with open(path, 'r') as f:
        return json.load(f)

def format_latency(val):
    if val is None:
        return "-"
    if isinstance(val, dict) and val.get("excluded"):
        return "N/A"
    return str(val)

def main():
    old_res = load_results("experiments/results/real_data_results.json")['checkpoints']
    new_res = load_results("experiments/results/real_data_results_audit4.json")['checkpoints']
    
    # Latency comparison
    lat_lines = [
        "### Comparación de Latencias (Días de trading)",
        "",
        "| Evento | Índice | D | Antiguo | Nuevo | ¿Cambió? |",
        "|---|---|---|---|---|---|"
    ]
    
    events = [
        'E1_BlackMonday', 'E2_AsianCrisis', 'E3_RussianCrisis', 
        'E4_DotCom', 'E5_Subprime', 'E6_COVID'
    ]
    
    old_map = {(c['index'], c['D']): c for c in old_res}
    new_map = {(c['index'], c['D']): c for c in new_res}
    
    for event in events:
        for idx in ['SP500', 'FTSE', 'NIKKEI', 'DAX']:
            for D in [150, 200, 250, 300]:
                if (idx, D) not in old_map or (idx, D) not in new_map:
                    continue
                o = old_map[(idx, D)]['latencies'].get(event, {})
                n = new_map[(idx, D)]['latencies'].get(event, {})
                
                v_old = o.get('ours') if isinstance(o, dict) else o
                v_new = n.get('ours') if isinstance(n, dict) else n
                
                if isinstance(v_old, dict) and v_old.get('excluded'):
                    continue
                    
                s_old = format_latency(v_old)
                s_new = format_latency(v_new)
                changed = "**SÍ**" if s_old != s_new else "No"
                
                if s_old != "N/A" and s_new != "N/A":
                    lat_lines.append(f"| {event} | {idx} | {D} | {s_old} | {s_new} | {changed} |")
                    
    lat_lines.append("")
    
    # FP comparison
    lat_lines.extend([
        "### Comparación de Tasas de Falsos Positivos",
        "",
        "| Periodo Control | Índice | D | Antiguo (%) | Nuevo (%) | Diff (pp) | ¿Cambió? |",
        "|---|---|---|---|---|---|---|"
    ])
    
    periods = ['C1_Calm90s', 'C2_Mid2000s', 'C3_Mid2010s']
    for p in periods:
        for idx in ['SP500', 'FTSE', 'NIKKEI', 'DAX']:
            for D in [150, 200, 250, 300]:
                if (idx, D) not in old_map or (idx, D) not in new_map:
                    continue
                o = old_map[(idx, D)]['false_positive_rates'].get(p, {})
                n = new_map[(idx, D)]['false_positive_rates'].get(p, {})
                
                if not isinstance(o, dict) or not isinstance(n, dict):
                    continue
                    
                v_old = o.get('ours')
                v_new = n.get('ours')
                
                if v_old is None or v_new is None:
                    continue
                
                diff = (v_new - v_old) * 100
                changed = "**SÍ**" if abs(diff) > 1e-4 else "No"
                lat_lines.append(f"| {p} | {idx} | {D} | {v_old*100:.2f} | {v_new*100:.2f} | {diff:+.2f} | {changed} |")

    lat_lines.append("")
    
    with open("experiments/results/resultados_auditoria_4_D.md", "w", encoding="utf-8") as f:
        f.write("## Tarea D: Análisis Empírico (Aplicación con fórmula corregida)\n\n")
        f.write("\n".join(lat_lines))

if __name__ == "__main__":
    main()
