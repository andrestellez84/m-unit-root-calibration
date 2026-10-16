import numpy as np
import pandas as pd
from stationarity_test.kl_eigenvalues import _gauss_legendre_mesh, _cov_s2_s2_vectorized, _covariance_kernel_component2

from joblib import Parallel, delayed

def _compute_row(i, M, u_grid, theta, n_sub):
    u_i = u_grid[i]
    s1, w1 = _gauss_legendre_mesh(u_i, u_i + theta, n_sub)
    w1_normed = w1 / theta
    row_vals = np.zeros(M - i)
    for idx, j in enumerate(range(i, M)):
        u_j = u_grid[j]
        s2, w2 = _gauss_legendre_mesh(u_j, u_j + theta, n_sub)
        w2_normed = w2 / theta
        row_vals[idx] = _cov_s2_s2_vectorized(s1, w1_normed, s2, w2_normed)
    return i, row_vals

def compute_traces(theta, M, n_sub):
    u_grid = np.linspace(0.0, 1.0 - theta, M)
    K_uncentered = np.empty((M, M), dtype=np.float64)
    
    results = Parallel(n_jobs=-1)(
        delayed(_compute_row)(i, M, u_grid, theta, n_sub) for i in range(M)
    )
    
    for i, row_vals in results:
        for idx, j in enumerate(range(i, M)):
            K_uncentered[i, j] = row_vals[idx]
            K_uncentered[j, i] = row_vals[idx]
            
    weight = 1.0 / max(M - 1, 1)
    # The centered matrix is returned by _covariance_kernel_component2 directly
    # Wait, _covariance_kernel_component2 uses its internally hardcoded n_sub.
    # In kl_eigenvalues.py, n_sub is internally set inside _covariance_kernel_component2.
    # The user asks to vary n_sub! I need to redefine it or just accept the one for centered.
    # Wait, _covariance_kernel_component2 calls _cov_s2_s2_vectorized.
    # I can just implement the projection myself!
    
    # K_centered = P @ K_uncentered @ P
    # P = I - 11^T / M.
    # No, P is integral projection: f(u) - \int f(v) dv / (1-theta).
    # Since weight is uniform, P = I - 11^T / M.
    K_centered = K_uncentered.copy()
    row_means = K_centered.mean(axis=1)
    col_means = K_centered.mean(axis=0)
    total_mean = K_centered.mean()
    
    for i in range(M):
        for j in range(M):
            K_centered[i, j] = K_uncentered[i, j] - row_means[i] - col_means[j] + total_mean
            
    return np.trace(K_uncentered) * weight, np.trace(K_centered) * weight

def main():
    thetas = [0.1, 0.3, 0.5]
    Ms = [100, 200, 500]
    n_subs = [8, 16, 32, 64]
    
    target_cen_map = {
        0.1: 2.0503e-4,
        0.3: 1.4468e-3,
        0.5: 2.4802e-3
    }
    
    results = []
    
    for theta in thetas:
        target_unc = (theta**2) / 45.0
        target_cen = target_cen_map[theta]
        
        for M in Ms:
            for n_sub in n_subs:
                print(f"theta={theta}, M={M}, n_sub={n_sub}...")
                tr_unc, tr_cen = compute_traces(theta, M, n_sub)
                err_unc = abs(tr_unc - target_unc) / target_unc
                err_cen = abs(tr_cen - target_cen) / target_cen
                
                results.append({
                    'theta': theta,
                    'M': M,
                    'n_sub': n_sub,
                    'Traza Cen': tr_cen,
                    'Error Cen': err_cen,
                    'Traza Unc': tr_unc,
                    'Error Unc': err_unc
                })
                
    df = pd.DataFrame(results)
    df.to_csv("experiments/results/audit4b_tarea4.csv", index=False)

if __name__ == "__main__":
    main()
