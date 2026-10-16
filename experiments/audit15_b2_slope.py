"""
Auditoria A15 - B15.2: pendientes (protocol_audit15.md, lecturas 2.1 y 2.2).

(a) sha256 en disco y commiteado de audit5_tarea5.py y audit4_tarea_E.py frente a los que
registro A14 (b2_sources_audit14.json).
(b) Replica de audit4_tarea_E.py sin editarlo: default_rng(42), procesos RW, AR 0.95 y AR 0.5 en
ese orden, n in {200, 500, 1000, 2000, 5000}, 500 replicas y la misma secuencia de extracciones.
En cada camino, B antes del techo con dos rho-hat: el del script (np.var ddof = 0 y np.cov ddof
= 1 con medias separadas) y el de la libreria (hac_newey_west: serie centrada con la media
completa, gamma0 y gamma1 con divisor n). Paso 0: el rho-hat del script reproduce las columnas
de resultados_auditoria_4_E.md a los 4 decimales publicados.

Salida: experiments/results/e4_slope_audit15.json.
"""
import os
import sys
import time

import numpy as np
from scipy.stats import linregress

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k   # noqa: E402
from stationarity_test.hac_estimator import hac_newey_west          # noqa: E402

OUT = os.path.join(C.RESULTS, "e4_slope_audit15.json")
MD = "experiments/results/resultados_auditoria_4_E.md"
SCRIPTS = {"i": "experiments/audit5_tarea5.py", "iv": "experiments/audit4_tarea_E.py"}
N_GRID = (200, 500, 1000, 2000, 5000)
RHOS = (("RW", 1.0), ("AR 0.95", 0.95), ("AR 0.5", 0.5))
REPS = 500
SEED = 42
BW_CONST = 1.1447                  # constante de Andrews (1991) para Bartlett, la del script
CLIP = 0.99                        # recorte de rho-hat del script y de la libreria
FLOOR = 10 ** -10                  # piso del denominador de alpha-hat en el script
THETA = (0.1, 0.1)                 # ventanas del script (theta_1, theta_2)
SMALL = 10 ** -15


def generate_ar1(n, rho, rng):
    """Copia literal del generador de audit4_tarea_E.py (misma secuencia de extracciones)."""
    eps = rng.standard_normal(n)
    Y = np.zeros(n + 1)
    for t in range(n):
        Y[t + 1] = rho * Y[t] + eps[t]
    return Y


def rho_script(diffs):
    gamma_0 = np.var(diffs)
    gamma_1 = np.cov(diffs[:-1], diffs[1:])[0, 1] if gamma_0 > 0 else 0.0
    r = gamma_1 / gamma_0 if gamma_0 > 0 else 0.0
    return float(np.clip(r, -CLIP, CLIP))


def rho_library(diffs):
    x = np.asarray(diffs, dtype=np.float64)
    n = len(x)
    xc = x - np.mean(x)
    g0 = float(np.dot(xc, xc) / n)
    if g0 < SMALL:
        return 0.0
    g1 = float(np.dot(xc[1:], xc[:n - 1]) / n)
    return float(np.clip(g1 / g0, -CLIP, CLIP))


def b_pre(r, n):
    a = (4.0 * r ** 2) / max((1.0 - r ** 2) ** 2, FLOOR)
    return BW_CONST * (a * n) ** (1.0 / 3.0)


