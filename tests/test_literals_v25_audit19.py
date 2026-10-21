"""
A19, punto 4 (protocol_audit19.md, L4): pruebas literales de las cifras nuevas del manuscrito v25.

  Remark 1 / Apendice A.4: lambda(-7) = 1225, kappa(-7) ~ 39.7, E[S^2] exacto (0.360, 0.432, 0.481; 6 decimales 0.360459,
  0.431812, 0.480933), su coincidencia con la forma matricial, la cota 4.8e-6 de la expansion con m = n + cbar^2, y los valores
  de primer orden 0.302, 0.421, 0.480.
  Apendice A.5: la identidad muestral exacta sigma^2 = 2(C(0) - C(B+1))/(B+1) frente a hac_newey_west.
Aritmetica exacta (fractions y enteros de Python); no lee ningun JSON.
"""
from fractions import Fraction

import numpy as np
import pytest

from stationarity_test.hac_estimator import hac_newey_west

CBAR = -7
A = abs(CBAR)


def kappa(c):
    a = abs(c)
    return 2 * a * (Fraction(1, 2) + Fraction(a, 3))


def lam(c):
    a = abs(c)
    return Fraction(c * c * (c * c + 3 * a + 5), 3)


def es2_moments(n, c=CBAR):
    """E[S^2] con los momentos exactos de A.4: E[Y_n Ybar] = (n-1)/2, E[Ybar^2] = (n-1)(2n-1)/(6n), E[Y_n^2] = n."""
    a = abs(c)
    D = n + c * c
    eyny = Fraction(n - 1, 2)
    eyy = Fraction((n - 1) * (2 * n - 1), 6 * n)
    eyn2 = Fraction(n)
    cross = Fraction(a, D) * (n * eyny + eyn2 + a * n * eyy + a * eyny)       # E[beta * sum_{t=0}^n Y_t]
    square = Fraction(a * a, D * D) * (eyn2 + 2 * a * eyny + a * a * eyy)    # E[beta^2]
    return Fraction(1, 2) - 2 * cross / (n * (n + 1)) + square / n


def es2_matrix(n, c=CBAR):
    """(tr S - 2 1'S w + (n+1) w'S w)/(n(n+1)), S_ij = min(i, j) en t = 0..n, beta = w'Y; enteros exactos (w escalado por nD)."""
    a = abs(c)
    D = n + c * c
    W = np.full(n + 1, a * a, dtype=np.int64)     # n D w_t, t < n
    W[n] = a * n                                  # n D w_n
    idx = np.arange(n + 1, dtype=np.int64)
    S = np.minimum.outer(idx, idx)
    SW = S @ W                                    # n D (S w), exacto en int64 (< 6e10)
    tr = int(idx.sum())
    one_sw = sum(int(v) for v in SW)
    wsw = sum(int(w) * int(v) for w, v in zip(W, SW))
    total = Fraction(tr) - 2 * Fraction(one_sw, n * D) + (n + 1) * Fraction(wsw, (n * D) ** 2)
    return total / (n * (n + 1))


def test_lambda_minus_7_is_1225():
    assert lam(CBAR) == 1225
    # forma de A.4: cbar^2 (1 + |cbar| + cbar^2/3) + 2 cbar^2/3
    assert CBAR ** 2 * (1 + A + Fraction(CBAR ** 2, 3)) + Fraction(2 * CBAR ** 2, 3) == 1225


def test_kappa_minus_7():
    assert kappa(CBAR) == Fraction(119, 3)
    assert "%.1f" % float(kappa(CBAR)) == "39.7"


@pytest.mark.parametrize("n,six,three", [(200, "0.360459", "0.360"), (500, "0.431812", "0.432"), (2000, "0.480933", "0.481")])
def test_exact_moment(n, six, three):
    e = es2_moments(n)
    assert "%.6f" % float(e) == six
    assert "%.3f" % float(e) == three


@pytest.mark.parametrize("n", [200, 500, 2000])
def test_exact_moment_matches_matrix_form(n):
    assert es2_moments(n) == es2_matrix(n)


def test_moments_of_the_random_walk_against_the_matrix():
    n = 37
    idx = np.arange(n + 1)
    S = np.minimum.outer(idx, idx)
    assert Fraction(int(S[n, :n].sum()), n) == Fraction(n - 1, 2)              # E[Y_n Ybar]
    assert Fraction(int(S[:n, :n].sum()), n * n) == Fraction((n - 1) * (2 * n - 1), 6 * n)   # E[Ybar^2]


@pytest.mark.parametrize("n", [200, 500, 1000, 2000])
def test_expansion_within_4p8e_6(n):
    m = n + CBAR ** 2
    approx = Fraction(1, 2) - kappa(CBAR) / m + lam(CBAR) / (m * m)
    assert abs(approx - es2_moments(n)) <= Fraction(48, 10 ** 7)


@pytest.mark.parametrize("n,three", [(200, "0.302"), (500, "0.421"), (2000, "0.480")])
def test_first_order(n, three):
    assert "%.3f" % float(Fraction(1, 2) - kappa(CBAR) / n) == three


def bartlett_identity(dx, B):
    n = len(dx)
    x = np.concatenate([[0.0], np.cumsum(dx)])
    t = np.arange(n + 1)
    s = (x - x[0]) - t / n * (x[n] - x[0])

    def chat(k):
        return float(np.dot(s[:n + 1 - k], s[k:])) / n if k <= n else 0.0
    return 2.0 * (chat(0) - chat(B + 1)) / (B + 1)


def series(kind, n, rng):
    e = rng.standard_normal(n + 1)
    if kind == "iid":
        return e[1:]
    if kind == "ar05":
        out = np.empty(n)
        prev = 0.0
        for i in range(n):
            prev = 0.5 * prev + e[i + 1]
            out[i] = prev
        return out
    return e[1:] - 0.8 * e[:-1]                    # MA(-0.8)


@pytest.mark.parametrize("kind", ["iid", "ar05", "ma_m08"])
def test_bartlett_identity_against_hac_newey_west(kind):
    n = 200
    rng = np.random.default_rng(19)
    dx = series(kind, n, rng)
    for B in (0, 3, 7, 20, n - 1):
        assert abs(bartlett_identity(dx, B) - hac_newey_west(dx, bandwidth=B)) <= 1e-12, (kind, B)
