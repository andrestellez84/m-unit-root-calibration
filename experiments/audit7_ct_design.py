"""
Auditoria A7 - Bloque 2: diseno del caso con constante y tendencia ("ct").

Fija, antes de correr nada:

Procedimientos
--------------
- Test propuesto "ct" con theta = (0.1, 0.1), R = 0.50, piloto alpha(1):
  rolling statistics sobre Y detrendada contra (1, t); sigma_HAC sobre diff(Y)
  de la serie original. Variante PRINCIPAL detrend="qd" (ERS, cbar = -13.5);
  secundaria detrend="ols".
- Nula PRINCIPAL: la del paquete (build_null_cdf con deterministics="ct"),
  que simula paseos aleatorios con sigma = 1 conocida, detrendados igual. Es
  la misma convencion que usa el caso "c", de modo que "c" y "ct" solo
  difieren en el detrending. N_cal = 50000.
- Nula SECUNDARIA (diagnostico): el estadistico de muestra finita completo,
  con sigma_HAC estimada en cada paseo simulado. N_cal = 50000.
- Referencia "c": el estadistico actual sobre la misma serie SIN su componente
  determinista (mismas innovaciones), con la nula del paper (seed 42, 50000).
- Comparadores con tendencia: ADF (statsmodels adfuller, regression="ct",
  AIC; coincide con arch ADF(trend="ct")), PP (arch, trend="ct") y DF-GLS
  (arch, trend="ct", AIC). Sin bootstrap.

Semillas (decision 4: familia*10^8 + celda*10^5, sustituye 700000 + n*100 + ...)
------------------------------------------------------------------------------
  71 tamano      celda = indice de n; COMPARTIDA entre los tres mu (numeros
                 aleatorios comunes deliberados: la no dependencia de mu se
                 comprueba serie a serie).
  72 DGP 1-ct    celda = indice de (n, rho)
  73 DGP 3-ct    celda = indice de (n, r)
  74 nula HAC    celda = indice de (n, detrend), semilla seed_base + i
  75 nula del paquete  celda = indice de (n, detrend), semilla de un solo flujo
  76 verificaciones 1 y 2

Componentes deterministas de los DGP
------------------------------------
Todos los procedimientos "ct" son invariantes a b + c*t (verificacion 2 para el
propuesto; algebra de MCO para ADF, PP y DF-GLS con tendencia), asi que la
pendiente no altera ningun rechazo. Se fija DRIFT = TREND_SLOPE = 0.2, el mayor
mu de la tabla de tamano.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
SRC = os.path.join(os.path.dirname(HERE), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import audit7_common as C                                           # noqa: E402
from power_comparison import generate_ar1, generate_rw_break_variance  # noqa: E402

THETA = (0.1, 0.1)
R = 0.50
PILOT = "alpha1"
DETRENDS = ("qd", "ols")
MAIN_DETREND = "qd"

N_CAL = 50000
N_SIM = 5000
N_REGRESSION = 100
N_PAIRING = 50
REL_TOL_INVARIANCE = 1e-9          # "a precision de maquina", registrada antes de medir
COMPONENT_TOL = 1e-12

FAM_SIZE = 71
FAM_DGP1 = 72
FAM_DGP3 = 73
FAM_NULL_HAC = 74
FAM_NULL_PKG = 75
FAM_VERIFY = 76

SIZE_N = (200, 500, 1000)
SIZE_MUS = (0.0, 0.05, 0.2)
DGP1_N = (200, 500, 1000)
DGP1_RHOS = (0.90, 0.93, 0.95, 0.97, 0.99)
DGP3_N = (200, 1000)
DGP3_RATIOS = (1.0, 2.0, 3.0, 4.0)
DRIFT = 0.2
TREND_SLOPE = 0.2
C_REFERENCE_NULL_SEED = 42         # nula del paper (power_comparison.py)

INVARIANCE_A = (0.1, 10.0)
INVARIANCE_BC = ((3.7, -0.25), (-150.0, 2.5))
NULL_N = tuple(sorted(set(SIZE_N) | set(DGP1_N) | set(DGP3_N)))


# ---------------------------------------------------------------------------
# Celdas, etiquetas y semillas
# ---------------------------------------------------------------------------
def size_cells():
    return [(n, mu) for n in SIZE_N for mu in SIZE_MUS]


def dgp1_cells():
    return [(n, rho) for n in DGP1_N for rho in DGP1_RHOS]


def dgp3_cells():
    return [(n, r) for n in DGP3_N for r in DGP3_RATIOS]


def null_cells():
    return [(n, d) for n in NULL_N for d in DETRENDS]


def tag(kind, n, param):
    if kind == "size":
        return "ctsize_n%d_mu%.2f" % (n, param)
    if kind == "dgp1":
        return "ctdgp1_n%d_rho%.2f" % (n, param)
    if kind == "dgp3":
        return "ctdgp3_n%d_r%.1f" % (n, param)
    raise ValueError(kind)


def seed_base(kind, n, param):
    if kind == "size":
        return C.seed_base(FAM_SIZE, SIZE_N.index(n))           # comun a los tres mu
    if kind == "dgp1":
        return C.seed_base(FAM_DGP1, dgp1_cells().index((n, param)))
    if kind == "dgp3":
        return C.seed_base(FAM_DGP3, dgp3_cells().index((n, param)))
    raise ValueError(kind)


def null_seed(convention, n, detrend):
    fam = FAM_NULL_PKG if convention == "known" else FAM_NULL_HAC
    return C.seed_base(fam, null_cells().index((n, detrend)))


def all_seed_bases():
    """Bases distintas (el tamano cuenta una por n: los mu la comparten a proposito)."""
    out = {"ctsize_n%d_allmu" % n: seed_base("size", n, None) for n in SIZE_N}
    out.update({tag("dgp1", n, rho): seed_base("dgp1", n, rho) for n, rho in dgp1_cells()})
    out.update({tag("dgp3", n, r): seed_base("dgp3", n, r) for n, r in dgp3_cells()})
    out.update({"ctnull_hac_n%d_%s" % (n, d): null_seed("hac", n, d) for n, d in null_cells()})
    out.update({"ctnull_pkg_n%d_%s" % (n, d): null_seed("known", n, d) for n, d in null_cells()})
    out["ct_verify"] = C.seed_base(FAM_VERIFY, 0)
    return out


# ---------------------------------------------------------------------------
# Generadores: serie observada y su parte sin componente determinista
# ---------------------------------------------------------------------------
def generate(kind, n, param, sb, i):
    """(Y observada, Y sin componente determinista) con default_rng(sb + i)."""
    rng = np.random.default_rng(sb + i)
    t = np.arange(n + 1, dtype=np.float64)
    if kind == "size":
        base = generate_rw_break_variance(n=n, ratio=1.0, rng=rng)
        return base + param * t, base
    if kind == "dgp1":
        base = generate_ar1(n=n, rho=param, rng=rng)
        return base + TREND_SLOPE * t, base
    if kind == "dgp3":
        base = generate_rw_break_variance(n=n, ratio=param, rng=rng)
        return base + DRIFT * t, base
    raise ValueError(kind)
