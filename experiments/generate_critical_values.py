"""
Generate critical values table for the stationarity test.

Produces a table of q_alpha (lower-tail quantiles) for standard
configurations of (theta, R, n, alpha).

Output: CSV and JSON files with 360 entries (5θ × 3R × 6n × 4α).

Usage:
    python experiments/generate_critical_values.py          # generate table
    python experiments/generate_critical_values.py --verify  # verify 10%
"""

import argparse
import csv
import json
import os
import sys
import time

import numpy as np

# Ensure stationarity_test is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stationarity_test.empirical_eigenvalues import _simulate_null_statistics


# ======================================================================
# Configuration
# ======================================================================

THETA_GRID = [
    (0.05, 0.05),
    (0.10, 0.10),
    (0.15, 0.15),
    (0.20, 0.20),
    (0.30, 0.30),
]
R_GRID = [0.25, 0.50, 0.75]
N_GRID = [100, 200, 500, 1000, 2000, 5000]
ALPHA_GRID = [0.01, 0.025, 0.05, 0.10]

N_CAL = 100_000
SEED_PRIMARY = 42
SEED_VERIFY = 7777

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def generate_table():
    """Generate the full table of critical values."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    total_configs = len(THETA_GRID) * len(R_GRID) * len(N_GRID)
    rows = []
    config_idx = 0
    start_time = time.time()

    print("=" * 70)
    print(f"  Generating critical values table")
    print(f"  Configurations: {total_configs} ({len(THETA_GRID)} theta x "
          f"{len(R_GRID)}R x {len(N_GRID)}n)")
    print(f"  N_cal = {N_CAL:,}, seed = {SEED_PRIMARY}")
    print(f"  Quantiles: {ALPHA_GRID}")
    print("=" * 70)

    for theta in THETA_GRID:
        for R in R_GRID:
            for n in N_GRID:
                config_idx += 1
                t0 = time.time()

                # Simulate null statistics
                stats = _simulate_null_statistics(
                    theta, R, n, N_CAL, SEED_PRIMARY
                )

                # Extract quantiles (lower tail)
                for alpha in ALPHA_GRID:
                    q = float(np.quantile(stats, alpha))

                    # Estimate density at the quantile for error estimation
                    # Using kernel density estimation
                    h = 1.06 * np.std(stats) * N_CAL ** (-1/5)
                    kernel_vals = np.exp(-0.5 * ((stats - q) / h) ** 2) / (
                        h * np.sqrt(2 * np.pi)
                    )
                    f_q = float(np.mean(kernel_vals))

                    # Error of the quantile: ± 1.96 * sqrt(α(1-α)) / (N * f(q))
                    if f_q > 1e-10:
                        q_error = 1.96 * np.sqrt(
                            alpha * (1 - alpha)
                        ) / (N_CAL * f_q)
                    else:
                        q_error = np.nan

                    rows.append({
                        'theta_1': theta[0],
                        'theta_2': theta[1],
                        'R': R,
                        'n': n,
                        'alpha': alpha,
                        'q_alpha': round(q, 8),
                        'q_error': round(float(q_error), 8),
                        'N_cal': N_CAL,
                        'seed': SEED_PRIMARY,
                    })

                elapsed = time.time() - t0
                total_elapsed = time.time() - start_time
                eta = total_elapsed / config_idx * (total_configs - config_idx)
                print(f"  [{config_idx:3d}/{total_configs}] "
                      f"theta=({theta[0]},{theta[1]}) R={R:.2f} n={n:5d} "
                      f"-- {elapsed:.1f}s  (ETA: {eta/60:.1f} min)")

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, 'critical_values.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Save JSON
    json_path = os.path.join(RESULTS_DIR, 'critical_values.json')
    with open(json_path, 'w') as f:
        json.dump({
            'description': (
                'Lower-tail critical values q_alpha for the stationarity test. '
                'Reject H0 (non-stationarity) when stat < q_alpha.'
            ),
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'N_cal': N_CAL,
            'seed': SEED_PRIMARY,
            'entries': rows,
        }, f, indent=2)

    total_time = time.time() - start_time
    print(f"\n  Table generated: {len(rows)} entries")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Total time: {total_time/60:.1f} minutes")

    return rows


def verify_table(fraction=0.10):
    """
    Verify a fraction of the table by regenerating with a different seed.

    Mandatory inclusion: at least one entry with n=5000, theta=0.3
    (where discretization variability is largest).
    """
    json_path = os.path.join(RESULTS_DIR, 'critical_values.json')
    if not os.path.exists(json_path):
        print("ERROR: critical_values.json not found. Run generation first.")
        return False

    with open(json_path) as f:
        data = json.load(f)

    entries = data['entries']
    n_verify = max(1, int(len(entries) * fraction))

    # Select entries to verify
    rng = np.random.default_rng(999)
    indices = list(rng.choice(len(entries), size=n_verify, replace=False))

    # Ensure mandatory entries: n=5000, theta=(0.3, 0.3)
    mandatory_idx = [
        i for i, e in enumerate(entries)
        if e['n'] == 5000 and e['theta_1'] == 0.3
    ]
    for mi in mandatory_idx[:2]:
        if mi not in indices:
            indices.append(mi)

    print(f"\n  Verifying {len(indices)} entries with seed={SEED_VERIFY}...")

    max_delta = 0.0
    failures = 0
    threshold = 0.01

    for idx in sorted(indices):
        e = entries[idx]
        theta = (e['theta_1'], e['theta_2'])
        R = e['R']
        n = e['n']
        alpha = e['alpha']
        q_original = e['q_alpha']

        stats = _simulate_null_statistics(theta, R, n, N_CAL, SEED_VERIFY)
        q_verify = float(np.quantile(stats, alpha))

        delta = abs(q_original - q_verify)
        max_delta = max(max_delta, delta)
        status = "OK" if delta < threshold else "FAIL"

        if delta >= threshold:
            failures += 1
            print(f"  {status}  theta=({theta[0]},{theta[1]}) R={R:.2f} "
                  f"n={n:5d} alpha={alpha:.3f}: "
                  f"q={q_original:.6f} vs {q_verify:.6f} (delta={delta:.6f})")

    print(f"\n  Verification complete:")
    print(f"    Entries checked: {len(indices)}")
    print(f"    Max |dq|: {max_delta:.6f}")
    print(f"    Threshold: {threshold}")
    print(f"    Failures: {failures}")
    print(f"    Result: {'PASS' if failures == 0 else 'FAIL'}")

    return failures == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate critical values table for the stationarity test.'
    )
    parser.add_argument('--verify', action='store_true',
                        help='Verify 10%% of the table with a different seed')
    parser.add_argument('--verify-only', action='store_true',
                        help='Only verify (do not regenerate)')
    args = parser.parse_args()

    if args.verify_only:
        success = verify_table()
        sys.exit(0 if success else 1)

    generate_table()

    if args.verify:
        verify_table()
