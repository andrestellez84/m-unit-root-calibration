"""
Auditoria A11 - T3: sesgo del ancla GLS (Observacion 1 / rem:anchorbias del manuscrito v12).

S_theta = audit9_engine.rmgls(Y, n, theta, 1.0, "c"): rutina de produccion
(rm_core.path_statistic, anchor = "gls", R = 0) con sigma^2 = 1 fijo. Paseos
gaussianos de A8 (Y_0 = 0), familia 123, celda t3_n<n>, N = 40 000 por n; los tres
theta sobre las mismas trayectorias. Se reporta media y EE de S_theta^2.

Paso 0: en las 100 primeras trayectorias de cada n, S_0^2 frente a
(n+1)^-1 sum_t (Y_t - beta_GLS)^2 / n (formula de la Observacion), tolerancia 1e-12.

Criterio (protocolo, lectura 6): fila n = 20 000, theta = 0, |media - (1/2 - kappa/n)|
< 3 EE, con kappa = 2|cbar|(1/2 + |cbar|/3) y con el literal 39.67. Numeros del
manuscrito reproducidos si |media - valor impreso| < 3 EE.

Uso: python experiments/audit11_t3_anchor.py --run --cores 14 ; --analyze
Salida: experiments/results/t3_anchor_audit11.json (checkpoints en checkpoints/audit11_t3).
"""
import argparse
import math
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
from stationarity_test.rm_core import gls_mean, CBAR_CONST         # noqa: E402

FAM = C.FAMILY["T3"]
CKPT = os.path.join(C.CKPT_ROOT, "audit11_t3")
OUT = os.path.join(C.RESULTS, "t3_anchor_audit11.json")
CHUNK = 1000
PASO0 = 100
PASO0_TOL = 1e-12
Z_CRIT = 3.0
KAPPA_LITERAL = 39.67
# Cifras impresas en el manuscrito v12 (paper_latex_v12.zip): sec3_theory.tex:65-67 y appA_proofs.tex:77-79.
MANUSCRIPT_SIMULATED = {200: 0.360, 500: 0.438, 2000: 0.481}
MANUSCRIPT_FIRST_ORDER = {200: 0.302, 500: 0.421, 2000: 0.480}
MANUSCRIPT_DECIMALS = 3
MANUSCRIPT_REFS = {"simulated": ["v12/sec3_theory.tex:65-67", "v12/appA_proofs.tex:77-79"],
                   "limit": "E[G_theta(W)] = (1-theta)/2 + theta/3 (encargo A11, T3)"}


def kappa(cbar=CBAR_CONST):
    c = abs(cbar)
    return 2.0 * c * (0.5 + c / 3.0)


def _rows(n, idx):
    out = []
    for i in idx:
        y = D.t3_path(n, i)
        out.append([E.rmgls(y, n, t, 1.0, "c") ** 2 for t in D.T3_THETAS])
    return out


def ckpt_path(n, i0):
    return os.path.join(CKPT, "t3_n%d_i%06d.npz" % (n, i0))


def run(cores, max_seconds):
    t_block = time.time()
    os.makedirs(CKPT, exist_ok=True)
    step = CHUNK * cores
    for n in D.T3_N:
        for i0 in range(0, D.N_T3, step):
            p = ckpt_path(n, i0)
            if os.path.exists(p):
                continue
            if time.time() - t_block > max_seconds:
                raise C.BudgetExhausted("T3: tope antes de n=%d i0=%d. REANUDAR CON: "
                                        "python experiments/audit11_t3_anchor.py --run --cores %d" % (n, i0, cores))
            t0 = time.time()
            idx = list(range(i0, min(i0 + step, D.N_T3)))
            split = [s for s in (idx[j::cores] for j in range(cores)) if s]
            res = Parallel(n_jobs=cores, backend="loky")(delayed(_rows)(n, s) for s in split)
            rows = np.zeros((len(idx), len(D.T3_THETAS)))
            for s, r in zip(split, res):
                rows[np.array(s) - i0] = r
            np.savez(p + ".tmp.npz", rows=rows, i0=i0, step=step, elapsed=time.time() - t0)
            os.replace(p + ".tmp.npz", p)
            print("  n=%d i0=%d  %.1f s" % (n, i0, time.time() - t0), flush=True)


def load(n):
    parts, el, i0 = [], 0.0, 0
    while i0 < D.N_T3:
        with np.load(ckpt_path(n, i0)) as z:
            parts.append(z["rows"])
            el += float(z["elapsed"])
            i0 += z["rows"].shape[0]
    R = np.vstack(parts)
    if R.shape != (D.N_T3, len(D.T3_THETAS)):
        raise KeyError("T3 n=%d: forma %s" % (n, R.shape))
    return R, el


