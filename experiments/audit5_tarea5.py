import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
import numpy as np
from stationarity_test.statistic import compute_statistic
from stationarity_test.optimal_weight import compute_optimal_R
from experiments.power_comparison import generate_ar1, generate_ar1_break_variance, generate_rw_break_variance

def run_t5():
    # We want to collect R_hat distribution for alpha1 and alpha2
    N_sim = 5000
    theta = (0.1, 0.1)
    
    from joblib import Parallel, delayed

    def compute_one(rng_seed, n, pilot):
        rng = np.random.default_rng(rng_seed)
        Y = generate_ar1(n=n, rho=1.0, rng=rng)
        res = compute_statistic(Y, theta, 0.5, eps=1e-6, andrews_pilot=pilot)
        return res['g1_std'], res['g2_std']

    m_cache_alpha1 = {}
    m_cache_alpha2 = {}
    for n in [200, 500, 1000]:
        for pilot, m_c in [("alpha1", m_cache_alpha1), ("alpha2", m_cache_alpha2)]:
            print(f"Computing m1, m2 for n={n}, pilot={pilot}...")
            res_list = Parallel(n_jobs=-1)(
                delayed(compute_one)(42 + i, n, pilot) for i in range(50000)
            )
            g1_sum = sum(r[0] for r in res_list)
            g2_sum = sum(r[1] for r in res_list)
            m_c[n] = (g1_sum / 50000, g2_sum / 50000)
            
    with open("experiments/results/rebalance_constants_audit5.json", "w") as f:
        json.dump({"alpha1": m_cache_alpha1, "alpha2": m_cache_alpha2}, f, indent=2)

    scenarios = [
        {"name": "H0_n200", "dgp": "H0", "n": 200, "seed_base": 70000},
        {"name": "H0_n500", "dgp": "H0", "n": 500, "seed_base": 70000},
        {"name": "H0_n1000", "dgp": "H0", "n": 1000, "seed_base": 70000},
        {"name": "DGP3_n1000_r4", "dgp": "DGP3", "n": 1000, "r": 4.0, "seed_base": 80000},
        {"name": "DGP4_n500_r3", "dgp": "DGP4", "n": 500, "r": 3.0, "seed_base": 90000},
    ]

    results = {"alpha1": {}, "alpha2": {}}
    
    for pilot in ["alpha1", "alpha2"]:
        for sc in scenarios:
            n = sc["n"]
            m_c = m_cache_alpha1 if pilot == "alpha1" else m_cache_alpha2
            m1, m2 = m_c[n]
            
            r_hats = []
            r_bals = []
            
            for i in range(N_sim):
                rng = np.random.default_rng(sc["seed_base"] + i)
                if sc["dgp"] == "H0":
                    Y = generate_ar1(n=n, rho=1.0, rng=rng)
                elif sc["dgp"] == "DGP3":
                    Y = generate_rw_break_variance(n=n, ratio=sc["r"], rng=rng)
                elif sc["dgp"] == "DGP4":
                    Y = generate_ar1_break_variance(n=n, rho=0.5, ratio=sc["r"], rng=rng)
                    
                res = compute_statistic(Y, theta, 0.5, eps=1e-6, andrews_pilot=pilot)
                g1 = res['g1_std']
                g2 = res['g2_std']
                
                # compute R_hat
                # R_hat = g2^2 / (g1^2 + g2^2)
                r_hat = g2**2 / (g1**2 + g2**2) if (g1**2 + g2**2) > 0 else 0.5
                r_hats.append(r_hat)
                
                # R_bal
                b1 = g1 / m1
                b2 = g2 / m2
                r_bal = b2**2 / (b1**2 + b2**2) if (b1**2 + b2**2) > 0 else 0.5
                r_bals.append(r_bal)
                
            r_hats = np.array(r_hats)
            r_bals = np.array(r_bals)
            
            results[pilot][sc["name"]] = {
                "r_hat": {
                    "mean": float(np.mean(r_hats)),
                    "median": float(np.median(r_hats)),
                    "q05": float(np.percentile(r_hats, 5)),
                    "q95": float(np.percentile(r_hats, 95))
                },
                "r_bal": {
                    "mean": float(np.mean(r_bals)),
                    "median": float(np.median(r_bals)),
                    "q05": float(np.percentile(r_bals, 5)),
                    "q95": float(np.percentile(r_bals, 95))
                }
            }
            
    with open("experiments/results/rhat_distribution_audit5.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_t5()
