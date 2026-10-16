"""
A8 - clave de cache de la nula (enmienda 2).

Hasta A8 la clave era (theta, R, n): una segunda llamada en el mismo proceso con
otro N_cal o con otra semilla devolvia la CDF de la primera.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from stationarity_test.empirical_eigenvalues import build_null_cdf, clear_cache  # noqa: E402

THETA = (0.1, 0.1)
N = 60


def test_ncal_10000_then_50000_same_process_differ():
    clear_cache()
    a = build_null_cdf(THETA, 0.5, N, N_cal=10000, seed=42)
    b = build_null_cdf(THETA, 0.5, N, N_cal=50000, seed=42)
    assert len(a.x) == 10000 and len(b.x) == 50000
    assert a is not b


def test_seed_and_variant_are_in_the_key():
    clear_cache()
    a = build_null_cdf(THETA, 0.5, N, N_cal=500, seed=1)
    b = build_null_cdf(THETA, 0.5, N, N_cal=500, seed=2)
    c = build_null_cdf(THETA, 0.5, N, N_cal=500, seed=1, cal_sigma="hac")
    d = build_null_cdf(THETA, 0.5, N, N_cal=500, seed=1, deterministics="ct")
    assert not np.array_equal(a.x, b.x)
    assert not np.array_equal(a.x, c.x)
    assert not np.array_equal(a.x, d.x)


def test_identical_arguments_hit_the_cache():
    clear_cache()
    a = build_null_cdf(THETA, 0.5, N, N_cal=500, seed=3)
    assert build_null_cdf(THETA, 0.5, N, N_cal=500, seed=3) is a
    ss = np.random.SeedSequence(3, spawn_key=(1,))
    s1 = build_null_cdf(THETA, 0.5, N, N_cal=500, seed=ss)
    assert build_null_cdf(THETA, 0.5, N, N_cal=500, seed=np.random.SeedSequence(3, spawn_key=(1,))) is s1
