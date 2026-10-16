import numpy as np
import pandas as pd
from stationarity_test.hac_estimator import hac_newey_west

def generate_ar1(n, rho, rng):
    eps = rng.standard_normal(n)
    Y = np.zeros(n + 1)
    for t in range(n):
        Y[t+1] = rho * Y[t] + eps[t]
    return Y

def get_median_B(n, rho, reps=200, seed=42):
    rng = np.random.default_rng(seed)
    Bs = []
    for _ in range(reps):
        Y = generate_ar1(n, rho, rng)
        diffs = np.diff(Y)
        gamma_0 = np.var(diffs)
        gamma_1 = np.cov(diffs[:-1], diffs[1:])[0, 1] if gamma_0 > 0 else 0.0
        rho_hat = gamma_1 / gamma_0 if gamma_0 > 0 else 0.0
        rho_hat = np.clip(rho_hat, -0.99, 0.99)
        alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat**2)**2, 1e-10)
        B_ceil = np.ceil(1.1447 * (alpha_hat * len(diffs)) ** (1.0 / 3.0))
        Bs.append(B_ceil)
    return np.median(Bs)

def search_n(rho):
    lo = 10
    hi = 50000
    
    if get_median_B(hi, rho) < 3:
        return hi
    
    while lo < hi:
        mid = (lo + hi) // 2
        med_B = get_median_B(mid, rho)
        if med_B >= 3:
            hi = mid
        else:
            lo = mid + 1
    return lo

def main():
    rhos = [0.5, 0.8, 0.9, 0.95, 0.99]
    results = []
    
    for rho in rhos:
        print(f"Búsqueda para rho = {rho}...")
        n_crit = search_n(rho)
        n_aprox = 1.0 / ((1 - rho)**2)
        results.append({
            'rho': rho,
            'n_critico (B>=3)': n_crit,
            'n_aprox (1-rho)^-2': n_aprox,
            'Ratio': n_crit / n_aprox
        })
        
    df = pd.DataFrame(results)
    def to_md(df):
        cols = df.columns.tolist()
        header = "| " + " | ".join(cols) + " |"
        sep = "|" + "|".join(["---"]*len(cols)) + "|"
        lines = [header, sep]
        for _, row in df.iterrows():
            vals = []
            for val in row:
                if isinstance(val, float):
                    vals.append(f"{val:.2f}")
                else:
                    vals.append(str(val))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)
    
    md_table = to_md(df)
    print(md_table)
    
    with open("experiments/results/resultados_auditoria_4_F.md", "w", encoding="utf-8") as f:
        f.write("\n## Tarea F: Frontera Asintótica Empírica del Ancho de Banda\n\n")
        f.write(md_table)

if __name__ == "__main__":
    main()
