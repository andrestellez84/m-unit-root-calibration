"""
Add DF-GLS to the real data rolling window analysis.

Re-runs the 16 (index, D) combinations, computing ONLY DF-GLS p-values
(ADF/PP/KPSS/Ours are loaded from existing rolling_*.json files).
Updates checkpoints with DF-GLS latencies and FP rates.
"""

import sys, os, json, time, warnings
from datetime import datetime
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from arch.unitroot import DFGLS

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
CHECKPOINTS_DIR = os.path.join(RESULTS_DIR, 'checkpoints')

INDICES = ['SP500', 'FTSE', 'NIKKEI', 'DAX']
WINDOW_SIZES = [150, 200, 250, 300]
ALPHA = 0.05

EVENTS = {
    'E1_BlackMonday':  '1987-10-19',
    'E2_AsianCrisis':  '1997-07-02',
    'E3_RussianCrisis': '1998-08-17',
    'E4_DotCom':       '2000-03-10',
    'E5_Subprime':     '2008-09-15',
    'E6_COVID':        '2020-02-20',
}

EXCLUSIONS = {
    ('FTSE', 'E1_BlackMonday'),
    ('DAX', 'E1_BlackMonday'),
}

CONTROL_PERIODS = {
    'C1_1993': ('1993-01-01', '1993-12-31'),
    'C2_2005': ('2005-01-01', '2005-12-31'),
    'C3_2017': ('2017-01-01', '2017-12-31'),
}

LATENCY_WINDOW = 120


def load_log_prices(index_name):
    csv_path = os.path.join(DATA_DIR, f'{index_name}_daily.csv')
    df = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
    return df['LogPrice']


def run_dfgls(window):
    try:
        return DFGLS(window, trend='c').pvalue
    except Exception:
        return np.nan


def compute_latency_single(dates, p_values, event_date_str):
    for i, d in enumerate(dates):
        if d >= event_date_str:
            for j in range(i, min(i + LATENCY_WINDOW, len(dates))):
                p = p_values[j]
                if p is not None and not np.isnan(p) and p < ALPHA:
                    return j - i
            return None
    return None


