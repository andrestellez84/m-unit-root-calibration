"""
Auditoria A8 - diseno: celdas, familias de semillas y generadores de trayectorias.

Cada familia nueva (90-98) tiene una lista ORDENADA de celdas; el indice de la
celda en la lista es el primer elemento del spawn_key. Las listas solo se
amplian al final: nunca se reordenan.

Celdas reutilizadas (excepcion de pareo con lo publicado): se regeneran con las
semillas y los generadores originales, importados de sus scripts:
  - gaussianas n in {60, 100, 150, 200, 500, 1000}: power_comparison.generate_ar1
    (rho = 1) con default_rng(0 + i) (audit5_tarea1.py / audit5_tarea3.py);
  - colas pesadas t(5), t(3): size_robustness_heavy_tails.generate_rw_heavy con
    default_rng(900000 + n*100 + df*10 + i) (audit5b_tarea_r3.py, fuente de la
    Tabla 8 publicada segun B0);
  - GARCH (16 celdas): audit7_garch_size.generate con sus semillas de A7.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402

THETA_PRIMARY = 0.1
THETA_SENS = (0.02, 0.05, 0.2)
R_PRIMARY = 0.0
R_PUBLISHED = 0.5
N_SIM = 5000
N_SIM_BOOT = 2000
N_CAL = 50000
N_INDEP = 20000                   # enmienda 2: referencia gaussiana independiente por n
DRIFT_MU_REPORT = (0.0, 0.05, 0.2)
N_BOOT_MAX = 1000                 # enmienda 2: bootstrap solo en n <= 1000
CAL_SEED_PUBLISHED = 42           # semilla de build_null_cdf en todas las tablas publicadas
CBAR_CONST = -7.0
CBAR_TREND = -13.5

N_GAUSS_REUSED = (60, 100, 150, 200, 500, 1000)
N_GAUSS_NEW = (2000, 5000)
N_ALL = N_GAUSS_REUSED + N_GAUSS_NEW
N_MAIN = (200, 500, 1000, 2000, 5000)
HEAVY = (("t5", 5), ("t3", 3))
N_HEAVY = (200, 500, 1000)

# GARCH: (clave de A7, n); orden de la Tabla 1.4a/1.4a-bis de A7
GARCH_CELLS = tuple([("base", n) for n in (200, 500, 1000)]
                    + [("p099", n) for n in (200, 500, 1000, 2000, 5000)]
                    + [("p098", n) for n in (200, 500, 1000)]
                    + [("p095_t5", n) for n in (200, 500, 1000, 2000, 5000)])

# ---------------------------------------------------------------------------
# Celdas por familia (indice = posicion)
# ---------------------------------------------------------------------------
B4_C = tuple(range(0, 31))
B4_C_EXTRA = (13.5,)          # el reporte pide c = 13.5, fuera de la rejilla entera
B5_DGP1_RHO = (0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99)
B5_DGP2_DELTA = (0, 0.5, 1, 2, 3, 5)
B5_DGP3_R = (1, 1.5, 2, 3, 4)
B5_CT_RHO = (0.90, 0.95, 0.97, 0.99)
B6_D = (150, 200, 250, 300)
B7_N = (100, 200, 500, 1000, 2000, 5000)


def fmt(x):
    return ("%g" % x).replace(".", "p")


CELLS = {
    90: (),
    91: ("np_validation_dm", "np_validation_ct", "invariance_dm", "invariance_ct", "drift_ct", "regression",
         "np_diag_T501_dm", "np_diag_T501_ct", "np_diag_T10001_dm", "np_diag_T10001_ct",
         "np_diag_arch_dm", "np_diag_arch_ct"),
    92: tuple(["gauss_n%d" % n for n in N_GAUSS_NEW] + ["cal_dm_n%d" % n for n in N_ALL]
              + ["diag_gauss_n%d" % n for n in (200, 500, 1000)] + ["diag_cal_n200"]
              + ["indep_gauss_n%d" % n for n in N_ALL]),
    93: tuple(["boot_gauss_n200_N5000"] + ["rseed_boot_gauss_n200_N5000"]
              + ["rseed_%s" % k for k in ("gauss_n%d" % n for n in N_MAIN)]
              + ["rseed_heavy_%s_n%d" % (d, n) for d, _ in HEAVY for n in N_HEAVY]
              + ["rseed_garch_%s_n%d" % (k, n) for k, n in GARCH_CELLS]
              + ["rseed_indep_gauss_n%d" % n for n in (200, 500, 1000)]),
    94: tuple(["lap_%s_%s" % (case, role) for case in ("dm", "ct") for role in ("cal", "envcal", "test0")]
              + ["lap_%s_c%d" % (case, c) for case in ("dm", "ct") for c in B4_C]
              + ["lap_%s_c13.5" % case for case in ("dm", "ct")]),
    95: tuple(["dgp1_rho%s_n%d" % (fmt(r), n) for r in B5_DGP1_RHO for n in (200, 500, 1000)]
              + ["dgp2_delta%s_n%d" % (fmt(d), n) for d in B5_DGP2_DELTA for n in (200, 500, 1000)]
              + ["za_rw_n%d" % n for n in (200, 500, 1000)]
              + ["za_rwbreak_n%d" % n for n in (200, 500, 1000)]
              + ["dgp3_r%s_n%d" % (fmt(r), n) for r in B5_DGP3_R for n in (200, 500, 1000)]
              + ["ct_size_n%d" % n for n in N_MAIN]
              + ["ct_power_rho%s_n%d" % (fmt(r), n) for r in B5_CT_RHO for n in (200, 500, 1000)]
              + ["cal_ct_n%d" % n for n in N_MAIN]
              + ["rseed_dgp1_rho%s_n%d" % (fmt(r), n) for r in (0.90, 0.95, 0.97, 0.99) for n in (200, 500, 1000)]
              + ["rseed_dgp3_r%s_n%d" % (fmt(r), n) for r in B5_DGP3_R for n in (200, 500, 1000)]),
    96: tuple(["oos_D%d" % d for d in B6_D]),
    97: tuple(["cv_%s_n%d" % (case, n) for case in ("dm", "ct") for n in B7_N]
              + ["cvx_%s_n%d" % (case, n) for case in ("dm", "ct") for n in B7_N]
              + ["gls_n20000"]),
    98: (),
}

# replicas por celda (para el mapa de semillas); None = segun rol
REPS = {"cal": N_CAL, "envcal": 20000, "test0": 5000}


def cell_index(family, name):
    return CELLS[family].index(name)


def cell_reps(family, name):
    if family == 91:
        if name.startswith("np_validation") or name.startswith("np_diag_T"):
            return 20000
        if name.startswith("np_diag_arch"):
            return 200
        return 100
    if family == 92:
        if name.startswith(("diag_gauss", "indep_gauss")):
            return N_INDEP
        return N_CAL if name.startswith(("cal_", "diag_cal")) else N_SIM
    if family == 93:
        if name.startswith("rseed_boot_gauss") or name == "boot_gauss_n200_N5000":
            return N_SIM
        return N_SIM_BOOT
    if family == 94:
        role = name.split("_")[2]
        return REPS.get(role, 20000)
    if family == 95:
        if name.startswith("cal_ct"):
            return N_CAL
        if name.startswith("rseed_"):
            return N_SIM_BOOT
        return N_SIM
    if family == 96:
        return N_SIM
    if family == 97:
        return 20000 if name == "gls_n20000" else 100000
    return 0


# ---------------------------------------------------------------------------
# Generadores
# ---------------------------------------------------------------------------
def gauss_rw(n, rng):
    from power_comparison import generate_ar1
    return generate_ar1(n=n, rho=1.0, rng=rng)


def reused_gauss(n, i):
    return gauss_rw(n, np.random.default_rng(0 + i))


def heavy_seed_base(df, n):
    return 900000 + n * 100 + df * 10


def reused_heavy(dist, n, i):
    from size_robustness_heavy_tails import DISTRIBUTIONS, generate_rw_heavy
    p = DISTRIBUTIONS[dist]
    return generate_rw_heavy(n, p["df"], p["scale"], np.random.default_rng(heavy_seed_base(p["df"], n) + i))


def reused_garch(key, n, i):
    import audit7_garch_size as G
    return G.generate(key, n, G.cell_seed_base(key, n), i)[0]


def new_gauss(family, cell_name, n, i):
    return gauss_rw(n, C.rep_rng(family, cell_index(family, cell_name), i))


# Celdas de tamano de B2/B3: nombre -> (tipo, n, generador(i))
def size_cells():
    cells = {}
    for n in N_GAUSS_REUSED:
        cells["gauss_n%d" % n] = {"kind": "gauss", "n": n, "reused": True, "source": "power_comparison.generate_ar1, default_rng(0 + i)"}
    for n in N_GAUSS_NEW:
        cells["gauss_n%d" % n] = {"kind": "gauss", "n": n, "reused": False, "source": "familia 92"}
    for d, df in HEAVY:
        for n in N_HEAVY:
            cells["heavy_%s_n%d" % (d, n)] = {"kind": "heavy", "dist": d, "n": n, "reused": True,
                                             "source": "size_robustness_heavy_tails.generate_rw_heavy, default_rng(900000 + n*100 + df*10 + i)"}
    for k, n in GARCH_CELLS:
        cells["garch_%s_n%d" % (k, n)] = {"kind": "garch", "key": k, "n": n, "reused": True,
                                         "source": "audit7_garch_size.generate (A7)"}
    return cells


def indep_cells():
    """Enmienda 2: trayectorias gaussianas independientes (familia 92), un hijo por n."""
    return {"indep_gauss_n%d" % n: {"kind": "gauss_indep", "n": n, "reused": False,
                                    "source": "familia 92, un hijo de SeedSequence por n"} for n in N_ALL}


def size_path(cell_name, spec, i):
    if spec["kind"] == "gauss_indep":
        return new_gauss(92, cell_name, spec["n"], i)
    if spec["kind"] == "gauss":
        if spec["reused"]:
            return reused_gauss(spec["n"], i)
        return new_gauss(92, cell_name, spec["n"], i)
    if spec["kind"] == "heavy":
        return reused_heavy(spec["dist"], spec["n"], i)
    return reused_garch(spec["key"], spec["n"], i)


def cal_path(n, i):
    """Camino de calibracion de los valores criticos simulados (familia 92)."""
    return new_gauss(92, "cal_dm_n%d" % n, n, i)
