"""
Auditoria A13 - B13.Q, Q3: coherencia de las cifras del v14 contra sus JSON.

Lee paper_latex_v14.zip sin extraerlo (protocol_audit13_amend1.md, lectura 5). Cada
frase del registro se localiza por una plantilla (texto literal; <> marca una cifra
capturada, <w> una palabra-numero; los espacios admiten saltos de linea) y cada cifra
capturada se recalcula desde su JSON o, si es una constante derivada, desde su formula.
Convenciones de redondeo probadas: binaria ("%.*f"), mitad hacia arriba sobre el decimal
(la de una transcripcion a mano) y, solo donde el texto da una cota ("within", "below",
"at most"), hacia arriba. Veredicto por cifra: reproduce, reproduce como cota, no
reproduce (con la cifra correcta a los mismos decimales).
Barrido de cobertura: todo numero con decimales del texto (fuera de comentarios y de
tabulares \\input) queda cubierto por una frase, clasificado como parametro de diseno o
definicion por su contexto, o listado como no verificado.

Salida: experiments/results/q_claims_audit13.json.
"""
import decimal
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402
import audit13_q_common as Q                                       # noqa: E402

OUT = os.path.join(C.RESULTS, "q_claims_audit13.json")
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16}
NUMRE = r"([-+]?\d+(?:\.\d+)?)"
WORDRE = r"([a-z]+)"
PRIM, V13P = C.PRIM, C.PRIM_V13
LEVEL = C.ALPHA
BOUND_EPS = 10 ** -12          # tolerancia numerica de las cotas ("within", "at most", "at least")


# ---------------------------------------------------------------------------
# Fuentes
# ---------------------------------------------------------------------------
class S:
    _c = {}

    @classmethod
    def J(cls, name):
        if name not in cls._c:
            cls._c[name] = C.read_json(name)
        return cls._c[name]


P01 = 10 ** -2                 # umbral "p < 0.01" y "less than 0.01" de las frases de DGP 2


def CBAR():
    return S.J("bF_anchor_audit12.json")["config"]["cbar"]


def THETAS():
    return tuple(S.J("b92_theta_audit9.json")["config"]["thetas"])


def LP_C():
    """Valores de c de las filas de tab:localpower (los del v13, exportados por A13)."""
    rows = C.read_json("tables_audit13.json")["tables"]["localpower"]["rows"]
    return sorted({TB.num(r["keys"][0]) for r in rows})


def cal(case, n, leaf="size_with_cv_n20000"):
    return S.J("e_calib_audit13.json")["cases_by_theta"][PRIM][case]["approximation_cost"][str(n)][leaf]["rate"]


def calc(case, n, proc, leaf="size_published_asymptotic"):
    return S.J("e_calib_audit13.json")["cases_by_theta"][PRIM][case]["approximation_cost_comparators"][str(n)][proc][leaf]


def eq(k, p=PRIM):
    return S.J("e_equalized_audit13.json")["cells"][k]["rates_sim"][p]["rate"]


def eqp(k):
    return S.J("e_equalized_audit13.json")["cells"][k]["mcnemar_primary_vs_sim"]["dfgls"]["p_value"]


def dd(k, other="dfgls"):
    return (eq(k) - eq(k, other)) * C.PP


def sz(err, n, case, proc=PRIM, block="iid"):
    return S.J("bA_ma_audit12.json")["size"]["sz_%s_n%d_%s" % (err, n, case)][block][proc]["rate"]


def szc(err, n, case):
    return S.J("bA_ma_audit12.json")["size"]["sz_%s_n%d_%s" % (err, n, case)]


def ini(rho, var, proc):
    return S.J("bC_initial_audit12.json")["cells"]["%s|%s" % (rho, var)]["power"][proc]["rate"]


def awbc(cell, which="awb"):
    return S.J("e_awb_audit13.json")["cells"][cell][which]["rate"]


def app():
    return S.J("e_application_audit13.json")


def summ(t, f):
    return app()["summary"][t][f]


def mt(t, f):
    return app()["matched_rate"]["tests"][t][f]


def lp(case, c, p=PRIM):
    return S.J("b92_theta_audit9.json")["local_power"][case]["power"]["%s" % float(c)][p]


def gap(case, c, p=PRIM):
    return (lp(case, c, "envelope") - lp(case, c, p)) * C.PP


def attrib():
    return S.J("bB_attrib_audit12.json")


def anchor(n, f="exact"):
    return S.J("bF_anchor_audit12.json")["rows"][str(n)][f]


def mis(k, p=PRIM):
    return S.J("b92_theta_audit9.json")["misspec"][k]["rates"][p]


def shift(n, p=PRIM):
    m = S.J("b92_theta_audit9.json")["misspec"]
    ds = [m[k]["delta_vs_independent"][p]["delta"] for k in m if k.startswith("c|garch_") and k.endswith("_n%d" % n)]
    return sum(ds) / len(ds) * C.PP


def garch_inside(p):
    m = S.J("b92_theta_audit9.json")["misspec"]
    return sum(1 for k in m if k.startswith("c|garch_") and m[k]["rates"][p]["in_region"])


def d5():
    return S.J("e_dgp5_audit13.json")["cells"]


def dkw(N):
    return math.sqrt(math.log(2 / (1 - 0.95)) / (2 * N))


def kappa(cb):
    return 2 * abs(cb) * (0.5 + abs(cb) / 3)


def lam(cb):
    return cb ** 2 * (1 + abs(cb) + cb ** 2 / 3)


def theta_vs_v13():
    """Seccion 4.2: McNemar exacta gls_t0 frente a gls_t0.02 (b103_equalized, primaria = 0.02)."""
    e = S.J("b103_equalized_audit10.json")["cells"]
    pw = [k for k in e if k.startswith(("dgp1_", "ct_power_", "dgp2_"))]

    def r(k, p):
        return e[k]["rates_sim"][p]["rate"]
    uns = [k for k in pw if min(r(k, PRIM), r(k, V13P)) < 0.99 and max(r(k, PRIM), r(k, V13P)) > 0]
    up = [k for k in uns if e[k]["mcnemar_primary_vs_sim"][PRIM]["p_value"] < LEVEL and r(k, PRIM) > r(k, V13P)]
    dn = [k for k in uns if e[k]["mcnemar_primary_vs_sim"][PRIM]["p_value"] < LEVEL and r(k, PRIM) < r(k, V13P)]
    d3 = [k for k in e if k.startswith("dgp3_") and not k.startswith("dgp3_r1_")]
    less = [k for k in d3 if e[k]["mcnemar_primary_vs_sim"][PRIM]["p_value"] < LEVEL and r(k, PRIM) < r(k, V13P)]
    more = [k for k in d3 if e[k]["mcnemar_primary_vs_sim"][PRIM]["p_value"] < LEVEL and r(k, PRIM) > r(k, V13P)]
    uns5 = [k for k in pw if min(r(k, PRIM), r(k, V13P)) < 0.99]
    return {"unsaturated": uns, "unsaturated_reading5": len(uns5), "higher": up, "lower": dn, "max_lower_pp": max((r(k, V13P) - r(k, PRIM)) * C.PP for k in dn),
            "dgp3": d3, "less_distorted": less, "more_distorted": more,
            "definition": "no saturada: min(theta 0, theta 0.02) < 0.99 y max > 0 (excluye las 3 celdas delta = 5 con potencia nula)"}


# ---------------------------------------------------------------------------
# Registro: clave -> (archivo, plantilla, funcion) ; funcion -> (valores, fuente, comprobaciones)
# ---------------------------------------------------------------------------
def c_abs_limit():
    return [cal("c", 200), cal("ct", 60)], "e_calib_audit13.json cases_by_theta.gls_t0.<c|ct>.approximation_cost.<n>.size_with_cv_n20000", []


def c_msb_pub200():
    return [calc("ct", 200, "msb")["rate"]], "e_calib_audit13.json ...ct.approximation_cost_comparators.200.msb.size_published_asymptotic", []


def c_attr_means():
    b = attrib()["by_n"]["c|200"]
    return [b["a_minus_b"]["mean"] * C.PP, b["a_minus_bp"]["mean"] * C.PP], "bB_attrib_audit12.json by_n.c|200.<a_minus_b|a_minus_bp>.mean", []


def c_ma_042():
    return [sz("ma_m0p8", 200, "c"), sz("ma_m0p8", 200, "c", "glsb_t0")], "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.iid.<gls_t0|glsb_t0>", []


def c_cover_msb():
    return [calc("ct", 200, "msb")["rate"] * C.PP], "e_calib_audit13.json ...ct.200.msb.size_published_asymptotic (x100)", []


def c_kappa():
    return [kappa(CBAR())], "formula kappa = 2|c|(1/2 + |c|/3), c = -7", []


def c_exact200():
    return [anchor(200)], "bF_anchor_audit12.json rows.200.exact", []


def c_intro_lim():
    return [cal("c", 200), cal("ct", 60), cal("c", 200, "size_with_cv_at_n"), cal("ct", 60, "size_with_cv_at_n")], \
        "e_calib_audit13.json approximation_cost.<n>.<size_with_cv_n20000|size_with_cv_at_n>", []


def c_intro_pub():
    return [calc("ct", 200, "msb")["rate"], calc("ct", 60, "msb")["rate"], calc("ct", 200, "dfgls")["rate"]], \
        "e_calib_audit13.json approximation_cost_comparators (publicado)", []


def c_factor54():
    b = szc("ma_m0p8", 200, "c")["bartlett_factor_at_median_B"]
    return [b["factor"]], "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.bartlett_factor_at_median_B.factor (B = %d)" % b["B"], []


def c_intro_ma():
    return [sz("ma_m0p8", 200, "c"), sz("ma_m0p8", 200, "c", "glsb_t0")], "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.iid", []


def c_intro_ar05():
    return [sz("ar_0p5", 200, "ct")], "bA_ma_audit12.json size.sz_ar_0p5_n200_ct.iid.gls_t0", []


def c_intro_dgp3():
    k = "dgp3_r4_n200"
    loss = max(v["power_loss_pp"] for c, v in S.J("e_awb_audit13.json")["cells"].items() if c.startswith("dgp1_"))
    return [eq(k), eq(k, "dfgls"), eq(k, "adf"), awbc(k), loss], "e_equalized_audit13.json dgp3_r4_n200; e_awb_audit13.json", []


