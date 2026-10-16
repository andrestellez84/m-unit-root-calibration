"""
Auditoria A16 - B16.2 (enmienda 6, lecturas E6.2-E6.4): verificacion del texto del v17 contra el codigo.

(a) eq:mstats y su entorno (sec2_statistics.tex) frente a audit8_unitroot.np_statistics y a arch.DFGLS.
(b) Sec. 3.5 (sec3_theory.tex, SB/SWB) frente al codigo fuente de bootUR 1.0.5.
(c) prop:invariance (appA_proofs.tex) para los tests con s2_AR: argumento sobre el codigo y control numerico
    determinista (familia 160; no es una simulacion de resultados).

Los numeros de linea se localizan con expresiones regulares sobre los archivos (no se escriben a mano).
Salida: experiments/results/code_check_audit16.json.
"""
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C                                         # noqa: E402
import audit8_unitroot as U                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "code_check_audit16.json")
FAM = C.FAMILY["INVAR"]
NS = (100, 200, 500)
CASES = ("c", "ct")
PATHS = 1000
A_SET = (-3.0, 1e-2, 1e3)
B_SHIFT = 5.0
C_SLOPE = 0.1
TOL = 1e-10


# ---------------------------------------------------------------------------
# Localizacion de lineas
# ---------------------------------------------------------------------------
def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def locate(lines, pattern, start=0):
    rx = re.compile(pattern)
    for i in range(start, len(lines)):
        if rx.search(lines[i]):
            return i + 1
    raise LookupError(pattern)


def cite(label, lines, pattern, start_pattern=None):
    s = locate(lines, start_pattern) - 1 if start_pattern else 0
    ln = locate(lines, pattern, s)
    return {"where": "%s:%d" % (label, ln), "text": lines[ln - 1].strip()}


def arch_file():
    import arch
    import arch.unitroot.unitroot as au
    return au.__file__, "arch %s, arch/unitroot/unitroot.py" % arch.__version__


