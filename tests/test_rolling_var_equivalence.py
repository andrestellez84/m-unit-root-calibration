"""
Test: rolling_var O(n) equivalence against reference implementation.

Verifies that the O(n) Kahan-compensated sliding-window rolling_var
produces numerically equivalent results to the O(n*tau) two-pass
reference implementation.
"""
import numpy as np
import pytest

from stationarity_test.utils import rolling_var, rolling_var_reference


@pytest.mark.parametrize("n", [100, 500, 2000])
def test_rolling_var_equivalence(n):
    """
    200 Gaussian series per (n, tau) configuration.
    All tau in {5, 50, n//4} (where applicable).
    Threshold: max|diff| < 1e-9.
    """
    rng = np.random.default_rng(12345 + n)
    taus = [t for t in [5, 50, n // 4] if t < n]

    for tau in taus:
        max_diff = 0.0
        for _ in range(200):
            x = np.cumsum(rng.standard_normal(n + 1))
            v_ref = rolling_var_reference(x, tau)
            v_new = rolling_var(x, tau)
            assert v_ref.shape == v_new.shape, (
                f"Shape mismatch: ref={v_ref.shape}, new={v_new.shape}"
            )
            diff = np.max(np.abs(v_ref - v_new))
            max_diff = max(max_diff, diff)

        assert max_diff < 1e-9, (
            f"n={n}, tau={tau}: max|diff|={max_diff:.2e} >= 1e-9"
        )


def test_rolling_var_nonnegative():
    """Verify rolling_var never returns negative values."""
    rng = np.random.default_rng(99999)
    for _ in range(100):
        x = np.cumsum(rng.standard_normal(501))
        for tau in [5, 50, 125]:
            v = rolling_var(x, tau)
            assert np.all(v >= 0.0), (
                f"Negative variance detected: min={v.min()}"
            )


def test_rolling_var_constant_series():
    """For a constant series, variance should be exactly 0."""
    x = np.ones(101, dtype=np.float64) * 42.0
    v = rolling_var(x, 10)
    assert np.allclose(v, 0.0, atol=1e-15), (
        f"Constant series should have zero variance, got max={v.max()}"
    )
