"""
Auditoria A16 - B16.3 (enmienda 6, lectura E6.5): literales del v17. Solo lee JSON y el zip del v17.

- N1-N8: cada literal nuevo del encargo, con su valor desde JSON, redondeo binario a los decimales impresos (rangos:
  minimo y maximo, y el hacia afuera), y su localizacion en el v17 (archivo:linea).
- N6: registro de frases de sec1_introduction.tex y sec4_montecarlo.tex (plantillas del marco de A13: <> captura una
  cifra, <w> una palabra-numero; los espacios admiten saltos de linea). Cada cifra se recalcula desde su JSON (fuentes
  de A13, A14 y A15) y se compara con las convenciones de A13 (binaria, mitad hacia arriba, cota). Cada frase lleva
  su grupo: "v16" (la cifra ya estaba en el v16) o "v17" (nueva, de A15); se comprueba tambien, automaticamente, si cada
  cifra aparece en el texto del v16. Un barrido lista todo numero con decimales de los dos archivos fuera de tabulares
  \\input: cubierto por una frase, de diseno, o no verificado.
Salida: experiments/results/literals_v17b_audit16.json.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C                                         # noqa: E402
import audit13_q_claims as QC                                      # noqa: E402
import audit13_tables as TB                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "literals_v17b_audit16.json")
FILES = ("sec1_introduction.tex", "sec4_montecarlo.tex")
J = QC.S.J
PRIM = QC.PRIM
ARMS5 = ("i", "ii", "iii", "iv", "v_prime")
GLS_INIT = ("gls_t0", "gls_t0.02", "glsb_t0", "glsbp_t0", "dfgls", "mzt", "msb")
P4 = 10 ** -4                                   # "McNemar p < 10^{-4}"
HALF_TOL = 10 ** -6                             # un valor a menos de esto de la mitad de la ultima cifra es sensible al redondeo
THIRTY_SIX = 36                                 # "thirty-six designs"


# ---------------------------------------------------------------------------
# Fuentes de A15 y A12
# ---------------------------------------------------------------------------
def b1():
    return J("b1_boot_audit15.json")


def b3():
    return J("b3_fixedb_audit15.json")


def a12():
    return J("bA_ma_audit12.json")


def ss(arm, f):
    return b1()["size_summary"][arm][f]


def b1rate(cell, arm):
    return b1()["size"][cell]["rates"][arm]["rate"]


def a12rates(proc):
    return [v["iid"][proc]["rate"] for v in a12()["size"].values()]


def b3rates(cfg):
    return [v["rates"][cfg]["rate"] for v in b3()["size"].values()]


def b3pow(cfg, rho="0p9"):
    return b3()["power"]["pw3_rho%s_n200_c" % rho]["rates"][cfg]["rate"]


def sig_cells(arm):
    """Celdas de potencia con McNemar p < 0.05 del brazo frente a (ii): |diferencia ajustada| en pp."""
    return {k: abs(v["vs_ii"][arm]["diff_pp"]) for k, v in b1()["power"].items() if v["vs_ii"][arm]["mcnemar"]["p_value"] < C.ALPHA}


N1_CELLS = ("sz_ma_0p5_n100_ct", "sz_ma_0p5_n200_ct", "sz_ar_0p5_n100_ct", "sz_ar_0p5_n200_ct")


def ks_upto(case):
    """Mayor n tal que la distancia KS supera el umbral en todo n' <= n."""
    ks = J("e_calib_audit13.json")["cases_by_theta"][PRIM][case]["ks"]
    ns = sorted(int(n) for n in ks)
    last = None
    for n in ns:
        if ks[str(n)]["below_threshold"]:
            break
        last = n
    return last


def ks_d(case, n):
    return J("e_calib_audit13.json")["cases_by_theta"][PRIM][case]["ks"][str(n)]["D"]


def lp_se_max():
    lp = J("b92_theta_audit9.json")["local_power"]
    procs = ("gls_t0", "gls_t0.02", "dfgls", "mzt", "msb", "msb_asy", "envelope")
    N = J("b92_theta_audit9.json")["config"].get("N_local", None) or 20000
    vals = [lp[case]["power"]["%s" % float(c)][p] for case in lp for c in QC.LP_C() for p in procs if p != "envelope"]
    return max((v * (1 - v) / N) ** 0.5 for v in vals), N


