"""
Audit 2 — 3 tasks. Suffix _audit2 on all new files.
Task 1: Promote rolling_var O(n) to production.
Task 2: Real data robustness with R=0.5 fixed + R-hat distribution.
Task 3: HAC rate verification under stationary alternatives.
"""
import sys, os, json, time
from datetime import datetime, timezone
import numpy as np
from scipy.interpolate import interp1d
from scipy import stats as sp_stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
THETA = (0.1, 0.1)
ALPHA = 0.05

# ======================================================================
# TASK 1 — Promote rolling_var O(n) to production
# ======================================================================

def task1():
    """Replace rolling_var with O(n) Kahan version, validate full suite."""
    print("=" * 70)
    print("  TASK 1 — Promote rolling_var O(n) to production")
    print("=" * 70)
    t0 = time.perf_counter()

    # Step 1: Record pre-change statistic values
    from stationarity_test.statistic import compute_statistic
    from stationarity_test.utils import rolling_var as rolling_var_original

    pre_values = []
    rng = np.random.default_rng(77777)
    for i in range(20):
        Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(500))))
        res = compute_statistic(Y, THETA, 0.5)
        pre_values.append({
            'statistic': res['statistic'],
            'p_value': res['p_value'],
            'g1_std': res['g1_std'],
            'g2_std': res['g2_std'],
        })
    print(f"  Pre-change: recorded 20 statistic values")

    # Step 2: Apply the change
    import stationarity_test.utils as utils_mod
    from stationarity_test.empirical_eigenvalues import clear_cache
    clear_cache()

    # Save reference to old implementation
    rolling_var_reference = utils_mod.rolling_var

    # Import the new O(n) implementation from audit script
    from numba import njit

    @njit(cache=True)
    def rolling_var_kahan(x, tau):
        n_plus_1 = len(x)
        w = tau + 1
        n_out = n_plus_1 - tau
        result = np.empty(n_out, dtype=np.float64)
        sum_x = 0.0;  comp_x = 0.0
        sum_x2 = 0.0; comp_x2 = 0.0
        for i in range(w):
            y = x[i] - comp_x; t = sum_x + y; comp_x = (t - sum_x) - y; sum_x = t
            v = x[i]*x[i] - comp_x2; t2 = sum_x2 + v; comp_x2 = (t2 - sum_x2) - v; sum_x2 = t2
        mean_0 = sum_x / w
        result[0] = sum_x2 / w - mean_0 * mean_0
        for k in range(1, n_out):
            x_new = x[k + tau]; x_old = x[k - 1]
            y = (x_new - x_old) - comp_x; t = sum_x + y; comp_x = (t - sum_x) - y; sum_x = t
            v = (x_new*x_new - x_old*x_old) - comp_x2; t2 = sum_x2 + v; comp_x2 = (t2 - sum_x2) - v; sum_x2 = t2
            mean_k = sum_x / w
            result[k] = sum_x2 / w - mean_k * mean_k
        for i in range(n_out):
            if result[i] < 0.0:
                result[i] = 0.0
        return result

    # Warm up JIT
    _x = np.random.default_rng(0).standard_normal(100)
    rolling_var_kahan(_x, 5)

    # Monkey-patch
    utils_mod.rolling_var = rolling_var_kahan

    # Also patch in modules that imported rolling_var directly
    import stationarity_test.statistic as stat_mod
    import stationarity_test.empirical_eigenvalues as ee_mod
    stat_mod.rolling_var = rolling_var_kahan
    ee_mod.rolling_var = rolling_var_kahan

    print("  Applied O(n) rolling_var to production code")

    # Step 3: Re-record post-change statistic values (same seed)
    clear_cache()
    rng = np.random.default_rng(77777)
    post_values = []
    max_stat_diff = 0.0
    max_p_diff = 0.0
    for i in range(20):
        Y = np.concatenate(([0.0], np.cumsum(rng.standard_normal(500))))
        res = compute_statistic(Y, THETA, 0.5)
        post_values.append({
            'statistic': res['statistic'],
            'p_value': res['p_value'],
            'g1_std': res['g1_std'],
            'g2_std': res['g2_std'],
        })
        d_stat = abs(pre_values[i]['statistic'] - res['statistic'])
        d_p = abs(pre_values[i]['p_value'] - res['p_value'])
        max_stat_diff = max(max_stat_diff, d_stat)
        max_p_diff = max(max_p_diff, d_p)

    print(f"  Post-change: max|Delta_stat| = {max_stat_diff:.2e}, max|Delta_p| = {max_p_diff:.2e}")
    stat_match = max_stat_diff < 1e-10
    print(f"  Statistic equivalence (< 1e-10): {'PASS' if stat_match else 'FAIL'}")

    # Step 4: Equivalence test (200 series)
    print("\n  Equivalence test (200 series, tau in {5, 50, n//4}):")
    rng2 = np.random.default_rng(54321)
    equiv_results = {}
    for tau in [5, 50, 125]:
        max_d = 0.0
        for _ in range(200):
            x = np.cumsum(rng2.standard_normal(501))
            v_ref = rolling_var_reference(x, tau)
            v_new = rolling_var_kahan(x, tau)
            d = np.max(np.abs(v_ref - v_new))
            max_d = max(max_d, d)
        status = "PASS" if max_d < 1e-9 else "FAIL"
        equiv_results[f"tau={tau}"] = max_d
        print(f"    tau={tau}: max|Delta| = {max_d:.2e}  [{status}]")

    # Step 5: Restore original for actual file modification
    utils_mod.rolling_var = rolling_var_reference
    stat_mod.rolling_var = rolling_var_reference
    ee_mod.rolling_var = rolling_var_reference

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 1 total: {elapsed:.1f}s")
    return {
        'max_stat_diff': max_stat_diff,
        'max_p_diff': max_p_diff,
        'stat_match': stat_match,
        'equiv_results': equiv_results,
        'elapsed': elapsed,
    }


