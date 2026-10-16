"""
Auditoria A9 - diseno: familias de semillas, celdas y trayectorias.

Familias nuevas (una por bloque): 100 B9.0 (sin celdas), 101 B9.1 (sin celdas:
reutiliza las trayectorias de B5 de A8 y calibra sobre los caminos de
produccion), 102 B9.2, 103 B9.3 (sin celdas: mismas trayectorias que B9.1/B9.2),
104 B9.4, 105 B9.5, 106 B9.6, 107 B9.7; 108-109 reservadas para enmiendas.
Cada lista de celdas es ORDENADA: el indice es el primer elemento del
spawn_key; solo se amplian al final.

Trayectorias reutilizadas de A8 (Paso 0 frente a sus checkpoints):
  - B5 (familia 95): DGP 1, DGP 2, tamano de ZA, DGP 3, potencia con tendencia
    (audit8_b5_power.path).
  - B2 (celdas de mala especificacion): colas pesadas publicadas y GARCH de A7
    (audit8_design.size_path).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit9_common as C                                          # noqa: E402
import audit8_design as D8                                         # noqa: E402

N_INDEP = 20000
N_SIM = 5000
N_LP = 2000
N_POWER = 20000
N_TEST0 = 5000
N_BIG = 20000
N_BIG_N = 20000
N_AWB = 2000
B_AWB = 399
N_CV = 100000
N_OOS = 5000
N_APP_MAX = 11000                  # cota de ventanas por (indice, D) para el mapa de semillas
N_ALL = (60, 100, 150, 200, 500, 1000, 2000, 5000)
N3 = (200, 500, 1000)
B7_N = (100, 200, 500, 1000, 2000, 5000)
B6_D = (150, 200, 250, 300)
C_GRID = tuple(float(c) for c in range(0, 31)) + (13.5,)
LP_CASES = ("dm", "ct")
CASE_DET = {"dm": "c", "ct": "ct"}


def cname(c):
    return ("%d" % c) if float(c).is_integer() else ("%g" % c)


# B9.5: celdas del encargo y su fuente de trayectorias
AWB_CELLS = (tuple(("dgp3_r%s_n%d" % (r, n), "b5") for r in ("1", "2", "4") for n in (200, 500))
             + tuple(("garch_%s_n200" % k, "b2") for k in ("base", "p099", "p098", "p095_t5"))
             + tuple(("dgp1_rho%s_n%d" % (r, n), "b5") for r in ("0p95", "0p99") for n in (200, 500))
             + tuple(("indep_n%d" % n, "indep") for n in (200, 500)))

CELLS = {
    100: (),
    101: (),
    102: tuple(["lp_%s_c%s" % (case, cname(c)) for case in LP_CASES for c in C_GRID]
               + ["lp_%s_test0" % case for case in LP_CASES]
               + ["indep_n%d" % n for n in N_ALL]),
    103: (),
    104: ("big_n%d" % N_BIG_N,),
    105: tuple("awb_%s" % c for c, _ in AWB_CELLS),
    106: (tuple("oos_D%d" % d for d in B6_D)
          # anadidas al final tras la recomendacion de B9.5: remuestreo AWB de la aplicacion
          + tuple("awbapp_%s_D%d" % (i, d) for i in ("SP500", "FTSE", "NIKKEI", "DAX") for d in B6_D)
          + tuple("awboos_D%d" % d for d in B6_D)),
    107: tuple(["cv_%s_n%d" % (case, n) for case in LP_CASES for n in B7_N]
               + ["cvx_%s_n%d" % (case, n) for case in LP_CASES for n in B7_N]),
}


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 102:
        if name.startswith("indep"):
            return N_INDEP
        return N_TEST0 if name.endswith("test0") else N_POWER
    if family == 104:
        return N_BIG
    if family == 105:
        return N_AWB
    if family == 106:
        return N_APP_MAX if name.startswith("awbapp") else N_OOS
    if family == 107:
        return N_CV
    return 0


# ---------------------------------------------------------------------------
# Trayectorias
# ---------------------------------------------------------------------------
def indep_path(n, i):
    return D8.gauss_rw(n, C.rep_rng(102, cell_index(102, "indep_n%d" % n), i))


def lp_path(case, c, i):
    from power_comparison import generate_ar1
    return generate_ar1(n=N_LP, rho=1.0 - c / N_LP, rng=C.rep_rng(102, cell_index(102, "lp_%s_c%s" % (case, cname(c))), i))


def test0_path(case, i):
    from power_comparison import generate_ar1
    return generate_ar1(n=N_LP, rho=1.0, rng=C.rep_rng(102, cell_index(102, "lp_%s_test0" % case), i))


def big_path(i):
    return D8.gauss_rw(N_BIG_N, C.rep_rng(104, 0, i))


def cv_path(case, n, i, cross=False):
    name = "%s_%s_n%d" % ("cvx" if cross else "cv", case, n)
    return D8.gauss_rw(n, C.rep_rng(107, cell_index(107, name), i))


_B5 = None


def b5():
    global _B5
    if _B5 is None:
        import audit8_b5_power as B5
        _B5 = (B5, B5.cells())
    return _B5


def b5_path(name, i):
    B5, cells = b5()
    return B5.path(name, cells[name], i)


def b5_spec(name):
    return b5()[1][name]


def misspec_cells():
    """Las 22 celdas de mala especificacion de A8 (6 de colas pesadas, 16 GARCH), en el orden de A8."""
    return {k: s for k, s in D8.size_cells().items() if s["kind"] in ("heavy", "garch")}


def misspec_path(name, i):
    return D8.size_path(name, D8.size_cells()[name], i)


def awb_source_path(cell, src, i):
    if src == "b5":
        return b5_path(cell, i)
    if src == "b2":
        return misspec_path(cell, i)
    return indep_path(int(cell.split("_n")[1]), i)


def awb_rng(cell, i):
    return C.rep_rng(105, cell_index(105, "awb_" + cell), i)
