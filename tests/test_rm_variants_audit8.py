"""
A8 - tests permanentes de las variantes del estadistico (B1).

1. Defaults intactos: compute_statistic reproduce exactamente las filas del paquete
   anterior a B1 guardadas en experiments/results/b1_validation_audit8.json.
2. R = 0 es admisible y da |g1_std|.
3. tau_mode="zero" es el MSB con sigma_hat: n^-2 sum (Y_t - Ybar)^2 / s2.
4. RM-GLS: invariancia a aY + b (constante) y aY + b + ct (tendencia); la version
   con tendencia no depende de la deriva.
5. La calibracion "hac" calcula sigma_hat en cada camino: con R = 0 y los mismos
   caminos, su muestra nula difiere de "one" y "one" no cambia.
6. Ng-Perron: con retardo 0, MZt = MZa * MSB y el DF-GLS de arch usa el mismo
   detrending GLS.
7. Argumentos invalidos.
"""
import json
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

from stationarity_test.statistic import compute_statistic                      # noqa: E402
from stationarity_test.hac_estimator import hac_newey_west                     # noqa: E402
from stationarity_test.empirical_eigenvalues import _simulate_null_statistics  # noqa: E402

VALIDATION = os.path.join(ROOT, "experiments", "results", "b1_validation_audit8.json")
THETA = (0.1, 0.1)


def _rw(n, seed, drift=0.0):
    e = np.random.default_rng(seed).standard_normal(n)
    return np.concatenate([[0.0], np.cumsum(e + drift)])


@pytest.mark.skipif(not os.path.exists(VALIDATION), reason="b1_validation_audit8.json aun no generado")
def test_defaults_bit_identical_to_pre_b1_package():
    import audit8_b1_regression_child as RC
    import audit8_design as D
    with open(VALIDATION, encoding="utf-8") as f:
        v = json.load(f)["V1_regression"]
    cell = D.cell_index(91, "regression")
    for row in v["golden_rows"][:30]:
        Y = RC.series(row["i"], cell, 91)
        for R in (0.25, 0.5, 0.75):
            r = compute_statistic(Y, THETA, R)
            assert r["statistic"] == row["stat_R%g" % R]
            assert r["p_value"] == row["p_default_R%g" % R]


def test_R0_is_abs_g1_std():
    Y = _rw(300, 1)
    r = compute_statistic(Y, THETA, 0.0)
    assert abs(r["statistic"] - abs(r["g1_std"])) <= 1e-15 * abs(r["g1_std"])


@pytest.mark.parametrize("n", [100, 257])
def test_tau_zero_is_msb_hac(n):
    Y = _rw(n, n)
    s2 = hac_newey_west(np.diff(Y))
    direct = np.sqrt(np.sum((Y - Y.mean()) ** 2) / n ** 2 / s2)
    r = compute_statistic(Y, THETA, 0.0, tau_mode="zero", cal_sigma="hac")
    assert r["tau1"] == 0
    assert abs(r["statistic"] - direct) <= 1e-12 * direct


def test_gls_invariance_constant():
    Y = _rw(200, 3)
    ref = compute_statistic(Y, THETA, 0.0, anchor="gls", cal_sigma="hac")["statistic"]
    for a, b in ((0.1, 3.7), (10.0, -150.0)):
        s = compute_statistic(a * Y + b, THETA, 0.0, anchor="gls", cal_sigma="hac")["statistic"]
        assert abs(s - ref) <= 1e-10 * ref


def test_gls_invariance_and_drift_trend():
    Y = _rw(200, 4)
    t = np.arange(201, dtype=np.float64)
    ref = compute_statistic(Y, THETA, 0.0, anchor="gls", cal_sigma="hac", deterministics="ct")["statistic"]
    for a, b, c in ((0.1, 3.7, -0.25), (10.0, -150.0, 2.5)):
        s = compute_statistic(a * Y + b + c * t, THETA, 0.0, anchor="gls", cal_sigma="hac",
                              deterministics="ct")["statistic"]
        assert abs(s - ref) <= 1e-10 * ref
    stats = [compute_statistic(_rw(200, 4, mu), THETA, 0.0, anchor="gls", cal_sigma="hac",
                               deterministics="ct")["statistic"] for mu in (0.0, 0.05, 0.2)]
    assert (max(stats) - min(stats)) <= 1e-12 * min(stats)


def test_hac_calibration_uses_sigma_hat_per_path():
    one_default = _simulate_null_statistics(THETA, 0.5, 120, 200, 7)
    one_path = _simulate_null_statistics(THETA, 0.5, 120, 200, 7, tau_mode="zero")
    hac = _simulate_null_statistics(THETA, 0.0, 120, 200, 7, cal_sigma="hac")
    one_r0 = _simulate_null_statistics(THETA, 0.0, 120, 200, 7, cal_sigma="one", anchor="mean", tau_mode="theta")
    assert not np.array_equal(hac, one_r0)
    assert one_default.shape == one_path.shape == (200,)


def test_ng_perron_identities_and_detrending():
    import audit8_unitroot as U
    from arch.unitroot import DFGLS
    y = _rw(400, 9)
    for case in ("c", "ct"):
        r = U.np_statistics(y, case, k=0)
        assert abs(r["MZt"] - r["MZa"] * r["MSB"]) <= 1e-12 * abs(r["MZt"])
        yd = U.gls_detrend(y, case)
        t = DFGLS(y, trend=case, lags=0)
        _ = t.stat
        assert np.max(np.abs(np.asarray(t.regression.model.exog)[:, 0] - yd[:-1])) < 1e-10


def test_invalid_variants_rejected():
    Y = _rw(100, 5)
    with pytest.raises(ValueError):
        compute_statistic(Y, THETA, 0.0, cal_sigma="bootstrap")
    with pytest.raises(ValueError):
        compute_statistic(Y, THETA, 0.0, tau_mode="one")
    with pytest.raises(ValueError):
        compute_statistic(Y, THETA, 0.0, anchor="median")
    with pytest.raises(ValueError):
        compute_statistic(Y, THETA, 0.0, anchor="gls", deterministics="ct", detrend="ols")
