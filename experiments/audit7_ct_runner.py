"""
Auditoria A7 - Bloque 2: runner del caso "ct" (tamano, DGP 1-ct, DGP 3-ct).

Por serie guarda COLUMNS: componentes estandarizados del test propuesto "ct"
con detrend QD y MCO (sigma_HAC sobre diff(Y) de la serie original), los de la
referencia "c" sobre la misma serie sin su componente determinista, y los
p-valores de ADF, PP y DF-GLS con tendencia. Los p-valores del test propuesto
no se calculan aqui: los aplica audit7_ct_analysis.py con las nulas de 50000
replicas. Un comparador que falla en una serie deja NaN (se cuenta en el
analisis y no rechaza).

Guardas: no corre si ct_verification_audit7.json no existe o su veredicto no es
PASA (verificaciones 1 y 2 y Paso 0). Checkpoint atomico por lote, sonda de 14
series y tope con parada limpia (audit7_common.run_cell_batched).

Uso:
  python experiments/audit7_ct_runner.py --cells "size;dgp1;dgp3" --cores 14 --max-seconds 14400
  (filtros: "dgp1:n=200", "size:n=1000", "dgp3:r=4.0")
"""
import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402
import audit7_ct_design as D                                     # noqa: E402
from power_comparison import C_1, C_2                            # noqa: E402
from stationarity_test.utils import (rolling_mean, rolling_var,  # noqa: E402
                                     sample_variance_over_k)
from stationarity_test.hac_estimator import hac_newey_west       # noqa: E402
from stationarity_test.deterministics import apply_deterministics  # noqa: E402
from statsmodels.tsa.stattools import adfuller                   # noqa: E402
from arch.unitroot import DFGLS, PhillipsPerron                  # noqa: E402

CKPT = os.path.join(C.CKPT_ROOT, "audit7_ct")
MANIFEST = os.path.join(C.RESULTS, "ct_manifest_audit7.json")
VERIFY = os.path.join(C.RESULTS, "ct_verification_audit7.json")

COLUMNS = ["g1_qd", "g2_qd", "g1_ols", "g2_ols", "sigma_hat",
           "g1_c_nodet", "g2_c_nodet", "sigma_hat_nodet",
           "p_adf_ct", "lag_adf_ct", "p_pp_ct", "p_dfgls_ct"]
IDX = {c: i for i, c in enumerate(COLUMNS)}
NSIM = {"size": D.N_SIM, "dgp1": D.N_SIM, "dgp3": D.N_SIM}


