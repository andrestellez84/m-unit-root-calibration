"""
Auditoria A10 - B10.5: constantes de maquetacion de las figuras (no son resultados).

Reutiliza las de A9 (audit9_figconfig) y anade las de la figura nueva.
"""
from audit9_figconfig import *                                     # noqa: F401,F403
from audit9_figconfig import STYLE as _STYLE9

GAIN_N = (60, 100, 150, 200, 500, 1000, 2000, 5000)
GAIN_YMIN = 0.0
GAIN_YMAX = 0.1

STYLE = dict(_STYLE9)
STYLE.update({
    "cv_at_n": ("0.0", "o", "-"),
    "cv_big": ("0.4", "s", "--"),
    "msb_pub": ("0.6", "^", ":"),
    "region": ("0.75", "", "-"),
})
GAIN_TICK_ROTATION = 45