# ---------------------------------------------------------------------------
# N1-N8
# ---------------------------------------------------------------------------
def n_literals():
    exact = {}
    out = []
    ii = [b1rate(k, "ii") for k in N1_CELLS]
    i_ = [b1rate(k, "i") for k in N1_CELLS]
    out.append(("N1", "sec4_montecarlo.tex", "the simulated values give rejection rates between $<>$ and $<>$", [min(ii), max(ii)],
                "b1_boot_audit15.json size.<%s>.rates.ii" % "|".join(N1_CELLS), "range"))
    out.append(("N2", "sec4_montecarlo.tex", "the asymptotic ones between $<>$ and $<>$", [min(i_), max(i_)],
                "b1_boot_audit15.json size.<%s>.rates.i" % "|".join(N1_CELLS), "range"))
    gt = sum(1 for k in b1()["size"] if b1rate(k, "ii") > b1rate(k, "i"))
    ties = sum(1 for k in b1()["size"] if b1rate(k, "ii") == b1rate(k, "i"))
    exact["N3"] = {"cells": len(b1()["size"]), "ii_gt_i": gt, "ties": ties}
    lag = J("b0b_lag_audit15.json")
    v1 = lag["cells"]["sz_ar_0p5_n100_ct"]["procs"]["mzt"]["by_k"]["1"]["iid"]["rate"]
    v2 = lag["a10_null"]["100|ct"]["procs"]["mzt"]["by_k"]["1"]["iid"]["rate"]
    out.append(("N4", "sec4_montecarlo.tex", "which the MAIC selects one lag reject $<>$ with the simulated critical value, against $<>$ for "
                "the i.i.d.\\ null paths", [v1, v2],
                "b0b_lag_audit15.json cells.sz_ar_0p5_n100_ct.procs.mzt.by_k.1.iid.rate; a10_null.100|ct.procs.mzt.by_k.1.iid.rate", "values"))
    comp = J("e_calib_audit13.json")["cases_by_theta"][PRIM]["c"]["approximation_cost_comparators"]
    msb = [comp[n]["msb"]["size_published_asymptotic"]["rate"] for n in comp]
    out.append(("N5a", "sec4_montecarlo.tex", "under-reject more mildly, between $<>$ and $<>$", [min(msb), max(msb)],
                "e_calib_audit13.json cases_by_theta.gls_t0.c.approximation_cost_comparators.<n>.msb.size_published_asymptotic", "range"))
    df60 = comp["60"]["dfgls"]["size_published_asymptotic"]
    exact["N5b"] = {"rejections": df60["rejections"], "n": df60["n"], "exact_value": "%d/%d" % (df60["rejections"], df60["n"])}
    out.append(("N5b", "sec4_montecarlo.tex", "DF-GLS over-reject at small $n$ ($<>$ at $n = 60$)", [df60["rate"]],
                "e_calib_audit13.json ...c.approximation_cost_comparators.60.dfgls.size_published_asymptotic", "values"))
    bd = J("b0_iidasy_audit15.json")["b_abs_dev"]["mzt"]["both"]
    out.append(("N7", "sec4_montecarlo.tex", "gives mean absolute deviations of $<>$ and $<>$", [bd["iid"]["mean"], bd["asy"]["mean"]],
                "b0_iidasy_audit15.json b_abs_dev.mzt.both.<iid|asy>.mean", "values"))
    rows = []
    for key, fname, tpl, vals, src, kind in out:
        rows.append(evaluate(key, fname, tpl, vals, src, kind))
    n3 = {"id": "N3", "printed": "in all thirty-six designs", "source": "b1_boot_audit15.json size.<celda>.rates.<ii|i>",
          "value": {"ii_gt_i": gt, "ties": ties, "cells": len(b1()["size"])}, "locations": []}
    for fname, rx in (("sec4_montecarlo.tex", r"relative\s+to\s+the\s+asymptotic\s+ones\s+in\s+all\s+thirty-six\s+designs"),
                      ("sec1_introduction.tex", r"raise\s+every\s+rejection\s+rate\s+relative\s+to\s+the\s+asymptotic\s+ones")):
        m = re.search(rx, V17.files[fname])
        n3["locations"].append({"file": fname, "line": None if m is None else V17.files[fname][:m.start()].count("\n") + 1,
                                "span": None if m is None else [m.start(), m.end()]})
    n3["found"] = all(x["line"] for x in n3["locations"])
    n3["verdict"] = "confirma" if gt == len(b1()["size"]) == THIRTY_SIX else "corrige"
    rows.insert(2, n3)
    swb, awb = sig_cells("v_prime"), sig_cells("iv")
    n8 = {"id": "N8", "printed": "the SWB and the AWB lose comparable amounts", "file": "sec4_montecarlo.tex",
          "line": locate("sec4_montecarlo.tex", r"The\s+SWB\s+and\s+the\s+AWB\s+lose\s+comparable"),
          "source": "b1_boot_audit15.json power.<celda>.vs_ii.<v_prime|iv> (McNemar p < 0.05)",
          "SWB": {"cells": len(swb), "of": len(b1()["power"]), "min_pp": min(swb.values()) if swb else None, "max_pp": max(swb.values()) if swb else None,
                  "by_cell": swb},
          "AWB": {"cells": len(awb), "of": len(b1()["power"]), "min_pp": min(awb.values()) if awb else None, "max_pp": max(awb.values()) if awb else None,
                  "by_cell": awb},
          "SB": {"cells": len(sig_cells("iii")), "min_pp": min(sig_cells("iii").values()), "max_pp": max(sig_cells("iii").values())},
          "verdict": "se reportan los rangos; 'comparable' no se juzga (E6.5)"}
    rows.append(n8)
    return rows, exact


V17 = None


def locate(fname, rx):
    m = re.search(rx, V17.files[fname])
    return None if m is None else V17.files[fname][:m.start()].count("\n") + 1


def evaluate(key, fname, tpl, vals, src, kind):
    text = V17.files[fname]
    m = re.search(QC.pattern(tpl), text)
    if m is None:
        return {"id": key, "file": fname, "found": False, "template": tpl, "value": vals, "source": src}
    line = text[:m.start()].count("\n") + 1
    nums = []
    for p, x in zip(m.groups(), vals):
        conv = QC.conventions(p, x, False)
        rec = {"printed": p, "value": x, "conventions": conv, "binary": None if p in QC.WORDS else QC.correct(p, x),
               "verdict": "confirma" if ("binaria" in conv or conv == ["palabra"]) else ("confirma (mitad hacia arriba)" if conv else "corrige"),
               "correct": None if conv else QC.correct(p, x)}
        if p not in QC.WORDS and kind != "count":
            d = len(p.split(".")[1]) if "." in p else 0
            scaled = abs(x) * 10 ** d
            rec["rounding_sensitive"] = abs(scaled - int(scaled) - 0.5) < HALF_TOL
        nums.append(rec)
    out = {"id": key, "file": fname, "line": line, "found": True, "span": [m.start(), m.end()], "quote": re.sub(r"\s+", " ", m.group(0)),
           "source": src, "kind": kind,
           "numbers": nums, "verdict": "confirma" if all(n["verdict"].startswith("confirma") for n in nums) else "corrige"}
    if kind == "range":
        a, b = nums
        out["outward"] = [QC.correct(a["printed"], a["value"], "lower"), QC.correct(b["printed"], b["value"], "upper")]
    return out


