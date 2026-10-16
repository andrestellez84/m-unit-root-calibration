"""
Auditoria A10 - diseno: familias de semillas, celdas y trayectorias.

Familias (una por bloque): 110 B10.0 (sin celdas), 111 B10.1, 112 B10.2,
113 B10.3 (condicional: solo se usa si el theta de B10.1 != 0.1), 114 B10.4,
115 B10.5 (sin celdas); 116-119 reservadas para enmiendas. Cada lista de celdas
es ORDENADA: el indice es el primer elemento del spawn_key; solo se amplian al
final. Casos deterministas y muestras usan celdas (hijos) distintas.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit8_design as D8                                         # noqa: E402

CASES = ("dm", "ct")
CASE_DET = {"dm": "c", "ct": "ct"}
A1_N = (200, 500, 1000)
A1_SAMPLES = (1, 2)
N_A1 = 50000
N_CAL = 500000
N_ID = 1000
ID_N = (200, 1000)
LOW_N = (60, 100, 150)
N_LOW = 50000
N_CV = 100000
CV_N = 5000
CV_REPLICAS = (1, 2, 3, 4, 5)
B7_N = (100, 200, 500, 1000, 2000, 5000)
B6_D = (150, 200, 250, 300)
N_AWB = 2000
N_OOS = 5000
N_APP_MAX = 11000
AWB_SOURCE = ("dgp3_r1_n200", "dgp3_r1_n500", "dgp3_r2_n200", "dgp3_r2_n500", "dgp3_r4_n200", "dgp3_r4_n500",
              "garch_base_n200", "garch_p099_n200", "garch_p098_n200", "garch_p095_t5_n200",
              "dgp1_rho0p95_n200", "dgp1_rho0p95_n500", "dgp1_rho0p99_n200", "dgp1_rho0p99_n500",
              "indep_n200", "indep_n500")

CELLS = {
    110: (),
    111: tuple("a1_%s_n%d_s%d" % (case, n, k) for case in CASES for n in A1_N for k in A1_SAMPLES),
    112: tuple("id_%s_n%d" % (case, n) for case in CASES for n in ID_N),
    113: (tuple("awb_%s" % c for c in AWB_SOURCE)
          + tuple("awbapp_%s_D%d" % (i, d) for i in ("SP500", "FTSE", "NIKKEI", "DAX") for d in B6_D)
          + tuple("awboos_D%d" % d for d in B6_D)
          + tuple("low_%s_n%d" % (case, n) for case in CASES for n in LOW_N)
          + tuple("cvx_%s_n%d" % (case, n) for case in CASES for n in B7_N)),
    114: tuple("cv5000_r%d" % k for k in CV_REPLICAS),
    115: (),
}


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 111:
        return N_A1
    if family == 112:
        return N_ID
    if family == 113:
        if name.startswith("awbapp"):
            return N_APP_MAX
        if name.startswith("awboos"):
            return N_OOS
        if name.startswith("awb_"):
            return N_AWB
        if name.startswith("low_"):
            return N_LOW
        return N_CV
    if family == 114:
        return N_CV
    return 0


# ---------------------------------------------------------------------------
# Trayectorias (paseo aleatorio gaussiano de A8: Y_0 = 0, Y = cumsum eps)
# ---------------------------------------------------------------------------
def a1_path(case, n, k, i):
    return D8.gauss_rw(n, C.rep_rng(111, cell_index(111, "a1_%s_n%d_s%d" % (case, n, k)), i))


def id_path(case, n, i):
    return D8.gauss_rw(n, C.rep_rng(112, cell_index(112, "id_%s_n%d" % (case, n)), i))


def low_path(case, n, i):
    return D8.gauss_rw(n, C.rep_rng(113, cell_index(113, "low_%s_n%d" % (case, n)), i))


def cvx_path(case, n, i):
    return D8.gauss_rw(n, C.rep_rng(113, cell_index(113, "cvx_%s_n%d" % (case, n)), i))


def cv5000_path(k, i):
    return D8.gauss_rw(CV_N, C.rep_rng(114, cell_index(114, "cv5000_r%d" % k), i))


def awb_rng(cell, i):
    return C.rep_rng(113, cell_index(113, "awb_" + cell), i)