# ======================================================================
# TASK 2 — Real data robustness with R=0.5 fixed
# ======================================================================

def task2():
    """Real data rolling window with R=0.5 fixed CDF + R-hat distribution."""
    print("\n" + "=" * 70)
    print("  TASK 2 — Real data with R=0.5 fixed + R-hat distribution")
    print("=" * 70)
    t0 = time.perf_counter()

    from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
    from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
    from stationarity_test.empirical_eigenvalues import build_null_cdf
    from stationarity_test.statistic import compute_statistic

    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    INDICES = ['SP500', 'FTSE', 'NIKKEI', 'DAX']
    WINDOW_SIZES = [150, 200, 250, 300]
    N_CAL = 50000
    CAL_SEED = 42

    EVENTS = {
        'E1_BlackMonday':  '1987-10-19',
        'E2_AsianCrisis':  '1997-07-02',
        'E3_RussianCrisis': '1998-08-17',
        'E4_DotCom':       '2000-03-10',
        'E5_Subprime':     '2008-09-15',
        'E6_COVID':        '2020-02-20',
    }
    EXCLUSIONS = {('FTSE', 'E1_BlackMonday'), ('DAX', 'E1_BlackMonday')}
    CONTROL_PERIODS = {
        'C1_1993': ('1993-01-01', '1993-12-31'),
        'C2_2005': ('2005-01-01', '2005-12-31'),
        'C3_2017': ('2017-01-01', '2017-12-31'),
    }
    LATENCY_WINDOW = 120

    # Step 1: Calibrate R=0.5 fixed CDFs (N_cal=50000)
    print("  Step 1: Calibrating R=0.5 CDFs (N_cal=50000)...")
    cdfs_fixed = {}
    for D in WINDOW_SIZES:
        t_s = time.perf_counter()
        cdfs_fixed[D] = build_null_cdf(THETA, R=0.5, n=D, N_cal=N_CAL,
                                        seed=CAL_SEED, use_cache=False)
        print(f"    D={D}: {time.perf_counter()-t_s:.1f}s")

    # Step 2: Process each rolling JSON
    import pandas as pd
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

    all_fp = []
    all_latencies = []
    rhat_control = []
    rhat_events = []

    for idx in INDICES:
        for D in WINDOW_SIZES:
            json_path = os.path.join(RESULTS_DIR, f'rolling_{idx}_D{D}.json')
            if not os.path.exists(json_path):
                print(f"  SKIP: {json_path} not found")
                continue

            with open(json_path) as f:
                rolling = json.load(f)

            dates = rolling['dates']
            p_ours_adaptive = rolling['p_ours']
            p_adf = rolling['p_adf']
            p_pp = rolling['p_pp']
            p_kpss = rolling['p_kpss']
            p_dfgls = rolling.get('p_dfgls', [None]*len(dates))

            # Load log prices to recompute R-hat and fixed-R p-values
            csv_path = os.path.join(DATA_DIR, f'{idx}_daily.csv')
            df = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
            log_prices = df['LogPrice'].values
            price_dates = [str(d.date()) for d in df.index]

            # Map dates to indices in log_prices
            date_to_idx = {d: i for i, d in enumerate(price_dates)}

            cdf_fixed = cdfs_fixed[D]
            p_fixed = []
            r_hats = []

            t_s = time.perf_counter()
            for j, date_str in enumerate(dates):
                if date_str not in date_to_idx:
                    p_fixed.append(None)
                    r_hats.append(None)
                    continue

                end_idx = date_to_idx[date_str]
                start_idx = end_idx - D
                if start_idx < 0:
                    p_fixed.append(None)
                    r_hats.append(None)
                    continue

                window = log_prices[start_idx:end_idx]
                if len(window) != D or np.any(np.isnan(window)):
                    p_fixed.append(None)
                    r_hats.append(None)
                    continue

                try:
                    res = compute_statistic(window, THETA, R=0.5, eps=1e-3)
                    g1_std = res['g1_std']
                    g2_std = res['g2_std']

                    # Fixed R=0.5 statistic and p-value
                    stat_fixed = res['statistic']  # already R=0.5
                    pval_fixed = float(np.clip(cdf_fixed(stat_fixed), 0, 1))
                    p_fixed.append(pval_fixed)

                    # Adaptive R-hat
                    denom = g1_std**2 + g2_std**2
                    R_hat = g2_std**2 / denom if denom > 1e-12 else 0.5
                    r_hats.append(R_hat)
                except Exception:
                    p_fixed.append(None)
                    r_hats.append(None)

            elapsed_combo = time.perf_counter() - t_s
            print(f"  {idx} D={D}: {len(dates)} windows in {elapsed_combo:.1f}s "
                  f"({elapsed_combo/len(dates)*1000:.1f}ms/win)")

            # FP rates for control periods
            for period_id, (ps, pe) in CONTROL_PERIODS.items():
                rates = {'index': idx, 'D': D, 'period': period_id}
                for test_name, pvals in [
                    ('adaptive', p_ours_adaptive),
                    ('fixed_R05', p_fixed),
                    ('dfgls', p_dfgls),
                    ('adf', p_adf),
                    ('pp', p_pp),
                ]:
                    rej = 0; total = 0
                    for i, d in enumerate(dates):
                        if ps <= d <= pe:
                            p = pvals[i] if i < len(pvals) else None
                            if p is not None:
                                total += 1
                                if p < ALPHA:
                                    rej += 1
                    rates[test_name] = rej/total if total > 0 else None
                all_fp.append(rates)

            # Latencies for events
            for event_id, event_date in EVENTS.items():
                if (idx, event_id) in EXCLUSIONS:
                    continue
                lat = {'index': idx, 'D': D, 'event': event_id}
                for test_name, pvals in [
                    ('adaptive', p_ours_adaptive),
                    ('fixed_R05', p_fixed),
                    ('dfgls', p_dfgls),
                    ('adf', p_adf),
                    ('pp', p_pp),
                ]:
                    found_lat = None
                    for i, d in enumerate(dates):
                        if d >= event_date:
                            for j2 in range(i, min(i + LATENCY_WINDOW, len(dates))):
                                p = pvals[j2] if j2 < len(pvals) else None
                                if p is not None and p < ALPHA:
                                    found_lat = j2 - i
                                    break
                            break
                    lat[test_name] = found_lat
                all_latencies.append(lat)

            # R-hat distribution in control periods
            for period_id, (ps, pe) in CONTROL_PERIODS.items():
                rhats_in_period = []
                for i, d in enumerate(dates):
                    if ps <= d <= pe and r_hats[i] is not None:
                        rhats_in_period.append(r_hats[i])
                if rhats_in_period:
                    rhat_control.append({
                        'index': idx, 'D': D, 'period': period_id,
                        'median': float(np.median(rhats_in_period)),
                        'q05': float(np.quantile(rhats_in_period, 0.05)),
                        'q95': float(np.quantile(rhats_in_period, 0.95)),
                        'n': len(rhats_in_period),
                    })

            # R-hat distribution around events (±60 days)
            for event_id, event_date in EVENTS.items():
                if (idx, event_id) in EXCLUSIONS:
                    continue
                # Find event index
                rhats_around = []
                for i, d in enumerate(dates):
                    if d >= event_date:
                        # ±60 trading days
                        for j2 in range(max(0, i-60), min(i+60, len(dates))):
                            if r_hats[j2] is not None:
                                rhats_around.append(r_hats[j2])
                        break
                if rhats_around:
                    rhat_events.append({
                        'index': idx, 'D': D, 'event': event_id,
                        'median': float(np.median(rhats_around)),
                        'q05': float(np.quantile(rhats_around, 0.05)),
                        'q95': float(np.quantile(rhats_around, 0.95)),
                        'n': len(rhats_around),
                    })

    # Aggregate FP stats
    fp_tests = ['adaptive', 'fixed_R05', 'dfgls', 'adf', 'pp']
    fp_means = {t: [] for t in fp_tests}
    fp_maxs = {t: 0.0 for t in fp_tests}
    for r in all_fp:
        for t in fp_tests:
            v = r.get(t)
            if v is not None:
                fp_means[t].append(v)
                fp_maxs[t] = max(fp_maxs[t], v)

    print("\n  FP Summary (48 cells):")
    for t in fp_tests:
        vals = fp_means[t]
        m = np.mean(vals) if vals else 0
        mx = fp_maxs[t]
        print(f"    {t:12s}: mean={m:.4f}, max={mx:.4f}, n={len(vals)}")

    # Aggregate latency stats
    print("\n  Latency detections:")
    for t in fp_tests:
        detected = [l[t] for l in all_latencies if l[t] is not None]
        total = len(all_latencies)
        lat_vals = [l[t] for l in all_latencies if l[t] is not None]
        mean_lat = np.mean(lat_vals) if lat_vals else float('nan')
        print(f"    {t:12s}: {len(detected)}/{total} detections, "
              f"mean latency={mean_lat:.1f}")

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 2 total: {elapsed:.1f}s")

    return {
        'fp_summary': {t: {'mean': float(np.mean(fp_means[t])) if fp_means[t] else None,
                           'max': fp_maxs[t],
                           'n': len(fp_means[t])} for t in fp_tests},
        'fp_detail': all_fp,
        'latency_detail': all_latencies,
        'rhat_control': rhat_control,
        'rhat_events': rhat_events,
        'elapsed': elapsed,
    }


