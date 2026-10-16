"""
Pre-submission audit — 4 computational tasks.
All new files have suffix _audit. Does NOT modify existing code or results.
"""
import sys, os, json, time, hashlib
from datetime import datetime, timezone

import numpy as np
from scipy.interpolate import interp1d

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.hac_estimator import hac_newey_west
from numba import njit

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
THETA = (0.1, 0.1)
ALPHA = 0.05

# ======================================================================
# TASK 1 — O(n) rolling_var with Kahan compensated summation
# ======================================================================

@njit(cache=True)
def rolling_var_audit(x, tau):
    """
    O(n) sliding-window population variance using the identity:
        Var(X) = E[X^2] - (E[X])^2
    
    Maintains running sums of x and x^2 with Kahan compensated summation.
    Divisor is population (tau+1), matching the existing implementation.
    """
    n_plus_1 = len(x)
    w = tau + 1  # window size
    n_out = n_plus_1 - tau
    result = np.empty(n_out, dtype=np.float64)

    # Initial sums for window [0, w-1] with Kahan
    sum_x = 0.0;  comp_x = 0.0
    sum_x2 = 0.0; comp_x2 = 0.0
    for i in range(w):
        # Kahan add x[i]
        y = x[i] - comp_x
        t = sum_x + y
        comp_x = (t - sum_x) - y
        sum_x = t
        # Kahan add x[i]^2
        v = x[i] * x[i] - comp_x2
        t2 = sum_x2 + v
        comp_x2 = (t2 - sum_x2) - v
        sum_x2 = t2

    mean_0 = sum_x / w
    result[0] = sum_x2 / w - mean_0 * mean_0

    # Slide
    for k in range(1, n_out):
        x_new = x[k + tau]
        x_old = x[k - 1]

        # Remove x_old, add x_new to sum_x (Kahan)
        y = (x_new - x_old) - comp_x
        t = sum_x + y
        comp_x = (t - sum_x) - y
        sum_x = t

        # Remove x_old^2, add x_new^2 to sum_x2 (Kahan)
        v = (x_new * x_new - x_old * x_old) - comp_x2
        t2 = sum_x2 + v
        comp_x2 = (t2 - sum_x2) - v
        sum_x2 = t2

        mean_k = sum_x / w
        result[k] = sum_x2 / w - mean_k * mean_k

    # Clamp negative values (numerical noise)
    for i in range(n_out):
        if result[i] < 0.0:
            result[i] = 0.0

    return result


def task1():
    """O(n) rolling_var verification and benchmarking."""
    print("=" * 70)
    print("  TASK 1 — O(n) rolling_var with Kahan compensated summation")
    print("=" * 70)
    t0 = time.perf_counter()

    # Warm up JIT
    _x = np.random.default_rng(0).standard_normal(100)
    rolling_var_audit(_x, 5)
    rolling_var(_x, 5)

    # (a) Numerical equivalence
    rng = np.random.default_rng(12345)
    configs = []
    for n in [100, 500, 2000]:
        for tau in [5, 50, 500]:
            if tau < n:
                configs.append((n, tau))

    max_diffs = {}
    for n, tau in configs:
        max_d = 0.0
        for rep in range(1000):
            x = np.cumsum(rng.standard_normal(n + 1))
            v_old = rolling_var(x, tau)
            v_new = rolling_var_audit(x, tau)
            d = np.max(np.abs(v_old - v_new))
            max_d = max(max_d, d)
        max_diffs[(n, tau)] = max_d
        status = "PASS" if max_d < 1e-9 else "FAIL"
        print(f"  n={n:5d}, tau={tau:4d}: max|diff| = {max_d:.2e}  [{status}]")

    # (b) Test suite sanity
    from stationarity_test.statistic import compute_statistic
    rng2 = np.random.default_rng(999)
    Y = np.cumsum(np.concatenate(([0.0], rng2.standard_normal(500))))
    res = compute_statistic(Y, THETA, 0.5)
    print(f"\n  Test pipeline sanity: stat={res['statistic']:.6f}, p={res['p_value']:.4f}")

    # (c) Benchmark
    print("\n  Benchmark n=20000:")
    benchmarks = {}
    for tau in [10, 100, 1000]:
        x = rng.standard_normal(20001)
        x = np.cumsum(x)

        times_old = []
        for _ in range(5):
            t_s = time.perf_counter()
            rolling_var(x, tau)
            times_old.append(time.perf_counter() - t_s)
        t_old = np.median(times_old)

        times_new = []
        for _ in range(5):
            t_s = time.perf_counter()
            rolling_var_audit(x, tau)
            times_new.append(time.perf_counter() - t_s)
        t_new = np.median(times_new)

        speedup = t_old / t_new if t_new > 0 else float('inf')
        benchmarks[tau] = (t_old, t_new, speedup)
        print(f"    tau={tau:5d}: old={t_old*1000:.2f}ms, new={t_new*1000:.2f}ms, "
              f"speedup={speedup:.1f}x")

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 1 total: {elapsed:.1f}s")

    return {
        'max_diffs': {f"n={k[0]}_tau={k[1]}": v for k, v in max_diffs.items()},
        'benchmarks': {str(k): {'old_ms': v[0]*1000, 'new_ms': v[1]*1000,
                                 'speedup': v[2]} for k, v in benchmarks.items()},
        'elapsed': elapsed,
    }


