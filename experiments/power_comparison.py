"""
Phase 3, Experiment 2: Local power comparison against ADF, PP, KPSS.

Compares the rejection rate (power) of four stationarity/unit-root tests
across three families of DGPs designed to highlight different strengths.

DGP 1: Near-unit-root AR(1) — classical power comparison
DGP 2: Near-unit-root AR(1) + structural break in mean — persistence + break
DGP 3: Break in variance (white noise base) — variance component advantage

Usage:
    python experiments/power_comparison.py [--stage SIZE|DGP1|DGP2|DGP3|ALL]
"""

import sys
import os
import time
import json
import warnings
from datetime import datetime

import numpy as np
from scipy.stats import kstest

# Suppress KPSS interpolation warnings
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
warnings.filterwarnings("ignore", message=".*p-value.*")
warnings.filterwarnings("ignore", message=".*InterpolationWarning.*")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.empirical_eigenvalues import build_null_cdf

# Baseline tests
from statsmodels.tsa.stattools import adfuller, kpss
from arch.unitroot import PhillipsPerron


# ======================================================================
# Configuration
# ======================================================================

ALPHA = 0.05
N_SIM = 5000
N_GRID = [200, 500, 1000]

# Fixed parameters for our test (main experiment)
THETA_FIXED = (0.1, 0.1)
R_CONFIGS = {
    'R050': 0.50,   # equiponderado (main)
    'R025': 0.25,   # énfasis media
    'R075': 0.75,   # énfasis varianza
}

# DGP parameters
DGP1_RHOS = [0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 1.00]
DGP2_DELTAS = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]  # in units of sigma_unconditional
DGP2_RHO = 0.95  # fixed near-unit-root persistence
DGP3_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
DGP4_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
DGP4_RHO = 0.50  # strongly stationary, fast mean-reversion

# Scaling exponents
C_1 = DEFAULT_SCALING_EXPONENTS[1]
C_2 = DEFAULT_SCALING_EXPONENTS[2]


# ======================================================================
# DGP Generators
# ======================================================================

def generate_ar1(n, rho, sigma=1.0, rng=None):
    """Generate AR(1): Y_t = rho * Y_{t-1} + eps_t."""
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for t in range(n):
        Y[t + 1] = rho * Y[t] + eps[t]
    return Y


def generate_ar1_break_mean(n, rho, delta, sigma=1.0, rng=None):
    """
    Generate stationary AR(1) with structural break in mean at midpoint.

    First half:  Y_t = rho * (Y_{t-1} - 0) + 0 + eps_t  (mean-reverts to 0)
    Second half: Y_t = rho * (Y_{t-1} - mu) + mu + eps_t (mean-reverts to mu)

    where mu = delta * sigma_unconditional = delta * sigma / sqrt(1 - rho^2)

    delta is in units of the unconditional standard deviation.
    The series is stationary in both regimes (rho < 1) => under H_A.
    """
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    t_break = n // 2
    # Level shift in units of sigma_unconditional
    sigma_unc = sigma / np.sqrt(1 - rho ** 2)
    mu = delta * sigma_unc
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for t in range(n):
        mu_t = mu if t >= t_break else 0.0
        Y[t + 1] = rho * (Y[t] - mu_t) + mu_t + eps[t]
    return Y


def generate_rw_break_variance(n, ratio, sigma1=1.0, rng=None):
    """
    Generate random walk with heteroscedastic innovations.
    Y_t = Y_{t-1} + eps_t, where:
        eps_t ~ N(0, sigma1^2) for t <= n/2
        eps_t ~ N(0, sigma2^2) for t > n/2

    For ratio=1: pure random walk with constant variance (H0).
    For ratio>1: random walk with variance break in innovations.
    ADF/PP still see a unit root (insensitive to heteroscedasticity).
    Our g2 component detects the variance regime change.
    """
    if rng is None:
        rng = np.random.default_rng()
    t_break = n // 2
    sigma2 = sigma1 * ratio
    eps = np.empty(n)
    eps[:t_break] = rng.standard_normal(t_break) * sigma1
    eps[t_break:] = rng.standard_normal(n - t_break) * sigma2
    Y = np.empty(n + 1)
    Y[0] = 0.0
    Y[1:] = np.cumsum(eps)
    return Y


