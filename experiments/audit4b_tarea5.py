import numpy as np
import scipy.stats as st
import pandas as pd
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k

def generate_rw(n, rng):
    eps = rng.standard_normal(n)
    Y = np.zeros(n + 1)
    Y[1:] = np.cumsum(eps)
    return Y

def run_tarea5():
    N_sim = 10000
    B_boot = 2000
    thetas = [0.1, 0.3, 0.5]
    ns = [200, 1000, 5000, 20000]
    
    rng = np.random.default_rng(42)
    results = []
    
    for theta in thetas:
        for n in ns:
            print(f"Tarea G: theta={theta}, n={n}...")
            tau = max(2, int(round(theta * n)))
            
            g1_sq = np.zeros(N_sim)
            g2_sq = np.zeros(N_sim)
            
            for i in range(N_sim):
                Y = generate_rw(n, rng)
                m = rolling_mean(Y, tau)
                v = rolling_var(Y, tau)
                g1_sq[i] = max(sample_variance_over_k(m), 0.0)
                g2_sq[i] = max(sample_variance_over_k(v), 0.0)
                
            r, _ = st.pearsonr(g1_sq, g2_sq)
            
            # Bootstrap CI
            boot_corrs = np.zeros(B_boot)
            for b in range(B_boot):
                idx = rng.choice(N_sim, size=N_sim, replace=True)
                boot_corrs[b], _ = st.pearsonr(g1_sq[idx], g2_sq[idx])
            ci_boot = np.percentile(boot_corrs, [2.5, 97.5])
            w_boot = (ci_boot[1] - ci_boot[0]) / 2.0
            
            # Fisher CI
            z = np.arctanh(r)
            se = 1.0 / np.sqrt(N_sim - 3)
            z_lo = z - 1.96 * se
            z_hi = z + 1.96 * se
            ci_fisher = (np.tanh(z_lo), np.tanh(z_hi))
            w_fisher = (ci_fisher[1] - ci_fisher[0]) / 2.0
            
            ratio_w = w_boot / w_fisher if w_fisher > 0 else 0
            
            results.append({
                'theta': theta,
                'n': n,
                'r': r,
                'CI Boot': f"[{ci_boot[0]:.4f}, {ci_boot[1]:.4f}]",
                'CI Fisher': f"[{ci_fisher[0]:.4f}, {ci_fisher[1]:.4f}]",
                'Ratio Anchos': ratio_w
            })
            
    df = pd.DataFrame(results)
    df.to_csv("experiments/results/audit4b_tarea5.csv", index=False)

if __name__ == "__main__":
    run_tarea5()