# ======================================================================
# TASK 2 — Diagnostic of adaptive weight R-hat
# ======================================================================

def _compute_Rhat(Y, theta, sigma_known=None):
    """Compute R-hat = g2_std^2 / (g1_std^2 + g2_std^2) for a single path."""
    n = len(Y) - 1
    theta_1, theta_2 = theta
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    if sigma_known is not None:
        sigma_hat = sigma_known
        sigma_hat_sq = sigma_known ** 2
    else:
        diffs = np.diff(Y)
        sigma_hat_sq = hac_newey_west(diffs)
        sigma_hat = np.sqrt(sigma_hat_sq)

    scale_1 = sigma_hat * n ** (c_1 / 2.0)
    scale_2 = sigma_hat_sq * n ** (c_2 / 2.0)

    means = rolling_mean(Y, tau_1)
    g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
    variances = rolling_var(Y, tau_2)
    g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

    g1_std = g1_raw / scale_1 if scale_1 > 0 else 0.0
    g2_std = g2_raw / scale_2 if scale_2 > 0 else 0.0

    denom = g1_std**2 + g2_std**2
    if denom > 0:
        R_hat = g2_std**2 / denom
    else:
        R_hat = 0.5
    return R_hat, g1_std, g2_std


def task2():
    """Diagnostic of adaptive weight R-hat."""
    print("\n" + "=" * 70)
    print("  TASK 2 — Diagnostic of adaptive weight R-hat")
    print("=" * 70)
    t0 = time.perf_counter()

    N_SIM = 5000
    results = {}

    # (i) H0 random walk
    for n in [200, 500, 1000]:
        Rhats = np.empty(N_SIM)
        for i in range(N_SIM):
            rng = np.random.default_rng(70000 + i)
            Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
            Rhats[i] = _compute_Rhat(Y, THETA, sigma_known=1.0)[0]
        results[f"H0_n{n}"] = {
            'mean': float(np.mean(Rhats)),
            'median': float(np.median(Rhats)),
            'q05': float(np.quantile(Rhats, 0.05)),
            'q95': float(np.quantile(Rhats, 0.95)),
        }
        print(f"  H0 n={n}: mean={np.mean(Rhats):.4f}, med={np.median(Rhats):.4f}, "
              f"q05={np.quantile(Rhats,0.05):.4f}, q95={np.quantile(Rhats,0.95):.4f}")

    # (ii) DGP3: RW + variance break r=4, n=1000
    n = 1000
    Rhats = np.empty(N_SIM)
    for i in range(N_SIM):
        rng = np.random.default_rng(80000 + i)
        t_break = n // 2
        eps = np.empty(n)
        eps[:t_break] = rng.standard_normal(t_break) * 1.0
        eps[t_break:] = rng.standard_normal(n - t_break) * 4.0
        Y = np.concatenate(([0.0], np.cumsum(eps)))
        Rhats[i] = _compute_Rhat(Y, THETA, sigma_known=1.0)[0]
    results["DGP3_r4_n1000"] = {
        'mean': float(np.mean(Rhats)),
        'median': float(np.median(Rhats)),
        'q05': float(np.quantile(Rhats, 0.05)),
        'q95': float(np.quantile(Rhats, 0.95)),
    }
    print(f"  DGP3 r=4 n=1000: mean={np.mean(Rhats):.4f}, med={np.median(Rhats):.4f}, "
          f"q05={np.quantile(Rhats,0.05):.4f}, q95={np.quantile(Rhats,0.95):.4f}")

    # (iii) DGP4: AR(0.5) + variance break r=3, n=500
    n = 500; rho = 0.5
    Rhats = np.empty(N_SIM)
    for i in range(N_SIM):
        rng = np.random.default_rng(90000 + i)
        t_break = n // 2
        eps = np.empty(n)
        eps[:t_break] = rng.standard_normal(t_break) * 1.0
        eps[t_break:] = rng.standard_normal(n - t_break) * 3.0
        Y = np.empty(n + 1); Y[0] = 0.0
        for t in range(n):
            Y[t+1] = rho * Y[t] + eps[t]
        Rhats[i] = _compute_Rhat(Y, THETA, sigma_known=1.0)[0]
    results["DGP4_r3_n500"] = {
        'mean': float(np.mean(Rhats)),
        'median': float(np.median(Rhats)),
        'q05': float(np.quantile(Rhats, 0.05)),
        'q95': float(np.quantile(Rhats, 0.95)),
    }
    print(f"  DGP4 r=3 n=500: mean={np.mean(Rhats):.4f}, med={np.median(Rhats):.4f}, "
          f"q05={np.quantile(Rhats,0.05):.4f}, q95={np.quantile(Rhats,0.95):.4f}")

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 2 total: {elapsed:.1f}s")
    results['elapsed'] = elapsed
    return results


