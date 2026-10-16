"""
Auditoria A12 - B12.F: E[S0^2] exacto con sigma conocido (sin simulacion; familia 135 sin trayectorias).

S0^2 = (n+1)^-1 sum_{t=0}^{n} (Y_t - beta_GLS)^2 / n, Y paseo aleatorio gaussiano con
Y_0 = 0 (Sigma_st = min(s, t)), beta_GLS = w'Y con w el mapa lineal de
rm_core.gls_mean (cbar = -7, a = 1 + cbar/n). Con M = I - 1 w':
    E[u'u] = tr(M Sigma M') = tr Sigma - 2 1' Sigma w + (n+1) w' Sigma w,
con Sigma w por sumas acumuladas (O(n)). Control: tr(M Sigma M') denso en n <= 5000.

Contrasta la hipotesis E[S0^2] ~ 1/2 - kappa/(n + cbar^2) + lambda/(n + cbar^2)^2 y las
medias simuladas de t3_anchor_audit11.json (theta = 0). Compuerta INFORMATIVA:
|formula - exacta| < 0.002 para n >= 200. Compatibilidad: |media - exacta| < 3 EE.

Salida: experiments/results/bF_anchor_audit12.json.
"""
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
from stationarity_test.rm_core import CBAR_CONST                   # noqa: E402

OUT = os.path.join(C.RESULTS, "bF_anchor_audit12.json")
NS = (60, 100, 200, 500, 1000, 2000, 5000, 20000)
DENSE_MAX = 5000
GATE_TOL = 0.002
GATE_N_MIN = 200
Z_CRIT = 3.0


def anchor_weights(n, cbar=CBAR_CONST):
    """w con beta_GLS = w'Y para Y de longitud n + 1 (rm_core.gls_mean)."""
    a = 1.0 + cbar / n
    z = np.full(n + 1, 1.0 - a)
    z[0] = 1.0
    zz = float(z @ z)
    w = np.empty(n + 1)
    w[:n] = (z[:n] - a * z[1:]) / zz      # Y_t entra en yq_t (peso z_t) y en yq_{t+1} (peso -a z_{t+1})
    w[n] = z[n] / zz
    return w


def sigma_times(v):
    """(Sigma v)_s = sum_t min(s, t) v_t, s, t = 0..n (O(n))."""
    n1 = len(v)
    t = np.arange(n1, dtype=np.float64)
    tail = np.cumsum(v[::-1])[::-1]                    # sum_{t >= s} v_t
    head = np.concatenate([[0.0], np.cumsum(t * v)[:-1]])  # sum_{t < s} t v_t
    return head + t * tail


def exact_fast(n):
    w = anchor_weights(n)
    one = np.ones(n + 1)
    tr = float(np.arange(n + 1, dtype=np.float64).sum())
    sw = sigma_times(w)
    euu = tr - 2.0 * float(one @ sw) + (n + 1) * float(w @ sw)
    return euu / (n * (n + 1))


def exact_dense(n):
    w = anchor_weights(n)
    t = np.arange(n + 1, dtype=np.float64)
    S = np.minimum.outer(t, t)
    M = np.eye(n + 1) - np.outer(np.ones(n + 1), w)
    return float(np.trace(M @ S @ M.T)) / (n * (n + 1))


def kappa(cbar=CBAR_CONST):
    c = abs(cbar)
    return 2.0 * c * (0.5 + c / 3.0)


def lam(cbar=CBAR_CONST):
    c = abs(cbar)
    return c * c * (1.0 + c + c * c / 3.0)


def formula(n, cbar=CBAR_CONST):
    m = n + cbar * cbar
    return 0.5 - kappa(cbar) / m + lam(cbar) / m ** 2


def main():
    t0 = time.time()
    t3 = C.read_json("t3_anchor_audit11.json")
    rows = {}
    for n in NS:
        ex = exact_fast(n)
        dense = exact_dense(n) if n <= DENSE_MAX else None
        fo = formula(n)
        first = 0.5 - kappa() / n
        r = {"n": n, "exact": ex, "exact_dense": dense, "dense_minus_fast": (dense - ex) if dense is not None else None,
             "formula": fo, "formula_minus_exact": fo - ex, "first_order_A11": first, "first_order_minus_exact": first - ex}
        cell = t3["cells"].get(str(n))
        if cell is not None:
            s = cell["by_theta"]["0"]
            r["sim_A11"] = {"mean": s["mean"], "se": s["se"], "N": s["N"], "z_vs_exact": (s["mean"] - ex) / s["se"],
                            "compatible": abs((s["mean"] - ex) / s["se"]) < Z_CRIT,
                            "source": "t3_anchor_audit11.json cells.%d.by_theta.0" % n}
        rows[str(n)] = r
    gate_ns = [n for n in NS if n >= GATE_N_MIN]
    worst = max(abs(rows[str(n)]["formula_minus_exact"]) for n in gate_ns)
    dense_worst = max(abs(r["dense_minus_fast"]) for r in rows.values() if r["dense_minus_fast"] is not None)
    top = rows[str(max(NS))]
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["F"]),
           "config": {"cbar": CBAR_CONST, "kappa": kappa(), "lambda": lam(), "sigma": 1.0, "n": list(NS),
                      "dense_max_n": DENSE_MAX, "gate_tol": GATE_TOL, "gate_n_min": GATE_N_MIN, "z_threshold": Z_CRIT,
                      "method": "E[u'u] = tr Sigma - 2 1'Sigma w + (n+1) w'Sigma w; control denso tr(M Sigma M')"},
           "rows": rows, "dense_vs_fast_max_abs": dense_worst,
           "gate": {"rule": "|formula - exacta| < %g para n >= %d" % (GATE_TOL, GATE_N_MIN), "worst": worst,
                    "passes": worst < GATE_TOL},
           "a11_anomaly_n20000": {"mean": top["sim_A11"]["mean"], "se": top["sim_A11"]["se"], "exact": top["exact"],
                                  "z": top["sim_A11"]["z_vs_exact"], "compatible": top["sim_A11"]["compatible"]},
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for n in NS:
        r = rows[str(n)]
        print(n, "exacta %.6f formula %.6f dif %.2e" % (r["exact"], r["formula"], r["formula_minus_exact"]),
              "" if "sim_A11" not in r else "sim %.5f z %.2f" % (r["sim_A11"]["mean"], r["sim_A11"]["z_vs_exact"]))
    print("compuerta", out["gate"], "denso-rapido", dense_worst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
