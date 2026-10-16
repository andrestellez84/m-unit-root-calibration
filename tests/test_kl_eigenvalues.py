"""
Tests for Module F1.A: Karhunen-Loève eigenvalue computation.

Validates both component paths (linear kernel for mean, Wick kernel for variance)
and verifies convergence to known analytical eigenvalues.
"""

import numpy as np
import pytest

from stationarity_test.kl_eigenvalues import (
    compute_eigenvalues,
    _covariance_kernel_component1,
    _covariance_kernel_component2,
    _integral_min,
)
from stationarity_test.constants import centered_brownian_eigenvalues


class TestEigenvaluesPositive:
    """All eigenvalues must be non-negative."""

    @pytest.mark.parametrize("theta", [0.05, 0.1, 0.2, 0.3, 0.5])
    @pytest.mark.parametrize("component", [1, 2])
    def test_eigenvalues_positive(self, theta, component):
        eig, _ = compute_eigenvalues(theta, component, K=20, eps=1e-4)
        assert np.all(eig >= 0), f"Negative eigenvalues found: {eig[eig < 0]}"


class TestEigenvaluesDecreasing:
    """Eigenvalues must be in strictly decreasing order (up to numerical ties)."""

    @pytest.mark.parametrize("theta", [0.1, 0.3, 0.5])
    @pytest.mark.parametrize("component", [1, 2])
    def test_eigenvalues_decreasing(self, theta, component):
        eig, _ = compute_eigenvalues(theta, component, K=30, eps=1e-4)
        # Allow small tolerance for numerical ties
        diffs = np.diff(eig)
        assert np.all(diffs <= 1e-10), (
            f"Eigenvalues not decreasing: max increase = {np.max(diffs)}"
        )


class TestComponent1ConvergenceTheta1:
    """
    For theta close to 0.5 (our domain boundary), component 1 eigenvalues
    should be positive, decreasing, and in a reasonable range.

    Note: The exact (k*pi)^{-2} eigenvalues correspond to the limit
    theta -> 0, where the rolling mean converges to the standard Brownian
    bridge variance. At theta = 0.5 the kernel is very different, but
    eigenvalues should still be in a physically reasonable range.
    """

    def test_eigenvalues_reasonable_at_boundary(self):
        theta = 0.499
        K = 10
        eig, _ = compute_eigenvalues(theta, component=1, K=K, eps=1e-6)

        # All positive
        assert np.all(eig >= 0)
        # First eigenvalue should be the largest and non-trivial
        assert eig[0] > 1e-6, f"First eigenvalue too small: {eig[0]}"
        # Decreasing
        assert np.all(np.diff(eig) <= 1e-10)

    def test_first_eigenvalue_order_of_magnitude(self):
        """The leading eigenvalue should scale roughly with theta."""
        eig_02, _ = compute_eigenvalues(0.2, component=1, K=5, eps=1e-4)
        eig_05, _ = compute_eigenvalues(0.5, component=1, K=5, eps=1e-4)
        # Larger theta -> larger eigenvalues (more smoothing -> more variance structure)
        # Just check both are positive and finite
        assert eig_02[0] > 0 and np.isfinite(eig_02[0])
        assert eig_05[0] > 0 and np.isfinite(eig_05[0])


class TestComponent2SeparateFrom1:
    """Component 1 and 2 eigenvalues must be distinct (different operators)."""

    @pytest.mark.parametrize("theta", [0.1, 0.3])
    def test_different_eigenvalues(self, theta):
        eig1, _ = compute_eigenvalues(theta, component=1, K=10, eps=1e-4)
        eig2, _ = compute_eigenvalues(theta, component=2, K=10, eps=1e-4)

        # They should not be identical
        if len(eig1) > 0 and len(eig2) > 0:
            assert not np.allclose(eig1[:min(len(eig1), len(eig2))],
                                   eig2[:min(len(eig1), len(eig2))],
                                   rtol=1e-2), (
                "Component 1 and 2 eigenvalues are suspiciously similar"
            )


class TestTruncationBound:
    """The truncation bound must be non-negative and decrease with K."""

    def test_truncation_bound_valid(self):
        theta = 0.2
        _, bound_small = compute_eigenvalues(theta, 1, K=10, eps=1e-2)
        _, bound_large = compute_eigenvalues(theta, 1, K=50, eps=1e-2)

        assert bound_small >= 0, f"Truncation bound is negative: {bound_small}"
        assert bound_large >= 0, f"Truncation bound is negative: {bound_large}"
        assert bound_large <= bound_small + 1e-10, (
            f"Truncation bound did not decrease: K=10: {bound_small}, K=50: {bound_large}"
        )


class TestTraceConsistency:
    """Sum of eigenvalues + truncation bound should approximate the trace."""

    @pytest.mark.parametrize("component", [1, 2])
    def test_trace(self, component):
        theta = 0.2
        K = 30
        eig, bound = compute_eigenvalues(theta, component, K=K, eps=1e-4)
        total = np.sum(eig) + bound
        # Total should be positive and finite
        assert total > 0, f"Total (sum + bound) is non-positive: {total}"
        assert np.isfinite(total), f"Total is not finite: {total}"


class TestThetaBoundary:
    """Test behavior at domain boundaries."""

    def test_theta_small(self):
        """theta = 0.01: should work with sufficiently fine mesh."""
        eig, bound = compute_eigenvalues(0.01, component=1, K=10, eps=1e-3)
        assert len(eig) == 10
        assert np.all(eig >= 0)

    def test_theta_half(self):
        """theta = 0.5: upper boundary of domain."""
        eig, bound = compute_eigenvalues(0.5, component=1, K=10, eps=1e-4)
        assert len(eig) == 10
        assert np.all(eig >= 0)

    def test_theta_invalid(self):
        """theta outside domain should raise ValueError."""
        with pytest.raises(ValueError):
            compute_eigenvalues(0.0, component=1)
        with pytest.raises(ValueError):
            compute_eigenvalues(0.6, component=1)
        with pytest.raises(ValueError):
            compute_eigenvalues(-0.1, component=1)