def c_intro_init():
    gls = ("gls_t0", "gls_t0.02", "glsb_t0", "glsbp_t0", "dfgls", "mzt", "msb")
    return [max(ini("0p9", "alpha2", p) for p in gls), ini("0p9", "alpha2", "adf"), ini("0p9", "alpha1", PRIM),
            ini("0p9", "alpha1", "dfgls")], "bC_initial_audit12.json cells.0.9|<alpha2|alpha1>.power", []


def c_248():
    t = S.J("t5_claims_audit11.json")["claims"]["3"]["by_case"]["dm"]["0.1"]
    return [t["cost_pp"]], "t5_claims_audit11.json claims.3.by_case.dm.0.1.cost_pp (A8 B4)", []


def c_invariance():
    v = S.J("b1_validation_audit8.json")["V4_gls"]
    inv = max(v["invariance"]["worst_rel_diff"].values())
    dr = v["drift"]["worst_rel_diff_rm_gls_ct"]
    return [inv * 10 ** 13, dr * 10 ** 15], "b1_validation_audit8.json V4_gls.invariance.worst_rel_diff (max c, ct); V4_gls.drift.worst_rel_diff_rm_gls_ct", []


def c_endpoint():
    c = S.J("b102_identity_audit10.json")["cells"]
    return [c["dm|200"]["endpoint_term_share_of_rm2"]["median"] * C.PP, c["dm|1000"]["endpoint_term_share_of_rm2"]["median"] * C.PP], \
        "b102_identity_audit10.json cells.dm|<200|1000>.endpoint_term_share_of_rm2.median (x100)", []


def c_identity():
    return [S.J("b102_identity_audit10.json")["worst_ii"] * 10 ** 15], "b102_identity_audit10.json worst_ii", []


def c_kappa_lambda():
    return [kappa(CBAR()), lam(CBAR())], "formulas kappa y lambda con c = -7; bF_anchor_audit12.json config.<kappa|lambda>", \
        [("kappa del JSON = formula", abs(S.J("bF_anchor_audit12.json")["config"]["kappa"] - kappa(CBAR())) < 10 ** -12),
         ("lambda del JSON = formula", abs(S.J("bF_anchor_audit12.json")["config"]["lambda"] - lam(CBAR())) < 10 ** -9)]


def c_exact3():
    return [anchor(200), anchor(500), anchor(2000)], "bF_anchor_audit12.json rows.<n>.exact", []


def c_within():
    return [S.J("bF_anchor_audit12.json")["gate"]["worst"] * 10 ** 4, anchor(200, "first_order_A11")], \
        "bF_anchor_audit12.json gate.worst (max |formula - exacta|, n >= 200); rows.200.first_order_A11", []


def c_mabias_b8():
    b = szc("ma_m0p8", 200, "c")["bartlett_factor_at_median_B"]
    return [b["B"], b["factor"]], "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.bartlett_factor_at_median_B", []


def c_ar_factors():
    fm = szc("ar_m0p5", 200, "c")["bartlett_factor_at_median_B"]["factor"]
    fp = szc("ar_0p5", 200, "c")["bartlett_factor_at_median_B"]["factor"]
    same = all(szc(e, 200, "ct")["bartlett_factor_at_median_B"]["factor"] == szc(e, 200, "c")["bartlett_factor_at_median_B"]["factor"]
               for e in ("ar_m0p5", "ar_0p5"))
    return [fm, fp], "bA_ma_audit12.json size.sz_ar_<m0p5|0p5>_n200_c.bartlett_factor_at_median_B.factor", [("igual en c y ct", same)]


def c_slopes():
    t = S.J("t4_trend_audit11.json")["by_rho"]
    return [t["0.5"]["quantities"]["resid_ms"]["slope"], t["0.9"]["quantities"]["resid_ms"]["slope"],
            t["0.5"]["quantities"]["statistic"]["slope"], t["0.9"]["quantities"]["statistic"]["slope"]], \
        "t4_trend_audit11.json by_rho.<0.5|0.9>.quantities.<resid_ms|statistic>.slope", []


def c_dkw():
    return [dkw(10 ** 5), dkw(5 * 10 ** 5)], "formula DKW-Massart: eps = sqrt(ln(2/0.05)/(2 N_cal))", []


def c_mismatch():
    r = S.J("b2_size_audit8.json")["paso0"]["cells"]["gauss_n200"]["published_rates"]["rm_R0.5_t0.1_one"]
    return [r], "b2_size_audit8.json paso0.cells.gauss_n200.published_rates.rm_R0.5_t0.1_one (calibracion sigma = 1)", []


def c_gamma():
    import audit9_engine as E
    return [E.awb_gamma(200)[0], E.awb_gamma(500)[0]], "formula gamma = 0.01^(1/l), l = round(1.75 (n+1)^(1/3)) (audit9_engine.awb_gamma)", []


def c_rule_P():
    P = S.J("b92_theta_audit9.json")["theta_rule"]["P"]
    return [P[C.tname(t)] for t in THETAS()], "b92_theta_audit9.json theta_rule.P", []


def c_rule_worst():
    a = S.J("b101_theta_audit10.json")["A1prime"]
    return [max(v["abs_dev_from_alpha"] for t in THETAS() for v in a[C.tname(t)].values()) * C.PP], \
        "b101_theta_audit10.json A1prime.<theta>.<celda>.abs_dev_from_alpha (max, x100)", []


def c_rule_amend():
    r = S.J("b92_theta_audit9.json")["theta_rule"]
    a1 = r["A1"]
    fails = [t for t in THETAS() if not all(v["in_region"] for v in a1[C.tname(t)].values())]
    cells = {k for t in fails for k, v in a1[C.tname(t)].items() if not v["in_region"]}
    reg = S.J("b92_theta_audit9.json")["exact_region_20000"]
    margin = max(min(abs(v["rate"] - reg[0]), abs(v["rate"] - reg[1])) for t in fails for k, v in a1[C.tname(t)].items()
                 if not v["in_region"])
    b = S.J("b101_theta_audit10.json")["A1prime"]
    ct = [v["ct|200"]["rate"] for v in b.values() if "ct|200" in v]
    return [len(fails), min(ct), max(ct)], "b92_theta_audit9.json theta_rule.A1; b101_theta_audit10.json A1prime.<proc>.ct|200", \
        [("todas las fallas en una sola celda (ct|200)", cells == {"ct|200"}), ("margen < 0.001", margin < 10 ** -3)]


def c_rule_a2():
    d = S.J("b92_theta_audit9.json")["theta_rule"]["A2_mean_delta"]
    return [abs(d[PRIM]["mean"] - d[V13P]["mean"]) * C.PP], "b92_theta_audit9.json theta_rule.A2_mean_delta (|theta 0 - theta 0.02|, x100)", []


def c_sec42():
    t = theta_vs_v13()
    return [len(t["higher"]), len(t["unsaturated"]), len(t["lower"]), t["max_lower_pp"], len(t["less_distorted"]), len(t["dgp3"])], \
        "b103_equalized_audit10.json cells.<celda>.mcnemar_primary_vs_sim.gls_t0 (primaria theta 0.02) y rates_sim; %s" % t["definition"], \
        [("ninguna celda de DGP 3 mas distorsionada", not t["more_distorted"])]


def c_sec42_ma():
    return [sz("ma_m0p8", 200, "c"), sz("ma_m0p8", 200, "ct"), sz("ma_m0p8", 200, "c", V13P), sz("ma_m0p8", 200, "ct", V13P)], \
        "bA_ma_audit12.json size.sz_ma_m0p8_n200_<c|ct>.iid.<gls_t0|gls_t0.02>", []


def c_region5000():
    return list(C.exact_region(5000)), "formula: region binomial exacta de N = 5000 (audit9_common.exact_region)", []


def c_size_text():
    es = S.J("e_size_audit13.json")["cells"]
    k = max(es, key=lambda k: abs(es[k]["rates"][PRIM]["rate"] - LEVEL))
    c = es[k]
    return [abs(c["rates"][PRIM]["rate"] - LEVEL) * C.PP, c["n"], c["rates"][PRIM]["rate"], c["rates"][V13P]["rate"],
            c["a10_lown"]["theta0"]["rate"]], "e_size_audit13.json cells.%s" % k, \
        [("celda de tendencia a n = 100", k == "ct|100"), ("fuera de la region de 5e4", not c["rates"][PRIM]["in_region"]),
         ("todas dentro de 0.25 pp", all(abs(v["rates"][PRIM]["rate"] - LEVEL) <= S.J("b101_theta_audit10.json")["config"]["tolerance"]
                                         for v in es.values()))]


def c_calib_text():
    return [cal("c", 60), cal("c", 100), cal("c", 200), cal("c", 60, "size_with_cv_at_n"), cal("c", 100, "size_with_cv_at_n"),
            cal("c", 200, "size_with_cv_at_n"), cal("ct", 60), cal("ct", 100), cal("ct", 200), cal("ct", 60, "size_with_cv_at_n"),
            cal("ct", 100, "size_with_cv_at_n"), cal("ct", 200, "size_with_cv_at_n")], "e_calib_audit13.json approximation_cost", []


def c_ks():
    ks = S.J("e_calib_audit13.json")["cases_by_theta"][PRIM]
    c_ok = all(not v["below_threshold"] for v in ks["c"]["ks"].values())
    ct_above = sorted(int(n) for n, v in ks["ct"]["ks"].items() if not v["below_threshold"])
    return [ks["c"]["ks"]["200"]["D"], ks["c"]["ks"]["1000"]["D"], max(ct_above)], "e_calib_audit13.json cases_by_theta.gls_t0.<c|ct>.ks", \
        [("constante: por encima del umbral en todo n hasta 5000", c_ok),
         ("tendencia: por encima del umbral exactamente hasta 1000", ct_above == [n for n in sorted(int(x) for x in ks["ct"]["ks"]) if n <= max(ct_above)])]


def c_pub_trend():
    sims = [calc("ct", n, p, "size_simulated_at_n")["in_region"] for n in (60, 100, 150, 200, 500, 1000, 2000, 5000) for p in ("msb", "dfgls")]
    return [calc("ct", 60, "msb")["rate"], calc("ct", 200, "msb")["rate"], calc("ct", 1000, "msb")["rate"], calc("ct", 200, "dfgls")["rate"]], \
        "e_calib_audit13.json approximation_cost_comparators (tendencia)", [("con cv simulado, ambos dentro en todo n", all(sims))]