# ---------------------------------------------------------------------------
# N6: registro de frases de sec1 y sec4 del v17
# ---------------------------------------------------------------------------
def r(v, src, checks=()):
    return v, src, list(checks)


def reg():
    cal, calc, eq, dd, sz, szc, ini, awbc, gap, att = QC.cal, QC.calc, QC.eq, QC.dd, QC.sz, QC.szc, QC.ini, QC.awbc, QC.gap, QC.attrib
    b = lambda: att()["by_n"]                                           # noqa: E731
    diag = lambda: att()["diagnostics_n200"]                            # noqa: E731
    ma = lambda: szc("ma_m0p8", 200, "c")                               # noqa: E731
    reg1 = J("b1_boot_audit15.json")["exact_region"]
    reg2 = J("bA_ma_audit12.json")["exact_region_20000"]
    lpv = [att()["cells"]["lp_dm_c%d" % c]["diffs"]["a_minus_bp"]["delta"] * C.PP for c in (5, 10, 15)]
    k4 = "dgp3_r4_n200"
    cells_awb = J("e_awb_audit13.json")["cells"]
    rule = J("e_awb_audit13.json")["rule"]
    a7 = [v["bootstrap_dfgls"]["rate"] for v in J("dgp3_recast_composite_null_audit7.json")["cells"].values()]
    comp_ct = J("e_calib_audit13.json")["cases_by_theta"][PRIM]["ct"]["approximation_cost_comparators"]
    se, Nlp = lp_se_max()
    lpc = QC.LP_C()
    lp_trend = max(abs(gap("ct", c, p)) for c in lpc if c > 0 for p in (PRIM, "msb", "dfgls", "mzt"))
    return [
        # --- sec1 ---
        ("i_kappa", "sec1_introduction.tex", "with $\\kappa(-7) \\approx <>$", lambda: r([QC.kappa(QC.CBAR())], "formula kappa, c = -7"), (), "v16"),
        ("i_exact", "sec1_introduction.tex", "squared statistic is $<>$ at $n = 200$", lambda: r([QC.anchor(200)], "bF_anchor_audit12.json rows.200.exact"), (), "v16"),
        ("i_pub", "sec1_introduction.tex", "values of MSB-GLS reject $<>$ at $n = 200$ and $<>$ at $n = 60$, and DF-GLS $<>$ at $n = 200$",
         lambda: r([calc("ct", 200, "msb")["rate"], calc("ct", 60, "msb")["rate"], calc("ct", 200, "dfgls")["rate"]],
                   "e_calib_audit13.json ...ct.approximation_cost_comparators.<n>.<msb|dfgls>.size_published_asymptotic"), (), "v16"),
        ("i_boot", "sec1_introduction.tex", "lowers the mean absolute size distortion from $<>$ to $<>$ and the largest from $<>$ to $<>$",
         lambda: r([ss("ii", "D"), ss("iii", "D"), ss("ii", "M"), ss("iii", "M")], "b1_boot_audit15.json size_summary.<ii|iii>.<D|M>",
                   [("D(ii) >= D(i): 'no closer' sobre los treinta disenos", ss("ii", "D") >= ss("i", "D"))]), (), "v17"),
        ("i_bootpower", "sec1_introduction.tex", "costs between $<>$ and $<>$ points of size-adjusted power in <w> of <w> designs",
         lambda: r([min(sig_cells("iii").values()), max(sig_cells("iii").values()), len(sig_cells("iii")), len(b1()["power"])],
                   "b1_boot_audit15.json power.<celda>.vs_ii.iii (McNemar p < 0.05)"), (), "v17"),
        ("i_attrib", "sec1_introduction.tex", "raises power by $<>$ percentage points on average over seven autoregressive alternatives at "
         "$n = 200$, of which $<>$ survive",
         lambda: r([b()["c|200"]["a_minus_b"]["mean"] * C.PP, b()["c|200"]["a_minus_bp"]["mean"] * C.PP],
                   "bB_attrib_audit12.json by_n.c|200.<a_minus_b|a_minus_bp>.mean"), (), "v16"),
        ("i_mabias", "sec1_introduction.tex", "$<>$ at $\\psi = -0.8$ and $n = 200$; the calibrated test then rejects $<>$",
         lambda: r([ma()["bartlett_factor_at_median_B"]["factor"], sz("ma_m0p8", 200, "c")],
                   "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.<bartlett_factor_at_median_B.factor|iid.gls_t0>"), (), "v16"),
        ("i_fixedb", "sec1_introduction.tex", "the rejection rate stays between $<>$ and $<>$ over thirty-six designs, but power against an "
         "autoregression of $0.90$ at $n = 200$ falls to $<>$, against $<>$ with the Andrews bandwidth",
         lambda: r([min(b3rates("b=0.3")), max(b3rates("b=0.3")), b3pow("b=0.3"), b3pow("gls_t0")],
                   "b3_fixedb_audit15.json size.<celda>.rates.b=0.3; power.pw3_rho0p9_n200_c.rates.<b=0.3|gls_t0>"), (), "v17"),
        ("i_dgp3", "sec1_introduction.tex", "rejects $<>$ at $n = 200$ and a fourfold standard-deviation ratio, as much as MSB-GLS and more than "
         "DF-GLS ($<>$); a wild-bootstrap calibration brings the rate to $<>$ at a power cost of at most $<>$ points",
         lambda: r([eq(k4), eq(k4, "dfgls"), awbc(k4), rule["ii_threshold_pp"]],
                   "e_equalized_audit13.json dgp3_r4_n200; e_awb_audit13.json cells.dgp3_r4_n200 y rule.ii_threshold_pp",
                   [("MSB-GLS 'as much': |MSB-B - MSB-GLS| <= 1 punto", abs(eq(k4) - eq(k4, "msb")) * C.PP <= 1),
                    ("perdida de potencia maxima <= umbral", max(rule["ii_power_loss_pp"].values()) <= rule["ii_threshold_pp"])]), {3: "upper"}, "v16"),
        ("i_init", "sec1_introduction.tex", "no GLS-based test rejects more than $<>$, while ADF rejects $<>$",
         lambda: r([max(ini("0p9", "alpha2", p) for p in GLS_INIT), ini("0p9", "alpha2", "adf")], "bC_initial_audit12.json cells.0p9|alpha2.power"),
         {0: "upper"}, "v16"),
        ("i_garch", "sec1_introduction.tex", "the size distortion of \\RMGLS{} lies between that of DF-GLS and that of ADF",
         lambda: r([], "b92_theta_audit9.json misspec (desplazamiento GARCH, n = 200)",
                   [("DF-GLS < MSB-B < ADF (desplazamiento medio, n = 200)", QC.shift(200, "dfgls") < QC.shift(200) < QC.shift(200, "adf"))]), (), "v16"),
        # --- sec4 ---
        ("m_regions", "sec4_montecarlo.tex", "$[<>, <>]$ for 5000 paths and $[<>, <>]$ for",
         lambda: r([reg1[0], reg1[1], reg2[0], reg2[1]], "b1_boot_audit15.json exact_region; bA_ma_audit12.json exact_region_20000"), (), "v16"),
        ("m_cal_c", "sec4_montecarlo.tex", "over-rejects: $<>$ at $n = 60$, $<>$ at $n = 100$ and $<>$ at $n = 200$, against $<>$, $<>$ and $<>$",
         lambda: r([cal("c", 60), cal("c", 100), cal("c", 200), cal("c", 60, "size_with_cv_at_n"), cal("c", 100, "size_with_cv_at_n"),
                    cal("c", 200, "size_with_cv_at_n")], "e_calib_audit13.json ...c.approximation_cost.<n>.<size_with_cv_n20000|size_with_cv_at_n>"),
         (), "v16"),
        ("m_cal_ct", "sec4_montecarlo.tex", "under-rejects: $<>$ at $n = 60$, $<>$ at $n = 100$ and $<>$ at $n = 200$, against $<>$, $<>$ and $<>$",
         lambda: r([cal("ct", 60), cal("ct", 100), cal("ct", 200), cal("ct", 60, "size_with_cv_at_n"), cal("ct", 100, "size_with_cv_at_n"),
                    cal("ct", 200, "size_with_cv_at_n")], "e_calib_audit13.json ...ct.approximation_cost.<n>.<size_with_cv_n20000|size_with_cv_at_n>"),
         (), "v16"),
        ("m_ks", "sec4_montecarlo.tex", "at every $n$ up to $<>$ in the constant case ($D = <>$ at $n = 200$, $<>$ at $n = 1000$) and up to $<>$ in the trend",
         lambda: r([ks_upto("c"), ks_d("c", 200), ks_d("c", 1000), ks_upto("ct")], "e_calib_audit13.json cases_by_theta.gls_t0.<c|ct>.ks"), (), "v16"),
        ("m_pub_ct", "sec4_montecarlo.tex", "MSB-GLS rejects $<>$ at $n = 60$, $<>$ at $n = 200$ and $<>$ at $n = 1000$, and DF-GLS $<>$ at $n = 200$",
         lambda: r([calc("ct", 60, "msb")["rate"], calc("ct", 200, "msb")["rate"], calc("ct", 1000, "msb")["rate"], calc("ct", 200, "dfgls")["rate"]],
                   "e_calib_audit13.json ...ct.approximation_cost_comparators.<n>.<msb|dfgls>.size_published_asymptotic",
                   [("simulados en la region en todo n (tendencia), MSB-GLS y DF-GLS",
                     all(comp_ct[n][p]["size_simulated_at_n"]["in_region"] for n in comp_ct for p in ("msb", "dfgls")))]), (), "v16"),
        ("m_note_calib", "sec4_montecarlo.tex", "$[<>, <>]$. $q(20\\,000)$ is $<>$ (constant) and $<>$ (trend)",
         lambda: r([reg2[0], reg2[1], J("e_calib_audit13.json")["cases_by_theta"][PRIM]["c"]["cv_n20000"],
                    J("e_calib_audit13.json")["cases_by_theta"][PRIM]["ct"]["cv_n20000"]],
                   "bA_ma_audit12.json exact_region_20000; e_calib_audit13.json cases_by_theta.gls_t0.<c|ct>.cv_n20000"), (), "v16"),
        ("m_lp", "sec4_montecarlo.tex", "\\RMGLS{} lies $<>$, $<>$ and $<>$ points below the envelope at $c = 5$, $10$ and $15$, and MSB-GLS, "
         "which differs from it only in the scale, $<>$, $<>$ and $<>$ points below",
         lambda: r([gap("dm", 5), gap("dm", 10), gap("dm", 15), gap("dm", 5, "msb"), gap("dm", 10, "msb"), gap("dm", 15, "msb")],
                   "b92_theta_audit9.json local_power.dm.power.<c>.<envelope - gls_t0|msb> (x100)"), (), "v16"),
        ("m_lp_ct", "sec4_montecarlo.tex", "the four tests are within $<>$ points of the envelope",
         lambda: r([lp_trend], "b92_theta_audit9.json local_power.ct: max |envelope - p| sobre c > 0 y p en MSB-B, MSB-GLS, DF-GLS, MZ_t-GLS"),
         {0: "upper"}, "v16"),
        ("m_eq", "sec4_montecarlo.tex", "\\RMGLS{} exceeds DF-GLS by $<>$ points at $\\rho = 0.90$ ($<>$ against $<>$, McNemar $p < 10^{-4}$), and in "
         "the trend case by $<>$ points",
         lambda: r([dd("dgp1_rho0p9_n200"), eq("dgp1_rho0p9_n200"), eq("dgp1_rho0p9_n200", "dfgls"), dd("ct_power_rho0p9_n200")],
                   "e_equalized_audit13.json <dgp1_rho0p9_n200|ct_power_rho0p9_n200>.rates_sim.<gls_t0|dfgls>",
                   [("McNemar p < 1e-4", QC.eqp("dgp1_rho0p9_n200") < P4)]), (), "v16"),
        ("m_lp_se", "sec4_montecarlo.tex", "Monte Carlo standard errors are at most $<>$",
         lambda: r([se], "b92_theta_audit9.json local_power (EE binomial con N = %d)" % Nlp), {0: "upper"}, "v16"),
        ("m_attrib", "sec4_montecarlo.tex", "(a)$-$(b) is $<>$ points on average over the seven autoregressive alternatives at $n=200$ in the "
         "constant case, falling to $<>$ points at $n = 500$ and $<>$ at $n = 1000$, and $<>$ points in the trend case",
         lambda: r([b()["c|200"]["a_minus_b"]["mean"] * C.PP, b()["c|500"]["a_minus_b"]["mean"] * C.PP, b()["c|1000"]["a_minus_b"]["mean"] * C.PP,
                    b()["ct|200"]["a_minus_b"]["mean"] * C.PP], "bB_attrib_audit12.json by_n.<celda>.a_minus_b.mean (x100)"), (), "v16"),
        ("m_attrib_pq", "sec4_montecarlo.tex", "(b$'$)$-$(b) is $<>$ points at $n = 200$, and (a)$-$(b$'$) is still $<>$",
         lambda: r([b()["c|200"]["bp_minus_b"]["mean"] * C.PP, b()["c|200"]["a_minus_bp"]["mean"] * C.PP],
                   "bB_attrib_audit12.json by_n.c|200.<bp_minus_b|a_minus_bp>.mean (x100)"), (), "v16"),
        ("m_attrib_lp", "sec4_montecarlo.tex", "(a)$-$(b$'$) lying between $<>$ and $<>$ points",
         lambda: r([min(lpv), max(lpv)], "bB_attrib_audit12.json cells.lp_dm_c<5|10|15>.diffs.a_minus_bp.delta (x100)"), (), "v16"),
        ("m_attrib_size", "sec4_montecarlo.tex", "which translates into $<>$ points of power in the trend case",
         lambda: r([b()["ct|200"]["b_minus_c"]["mean"] * C.PP], "bB_attrib_audit12.json by_n.ct|200.b_minus_c.mean (x100)"), (), "v16"),
        ("m_attrib_diag", "sec4_montecarlo.tex", "the median of $\\sAR$ is $<>$ at $\\rho = 0.90$, against $<>$ for $\\hacsig^2$",
         lambda: r([diag()["dgp1_rho0p9_n200"]["s2ar_gls"], diag()["dgp1_rho0p9_n200"]["s2_hac"]],
                   "bB_attrib_audit12.json diagnostics_n200.dgp1_rho0p9_n200.<s2ar_gls|s2_hac>",
                   [("MAIC sin retardos en la mediana para rho >= 0.90",
                     all(v["k_gls"] == 0 for v in diag().values()
                         if v["case"] == "c" and v["rho"] >= diag()["dgp1_rho0p9_n200"]["rho"]))]), (), "v16"),
        ("m_serial_range", "sec4_montecarlo.tex", "Its rejection rate ranges from $<>$ to $<>$",
         lambda: r([min(a12rates(PRIM)), max(a12rates(PRIM))], "bA_ma_audit12.json size.<celda>.iid.gls_t0 (36 celdas)"), (), "v16"),
        ("m_serial_ma", "sec4_montecarlo.tex", "over-rejects heavily: $<>$ at $\\psi = -0.8$ and $n = 200$ in the constant case, $<>$ in the trend "
         "case, and $<>$ and $<>$ at $n = 500$",
         lambda: r([sz("ma_m0p8", 200, "c"), sz("ma_m0p8", 200, "ct"), sz("ma_m0p8", 500, "c"), sz("ma_m0p8", 500, "ct")],
                   "bA_ma_audit12.json size.sz_ma_m0p8_n<200|500>_<c|ct>.iid.gls_t0"), (), "v16"),
        ("m_serial_diag", "sec4_montecarlo.tex", "$\\psi = -0.8$ and $n = 200$ is $<>$, against the population factor $<>$",
         lambda: r([ma()["diagnostics"]["s2_over_omega2"]["median"], ma()["bartlett_factor_at_median_B"]["factor"]],
                   "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.<diagnostics.s2_over_omega2.median|bartlett_factor_at_median_B.factor>"), (), "v16"),
        ("m_serial_ar", "sec4_montecarlo.tex", "rejecting $<>$ at $\\phi = 0.5$ and $n = 200$ in the trend case",
         lambda: r([sz("ar_0p5", 200, "ct")], "bA_ma_audit12.json size.sz_ar_0p5_n200_ct.iid.gls_t0"), (), "v16"),
        ("m_serial_lag", "sec4_montecarlo.tex", "its median lag at $\\psi = -0.8$ and $n = 200$ is $<>$ in the constant case, and the median of "
         "$\\sAR/\\omega^2$ is $<>$",
         lambda: r([ma()["diagnostics"]["k"]["median"], ma()["diagnostics"]["s2ar_over_omega2"]["median"]],
                   "bA_ma_audit12.json size.sz_ma_m0p8_n200_c.diagnostics.<k|s2ar_over_omega2>.median"), (), "v16"),
        ("m_serial_others", "sec4_montecarlo.tex", "rejects between $<>$ and $<>$, DF-GLS between $<>$ and $<>$, and ADF up to $<>$",
         lambda: r([min(a12rates("msb")), max(a12rates("msb")), min(a12rates("dfgls")), max(a12rates("dfgls")), max(a12rates("adf"))],
                   "bA_ma_audit12.json size.<celda>.iid.<msb|dfgls|adf> (36 celdas)"), (), "v17"),
        ("m_mzt_dm", "sec4_montecarlo.tex", "deviation from the nominal level is $<>$ with simulated and $<>$ with asymptotic critical values, and the "
         "largest is $<>$ and $<>$",
         lambda: r([ss("ii", "D"), ss("i", "D"), ss("ii", "M"), ss("i", "M")], "b1_boot_audit15.json size_summary.<ii|i>.<D|M>"), (), "v17"),
        ("m_boot_dm", "sec4_montecarlo.tex", "is $<>$ with the SB, $<>$ with the SWB and $<>$ with the AWB, against $<>$ with the tabulated values",
         lambda: r([ss("iii", "D"), ss("v_prime", "D"), ss("iv", "D"), ss("ii", "D")], "b1_boot_audit15.json size_summary.<iii|v_prime|iv|ii>.D"),
         (), "v17"),
        ("m_boot_region", "sec4_montecarlo.tex", "in one i.i.d.\\ design ($<>$ against a lower limit of $<>$), and the AWB in <w>",
         lambda: r([b1rate("sz_ma_0_n500_ct", "v_prime"), b1()["exact_region"][0],
                    sum(1 for k, v in b1()["size"].items() if v["err_tag"] == "ma_0" and not v["rates"]["iv"]["in_region"])],
                   "b1_boot_audit15.json size.sz_ma_0_n500_ct.rates.v_prime; exact_region; celdas iid fuera para iv",
                   [("SWB fuera en exactamente una celda iid",
                     sum(1 for v in b1()["size"].values() if v["err_tag"] == "ma_0" and not v["rates"]["v_prime"]["in_region"]) == 1)]), (), "v17"),
        ("m_boot_ar", "sec4_montecarlo.tex", "($<>$ against $<>$ with an autoregressive coefficient",
         lambda: r([b1rate("sz_ar_0p5_n100_ct", "iii"), b1rate("sz_ar_0p5_n100_ct", "ii")], "b1_boot_audit15.json size.sz_ar_0p5_n100_ct.rates.<iii|ii>"),
         (), "v17"),
        ("m_boot_ma", "sec4_montecarlo.tex", "it rejects $<>$ at $n = 500$ in the constant case, and at $n = 100$ in the trend case every calibration "
         "rejects between $<>$ and $<>$",
         lambda: r([b1rate("sz_ma_m0p8_n500_c", "iii"), min(b1rate("sz_ma_m0p8_n100_ct", a) for a in ARMS5),
                    max(b1rate("sz_ma_m0p8_n100_ct", a) for a in ARMS5)], "b1_boot_audit15.json size.<sz_ma_m0p8_n500_c|sz_ma_m0p8_n100_ct>.rates"),
         (), "v17"),
        ("m_bootpower", "sec4_montecarlo.tex", "the SB loses between $<>$ and $<>$ points of size-adjusted power in <w> of <w> designs",
         lambda: r([min(sig_cells("iii").values()), max(sig_cells("iii").values()), len(sig_cells("iii")), len(b1()["power"])],
                   "b1_boot_audit15.json power.<celda>.vs_ii.iii (McNemar p < 0.05)",
                   [("en las otras dos |dif| < 1 punto y p >= 0.05",
                     all(abs(v["vs_ii"]["iii"]["diff_pp"]) < 1 and v["vs_ii"]["iii"]["mcnemar"]["p_value"] >= C.ALPHA
                         for v in b1()["power"].values() if v["vs_ii"]["iii"]["mcnemar"]["p_value"] >= C.ALPHA))]), (), "v17"),
        ("m_fixedb", "sec4_montecarlo.tex", "With $b = 0.3$ the rejection rate stays between $<>$ and $<>$ over the thirty-six designs, but power "
         "against an autoregression of $0.90$ at $n = 200$ falls to $<>$, against $<>$ with the Andrews bandwidth and $<>$ with $\\sAR$; with "
         "$b = 1$ it is $<>$",
         lambda: r([min(b3rates("b=0.3")), max(b3rates("b=0.3")), b3pow("b=0.3"), b3pow("gls_t0"), b3pow("glsb_t0"), b3pow("b=1")],
                   "b3_fixedb_audit15.json size.<celda>.rates.b=0.3; power.pw3_rho0p9_n200_c.rates.<b=0.3|gls_t0|glsb_t0|b=1>"), (), "v17"),
        ("m_fixedb2", "sec4_montecarlo.tex", "has power $<>$ and rejects up to $<>$, and $b = 0.1$ has power $<>$ and rejects up to $<>$",
         lambda: r([b3pow("LLSW"), max(b3rates("LLSW")), b3pow("b=0.1"), max(b3rates("b=0.1"))],
                   "b3_fixedb_audit15.json power.pw3_rho0p9_n200_c.rates.<LLSW|b=0.1>; max size.<celda>.rates.<LLSW|b=0.1>"), (), "v17"),
        ("m_dgp3", "sec4_montecarlo.tex", "\\RMGLS{} rejects $<>$, $<>$ and $<>$ at $r = 4$ and $n = 200$, $500$ and $1000$, as much as MSB-GLS and more "
         "than MZ$_t$-GLS ($<>$ at $n = 200$) and DF-GLS ($<>$)",
         lambda: r([eq(k4), eq("dgp3_r4_n500"), eq("dgp3_r4_n1000"), eq(k4, "mzt"), eq(k4, "dfgls")],
                   "e_equalized_audit13.json dgp3_r4_n<n>.rates_sim.<gls_t0|mzt|dfgls>",
                   [("'as much as MSB-GLS': |MSB-B - MSB-GLS| <= 1 punto en r = 4",
                     all(abs(eq("dgp3_r4_n%d" % n) - eq("dgp3_r4_n%d" % n, "msb")) * C.PP <= 1 for n in (200, 500, 1000)))]), (), "v16"),
        ("m_awb", "sec4_montecarlo.tex", "brings the rate to $<>$ at $r = 4$, and it holds size under homoskedastic innovations, at a power cost of at "
         "most $<>$ points. The wild bootstrap DF-GLS of Cavaliere and Taylor~\\cite{cavaliere2008bootstrap} rejects between $<>$ and $<>$",
         lambda: r([awbc(k4), rule["ii_threshold_pp"], min(a7), max(a7)],
                   "e_awb_audit13.json cells.dgp3_r4_n200.awb y rule; dgp3_recast_composite_null_audit7.json cells.<celda>.bootstrap_dfgls",
                   [("perdida maxima <= umbral", max(rule["ii_power_loss_pp"].values()) <= rule["ii_threshold_pp"]),
                    ("AWB en la region bajo homocedasticidad (indep n200, n500)",
                     all(cells_awb[c]["awb"].get("in_region", True) for c in ("indep_n200", "indep_n500")))]), {1: "upper"}, "v16"),
        ("m_init", "sec4_montecarlo.tex", "at $\\alpha = 2$ and $\\rho = 0.90$ none rejects more than $<>$, and at $\\alpha = 4$ all reject $<>$, while "
         "ADF rejects $<>$ and $<>$",
         lambda: r([max(ini("0p9", "alpha2", p) for p in GLS_INIT), max(ini("0p9", "alpha4", p) for p in GLS_INIT), ini("0p9", "alpha2", "adf"),
                    ini("0p9", "alpha4", "adf")], "bC_initial_audit12.json cells.0p9|<alpha2|alpha4>.power"), {0: "upper"}, "v16"),
        ("m_init1", "sec4_montecarlo.tex", "rejecting $<>$ against $<>$ for DF-GLS",
         lambda: r([ini("0p9", "alpha1", PRIM), ini("0p9", "alpha1", "dfgls")], "bC_initial_audit12.json cells.0p9|alpha1.power.<gls_t0|dfgls>",
                   [("MSB-B pierde menos que los otros GLS a alpha = 1",
                     all(ini("0p9", "alpha1", PRIM) >= ini("0p9", "alpha1", p) for p in GLS_INIT))]), (), "v16"),
        ("m_garch", "sec4_montecarlo.tex", "is $<>$ points, against $<>$ for DF-GLS, $<>$ for MZ$_t$-GLS and $<>$ for ADF",
         lambda: r([QC.shift(200), QC.shift(200, "dfgls"), QC.shift(200, "mzt"), QC.shift(200, "adf")],
                   "b92_theta_audit9.json misspec (GARCH, caso constante, n = 200): delta_vs_independent medio (x100)"), (), "v16"),
    ]


