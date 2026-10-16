"""
Auditoria A12 - diseno: familias de semillas, celdas y trayectorias.

Familias (protocolo_audit12, lectura 1): 130 B12.A, 131 B12.B (sin trayectorias nuevas:
usa las de B5 de A8, familia 95), 132 B12.C, 133 B12.D y 134 B12.E (reservadas, sin
uso), 135 B12.F (calculo exacto, sin trayectorias), 136 calibraciones nuevas, 137
sondas; 138-139 enmiendas. Cada lista de celdas es ORDENADA (el indice es el primer
elemento del spawn_key) y solo se amplia al final.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
import audit12_unitroot as P                                       # noqa: E402
import audit8_design as D8                                         # noqa: E402

CASES = ("c", "ct")
A_N = (100, 200, 500)
N_SIZE = 20000
N_POW = 5000
CBAR_POW = {"c": -7.0, "ct": -13.5}
POW_RHO_EXTRA = (0.90, 0.95)
POW_EXTRA_N = 200
CAL_N = (100, 200, 500, 1000, 2000)
N_CAL = 500000
PROBE_N = 500
PROBE_CASE = "ct"
PROBE_ERR = ("ma", -0.8)
PROBE_PATHS = 14 * 50
C_N = 200
C_RHO = (0.90, 0.95, 0.97)
C_ALPHA = (0.0, 1.0, 2.0, 4.0)
N_C = 5000


def rtag(x):
    return ("%g" % x).replace("-", "m").replace(".", "p")


def size_cell(err, n, case):
    return "sz_%s_n%d_%s" % (P.err_tag(err), n, case)


def pow_cell(err, n, case):
    return "pw_%s_n%d_%s" % (P.err_tag(err), n, case)


def pow_extra_cell(err, rho):
    return "pwr_%s_rho%s_n%d_c" % (P.err_tag(err), rtag(rho), POW_EXTRA_N)


CELLS = {
    130: (tuple(size_cell(e, n, c) for e in P.ERRORS for n in A_N for c in CASES)
          + tuple(pow_cell(e, n, c) for e in P.ERRORS for n in A_N for c in CASES)
          + tuple(pow_extra_cell(e, r) for e in P.ERRORS for r in POW_RHO_EXTRA)),
    131: (),
    132: tuple("c_rho%s" % rtag(r) for r in C_RHO) + tuple("c_u0_rho%s" % rtag(r) for r in C_RHO),
    133: (),
    134: (),
    135: (),
    136: tuple("cal_n%d" % n for n in CAL_N),
    137: ("probe_%s_n%d_%s" % (P.err_tag(PROBE_ERR), PROBE_N, PROBE_CASE),),
}


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 130:
        return N_SIZE if name.startswith("sz_") else N_POW
    if family == 132:
        return N_C
    if family == 136:
        return N_CAL
    if family == 137:
        return PROBE_PATHS
    return 0


def pow_rho(n, case):
    return 1.0 + CBAR_POW[case] / n


# ---------------------------------------------------------------------------
# Especificacion de las celdas de B12.A
# ---------------------------------------------------------------------------
def a_cells():
    """nombre -> dict(kind, err, n, case, rho, reps, size_cell)."""
    out = {}
    for e in P.ERRORS:
        for n in A_N:
            for c in CASES:
                out[size_cell(e, n, c)] = {"kind": "size", "err": e, "n": n, "case": c, "rho": 1.0, "reps": N_SIZE,
                                           "size_cell": size_cell(e, n, c)}
                out[pow_cell(e, n, c)] = {"kind": "power", "err": e, "n": n, "case": c, "rho": pow_rho(n, c),
                                          "reps": N_POW, "size_cell": size_cell(e, n, c)}
        for r in POW_RHO_EXTRA:
            out[pow_extra_cell(e, r)] = {"kind": "power", "err": e, "n": POW_EXTRA_N, "case": "c", "rho": r,
                                         "reps": N_POW, "size_cell": size_cell(e, POW_EXTRA_N, "c")}
    return out


def a_path(name, spec, i):
    rng = C.rep_rng(130, cell_index(130, name), i)
    if spec["kind"] == "size":
        return P.null_path(spec["err"], spec["n"], rng)
    return P.alt_path(spec["err"], spec["n"], spec["rho"], rng)


def probe_path(i):
    rng = C.rep_rng(137, 0, i)
    return P.null_path(PROBE_ERR, PROBE_N, rng)


def cal_path(n, i):
    return D8.gauss_rw(n, C.rep_rng(136, cell_index(136, "cal_n%d" % n), i))


def c_innov_rng(rho, i):
    return C.rep_rng(132, cell_index(132, "c_rho%s" % rtag(rho)), i)


def c_u0_rng(rho, i):
    return C.rep_rng(132, cell_index(132, "c_u0_rho%s" % rtag(rho)), i)
