"""
Auditoria A15 - motor de B15.1 (protocol_audit15.md, lecturas 1.2-1.7; enmienda 2).

Funciones numba, sin tocar src/:
  - mzt_gls: MZ_t-GLS y MSB-GLS con la MAIC GLS de Ng-Perron, replica de
    audit8_unitroot.np_statistics (cuasi-diferencia GLS, regresion ADF-GLS en la muestra
    comun de kmax, QR, MAIC con tau_k, s2_AR = (SSR/filas)/(1 - sum b)^2).
  - bootUR 1.0.5 (enmienda 2, R1-R7): de_trend, adf_cpp, adf_selectlags (MAIC con la
    correccion de Perron-Qu), el DGP del bootstrap (residuos de la regresion ADF sin recorte)
    y los generadores SB y SWB; estadistico ADF-QD (DF-GLS).
  - Brazo (iii): AR(p) por MCO sobre Delta y centrado, p por AIC en la muestra comun de
    pmax retardos, residuos centrados remuestreados iid.
  - Brazo (iv): AWB de def:awb (el generador de audit9_engine.awb_pvalue).
  - Brazo (v'): DGP de bootUR (R2) con multiplicadores gaussianos (R4).
Los numeros aleatorios se generan fuera (numpy Generator del stream de cada brazo) y se
pasan como arreglos.
"""
import math

import numpy as np
from numba import njit

CBAR_NP = {"c": -7.0, "ct": -13.5}          # c-barra de Ng-Perron (audit8_unitroot.NP_CBAR)
CQD_BOOTUR = (7.0, 13.5)                     # c-barra de bootUR (de_trend, C:111)
SSR_FLOOR = 1e-300                           # piso de audit8_unitroot.adf_gls_path


def kmax_rule(T):
    return int(math.floor(12.0 * (T / 100.0) ** 0.25))


# ---------------------------------------------------------------------------
# MZ_t-GLS con MAIC GLS (replica de audit8_unitroot.np_statistics)
# ---------------------------------------------------------------------------
@njit(cache=True)
def _gls_detrend(y, ct, cbar):
    T = y.shape[0]
    a = 1.0 + cbar / T
    ncol = 2 if ct else 1
    z = np.empty((T, ncol))
    for t in range(T):
        z[t, 0] = 1.0
        if ct:
            z[t, 1] = t + 1.0
    yq = y.copy()
    zq = z.copy()
    for t in range(1, T):
        yq[t] = y[t] - a * y[t - 1]
        for c in range(ncol):
            zq[t, c] = z[t, c] - a * z[t - 1, c]
    beta = np.linalg.lstsq(zq, yq)[0]
    out = np.empty(T)
    for t in range(T):
        s = 0.0
        for c in range(ncol):
            s += z[t, c] * beta[c]
        out[t] = y[t] - s
    return out


@njit(cache=True)
def mzt_gls(y, ct, cbar, kmax):
    """(MZt, MSB, k) de Ng-Perron con MAIC GLS; y incluye y_0."""
    yt = _gls_detrend(y, ct, cbar)
    T = yt.shape[0]
    dy = yt[1:] - yt[:-1]
    rows = T - 1 - kmax
    X = np.empty((rows, kmax + 1))
    for r in range(rows):
        X[r, 0] = yt[kmax + r]
        for j in range(1, kmax + 1):
            X[r, j] = dy[kmax - j + r]
    yv = dy[kmax:].copy()
    Q, R = np.linalg.qr(X)
    qy = Q.T @ yv
    tot = 0.0
    for r in range(rows):
        tot += yv[r] * yv[r]
    sum_y2 = 0.0
    for r in range(rows):
        sum_y2 += X[r, 0] * X[r, 0]
    ssr = tot
    best = 1e308
    k_sel = 0
    ssr_sel = 0.0
    bsum_sel = 0.0
    for k in range(kmax + 1):
        ssr -= qy[k] ** 2
        s = max(ssr, SSR_FLOOR)
        # b = solve(R[:k+1,:k+1], qy[:k+1]) por sustitucion hacia atras
        b = np.empty(k + 1)
        for i in range(k, -1, -1):
            acc = qy[i]
            for j2 in range(i + 1, k + 1):
                acc -= R[i, j2] * b[j2]
            b[i] = acc / R[i, i]
        s2k = s / rows
        tau = b[0] * b[0] * sum_y2 / s2k
        m = math.log(s2k) + 2.0 * (tau + k) / rows
        if m < best:
            best = m
            k_sel = k
            ssr_sel = s
            bs = 0.0
            for j2 in range(1, k + 1):
                bs += b[j2]
            bsum_sel = bs
    s2 = (ssr_sel / rows) / (1.0 - bsum_sel) ** 2
    S = 0.0
    for t in range(T - 1):
        S += yt[t] * yt[t]
    S /= T * T
    yT2 = yt[T - 1] ** 2 / T
    mza = (yT2 - s2) / (2.0 * S)
    msb = math.sqrt(S / s2)
    return mza * msb, msb, k_sel


