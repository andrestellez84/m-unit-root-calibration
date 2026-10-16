"""
Tests for Module F1.C: Null distribution quantiles.

Validates CDF monotonicity, quantile inversion, R boundary cases,
and consistency between empirical and Monte Carlo quantiles.
"""

import numpy as np
import pytest

from stationarity_test.null_quantiles import (
    null_cdf,
    null_quantile,
    null_quantile_mc,
)


# Default n for all tests (empirical CDF requires a sample size)
N_TEST = 500


class TestCdfMonotone:
    """CDF must be non-decreasing."""

    def test_monotonicity(self):
        theta = (0.2, 0.2)
        R = 0.5
        v_values = np.linspace(0.01, 1.5, 15)
        cdf_values = [null_cdf(v, theta, R, n=N_TEST) for v in v_values]
        for i in range(1, len(cdf_values)):
            # Allow tolerance for numerical integration noise
            assert cdf_values[i] >= cdf_values[i - 1] - 0.01, (
                f"CDF not monotone: F({v_values[i-1]:.3f})={cdf_values[i-1]:.6f} > "
                f"F({v_values[i]:.3f})={cdf_values[i]:.6f}"
            )


class TestCdfRange:
    """CDF values must be in [0, 1]."""

    @pytest.mark.parametrize("v", [0.0, 0.1, 0.5, 1.0, 3.0])
    def test_range(self, v):
        theta = (0.2, 0.2)
        R = 0.5
        prob = null_cdf(v, theta, R, n=N_TEST)
        assert 0.0 <= prob <= 1.0, f"CDF({v}) = {prob} out of [0, 1]"

    def test_negative_v(self):
        """CDF at v <= 0 should be 0."""
        prob = null_cdf(-1.0, (0.2, 0.2), 0.5, n=N_TEST)
        assert prob == 0.0

    def test_zero_v(self):
        prob = null_cdf(0.0, (0.2, 0.2), 0.5, n=N_TEST)
        assert prob == 0.0


class TestQuantileInversion:
    """F(q_alpha) should approximately equal alpha (lower tail)."""

    @pytest.mark.parametrize("alpha", [0.10, 0.05])
    def test_inversion(self, alpha):
        theta = (0.2, 0.2)
        R = 0.5
        q = null_quantile(theta, R, alpha, n=N_TEST)
        prob = null_cdf(q, theta, R, n=N_TEST)
        assert abs(prob - alpha) < 0.05, (
            f"Inversion failed: F(q_{{{alpha}}}) = {prob:.4f}, "
            f"expected {alpha:.2f}"
        )


class TestQuantileOrdering:
    """Lower-tail: q_{0.01} < q_{0.05} < q_{0.10}."""

    def test_ordering(self):
        theta = (0.2, 0.2)
        R = 0.5
        q_90 = null_quantile(theta, R, 0.10, n=N_TEST)
        q_95 = null_quantile(theta, R, 0.05, n=N_TEST)
        q_99 = null_quantile(theta, R, 0.01, n=N_TEST)
        assert q_99 < q_95 < q_90, (
            f"Ordering violated: q_01={q_99:.4f}, q_05={q_95:.4f}, q_10={q_90:.4f}"
        )


class TestR0OnlyComponent1:
    """R = 0: statistic reduces to component 1 only."""

    def test_R0(self):
        theta = (0.2, 0.3)
        q_R0 = null_quantile(theta, R=0.0, alpha=0.05, n=N_TEST)
        # Should only depend on theta_1
        theta2 = (0.2, 0.1)  # different theta_2
        q_R0_alt = null_quantile(theta2, R=0.0, alpha=0.05, n=N_TEST)
        # Both should be the same since R=0 ignores component 2
        assert abs(q_R0 - q_R0_alt) < 0.05, (
            f"R=0 but depends on theta_2: q={q_R0:.4f} vs {q_R0_alt:.4f}"
        )


class TestR1OnlyComponent2:
    """R = 1: statistic reduces to component 2 only."""

    def test_R1(self):
        theta = (0.2, 0.3)
        q_R1 = null_quantile(theta, R=1.0, alpha=0.05, n=N_TEST)
        # Should only depend on theta_2
        theta2 = (0.1, 0.3)  # different theta_1
        q_R1_alt = null_quantile(theta2, R=1.0, alpha=0.05, n=N_TEST)
        assert abs(q_R1 - q_R1_alt) < 0.05, (
            f"R=1 but depends on theta_1: q={q_R1:.4f} vs {q_R1_alt:.4f}"
        )


class TestDaviesVsMcConsistency:
    """
    Empirical-based quantiles should agree with Monte Carlo quantiles
    within the expected MC error.
    """

    @pytest.mark.slow
    def test_consistency(self):
        theta = (0.2, 0.2)
        R = 0.5
        alpha = 0.05

        q_emp = null_quantile(theta, R, alpha, n=N_TEST)
        q_mc = null_quantile_mc(
            theta, R, alpha,
            n_sims=50_000,
            M_mesh=500,
            seed=42
        )

        # MC error ~ 1/sqrt(n_sims) ~ 0.005; allow generous tolerance
        # because the MC simulation is on a coarse mesh
        assert abs(q_emp - q_mc) / max(q_emp, 0.01) < 0.30, (
            f"Empirical vs MC discrepancy: emp={q_emp:.4f}, mc={q_mc:.4f}"
        )


class TestInvalidInputs:
    """Invalid parameters should raise errors."""

    def test_invalid_alpha(self):
        with pytest.raises(ValueError):
            null_quantile((0.2, 0.2), 0.5, alpha=0.0, n=N_TEST)
        with pytest.raises(ValueError):
            null_quantile((0.2, 0.2), 0.5, alpha=1.0, n=N_TEST)

    def test_invalid_R(self):
        with pytest.raises(ValueError):
            null_quantile((0.2, 0.2), R=-0.1, alpha=0.05, n=N_TEST)
        with pytest.raises(ValueError):
            null_quantile((0.2, 0.2), R=1.5, alpha=0.05, n=N_TEST)

    def test_invalid_theta(self):
        with pytest.raises(ValueError):
            null_quantile((0.0, 0.2), 0.5, alpha=0.05, n=N_TEST)
        with pytest.raises(ValueError):
            null_quantile((0.2, 0.6), 0.5, alpha=0.05, n=N_TEST)