def c_calib_out():
    reg = S.J("e_calib_audit13.json")["exact_region_20000"]
    outs = [(c, n) for c in ("c", "ct") for n in (60, 100, 150, 200, 500, 1000, 2000, 5000)
            if not S.J("e_calib_audit13.json")["cases_by_theta"][PRIM][c]["approximation_cost"][str(n)]["size_with_cv_at_n"]["in_region"]]
    return [cal("c", 60, "size_with_cv_at_n"), (cal("c", 60, "size_with_cv_at_n") - reg[1]) * C.PP], \
        "e_calib_audit13.json approximation_cost.60.size_with_cv_at_n; exact_region_20000", [("unica celda calibrada fuera", outs == [("c", 60)])]


def c_calib_note():
    ks = S.J("e_calib_audit13.json")["cases_by_theta"][PRIM]
    return list(C.exact_region(20000)) + [ks["c"]["cv_n20000"], ks["ct"]["cv_n20000"]], "formula exact_region(20000); e_calib_audit13.json cv_n20000", []


def c_lp_text():
    lpd = [gap("dm", c) for c in (5, 10, 15)] + [gap("dm", c, "msb") for c in (5, 10, 15)]
    half = sum(gap("dm", c, "msb") - gap("dm", c) for c in (5, 10, 15)) / 3
    cs = LP_C()
    tr = max(gap("ct", c, p) for c in cs for p in (PRIM, "dfgls", "mzt", "msb"))
    th = [(lp("dm", c) - lp("dm", c, V13P)) * C.PP for c in cs if 5 <= c <= 15]
    lad = [gap("dm", 10, C.tname(t)) for t in THETAS()]
    return lpd + [tr, min(th), max(th)] + lad, "b92_theta_audit9.json local_power.<dm|ct>.power", \
        [("'about half a point': media de MSB - primaria en c = 5, 10, 15 = %.2f pp (redondea a medio punto si round(2 x) = 1)" % half,
          round(half * 2) == 1)]


def c_lp_se():
    return [max(math.sqrt(p * (1 - p) / 20000) for case in ("dm", "ct") for c in LP_C()
                for p in (lp(case, c, q) for q in ("envelope", PRIM, V13P, "dfgls", "mzt", "msb", "msb_asy")))], \
        "b92_theta_audit9.json local_power (EE binomial con N = 2e4)", []


def c_power200():
    k = {r: "dgp1_rho%s_n200" % TB.rtag(r) for r in (0.8, 0.85, 0.9, 0.93, 0.95, 0.97)}
    return [dd(k[0.9]), eq(k[0.9]), eq(k[0.9], "dfgls"), dd(k[0.93]), dd(k[0.8]), dd(k[0.85]), dd(k[0.95]), eqp(k[0.95]),
            -dd(k[0.97]), eqp(k[0.97])], "e_equalized_audit13.json dgp1_rho<rho>_n200", \
        [("p < 1e-4 en rho = 0.90 y 0.93", eqp(k[0.9]) < 10 ** -4 and eqp(k[0.93]) < 10 ** -4)]


def c_power500():
    return [dd("dgp1_rho0p97_n500"), -dd("dgp1_rho0p99_n500"), -dd("dgp1_rho0p99_n1000"),
            (eq("dgp1_rho0p99_n1000") - eq("dgp1_rho0p99_n1000", "adf")) * C.PP,
            (eq("dgp1_rho0p99_n1000") - eq("dgp1_rho0p99_n1000", "pp")) * C.PP], "e_equalized_audit13.json dgp1", []


def c_power_trend():
    rows = C.read_json("tables_audit13.json")["tables"]["ctpower"]["rows"]
    keys = ["ct_power_rho%s_n%d" % (TB.rtag(TB.num(r["keys"][0])), int(TB.num(r["keys"][1]))) for r in rows]
    return [dd("ct_power_rho0p9_n200"), dd("ct_power_rho0p95_n500"), sum(1 for k in keys if eqp(k) >= LEVEL)], \
        "e_equalized_audit13.json ct_power; filas de tab:ctpower", []


def c_attr_text():
    b = attrib()["by_n"]
    lpv = [attrib()["cells"]["lp_dm_c%d" % c]["diffs"]["a_minus_bp"]["delta"] * C.PP for c in (5, 10, 15)]
    size = (calc("ct", 200, "msb", "size_simulated_at_n")["rate"] - calc("ct", 200, "msb")["rate"]) * C.PP
    return [b["c|200"]["a_minus_b"]["mean"] * C.PP, b["c|500"]["a_minus_b"]["mean"] * C.PP, b["c|1000"]["a_minus_b"]["mean"] * C.PP,
            b["ct|200"]["a_minus_b"]["mean"] * C.PP, b["c|200"]["bp_minus_b"]["mean"] * C.PP, b["c|200"]["a_minus_bp"]["mean"] * C.PP,
            min(lpv), max(lpv), size, b["ct|200"]["b_minus_c"]["mean"] * C.PP], \
        "bB_attrib_audit12.json by_n y lp_dm_c<c>; tamano: e_calib_audit13.json ct.200 msb (simulado - publicado)", []


def c_attr_diag():
    d = attrib()["diagnostics_n200"]
    ks = [d["dgp1_rho%s_n200" % TB.rtag(r)]["k_gls"] for r in (0.9, 0.93, 0.95, 0.97, 0.99)]
    return [d["dgp1_rho0p9_n200"]["s2ar_gls"], d["dgp1_rho0p93_n200"]["s2ar_gls"], d["dgp1_rho0p9_n200"]["s2_hac"],
            d["dgp1_rho0p93_n200"]["s2_hac"]], "bB_attrib_audit12.json diagnostics_n200 (medianas)", \
        [("MAIC sin retardos en la mediana para rho >= 0.90", all(k == 0 for k in ks))]


def c_serial1():
    return [sz("ma_m0p8", 200, "c"), sz("ma_m0p8", 200, "ct"), sz("ma_m0p8", 500, "c"), sz("ma_m0p8", 500, "ct"),
            min(sz("ma_m0p5", n, c) for n in (200, 500) for c in ("c", "ct")),
            max(sz("ma_m0p5", n, c) for n in (200, 500) for c in ("c", "ct")),
            szc("ma_m0p8", 200, "c")["diagnostics"]["s2_over_omega2"]["median"],
            szc("ma_m0p8", 200, "c")["bartlett_factor_at_median_B"]["factor"],
            sz("ma_0p5", 200, "ct"), sz("ar_0p5", 200, "ct"), sz("ar_0p5", 100, "ct"), sz("ma_m0p8", 100, "ct")], \
        "bA_ma_audit12.json size.<celda>.iid.gls_t0; diagnostics; bartlett_factor_at_median_B", []


def serial_cells():
    return list(S.J("bA_ma_audit12.json")["size"].values())


def c_serial2():
    cells = serial_cells()
    b = [c["iid"]["glsb_t0"]["rate"] for c in cells]
    a = [c["iid"][PRIM]["rate"] for c in cells]
    def gapb(c):
        return max(abs(c["iid"]["msb"]["rate"] - c["iid"]["glsb_t0"]["rate"]), abs(c["iid"]["mzt"]["rate"] - c["iid"]["glsb_t0"]["rate"]))
    worst = max(cells, key=gapb)
    half = gapb(worst) * C.PP
    pp08 = min(c["iid"]["pp"]["rate"] for c in cells if c["err_tag"] == "ma_m0p8")
    return [len(cells), min(b), max(b), min(a), max(a), sz("ma_m0p8", 200, "c", "glsb_t0"), sz("ma_m0p8", 200, "ct", "glsb_t0"),
            max(c["iid"]["dfgls"]["rate"] for c in cells), max(c["iid"]["adf"]["rate"] for c in cells)], \
        "bA_ma_audit12.json size (36 celdas, bloque iid)", \
        [("MSB-GLS y MZ_t-GLS a menos de medio punto de (b) en todas las celdas (max %.2f pp, celda %s n = %d %s)"
          % (half, worst["err_tag"], worst["n"], worst["case"]), half <= 0.5),
         ("PP rechaza casi siempre a psi = -0.8 (min %.3f)" % pp08, pp08 >= 0.95)]


def c_serial3():
    d = szc("ma_m0p8", 200, "c")["diagnostics"]
    return [d["k"]["median"], d["s2ar_over_omega2"]["median"], sz("ma_m0p8", 200, "c", V13P), sz("ma_m0p8", 200, "ct", V13P)], \
        "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.diagnostics; iid.gls_t0.02", []


def c_initial():
    gls = ("gls_t0", "gls_t0.02", "glsb_t0", "glsbp_t0", "dfgls", "mzt", "msb")
    a4 = [ini("0p9", "alpha4", p) for p in gls]
    return [max(ini("0p9", "alpha2", p) for p in gls), ini("0p9", "alpha2", "adf"), ini("0p9", "alpha4", "adf"), ini("0p9", "alpha2", "pp"),
            ini("0p9", "alpha4", "pp"), ini("0p9", "alpha1", PRIM), ini("0p9", "alpha1", "dfgls"), ini("0p9", "alpha1", "glsb_t0"),
            ini("0p9", "alpha1", "msb"), ini("0p9", "random", PRIM), ini("0p9", "random", "dfgls")], "bC_initial_audit12.json cells.0.9|<variante>.power", \
        [("a alpha = 4 todos los GLS rechazan 0.000 (max %.4f)" % max(a4), TB.fdec(max(a4), 3) == TB.fdec(0.0, 3))]


