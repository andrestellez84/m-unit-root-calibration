import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import time
import numpy as np
from stationarity_test.statistic import compute_statistic
from stationarity_test.empirical_eigenvalues import build_null_cdf

def run_t10():
    print("Midiendo costos...")
    
    # 1. compute_statistic
    n = 1000
    theta = (0.1, 0.1)
    rng = np.random.default_rng(42)
    Ys = [rng.standard_normal(n+1) for _ in range(1000)]
    for Y in Ys: Y[1:] = np.cumsum(Y[1:])
    
    t0 = time.perf_counter()
    for Y in Ys:
        compute_statistic(Y, theta, 0.5, eps=1e-6, andrews_pilot="alpha1")
    t1 = time.perf_counter()
    ms_per_series_a1 = (t1 - t0) * 1000.0 / 1000
    
    t0 = time.perf_counter()
    for Y in Ys:
        compute_statistic(Y, theta, 0.5, eps=1e-6, andrews_pilot="alpha2")
    t1 = time.perf_counter()
    ms_per_series_a2 = (t1 - t0) * 1000.0 / 1000
    
    print(f"Costo por serie (n=1000): alpha1 = {ms_per_series_a1:.3f} ms, alpha2 = {ms_per_series_a2:.3f} ms")
    
    # 2. build_null_cdf
    t0 = time.perf_counter()
    build_null_cdf(theta, 0.5, n, N_cal=10000, seed=42)
    t1 = time.perf_counter()
    s_per_cdf_10k = t1 - t0
    
    t0 = time.perf_counter()
    build_null_cdf(theta, 0.5, n, N_cal=50000, seed=42)
    t1 = time.perf_counter()
    s_per_cdf_50k = t1 - t0
    
    print(f"Costo build_null_cdf: 10k = {s_per_cdf_10k:.3f} s, 50k = {s_per_cdf_50k:.3f} s")
    
if __name__ == "__main__":
    run_t10()