# ======================================================================
# TASK 3 — Rebalanced adaptive weight
# ======================================================================

def task3():
    """Rebalanced adaptive weight experiment."""
    print("\n" + "=" * 70)
    print("  TASK 3 — Rebalanced adaptive weight")
    print("=" * 70)
    t0 = time.perf_counter()

    N_CAL_CONST = 50000
    N_CAL_CDF = 10000
    N_SIM = 5000

    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    # Step 1: Estimate rebalancing constants m_i(theta, n)
    print("  Step 1: Estimating rebalance constants (50k sims)...")
    rebalance = {}
    for n in [200, 500, 1000]:
        theta_1, theta_2 = THETA
        tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
        tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))
        scale_1 = 1.0 * n ** (c_1 / 2.0)
        scale_2 = 1.0 * n ** (c_2 / 2.0)

        rng = np.random.default_rng(42)
        g1_vals = np.empty(N_CAL_CONST)
        g2_vals = np.empty(N_CAL_CONST)
        for j in range(N_CAL_CONST):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_vals[j] = g1_raw / scale_1
            g2_vals[j] = g2_raw / scale_2

        m1 = float(np.mean(g1_vals))
        m2 = float(np.mean(g2_vals))
        rebalance[n] = {'m1': m1, 'm2': m2}
        print(f"    n={n}: m1={m1:.6f}, m2={m2:.6f}, ratio m1/m2={m1/m2:.3f}")

    # Save rebalance constants
    rebal_path = os.path.join(RESULTS_DIR, 'rebalance_constants_audit.json')
    with open(rebal_path, 'w') as f:
        json.dump({'theta': list(THETA), 'N_cal': N_CAL_CONST,
                   'constants': {str(k): v for k, v in rebalance.items()},
                   'seed': 42}, f, indent=2)
    print(f"    Saved: {rebal_path}")

    # Step 2: Build null CDFs
    print("\n  Step 2: Building null CDFs (N_cal=10000)...")

    def build_cdf_rebalanced(n, N_cal, seed):
        theta_1, theta_2 = THETA
        tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
        tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))
        scale_1 = 1.0 * n ** (c_1 / 2.0)
        scale_2 = 1.0 * n ** (c_2 / 2.0)
        m1 = rebalance[n]['m1']
        m2 = rebalance[n]['m2']

        rng = np.random.default_rng(seed)
        stats = np.empty(N_cal)
        for j in range(N_cal):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_std = g1_raw / scale_1
            g2_std = g2_raw / scale_2

            b1 = g1_std / m1
            b2 = g2_std / m2

            denom = b1**2 + b2**2
            R_bal = b2**2 / denom if denom > 0 else 0.5

            stats[j] = np.sqrt((1.0 - R_bal)**2 * b1**2 + R_bal**2 * b2**2)

        stats_sorted = np.sort(stats)
        ecdf_y = np.arange(1, N_cal + 1) / N_cal
        return interp1d(stats_sorted, ecdf_y, kind='linear',
                       bounds_error=False, fill_value=(0.0, 1.0))

    def build_cdf_adaptive(n, N_cal, seed):
        theta_1, theta_2 = THETA
        tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
        tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))
        scale_1 = 1.0 * n ** (c_1 / 2.0)
        scale_2 = 1.0 * n ** (c_2 / 2.0)

        rng = np.random.default_rng(seed)
        stats = np.empty(N_cal)
        for j in range(N_cal):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_std = g1_raw / scale_1
            g2_std = g2_raw / scale_2

            denom = g1_std**2 + g2_std**2
            R_hat = g2_std**2 / denom if denom > 0 else 0.5

            stats[j] = np.sqrt((1.0 - R_hat)**2 * g1_std**2 + R_hat**2 * g2_std**2)

        stats_sorted = np.sort(stats)
        ecdf_y = np.arange(1, N_cal + 1) / N_cal
        return interp1d(stats_sorted, ecdf_y, kind='linear',
                       bounds_error=False, fill_value=(0.0, 1.0))

    cdf_adaptive = {}
    cdf_rebalanced = {}
    for n in [200, 500, 1000]:
        t_s = time.perf_counter()
        cdf_adaptive[n] = build_cdf_adaptive(n, N_CAL_CDF, seed=42)
        cdf_rebalanced[n] = build_cdf_rebalanced(n, N_CAL_CDF, seed=42)
        print(f"    n={n}: {time.perf_counter()-t_s:.1f}s")

    # Step 3: Comparisons
    print("\n  Step 3: Running comparisons (5k sims each)...")
    results = {}

    def ci_wilson(p_hat, n_sim):
        z = 1.96
        denom = 1 + z**2/n_sim
        center = (p_hat + z**2/(2*n_sim)) / denom
        width = z * np.sqrt(p_hat*(1-p_hat)/n_sim + z**2/(4*n_sim**2)) / denom
        return round(float(center - width), 4), round(float(center + width), 4)

    def eval_both(Y, n, cdf_a, cdf_r, sigma_known=1.0):
        theta_1, theta_2 = THETA
        tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
        tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))
        scale_1 = sigma_known * n ** (c_1 / 2.0)
        scale_2 = sigma_known**2 * n ** (c_2 / 2.0)

        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

        g1_std = g1_raw / scale_1
        g2_std = g2_raw / scale_2

        # Adaptive
        denom_a = g1_std**2 + g2_std**2
        R_hat = g2_std**2 / denom_a if denom_a > 0 else 0.5
        stat_a = np.sqrt((1-R_hat)**2 * g1_std**2 + R_hat**2 * g2_std**2)
        p_a = float(np.clip(cdf_a(stat_a), 0, 1))

        # Rebalanced
        m1 = rebalance[n]['m1']
        m2 = rebalance[n]['m2']
        b1 = g1_std / m1
        b2 = g2_std / m2
        denom_r = b1**2 + b2**2
        R_bal = b2**2 / denom_r if denom_r > 0 else 0.5
        stat_r = np.sqrt((1-R_bal)**2 * b1**2 + R_bal**2 * b2**2)
        p_r = float(np.clip(cdf_r(stat_r), 0, 1))

        return p_a, p_r, R_hat, R_bal

    # (a) Size under H0
    print("    (a) Size under H0:")
    for n in [200, 500, 1000]:
        rej_a = 0; rej_r = 0
        for i in range(N_SIM):
            rng = np.random.default_rng(100000 + i)
            Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
            p_a, p_r, _, _ = eval_both(Y, n, cdf_adaptive[n], cdf_rebalanced[n])
            if p_a < ALPHA: rej_a += 1
            if p_r < ALPHA: rej_r += 1
        rate_a = rej_a / N_SIM; rate_r = rej_r / N_SIM
        ci_a = ci_wilson(rate_a, N_SIM); ci_r = ci_wilson(rate_r, N_SIM)
        results[f"size_H0_n{n}"] = {
            'adaptive': rate_a, 'adaptive_ci': ci_a,
            'rebalanced': rate_r, 'rebalanced_ci': ci_r,
        }
        print(f"      n={n}: adapt={rate_a:.4f} {ci_a}, rebal={rate_r:.4f} {ci_r}")

    # (b) Power DGP1
    print("    (b) Power DGP1:")
    dgp1_cells = [(0.95, 200), (0.97, 500), (0.99, 1000)]
    for rho, n in dgp1_cells:
        rej_a = 0; rej_r = 0
        for i in range(N_SIM):
            rng = np.random.default_rng(200000 + i)
            eps = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            for t in range(n):
                Y[t+1] = rho * Y[t] + eps[t]
            p_a, p_r, _, _ = eval_both(Y, n, cdf_adaptive[n], cdf_rebalanced[n])
            if p_a < ALPHA: rej_a += 1
            if p_r < ALPHA: rej_r += 1
        rate_a = rej_a / N_SIM; rate_r = rej_r / N_SIM
        ci_a = ci_wilson(rate_a, N_SIM); ci_r = ci_wilson(rate_r, N_SIM)
        results[f"power_DGP1_rho{rho}_n{n}"] = {
            'adaptive': rate_a, 'adaptive_ci': ci_a,
            'rebalanced': rate_r, 'rebalanced_ci': ci_r,
        }
        print(f"      rho={rho}, n={n}: adapt={rate_a:.4f} {ci_a}, "
              f"rebal={rate_r:.4f} {ci_r}")

    # (c) DGP3 r=4, n=1000
    print("    (c) DGP3 r=4, n=1000:")
    n = 1000
    rej_a = 0; rej_r = 0
    for i in range(N_SIM):
        rng = np.random.default_rng(300000 + i)
        t_break = n // 2
        eps = np.empty(n)
        eps[:t_break] = rng.standard_normal(t_break)
        eps[t_break:] = rng.standard_normal(n - t_break) * 4.0
        Y = np.concatenate(([0.0], np.cumsum(eps)))
        p_a, p_r, _, _ = eval_both(Y, n, cdf_adaptive[n], cdf_rebalanced[n])
        if p_a < ALPHA: rej_a += 1
        if p_r < ALPHA: rej_r += 1
    rate_a = rej_a / N_SIM; rate_r = rej_r / N_SIM
    ci_a = ci_wilson(rate_a, N_SIM); ci_r = ci_wilson(rate_r, N_SIM)
    results["DGP3_r4_n1000"] = {
        'adaptive': rate_a, 'adaptive_ci': ci_a,
        'rebalanced': rate_r, 'rebalanced_ci': ci_r,
    }
    print(f"      adapt={rate_a:.4f} {ci_a}, rebal={rate_r:.4f} {ci_r}")

    # (d) DGP4 r=3, n=500
    print("    (d) DGP4 r=3, n=500:")
    n = 500; rho = 0.5
    rej_a = 0; rej_r = 0
    for i in range(N_SIM):
        rng = np.random.default_rng(400000 + i)
        t_break = n // 2
        eps = np.empty(n)
        eps[:t_break] = rng.standard_normal(t_break)
        eps[t_break:] = rng.standard_normal(n - t_break) * 3.0
        Y = np.empty(n + 1); Y[0] = 0.0
        for t in range(n):
            Y[t+1] = rho * Y[t] + eps[t]
        p_a, p_r, _, _ = eval_both(Y, n, cdf_adaptive[500], cdf_rebalanced[500])
        if p_a < ALPHA: rej_a += 1
        if p_r < ALPHA: rej_r += 1
    rate_a = rej_a / N_SIM; rate_r = rej_r / N_SIM
    ci_a = ci_wilson(rate_a, N_SIM); ci_r = ci_wilson(rate_r, N_SIM)
    results["DGP4_r3_n500"] = {
        'adaptive': rate_a, 'adaptive_ci': ci_a,
        'rebalanced': rate_r, 'rebalanced_ci': ci_r,
    }
    print(f"      adapt={rate_a:.4f} {ci_a}, rebal={rate_r:.4f} {ci_r}")

    # (e) R_bal distribution under H0
    print("    (e) R_bal distribution under H0:")
    for n in [200, 500, 1000]:
        Rhats_bal = np.empty(N_SIM)
        for i in range(N_SIM):
            rng = np.random.default_rng(500000 + i)
            Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(n))))
            _, _, _, rh_bal = eval_both(Y, n, cdf_adaptive[n], cdf_rebalanced[n])
            Rhats_bal[i] = rh_bal
        results[f"Rbal_H0_n{n}"] = {
            'mean': float(np.mean(Rhats_bal)),
            'q05': float(np.quantile(Rhats_bal, 0.05)),
            'q95': float(np.quantile(Rhats_bal, 0.95)),
        }
        print(f"      n={n}: mean={np.mean(Rhats_bal):.4f}, "
              f"q05={np.quantile(Rhats_bal,0.05):.4f}, "
              f"q95={np.quantile(Rhats_bal,0.95):.4f}")

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 3 total: {elapsed:.1f}s")
    results['elapsed'] = elapsed
    return results