def c_dgp2():
    e = S.J("e_equalized_audit13.json")["cells"]

    def k(d, n):
        return "dgp2_delta%s_n%d" % (TB.rtag(d), n)
    lead = [kk for kk in e if kk.startswith("dgp2_") and 0.5 <= e[kk]["delta"] <= 3 and min(eq(kk), eq(kk, "dfgls")) < 0.99]
    wins = [kk for kk in lead if eq(kk) > eq(kk, "dfgls")]
    hi_p = [kk for kk in wins if eqp(kk) >= P01]
    vals = [eq(k(0, 200)), eq(k(0, 200), "dfgls"), eqp(k(0, 200))]
    for d, n in ((1, 200), (2, 500), (2, 1000), (3, 1000)):
        vals += [eq(k(d, n)), eq(k(d, n), "dfgls")]
    return vals, "e_equalized_audit13.json dgp2", \
        [("lidera en toda celda no saturada con 0.5 <= delta <= 3", len(wins) == len(lead)),
         ("p < 0.01 salvo (3, 200): %s" % hi_p, hi_p == [k(3, 200)]),
         ("en (3, 200) ambos por debajo de 0.01", max(eq(k(3, 200)), eq(k(3, 200), "dfgls")) < P01)]


def c_za():
    a8 = S.J("b5_power_audit8.json")["za_size"]
    e = S.J("e_equalized_audit13.json")["cells"]
    ex = sorted(kk for kk in e if kk.startswith("dgp2_") and eq(kk, "za") > eq(kk))
    return [eq("dgp2_delta0_n200", "za"), eq("dgp2_delta0_n200"), eq("dgp2_delta5_n200", "za"), eq("dgp2_delta5_n500", "za"),
            eq("dgp2_delta5_n1000", "za")] + [a8["za_%s_n%d" % (kind, n)]["rates"]["za"]["rate"] for kind in ("rw", "rwbreak")
                                              for n in (200, 500, 1000)], \
        "e_equalized_audit13.json dgp2 (za); b5_power_audit8.json za_size.<za_rw|za_rwbreak>_n<n>.rates.za", \
        [("ZA supera a la primaria en delta = 3 (todo n) y (2, 200): %s" % ex,
          set(ex) >= {"dgp2_delta3_n200", "dgp2_delta3_n500", "dgp2_delta3_n1000", "dgp2_delta2_n200"})]


def c_dgp3():
    k4 = "dgp3_r4_n200"
    return [eq(k4), eq("dgp3_r4_n500"), eq("dgp3_r4_n1000"), eq(k4, "mzt"), eq(k4, "dfgls"), eq(k4, "rm_t0.1")], \
        "e_equalized_audit13.json dgp3_r4_n<n>", [("RM menos distorsionado que la primaria", eq(k4, "rm_t0.1") < eq(k4))]


def c_awb_text():
    cells = S.J("e_awb_audit13.json")["cells"]
    rule = S.J("e_awb_audit13.json")["rule"]
    rest = [v["power_loss_pp"] for c, v in cells.items() if c.startswith("dgp1_") and c != "dgp1_rho0p95_n200"]
    a7 = S.J("dgp3_recast_composite_null_audit7.json")["cells"]
    aw = [v["bootstrap_dfgls"]["rate"] for v in a7.values()]
    return [awbc("dgp3_r2_n200"), awbc("dgp3_r2_n500"), awbc("dgp3_r2_n200", "sim"), awbc("dgp3_r2_n500", "sim"),
            awbc("dgp3_r4_n200"), awbc("dgp3_r4_n500"), awbc("dgp3_r4_n200", "sim"), awbc("dgp3_r4_n500", "sim"),
            awbc("indep_n200"), awbc("indep_n500"), cells["dgp1_rho0p95_n200"]["power_loss_pp"], max(rest),
            rule["ii_threshold_pp"] - max(rule["ii_power_loss_pp"].values()), min(aw), max(aw)], \
        "e_awb_audit13.json cells y rule; dgp3_recast_composite_null_audit7.json cells.<celda>.bootstrap_dfgls (experimento aparte, A7)", \
        [("GARCH: AWB <= simulada en las cuatro", all(v["awb"]["rate"] <= v["sim"]["rate"] for c, v in cells.items() if c.startswith("garch"))),
         ("primera condicion con igualdad", rule["i_in_region_dgp3"] == rule["i_min"])]


def c_misspec():
    return [mis("c|heavy_t5_n200")["rate"], mis("c|heavy_t3_n200")["rate"], shift(200), shift(200, "dfgls"), shift(200, "mzt"),
            shift(200, "adf"), shift(1000), shift(1000, "dfgls"), shift(1000, "mzt"), shift(1000, "adf"),
            garch_inside(PRIM), garch_inside("dfgls"), garch_inside("msb"), garch_inside("adf"), garch_inside("adf_asy"),
            garch_inside("pp_asy")], "b92_theta_audit9.json misspec (16 celdas GARCH, caso constante)", \
        [("DF-GLS y MZ_t-GLS con el mismo recuento", garch_inside("dfgls") == garch_inside("mzt"))]


def c_dgp5():
    cells = d5()
    inter = [v for v in cells.values() if v["r"] in (2.0, 3.0)]
    g2 = [v["g2_share_R050_median"] * C.PP for v in cells.values()]
    rows = C.read_json("tables_audit13.json")["tables"]["dgp5"]["rows"]
    import audit7_design as D7
    keys = [D7.dgp5_tag(200, TB.num(r["keys"][0]), float(TB.num(r["keys"][1]))) for r in rows]

    def gapc(v):
        return (v["size_matched"]["primary"]["rate"] - v["size_matched"]["proposed_R050"]["rate"]) * C.PP
    return [min(v["size_matched"]["union_joint"]["rate"] for v in inter), max(v["size_matched"]["union_joint"]["rate"] for v in inter),
            min(v["size_matched"]["proposed_R050"]["rate"] for v in inter), max(v["size_matched"]["proposed_R050"]["rate"] for v in inter),
            min(g2), max(g2), min(gapc(cells[k]) for k in keys), max(gapc(cells[k]) for k in keys), min(gapc(v) for v in cells.values()),
            S.J("e_dgp5_audit13.json")["a7_joint_alpha_star"]], "e_dgp5_audit13.json cells; a7_joint_alpha_star", \
        [("supera al bootstrap para r >= 1.5", all(v["size_matched"]["primary"]["rate"] > v["size_matched"]["bootstrap_dfgls"]["rate"]
                                                    for v in cells.values() if v["r"] >= 1.5)),
         ("supera a la union para r <= 1.25", all(v["size_matched"]["primary"]["rate"] > v["size_matched"]["union_joint"]["rate"]
                                                   for v in cells.values() if v["r"] <= 1.25)),
         ("la union domina en el interior", all(v["size_matched"]["union_joint"]["rate"] > v["size_matched"]["primary"]["rate"] for v in inter))]


def c_negative():
    t = S.J("t5_claims_audit11.json")["claims"]
    return [t["1"]["max_abs_delta_pp"], t["2"]["operative"]["min"], t["2"]["operative"]["max"],
            t["3"]["by_case"]["dm"]["0.1"]["cost_pp"], t["3"]["by_case"]["dm"]["0.1"]["gap_rm_pp"]], \
        "t5_claims_audit11.json claims.1 (b2_size_audit8), claims.2 (adaptive_size_power_audit5b), claims.3 (A8 B4)", []


def c_app_oos():
    o = app()["oos_size"]["by_D"]
    a = app()["oos_size_awb"]["by_D"]
    return [o[d]["rate"] for d in ("150", "200", "250", "300")] + [a["250"]["rate"]], "e_application_audit13.json oos_size y oos_size_awb", \
        [("theta 0: las cuatro dentro", all(v["in_region"] for v in o.values())), ("AWB D = 250 por debajo de la region",
                                                                                   a["250"]["rate"] < app()["oos_size_awb"]["region"][0])]


def c_app_counts():
    s = app()["summary"]["final"]
    return [len(app()["fp_cells"]["final"]), s["event_cells"]], "e_application_audit13.json fp_cells.final; summary.final.event_cells", []


def c_app_res():
    return [summ("final", "fp_mean"), summ("adf", "fp_mean"), summ("pp", "fp_mean"), summ("dfgls_maic", "fp_mean"),
            summ("final", "detections"), summ("adf", "detections"), summ("pp", "detections"), summ("dfgls_maic", "detections"),
            summ("mzt", "fp_mean"), summ("mzt", "detections"), summ("mzt", "mean_latency_detected"), summ("final", "mean_latency_detected"),
            summ("final_awb", "fp_mean"), summ("final_awb", "detections")], "e_application_audit13.json summary", []


def c_app_matched():
    return [app()["matched_rate"]["target_fpr_pooled_primary"], mt("final", "false_alarm_episodes"),
            mt("final", "false_alarm_episodes") - mt("dfgls_aic", "false_alarm_episodes"), mt("adf", "false_alarm_episodes"),
            mt("pp", "false_alarm_episodes"), mt("final", "censored_latency_mean"), mt("dfgls_aic", "censored_latency_mean"),
            mt("mzt", "censored_latency_mean"), len(app()["adverse_cells_primary"]), mt("rhat_prereg", "false_alarm_episodes"),
            summ("rhat_prereg", "detections")], "e_application_audit13.json matched_rate, adverse_cells_primary, summary", []


def c_app_target():
    return [app()["matched_rate"]["target_fpr_pooled_primary"]], "e_application_audit13.json matched_rate.target_fpr_pooled_primary", []


def dev8(i, side, f):
    return S.J("deviation_table_audit8.json")["rows"][i][side][f] if side.startswith("effect") else S.J("deviation_table_audit8.json")["rows"][i][side]


def c_dev_pilot():
    return [dev8(0, "preregistered_value", None), dev8(0, "deployed_value", None)], "deviation_table_audit8.json rows[0] (i, A5bis)", []


def c_dev_stat():
    a13 = app()["summary"]
    v13 = S.J("b103_application_audit10.json")["summary"]
    return [a13["rhat_prereg"]["fp_mean"], a13["final"]["fp_mean"], a13["rhat_prereg"]["detections"], a13["final"]["detections"],
            a13["rhat_prereg"]["mean_latency_detected"], a13["final"]["mean_latency_detected"],
            v13["final"]["fp_mean"], a13["final"]["fp_mean"], v13["final"]["detections"], a13["final"]["detections"],
            v13["final"]["mean_latency_detected"], a13["final"]["mean_latency_detected"]], \
        "e_application_audit13.json summary; b103_application_audit10.json summary.final (theta 0.02)", []


def c_dev_cal():
    return [dkw(5 * 10 ** 4)], "formula DKW con N_cal = 5e4 (deviation_table_audit8.json rows[1])", []


