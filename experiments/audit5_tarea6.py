import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
import numpy as np
from joblib import Parallel, delayed
from stationarity_test.empirical_eigenvalues import build_null_cdf_adaptive
from experiments.power_comparison import generate_ar1, generate_ar1_break_variance, generate_rw_break_variance
from stationarity_test.statistic import compute_statistic

def simulate_adaptive_both(rng_seed, n, pilot, dgp, rho, r_val, theta, m1, m2):
    rng = np.random.default_rng(rng_seed)
    if dgp == "H0":
        Y = generate_ar1(n=n, rho=1.0, rng=rng)
    elif dgp == "DGP1":
        Y = generate_ar1(n=n, rho=rho, rng=rng)
    elif dgp == "DGP3":
        Y = generate_rw_break_variance(n=n, ratio=r_val, rng=rng)
    elif dgp == "DGP4":
        Y = generate_ar1_break_variance(n=n, rho=0.5, ratio=r_val, rng=rng)
        
    res = compute_statistic(Y, theta, 0.5, eps=1e-6, andrews_pilot=pilot)
    g1 = res['g1_std']
    g2 = res['g2_std']
    
    # R_hat
    r_hat = g2**2 / (g1**2 + g2**2) if (g1**2 + g2**2) > 0 else 0.5
    stat_hat = np.sqrt((1.0 - r_hat)**2 * g1**2 + r_hat**2 * g2**2)
    
    # R_bal
    b1 = g1 / m1
    b2 = g2 / m2
    r_bal = b2**2 / (b1**2 + b2**2) if (b1**2 + b2**2) > 0 else 0.5
    stat_bal = np.sqrt((1.0 - r_bal)**2 * g1**2 + r_bal**2 * g2**2)
    
    return stat_hat, stat_bal

def build_adaptive_cdfs_for_pilot(theta, n, pilot, m1, m2, N_cal=50000, seed=42):
    print(f"Building adaptive CDFs for n={n}, pilot={pilot}, N_cal={N_cal}...")
    stats = Parallel(n_jobs=-1)(
        delayed(simulate_adaptive_both)(seed + i, n, pilot, "H0", 1.0, None, theta, m1, m2)
        for i in range(N_cal)
    )
    
    stats_hat = np.sort([s[0] for s in stats])
    stats_bal = np.sort([s[1] for s in stats])
    
    def cdf_hat(v): return np.searchsorted(stats_hat, v, side='right') / N_cal
    def cdf_bal(v): return np.searchsorted(stats_bal, v, side='right') / N_cal
    
    return cdf_hat, cdf_bal

def run_t6():
    theta = (0.1, 0.1)
    N_sim = 5000
    alpha = 0.05
    
    with open("experiments/results/rebalance_constants_audit5.json", "r") as f:
        m_cache = json.load(f)
        
    results = {"alpha1": {}, "alpha2": {}}
    
    scenarios = [
        {"name": "H0_n200", "dgp": "H0", "n": 200, "rho": 1.0, "r": None, "seed_base": 100000},
        {"name": "H0_n500", "dgp": "H0", "n": 500, "rho": 1.0, "r": None, "seed_base": 100000},
        {"name": "H0_n1000", "dgp": "H0", "n": 1000, "rho": 1.0, "r": None, "seed_base": 100000},
        {"name": "DGP1_n200", "dgp": "DGP1", "n": 200, "rho": 0.95, "r": None, "seed_base": 100000},
        {"name": "DGP1_n500", "dgp": "DGP1", "n": 500, "rho": 0.97, "r": None, "seed_base": 100000},
        {"name": "DGP1_n1000", "dgp": "DGP1", "n": 1000, "rho": 0.99, "r": None, "seed_base": 100000},
        {"name": "DGP3_n1000", "dgp": "DGP3", "n": 1000, "rho": 1.0, "r": 4.0, "seed_base": 100000},
        {"name": "DGP4_n500", "dgp": "DGP4", "n": 500, "rho": 0.5, "r": 3.0, "seed_base": 100000},
    ]
    
    cdfs_50k_a1 = {}
    cdfs_50k_a2 = {}
    for n in [200, 500, 1000]:
        m1, m2 = m_cache["alpha1"][str(n)]
        cdfs_50k_a1[n] = build_adaptive_cdfs_for_pilot(theta, n, "alpha1", m1, m2, 50000)
        
        m1, m2 = m_cache["alpha2"][str(n)]
        cdfs_50k_a2[n] = build_adaptive_cdfs_for_pilot(theta, n, "alpha2", m1, m2, 50000)
        
    m1_a1, m2_a1 = m_cache["alpha1"]["200"]
    cdf_10k_a1_n200 = build_adaptive_cdfs_for_pilot(theta, 200, "alpha1", m1_a1, m2_a1, 10000)
    
    m1_a2, m2_a2 = m_cache["alpha2"]["200"]
    cdf_10k_a2_n200 = build_adaptive_cdfs_for_pilot(theta, 200, "alpha2", m1_a2, m2_a2, 10000)
    
    for pilot, cdfs, cdf_10k in [("alpha1", cdfs_50k_a1, cdf_10k_a1_n200), ("alpha2", cdfs_50k_a2, cdf_10k_a2_n200)]:
        for sc in scenarios:
            n = sc["n"]
            cdf_hat, cdf_bal = cdfs[n]
            m1, m2 = m_cache[pilot][str(n)]
            
            stats = Parallel(n_jobs=-1)(
                delayed(simulate_adaptive_both)(sc["seed_base"] + i, n, pilot, sc["dgp"], sc["rho"], sc["r"], theta, m1, m2)
                for i in range(N_sim)
            )
            
            rej_hat = sum(1 for s in stats if cdf_hat(s[0]) < alpha)
            rej_bal = sum(1 for s in stats if cdf_bal(s[1]) < alpha)
            
            results[pilot][sc["name"]] = {"R_hat": rej_hat / N_sim, "R_bal": rej_bal / N_sim}
            
            if sc["name"] == "H0_n200":
                cdf_10k_hat, cdf_10k_bal = cdf_10k
                rej_10k_hat = sum(1 for s in stats if cdf_10k_hat(s[0]) < alpha)
                rej_10k_bal = sum(1 for s in stats if cdf_10k_bal(s[1]) < alpha)
                results[pilot]["H0_n200_cal10k"] = {"R_hat": rej_10k_hat / N_sim, "R_bal": rej_10k_bal / N_sim}
                
    with open("experiments/results/adaptive_size_power_audit5.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_t6()
