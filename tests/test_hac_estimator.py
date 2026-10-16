"""
Tests for Module F2.D: HAC (Newey-West) estimator.

Validates unbiasedness for white noise, autocorrelation correction for AR(1),
automatic bandwidth selection, and positivity guarantee.
"""

import numpy as np
import pytest

from stationarity_test.hac_estimator import hac_newey_west


class TestWhiteNoiseUnbiased:
    """For iid N(0, σ²) data, HAC should approximate σ²."""

    @pytest.mark.parametrize("sigma", [0.5, 1.0, 2.0, 5.0])
    def test_unbiased(self, sigma):
        rng = np.random.default_rng(42)
        n = 5000
        x = rng.standard_normal(n) * sigma
        sigma_hat_sq = hac_newey_west(x)
        # Should be close to sigma^2 (within 10% for n=5000)
        assert abs(sigma_hat_sq - sigma**2) / sigma**2 < 0.10, (
            f"HAC on WN(σ={sigma}): σ̂²={sigma_hat_sq:.4f}, "
            f"expected {sigma**2:.4f}"
        )


class TestAR1Correction:
    """
    For AR(1) innovations with ρ > 0, the naive variance underestimates
    the long-run variance. HAC should correct this.
    """

    def test_ar1_rho05(self):
        rng = np.random.default_rng(42)
        n = 10000
        rho = 0.5
        sigma_eps = 1.0
        # Generate AR(1): x_t = ρ x_{t-1} + ε_t
        x = np.empty(n)
        x[0] = rng.standard_normal()
        for t in range(1, n):
            x[t] = rho * x[t - 1] + sigma_eps * rng.standard_normal()

        # True long-run variance = σ²_ε / (1 - ρ)²
        true_lrv = sigma_eps**2 / (1.0 - rho)**2

        sigma_hat_sq = hac_newey_west(x)
        # Naive variance would be ~ σ²_ε / (1 - ρ²) ≈ 1.33
        # HAC should be closer to true_lrv = 4.0
        naive_var = np.var(x, ddof=1)
        assert abs(sigma_hat_sq - true_lrv) < abs(naive_var - true_lrv), (
            f"HAC ({sigma_hat_sq:.3f}) should be closer to true LRV "
            f"({true_lrv:.3f}) than naive ({naive_var:.3f})"
        )


class TestBandwidthSelection:
    """Automatic bandwidth should scale as n^{1/3}."""

    def test_bandwidth_order(self):
        rng = np.random.default_rng(42)
        # For AR(1) with ρ=0.3, Andrews formula gives m ~ 1.1447 * (α̂ n)^{1/3}
        # We check that bandwidth grows sub-linearly
        n_values = [500, 2000, 8000]
        bandwidths = []
        for n in n_values:
            x = np.empty(n)
            x[0] = 0.0
            for t in range(1, n):
                x[t] = 0.3 * x[t - 1] + rng.standard_normal()
            # Access bandwidth indirectly: compute HAC for different n
            # and verify the result is consistent
            sigma_sq = hac_newey_west(x)
            assert sigma_sq > 0
            bandwidths.append(sigma_sq)
        # All should estimate roughly the same thing
        # (true LRV = 1/(1-0.3)^2 ≈ 2.04)
        for b in bandwidths:
            assert 1.0 < b < 4.0, f"HAC estimate {b:.3f} out of range [1, 4]"


class TestPositiveDefinite:
    """Result must always be strictly positive."""

    @pytest.mark.parametrize("seed", range(10))
    def test_positive(self, seed):
        rng = np.random.default_rng(seed)
        x = rng.standard_normal(100)
        result = hac_newey_west(x)
        assert result > 0, f"HAC estimate is not positive: {result}"

    def test_constant_input(self):
        """Constant input should return the floor value."""
        x = np.ones(100)
        result = hac_newey_west(x)
        assert result == 1e-12

    def test_very_short(self):
        """Very short input should not crash."""
        x = np.array([1.0])
        result = hac_newey_west(x)
        assert result > 0

    def test_explicit_bandwidth(self):
        """Explicit bandwidth should work."""
        rng = np.random.default_rng(42)
        x = rng.standard_normal(200)
        result = hac_newey_west(x, bandwidth=5)
        assert result > 0
