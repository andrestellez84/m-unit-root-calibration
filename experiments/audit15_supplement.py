"""
Auditoria A15 - B15.7: reconstruccion de supplementary/ segun SUPPLEMENT_PLAN.md (S1-S9) para el
articulo actual (enmienda 4, lecturas 7.1-7.5). Sin simulacion: solo lee JSON y exportaciones ya
commiteadas; lo recorre tests/test_no_literals_audit15.py.

Estructura: supplementary/{supplement.tex, README.md, MANIFEST.sha256, tables/, data/, protocols/}.
Anonimizado segun B15.5 (enmienda 1, E1.7): sin rutas ni nombres de usuario, apellido, correo ni URL;
hashes de commit conservados; sin URL externa. Compilacion de control con pdflatex en un directorio
temporal (el PDF no se guarda).

B15.7b (enmienda 5, lecturas 7b.1-7b.9): etiquetas legibles en S3b/S3c, titulos descriptivos en S6,
sin critB en S6, nota de RM en S1 y S6, p-valores con un solo formato, "normal" en misspec y notas de
las marcas del v13. Con --out <dir> genera y compila en <dir> (nunca en supplementary/) y escribe
supplement_fix_audit15.json con el diagnostico de columnas de las tablas dgp5 y el control de KPSS^a.

Salida: experiments/results/supplement_audit15.json (o supplement_fix_audit15.json con --out).
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_b5_anon as AN                                       # noqa: E402
import audit13_common as C13                                       # noqa: E402
import audit13_tables as TB                                        # noqa: E402
import audit13_t_tables as T13                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "supplement_audit15.json")
OUT_FIX = os.path.join(C.RESULTS, "supplement_fix_audit15.json")        # enmienda 5, 7b: generacion de control con --out
SUPP = os.path.join(C.REPO, "supplementary")
OLD_MARKER = "supplementary/code/stationarity_test/statistic.py"     # archivo del paquete anterior (dos canales)
PDFLATEX = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe")
EXPORTS = {
    "tab_lag_audit15.tex": C.TABLES, "tab_fixedb_size_audit15.tex": C.TABLES, "tab_fixedb_size_note_audit15.tex": C.TABLES,
    "tab_serial_asy_audit15.tex": C.TABLES, "tab_critMSB_audit14.tex": C.C14.TABLES, "tab_critMSB_note_audit14.tex": C.C14.TABLES,
}
DATA = ("e_equalized_audit13.json", "e_dgp5_audit13.json", "t5_claims_audit11.json", "b2_size_audit8.json",
        "rhat_distribution_audit5.json", "rhat_distribution_audit5b.json", "adaptive_size_power_audit5b.json",
        "b4_local_power_audit8.json", "e4_slope_audit15.json", "audit2_results_audit2.json", "b103_cv_audit10.json",
        "critical_values_audit10.csv", "b1_critical_audit14.json", "tables_audit13.json", "e_application_audit13.json",
        "bA_ma_audit12.json", "bB_attrib_audit12.json", "b0b_lag_audit15.json", "b0_iidasy_audit15.json",
        "b3_fixedb_audit15.json", "b1_boot_audit15.json")
DATA_EXTRA = {"crit_msb_mzt_audit14.csv": C.C14.TABLES}
S6_TABLES = (("size", 1), ("calib", 1), ("localpower", 1), ("dgp1", 2), ("ctpower", 2), ("dgp2", 2), ("dgp3", 2),
             ("misspec", 2), ("awb", 2), ("dgp5", 2), ("fp", 1))   # critB con theta = 0.02 ya esta en S5 (enmienda 5, 7b.5)
S6_CAPTION = {
    "size": "Size under the Gaussian random walk with Wilson intervals.",
    "calib": "Size with the limiting and the finite-sample critical values.",
    "localpower": "Local power, $n = 2000$.",
    "dgp1": "Power against AR(1), constant case, equalized size.",
    "ctpower": "Power against AR(1), trend case, equalized size.",
    "dgp2": "Power with a mean break, equalized size.",
    "dgp3": "Rejection rates with a variance break under the null.",
    "misspec": "Size with heavy tails and GARCH innovations.",
    "awb": "AWB calibration against the simulated calibration.",
    "dgp5": "The pre-registered two-channel experiment.",
    "fp": "Pre-registered application.",
}
RM_NOTE = "RM: the centred rolling-means statistic with $\\theta = 0.1$."
S6_SUBS = (("\\RMGLS{}", "$S_{0.02}$"),)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def f(x, d):
    if x is None:
        return "--"
    s = TB.fdec(x, d, "binary")
    return "$-$" + s[1:] if s.startswith("-") else s


def tabular(colspec, head_lines, rows, groups=None):
    L = ["\\begin{tabular}{%s}" % colspec, "\\toprule"] + head_lines + ["\\midrule"]
    last = None
    for i, r in enumerate(rows):
        g = groups[i] if groups else None
        if last is not None and g != last:
            L.append("\\addlinespace")
        last = g
        L.append(" & ".join(str(c) for c in r) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def header_of(tex):
    """Lineas de encabezado de un tabular exportado (entre \\toprule y \\midrule)."""
    a = tex.index("\\toprule") + len("\\toprule")
    b = tex.index("\\midrule")
    return [l for l in tex[a:b].strip().splitlines() if l.strip()]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def gen_header(src):
    return "% Generado por experiments/audit15_supplement.py desde " + src + " (no editar a mano)\n"


class Writer:
    def __init__(self):
        self.files = {}

    def text(self, rel, content, sources):
        p = os.path.join(SUPP, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        self.files[rel] = {"sources": list(sources)}

    def copy(self, rel, src_path, anonymize=True):
        p = os.path.join(SUPP, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if anonymize and src_path.lower().endswith(AN.TEXT_EXT):
            content = AN.anonymize_text(read(src_path), C.rel(src_path))
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
        else:
            shutil.copy2(src_path, p)
        self.files[rel] = {"sources": [C.rel(src_path)], "source_sha256": C.sha256_file(src_path)}


# ---------------------------------------------------------------------------
# S1-S9
# ---------------------------------------------------------------------------
def s1(W):
    eq = C.read_json("e_equalized_audit13.json")["cells"]
    TB.ROUNDING["mode"] = "binary"
    out = {}
    for label, prefix in (("dgp1", "dgp1"), ("ctpower", "ct_power")):
        keys = sorted(((eq[k]["n"], eq[k]["rho"]) for k in eq if k.startswith(prefix + "_rho")))
        rows = [(None, None, ["%.2f" % r, "%d" % n], None) for n, r in keys]
        cells, _ = TB.build_power(rows, eq, C13.PRIM, prefix)
        head = header_of(read(os.path.join(C.C14.TABLES_A13, "tab_%s_audit13.tex" % label)))
        body = [row[2] + c for row, c in zip(rows, cells)]
        W.text("tables/S1_tab_%s_full.tex" % label, gen_header("e_equalized_audit13.json") +
               tabular("rrcccccccc", head, body, [n for n, _ in keys]), ["e_equalized_audit13.json"])
        out[label] = len(body)
    return out


def s2(W):
    d5 = C.read_json("e_dgp5_audit13.json")["cells"]
    TB.ROUNDING["mode"] = "half_up"                      # convencion de tab:dgp5 (A13)
    keys = sorted(((v["rho"], v["r"]) for v in d5.values()))
    rows = [(None, None, ["%.2f" % rho, "%g" % r], None) for rho, r in keys]
    cells, _ = TB.build_dgp5(rows, d5)
    TB.ROUNDING["mode"] = "binary"
    head = header_of(read(os.path.join(C.C14.TABLES_A13, "tab_dgp5_audit13.tex")))
    W.text("tables/S2_tab_dgp5_full.tex", gen_header("e_dgp5_audit13.json") +
           tabular("rrccccc", head, [row[2] + c for row, c in zip(rows, cells)], [rho for rho, _ in keys]), ["e_dgp5_audit13.json"])
    return {"cells": len(rows)}


STD_LABEL = {"sigma_known": "$\\sigma$ known", "alpha1_hac": "HAC, pilot $\\alpha(1)$", "alpha2_hac": "HAC, pilot $\\alpha(2)$"}
P_SMALL = 10 ** -3


def pfmt(p):
    """p-valor: <0.001 por debajo de 0.001; tres decimales (binario) en el resto (enmienda 5, 7b.7)."""
    return "$<$0.001" if p < P_SMALL else TB.fdec(p, 3, "binary")


def label_std(key):
    return STD_LABEL.get(key, key.replace("_", "\\_"))


def label_config(key):
    """alpha1_hac_Ncal50000 -> 'HAC, pilot alpha(1), N_cal = 5 x 10^4'."""
    m = re.match(r"(.*)_Ncal(\d+)$", key)
    if not m:
        return label_std(key)
    n = int(m.group(2))
    e = len(str(n)) - 1
    mant = n // 10 ** e
    return "%s, $\\ncal = %s10^{%d}$" % (label_std(m.group(1)), ("%d\\times" % mant) if mant != 1 else "", e)


def label_scenario(key):
    """H0_n200 -> 'H_0, n = 200'; DGP3_r4_n1000 -> 'DGP 3, r = 4, n = 1000'; DGP1_rho095_n200 -> 'rho = 0.95, n = 200'."""
    parts = key.split("_")
    out = []
    for p in parts:
        if p == "H0":
            out.append("$H_0$")
        elif re.match(r"DGP\d$", p):
            out.append("DGP %s" % p[3:])
        elif p.startswith("rho"):
            out.append("$\\rho = %s.%s$" % (p[3], p[4:]))
        elif re.match(r"r\d", p):
            out.append("$r = %s$" % p[1:])
        elif re.match(r"n\d", p):
            out.append("$n = %s$" % p[1:])
        else:
            out.append(p.replace("_", "\\_"))
    if out and out[0].startswith("DGP 1"):
        out = out[1:]
    return ", ".join(out)


def s3(W):
    b2 = C.read_json("b2_size_audit8.json")["B2a"]
    rows = []
    for k in b2["gate"]["cells_evaluated"]:
        c = b2["cells"][k]
        rows.append([k.replace("_", "\\_"), f(c["rate_R0"]["rate"], 4), f(c["rate_R05"]["rate"], 4), f(c["delta_pp"], 2),
                     pfmt(c["mcnemar_p"])])
    W.text("tables/S3a_variance_channel.tex", gen_header("b2_size_audit8.json (B2a)") + tabular(
        "lcccc", ["Cell & One channel & Two channels ($R = 0.5$) & $\\Delta$ (pp) & McNemar $p$ \\\\"], rows),
           ["b2_size_audit8.json"])
    rh = C.read_json("rhat_distribution_audit5b.json")
    rows = [[label_std(m), label_scenario(sc)] + [f(v["r_hat"][q], 4) for q in ("mean", "median", "q05", "q95")]
            for m, scs in rh.items() for sc, v in scs.items()]
    W.text("tables/S3b_adaptive_weight.tex", gen_header("rhat_distribution_audit5b.json") + tabular(
        "llcccc", ["Standardization & Scenario & Mean & Median & $q_{0.05}$ & $q_{0.95}$ \\\\"], rows,
        [m for m in rh for _ in rh[m]]), ["rhat_distribution_audit5b.json"])
    ap = C.read_json("adaptive_size_power_audit5b.json")
    rows = []
    for cfg, cells in ap.items():
        for k, v in cells.items():
            if k.startswith("DGP1"):
                rows.append([label_config(cfg), label_scenario(k), f(v["adaptive"], 4), f(v["rebalanced"], 4),
                             f((v["adaptive"] - v["rebalanced"]) * C.PP, 2)])
    W.text("tables/S3c_rebalancing.tex", gen_header("adaptive_size_power_audit5b.json") + tabular(
        "llccc", ["Configuration & Cell & Adaptive & Rebalanced & Difference (pp) \\\\"], rows, [r[0] for r in rows]),
           ["adaptive_size_power_audit5b.json"])
    bc = C.read_json("t5_claims_audit11.json")["claims"]["3"]["by_case"]
    rows = [[T13.CASE.get("c" if case == "dm" else case, case), th, f(v["power_rmgls"], 4), f(v["power_rm"], 4), f(v["cost_pp"], 2),
             f(v["gap_rmgls_pp"], 2), f(v["gap_rm_pp"], 2)] for case, ths in bc.items() for th, v in ths.items()]
    W.text("tables/S3d_mean_anchor.tex", gen_header("t5_claims_audit11.json (b4_local_power_audit8.json)") + tabular(
        "lcccccc", ["Case & $\\theta$ & GLS anchor & Mean anchor & Cost (pp) & GLS gap (pp) & Mean gap (pp) \\\\"], rows,
        [r[0] for r in rows]), ["t5_claims_audit11.json", "b4_local_power_audit8.json"])
    return {"variance_cells": len(b2["gate"]["cells_evaluated"])}


def s4(W):
    e4 = C.read_json("e4_slope_audit15.json")["b"]
    rows = [[lab, f(r["slope_B_pre_script"], 4), f(r["R2_B_pre_script"], 4), f(r["slope_B_ceil_script"], 4), f(r["R2_B_ceil_script"], 4),
             f(r["slope_B_pre_lib"], 4), f(r["slope_g1s"], 4), f(r["slope_g2s"], 4)] for lab, r in e4.items()]
    W.text("tables/S4a_rates.tex", gen_header("e4_slope_audit15.json") + tabular(
        "lccccccc", ["Process & $B$ before ceiling & $R^2$ & $B$ & $R^2$ & $B$ before ceiling, library $\\hat\\rho$ & "
                     "$g_1$ std. & $g_2$ std. \\\\"], rows), ["e4_slope_audit15.json"])
    a2 = C.read_json("audit2_results_audit2.json")["task3"]["rho=0.5"]["by_n"]
    rows = [[n, f(v["sigma_hac_median"], 4), "%d" % int(v["bw_median"])] for n, v in a2.items()]
    W.text("tables/S4b_hac_median.tex", gen_header("audit2_results_audit2.json (task3)") + tabular(
        "rcc", ["$n$ & Median of $\\hat\\sigma^2_{\\mathrm{HAC}}$ & Median bandwidth \\\\"], rows), ["audit2_results_audit2.json"])
    pilot = C.read_json("b2_sources_audit14.json")["figures"]["iii"]["script_bandwidth_pilot"]
    return {"hac_median_pilot": pilot}


def s5(W):
    cv = C.read_json("b103_cv_audit10.json")
    thetas = cv["config"]["thetas"]
    alphas = cv["config"]["alphas"]
    tab = cv["table"]
    out = []
    for th in thetas:
        rows, groups = [], []
        for n in cv["config"]["n"]:
            row = ["%d" % n]
            for case in ("dm", "ct"):
                e = tab["%s|%g|%d" % (case, th, n)]
                row += [f(e["cv"][str(a)] if str(a) in e["cv"] else e["cv"]["%g" % a], 4) for a in alphas]
            rows.append(row)
        head = ["& \\multicolumn{%d}{c}{Constant} & \\multicolumn{%d}{c}{Trend}\\\\" % (len(alphas), len(alphas)),
                "\\cmidrule(lr){2-%d}\\cmidrule(lr){%d-%d}" % (1 + len(alphas), 2 + len(alphas), 1 + 2 * len(alphas)),
                "$n$ & " + " & ".join("$%g$" % a for _ in range(2) for a in alphas) + "\\\\"]
        name = "tables/S5_critical_theta_%s.tex" % ("%g" % th).replace(".", "p")
        W.text(name, gen_header("b103_cv_audit10.json") + tabular("r" + "c" * 2 * len(alphas), head, rows), ["b103_cv_audit10.json"])
        out.append(name)
    return {"theta_tables": out, "N_cal": cv["config"]["N_cal"], "max_se": max(e["max_se"] for e in tab.values())}


def s6(W):
    v = TB.V13(C13.MANUSCRIPT)
    t13 = C.read_json("tables_audit13.json")["tables"]
    out = {}
    for label, nkey in S6_TABLES:
        fname, tab = v.tabular(label)
        chunks, rows = TB.data_rows(tab, nkey)
        vals = [r["v13"] for r in t13[label]["rows"]]
        if len(vals) != len(rows):
            out[label] = {"rows_json": len(vals), "rows_v13": len(rows), "written": False}
            continue
        tex = TB.rebuild(chunks, rows, vals, ())
        for old, new in S6_SUBS:
            tex = tex.replace(old, new)
        tex, n_sci = re.subn(r"\$(\d+(?:\.\d+)?)\\times10\^\{(-?\d+)\}\$", lambda m: pfmt(float(m.group(1)) * 10 ** int(m.group(2))), tex)
        tex, n_norm = re.subn(r"(G [\d.]+), N(?=\s*&)", r"\1, normal", tex)
        W.text("tables/S6_tab_%s_theta0p02.tex" % label, gen_header("tables_audit13.json (valores con theta = 0.02, disposicion del v13)")
               + tex + "\n", ["tables_audit13.json"])
        marks = v13_marks(v, label)
        if marks:
            W.text("tables/S6_tab_%s_theta0p02_note.tex" % label, gen_header("texto de las marcas del v13 (tab:%s)" % label) +
                   " ".join(marks) + "\n", ["paper_latex_v13.zip"])
        out[label] = {"rows": len(rows), "written": True, "rounding": t13[label]["rounding"], "p_scientific_replaced": n_sci,
                      "normal_replaced": n_norm, "mark_notes": len(marks)}
    return out


def v13_marks(v, label):
    """Notas literales de las marcas (a, c, dagger) del tabular de tab:<label> en el v13 (enmienda 5, 7b.9)."""
    for fname, text in v.files.items():
        i = text.find("\\label{tab:%s}" % label)
        if i < 0:
            continue
        m_end = re.compile(r"\\end\{table\*?\}").search(text, i)
        end = m_end.start() if m_end else -1
        a = text.find("\\begin{tablenotes}", i)
        b = text.find("\\end{tablenotes}", a)
        if a < 0 or b < 0 or (end >= 0 and a > end):
            return []
        body = re.sub(r"\s+", " ", text[a:b])
        out = []
        m = re.search(r"\\item\[\$a\$\]\s*(.*?)(?=\\item|$)", body)
        if m:
            out.append("$^a$" + m.group(1).strip())
        m = re.search(r"(latency\$\^c\$ is [^.;]*)", body)
        if m:
            out.append(m.group(1)[0].upper() + m.group(1)[1:].strip() + ".")
        m = re.search(r"(\$\^\\dagger\$[^.]*\.)", body)
        if m:
            out.append(m.group(1).strip())
        return out
    return []


def s7(W):
    a = C.read_json("e_application_audit13.json")
    o, aw = a["oos_size"], a["oos_size_awb"]
    rows = [[D, f(o["by_D"][D]["rate"], 4), "[%s, %s]" % (f(o["by_D"][D]["wilson_lower"], 4), f(o["by_D"][D]["wilson_upper"], 4)),
             f(aw["by_D"][D]["rate"], 4), "[%s, %s]" % (f(aw["by_D"][D]["wilson_lower"], 4), f(aw["by_D"][D]["wilson_upper"], 4))]
            for D in o["by_D"]]
    W.text("tables/S7a_oos_size.tex", gen_header("e_application_audit13.json (oos_size, oos_size_awb)") + tabular(
        "rcccc", ["$D$ & Simulated & Wilson 95\\% & AWB & Wilson 95\\% \\\\"], rows), ["e_application_audit13.json"])
    rows = [[c["cell"].replace("_", "\\_").replace("|", ", "), f(c["primary"], 3), f(c["adf"], 3), f(c["pp"], 3), f(c["kpss"], 3),
             ", ".join(c["exceeds"]).upper()] for c in a["adverse_cells_primary"]]
    W.text("tables/S7b_adverse_cells.tex", gen_header("e_application_audit13.json (adverse_cells_primary)") + tabular(
        "lccccl", ["Control cell & \\RMGLS{} & ADF & PP & KPSS & Exceeds \\\\"], rows), ["e_application_audit13.json"])
    fp = a["fp_cells"]["final"]
    Ds = sorted({k.split("|")[1] for k in fp}, key=int)
    idx = sorted({(k.split("|")[0], k.split("|")[2]) for k in fp})
    rows = [[i.replace("_", "\\_"), p.replace("_", "\\_")] + [f(fp["%s|%s|%s" % (i, D, p)], 3) for D in Ds] for i, p in idx]
    W.text("tables/S7c_fp_by_cell.tex", gen_header("e_application_audit13.json (fp_cells.final)") + tabular(
        "ll" + "c" * len(Ds), ["Index & Control period & " + " & ".join("$D = %s$" % D for D in Ds) + " \\\\"], rows,
        [i for i, _ in idx]), ["e_application_audit13.json"])
    lat = a["latency_cells"]["final"]
    ev = sorted({(k.split("|")[0], k.split("|")[2]) for k in lat})
    rows = [[i.replace("_", "\\_"), e.replace("_", "\\_")] + [("%d" % lat["%s|%s|%s" % (i, D, e)]) if lat.get("%s|%s|%s" % (i, D, e)) is not None
                                                            else "--" for D in Ds] for i, e in ev]
    W.text("tables/S7d_latency_by_event.tex", gen_header("e_application_audit13.json (latency_cells.final)") + tabular(
        "ll" + "c" * len(Ds), ["Index & Event & " + " & ".join("$D = %s$" % D for D in Ds) + " \\\\"], rows, [i for i, _ in ev]),
           ["e_application_audit13.json"])
    return {"control_cells": len(fp), "event_cells": len(lat), "adverse": len(a["adverse_cells_primary"])}


def s8(W):
    files = sorted(glob.glob(os.path.join(HERE, "protocol*.md")) + glob.glob(os.path.join(HERE, "prediccion*.md")))
    for p in files:
        W.copy("protocols/" + os.path.basename(p), p)
    return {"documents": len(files)}


def diag_row(d, keys):
    return ["%s [%s, %s]" % (f(d[k]["median"], 2), f(d[k]["q25"], 2), f(d[k]["q75"], 2)) for k in keys]


def s9(W):
    bA = C.read_json("bA_ma_audit12.json")
    order = [tuple(e) for e in bA["config"]["errors"]]
    tags = [T13_tag(e) for e in order]
    keys = ("s2_over_omega2", "s2ar_over_omega2", "s2ar_pq_over_omega2")

    def rows_for(block, with_rho):
        items = sorted(block.items(), key=lambda kv: (tags.index(kv[1]["err_tag"]), kv[1]["n"], kv[1]["case"], kv[1].get("rho") or 0))
        rows, groups = [], []
        for k, c in items:
            e = order[tags.index(c["err_tag"])]
            d = c["diagnostics"]
            fac = c.get("bartlett_factor_at_median_B", {}).get("factor")
            lead = [T13.err_tex(e), "%d" % c["n"], T13.CASE[c["case"]]] + ([f(c["rho"], 2)] if with_rho else [])
            rows.append(lead + diag_row(d, keys) + ["%d" % d["B"]["median"], "%d" % d["k"]["median"]] +
                        ([f(fac, 2)] if fac is not None else []))
            groups.append(c["err_tag"])
        return rows, groups
    diag = "$\\hat\\sigma^2_{\\mathrm{HAC}}/\\omega^2$ & $s^2_{\\mathrm{AR}}/\\omega^2$ (GLS) & $s^2_{\\mathrm{AR}}/\\omega^2$ (OLS) & $B$ & $k$"
    rows, groups = rows_for(bA["size"], False)
    W.text("tables/S9a_diagnostics_null.tex", gen_header("bA_ma_audit12.json (size.<celda>.diagnostics)") + tabular(
        "lrl" + "c" * 6, ["Errors & $n$ & Case & " + diag + " & Bartlett factor \\\\"], rows, groups), ["bA_ma_audit12.json"])
    rows, groups = rows_for(bA["power"], True)
    W.text("tables/S9b_diagnostics_alt.tex", gen_header("bA_ma_audit12.json (power.<celda>.diagnostics)") + tabular(
        "lrlc" + "c" * 5, ["Errors & $n$ & Case & $\\rho$ & " + diag + " \\\\"], rows, groups), ["bA_ma_audit12.json"])
    bB = C.read_json("bB_attrib_audit12.json")["diagnostics_n200"]
    rows = [[f(v["rho"], 2), T13.CASE[v["case"]], f(v["k_gls"], 1), f(v["k_ols"], 1), f(v["s2ar_gls"], 3), f(v["s2ar_ols"], 3),
             f(v["s2_hac"], 3)] for v in bB.values()]
    W.text("tables/S9c_attribution_diagnostics.tex", gen_header("bB_attrib_audit12.json (diagnostics_n200)") + tabular(
        "rlccccc", ["$\\rho$ & Case & $k$ (GLS) & $k$ (OLS) & $s^2_{\\mathrm{AR}}$ (GLS) & $s^2_{\\mathrm{AR}}$ (OLS) & "
                    "$\\hat\\sigma^2_{\\mathrm{HAC}}$ \\\\"], rows), ["bB_attrib_audit12.json"])
    return {"null_cells": len(bA["size"]), "alt_cells": len(bA["power"]), "attrib_cells": len(bB)}


def T13_tag(err):
    kind, v = err
    return "%s_%s" % (kind, ("%g" % v).replace("-", "m").replace(".", "p"))


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
SECTIONS = [
    ("S1", "Omitted rows of the power tables", [("S1_tab_dgp1_full", "Power against AR(1), constant case, equalized size: all cells."),
                                                ("S1_tab_ctpower_full", "Power against AR(1), trend case, equalized size: all cells.")]),
    ("S2", "The pre-registered two-channel experiment in full", [("S2_tab_dgp5_full", "All cells of the variance-break experiment.")]),
    ("S3", "Negative results", [("S3a_variance_channel", "The variance channel: size with one and with two channels."),
                                ("S3b_adaptive_weight", "Distribution of the signal-proportional weight under the null."),
                                ("S3c_rebalancing", "Power of the adaptive and rebalanced combinations."),
                                ("S3d_mean_anchor", "Local power with the GLS anchor and with the sample mean.")]),
    ("S4", "Rate of the HAC estimator under stationary alternatives",
     [("S4a_rates", "Log--log slopes in $n$ (means over replications)."),
      ("S4b_hac_median", "Median of the HAC estimator and of the bandwidth, AR$(0.5)$. These medians were produced with the "
                         "previous bandwidth pilot $\\hat a = 4\\hat\\rho^2/(1-\\hat\\rho)^4$, not the one of the main text.")]),
    ("S5", "Critical values", []),
    ("S6", "Tables with the smoothed statistic $\\theta = 0.02$", []),
    ("S7", "Application: details", [("S7a_oos_size", "Out-of-sample size by window length."),
                                    ("S7b_adverse_cells", "Control cells flagged by the pre-registered adverse-reporting rule."),
                                    ("S7c_fp_by_cell", "False-positive rate by control cell."),
                                    ("S7d_latency_by_event", "Detection latency (trading days) by event cell; -- = not detected.")]),
    ("S8", "Protocols, amendments and predictions", []),
    ("S9", "Scale diagnostics", [("S9a_diagnostics_null", "Diagnostics under each null: median [q25, q75]."),
                                 ("S9b_diagnostics_alt", "The same diagnostics under the alternatives."),
                                 ("S9c_attribution_diagnostics", "Diagnostics of the attribution experiment at $n = 200$ (medians).")]),
    ("S10", "Additional tables", [("tab_serial_asy_audit15", "Size with simulated (iid) and published asymptotic critical values."),
                                  ("tab_lag_audit15", "Size by the lag chosen by the GLS MAIC."),
                                  ("tab_fixedb_size_audit15", "Size of \\RMGLS{} with a fixed Bartlett bandwidth.")]),
]


def doc(res):
    L = ["\\documentclass[11pt]{article}", "\\usepackage[margin=2cm]{geometry}", "\\usepackage{booktabs,graphicx,amsmath,amssymb,placeins,adjustbox}",
         "\\newcommand{\\RMGLS}{MSB-B}", "\\newcommand{\\ncal}{N_{\\mathrm{cal}}}",
         "\\newcommand{\\cref}[1]{the null model of the main text}", "\\newcommand{\\citet}[1]{Ng and Perron (2001)}",
         "\\title{Supplementary material}", "\\date{}", "\\begin{document}", "\\maketitle",
         "Every table below is generated from the machine-readable files in \\texttt{data/}; \\texttt{README.md} maps each table "
         "to its source.", ""]
    for sid, title, tabs in SECTIONS:
        L.append("\\FloatBarrier")
        L.append("\\section*{%s. %s}" % (sid, title))
        if sid == "S5":
            for name in res["S5"]["theta_tables"]:
                base = os.path.splitext(os.path.basename(name))[0]
                th = base.split("_theta_")[1].replace("p", ".")
                tabs = tabs + [(base, "Lower-tail critical values of $S_\\theta$, $\\theta = %s$." % th)]
            tabs = tabs + [("tab_critMSB_audit14", "Critical values of MSB-GLS and MZ$_t$-GLS.")]
        if sid == "S6":
            L.append("Bold entries follow the rule stated in the note of the corresponding table of the main text. " + RM_NOTE)
            tabs = [("S6_tab_%s_theta0p02" % lab, S6_CAPTION[lab][:-1] + ", computed with $\\theta = 0.02$.")
                    for lab, v in res["S6"].items() if v.get("written")]
        if sid == "S1":
            L.append("Columns as in the corresponding tables of the main text; $p$: exact McNemar test of \\RMGLS{} against DF-GLS. "
                     + RM_NOTE)
        if sid == "S8":
            L.append("The protocols, amendments and predictions are in \\texttt{protocols/}, in the order in which they were committed.")
        for base, cap in tabs:
            L += ["\\begin{table}[htbp]", "\\centering", "\\caption{%s}" % cap, "\\small", "\\begin{adjustbox}{max width=\\textwidth}",
                  "\\input{tables/%s}" % base, "\\end{adjustbox}"]
            note = base.replace("_audit1", "_note_audit1") if "_audit1" in base else base + "_note"
            if os.path.exists(os.path.join(SUPP, "tables", note + ".tex")):
                L += ["\\par\\medskip\\begin{minipage}{\\textwidth}\\footnotesize", "\\input{tables/%s}" % note, "\\end{minipage}"]
            L += ["\\end{table}", "\\clearpage" if base.startswith(("S7c", "S7d", "S9a", "S9b")) else ""]
    L += ["\\end{document}", ""]
    return "\n".join(L)


def readme(W):
    L = ["# Supplementary material", "", "Generated by `experiments/audit15_supplement.py` from the result files in `data/`. "
         "Do not edit by hand.", "", "| Section | Table | Source |", "|---|---|---|"]
    for rel, v in sorted(W.files.items()):
        if rel.startswith("tables/"):
            sec = os.path.basename(rel).split("_")[0] if os.path.basename(rel).startswith("S") else "S10/S5"
            L.append("| %s | `%s` | %s |" % (sec, rel, ", ".join("`%s`" % s for s in v["sources"])))
    L += ["", "`protocols/`: protocols, amendments and predictions. `MANIFEST.sha256`: sha256 of every file.", ""]
    return "\n".join(L)


def compile_check():
    tmp = tempfile.mkdtemp(prefix="a15_supp_")
    dst = os.path.join(tmp, "supplementary")
    shutil.copytree(SUPP, dst)
    if not os.path.exists(PDFLATEX):
        return {"compiled": False, "reason": "pdflatex no encontrado"}
    for _ in range(2):
        r = subprocess.run([PDFLATEX, "-interaction=nonstopmode", "supplement.tex"], cwd=dst, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    log = read(os.path.join(dst, "supplement.log")) if os.path.exists(os.path.join(dst, "supplement.log")) else ""
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    res = {"compiled": os.path.exists(os.path.join(dst, "supplement.pdf")), "errors": len(re.findall(r"^! ", log, flags=re.M)),
           "undefined_references": len(re.findall(r"undefined", log, flags=re.I)),
           "overfull": len(re.findall(r"Overfull \\hbox", log)), "pages": int(pages.group(1)) if pages else None,
           "first_errors": re.findall(r"^! .*$", log, flags=re.M)[:5]}
    shutil.rmtree(tmp, ignore_errors=True)
    return res


def scan():
    files = [os.path.join(dp, fn) for dp, _, fs in os.walk(SUPP) for fn in fs]
    inv, pdfs = AN.inventory(files, SUPP)
    tot = AN.totals(inv)
    return {"files": len(files), "totals": tot, "non_hash_hits": sum(v["hits"] for k, v in tot.items() if k != "hash_de_commit"),
            "hits": {f: {c: x for c, x in h.items() if c != "hash_de_commit"} for f, h in inv.items()
                     if any(c != "hash_de_commit" for c in h)}}


def ncols(line):
    """Columnas de una linea de tabular: celdas separadas por & (sin \\&), con \\multicolumn{k}."""
    cells = re.split(r"(?<!\\)&", line.split("\\\\")[0])
    return sum(int(m.group(1)) if (m := re.match(r"\s*\\multicolumn\{(\d+)\}", c)) else 1 for c in cells)


def column_diagnosis(rel):
    """Enmienda 5, 7b.2: columnas del colspec, de la cabecera y de cada fila de datos."""
    tex = read(os.path.join(SUPP, rel))
    spec = re.search(r"\\begin\{tabular\}\{([^}]*)\}", tex).group(1)
    ncs = len(re.findall(r"[lcrpmbX]", re.sub(r"@\{[^}]*\}|\{[^}]*\}", "", spec)))
    a, b = tex.index("\\toprule"), tex.index("\\midrule")
    head = [ncols(l) for l in tex[a + len("\\toprule"):b].splitlines() if "\\\\" in l]
    body = tex[b + len("\\midrule"):tex.index("\\bottomrule")]
    rows = [ncols(l) for l in body.splitlines() if "\\\\" in l]
    return {"file": rel, "colspec": spec, "colspec_columns": ncs, "header_columns": head,
            "row_columns": sorted(set(rows)), "rows": len(rows),
            "consistent": all(h == ncs for h in head) and set(rows) == {ncs}}


def main():
    global SUPP
    args = sys.argv[1:]
    test_mode = "--out" in args
    if test_mode:
        SUPP = os.path.abspath(args[args.index("--out") + 1])
        if os.path.normcase(SUPP) == os.path.normcase(os.path.join(C.REPO, "supplementary")):
            raise SystemExit("--out no puede ser supplementary/ (enmienda 5, 7b.1)")
    old_commit = C.git("log", "-1", "--format=%H", "--", OLD_MARKER).strip() or None
    if os.path.exists(SUPP):
        shutil.rmtree(SUPP)
    W = Writer()
    res = {"S1": s1(W), "S2": s2(W), "S3": s3(W), "S4": s4(W), "S5": s5(W), "S6": s6(W), "S7": s7(W), "S8": s8(W), "S9": s9(W)}
    for name, folder in EXPORTS.items():
        W.copy("tables/" + name, os.path.join(folder, name))
    for name in DATA:
        W.copy("data/" + name, os.path.join(C.RESULTS, name))
    for name, folder in DATA_EXTRA.items():
        W.copy("data/" + name, os.path.join(folder, name))
    W.text("supplement.tex", doc(res), ["generado"])
    W.text("README.md", readme(W), ["generado"])
    man = []
    for dp, _, fs in os.walk(SUPP):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            man.append("%s  %s" % (C.sha256_file(p), os.path.relpath(p, SUPP).replace("\\", "/")))
    W.text("MANIFEST.sha256", "\n".join(sorted(man, key=lambda s: s.split("  ", 1)[1])) + "\n", ["generado"])
    sc = scan()
    comp = compile_check()
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 4, lecturas 7.1-7.5",
           "old_package": {"marker": OLD_MARKER, "last_commit_with_it": old_commit, "removed_from_worktree": True},
           "sections": res, "files": {k: v for k, v in sorted(W.files.items())}, "n_files": len(W.files),
           "anonymization_scan": sc, "compile": comp,
           "pending": [k for k, v in res["S6"].items() if not v.get("written")]}
    if test_mode:
        out["reading"] = "enmienda 5, lecturas 7b.1-7b.9 (generacion de control en --out; supplementary/ no se toca)"
        out["out_dir"] = "<temporal>"
        out["old_package"] = None
        out["column_diagnosis"] = [column_diagnosis(r) for r in ("tables/S2_tab_dgp5_full.tex", "tables/S6_tab_dgp5_theta0p02.tex")]
        fp = read(os.path.join(SUPP, "tables", "S6_tab_fp_theta0p02.tex"))
        fpn = os.path.join(SUPP, "tables", "S6_tab_fp_theta0p02_note.tex")
        out["kpss_mark"] = {"in_tabular": "KPSS$^a$" in fp or "KPSS$^{a}$" in fp,
                            "note_file": os.path.exists(fpn), "note_has_a": os.path.exists(fpn) and "$^a$" in read(fpn),
                            "note_in_supplement_tex": "S6_tab_fp_theta0p02_note" in read(os.path.join(SUPP, "supplement.tex"))}
        out["critB_in_S6"] = "critB" in res["S6"]
        C.write_result(OUT_FIX, out, __file__)
        print(json.dumps({"column_diagnosis": out["column_diagnosis"], "kpss_mark": out["kpss_mark"]}, indent=1))
    else:
        C.write_result(OUT, out, __file__)
    print("archivos:", len(W.files), "| aciertos no-hash:", sc["non_hash_hits"], "| compilacion:", comp)
    print({k: v for k, v in res.items() if k != "S6"}, "S6:", {k: v.get("written") for k, v in res["S6"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
