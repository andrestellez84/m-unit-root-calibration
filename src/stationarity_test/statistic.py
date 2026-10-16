"""
Module F1.D: Statistic evaluation.

Evaluates the quadratic statistic tilde{g}_R^{theta}(Y) on an observed
time series and computes the asymptotic p-value.

Under Decision D1 (quadratic combination):
    tilde{g}_R = sqrt((1-R)^2 * [g_1^std]^2 + R^2 * [g_2^std]^2)

Under Decision D2 (squared standard deviations):
    g_2^tau(Y) = sqrt(Var_k([sigma_k^tau]^2))
    operates on VARIANCES, not standard deviations.

Under Decision D3 (asymmetric standardization, Section 2.4):
    g_1^std = g_1^tau(Y) / (sigma_hat * n^{c_1/2})
    g_2^std = g_2^tau(Y) / (sigma_hat^2 * n^{c_2/2})
    where sigma_hat is the HAC (Newey-West) estimator of the innovation std dev.
    The eigenvalues already encode the asymptotic scale (no d_bar factor needed).
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
# standardization_factor no longer used -- eigenvalues encode the scale directly
from stationarity_test.null_quantiles import null_cdf
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.deterministics import apply_deterministics, validate_deterministics
from stationarity_test.rm_core import g1_raw as _g1_raw_variant, validate_variant


def _compute_g1(Y: np.ndarray, tau: int) -> float:
    """
    Compute the rolling mean seminorm g_1^tau(Y).

    g_1^tau(Y) = sqrt(Var_k(e_k^tau))
    where e_k^tau = (1/(tau+1)) * sum_{i=k}^{k+tau} Y_i

    Parameters
    ----------
    Y : np.ndarray
        Time series of shape (n+1,).
    tau : int
        Window parameter (window contains tau+1 observations).

    Returns
    -------
    float
        Seminorm value g_1^tau(Y) >= 0.
    """
    means = rolling_mean(Y, tau)
    var_k = sample_variance_over_k(means)
    return float(np.sqrt(max(var_k, 0.0)))


def _compute_g2(Y: np.ndarray, tau: int) -> float:
    """
    Compute the rolling variance seminorm g_2^tau(Y).

    Under Decision D2:
        g_2^tau(Y) = sqrt(Var_k(v_k^tau))
    where v_k^tau = [sigma_k^tau]^2 is the rolling VARIANCE (not std dev).

    Parameters
    ----------
    Y : np.ndarray
        Time series of shape (n+1,).
    tau : int
        Window parameter.

    Returns
    -------
    float
        Seminorm value g_2^tau(Y) >= 0.
    """
    variances = rolling_var(Y, tau)  # D2: returns [sigma_k]^2
    var_k = sample_variance_over_k(variances)
    return float(np.sqrt(max(var_k, 0.0)))


def compute_statistic(
    Y: np.ndarray,
    theta: tuple[float, float],
    R: float,
    eps: float = 1e-6,
    andrews_pilot: str = 'alpha1',
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
) -> dict:
    """
    Evaluate tilde{g}_R^theta(Y) and its asymptotic p-value.

    A8 variants (defaults reproduce the published statistic exactly):
    cal_sigma ("one" | "hac") selects the null calibration; tau_mode="zero"
    sets tau_1 = 0 (MSB-HAC); anchor="gls" uses the GLS-anchored non-centred
    moment of the rolling means (RM-GLS). See rm_core.

    deterministics="c" (default) is the original statistic, unchanged.
    deterministics="ct" forms the rolling statistics on the residuals of Y
    detrended against (1, t) (detrend="qd", ERS with cbar=-13.5, or "ols") and
    evaluates the p-value against a null calibrated on random walks detrended
    the same way. sigma_hat is always computed on diff(Y) of the original series.

    This is the main entry point for the stationarity test (Phase 1).

    Parameters
    ----------
    Y : np.ndarray
        Observed time series, array of shape (n+1,).
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2) in (0, 1/2] each.
    R : float
        Combination weight in [0, 1].
    eps : float
        Numerical tolerance for quantile/CDF computation.

    Returns
    -------
    dict
        {
            'statistic': float    - tilde{g}_R^theta(Y), standardized
            'p_value': float      - 1 - F_G(tilde{g}_R^theta(Y))
            'g1_raw': float       - g_1^{tau_1}(Y) before standardization
            'g2_raw': float       - g_2^{tau_2}(Y) before standardization
            'g1_std': float       - g_1 after standardization (should be O(1))
            'g2_std': float       - g_2 after standardization (should be O(1))
            'tau1': int           - discrete window for mean component
            'tau2': int           - discrete window for variance component
            'n': int              - sample size (number of increments)
        }
    """
    # --- Validation ---
    validate_series(Y)
    validate_theta_pair(theta)
    validate_R(R)
    validate_deterministics(deterministics, detrend)
    validate_variant(cal_sigma, tau_mode, anchor, detrend)

    n = len(Y) - 1  # number of increments
    # Series on which the rolling statistics are formed ("c": Y itself)
    Y_stat = apply_deterministics(Y, deterministics, detrend)
    theta_1, theta_2 = theta

    # --- Discretize windows ---
    tau_1 = max(2, int(round(theta_1 * n)))
    tau_2 = max(2, int(round(theta_2 * n)))

    # Ensure tau doesn't exceed n/2
    tau_1 = min(tau_1, n // 2)
    tau_2 = min(tau_2, n // 2)

    if tau_mode == "zero":
        tau_1 = 0

    # --- Compute raw seminorms ---
    if anchor == "mean":
        g1_raw = _compute_g1(Y_stat, tau_1)
    else:
        g1_raw = _g1_raw_variant(Y, Y_stat, tau_1, deterministics, anchor)
    g2_raw = _compute_g2(Y_stat, tau_2)

    # --- HAC estimation of innovation scale (Section 2.4) ---
    diffs = np.diff(Y)  # ΔY_t = Y_t - Y_{t-1}
    sigma_hat_sq = hac_newey_west(diffs, andrews_pilot=andrews_pilot)
    sigma_hat = np.sqrt(sigma_hat_sq)

    # --- Standardization (D3: asymmetric scaling) ---
    # The analytical eigenvalues already encode the asymptotic scale,
    # so we only divide by sigma^{power} * n^{c/2}.
    # E[g_std^2] converges to trace(Lambda) = sum of eigenvalues.
    c_1 = DEFAULT_SCALING_EXPONENTS[1]  # = 1.0
    c_2 = DEFAULT_SCALING_EXPONENTS[2]  # = 2.0

    scale_1 = sigma_hat * n ** (c_1 / 2.0)
    scale_2 = sigma_hat_sq * n ** (c_2 / 2.0)

    g1_std = g1_raw / scale_1 if scale_1 > 0 else 0.0
    g2_std = g2_raw / scale_2 if scale_2 > 0 else 0.0

    # --- Quadratic combination (D1) ---
    statistic = np.sqrt((1.0 - R)**2 * g1_std**2 + R**2 * g2_std**2)

    # --- P-value (lower tail: small stat = evidence against H0) ---
    p_value = null_cdf(statistic, theta, R, n=n, eps=eps,
                       deterministics=deterministics, detrend=detrend,
                       cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                       andrews_pilot=andrews_pilot)
    p_value = float(np.clip(p_value, 0.0, 1.0))

    return {
        'statistic': float(statistic),
        'p_value': p_value,
        'g1_raw': g1_raw,
        'g2_raw': g2_raw,
        'g1_std': g1_std,
        'g2_std': g2_std,
        'sigma_hat': float(sigma_hat),
        'tau1': tau_1,
        'tau2': tau_2,
        'n': n,
    }
