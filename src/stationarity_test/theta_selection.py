"""
Module F2.A: Spectral selection of optimal window parameter θ*.

For each component (mean or variance), selects the smallest θ that produces
a persistent spectral peak in the auxiliary rolling series, indicating
detectable temporal structure at that scale.

The selection criterion is:
    θ* = smallest θ such that the normalized spectral peak A(θ) exceeds
    a data-driven threshold A_min (calibrated as the 0.95 quantile of A
    under white noise) and is a persistent local maximum (exceeds w=3
    neighbors on each side).

If no persistent peak is found, defaults to θ* = 0.5 (maximum window,
most conservative choice).
"""

import numpy as np

from stationarity_test.utils import (
    validate_series,
    validate_theta,
    rolling_mean,
    rolling_var,
)


def select_theta(
    Y: np.ndarray,
    component: int,
    theta_grid: np.ndarray | None = None,
    persistence_width: int = 3,
    A_min: float | None = None,
    n_calibration_sims: int = 500,
    seed: int | None = None,
) -> dict:
    """
    Select optimal window parameter θ* by spectral criterion.

    For a given component (1=mean, 2=variance), computes the rolling
    statistic at each candidate θ, takes its FFT to measure spectral
    concentration, and selects the smallest θ with a persistent peak
    above the noise threshold.

    Parameters
    ----------
    Y : np.ndarray
        Observed time series of shape (n+1,).
    component : int
        1 for rolling mean, 2 for rolling variance.
    theta_grid : np.ndarray or None
        Grid of candidate θ values in (0, 0.5]. If None, auto-generated.
    persistence_width : int
        Number of neighbors w on each side for peak persistence check.
    A_min : float or None
        Minimum spectral amplitude threshold. If None, auto-calibrated
        as the 0.95 quantile of max spectral amplitude under white noise.
    n_calibration_sims : int
        Number of white noise simulations for A_min calibration.
    seed : int or None
        Random seed for calibration simulations.

    Returns
    -------
    dict
        {
            'theta_star': float,          # selected θ*
            'A_max': float,               # spectral amplitude at θ*
            'spectral_profile': np.ndarray,  # A(θ) for all θ in grid
            'theta_grid': np.ndarray,     # the grid used
            'A_min': float                # threshold used
        }

    Raises
    ------
    ValueError
        If component is not 1 or 2.
    """
    if component not in (1, 2):
        raise ValueError(f"component must be 1 or 2, got {component}")

    validate_series(Y)
    n = len(Y) - 1

    # Build theta grid
    if theta_grid is None:
        n_grid = min(200, n // 4)
        n_grid = max(n_grid, 10)
        theta_grid = np.linspace(2.0 / n, 0.5, num=n_grid)

    # Ensure theta values are valid
    theta_grid = theta_grid[(theta_grid > 0) & (theta_grid <= 0.5)]

    # Compute spectral amplitude A(θ) for each candidate
    spectral_profile = np.empty(len(theta_grid), dtype=np.float64)
    for idx, theta in enumerate(theta_grid):
        spectral_profile[idx] = _spectral_amplitude(Y, theta, n, component)

    # Calibrate A_min if needed
    if A_min is None:
        A_min = _calibrate_threshold(
            n, component, theta_grid, n_calibration_sims, seed
        )

    # Find persistent peaks
    w = persistence_width
    peaks = []
    for j in range(w, len(theta_grid) - w):
        is_peak = True
        for m in range(1, w + 1):
            if spectral_profile[j] <= spectral_profile[j - m]:
                is_peak = False
                break
            if spectral_profile[j] <= spectral_profile[j + m]:
                is_peak = False
                break
        if is_peak and spectral_profile[j] > A_min:
            peaks.append(j)

    # Select smallest θ with a persistent peak
    if peaks:
        best_idx = peaks[0]  # smallest θ
        theta_star = float(theta_grid[best_idx])
        A_max = float(spectral_profile[best_idx])
    else:
        # Default: θ = 0.5 (conservative, maximum window)
        theta_star = 0.5
        A_max = float(spectral_profile[-1]) if len(spectral_profile) > 0 else 0.0

    return {
        'theta_star': theta_star,
        'A_max': A_max,
        'spectral_profile': spectral_profile,
        'theta_grid': theta_grid,
        'A_min': float(A_min),
    }


def _spectral_amplitude(
    Y: np.ndarray,
    theta: float,
    n: int,
    component: int,
) -> float:
    """
    Compute the maximum normalized spectral amplitude of the rolling
    statistic at scale θ.

    The spectral amplitude A(θ) = max_f |Ŝ(f)|² / Σ|Ŝ(f)|² measures
    how concentrated the spectral energy is at a single frequency.
    High A indicates periodic/structured variation; low A indicates noise.
    """
    tau = max(2, int(round(theta * n)))
    tau = min(tau, n // 2)

    if component == 1:
        series = rolling_mean(Y, tau)
    else:
        series = rolling_var(Y, tau)

    if len(series) < 4:
        return 0.0

    # Demean
    series = series - np.mean(series)

    # FFT (one-sided periodogram)
    fft_vals = np.abs(np.fft.rfft(series))**2
    # Skip DC component (index 0)
    fft_vals = fft_vals[1:]

    total_power = np.sum(fft_vals)
    if total_power < 1e-30:
        return 0.0

    # Normalized max amplitude
    return float(np.max(fft_vals) / total_power)


def _calibrate_threshold(
    n: int,
    component: int,
    theta_grid: np.ndarray,
    n_sims: int,
    seed: int | None,
) -> float:
    """
    Calibrate A_min as the 0.95 quantile of max spectral amplitude
    under white noise.

    Under the null of white noise, the rolling statistics should show
    no concentrated spectral structure. A_min is set so that only 5%
    of white noise realizations would produce a peak above it.
    """
    rng = np.random.default_rng(seed)
    max_amplitudes = np.empty(n_sims, dtype=np.float64)

    for sim in range(n_sims):
        # Generate white noise of same length
        z = rng.standard_normal(n + 1)

        # Compute max A(θ) over the grid
        best_A = 0.0
        for theta in theta_grid:
            A = _spectral_amplitude(z, theta, n, component)
            if A > best_A:
                best_A = A
        max_amplitudes[sim] = best_A

    return float(np.quantile(max_amplitudes, 0.95))
