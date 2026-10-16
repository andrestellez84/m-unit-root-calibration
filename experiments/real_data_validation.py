"""
Phase 5 — Real data validation: rolling window analysis.

Implements Algorithm F5.2 from the protocol:
- Rolling window stationarity test + ADF + PP + KPSS
- Latency computation for pre-specified events
- False positive rate for control periods
- Incremental checkpoints per (index, D)

Usage:
    python -u experiments/real_data_validation.py [INDEX] [D]
    python -u experiments/real_data_validation.py           # all combinations
    python -u experiments/real_data_validation.py SP500 200 # single combo
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stationarity_test.statistic import compute_statistic
from stationarity_test.empirical_eigenvalues import build_null_cdf_adaptive

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
CHECKPOINTS_DIR = os.path.join(RESULTS_DIR, 'checkpoints')

# ======================================================================
# Protocol configuration (from protocol.md)
# ======================================================================

INDICES = ['SP500', 'FTSE', 'NIKKEI', 'DAX']
WINDOW_SIZES = [150, 200, 250, 300]
THETA = (0.1, 0.1)
ALPHA = 0.05
CAL_SEED = 42

# Pre-specified events (date strings)
EVENTS = {
    'E1_BlackMonday':  '1987-10-19',
    'E2_AsianCrisis':  '1997-07-02',
    'E3_RussianCrisis': '1998-08-17',
    'E4_DotCom':       '2000-03-10',
    'E5_Subprime':     '2008-09-15',
    'E6_COVID':        '2020-02-20',
}

# Pre-specified exclusions (from protocol.md §7, verified)
EXCLUSIONS = {
    ('FTSE', 'E1_BlackMonday'),   # No reliable data before 1988
    ('DAX', 'E1_BlackMonday'),    # DAX officially from 1988-07-01
}

# Control periods for false positive rate
CONTROL_PERIODS = {
    'C1_1993': ('1993-01-01', '1993-12-31'),
    'C2_2005': ('2005-01-01', '2005-12-31'),
    'C3_2017': ('2017-01-01', '2017-12-31'),
}

# Latency search window: up to 120 trading days after event
LATENCY_WINDOW = 120


def load_log_prices(index_name):
    """Load pre-computed log prices from frozen CSV."""
    csv_path = os.path.join(DATA_DIR, f'{index_name}_daily.csv')
    df = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
    return df['LogPrice']


def run_adf(window):
    """Run ADF test, return p-value."""
    from statsmodels.tsa.stattools import adfuller
    try:
        result = adfuller(window, autolag='AIC')
        return result[1]  # p-value
    except Exception:
        return np.nan


def run_pp(window):
    """Run Phillips-Perron test, return p-value."""
    from arch.unitroot import PhillipsPerron
    try:
        result = PhillipsPerron(window, lags=None)
        return result.pvalue
    except Exception:
        return np.nan


def run_kpss(window):
    """Run KPSS test, return p-value (H0: stationarity)."""
    import warnings
    from statsmodels.tsa.stattools import kpss
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stat, pvalue, lags, crit = kpss(window, regression='c', nlags='auto')
        return pvalue
    except Exception:
        return np.nan


def run_rolling_analysis(index_name, D, cdf_adaptive, pilot="alpha1"):
    """
    Run rolling window analysis for one (index, D) combination.

    Uses compute_statistic for sigma-hat normalization, adaptive R,
    and pre-calibrated adaptive CDF for fast p-value evaluation.
    Returns dict with rolling p-values and metadata.
    """
    log_prices = load_log_prices(index_name)
    n_total = len(log_prices)

    print(f"  Rolling analysis: {index_name}, D={D}, "
          f"n_total={n_total}, windows={n_total - D}, pilot={pilot}")

    dates = []
    p_ours = []
    p_adf = []
    p_pp = []
    p_kpss = []

    t0 = time.time()
    n_windows = n_total - D

    for i in range(D, n_total):
        window = log_prices.iloc[i - D:i].values

        # Skip if window has NaN
        if np.any(np.isnan(window)):
            continue

        date_str = str(log_prices.index[i].date())
        dates.append(date_str)

        # Our test (adaptive R with pre-calibrated adaptive CDF)
        try:
            # compute_statistic estimates sigma_hat and normalizes g1/g2
            result = compute_statistic(
                window, THETA, R=0.5, eps=1e-3, andrews_pilot=pilot
            )
            g1_std = result['g1_std']
            g2_std = result['g2_std']

            # Adaptive weight (same formula as calibrator)
            denom = g1_std**2 + g2_std**2
            if denom > 1e-12:
                R_hat = g2_std**2 / denom
            else:
                R_hat = 0.5

            # Combined statistic with CORRECT formula matching calibrator
            # sqrt((1-R)^2 * g1^2 + R^2 * g2^2)
            stat_adaptive = np.sqrt(
                (1 - R_hat)**2 * g1_std**2 + R_hat**2 * g2_std**2
            )

            # p-value from pre-calibrated adaptive CDF
            p = float(cdf_adaptive(stat_adaptive))
            p_ours.append(p)
        except Exception:
            p_ours.append(np.nan)

        # Baselines
        p_adf.append(run_adf(window))
        p_pp.append(run_pp(window))
        p_kpss.append(run_kpss(window))

        # Progress every 500 windows
        if (i - D) % 500 == 0 and i > D:
            elapsed = time.time() - t0
            pct = (i - D) / n_windows * 100
            eta = elapsed / (i - D) * (n_windows - (i - D))
            print(f"    [{i-D:5d}/{n_windows}] {pct:5.1f}% "
                  f"elapsed={elapsed:.0f}s ETA={eta:.0f}s "
                  f"date={date_str}")

    elapsed = time.time() - t0
    print(f"    Done: {len(dates)} windows in {elapsed:.1f}s "
          f"({elapsed/len(dates)*1000:.1f}ms/window)")

    return {
        'index': index_name,
        'D': D,
        'theta': list(THETA),
        'alpha': ALPHA,
        'n_windows': len(dates),
        'dates': dates,
        'p_ours': [float(x) if not np.isnan(x) else None for x in p_ours],
        'p_adf': [float(x) if not np.isnan(x) else None for x in p_adf],
        'p_pp': [float(x) if not np.isnan(x) else None for x in p_pp],
        'p_kpss': [float(x) if not np.isnan(x) else None for x in p_kpss],
    }


def compute_latency(rolling_result, event_date_str):
    """
    Compute latency: trading days from event to first rejection.

    Returns int (days) or None if no rejection within LATENCY_WINDOW.
    """
    dates = rolling_result['dates']
    latencies = {}

    for test_name, p_values in [
        ('ours', rolling_result['p_ours']),
        ('adf', rolling_result['p_adf']),
        ('pp', rolling_result['p_pp']),
        ('kpss', rolling_result['p_kpss']),
    ]:
        # Find first date after event
        found = False
        for i, d in enumerate(dates):
            if d >= event_date_str:
                # Search within LATENCY_WINDOW trading days
                for j in range(i, min(i + LATENCY_WINDOW, len(dates))):
                    p = p_values[j]
                    if p is not None:
                        # For KPSS: reject stationarity when p < alpha
                        # For others: reject unit root when p < alpha
                        if p < ALPHA:
                            latencies[test_name] = j - i
                            found = True
                            break
                if not found:
                    latencies[test_name] = None
                break
        if test_name not in latencies:
            latencies[test_name] = None

    return latencies


def compute_false_positive_rate(rolling_result, period_start, period_end):
    """Compute false positive rate during a control period."""
    dates = rolling_result['dates']
    rates = {}

    for test_name, p_values in [
        ('ours', rolling_result['p_ours']),
        ('adf', rolling_result['p_adf']),
        ('pp', rolling_result['p_pp']),
        ('kpss', rolling_result['p_kpss']),
    ]:
        rejections = 0
        total = 0
        for i, d in enumerate(dates):
            if period_start <= d <= period_end:
                p = p_values[i]
                if p is not None:
                    total += 1
                    if p < ALPHA:
                        rejections += 1
        rates[test_name] = rejections / total if total > 0 else None

    return rates


def save_checkpoint(rolling_result, index_name, D, suffix=""):
    """Save checkpoint for one (index, D) combination."""
    if suffix == "":
        raise RuntimeError("Esta sesión exige --suffix no vacío; no se sobrescribe el pre-registro.")
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    path = os.path.join(CHECKPOINTS_DIR, f'{index_name}_D{D}{suffix}.json')

    # Don't save full rolling p-values in checkpoint (too large)
    # Save summary + latencies + FP rates
    checkpoint = {
        'index': index_name,
        'D': D,
        'n_windows': rolling_result['n_windows'],
        'first_date': rolling_result['dates'][0] if rolling_result['dates'] else None,
        'last_date': rolling_result['dates'][-1] if rolling_result['dates'] else None,
        'completed_at': datetime.utcnow().isoformat(),
    }

    # Compute latencies for all events
    latencies = {}
    for event_id, event_date in EVENTS.items():
        if (index_name, event_id) in EXCLUSIONS:
            latencies[event_id] = {'excluded': True, 'reason': 'data_availability'}
            continue
        latencies[event_id] = compute_latency(rolling_result, event_date)
    checkpoint['latencies'] = latencies

    # Compute false positive rates for control periods
    fp_rates = {}
    for period_id, (start, end) in CONTROL_PERIODS.items():
        fp_rates[period_id] = compute_false_positive_rate(
            rolling_result, start, end
        )
    checkpoint['false_positive_rates'] = fp_rates

    with open(path, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    print(f"  Checkpoint saved: {path}")
    return checkpoint


def save_rolling_pvalues(rolling_result, index_name, D, suffix=""):
    """Save full rolling p-values for plotting."""
    if suffix == "":
        raise RuntimeError("Esta sesión exige --suffix no vacío; no se sobrescribe el pre-registro.")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f'rolling_{index_name}_D{D}{suffix}.json')
    with open(path, 'w') as f:
        json.dump(rolling_result, f)
    print(f"  Rolling p-values saved: {path}")


def main():
    parser = argparse.ArgumentParser(
        description='Rolling window real data validation.'
    )
    parser.add_argument('index', nargs='?', default=None,
                        help='Index name (SP500, FTSE, NIKKEI, DAX)')
    parser.add_argument('window', nargs='?', type=int, default=None,
                        help='Window size D')
    parser.add_argument('--n-cal', type=int, default=10000,
                        help='Number of calibration simulations (default: 10000)')
    parser.add_argument('--pilot', type=str, default='alpha1', choices=['alpha1', 'alpha2'],
                        help='Andrews pilot formula (default: alpha1)')
    parser.add_argument('--suffix', type=str, default='', required=True,
                        help='Output suffix for checkpoints and results (required, non-empty)')
    args = parser.parse_args()

    if not args.suffix:
        raise RuntimeError("Esta sesión exige --suffix no vacío; no se sobrescribe el pre-registro.")

    suffix = args.suffix
    n_cal = args.n_cal
    pilot = args.pilot

    # Determine which combinations to run
    if args.index and args.window:
        combos = [(args.index, args.window)]
    elif args.index:
        combos = [(args.index, D) for D in WINDOW_SIZES]
    else:
        combos = [(idx, D) for idx in INDICES for D in WINDOW_SIZES]

    print("=" * 70)
    print("  Real Data Validation — Rolling Window Analysis")
    print(f"  Combinations: {len(combos)}")
    print(f"  Theta: {THETA}, Alpha: {ALPHA}")
    print(f"  Pilot: {pilot}, Suffix: {suffix}")
    print(f"  Using pre-calibrated adaptive CDF (N_cal={n_cal})")
    print("=" * 70)

    # Pre-calibrate adaptive CDFs for each window size
    cdfs = {}
    for D in sorted(set(d for _, d in combos)):
        print(f"\n  Calibrating adaptive CDF for D={D} "
              f"(N_cal={n_cal}, seed={CAL_SEED})...")
        t0 = time.time()
        cdfs[D] = build_null_cdf_adaptive(THETA, D, n_cal, CAL_SEED)
        print(f"    Done in {time.time()-t0:.1f}s")

    # Run rolling analysis for each combination
    all_checkpoints = []
    for combo_idx, (index_name, D) in enumerate(combos):
        print(f"\n{'='*70}")
        print(f"  [{combo_idx+1}/{len(combos)}] {index_name}, D={D}")
        print(f"{'='*70}")

        # Check if checkpoint already exists
        cp_path = os.path.join(CHECKPOINTS_DIR, f'{index_name}_D{D}{suffix}.json')
        if os.path.exists(cp_path):
            print(f"  Checkpoint exists, skipping. Delete to re-run.")
            with open(cp_path) as f:
                all_checkpoints.append(json.load(f))
            continue

        # Run analysis
        rolling = run_rolling_analysis(index_name, D, cdfs[D], pilot=pilot)

        # Save checkpoint and rolling data
        checkpoint = save_checkpoint(rolling, index_name, D, suffix=suffix)
        save_rolling_pvalues(rolling, index_name, D, suffix=suffix)
        all_checkpoints.append(checkpoint)

    # Aggregate results
    print(f"\n{'='*70}")
    print("  RESULTS SUMMARY")
    print(f"{'='*70}")

    # Latency table
    print("\n  Latency (trading days to first rejection):")
    print(f"  {'Event':<20s} {'Index':<8s} {'D':>4s} "
          f"{'Ours':>6s} {'ADF':>6s} {'PP':>6s} {'KPSS':>6s}")
    print("  " + "-" * 60)

    def fmt_lat(v):
        """Format latency value: int or '-' for None."""
        if v is None:
            return "    -"
        return f"{v:5d}"

    for cp in all_checkpoints:
        for event_id, lat in cp.get('latencies', {}).items():
            if isinstance(lat, dict) and lat.get('excluded'):
                continue
            if lat is None:
                continue
            print(f"  {event_id:<20s} {cp['index']:<8s} {cp['D']:>4d} "
                  f"{fmt_lat(lat.get('ours'))} "
                  f"{fmt_lat(lat.get('adf'))} "
                  f"{fmt_lat(lat.get('pp'))} "
                  f"{fmt_lat(lat.get('kpss'))}")

    # False positive table
    print("\n  False positive rates (control periods):")
    print(f"  {'Period':<12s} {'Index':<8s} {'D':>4s} "
          f"{'Ours':>8s} {'ADF':>8s} {'PP':>8s} {'KPSS':>8s}")
    print("  " + "-" * 60)

    def fmt_fp(v):
        """Format false positive rate."""
        if v is None:
            return "     N/A"
        return f"{v:8.3f}"

    for cp in all_checkpoints:
        for period_id, rates in cp.get('false_positive_rates', {}).items():
            if rates is None:
                continue
            print(f"  {period_id:<12s} {cp['index']:<8s} {cp['D']:>4d} "
                  f"{fmt_fp(rates.get('ours'))} "
                  f"{fmt_fp(rates.get('adf'))} "
                  f"{fmt_fp(rates.get('pp'))} "
                  f"{fmt_fp(rates.get('kpss'))}")

    # Save aggregated results
    agg_path = os.path.join(RESULTS_DIR, f'real_data_results{suffix}.json')
    with open(agg_path, 'w') as f:
        json.dump({
            'completed_at': datetime.utcnow().isoformat(),
            'checkpoints': all_checkpoints,
        }, f, indent=2)
    print(f"\n  Aggregated results: {agg_path}")


if __name__ == '__main__':
    main()
