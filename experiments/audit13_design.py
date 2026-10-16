"""
Auditoria A13 - diseno: familias de semillas, celdas y trayectorias.

Familias (protocol_audit13.md, lectura 1): 140 B13.E (sin celdas), 141 tab:size en
n in {60, 100, 150}, 142 remuestreo AWB sobre las trayectorias de B9.5, 143
aplicacion (AWB por ventana y AWB fuera de muestra); 144-149 enmiendas. Cada
lista de celdas es ORDENADA (el indice es el primer elemento del spawn_key) y
solo se amplia al final. Los casos van en celdas distintas.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit10_design as D10                                       # noqa: E402

CASES = ("dm", "ct")
CASE_DET = {"dm": "c", "ct": "ct"}
LOW_N = (60, 100, 150)
N_LOW = 50000
INDICES = ("SP500", "FTSE", "NIKKEI", "DAX")
B6_D = D10.B6_D
N_AWB = D9.N_AWB
N_OOS = D10.N_OOS
N_APP_MAX = D10.N_APP_MAX
PASO0 = 50

CELLS = {
    140: (),
    141: tuple("size_%s_n%d" % (case, n) for case in CASES for n in LOW_N),
    142: tuple("awb_%s" % c for c, _ in D9.AWB_CELLS),
    143: (tuple("awbapp_%s_D%d" % (i, d) for i in INDICES for d in B6_D)
          + tuple("awboos_D%d" % d for d in B6_D)),
    144: (), 145: (), 146: (), 147: (), 148: (), 149: (),
}


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 141:
        return N_LOW
    if family == 142:
        return N_AWB
    if family == 143:
        return N_APP_MAX if name.startswith("awbapp") else N_OOS
    return 0


def size_path(case, n, i):
    return D8.gauss_rw(n, C.rep_rng(141, cell_index(141, "size_%s_n%d" % (case, n)), i))


def awb_rng(cell, i):
    return C.rep_rng(142, cell_index(142, "awb_" + cell), i)
