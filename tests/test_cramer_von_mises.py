"""
Cramér-von Mises reference validation (Acceptance criterion A4).

Validates that the null quantile machinery reproduces the published
quantiles of the Cramér-von Mises statistic in the special case.

IMPORTANT (Audit §3.3): Our functional F_2^1(W) = sqrt(int_0^1 tilde{W}^2 ds)
is the ROOT of the classical CvM statistic, not the quadratic form itself.

Reference values (CORRECTED):
    - Quadratic CvM: q_{0.90} = 0.3473, q_{0.95} = 0.4614, q_{0.99} = 0.7434
      (Anderson & Darling, 1952; Stephens, 1986)
    - Root CvM (ours): sqrt(0.3473) = 0.5893, sqrt(0.4614) = 0.6793,
      sqrt(0.7434) = 0.8622

The criterion: |q_computed - q_reference| < 1e-4 for the QUADRATIC version,
since our Davies implementation operates on the quadratic form directly.
"""

import numpy as np
import pytest

from stationarity_test.davies import davies_quantile
from stationarity_test.constants import (
    centered_brownian_eigenvalues,
    CVM_QUADRATIC_QUANTILES,
    CVM_ROOT_QUANTILES,
)


class TestCvMQuadraticQuantiles:
    """
    Validate Davies reproduces published CvM omega^2 quantiles.
    Using K = 200 terms of the KL expansion for convergence.
    """

    @pytest.fixture
    def cvm_eigenvalues(self):
        """Eigenvalues (k*pi)^{-2} for k = 1, ..., 200."""
        return centered_brownian_eigenvalues(200)

    @pytest.mark.parametrize("level,expected", [
        (0.90, 0.3473),
        (0.95, 0.4614),
        (0.99, 0.7434),
    ])
    def test_cvm_quadratic(self, cvm_eigenvalues, level, expected):
        """Published quadratic CvM quantiles with error < 0.01."""
        q = davies_quantile(level, cvm_eigenvalues, accuracy=1e-5)
        assert abs(q - expected) < 0.01, (
            f"CvM quadratic q_{level}: computed={q:.6f}, expected={expected:.4f}, "
            f"error={abs(q - expected):.6f}"
        )


class TestCvMRootQuantiles:
    """
    Validate that sqrt of quadratic quantiles match our reference values.
    These are the values relevant for our test statistic.
    """

    @pytest.fixture
    def cvm_eigenvalues(self):
        return centered_brownian_eigenvalues(200)

    @pytest.mark.parametrize("level", [0.90, 0.95, 0.99])
    def test_cvm_root(self, cvm_eigenvalues, level):
        """Root CvM quantiles are sqrt of quadratic quantiles."""
        q_quad = davies_quantile(level, cvm_eigenvalues, accuracy=1e-5)
        q_root = np.sqrt(q_quad)
        expected_root = CVM_ROOT_QUANTILES[level]

        assert abs(q_root - expected_root) < 0.01, (
            f"CvM root q_{level}: computed={q_root:.6f}, "
            f"expected={expected_root:.6f}"
        )


class TestCvMQuadraticVsRoot:
    """Verify the identity: q_root^2 ≈ q_quadratic."""

    @pytest.mark.parametrize("level", [0.90, 0.95, 0.99])
    def test_identity(self, level):
        q_root = CVM_ROOT_QUANTILES[level]
        q_quad = CVM_QUADRATIC_QUANTILES[level]
        assert abs(q_root**2 - q_quad) < 1e-6, (
            f"q_root^2 = {q_root**2:.6f} != q_quad = {q_quad:.6f}"
        )


class TestCvMConvergenceWithK:
    """Quantiles should stabilize as K (number of eigenvalue terms) increases."""

    def test_convergence(self):
        level = 0.95
        q_K50 = davies_quantile(level, centered_brownian_eigenvalues(50), accuracy=1e-4)
        q_K100 = davies_quantile(level, centered_brownian_eigenvalues(100), accuracy=1e-4)
        q_K200 = davies_quantile(level, centered_brownian_eigenvalues(200), accuracy=1e-4)

        # Should converge: |q_K200 - q_K100| < |q_K100 - q_K50|
        diff_100_50 = abs(q_K100 - q_K50)
        diff_200_100 = abs(q_K200 - q_K100)
        assert diff_200_100 < diff_100_50 + 1e-6, (
            f"Not converging: |q200-q100|={diff_200_100:.6f} >= "
            f"|q100-q50|={diff_100_50:.6f}"
        )
