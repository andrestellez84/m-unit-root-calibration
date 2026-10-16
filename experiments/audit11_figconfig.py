"""
Auditoria A11 - T1: constantes de maquetacion y textos de las figuras en ingles (no son resultados).

Reutiliza las de A10 (audit10_figconfig: tamanos, estilos, GAIN_N) sin cambiarlas.
"""
from audit10_figconfig import *                                    # noqa: F401,F403

CASE_TITLE_EN = {"dm": "Constant", "ct": "Trend", "c": "Constant"}
GARCH_PANELS_EN = (("p099", "Persistence 0.99, normal"), ("p095_t5", "Persistence 0.95, t(5)"))
EQ_ROWS_EN = (("dgp1_", "Constant"), ("ct_power_", "Trend"))
PRIMARY_LABEL = "RM-GLS"
GAIN_HIDDEN_TICK_LABELS = (150,)
LADDER_TICK_FORMAT = "%.2f"
LADDER_TICK_ALIGN = {0: "right"}                # indice de la marca -> alineacion: 0.00 a la derecha de su marca
GAIN_LEGEND_NCOL = 2
GAIN_LEGEND_BOTTOM = -0.1
