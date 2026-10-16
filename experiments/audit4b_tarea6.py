import numpy as np
import scipy.stats as st
import pandas as pd
from stationarity_test.empirical_eigenvalues import _simulate_null_statistics
from stationarity_test.kl_eigenvalues import compute_eigenvalues
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k

def simulate_components(n, theta, N_sim, seed):
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

def run_tarea6():
    thetas = [0.1, 0.3, 0.5]
    ns = [100, 200, 500, 1000, 2000, 5000]
    N = 10000
    n_inf = 20000
    
    results = []
    
    for theta_val in thetas:
        theta = (theta_val, theta_val)
        
        # Reference (n=20000)
        print(f"Generating reference for theta={theta_val}...")
        g1_ref, g2_ref = simulate_components(n_inf, theta, N, 42)
        stat_ref = np.sqrt(0.25 * g1_ref**2 + 0.25 * g2_ref**2)
        
        # Davies MC
        eigs1, _ = compute_eigenvalues(theta_val, component=1, K=200)
        rng_mc = np.random.default_rng(777)
        Z_sq = rng_mc.chisquare(1, size=(500_000, len(eigs1)))
        g1_mc_samples = np.dot(Z_sq, eigs1) # squared!
        g1_mc_sorted = np.sort(g1_mc_samples)
        
        def cdf_davies(x):
            return np.searchsorted(g1_mc_sorted, x, side='right') / 500_000.0
            
        for n in ns:
            print(f"Testing theta={theta_val}, n={n}...")
            g1_test, g2_test = simulate_components(n, theta, N, 999+n)
            stat_test = np.sqrt(0.25 * g1_test**2 + 0.25 * g2_test**2)
            
            # g1 squared against Davies
            D_g1, p_g1 = st.kstest(g1_test**2, lambda x: [cdf_davies(val) for val in x])
            thresh_1 = 1.358 / np.sqrt(N)
            
            # g2 squared against g2_ref squared
            # Wait, ks_2samp is invariant to monotonic transformations, so g2 or g2**2 gives same D!
            D_g2, p_g2 = st.ks_2samp(g2_test**2, g2_ref**2)
            thresh_2 = 1.358 * np.sqrt(2.0 / N)
            
            # combined
            D_comb, p_comb = st.ks_2samp(stat_test, stat_ref)
            
            results.append({
                'theta': theta_val,
                'n': n,
                'N': N,
                'D_g1': D_g1,
                'rej_g1': D_g1 > thresh_1,
                'D_g2': D_g2,
                'rej_g2': D_g2 > thresh_2,
                'D_comb': D_comb,
                'rej_comb': D_comb > thresh_2,
                'thresh_1': thresh_1,
                'thresh_2': thresh_2
            })
            
    df = pd.DataFrame(results)
    df.to_csv("experiments/results/audit4b_tarea6.csv", index=False)

if __name__ == "__main__":
    run_tarea6()
