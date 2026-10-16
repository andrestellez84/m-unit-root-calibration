"""
A12 - B12.0: tests unitarios de experiments/audit12_unitroot.py.

1. Paso GLS de Perron-Qu con k fijo frente a audit8_unitroot.np_statistics(k=k): 1e-12.
2. Ancho de Andrews replicado: hac_newey_west(dy, bandwidth=B) == hac_sigma_sq(y).
3. Con psi = 0 el generador MA es bit a bit audit8_design.gauss_rw con el mismo rng.
4. Factor de Bartlett: formula cerrada del MA(1) de la prediccion.
5. Pesos del ancla GLS de B12.F frente a rm_core.gls_mean.
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import audit12_unitroot as P                                       # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit8_design as D8                                         # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq, gls_mean       # noqa: E402

TOL = 1e-12


def paths():
    rng = np.random.default_rng(20260921)
    out = []
    for err in P.ERRORS:
        for n in (100, 200, 500):
            out.append(P.null_path(err, n, rng))
            out.append(P.alt_path(err, n, 0.9, rng))
    return out


@pytest.mark.parametrize("case", ["c", "ct"])
def test_gls_fixed_k_matches_np_statistics(case):
    worst = 0.0
    for y in paths():
        for k in (0, 1, 3, 6):
            a = P.gls_stats_fixed_k(y, case, k)
            b = U.np_statistics(y, case, k=k)
            for key in ("MZa", "MZt", "MSB", "s2_ar"):
                worst = max(worst, abs(a[key] - b[key]))
    assert worst <= TOL, worst


def test_andrews_bandwidth_replica():
    for y in paths():
        B = P.andrews_bandwidth(y)
        assert P.hac_with_bandwidth(y, B) == hac_sigma_sq(y)


def test_ma_psi0_is_gauss_rw():
    for n in (100, 200, 500):
        a = P.null_path(("ma", 0.0), n, np.random.default_rng(7 + n))
        b = D8.gauss_rw(n, np.random.default_rng(7 + n))
        assert np.array_equal(a, b)


def test_bartlett_factor_closed_form():
    for psi in (-0.8, -0.5, 0.5):
        for B in (0, 4, 8, 12):
            closed = 1.0 - 2.0 * psi / ((B + 1.0) * (1.0 + psi) ** 2)
            assert abs(P.bartlett_factor(("ma", psi), B) - closed) < TOL


def test_anchor_weights_match_gls_mean():
    import audit12_bF_anchor as F
    rng = np.random.default_rng(3)
    for n in (60, 200, 1000):
        w = F.anchor_weights(n)
        for _ in range(5):
            y = np.concatenate([[0.0], np.cumsum(rng.standard_normal(n))])
            assert abs(float(w @ y) - gls_mean(y)) < 1e-10
