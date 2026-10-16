"""
Tests for Davies Algorithm AS 155.

Validates the CDF and quantile computation against known distributions
(chi-squared, scaled chi-squared, Cramér-von Mises).
"""

import numpy as np
import pytest
from scipy.stats import chi2

from stationarity_test.davies import davies_cdf, davies_quantile
from stationarity_test.constants import (
    centered_brownian_eigenvalues,
    CVM_QUADRATIC_QUANTILES,
)


class TestSingleChi2:
    """One eigenvalue lambda = 1 should give chi^2(1) distribution."""

    def test_cdf_at_median(self):
        eigenvalues = np.array([1.0])
        prob, bound, ifault = davies_cdf(0.4549, eigenvalues)
        expected = chi2.cdf(0.4549, df=1)
        assert abs(prob - expected) < 0.01, (
            f"Single chi2: P(Q <= 0.4549) = {prob:.6f}, expected {expected:.6f}"
        )

    def test_cdf_at_95(self):
        eigenvalues = np.array([1.0])
        x_95 = chi2.ppf(0.95, df=1)  # ≈ 3.8415
        prob, bound, ifault = davies_cdf(x_95, eigenvalues)
        assert abs(prob - 0.95) < 0.01

    def test_quantile(self):
        eigenvalues = np.array([1.0])
        q = davies_quantile(0.95, eigenvalues)
        expected = chi2.ppf(0.95, df=1)
        assert abs(q - expected) < 0.1, (
            f"Quantile: {q:.4f}, expected {expected:.4f}"
        )


class TestEqualEigenvalues:
    """K equal eigenvalues lambda -> chi^2(K) scaled by lambda."""

    @pytest.mark.parametrize("K", [3, 5, 10])
    def test_scaled_chi2(self, K):
        lam = 0.5
        eigenvalues = np.full(K, lam)
        # Q = lam * chi^2(K), so P(Q <= x) = P(chi^2(K) <= x/lam)
        x = lam * chi2.ppf(0.95, df=K)
        prob, bound, ifault = davies_cdf(x, eigenvalues)
        assert abs(prob - 0.95) < 0.02, (
            f"K={K}: P(Q <= {x:.4f}) = {prob:.6f}, expected 0.95"
        )


class TestKnownCvMDistribution:
    """
    With eigenvalues (k*pi)^{-2}, the distribution is the classical
    Cramér-von Mises omega^2 = sum xi_k^2 / (k*pi)^2.

    Published quantiles: q_{0.90} = 0.3473, q_{0.95} = 0.4614, q_{0.99} = 0.7434.
    """

    @pytest.mark.parametrize("level,expected", [
        (0.90, 0.3473),
        (0.95, 0.4614),
        (0.99, 0.7434),
    ])
    def test_cvm_quantile(self, level, expected):
        K = 200  # enough terms for convergence
        eigenvalues = centered_brownian_eigenvalues(K)
        q = davies_quantile(level, eigenvalues, accuracy=1e-4)
        assert abs(q - expected) < 0.01, (
            f"CvM q_{level}: computed={q:.6f}, expected={expected:.4f}"
        )


class TestAccuracyBound:
    """The reported error bound should be consistent with actual error."""

    def test_bound_reasonable(self):
        eigenvalues = centered_brownian_eigenvalues(50)
        x = 0.5
        prob, bound, ifault = davies_cdf(x, eigenvalues, accuracy=1e-4)
        assert bound < 1.0, f"Error bound too large: {bound}"
        assert prob >= 0 and prob <= 1


class TestQuantileInversion:
    """davies_cdf(davies_quantile(p)) should approximately equal p."""

    @pytest.mark.parametrize("p", [0.5, 0.9, 0.95, 0.99])
    def test_inversion(self, p):
        eigenvalues = centered_brownian_eigenvalues(50)
        q = davies_quantile(p, eigenvalues, accuracy=1e-4)
        prob, _, _ = davies_cdf(q, eigenvalues, accuracy=1e-4)
        assert abs(prob - p) < 0.02, (
            f"Inversion: cdf(quantile({p})) = {prob:.6f}, expected {p}"
        )


class TestLargeKStability:
    """Should handle K = 200+ eigenvalues without overflow."""

    def test_no_overflow(self):
        eigenvalues = centered_brownian_eigenvalues(200)
        prob, bound, ifault = davies_cdf(0.5, eigenvalues, accuracy=1e-3)
        assert np.isfinite(prob), f"Overflow: prob = {prob}"
        assert 0 <= prob <= 1


class TestExtremeQuantiles:
    """Test behavior at extreme probability levels."""

    def test_low_quantile(self):
        eigenvalues = centered_brownian_eigenvalues(50)
        q = davies_quantile(0.1, eigenvalues)
        assert q > 0 and np.isfinite(q)

    def test_high_quantile(self):
        eigenvalues = centered_brownian_eigenvalues(50)
        q = davies_quantile(0.999, eigenvalues)
        assert q > 0 and np.isfinite(q)

    def test_invalid_p(self):
        eigenvalues = np.array([1.0])
        with pytest.raises(ValueError):
            davies_quantile(0.0, eigenvalues)
        with pytest.raises(ValueError):
            davies_quantile(1.0, eigenvalues)


class TestEdgeCases:
    """Test edge cases and invalid inputs."""

    def test_negative_x(self):
        eigenvalues = np.array([1.0, 0.5])
        prob, _, _ = davies_cdf(-1.0, eigenvalues)
        assert prob == 0.0

    def test_zero_x(self):
        eigenvalues = np.array([1.0, 0.5])
        prob, _, _ = davies_cdf(0.0, eigenvalues)
        assert prob == 0.0

    def test_negative_eigenvalue(self):
        """Should return error code for non-positive eigenvalues."""
        eigenvalues = np.array([1.0, -0.5])
        _, _, ifault = davies_cdf(1.0, eigenvalues)
        assert ifault == 4