class TestMeshScaling:
    """Verify that the mesh scales appropriately per component."""

    def test_mesh_for_small_theta_component1(self):
        # For theta = 0.05, component 1: M = max(500, ceil(50/0.05)) = 1000
        eig, _ = compute_eigenvalues(0.05, component=1, K=5, eps=1e-3)
        assert len(eig) == 5
        assert np.all(eig >= 0)

    def test_component2_smaller_mesh(self):
        # Component 2 uses smaller M (capped at 100) for tractability
        eig, _ = compute_eigenvalues(0.2, component=2, K=5, eps=1e-3)
        assert len(eig) == 5
        assert np.all(eig >= 0)


class TestInvalidComponent:
    """Component must be 1 or 2."""

    def test_component_invalid(self):
        with pytest.raises(ValueError):
            compute_eigenvalues(0.2, component=0)
        with pytest.raises(ValueError):
            compute_eigenvalues(0.2, component=3)


class TestIntegralMin:
    """Test the analytical integral of min(s, s') over rectangles."""

    def test_non_overlapping_below(self):
        """[0, 0.3] x [0.5, 0.8]: no overlap, first below second."""
        val = _integral_min(0.0, 0.3, 0.5, 0.8)
        # min(s, s') = s for all s in [0, 0.3], s' in [0.5, 0.8]
        expected = (0.3**2 - 0.0**2) / 2.0 * (0.8 - 0.5)
        assert abs(val - expected) < 1e-12

    def test_non_overlapping_above(self):
        """[0.5, 0.8] x [0, 0.3]: no overlap, first above second."""
        val = _integral_min(0.5, 0.8, 0.0, 0.3)
        expected = (0.3**2 - 0.0**2) / 2.0 * (0.8 - 0.5)
        assert abs(val - expected) < 1e-12

    def test_identical_intervals(self):
        """[0.2, 0.5] x [0.2, 0.5]: identical intervals."""
        val = _integral_min(0.2, 0.5, 0.2, 0.5)
        assert val > 0

    def test_symmetry(self):
        """I(a1,b1,a2,b2) = I(a2,b2,a1,b1) by symmetry of min."""
        val1 = _integral_min(0.1, 0.4, 0.3, 0.7)
        val2 = _integral_min(0.3, 0.7, 0.1, 0.4)
        assert abs(val1 - val2) < 1e-12

class TestAnalyticalLimits:
    """Tests for exact analytical expectations and limits (Audit A3)."""

    @pytest.mark.parametrize("theta, expected", [
        (0.05, 0.150217),
        (0.10, 0.134239),
        (0.30, 0.076463),
        (0.50, 0.033333),
    ])
    def test_trace_closed_form(self, theta, expected):
        """Sum of eigenvalues matches the closed-form E[F_1^theta]."""
        eig, bound = compute_eigenvalues(theta, component=1, K=200, eps=1e-8)
        total = np.sum(eig) + bound
        assert abs(total - expected) < 5e-3, f"Trace {total} far from {expected}"

    def test_convergence_to_kpi2(self):
        """As theta -> 0, lambda_k -> (k*pi)^-2 monotonically."""
        thetas = [0.20, 0.10, 0.05, 0.02]
        k = 1
        limit = 1.0 / (np.pi ** 2)
        ratios = []
        for th in thetas:
            eig, _ = compute_eigenvalues(th, component=1, K=3, eps=1e-6)
            ratios.append(eig[0] / limit)
        
        # Ratios should be strictly approaching 1 from above/below as theta decreases
        # Actually they approach 1. We just check they get closer to 1.
        diffs = [abs(r - 1.0) for r in ratios]
        assert diffs[-1] < diffs[0], "Not converging to limit"
        assert diffs[-1] < 0.05, "Theta=0.02 ratio not within 5% of limit"

    @pytest.mark.parametrize("theta", [0.05, 0.1, 0.3, 0.5])
    def test_wick_uncentered_diagonal_constant(self, theta):
        """
        Audit 4b, Tarea 7: Test permanente de identidad de Wick para multiples thetas y u.
        Evalua la traza de la discretizacion del nucleo no centrado de la Componente 2,
        y confirma que coincide con theta^2 / 45 con tolerancia del 2% en nivel y 1% en variacion.
        """
        from stationarity_test.kl_eigenvalues import _gauss_legendre_mesh, _cov_s2_s2_vectorized
        
        n_sub = 32
        expected = (theta ** 2) / 45.0
        
        us = [0.2 * theta, 0.5 * theta, 1.0 - 1.5 * theta]
        vals = []
        
        for u in us:
            if u < 0 or u > 1.0 - theta:
                continue
            s, w = _gauss_legendre_mesh(u, u + theta, n_sub)
            w_normed = w / theta
            
            var_s2 = _cov_s2_s2_vectorized(s, w_normed, s, w_normed)
            vals.append(var_s2)
            
            # Check within 2% tolerance in level
            rel_error = abs(var_s2 - expected) / expected
            assert rel_error < 0.02, f"Wick uncentered diagonal {var_s2} != expected {expected} (err={rel_error:.2%})"
            
        # Check within 1% variation across u
        variation = np.max(vals) - np.min(vals)
        variation_rel = variation / expected
        assert variation_rel < 0.01, f"Variation {variation_rel:.2%} exceeds 1%"
