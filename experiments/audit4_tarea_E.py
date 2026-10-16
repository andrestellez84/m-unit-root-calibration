import numpy as np
import pandas as pd
from scipy.stats import linregress
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.hac_estimator import hac_newey_west

def generate_ar1(n, rho, rng):
    eps = rng.standard_normal(n)
    Y = np.zeros(n + 1)
    for t in range(n):
        Y[t+1] = rho * Y[t] + eps[t]
    return Y

def generate_rw(n, rng):
    return generate_ar1(n, 1.0, rng)

def analyze():
    n_grid = [200, 500, 1000, 2000, 5000]
    rhos = [("RW", 1.0), ("AR 0.95", 0.95), ("AR 0.5", 0.5)]
    reps = 500
    rng = np.random.default_rng(42)
    
    results = []
    
    for label, rho in rhos:
        print(f"Processing {label}...")
        means_n = {n: [] for n in n_grid}
        
        for n in n_grid:
            theta_1, theta_2 = 0.1, 0.1
            tau_1 = max(2, int(round(theta_1 * n)))
            tau_2 = max(2, int(round(theta_2 * n)))
            
            for _ in range(reps):
                if rho == 1.0:
                    Y = generate_rw(n, rng)
                else:
                    Y = generate_ar1(n, rho, rng)
                
                # Raw stats
                means = rolling_mean(Y, tau_1)
                g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
                variances = rolling_var(Y, tau_2)
                g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))
                
                # HAC
                diffs = np.diff(Y)
                n_diffs = len(diffs)
                gamma_0 = np.var(diffs)
                gamma_1 = np.cov(diffs[:-1], diffs[1:])[0, 1] if gamma_0 > 0 else 0.0
                rho_hat = gamma_1 / gamma_0 if gamma_0 > 0 else 0.0
                rho_hat = np.clip(rho_hat, -0.99, 0.99)
                
                alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat**2)**2, 1e-10)
                B_pre = 1.1447 * (alpha_hat * n_diffs) ** (1.0 / 3.0)
                B_ceil = np.ceil(B_pre)
                
                s2 = hac_newey_west(diffs)
                
                # We need to measure how g1 and g2 scale with n
                # g1 scales with n^(c1/2) * s = n^0.5 * s
                # g2 scales with n^(c2/2) * s2 = n^1.0 * s2
                
                means_n[n].append({
                    'rho_hat': rho_hat,
                    'alpha_hat': alpha_hat,
                    'B_pre': B_pre,
                    'B_ceil': B_ceil,
                    'g1_raw': g1_raw,
                    'g2_raw': g2_raw,
                    's': np.sqrt(s2),
                    's2': s2
                })
        
        # Now compute log-log slopes across n
        # For each n, get the mean of each quantity
        B_pre_means = [np.mean([x['B_pre'] for x in means_n[n]]) for n in n_grid]
        B_ceil_means = [np.mean([x['B_ceil'] for x in means_n[n]]) for n in n_grid]
        g1_means = [np.mean([x['g1_raw'] for x in means_n[n]]) for n in n_grid]
        g2_means = [np.mean([x['g2_raw'] for x in means_n[n]]) for n in n_grid]
        
        g1_std_means = [np.mean([x['g1_raw'] / (x['s'] * n**0.5) for x in means_n[n]]) for n in n_grid]
        g2_std_means = [np.mean([x['g2_raw'] / (x['s2'] * n**1.0) for x in means_n[n]]) for n in n_grid]
        
        log_n = np.log(n_grid)
        slope_B_pre, _, r_B_pre, _, _ = linregress(log_n, np.log(B_pre_means))
        slope_B_ceil, _, r_B_ceil, _, _ = linregress(log_n, np.log(B_ceil_means))
        slope_g1, _, r_g1, _, _ = linregress(log_n, np.log(g1_means))
        slope_g2, _, r_g2, _, _ = linregress(log_n, np.log(g2_means))
        
        slope_g1_std, _, _, _, _ = linregress(log_n, np.log(g1_std_means))
        slope_g2_std, _, _, _, _ = linregress(log_n, np.log(g2_std_means))
        
        true_rho_delta = 0.0 if rho == 1.0 else -(1-rho)/2.0
        true_alpha = (4.0 * true_rho_delta**2) / ((1.0 - true_rho_delta**2)**2)
        
        results.append({
            'Process': label,
            'alpha_teo': true_alpha,
            'slope_B_pre': slope_B_pre,
            'R2_B_pre': r_B_pre**2,
            'slope_B_ceil': slope_B_ceil,
            'R2_B_ceil': r_B_ceil**2,
            'slope_g1_std': slope_g1_std,
            'slope_g2_std': slope_g2_std
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
                    vals.append(f"{val:.4f}")
                else:
                    vals.append(str(val))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)
        
    md_table = to_md(df)
    print(md_table)

    # Guardar en markdown
    with open("experiments/results/resultados_auditoria_4_E.md", "w", encoding="utf-8") as f:
        f.write("## Tarea E: Verificación de Tasas de Convergencia (Corrección HAC)\n\n")
        f.write(md_table)

if __name__ == "__main__":
    analyze()
