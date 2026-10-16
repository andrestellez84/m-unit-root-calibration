"""
Auditoria A8 - B8: constantes de maquetacion de las figuras (no son resultados).

make_figures_audit8.py no contiene literales de punto flotante fuera de la lista
blanca del test de literales; las medidas y estilos viven aqui.
"""
CM = 1 / 2.54
WIDTH_DOUBLE = 19.0 * CM
HEIGHT_TWO_PANEL = 7.5 * CM
HEIGHT_THREE_PANEL = 6.8 * CM
HEIGHT_DGP5 = 12.0 * CM
FONT_SIZE = 8.5
LEGEND_SIZE = 8.0
LINE_WIDTH = 1.2
MARKER_SIZE = 4.0
BAND_ALPHA = 0.18
SHADE_ALPHA = 0.15
GRID_ALPHA = 0.3
NOMINAL_LINE = 0.05
SHARE_LINE = 0.025
DGP1_N1000_RHO_MIN = 0.93
DGP1_RHO_MAX = 1.0
POWER_YMAX = 1.02
POWER_YMIN = -0.02
SUBPLOT_HSPACE = 0.45
SUBPLOT_WSPACE = 0.28
LEGEND_BOTTOM = -0.02
BOTTOM_MARGIN = 0.26
BOTTOM_MARGIN_DGP5 = 0.16
REGISTERED_INTERIOR = (2.0, 3.0)
LOG2_BASE = 2

# (color en escala de grises, marcador, estilo de linea) por curva
STYLE = {
    "envelope": ("0.0", "", "-"),
    "primary": ("0.0", "o", "-"),
    "rm": ("0.35", "D", "--"),
    "dfgls": ("0.25", "s", "--"),
    "msb": ("0.45", "^", "-."),
    "mzt": ("0.55", "v", ":"),
    "adf": ("0.3", "x", "-."),
    "pp": ("0.6", "+", ":"),
    "adf_sim": ("0.3", "x", "-."),
    "dfgls_sim": ("0.25", "s", "--"),
    "mzt_sim": ("0.55", "v", ":"),
    "msbhac": ("0.45", "^", "-."),
    "awb": ("0.65", "P", (0, (5, 1))),
    "r05": ("0.3", "s", "--"),
    "rhat": ("0.5", "^", ":"),
    "union": ("0.6", "D", "-."),
    "bootstrap": ("0.4", "P", (0, (5, 1))),
}