# ---------------------------------------------------------------------------
# (a) eq:mstats
# ---------------------------------------------------------------------------
def part_a(v17):
    code = read_lines(os.path.join(HERE, "audit8_unitroot.py"))
    L = "experiments/audit8_unitroot.py"
    af, alab = arch_file()
    arch_lines = read_lines(af)
    sec2 = v17.lines("sec2_statistics.tex")
    T = "sec2_statistics.tex"
    c = {
        "gls_a": cite(L, code, r"a = 1\.0 \+ cbar / T", r"def gls_detrend"),
        "gls_T": cite(L, code, r"T = len\(y\)", r"def gls_detrend"),
        "reg_design": cite(L, code, r"X = np\.empty\(\(rows, kmax \+ 1\)\)"),
        "reg_ylag": cite(L, code, r"X\[:, 0\] = yt\[kmax:T - 1\]"),
        "reg_rows": cite(L, code, r"rows = T - 1 - kmax"),
        "kmax": cite(L, code, r"12\.0 \* \(T / 100\.0\) \*\* 0\.25"),
        "tau": cite(L, code, r"tau = b0 \* b0 \* sum_y2 / s2k"),
        "sum_y2": cite(L, code, r"sum_y2 = float\(X\[:, 0\] @ X\[:, 0\]\)"),
        "maic": cite(L, code, r"maic\.append\(math\.log\(s2k\)"),
        "s2_ar": cite(L, code, r"s2 = \(ssr / rows\) / \(1\.0 - bsum\) \*\* 2"),
        "S": cite(L, code, r"S = float\(yt\[:-1\] @ yt\[:-1\]\) / T \*\* 2"),
        "yT2": cite(L, code, r"yT2 = yt\[-1\] \*\* 2 / T"),
        "mza": cite(L, code, r"mza = \(yT2 - s2\) / \(2\.0 \* S\)"),
        "msb": cite(L, code, r"msb = math\.sqrt\(S / s2\)"),
        "mzt": cite(L, code, r"mzt = mza \* msb"),
        "dfgls_call": cite(L, code, r"t = DFGLS\(y, trend=case, lags=int\(k\)\)"),
        "arch_nobs": cite(alab, arch_lines, r"nobs = self\._y\.shape\[0\]", r"class DFGLS"),
        "arch_ct": cite(alab, arch_lines, r"ct = c / nobs", r"class DFGLS"),
        "arch_reg": cite(alab, arch_lines, r"_estimate_df_regression\(y_detrended, lags=lags, trend=\"n\"\)", r"class DFGLS"),
    }
    src = read_lines(os.path.join(C.REPO, "src", "stationarity_test", "rm_core.py"))
    c["msbb_gls_const"] = cite("src/stationarity_test/rm_core.py", src, r"a = 1\.0 \+ cbar / n", r"def gls_mean")
    dq = read_lines(os.path.join(C.REPO, "src", "stationarity_test", "deterministics.py"))
    c["msbb_gls_trend"] = cite("src/stationarity_test/deterministics.py", dq, r"alpha = 1\.0 \+ cbar / T", r"def detrend_qd")
    t = {
        "Tn": cite(T, sec2, r"T_n = n\$ and \$T_n = n\+1"),
        "eq_msb": cite(T, sec2, r"\\mathrm\{MSB\} = "),
        "eq_mza": cite(T, sec2, r"\\mathrm\{MZ\}_\\alpha = "),
        "eq_mzt": cite(T, sec2, r"\\mathrm\{MZ\}_t = \\mathrm\{MZ\}_\\alpha \\times"),
        "s2_ar": cite(T, sec2, r"\\sAR = \\hat\\sigma_k\^2"),
        "reg": cite(T, sec2, r"regression of \$\\Delta\\uhat_t\$ on \$\\uhat_\{t-1\}\$"),
        "maic": cite(T, sec2, r"modified Akaike criterion"),
        "dfgls": cite(T, sec2, r"DF-GLS is the \$t\$-ratio"),
    }
    items = [
        {"item": "MSB, MZ_alpha y MZ_t: forma", "text": [t["eq_msb"], t["eq_mza"], t["eq_mzt"]],
         "code": [c["S"], c["yT2"], c["mza"], c["msb"], c["mzt"]],
         "verdict": "coincide",
         "detail": "MSB = (S/s2)^(1/2), MZ_alpha = (T^-1 u_n^2 - s2)/(2S), MZ_t = MZ_alpha x MSB, con S la suma de u_{t-1}^2, "
                   "t = 1..n."},
        {"item": "MSB, MZ_alpha y MZ_t: normalizacion", "text": [t["eq_msb"], t["eq_mza"]], "code": [c["gls_T"], c["S"], c["yT2"]],
         "verdict": "difiere, sin efecto en el tamano de los brazos calibrados",
         "detail": "El texto normaliza con n (n^-2 y n^-1). El codigo usa T = len(y) = n + 1 ((n+1)^-2 y (n+1)^-1). MSB del codigo = "
                   "MSB del texto x n/(n+1). El brazo con valores criticos asintoticos publicados si depende de ello (control "
                   "numerico abajo)."},
        {"item": "Convencion T_n del detrending GLS", "text": [t["Tn"]],
         "code": [c["gls_a"], c["gls_T"], c["arch_nobs"], c["arch_ct"], c["msbb_gls_const"], c["msbb_gls_trend"]],
         "verdict": "difiere para MSB-GLS, MZ_t-GLS y DF-GLS en el caso constante",
         "detail": "El texto dice T_n = n (constante) y T_n = n + 1 (tendencia), 'the convention of the replication code'. Es la de "
                   "MSB-B (src/). np_statistics y arch.DFGLS usan a = 1 + cbar/(n + 1) en los dos casos."},
        {"item": "Regresion de s2_AR: deterministas", "text": [t["reg"]], "code": [c["reg_design"], c["reg_ylag"]],
         "verdict": "coincide",
         "detail": "Sin constante: la matriz tiene u_{t-1} y k diferencias retardadas sobre el residuo GLS."},
        {"item": "Regresion de s2_AR: muestra e indices", "text": [t["reg"], t["s2_ar"]], "code": [c["reg_rows"], c["s2_ar"]],
         "verdict": "no especificado en el texto",
         "detail": "Muestra comun t = kmax+1..n (n - kmax observaciones) para todo k, tambien para el s2_AR final (no se reestima "
                   "con t = k+1..n); sigma2_k = SSR_k/(n - kmax)."},
        {"item": "Formula de s2_AR", "text": [t["s2_ar"]], "code": [c["s2_ar"]], "verdict": "coincide",
         "detail": "s2_AR = sigma2_k/(1 - sum b_j)^2."},
        {"item": "MAIC", "text": [t["maic"]], "code": [c["maic"], c["tau"], c["sum_y2"], c["kmax"]], "verdict": "coincide",
         "detail": "MAIC(k) = ln sigma2_k + 2(tau(k) + k)/(n - kmax), tau(k) = b0^2 sum u_{t-1}^2/sigma2_k en la muestra comun, "
                   "kmax = floor(12((n+1)/100)^(1/4)): la forma de Ng y Perron (2001) con T - kmax observaciones de la regresion."},
        {"item": "DF-GLS 'in the same regression'", "text": [t["dfgls"]], "code": [c["dfgls_call"], c["arch_reg"]],
         "verdict": "difiere (muestra)",
         "detail": "DF-GLS es arch.DFGLS con el k de la MAIC: mismo detrending y mismo k, pero regresion sobre t = k+1..n, no sobre la "
                   "muestra comun t = kmax+1..n de la MAIC."},
    ]
    return items


