import numpy as np
import scipy.stats as st
from stationarity_test.empirical_eigenvalues import _simulate_null_statistics, build_null_cdf
from stationarity_test.kl_eigenvalues import compute_eigenvalues
from stationarity_test.null_quantiles import null_cdf

def main():
    N = 20000
    theta = (0.1, 0.1)
    
    n_small = 1000
    n_inf = 20000
    R = 0.5
    
    # Simulate n_inf distribution (reference)
    print("Simulating n=20000 (reference)...")
    from stationarity_test.empirical_eigenvalues import _simulate_null_statistics
    stats_inf = _simulate_null_statistics(theta, R, n_inf, N_cal=N, seed=42)
    
    rng1 = np.random.default_rng(42)
    from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
    
    def simulate_components(n, N_sim, seed):
        rng = np.random.default_rng(seed)
        g1 = np.zeros(N_sim)
        g2 = np.zeros(N_sim)
        scale1 = 1.0 * n**0.5
        scale2 = 1.0 * n**1.0
        tau1 = max(2, int(round(theta[0] * n)))
        tau2 = max(2, int(round(theta[1] * n)))
        for i in range(N_sim):
            Y = np.zeros(n+1)
            Y[1:] = np.cumsum(rng.standard_normal(n))
            m = rolling_mean(Y, tau1)
            v = rolling_var(Y, tau2)
            g1[i] = np.sqrt(max(sample_variance_over_k(m), 0.0)) / scale1
            g2[i] = np.sqrt(max(sample_variance_over_k(v), 0.0)) / scale2
        return g1, g2
    
    print(f"Simulating n={n_inf} reference...")
    g1_ref, g2_ref = simulate_components(n_inf, N, 42)
    stat_ref = np.sqrt(0.25 * g1_ref**2 + 0.25 * g2_ref**2)
    
    print(f"Simulating n={n_small} test...")
    g1_test, g2_test = simulate_components(n_small, N, 999)
    stat_test = np.sqrt(0.25 * g1_test**2 + 0.25 * g2_test**2)
    
    # KS test for g1 (one-sample against analytical MC CDF)
    print("Computing CDF for g1 using MC on eigenvalues (N=1_000_000)...")
    from stationarity_test.kl_eigenvalues import compute_eigenvalues
    eigs1, _ = compute_eigenvalues(theta[0], component=1, K=200)
    
    rng_mc = np.random.default_rng(777)
    Z_sq = rng_mc.chisquare(1, size=(1_000_000, len(eigs1)))
    g1_mc_samples = np.sqrt(np.dot(Z_sq, eigs1))
    
    # We can use np.searchsorted to evaluate the empirical CDF very fast
    g1_mc_sorted = np.sort(g1_mc_samples)
    def cdf_davies(x):
        return np.searchsorted(g1_mc_sorted, x, side='right') / 1_000_000.0
    
    # KS test for g1
    D_g1, p_g1 = st.kstest(g1_test, lambda x: [cdf_davies(val) for val in x])
    thresh_1 = 1.358 / np.sqrt(N)
    
    # KS test for g2 (two-sample)
    D_g2, p_g2 = st.ks_2samp(g2_test, g2_ref)
    thresh_2 = 1.358 * np.sqrt(2 / N)
    
    # KS test for combined (two-sample)
    D_comb, p_comb = st.ks_2samp(stat_test, stat_ref)
    
    lines = [
        "## Tarea H: KS por canal con umbrales estrictos",
        "",
        f"Simulación de $N={N}$ caminos. Contraste de $n={n_small}$ vs $n={n_inf}$ (discreto).",
        "",
        "| Componente | Tipo KS | Estadístico D | Valor p | Umbral 5% | ¿Rechaza $H_0$? |",
        "|---|---|---|---|---|---|",
        f"| $g_1$ | 1-sample (Davies) | {D_g1:.5f} | {p_g1:.4e} | {thresh_1:.5f} | {'SÍ' if D_g1 > thresh_1 else 'No'} |",
        f"| $g_2$ | 2-sample ($n={n_inf}$) | {D_g2:.5f} | {p_g2:.4e} | {thresh_2:.5f} | {'SÍ' if D_g2 > thresh_2 else 'No'} |",
        f"| Combinada | 2-sample ($n={n_inf}$) | {D_comb:.5f} | {p_comb:.4e} | {thresh_2:.5f} | {'SÍ' if D_comb > thresh_2 else 'No'} |",
        ""
    ]
    
    print("\n".join(lines))
    
    with open("experiments/results/resultados_auditoria_4_H.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    main()
