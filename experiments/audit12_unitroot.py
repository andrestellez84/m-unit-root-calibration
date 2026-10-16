"""
Auditoria A12 - generadores con errores MA(1)/AR(1), MAIC-MCO a la Perron-Qu (2007),
variante (b') y la fila de procedimientos de B12.A (codigo de experimentos; no toca src/).

(i)  Generadores (protocolo_audit12, lectura 3):
       MA(1): e = rng.standard_normal(n) -> e_1..e_n, e_0 = 0, v_t = e_t + psi e_{t-1};
       AR(1): z = rng.standard_normal(n + 1), v_0 = z_0 / sqrt(1 - phi^2), v_t = phi v_{t-1} + z_t;
       nula: y_0 = 0, y_t = y_{t-1} + v_t; alternativa: y_t = u_t, u_0 = 0, u_t = rho u_{t-1} + v_t.
     Con psi = 0 el MA es bit a bit audit8_design.gauss_rw con el mismo rng.
(ii) MAIC-MCO (PQ): k con la MAIC de Ng-Perron sobre el residuo MCO (constante o
     constante + tendencia), muestra comun kmax; con ese k, regresion ADF sobre el
     residuo GLS reestimada en t = k+1..T-1 (convencion de np_statistics(k=k)):
     s2_AR, MSB, MZ_t; DF-GLS con arch (lags = k). El paso GLS es codigo propio
     (QR propia), contrastado con audit8_unitroot.np_statistics(k=k) a 1e-12 en
     tests/test_audit12_unitroot.py.
(iii) (b') = RM-GLS con tau_1 = 0 y s2_AR de (ii).

El lado NP (MAIC-GLS) es exactamente el de audit9_engine.row (A9-A10), de modo que
con psi = 0 las columnas comunes reproducen las filas de A10 (Paso 0 de B12.0).
"""
import math
import warnings

import numpy as np

import audit8_unitroot as U
import audit9_engine as E
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.rm_core import hac_sigma_sq

THETA_FINAL = 0.02
ERRORS = (("ma", -0.8), ("ma", -0.5), ("ma", 0.0), ("ma", 0.5), ("ar", -0.5), ("ar", 0.5))
COLS_NP = ("s2", "B", "gls_t0.02", "gls_t0", "glsb_t0", "dfgls", "dfgls_p", "mzt", "msb", "k", "s2ar",
           "adf", "adf_p", "pp", "pp_p")
COLS_PQ = ("kpq", "s2ar_pq", "glsbp_t0", "mzt_pq", "msb_pq", "dfgls_pq", "dfgls_pq_p")
COLS_A = COLS_NP + COLS_PQ
RM_LIKE = ("gls_t0.02", "gls_t0", "glsb_t0", "glsbp_t0")
SIM_LOWER = ("dfgls", "dfgls_pq", "mzt", "mzt_pq", "msb", "msb_pq", "adf", "pp")
PROCS = ("gls_t0.02", "gls_t0", "glsb_t0", "glsbp_t0", "msb", "mzt", "msb_pq", "mzt_pq", "dfgls", "dfgls_pq",
         "adf", "pp")


def err_tag(err):
    kind, p = err
    return "%s_%s" % (kind, ("%g" % p).replace("-", "m").replace(".", "p"))


# ---------------------------------------------------------------------------
# (i) Generadores
# ---------------------------------------------------------------------------
def innovations(err, n, rng):
    """v_1..v_n de la estructura de error (lectura 3)."""
    kind, p = err
    if kind == "ma":
        e = rng.standard_normal(n)
        v = e.copy()
        v[1:] = e[1:] + p * e[:-1]          # e_0 = 0: v_1 = e_1
        return v
    z = rng.standard_normal(n + 1)
    v = np.empty(n + 1)
    v[0] = z[0] / math.sqrt(1.0 - p * p)
    for t in range(1, n + 1):
        v[t] = p * v[t - 1] + z[t]
    return v[1:]


def null_path(err, n, rng):
    v = innovations(err, n, rng)
    y = np.empty(n + 1)
    y[0] = 0.0
    for t in range(n):
        y[t + 1] = y[t] + v[t]
    return y


def alt_path(err, n, rho, rng):
    v = innovations(err, n, rng)
    y = np.empty(n + 1)
    y[0] = 0.0
    for t in range(n):
        y[t + 1] = rho * y[t] + v[t]
    return y


def omega2(err):
    kind, p = err
    return (1.0 + p) ** 2 if kind == "ma" else 1.0 / (1.0 - p) ** 2


def autocov(err, j):
    kind, p = err
    if kind == "ma":
        return 1.0 + p * p if j == 0 else (p if j == 1 else 0.0)
    return p ** j / (1.0 - p * p)


def bartlett_factor(err, B):
    """Sesgo poblacional del Bartlett con ancho B: [g0 + 2 sum_{j<=B} (1 - j/(B+1)) g_j] / omega^2."""
    s = autocov(err, 0) + 2.0 * sum((1.0 - j / (B + 1.0)) * autocov(err, j) for j in range(1, B + 1))
    return s / omega2(err)


# ---------------------------------------------------------------------------
# Ancho de Andrews (replica de hac_estimator.hac_newey_west, lectura 6)
# ---------------------------------------------------------------------------
def andrews_bandwidth(y):
    x = np.diff(np.asarray(y, dtype=np.float64))
    n = len(x)
    xc = x - np.mean(x)
    g0 = float(np.dot(xc, xc) / n)
    if g0 < 1e-15:
        return 0
    g1 = float(np.dot(xc[1:], xc[:n - 1]) / n)
    r = float(np.clip(g1 / g0, -0.99, 0.99))
    a = (4.0 * r ** 2) / max((1.0 - r ** 2) ** 2, 1e-10)
    B = int(np.ceil(1.1447 * (a * n) ** (1.0 / 3.0)))
    return max(0, min(B, n - 1))


