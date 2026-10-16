"""
Tests for Module F2.B: Optimal weight R*.

Validates that the adaptive weight correctly identifies:
- Pure mean instability → R ≈ 0
- Pure variance instability → R ≈ 1
- Symmetric case → R ≈ 0.5
- Degenerate case → R = 0.5 (fallback)
"""

import numpy as np
import pytest

from stationarity_test.optimal_weight import compute_optimal_R, oracle_R


class TestRPureMean:
    """When only mean component is active, R should be near 0."""

    def test_R_pure_mean(self):
        result = compute_optimal_R(g1_std=5.0, g2_std=0.01)
        assert result['R_star'] < 0.001, (
            f"Pure mean: R*={result['R_star']:.4f}, expected ≈ 0"
        )

    def test_R_dominant_mean(self):
        result = compute_optimal_R(g1_std=10.0, g2_std=1.0)
        assert result['R_star'] < 0.10, (
            f"Dominant mean: R*={result['R_star']:.4f}, expected < 0.10"
        )


class TestRPureVariance:
    """When only variance component is active, R should be near 1."""

    def test_R_pure_variance(self):
        result = compute_optimal_R(g1_std=0.01, g2_std=5.0)
        assert result['R_star'] > 0.999, (
            f"Pure variance: R*={result['R_star']:.4f}, expected ≈ 1"
        )

    def test_R_dominant_variance(self):
        result = compute_optimal_R(g1_std=1.0, g2_std=10.0)
        assert result['R_star'] > 0.90, (
            f"Dominant variance: R*={result['R_star']:.4f}, expected > 0.90"
        )


class TestRSymmetric:
    """When both components are equal, R should be 0.5."""

    def test_symmetric(self):
        result = compute_optimal_R(g1_std=3.0, g2_std=3.0)
        assert abs(result['R_star'] - 0.5) < 0.01, (
            f"Symmetric: R*={result['R_star']:.4f}, expected 0.5"
        )


class TestRDegenerate:
    """When both components are near zero, R should default to 0.5."""

    def test_both_zero(self):
        result = compute_optimal_R(g1_std=0.0, g2_std=0.0)
        assert result['R_star'] == 0.5

    def test_both_tiny(self):
        result = compute_optimal_R(g1_std=1e-15, g2_std=1e-15)
        assert result['R_star'] == 0.5


class TestOracleR:
    """Oracle R with known (c1, d1) parameters."""

    def test_pure_mean_oracle(self):
        R = oracle_R(c1=10.0, d1=0.0)
        assert R == 0.0

    def test_pure_variance_oracle(self):
        R = oracle_R(c1=0.0, d1=10.0)
        assert R == 1.0

    def test_equal_oracle(self):
        R = oracle_R(c1=5.0, d1=5.0)
        assert abs(R - 0.5) < 1e-10

    def test_mixed_oracle(self):
        R = oracle_R(c1=3.0, d1=7.0)
        expected = 7.0 / 10.0
        assert abs(R - expected) < 1e-10

    def test_degenerate_oracle(self):
        R = oracle_R(c1=0.0, d1=0.0)
        assert R == 0.5

    def test_invalid_oracle(self):
        with pytest.raises(ValueError):
            oracle_R(c1=-1.0, d1=5.0)


class TestMethodParameter:
    """Test method selection."""

    def test_fixed(self):
        result = compute_optimal_R(g1_std=1.0, g2_std=10.0, method='fixed')
        assert result['R_star'] == 0.5
        assert result['method'] == 'fixed'
        # fisher_ratio should still be computed
        assert result['fisher_ratio'] > 0.90

    def test_adaptive(self):
        result = compute_optimal_R(g1_std=1.0, g2_std=10.0, method='adaptive')
        assert result['R_star'] > 0.90
        assert result['method'] == 'adaptive'

    def test_invalid_method(self):
        with pytest.raises(ValueError, match="method"):
            compute_optimal_R(g1_std=1.0, g2_std=1.0, method='invalid')


class TestFisherRatio:
    """fisher_ratio should always be in [0, 1]."""

    @pytest.mark.parametrize("g1,g2", [
        (0.0, 0.0), (1.0, 0.0), (0.0, 1.0),
        (3.0, 7.0), (100.0, 0.01),
    ])
    def test_range(self, g1, g2):
        result = compute_optimal_R(g1_std=g1, g2_std=g2)
        assert 0.0 <= result['fisher_ratio'] <= 1.0
