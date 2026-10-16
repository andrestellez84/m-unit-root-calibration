"""
Module F2.C: Full stationarity test pipeline.

Top-level entry point that orchestrates all modules to produce a complete
test result from a raw time series, with no manual parameter tuning.

Pipeline:
    1. Validate input
    2. Estimate σ̂ via HAC (Newey-West)
    3. Select θ* via spectral criterion (if not provided)
    4. Compute raw seminorms g₁, g₂
    5. Standardize with σ̂, n^{c_i/2}
    6. Optimize R* via adaptive MLE (if not provided)
    7. Compute combined statistic
    8. Compute p-value (lower tail) and critical value
    9. Decision: reject H₀ (non-stationarity) if p < α

The lower-tail convention is justified because under H₁ (stationarity),
the statistic converges to 0: rolling means converge to the population
mean and rolling variances converge to the marginal variance, so both
g₁_std and g₂_std → 0 after normalization by n^{c_i/2}. Small values
of the statistic are evidence against H₀ (random walk).
"""

import numpy as np

from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.utils import (
    validate_series,
    validate_theta_pair,
    validate_R,
    rolling_mean,
    rolling_var,
    sample_variance_over_k,
)
from stationarity_test.null_quantiles import null_cdf, null_quantile
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.theta_selection import select_theta
from stationarity_test.optimal_weight import compute_optimal_R
from stationarity_test.deterministics import apply_deterministics, validate_deterministics
from stationarity_test.rm_core import g1_raw as _g1_raw_variant, validate_variant


