"""
Module F2.B: Optimal weight R* by maximum likelihood.

Implements the adaptive weight selection from Section 2.7 of the paper:

    R̂ = [g₂_std]² / ([g₁_std]² + [g₂_std]²)

This formula arises from the first-order condition of the local MLE
under the mixed local alternatives model. It auto-balances between
mean and variance components: R̂ → 0 when non-stationarity is purely
in mean, R̂ → 1 when purely in variance.

The oracle version (for validation) computes the theoretical R* when
the alternative parameters (c₁, d₁) are known.
"""

import numpy as np


def compute_optimal_R(
    g1_std: float,
    g2_std: float,
    method: str = 'adaptive',
) -> dict:
    """
    Compute the optimal combination weight R*.

    Parameters
    ----------
    g1_std : float
        Standardized component 1 (rolling mean seminorm).
    g2_std : float
        Standardized component 2 (rolling variance seminorm).
    method : str
        'adaptive' : empirical MLE formula R̂ = g₂²/(g₁²+g₂²)
        'fixed'    : returns R = 0.5 (baseline for comparison)

    Returns
    -------
    dict
        {
            'R_star': float,       # optimal weight in [0, 1]
            'method': str,         # method used
            'fisher_ratio': float  # g₂²/(g₁²+g₂²) regardless of method
        }

    Raises
    ------
    ValueError
        If method is not recognized.
    """
    if method not in ('adaptive', 'fixed'):
        raise ValueError(f"method must be 'adaptive' or 'fixed', got '{method}'")

    g1_sq = g1_std**2
    g2_sq = g2_std**2
    denom = g1_sq + g2_sq

    # Fisher ratio (always computed for diagnostics)
    if denom < 1e-12:
        fisher_ratio = 0.5  # degenerate: both components near zero
    else:
        fisher_ratio = g2_sq / denom

    if method == 'adaptive':
        R_star = fisher_ratio
    else:  # 'fixed'
        R_star = 0.5

    return {
        'R_star': float(np.clip(R_star, 0.0, 1.0)),
        'method': method,
        'fisher_ratio': float(fisher_ratio),
    }


def oracle_R(
    c1: float,
    d1: float,
) -> float:
    """
    Compute theoretical R* when alternative parameters are known.

    Under the local alternatives model:
        H_A: ρ_n = 1 - c₁/n,  Var(ε_t) = σ²(1 + d₁/n)

    The optimal weight is:
        R* = d₁ / (c₁ + d₁)

    This simplified form assumes I₁₁ ≈ I₂₂ (equal Fisher information
    per unit of departure). For validation only.

    Parameters
    ----------
    c1 : float
        Intensity of mean non-stationarity (c₁ ≥ 0).
    d1 : float
        Intensity of variance non-stationarity (d₁ ≥ 0).

    Returns
    -------
    float
        Theoretical R* in [0, 1].
    """
    if c1 < 0 or d1 < 0:
        raise ValueError(f"c1 and d1 must be non-negative, got c1={c1}, d1={d1}")

    total = c1 + d1
    if total < 1e-12:
        return 0.5  # degenerate: no non-stationarity

    return float(d1 / total)