def literal_text(y, case, k):
    """Evaluacion literal de eq:mstats con la convencion T_n del texto y normalizacion por n, con el k del codigo."""
    n = len(y) - 1
    Tn = n if case == "c" else n + 1
    cbar = U.NP_CBAR[case]
    a = 1.0 + cbar / Tn
    z = U.deterministic_matrix(n + 1, case)
    yq, zq = y.copy(), z.copy()
    yq[1:] = y[1:] - a * y[:-1]
    zq[1:] = z[1:] - a * z[:-1]
    beta, *_ = np.linalg.lstsq(zq, yq, rcond=None)
    u = y - z @ beta
    kmax = U.kmax_rule(n + 1)
    path, rows, _ = U.adf_gls_path(u, kmax)
    ssr, _, bsum = path[k]
    s2 = (ssr / rows) / (1.0 - bsum) ** 2
    S = float(u[:-1] @ u[:-1]) / n ** 2
    mza = (u[-1] ** 2 / n - s2) / (2.0 * S)
    msb = math.sqrt(S / s2)
    return {"MSB": msb, "MZt": mza * msb}


# ---------------------------------------------------------------------------
# (b) bootUR
# ---------------------------------------------------------------------------
def part_b(v17):
    aux = read_lines(os.path.join(C.BOOTUR_SRC, "R", "auxiliary.R"))
    tst = read_lines(os.path.join(C.BOOTUR_SRC, "R", "bootURtests.R"))
    cpp = read_lines(os.path.join(C.BOOTUR_SRC, "src", "bootURfunctions.cpp"))
    A, Tt, P = "bootUR/R/auxiliary.R", "bootUR/R/bootURtests.R", "bootUR/src/bootURfunctions.cpp"
    sec3 = v17.lines("sec3_theory.tex")
    S3 = "sec3_theory.tex"
    q = {
        "dgp_call": cite(A, aux, r"dc = dc_boot, QD = FALSE, trim = FALSE"),
        "under_alt": cite(Tt, tst, r"residual bootstrap \(under the alternative\)"),
        "defaults": cite(Tt, tst, r"criterion = \"MAIC\", criterion_scale = TRUE", r"^boot_ur <- function"),
        "rescale": cite(P, cpp, r"ys = rescale_cpp\(", r"adfvout adf_selectlags_cpp"),
        "select_ols": cite(P, cpp, r"adfp = adf_cpp\(ys, ip, dc, false, trim, pmax\)", r"adfvout adf_selectlags_cpp"),
        "adf_x": cite(P, cpp, r"x = arma::join_rows\(y_lag, y_dif_lags\)", r"adfvout adf_cpp"),
        "adf_e": cite(P, cpp, r"const arma::vec e = y_dif - x \* b;", r"adfvout adf_cpp"),
        "lag_zero_fill": cite(P, cpp, r"arma::mat lag_x = arma::mat\(n, k \* p, arma::fill::zeros\)"),
        "res": cite(A, aux, r"res <- panel_est\$res"),
        "ar_est": cite(A, aux, r"ar_est <- panel_est\$par\[-1, , drop = FALSE\]"),
        "y0": cite(A, aux, r"y0 = matrix\(0, ncol = N\)"),
        "sb_resample": cite(P, cpp, r"const arma::mat e_star = e\.rows\(index\);", r"arma::mat SB_cpp"),
        "sb_ar": cite(P, cpp, r"gen_AR_cpp\(e_star\.col\(iN\), ar_est\.col\(iN\), init, false\)", r"arma::mat SB_cpp"),
        "sb_cumsum": cite(P, cpp, r"const arma::mat y_star = cumsum\(u_star\);", r"arma::mat SB_cpp"),
        "swb_weights": cite(P, cpp, r"const arma::mat e_star = repelem\(z, 1, N\) % e;", r"arma::mat SWB_cpp"),
        "swb_ar": cite(P, cpp, r"gen_AR_cpp\(e_star\.col\(iN\), ar_est\.col\(iN\), init, false\)", r"arma::mat SWB_cpp"),
        "swb_cumsum": cite(P, cpp, r"const arma::mat y_star = cumsum\(u_star\);", r"arma::mat SWB_cpp"),
        "z_normal": cite(P, cpp, r"const arma::vec z_vec = Rcpp::rnorm\(T \* B, 0, 1\);", r"arma::mat bootstrap_cpp"),
        "ub": cite(P, cpp, r"ub = l;", r"arma::mat bootstrap_cpp"),
        "sb_index": cite(P, cpp, r"RcppArmadillo::sample\(linspace<arma::uvec>\(0, T - ub, T - ub \+ 1\)", r"arma::mat bootstrap_cpp"),
        "e0": cite(P, cpp, r"e0\.replace\(datum::nan, 0\);", r"arma::mat bootstrap_cpp"),
        "pvalue": cite(P, cpp, r"sum\(t_star\.col\(i\) < test_i\(i\)\)", r"arma::vec iADF_cpp"),
    }
    t = {
        "dgp": cite(S3, sec3, r"autoregression in first differences implied by an augmented Dickey"),
        "null": cite(S3, sec3, r"regression with the null imposed"),
        "resample": cite(S3, sec3, r"residuals are resampled independently \(SB\)"),
        "weights": cite(S3, sec3, r"random weights \(SWB\)"),
        "rebuild": cite(S3, sec3, r"cumulation"),
    }
    items = [
        {"question": "Como se impone la nula", "text": [t["dgp"], t["null"]],
         "code": [q["under_alt"], q["dgp_call"], q["adf_x"], q["ar_est"], q["sb_ar"], q["sb_cumsum"]],
         "answer": "La regresion ADF se estima sin restringir, con rho estimado ('residual bootstrap (under the alternative)'). La nula "
                   "se impone al generar: se descarta el coeficiente de y_{t-1} (par[-1]), las innovaciones se filtran por el AR de "
                   "las diferencias y la serie se acumula (raiz unitaria).",
         "verdict": "matiz: 'regression with the null imposed' describe la generacion, no la estimacion"},
        {"question": "Autorregresion en diferencias; detrending y criterio", "text": [t["dgp"]],
         "code": [q["dgp_call"], q["adf_x"], q["defaults"], q["rescale"], q["select_ols"]],
         "answer": "Si: u*_t = Delta y*_t sigue el AR(p) de los coeficientes de las diferencias retardadas de la regresion ADF. La "
                   "regresion del DGP usa detrending MCO (QD = FALSE) y la muestra sin recortar (trim = FALSE); p se elige con la "
                   "MAIC reescalada de Perron y Qu (criterion_scale = TRUE por defecto) sobre datos detrendidos por MCO.",
         "verdict": "coincide; el texto no menciona el detrending MCO ni el reescalado de Perron-Qu"},
        {"question": "Pesos del SWB", "text": [t["weights"]], "code": [q["z_normal"], q["swb_weights"]],
         "answer": "Gaussianos N(0, 1) independientes (Rcpp::rnorm), multiplicados por los residuos.",
         "verdict": "coincide; el texto no dice que sean gaussianos"},
        {"question": "Centrado de residuos", "text": [t["resample"], t["weights"]], "code": [q["adf_e"], q["res"], q["e0"]],
         "answer": "No se centran: los residuos de la regresion ADF pasan tal cual al remuestreo (SB) y a la multiplicacion (SWB).",
         "verdict": "el texto no lo dice"},
        {"question": "Indices del SB", "text": [t["resample"]], "code": [q["ub"], q["sb_index"], q["sb_resample"]],
         "answer": "Remuestreo iid de residuos individuales con indices 0..T - l, l = longitud de bloque por defecto: los ultimos l - 1 "
                   "residuos no se sortean nunca.",
         "verdict": "detalle no descrito en el texto"},
        {"question": "Residuos sin recortar y valor inicial", "text": [t["rebuild"]],
         "code": [q["dgp_call"], q["lag_zero_fill"], q["adf_e"], q["y0"], q["sb_ar"]],
         "answer": "Con trim = FALSE, los retardos iniciales se rellenan con ceros, asi que los primeros p + 1 residuos entran en el "
                   "remuestreo con regresores nulos (el primero es el nivel detrendido). El AR arranca en cero y y*_0 = 0.",
         "verdict": "detalle no descrito en el texto"},
        {"question": "p-valor de bootUR", "text": [], "code": [q["pvalue"]],
         "answer": "#{t* < t}/B en bootUR; nuestros brazos usan (1 + #{T* <= T})/(R + 1), declarado en la enmienda 3.",
         "verdict": "declarado"},
    ]
    return items


