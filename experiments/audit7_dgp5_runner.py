"""
Auditoria A7 - Bloque 1: runner de DGP 5, de la calibracion bajo la nula
compuesta y de la nula nominal del test adaptativo.

Clases de celda
---------------
  cal       paseo aleatorio gaussiano homoscedastico, N_cal = 5000 por n
            (familia 70). Todos los procedimientos. Fija los umbrales a tamano
            igualado y el nivel comun de la union calibrada conjuntamente.
  dgp5      AR(1) con quiebre de varianza, 2000 replicas por celda (familia 60).
            Todos los procedimientos. Toda la rejilla es potencia.
  adaptnull nula nominal del test con R adaptativo: replica exactamente la de A5
            (50000 paseos aleatorios generate_ar1(rho=1), semillas 42 + i,
            componentes con sigma HAC). Solo componentes, sin tests.

Por serie se guardan las columnas COLUMNS (cal y dgp5) o ADAPTNULL_COLUMNS.
Nada se agrega aqui: el analisis lee los checkpoints en otro script, cuyo
codigo se commitea antes de ejecutar DGP 5.

Guardas
-------
- No se toca ninguna serie de DGP 5 si las dos enmiendas
  (experiments/enmienda_dgp5_audit7.md y enmienda2_dgp5_audit7.md) no estan
  commiteadas y sin cambios.
- Seleccion por defecto (segunda enmienda): n in D.CAL_N_ACTIVE y las celdas
  D.dgp5_cells_active(). "dgp5:confirm" (retiradas), "dgp5:weak" y
  "dgp5:registered" solo a peticion explicita.
- El p-valor nominal de R = 0.50 se evalua en el proceso padre: el pool de loky
  expira tras 300 s ociosos durante cada lote de R, y reconstruir la nula de
  50000 replicas en cada trabajador y en cada lote seria un costo oculto.
- Checkpoint atomico por lote, sonda de 14 series, tope de tiempo y parada
  limpia entre lotes con el comando de reanudacion completo (audit7_common).
- El worker de R conserva su guardia de orden de bytes.

Uso:
  python experiments/audit7_dgp5_runner.py --cells "cal:n=200;dgp5:n=200,rho=0.93" \
      --cores 14 --B 399 --n-sim-dgp5 2000 --n-cal 5000 --max-seconds 14400
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
import warnings

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402
import audit7_design as D                                        # noqa: E402
import audit7_readout as RO                                      # noqa: E402
from audit7_kappa2 import kappa2_on_adf_residuals                # noqa: E402
import power_comparison as PC                                    # noqa: E402
from power_comparison import C_1, C_2                            # noqa: E402
from stationarity_test.utils import (rolling_mean, rolling_var,  # noqa: E402
                                     sample_variance_over_k)
from stationarity_test.hac_estimator import hac_newey_west       # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf  # noqa: E402
from arch.unitroot import DFGLS                                  # noqa: E402
from audit6_wild_bootstrap_sweep import find_rscript             # noqa: E402

CKPT = os.path.join(C.CKPT_ROOT, "audit7_block1")
MANIFEST = os.path.join(C.RESULTS, "block1_manifest_audit7.json")
# Worker con semilla por serie. El de A6 (audit6_wild_bootstrap_worker.R) no
# fija la semilla del generador de R y su p-valor de una misma serie cambia
# entre ejecuciones.
WORKER_R = os.path.join(HERE, "audit7_bootstrap_worker.R")
AMENDMENTS = ("experiments/enmienda_dgp5_audit7.md", "experiments/enmienda2_dgp5_audit7.md")

THETA = (0.1, 0.1)
PILOT = "alpha1"
N_CAL_R050 = 50000          # nula nominal de R = 0.50: la de power_comparison.py
CAL_SEED_R050 = 42
ADAPT_NULL_N = 50000        # nula nominal del adaptativo: la de A5 (audit5_tarea6)
ADAPT_NULL_SEED = 42
FAM_TIEBREAK = 69           # uniforme de desempate por serie, flujo propio
R_SEED_MODULUS = 2147483647 - 1000000   # igual que SEED_MODULUS del worker de R


def r_seed_start(seed_base, i0):
    """Semilla de R de la serie de indice global i0: (seed_base + i0) mod M.

    La serie i usa (seed_base + i) mod M, de modo que la semilla depende solo del
    indice global y no de las fronteras de lote ni del reparto entre nucleos.
    La ausencia de choques entre celdas se verifica en el Paso 0.
    """
    return int((int(seed_base) + int(i0)) % R_SEED_MODULUS)

COLUMNS = ["g1_std", "g2_std", "stat_R050", "p_R050_nominal", "R_hat",
           "stat_adaptive", "g2_share_R050", "g2_share_adaptive",
           "p_adf", "p_pp", "p_dfgls", "kappa2", "kappa2_adf_lag",
           "p_boot_dfgls", "tiebreak_u"]
ADAPTNULL_COLUMNS = ["g1_std", "g2_std"]
IDX = {c: i for i, c in enumerate(COLUMNS)}


# ---------------------------------------------------------------------------
# Procedimientos sobre una serie
# ---------------------------------------------------------------------------
_R050_CDF = {}


def r050_cdf(n):
    if n not in _R050_CDF:
        _R050_CDF[n] = build_null_cdf(THETA, 0.5, n, N_cal=N_CAL_R050, seed=CAL_SEED_R050)
    return _R050_CDF[n]


def components(Y):
    """g1_std y g2_std con el mismo camino que run_experiment_cell de power_comparison."""
    n = len(Y) - 1
    tau_1 = max(2, min(int(round(THETA[0] * n)), n // 2))
    tau_2 = max(2, min(int(round(THETA[1] * n)), n // 2))
    g1_raw = float(np.sqrt(max(sample_variance_over_k(rolling_mean(Y, tau_1)), 0.0)))
    g2_raw = float(np.sqrt(max(sample_variance_over_k(rolling_var(Y, tau_2)), 0.0)))
    s2 = hac_newey_west(np.diff(Y), andrews_pilot=PILOT)
    s = np.sqrt(s2)
    g1 = g1_raw / (s * n ** (C_1 / 2)) if s > 0 else 0.0
    g2 = g2_raw / (s2 * n ** (C_2 / 2)) if s2 > 0 else 0.0
    return float(g1), float(g2)


def dfgls_pvalue(Y):
    try:
        return float(DFGLS(Y, trend="c").pvalue)
    except Exception:
        return 1.0


def python_row(Y, n, u):
    g1, g2 = components(Y)
    stat050 = RO.statistic(g1, g2, 0.5)
    p050 = float("nan")        # lo rellena make_batch_fn en el proceso padre
    r_hat = RO.adaptive_R(g1, g2)
    stat_a = RO.statistic(g1, g2, r_hat)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p_adf = float(PC.run_adf(Y))
        p_pp = float(PC.run_pp(Y))
        p_dfgls = dfgls_pvalue(Y)
        k2, lag, _ = kappa2_on_adf_residuals(Y)
    return [g1, g2, stat050, p050, r_hat, stat_a,
            RO.g2_energy_share(g1, g2, 0.5), RO.g2_energy_share(g1, g2, r_hat),
            p_adf, p_pp, p_dfgls, k2, float(lag), float("nan"), u]


# ---------------------------------------------------------------------------
# Series y semillas
# ---------------------------------------------------------------------------
def cell_tag(kind, n, rho, r):
    if kind == "cal":
        return D.cal_tag(n)
    if kind == "dgp5":
        return D.dgp5_tag(n, rho, r)
    if kind == "adaptnull":
        return "adaptnull_n%d" % n
    raise ValueError(kind)


def cell_seed_base(kind, n, rho, r):
    if kind == "cal":
        return D.cal_seed_base(n)
    if kind == "dgp5":
        return D.dgp5_seed_base(n, rho, r)
    if kind == "adaptnull":
        return ADAPT_NULL_SEED
    raise ValueError(kind)


def generate(kind, n, rho, r, sb, i):
    rng = np.random.default_rng(sb + i)
    if kind == "cal":
        return D.generate_calibration(n, rng)
    if kind == "dgp5":
        return D.generate_dgp5(n, rho, r, rng)
    if kind == "adaptnull":
        return PC.generate_ar1(n=n, rho=1.0, rng=rng)
    raise ValueError(kind)


def tiebreak_u(sb, i):
    return float(np.random.default_rng([FAM_TIEBREAK, int(sb), int(i)]).random())


def _py_rows(kind, n, rho, r, sb, indices):
    if kind == "adaptnull":
        return [list(components(generate(kind, n, rho, r, sb, i))) for i in indices]
    return [python_row(generate(kind, n, rho, r, sb, i), n, tiebreak_u(sb, i)) for i in indices]


def _warm(ns):
    for n in ns:
        python_row(D.generate_calibration(n, np.random.default_rng(1)), n, 0.5)
    return True


def warm_pool(cores, ns):
    for n in ns:
        r050_cdf(n)                 # en el padre, una vez
    Parallel(n_jobs=cores, backend="loky")(delayed(_warm)(tuple(ns)) for _ in range(cores))


# ---------------------------------------------------------------------------
# Bootstrap via R
# ---------------------------------------------------------------------------
RSCRIPT = find_rscript()


def run_bootstrap(kind, n, rho, r, sb, indices, cores, B):
    tag = cell_tag(kind, n, rho, r)
    if list(indices) != list(range(indices[0], indices[0] + len(indices))):
        raise ValueError("%s: el worker con semilla exige indices contiguos" % tag)
    mat = np.column_stack([generate(kind, n, rho, r, sb, i) for i in indices])
    return run_bootstrap_matrix(tag, mat, indices[0], r_seed_start(sb, indices[0]), cores, B)


def run_bootstrap_matrix(tag, mat, i0, seed_start, cores, B, tmp_dir=CKPT):
    """boot_adf con semilla sobre las columnas de mat (series de indices i0, i0+1, ...)."""
    n = mat.shape[0] - 1
    n_series = mat.shape[1]
    os.makedirs(tmp_dir, exist_ok=True)
    stem = os.path.join(tmp_dir, "_tmp_%s_i%06d" % (tag, i0))
    bin_path, out_json = stem + ".bin", stem + ".json"
    mat.T.tofile(bin_path)                                  # disposicion columnar para R
    expected5 = ",".join("%.6f" % v for v in mat[:5, 0])
    cmd = [RSCRIPT, WORKER_R, bin_path, str(n), str(n_series), str(B),
           str(cores), out_json, expected5, "adf", str(seed_start)]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    wall = time.time() - t0
    try:
        if proc.returncode != 0:
            raise RuntimeError("worker de R fallo (rc=%d):\n%s"
                               % (proc.returncode, (proc.stdout + proc.stderr)[-3000:]))
        with open(out_json, encoding="utf-8") as f:
            d = json.load(f)
    finally:
        for p in (bin_path, out_json):
            if os.path.exists(p):
                os.remove(p)
    p = d["p_adf"]
    if p is None or len(p) != n_series:
        raise RuntimeError("%s: el worker devolvio %s p-valores para %d series"
                           % (tag, None if p is None else len(p), n_series))
    return [float("nan") if v is None else float(v) for v in p], {
        "r_wall_sec": wall, "r_internal_sec": float(d["elapsed_sec"]),
        "r_internal_sec_per_series": float(d["sec_per_series"]),
        "r_seed_start": seed_start}


def make_batch_fn(kind, n, rho, r, sb, cores, B):
    tag = cell_tag(kind, n, rho, r)

    def batch_fn(indices):
        timing = {"k": len(indices)}
        if kind != "adaptnull":
            p_boot, tinfo = run_bootstrap(kind, n, rho, r, sb, indices, cores, B)
            timing.update(tinfo)
        t1 = time.time()
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(
            delayed(_py_rows)(kind, n, rho, r, sb, p) for p in parts)
        timing["py_wall_sec"] = time.time() - t1
        by = {}
        for p, rows in zip(parts, res):
            by.update(zip(p, rows))
        rows = [by[i] for i in indices]
        if kind != "adaptnull":
            cdf = r050_cdf(n)
            for row, pb in zip(rows, p_boot):
                row[IDX["p_boot_dfgls"]] = pb
                row[IDX["p_R050_nominal"]] = float(np.clip(cdf(row[IDX["stat_R050"]]), 0.0, 1.0))
        C.atomic_write_json(os.path.join(CKPT, "%s_i%06d_k%05d.timing.json"
                                         % (tag, indices[0], len(indices))), timing)
        return rows
    return batch_fn


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def amendment_committed():
    """Las dos enmiendas deben estar commiteadas y sin cambios."""
    tracked = C._git("ls-files").splitlines()
    modified = C._git("diff", "--name-only", "HEAD").splitlines()
    return all(a in tracked and a not in modified for a in AMENDMENTS)


def parse_k_batch(spec):
    """'200:1400,500:280' -> {200: 1400, 500: 280}."""
    out = {}
    for item in [x.strip() for x in spec.split(",") if x.strip()]:
        n, k = item.split(":")
        out[int(n)] = int(k)
    return out


def parse_cells(spec):
    out = []
    for part in [p.strip() for p in spec.split(";") if p.strip()]:
        kind, _, rest = part.partition(":")
        kind = kind.strip()
        kv = {}
        for item in [x for x in rest.split(",") if "=" in x]:
            k, v = item.split("=")
            kv[k.strip()] = v.strip()
        if kind in ("cal", "adaptnull"):
            ns = [int(kv["n"])] if "n" in kv else list(D.CAL_N_ACTIVE)
            out += [(kind, n, None, None) for n in ns]
        elif kind == "dgp5":
            first = rest.split(",")[0].strip()
            if first == "confirm":          # retiradas por la segunda enmienda
                cells = list(D.DGP5_CONFIRM)
            elif first == "weak":
                cells = D.dgp5_cells_weak()
            elif first == "registered":
                cells = [c for c in D.dgp5_cells_registered() if c[0] in D.CAL_N_ACTIVE]
            else:
                cells = D.dgp5_cells_active()
            if "n" in kv:
                cells = [c for c in cells if c[0] == int(kv["n"])]
            if "rho" in kv:
                cells = [c for c in cells if abs(c[1] - float(kv["rho"])) < 1e-9]
            if "r" in kv:
                cells = [c for c in cells if abs(c[2] - float(kv["r"])) < 1e-9]
            out += [("dgp5",) + tuple(c) for c in cells]
        else:
            raise ValueError("clase de celda desconocida: %r" % kind)
    if not out:
        raise ValueError("la especificacion %r no selecciona ninguna celda" % spec)
    return out


def n_sim_for(kind, a):
    return {"cal": a.n_cal, "dgp5": a.n_sim_dgp5, "adaptnull": ADAPT_NULL_N}[kind]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--B", type=int, default=D.DGP5_B)
    ap.add_argument("--n-sim-dgp5", type=int, default=D.DGP5_N_SIM)
    ap.add_argument("--n-cal", type=int, default=D.N_CAL)
    ap.add_argument("--max-seconds", type=float, default=C.DEFAULT_MAX_SECONDS)
    ap.add_argument("--k-batch", default="",
                    help="lote por n, p.ej. 200:1400,500:280 (multiplo de 14); "
                         "por defecto lo fija la sonda de 14 series")
    a = ap.parse_args()
    k_batch = parse_k_batch(a.k_batch)
    if (a.B, a.n_sim_dgp5, a.n_cal) != (D.DGP5_B, D.DGP5_N_SIM, D.N_CAL):
        raise SystemExit("B, N_sim y N_cal estan fijados por la enmienda: %s"
                         % ((D.DGP5_B, D.DGP5_N_SIM, D.N_CAL),))
    cells = parse_cells(a.cells)
    if any(c[0] == "dgp5" for c in cells) and not amendment_committed():
        raise SystemExit("GUARDA: %s no estan commiteadas y sin cambios; no se toca DGP 5."
                         % ", ".join(AMENDMENTS))
    resume = ('python experiments/audit7_dgp5_runner.py --cells "%s" --cores %d --B %d '
              '--n-sim-dgp5 %d --n-cal %d --max-seconds %.0f --k-batch "%s"'
              % (a.cells, a.cores, a.B, a.n_sim_dgp5, a.n_cal, a.max_seconds, a.k_batch))

    manifest = {"cells": {}}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)

    print("=" * 78)
    print("  A7 / Bloque 1 - runner   celdas=%d   cores=%d   B=%d   tope=%.2f h"
          % (len(cells), a.cores, a.B, a.max_seconds / 3600))
    print("=" * 78)
    t_block = time.time()
    warm_pool(a.cores, sorted({c[1] for c in cells}))

    status = 0
    for kind, n, rho, r in cells:
        tag, sb = cell_tag(kind, n, rho, r), cell_seed_base(kind, n, rho, r)
        n_sim = n_sim_for(kind, a)
        print("\n[CELDA] %s  seed_base=%d  N=%d" % (tag, sb, n_sim))
        rec = {"kind": kind, "n": n, "rho": rho, "r": r, "seed_base": sb,
               "n_sim": n_sim, "B": (a.B if kind != "adaptnull" else None),
               "columns": ADAPTNULL_COLUMNS if kind == "adaptnull" else COLUMNS}
        try:
            _, info = C.run_cell_batched(tag, n_sim, make_batch_fn(kind, n, rho, r, sb, a.cores, a.B),
                                         CKPT, a.cores, t_block, a.max_seconds, resume,
                                         k_batch_override=k_batch.get(n))
            rec.update(info)
        except C.BudgetExhausted as exc:
            rec.update({"complete": False, "stopped": str(exc)})
            manifest["cells"][tag] = rec
            print("  [TOPE] %s" % exc)
            status = 2
            break
        manifest["cells"][tag] = rec
        manifest["provenance"] = C.provenance(
            dgp="block1_runner", n_sim=None,
            seed_formula="cal 70*10^8+n_idx*10^5; dgp5 60*10^8+idx*10^5; adaptnull 42+i; desempate [69, seed_base, i]",
            extra_code_files=[WORKER_R])
        C.atomic_write_json(MANIFEST, manifest)
        print("  [COMPLETA] %s en %.0f s" % (tag, info["elapsed_sec"]))

    if status == 0:
        manifest["provenance"] = C.provenance(dgp="block1_runner", n_sim=None,
                                              seed_formula="ver celdas", extra_code_files=[WORKER_R])
        C.atomic_write_json(MANIFEST, manifest)
    print("\n" + "=" * 78)
    print("  bloque: %.2f h   %s" % ((time.time() - t_block) / 3600,
                                    "COMPLETO" if status == 0 else "DETENIDO POR TOPE"))
    if status:
        print("  REANUDAR CON:\n    %s" % resume)
    print("=" * 78)
    return status


if __name__ == "__main__":
    sys.exit(main())