def c_dev_awb():
    a = app()["summary"]
    return [a["final"]["fp_mean"], a["final_awb"]["fp_mean"], a["final"]["detections"], a["final_awb"]["detections"],
            a["final"]["mean_latency_detected"], a["final_awb"]["mean_latency_detected"]], "e_application_audit13.json summary", []


def c_concl():
    return [(LEVEL - calc("ct", 200, "msb")["rate"]) * C.PP, (LEVEL - calc("ct", 60, "msb")["rate"]) * C.PP,
            sz("ma_m0p8", 200, "c")], "e_calib_audit13.json comparadores publicados (tendencia); bA_ma_audit12.json", []


def c_concl25():
    return [S.J("t5_claims_audit11.json")["claims"]["3"]["by_case"]["dm"]["0.1"]["cost_pp"]], "t5_claims_audit11.json claims.3", []


def c_appA():
    return [1 / (1 + 49 / 200), anchor(200), anchor(500), anchor(2000), anchor(200, "first_order_A11"),
            anchor(500, "first_order_A11"), anchor(2000, "first_order_A11")], "formula (1 + c^2/n)^-1; bF_anchor_audit12.json rows", []


def c_appB():
    t = S.J("b103_cv_audit10.json")["table"]
    return [max(e["max_se"] for e in t.values() if e["theta"] == C.THETA), t["dm|0|100"]["cv"]["0.05"], t["dm|0|1000"]["cv"]["0.05"],
            t["ct|0|100"]["cv"]["0.05"], t["ct|0|1000"]["cv"]["0.05"]], "b103_cv_audit10.json table.<caso>|0|<n>", []


def c_appC():
    return [], "disenio", []


