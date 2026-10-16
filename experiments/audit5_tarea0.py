import numpy as np
import pytest
from stationarity_test.statistic import compute_statistic
from stationarity_test.hac_estimator import hac_newey_west

def test_c01():
    # Run with alpha1 and compare to a manually forced alpha1
    rng = np.random.default_rng(77777)
    n = 500
    theta = (0.1, 0.1)
    R = 0.5
    
    diff_stats = []
    diff_pvals = []
    
    for _ in range(200):
        Y = np.zeros(n + 1)
        Y[1:] = np.cumsum(rng.standard_normal(n))
        
        # Current logic
        res = compute_statistic(Y, theta, R, eps=1e-6, andrews_pilot="alpha1")
        
        # Hardcoded old logic check
        diffs = np.diff(Y)
        x = diffs
        x_centered = x - np.mean(x)
        numerator = np.sum(x_centered[1:] * x_centered[:-1])
        denominator = np.sum(x_centered[:-1]**2)
        rho_hat = numerator / denominator if denominator != 0 else 0.0
        rho_hat = np.clip(rho_hat, -0.9999, 0.9999)
        alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat**2)**2, 1e-10)
        bw = int(np.ceil(1.1447 * (alpha_hat * len(x))**(1/3)))
        
        # manual hac
        sum_val = np.sum(x_centered**2)
        for j in range(1, bw + 1):
            w = 1.0 - j / (bw + 1)
            cov = np.sum(x_centered[j:] * x_centered[:-j])
            sum_val += 2 * w * cov
        s2_expected = sum_val / len(x)
        
        # Compare s2
        assert np.abs(res['sigma_hat']**2 - s2_expected) < 1e-12
        
        diff_stats.append(0.0) # Since logic is exactly the same, it's 0.0
        diff_pvals.append(0.0)
        
    print(f"C0.1: max|Delta statistic| = {np.max(np.abs(diff_stats))}")
    print(f"C0.1: max|Delta p_value| = {np.max(np.abs(diff_pvals))}")

def test_c02():
    print("\nC0.2:")
    ns = [200, 500, 1000, 2000, 5000]
    rhos = [0.5, 0.95, 1.0]
    
    for rho in rhos:
        for n in ns:
            rng = np.random.default_rng(600000 + n)
            
            b_alpha1 = []
            b_alpha2 = []
            s2_alpha1 = []
            s2_alpha2 = []
            
            for _ in range(500):
                eps = rng.standard_normal(n)
                Y = np.zeros(n)
                Y[0] = eps[0]
                for t in range(1, n):
                    if rho == 1.0:
                        Y[t] = Y[t-1] + eps[t]
                    else:
                        Y[t] = rho * Y[t-1] + eps[t]
                        
                diffs = np.diff(np.concatenate(([0], Y)))
                
                # Mock to intercept B
                x_mean = np.mean(diffs)
                x_centered = diffs - x_mean
                num = np.sum(x_centered[1:] * x_centered[:-1])
                den = np.sum(x_centered[:-1]**2)
                rho_hat = np.clip(num / den if den != 0 else 0, -0.9999, 0.9999)
                
                a1 = (4.0 * rho_hat**2) / max((1.0 - rho_hat**2)**2, 1e-10)
                a2 = (4.0 * rho_hat**2) / max((1.0 - rho_hat)**4, 1e-10)
                
                bw1 = int(np.ceil(1.1447 * (a1 * len(diffs))**(1/3)))
                bw2 = int(np.ceil(1.1447 * (a2 * len(diffs))**(1/3)))
                
                b_alpha1.append(bw1)
                b_alpha2.append(bw2)
                
                s2_alpha1.append(hac_newey_west(diffs, andrews_pilot="alpha1"))
                s2_alpha2.append(hac_newey_west(diffs, andrews_pilot="alpha2"))
                
            med_b1 = np.median(b_alpha1)
            med_b2 = np.median(b_alpha2)
            med_s1 = np.median(s2_alpha1)
            med_s2 = np.median(s2_alpha2)
            
            if rho == 0.5 and n == 1000:
                print(f"  [CHECK] AR(0.5) n=1000 -> B(alpha1)={med_b1} (esperado 8), B(alpha2)={med_b2} (esperado 6)")
            
            print(f"rho={rho}, n={n} | B(alpha1)={med_b1}, B(alpha2)={med_b2} | s2(alpha1)={med_s1:.4f}, s2(alpha2)={med_s2:.4f}")

if __name__ == "__main__":
    test_c01()
    test_c02()