def md_table():
    with open(os.path.join(C.REPO, MD), encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip().startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    return {c[0]: dict(zip(head, c)) for c in ([x.strip() for x in l.strip("|").split("|")] for l in lines[2:])}


def slope(ns, v):
    s, _, r, _, _ = linregress(np.log(ns), np.log(v))
    return float(s), float(r ** 2)


def main():
    t0 = time.time()
    a14 = C.read_json("b2_sources_audit14.json")["figures"]
    scripts = {}
    for k, p in SCRIPTS.items():
        full = os.path.join(C.REPO, p)
        blob = C.C14.C13.C10.C9.C8.git_blob_sha256(p)
        scripts[k] = {"path": p, "sha256_a14": a14[k]["script"]["sha256"], "sha256_disk": C.sha256_file(full),
                      "sha256_committed": blob, "last_commit": C.last_commit(p)}
        scripts[k]["matches"] = scripts[k]["sha256_a14"] == scripts[k]["sha256_disk"] == scripts[k]["sha256_committed"]
    rng = np.random.default_rng(SEED)
    md = md_table()
    res, paso0 = {}, []
    for label, rho in RHOS:
        acc = {n: {"B_pre_script": [], "B_ceil_script": [], "B_pre_lib": [], "B_ceil_lib": [], "g1s": [], "g2s": [],
                   "rho_script": [], "rho_lib": []} for n in N_GRID}
        for n in N_GRID:
            tau_1 = max(2, int(round(THETA[0] * n)))
            tau_2 = max(2, int(round(THETA[1] * n)))
            for _ in range(REPS):
                Y = generate_ar1(n, rho, rng)
                diffs = np.diff(Y)
                rs, rl = rho_script(diffs), rho_library(diffs)
                bs, bl = b_pre(rs, len(diffs)), b_pre(rl, len(diffs))
                s2 = hac_newey_west(diffs)
                g1_raw = float(np.sqrt(max(sample_variance_over_k(rolling_mean(Y, tau_1)), 0.0)))
                g2_raw = float(np.sqrt(max(sample_variance_over_k(rolling_var(Y, tau_2)), 0.0)))
                a = acc[n]
                a["B_pre_script"].append(bs)
                a["B_ceil_script"].append(np.ceil(bs))
                a["B_pre_lib"].append(bl)
                a["B_ceil_lib"].append(np.ceil(bl))
                a["g1s"].append(g1_raw / (np.sqrt(s2) * n ** 0.5))
                a["g2s"].append(g2_raw / (s2 * n ** 1.0))
                a["rho_script"].append(rs)
                a["rho_lib"].append(rl)
        means = {q: [float(np.mean(acc[n][q])) for n in N_GRID] for q in acc[N_GRID[0]]}
        rec = {"means_by_n": {q: dict(zip(map(str, N_GRID), v)) for q, v in means.items()},
               "max_abs_rho_diff": max(float(np.max(np.abs(np.array(acc[n]["rho_script"]) - np.array(acc[n]["rho_lib"])))) for n in N_GRID)}
        for q in ("B_pre_script", "B_ceil_script", "B_pre_lib", "B_ceil_lib", "g1s", "g2s"):
            rec["slope_" + q], rec["R2_" + q] = slope(N_GRID, means[q])
        rec["slope_diff_B_pre"] = rec["slope_B_pre_lib"] - rec["slope_B_pre_script"]
        rec["slope_diff_B_ceil"] = rec["slope_B_ceil_lib"] - rec["slope_B_ceil_script"]
        true_d = 0.0 if rho == 1.0 else -(1 - rho) / 2.0
        rec["alpha_teo"] = (4.0 * true_d ** 2) / ((1.0 - true_d ** 2) ** 2)
        res[label] = rec
        row = md[label]
        comp = {"alpha_teo": ("alpha_teo", False), "slope_B_pre": ("slope_B_pre_script", True), "R2_B_pre": ("R2_B_pre_script", True),
                "slope_B_ceil": ("slope_B_ceil_script", True), "R2_B_ceil": ("R2_B_ceil_script", True),
                "slope_g1_std": ("slope_g1s", False), "slope_g2_std": ("slope_g2s", False)}
        for col, (key, used) in comp.items():
            mine = "%.4f" % rec[key]
            paso0.append({"process": label, "column": col, "used": used, "published": row[col], "recomputed": mine,
                          "recomputed_full": rec[key], "equal_at_4_decimals": mine == row[col]})
    out = {"provenance": C.provenance(__file__, seed_family=None, seed=SEED),
           "reading": "protocol_audit15.md, lecturas 2.1 y 2.2", "a_scripts": scripts,
           "a_all_match": all(s["matches"] for s in scripts.values()),
           "config": {"seed": SEED, "reps": REPS, "n_grid": list(N_GRID), "processes": [r[0] for r in RHOS], "aggregation": "media",
                      "rho_script": "np.var(diffs) (ddof = 0) y np.cov(diffs[:-1], diffs[1:])[0, 1] (ddof = 1, medias separadas)",
                      "rho_library": "hac_newey_west: serie centrada con la media completa; gamma0 y gamma1 con divisor n",
                      "assignment_says": "np.var y np.cov con ddof = 1"},
           "b": res, "paso0": {"rows": paso0, "used_all_equal": all(r["equal_at_4_decimals"] for r in paso0 if r["used"]),
                               "other_all_equal": all(r["equal_at_4_decimals"] for r in paso0 if not r["used"]),
                               "precision": "4 decimales (la del archivo publicado)"},
           "elapsed_sec": time.time() - t0}
    C.write_result(OUT, out, __file__)
    print("(a) sha256 coinciden:", out["a_all_match"])
    print("Paso 0: usadas", out["paso0"]["used_all_equal"], "resto", out["paso0"]["other_all_equal"])
    for r in paso0:
        if not r["equal_at_4_decimals"]:
            print("   DIFIERE", r)
    for label, rec in res.items():
        print("%-8s pendiente B_pre script %.6f lib %.6f |D| %.2e ; B_ceil script %.6f lib %.6f ; max|D rho| %.2e" % (
            label, rec["slope_B_pre_script"], rec["slope_B_pre_lib"], abs(rec["slope_diff_B_pre"]), rec["slope_B_ceil_script"],
            rec["slope_B_ceil_lib"], rec["max_abs_rho_diff"]))
    print("%.1f s" % out["elapsed_sec"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
