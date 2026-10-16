"""
Module: Empirical null distribution for the combined statistic.

Estimates the null CDF of the combined statistic
    stat = sqrt((1-R)^2 * g1_std^2 + R^2 * g2_std^2)
by Monte Carlo simulation under H0 (random walk with sigma=1).

The critical finding is that g1 and g2 are computed from the SAME
random walk trajectory, creating inter-component correlation that a
model based on independent chi-squared mixtures cannot capture.
Estimating the distribution of the combined statistic directly
(rather than combining eigenvalues from individual components)
resolves this issue.

The empirical distribution is stored as a sorted array of null
statistic values, and the CDF is computed by interpolation.
With N_cal = 10000, the CDF resolution is ~0.01%, more than
sufficient for the KS threshold of 0.0163.
"""

import numpy as np
from scipy.interpolate import interp1d

from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.deterministics import apply_deterministics, validate_deterministics
from stationarity_test.rm_core import hac_sigma_sq, path_statistic, validate_variant


def _simulate_null_statistics(
    theta: tuple[float, float],
    R: float,
    n: int,
    N_cal: int,
    seed: int,
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
    andrews_pilot: str = "alpha1",
) -> np.ndarray:
    """
    Simulate N_cal realizations of the combined statistic under H0.

    Default (cal_sigma="one"): uses sigma=1 (known) for standardization, not HAC
    estimation (Definition 1 of the paper). cal_sigma="hac" computes sigma_hat
    on every simulated path with the same HAC routine as the data. tau_mode and
    anchor select the rolling-mean variant (see rm_core). The default branch is
    the original code, unchanged.

    Parameters
    ----------
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2).
    R : float
        Combination weight in [0, 1].
    n : int
        Sample size (number of increments).
    N_cal : int
        Number of calibration replications.
    seed : int
        RNG seed.

    Returns
    -------
    np.ndarray
        Array of shape (N_cal,) with simulated statistic values.
    """
    c_1 = DEFAULT_SCALING_EXPONENTS[1]  # = 1.0
    c_2 = DEFAULT_SCALING_EXPONENTS[2]  # = 2.0
    validate_deterministics(deterministics, detrend)
    validate_variant(cal_sigma, tau_mode, anchor, detrend)

    theta_1, theta_2 = theta
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    rng = np.random.default_rng(seed)
    stats = np.empty(N_cal, dtype=np.float64)

    if (cal_sigma, tau_mode, anchor) != ("one", "theta", "mean"):
        if tau_mode == "zero":
            tau_1 = 0
        for j in range(N_cal):
            innovations = rng.standard_normal(n)
            Y = np.empty(n + 1, dtype=np.float64)
            Y[0] = 0.0
            np.cumsum(innovations, out=Y[1:])
            s2 = 1.0 if cal_sigma == "one" else hac_sigma_sq(Y, andrews_pilot)
            stats[j] = path_statistic(Y, n, tau_1, tau_2, R, s2, c_1, c_2,
                                      deterministics=deterministics, detrend=detrend,
                                      anchor=anchor, need_g2=(R != 0.0))[0]
        return stats

    # Standardization with sigma=1 (known)
    scale_1 = 1.0 * n ** (c_1 / 2.0)  # sigma * n^{c1/2}
    scale_2 = 1.0 * n ** (c_2 / 2.0)  # sigma^2 * n^{c2/2}

    for j in range(N_cal):
        innovations = rng.standard_normal(n)
        Y = np.empty(n + 1, dtype=np.float64)
        Y[0] = 0.0
        np.cumsum(innovations, out=Y[1:])
        if deterministics == "ct":
            # Random walk detrended exactly as the observed series ("c": untouched)
            Y = apply_deterministics(Y, deterministics, detrend)

        # Raw seminorms
        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))

        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

        # Standardize (sigma=1 exactly)
        g1_std = g1_raw / scale_1
        g2_std = g2_raw / scale_2

        # Combined statistic
        stats[j] = np.sqrt((1.0 - R)**2 * g1_std**2 + R**2 * g2_std**2)

    return stats


# Cache: CDF interpolators keyed by every argument of build_null_cdf that
# changes the null sample (see build_null_cdf)
_cdf_cache: dict[tuple, interp1d] = {}


def _seed_key(seed) -> tuple:
    """Hashable identity of an RNG seed (int or numpy SeedSequence)."""
    if isinstance(seed, np.random.SeedSequence):
        return ("SeedSequence", repr(seed.entropy), tuple(seed.spawn_key), seed.pool_size)
    return ("int", int(seed))


def cdf_from_null_stats(null_stats: np.ndarray) -> interp1d:
    """Empirical CDF (linear interpolation) of a sample of null statistics."""
    null_stats_sorted = np.sort(null_stats)
    N_cal = len(null_stats_sorted)
    ecdf_y = np.arange(1, N_cal + 1) / N_cal
    return interp1d(
        null_stats_sorted, ecdf_y,
        kind='linear',
        bounds_error=False,
        fill_value=(0.0, 1.0),
    )


