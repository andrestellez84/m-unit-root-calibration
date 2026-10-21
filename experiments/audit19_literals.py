"""
Auditoria A19 - punto 4 (protocol_audit19.md, L4): valores de las cifras nuevas del v25 para el reporte.

Remark 1 / Apendice A.4 (cbar = -7, Y_0 = 0, sigma = 1): kappa, lambda, E[S^2] exacto con los momentos de A.4, la expansion
1/2 - kappa/m + lambda/m^2 (m = n + cbar^2) y su distancia al momento exacto, y el primer orden 1/2 - kappa/n.
Apendice A.5: maxima diferencia entre la identidad 2(C(0) - C(B+1))/(B+1) y hac_newey_west en B = 0, 3, 7, 20, n - 1.
La comprobacion independiente es tests/test_literals_v25_audit19.py. Salida: experiments/results/literals_v25_audit19.json.
"""
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(os.path.dirname(HERE), "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import audit19_common as C                                         # noqa: E402
from stationarity_test.hac_estimator import hac_newey_west         # noqa: E402

OUT = os.path.join(C.RESULTS, "literals_v25_audit19.json")
CBAR = -7
NS = (200, 500, 1000, 2000)
BOUND = Fraction(48, 10 ** 7)
TEXT = {"lambda": "1225", "kappa": "39.7", "exact": {"200": "0.360", "500": "0.432", "2000": "0.481"},
        "first_order": {"200": "0.302", "500": "0.421", "2000": "0.480"}, "bound": "4.8e-6"}
SEED = 19          # semilla fija de las series de la identidad (no es una familia de resultados)


def moment(n, c):
    a, D = abs(c), n + c * c
    eyny, eyy, eyn2 = Fraction(n - 1, 2), Fraction((n - 1) * (2 * n - 1), 6 * n), Fraction(n)
    cross = Fraction(a, D) * (n * eyny + eyn2 + a * n * eyy + a * eyny)
    square = Fraction(a * a, D * D) * (eyn2 + 2 * a * eyny + a * a * eyy)
    return Fraction(1, 2) - 2 * cross / (n * (n + 1)) + square / n


def identity_gap(n=200):
    rng = np.random.default_rng(SEED)
    out = {}
    for kind in ("iid", "ar05", "ma_m08"):
        e = rng.standard_normal(n + 1)
        if kind == "iid":
            dx = e[1:]
        elif kind == "ar05":
            dx = np.empty(n)
            prev = 0.0
            for i in range(n):
                prev = 0.5 * prev + e[i + 1]
                dx[i] = prev
        else:
            dx = e[1:] - 0.8 * e[:-1]
        x = np.concatenate([[0.0], np.cumsum(dx)])
        s = x - np.arange(n + 1) / n * x[n]
        gaps = {}
        for B in (0, 3, 7, 20, n - 1):
            c0 = float(np.dot(s, s)) / n
            ck = float(np.dot(s[:n - B], s[B + 1:])) / n
            gaps[str(B)] = abs(2.0 * (c0 - ck) / (B + 1) - hac_newey_west(dx, bandwidth=B))
        out[kind] = gaps
    return out


def main():
    a = abs(CBAR)
    kap = 2 * a * (Fraction(1, 2) + Fraction(a, 3))
    lam = Fraction(CBAR ** 2 * (CBAR ** 2 + 3 * a + 5), 3)
    rows = {}
    for n in NS:
        e = moment(n, CBAR)
        m = n + CBAR ** 2
        approx = Fraction(1, 2) - kap / m + lam / (m * m)
        rows[str(n)] = {"exact": float(e), "exact_6": "%.6f" % float(e), "exact_3": "%.3f" % float(e),
                        "expansion": float(approx), "abs_gap": float(abs(approx - e)), "within_bound": abs(approx - e) <= BOUND,
                        "first_order": float(Fraction(1, 2) - kap / n), "first_order_3": "%.3f" % float(Fraction(1, 2) - kap / n)}
    gaps = identity_gap()
    max_gap = max(v for g in gaps.values() for v in g.values())
    checks = {"lambda": lam == 1225, "kappa": "%.1f" % float(kap) == TEXT["kappa"],
              "exact": all(rows[n]["exact_3"] == v for n, v in TEXT["exact"].items()),
              "first_order": all(rows[n]["first_order_3"] == v for n, v in TEXT["first_order"].items()),
              "bound": all(r["within_bound"] for r in rows.values()), "identity": max_gap <= 1e-12}
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit19.md, L4", "cbar": CBAR,
           "kappa": float(kap), "kappa_fraction": str(kap), "lambda": int(lam), "text_v25": TEXT, "by_n": rows,
           "max_abs_gap_expansion": max(r["abs_gap"] for r in rows.values()), "bound": float(BOUND),
           "identity": {"n": 200, "seed": SEED, "bandwidths": [0, 3, 7, 20, 199], "abs_gap": gaps, "max_abs_gap": max_gap,
                        "tolerance": 1e-12},
           "checks": checks, "all_hold": all(checks.values())}
    C.write_result(OUT, out, __file__)
    print({k: (v["exact_6"], "%.2e" % v["abs_gap"]) for k, v in rows.items()}, "| identidad max", "%.1e" % max_gap, "|", checks)
    return 0 if out["all_hold"] else 1


if __name__ == "__main__":
    sys.exit(main())
