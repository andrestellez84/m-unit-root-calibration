import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
import numpy as np
import scipy.stats as st
from datetime import datetime

from arch.unitroot import DFGLS
from stationarity_test.empirical_eigenvalues import build_null_cdf
from stationarity_test.statistic import compute_statistic
from experiments.power_comparison import generate_ar1, run_adf, run_pp, run_kpss

def run_dfgls(Y):
    try:
        return DFGLS(Y, trend='c').pvalue
    except:
        return 1.0

def run_size_verification(pilot="alpha1"):
    ns = [200, 500, 1000]
    N_cal = 50000
    N_sim = 5000
    alpha = 0.05
    theta = (0.1, 0.1)
    Rs = {"R025": 0.25, "R050": 0.5, "R075": 0.75}
    
    lb = st.binom.ppf(0.025, N_sim, alpha) / N_sim
    ub = st.binom.ppf(0.975, N_sim, alpha) / N_sim
    
    results = {}
    
    for n in ns:
        print(f"n={n}, pilot={pilot}")
        # Pre-calibrate CDFs for all Rs at this n
        cdf_cache = {}
        for r_name, r_val in Rs.items():
            print(f"  Calibrating R={r_val}...")
            cdf_cache[r_name] = build_null_cdf(
                theta=theta, R=r_val, n=n, N_cal=N_cal, seed=42
            )
            
        rej_ours = {k: 0 for k in Rs}
        rej_adf = 0
        rej_pp = 0
        rej_dfgls = 0
        rej_kpss = 0
        rej_kpss_wn = 0
        
        for i in range(N_sim):
            rng = np.random.default_rng(0 + i) # seed_base = 0
            Y_rw = generate_ar1(n=n, rho=1.0, rng=rng)
            
            # Ours
            for r_name, r_val in Rs.items():
                res = compute_statistic(Y_rw, theta, r_val, eps=1e-6, andrews_pilot=pilot)
                stat = res['statistic']
                p_val = cdf_cache[r_name](stat)
                if p_val < alpha:
                    rej_ours[r_name] += 1
                    
            if run_adf(Y_rw) < alpha: rej_adf += 1
            if run_pp(Y_rw) < alpha: rej_pp += 1
            if run_dfgls(Y_rw) < alpha: rej_dfgls += 1
            if run_kpss(Y_rw) < alpha: rej_kpss += 1
            
            rng_wn = np.random.default_rng(50000 + i)
            Y_wn = rng_wn.standard_normal(n + 1)
            if run_kpss(Y_wn) < alpha: rej_kpss_wn += 1
            
        results[str(n)] = {
            'ours_R025': rej_ours["R025"] / N_sim,
            'ours_R050': rej_ours["R050"] / N_sim,
            'ours_R075': rej_ours["R075"] / N_sim,
            'adf': rej_adf / N_sim,
            'pp': rej_pp / N_sim,
            'dfgls': rej_dfgls / N_sim,
            'kpss_rw': rej_kpss / N_sim,
            'kpss_wn': rej_kpss_wn / N_sim
        }
        
    return results

def main():
    res_a1 = run_size_verification(pilot="alpha1")
    res_a2 = run_size_verification(pilot="alpha2")
    
    with open("experiments/results/size_audit5.json", "w") as f:
        json.dump({"alpha1": res_a1, "alpha2": res_a2}, f, indent=2)

if __name__ == "__main__":
    main()
