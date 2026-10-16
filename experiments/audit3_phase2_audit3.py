"""
Audit 3 — Phase 2: Execution of T1c, T1d, T2, T3, T4.
"""
import sys, os, json, time
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kstest, norm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

def task1c():
    from stationarity_test.kl_eigenvalues import compute_eigenvalues
    print("=" * 70)
    print("  TASK 1c: Trace validation against Wick quadrature (Component 2)")
    print("=" * 70)
    
    thetas_test = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
    expected_F2 = [5.349e-5, 2.0503e-4, 4.3948e-4, 7.3909e-4, 1.4468e-3, 2.4802e-3]
    
    trace_results = []
    print(f"  {'theta':>6s}  {'sum(eig)+tb':>12s}  {'quadrature':>12s}  {'rel error':>10s}  {'status':>6s}")
    for th, exp in zip(thetas_test, expected_F2):
        eig, tb = compute_eigenvalues(th, component=2, K=100, eps=1e-8)
        total = float(np.sum(eig) + tb)
        rel_err = abs(total - exp) / exp
        status = "PASS" if rel_err < 0.02 else "FAIL"
        print(f"  {th:6.2f}  {total:12.6e}  {exp:12.6e}  {rel_err:10.6f}  {status:>6s}")
        trace_results.append({'theta': th, 'total': total, 'expected': exp, 'rel_err': rel_err})
    
    # Check internal identity C_theta(0) = theta^2 / 90
    from stationarity_test.kl_eigenvalues import _covariance_kernel_component2
    K_mat = _covariance_kernel_component2(0.1, M=100)
    # The trace of the uncentered kernel divided by M is roughly C_theta(0).
    # Since K_mat is centered, its trace is a bit smaller. 
    # The identity is C_theta(0) = theta^2/90 for S^2(u) covariance.
    val = 0.1**2 / 90
    print(f"  Identity C_theta(0) expected for theta=0.1: {val:.6e}")
    return trace_results

def task1d():
    from stationarity_test.kl_eigenvalues import compute_eigenvalues
    print("\n" + "=" * 70)
    print("  TASK 1d: Eigenvalue table for paper")
    print("=" * 70)
    
    thetas_test = [0.02, 0.05, 0.10, 0.20, 0.30, 0.50]
    k_pi_2 = [1.0 / (k * np.pi)**2 for k in range(1, 6)]
    
    print("  (k*pi)^-2:", [f"{v:.6f}" for v in k_pi_2])
    
    eig_results = {}
    for th in thetas_test:
        eig, _ = compute_eigenvalues(th, component=1, K=5, eps=1e-6)
        ratios = [e / ref for e, ref in zip(eig, k_pi_2)]
        eig_results[th] = {'eig': list(eig), 'ratios': ratios}
        print(f"  theta={th:.2f}:")
        print(f"    lambda_k: {[f'{e:.6f}' for e in eig]}")
        print(f"    ratio:    {[f'{r:.4f}' for r in ratios]}")
        
    return eig_results

