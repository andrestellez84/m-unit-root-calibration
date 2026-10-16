"""
Size robustness under heavy-tailed innovations.

Random walk Y_t = Y_{t-1} + eps_t with:
  - eps_t ~ t(5) / sqrt(5/3)   (variance = 1)
  - eps_t ~ t(3) / sqrt(3)     (variance = 1)

Uses the GAUSSIAN null CDF without recalibration to measure
size distortion from distributional misspecification.

Reports rejection rates with Wilson binomial CIs.
"""

import sys
import os
import json
import time
import warnings
from datetime import datetime

import numpy as np
from scipy.stats import t as tdist

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*InterpolationWarning.*")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.empirical_eigenvalues import build_null_cdf
from statsmodels.tsa.stattools import adfuller, kpss
from arch.unitroot import PhillipsPerron

# ======================================================================
# Configuration
# ======================================================================
ALPHA = 0.05
N_SIM = 5000
N_GRID = [200, 500, 1000]
THETA = (0.1, 0.1)
R = 0.50
C_1 = DEFAULT_SCALING_EXPONENTS[1]
C_2 = DEFAULT_SCALING_EXPONENTS[2]

DISTRIBUTIONS = {
    't5': {'df': 5, 'scale': np.sqrt(5.0 / 3.0)},   # Var(t5) = 5/3
    't3': {'df': 3, 'scale': np.sqrt(3.0 / 1.0)},   # Var(t3) = 3/1
}

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def ci_wilson(p_hat, n):
    """Wilson score 95% CI."""
    z = 1.96
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    width = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return round(float(center - width), 4), round(float(center + width), 4)


def generate_rw_heavy(n, df, scale, rng):
    """Random walk with standardized t(df) innovations."""
    eps = rng.standard_t(df, size=n) / scale  # variance = 1
    Y = np.empty(n + 1)
    Y[0] = 0.0
    Y[1:] = np.cumsum(eps)
    return Y


def run_our_test(Y, cdf_interp, R_val=0.50, andrews_pilot="alpha1"):
    """Our test, returns p-value."""
    n = len(Y) - 1
    theta_1, theta_2 = THETA
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    means = rolling_mean(Y, tau_1)
    g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
    variances = rolling_var(Y, tau_2)
    g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

    diffs = np.diff(Y)
    s2 = hac_newey_west(diffs, andrews_pilot=andrews_pilot)
    s = np.sqrt(s2)

    g1s = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
    g2s = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0

    stat = np.sqrt((1.0 - R_val) ** 2 * g1s ** 2 + R_val ** 2 * g2s ** 2)
    p = float(cdf_interp(stat))
    return float(np.clip(p, 0.0, 1.0))


def run_adf(Y):
    try:
        return adfuller(Y, autolag='AIC')[1]
    except Exception:
        return 1.0


def run_pp(Y):
    try:
        return PhillipsPerron(Y).pvalue
    except Exception:
        return 1.0


def run_kpss_test(Y):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, p, _, _ = kpss(Y, regression='c', nlags='auto')
        return p
    except Exception:
        return 1.0


def check(val):
    if 0.035 <= val <= 0.065:
        return "ROBUST"
    elif val < 0.035:
        return f"CONSERV ({val:.3f})"
    else:
        return f"LIBERAL ({val:.3f})"