def build_null_cdf(
    theta: tuple[float, float],
    R: float,
    n: int,
    N_cal: int = 10000,
    seed: int = 42,
    use_cache: bool = True,
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
    andrews_pilot: str = "alpha1",
) -> interp1d:
    """
    Build an interpolated CDF for the null distribution of the combined
    statistic at a given (theta, R, n) and deterministic specification.

    Parameters
    ----------
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2).
    R : float
        Combination weight in [0, 1].
    n : int
        Sample size (number of increments).
    N_cal : int
        Number of calibration simulations.
    seed : int
        RNG seed for reproducibility.
    use_cache : bool
        If True, cache and reuse results.

    Returns
    -------
    interp1d
        Interpolator: statistic_value -> CDF_value in [0, 1].
    """
    # A8: the key holds every argument that changes the null sample. Until A8 it
    # was (theta, R, n) only, so a second call with another N_cal or seed in the
    # same process silently returned the first CDF.
    key = (tuple(round(t, 6) for t in theta), round(R, 6), n, int(N_cal), _seed_key(seed),
           deterministics, detrend, cal_sigma, tau_mode, anchor, andrews_pilot)

    if use_cache and key in _cdf_cache:
        return _cdf_cache[key]

    # Simulate null statistics
    null_stats = _simulate_null_statistics(theta, R, n, N_cal, seed,
                                           deterministics=deterministics, detrend=detrend,
                                           cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                                           andrews_pilot=andrews_pilot)
    cdf_func = cdf_from_null_stats(null_stats)

    if use_cache:
        _cdf_cache[key] = cdf_func

    return cdf_func


# ---------------------------------------------------------------------------
# Adaptive-R null distribution
# ---------------------------------------------------------------------------

def _simulate_null_statistics_adaptive(
    theta: tuple[float, float],
    n: int,
    N_cal: int,
    seed: int,
) -> np.ndarray:
    """
    Simulate N_cal realizations of the combined statistic under H0
    using an adaptive (per-path) combination weight R_hat.

    For each simulated random walk path:
        1. Compute g1_std and g2_std (with sigma=1 known).
        2. Set R_hat = g2_std^2 / (g1_std^2 + g2_std^2).
        3. Compute stat = sqrt((1 - R_hat)^2 * g1_std^2
                               + R_hat^2 * g2_std^2).

    Parameters
    ----------
    theta : tuple[float, float]
        Window parameters (theta_1, theta_2).
    n : int
        Sample size (number of increments).
    N_cal : int
        Number of calibration replications.
    seed : int
        RNG seed.

    Returns
    -------
    np.ndarray
        Array of shape (N_cal,) with simulated statistic values.
    """
    c_1 = DEFAULT_SCALING_EXPONENTS[1]  # = 1.0
    c_2 = DEFAULT_SCALING_EXPONENTS[2]  # = 2.0

    theta_1, theta_2 = theta
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    rng = np.random.default_rng(seed)
    stats = np.empty(N_cal, dtype=np.float64)

    # Standardization with sigma=1 (known)
    scale_1 = 1.0 * n ** (c_1 / 2.0)  # sigma * n^{c1/2}
    scale_2 = 1.0 * n ** (c_2 / 2.0)  # sigma^2 * n^{c2/2}

    for j in range(N_cal):
        innovations = rng.standard_normal(n)
        Y = np.empty(n + 1, dtype=np.float64)
        Y[0] = 0.0
        np.cumsum(innovations, out=Y[1:])

        # Raw seminorms
        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))

        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

        # Standardize (sigma=1 exactly)
        g1_std = g1_raw / scale_1
        g2_std = g2_raw / scale_2

        # Adaptive weight
        denom = g1_std**2 + g2_std**2
        if denom > 0.0:
            R_hat = g2_std**2 / denom
        else:
            R_hat = 0.5  # degenerate case: equal weight

        # Combined statistic with adaptive R
        stats[j] = np.sqrt(
            (1.0 - R_hat)**2 * g1_std**2 + R_hat**2 * g2_std**2
        )

    return stats


# Cache: store adaptive CDF interpolators by (theta, n)
_adaptive_cdf_cache: dict[tuple[tuple[float, float], int], interp1d] = {}