CLAIMS = [
    ("abstract_limit", "main.tex", "rejects $<>$ at $n = 200$ in the constant case and $<>$ at $n = 60$ in the trend case", c_abs_limit, ()),
    ("abstract_msb", "main.tex", "asymptotic critical values of MSB-GLS reject $<>$ at $n = 200$", c_msb_pub200, ()),
    ("abstract_attrib", "main.tex", "by $<>$ percentage points on average, $<>$ of which survive", c_attr_means, ()),
    ("abstract_ma", "main.tex", "the calibrated test rejects $<>$ at $n = 200$, against $<>$ with the autoregressive scale", c_ma_042, ()),
    ("cover_msb", "cover_letter.md", "(a rejection rate of <> per cent at n = 200)", c_cover_msb, ()),
    ("cover_attrib", "cover_letter.md", "raises power by <> points on average at n = 200", lambda: (c_attr_means()[0][:1], c_attr_means()[1], []), ()),
    ("cover_ma", "cover_letter.md", "the calibrated test rejects <> at n = 200, against <> with the autoregressive scale", c_ma_042, ()),
    ("intro_248", "sec1_introduction.tex", "cost $<>$ points of local power at $c = 10$", c_248, ()),
    ("intro_kappa", "sec1_introduction.tex", "with $\\kappa(-7) \\approx <>$", c_kappa, ()),
    ("intro_exact", "sec1_introduction.tex", "squared statistic is $<>$ at $n = 200$", c_exact200, ()),
    ("intro_limit", "sec1_introduction.tex", "gives a rejection rate of $<>$ at $n = 200$ in the constant case and $<>$ at $n = 60$ in the trend "
     "case, against $<>$ and $<>$ with the value simulated at $n$", c_intro_lim, ()),
    ("intro_pub", "sec1_introduction.tex", "MSB-GLS rejects $<>$ at $n = 200$ and $<>$ at $n = 60$, and DF-GLS $<>$ at $n = 200$", c_intro_pub, ()),
    ("intro_attrib", "sec1_introduction.tex", "raises power by $<>$ percentage points on average over seven autoregressive alternatives at "
     "$n = 200$, of which $<>$ survive", c_attr_means, ()),
    ("intro_factor", "sec1_introduction.tex", "(\\cref{rem:mabias}), $<>$ at $\\psi = -0.8$", c_factor54, ()),
    ("intro_ma", "sec1_introduction.tex", "the calibrated test then rejects $<>$ in the constant case, against $<>$ with the autoregressive scale",
     c_intro_ma, ()),
    ("intro_ar05", "sec1_introduction.tex", "it rejects $<>$ at $n = 200$ in the trend case with autoregressive errors", c_intro_ar05, ()),
    ("intro_dgp3", "sec1_introduction.tex", "rejects $<>$ at $n = 200$ and a fourfold standard-deviation ratio, as much as MSB-GLS and more "
     "than DF-GLS ($<>$) or ADF ($<>$); a wild-bootstrap calibration of the same statistic brings the rate to $<>$, at a power cost of at "
     "most $<>$ points", c_intro_dgp3, (4,)),
    ("intro_initial", "sec1_introduction.tex", "no GLS-based test rejects more than $<>$, while ADF rejects $<>$. The Bartlett scale loses the "
     "least at a moderate initial condition, rejecting $<>$ against $<>$ for DF-GLS", c_intro_init, (0,)),
    ("sec2_248", "sec2_statistic.tex", "loses $<>$ points of local power at $c = 10$", c_248, ()),
    ("sec2_invariance", "sec2_statistic.tex", "worst relative discrepancy of $<>\\times10^{-13}$ and the independence of the drift, with common "
     "random numbers, to $<>\\times10^{-15}$", c_invariance, ()),
    ("sec2_endpoint", "sec2_statistic.tex", "is $<>$ per cent at $n = 200$ and $<>$ per cent at $n = 1000$", c_endpoint, ()),
    ("sec2_identity", "sec2_statistic.tex", "discrepancy of $<>\\times 10^{-15}$ in both cases", c_identity, ()),
    ("sec3_kappa_lambda", "sec3_theory.tex", "$\\kappa(-7) \\approx <>$ and $\\lambda(-7) \\approx <>$", c_kappa_lambda, ()),
    ("sec3_exact", "sec3_theory.tex", "is $<>$ at $n = 200$, $<>$ at $n = 500$ and $<>$ at $n = 2000$", c_exact3, ()),
    ("sec3_within", "sec3_theory.tex", "to within $<>\\times10^{-4}$ for $n \\geq 200$, whereas the first-order term $1/2 - \\kappa(\\cbar)/n$ "
     "gives $<>$ at $n = 200$", c_within, (0,)),
    ("sec3_mabias", "sec3_theory.tex", "$B = <>$ at $\\psi = -0.8$ and $n = 200$, and the factor is $<>$", c_mabias_b8, ()),
    ("sec3_ar_factors", "sec3_theory.tex", "gives factors of $<>$ and $<>$ at coefficients", c_ar_factors, ()),
    ("sec3_slopes", "sec3_theory.tex", "(log--log slopes $<>$ and $<>$), while the median of the trend-case statistic falls with slopes $<>$ "
     "and $<>$", c_slopes, ()),
    ("sec3_dkw", "sec3_theory.tex", "so that $\\epsilon = <>$ at $\\ncal = 10^5$ and $<>$ at", c_dkw, ()),
    ("sec3_mismatch", "sec3_theory.tex", "produced a rejection rate of $<>$ at $n=200$ in an earlier table", c_mismatch, ()),
    ("sec3_gamma", "sec3_theory.tex", "which gives $\\gamma = <>$ at $n = 200$ and $<>$", c_gamma, ()),
    ("sec4_P", "sec4_implementation.tex", "Mean local power was $<>$, $<>$, $<>$, $<>$ and $<>$ for the five", c_rule_P, ()),
    ("sec4_worst", "sec4_implementation.tex", "with a worst deviation from $0.05$ of $<>$ points", c_rule_worst, ()),
    ("sec4_amend", "sec4_implementation.tex", "<w> of the five windows failed (A1) in a single cell, the trend case at $n=200$, by margins below "
     "$0.001$, and so did nine of twelve comparator tests evaluated on the same paths. A second evaluation with independent paths per case "
     "and a tenfold larger calibration found every procedure within tolerance in that cell (rates from $<>$ to $<>$)", c_rule_amend, ()),
    ("sec4_a2", "sec4_implementation.tex", "on which the two windows differ by $<>$ points", c_rule_a2, ()),
    ("sec4_mcnemar", "sec4_implementation.tex", "(McNemar $p < 0.05$) in <> of the <> cells in which power is not saturated and lower power in "
     "<>, by at most $<>$ points; under a variance break with the null true it is less distorted in <> of <> cells", c_sec42, (3,)),
    ("sec4_ma", "sec4_implementation.tex", "it rejects $<>$ and $<>$ in the constant and trend cases, against $<>$ and $<>$ with", c_sec42_ma, ()),
    ("sec5_region", "sec5_montecarlo.tex", "the number of paths used, $[<>, <>]$ for $\\Nsim=5000$", c_region5000, ()),
    ("sec5_size", "sec5_montecarlo.tex", "The largest deviation, $<>$ points in the trend case at $n = <>$, is a rate of $<>$ that lies just above "
     "the exact region for $5\\times 10^4$ paths; the smoothed statistic with $\\theta = 0.02$ gives $<>$ on the same paths and an "
     "independent replication gives $<>$", c_size_text, ()),
    ("sec5_calib", "sec5_montecarlo.tex", "In the constant case it over-rejects: $<>$ at $n = 60$, $<>$ at $n = 100$ and $<>$ at $n = 200$, "
     "against $<>$, $<>$ and $<>$ with the value calibrated at $n$. In the trend case it under-rejects: $<>$ at $n = 60$, $<>$ at $n = 100$ "
     "and $<>$ at $n = 200$, against $<>$, $<>$ and $<>$", c_calib_text, ()),
    ("sec5_ks", "sec5_montecarlo.tex", "($D = <>$ at $n = 200$, $<>$ at $n = 1000$) and up to $<>$ in the trend case", c_ks, ()),
    ("sec5_pub", "sec5_montecarlo.tex", "rejects $<>$ at $n = 60$, $<>$ at $n = 200$ and $<>$ at $n = 1000$, and DF-GLS $<>$ at $n = 200$",
     c_pub_trend, ()),
    ("sec5_calib_out", "sec5_montecarlo.tex", "region, $<>$ at $n = 60$ in the constant case, is $<>$ points above", c_calib_out, ()),
    ("sec5_calib_note", "sec5_montecarlo.tex", "Bold: outside the exact region $[<>, <>]$ for $2\\times10^4$ paths. $q(20\\,000)$ is $<>$ "
     "(constant) and $<>$ (trend)", c_calib_note, ()),
    ("sec5_lp", "sec5_montecarlo.tex", "lies $<>$, $<>$ and $<>$ points below the envelope at $c = 5$, $10$ and $15$. MSB-GLS, which differs from "
     "it only in the scale, lies $<>$, $<>$ and $<>$ points below, so the Bartlett scale is worth about half a point locally; DF-GLS and "
     "MZ$_t$-GLS are on the envelope to within Monte Carlo error. In the trend case the four tests are within $<>$ points of the envelope "
     "throughout. The smoothed statistic with $\\theta = 0.02$ is lower by $<>$ to $<>$ points, and \\cref{fig:thetaladder} shows the gap "
     "growing with $\\theta$: at $c = 10$ in the constant case the distance to the envelope is $<>$, $<>$, $<>$, $<>$ and $<>$ points",
     c_lp_text, ()),
    ("sec5_lp_se", "sec5_montecarlo.tex", "Monte Carlo standard errors are at most $<>$", c_lp_se, (0,)),
    ("sec5_power200", "sec5_montecarlo.tex", "exceeds DF-GLS by $<>$ points at $\\rho = 0.90$ ($<>$ against $<>$) and $<>$ points at $\\rho = "
     "0.93$, both with McNemar $p < 10^{-4}$, by $<>$ and $<>$ points at $\\rho = 0.80$ and $0.85$, and by $<>$ points at $\\rho = 0.95$ ($p = "
     "<>$); it concedes $<>$ points at $\\rho = 0.97$ ($p = <>$)", c_power200, ()),
    ("sec5_power500", "sec5_montecarlo.tex", "is ahead at $\\rho = 0.97$, $n = 500$ by $<>$ points and behind at $\\rho = 0.99$ by $<>$ points at "
     "$n = 500$ and $<>$ at $n = 1000$. Against ADF and PP the margin is large everywhere, up to $<>$ and $<>$ points", c_power500, ()),
    ("sec5_power_trend", "sec5_montecarlo.tex", "leads DF-GLS by $<>$ points at $(\\rho, n) = (0.90, 200)$ and by $<>$ points at $(0.95, 500)$, "
     "and the two are statistically level in <w> of the nine", c_power_trend, ()),
    ("sec5_attrib", "sec5_montecarlo.tex", "(a)$-$(b) is $<>$ points on average over the seven autoregressive alternatives at $n=200$ in the "
     "constant case, falling to $<>$ points at $n = 500$ and $<>$ at $n = 1000$, and $<>$ points in the trend case at $n=200$. The "
     "modification of Perron and Qu recovers little of it: (b$'$)$-$(b) is $<>$ points at $n = 200$, and (a)$-$(b$'$) is still $<>$. In "
     "local asymptotics the advantage disappears, (a)$-$(b$'$) lying between $<>$ and $<>$ points. The calibration carries the size "
     "correction, which is large in the trend case ($<>$ points of size at $n = 200$, from \\cref{tab:calib}) and translates into $<>$ points "
     "of power there", c_attr_text, ()),
    ("sec5_attrib_diag", "sec5_montecarlo.tex", "the median of $s^2_{\\mathrm{AR}}$ is $<>$ at $\\rho = 0.90$ and $<>$ at $\\rho = 0.93$, against "
     "$<>$ and $<>$ for", c_attr_diag, ()),
    ("sec5_serial1", "sec5_montecarlo.tex", "$<>$ at $\\psi = -0.8$ and $n = 200$ in the constant case, $<>$ in the trend case, $<>$ and $<>$ at "
     "$n = 500$, and between $<>$ and $<>$ at $\\psi = -0.5$ for $n \\geq 200$. The median of $\\hacsig^2/\\omega^2$ at $\\psi = -0.8$ and $n = "
     "200$ is $<>$, against the population factor $<>$ of \\cref{rem:mabias}. Under positive dependence the test is conservative: $<>$ at "
     "$\\psi = 0.5$ and $<>$ at $\\phi = 0.5$, both at $n = 200$ in the trend case, and $<>$ at $\\phi = 0.5$ and $n = 100$. The one cell in "
     "which it looks correct, $<>$ at", c_serial1, ()),
    ("sec5_serial2", "sec5_montecarlo.tex", "Over the $<>$ cells its size ranges from $<>$ to $<>$, against $<>$ to $<>$ for \\RMGLS{}, and at "
     "$\\psi = -0.8$ and $n = 200$ it rejects $<>$ and $<>$ in the two cases. MSB-GLS and MZ$_t$-GLS with their own simulated critical "
     "values are within half a point of it; DF-GLS over-rejects moderately (up to $<>$), ADF more (up to $<>$)", c_serial2, ()),
    ("sec5_serial3", "sec5_montecarlo.tex", "its median lag at $\\psi = -0.8$ and $n = 200$ is $<>$ in the constant case, and the median of "
     "$s^2_{\\mathrm{AR}}/\\omega^2$ is $<>$. The smoothed statistic with $\\theta = 0.02$ is worse still ($<>$ and $<>$", c_serial3, ()),
    ("sec5_initial", "sec5_montecarlo.tex", "none rejects more than $<>$, and at $\\alpha = 4$ all reject $0.000$, while ADF rejects $<>$ and $<>$ "
     "at the two values and PP $<>$ and $<>$. At a moderate initial condition the Bartlett scale loses the least: at $\\alpha = 1$ and $\\rho = "
     "0.90$ \\RMGLS{} rejects $<>$, against $<>$ for DF-GLS, $<>$ for the autoregressive scale (b) and $<>$ for MSB-GLS, and with a "
     "stationary draw $<>$ against $<>$", c_initial, ()),
    ("sec5_dgp2", "sec5_montecarlo.tex", "is ahead of DF-GLS ($<>$ against $<>$, $p = <>$). With a break \\RMGLS{} leads DF-GLS in every cell "
     "with $0.5 \\leq \\delta \\leq 3$ in which power is not saturated, with McNemar $p < 0.01$ in all of them but $(\\delta, n) = (3, 200)$, "
     "where both reject less than $0.01$; and the lead grows with the break: $<>$ against $<>$ at $(\\delta, n) = (1, 200)$, $<>$ against $<>$ "
     "at $(2, 500)$, $<>$ against $<>$ at $(2, 1000)$ and $<>$ against $<>$ at $(3, 1000)$", c_dgp2, ()),
    ("sec5_za", "sec5_montecarlo.tex", "break ($<>$ at $\\delta = 0$, $n = 200$, against $<>$ for \\RMGLS{}); at $\\delta = 5$, where every other "
     "test has no power, it rejects $<>$, $<>$ and $<>$ at $n = 200$, $500$ and $1000$, and it exceeds \\RMGLS{} at $\\delta = 3$ for every $n$ "
     "and at $(\\delta, n) = (2, 200)$. Its size is correct under the two nulls we examined, a pure random walk ($<>$, $<>$ and $<>$ at $n = "
     "200$, $500$ and $1000$) and a random walk with a mid-sample mean shift of one innovation standard deviation ($<>$, $<>$ and $<>$)",
     c_za, ()),
    ("sec5_dgp3", "sec5_montecarlo.tex", "at $r = 4$ it rejects $<>$, $<>$ and $<>$ at $n = 200$, $500$ and $1000$, as much as MSB-GLS and more "
     "than MZ$_t$-GLS ($<>$ at $n = 200$) and DF-GLS ($<>$). ADF and PP are close to the nominal level throughout, a consequence of their "
     "insensitivity to the second moment rather than of their design. The mean-anchored RM statistic is less distorted ($<>$", c_dgp3, ()),
    ("sec5_awb", "sec5_montecarlo.tex", "it rejects $<>$ and $<>$ at $r=2$ with $n = 200$ and $500$, against $<>$ and $<>$ for the simulated "
     "calibration, and $<>$ and $<>$ at $r = 4$, against $<>$ and $<>$; it is conservative there. Under homoskedastic innovations it holds size "
     "($<>$ and $<>$), and under GARCH it is at or below the simulated calibration in all four cells. Its power cost is $<>$ points at $(\\rho, n) "
     "= (0.95, 200)$ and at most $<>$ points elsewhere. The rule registered for recommending the variant required at least four of six "
     "variance-break cells inside the region and at most three points of power loss; the first condition was met with equality and the second "
     "with $<>$ points to spare, and we report the variant as a recommendation with that qualification. It addresses volatility, not serial "
     "correlation. For reference, the AWB DF-GLS of \\citet{cavaliere2008bootstrap} rejects between $<>$ and $<>$", c_awb_text, (11,)),
    ("sec5_misspec", "sec5_montecarlo.tex", "slightly conservative at $n = 200$ ($<>$ and $<>$) and within the region at larger $n$, like DF-GLS "
     "and the M tests, while ADF and PP with asymptotic critical values over-reject. Under GARCH its distortion lies between that of the GLS "
     "tests and that of ADF: at $n = 200$ its mean shift is $<>$ points, against $<>$ for DF-GLS, $<>$ for MZ$_t$-GLS and $<>$ for ADF with "
     "simulated critical values; at $n = 1000$ the figures are $<>$, $<>$, $<>$ and $<>$. It is inside the exact region in <w> of the sixteen "
     "GARCH cells, against <w> for DF-GLS and MZ$_t$-GLS, <w> for MSB-GLS, <w> for ADF with simulated and <w> with asymptotic critical values, "
     "and <w> for PP", c_misspec, ()),
    ("sec5_dgp5", "sec5_montecarlo.tex", "The union rejects with probability $<>$ to $<>$ there, against $<>$ to $<>$ for the two-channel "
     "statistic. The variance channel carried between $<>$ and $<>$ per cent", c_dgp5, ()),
    ("sec5_dgp5b", "sec5_montecarlo.tex", "exceeds the two-channel statistic by $<>$ to $<>$ points in the rows of \\cref{tab:dgp5} and by at "
     "least $<>$ points in every cell of the full grid", lambda: (c_dgp5()[0][6:9], c_dgp5()[1], c_dgp5()[2]), {2: "lower"}),
    ("sec5_dgp5_alpha", "sec5_montecarlo.tex", "calibrated jointly ($\\alpha^\\ast = <>$)", lambda: (c_dgp5()[0][9:], c_dgp5()[1], []), ()),
    ("sec5_negative", "sec5_montecarlo.tex", "dropping it changes size by at most $<>$ points in any of the null cells examined under Gaussian, "
     "heavy-tailed and GARCH innovations. Second, a signal-proportional weight between the two channels concentrated at zero under the null "
     "(mean $<>$) and handed control to the mean channel; rebalancing the channels to a common scale lowered power by $<>$ to $<>$ points. "
     "Third, measuring the rolling means from their own average rather than from the GLS anchor costs $<>$ points of local power at $c = 10$, "
     "measured with $\\theta = 0.1$; the centered statistic lies $<>$ points", lambda: (
         c_negative()[0][:1] + [None] + c_negative()[0][1:], c_negative()[1] + "; la media 0.003 del peso no tiene JSON localizado", []), (0,)),
    ("app_oos", "sec6_application.tex", "give $<>$, $<>$, $<>$ and $<>$ at $D = 150$, $200$, $250$ and $300$, all inside the exact region; with "
     "the AWB calibration the check at $D = 250$, $<>$, falls just below it", c_app_oos, ()),
    ("app_cells", "sec6_application.tex", "leaving <> control cells and <> event cells", c_app_counts, ()),
    ("app_results", "sec6_application.tex", "has a mean false-positive rate of $<>$ over the 48 control cells, against $<>$ for ADF, $<>$ for PP "
     "and $<>$ for DF-GLS with MAIC; it detects <> of the 88 event cells, against <>, <> and <>. MZ$_t$-GLS dominates it on all three metrics: "
     "a lower false-positive rate ($<>$), more detections (<>) and a shorter mean latency when it detects ($<>$ against $<>$ days). The AWB "
     "calibration lowers the false-positive rate slightly and detects fewer events ($<>$, <> detections)", c_app_res, ()),
    ("app_matched", "sec6_application.tex", "At a common false-alarm rate of $<>$, with contiguous rejections grouped into alarm episodes, "
     "\\RMGLS{} produces <> false-alarm episodes over the control years, <w> more than DF-GLS with AIC lag selection and fewer than ADF (<>) "
     "or PP (<>), and a censored latency of $<>$ days, against $<>$ for DF-GLS and $<>$ for MZ$_t$-GLS. Under the pre-registered "
     "adverse-reporting rule, the rate of \\RMGLS{} exceeds a registered baseline in <> of the 48 control cells. The registered two-channel "
     "statistic had fewer false-alarm episodes (<>) and fewer detections (<>)", c_app_matched, ()),
    ("app_caption", "sec6_application.tex", "comparison at a common false-alarm rate of $<>$.}", c_app_target, ()),
    ("app_note", "sec6_application.tex", "false-alarm rate over the control years is $<>$, the rate of", c_app_target, ()),
    ("dev_pilot", "sec6_application.tex", "Registered statistic: mean FP $<> \\to <>$", c_dev_pilot, ()),
    ("dev_stat", "sec6_application.tex", "Mean FP $<> \\to <>$; detections $<> \\to <>$; mean latency $<> \\to <>$ days \\\\ \\addlinespace Window "
     "& -- & $\\theta = 0$ instead of the $\\theta = 0.02$ selected by the registered rule of \\cref{sec:theta} & Mean FP $<> \\to <>$; "
     "detections $<> \\to <>$; mean latency $<> \\to <>$ days", c_dev_stat, ()),
    ("dev_cal", "sec6_application.tex", "uniform error $<>$ by \\cref{eq:dkw}", c_dev_cal, ()),
    ("dev_awb", "sec6_application.tex", "Mean FP $<> \\to <>$; detections $<> \\to <>$; latency $<> \\to <>$ \\\\", c_dev_awb, ()),
    ("dev_ncal", "sec6_application.tex", "raising it to $5\\times10^4$ moved its mean FP to $<>$ with the same <> detections",
     lambda: ([None, S.J("deviation_table_audit8.json")["rows"][7]["effect_before"]["detections"]],
              "detecciones: deviation_table_audit8.json rows[7]; la FP 0.0301 no tiene JSON localizado", []), ()),
    ("concl_pub", "sec7_conclusion.tex", "under-reject in the trend case by $<>$ percentage points at $n = 200$ and $<>$ at $n = 60$",
     lambda: (c_concl()[0][:2], c_concl()[1], []), ()),
    ("concl_ma", "sec7_conclusion.tex", "calibrated test rejects $<>$ at $n = 200$, and under positive", lambda: (c_concl()[0][2:], c_concl()[1], []), ()),
    ("concl_25", "sec7_conclusion.tex", "cost about <> points of local power", c_concl25, ()),
    ("appA_factor", "appA_proofs.tex", "the factor is $<>$ at $n = 200$. The exact moment, computed as", lambda: (c_appA()[0][:1], c_appA()[1], []), ()),
    ("appA_exact", "appA_proofs.tex", "is $<>$, $<>$ and $<>$ at $n = 200$, $500$ and $2000$, against the first-order values $<>$, $<>$ and $<>$",
     lambda: (c_appA()[0][1:], c_appA()[1], []), ()),
    ("appA_hacrate", "appA_proofs.tex", "with a relative deviation falling from $<>\\%$ at $n = 200$ to $<>\\%$ at $n = 5000$, and the selected "
     "bandwidth grows with slope $<>$", lambda: ([None, None, None], "sin JSON localizado (Observacion rem:hacrate; el v14 remite al suplemento)", []), ()),
    ("appB", "appB_critical_values.tex", "standard error of each quantile is below $<>$. The dependence on $n$ is the anchor effect of "
     "\\cref{rem:anchorbias}: in the constant case the $5\\%$ critical value rises from $<>$ at $n = 100$ to $<>$ at $n = 1000$, and in the trend "
     "case it falls from $<>$ to $<>$", c_appB, (0,)),
    ("intro_window", "sec1_introduction.tex", "local power falls monotonically in the window, which also doubles the size distortion under "
     "negative moving-average errors", lambda: c_window(), ()),
    ("concl_window", "sec7_conclusion.tex", "lowers local power monotonically and doubles the size distortion under negative moving-average "
     "errors", lambda: c_window(), ()),
    ("attrib_note", "sec5_montecarlo.tex", "Means of (a)$-$(b): $<>$ (<>), $<>$ (<>) and $<>$ (<>) in the constant case at $n = 200$, $500$ and "
     "$1000$; $<>$ (<>) and $<>$ (<>) in the trend case at $n = 200$ and $500$. Means of (b)$-$(c): $<>$, $<>$ and $<>$; $<>$ and $<>$",
     lambda: c_attrib_note(), ()),
    ("note_region_serial", "sec5_montecarlo.tex", "(in parentheses). Bold: outside the exact region $[<>, <>]$ for $2\\times10^4$ paths",
     lambda: (list(C.exact_region(20000)), "formula exact_region(20000)", []), ()),
    ("note_region_dgp2", "sec5_montecarlo.tex", "lies inside the exact region $[<>, <>]$ in all six cells",
     lambda: (list(C.exact_region(5000)), "formula exact_region(5000); tamanos de ZA en sec5_za",
              [("ZA dentro de la region en las seis celdas", all(S.J("b5_power_audit8.json")["za_size"]["za_%s_n%d" % (k, n)]["rates"]["za"]["in_region"]
                                                               for k in ("rw", "rwbreak") for n in (200, 500, 1000)))]), ()),
    ("note_region_dgp3", "sec5_montecarlo.tex", "all procedures at simulated critical values. Bold: outside $[<>, <>]$",
     lambda: (list(C.exact_region(5000)), "formula exact_region(5000)", []), ()),
    ("note_region_awb", "sec5_montecarlo.tex", "Bold: outside the exact region $[<>, <>]$ for 2000 paths",
     lambda: (list(C.exact_region(2000)), "formula exact_region(2000)", []), ()),
    ("note_region_misspec", "sec5_montecarlo.tex", "asymptotic critical values. Bold: outside $[<>, <>]$. Shifts",
     lambda: (list(C.exact_region(5000)), "formula exact_region(5000)", []), ()),
]