def stationarity_test(
    Y: np.ndarray,
    alpha: float = 0.05,
    theta: tuple[float, float] | None = None,
    R: float | None = None,
    eps: float = 1e-6,
    andrews_pilot: str = 'alpha1',
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
) -> dict:
    """
    Complete stationarity test pipeline.

    cal_sigma, tau_mode and anchor select the A8 variants (see rm_core); the
    defaults are the original pipeline. R = 0 (mean channel only) is admissible.

    deterministics="c" (default) is the original pipeline, unchanged.
    deterministics="ct" selects theta and forms the seminorms on Y detrended
    against (1, t) (detrend="qd" or "ols"), keeps sigma_hat on diff(Y) of the
    original series, and uses the null calibrated on detrended random walks.

    Given an observed time series Y, automatically selects the optimal
    window parameters θ* and combination weight R*, evaluates the
    standardized statistic, and computes the asymptotic p-value.

    Parameters
    ----------
    Y : np.ndarray
        Observed time series, array of shape (n+1,).
    alpha : float
        Significance level in (0, 1). Default: 0.05.
    theta : tuple[float, float] or None
        Window parameters (θ₁, θ₂). If None, selected automatically
        via spectral criterion (Module F2.A).
    R : float or None
        Combination weight in [0, 1]. If None, optimized adaptively
        via MLE (Module F2.B).
    eps : float
        Numerical tolerance.

    Returns
    -------
    dict
        {
            'statistic': float,       # value of g̃_R^θ(Y)
            'p_value': float,         # lower-tail p-value: F̂₀(stat)
            'reject_H0': bool,        # True if p < alpha
            'rejection_rule': str,    # 'reject if stat < critical_value'
            'theta_1': float,         # window selected (mean)
            'theta_2': float,         # window selected (variance)
            'R': float,               # weight used
            'g1_raw': float,          # raw mean seminorm
            'g2_raw': float,          # raw variance seminorm
            'g1_std': float,          # standardized mean component
            'g2_std': float,          # standardized variance component
            'sigma_hat': float,       # HAC estimate of σ
            'n': int,                 # sample size (increments)
            'critical_value': float,  # q_α (lower-tail threshold)
            'alpha': float,           # significance level used
            'theta_auto': bool,       # True if θ was auto-selected
            'R_auto': bool,           # True if R was auto-optimized
        }

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    # --- 1. VALIDATION ---
    validate_series(Y)
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    validate_deterministics(deterministics, detrend)
    validate_variant(cal_sigma, tau_mode, anchor, detrend)

    n = len(Y) - 1
    Y_stat = apply_deterministics(Y, deterministics, detrend)  # "c": Y itself

    # --- 2. HAC ESTIMATION ---
    diffs = np.diff(Y)
    sigma_hat_sq = hac_newey_west(diffs, andrews_pilot=andrews_pilot)
    sigma_hat = np.sqrt(sigma_hat_sq)

    # --- 3. THETA SELECTION ---
    theta_auto = theta is None
    if theta_auto:
        result_theta1 = select_theta(Y_stat, component=1, seed=42)
        result_theta2 = select_theta(Y_stat, component=2, seed=43)
        theta = (result_theta1['theta_star'], result_theta2['theta_star'])

    validate_theta_pair(theta)
    theta_1, theta_2 = theta

    # --- 4. RAW SEMINORMS ---
    tau_1 = max(2, int(round(theta_1 * n)))
    tau_2 = max(2, int(round(theta_2 * n)))
    tau_1 = min(tau_1, n // 2)
    tau_2 = min(tau_2, n // 2)

    if tau_mode == "zero":
        tau_1 = 0
    if anchor == "mean":
        means = rolling_mean(Y_stat, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
    else:
        g1_raw = _g1_raw_variant(Y, Y_stat, tau_1, deterministics, anchor)

    variances = rolling_var(Y_stat, tau_2)
    g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

    # --- 5. STANDARDIZATION (Section 2.4) ---
    # Scale = sigma^{p_i} * n^{c_i/2}
    # Empirical eigenvalues already encode the full discrete structure,
    # so no d_bar correction is needed.
    c_1 = DEFAULT_SCALING_EXPONENTS[1]  # = 1.0
    c_2 = DEFAULT_SCALING_EXPONENTS[2]  # = 2.0

    scale_1 = sigma_hat * n ** (c_1 / 2.0)
    scale_2 = sigma_hat_sq * n ** (c_2 / 2.0)

    g1_std = g1_raw / scale_1 if scale_1 > 0 else 0.0
    g2_std = g2_raw / scale_2 if scale_2 > 0 else 0.0

    # --- 6. OPTIMAL WEIGHT ---
    R_auto = R is None
    if R_auto:
        R_result = compute_optimal_R(g1_std, g2_std, method='adaptive')
        R = R_result['R_star']
    else:
        validate_R(R)

    # --- 7. COMBINED STATISTIC ---
    statistic = float(np.sqrt(
        (1.0 - R)**2 * g1_std**2 + R**2 * g2_std**2
    ))

    # --- 8. P-VALUE AND CRITICAL VALUE (lower tail) ---
    # Under H₁ (stationarity), stat → 0, so small values are evidence
    # against H₀. p = F̂₀(stat): probability of seeing a value ≤ stat
    # under the null.
    p_value = null_cdf(statistic, theta, R, n=n, eps=eps,
                       deterministics=deterministics, detrend=detrend,
                       cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                       andrews_pilot=andrews_pilot)
    p_value = float(np.clip(p_value, 0.0, 1.0))

    critical_value = null_quantile(theta, R, alpha, n=n, eps=eps,
                                   deterministics=deterministics, detrend=detrend,
                                   cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                                   andrews_pilot=andrews_pilot)

    # --- 9. DECISION ---
    reject_H0 = p_value < alpha

    return {
        'statistic': statistic,
        'p_value': p_value,
        'reject_H0': reject_H0,
        'rejection_rule': 'reject if stat < critical_value',
        'theta_1': float(theta_1),
        'theta_2': float(theta_2),
        'R': float(R),
        'g1_raw': g1_raw,
        'g2_raw': g2_raw,
        'g1_std': g1_std,
        'g2_std': g2_std,
        'sigma_hat': float(sigma_hat),
        'n': n,
        'critical_value': float(critical_value),
        'alpha': float(alpha),
        'theta_auto': theta_auto,
        'R_auto': R_auto,
    }
