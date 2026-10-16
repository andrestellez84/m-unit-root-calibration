"""
Auditoria A13 - cifras del texto del v13 que dependen de theta (para el reporte).

Lee paper_latex_v13.zip sin extraerlo. Para cada frase del texto (resumen,
introduccion, secciones 5 y 6, apendice B, highlights) que cita una cifra de una
tabla regenerada con theta = 0, registra archivo:linea y la cita, y calcula desde
los JSON la misma cantidad dos veces: con las fuentes del v13 (theta = 0.02) y con
las de A13 (theta = 0). Paso 0 del texto: la version theta = 0.02 reproduce la cifra
impresa a sus decimales; si no, se marca y se reporta en la seccion 7. No reescribe
ninguna frase.

Salida: experiments/results/claims_audit13.json.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402
from audit11_t5_claims import Manuscript, decimals                 # noqa: E402

OUT = os.path.join(C.RESULTS, "claims_audit13.json")
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16}
V13, A13 = "v13", "a13"
SPAN = 6             # ventana de lineas; find devuelve la linea donde empieza la coincidencia
TOL = C.read_json("b101_theta_audit10.json")["config"]["tolerance"]      # criterio A1' (0.25 pp) de A10


class M13(Manuscript):
    def find(self, fname, pattern, span=1):
        r = super().find(fname, pattern, span)
        r["file"] = "v13/" + fname
        return r


# ---------------------------------------------------------------------------
# Fuentes por version
# ---------------------------------------------------------------------------
class Src:
    def __init__(self, ver):
        self.ver = ver
        self.prim = C.PRIM if ver == A13 else C.PRIM_V13
        self.other = C.PRIM_V13 if ver == A13 else C.PRIM
        self.eq = C.read_json("e_equalized_audit13.json" if ver == A13 else "b103_equalized_audit10.json")["cells"]
        self.cal = C.read_json("e_calib_audit13.json")["cases_by_theta"][self.prim]
        self.b92 = C.read_json("b92_theta_audit9.json")
        self.awb = C.read_json("e_awb_audit13.json" if ver == A13 else "b103_awb_audit10.json")
        self.d5 = C.read_json("e_dgp5_audit13.json" if ver == A13 else "b103_dgp5_audit10.json")["cells"]
        self.cv = C.read_json("b103_cv_audit10.json")["table"]
        if ver == A13:
            ap = C.read_json("e_application_audit13.json")
            self.app = {"summary": ap["summary"], "matched": ap["matched_rate"], "oos": ap["oos_size"],
                        "oos_awb": ap["oos_size_awb"], "adverse": ap["adverse_cells_primary"]}
        else:
            ap = C.read_json("b103_application_audit10.json")
            self.app = {"summary": ap["summary"], "matched": ap["matched_rate"], "oos": ap["oos_size"],
                        "oos_awb": ap["oos_size_awb"], "adverse": ap["adverse_cells_primary"]}
        new, old = TB.size_sources()
        self.size = new if ver == A13 else old

    def r(self, key, proc=None):
        return self.eq[key]["rates_sim"][proc or self.prim]["rate"]

    def p_df(self, key):
        return self.eq[key]["mcnemar_primary_vs_sim"]["dfgls"]["p_value"]

    def d_df(self, key):
        return (self.r(key) - self.r(key, "dfgls")) * C.PP

    def lp(self, case, c, proc=None):
        return self.b92["local_power"][case]["power"]["%s" % float(c)][proc or self.prim]

    def gap(self, case, c, proc=None):
        return (self.lp(case, c, "envelope") - self.lp(case, c, proc)) * C.PP


def dgp1(rho, n):
    return "dgp1_rho%s_n%d" % (TB.rtag(rho), n)


def lp_table_c(section):
    t = C.read_json("tables_audit13.json")["tables"]["localpower"]["rows"]
    return [TB.num(r["keys"][0]) for r in t if r["section"] == section]


# ---------------------------------------------------------------------------
# Frases: (archivo, patron, lineas, funcion(S) -> (valores alineados con los grupos, extra))
# ---------------------------------------------------------------------------
def size_max(S):
    k = max(S.size, key=lambda k: abs(S.size[k]["rate"] - C.ALPHA))
    r = S.size[k]
    return [abs(r["rate"] - C.ALPHA) * C.PP, int(k.split("|")[1]), r["rate"]], {
        "cell": k, "all_within_A1prime_tolerance": all(abs(v["rate"] - C.ALPHA) <= TOL for v in S.size.values()),
        "outside_exact_region": sorted(k for k, v in S.size.items() if not v["in_region"])}


def calib_lim(S):
    ac = S.cal["c"]["approximation_cost"]
    return ([ac[n]["size_with_cv_n20000"]["rate"] for n in ("60", "100", "200")]
            + [ac[n]["size_with_cv_at_n"]["rate"] for n in ("60", "100", "200")]), {}


def calib_ks(S):
    ks = S.cal["c"]["ks"]
    return [ks["200"]["D"], ks["1000"]["D"]], {"below_threshold_c": {n: v["below_threshold"] for n, v in ks.items()},
                                               "below_threshold_ct": {n: v["below_threshold"] for n, v in S.cal["ct"]["ks"].items()}}


def calib_trend(S):
    ac = S.cal["ct"]["approximation_cost"]
    return [], {"trend_size_with_cv_n20000": {n: v["size_with_cv_n20000"]["rate"] for n, v in ac.items()},
                "trend_outside_exact_region": sorted((int(n) for n, v in ac.items() if not v["size_with_cv_n20000"]["in_region"])),
                "cv_n20000": {"c": S.cal["c"]["cv_n20000"], "ct": S.cal["ct"]["cv_n20000"]}}


def intro_lim(S):
    ac = S.cal["c"]["approximation_cost"]["200"]
    return [ac["size_with_cv_n20000"]["rate"], ac["size_with_cv_at_n"]["rate"]], {}


def abs_lim(S):
    return [S.cal["c"]["approximation_cost"]["200"]["size_with_cv_n20000"]["rate"]], {}


def lp_gap(S):
    return [S.gap("dm", c) for c in (5, 10, 15)], {"msb_gap": [S.gap("dm", c, "msb") for c in (5, 10, 15)],
                                                     "primary_minus_msb_pp": [S.gap("dm", c, "msb") - S.gap("dm", c) for c in (5, 10, 15)]}


def lp_trend(S):
    cs = lp_table_c("Trend")
    return [max(S.gap("ct", c, p) for c in cs for p in (S.prim, "dfgls", "mzt", "msb"))], {"c_values": cs}


def lp_theta(S):
    cs = [c for c in lp_table_c("Constant") if 5 <= c <= 15]
    d = [(S.lp("dm", c, C.PRIM) - S.lp("dm", c, C.PRIM_V13)) * C.PP for c in cs]
    return [min(d), max(d)], {"c_values": cs, "theta0_minus_theta002_pp": d}


def lp_max(S):
    return [max(S.gap("dm", c) for c in (5, 10, 15))], {}


def pow200(S):
    k = {r: dgp1(r, 200) for r in (0.8, 0.85, 0.9, 0.93, 0.95, 0.97)}
    return ([S.d_df(k[0.9]), S.r(k[0.9]), S.r(k[0.9], "dfgls"), S.d_df(k[0.93]), S.d_df(k[0.8]), S.d_df(k[0.85]),
             S.p_df(k[0.95]), -S.d_df(k[0.97]), S.p_df(k[0.97])],
            {"p_rho090": S.p_df(k[0.9]), "p_rho093": S.p_df(k[0.93]), "p_rho080": S.p_df(k[0.8]), "p_rho085": S.p_df(k[0.85])})


def intro_pow(S):
    return [S.d_df(dgp1(0.9, 200)), S.d_df(dgp1(0.93, 200)), -S.d_df(dgp1(0.97, 200))], {"p_rho095": S.p_df(dgp1(0.95, 200))}


def abs_pow(S):
    cells = [k for k in S.eq if k.startswith("dgp1_")]
    c200 = [k for k in cells if S.eq[k]["n"] == 200]
    up = max(c200, key=S.d_df)
    down = min(cells, key=S.d_df)
    return [S.d_df(up), -S.d_df(down)], {"max_gain_cell_n200": up, "max_loss_cell": down}


def pow500(S):
    return [S.d_df(dgp1(0.97, 500)), -S.d_df(dgp1(0.99, 500)), -S.d_df(dgp1(0.99, 1000))], {}


def pow_adf(S):
    """Margen sobre ADF y PP a la vez: min(primaria - ADF, primaria - PP); maximo sobre las celdas de DGP 1."""
    cells = [c for c in S.eq if c.startswith("dgp1_")]

    def margin(c):
        return min(S.r(c) - S.r(c, "adf"), S.r(c) - S.r(c, "pp")) * C.PP
    top = max(cells, key=margin)
    k = dgp1(0.99, 1000)
    return [margin(k)], {"max_margin_cell": top, "max_margin_pp": margin(top),
                         "minus_adf_pp": (S.r(k) - S.r(k, "adf")) * C.PP, "minus_pp_pp": (S.r(k) - S.r(k, "pp")) * C.PP}


def pow_trend(S):
    rows = C.read_json("tables_audit13.json")["tables"]["ctpower"]["rows"]
    keys = ["ct_power_rho%s_n%d" % (TB.rtag(TB.num(r["keys"][0])), int(TB.num(r["keys"][1]))) for r in rows]
    level = [k for k in keys if S.p_df(k) >= C.ALPHA]
    return [S.d_df("ct_power_rho0p9_n200"), S.d_df("ct_power_rho0p95_n500"), len(level)], {"level_cells": level}


def dgp2(S):
    def k(d, n):
        return "dgp2_delta%s_n%d" % (TB.rtag(d), n)
    lead = [kk for kk in S.eq if kk.startswith("dgp2_") and 0.5 <= S.eq[kk]["delta"] <= 3
            and min(S.r(kk), S.r(kk, "dfgls")) < 0.99]
    wins = [kk for kk in lead if S.r(kk) > S.r(kk, "dfgls")]
    vals = [S.r(k(0, 200)), S.r(k(0, 200), "dfgls"), S.p_df(k(0, 200)), max(S.p_df(kk) for kk in wins)]
    for d, n in ((1, 200), (2, 500), (2, 1000), (3, 1000)):
        vals += [S.r(k(d, n)), S.r(k(d, n), "dfgls")]
    return vals, {"unsaturated_cells": sorted(lead), "cells_where_primary_leads": sorted(wins),
                  "leads_in_every_unsaturated_cell": len(wins) == len(lead)}


def za(S):
    cells = sorted(k for k in S.eq if k.startswith("dgp2_") and S.r(k, "za") > S.r(k))
    return [], {"cells_where_za_exceeds_primary": cells}


def za0(S):
    return [S.r("dgp2_delta0_n200", "za"), S.r("dgp2_delta0_n200")], {}


def dgp3(S):
    return [S.r("dgp3_r4_n%d" % n) for n in (200, 500, 1000)], {
        "rm_below_primary_r4_n200": S.r("dgp3_r4_n200", "rm_t0.1") < S.r("dgp3_r4_n200"),
        "msb_r4": [S.r("dgp3_r4_n%d" % n, "msb") for n in (200, 500, 1000)]}


def intro_dgp3(S):
    a = S.awb["cells"]
    return [S.r("dgp3_r4_n200"), a["dgp3_r4_n200"]["awb"]["rate"],
            max(v["power_loss_pp"] for k, v in a.items() if k.startswith("dgp1_"))], {}


def awb1(S):
    a = S.awb["cells"]
    return [a["dgp3_r2_n200"]["awb"]["rate"], a["dgp3_r2_n500"]["awb"]["rate"], a["dgp3_r2_n200"]["sim"]["rate"],
            a["dgp3_r2_n500"]["sim"]["rate"], a["dgp3_r4_n200"]["awb"]["rate"], a["dgp3_r4_n200"]["sim"]["rate"],
            a["dgp3_r4_n500"]["sim"]["rate"]], {"awb_r4_n500": a["dgp3_r4_n500"]["awb"]["rate"],
                                                 "garch_awb_at_or_below_sim_all": all(v["awb"]["rate"] <= v["sim"]["rate"]
                                                                                      for k, v in a.items() if k.startswith("garch"))}


def awb2(S):
    a = S.awb["cells"]
    return [a["indep_n200"]["awb"]["rate"], a["indep_n500"]["awb"]["rate"]], {}


def awb3(S):
    a = S.awb["cells"]
    rest = [v["power_loss_pp"] for k, v in a.items() if k.startswith("dgp1_") and k != "dgp1_rho0p95_n200"]
    return [a["dgp1_rho0p95_n200"]["power_loss_pp"], max(rest)], {}


def awb4(S):
    r = S.awb["rule"]
    return [], {"i_in_region_dgp3": r["i_in_region_dgp3"], "i_min": r["i_min"], "i_equality": r["i_in_region_dgp3"] == r["i_min"],
                "max_power_loss_pp": max(r["ii_power_loss_pp"].values()), "ii_threshold_pp": r["ii_threshold_pp"],
                "ii_equality": max(r["ii_power_loss_pp"].values()) == r["ii_threshold_pp"],
                "recommend_awb": r["recommend_awb"]}


MIS_GARCH_N = (200, 500, 1000, 2000, 5000)


def mis1(S):
    m = S.b92["misspec"]
    return [m["c|heavy_t5_n200"]["rates"][S.prim]["rate"], m["c|heavy_t3_n200"]["rates"][S.prim]["rate"]], {}


def mis_shift(n):
    def f(S):
        m = S.b92["misspec"]
        ds = [m[k]["delta_vs_independent"][S.prim]["delta"] for k in m if k.startswith("c|garch_") and k.endswith("_n%d" % n)]
        return [sum(ds) / len(ds) * C.PP], {}
    return f


def mis4(S):
    m = S.b92["misspec"]
    cells = [k for k in m if k.startswith("c|garch_") and int(k.rsplit("_n", 1)[1]) in MIS_GARCH_N]
    inside = [k for k in cells if m[k]["rates"][S.prim]["in_region"]]
    return [len(inside)], {"garch_cells": len(cells), "inside": sorted(inside)}


def dgp5(S):
    d = [(v["size_matched"]["primary"]["rate"] - v["size_matched"]["proposed_R050"]["rate"]) * C.PP for v in S.d5.values()]
    boot = all(v["size_matched"]["primary"]["rate"] > v["size_matched"]["bootstrap_dfgls"]["rate"]
               for v in S.d5.values() if v["r"] >= 1.5)
    union = all(v["size_matched"]["primary"]["rate"] > v["size_matched"]["union_joint"]["rate"]
                for v in S.d5.values() if v["r"] <= 1.25)
    inter = all(v["size_matched"]["union_joint"]["rate"] > v["size_matched"]["primary"]["rate"]
                for v in S.d5.values() if v["r"] in (2.0, 3.0))
    import audit7_design as D7
    rows = C.read_json("tables_audit13.json")["tables"]["dgp5"]["rows"]
    keys = [D7.dgp5_tag(200, TB.num(r["keys"][0]), float(TB.num(r["keys"][1]))) for r in rows]
    dt = [(S.d5[k]["size_matched"]["primary"]["rate"] - S.d5[k]["size_matched"]["proposed_R050"]["rate"]) * C.PP for k in keys]
    return [min(d), max(d)], {"cells": len(d), "exceeds_bootstrap_r_ge_1.5": boot, "exceeds_union_r_le_1.25": union,
                              "union_dominates_interior": inter, "min_table_rows_pp": min(dt), "max_table_rows_pp": max(dt),
                              "table_rows": len(dt),
                              "min_cell": min(S.d5, key=lambda k: S.d5[k]["size_matched"]["primary"]["rate"]
                                              - S.d5[k]["size_matched"]["proposed_R050"]["rate"])}


def appb(S):
    t = S.theta_cv()
    return [S.cv["dm|%g|100" % t]["cv"]["0.05"], S.cv["dm|%g|1000" % t]["cv"]["0.05"]], {}


def appb_se(S):
    t = S.theta_cv()
    return [max(e["max_se"] for e in S.cv.values() if e["theta"] == t)], {}


Src.theta_cv = lambda self: C.THETA if self.ver == A13 else C.THETA_V13


def app_oos(S):
    return [S.app["oos"]["by_D"][d]["rate"] for d in ("150", "200", "250", "300")], {
        "in_region": {d: v["in_region"] for d, v in S.app["oos"]["by_D"].items()},
        "awb": {d: v["rate"] for d, v in S.app["oos_awb"]["by_D"].items()}}


def s_(S, t):
    return S.app["summary"][t]


def app_fp(S):
    return [s_(S, "final")["fp_mean"]], {}


def app_det(S):
    return [s_(S, "final")["detections"]], {}


def app_mzt(S):
    f, m = s_(S, "final"), s_(S, "mzt")
    return [m["mean_latency_detected"], f["mean_latency_detected"]], {
        "mzt_dominates_all_three": m["fp_mean"] < f["fp_mean"] and m["detections"] > f["detections"]
        and m["mean_latency_detected"] < f["mean_latency_detected"]}


def app_awb(S):
    return [s_(S, "final_awb")["fp_mean"], s_(S, "final_awb")["detections"]], {}


def app_target(S):
    return [S.app["matched"]["target_fpr_pooled_primary"]], {}


def app_episodes(S):
    t = S.app["matched"]["tests"]
    return [t["final"]["false_alarm_episodes"]], {k: t[k]["false_alarm_episodes"] for k in ("dfgls_aic", "adf", "pp")}


def app_latc(S):
    t = S.app["matched"]["tests"]
    return [t["final"]["censored_latency_mean"], t["dfgls_aic"]["censored_latency_mean"], t["mzt"]["censored_latency_mean"]], {}


def app_adverse(S):
    return [len(S.app["adverse"])], {}


def app_rhat(S):
    return [S.app["matched"]["tests"]["rhat_prereg"]["false_alarm_episodes"], s_(S, "rhat_prereg")["detections"]], {}


def app_dev1(S):
    r, f = s_(S, "rhat_prereg"), s_(S, "final")
    return [r["fp_mean"], f["fp_mean"], r["detections"], f["detections"], r["mean_latency_detected"],
            f["mean_latency_detected"]], {}


def app_dev2(S):
    f, a = s_(S, "final"), s_(S, "final_awb")
    return [f["fp_mean"], a["fp_mean"], f["detections"], a["detections"], f["mean_latency_detected"],
            a["mean_latency_detected"]], {}


CLAIMS = {
    "size_max": ("sec5_montecarlo.tex", r"largest deviation being \$([0-9.]+)\$ points at \$n = (\d+)\$ in the constant case, "
                 r"where the rate of \$([0-9.]+)\$", 3, size_max),
    "calib_limit": ("sec5_montecarlo.tex", r"over-rejects in short samples: \$([0-9.]+)\$ at \$n = 60\$, \$([0-9.]+)\$ at "
                    r"\$n = 100\$ and \$([0-9.]+)\$ at \$n=200\$, against \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$", 3, calib_lim),
    "calib_ks": ("sec5_montecarlo.tex", r"\(\$D = ([0-9.]+)\$ at \$n = 200\$, \$([0-9.]+)\$ at \$n=1000\$\)", 2, calib_ks),
    "calib_trend": ("sec5_montecarlo.tex", r"In the trend case the limiting value happens to be close at every \$n\$", 2, calib_trend),
    "intro_limit": ("sec1_introduction.tex", r"gives a rejection rate of \$([0-9.]+)\$; using the one simulated at \$n = 200\$ "
                    r"gives \$([0-9.]+)\$", 2, intro_lim),
    "abstract_limit": ("main.tex", r"asymptotic critical value gives a rejection rate of \$([0-9.]+)\$", 1, abs_lim),
    "lp_gap": ("sec5_montecarlo.tex", r"lies \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$ points below the envelope at "
               r"\$c = 5\$, \$10\$ and \$15\$", 2, lp_gap),
    "lp_trend": ("sec5_montecarlo.tex", r"the four tests are within \$([0-9.]+)\$ points of the envelope throughout", 2, lp_trend),
    "lp_theta": ("sec5_montecarlo.tex", r"marginally closer than \$\\theta=0\.02\$, by \$([0-9.]+)\$ to \$([0-9.]+)\$ points", 2,
                 lp_theta),
    "intro_lp": ("sec1_introduction.tex", r"within \$([0-9.]+)\$ points of the Gaussian envelope", 2, lp_max),
    "abstract_lp": ("main.tex", r"within \$([0-9.]+)\$ percentage points of", 1, lp_max),
    "highlights_lp": ("highlights.tex", r"Local power within ([0-9.]+) points of the envelope", 1, lp_max),
    "power_n200": ("sec5_montecarlo.tex", r"exceeds DF-GLS by \$([0-9.]+)\$ points at \$\\rho = 0\.90\$ \(\$([0-9.]+)\$ against "
                   r"\$([0-9.]+)\$\) and \$([0-9.]+)\$ points at \$\\rho = 0\.93\$, both with McNemar \$p < 10\^\{-4\}\$, and by "
                   r"\$([0-9.]+)\$ and \$([0-9.]+)\$ points at \$\\rho = 0\.80\$ and \$0\.85\$\. It is level with DF-GLS at "
                   r"\$\\rho = 0\.95\$ \(\$p = ([0-9.]+)\$\) and concedes \$([0-9.]+)\$ points at \$\\rho = 0\.97\$ "
                   r"\(\$p = ([0-9.]+)\$\)", 5, pow200),
    "intro_power": ("sec1_introduction.tex", r"exceeds DF-GLS by \$([0-9.]+)\$ points at \$\\rho = 0\.90\$ and \$([0-9.]+)\$ "
                    r"points at \$\\rho = 0\.93\$ with \$n = 200\$, ties it at \$\\rho = 0\.95\$, and concedes \$([0-9.]+)\$ "
                    r"points at \$\\rho = 0\.97\$", 4, intro_pow),
    "abstract_power": ("main.tex", r"exceeds DF-GLS by up to \$([0-9.]+)\$ points.*concedes up to \$([0-9.]+)\$ points", 4, abs_pow),
    "power_n500": ("sec5_montecarlo.tex", r"ahead at \$\\rho = 0\.97\$, \$n = 500\$ by \$([0-9.]+)\$ points and behind at "
                   r"\$\\rho = 0\.99\$ by \$([0-9.]+)\$ points at \$n = 500\$ and \$([0-9.]+)\$ at \$n = 1000\$", 3, pow500),
    "power_adf": ("sec5_montecarlo.tex", r"up to \$(\d+)\$ points at \$\(\\rho, n\) = \(0\.99, 1000\)\$", 2, pow_adf),
    "power_trend": ("sec5_montecarlo.tex", r"leads DF-GLS by \$([0-9.]+)\$ points at \$\(\\rho, n\) = \(0\.90, 200\)\$ and by "
                    r"\$([0-9.]+)\$ points at \$\(0\.95, 500\)\$, and the two are statistically level in (\w+) of the nine "
                    r"informative cells", 3, pow_trend),
    "dgp2": ("sec5_montecarlo.tex", r"level \(\$([0-9.]+)\$ against \$([0-9.]+)\$, \$p = ([0-9.]+)\$\)\. With a break "
             r"\\RMGLS\{\} leads DF-GLS in every cell with \$0\.5 \\leq \\delta \\leq 3\$ in which power is not saturated, "
             r"with McNemar \$p \\leq ([0-9.]+)\$, and the lead grows with the break: \$([0-9.]+)\$ against \$([0-9.]+)\$ at "
             r"\$\(\\delta, n\) = \(1, 200\)\$, \$([0-9.]+)\$ against \$([0-9.]+)\$ at \$\(2, 500\)\$, \$([0-9.]+)\$ against "
             r"\$([0-9.]+)\$ at \$\(2, 1000\)\$ and \$([0-9.]+)\$ against \$([0-9.]+)\$ at \$\(3, 1000\)\$", 6, dgp2),
    "za_exceeds": ("sec5_montecarlo.tex", r"it exceeds \\RMGLS\{\} at \$\\delta = 3\$ for every \$n\$", 2, za),
    "za_delta0": ("sec5_montecarlo.tex", r"\(\$([0-9.]+)\$ at \$\\delta = 0\$, \$n = 200\$, against \$([0-9.]+)\$ for \\RMGLS\{\}\)",
                  2, za0),
    "dgp3": ("sec5_montecarlo.tex", r"at \$r = 4\$ it rejects \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$ at \$n = 200\$, "
             r"\$500\$ and \$1000\$", 2, dgp3),
    "intro_dgp3": ("sec1_introduction.tex", r"rejects \$([0-9.]+)\$ at \$n = 200\$ and a fourfold standard-deviation ratio.*"
                   r"brings the rate to \$([0-9.]+)\$, at a power cost of at most \$(\d+)\$ points", 4, intro_dgp3),
    "awb_rates": ("sec5_montecarlo.tex", r"rejects \$([0-9.]+)\$ and \$([0-9.]+)\$ at \$r=2\$ with \$n = 200\$ and \$500\$, "
                  r"against \$([0-9.]+)\$ and \$([0-9.]+)\$ for the simulated calibration, and \$([0-9.]+)\$ at \$r = 4\$ in "
                  r"both, against \$([0-9.]+)\$ and \$([0-9.]+)\$", 4, awb1),
    "awb_homosk": ("sec5_montecarlo.tex", r"holds size \(\$([0-9.]+)\$ and \$([0-9.]+)\$\)", 1, awb2),
    "awb_cost": ("sec5_montecarlo.tex", r"power cost is \$([0-9.]+)\$ points at \$\(\\rho, n\) = \(0\.95, 200\)\$ and at most "
                 r"\$([0-9.]+)\$ points elsewhere", 2, awb3),
    "awb_rule": ("sec5_montecarlo.tex", r"both conditions were met with equality", 2, awb4),
    "misspec_heavy": ("sec5_montecarlo.tex", r"slightly conservative at \$n = 200\$ \(\$([0-9.]+)\$ and \$([0-9.]+)\$\)", 2, mis1),
    "misspec_shift200": ("sec5_montecarlo.tex", r"at \$n = 200\$ its mean shift is \$\+([0-9.]+)\$ points", 1, mis_shift(200)),
    "misspec_shift1000": ("sec5_montecarlo.tex", r"at \$n = 1000\$ the figures are \$\+([0-9.]+)\$", 2, mis_shift(1000)),
    "misspec_inside": ("sec5_montecarlo.tex", r"It is inside the exact region in (\w+) of the sixteen GARCH cells", 2, mis4),
    "dgp5": ("sec5_montecarlo.tex", r"exceeds the two-channel statistic by \$(\d+)\$ to \$(\d+)\$ points in every cell", 2, dgp5),
    "appB_cv": ("appB_critical_values.tex", r"rises from \$([0-9.]+)\$ at \$n = 100\$ to \$([0-9.]+)\$ at \$n = 1000\$", 2, appb),
    "appB_se": ("appB_critical_values.tex", r"standard error of each quantile is below \$([0-9.]+)\$", 2, appb_se),
    "app_oos": ("sec6_application.tex", r"give \$([0-9.]+)\$, \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$ at \$D = 150\$", 2, app_oos),
    "app_fp": ("sec6_application.tex", r"mean false-positive rate of \$([0-9.]+)\$ over the 48 control", 1, app_fp),
    "app_detections": ("sec6_application.tex", r"it detects (\d+) of the 88 event cells", 1, app_det),
    "app_mzt": ("sec6_application.tex", r"shorter mean latency when it detects \(\$([0-9.]+)\$ against \$([0-9.]+)\$ days\)", 2, app_mzt),
    "app_awb": ("sec6_application.tex", r"The AWB calibration changes little \(\$([0-9.]+)\$, (\d+) detections\)", 2, app_awb),
    "app_target": ("sec6_application.tex", r"At a common false-alarm rate of \$([0-9.]+)\$", 1, app_target),
    "app_episodes": ("sec6_application.tex", r"produces (\d+) false-alarm episodes", 1, app_episodes),
    "app_latency_c": ("sec6_application.tex", r"censored latency of \$([0-9.]+)\$ days, against \$([0-9.]+)\$ for DF-GLS and "
                      r"\$([0-9.]+)\$ for MZ\$_t\$-GLS", 2, app_latc),
    "app_adverse": ("sec6_application.tex", r"registered baseline in (\d+) of the 48 control cells", 1, app_adverse),
    "app_registered": ("sec6_application.tex", r"fewer false-alarm episodes \((\d+)\) and fewer detections \((\d+)\)", 2, app_rhat),
    "dev_statistic": ("sec6_application.tex", r"Mean FP \$([0-9.]+) \\to ([0-9.]+)\$; detections \$(\d+) \\to (\d+)\$; mean "
                      r"latency \$([0-9.]+) \\to ([0-9.]+)\$", 2, app_dev1),
    "dev_awb": ("sec6_application.tex", r"Mean FP \$([0-9.]+) \\to ([0-9.]+)\$; detections \$(\d+) \\to (\d+)\$; latency "
                r"\$([0-9.]+) \\to ([0-9.]+)\$", 2, app_dev2),
}
PLAIN_THETA = {"sec5_montecarlo.tex": r"\\RMGLS\{\} uses \$\\theta = 0\.02\$", "sec1_introduction.tex": r"report everything with \$\\theta = 0\.02\$",
               "sec6_application.tex": r"the constant specification, \$\\theta = 0\.02\$"}


def match(printed, value):
    """La cifra impresa (texto) frente al valor calculado con las fuentes del v13."""
    if printed in WORDS:
        return WORDS[printed] == value
    if re.fullmatch(r"\d+", printed) and float(value).is_integer():
        return int(printed) == int(value)
    d = decimals(printed)
    return TB.fdec(value, d, "binary") == printed or TB.fdec(value, d, "half_up") == printed


def main():
    M = M13(C.MANUSCRIPT)
    S = {V13: Src(V13), A13: Src(A13)}
    out_claims, fails = {}, []
    for key, (fname, pat, span, fn) in CLAIMS.items():
        q = M.find(fname, pat, max(span, SPAN))
        v13, x13 = fn(S[V13])
        v0, x0 = fn(S[A13])
        checks = [match(g, v) for g, v in zip(q["groups"], v13)]
        rec = {"file": q["file"], "line": q["line"], "quote": q["quote"], "printed": q["groups"], "v13": v13, "theta0": v0,
               "extra_v13": x13, "extra_theta0": x0, "v13_reproduces_printed": checks, "reproduced": all(checks)}
        out_claims[key] = rec
        if not all(checks):
            fails.append(key)
    theta_mentions = {f: M.find(f, p, 2) for f, p in PLAIN_THETA.items()}
    out = {"provenance": C.provenance(__file__), "manuscript": {"zip": os.path.basename(C.MANUSCRIPT),
                                                               "sha256": C.sha256_file(C.MANUSCRIPT)},
           "claims": out_claims, "not_reproduced": fails, "theta_mentions": theta_mentions}
    C.write_result(OUT, out, __file__)
    for k, v in out_claims.items():
        print("%-18s %s:%d  impreso %s  v13 %s  theta0 %s %s" % (k, v["file"], v["line"], v["printed"],
                                                               [round(x, 4) if isinstance(x, float) else x for x in v["v13"]],
                                                               [round(x, 4) if isinstance(x, float) else x for x in v["theta0"]],
                                                               "" if v["reproduced"] else "NO REPRODUCE"))
    print("no reproducidas:", fails)
    return 0


if __name__ == "__main__":
    sys.exit(main())
