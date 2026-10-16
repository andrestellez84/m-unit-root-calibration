"""
Module F2.D: HAC (Heteroskedasticity and Autocorrelation Consistent) estimator.

Implements the Newey-West estimator of the long-run variance of a time series,
using the Bartlett kernel with automatic bandwidth selection (Andrews, 1991).

References:
    Newey, W.K. and West, K.D. (1987), "A Simple, Positive Semi-definite,
    Heteroskedasticity and Autocorrelation Consistent Covariance Matrix",
    Econometrica, 55(3), 703-708.

    Andrews, D.W.K. (1991), "Heteroskedasticity and Autocorrelation Consistent
    Covariance Matrix Estimation", Econometrica, 59(3), 817-858.

Usage in the stationarity test (Section 2.4 of the paper):
    The HAC estimator provides σ̂² = σ̂²_HAC(ΔY) where ΔY_t = Y_t - Y_{t-1}.
    This estimate is used to normalize the seminorms:
        g₁_std = g₁_raw / (σ̂ · n^{c₁/2} · √d̄₁)
        g₂_std = g₂_raw / (σ̂² · √d̄₂)
    making the standardized statistic invariant to the unknown innovation scale σ.
"""

import numpy as np


def hac_newey_west(
    x: np.ndarray,
    bandwidth: int | None = None,
    andrews_pilot: str = 'alpha1'
) -> float:
    """
    Newey-West HAC estimator of the long-run variance.

    Computes σ̂² = γ₀ + 2 Σⱼ₌₁ᵐ wⱼ γⱼ  where wⱼ = 1 - j/(m+1) (Bartlett kernel)
    and γⱼ = (1/n) Σₜ (xₜ - x̄)(xₜ₋ⱼ - x̄) is the lag-j autocovariance.

    Parameters
    ----------
    x : np.ndarray
        1-D array, typically first differences ΔYₜ = Yₜ - Yₜ₋₁.
    bandwidth : int or None
        Truncation lag m for the Bartlett kernel. If None, uses the
        Andrews (1991) automatic selection: m = ceil(1.1447 * (α̂ · n)^{1/3})
        where α̂ is estimated from the first-order autocorrelation.

    Returns
    -------
    float
        HAC estimate σ̂² > 0. Floored at 1e-12 for numerical safety.

    Notes
    -----
    For iid data (white noise), the Bartlett correction is negligible and
    the estimator reduces approximately to the sample variance.
    For AR(1) with parameter ρ, the estimator corrects the naive variance
    by the factor (1+ρ)/(1-ρ), removing the ~15.5% bias at ρ=0.5.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)

    if n < 2:
        return max(np.var(x, ddof=0), 1e-12)

    x_centered = x - np.mean(x)

    # Autocovariance function γ(j) = (1/n) Σ (x_t - x̄)(x_{t-j} - x̄)
    def _autocovariance(lag: int) -> float:
        if lag >= n:
            return 0.0
        return float(np.dot(x_centered[lag:], x_centered[:n - lag]) / n)

    gamma_0 = _autocovariance(0)

    if gamma_0 < 1e-15:
        return 1e-12

    # Automatic bandwidth selection (Andrews, 1991)
    if bandwidth is None:
        # Estimate first-order autocorrelation
        gamma_1 = _autocovariance(1)
        rho_hat = gamma_1 / gamma_0 if gamma_0 > 0 else 0.0
        rho_hat = np.clip(rho_hat, -0.99, 0.99)

        # Andrews formula for Bartlett kernel (Andrews 1991, Table I)
        if andrews_pilot == "alpha1":
            alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat**2)**2, 1e-10)
        elif andrews_pilot == "alpha2":
            alpha_hat = (4.0 * rho_hat**2) / max((1.0 - rho_hat)**4, 1e-10)
        else:
            raise ValueError(f"andrews_pilot must be 'alpha1' or 'alpha2', not {andrews_pilot!r}")

        # Optimal bandwidth: m = ceil(1.1447 * (α̂ · n)^{1/3})
        bandwidth = int(np.ceil(1.1447 * (alpha_hat * n) ** (1.0 / 3.0)))

    # Enforce reasonable bounds
    bandwidth = max(0, min(bandwidth, n - 1))

    # HAC estimate with Bartlett kernel
    sigma_sq = gamma_0
    for j in range(1, bandwidth + 1):
        w_j = 1.0 - j / (bandwidth + 1)  # Bartlett weight
        gamma_j = _autocovariance(j)
        sigma_sq += 2.0 * w_j * gamma_j

    # Floor at 1e-12 (must be positive for division)
    return max(float(sigma_sq), 1e-12)
