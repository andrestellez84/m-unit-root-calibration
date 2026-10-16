import numpy as np
import pandas as pd
from stationarity_test.kl_eigenvalues import _gauss_legendre_mesh, _cov_s2_s2_vectorized

def test_wick_diagonal_multiple():
    thetas = [0.05, 0.1, 0.3, 0.5]
    n_sub = 64
    
    results = []
    
    for theta in thetas:
        us = [0.2 * theta, 0.5 * theta, 1.0 - 1.5 * theta]
        expected = (theta**2) / 45.0
        
        vals = []
        for u in us:
            if u < 0 or u > 1.0 - theta:
                continue
            s, w = _gauss_legendre_mesh(u, u + theta, n_sub)
            w_normed = w / theta
            var_s2 = _cov_s2_s2_vectorized(s, w_normed, s, w_normed)
            vals.append(var_s2)
            
            results.append({
                'theta': theta,
                'u': u,
                'expected': expected,
                'observed': var_s2,
                'err_level': abs(var_s2 - expected) / expected
            })
            
        vals = np.array(vals)
        variation = np.max(vals) - np.min(vals)
        variation_rel = variation / expected
        
        print(f"theta={theta}: Variation={variation_rel:.2%}")
        
    df = pd.DataFrame(results)
    df.to_csv("experiments/results/audit4b_tarea7.csv", index=False)
    
if __name__ == "__main__":
    test_wick_diagonal_multiple()