# ---------------------------------------------------------------------------
# bootUR 1.0.5 (enmienda 2, R1-R7)
# ---------------------------------------------------------------------------
@njit(cache=True)
def _de_trend(y, dc, qd, cqd):
    n = y.shape[0]
    if dc == 0:
        return y.copy()
    d = np.empty((n, dc))
    for t in range(n):
        for i in range(dc):
            d[t, i] = (t + 1.0) ** i
    c_n = (1.0 - cqd / n) if qd else 0.0
    dq = d.copy()
    yq = y.copy()
    for t in range(1, n):
        yq[t] = y[t] - c_n * y[t - 1]
        for i in range(dc):
            dq[t, i] = d[t, i] - c_n * d[t - 1, i]
    b = np.linalg.inv(dq.T @ dq) @ (dq.T @ yq)
    out = np.empty(n)
    for t in range(n):
        s = 0.0
        for i in range(dc):
            s += d[t, i] * b[i]
        out[t] = y[t] - s
    return out


@njit(cache=True)
def _adf(z, p, dc, qd, cqd, trim, trim_ic):
    """adf_cpp (C:145-185): (t, b, e) con e = y_dif - x b en todas las filas."""
    n = z.shape[0]
    y = _de_trend(z, dc, qd, cqd)
    y_lag = np.zeros(n)
    y_lag[1:] = y[:-1]
    y_dif = y - y_lag
    x = np.zeros((n, p + 1))
    for t in range(n):
        x[t, 0] = y_lag[t]
        for j in range(p):
            if t - j - 1 >= 0:
                x[t, j + 1] = y_dif[t - j - 1]
    trim_t = (p if trim_ic == 0 else 0) + trim_ic
    if trim:
        xl = x[trim_t + 1:, :]
        yl = y_dif[trim_t + 1:]
    else:
        xl = x
        yl = y_dif
    xxi = np.linalg.inv(xl.T @ xl)
    b = xxi @ (xl.T @ yl)
    e = y_dif - x @ b
    el = e[trim_t + 1:]
    s2 = 0.0
    for v in el:
        s2 += v * v
    s2 /= el.shape[0]
    t_adf = b[0] / math.sqrt(s2 * xxi[0, 0])
    return t_adf, b, e


@njit(cache=True)
def bootur_select(y, pmax, dc, qd, cqd, trim):
    """adf_selectlags_cpp (C:248-266) con MAIC, pmin = 0, sin reescalado: (t, p, b, e)."""
    n = y.shape[0]
    yols = _de_trend(y, dc, False, cqd)
    ylag = yols[pmax + 1:n - 1]
    yy = 0.0
    for v in ylag:
        yy += v * v
    neff = n - pmax - 1
    best = 1e308
    p_opt = 0
    for ip in range(pmax + 1):
        t_, b, e = _adf(y, ip, dc, False, cqd, trim, pmax)
        et = e[n - neff:]
        s2 = 0.0
        for v in et:
            s2 += v * v
        s2 /= neff
        tk = yy * b[0] * b[0] / s2
        ic = math.log(s2) + (ip + tk) * 2.0 / neff
        if ic < best:
            best = ic
            p_opt = ip
    t_adf, b, e = _adf(y, p_opt, dc, qd, cqd, trim, 0)
    return t_adf, p_opt, b, e


