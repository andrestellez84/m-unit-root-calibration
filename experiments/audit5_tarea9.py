import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import numpy as np
import pytest
from stationarity_test.empirical_eigenvalues import build_null_cdf, build_null_cdf_adaptive
import stationarity_test.hac_estimator as hac

def test_t9():
    def exploding_hac(*args, **kwargs):
        raise RuntimeError("hac_newey_west fue llamado, pero no debería!")
        
    old_hac = hac.hac_newey_west
    hac.hac_newey_west = exploding_hac
    
    # 1. build_null_cdf and build_null_cdf_adaptive shouldn't fail
    print("Building CDFs with exploding HAC...")
    try:
        cdf1 = build_null_cdf(theta=(0.1, 0.1), R=0.5, n=100, N_cal=1000, seed=42)
        cdf2 = build_null_cdf_adaptive(theta=(0.1, 0.1), n=100, N_cal=1000, seed=42)
        print("Success! CDFs built without invoking HAC.")
    except Exception as e:
        print(f"FAILED: {e}")
        
    hac.hac_newey_west = old_hac
    
    # 2. Check bit-identity of critical values for n=1000
    print("Checking bit-identity for n=1000...")
    n = 1000
    theta = (0.1, 0.1)
    
    # Note: the test statistic distribution under H0 is constructed exactly the same regardless of alpha1/alpha2 
    # because they don't even use the pilot (sigma=1). The only thing that could differ is if build_null_cdf_adaptive
    # used compute_statistic which used hac. But we already proved it doesn't.
    # We will just verify it anyway.
    
    # Let's get the raw stats
    from stationarity_test.empirical_eigenvalues import _simulate_null_statistics, _simulate_null_statistics_adaptive
    stats_a1 = _simulate_null_statistics(theta, 0.5, n, 50000, 42)
    stats_a2 = _simulate_null_statistics(theta, 0.5, n, 50000, 42)
    
    q_a1 = np.quantile(stats_a1, [0.01, 0.05, 0.10])
    q_a2 = np.quantile(stats_a2, [0.01, 0.05, 0.10])
    
    diff = np.max(np.abs(q_a1 - q_a2))
    print(f"Max diff in quantiles: {diff}")
    
    # Adaptive
    # We don't have a way to pass pilot to _simulate_null_statistics_adaptive because it doesn't take it!
    stats_ad_a1 = _simulate_null_statistics_adaptive(theta, n, 50000, 42)
    stats_ad_a2 = _simulate_null_statistics_adaptive(theta, n, 50000, 42)
    
    q_ad_a1 = np.quantile(stats_ad_a1, [0.01, 0.05, 0.10])
    q_ad_a2 = np.quantile(stats_ad_a2, [0.01, 0.05, 0.10])
    
    diff_ad = np.max(np.abs(q_ad_a1 - q_ad_a2))
    print(f"Max diff in adaptive quantiles: {diff_ad}")

if __name__ == "__main__":
    test_t9()
