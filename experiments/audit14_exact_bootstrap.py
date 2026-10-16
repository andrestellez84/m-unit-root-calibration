"""
Auditoria A14 - EE bootstrap exacto (B -> infinito) de un cuantil muestral con interpolacion
lineal (protocol_audit14.md, lectura 5). Sin numeros aleatorios.

Con x_(1) <= ... <= x_(N), h = (N - 1) alpha, r = floor(h) + 1 y g = h - floor(h), el
cuantil de numpy.quantile (metodo 'linear') es Q = (1 - g) x_(r) + g x_(r+1). Con C_k el
numero de extracciones bootstrap de indice <= k, C_k ~ Bin(N, k/N):
  P(X*_(r) <= x_(k)) = P(C_k >= r);
  P(X*_(r) = x_(a), X*_(r+1) = x_(b)), a < b,
      = P(C_a = r) (1 - (1 - 1/a)^r) [((N-b+1)/(N-a))^(N-r) - ((N-b)/(N-a))^(N-r)];
  E*[X*_(r) X*_(r+1)] = (E*[X*_(r)^2] + E*[X*_(r+1)^2] - E*[(X*_(r+1) - X*_(r))^2]) / 2.
Los valores se centran en un punto de referencia antes de sumar.
"""
import math

import numpy as np
from scipy import stats

TAIL = 10 ** -15               # masa omitida admitida en cada truncamiento


def _window(N, r):
    """Atomos 1..N donde la marginal de X*_(r) tiene masa apreciable."""
    half = int(math.ceil(40 * math.sqrt(r + 1))) + 50
    return max(1, r - half), min(N, r + 1 + half)


def order_stat_marginal(N, r, lo, hi):
    """Pesos w_k = P(X*_(r) = x_(k)) para k = lo..hi y masa total de la ventana."""
    k = np.arange(lo - 1, hi + 1, dtype=np.float64)
    F = stats.binom.sf(r - 1, N, k / N)          # P(C_k >= r)
    w = np.diff(F)
    return w, float(F[-1] - F[0])


def gap_second_moment(xs, N, r, lo, hi, k_max=None):
    """E*[(X*_(r+1) - X*_(r))^2] y la masa omitida por truncar b - a."""
    a = np.arange(lo, hi + 1, dtype=np.float64)
    pa = stats.binom.pmf(r, N, a / N) * (1.0 - np.power(1.0 - 1.0 / a, r))
    K = k_max if k_max is not None else N
    total, resid = 0.0, 0.0
    for i, ai in enumerate(range(lo, hi + 1)):
        if pa[i] == 0.0:
            continue
        b = np.arange(ai + 1, min(N, ai + K) + 1, dtype=np.float64)
        if b.size == 0:
            continue
        base = N - ai
        upper = np.exp((N - r) * np.log1p(-(b - 1 - ai) / base))
        lower = np.exp((N - r) * np.log1p(-(b - ai) / base)) if b[-1] < N else None
        if lower is None:
            lower = np.exp((N - r) * np.log1p(-(b[:-1] - ai) / base))
            lower = np.append(lower, 0.0)
        prob = upper - lower
        d = xs[b.astype(np.int64) - 1] - xs[ai - 1]
        total += pa[i] * float(np.sum(prob * d * d))
        resid = max(resid, float(lower[-1]))
    return total, resid


def exact_bootstrap(x, alpha, k_max=64):
    """
    EE bootstrap exacto del cuantil lineal de x al nivel alpha y EE de Maritz-Jarrett.
    Devuelve un dict con el cuantil (numpy.quantile), el EE, el sesgo bootstrap y los
    controles de truncamiento.
    """
    xs = np.sort(np.asarray(x, dtype=np.float64))
    N = xs.size
    q = float(np.quantile(xs, alpha))
    h = (N - 1) * alpha
    j = int(math.floor(h))
    g = h - j
    r = j + 1
    c = xs - q
    lo, hi = _window(N, r + 1)
    lo = max(1, min(lo, _window(N, r)[0]))
    wr, mr = order_stat_marginal(N, r, lo, hi)
    ws, ms = order_stat_marginal(N, r + 1, lo, hi) if r + 1 <= N else (np.zeros(hi - lo + 1), 1.0)
    cw = c[lo - 1:hi]
    m1r, m2r = float(np.sum(wr * cw)), float(np.sum(wr * cw * cw))
    m1s, m2s = float(np.sum(ws * cw)), float(np.sum(ws * cw * cw))
    D, resid = gap_second_moment(c, N, r, lo, hi, k_max if N > 2 * k_max else None)
    cross = 0.5 * (m2r + m2s - D)
    mean = (1 - g) * m1r + g * m1s
    second = (1 - g) ** 2 * m2r + g ** 2 * m2s + 2 * g * (1 - g) * cross
    var = second - mean * mean
    m = int(math.floor(N * alpha + 0.5))
    m = min(max(m, 1), N)
    lo_m, hi_m = _window(N, m)
    wm, mm = order_stat_marginal(N, m, lo_m, hi_m)
    cm = c[lo_m - 1:hi_m]
    var_mj = float(np.sum(wm * cm * cm)) - float(np.sum(wm * cm)) ** 2
    return {"quantile": q, "N": int(N), "alpha": alpha, "r": r, "g": g,
            "se": math.sqrt(max(var, 0.0)), "bootstrap_mean_minus_estimate": mean,
            "se_maritz_jarrett": math.sqrt(max(var_mj, 0.0)), "mj_index": m,
            "window": [lo, hi], "mass_r": mr, "mass_r1": ms, "mass_mj": mm,
            "gap_truncation_residual": resid,
            "truncation_ok": abs(1 - mr) <= 10 ** -12 and abs(1 - ms) <= 10 ** -12 and abs(1 - mm) <= 10 ** -12 and resid <= TAIL}
