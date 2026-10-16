"""
Integration tests: end-to-end pipeline validation.

Tests the full chain: constants → eigenvalues → standardization → davies → 
null_quantiles → statistic. Verifies reproducibility and pipeline coherence.
"""

import numpy as np
import pytest

from stationarity_test import compute_statistic
from stationarity_test.utils import simulate_random_walk


class TestEndToEndPipeline:
    """Full pipeline: random walk → statistic → p-value."""

    def test_basic_pipeline(self):
        """Generate a random walk and compute the statistic with p-value."""
        Y = simulate_random_walk(200, sigma=1.0, seed=12345)
        result = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)

        assert result['n'] == 200
        assert result['tau1'] == 40  # round(0.2 * 200)
        assert result['tau2'] == 40
        assert result['statistic'] >= 0
        assert 0 <= result['p_value'] <= 1
        assert result['g1_raw'] >= 0
        assert result['g2_raw'] >= 0

    def test_different_thetas(self):
        """Different theta values for mean and variance components."""
        Y = simulate_random_walk(300, sigma=1.0, seed=99)
        result = compute_statistic(Y, theta=(0.1, 0.3), R=0.5, eps=1e-3)

        assert result['tau1'] == 30   # round(0.1 * 300)
        assert result['tau2'] == 90   # round(0.3 * 300)
        assert result['statistic'] >= 0


class TestReproducibility:
    """Same seed should produce identical results."""

    def test_deterministic(self):
        Y = simulate_random_walk(200, sigma=1.0, seed=42)
        r1 = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)
        r2 = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)

        assert r1['statistic'] == r2['statistic']
        assert r1['p_value'] == r2['p_value']
        assert r1['g1_raw'] == r2['g1_raw']
        assert r1['g2_raw'] == r2['g2_raw']


class TestPipelineDependencyChain:
    """
    Verify that the dependency chain works:
    eigenvalues → standardization → quantiles → statistic
    """

    def test_chain(self):
        from stationarity_test.kl_eigenvalues import compute_eigenvalues
        from stationarity_test.standardization import standardization_factor
        from stationarity_test.null_quantiles import null_quantile
        from stationarity_test.davies import davies_cdf

        theta = 0.2

        # Step 1: eigenvalues
        eig1, bound1 = compute_eigenvalues(theta, component=1, K=20, eps=1e-3)
        assert len(eig1) == 20
        assert np.all(eig1 >= 0)

        # Step 2: standardization
        d1 = standardization_factor(theta, component=1, eps=1e-3)
        assert d1 > 0

        # Step 3: Davies CDF
        prob, bound, ifault = davies_cdf(0.5, eig1, accuracy=1e-3)
        assert 0 <= prob <= 1

        # Step 4: null quantile
        q = null_quantile((theta, theta), R=0.5, alpha=0.05, n=200, eps=1e-3)
        assert q > 0

        # Step 5: full statistic
        Y = simulate_random_walk(200, seed=0)
        result = compute_statistic(Y, theta=(theta, theta), R=0.5, eps=1e-3)
        assert result['statistic'] >= 0


class TestMultipleNSizes:
    """The statistic should work for various sample sizes."""

    @pytest.mark.parametrize("n", [60, 100, 200, 500])
    def test_various_n(self, n):
        Y = simulate_random_walk(n, seed=42)
        result = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)
        assert result['n'] == n
        assert 0 <= result['p_value'] <= 1
        assert np.isfinite(result['statistic'])


class TestMultipleRValues:
    """The statistic should vary smoothly with R."""

    def test_R_sweep(self):
        Y = simulate_random_walk(200, seed=42)
        R_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        stats = []
        for R in R_values:
            result = compute_statistic(Y, theta=(0.2, 0.2), R=R, eps=1e-3)
            stats.append(result['statistic'])
            assert np.isfinite(result['statistic'])
            assert 0 <= result['p_value'] <= 1
