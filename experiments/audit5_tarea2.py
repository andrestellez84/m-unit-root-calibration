import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
import numpy as np
import scipy.stats as st
from arch.unitroot import DFGLS
from experiments.power_comparison import run_adf, run_pp, run_kpss
from stationarity_test.empirical_eigenvalues import build_null_cdf
from stationarity_test.statistic import compute_statistic

def run_dfgls(Y):
    try:
        return DFGLS(Y, trend='c').pvalue
    except:
        return 1.0

def run_heavy_tails(pilot="alpha1"):
    ns = [200, 500, 1000]
    dofs = [5, 3]
    N_cal = 50000
    N_sim = 5000
    alpha = 0.05
    theta = (0.1, 0.1)
    Rs = {"R025": 0.25, "R050": 0.5, "R075": 0.75}
    
    results = {str(d): {} for d in dofs}
    
    for n in ns:
        print(f"n={n}, pilot={pilot}")
        cdf_cache = {}
        for r_name, r_val in Rs.items():
            cdf_cache[r_name] = build_null_cdf(theta=theta, R=r_val, n=n, N_cal=N_cal, seed=42)
            
        for dof in dofs:
            rej_ours = {k: 0 for k in Rs}
            rej_adf = 0
            rej_pp = 0
            rej_dfgls = 0
            rej_kpss = 0
            
            for i in range(N_sim):
                # Same seed logic as old script
                seed = 200000 + n * 100 + dof * 10 + i
                rng = np.random.default_rng(seed)
                eps = rng.standard_t(df=dof, size=n)
                # scale to variance 1 for dof>2
                eps = eps / np.sqrt(dof / (dof - 2.0))
                
                Y = np.zeros(n + 1)
                Y[1:] = np.cumsum(eps)
                
                for r_name, r_val in Rs.items():
                    res = compute_statistic(Y, theta, r_val, eps=1e-6, andrews_pilot=pilot)
                    p_val = cdf_cache[r_name](res['statistic'])
                    if p_val < alpha:
                        rej_ours[r_name] += 1
                        
                if run_adf(Y) < alpha: rej_adf += 1
                if run_pp(Y) < alpha: rej_pp += 1
                if run_dfgls(Y) < alpha: rej_dfgls += 1
                if run_kpss(Y) < alpha: rej_kpss += 1
                
            results[str(dof)][str(n)] = {
                'ours_R025': rej_ours["R025"] / N_sim,
                'ours_R050': rej_ours["R050"] / N_sim,
                'ours_R075': rej_ours["R075"] / N_sim,
                'adf': rej_adf / N_sim,
                'pp': rej_pp / N_sim,
                'dfgls': rej_dfgls / N_sim,
                'kpss_rw': rej_kpss / N_sim
            }
            
    return results

def main():
    res_a1 = run_heavy_tails(pilot="alpha1")
    res_a2 = run_heavy_tails(pilot="alpha2")
    with open("experiments/results/size_robustness_heavy_tails_audit5.json", "w") as f:
        json.dump({"alpha1": res_a1, "alpha2": res_a2}, f, indent=2)

if __name__ == "__main__":
    main()
