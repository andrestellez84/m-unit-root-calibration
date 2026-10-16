"""
A7 - tests permanentes de kappa_2 (CUSUM de cuadrados de Sanso-Arago-Carrion).

1. Los valores criticos asintoticos son los cuantiles del supremo del puente
   browniano (distribucion de Kolmogorov).
2. El estadistico es invariante a la escala de los residuos.
3. Rechaza un quiebre de varianza fuerte.
4. Bajo ruido iid homoscedastico no sobre-rechaza al valor critico asintotico
   (en muestra finita es conservador; medido en A7).
"""
import os
import sys

import numpy as np
import pytest
from scipy.stats import kstwobign

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

from audit7_kappa2 import KAPPA2_CRITICAL, kappa2_statistic   # noqa: E402


@pytest.mark.parametrize("level", sorted(KAPPA2_CRITICAL))
def test_critical_values_are_sup_brownian_bridge_quantiles(level):
    assert abs(KAPPA2_CRITICAL[level] - kstwobign.ppf(1.0 - level)) < 1e-3


def test_scale_invariance():
    e = np.random.default_rng(11).standard_normal(500)
    k = kappa2_statistic(e)
    for a in (0.01, 3.0, 250.0):
        assert abs(kappa2_statistic(a * e) - k) < 1e-9 * k


def test_rejects_strong_variance_break():
    rng = np.random.default_rng(12)
    e = np.concatenate([rng.standard_normal(250), 3.0 * rng.standard_normal(250)])
    assert kappa2_statistic(e) > KAPPA2_CRITICAL[0.05]


def test_not_oversized_under_iid_null():
    rng = np.random.default_rng(13)
    reps, T = 400, 500
    rej = sum(kappa2_statistic(rng.standard_normal(T)) > KAPPA2_CRITICAL[0.05] for _ in range(reps))
    assert rej / reps < 0.08
