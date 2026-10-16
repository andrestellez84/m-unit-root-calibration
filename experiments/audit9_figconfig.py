"""
Auditoria A9 - B9.7 (2): constantes de maquetacion de las figuras (no son resultados).

Reutiliza las de A8 (audit8_figconfig) y anade las propias de A9.
"""
from audit8_figconfig import *                                     # noqa: F401,F403
from audit8_figconfig import STYLE as _STYLE8

HEIGHT_EQUALIZED = 12.5 * (1 / 2.54)
BOTTOM_MARGIN_EQUALIZED = 0.14
Z95 = 1.96
PP = 100
LADDER_C = (5.0, 10.0, 15.0)
SIZE_N = (200, 500, 1000, 2000, 5000)
DGP3_N = (200, 500, 1000)
EQ_N = (200, 500, 1000)

STYLE = dict(_STYLE8)
STYLE.update({
    "theta0": ("0.5", "o", ":"),
    "msb_sim": ("0.45", "^", "-."),
    "pp_sim": ("0.6", "+", ":"),
    "primary_awb": ("0.2", "*", (0, (3, 1, 1, 1))),
    "awb_dfgls": ("0.65", "P", (0, (5, 1))),
    "c5": ("0.0", "o", "-"),
    "c10": ("0.35", "s", "--"),
    "c15": ("0.6", "^", ":"),
})
