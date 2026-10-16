import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
import pandas as pd
import numpy as np
import scipy.stats as st
from datetime import datetime

from arch.unitroot import DFGLS
from stationarity_test.empirical_eigenvalues import build_null_cdf
from stationarity_test.kl_eigenvalues import compute_eigenvalues
from stationarity_test.statistic import compute_statistic
from experiments.power_comparison import generate_ar1, run_adf, run_pp, run_kpss
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k

def run_dfgls(Y):
    try:
        return DFGLS(Y, trend='c').pvalue
    except:
        return 1.0

def simulate_components(n, theta, N_sim, seed):
    rng = np.random.default_rng(seed)
    g1_std = np.zeros(N_sim)
    g2_std = np.zeros(N_sim)
    bs = []
    
    for i in range(N_sim):
        Y = np.zeros(n + 1)
        Y[1:] = np.cumsum(rng.standard_normal(n))
        res = compute_statistic(Y, theta, 0.5, eps=1e-6, andrews_pilot="alpha1")
        g1_std[i] = res['g1_std']
        g2_std[i] = res['g2_std']
        
        # approximate bandwidth B from sigma_hat and diffs
        # actually, compute_statistic doesn't return B directly.
        # But we can approximate it or re-run the pilot logic.
        diffs = np.diff(Y)
        x_centered = diffs - np.mean(diffs)
        num = np.sum(x_centered[1:] * x_centered[:-1])
        den = np.sum(x_centered[:-1]**2)
        rho_hat = np.clip(num / den if den != 0 else 0, -0.9999, 0.9999)
        alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat**2)**2, 1e-10)
        bw = int(np.ceil(1.1447 * (alpha_hat * n)**(1/3)))
        bw = max(0, min(bw, n - 1))
        bs.append(bw)
        
    return g1_std, g2_std, np.median(bs)

def main():
    ns = [60, 100, 150, 200]
    thetas = [(0.1, 0.1), (0.3, 0.3), (0.5, 0.5)]
    Rs = {"R025": 0.25, "R050": 0.5, "R075": 0.75}
    alpha = 0.05
    N_cal = 50000
    N_sim = 5000
    N_sim_ks = 10000
    
    size_results = []
    ks_results = []
    
    # reference 20000 for g2
    ref_g2 = {}
    for t in thetas:
        print(f"Generating reference for theta={t}...")
        _, g2, _ = simulate_components(20000, t, N_sim_ks, 42)
        ref_g2[t] = g2
    
    for t in thetas:
        # Davies MC for g1
        eigs1, _ = compute_eigenvalues(t[0], component=1, K=200)
        rng_mc = np.random.default_rng(777)
        Z_sq = rng_mc.chisquare(1, size=(500_000, len(eigs1)))
        g1_mc_samples = np.dot(Z_sq, eigs1) # squared!
        g1_mc_sorted = np.sort(g1_mc_samples)
        def cdf_davies(x):
            return np.searchsorted(g1_mc_sorted, x, side='right') / 500_000.0
            
        for n in ns:
            print(f"Running Tarea 3 for n={n}, theta={t}...")
            tau = max(2, int(round(t[0] * n)))
            N_k = n - tau + 1
            
            # --- 1. KS tests ---
            g1, g2, med_b = simulate_components(n, t, N_sim_ks, 999)
            D_g1, _ = st.kstest(g1**2, lambda x: [cdf_davies(val) for val in x])
            D_g2, _ = st.ks_2samp(g2**2, ref_g2[t]**2)
            
            ks_results.append({
                'theta': t[0], 'n': n, 'tau': tau, 'N_k': N_k, 'median_B': med_b,
                'D_g1': D_g1, 'D_g2': D_g2
            })
            
            # --- 2. Size tests ---
            cdf_cache = {}
            for r_name, r_val in Rs.items():
                cdf_cache[r_name] = build_null_cdf(theta=t, R=r_val, n=n, N_cal=N_cal, seed=42)
                
            rej_ours = {k: 0 for k in Rs}
            rej_adf = 0; rej_pp = 0; rej_dfgls = 0; rej_kpss = 0
            
            for i in range(N_sim):
                rng = np.random.default_rng(0 + i)
                Y_rw = generate_ar1(n=n, rho=1.0, rng=rng)
                
                for r_name, r_val in Rs.items():
                    res = compute_statistic(Y_rw, t, r_val, eps=1e-6, andrews_pilot="alpha1")
                    if cdf_cache[r_name](res['statistic']) < alpha:
                        rej_ours[r_name] += 1
                
                # Only need to run baselines once per n (they don't depend on theta)
                if t == (0.1, 0.1):
                    if run_adf(Y_rw) < alpha: rej_adf += 1
                    if run_pp(Y_rw) < alpha: rej_pp += 1
                    if run_dfgls(Y_rw) < alpha: rej_dfgls += 1
                    if run_kpss(Y_rw) < alpha: rej_kpss += 1
                    
            size_results.append({
                'theta': t[0], 'n': n,
                'ours_R025': rej_ours['R025'] / N_sim,
                'ours_R050': rej_ours['R050'] / N_sim,
                'ours_R075': rej_ours['R075'] / N_sim,
                'adf': rej_adf / N_sim if t == (0.1, 0.1) else None,
                'pp': rej_pp / N_sim if t == (0.1, 0.1) else None,
                'dfgls': rej_dfgls / N_sim if t == (0.1, 0.1) else None,
                'kpss_rw': rej_kpss / N_sim if t == (0.1, 0.1) else None,
            })
            
    with open("experiments/results/small_n_size_audit5.json", "w") as f:
        json.dump(size_results, f, indent=2)
        
    df_ks = pd.DataFrame(ks_results)
    df_ks.to_csv("experiments/results/small_n_ks_audit5.csv", index=False)

if __name__ == "__main__":
    main()
