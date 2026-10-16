"""
Auditoria A9 - motor de estadisticos (codigo de experimentos; no toca produccion).

Una fila por trayectoria con todas las columnas que piden B9.1-B9.5, calculadas
con las mismas rutinas que A8:

  RM-GLS con theta in THETAS (theta = 0: tau_1 = 0, el estadistico sin suavizado
  rodante), calibracion hac (sigma_hat HAC de Newey-West con piloto de Andrews
  alpha(1), la de produccion); RM anclado en la media (theta = 0.1); MSB-HAC
  (anclaje en la media, tau = 0); la variante (b) de B9.3: RM-GLS con tau = 0 y
  escala s2_AR (MAIC) en lugar de sigma_hat HAC; ADF (AIC), PP, DF-GLS (MAIC),
  MZt-GLS, MSB-GLS (MAIC original), KPSS y ZA con sus estadisticos y p-valores
  asintoticos; P_T de ERS para la envolvente.

Columnas: "<caso>|<nombre>", caso in {"c", "ct"}; la escala HAC es comun a los
dos casos (se calcula sobre las primeras diferencias de la serie original) y se
guarda como "s2".

Calibracion bajo la Ec. (3): los caminos son exactamente los de produccion
(build_null_cdf con semilla 42: default_rng(42), una llamada standard_normal(n)
por camino, Y_0 = 0, Y = cumsum), de modo que la columna RM-GLS theta = 0.1 es
bit a bit la nula de produccion (control en cada analisis). Todos los
procedimientos se calibran sobre esos mismos caminos, con la seleccion de
retardos dentro del bucle.
"""
import math
import os
import time
import warnings

import numpy as np
from joblib import Parallel, delayed

import audit8_unitroot as U
import audit9_common as C
from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.rm_core import hac_sigma_sq, path_statistic

C1, C2 = DEFAULT_SCALING_EXPONENTS[1], DEFAULT_SCALING_EXPONENTS[2]
THETAS = (0.0, 0.02, 0.05, 0.1, 0.2)
THETA_A8 = 0.1
CASES = ("c", "ct")
CAL_SEED = 42
N_CAL = 50000
C_GRID = tuple(float(c) for c in range(0, 31)) + (13.5,)
CBARS = tuple(-c for c in C_GRID if c > 0)
DFGLS_CV5_PUBLISHED = {"c": -1.95, "ct": -2.89}   # ERS (1996): DF sin constante (c) y Tabla 1 (ct), asintotico al 5%
MSB_CV5_PUBLISHED = {"c": U.NP_CV5["c"]["MSB"], "ct": U.NP_CV5["ct"]["MSB"]}


def tname(theta):
    return "gls_t%g" % theta


