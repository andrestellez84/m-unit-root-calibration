"""
A7 - tests permanentes del caso con constante y tendencia.

1. Regresion bit-identica de deterministics="c": compute_statistic reproduce
   exactamente (statistic y p_value) las 100 filas que produjo el paquete anterior
   a deterministics.py, guardadas en experiments/results/ct_verification_audit7.json.
2. Invariancia de escala de "ct": el estadistico no cambia con Y -> a*Y + b + c*t
   para a in {0.1, 10} y dos pares (b, c), con detrend "qd" y "ols".
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

from stationarity_test.statistic import compute_statistic          # noqa: E402
from stationarity_test.deterministics import detrend_ols, detrend_qd  # noqa: E402

VERIFY = os.path.join(ROOT, "experiments", "results", "ct_verification_audit7.json")
REL_TOL = 1e-9


@pytest.fixture(scope="module")
def design():
    import audit7_ct_design as D
    return D


def _regression_series(D):
    from power_comparison import generate_ar1, generate_rw_break_variance
    import audit7_common as C
    sb = C.seed_base(D.FAM_VERIFY, 0)
    out = []
    for i in range(D.N_REGRESSION):
        n = D.NULL_N[i % len(D.NULL_N)]
        rng = np.random.default_rng(sb + i)
        y = generate_rw_break_variance(n=n, ratio=1.0, rng=rng) if i % 2 == 0 \
            else generate_ar1(n=n, rho=0.93, rng=rng)
        out.append(y)
    return out


def test_c_bit_identical_to_pre_deterministics_package(design):
    with open(VERIFY, encoding="utf-8") as f:
        golden = json.load(f)["V1_regression_c"]["golden_baseline_rows"]
    series = _regression_series(design)
    assert len(series) == len(golden)
    for y, g in zip(series, golden):
        r = compute_statistic(y, design.THETA, design.R)
        assert r["statistic"] == g["statistic"]
        assert r["p_value"] == g["p_value"]


def test_c_is_the_default(design):
    y = _regression_series(design)[1]
    a = compute_statistic(y, design.THETA, design.R)
    b = compute_statistic(y, design.THETA, design.R, deterministics="c")
    assert a["statistic"] == b["statistic"] and a["p_value"] == b["p_value"]


@pytest.mark.parametrize("detrend", ["qd", "ols"])
def test_ct_scale_invariance(design, detrend):
    n = 200
    t = np.arange(n + 1, dtype=np.float64)
    sb = 76 * 10 ** 8 + 90000
    ys = [design.generate("dgp1", n, 0.93, sb, i)[0] for i in range(3)]
    ys += [design.generate("dgp3", n, 2.0, sb, 10 + i)[0] for i in range(3)]
    for y in ys:
        ref = compute_statistic(y, design.THETA, design.R, deterministics="ct", detrend=detrend)
        for a in (0.1, 10.0):
            for b, c in ((3.7, -0.25), (-150.0, 2.5)):
                r = compute_statistic(a * y + b + c * t, design.THETA, design.R,
                                      deterministics="ct", detrend=detrend)
                assert abs(r["statistic"] - ref["statistic"]) <= REL_TOL * ref["statistic"]


@pytest.mark.parametrize("fn", [detrend_ols, detrend_qd])
def test_detrending_removes_linear_trend_exactly(fn):
    rng = np.random.default_rng(2026)
    y = np.cumsum(rng.standard_normal(301))
    t = np.arange(301, dtype=np.float64)
    assert np.max(np.abs(fn(y + 5.0 - 0.3 * t) - fn(y))) < 1e-9


def test_invalid_deterministics_rejected(design):
    y = _regression_series(design)[0]
    with pytest.raises(ValueError):
        compute_statistic(y, design.THETA, design.R, deterministics="trend")
    with pytest.raises(ValueError):
        compute_statistic(y, design.THETA, design.R, deterministics="ct", detrend="gls")