def hac_with_bandwidth(y, B):
    return hac_newey_west(np.diff(np.asarray(y, dtype=np.float64)), bandwidth=B)


# ---------------------------------------------------------------------------
# (ii) MAIC-MCO (Perron-Qu)
# ---------------------------------------------------------------------------
def ols_detrend(y, case):
    y = np.asarray(y, dtype=np.float64)
    Z = U.deterministic_matrix(len(y), case)
    beta, *_ = np.linalg.lstsq(Z, y, rcond=None)
    return y - Z @ beta


def maic_ols_k(y, case, kmax=None):
    """k MAIC de Ng-Perron sobre el residuo MCO (muestra comun t = kmax+1..T-1)."""
    T = len(y)
    kmax = U.kmax_rule(T) if kmax is None else kmax
    yo = ols_detrend(y, case)
    path, rows, sum_y2 = U.adf_gls_path(yo, kmax)
    maic = []
    for kk, (ssr, b0, _) in enumerate(path):
        s2k = ssr / rows
        maic.append(math.log(s2k) + 2.0 * (b0 * b0 * sum_y2 / s2k + kk) / rows)
    return int(np.argmin(maic)), kmax


def gls_stats_fixed_k(y, case, k):
    """MZa, MZ_t, MSB y s2_AR sobre el residuo GLS con k fijo (muestra t = k+1..T-1), codigo propio."""
    y = np.asarray(y, dtype=np.float64)
    T = len(y)
    yt = U.gls_detrend(y, case)
    dy = np.diff(yt)
    X = np.empty((T - 1 - k, k + 1))
    X[:, 0] = yt[k:T - 1]
    for j in range(1, k + 1):
        X[:, j] = dy[k - j:T - 1 - j]
    yv = dy[k:]
    Q, R = np.linalg.qr(X)
    qy = Q.T @ yv
    beta = np.linalg.solve(R, qy)
    rows = T - 1 - k
    ssr = float(yv @ yv) - float(qy @ qy)
    s2 = (ssr / rows) / (1.0 - float(beta[1:].sum())) ** 2
    S = float(yt[:-1] @ yt[:-1]) / T ** 2
    yT2 = yt[-1] ** 2 / T
    mza = (yT2 - s2) / (2.0 * S)
    msb = math.sqrt(S / s2)
    return {"MZa": mza, "MZt": mza * msb, "MSB": msb, "s2_ar": s2}


def pq_statistics(y, case):
    k, kmax = maic_ols_k(y, case)
    st = gls_stats_fixed_k(y, case, k)
    st.update({"k": k, "kmax": kmax})
    return st


# ---------------------------------------------------------------------------
# Filas
# ---------------------------------------------------------------------------
def np_part(y, n, case):
    """Columnas COLS_NP con exactamente el codigo de audit9_engine.row (lado NP)."""
    s2 = hac_sigma_sq(y)
    out = {"s2": s2, "B": float(andrews_bandwidth(y)),
           "gls_t0.02": E.rmgls(y, n, THETA_FINAL, s2, case), "gls_t0": E.rmgls(y, n, 0.0, s2, case)}
    npr = U._safe(lambda: U.np_statistics(y, case), 1)
    if isinstance(npr, dict):
        s2ar = npr["s2_ar"]
        d_stat, d_p = U._safe(lambda: U.dfgls_maic(y, case, npr["k"]))
        out.update({"glsb_t0": E.rmgls(y, n, 0.0, s2ar, case), "dfgls": d_stat, "dfgls_p": d_p, "mzt": npr["MZt"],
                    "msb": npr["MSB"], "k": npr["k"], "s2ar": s2ar})
    else:
        out.update({c: float("nan") for c in ("glsb_t0", "dfgls", "dfgls_p", "mzt", "msb", "k", "s2ar")})
    a_stat, a_p = U.adf_aic(y, case)
    p_stat, p_p = U.pp(y, case)
    out.update({"adf": a_stat, "adf_p": a_p, "pp": p_stat, "pp_p": p_p})
    return out


def pq_part(y, n, case):
    pq = U._safe(lambda: pq_statistics(y, case), 1)
    if not isinstance(pq, dict):
        return {c: float("nan") for c in COLS_PQ}
    d_stat, d_p = U._safe(lambda: U.dfgls_maic(y, case, pq["k"]))
    return {"kpq": pq["k"], "s2ar_pq": pq["s2_ar"], "glsbp_t0": E.rmgls(y, n, 0.0, pq["s2_ar"], case),
            "mzt_pq": pq["MZt"], "msb_pq": pq["MSB"], "dfgls_pq": d_stat, "dfgls_pq_p": d_p}


def row_a(y, n, case):
    y = np.asarray(y, dtype=np.float64)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = np_part(y, n, case)
        d.update(pq_part(y, n, case))
    return [float(d[c]) for c in COLS_A]


def row_pq(y, n, cases=("c", "ct")):
    """Columnas PQ de los dos casos (calibracion de la familia 136 y B12.B)."""
    y = np.asarray(y, dtype=np.float64)
    out = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for case in cases:
            d = pq_part(y, n, case)
            out += [float(d[c]) for c in COLS_PQ]
    return out


def pq_cols(cases=("c", "ct")):
    return tuple("%s|%s" % (case, c) for case in cases for c in COLS_PQ)