def taus(theta, n):
    """tau_1 = round(theta n) acotado a [2, n // 2]; theta = 0 da tau_1 = 0 (tau_2 no interviene con R = 0)."""
    t = min(max(2, int(round(max(theta, 0.0) * n))), n // 2)
    return (0 if theta == 0 else t), t


def rmgls(y, n, theta, s2, case):
    t1, t2 = taus(theta, n)
    return path_statistic(y, n, t1, t2, 0.0, s2, C1, C2, deterministics=case, anchor="gls", need_g2=False)[0]


def rm_mean(y, n, theta, s2, case, zero=False):
    t1, t2 = taus(theta, n)
    return path_statistic(y, n, 0 if zero else t1, t2, 0.0, s2, C1, C2, deterministics=case, anchor="mean",
                          need_g2=False)[0]


def kpss_both(y, case="c"):
    from statsmodels.tsa.stattools import kpss

    def f():
        r = kpss(y, regression=case, nlags="auto")
        return float(r[0]), float(r[1])
    return U._safe(f)


# ---------------------------------------------------------------------------
# Esquema de columnas
# ---------------------------------------------------------------------------
BASE = tuple(tname(t) for t in THETAS) + ("rm_t0.1", "msbhac", "glsb_t0", "dfgls", "dfgls_p", "mzt", "msb", "k", "s2ar")
ADFPP = ("adf", "adf_p", "pp", "pp_p")


def columns(cases=CASES, adfpp=True, kpss=False, za=False, pt=False):
    cols = ["s2"]
    for case in cases:
        cols += ["%s|%s" % (case, b) for b in BASE]
        if adfpp:
            cols += ["%s|%s" % (case, b) for b in ADFPP]
        if kpss and case == "c":
            cols += ["c|kpss", "c|kpss_p"]
        if za and case == "c":
            cols += ["c|za", "c|za_p"]
        if pt:
            cols += ["%s|pt_%g" % (case, -cb) for cb in CBARS]
    return tuple(cols)


def row(y, n, cases=CASES, adfpp=True, kpss=False, za=False, pt=False):
    y = np.asarray(y, dtype=np.float64)
    s2 = hac_sigma_sq(y)
    out = [s2]
    for case in cases:
        vals = [rmgls(y, n, t, s2, case) for t in THETAS]
        vals.append(rm_mean(y, n, THETA_A8, s2, case))
        vals.append(rm_mean(y, n, THETA_A8, s2, case, zero=True))
        npr = U._safe(lambda: U.np_statistics(y, case), 1)
        if isinstance(npr, dict):
            s2ar = npr["s2_ar"]
            glsb = rmgls(y, n, 0.0, s2ar, case)
            d_stat, d_p = U._safe(lambda: U.dfgls_maic(y, case, npr["k"]))
            vals += [glsb, d_stat, d_p, npr["MZt"], npr["MSB"], npr["k"], s2ar]
        else:
            vals += [float("nan")] * 7
        if adfpp:
            vals += list(U.adf_aic(y, case)) + list(U.pp(y, case))
        if kpss and case == "c":
            vals += list(kpss_both(y, "c"))
        if za and case == "c":
            vals += list(U.za(y, "c"))
        if pt:
            w2 = npr["s2_ar"] if isinstance(npr, dict) else float("nan")
            vals += [U.ers_pt(y, case, cb, w2) for cb in CBARS]
        out += vals
    return [float(v) for v in out]


def index(cols):
    return {c: i for i, c in enumerate(cols)}


# ---------------------------------------------------------------------------
# Lotes paralelos para run_cell (A8)
# ---------------------------------------------------------------------------
def make_batch_fn(path_fn, n, cores, **flags):
    def _rows(idx):
        return [row(path_fn(i), n, **flags) for i in idx]

    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def warm(cores):
    Parallel(n_jobs=cores, backend="loky")(delayed(len)([k]) for k in range(cores))


# ---------------------------------------------------------------------------
# Calibracion sobre los caminos de produccion (semilla 42)
# ---------------------------------------------------------------------------
def cal_chunk_size(n):
    return int(min(2000, max(50, 250000 // n)))


def _cal_rows(block, n, flags):
    out = []
    for z in block:
        Y = np.empty(n + 1, dtype=np.float64)
        Y[0] = 0.0
        np.cumsum(z, out=Y[1:])
        out.append(row(Y, n, **flags))
    return np.asarray(out, dtype=np.float64)


def cal_flags(n):
    return {"cases": CASES, "adfpp": True, "kpss": n in (200, 500, 1000), "za": n in (200, 500, 1000),
            "pt": n == 2000}


def calibration(n, cores, ckpt_dir, t_block, max_seconds, resume_cmd, n_cal=N_CAL, log=print):
    """Muestra nula en n (N_cal caminos de produccion); checkpoint por trozo en npz; reanudable."""
    flags = cal_flags(n)
    cols = columns(**flags)
    final = os.path.join(ckpt_dir, "cal_n%d.npz" % n)
    if os.path.exists(final):
        with np.load(final) as z:
            if bool(z["complete"]) and z["rows"].shape == (n_cal, len(cols)):
                return z["rows"], cols
    os.makedirs(ckpt_dir, exist_ok=True)
    m = cal_chunk_size(n)
    n_chunks = int(math.ceil(n_cal / m))
    rng = np.random.default_rng(CAL_SEED)

    def cpath(j):
        return os.path.join(ckpt_dir, "cal_n%d_m%d_j%05d.npz" % (n, m, j))
    j = 0
    sps = None
    while j < n_chunks:
        wave = []
        for jj in range(j, min(n_chunks, j + cores)):
            k = min(m, n_cal - jj * m)
            block = rng.standard_normal((k, n))   # mismo orden de consumo que k llamadas standard_normal(n)
            if not os.path.exists(cpath(jj)):
                wave.append((jj, block))
        if wave:
            need = (sps or 0.0) * sum(b.shape[0] for _, b in wave) / max(1, min(cores, len(wave)))
            if time.time() - t_block + need > max_seconds:
                raise C.BudgetExhausted("cal n=%d: trozo %d no cabe en el tope.\nREANUDAR CON:\n  %s" % (n, j, resume_cmd))
            t0 = time.time()
            res = Parallel(n_jobs=min(cores, len(wave)), backend="loky")(
                delayed(_cal_rows)(b, n, flags) for _, b in wave)
            el = time.time() - t0
            for (jj, b), r in zip(wave, res):
                tmp = cpath(jj) + ".tmp.npz"
                np.savez(tmp, rows=r, complete=True, elapsed=el)
                os.replace(tmp, cpath(jj))
            sps = el * min(cores, len(wave)) / sum(b.shape[0] for _, b in wave)
            log("    cal n=%d trozos %d-%d de %d  %.1f s" % (n, j, j + len(wave) - 1, n_chunks, el))
        j += cores
    parts = []
    for jj in range(n_chunks):
        with np.load(cpath(jj)) as z:
            parts.append(z["rows"])
    rows = np.vstack(parts)
    tmp = final + ".tmp.npz"
    np.savez(tmp, rows=rows, cols=np.array(cols), complete=True)
    os.replace(tmp, final)
    for jj in range(n_chunks):
        os.remove(cpath(jj))
    return rows, cols


def production_control(n, rows, cols):
    """RM-GLS theta = 0.1 y theta = 0 (hac) frente a _simulate_null_statistics de produccion."""
    from stationarity_test.empirical_eigenvalues import _simulate_null_statistics
    I = index(cols)
    out = {}
    for case in CASES:
        ref = _simulate_null_statistics((0.1, 0.1), 0.0, n, rows.shape[0], CAL_SEED, deterministics=case,
                                        cal_sigma="hac", anchor="gls")
        out["%s|gls_t0.1" % case] = float(np.max(np.abs(rows[:, I["%s|gls_t0.1" % case]] - ref)))
        ref0 = _simulate_null_statistics((0.1, 0.1), 0.0, n, rows.shape[0], CAL_SEED, deterministics=case,
                                         cal_sigma="hac", anchor="gls", tau_mode="zero")
        out["%s|gls_t0" % case] = float(np.max(np.abs(rows[:, I["%s|gls_t0" % case]] - ref0)))
    return out


# ---------------------------------------------------------------------------
# Reglas de rechazo
# ---------------------------------------------------------------------------
RM_LIKE = tuple(tname(t) for t in THETAS) + ("rm_t0.1", "msbhac", "glsb_t0")
SIM_LOWER = ("adf", "pp", "dfgls", "mzt", "msb", "kpss", "za")


def rejector(cal_rows, cal_cols, case):
    """Rechazo con valores criticos simulados en el mismo n y caso (cola inferior en todos)."""
    from stationarity_test.empirical_eigenvalues import cdf_from_null_stats
    I = index(cal_cols)
    cdfs, qs = {}, {}
    for p in RM_LIKE:
        cdfs[p] = cdf_from_null_stats(cal_rows[:, I["%s|%s" % (case, p)]])
    for p in SIM_LOWER:
        key = "%s|%s" % (case, p)
        if key in I:
            qs[p] = float(np.nanquantile(cal_rows[:, I[key]], C.ALPHA))

    def rej(rows, cols, p):
        J = index(cols)
        x = rows[:, J["%s|%s" % (case, p)]]
        if p in cdfs:
            return np.clip(cdfs[p](x), 0.0, 1.0) < C.ALPHA
        return np.nan_to_num(x, nan=np.inf) < qs[p]
    return rej, qs


def reject_asy(rows, cols, case, p):
    """Rechazo con el valor critico asintotico (convencion de A8)."""
    J = index(cols)
    if p in ("adf", "pp", "dfgls"):
        return np.nan_to_num(rows[:, J["%s|%s_p" % (case, p)]], nan=1.0) < C.ALPHA
    if p == "mzt":
        return np.nan_to_num(rows[:, J["%s|mzt" % case]], nan=np.inf) < U.NP_CV5[case]["MZt"]
    if p == "msb":
        return np.nan_to_num(rows[:, J["%s|msb" % case]], nan=np.inf) < U.NP_CV5[case]["MSB"]
    if p == "kpss":     # KPSS como test de estacionariedad: rechaza la estacionariedad (A8)
        return np.nan_to_num(rows[:, J["c|kpss_p"]], nan=1.0) < C.ALPHA
    if p == "za":
        return np.nan_to_num(rows[:, J["c|za_p"]], nan=1.0) < C.ALPHA
    raise KeyError(p)


def reject_published(rows, cols, case, p):
    """B9.4: valores criticos asintoticos publicados (ERS 1996 para DF-GLS; Ng-Perron 2001 para MSB)."""
    J = index(cols)
    cv = DFGLS_CV5_PUBLISHED[case] if p == "dfgls" else MSB_CV5_PUBLISHED[case]
    return np.nan_to_num(rows[:, J["%s|%s" % (case, p)]], nan=np.inf) < cv


# ---------------------------------------------------------------------------
# B9.5: bootstrap salvaje autorregresivo del propio estadistico
# ---------------------------------------------------------------------------
def awb_gamma(n):
    """Parametro por defecto de bootUR 1.0.5 (check_inputs): l = round(1.75 T^{1/3}), gamma = 0.01^{1/l}, T = n + 1."""
    l = int(round(1.75 * (n + 1) ** (1.0 / 3.0)))
    return 0.01 ** (1.0 / l), l


def awb_pvalue(y, n, theta, case, B, rng):
    """
    p-valor AWB del estadistico RM-GLS (theta, caso), cola inferior.

    Residuos bajo la nula con intercepto y retardo 0 (como boot_adf con min_lag =
    max_lag = 0 en A6-A8): u_t = dY_t - media(dY). Remuestra:
    xi_1 = nu_1, xi_t = gamma xi_{t-1} + sqrt(1 - gamma^2) nu_t, nu iid N(0, 1);
    dY*_t = xi_t u_t; Y*_0 = 0, Y* = cumsum(dY*). El estadistico se recalcula por
    completo en cada remuestra (sigma_hat HAC y anclaje GLS incluidos).
    """
    from scipy.signal import lfilter
    y = np.asarray(y, dtype=np.float64)
    s_obs = rmgls(y, n, theta, hac_sigma_sq(y), case)
    dy = np.diff(y)
    u = dy - dy.mean()
    g, _ = awb_gamma(n)
    b = math.sqrt(1.0 - g * g)
    nu = rng.standard_normal((B, n))
    xi = np.empty_like(nu)
    xi[:, 0] = nu[:, 0]
    xi[:, 1:] = lfilter([b], [1.0, -g], nu[:, 1:], axis=1, zi=(g * nu[:, :1]))[0]
    stars = np.empty(B)
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for j in range(B):
        np.cumsum(xi[j] * u, out=Y[1:])
        stars[j] = rmgls(Y, n, theta, hac_sigma_sq(Y), case)
    return float(np.mean(stars <= s_obs)), s_obs