def generate_ar1_break_variance(n, rho, ratio, sigma1=1.0, rng=None):
    """
    Generate stationary AR(1) with break in innovation variance at midpoint.
    Y_t = rho * Y_{t-1} + eps_t, where:
        eps_t ~ N(0, sigma1^2) for t <= n/2
        eps_t ~ N(0, (sigma1*ratio)^2) for t > n/2

    For ratio=1: stationary AR(1) with constant variance.
    For ratio>1: stationary AR(1) with variance regime change.
    The series is stationary in mean throughout (rho=0.5 < 1),
    so g1 should remain approximately flat.
    g2 should detect the variance regime change.
    """
    if rng is None:
        rng = np.random.default_rng()
    t_break = n // 2
    sigma2 = sigma1 * ratio
    eps = np.empty(n)
    eps[:t_break] = rng.standard_normal(t_break) * sigma1
    eps[t_break:] = rng.standard_normal(n - t_break) * sigma2
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for t in range(n):
        Y[t + 1] = rho * Y[t] + eps[t]
    return Y


# ======================================================================
# Test Wrappers
# ======================================================================

def run_our_test(Y, theta, R, cdf_interp, andrews_pilot="alpha1"):
    """
    Run our stationarity test. Returns p-value.
    Uses precomputed CDF interpolator for speed.
    """
    n = len(Y) - 1
    theta_1, theta_2 = theta
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    # Raw seminorms
    means = rolling_mean(Y, tau_1)
    g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
    variances = rolling_var(Y, tau_2)
    g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

    # HAC standardization
    diffs = np.diff(Y)
    s2 = hac_newey_west(diffs, andrews_pilot=andrews_pilot)
    s = np.sqrt(s2)

    g1s = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
    g2s = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0

    stat = np.sqrt((1.0 - R) ** 2 * g1s ** 2 + R ** 2 * g2s ** 2)
    # Lower-tail test: reject H0 (random walk) when statistic is small
    # (stationarity → less dispersion in rolling stats → small statistic)
    p_value = float(cdf_interp(stat))
    return float(np.clip(p_value, 0.0, 1.0))


def run_adf(Y):
    """Run ADF test (autolag=AIC). Returns p-value."""
    try:
        result = adfuller(Y, autolag='AIC')
        return result[1]  # p-value
    except Exception:
        return 1.0  # fail-safe: don't reject


def run_pp(Y):
    """Run Phillips-Perron test. Returns p-value."""
    try:
        result = PhillipsPerron(Y)
        return result.pvalue
    except Exception:
        return 1.0


def run_kpss(Y):
    """Run KPSS test (level stationarity). Returns p-value."""
    try:
        stat, p_value, _, _ = kpss(Y, regression='c', nlags='auto')
        return p_value
    except Exception:
        return 1.0


# ======================================================================
# Precalibration
# ======================================================================

def precalibrate_cdfs(theta, r_values, n_grid, N_cal=50000):
    """Precompute empirical null CDFs for all (R, n) combinations."""
    cache = {}
    total = len(r_values) * len(n_grid)
    idx = 0
    print(f"  Precalibrating {total} null CDFs (N_cal={N_cal})...")
    for R_name, R_val in r_values.items():
        for n in n_grid:
            idx += 1
            t0 = time.perf_counter()
            cdf = build_null_cdf(theta, R_val, n, N_cal=N_cal, seed=42)
            elapsed = time.perf_counter() - t0
            cache[(R_name, n)] = cdf
            print(f"    [{idx}/{total}] R={R_val:.2f}, n={n} -- {elapsed:.1f}s")
    return cache


# ======================================================================
# Experiment Runners
# ======================================================================

def run_experiment_cell(dgp_func, dgp_kwargs, n, theta,
                        r_configs, cdf_cache, N_sim,
                        alpha=ALPHA, seed_base=10000, andrews_pilot="alpha1"):
    """
    Run one cell: N_sim simulations, reporting rejection rates
    for all 3 R configs of our test + ADF + PP + KPSS,
    and recording component diagnostics E[g1_std] and E[g2_std].
    """
    rej_ours = {name: 0 for name in r_configs}
    rej_adf = 0
    rej_pp = 0
    rej_kpss = 0
    g1_vals = []
    g2_vals = []

    theta_1, theta_2 = theta
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    for i in range(N_sim):
        rng = np.random.default_rng(seed_base + i)
        Y = dgp_func(n=n, rng=rng, **dgp_kwargs)

        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

        diffs = np.diff(Y)
        s2 = hac_newey_west(diffs, andrews_pilot=andrews_pilot)
        s = np.sqrt(s2)
        g1s = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
        g2s = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0
        g1_vals.append(g1s)
        g2_vals.append(g2s)

        # Our test — all 3 R configs on same series
        for R_name, R_val in r_configs.items():
            stat = np.sqrt((1.0 - R_val) ** 2 * g1s ** 2 + R_val ** 2 * g2s ** 2)
            cdf_interp = cdf_cache[(R_name, n)]
            p_ours = float(cdf_interp(stat))
            p_ours = float(np.clip(p_ours, 0.0, 1.0))
            if p_ours < alpha:
                rej_ours[R_name] += 1

        # ADF
        if run_adf(Y) < alpha:
            rej_adf += 1

        # PP
        if run_pp(Y) < alpha:
            rej_pp += 1

        # KPSS
        if run_kpss(Y) < alpha:
            rej_kpss += 1

    g1_arr = np.array(g1_vals)
    g2_arr = np.array(g2_vals)

    result = {f'ours_{name}': rej_ours[name] / N_sim for name in r_configs}
    result['adf'] = rej_adf / N_sim
    result['pp'] = rej_pp / N_sim
    result['kpss_rej'] = rej_kpss / N_sim
    result['E_g1_std'] = float(g1_arr.mean())
    result['E_g2_std'] = float(g2_arr.mean())
    result['std_g1'] = float(g1_arr.std())
    result['std_g2'] = float(g2_arr.std())
    return result


