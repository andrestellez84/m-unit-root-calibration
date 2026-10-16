"""
A17, B17.1 (enmienda 7, lecturas E7.1 y E7.6): recalculo independiente de la evaluacion literal de eq:mstats del v18 en una
submuestra de los caminos de E6.4 (primeros caminos de cada celda), con codigo propio del test (no importa audit17_mstats),
frente a audit8_unitroot.np_statistics; y coherencia con los maximos declarados en mstats_v18_audit17.json.
"""
import json
import math
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
RES = os.path.join(ROOT, "experiments", "results")
SUB = 20


def load():
    p = os.path.join(RES, "mstats_v18_audit17.json")
    if not os.path.exists(p):
        pytest.skip("mstats_v18_audit17.json aun no existe")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def eq_mstats(y, trend, k):
    """Texto del v18: T = n + 1; GLS con abar = 1 + cbar/T; regresion sin intercepto en t = kmax+1..n; sigma2 = SSR/(n - kmax)."""
    T = len(y)
    n = T - 1
    cbar = -13.5 if trend else -7.0
    a = 1.0 + cbar / T
    Z = np.column_stack([np.ones(T), np.arange(T, dtype=float)]) if trend else np.ones((T, 1))
    yq = np.r_[y[0], y[1:] - a * y[:-1]]
    Zq = np.vstack([Z[0], Z[1:] - a * Z[:-1]])
    u = y - Z @ np.linalg.lstsq(Zq, yq, rcond=None)[0]
    kmax = int(12 * (T / 100) ** 0.25)
    du = u[1:] - u[:-1]
    rows = range(kmax + 1, n + 1)
    X = np.array([[u[t - 1]] + [du[t - 1 - j] for j in range(1, k + 1)] for t in rows])
    yy = np.array([du[t - 1] for t in rows])
    b = np.linalg.lstsq(X, yy, rcond=None)[0]
    ssr = float(np.sum((yy - X @ b) ** 2))
    s2 = ssr / (n - kmax) / (1 - b[1:].sum()) ** 2
    S = float(np.sum(u[:n] ** 2)) / T ** 2
    msb = math.sqrt(S / s2)
    mza = (u[n] ** 2 / T - s2) / (2 * S)
    return msb, mza * msb


def test_declared_passes():
    d = load()
    assert d["passes"] is True
    for c in d["cells"].values():
        assert c["variants"]["text"]["msb_rel"] <= d["criteria"]["msb_rel"]
        assert c["variants"]["text"]["mzt_abs"] <= d["criteria"]["mzt_abs"]
        assert c["kmax_disagreements"] == 0 and c["maic_disagreements"] == 0


def test_independent_subsample():
    import audit8_unitroot as U
    import audit16_code_check as K
    d = load()
    keys, _, _ = K.seeds()
    for ci, (n, case) in enumerate([(n, c) for n in K.NS for c in K.CASES]):
        rng = np.random.default_rng(np.random.SeedSequence(K.FAM, spawn_key=keys[ci]))
        for _ in range(SUB):
            y = np.concatenate([[0.0], np.cumsum(rng.standard_normal(n))])
            base = U.np_statistics(y, case)
            msb, mzt = eq_mstats(y, case == "ct", base["k"])
            assert abs(msb / base["MSB"] - 1) <= d["criteria"]["msb_rel"]
            assert abs(mzt - base["MZt"]) <= d["criteria"]["mzt_abs"]
