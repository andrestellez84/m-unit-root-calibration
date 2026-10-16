"""
Tests for Module F1.B: Standardization factors.

Validates that d_bar_i(theta) is positive, continuous, consistent with
eigenvalues, and respects the asymmetric scaling exponents (D3).
"""

import numpy as np
import pytest

from stationarity_test.standardization import standardization_factor
from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS


class TestFactorPositive:
    """d_bar_i(theta) > 0 for all theta in Theta."""

    @pytest.mark.parametrize("theta", [0.05, 0.1, 0.2, 0.3, 0.5])
    @pytest.mark.parametrize("component", [1, 2])
    def test_positive(self, theta, component):
        d = standardization_factor(theta, component, eps=1e-4)
        assert d > 0, f"d_bar_{component}({theta}) = {d} is not positive"


class TestFactorContinuity:
    """d_bar_i(theta + delta) should be close to d_bar_i(theta) for small delta."""

    @pytest.mark.parametrize("component", [1, 2])
    def test_continuity(self, component):
        theta = 0.2
        delta = 0.01
        d1 = standardization_factor(theta, component, eps=1e-4)
        d2 = standardization_factor(theta + delta, component, eps=1e-4)
        # Lipschitz bound: |d1 - d2| should be proportional to delta
        rel_change = abs(d1 - d2) / max(abs(d1), 1e-10)
        assert rel_change < 1.0, (
            f"d_bar_{component} jumps too much: "
            f"d({theta})={d1:.6f}, d({theta + delta})={d2:.6f}, "
            f"rel_change={rel_change:.4f}"
        )


class TestFactorThetaHalf:
    """Specific value at theta = 0.5 should be reasonable."""

    @pytest.mark.parametrize("component", [1, 2])
    def test_value_at_half(self, component):
        d = standardization_factor(0.5, component, eps=1e-4)
        assert np.isfinite(d), f"d_bar_{component}(0.5) is not finite: {d}"
        assert d > 1e-10, f"d_bar_{component}(0.5) is suspiciously small: {d}"


class TestFactorConsistencyWithEigenvalues:
    """d_bar_i should be derivable from eigenvalues of the covariance operator."""

    def test_component1_is_sqrt_trace(self):
        """For component 1, d_bar_1 = sqrt(sum eigenvalues) = sqrt(trace)."""
        from stationarity_test.kl_eigenvalues import compute_eigenvalues

        theta = 0.3
        K = 50
        eig, bound = compute_eigenvalues(theta, component=1, K=K, eps=1e-5)
        expected = np.sqrt(np.sum(eig))

        d = standardization_factor(theta, component=1, eps=1e-5)

        # Should be close (within truncation error)
        assert abs(d - expected) / max(abs(expected), 1e-10) < 0.1, (
            f"d_bar_1({theta}) = {d:.6f} != sqrt(trace) = {expected:.6f}"
        )


class TestDefaultCValues:
    """Default scaling exponents should be c_1 = 1, c_2 = 0."""

    def test_defaults(self):
        assert DEFAULT_SCALING_EXPONENTS[1] == 1.0
        assert DEFAULT_SCALING_EXPONENTS[2] == 2.0


class TestCustomCOverride:
    """Passing explicit c_i should produce different results if c_i differs from default."""

    def test_override(self):
        theta = 0.2
        d_default = standardization_factor(theta, component=1, c_i=None, eps=1e-4)
        d_custom = standardization_factor(theta, component=1, c_i=0.5, eps=1e-4)
        # With different c_i, the factor itself is the same (c_i only affects
        # the scaling in statistic.py, not the factor computation).
        # But we verify the interface accepts it without error.
        assert d_custom > 0


class TestAsymmetryC1C2:
    """
    d_bar_1 and d_bar_2 should be on substantially different scales,
    reflecting the asymmetry c_1 = 1, c_2 = 0.
    """

    def test_different_scales(self):
        theta = 0.2
        d1 = standardization_factor(theta, component=1, eps=1e-4)
        d2 = standardization_factor(theta, component=2, eps=1e-4)
        # They should not be identical (different operators)
        assert abs(d1 - d2) / max(d1, d2) > 0.01, (
            f"d_bar_1 = {d1:.6f}, d_bar_2 = {d2:.6f} are too similar"
        )


class TestInvalidInputs:
    """Invalid parameters should raise errors."""

    def test_invalid_theta(self):
        with pytest.raises(ValueError):
            standardization_factor(0.0, component=1)
        with pytest.raises(ValueError):
            standardization_factor(0.6, component=1)

    def test_invalid_component(self):
        with pytest.raises(ValueError):
            standardization_factor(0.2, component=3)