def c_window():
    """Potencia local media por theta (regla de A9) y distorsion de tamano bajo MA negativo, theta 0.02 frente a theta 0."""
    P = S.J("b92_theta_audit9.json")["theta_rule"]["P"]
    ps = [P[C.tname(t)] for t in THETAS()]
    cells = [c for c in S.J("bA_ma_audit12.json")["size"].values() if c["err_tag"] in ("ma_m0p8", "ma_m0p5")]
    d0 = sum(c["iid"][PRIM]["rate"] - LEVEL for c in cells)
    d2 = sum(c["iid"][V13P]["rate"] - LEVEL for c in cells)
    ratio = d2 / d0
    per = sorted((c["iid"][V13P]["rate"] - LEVEL) / (c["iid"][PRIM]["rate"] - LEVEL) for c in cells if c["iid"][PRIM]["rate"] > LEVEL)
    return [], "b92_theta_audit9.json theta_rule.P; bA_ma_audit12.json size (12 celdas MA con psi < 0, iid)", \
        [("potencia local media decreciente en theta (%s)" % ", ".join("%.4f" % p for p in ps), all(a > b for a, b in zip(ps, ps[1:]))),
         ("'dobla': cociente de distorsiones medias theta 0.02 / theta 0 = %.2f (redondea a 2 si esta en [1.5, 2.5)); por celda con "
          "distorsion positiva, de %.2f a %.2f" % (ratio, per[0], per[-1]), round(ratio) == 2)]


def c_attrib_note():
    b = attrib()["by_n"]
    ks = ("c|200", "c|500", "c|1000", "ct|200", "ct|500")
    vals = []
    for k in ks:
        vals += [b[k]["a_minus_b"]["mean"] * C.PP, b[k]["a_minus_b"]["se"] * C.PP]
    vals += [b[k]["b_minus_c"]["mean"] * C.PP for k in ks]
    return vals, "bB_attrib_audit12.json by_n.<celda>.<a_minus_b|b_minus_c>", []


# ---------------------------------------------------------------------------
# Comparacion
# ---------------------------------------------------------------------------
def pattern(template):
    parts = re.split(r"(<>|<w>)", template)
    out = []
    for p in parts:
        if p == "<>":
            out.append(NUMRE)
        elif p == "<w>":
            out.append(WORDRE)
        else:
            out.append(r"\s+".join(re.escape(x) for x in re.split(r"\s+", p)) if p.strip() else (r"\s+" if p else ""))
    return "".join(out)


