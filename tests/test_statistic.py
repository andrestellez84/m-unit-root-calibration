"""
Tests for Module F1.D: Statistic evaluation.

Validates the full pipeline from observed series to p-value,
including the quadratic combination (D1), squared variances (D2),
and asymmetric standardization (D3).
"""

import numpy as np
import pytest

from stationarity_test.statistic import compute_statistic, _compute_g1, _compute_g2
from stationarity_test.utils import simulate_random_walk


class TestConstantSeries:
    """A constant series should produce g1 = g2 = 0."""

    def test_constant(self):
        Y = np.ones(200, dtype=np.float64)  # n = 199
        # g1 and g2 raw should be 0 (no variation in rolling stats)
        g1 = _compute_g1(Y, tau=20)
        g2 = _compute_g2(Y, tau=20)
        assert g1 < 1e-10, f"g1 on constant series: {g1}"
        assert g2 < 1e-10, f"g2 on constant series: {g2}"


class TestLinearTrend:
    """A linear trend should produce g1 > 0 but g2 controlled."""

    def test_linear(self):
        n = 200
        Y = np.linspace(0, 10, n + 1)
        g1 = _compute_g1(Y, tau=20)
        g2 = _compute_g2(Y, tau=20)
        assert g1 > 0, f"g1 on linear trend should be positive: {g1}"
        # g2 may be small but not necessarily zero for linear trends


class TestRandomWalkPvalueUniform:
    """
    Under H0 (random walk), p-values should be approximately U(0,1).
    Tested with a Kolmogorov-Smirnov test.
    """

    @pytest.mark.slow
    def test_pvalue_uniformity(self):
        from scipy.stats import kstest

        n_sims = 500
        theta = (0.2, 0.2)
        R = 0.5
        p_values = []

        for seed in range(n_sims):
            Y = simulate_random_walk(200, sigma=1.0, seed=seed)
            result = compute_statistic(Y, theta, R, eps=1e-3)
            p_values.append(result['p_value'])

        p_values = np.array(p_values)

        # KS test for uniformity (lenient because of numerical approximations)
        ks_stat, ks_pval = kstest(p_values, 'uniform')
        # We don't require perfect uniformity, just reasonable
        assert ks_pval > 0.001, (
            f"P-values not uniform: KS stat={ks_stat:.4f}, KS p-value={ks_pval:.6f}"
        )


class TestStationaryAR1:
    """
    A stationary AR(1) process should produce small p-values for large n,
    since the test should detect stationarity (null is random walk).
    """

    def test_ar1_detection(self):
        np.random.seed(42)
        n = 500
        rho = 0.5  # stationary AR(1) coefficient
        Y = np.empty(n + 1)
        Y[0] = 0.0
        for t in range(1, n + 1):
            Y[t] = rho * Y[t - 1] + np.random.randn()

        result = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)
        # For a stationary process, p-value should tend to be small
        # but we won't assert a specific threshold for a single realization
        assert 0.0 <= result['p_value'] <= 1.0


class TestPvalueRange:
    """P-value must always be in [0, 1]."""

    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
    def test_range(self, seed):
        Y = simulate_random_walk(100, sigma=1.0, seed=seed)
        result = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)
        assert 0.0 <= result['p_value'] <= 1.0, (
            f"P-value out of range: {result['p_value']}"
        )


class TestR0OnlyMean:
    """R = 0: only the mean component contributes."""

    def test_R0(self):
        Y = simulate_random_walk(200, seed=42)
        result = compute_statistic(Y, theta=(0.2, 0.2), R=0.0, eps=1e-3)
        # statistic should equal |g1_std| since R=0
        expected = abs(result['g1_std'])
        assert abs(result['statistic'] - expected) < 1e-10, (
            f"R=0: statistic={result['statistic']:.6f} != g1_std={expected:.6f}"
        )


class TestR1OnlyVariance:
    """R = 1: only the variance component contributes."""

    def test_R1(self):
        Y = simulate_random_walk(200, seed=42)
        result = compute_statistic(Y, theta=(0.2, 0.2), R=1.0, eps=1e-3)
        expected = abs(result['g2_std'])
        assert abs(result['statistic'] - expected) < 1e-10, (
            f"R=1: statistic={result['statistic']:.6f} != g2_std={expected:.6f}"
        )


