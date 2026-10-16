"""
Module F1.C: Null distribution CDF and quantiles.

Computes the CDF and quantiles of the null distribution G_R^{theta}(W)
under H0 (random walk).

The null distribution is estimated empirically by simulating the
combined statistic under H0. This approach correctly captures the
inter-component correlation between g1 and g2 (which share the same
trajectory), unlike the eigenvalue-based model which assumes independence.

The empirical CDF with N_cal = 10000 provides resolution ~0.01%,
sufficient for the KS acceptance criterion D_N <= 0.0163.

The Monte Carlo fallback (null_quantile_mc) simulates Brownian paths
for comparison with the continuous-limit distribution.

Notation follows the Strict Mathematical Glossary (docs/glossary.md).
"""

import numpy as np

from stationarity_test.empirical_eigenvalues import (
    null_cdf_empirical,
    null_quantile_empirical,
    build_null_cdf,
)
from stationarity_test.utils import (
    validate_theta_pair,
    validate_R,
    simulate_brownian,
)


def null_cdf(
    v: float,
    theta: tuple[float, float],
    R: float,
    n: int,
    eps: float = 1e-6,
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
    andrews_pilot: str = "alpha1",
) -> float:
    """
    Evaluate the CDF of the null distribution: F_G(v) = P(tilde{G}_R^theta(W) <= v).

    Uses the empirical null distribution estimated by Monte Carlo
    simulation of the combined statistic under H0 (sigma=1 random walk).

    Parameters
    ----------
    v : float
        Point at which to evaluate the CDF.
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2).
    R : float
        Combination weight in [0, 1].
    n : int
        Sample size (number of increments).
    eps : float
        Numerical tolerance (unused, kept for API compatibility).

    Returns
    -------
    float
        CDF value F_G(v) in [0, 1].
    """
    validate_theta_pair(theta)
    validate_R(R)

    if v <= 0:
        return 0.0

    return null_cdf_empirical(v, theta, R, n, deterministics=deterministics, detrend=detrend,
                              cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                              andrews_pilot=andrews_pilot)


def null_quantile(
    theta: tuple[float, float],
    R: float,
    alpha: float,
    n: int,
    eps: float = 1e-6,
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
    andrews_pilot: str = "alpha1",
) -> float:
    """
    Compute lower-tail quantile q_alpha of the null distribution.

    q_alpha is such that P(tilde{G}_R^theta(W) <= q_alpha) = alpha.
    Reject H0 when the observed statistic is <= q_alpha (lower tail).

    Parameters
    ----------
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2).
    R : float
        Combination weight in [0, 1].
    alpha : float
        Significance level in (0, 1). Typical: 0.01, 0.05, 0.10.
    n : int
        Sample size (number of increments).
    eps : float
        Numerical tolerance (unused, kept for API compatibility).

    Returns
    -------
    float
        Critical value q_alpha (lower-tail threshold).
    """
    validate_theta_pair(theta)
    validate_R(R)
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")

    return null_quantile_empirical(theta, R, alpha, n, deterministics=deterministics, detrend=detrend,
                                   cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                                   andrews_pilot=andrews_pilot)


def null_quantile_mc(
    theta: tuple[float, float],
    R: float,
    alpha: float,
    n_sims: int = 10**6,
    M_mesh: int = 2000,
    seed: int | None = None,
) -> float:
    """
    Compute quantile by Monte Carlo simulation of the full Brownian path.

    IMPORTANT (Audit §3.2): This simulates the entire Brownian trajectory
    W(s) on a fine mesh and evaluates BOTH functionals on the SAME path.
    DO NOT use independent xi_k vectors for each component — this would
    produce incorrect null distribution due to spurious decorrelation.

    Parameters
    ----------
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2).
    R : float
        Combination weight in [0, 1].
    alpha : float
        Significance level in (0, 1).
    n_sims : int
        Number of Brownian paths to simulate.
    M_mesh : int
        Number of mesh points for each Brownian path.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    float
        Empirical quantile q_{1-alpha}.
    """
    validate_theta_pair(theta)
    validate_R(R)

    rng = np.random.default_rng(seed)
    samples = np.empty(n_sims, dtype=np.float64)

    ds = 1.0 / M_mesh
    s_grid = np.linspace(0.0, 1.0, M_mesh + 1)

    theta_1, theta_2 = theta

    for sim in range(n_sims):
        # Simulate one Brownian path
        increments = rng.standard_normal(M_mesh) * np.sqrt(ds)
        W = np.empty(M_mesh + 1, dtype=np.float64)
        W[0] = 0.0
        np.cumsum(increments, out=W[1:])

        # Evaluate F_1^{theta_1}(W): sqrt(Var_u[W_bar_u^theta_1])
        F1_val = _evaluate_F1_on_path(W, s_grid, theta_1, M_mesh)

        # Evaluate F_2^{theta_2}(W): sqrt(Var_u[[S_theta_2(u)]^2])
        F2_val = _evaluate_F2_on_path(W, s_grid, theta_2, M_mesh)

        # Combine quadratically (D1)
        G = np.sqrt((1.0 - R)**2 * F1_val**2 + R**2 * F2_val**2)
        samples[sim] = G

    return float(np.quantile(samples, alpha))


def _evaluate_F1_on_path(
    W: np.ndarray,
    s_grid: np.ndarray,
    theta: float,
    M: int
) -> float:
    """
    Evaluate F_1^theta(W) = sqrt(Var_u[W_bar_u^theta]) on a Brownian path.

    W_bar_u^theta = (1/theta) * int_u^{u+theta} W(s) ds
    """
    ds = 1.0 / M
    window_points = max(1, int(round(theta * M)))

    # Number of u positions
    n_u = M - window_points + 1
    if n_u < 2:
        return 0.0

    # Compute rolling means of W using cumulative sums
    cumsum_W = np.cumsum(W)
    # int_u^{u+theta} W(s) ds ≈ ds * sum of W values in window
    # W_bar_u = (1/theta) * ds * sum_{j in window} W[j]
    # = sum_{j=start}^{start+window_points-1} W[j] / window_points

    means = np.empty(n_u, dtype=np.float64)
    for k in range(n_u):
        window_sum = 0.0
        for j in range(k, k + window_points):
            window_sum += W[j]
        means[k] = window_sum / window_points

    # Var_u of the means
    var_means = np.var(means, ddof=1) if n_u > 1 else 0.0
    return np.sqrt(max(var_means, 0.0))


def _evaluate_F2_on_path(
    W: np.ndarray,
    s_grid: np.ndarray,
    theta: float,
    M: int
) -> float:
    """
    Evaluate F_2^theta(W) = sqrt(Var_u[[S_theta(u)]^2]) on a Brownian path.

    S_theta(u)^2 = (1/theta) * int_u^{u+theta} (W(s) - W_bar_u^theta)^2 ds

    Under D2, we operate on the VARIANCE [S_theta(u)]^2, not the std dev.
    """
    window_points = max(1, int(round(theta * M)))

    n_u = M - window_points + 1
    if n_u < 2:
        return 0.0

    # Compute [S_theta(u)]^2 for each u
    variances = np.empty(n_u, dtype=np.float64)
    for k in range(n_u):
        # Window: W[k], W[k+1], ..., W[k+window_points-1]
        window = W[k:k + window_points]
        mean_w = np.mean(window)
        var_w = np.mean((window - mean_w)**2)  # population variance (1/theta integral)
        variances[k] = var_w

    # Var_u of the variances
    var_of_var = np.var(variances, ddof=1) if n_u > 1 else 0.0
    return np.sqrt(max(var_of_var, 0.0))