def compute_fp_rate_single(dates, p_values, period_start, period_end):
    rej = 0
    total = 0
    for i, d in enumerate(dates):
        if period_start <= d <= period_end:
            p = p_values[i]
            if p is not None and not np.isnan(p):
                total += 1
                if p < ALPHA:
                    rej += 1
    return rej / total if total > 0 else None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Add DF-GLS to rolling window analysis')
    parser.add_argument('--suffix', type=str, default='', help='Suffix for checkpoints and rolling data')
    args = parser.parse_args()
    suffix = args.suffix

    print("=" * 70)
    print("  Real Data: Adding DF-GLS to rolling window analysis")
    print(f"  16 combinations: {len(INDICES)} indices x {len(WINDOW_SIZES)} windows")
    if suffix:
        print(f"  Suffix: {suffix}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    combos = [(idx, D) for idx in INDICES for D in WINDOW_SIZES]
    all_results = []

    for combo_idx, (index_name, D) in enumerate(combos):
        print(f"\n  [{combo_idx+1}/16] {index_name}, D={D}")

        # Load existing rolling data for dates
        rolling_path = os.path.join(RESULTS_DIR, f'rolling_{index_name}_D{D}{suffix}.json')
        if not os.path.exists(rolling_path):
            print(f"    SKIP: {rolling_path} not found")
            continue

        with open(rolling_path) as f:
            rolling = json.load(f)

        dates = rolling['dates']
        log_prices = load_log_prices(index_name)
        n_total = len(log_prices)

        # Compute DF-GLS p-values
        t0 = time.time()
        p_dfgls = []

        for i in range(D, n_total):
            window = log_prices.iloc[i - D:i].values
            if np.any(np.isnan(window)):
                continue
            p_dfgls.append(run_dfgls(window))

        elapsed = time.time() - t0
        print(f"    {len(p_dfgls)} windows in {elapsed:.1f}s "
              f"({elapsed/len(p_dfgls)*1000:.1f}ms/win)")

        # Verify alignment
        assert len(p_dfgls) == len(dates), \
            f"Mismatch: {len(p_dfgls)} vs {len(dates)}"

        # Save DF-GLS p-values into rolling data
        rolling['p_dfgls'] = [float(x) if not np.isnan(x) else None
                              for x in p_dfgls]
        with open(rolling_path, 'w') as f:
            json.dump(rolling, f)

        # Compute latencies
        latencies = {}
        for eid, edate in EVENTS.items():
            if (index_name, eid) in EXCLUSIONS:
                latencies[eid] = None
                continue
            latencies[eid] = compute_latency_single(dates, p_dfgls, edate)

        # Compute FP rates
        fp_rates = {}
        for pid, (start, end) in CONTROL_PERIODS.items():
            fp_rates[pid] = compute_fp_rate_single(dates, p_dfgls, start, end)

        # Update checkpoint
        cp_path = os.path.join(CHECKPOINTS_DIR, f'{index_name}_D{D}{suffix}.json')
        with open(cp_path) as f:
            cp = json.load(f)

        # Add dfgls to latencies
        for eid in EVENTS:
            if isinstance(cp['latencies'].get(eid), dict) and \
               cp['latencies'][eid].get('excluded'):
                continue
            if cp['latencies'].get(eid) is not None:
                cp['latencies'][eid]['dfgls'] = latencies.get(eid)
            else:
                cp['latencies'][eid] = {'dfgls': latencies.get(eid)}

        # Add dfgls to FP rates
        for pid in CONTROL_PERIODS:
            if cp['false_positive_rates'].get(pid) is not None:
                cp['false_positive_rates'][pid]['dfgls'] = fp_rates.get(pid)

        cp['dfgls_added_at'] = datetime.utcnow().isoformat()
        with open(cp_path, 'w') as f:
            json.dump(cp, f, indent=2)

        all_results.append({
            'index': index_name, 'D': D,
            'latencies': latencies, 'fp_rates': fp_rates
        })

        # Print FP rates
        for pid, rate in fp_rates.items():
            other = cp['false_positive_rates'][pid]
            print(f"    {pid}: DFGLS={rate:.3f}  "
                  f"Ours={other.get('ours', '?'):.3f}  "
                  f"ADF={other.get('adf', '?'):.3f}")

    # Summary
    print(f"\n{'=' * 70}")
    print("  SUMMARY: DF-GLS FP rates vs others")
    print(f"{'=' * 70}")

    fp_dfgls_all = []
    fp_ours_all = []
    fp_adf_all = []
    for r in all_results:
        for pid, rate in r['fp_rates'].items():
            if rate is not None:
                fp_dfgls_all.append(rate)

    # Reload all checkpoints for comparison
    for idx in INDICES:
        for D in WINDOW_SIZES:
            cp_path = os.path.join(CHECKPOINTS_DIR, f'{idx}_D{D}{suffix}.json')
            if os.path.exists(cp_path):
                with open(cp_path) as f:
                    cp = json.load(f)
                for pid, rates in cp.get('false_positive_rates', {}).items():
                    if rates:
                        if rates.get('ours') is not None:
                            fp_ours_all.append(rates['ours'])
                        if rates.get('adf') is not None:
                            fp_adf_all.append(rates['adf'])

    print(f"  Mean FP: DFGLS={np.mean(fp_dfgls_all):.4f}  "
          f"Ours={np.mean(fp_ours_all):.4f}  "
          f"ADF={np.mean(fp_adf_all):.4f}")
    print(f"  Max FP:  DFGLS={np.max(fp_dfgls_all):.4f}  "
          f"Ours={np.max(fp_ours_all):.4f}  "
          f"ADF={np.max(fp_adf_all):.4f}")


if __name__ == '__main__':
    main()