@njit(cache=True)
def bootur_stat(y, pmax, dc, cqd):
    """Estadistico ADF-QD de boot_adf(detrend = 'QD') y retardo elegido (R1)."""
    t_adf, p, b, e = bootur_select(y, pmax, dc, True, cqd, True)
    return t_adf, p


@njit(cache=True)
def bootur_dgp(y, pmax, dc, cqd):
    """R2: residuos e (T valores, sin centrar) y ar_est (pmax, relleno con ceros)."""
    t_adf, p, b, e = bootur_select(y, pmax, dc, False, cqd, False)
    ar = np.zeros(pmax)
    for j in range(p):
        ar[j] = b[j + 1]
    return e, ar


@njit(cache=True)
def gen_ar_cumsum(x, ar, lead_zero):
    """gen_AR_cpp con init 0 y acumulado (C:442-461, C:517-520); lead_zero antepone y_0 = 0."""
    T = x.shape[0]
    p = ar.shape[0]
    u = np.zeros(T + p)
    for t in range(p, T + p):
        s = x[t - p]
        for j in range(p):
            s += ar[j] * u[t - 1 - j]
        u[t] = s
    off = 1 if lead_zero else 0
    y = np.empty(T + off)
    if lead_zero:
        y[0] = 0.0
    acc = 0.0
    for t in range(T):
        acc += u[p + t]
        y[t + off] = acc
    return y


# ---------------------------------------------------------------------------
# Brazo (iii): sieve sobre Delta y centrado con AIC
# ---------------------------------------------------------------------------
@njit(cache=True)
def sieve_fit(y, pmax):
    """AR(p) por MCO sobre x = Delta y - media, muestra comun t = pmax..n-1; p por AIC. (resid centrados, ar)."""
    dy = y[1:] - y[:-1]
    n = dy.shape[0]
    m = 0.0
    for v in dy:
        m += v
    x = dy - m / n
    neff = n - pmax
    best = 1e308
    best_p = 0
    best_ar = np.zeros(0)
    best_e = x[pmax:].copy()
    for p in range(pmax + 1):
        yv = x[pmax:].copy()
        if p == 0:
            e = yv
            ar = np.zeros(0)
        else:
            Xm = np.empty((neff, p))
            for r in range(neff):
                for j in range(p):
                    Xm[r, j] = x[pmax + r - j - 1]
            ar = np.linalg.lstsq(Xm, yv)[0]
            e = yv - Xm @ ar
        ssr = 0.0
        for v in e:
            ssr += v * v
        aic = math.log(ssr / neff) + 2.0 * p / neff
        if aic < best:
            best = aic
            best_p = p
            best_ar = ar.copy()
            best_e = e.copy()
    me = 0.0
    for v in best_e:
        me += v
    return best_e - me / best_e.shape[0], best_ar, best_p


# ---------------------------------------------------------------------------
# p-valores por brazo (R replicas; numeros aleatorios pasados desde fuera)
# ---------------------------------------------------------------------------
@njit(cache=True)
def pvalue_sieve(y, ct, cbar, kmax, pmax, idx):
    """Brazo (iii): idx (R x n) indices en 0..len(e)-1. p = (1 + #{T* <= T})/(R + 1)."""
    t_obs = mzt_gls(y, ct, cbar, kmax)[0]
    e, ar, p = sieve_fit(y, pmax)
    R = idx.shape[0]
    n = idx.shape[1]
    cnt = 0
    for r in range(R):
        es = np.empty(n)
        for t in range(n):
            es[t] = e[idx[r, t]]
        ys = gen_ar_cumsum(es, ar, True)
        if mzt_gls(ys, ct, cbar, kmax)[0] <= t_obs:
            cnt += 1
    return (1.0 + cnt) / (R + 1.0), t_obs, p


