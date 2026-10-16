"""
Module F1.B: Standardization factors.

Evaluates the analytical standardization functions d_bar_i(theta) as spectral
sums of the Karhunen-Loève eigenvalues.

Under Decision D3, the scaling exponents c_i are configurable parameters
with defaults c_1 = 1 (rolling mean) and c_2 = 0 (rolling variance).

The standardization factors bring both components to the same asymptotic
scale Theta_p(1) before combining them into the quadratic statistic (D1).

DEPRECATED: This module implements an abandoned architecture for standardization
factors and is NOT in the production path (it is retained for historical
reference only). The docstring mentioning c_2 = 0 contradicts the paper
(where c_2 = 2). See `constants.py` for the correct and current scaling exponents.

Notation follows the Strict Mathematical Glossary (docs/glossary.md).
"""

import numpy as np

from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.kl_eigenvalues import compute_eigenvalues
from stationarity_test.utils import validate_theta


def standardization_factor(
    theta: float,
    component: int,
    c_i: float | None = None,
    eps: float = 1e-6
) -> float:
    """
    Compute the analytical standardization factor d_bar_i(theta).

    d_bar_i(theta) = lim_{n -> inf} d_i(theta * n, n) / n^{c_i}

    This factor is used to normalize the i-th seminorm so that the
    standardized version is Theta_p(1) under H0.

    Parameters
    ----------
    theta : float
        Window parameter in (0, 1/2].
    component : int
        1 for rolling mean component, 2 for rolling variance component.
    c_i : float or None
        Scaling exponent. If None, uses defaults from D3:
        component 1 -> c_1 = 1, component 2 -> c_2 = 0.
    eps : float
        Tolerance for numerical error.

    Returns
    -------
    float
        Standardization factor d_bar_i(theta) > 0.

    Raises
    ------
    ValueError
        If theta or component is invalid.

    Notes
    -----
    Both components use the same formula:
        d_bar_i(theta) = sqrt(sum_k lambda_k^{(i, theta)})
        This is the square root of the trace of the covariance operator,
        which equals sqrt(E[Q_i]) where Q_i = sum_k lambda_k * Z_k^2.

    Our functional is F_i = sqrt(Q_i), so E[F_i] ~ sqrt(E[Q_i]) = d_bar_i
    by Jensen's approximation. This ensures F_i / d_bar_i is O(1).
    """
    validate_theta(theta)
    if component not in (1, 2):
        raise ValueError(f"component must be 1 or 2, got {component}")

    # Resolve scaling exponent
    if c_i is None:
        c_i = DEFAULT_SCALING_EXPONENTS[component]

    # Determine initial K from tolerance
    K = max(50, int(np.ceil(1.0 / np.sqrt(eps))))

    # Get eigenvalues
    eigenvalues, truncation_bound = compute_eigenvalues(
        theta, component, K=K, eps=eps
    )

    # Remove numerical zeros
    eigenvalues = eigenvalues[eigenvalues > 0]

    # d_bar_i = sqrt(trace) = sqrt(sum lambda_k)
    # This is sqrt(E[Q]) where Q = sum lambda_k * Z_k^2.
    # Our functional F_i = sqrt(Q), so E[F_i] ~ sqrt(E[Q]) = d_bar_i.
    factor = np.sqrt(np.sum(eigenvalues))

    if factor <= 0:
        raise RuntimeError(
            f"Standardization factor is non-positive ({factor}) for "
            f"theta={theta}, component={component}. This indicates a "
            f"numerical issue in the eigenvalue computation."
        )

    return float(factor)
