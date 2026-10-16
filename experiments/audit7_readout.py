"""
Auditoria A7 - reglas de lectura del Bloque 1, registradas antes de computar DGP 5.

Fuente unica de las reglas que usan la enmienda, la medicion del handicap de
kappa_2, el runner de DGP 5 y el generador del reporte. Si una regla cambia
despues de ver datos, cambia este archivo y el cambio queda en git.

1. Quien gana en una celda: contraste pareado sobre las MISMAS series, con los
   rechazos a tamano igualado. McNemar exacto sobre los pares discordantes;
   si p < WIN_ALPHA gana el de mas rechazos, si no es "empate".
2. Las dos versiones del test propuesto (R = 0.50 y R adaptativo) se evaluan
   por separado contra cada comparador.
3. Cuota de energia de g2 en el estadistico: R^2 g2^2 / stat^2, por serie; en
   cada celda se resume por la mediana sobre las series.
4. Desdoblamiento de la prediccion 1 segun esa cuota (en las celdas donde la
   version ganadora gana):
     mediana <  SHARE_LOW  -> gana la agregacion cuadratica de un canal de media
                              dominante frente a una union, no el segundo canal
     mediana >= SHARE_HIGH -> evidencia de la arquitectura dual
     en medio              -> indeterminado, se reporta como tal
5. Handicap de kappa_2 por persistencia: McNemar exacto p < HANDICAP_ALPHA con la
   potencia bajo paseo aleatorio con quiebre POR ENCIMA de la del AR con el mismo
   quiebre, y deficit relativo >= HANDICAP_REL_SHORTFALL_MIN. Declarado para un n
   si ocurre en al menos una celda del interior de la prediccion 1.
"""
import os
import sys

import numpy as np
from scipy.stats import binomtest

# El modulo debe poder importarse solo: antes dependia de que otro import previo
# hubiera anadido src/ al path.
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from stationarity_test.optimal_weight import compute_optimal_R  # noqa: E402

ALPHA = 0.05
WIN_ALPHA = 0.05

SHARE_LOW = 0.01
SHARE_HIGH = 0.10

HANDICAP_ALPHA = 0.05
HANDICAP_REL_SHORTFALL_MIN = 0.10

# Regiones de la prediccion registrada (commit 62216ee)
INTERIOR_P1 = frozenset({(0.93, 2.0), (0.93, 3.0), (0.95, 2.0), (0.95, 3.0)})
EXTREME_MEAN_P2_R = 1.0
EXTREME_VARIANCE_P3 = (0.95, 4.0)

# Segunda enmienda: extension de quiebres debiles con la persistencia del
# interior registrado. Es un contraste POST-REGISTRO con veredicto propio: la
# condicion de falsacion registrada se evalua literalmente sobre INTERIOR_P1 y
# gobierna la consecuencia; la extension no la anula.
EXTENSION_P1 = frozenset({(rho, r) for rho in (0.93, 0.95) for r in (1.1, 1.25, 1.5)})


def adaptive_R(g1_std, g2_std):
    """R adaptativo de la implementacion del paquete (identico al usado en A5)."""
    return compute_optimal_R(g1_std, g2_std, method="adaptive")["R_star"]


def statistic(g1_std, g2_std, R):
    return float(np.sqrt((1.0 - R) ** 2 * g1_std ** 2 + R ** 2 * g2_std ** 2))


def g2_energy_share(g1_std, g2_std, R):
    """R^2 g2^2 / ((1-R)^2 g1^2 + R^2 g2^2). NaN si el estadistico es nulo."""
    num = R ** 2 * g2_std ** 2
    den = (1.0 - R) ** 2 * g1_std ** 2 + num
    return float(num / den) if den > 0 else float("nan")


def share_band(median_share):
    if not np.isfinite(median_share):
        return "indeterminado"
    if median_share < SHARE_LOW:
        return "agregacion_de_canal_de_media"
    if median_share >= SHARE_HIGH:
        return "arquitectura_dual"
    return "indeterminado"


def paired_winner(rej_a, rej_b, alpha=WIN_ALPHA):
    """McNemar exacto sobre rechazos pareados. Devuelve ('A'|'B'|'empate', p, b, c)."""
    a = np.asarray(rej_a, dtype=bool)
    b_ = np.asarray(rej_b, dtype=bool)
    if a.shape != b_.shape:
        raise ValueError("rechazos no pareados: %s vs %s" % (a.shape, b_.shape))
    b = int((a & ~b_).sum())
    c = int((~a & b_).sum())
    p = float(binomtest(min(b, c), b + c, 0.5).pvalue) if (b + c) > 0 else 1.0
    if p < alpha:
        return ("A" if b > c else "B"), p, b, c
    return "empate", p, b, c