@njit(cache=True)
def pvalue_awb(y, ct, cbar, kmax, gamma, nu):
    """Brazo (iv): nu (R x n) N(0,1); xi_1 = nu_1, xi_t = g xi_{t-1} + sqrt(1-g^2) nu_t."""
    t_obs = mzt_gls(y, ct, cbar, kmax)[0]
    dy = y[1:] - y[:-1]
    n = dy.shape[0]
    m = 0.0
    for v in dy:
        m += v
    u = dy - m / n
    b = math.sqrt(1.0 - gamma * gamma)
    R = nu.shape[0]
    cnt = 0
    ys = np.empty(n + 1)
    for r in range(R):
        xi = nu[r, 0]
        ys[0] = 0.0
        acc = xi * u[0]
        ys[1] = acc
        for t in range(1, n):
            xi = gamma * xi + b * nu[r, t]
            acc += xi * u[t]
            ys[t + 1] = acc
        if mzt_gls(ys, ct, cbar, kmax)[0] <= t_obs:
            cnt += 1
    return (1.0 + cnt) / (R + 1.0), t_obs


@njit(cache=True)
def pvalue_swb(y, ct, cbar, kmax, pmax, dc, cqd, z):
    """Brazo (v') «SWB (bootUR)»: DGP R2 + multiplicadores R4; estadistico MZ_t-GLS. z (R x T)."""
    t_obs = mzt_gls(y, ct, cbar, kmax)[0]
    e, ar = bootur_dgp(y, pmax, dc, cqd)
    R = z.shape[0]
    T = z.shape[1]
    cnt = 0
    for r in range(R):
        es = np.empty(T)
        for t in range(T):
            es[t] = z[r, t] * e[t]
        ys = gen_ar_cumsum(es, ar, False)
        if mzt_gls(ys, ct, cbar, kmax)[0] <= t_obs:
            cnt += 1
    return (1.0 + cnt) / (R + 1.0), t_obs


@njit(cache=True)
def pvalue_sb(y, ct, cbar, kmax, pmax, dc, cqd, idx):
    """Brazo (iii) «SB (bootUR)» (enmienda 3, E3.3): DGP R2 + R3 (idx en 0..T-l); estadistico MZ_t-GLS."""
    t_obs = mzt_gls(y, ct, cbar, kmax)[0]
    e, ar = bootur_dgp(y, pmax, dc, cqd)
    R = idx.shape[0]
    T = idx.shape[1]
    cnt = 0
    es = np.empty(T)
    for r in range(R):
        for t in range(T):
            es[t] = e[idx[r, t]]
        ys = gen_ar_cumsum(es, ar, False)
        if mzt_gls(ys, ct, cbar, kmax)[0] <= t_obs:
            cnt += 1
    return (1.0 + cnt) / (R + 1.0), t_obs


# ---------------------------------------------------------------------------
# Replica de boot_adf para el Paso 0 (estadistico ADF-QD; p = #{t* < t}/B)
# ---------------------------------------------------------------------------
@njit(cache=True)
def bootur_pvalue(y, pmax, dc, cqd, swb, draws_i, draws_z):
    t_obs, p_obs = bootur_stat(y, pmax, dc, cqd)
    e, ar = bootur_dgp(y, pmax, dc, cqd)
    B = draws_z.shape[0] if swb else draws_i.shape[0]
    T = y.shape[0]
    cnt = 0
    es = np.empty(T)
    for r in range(B):
        for t in range(T):
            es[t] = draws_z[r, t] * e[t] if swb else e[draws_i[r, t]]
        ys = gen_ar_cumsum(es, ar, False)
        if bootur_stat(ys, pmax, dc, cqd)[0] < t_obs:
            cnt += 1
    return cnt / B, t_obs, p_obs


def bootur_block_length(T):
    return int(round(1.75 * T ** (1.0 / 3.0)))
