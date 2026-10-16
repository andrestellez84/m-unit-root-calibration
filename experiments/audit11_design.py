"""
Auditoria A11 - diseno: familias de semillas, celdas y trayectorias.

Familias: 120 T0 (sin celdas), 121 T1, 122 T2 y 125 T5 (sin celdas: solo leen
JSON), 123 T3, 124 T4; 126-129 reservadas para enmiendas. Cada lista de celdas es
ORDENADA: el indice es el primer elemento del spawn_key; solo se amplia al final.
Trayectorias y bootstrap usan celdas (hijos) distintas.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402

T3_N = (200, 500, 1000, 2000, 5000, 20000)
T3_THETAS = (0.0, 0.02, 0.1)
N_T3 = 40000
T4_RHO = (0.5, 0.9)
T4_N = (200, 500, 1000, 2000, 5000)
N_T4 = 2000
T4_BOOT = 2000
T4_INTERCEPT = 1.0
T4_SLOPE = 0.1
T4_THETA = 0.02


def rho_tag(rho):
    return ("%g" % rho).replace(".", "p")


CELLS = {
    120: (),
    121: (),
    122: (),
    123: tuple("t3_n%d" % n for n in T3_N),
    124: (tuple("t4_rho%s_n%d" % (rho_tag(r), n) for r in T4_RHO for n in T4_N)
          + tuple("t4boot_rho%s" % rho_tag(r) for r in T4_RHO)),
    125: (),
}


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 123:
        return N_T3
    if family == 124:
        return 1 if name.startswith("t4boot") else N_T4
    return 0


def t3_path(n, i):
    """Paseo aleatorio gaussiano de A8 (Y_0 = 0, Y = cumsum eps, n + 1 puntos)."""
    return D8.gauss_rw(n, C.rep_rng(123, cell_index(123, "t3_n%d" % n), i))


def t4_path(rho, n, i):
    """Y_t = 1 + 0.1 t + x_t, t = 0..n; x_0 ~ N(0, 1/(1 - rho^2)), x_t = rho x_{t-1} + eps_t."""
    rng = C.rep_rng(124, cell_index(124, "t4_rho%s_n%d" % (rho_tag(rho), n)), i)
    z = rng.standard_normal(n + 1)
    x = np.empty(n + 1)
    x[0] = z[0] / np.sqrt(1.0 - rho * rho)
    for t in range(1, n + 1):
        x[t] = rho * x[t - 1] + z[t]
    return T4_INTERCEPT + T4_SLOPE * np.arange(n + 1, dtype=np.float64) + x


def t4_boot_rng(rho):
    return C.rep_rng(124, cell_index(124, "t4boot_rho%s" % rho_tag(rho)), 0)