def main(pilot="alpha1"):
    print("=" * 70)
    print("  Size Robustness: Heavy-Tailed Innovations")
    print(f"  Distributions: t(5), t(3) — standardized to Var=1")
    print(f"  Using GAUSSIAN null CDF (misspecification test)")
    print(f"  N_sim={N_SIM}, alpha={ALPHA}, theta={THETA}, R={R}")
    print(f"  n in {N_GRID}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Precalibrate Gaussian CDFs
    print("\n  Precalibrating Gaussian null CDFs...")
    cdfs = {}
    for n in N_GRID:
        t0 = time.perf_counter()
        cdfs[n] = build_null_cdf(THETA, R, n, N_cal=50000, seed=42)
        print(f"    n={n}: {time.perf_counter()-t0:.1f}s")

    results = {}

    for dist_name, dist_params in DISTRIBUTIONS.items():
        df = dist_params['df']
        scale = dist_params['scale']
        print(f"\n{'=' * 70}")
        print(f"  Distribution: {dist_name} (df={df}, scale={scale:.4f})")
        print(f"{'=' * 70}")

        results[dist_name] = {}

        for n in N_GRID:
            t0 = time.perf_counter()
            cdf_interp = cdfs[n]
            seed_base = 900000 + n * 100 + df * 10

            rej_ours = 0
            rej_adf = 0
            rej_pp = 0
            rej_kpss = 0

            for i in range(N_SIM):
                rng = np.random.default_rng(seed_base + i)
                Y = generate_rw_heavy(n, df, scale, rng)

                if run_our_test(Y, cdf_interp) < ALPHA:
                    rej_ours += 1
                if run_adf(Y) < ALPHA:
                    rej_adf += 1
                if run_pp(Y) < ALPHA:
                    rej_pp += 1
                if run_kpss_test(Y) < ALPHA:
                    rej_kpss += 1

            elapsed = time.perf_counter() - t0

            cell = {}
            for name, rej in [('ours', rej_ours), ('adf', rej_adf),
                               ('pp', rej_pp), ('kpss', rej_kpss)]:
                rate = rej / N_SIM
                lo, hi = ci_wilson(rate, N_SIM)
                cell[name] = round(rate, 4)
                cell[f'{name}_ci_lo'] = lo
                cell[f'{name}_ci_hi'] = hi

            results[dist_name][str(n)] = cell

            print(f"  n={n:4d}: "
                  f"Ours={cell['ours']:.3f} [{cell['ours_ci_lo']:.3f},{cell['ours_ci_hi']:.3f}] "
                  f"{check(cell['ours']):12s}  "
                  f"ADF={cell['adf']:.3f} [{cell['adf_ci_lo']:.3f},{cell['adf_ci_hi']:.3f}] "
                  f"{check(cell['adf']):12s}  "
                  f"PP={cell['pp']:.3f} [{cell['pp_ci_lo']:.3f},{cell['pp_ci_hi']:.3f}] "
                  f"{check(cell['pp']):12s}  "
                  f"KPSS={cell['kpss']:.3f}  "
                  f"({elapsed:.1f}s)")

    # Save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = {
        'description': 'Size under H0 (random walk) with heavy-tailed innovations',
        'distributions': {k: {'df': v['df'], 'scale': float(v['scale'])}
                          for k, v in DISTRIBUTIONS.items()},
        'config': {
            'alpha': ALPHA, 'N_sim': N_SIM, 'theta': list(THETA),
            'R': R, 'null_cdf': 'Gaussian (not recalibrated)',
        },
        'completed_at': datetime.utcnow().isoformat(),
        'results': results,
    }
    out_path = os.path.join(RESULTS_DIR, 'size_robustness_heavy_tails.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results saved: {out_path}")

    # Summary table
    print(f"\n{'=' * 70}")
    print("  SUMMARY: Size Distortion Assessment")
    print(f"{'=' * 70}")
    print(f"  {'Dist':>4s} {'n':>5s} {'Ours':>7s} {'ADF':>7s} {'PP':>7s} {'KPSS':>7s}")
    print("  " + "-" * 45)
    for dist_name in DISTRIBUTIONS:
        for n in N_GRID:
            c = results[dist_name][str(n)]
            print(f"  {dist_name:>4s} {n:5d} "
                  f"{c['ours']:7.3f} {c['adf']:7.3f} "
                  f"{c['pp']:7.3f} {c['kpss']:7.3f}")

    # Environment info
    print(f"\n{'=' * 70}")
    print("  ENVIRONMENT")
    print(f"{'=' * 70}")
    import platform
    import statsmodels
    import arch
    import scipy
    print(f"  Python:      {platform.python_version()}")
    print(f"  NumPy:       {np.__version__}")
    print(f"  SciPy:       {scipy.__version__}")
    print(f"  statsmodels: {statsmodels.__version__}")
    print(f"  arch:        {arch.__version__}")
    print(f"  OS:          {platform.platform()}")


if __name__ == '__main__':
    pilot = 'alpha1'
    import sys
    for arg in sys.argv[1:]:
        if arg.startswith('--pilot='):
            pilot = arg.split('=')[1]
    main(pilot=pilot)