def task2_and_3():
    from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
    from stationarity_test.null_quantiles import _evaluate_F1_on_path, _evaluate_F2_on_path
    
    print("\n" + "=" * 70)
    print("  TASK 2: Moments and correlation by n")
    print("  TASK 3: Convergence of the law (KS tests and figure)")
    print("=" * 70)
    
    thetas_test = [0.1, 0.3, 0.5]
    ns = [100, 200, 500, 1000, 2000, 5000, 'inf']
    n_reps = 10000
    
    # E[F1^2] = trace(K1). 
    # But E[F1] is approximately E[g1_std]. 
    # E[F1^2] is exactly E[g1_std^2].
    
    def E_F1_sq_closed(theta):
        return (10 - 40*theta + 55*theta**2 - 26*theta**3) / (60*(1-theta)**2)
        
    expected_F2_sq = {0.1: 2.0503e-4, 0.3: 1.4468e-3, 0.5: 2.4802e-3}
    
    results = {}
    
    # For Davies CDF in T3
    from stationarity_test.kl_eigenvalues import compute_eigenvalues
    
    def simulate_davies_cdf(eigenvalues, n_sims=100000, seed=42):
        rng = np.random.default_rng(seed)
        Z2 = rng.chisquare(1, size=(n_sims, len(eigenvalues)))
        Q = np.sort(Z2 @ eigenvalues)
        def cdf(x):
            return np.searchsorted(Q, x, side='right') / n_sims
        return cdf
        
    davies_cdfs = {}
    for th in thetas_test:
        eig1, _ = compute_eigenvalues(th, component=1, K=200, eps=1e-8)
        davies_cdfs[th] = simulate_davies_cdf(eig1)
    
    # Prepare figure for T3
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for th_idx, th in enumerate(thetas_test):
        print(f"\n  --- Theta = {th} ---")
        results[th] = {}
        
        E_F1_sq = E_F1_sq_closed(th)
        E_F2_sq = expected_F2_sq[th]
        
        g1_sq_inf = None
        g2_sq_inf = None
        combo_inf = None
        
        ks_stats = []
        
        for n in ns:
            rng = np.random.default_rng(3000 + (n if isinstance(n, int) else 99999))
            g1_std = np.empty(n_reps)
            g2_std = np.empty(n_reps)
            
            if n == 'inf':
                # Continuous Brownian path approximation (simulated at fine mesh M=20000)
                M = 20000
                tau1 = int(round(th * M))
                tau2 = int(round(th * M))
                
                for i in range(n_reps):
                    increments = rng.standard_normal(M)
                    W = np.concatenate(([0.0], np.cumsum(increments))) / np.sqrt(M)
                    
                    # F1: Var_u of (1/theta) int_u W(s)ds
                    means = rolling_mean(W, tau1)
                    var_means = sample_variance_over_k(means)
                    F1 = np.sqrt(max(var_means, 0.0))
                    
                    # F2: Var_u of (1/theta) int_u (W - W_bar)^2
                    # The population variance of W in window is rolling_var(W, tau2)
                    variances = rolling_var(W, tau2)
                    var_of_var = sample_variance_over_k(variances)
                    F2 = np.sqrt(max(var_of_var, 0.0))
                    
                    g1_std[i] = F1
                    g2_std[i] = F2
            else:
                tau1 = max(2, min(int(round(th * n)), n // 2))
                tau2 = max(2, min(int(round(th * n)), n // 2))
                sc1 = 1.0 * n**(1/2.0)
                sc2 = 1.0 * n**(2/2.0)
                
                for i in range(n_reps):
                    Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
                    means = rolling_mean(Y, tau1)
                    g1 = np.sqrt(max(sample_variance_over_k(means), 0.0))
                    g1_std[i] = g1 / sc1
                    
                    variances = rolling_var(Y, tau2)
                    g2 = np.sqrt(max(sample_variance_over_k(variances), 0.0))
                    g2_std[i] = g2 / sc2
            
            g1_sq = g1_std**2
            g2_sq = g2_std**2
            
            mean_g1_sq = np.mean(g1_sq)
            mean_g2_sq = np.mean(g2_sq)
            mean_g1 = np.mean(g1_std)
            mean_g2 = np.mean(g2_std)
            
            # Fisher transformation for correlation CI
            r = np.corrcoef(g1_sq, g2_sq)[0, 1]
            z = np.arctanh(r)
            se = 1.0 / np.sqrt(n_reps - 3)
            z_low, z_high = z - 1.96*se, z + 1.96*se
            r_low, r_high = np.tanh(z_low), np.tanh(z_high)
            
            print(f"    n={str(n):>4}: E[g1^2]={mean_g1_sq:.5f} (ratio={mean_g1_sq/E_F1_sq:.3f}), "
                  f"E[g2^2]={mean_g2_sq:.5e} (ratio={mean_g2_sq/E_F2_sq:.3f}), "
                  f"corr={r:.3f} [{r_low:.3f}, {r_high:.3f}]")
            
            results[th][n] = {
                'E_g1_sq': mean_g1_sq, 'ratio_1': mean_g1_sq / E_F1_sq,
                'E_g2_sq': mean_g2_sq, 'ratio_2': mean_g2_sq / E_F2_sq,
                'E_g1': mean_g1, 'E_g2': mean_g2,
                'corr': r, 'corr_ci': [r_low, r_high]
            }
            
            # T3 - KS tests
            if n == 'inf':
                g1_sq_inf = g1_sq
                g2_sq_inf = g2_sq
                combo_inf = 0.25 * g1_sq + 0.25 * g2_sq  # R=0.5 -> (1-R)^2 = 0.25
                
                # KS for inf vs analytical Davies
                ks_1 = kstest(g1_sq_inf, davies_cdfs[th]).statistic
                results[th][n]['ks_1'] = ks_1
                print(f"      KS_1 (vs Davies) = {ks_1:.4f}")
            else:
                ks_1 = kstest(g1_sq, davies_cdfs[th]).statistic
                # We need the 'inf' row first to compare g2 and combo, so we will do that after the loop.
                ks_stats.append((n, g1_sq, g2_sq))
                
        # Now do the comparisons against 'inf'
        print("    KS tests vs n=inf:")
        for n_val, g1_s, g2_s in ks_stats:
            combo_s = 0.25 * g1_s + 0.25 * g2_s
            ks_2 = kstest(g2_s, g2_sq_inf).statistic
            ks_combo = kstest(combo_s, combo_inf).statistic
            
            results[th][n_val]['ks_1'] = kstest(g1_s, davies_cdfs[th]).statistic
            results[th][n_val]['ks_2'] = ks_2
            results[th][n_val]['ks_combo'] = ks_combo
            
            print(f"      n={n_val:<4}: KS_1={results[th][n_val]['ks_1']:.4f}, KS_2={ks_2:.4f}, KS_combo={ks_combo:.4f}")
        
        # Plotting
        ax = axes[th_idx]
        n_vals_plot = [n for n in ns if isinstance(n, int)]
        ks1_plot = [results[th][n]['ks_1'] for n in n_vals_plot]
        ks2_plot = [results[th][n]['ks_2'] for n in n_vals_plot]
        ksc_plot = [results[th][n]['ks_combo'] for n in n_vals_plot]
        
        ax.plot(n_vals_plot, ks1_plot, 'o-', label='KS(g1^2, Davies)')
        ax.plot(n_vals_plot, ks2_plot, 's-', label='KS(g2^2, n=inf)')
        ax.plot(n_vals_plot, ksc_plot, '^-', label='KS(Combined R=0.5, n=inf)')
        ax.axhline(1.36 / np.sqrt(10000), color='gray', linestyle='--', label='95% DKW noise limit (0.0136)')
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(f'Theta = {th}')
        ax.set_xlabel('Sample Size n')
        ax.set_ylabel('Kolmogorov-Smirnov Statistic')
        if th_idx == 0:
            ax.legend()

    plt.tight_layout()
    fig_path = os.path.join(RESULTS_DIR, 'fig_convergence_audit3.pdf')
    plt.savefig(fig_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"  Saved figure to {fig_path}")

    return results

def task4():
    print("\n" + "=" * 70)
    print("  TASK 4: Independent chi-squared model (Gap 2 quantification)")
    print("=" * 70)
    
    from stationarity_test.kl_eigenvalues import compute_eigenvalues
    
    def simulate_davies_cdf(eigenvalues, n_sims=100000, seed=42):
        rng = np.random.default_rng(seed)
        Z2 = rng.chisquare(1, size=(n_sims, len(eigenvalues)))
        Q = np.sort(Z2 @ eigenvalues)
        def cdf(x):
            return np.searchsorted(Q, x, side='right') / n_sims
        return cdf
    
    thetas_test = [0.1, 0.3, 0.5]
    Rs = [0.0, 0.25, 0.5, 0.75, 1.0]
    n_reps = 10000
    n = 1000
    
    results = {}
    
    for th in thetas_test:
        print(f"\n  --- Theta = {th} ---")
        results[th] = {}
        
        eig1, _ = compute_eigenvalues(th, component=1, K=200, eps=1e-8)
        eig2, _ = compute_eigenvalues(th, component=2, K=100, eps=1e-8)
        
        # We need the simulated ECDF of the actual statistic
        rng = np.random.default_rng(4000)
        
        from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
        tau1 = max(2, min(int(round(th * n)), n // 2))
        tau2 = max(2, min(int(round(th * n)), n // 2))
        sc1 = 1.0 * n**(1/2.0)
        sc2 = 1.0 * n**(2/2.0)
        
        g1_sq_sim = np.empty(n_reps)
        g2_sq_sim = np.empty(n_reps)
        
        for i in range(n_reps):
            Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
            means = rolling_mean(Y, tau1)
            g1_sq_sim[i] = max(sample_variance_over_k(means), 0.0) / (sc1**2)
            
            variances = rolling_var(Y, tau2)
            g2_sq_sim[i] = max(sample_variance_over_k(variances), 0.0) / (sc2**2)
            
        for R in Rs:
            combo_sim = np.sqrt((1-R)**2 * g1_sq_sim + R**2 * g2_sq_sim)
            
            # The independent model: sqrt( (1-R)^2 Q1 + R^2 Q2 )
            # Q1 = sum eig1 * Z^2, Q2 = sum eig2 * Z'^2
            # Z and Z' are independent.
            # So (1-R)^2 Q1 + R^2 Q2 is a single quadratic form with eigenvalues:
            eig_model = np.concatenate([ (1-R)**2 * eig1, R**2 * eig2 ])
            # Sort them just in case
            eig_model = np.sort(eig_model)[::-1]
            
            # Generate the CDF function for the independent model
            cdf_model = simulate_davies_cdf(eig_model)
            
            # Since our statistic is sqrt(Q), the CDF at q is cdf_model(q^2)
            def model_cdf_sqrt(q):
                return cdf_model(q**2)
                
            # KS test
            ks_stat = kstest(combo_sim, model_cdf_sqrt).statistic
            
            # Error de tamaño inducido
            # Encontrar el cuantil 0.05 del modelo (i.e. CDF_model(q) = 0.95, since p-value = 1-CDF)
            # Actually we want the 95th percentile of the statistic, which corresponds to alpha=0.05
            # We can find it by querying the simulated CDF of the model.
            model_sims = np.sqrt(np.random.default_rng(1).chisquare(1, (100000, len(eig_model))) @ eig_model)
            q_model_05 = np.quantile(model_sims, 0.95)
            
            # Empirical size of this quantile in the actual data
            actual_size = np.mean(combo_sim >= q_model_05)
            size_error = abs(actual_size - 0.05)
            
            print(f"    R={R:<4}: KS={ks_stat:.4f}, size_error=|{actual_size:.4f} - 0.05| = {size_error:.4f}")
            results[th][R] = {'ks': ks_stat, 'size_error': size_error, 'actual_size': actual_size}
            
    return results

if __name__ == "__main__":
    t0 = time.time()
    r1c = task1c()
    r1d = task1d()
    r23 = task2_and_3()
    r4 = task4()
    elapsed = time.time() - t0
    
    print(f"\nTotal elapsed time: {elapsed:.1f}s")
    
    all_results = {
        'task1c': r1c,
        'task1d': r1d,
        'task2_3': r23,
        'task4': r4,
        'elapsed': elapsed
    }
    
    json_path = os.path.join(RESULTS_DIR, 'audit3_phase2_audit3.json')
    with open(json_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to {json_path}")