# ======================================================================
# Stage: Size Verification (Table 1)
# ======================================================================

def run_size_verification(cdf_cache, pilot="alpha1"):
    """
    Verify empirical size under H0 for all tests.
    H0 for ADF/PP/ours: random walk (rho=1.0)
    H0 for KPSS: white noise (stationary)
    """
    print("\n" + "=" * 70)
    print("  SIZE VERIFICATION (Table 1)")
    print("  H0: random walk for ADF/PP/Ours | H0: stationarity for KPSS")
    print(f"  N_sim={N_SIM}, alpha={ALPHA}, pilot={pilot}")
    print(f"  Acceptance interval: [{0.035:.3f}, {0.065:.3f}]")
    print("=" * 70)

    results = {}

    def check(val):
        return "PASS" if 0.035 <= val <= 0.065 else "FAIL"

    for n in N_GRID:
        print(f"\n  n = {n}:")

        # Our test (all 3 R) + ADF + PP: H0 is random walk (rho=1)
        cell = run_experiment_cell(
            dgp_func=generate_ar1,
            dgp_kwargs={'rho': 1.0},
            n=n, theta=THETA_FIXED,
            r_configs=R_CONFIGS, cdf_cache=cdf_cache,
            N_sim=N_SIM, seed_base=0,
            andrews_pilot=pilot,
        )

        # KPSS: H0 is white noise (stationary)
        kpss_rej = 0
        for i in range(N_SIM):
            rng = np.random.default_rng(50000 + i)
            Y_wn = rng.standard_normal(n + 1)
            if run_kpss(Y_wn) < ALPHA:
                kpss_rej += 1
        kpss_size = kpss_rej / N_SIM

        results[n] = {**cell, 'kpss_size': kpss_size}

        for R_name in R_CONFIGS:
            print(f"    Ours({R_name}): {cell[f'ours_{R_name}']:.3f}  "
                  f"[{check(cell[f'ours_{R_name}'])}]")
        print(f"    ADF:        {cell['adf']:.3f}  [{check(cell['adf'])}]")
        print(f"    PP:         {cell['pp']:.3f}  [{check(cell['pp'])}]")
        print(f"    KPSS:       {kpss_size:.3f}  [{check(kpss_size)}]")

    return results


# ======================================================================
# Stage: DGP 1 — Near-unit-root AR(1)
# ======================================================================

