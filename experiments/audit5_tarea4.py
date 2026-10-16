import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
from experiments.power_comparison import run_dgp3, run_dgp4, build_null_cdf, THETA_FIXED

def run_dgp34_both_pilots():
    # We need to run them for both pilots.
    # The tests need cdf_cache. DGP3 and DGP4 use n=200, 500, 1000 and 3 R configs.
    ns = [200, 500, 1000]
    Rs = {"R025": 0.25, "R050": 0.5, "R075": 0.75}
    
    # Actually, run_dgp3 and run_dgp4 in power_comparison use THETA_FIXED=(0.1,0.1), N_GRID, R_CONFIGS
    # I will just call run_dgp3() and run_dgp4() with precalibrated cdf_cache
    cdf_cache = {}
    for n in ns:
        for r_name, r_val in Rs.items():
            # DGP3/4 use N_cal=50000 by default in the code?
            # Actually, `precalibrate_cdfs` uses N_cal=50000.
            cdf_cache[(r_name, n)] = build_null_cdf(theta=THETA_FIXED, R=r_val, n=n, N_cal=50000, seed=42)
            
    print("Running alpha1...")
    dgp3_a1 = run_dgp3(cdf_cache, pilot="alpha1")
    dgp4_a1 = run_dgp4(cdf_cache, pilot="alpha1")
    
    print("Running alpha2...")
    dgp3_a2 = run_dgp3(cdf_cache, pilot="alpha2")
    dgp4_a2 = run_dgp4(cdf_cache, pilot="alpha2")
    
    with open("experiments/results/power_comparison_dgp34_alpha1_audit5.json", "w") as f:
        json.dump({"dgp3": dgp3_a1, "dgp4": dgp4_a1}, f, indent=2)
        
    with open("experiments/results/power_comparison_dgp34_alpha2_audit5.json", "w") as f:
        json.dump({"dgp3": dgp3_a2, "dgp4": dgp4_a2}, f, indent=2)

if __name__ == "__main__":
    run_dgp34_both_pilots()
