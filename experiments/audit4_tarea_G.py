import numpy as np
import pandas as pd
import scipy.stats as st
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k

def generate_rw(n, rng):
    eps = rng.standard_normal(n)
    Y = np.zeros(n + 1)
    Y[1:] = np.cumsum(eps)
    return Y

def main():
    n = 2000
    N_sim = 10000
    B_boot = 1000
    theta = 0.1
    
    tau1 = max(2, int(round(theta * n)))
    tau2 = max(2, int(round(theta * n)))
    
    rng = np.random.default_rng(42)
    
    print(f"Simulating {N_sim} RW paths of length {n}...")
    g1_sq = np.zeros(N_sim)
    g2_sq = np.zeros(N_sim)
    
    for i in range(N_sim):
        Y = generate_rw(n, rng)
        means = rolling_mean(Y, tau1)
        variances = rolling_var(Y, tau2)
        
        g1_sq[i] = max(sample_variance_over_k(means), 0.0)
        g2_sq[i] = max(sample_variance_over_k(variances), 0.0)
        
    r, _ = st.pearsonr(g1_sq, g2_sq)
    print(f"Sample Pearson correlation: {r:.4f}")
    
    # Bootstrap CI
    print(f"Bootstrapping B={B_boot}...")
    boot_corrs = np.zeros(B_boot)
    for b in range(B_boot):
        idx = rng.choice(N_sim, size=N_sim, replace=True)
        boot_corrs[b], _ = st.pearsonr(g1_sq[idx], g2_sq[idx])
        
    ci_boot = np.percentile(boot_corrs, [2.5, 97.5])
    
    # Fisher CI
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(N_sim - 3)
    z_lo = z - 1.96 * se
    z_hi = z + 1.96 * se
    ci_fisher = (np.tanh(z_lo), np.tanh(z_hi))
    
    print(f"Bootstrap CI: [{ci_boot[0]:.4f}, {ci_boot[1]:.4f}]")
    print(f"Fisher CI:    [{ci_fisher[0]:.4f}, {ci_fisher[1]:.4f}]")
    
    # Markdown
    lines = [
        "## Tarea G: Bootstrap Correlación de Componentes",
        "",
        f"Simulación de $N={N_sim}$ caminos bajo $H_0$ con $n={n}$.",
        f"- **Correlación muestral $corr(g_1^2, g_2^2)$**: {r:.5f}",
        f"- **Intervalo Bootstrap (B=1000)**: [{ci_boot[0]:.5f}, {ci_boot[1]:.5f}]",
        f"- **Intervalo de Fisher**: [{ci_fisher[0]:.5f}, {ci_fisher[1]:.5f}]",
        ""
    ]
    
    with open("experiments/results/resultados_auditoria_4_G.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    main()