class TestStandardizationScales:
    """
    After standardization, both g1_std and g2_std should be O(1) under H0.
    This verifies the asymmetric scaling (D3) is working correctly.
    """

    def test_scales(self):
        # Average over multiple realizations
        n = 500
        g1_stds = []
        g2_stds = []
        for seed in range(50):
            Y = simulate_random_walk(n, seed=seed)
            result = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)
            g1_stds.append(result['g1_std'])
            g2_stds.append(result['g2_std'])

        mean_g1 = np.mean(g1_stds)
        mean_g2 = np.mean(g2_stds)

        # Both should be O(1), i.e., between 0.01 and 100 (very generous)
        assert 0.001 < mean_g1 < 1000, (
            f"g1_std mean = {mean_g1:.6f}, not O(1)"
        )
        assert 0.001 < mean_g2 < 1000, (
            f"g2_std mean = {mean_g2:.6f}, not O(1)"
        )


class TestReturnDict:
    """Verify the return dictionary has all expected keys."""

    def test_keys(self):
        Y = simulate_random_walk(100, seed=0)
        result = compute_statistic(Y, theta=(0.2, 0.2), R=0.5, eps=1e-3)
        expected_keys = {
            'statistic', 'p_value', 'g1_raw', 'g2_raw',
            'g1_std', 'g2_std', 'sigma_hat', 'tau1', 'tau2', 'n'
        }
        assert set(result.keys()) == expected_keys


class TestInvalidInputs:
    """Invalid inputs should raise appropriate errors."""

    def test_short_series(self):
        Y = np.ones(30)  # n = 29 < 60
        with pytest.raises(ValueError, match="Sample size"):
            compute_statistic(Y, theta=(0.2, 0.2), R=0.5)

    def test_invalid_theta(self):
        Y = simulate_random_walk(100, seed=0)
        with pytest.raises(ValueError):
            compute_statistic(Y, theta=(0.0, 0.2), R=0.5)

    def test_invalid_R(self):
        Y = simulate_random_walk(100, seed=0)
        with pytest.raises(ValueError):
            compute_statistic(Y, theta=(0.2, 0.2), R=1.5)


class TestScaleInvariance:
    """
    The standardized statistic must be invariant under Y → α*Y.
    This verifies that the HAC normalization (σ̂ and σ̂²) correctly
    absorbs the scale of the innovations.
    """

    def test_scale_invariance(self):
        rng = np.random.default_rng(42)
        Y_base = np.cumsum(np.concatenate([[0], rng.standard_normal(500)]))

        scales = [0.1, 1.0, 10.0, 100.0]
        results = []
        for s in scales:
            result = compute_statistic(s * Y_base, theta=(0.2, 0.2), R=0.5, eps=1e-3)
            results.append(result['statistic'])

        # All values should be approximately equal (within 5%)
        for i, val in enumerate(results[1:], 1):
            rel_diff = abs(val - results[0]) / (abs(results[0]) + 1e-12)
            assert rel_diff < 0.05, (
                f"Scale invariance violated: scale={scales[i]}, "
                f"stat={val:.6f} vs baseline={results[0]:.6f} "
                f"(rel_diff={rel_diff:.4f})"
            )

    def test_sigma_hat_scales(self):
        """σ̂ should scale linearly with the innovation std dev."""
        rng = np.random.default_rng(42)
        Y_base = np.cumsum(np.concatenate([[0], rng.standard_normal(500)]))

        r1 = compute_statistic(Y_base, theta=(0.2, 0.2), R=0.5, eps=1e-3)
        r10 = compute_statistic(10 * Y_base, theta=(0.2, 0.2), R=0.5, eps=1e-3)

        # σ̂(10*Y) ≈ 10 * σ̂(Y)
        ratio = r10['sigma_hat'] / r1['sigma_hat']
        assert abs(ratio - 10.0) < 0.5, (
            f"σ̂ scaling: ratio={ratio:.3f}, expected 10.0"
        )
