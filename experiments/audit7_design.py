"""
Auditoria A7 - diseno del Bloque 1: DGP 5 y calibracion bajo la nula compuesta.

Decisiones que fija este modulo (commit de la especificacion revisada):

- H0 del Bloque 1 es COMPUESTA: raiz unitaria Y homoscedasticidad (Ec. 3 del
  manuscrito: paseo aleatorio con innovaciones iid). Toda la calibracion se hace
  sobre un paseo aleatorio gaussiano homoscedastico, una celda por n. Toda la
  rejilla de DGP 5 es potencia.
- DGP 5 usa el generador existente generate_ar1_break_variance de
  power_comparison.py, que coincide con la especificacion
  Y_t = rho Y_{t-1} + eps_t, sd(eps_t) = 1 + (r-1) 1{t > floor(n/2)}.
- La calibracion usa generate_rw_break_variance(ratio=1.0), del mismo archivo.
- Semillas disjuntas: familia*10^8 + celda*10^5 (audit7_common.seed_base).

Segunda enmienda (experiments/enmienda2_dgp5_audit7.md):
- Se anade la extension de quiebres debiles r in DGP5_RATIOS_WEAK a n in
  DGP5_N_MAIN. Sus celdas van DESPUES de las 27 registradas en el orden
  canonico, de modo que ninguna celda registrada cambia de semilla.
- Se retiran las celdas de confirmacion n=1000 y, con ellas, la calibracion y
  la nula adaptativa de n=1000. Conservan su indice de semilla por si se
  reanudan.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                          # noqa: E402
from power_comparison import (generate_ar1_break_variance,          # noqa: E402
                              generate_rw_break_variance)

ALPHA = 0.05

# Familias de semillas de A7 (cada una con celdas disjuntas por construccion)
FAM_KAPPA2_VALIDATION = 91     # Bloque 1a: compuerta nominal de kappa_2
FAM_KAPPA2_DIAGNOSIS = 92      # Bloque 1a: descomposicion del infra-dimensionamiento
FAM_CALIBRATION = 70           # Bloque 1: nula compuesta, una celda por n
FAM_DGP5 = 60                  # Bloque 1: rejilla de potencia
FAM_SEED_CONTROL = 93          # semillas de R de la celda de control del bootstrap de A6
SEED_CONTROL_N_SIM = 2000      # la celda de A6 que se replica tiene 2000 series
FAM_SIZE_DIAG = 94             # semillas de R del diagnostico del tamano del bootstrap a n=200
SIZE_DIAG_N_SIM = 2000         # la celda de A6 dgp3 n=200 r=1.0 tiene 2000 series

# Calibracion bajo la nula compuesta
N_CAL = 5000
CAL_N_GRID = (200, 500, 1000)  # fija el indice de semilla; no cambiar
CAL_N_ACTIVE = (200, 500)      # segunda enmienda: n=1000 retirado

# Rejilla de DGP 5 (r = 1.5 eliminado de la registrada por la decision 4)
DGP5_RHOS = (0.90, 0.93, 0.95)
DGP5_RATIOS = (1.0, 2.0, 3.0, 4.0)
DGP5_N_MAIN = (200, 500)
DGP5_CONFIRM = ((1000, 0.93, 2.0), (1000, 0.93, 3.0), (1000, 0.95, 3.0))  # retiradas (enmienda 2)
DGP5_RATIOS_WEAK = (1.1, 1.25, 1.5)   # extension de la segunda enmienda
DGP5_N_SIM = 2000
DGP5_B = 399                   # B = 399 en toda la rejilla (decision 4)


def fmt_r(r):
    """Etiqueta de r: un decimal si basta (identica a la de la rejilla registrada), si no dos."""
    return "%.1f" % r if abs(r * 10 - round(r * 10)) < 1e-9 else "%.2f" % r


def dgp5_cells_registered():
    """Las 27 celdas de la especificacion revisada (indices de semilla 0..26)."""
    cells = [(n, rho, r) for n in DGP5_N_MAIN for rho in DGP5_RHOS for r in DGP5_RATIOS]
    cells += list(DGP5_CONFIRM)
    return cells


def dgp5_cells_weak():
    """Extension de la segunda enmienda (indices de semilla 27..44)."""
    return [(n, rho, r) for n in DGP5_N_MAIN for rho in DGP5_RHOS for r in DGP5_RATIOS_WEAK]


def dgp5_cells():
    """Orden canonico de todas las celdas: el indice fija la semilla."""
    return dgp5_cells_registered() + dgp5_cells_weak()


def dgp5_cells_active():
    """Celdas que se ejecutan tras la segunda enmienda (sin n=1000)."""
    return [c for c in dgp5_cells() if c[0] in CAL_N_ACTIVE]


def is_weak(r):
    return any(abs(r - w) < 1e-9 for w in DGP5_RATIOS_WEAK)


def dgp5_tag(n, rho, r):
    return "dgp5_n%d_rho%.2f_r%s" % (n, rho, fmt_r(r))


def dgp5_seed_base(n, rho, r):
    return C.seed_base(FAM_DGP5, dgp5_cells().index((n, rho, r)))


def cal_tag(n):
    return "cal_rw_n%d" % n


def cal_seed_base(n):
    return C.seed_base(FAM_CALIBRATION, CAL_N_GRID.index(n))


def generate_calibration(n, rng):
    """Paseo aleatorio gaussiano homoscedastico: la nula compuesta."""
    return generate_rw_break_variance(n=n, ratio=1.0, rng=rng)


def generate_dgp5(n, rho, r, rng):
    """AR(1) estacionario con quiebre de varianza de innovaciones a mitad."""
    return generate_ar1_break_variance(n=n, rho=rho, ratio=r, rng=rng)


def all_seed_bases():
    """Semillas de todas las celdas de la familia DGP 5 y de calibracion."""
    out = {dgp5_tag(*c): dgp5_seed_base(*c) for c in dgp5_cells()}
    out.update({cal_tag(n): cal_seed_base(n) for n in CAL_N_GRID})
    return out
