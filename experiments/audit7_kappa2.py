"""
Auditoria A7 - contraste kappa_2 de Sanso, Arago y Carrion-i-Silvestre (2004)
de un cambio en la varianza incondicional, robusto a curtosis y a correlacion
serial en los cuadrados.

Sobre una serie de residuos e_t, t = 1..T:

    C_k     = sum_{t<=k} e_t^2
    G_k     = omega4_hat^{-1/2} * (C_k - (k/T) C_T)
    kappa_2 = max_k | T^{-1/2} G_k |

omega4_hat es el estimador HAC con kernel de Bartlett de la varianza de largo
plazo de u_t = e_t^2 - mean(e^2), con ancho de banda floor(4 (T/100)^{2/9})
(regla deterministica de Newey y West, 1994). La ley limite es el supremo del
valor absoluto del puente browniano estandar.

Los residuos son los de MCO de la regresion ADF con intercepto y orden de
rezagos seleccionado por AIC: la serie que un practicante tiene a mano sin
saber de antemano si el proceso es estacionario.
"""
import numpy as np
from statsmodels.tsa.stattools import adfuller

# Cuantiles de sup|B(u)|, B puente browniano estandar (distribucion de
# Kolmogorov): nivel -> valor critico.
KAPPA2_CRITICAL = {0.10: 1.224, 0.05: 1.358, 0.01: 1.628}


def adf_residuals(y, regression="c", autolag="AIC"):
    """Residuos MCO y orden de rezagos de la regresion ADF seleccionada."""
    out = adfuller(np.asarray(y, dtype=float), regression=regression,
                   autolag=autolag, regresults=True)
    store = out[-1]
    return np.asarray(store.resols.resid, dtype=float), int(store.usedlag)


def newey_west_bandwidth(T):
    return int(np.floor(4.0 * (T / 100.0) ** (2.0 / 9.0)))


def bartlett_long_run_variance(u, L):
    """Varianza de largo plazo de u (media cero) con kernel de Bartlett."""
    u = np.asarray(u, dtype=float)
    T = u.size
    lrv = float(u @ u) / T
    for j in range(1, L + 1):
        lrv += 2.0 * (1.0 - j / (L + 1.0)) * float(u[j:] @ u[:-j]) / T
    return lrv


def kappa2_statistic(e):
    """kappa_2 sobre la serie de residuos e. NaN si omega4_hat no es positivo."""
    e = np.asarray(e, dtype=float)
    T = e.size
    if T < 20:
        raise ValueError("kappa_2 necesita al menos 20 residuos, recibio %d" % T)
    e2 = e * e
    C = np.cumsum(e2)
    k = np.arange(1, T + 1, dtype=float)
    D = C - (k / T) * C[-1]
    u = e2 - e2.mean()
    omega4 = bartlett_long_run_variance(u, newey_west_bandwidth(T))
    if not np.isfinite(omega4) or omega4 <= 0.0:
        return float("nan")
    return float(np.max(np.abs(D)) / np.sqrt(omega4 * T))


def kappa2_on_adf_residuals(y):
    """(kappa_2, orden de rezagos ADF, numero de residuos) para la serie y."""
    e, lag = adf_residuals(y)
    return kappa2_statistic(e), lag, int(e.size)
