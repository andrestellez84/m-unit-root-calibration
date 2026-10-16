"""
Auditoria A11 - T4: consistencia con tendencia (evidencia numerica para la Seccion 3).

DGP: Y_t = 1 + 0.1 t + x_t, t = 0..n, x_t AR(rho) estacionario (x_0 de la ley
estacionaria), rho in {0.5, 0.9}, n in {200, 500, 1000, 2000, 5000}, 2000 replicas,
familia 124, celda t4_rho<rho>_n<n>. Por replica (protocolo, lectura 7):
  A = n^-1 sum_{t=0}^{n} u_t^2, u = detrend_qd(Y) (cbar = -13.5);
  B = sigma_hat^2_HAC = rm_core.hac_sigma_sq(Y) (rutina de produccion);
  S = RM-GLS con theta = 0.02, caso con tendencia, con sigma_hat_HAC.
Medianas por (rho, n); pendiente log-log por MCO de log(mediana) sobre log n; IC
95% bootstrap percentil (2000 remuestras de replicas dentro de cada n; semilla de la
celda t4boot_rho<rho>). "Acotado" (lectura operativa): limite superior del IC de la
pendiente de A < 0.5. Solo reporta.

Uso: python experiments/audit11_t4_trend.py --run --cores 14 ; --analyze
Salida: experiments/results/t4_trend_audit11.json (checkpoints en checkpoints/audit11_t4).
"""
import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402
import audit11_design as D                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
from stationarity_test.deterministics import detrend_qd, CBAR_TREND  # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["T4"]
CKPT = os.path.join(C.CKPT_ROOT, "audit11_t4")
OUT = os.path.join(C.RESULTS, "t4_trend_audit11.json")
QUANTITIES = ("resid_ms", "sigma2_hac", "statistic")
BOUNDED_SLOPE_UPPER = 0.5
CI_LEVEL = 0.95


def _rows(rho, n, idx):
    out = []
    for i in idx:
        y = D.t4_path(rho, n, i)
        u = detrend_qd(y, CBAR_TREND)
        s2 = hac_sigma_sq(y)
        out.append([float(np.sum(u * u) / n), s2, E.rmgls(y, n, D.T4_THETA, s2, "ct")])
    return out


def ckpt_path(rho, n):
    return os.path.join(CKPT, "t4_rho%s_n%d.npz" % (D.rho_tag(rho), n))


def run(cores, max_seconds):
    t_block = time.time()
    os.makedirs(CKPT, exist_ok=True)
    for rho in D.T4_RHO:
        for n in D.T4_N:
            p = ckpt_path(rho, n)
            if os.path.exists(p):
                continue
            if time.time() - t_block > max_seconds:
                raise C.BudgetExhausted("T4: tope antes de rho=%g n=%d. REANUDAR CON: "
                                        "python experiments/audit11_t4_trend.py --run --cores %d" % (rho, n, cores))
            t0 = time.time()
            idx = list(range(D.N_T4))
            split = [idx[j::cores] for j in range(cores)]
            res = Parallel(n_jobs=cores, backend="loky")(delayed(_rows)(rho, n, s) for s in split)
            rows = np.zeros((D.N_T4, len(QUANTITIES)))
            for s, r in zip(split, res):
                rows[np.array(s)] = r
            np.savez(p + ".tmp.npz", rows=rows, elapsed=time.time() - t0)
            os.replace(p + ".tmp.npz", p)
            print("  rho=%g n=%d  %.1f s" % (rho, n, time.time() - t0), flush=True)


def slope(ns, med):
    X = np.log(np.asarray(ns, dtype=float))
    Y = np.log(np.asarray(med, dtype=float))
    b = np.polyfit(X, Y, 1)
    return float(b[0])


def analyze():
    res, elapsed = {}, {}
    for rho in D.T4_RHO:
        R = {}
        for n in D.T4_N:
            with np.load(ckpt_path(rho, n)) as z:
                R[n] = z["rows"]
                elapsed["%g|%d" % (rho, n)] = float(z["elapsed"])
        rng = D.t4_boot_rng(rho)
        boot = np.zeros((D.T4_BOOT, len(QUANTITIES)))
        for b in range(D.T4_BOOT):
            meds = {n: np.median(R[n][rng.integers(0, D.N_T4, D.N_T4)], axis=0) for n in D.T4_N}
            for j in range(len(QUANTITIES)):
                boot[b, j] = slope(D.T4_N, [meds[n][j] for n in D.T4_N])
        lo, hi = (1.0 - CI_LEVEL) / 2.0, 1.0 - (1.0 - CI_LEVEL) / 2.0
        by_q = {}
        for j, q in enumerate(QUANTITIES):
            med = {str(n): float(np.median(R[n][:, j])) for n in D.T4_N}
            nan = {str(n): int(np.sum(~np.isfinite(R[n][:, j]))) for n in D.T4_N}
            s = slope(D.T4_N, [med[str(n)] for n in D.T4_N])
            ci = [float(np.quantile(boot[:, j], lo)), float(np.quantile(boot[:, j], hi))]
            by_q[q] = {"median": med, "nan": nan, "slope": s, "slope_ci95": ci, "slope_boot_se": float(boot[:, j].std(ddof=1)),
                       "ci_contains_zero": ci[0] <= 0.0 <= ci[1],
                       "ratio_last_first": med[str(max(D.T4_N))] / med[str(min(D.T4_N))]}
        by_q["resid_ms"]["bounded"] = by_q["resid_ms"]["slope_ci95"][1] < BOUNDED_SLOPE_UPPER
        res["%g" % rho] = {"rho": rho, "stationary_variance": 1.0 / (1.0 - rho * rho), "quantities": by_q}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"N": D.N_T4, "n": list(D.T4_N), "rho": list(D.T4_RHO), "intercept": D.T4_INTERCEPT,
                      "trend_slope": D.T4_SLOPE, "theta": D.T4_THETA, "cbar_qd": CBAR_TREND, "bootstrap_B": D.T4_BOOT,
                      "ci_level": CI_LEVEL, "bounded_rule": "limite superior del IC de la pendiente de resid_ms < %g" % BOUNDED_SLOPE_UPPER,
                      "bounded_slope_upper": BOUNDED_SLOPE_UPPER,
                      "quantities": {"resid_ms": "n^-1 sum_{t=0}^{n} u_t^2, u = detrend_qd(Y) (cbar = -13.5)",
                                     "sigma2_hac": "rm_core.hac_sigma_sq(Y)",
                                     "statistic": "audit9_engine.rmgls(Y, n, 0.02, sigma2_hac, 'ct')"},
                      "paths": "audit11_design.t4_path, familia 124, celda t4_rho<rho>_n<n>; bootstrap: celda t4boot_rho<rho>"},
           "by_rho": res, "compute_elapsed_sec": elapsed}
    C.write_result(OUT, out, __file__)
    for rho, v in res.items():
        for q, w in v["quantities"].items():
            print(rho, q, {k: round(x, 4) for k, x in w["median"].items()}, "pendiente %.3f IC %s" % (w["slope"], [round(c, 3) for c in w["slope_ci95"]]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    if a.run:
        try:
            run(a.cores, a.max_seconds)
        except C.BudgetExhausted as exc:
            print("[TOPE] %s" % exc, flush=True)
            return 2
    if a.analyze:
        return analyze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
