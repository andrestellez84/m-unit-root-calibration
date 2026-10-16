"""
Stationarity Test — Asymptotically exact stationarity test for time series.

Phases 1 & 2: Complete test pipeline with automatic parameter selection.

This package implements the computational infrastructure for the stationarity
test based on adaptive seminorms with asymptotically exact null distribution
derived via Donsker's theorem and Karhunen-Loève expansions.

Architectural decisions (D1-D5):
    D1: Quadratic combination statistic g_R = sqrt((1-R)^2 g1^2 + R^2 g2^2)
    D2: g_2 operates on [sigma_k^tau]^2 (variances, not std deviations)
    D3: Scaling exponents c_i configurable (defaults: c1=1, c2=0)
    D4: Davies Algorithm AS 155 for quadratic form distributions
    D5: Quantitative KS acceptance criterion D_N <= 1.63/sqrt(N_sim)

Phase 2 additions:
    - HAC (Newey-West) estimator for sigma-hat
    - Spectral theta selection (auto window parameter)
    - Adaptive R* by MLE (auto combination weight)
    - Full pipeline: stationarity_test(Y) → p-value
"""

from stationarity_test.constants import (
    CALIBRATION_CONSTANT_C,
    CVM_ROOT_QUANTILES,
    DEFAULT_SCALING_EXPONENTS,
)
from stationarity_test.kl_eigenvalues import compute_eigenvalues
from stationarity_test.empirical_eigenvalues import build_null_cdf, build_null_cdf_adaptive
from stationarity_test.standardization import standardization_factor
from stationarity_test.davies import davies_cdf, davies_quantile
from stationarity_test.null_quantiles import null_cdf, null_quantile
from stationarity_test.statistic import compute_statistic
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.theta_selection import select_theta
from stationarity_test.optimal_weight import compute_optimal_R, oracle_R
from stationarity_test.full_pipeline import stationarity_test

__version__ = "0.3.0"

__all__ = [
    # Constants
    "CALIBRATION_CONSTANT_C",
    "CVM_ROOT_QUANTILES",
    "DEFAULT_SCALING_EXPONENTS",
    # Eigenvalues
    "compute_eigenvalues",      # analytical (KL) — for verification
    "build_null_cdf",           # empirical null CDF — operational
    "build_null_cdf_adaptive",  # adaptive-R empirical null CDF
    "standardization_factor",
    # Distribution
    "davies_cdf",
    "davies_quantile",
    "null_cdf",
    "null_quantile",
    "compute_statistic",
    # Phase 2
    "hac_newey_west",
    "select_theta",
    "compute_optimal_R",
    "oracle_R",
    "stationarity_test",
]
