"""Quick test: adaptive CDF with sigma-hat estimation on scaled RWs."""
import numpy as np
import sys
sys.path.insert(0, 'src')

from stationarity_test.statistic import compute_statistic
from stationarity_test.empirical_eigenvalues import build_null_cdf_adaptive

theta = (0.1, 0.1)
n = 200
cdf = build_null_cdf_adaptive(theta, n, 10000, 42)

rng = np.random.default_rng(9999)
N_test = 2000

for sigma in [0.001, 0.01, 0.1, 1.0, 10.0]:
    rejections = 0
    for _ in range(N_test):
        rw = np.cumsum(sigma * rng.standard_normal(n))
        rw = np.concatenate([[0], rw])
        
        # Use compute_statistic to get sigma-hat normalized components
        result = compute_statistic(rw, theta, R=0.5, eps=1e-3)
        g1s = result['g1_std']
        g2s = result['g2_std']
        
        # Adaptive R
        d = g1s**2 + g2s**2
        R_hat = g2s**2 / d if d > 1e-12 else 0.5
        
        # Correct formula (matching calibration)
        stat = np.sqrt((1-R_hat)**2 * g1s**2 + R_hat**2 * g2s**2)
        
        p = float(cdf(stat))
        if p < 0.05:
            rejections += 1
    
    rate = rejections / N_test
    print(f"  sigma={sigma:8.4f}  rejection_rate={rate:.4f}  "
          f"{'OK' if 0.025 < rate < 0.075 else 'PROBLEM'}")
