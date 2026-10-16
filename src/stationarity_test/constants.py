"""
Mathematical constants for the stationarity test.

This module contains all immutable constants referenced in the paper's glossary.
Any constant not listed here must NOT appear in the codebase.

Notation follows the Strict Mathematical Glossary (docs/glossary.md).
"""

import numpy as np

# ---------------------------------------------------------------------------
# Calibration constant C = 1 / E[sqrt(int_0^1 tilde{W}(s)^2 ds)]
# where tilde{W}(s) = W(s) - int_0^1 W(u) du is the centered Brownian motion.
# Numerical value computed to 6 significant digits.
# ---------------------------------------------------------------------------
CALIBRATION_CONSTANT_C: float = 2.6600

# ---------------------------------------------------------------------------
# Analytical eigenvalues of the centered Brownian motion covariance operator.
# lambda_k = 1 / (k * pi)^2,  k = 1, 2, 3, ...
# These are the eigenvalues of the integral operator with kernel
# K(s, t) = min(s, t) - s*t  on [0, 1].
# ---------------------------------------------------------------------------
def centered_brownian_eigenvalue(k: int) -> float:
    """
    Exact eigenvalue lambda_k = 1/(k*pi)^2 of the centered Brownian
    covariance operator.

    Parameters
    ----------
    k : int
        Index, k >= 1.

    Returns
    -------
    float
        The k-th eigenvalue.
    """
    if k < 1:
        raise ValueError(f"Eigenvalue index must be >= 1, got {k}")
    return 1.0 / (k * np.pi) ** 2


def centered_brownian_eigenvalues(K: int) -> np.ndarray:
    """
    First K eigenvalues of the centered Brownian covariance operator,
    in decreasing order.

    Parameters
    ----------
    K : int
        Number of eigenvalues to compute, K >= 1.

    Returns
    -------
    np.ndarray
        Array of shape (K,) with eigenvalues in decreasing order.
    """
    if K < 1:
        raise ValueError(f"K must be >= 1, got {K}")
    ks = np.arange(1, K + 1, dtype=np.float64)
    return 1.0 / (ks * np.pi) ** 2


# ---------------------------------------------------------------------------
# Cramér–von Mises reference quantiles.
#
# The classical CvM statistic omega^2 = int_0^1 tilde{W}(s)^2 ds has
# distribution sum_{k=1}^inf xi_k^2 / (k*pi)^2 with xi_k ~ N(0,1) iid.
#
# IMPORTANT (Audit §3.3): Our functional F_2^1(W) = sqrt(int_0^1 tilde{W}^2 ds)
# is the ROOT of the CvM statistic, not the quadratic form itself.
# Reference quantiles are therefore square roots of the published values.
# ---------------------------------------------------------------------------

# Published quantiles of the QUADRATIC CvM statistic omega^2
# (Anderson & Darling, 1952; Stephens, 1986)
CVM_QUADRATIC_QUANTILES: dict[float, float] = {
    0.90: 0.3473,
    0.95: 0.4614,
    0.99: 0.7434,
}

# Quantiles of the ROOT CvM statistic sqrt(omega^2) — OUR reference values
CVM_ROOT_QUANTILES: dict[float, float] = {
    0.90: np.sqrt(0.3473),   # ≈ 0.5893
    0.95: np.sqrt(0.4614),   # ≈ 0.6793
    0.99: np.sqrt(0.7434),   # ≈ 0.8622
}

# ---------------------------------------------------------------------------
# Default scaling exponents c_i (Decision D3).
#
# Under H0 (random walk with Gaussian innovations):
#   - Component 1 (rolling mean):     g_1^tau(Y) = Theta_p(sigma * sqrt(n))  => c_1 = 1
#   - Component 2 (rolling variance): g_2^tau(Y) = Theta_p(sigma^2 * n)      => c_2 = 2
#
# Empirically verified: E[g2/(sigma^2 * n * d_bar_2)] ~ 0.95 for all n.
# The original paper specification c_2=0 was incorrect for the null hypothesis;
# the random walk's local variance grows linearly with window size tau = theta*n,
# causing g2_raw = O(n) rather than O(1).
# ---------------------------------------------------------------------------
DEFAULT_SCALING_EXPONENTS: dict[int, float] = {
    1: 1.0,  # c_1 = 1: g1 scales as sigma * sqrt(n)
    2: 2.0,  # c_2 = 2: g2 scales as sigma^2 * n
}

# ---------------------------------------------------------------------------
# Domain constraints from the glossary.
# ---------------------------------------------------------------------------
MIN_SAMPLE_SIZE: int = 60          # n >= 60
THETA_DOMAIN: tuple[float, float] = (0.0, 0.5)  # theta in (0, 1/2], open at 0
R_DOMAIN: tuple[float, float] = (0.0, 1.0)       # R in [0, 1]