def conventions(printed, value, bound):
    """Convenciones que llevan el valor a la cifra impresa."""
    if printed in WORDS:
        return ["palabra"] if WORDS[printed] == round(value) else []
    s = printed.lstrip("+")
    d = len(s.split(".")[1]) if "." in s else 0
    out = []
    if TB.fdec(value, d, "binary") == s:
        out.append("binaria")
    if TB.fdec(value, d, "half_up") == s:
        out.append("mitad hacia arriba")
    if bound and not out:
        q = decimal.Decimal(1).scaleb(-d)
        if str(decimal.Decimal(repr(float(value))).quantize(q, rounding=decimal.ROUND_CEILING)) == s:
            out.append("hacia arriba (cota)")
    return out


def correct(printed, value, bound=None):
    """Cifra correcta a los decimales impresos; para una cota incumplida, la cota redondeada hacia afuera."""
    if bound is not None:
        s = printed.lstrip("+")
        d = len(s.split(".")[1]) if "." in s else 0
        q = decimal.Decimal(1).scaleb(-d)
        mode = decimal.ROUND_CEILING if bound == "upper" else decimal.ROUND_FLOOR
        return str(decimal.Decimal(repr(float(value))).quantize(q, rounding=mode))
    if printed in WORDS:
        inv = {v: k for k, v in WORDS.items()}
        return inv.get(round(value), "%d" % round(value))
    s = printed.lstrip("+")
    d = len(s.split(".")[1]) if "." in s else 0
    r = TB.fdec(value, d, "binary")
    return "+" + r if printed.startswith("+") and not r.startswith("-") else r


# ---------------------------------------------------------------------------
# Barrido de cobertura de los numeros con decimales
# ---------------------------------------------------------------------------
CONTEXT_DESIGN = [
    (r"errors of −0\.8|\\psi = -?0\.\d|\\phi = -?0\.\d|\\psi \\in|\\phi \\in|coefficients? \$-?0\.5\$|errors of \$-0\.8\$|of \$-0\.8\$|of coefficient",
     "parametro del error serial"),
    (r"\\rho = 0\.\d+|\\rho \\in|\\rho \\geq|\(\\rho, n\) = \(|at \$\(0\.\d+, \d+\)\$|\(\\delta, n\) = \(", "celda o rejilla de rho/delta"),
    (r"\\theta = 0\.\d+|\\theta \\in|\\theta = 0\$, \$0\.02\$|theta = 0\.1", "theta de diseno"),
    (r"\\delta \\in|\\delta = \d|\\leq \\delta \\leq", "delta de diseno"),
    (r"\\cbar = -\d|-13\.5|\\cbar\$ = -", "c-barra de ERS"),
    (r"1\.1447|0\.01\^\{1/l\}|1\.75", "constante de la regla de ancho de banda"),
    (r"persistence \$0\.\d+\$|persistence|G \$p\$|0\.95\$ \(\$t\(5\)", "persistencia GARCH"),
    (r"within \$0\.25\$|\$0\.25\$ percentage points|within \$0\.3\$ points|margins below", "tolerancia registrada"),
    (r"r \\in|r \\geq|r \\leq|r = 1\.1", "rejilla de r"),
    (r"\\alpha = 0\.05|\\alpha = \d|p=0\.05|p = 0\.05", "nivel nominal"),
    (r"weight \$0\.5\$|windows \$\(0\.1, 0\.1\)\$", "parametro del registro"),
    (r"\\times ?10\^", "exponente o tamano de simulacion"),
    (r"Python~3\.11", "version de software"),
    (r"p < 0\.05|p < 0\.01|less than \$0\.01\$|p < 10", "umbral de significacion"),
    (r"exceeds \$0\.99\$", "umbral de las notas"),
    (r"AR\$\(0\.\d+\)\$", "proceso de diseno"),
    (r"at \$0\.05\$|from \$0\.05\$|size \$0\.05\$|of \$0\.05\$", "nivel nominal"),
    (r"with probability \$0\.95\$", "nivel de la cota DKW"),
    (r"all reject \$0\.000\$", "comprobada en sec5_initial"),
]


def sweep(v, covered):
    items = []
    for fname in Q.TEXT_FILES:
        text = v.files[fname]
        starts = [m.start() for m in re.finditer(r"^", text, flags=re.M)]
        tabs = [(m.start(), m.end()) for m in re.finditer(r"\\begin\{tabular\}.*?\\end\{tabular\}", text, flags=re.S)]
        spans = covered.get(fname, [])
        for m in re.finditer(r"(?<![A-Za-z_\d.])\d+\.\d+", text):
            a = m.start()
            line = sum(1 for s in starts if s <= a)
            if fname.endswith(".tex") and re.search(r"(?<!\\)%", text[starts[line - 1]:a]):
                continue
            hit = next((k for x, y, k in spans if x <= a < y), None)
            ctx = re.sub(r"\s+", " ", text[max(0, a - 50):m.end() + 30])
            if hit:
                status, why = "cubierta", hit
            elif any(x <= a < y for x, y in tabs):
                status, why = "tabular", "celda del tabular transcrito (tab:attrib, Q1) o de tab:deviations (frases dev_*)"
            else:
                why = next((lab for pat, lab in CONTEXT_DESIGN if re.search(pat, ctx)), None)
                status = "diseno" if why else "no verificada"
            items.append({"file": "v14/" + fname, "line": line, "token": m.group(0), "status": status, "reason": why,
                          "context": re.sub(r"\s+", " ", text[max(0, a - 60):m.end() + 40])})
    return items


def main():
    v = Q.V14()
    claims, covered, missing = {}, {}, []
    for key, fname, template, fn, bound in CLAIMS:
        text = v.files[fname]
        m = re.search(pattern(template), text)
        if m is None:
            missing.append(key)
            claims[key] = {"file": "v14/" + fname, "line": None, "found": False, "template": template}
            continue
        starts = [x.start() for x in re.finditer(r"^", text, flags=re.M)]
        line = sum(1 for s in starts if s <= m.start())
        vals, src, checks = fn()
        printed = list(m.groups())
        rows = []
        bspec = bound if isinstance(bound, dict) else {i: "upper" for i in bound}
        for i, (p, x) in enumerate(zip(printed, list(vals) + [None] * (len(printed) - len(vals)))):
            if x is None:
                rows.append({"printed": p, "value": None, "conventions": [], "verdict": "sin fuente JSON", "correct": None})
                continue
            kind = bspec.get(i)
            conv = conventions(p, x, kind == "upper")
            pv = WORDS[p] if p in WORDS else float(p)
            holds = True if kind is None else (x <= pv + BOUND_EPS if kind == "upper" else x >= pv - BOUND_EPS)
            if conv and holds:
                verdict = "reproduce como cota" if conv == ["hacia arriba (cota)"] else "reproduce"
            elif conv:
                verdict = "no reproduce"
                conv = conv + ["cota %s incumplida" % ("superior" if kind == "upper" else "inferior")]
            else:
                verdict = "no reproduce"
            rows.append({"printed": p, "value": x, "conventions": conv, "bound": kind, "bound_holds": holds, "verdict": verdict,
                         "correct": None if verdict != "no reproduce" else correct(p, x, kind if conv else None)})
        covered.setdefault(fname, []).append((m.start(), m.end(), key))
        claims[key] = {"file": "v14/" + fname, "line": line, "found": True, "quote": re.sub(r"\s+", " ", m.group(0)), "source": src,
                       "numbers": rows, "checks": [{"check": c, "holds": bool(h)} for c, h in checks],
                       "all_reproduced": all(r["verdict"] != "no reproduce" for r in rows) and all(h for _, h in checks)}
    items = sweep(v, covered)
    counts = {s: sum(1 for i in items if i["status"] == s) for s in ("cubierta", "diseno", "tabular", "no verificada")}
    bad = [(k, r) for k, c in claims.items() if c.get("found") for r in c["numbers"] if r["verdict"] == "no reproduce"]
    fchecks = [(k, x["check"]) for k, c in claims.items() if c.get("found") for x in c["checks"] if not x["holds"]]
    nosrc = [(k, r["printed"]) for k, c in claims.items() if c.get("found") for r in c["numbers"] if r["verdict"] == "sin fuente JSON"]
    changelog = ["sec4_mcnemar", "sec4_ma", "sec4_a2", "sec3_mabias", "sec3_ar_factors", "sec3_within", "sec3_kappa_lambda", "sec5_attrib",
                 "sec5_attrib_diag", "attrib_note", "sec5_serial1", "sec5_serial2", "sec5_serial3", "sec5_initial", "sec5_calib_out",
                 "sec5_ks", "sec5_power500", "appA_factor"]
    out = {"provenance": C.provenance(__file__, seed_family=None), "manuscript": v.record(),
           "reading": "protocol_audit13_amend1.md, lectura 5", "claims": claims, "templates_not_found": missing,
           "not_reproduced": [{"claim": k, "file": claims[k]["file"], "line": claims[k]["line"], **r} for k, r in bad],
           "failed_checks": [{"claim": k, "file": claims[k]["file"], "line": claims[k]["line"], "check": c} for k, c in fchecks],
           "without_json": [{"claim": k, "file": claims[k]["file"], "line": claims[k]["line"], "printed": p} for k, p in nosrc],
           "changelog_s3_claims": changelog, "theta_vs_v13": theta_vs_v13(), "sweep": {"counts": counts, "items": items}}
    C.write_result(OUT, out, __file__)
    print("frases:", len(claims), "no encontradas:", missing)
    print("cifras:", sum(len(c["numbers"]) for c in claims.values() if c.get("found")), "no reproduce:", len(bad))
    for k, r in bad:
        print("   NO", k, claims[k]["file"], claims[k]["line"], r["printed"], "->", r["correct"], "(%s)" % r["value"])
    for k, c in fchecks:
        print("   COMPROBACION FALLA", k, c)
    print("sin JSON:", nosrc)
    print("barrido:", counts)
    for i in items:
        if i["status"] == "no verificada":
            print("   ?", i["file"], i["line"], i["token"], "|", i["context"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