DESIGN_CTX = QC.CONTEXT_DESIGN + [
    (r"\\ncal = 5\\times10\^5|\\times ?10\^", "tamano de simulacion"),
    (r"Opus~\d|Gemini~\d|Fable~\d|Claude", "version de modelo (declaracion de IA)"),
    (r"autoregression of \$0\.90\$|\\rho = 0\.90", "celda de diseno"),
    (r"b = 0\.\d|b = 1\$|b \\in", "b de diseno"),
    (r"at least \$0\.005\$|at least \$0\.010\$|below \$0\.02\$", "margen registrado (prediccion 14cbca7)"),
    (r"\\kappa\(-7\)|1/2", "constante"),
    (r"\\psi = -0\.8|\\psi \\in|coefficient of \$0\.5\$|errors of \$-0\.5\$", "parametro del error serial"),
    (r"\\supptab\{\d+\.\d+\}", "numero de tabla del suplemento"),
]


def sweep(covered):
    items = []
    for fname in FILES:
        text = V17.files[fname]
        tabs = [(m.start(), m.end()) for m in re.finditer(r"\\begin\{tabular\}.*?\\end\{tabular\}", text, flags=re.S)]
        for m in re.finditer(r"(?<![A-Za-z_\d.])\d+\.\d+", text):
            a = m.start()
            line = text[:a].count("\n") + 1
            ls = text.rfind("\n", 0, a) + 1
            if re.search(r"(?<!\\)%", text[ls:a]):
                continue
            hit = next((k for x, y, k in covered.get(fname, []) if x <= a < y), None)
            ctx = re.sub(r"\s+", " ", text[max(0, a - 50):m.end() + 30])
            if hit:
                status, why = "cubierta", hit
            elif any(x <= a < y for x, y in tabs):
                status, why = "tabular", None
            else:
                why = next((lab for pat, lab in DESIGN_CTX if re.search(pat, ctx)), None)
                status = "diseno" if why else "no verificada"
            items.append({"file": fname, "line": line, "token": m.group(0), "status": status, "reason": why, "context": ctx})
    return items


