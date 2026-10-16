"""
Auditoria A15 - diseno: familias, celdas (lista ORDENADA; el indice es el primer elemento del
spawn_key) y replicas (protocol_audit15.md, lecturas G1, 1.1, 1.9, 3.3-3.6; enmienda 2, seccion 3).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_design as D12                                       # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402

CASES = ("c", "ct")
A_N = D12.A_N                                   # (100, 200, 500)
N_SIZE1 = 5000
N_POW1 = 2000
POW1_N = 200
POW1_RHO = (0.90, 0.95)
POW1_ERR = (("ma", 0.0), ("ma", -0.5))
PROBE_ERR = ("ma", -0.8)
PROBE_N = 500
PROBE_CASE = "ct"
PROBE1_PATHS = 100
PROBE3_PATHS = 1000
N_CAL3 = 100000
CAL3_N = (100, 200, 500)
N_SIZE3 = 20000
N_POW3 = 5000
POW3_RHO = (0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99)
PASO0_CELLS = 6                                  # 0-3: 50 series cada una; 4-5: 2000 caminos iid (c, ct)
PASO0_REPS = (50, 50, 50, 50, 2000, 2000)
ARMS = {"iii": 3, "iv": 4, "v_prime": 5}         # segundo nivel del spawn_key (enmienda 2, seccion 3)
PASO0_ARMS = {"SB": 6, "SWB": 7}
R = 399
B_PASO0_V2 = 999                                 # enmienda 3, E3.1


def size_cell(err, n, case):
    return D12.size_cell(err, n, case)


def pow1_cell(err, rho, case):
    return "pw1_%s_rho%s_n%d_%s" % (P12.err_tag(err), D12.rtag(rho), POW1_N, case)


SIZE_CELLS = tuple(size_cell(e, n, c) for e in P12.ERRORS for n in A_N for c in CASES)
CELLS = {
    151: ("probe_%s_n%d_%s" % (P12.err_tag(PROBE_ERR), PROBE_N, PROBE_CASE),),
    152: SIZE_CELLS,
    153: tuple(pow1_cell(e, r, c) for e in POW1_ERR for r in POW1_RHO for c in CASES),
    154: tuple("paso0_%d" % k for k in range(PASO0_CELLS)),
    155: tuple("cal3_n%d" % n for n in CAL3_N),
    156: SIZE_CELLS,
    157: tuple("pw3_rho%s_n200_c" % D12.rtag(r) for r in POW3_RHO),
    158: ("probe3_%s_n%d_%s" % (P12.err_tag(PROBE_ERR), PROBE_N, PROBE_CASE),),
    159: tuple("paso0b_%d" % k for k in range(PASO0_CELLS)),   # enmienda 3, E3.1-a (Paso 0 con B = 999)
}
BOOT_FAMILIES = (151, 152, 153)                  # familias con streams por brazo (iii, iv, v')


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 151:
        return PROBE1_PATHS
    if family == 152:
        return N_SIZE1
    if family == 153:
        return N_POW1
    if family in (154, 159):
        return PASO0_REPS[CELLS[family].index(name)]
    if family == 155:
        return N_CAL3
    if family == 156:
        return N_SIZE3
    if family == 157:
        return N_POW3
    if family == 158:
        return PROBE3_PATHS
    return 0


def arm_keys(family, name):
    """Segundos niveles del spawn_key por camino (ademas del de la trayectoria)."""
    if family in BOOT_FAMILIES:
        return tuple(ARMS.values())
    if family in (154, 159):
        return tuple(PASO0_ARMS.values())
    return ()