# ---------------------------------------------------------------------------
# Procedimientos sobre una serie
# ---------------------------------------------------------------------------
def taus(n):
    tau_1 = max(2, min(int(round(D.THETA[0] * n)), n // 2))
    tau_2 = max(2, min(int(round(D.THETA[1] * n)), n // 2))
    return tau_1, tau_2


def components_from(Y_stat, Y_scale, n):
    """g1_std, g2_std con las rolling statistics sobre Y_stat y sigma_HAC sobre diff(Y_scale)."""
    tau_1, tau_2 = taus(n)
    g1_raw = float(np.sqrt(max(sample_variance_over_k(rolling_mean(Y_stat, tau_1)), 0.0)))
    g2_raw = float(np.sqrt(max(sample_variance_over_k(rolling_var(Y_stat, tau_2)), 0.0)))
    s2 = hac_newey_west(np.diff(Y_scale), andrews_pilot=D.PILOT)
    s = float(np.sqrt(s2))
    g1 = g1_raw / (s * n ** (C_1 / 2.0)) if s > 0 else 0.0
    g2 = g2_raw / (s2 * n ** (C_2 / 2.0)) if s2 > 0 else 0.0
    return float(g1), float(g2), s


def statistic(g1, g2, R=D.R):
    return np.sqrt((1.0 - R) ** 2 * np.asarray(g1) ** 2 + R ** 2 * np.asarray(g2) ** 2)


def adf_ct(Y):
    try:
        res = adfuller(Y, regression="ct", autolag="AIC")
        return float(res[1]), float(res[2])
    except Exception:
        return float("nan"), float("nan")


def pp_ct(Y):
    try:
        return float(PhillipsPerron(Y, trend="ct").pvalue)
    except Exception:
        return float("nan")


def dfgls_ct(Y):
    try:
        return float(DFGLS(Y, trend="ct").pvalue)
    except Exception:
        return float("nan")


def row(kind, n, param, sb, i):
    Y, base = D.generate(kind, n, param, sb, i)
    g1q, g2q, s = components_from(apply_deterministics(Y, "ct", "qd"), Y, n)
    g1o, g2o, _ = components_from(apply_deterministics(Y, "ct", "ols"), Y, n)
    g1c, g2c, sc = components_from(base, base, n)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p_adf, lag = adf_ct(Y)
        p_pp = pp_ct(Y)
        p_dfgls = dfgls_ct(Y)
    return [g1q, g2q, g1o, g2o, s, g1c, g2c, sc, p_adf, lag, p_pp, p_dfgls]


def _rows(kind, n, param, sb, indices):
    return [row(kind, n, param, sb, i) for i in indices]


def _warm(ns):
    for n in ns:
        row("size", n, 0.0, 1, 0)
    return True


def warm_pool(cores, ns):
    Parallel(n_jobs=cores, backend="loky")(delayed(_warm)(tuple(ns)) for _ in range(cores))


def make_batch_fn(kind, n, param, sb, cores):
    def batch_fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(
            delayed(_rows)(kind, n, param, sb, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return batch_fn


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_cells(spec):
    grids = {"size": D.size_cells, "dgp1": D.dgp1_cells, "dgp3": D.dgp3_cells}
    pname = {"size": "mu", "dgp1": "rho", "dgp3": "r"}
    out = []
    for part in [p.strip() for p in spec.split(";") if p.strip()]:
        kind, _, rest = part.partition(":")
        kind = kind.strip()
        if kind not in grids:
            raise ValueError("clase de celda desconocida: %r" % kind)
        kv = dict(x.split("=") for x in rest.split(",") if "=" in x)
        cells = grids[kind]()
        if "n" in kv:
            cells = [c for c in cells if c[0] == int(kv["n"])]
        if pname[kind] in kv:
            cells = [c for c in cells if abs(c[1] - float(kv[pname[kind]])) < 1e-9]
        out += [(kind,) + tuple(c) for c in cells]
    if not out:
        raise ValueError("la especificacion %r no selecciona ninguna celda" % spec)
    return out


def verification_passed():
    if not os.path.exists(VERIFY):
        return False, "no existe %s" % VERIFY
    with open(VERIFY, encoding="utf-8") as f:
        v = json.load(f)
    return v.get("verdict") == "PASA", "veredicto %s" % v.get("verdict")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="size;dgp1;dgp3")
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.DEFAULT_MAX_SECONDS)
    a = ap.parse_args()
    ok, why = verification_passed()
    if not ok:
        raise SystemExit("GUARDA: las verificaciones previas no pasan (%s); no se corre el caso ct." % why)
    cells = parse_cells(a.cells)
    resume = ('python experiments/audit7_ct_runner.py --cells "%s" --cores %d --max-seconds %.0f'
              % (a.cells, a.cores, a.max_seconds))
    manifest = {"cells": {}}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)

    print("=" * 78)
    print("  A7 / Bloque 2 - runner ct   celdas=%d   cores=%d   tope=%.2f h"
          % (len(cells), a.cores, a.max_seconds / 3600))
    print("=" * 78, flush=True)
    t_block = time.time()
    warm_pool(a.cores, sorted({c[1] for c in cells}))

    status = 0
    for kind, n, param in cells:
        tg, sb = D.tag(kind, n, param), D.seed_base(kind, n, param)
        print("\n[CELDA] %s  seed_base=%d  N=%d" % (tg, sb, NSIM[kind]), flush=True)
        rec = {"kind": kind, "n": n, "param": param, "seed_base": sb, "n_sim": NSIM[kind],
               "columns": COLUMNS}
        try:
            _, info = C.run_cell_batched(tg, NSIM[kind], make_batch_fn(kind, n, param, sb, a.cores),
                                         CKPT, a.cores, t_block, a.max_seconds, resume)
            rec.update(info)
        except C.BudgetExhausted as exc:
            rec.update({"complete": False, "stopped": str(exc)})
            manifest["cells"][tg] = rec
            C.atomic_write_json(MANIFEST, manifest)
            print("  [TOPE] %s" % exc)
            status = 2
            break
        manifest["cells"][tg] = rec
        manifest["provenance"] = C.provenance(dgp="ct_runner", n_sim=None,
                                              seed_formula="ver audit7_ct_design.py")
        C.atomic_write_json(MANIFEST, manifest)
        print("  [COMPLETA] %s en %.0f s" % (tg, info["elapsed_sec"]), flush=True)

    print("\n" + "=" * 78)
    print("  bloque: %.2f h   %s" % ((time.time() - t_block) / 3600,
                                    "COMPLETO" if status == 0 else "DETENIDO POR TOPE"))
    if status:
        print("  REANUDAR CON:\n    %s" % resume)
    print("=" * 78)
    return status


if __name__ == "__main__":
    sys.exit(main())