# ======================================================================
# TASK 4 — HAC-in-calibration effect
# ======================================================================

def task4():
    """HAC estimation effect on calibration."""
    print("\n" + "=" * 70)
    print("  TASK 4 — HAC-in-calibration effect")
    print("=" * 70)
    t0 = time.perf_counter()

    N_CAL = 10000
    N_SIM = 5000
    R = 0.5
    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    results = {}

    def ci_wilson(p_hat, n_sim):
        z = 1.96
        denom = 1 + z**2/n_sim
        center = (p_hat + z**2/(2*n_sim)) / denom
        width = z * np.sqrt(p_hat*(1-p_hat)/n_sim + z**2/(4*n_sim**2)) / denom
        return [round(float(center - width), 4), round(float(center + width), 4)]

    for n in [200, 500, 1000]:
        print(f"\n  n={n}:")
        theta_1, theta_2 = THETA
        tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
        tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

        # --- Build CDF with sigma=1 (current) ---
        t_s = time.perf_counter()
        rng = np.random.default_rng(42)
        stats_sigma1 = np.empty(N_CAL)
        scale_1_exact = 1.0 * n ** (c_1 / 2.0)
        scale_2_exact = 1.0 * n ** (c_2 / 2.0)
        for j in range(N_CAL):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_std = g1_raw / scale_1_exact
            g2_std = g2_raw / scale_2_exact
            stats_sigma1[j] = np.sqrt((1-R)**2 * g1_std**2 + R**2 * g2_std**2)

        cdf_sigma1 = interp1d(np.sort(stats_sigma1),
                              np.arange(1, N_CAL+1)/N_CAL,
                              kind='linear', bounds_error=False,
                              fill_value=(0.0, 1.0))
        print(f"    CDF sigma=1: {time.perf_counter()-t_s:.1f}s")

        # --- Build CDF with HAC (variant) ---
        t_s = time.perf_counter()
        rng = np.random.default_rng(42)  # SAME seed => same paths
        stats_hac = np.empty(N_CAL)
        for j in range(N_CAL):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            diffs = np.diff(Y)
            sigma_hat_sq = hac_newey_west(diffs)
            sigma_hat = np.sqrt(sigma_hat_sq)

            scale_1_hac = sigma_hat * n ** (c_1 / 2.0)
            scale_2_hac = sigma_hat_sq * n ** (c_2 / 2.0)

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_std = g1_raw / scale_1_hac if scale_1_hac > 0 else 0.0
            g2_std = g2_raw / scale_2_hac if scale_2_hac > 0 else 0.0
            stats_hac[j] = np.sqrt((1-R)**2 * g1_std**2 + R**2 * g2_std**2)

        cdf_hac = interp1d(np.sort(stats_hac),
                           np.arange(1, N_CAL+1)/N_CAL,
                           kind='linear', bounds_error=False,
                           fill_value=(0.0, 1.0))
        print(f"    CDF HAC: {time.perf_counter()-t_s:.1f}s")

        # --- Evaluate size with fresh sims (using HAC as in production) ---
        t_s = time.perf_counter()
        rng_test = np.random.default_rng(9999)
        rej_sigma1 = 0; rej_hac = 0
        for i in range(N_SIM):
            innovations = rng_test.standard_normal(n)
            Y = np.empty(n + 1); Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])

            diffs = np.diff(Y)
            sigma_hat_sq = hac_newey_west(diffs)
            sigma_hat = np.sqrt(sigma_hat_sq)

            scale_1_prod = sigma_hat * n ** (c_1 / 2.0)
            scale_2_prod = sigma_hat_sq * n ** (c_2 / 2.0)

            means = rolling_mean(Y, tau_1)
            g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
            variances = rolling_var(Y, tau_2)
            g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

            g1_std = g1_raw / scale_1_prod if scale_1_prod > 0 else 0.0
            g2_std = g2_raw / scale_2_prod if scale_2_prod > 0 else 0.0
            stat = np.sqrt((1-R)**2 * g1_std**2 + R**2 * g2_std**2)

            p_s1 = float(np.clip(cdf_sigma1(stat), 0, 1))
            p_hac = float(np.clip(cdf_hac(stat), 0, 1))

            if p_s1 < ALPHA: rej_sigma1 += 1
            if p_hac < ALPHA: rej_hac += 1

        rate_s1 = rej_sigma1 / N_SIM
        rate_hac = rej_hac / N_SIM
        ci_s1 = ci_wilson(rate_s1, N_SIM)
        ci_hac_v = ci_wilson(rate_hac, N_SIM)

        results[f"n{n}"] = {
            'sigma1_rate': rate_s1, 'sigma1_ci': ci_s1,
            'hac_rate': rate_hac, 'hac_ci': ci_hac_v,
        }
        print(f"    sigma=1 CDF: rate={rate_s1:.4f} {ci_s1}")
        print(f"    HAC CDF:     rate={rate_hac:.4f} {ci_hac_v}")
        print(f"    eval: {time.perf_counter()-t_s:.1f}s")

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 4 total: {elapsed:.1f}s")
    results['elapsed'] = elapsed
    return results


# ======================================================================
# MAIN
# ======================================================================

if __name__ == '__main__':
    import scipy
    import statsmodels
    try:
        import arch as arch_mod
        arch_ver = arch_mod.__version__
    except Exception:
        arch_ver = "N/A"

    print("=" * 70)
    print(f"  Pre-Submission Audit — {datetime.now().isoformat()}")
    print(f"  Python {sys.version.split()[0]}")
    print(f"  NumPy {np.__version__}, SciPy {scipy.__version__}")
    print(f"  statsmodels {statsmodels.__version__}, arch {arch_ver}")
    print("=" * 70)

    r1 = task1()
    r2 = task2()
    r3 = task3()
    r4 = task4()

    # Save all results as JSON backup
    all_results = {
        'task1': r1, 'task2': r2, 'task3': r3, 'task4': r4,
        'software': {
            'python': sys.version.split()[0],
            'numpy': np.__version__,
            'scipy': scipy.__version__,
            'statsmodels': statsmodels.__version__,
            'arch': arch_ver,
        },
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    json_path = os.path.join(RESULTS_DIR, 'audit_results_audit.json')
    with open(json_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  JSON backup: {json_path}")
    print("\n  ALL TASKS COMPLETE.")