def run_dgp1(cdf_cache, pilot="alpha1"):
    """Power curves for near-unit-root AR(1)."""
    print("\n" + "=" * 70)
    print("  DGP 1: Near-unit-root AR(1)")
    print(f"  rho in {DGP1_RHOS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print("=" * 70)

    results = {}
    total = len(DGP1_RHOS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        results[n] = {}
        for rho in DGP1_RHOS:
            idx += 1
            t0 = time.perf_counter()

            cell = run_experiment_cell(
                dgp_func=generate_ar1,
                dgp_kwargs={'rho': rho},
                n=n, theta=THETA_FIXED,
                r_configs=R_CONFIGS, cdf_cache=cdf_cache,
                N_sim=N_SIM,
                seed_base=100000 + n * 100 + int(rho * 100),
                andrews_pilot=pilot,
            )

            elapsed = time.perf_counter() - t0
            results[n][rho] = cell

            print(f"  [{idx:2d}/{total}] n={n:4d}, rho={rho:.2f}: "
                  f"R50={cell['ours_R050']:.3f}  R25={cell['ours_R025']:.3f}  "
                  f"R75={cell['ours_R075']:.3f}  "
                  f"ADF={cell['adf']:.3f}  PP={cell['pp']:.3f}  "
                  f"KPSS={cell['kpss_rej']:.3f}  ({elapsed:.1f}s)")

    return results


# ======================================================================
# Stage: DGP 2 — Stationary AR(1) + break in mean
# ======================================================================

def run_dgp2(cdf_cache, pilot="alpha1"):
    """Power curves for stationary AR(1) rho=0.95 + mean break."""
    print("\n" + "=" * 70)
    print(f"  DGP 2: Stationary AR(1) rho={DGP2_RHO} + break in mean")
    print(f"  delta in {DGP2_DELTAS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print("=" * 70)

    results = {}
    total = len(DGP2_DELTAS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        results[n] = {}
        for delta in DGP2_DELTAS:
            idx += 1
            t0 = time.perf_counter()

            cell = run_experiment_cell(
                dgp_func=generate_ar1_break_mean,
                dgp_kwargs={'rho': DGP2_RHO, 'delta': delta},
                n=n, theta=THETA_FIXED,
                r_configs=R_CONFIGS, cdf_cache=cdf_cache,
                N_sim=N_SIM,
                seed_base=200000 + n * 100 + int(delta * 10),
                andrews_pilot=pilot,
            )

            elapsed = time.perf_counter() - t0
            results[n][delta] = cell

            print(f"  [{idx:2d}/{total}] n={n:4d}, delta={delta:.1f}: "
                  f"R50={cell['ours_R050']:.3f}  R25={cell['ours_R025']:.3f}  "
                  f"R75={cell['ours_R075']:.3f}  "
                  f"ADF={cell['adf']:.3f}  PP={cell['pp']:.3f}  "
                  f"KPSS={cell['kpss_rej']:.3f}  ({elapsed:.1f}s)")

    return results


# ======================================================================
# Stage: DGP 3 — Break in variance
# ======================================================================

def run_dgp3(cdf_cache, pilot="alpha1"):
    """Power curves for random walk with heteroscedastic innovations."""
    print("\n" + "=" * 70)
    print("  DGP 3: Random walk with variance break in innovations")
    print(f"  ratio in {DGP3_RATIOS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print("=" * 70)

    results = {}
    total = len(DGP3_RATIOS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        results[n] = {}
        for ratio in DGP3_RATIOS:
            idx += 1
            t0 = time.perf_counter()

            cell = run_experiment_cell(
                dgp_func=generate_rw_break_variance,
                dgp_kwargs={'ratio': ratio},
                n=n, theta=THETA_FIXED,
                r_configs=R_CONFIGS, cdf_cache=cdf_cache,
                N_sim=N_SIM,
                seed_base=300000 + n * 100 + int(ratio * 10),
                andrews_pilot=pilot,
            )

            elapsed = time.perf_counter() - t0
            results[n][ratio] = cell

            print(f"  [{idx:2d}/{total}] n={n:4d}, ratio={ratio:.1f}: "
                  f"R50={cell['ours_R050']:.3f}  R25={cell['ours_R025']:.3f}  "
                  f"R75={cell['ours_R075']:.3f}  "
                  f"ADF={cell['adf']:.3f}  PP={cell['pp']:.3f}  "
                  f"KPSS={cell['kpss_rej']:.3f}  ({elapsed:.1f}s)")

    return results


# ======================================================================
# Stage: DGP 4 — Stationary AR(1) + break in variance (g2 justification)
# ======================================================================

def run_dgp4(cdf_cache, pilot="alpha1"):
    """Power curves + component diagnostics for stationary AR(0.5) + variance break."""
    print("\n" + "=" * 70)
    print(f"  DGP 4: Stationary AR(1) rho={DGP4_RHO} + break in innovation variance")
    print(f"  ratios in {DGP4_RATIOS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print("  ** Recording component diagnostics (E[g1_std], E[g2_std]) **")
    print("=" * 70)

    results = {}
    total = len(DGP4_RATIOS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        results[n] = {}
        tau_1 = max(2, min(int(round(THETA_FIXED[0] * n)), n // 2))
        tau_2 = max(2, min(int(round(THETA_FIXED[1] * n)), n // 2))

        for ratio in DGP4_RATIOS:
            idx += 1
            t0 = time.perf_counter()

            # Extended cell: rejection rates + component diagnostics
            rej_ours = {name: 0 for name in R_CONFIGS}
            rej_adf = 0
            rej_pp = 0
            rej_kpss = 0
            g1_vals = []
            g2_vals = []

            for i in range(N_SIM):
                rng = np.random.default_rng(
                    400000 + n * 100 + int(ratio * 10) + i)
                Y = generate_ar1_break_variance(
                    n=n, rho=DGP4_RHO, ratio=ratio, rng=rng)

                # Compute components once
                means = rolling_mean(Y, tau_1)
                g1_raw = float(np.sqrt(max(
                    sample_variance_over_k(means), 0.0)))
                variances = rolling_var(Y, tau_2)
                g2_raw = float(np.sqrt(max(
                    sample_variance_over_k(variances), 0.0)))
                diffs = np.diff(Y)
                s2 = hac_newey_west(diffs, andrews_pilot=pilot)
                s = np.sqrt(s2)
                g1s = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
                g2s = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0

                g1_vals.append(g1s)
                g2_vals.append(g2s)

                # Our test — all 3 R configs
                for R_name, R_val in R_CONFIGS.items():
                    stat = np.sqrt(
                        (1.0 - R_val) ** 2 * g1s ** 2
                        + R_val ** 2 * g2s ** 2)
                    cdf_interp = cdf_cache[(R_name, n)]
                    p_val = float(cdf_interp(stat))
                    p_val = float(np.clip(p_val, 0.0, 1.0))
                    if p_val < ALPHA:
                        rej_ours[R_name] += 1

                # Baselines
                if run_adf(Y) < ALPHA:
                    rej_adf += 1
                if run_pp(Y) < ALPHA:
                    rej_pp += 1
                if run_kpss(Y) < ALPHA:
                    rej_kpss += 1

            g1_arr = np.array(g1_vals)
            g2_arr = np.array(g2_vals)

            cell = {
                f'ours_{name}': rej_ours[name] / N_SIM
                for name in R_CONFIGS
            }
            cell['adf'] = rej_adf / N_SIM
            cell['pp'] = rej_pp / N_SIM
            cell['kpss_rej'] = rej_kpss / N_SIM
            # Component diagnostics
            cell['E_g1_std'] = float(g1_arr.mean())
            cell['E_g2_std'] = float(g2_arr.mean())
            cell['std_g1'] = float(g1_arr.std())
            cell['std_g2'] = float(g2_arr.std())

            elapsed = time.perf_counter() - t0
            results[n][ratio] = cell

            print(f"  [{idx:2d}/{total}] n={n:4d}, r={ratio:.1f}: "
                  f"R50={cell['ours_R050']:.3f}  R25={cell['ours_R025']:.3f}  "
                  f"R75={cell['ours_R075']:.3f}  "
                  f"ADF={cell['adf']:.3f}  PP={cell['pp']:.3f}  "
                  f"KPSS={cell['kpss_rej']:.3f}  "
                  f"E[g1]={cell['E_g1_std']:.4f}  "
                  f"E[g2]={cell['E_g2_std']:.4f}  ({elapsed:.1f}s)")

    return results


# ======================================================================
# Main
# ======================================================================

def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else 'ALL'
    stage = stage.upper()

    print("=" * 70)
    print(f"  Phase 3, Experiment 2: Power Comparison")
    print(f"  Stage: {stage}")
    print(f"  theta={THETA_FIXED}, alpha={ALPHA}, N_sim={N_SIM}")
    print(f"  n_grid={N_GRID}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    t_start = time.perf_counter()

    # Precalibrate CDFs for all (R, n) we'll need
    cdf_cache = precalibrate_cdfs(THETA_FIXED, R_CONFIGS, N_GRID)

    all_results = {}

    if stage in ('SIZE', 'ALL'):
        all_results['size'] = run_size_verification(cdf_cache)

    if stage in ('DGP1', 'ALL'):
        all_results['dgp1'] = run_dgp1(cdf_cache)

    if stage in ('DGP2', 'ALL'):
        all_results['dgp2'] = run_dgp2(cdf_cache)

    if stage in ('DGP3', 'ALL', 'DGP34'):
        all_results['dgp3'] = run_dgp3(cdf_cache)

    if stage in ('DGP4', 'ALL', 'DGP34'):
        all_results['dgp4'] = run_dgp4(cdf_cache)

    elapsed_total = time.perf_counter() - t_start

    # Save results
    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'power_comparison_{stage.lower()}.json')

    # Convert numpy types for JSON serialization
    def to_serializable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, dict):
            return {str(k): to_serializable(v) for k, v in obj.items()}
        return obj

    with open(out_path, 'w') as f:
        json.dump(to_serializable(all_results), f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  DONE. Total time: {elapsed_total / 60:.1f} minutes")
    print(f"  Results saved to: {out_path}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
