"""
Auditoria A17 - B17.1 (enmienda 7, lectura E7.1): eq:mstats del v18, evaluacion literal frente a np_statistics.

Implementacion propia (no usa audit8_unitroot para el calculo literal) de lo que dicen sec2_statistics.tex del v18:
GLS con T_n = T = n + 1; regresion sin intercepto de Delta u_t sobre u_{t-1} y Delta u_{t-1..t-k} en t = kmax+1..n;
sigma2_k = SSR/(n - kmax); kmax = floor(12 (T/100)^(1/4)); s2_AR = sigma2_k/(1 - sum b_j)^2; MSB y MZ_alpha con
T^-2 sum_{t=1}^{n} u_{t-1}^2 y T^-1 u_n^2; k del codigo. Caminos de E6.4 (familia 160, mismas claves).
Criterio: |Delta| relativo <= 1e-12 en MSB y absoluto <= 1e-10 en MZ_t. Variantes de un solo cambio (diagnostico).
Descripcion: kmax del texto = del codigo; la MAIC del texto elige el k del codigo; t de DF-GLS por MCO propio en
t = k+1..n frente a arch.DFGLS.
Salida: experiments/results/mstats_v18_audit17.json.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit17_common as C                                         # noqa: E402
import audit16_code_check as K                                     # noqa: E402
import audit8_unitroot as U                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "mstats_v18_audit17.json")
CBAR = {"c": -7, "ct": -13.5}
KMAX_C, KMAX_BASE, KMAX_POW = 12, 100, 4          # kmax = floor(12 (T/100)^(1/4)), texto del v18
TOL_MSB_REL = 10 ** -12
TOL_MZT_ABS = 10 ** -10
TOL_DF_REL = 10 ** -10
VARIANTS = ("text", "norm_n", "sample_k1", "sum_t0_n", "divisor_dof")


def gls(y, case, Tn):
    n1 = len(y)
    t = np.arange(n1, dtype=np.float64)                 # t = 0..n, como en el texto (d_t = (1, t)')
    D = np.ones((n1, 1)) if case == "c" else np.column_stack([np.ones(n1), t])
    a = 1 + CBAR[case] / Tn
    yq, Dq = y.copy(), D.copy()
    yq[1:] = y[1:] - a * y[:-1]
    Dq[1:] = D[1:] - a * D[:-1]
    beta = np.linalg.lstsq(Dq, yq, rcond=None)[0]
    return y - D @ beta


def adf_reg(u, k, t0, n):
    """Delta u_t sobre u_{t-1}, Delta u_{t-1..t-k}, t = t0..n (indices del texto: u_0..u_n). Sin intercepto."""
    du = np.diff(u)                                     # du[t-1] = Delta u_t, t = 1..n
    ts = np.arange(t0, n + 1)
    X = np.column_stack([u[ts - 1]] + [du[ts - 1 - j] for j in range(1, k + 1)])
    yv = du[ts - 1]
    b, *_ = np.linalg.lstsq(X, yv, rcond=None)
    r = yv - X @ b
    return b, float(r @ r), X, len(ts)


def literal(y, case, k, variant="text"):
    n = len(y) - 1
    T = n + 1
    u = gls(y, case, T)
    kmax = int(math.floor(KMAX_C * (T / KMAX_BASE) ** (1 / KMAX_POW)))
    t0 = k + 1 if variant == "sample_k1" else kmax + 1
    b, ssr, X, N = adf_reg(u, k, t0, n)
    div = N - (k + 1) if variant == "divisor_dof" else (n - kmax if variant != "sample_k1" else N)
    s2 = (ssr / div) / (1 - b[1:].sum()) ** 2
    norm = n if variant == "norm_n" else T
    S = (u[0:n] @ u[0:n]) if variant != "sum_t0_n" else (u @ u)
    S = S / norm ** 2
    mza = (u[n] ** 2 / norm - s2) / (2 * S)
    msb = math.sqrt(S / s2)
    return {"MSB": msb, "MZt": mza * msb, "kmax": kmax, "u": u}


def maic_text(u, n, kmax):
    vals = []
    for k in range(kmax + 1):
        b, ssr, X, N = adf_reg(u, k, kmax + 1, n)
        s2k = ssr / (n - kmax)
        tau = b[0] ** 2 * float(X[:, 0] @ X[:, 0]) / s2k
        vals.append(math.log(s2k) + 2 * (tau + k) / (n - kmax))
    return int(np.argmin(vals))


def dfgls_text(u, n, k):
    b, ssr, X, N = adf_reg(u, k, k + 1, n)
    s2 = ssr / (N - X.shape[1])
    cov = s2 * np.linalg.inv(X.T @ X)
    return b[0] / math.sqrt(cov[0, 0])


def main():
    v18 = C.v18()
    keys, coll, distinct = K.seeds()
    cells = {}
    for ci, (n, case) in enumerate([(n, c) for n in K.NS for c in K.CASES]):
        rng = np.random.default_rng(np.random.SeedSequence(K.FAM, spawn_key=keys[ci]))
        acc = {v: {"msb_rel": 0.0, "mzt_abs": 0.0} for v in VARIANTS}
        kmax_bad, maic_bad, df_rel, df_rel_n = 0, 0, 0.0, 0.0
        for _ in range(K.PATHS):
            y = np.concatenate([[0.0], np.cumsum(rng.standard_normal(n))])
            base = U.np_statistics(y, case)
            for v in VARIANTS:
                lt = literal(y, case, base["k"], v)
                acc[v]["msb_rel"] = max(acc[v]["msb_rel"], abs(lt["MSB"] / base["MSB"] - 1))
                acc[v]["mzt_abs"] = max(acc[v]["mzt_abs"], abs(lt["MZt"] - base["MZt"]))
                if v == "text":
                    kmax_bad += lt["kmax"] != base["kmax"]
                    maic_bad += maic_text(lt["u"], n, lt["kmax"]) != base["k"]
                    tdf = dfgls_text(lt["u"], n, base["k"])
                    tarch = U.dfgls_maic(y, case, base["k"])[0]
                    df_rel = max(df_rel, abs(tdf / tarch - 1))
        cells["n%d_%s" % (n, case)] = {"paths": K.PATHS, "variants": acc, "kmax_disagreements": kmax_bad, "maic_disagreements": maic_bad,
                                       "dfgls_max_rel": df_rel,
                                       "passes": acc["text"]["msb_rel"] <= TOL_MSB_REL and acc["text"]["mzt_abs"] <= TOL_MZT_ABS}
        print(n, case, {v: ("%.1e" % a["msb_rel"], "%.1e" % a["mzt_abs"]) for v, a in acc.items()}, kmax_bad, maic_bad, "%.1e" % df_rel)
    text = v18.files["sec2_statistics.tex"]
    lines = {lab: next(i + 1 for i, l in enumerate(text.splitlines()) if s in l) for lab, s in (
        ("eq_msb", "\\mathrm{MSB} = "), ("eq_mza", "\\mathrm{MZ}_\\alpha = "), ("T", "with $T = n + 1$"), ("common", "common sample"),
        ("kmax", "k_{\\max} = \\lfloor 12"), ("dfgls", "estimated over $t = k+1"), ("Tn", "$T_n = T = n + 1$"))}
    out = {"provenance": C.provenance(__file__, seed_family=K.FAM), "reading": "enmienda 7, lectura E7.1",
           "inputs": {"v18_zip_sha256": v18.sha256}, "paths_as": "E6.4 (audit16_code_check: familia 160, mismas claves)",
           "seed_collisions_vs_prior": coll, "criteria": {"msb_rel": TOL_MSB_REL, "mzt_abs": TOL_MZT_ABS, "dfgls_rel": TOL_DF_REL},
           "variants_meaning": {"text": "literal del v18", "norm_n": "normalizacion por n en lugar de T", "sample_k1": "regresion de s2 en t = k+1..n",
                                "sum_t0_n": "suma de u_t^2 en t = 0..n", "divisor_dof": "sigma2 = SSR/(N - k - 1)"},
           "text_lines": {k: "sec2_statistics.tex:%d" % v for k, v in lines.items()}, "cells": cells,
           "passes": all(c["passes"] for c in cells.values()),
           "description": {"kmax_agrees": all(c["kmax_disagreements"] == 0 for c in cells.values()),
                           "maic_agrees": all(c["maic_disagreements"] == 0 for c in cells.values()),
                           "dfgls_sample_agrees": all(c["dfgls_max_rel"] <= TOL_DF_REL for c in cells.values())}}
    C.write_result(OUT, out, __file__)
    print("cumple:", out["passes"], out["description"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