def in_v16(token, v16text):
    return re.search(r"(?<![\d.])%s(?![\d])" % re.escape(token.lstrip("+")), v16text) is not None


def main():
    global V17
    V17 = C.v17()
    v16 = C.v16()
    v16text = "\n".join(t for k, t in v16.files.items() if k.endswith(".tex"))
    nrows, exact = n_literals()
    claims, covered, missing = {}, {}, []
    for key, fname, tpl, fn, bound, group in reg():
        text = V17.files[fname]
        m = re.search(QC.pattern(tpl), text)
        if m is None:
            missing.append(key)
            claims[key] = {"file": fname, "found": False, "template": tpl, "group": group}
            continue
        vals, src, checks = fn()
        rows = []
        for i, (p, x) in enumerate(zip(m.groups(), list(vals) + [None] * len(m.groups()))):
            kind = bound.get(i) if isinstance(bound, dict) else None
            conv = QC.conventions(p, x, kind == "upper") if x is not None else []
            pv = QC.WORDS[p] if p in QC.WORDS else float(p)
            holds = True if kind is None or x is None else (x <= pv + QC.BOUND_EPS if kind == "upper" else x >= pv - QC.BOUND_EPS)
            if x is None:
                verdict = "sin fuente"
            elif conv and holds:
                verdict = "confirma" + ("" if "binaria" in conv or conv == ["palabra"] else " (%s)" % ", ".join(conv))
            else:
                verdict = "corrige"
            rows.append({"printed": p, "value": x, "conventions": conv, "bound": kind, "bound_holds": holds, "verdict": verdict,
                         "correct": None if verdict.startswith("confirma") else (QC.correct(p, x, kind if conv else None) if x is not None else None),
                         "in_v16_text": in_v16(p, v16text) if p not in QC.WORDS else None})
        covered.setdefault(fname, []).append((m.start(), m.end(), key))
        claims[key] = {"file": fname, "line": text[:m.start()].count("\n") + 1, "found": True, "group": group,
                       "quote": re.sub(r"\s+", " ", m.group(0)), "source": src, "numbers": rows,
                       "checks": [{"check": c, "holds": bool(h)} for c, h in checks],
                       "verdict": "confirma" if all(r["verdict"].startswith("confirma") for r in rows) and all(h for _, h in checks) else "corrige"}
    for x in nrows:
        for loc in ([x] if x.get("span") else []) + [l for l in x.get("locations", []) if l.get("span")]:
            covered.setdefault(loc["file"], []).append((loc["span"][0], loc["span"][1], x["id"]))
    items = sweep(covered)
    counts = {s: sum(1 for i in items if i["status"] == s) for s in ("cubierta", "diseno", "tabular", "no verificada")}
    v16_rows = [(k, n) for k, c in claims.items() if c.get("found") and c["group"] == "v16" for n in c["numbers"]]
    bad = [{"claim": k, "file": claims[k]["file"], "line": claims[k]["line"], **n} for k, c in claims.items() if c.get("found")
           for n in c["numbers"] if not n["verdict"].startswith("confirma")]
    failed = [{"claim": k, "check": x["check"]} for k, c in claims.items() if c.get("found") for x in c["checks"] if not x["holds"]]
    group_mismatch = [{"claim": k, "printed": n["printed"]} for k, c in claims.items() if c.get("found") and c["group"] == "v16"
                      for n in c["numbers"] if n["in_v16_text"] is False]
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 6, lectura E6.5",
           "inputs": {"v17_zip_sha256": V17.sha256, "v16_zip_sha256": v16.sha256},
           "N": nrows, "N_exact": exact,
           "N_summary": {"confirma": sum(1 for x in nrows if x.get("verdict") == "confirma"),
                         "corrige": sum(1 for x in nrows if x.get("verdict") == "corrige"),
                         "not_found": [x["id"] for x in nrows if x.get("found") is False]},
           "N6": {"claims": claims, "templates_not_found": missing, "not_confirmed": bad, "failed_checks": failed,
                  "v16_numbers": len(v16_rows), "v16_confirmed": sum(1 for _, n in v16_rows if n["verdict"].startswith("confirma")),
                  "group_vs_v16_text": group_mismatch, "sweep": {"counts": counts, "items": items}}}
    C.write_result(OUT, out, __file__)
    for x in nrows:
        print(x["id"], x.get("line"), x.get("verdict"), [(n["printed"], n["value"], n["verdict"]) for n in x.get("numbers", [])] or
              {k: x[k] for k in ("SWB", "AWB") if k in x})
    print("N6 frases:", len(claims), "no encontradas:", missing, "| cifras v16:", len(v16_rows), "confirmadas:", out["N6"]["v16_confirmed"])
    for b in bad:
        print("  NO", b["claim"], b["line"], b["printed"], "->", b["correct"], "(%s)" % b["value"])
    for f in failed:
        print("  COMPROBACION FALLA", f)
    print("grupo frente a texto v16:", group_mismatch)
    print("barrido:", counts)
    for i in items:
        if i["status"] == "no verificada":
            print("  ?", i["file"], i["line"], i["token"], "|", i["context"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