def build_null_cdf_adaptive(
    theta: tuple[float, float],
    n: int,
    N_cal: int = 10000,
    seed: int = 42,
    use_cache: bool = True,
) -> interp1d:
    """
    Build the empirical CDF of the test statistic under H0 with adaptive R.

    Under H0 (random walk), for each simulated path:
        1. Compute g1_std, g2_std using sigma=1 (known).
        2. Compute R_hat = g2_std^2 / (g1_std^2 + g2_std^2).
        3. Compute the combined statistic with that R_hat.
        4. Collect all statistics to build the empirical CDF.

    The resulting CDF depends only on (theta, n), not R.

    Parameters
    ----------
    theta : tuple[float, float]
        Trimming parameters for components 1 and 2.
    n : int
        Sample size (window length).
    N_cal : int
        Number of calibration simulations.
    seed : int
        Random seed for reproducibility.
    use_cache : bool
        If True, cache and reuse results.

    Returns
    -------
    callable
        Function cdf(v) -> probability,
        where cdf(v) = P(stat <= v | H0, adaptive R).
    """
    key = (tuple(round(t, 6) for t in theta), n, N_cal, seed)

    if use_cache and key in _adaptive_cdf_cache:
        return _adaptive_cdf_cache[key]

    # Simulate null statistics with adaptive R
    null_stats = _simulate_null_statistics_adaptive(theta, n, N_cal, seed)
    null_stats_sorted = np.sort(null_stats)

    # Build empirical CDF with linear interpolation
    ecdf_y = np.arange(1, N_cal + 1) / N_cal

    cdf_func = interp1d(
        null_stats_sorted, ecdf_y,
        kind='linear',
        bounds_error=False,
        fill_value=(0.0, 1.0),
    )

    if use_cache:
        _adaptive_cdf_cache[key] = cdf_func

    return cdf_func


def null_cdf_empirical(
    v: float,
    theta: tuple[float, float],
    R: float,
    n: int,
    N_cal: int = 10000,
    seed: int = 42,
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
    andrews_pilot: str = "alpha1",
) -> float:
    """
    Evaluate the null CDF at point v using the empirical distribution.

    Parameters
    ----------
    v : float
        Point at which to evaluate the CDF.
    theta : tuple[float, float]
        Window parameters.
    R : float
        Combination weight.
    n : int
        Sample size.
    N_cal : int
        Calibration sample size.
    seed : int
        RNG seed.

    Returns
    -------
    float
        CDF value in [0, 1].
    """
    if v <= 0:
        return 0.0

    cdf_func = build_null_cdf(theta, R, n, N_cal=N_cal, seed=seed,
                              deterministics=deterministics, detrend=detrend,
                              cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                              andrews_pilot=andrews_pilot)
    return float(cdf_func(v))


def null_quantile_empirical(
    theta: tuple[float, float],
    R: float,
    alpha: float,
    n: int,
    N_cal: int = 10000,
    seed: int = 42,
    deterministics: str = "c",
    detrend: str = "qd",
    cal_sigma: str = "one",
    tau_mode: str = "theta",
    anchor: str = "mean",
    andrews_pilot: str = "alpha1",
) -> float:
    """
    Compute the (1-alpha) quantile of the null distribution.

    Parameters
    ----------
    theta : tuple[float, float]
        Window parameters.
    R : float
        Combination weight.
    alpha : float
        Significance level.
    n : int
        Sample size.
    N_cal : int
        Calibration sample size.
    seed : int
        RNG seed.

    Returns
    -------
    float
        Critical value q_{1-alpha}.
    """
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")

    # Simulate null statistics
    null_stats = _simulate_null_statistics(theta, R, n, N_cal, seed,
                                           deterministics=deterministics, detrend=detrend,
                                           cal_sigma=cal_sigma, tau_mode=tau_mode, anchor=anchor,
                                           andrews_pilot=andrews_pilot)
    return float(np.quantile(null_stats, alpha))


def clear_cache() -> None:
    """Clear all CDF caches (fixed-R and adaptive)."""
    _cdf_cache.clear()
    _adaptive_cdf_cache.clear()


def verify_stability(
    theta: tuple[float, float],
    R: float,
    n: int,
    N_cal: int = 10000,
    seed1: int = 42,
    seed2: int = 123,
    alpha_levels: tuple = (0.01, 0.05, 0.10),
    rtol: float = 0.05,
) -> dict:
    """
    Verify stability of the null distribution across seeds.

    Compares quantiles at standard alpha levels from two independent
    calibration runs.

    Returns
    -------
    dict with keys:
        'stable': bool
        'max_rdiff': float
        'quantiles_1': dict[float, float]
        'quantiles_2': dict[float, float]
    """
    stats1 = _simulate_null_statistics(theta, R, n, N_cal, seed1)
    stats2 = _simulate_null_statistics(theta, R, n, N_cal, seed2)

    q1 = {a: float(np.quantile(stats1, 1 - a)) for a in alpha_levels}
    q2 = {a: float(np.quantile(stats2, 1 - a)) for a in alpha_levels}

    rdiffs = [abs(q1[a] - q2[a]) / max(q1[a], 1e-15) for a in alpha_levels]
    max_rdiff = max(rdiffs)

    return {
        'stable': max_rdiff < rtol,
        'max_rdiff': max_rdiff,
        'quantiles_1': q1,
        'quantiles_2': q2,
    }
