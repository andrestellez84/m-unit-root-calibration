"""
Auditoria A8 - comparadores de raiz unitaria (codigo de experimentos, no de produccion).

Ng y Perron (2001), familia M con detrending GLS:
  - y de longitud T (Y_0..Y_n, T = n + 1); detrending GLS con cbar = -7 (constante)
    o -13.5 (constante y tendencia), a = 1 + cbar / T (convencion de ERS y de
    arch.unitroot.DFGLS; deterministics.detrend_qd usa la misma).
  - Regresion ADF sobre el residuo yt: dyt_t = b0 yt_{t-1} + sum_{j=1..k} b_j dyt_{t-j} + e_t,
    estimada para k = 0..kmax sobre la MISMA muestra t = kmax+1..T-1 (indices 0..T-1),
    con kmax = floor(12 (T/100)^{1/4}) y una unica factorizacion QR (modelos anidados).
  - s2_AR(k) = sigma2_k / (1 - sum_j b_j)^2,  sigma2_k = SSR_k / (T - 1 - kmax).
  - MAIC original de Ng y Perron (2001): MAIC(k) = ln(sigma2_k) + 2 (tau_T(k) + k) / (T - 1 - kmax),
    tau_T(k) = b0^2 sum yt_{t-1}^2 / sigma2_k, sobre los mismos datos GLS-detrendidos.
    arch.unitroot.DFGLS no implementa MAIC (AIC/BIC/t-stat sobre datos detrendidos por
    MCO, a la Perron-Qu, sin la penalizacion tau_T), asi que se usa la MAIC original.
  - Con S = T^{-2} sum_{t=1}^{T-1} yt_{t-1}^2 ... en la notacion de indices 0-based:
    S = T^{-2} sum_{t=0}^{T-2} yt_t^2 y yT = yt_{T-1}:
      MZa = (T^{-1} yT^2 - s2) / (2 S)
      MSB = sqrt(S / s2)
      MZt = MZa * MSB
      MPT = (cbar^2 S - cbar T^{-1} yT^2) / s2                (constante)
      MPT = (cbar^2 S + (1 - cbar) T^{-1} yT^2) / s2          (tendencia)
    Todas rechazan en la cola inferior.
  - Valores criticos asintoticos al 5% de Ng y Perron (2001, Tabla 1).

DF-GLS (MAIC): estadistico t de arch.unitroot.DFGLS con el retardo seleccionado por la
MAIC anterior; p-valor asintotico de arch (mackinnonp, dist_type="dfgls").
DF-GLS (AIC, publicado): arch.unitroot.DFGLS con sus defaults (como las tablas publicadas).
P_T de ERS (punto optimo): P_T(cbar) = [S(a) - a S(1)] / w2, a = 1 + cbar / T, S(.) = SSR de la
regresion cuasi-diferenciada sobre los deterministas, w2 = s2_AR con el retardo MAIC del
caso (cbar = -7 o -13.5).
ADF (AIC): statsmodels.adfuller(autolag="AIC"); PP: arch.PhillipsPerron; KPSS:
statsmodels.kpss(nlags="auto"); ZA: arch.ZivotAndrews.
"""
import math
import warnings

import numpy as np

NP_CBAR = {"c": -7.0, "ct": -13.5}
NP_CV5 = {"c": {"MZa": -8.10, "MZt": -1.98, "MSB": 0.233, "MPT": 3.17},
          "ct": {"MZa": -17.3, "MZt": -2.91, "MSB": 0.168, "MPT": 5.48}}
NP_STATS = ("MZa", "MZt", "MSB", "MPT")
# Enmienda 1: MZa y MPT se retiran de B3-B5; solo estos entran como comparadores
NP_KEPT = ("MZt", "MSB")
# Elliott, Rothenberg y Stock (1996, Tabla I), P_T asintotico al 5% (solo diagnostico)
ERS_PT_CV5 = {"c": 3.26, "ct": 5.62}


def kmax_rule(T):
    return int(math.floor(12.0 * (T / 100.0) ** 0.25))


def deterministic_matrix(T, case):
    if case == "c":
        return np.ones((T, 1))
    return np.column_stack([np.ones(T), np.arange(1, T + 1, dtype=np.float64)])


def gls_detrend(y, case, cbar=None):
    y = np.asarray(y, dtype=np.float64)
    T = len(y)
    cbar = NP_CBAR[case] if cbar is None else cbar
    a = 1.0 + cbar / T
    z = deterministic_matrix(T, case)
    yq = y.copy()
    zq = z.copy()
    yq[1:] = y[1:] - a * y[:-1]
    zq[1:] = z[1:] - a * z[:-1]
    beta, *_ = np.linalg.lstsq(zq, yq, rcond=None)
    return y - z @ beta


def qd_ssr(y, case, a):
    T = len(y)
    z = deterministic_matrix(T, case)
    yq = y.copy()
    zq = z.copy()
    yq[1:] = y[1:] - a * y[:-1]
    zq[1:] = z[1:] - a * z[:-1]
    beta, *_ = np.linalg.lstsq(zq, yq, rcond=None)
    r = yq - zq @ beta
    return float(r @ r)