def paso0(n):
    worst = 0.0
    for i in range(PASO0):
        y = D.t3_path(n, i)
        s2 = E.rmgls(y, n, 0.0, 1.0, "c") ** 2
        formula = float(np.sum((y - gls_mean(y)) ** 2) / (n + 1) / n)
        worst = max(worst, abs(s2 - formula))
    return {"paths": PASO0, "max_abs_diff": worst, "tolerance": PASO0_TOL, "passes": worst <= PASO0_TOL}


def limit(theta):
    return (1.0 - theta) / 2.0 + theta / 3.0


def analyze():
    k = kappa()
    cells, elapsed = {}, {}
    for n in D.T3_N:
        R, el = load(n)
        elapsed[str(n)] = el
        by = {}
        for j, th in enumerate(D.T3_THETAS):
            x = R[:, j]
            m, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(x.size))
            L = limit(th)
            by["%g" % th] = {"mean": m, "se": se, "sd": float(x.std(ddof=1)), "N": int(x.size), "limit": L,
                             "limit_minus_kappa_over_n": L - k / n, "limit_minus_literal_over_n": L - KAPPA_LITERAL / n,
                             "z_vs_limit": (m - L) / se, "z_vs_first_order": (m - (L - k / n)) / se,
                             "z_vs_first_order_literal": (m - (L - KAPPA_LITERAL / n)) / se}
        cells[str(n)] = {"n": n, "by_theta": by, "paso0": paso0(n)}
    top = cells[str(max(D.T3_N))]["by_theta"]["0"]
    crit = {"n": max(D.T3_N), "theta": 0.0, "mean": top["mean"], "se": top["se"],
            "target": top["limit_minus_kappa_over_n"], "target_literal": top["limit_minus_literal_over_n"],
            "z": top["z_vs_first_order"], "z_literal": top["z_vs_first_order_literal"],
            "threshold_se": Z_CRIT, "passes": abs(top["z_vs_first_order"]) < Z_CRIT,
            "passes_literal": abs(top["z_vs_first_order_literal"]) < Z_CRIT}
    sim_claims = {}
    for n, v in MANUSCRIPT_SIMULATED.items():
        r = cells[str(n)]["by_theta"]["0"]
        z = (r["mean"] - v) / r["se"]
        sim_claims[str(n)] = {"printed": v, "mean": r["mean"], "se": r["se"], "z": z, "reproduced": abs(z) < Z_CRIT,
                              "rounds_to_printed": round(r["mean"], MANUSCRIPT_DECIMALS) == v}
    fo_claims = {}
    for n, v in MANUSCRIPT_FIRST_ORDER.items():
        val = 0.5 - k / n
        fo_claims[str(n)] = {"printed": v, "value": val, "value_literal": 0.5 - KAPPA_LITERAL / n,
                             "rounds_to_printed": round(val, MANUSCRIPT_DECIMALS) == v}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"N": D.N_T3, "n": list(D.T3_N), "thetas": list(D.T3_THETAS), "sigma_sq": 1.0, "case": "c",
                      "anchor": "gls", "cbar": CBAR_CONST, "kappa": k, "kappa_literal": KAPPA_LITERAL,
                      "z_threshold": Z_CRIT, "statistic": "audit9_engine.rmgls(Y, n, theta, 1.0, 'c') ** 2",
                      "paths": "audit8_design.gauss_rw (Y_0 = 0), familia 123, celda t3_n<n>",
                      "tau_1": {str(n): {"%g" % t: E.taus(t, n)[0] for t in D.T3_THETAS} for n in D.T3_N},
                      "manuscript_refs": MANUSCRIPT_REFS},
           "cells": cells, "criterion_n20000_theta0": crit, "manuscript_simulated": sim_claims,
           "manuscript_first_order": fo_claims,
           "paso0_all_pass": all(c["paso0"]["passes"] for c in cells.values()),
           "compute_elapsed_sec_by_n": elapsed}
    C.write_result(OUT, out, __file__)
    for n in D.T3_N:
        print(n, {t: (round(v["mean"], 5), round(v["se"], 5), round(v["z_vs_first_order"], 2))
                  for t, v in cells[str(n)]["by_theta"].items()})
    print("criterio", crit)
    print("manuscrito", sim_claims)
    print("primer orden", fo_claims)
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