# ---------------------------------------------------------------------------
# (c) invariancia
# ---------------------------------------------------------------------------
def maic_values(y, case):
    T = len(y)
    kmax = U.kmax_rule(T)
    path, rows, sum_y2 = U.adf_gls_path(U.gls_detrend(y, case), kmax)
    return np.array([math.log(s / rows) + 2.0 * (b0 * b0 * sum_y2 / (s / rows) + k) / rows for k, (s, b0, _) in enumerate(path)])


def seeds():
    keys = [(i,) for i in range(len(NS) * len(CASES))]
    ours = {np.random.SeedSequence(FAM, spawn_key=k).generate_state(1, np.uint64)[0] for k in keys}
    prior = {np.random.SeedSequence(f, spawn_key=k).generate_state(1, np.uint64)[0] for f in C.PRIOR_FAMILIES for k in keys}
    return keys, len(ours & prior), len(ours) == len(keys)


def part_c(v17):
    keys, coll, distinct = seeds()
    out, lit = {}, {}
    for ci, (n, case) in enumerate([(n, c) for n in NS for c in CASES]):
        rng = np.random.default_rng(np.random.SeedSequence(FAM, spawn_key=keys[ci]))
        t = np.arange(n + 1, dtype=np.float64)
        flips, rel_msb, rel_mzt, rel_s2, rel_df, margins = 0, 0.0, 0.0, 0.0, 0.0, []
        lit_msb, lit_mzt, abs_mzt, worst, lit_abs = [], [], 0.0, None, []
        for _ in range(PATHS):
            y = np.concatenate([[0.0], np.cumsum(rng.standard_normal(n))])
            base = U.np_statistics(y, case)
            df0 = U.dfgls_maic(y, case, base["k"])[0]
            mv = np.sort(maic_values(y, case))
            margins.append(float(mv[1] - mv[0]))
            tx = literal_text(y, case, base["k"])
            lit_msb.append(abs(tx["MSB"] / base["MSB"] - 1.0))
            lit_mzt.append(abs(tx["MZt"] / base["MZt"] - 1.0))
            lit_abs.append(abs(tx["MZt"] - base["MZt"]))
            for a in A_SET:
                yy = a * y + B_SHIFT + (C_SLOPE * t if case == "ct" else 0.0)
                st = U.np_statistics(yy, case)
                flips += st["k"] != base["k"]
                rel_msb = max(rel_msb, abs(st["MSB"] / base["MSB"] - 1.0))
                r_mzt = abs(st["MZt"] / base["MZt"] - 1.0)
                if r_mzt > rel_mzt:
                    worst = {"rel": r_mzt, "abs": abs(st["MZt"] - base["MZt"]), "mzt": base["MZt"], "mza_numerator_over_s2":
                             (U.gls_detrend(y, case)[-1] ** 2 / len(y)) / base["s2_ar"] - 1.0}
                rel_mzt = max(rel_mzt, r_mzt)
                abs_mzt = max(abs_mzt, abs(st["MZt"] - base["MZt"]))
                rel_s2 = max(rel_s2, abs(st["s2_ar"] / (a * a * base["s2_ar"]) - 1.0))
                rel_df = max(rel_df, abs(U.dfgls_maic(yy, case, st["k"])[0] / df0 - 1.0))
        key = "n%d_%s" % (n, case)
        out[key] = {"paths": PATHS, "transforms": len(A_SET), "k_changes": int(flips), "max_rel_msb": rel_msb, "max_rel_mzt": rel_mzt,
                    "max_rel_s2_over_a2": rel_s2, "max_rel_dfgls": rel_df, "min_maic_margin": min(margins),
                    "diagnostic_max_abs_mzt": abs_mzt, "diagnostic_worst_rel_mzt": worst,
                    "passes": flips == 0 and rel_msb <= TOL and rel_mzt <= TOL}
        lit[key] = {"median_rel_msb": float(np.median(lit_msb)), "max_rel_msb": float(max(lit_msb)),
                    "expected_rel_msb": 1.0 / n, "median_rel_mzt": float(np.median(lit_mzt)), "max_rel_mzt": float(max(lit_mzt)),
                    "max_abs_mzt": float(max(lit_abs)), "median_abs_mzt": float(np.median(lit_abs))}
        print(key, out[key], lit[key])
    proof = cite("appA_proofs.tex", v17.lines("appA_proofs.tex"), r"penalty that is a ratio of quadratic forms")
    return {"family": FAM, "seed_keys": [list(k) for k in keys], "collisions_vs_prior": coll, "distinct": distinct,
            "config": {"n": NS, "cases": CASES, "paths": PATHS, "a": A_SET, "b": B_SHIFT, "c": C_SLOPE, "tol": TOL},
            "cells": out, "passes": all(v["passes"] for v in out.values()), "proof_text": proof,
            "diagnostic_note": "Diagnostico anadido tras ver el resultado (declarado): |Delta| absoluto de MZ_t y, en el camino con "
                               "mayor |Delta| relativo, MZ_t y (T^-1 u_n^2)/s2_AR - 1, el factor que se cancela en el numerador de "
                               "MZ_alpha. El veredicto registrado no cambia.",
            "argument": "En el codigo, u = M y con MD = 0, asi que u(aY + D delta) = a u(Y). La regresion ADF-GLS sobre a u deja los "
                        "coeficientes igual y multiplica SSR_k por a^2 para todo k (misma muestra comun). tau(k) = b0^2 sum u^2 / "
                        "sigma2_k es invariante, y MAIC(k) se desplaza en ln a^2 para todo k: el argmin no cambia (salvo empates "
                        "exactos). s2_AR se multiplica por a^2, y MSB, MZ_t y el t de DF-GLS no cambian. El suelo 1e-300 del SSR no "
                        "actua en caminos no degenerados.",
            "literal_eq_mstats_vs_code": lit}


def main():
    v17 = C.v17()
    a, b = part_a(v17), part_b(v17)
    c = part_c(v17)
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "reading": "enmienda 6, lecturas E6.2-E6.4",
           "inputs": {"v17_zip_sha256": v17.sha256, "bootUR_tar_sha256": C.sha256_file(os.path.join(HERE, "external_audit15", "bootUR_1.0.5.tar.gz"))},
           "a_eq_mstats": a, "b_bootur": b, "c_invariance": c}
    C.write_result(OUT, out, __file__)
    for x in a:
        print("(a)", x["item"], "->", x["verdict"])
    for x in b:
        print("(b)", x["question"], "->", x["verdict"])
    print("(c) cumple:", c["passes"], "| colisiones:", c["collisions_vs_prior"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