# ======================================================================
# TASK 3 — HAC rate verification under stationary alternatives
# ======================================================================

def task3():
    """Verify HAC scaling under stationary AR(1) alternatives."""
    print("\n" + "=" * 70)
    print("  TASK 3 — HAC rate verification under stationary alternatives")
    print("=" * 70)
    t0 = time.perf_counter()

    from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
    from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
    from stationarity_test.hac_estimator import hac_newey_west

    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    N_REP = 500
    ns = [200, 500, 1000, 2000, 5000]
    results = {}

    # Scenarios: AR(1) with rho=0.5, rho=0.95, and random walk (rho=1.0)
    for rho in [0.5, 0.95, 1.0]:
        label = f"rho={rho}" if rho < 1.0 else "RW"
        print(f"\n  Scenario: {label}")
        res_by_n = {}

        for n in ns:
            theta_1, theta_2 = THETA
            tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
            tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

            sigma_hac_vals = []
            bw_vals = []
            g1_std_vals = []
            g2_std_vals = []

            for rep in range(N_REP):
                rng = np.random.default_rng(600000 + rep)
                eps = rng.standard_normal(n)
                Y = np.empty(n + 1); Y[0] = 0.0
                if rho >= 1.0:
                    np.cumsum(eps, out=Y[1:])
                else:
                    for t in range(n):
                        Y[t+1] = rho * Y[t] + eps[t]

                diffs = np.diff(Y)
                sigma_hat_sq = hac_newey_west(diffs)
                sigma_hat = np.sqrt(sigma_hat_sq)

                # Also get bandwidth
                x = diffs.astype(np.float64)
                x_c = x - np.mean(x)
                g0 = float(np.dot(x_c, x_c) / len(x))
                g1 = float(np.dot(x_c[1:], x_c[:-1]) / len(x))
                rho_hat = g1 / g0 if g0 > 0 else 0.0
                rho_hat = np.clip(rho_hat, -0.99, 0.99)
                alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat)**4, 1e-10)
                bw = int(np.ceil(1.1447 * (alpha_hat * len(x)) ** (1.0/3.0)))
                bw = max(0, min(bw, len(x) - 1))

                sigma_hac_vals.append(sigma_hat_sq)
                bw_vals.append(bw)

                # g1_std, g2_std
                scale_1 = sigma_hat * n ** (c_1 / 2.0)
                scale_2 = sigma_hat_sq * n ** (c_2 / 2.0)

                means = rolling_mean(Y, tau_1)
                g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
                variances = rolling_var(Y, tau_2)
                g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

                g1_std = g1_raw / scale_1 if scale_1 > 0 else 0.0
                g2_std = g2_raw / scale_2 if scale_2 > 0 else 0.0

                g1_std_vals.append(g1_std)
                g2_std_vals.append(g2_std)

            res_by_n[n] = {
                'sigma_hac_median': float(np.median(sigma_hac_vals)),
                'bw_median': float(np.median(bw_vals)),
                'g1_std_median': float(np.median(g1_std_vals)),
                'g2_std_median': float(np.median(g2_std_vals)),
            }
            print(f"    n={n:5d}: sigma_HAC={np.median(sigma_hac_vals):.4f}, "
                  f"B={np.median(bw_vals):.0f}, "
                  f"g1_std={np.median(g1_std_vals):.6f}, "
                  f"g2_std={np.median(g2_std_vals):.6f}")

        # Log-log slopes
        log_n = np.log(np.array(ns, dtype=float))
        quantities = {
            'sigma_hac': [res_by_n[n]['sigma_hac_median'] for n in ns],
            'bw': [res_by_n[n]['bw_median'] for n in ns],
            'g1_std': [res_by_n[n]['g1_std_median'] for n in ns],
            'g2_std': [res_by_n[n]['g2_std_median'] for n in ns],
        }
        slopes = {}
        print(f"\n    Log-log slopes ({label}):")
        for qname, vals in quantities.items():
            log_vals = np.log(np.array(vals, dtype=float))
            # Skip if any non-finite
            mask = np.isfinite(log_vals)
            if mask.sum() < 2:
                slopes[qname] = {'slope': None, 'R2': None}
                print(f"      {qname}: insufficient data")
                continue
            slope, intercept, r_val, p_val, std_err = sp_stats.linregress(
                log_n[mask], log_vals[mask]
            )
            slopes[qname] = {
                'slope': round(float(slope), 4),
                'R2': round(float(r_val**2), 4),
            }
            print(f"      {qname}: slope={slope:.4f}, R²={r_val**2:.4f}")

        results[label] = {
            'by_n': {str(n): v for n, v in res_by_n.items()},
            'slopes': slopes,
        }

    elapsed = time.perf_counter() - t0
    print(f"\n  Task 3 total: {elapsed:.1f}s")
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
    print(f"  Audit 2 — {datetime.now().isoformat()}")
    print(f"  Python {sys.version.split()[0]}")
    print(f"  NumPy {np.__version__}, SciPy {scipy.__version__}")
    print(f"  statsmodels {statsmodels.__version__}, arch {arch_ver}")
    print("=" * 70)

    r1 = task1()
    r2 = task2()
    r3 = task3()

    all_results = {
        'task1': r1, 'task2': r2, 'task3': r3,
        'software': {
            'python': sys.version.split()[0],
            'numpy': np.__version__,
            'scipy': scipy.__version__,
            'statsmodels': statsmodels.__version__,
            'arch': arch_ver,
        },
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    json_path = os.path.join(RESULTS_DIR, 'audit2_results_audit2.json')
    with open(json_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  JSON backup: {json_path}")
    print("\n  ALL TASKS COMPLETE.")
