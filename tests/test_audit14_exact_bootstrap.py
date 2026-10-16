"""
A14 - validacion del EE bootstrap exacto del cuantil lineal (protocol_audit14.md, lectura 5):
la formula cerrada coincide con la enumeracion exhaustiva de las N^N remuestras.
"""
import itertools
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))

import audit14_exact_bootstrap as EB                               # noqa: E402


def brute(x, alpha):
    N = len(x)
    idx = np.array(list(itertools.product(range(N), repeat=N)))
    qs = np.quantile(np.asarray(x)[idx], alpha, axis=1)
    q = np.quantile(x, alpha)
    return float(np.sqrt(np.mean((qs - qs.mean()) ** 2))), float(qs.mean() - q)


def brute_order(x, m):
    N = len(x)
    idx = np.array(list(itertools.product(range(N), repeat=N)))
    v = np.sort(np.asarray(x)[idx], axis=1)[:, m - 1]
    return float(v.std())


@pytest.mark.parametrize("N", [3, 4, 5, 6])
@pytest.mark.parametrize("alpha", [0.01, 0.05, 0.25, 0.5, 0.9])
def test_exact_bootstrap_matches_enumeration(N, alpha):
    x = np.random.default_rng(N).standard_normal(N)
    res = EB.exact_bootstrap(x, alpha)
    se, bias = brute(x, alpha)
    assert abs(res["se"] - se) < 1e-12
    assert abs(res["bootstrap_mean_minus_estimate"] - bias) < 1e-12
    assert abs(res["se_maritz_jarrett"] - brute_order(x, res["mj_index"])) < 1e-12
    assert res["truncation_ok"]


def test_ties_are_handled():
    x = np.array([0.3, 0.3, -1.0, 2.0, 0.3])
    res = EB.exact_bootstrap(x, 0.4)
    se, _ = brute(x, 0.4)
    assert abs(res["se"] - se) < 1e-12


def test_large_sample_agrees_with_asymptotic_order():
    x = np.random.default_rng(7).standard_normal(20000)
    res = EB.exact_bootstrap(x, 0.05)
    from scipy import stats
    q = stats.norm.ppf(0.05)
    asy = np.sqrt(0.05 * 0.95 / 20000) / stats.norm.pdf(q)
    assert res["truncation_ok"]
    assert 0.8 < res["se"] / asy < 1.25
