"""
Auditoria A17 - B17.2 (enmienda 7, lectura E7.2): cada afirmacion de la seccion 3.5 del v18 (sec3_theory.tex) frente al
codigo que la sustenta: bootUR 1.0.5 (SB, SWB, regla por defecto del AWB) y nuestro motor (R, p-valor, recalculo de MZ_t,
AWB). Lineas localizadas por expresion regular. Las cifras (eta = 0.631 en n = 200) se recalculan con la regla del texto
(n) y con la del codigo (T = n + 1). Solo lee codigo, JSON y el zip del v18.
Salida: experiments/results/boot35_v18_audit17.json.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit17_common as C                                         # noqa: E402
import audit16_code_check as K                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "boot35_v18_audit17.json")
L_C, L_EXP, ETA_BASE = 1.75, 3, 100          # l = round(1.75 n^(1/3)); eta = 0.01^(1/l) = (1/100)^(1/l)
ETA_DEC = 3
DESIGN_N = (100, 200, 500)


def eta(n):
    l = int(round(L_C * n ** (1 / L_EXP)))
    return l, (1 / ETA_BASE) ** (1 / l)


def main():
    v18 = C.v18()
    sec3 = v18.lines("sec3_theory.tex")
    S = "sec3_theory.tex"
    B = C.BOOTUR_SRC
    aux, tst = K.read_lines(os.path.join(B, "R", "auxiliary.R")), K.read_lines(os.path.join(B, "R", "bootURtests.R"))
    cpp = K.read_lines(os.path.join(B, "src", "bootURfunctions.cpp"))
    eng = K.read_lines(os.path.join(HERE, "audit15_boot_engine.py"))
    des = K.read_lines(os.path.join(HERE, "audit15_design.py"))
    e9 = K.read_lines(os.path.join(HERE, "audit9_engine.py"))
    b1r = K.read_lines(os.path.join(HERE, "audit15_b1_boot.py"))
    A, T, P, E = "bootUR/R/auxiliary.R", "bootUR/R/bootURtests.R", "bootUR/src/bootURfunctions.cpp", "experiments/audit15_boot_engine.py"
    t = lambda rx: K.cite(S, sec3, rx)                                  # noqa: E731
    b1 = C.read_json("b1_boot_audit15.json")
    p0 = C.read_json("b1_paso0_v2_audit15.json")
    etas = {n: {"text_rule_n": eta(n), "code_rule_T": eta(n + 1)} for n in DESIGN_N}
    claims = [
        ("R = 399 replicas", t(r"each with \$R = 399\$"), [K.cite("experiments/audit15_design.py", des, r"^R = 399"),
                                                            K.cite("experiments/audit15_b1_boot.py", b1r, r"R = D\.R if chosen")],
         "coincide", "b1_boot_audit15.json config.R = %d" % b1["config"]["R"], b1["config"]["R"] == 399),
        ("p-valor (1 + #{T* <= T})/(R + 1)", t(r"\(1 \+ \\#\\\{T\^\{\*\(r\)\} \\leq T\\\}\)/\(R\+1\)"),
         [K.cite(E, eng, r"if mzt_gls\(ys, ct, cbar, kmax\)\[0\] <= t_obs", r"def pvalue_sb"), K.cite(E, eng, r"return \(1\.0 \+ cnt\) / \(R \+ 1\.0\)", r"def pvalue_sb")],
         "coincide", "rechazo p <= 0.05 (config.pvalue: %s)" % b1["config"]["pvalue"], True),
        ("SB y SWB son los de bootUR 1.0.5", t(r"\(bootUR 1\.0\.5\)"), [],
         "coincide", "Paso 0 de A15 (enmienda 3): SB %s, SWB %s" % (p0["gate"]["iii_SB_bootUR"], p0["gate"]["v_prime_SWB_bootUR"]),
         p0["gate"]["iii_SB_bootUR"] and p0["gate"]["v_prime_SWB_bootUR"]),
        ("regresion ADF estimada sin restringir", t(r"estimated$|without restriction"), [K.cite(T, tst, r"residual bootstrap \(under the alternative\)"),
                                                                                         K.cite(P, cpp, r"x = arma::join_rows\(y_lag, y_dif_lags\)", r"adfvout adf_cpp")],
         "coincide", "la regresion incluye y_{t-1}; su coeficiente se estima", True),
        ("sobre datos detrendidos por MCO", t(r"on OLS-detrended data"), [K.cite(A, aux, r"dc = dc_boot, QD = FALSE, trim = FALSE"),
                                                                            K.cite(P, cpp, r"adfp = adf_cpp\(ys, ip, dc, false, trim, pmax\)", r"adfvout adf_selectlags_cpp")],
         "coincide", "QD = FALSE en el DGP y en la seleccion del retardo", True),
        ("retardo por la MAIC con el reescalado de Perron y Qu", t(r"MAIC with the rescaling of Perron and Qu"),
         [K.cite(T, tst, r"criterion = \"MAIC\", criterion_scale = TRUE", r"^boot_ur <- function"),
          K.cite(P, cpp, r"ys = rescale_cpp\(", r"adfvout adf_selectlags_cpp"), K.cite(P, cpp, r"return maic_cpp;")],
         "coincide", "valores por defecto de boot_ur", True),
        ("nula impuesta al generar, descartando el coeficiente del nivel retardado", t(r"by discarding the coefficient on"),
         [K.cite(A, aux, r"ar_est <- panel_est\$par\[-1, , drop = FALSE\]")], "coincide", "par[-1] quita el coeficiente de y_{t-1}", True),
        ("incrementos = AR de las diferencias retardadas; serie acumulada bajo raiz unitaria", t(r"autoregression of the lagged differences"),
         [K.cite(P, cpp, r"gen_AR_cpp\(e_star\.col\(iN\), ar_est\.col\(iN\), init, false\)", r"arma::mat SB_cpp"),
          K.cite(P, cpp, r"const arma::mat y_star = cumsum\(u_star\);", r"arma::mat SB_cpp")], "coincide", "SB_cpp y SWB_cpp", True),
        ("residuos sin centrar", t(r"not centred"), [K.cite(P, cpp, r"const arma::vec e = y_dif - x \* b;", r"adfvout adf_cpp"),
                                                      K.cite(A, aux, r"res <- panel_est\$res")], "coincide", "no hay resta de la media en el camino de e", True),
        ("SB: remuestreo independiente", t(r"resampled independently \(SB\)"),
         [K.cite(P, cpp, r"RcppArmadillo::sample\(linspace<arma::uvec>\(0, T - ub, T - ub \+ 1\), T \* B, true\)"),
          K.cite(P, cpp, r"const arma::mat e_star = e\.rows\(index\);", r"arma::mat SB_cpp")],
         "coincide con matiz", "con reposicion, indices 0..T - l (los ultimos l - 1 residuos no se sortean); el detalle va a S2", True),
        ("SWB: pesos gaussianos estandar independientes", t(r"Gaussian weights \(SWB\)"),
         [K.cite(P, cpp, r"const arma::vec z_vec = Rcpp::rnorm\(T \* B, 0, 1\);"), K.cite(P, cpp, r"const arma::mat e_star = repelem\(z, 1, N\) % e;")],
         "coincide", "N(0, 1)", True),
        ("replica propia con MZ_t-GLS y su MAIC recalculados en cada serie bootstrap", t(r"MZ\$_t\$-GLS and its MAIC recomputed"),
         [K.cite(E, eng, r"if mzt_gls\(ys, ct, cbar, kmax\)\[0\] <= t_obs", r"def pvalue_swb"), K.cite(E, eng, r"^def mzt_gls")],
         "coincide", "mzt_gls selecciona k por la MAIC GLS en cada ys", True),
        ("la replica se contrasta con el paquete (S2)", t(r"the replication against the package"), [],
         "coincide", "Paso 0 con B = %d (familia 159) y texto en S2" % p0["config"]["B"], True),
        ("SWB disenado para choques heterocedasticos", t(r"designed for$|heteroskedastic shocks"), [], "cita", "afirmacion bibliografica; no es codigo", None),
        ("def:awb: e_t = Delta Y_t - media", t(r"\\hat e_t = \\Delta\\rw_t - \\overline"),
         [K.cite(E, eng, r"u = dy - m / n", r"def pvalue_awb")], "coincide", "centrado de los incrementos", True),
        ("def:awb: xi_t = eta xi_{t-1} + (1 - eta^2)^{1/2} nu_t", t(r"\\xi_t = \\eta"),
         [K.cite(E, eng, r"xi = gamma \* xi \+ b \* nu\[r, t\]", r"def pvalue_awb"), K.cite(E, eng, r"b = math\.sqrt\(1\.0 - gamma \* gamma\)", r"def pvalue_awb")],
         "coincide", "xi_1 = nu_1 (arranque estacionario)", True),
        ("def:awb: eps* = xi e, Y* = suma acumulada", t(r"\\varepsilon\^\*_t = \\xi_t"),
         [K.cite(E, eng, r"acc \+= xi \* u\[t\]", r"def pvalue_awb")], "coincide", "Y*_0 = 0", True),
        ("eta = 0.01^{1/l}, l = round(1.75 n^{1/3}) por defecto de bootUR; eta = 0.631 en n = 200", t(r"l = \\mathrm\{round\}\(1\.75"),
         [K.cite(A, aux, r"block_length <- round\(1\.75 \* nrow\(data\)\^\(1/3\)\)"), K.cite(A, aux, r"ar_AWB <- 0\.01\^\(1/block_length\)"),
          K.cite("experiments/audit9_engine.py", e9, r"l = int\(round\(1\.75 \* \(n \+ 1\)"), K.cite("experiments/audit15_b1_boot.py", b1r, r"gam, _ = E9\.awb_gamma\(T - 1\)")],
         "coincide con matiz",
         "bootUR y nuestro codigo usan T = n + 1 observaciones (nrow(data)); el texto escribe n^{1/3}. En n = 100, 200, 500 dan la misma l: %s" % (
             "; ".join("n = %d: l(n) = %d, l(T) = %d" % (n, v["text_rule_n"][0], v["code_rule_T"][0]) for n, v in etas.items())),
         all(v["text_rule_n"][0] == v["code_rule_T"][0] for v in etas.values())),
    ]
    eta200 = etas[200]["code_rule_T"][1]
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 7, lectura E7.2",
           "inputs": {"v18_zip_sha256": v18.sha256, "bootUR_tar_sha256": C.sha256_file(os.path.join(HERE, "external_audit15", "bootUR_1.0.5.tar.gz"))},
           "claims": [{"claim": c, "text": tx, "code": cd, "verdict": v, "detail": d, "check": ok} for c, tx, cd, v, d, ok in claims],
           "eta": {str(n): {"l_text": v["text_rule_n"][0], "eta_text": v["text_rule_n"][1], "l_code": v["code_rule_T"][0], "eta_code": v["code_rule_T"][1]}
                   for n, v in etas.items()},
           "eta200_printed": {"printed": "0.631", "value": eta200, "binary": "%.*f" % (ETA_DEC, eta200), "confirma": "%.*f" % (ETA_DEC, eta200) == "0.631"},
           "summary": {v: sum(1 for c in claims if c[3] == v) for v in ("coincide", "coincide con matiz", "difiere", "cita")},
           "checks_failed": [c[0] for c in claims if c[5] is False]}
    C.write_result(OUT, out, __file__)
    for c in out["claims"]:
        print(c["text"]["where"], "|", c["claim"], "->", c["verdict"], "|", c["check"])
    print(out["summary"], out["eta200_printed"], out["checks_failed"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
