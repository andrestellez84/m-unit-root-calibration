import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
import numpy as np
from joblib import Parallel, delayed
import pandas as pd
from stationarity_test.empirical_eigenvalues import build_null_cdf_adaptive
from experiments.power_comparison import generate_ar1
from stationarity_test.statistic import compute_statistic

def simulate_one(rng_seed, n):
    rng = np.random.default_rng(rng_seed)
    Y = generate_ar1(n=n, rho=1.0, rng=rng)
    res = compute_statistic(Y, (0.1, 0.1), 0.5, eps=1e-6, andrews_pilot="alpha1")
    g1 = res['g1_std']
    g2 = res['g2_std']
    r_hat = g2**2 / (g1**2 + g2**2) if (g1**2 + g2**2) > 0 else 0.5
    stat = np.sqrt((1.0 - r_hat)**2 * g1**2 + r_hat**2 * g2**2)
    return stat

def run_t8():
    ns = [200, 250]
    N_cals = [10000, 50000]
    N_sim = 5000
    alpha = 0.05
    theta = (0.1, 0.1)
    
    results = []
    
    for n in ns:
        stats = Parallel(n_jobs=-1)(
            delayed(simulate_one)(400000 + i, n) for i in range(N_sim)
        )
        
        for n_cal in N_cals:
            print(f"Building adaptive CDF for n={n}, N_cal={n_cal}...")
            cdf_func = build_null_cdf_adaptive(theta=theta, n=n, N_cal=n_cal, seed=42)
            
            p_vals = [cdf_func(s) for s in stats]
            rej = sum(1 for p in p_vals if p < alpha)
            
            results.append({
                "n": n,
                "N_cal": n_cal,
                "size": rej / N_sim
            })
            
    df = pd.DataFrame(results)
    df.to_csv("experiments/results/adaptive_size_audit5.csv", index=False)

if __name__ == "__main__":
    run_t8()
