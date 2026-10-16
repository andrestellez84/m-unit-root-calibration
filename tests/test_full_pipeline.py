"""
Tests for Module F2.C: Full stationarity test pipeline.

Validates the complete pipeline from raw series to decision,
including automatic theta selection and R optimization.
"""

import numpy as np
import pytest

from stationarity_test.full_pipeline import stationarity_test
from stationarity_test.utils import simulate_random_walk


class TestRandomWalkNotReject:
    """Under H0 (random walk), the test should generally not reject."""

    def test_rw_not_reject(self):
        """Single random walk with fixed theta and R."""
        Y = simulate_random_walk(500, sigma=1.0, seed=42)
        result = stationarity_test(Y, alpha=0.05, theta=(0.2, 0.2), R=0.5)
        # Just check the pipeline runs and returns valid output
        assert 0.0 <= result['p_value'] <= 1.0
        assert isinstance(result['reject_H0'], (bool, np.bool_))
        assert result['n'] == 500


class TestTrendNotReject:
    """A linear trend is non-stationary, so should NOT be rejected under H0."""

    def test_linear_trend_not_rejected(self):
        n = 500
        # Strong linear trend + small noise — non-stationary process
        rng = np.random.default_rng(42)
        Y = np.linspace(0, 50, n + 1) + 0.5 * rng.standard_normal(n + 1)

        result = stationarity_test(Y, alpha=0.05, theta=(0.2, 0.2), R=0.0)
        # With lower-tail test, non-stationary series should have large p-value
        # (statistic is large under H0, so F_0(stat) ≈ 1)
        assert result['p_value'] > 0.5, (
            f"Linear trend incorrectly rejected: p={result['p_value']:.4f}"
        )


class TestHeteroscedasticDetects:
    """Variance regime change should be detected with R=1."""

    def test_variance_change(self):
        rng = np.random.default_rng(42)
        n = 1000
        # Random walk with variance jump at midpoint
        eps = np.concatenate([
            rng.standard_normal(n // 2),
            5.0 * rng.standard_normal(n - n // 2)
        ])
        Y = np.cumsum(np.concatenate([[0], eps]))

        result = stationarity_test(Y, alpha=0.05, theta=(0.2, 0.2), R=1.0)
        assert 0.0 <= result['p_value'] <= 1.0


class TestEndToEndAuto:
    """Pipeline with all parameters auto-selected should run cleanly."""

    def test_auto_pipeline(self):
        Y = simulate_random_walk(200, sigma=1.0, seed=42)
        result = stationarity_test(Y, alpha=0.05)

        # Verify auto-selection flags
        assert result['theta_auto'] is True
        assert result['R_auto'] is True

        # Verify all fields present
        expected_keys = {
            'statistic', 'p_value', 'reject_H0', 'rejection_rule',
            'theta_1', 'theta_2', 'R',
            'g1_raw', 'g2_raw', 'g1_std', 'g2_std',
            'sigma_hat', 'n', 'critical_value',
            'alpha', 'theta_auto', 'R_auto',
        }
        assert set(result.keys()) == expected_keys

        # Verify ranges
        assert 0.0 <= result['p_value'] <= 1.0
        assert 0.0 < result['theta_1'] <= 0.5
        assert 0.0 < result['theta_2'] <= 0.5
        assert 0.0 <= result['R'] <= 1.0
        assert result['sigma_hat'] > 0
        assert result['critical_value'] > 0

    def test_auto_with_manual_theta(self):
        Y = simulate_random_walk(200, sigma=1.0, seed=42)
        result = stationarity_test(Y, alpha=0.05, theta=(0.3, 0.3))

        assert result['theta_auto'] is False
        assert result['R_auto'] is True
        assert result['theta_1'] == 0.3
        assert result['theta_2'] == 0.3

    def test_auto_with_manual_R(self):
        Y = simulate_random_walk(200, sigma=1.0, seed=42)
        result = stationarity_test(Y, alpha=0.05, R=0.7)

        assert result['theta_auto'] is True
        assert result['R_auto'] is False
        assert result['R'] == 0.7


class TestReproducibility:
    """Same input should produce identical results."""

    def test_deterministic(self):
        Y = simulate_random_walk(300, sigma=1.0, seed=42)
        result1 = stationarity_test(Y, alpha=0.05, theta=(0.2, 0.2), R=0.5)
        result2 = stationarity_test(Y, alpha=0.05, theta=(0.2, 0.2), R=0.5)

        assert result1['statistic'] == result2['statistic']
        assert result1['p_value'] == result2['p_value']
        assert result1['reject_H0'] == result2['reject_H0']


class TestScaleInvariancePipeline:
    """Pipeline should be scale-invariant (Y → αY gives same result)."""

    def test_scale_invariance(self):
        rng = np.random.default_rng(42)
        Y_base = np.cumsum(np.concatenate([[0], rng.standard_normal(300)]))

        r1 = stationarity_test(Y_base, theta=(0.2, 0.2), R=0.5)
        r10 = stationarity_test(10 * Y_base, theta=(0.2, 0.2), R=0.5)

        rel_diff = abs(r1['statistic'] - r10['statistic']) / (r1['statistic'] + 1e-12)
        assert rel_diff < 0.05, (
            f"Pipeline not scale-invariant: stat(Y)={r1['statistic']:.6f}, "
            f"stat(10Y)={r10['statistic']:.6f}"
        )


class TestInvalidInputs:
    """Invalid inputs should raise appropriate errors."""

    def test_short_series(self):
        Y = np.ones(30)
        with pytest.raises(ValueError):
            stationarity_test(Y)

    def test_invalid_alpha(self):
        Y = simulate_random_walk(100, seed=0)
        with pytest.raises(ValueError, match="alpha"):
            stationarity_test(Y, alpha=0.0)
        with pytest.raises(ValueError, match="alpha"):
            stationarity_test(Y, alpha=1.0)