def adf_gls_path(yt, kmax):
    """SSR, b0, sum b_j y t-stat de b0 para k = 0..kmax sobre la muestra comun."""
    T = len(yt)
    dy = np.diff(yt)                       # dy[t-1] = yt[t] - yt[t-1], t = 1..T-1
    rows = T - 1 - kmax
    X = np.empty((rows, kmax + 1))
    X[:, 0] = yt[kmax:T - 1]               # yt_{t-1}
    for j in range(1, kmax + 1):
        X[:, j] = dy[kmax - j:T - 1 - j]   # dy_{t-j}
    yv = dy[kmax:]
    Q, Rm = np.linalg.qr(X)
    qy = Q.T @ yv
    tot = float(yv @ yv)
    out = []
    ssr = tot
    for k in range(kmax + 1):
        ssr -= qy[k] ** 2
        b = np.linalg.solve(Rm[:k + 1, :k + 1], qy[:k + 1]) if k > 0 else np.array([qy[0] / Rm[0, 0]])
        out.append((max(ssr, 1e-300), float(b[0]), float(b[1:].sum()) if k > 0 else 0.0))
    sum_y2 = float(X[:, 0] @ X[:, 0])
    return out, rows, sum_y2


def np_statistics(y, case, k=None, kmax=None):
    """
    Estadisticos M de Ng-Perron, DF-GLS con el mismo retardo y la informacion de la MAIC.
    k=None: seleccion MAIC; k entero: retardo fijo (kmax = k).
    """
    y = np.asarray(y, dtype=np.float64)
    T = len(y)
    cbar = NP_CBAR[case]
    yt = gls_detrend(y, case)
    if k is None:
        kmax = kmax_rule(T) if kmax is None else kmax
    else:
        kmax = int(k)
    path, rows, sum_y2 = adf_gls_path(yt, kmax)
    if k is None:
        maic = []
        for kk, (ssr, b0, _) in enumerate(path):
            s2k = ssr / rows
            tau = b0 * b0 * sum_y2 / s2k
            maic.append(math.log(s2k) + 2.0 * (tau + kk) / rows)
        k_sel = int(np.argmin(maic))
    else:
        k_sel = int(k)
    ssr, b0, bsum = path[k_sel]
    s2 = (ssr / rows) / (1.0 - bsum) ** 2
    S = float(yt[:-1] @ yt[:-1]) / T ** 2
    yT2 = yt[-1] ** 2 / T
    mza = (yT2 - s2) / (2.0 * S)
    msb = math.sqrt(S / s2)
    mzt = mza * msb
    if case == "c":
        mpt = (cbar * cbar * S - cbar * yT2) / s2
    else:
        mpt = (cbar * cbar * S + (1.0 - cbar) * yT2) / s2
    return {"MZa": mza, "MZt": mzt, "MSB": msb, "MPT": mpt, "k": k_sel, "kmax": kmax, "s2_ar": s2}


def dfgls_maic(y, case, k):
    from arch.unitroot import DFGLS
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t = DFGLS(y, trend=case, lags=int(k))
        return float(t.stat), float(t.pvalue)


def ers_pt(y, case, cbar, w2):
    """Estadistico P_T de ERS para un cbar dado (rechaza en la cola inferior)."""
    y = np.asarray(y, dtype=np.float64)
    T = len(y)
    a = 1.0 + cbar / T
    return (qd_ssr(y, case, a) - a * qd_ssr(y, case, 1.0)) / w2


def _safe(fn, n_out=2):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return fn()
    except Exception:
        return (float("nan"),) * n_out


def adf_aic(y, case="c"):
    from statsmodels.tsa.stattools import adfuller
    return _safe(lambda: tuple(float(v) for v in adfuller(y, regression=case, autolag="AIC")[:2]))


def pp(y, case="c"):
    from arch.unitroot import PhillipsPerron
    def f():
        t = PhillipsPerron(y, trend=case)
        return float(t.stat), float(t.pvalue)
    return _safe(f)


def dfgls_aic(y, case="c"):
    from arch.unitroot import DFGLS
    def f():
        t = DFGLS(y, trend=case)
        return float(t.stat), float(t.pvalue)
    return _safe(f)


def kpss_p(y, case="c"):
    from statsmodels.tsa.stattools import kpss
    return _safe(lambda: (float(kpss(y, regression=case, nlags="auto")[1]),), 1)[0]


def za(y, case="c"):
    from arch.unitroot import ZivotAndrews
    def f():
        t = ZivotAndrews(y, trend=case)
        return float(t.stat), float(t.pvalue)
    return _safe(f)


def comparator_row(y, case="c", with_kpss=False, with_dfgls_aic=True):
    """Estadisticos y p-valores asintoticos de todos los comparadores de tamano sobre una serie."""
    out = {}
    out["adf_stat"], out["adf_p"] = adf_aic(y, case)
    out["pp_stat"], out["pp_p"] = pp(y, case)
    npr = _safe(lambda: np_statistics(y, case), 1)
    if isinstance(npr, dict):
        for s in NP_KEPT:
            out["np_" + s] = npr[s]
        out["np_k"] = npr["k"]
        out["dfgls_stat"], out["dfgls_p"] = _safe(lambda: dfgls_maic(y, case, npr["k"]))
    else:
        for s in NP_KEPT:
            out["np_" + s] = float("nan")
        out["np_k"] = float("nan")
        out["dfgls_stat"], out["dfgls_p"] = float("nan"), float("nan")
    if with_dfgls_aic:
        out["dfglsaic_stat"], out["dfglsaic_p"] = dfgls_aic(y, case)
    if with_kpss:
        out["kpss_p"] = kpss_p(y, case)
    return out
