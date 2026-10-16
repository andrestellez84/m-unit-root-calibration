"""
Auditoria A16 - B15.7c (enmienda 6, lectura E6.6): reconstruccion unica de supplementary/ segun SUPPLEMENT_MAP_v17.md.

Secciones S1-S10 numeradas; tablas y figuras Sk.j con el contador reiniciado por seccion. Contenido:
- tabulares desde JSON (generadores de audit15_supplement, sin modificarlos) y tabulares de A13/A14/A15 ya exportados
  (se comprueba que son identicos a los del zip del v16 cuando alli existen);
- textos del v16 que el mapa manda al suplemento, transcritos literalmente desde paper_latex_v16.zip, con las
  referencias cruzadas reescritas: etiqueta del suplemento -> \\cref interno; etiqueta del cuerpo del v17 -> "Table N of
  the main text" (N de la compilacion de control del v17); otra -> sustitucion explicita registrada;
- texto nuevo de S2 (SB/SWB y Paso 0): solo hechos de code_check_audit16.json y cifras de b1_paso0_v2_audit15.json;
- figuras del zip del v16; bibliografia: union de references.bib del v16 y del v17 (natbib, plainnat).
Anonimizado con los patrones de B15.5; compilacion de control (pdflatex, bibtex, pdflatex x2) en un directorio temporal.
Con --out <dir> genera alli (prueba); sin --out, reconstruye supplementary/.
Salida: experiments/results/supplement_v17_audit16.json (o supplement_v17_trial_audit16.json con --out).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C                                         # noqa: E402
import audit15_supplement as A15S                                  # noqa: E402

OUT = os.path.join(C.RESULTS, "supplement_v17_audit16.json")
OUT_TRIAL = os.path.join(C.RESULTS, "supplement_v17_trial_audit16.json")
SUPP_REAL = os.path.join(C.REPO, "supplementary")
PDFLATEX = A15S.PDFLATEX
BIBTEX = os.path.join(os.path.dirname(PDFLATEX), "bibtex.exe")
T13 = os.path.join(C.RESULTS, "tables_audit13")
T14 = os.path.join(C.RESULTS, "tables_audit14")
T15 = os.path.join(C.RESULTS, "tables_audit15")
FIGS = ("fig_local_power_audit13q", "fig_power_equalized_audit13q", "fig_theta_ladder_audit13q", "fig_dgp3_audit13q",
        "fig_size_shift_audit13q")
A13_TABLES = ("tab_size_audit13", "tab_serial_audit13", "tab_serialpower_audit13", "tab_initial_audit13", "tab_dgp2_audit13",
              "tab_dgp3_audit13", "tab_awb_audit13", "tab_misspec_audit13", "tab_fp_audit13")
# Renombrado de los tabulares de audit15_supplement a la seccion nueva (enmienda 6, E6.6.2)
RENAME = (("S1_tab_", "s1_tab_"), ("S2_tab_dgp5_full", "s6_tab_dgp5_full"), ("S3", "s6_neg_"), ("S4", "s7_hac_"),
          ("S5_critical", "s8_critical"), ("S6_tab_", "s5_tab_"), ("S7", "s9_app_"), ("S9", "s2_diag_"))
MAP_S2 = ("tab:serial", "tab:serialasy", "tab:lag", "tab:boot", "tab:fixedbsize", "tab:serialpower", "tab:diagnull", "tab:diagalt",
          "tab:diagattrib")
SB_SWB_SENTENCE = ("The sieve bootstrap (SB) and the sieve wild bootstrap (SWB) calibrations of MZ$_t$-GLS were not evaluated under "
                   "variance breaks.")
RM_NOTE = A15S.RM_NOTE


# ---------------------------------------------------------------------------
# Bloques del v16 (archivo, inicio, fin exclusivo o None = fin de archivo, incluir el fin)
# ---------------------------------------------------------------------------
BLOCKS = {
    "S1_size": ("sec5_montecarlo.tex", r"\\subsection\{Size\}", r"\\subsection\{What calibration buys\}", False),
    "S1_power": ("sec5_montecarlo.tex", r"\\subsection\{Power in finite samples at equalized size\}",
                 r"\\subsection\{Where the finite-sample advantage", False),
    "S1_fig_lp": ("sec5_montecarlo.tex", r"\\begin\{figure\}\[t\]\s*\\centering\s*\\includegraphics\[width=\\textwidth\]\{fig_local_power",
                  r"\\end\{figure\}", True),
    "S2_serialpower": ("appC_tables.tex", r"\\begin\{table\}", r"\\end\{table\}", True),
    "S3_initial": ("sec5_montecarlo.tex", r"\\subsection\{The initial condition\}", r"\\subsection\{Mean breaks\}", False),
    "S4_breaks": ("sec5_montecarlo.tex", r"\\subsection\{Mean breaks\}", r"\\subsection\{A pre-registered test of a two-channel extension\}",
                  False),
    "S5_def": ("sec2_statistic.tex", r"For a window fraction", r"The statistic of this paper is the member with no window", False),
    "S5_theta": ("sec4_implementation.tex", r"\\subsection\{The smoothing window\}", None, False),
    "S5_fig": ("sec5_montecarlo.tex", r"\\begin\{figure\}\[t\]\s*\\centering\s*\\includegraphics\[width=\\textwidth\]\{fig_theta_ladder",
               r"\\end\{figure\}", True),
    "S6_twochannel": ("sec5_montecarlo.tex", r"\\subsection\{A pre-registered test of a two-channel extension\}", None, False),
    "S7_trend": ("sec3_theory.tex", r"And in the trend case the same argument requires", r"of \\cref\{sec:power\}\.", True),
    "S9_application": ("sec6_application.tex", r"(?<=\\label\{sec:application\})", None, False),
}
# Sustituciones editoriales declaradas sobre los textos transcritos (se registran todas)
EDITS = (
    ("S1_power", r"\s*Rows in which every procedure exceeds \$0\.99\$\s+are omitted; they are in the\s+supplement\.", ""),
    ("S1_power", r"\s*Rows in which every procedure exceeds \$0\.99\$\s+are omitted\.", ""),
    ("S7_trend", r"^And in the trend case", "In the trend case"),
    ("S3_initial", r"^\\subsection\{The initial condition\}\\label\{sec:initial\}\s*", ""),     # repite el titulo de la seccion S3
    # tab:dgp5 pasa completo (S6.1), sin marcas: la nota del v16 remitia al suplemento y a una marca que ya no hay
    ("S6_twochannel", r"\$\^\\dagger\$Registered interior\.\s*", ""),
    ("S6_twochannel", r"\s*Rows with \$\\rho = 0\.90\$ and the weak-break\s+extension \$r = 1\.1\$ are in the supplement\.", ""),
    ("S6_twochannel", r"The supplement reports these experiments in full\.",
     r"\\Cref{tab:negvariance,tab:negweight,tab:negrebal,tab:neganchor} report these experiments in full."),
)
SEC_LABELS_DROPPED = {"sec:initial": "S3"}
INPUT_SWAP = {"tab_dgp1_audit13": "s1_tab_dgp1_full", "tab_ctpower_audit13": "s1_tab_ctpower_full", "tab_dgp5_audit13": "s6_tab_dgp5_full"}


def extract(v16, key):
    fname, start, end, incl = BLOCKS[key]
    text = v16.files[fname]
    m = re.search(start, text)
    if m is None:
        raise LookupError("%s: inicio %s" % (key, start))
    a = m.start() if key != "S9_application" else m.end()
    if end is None:
        b = len(text)
    else:
        e = re.compile(end).search(text, m.end() if key != "S2_serial_table" else a)
        if e is None:
            raise LookupError("%s: fin %s" % (key, end))
        b = e.end() if incl else e.start()
    body = text[a:b]
    if key == "S2_serial_table":
        s = body.rfind("\\begin{table}")
        body = body[s:] if "\\label{tab:serial}" in body[s:] else body
    return body.strip("\n") + "\n", {"file": fname, "chars": [a, b], "line_from": text[:a].count("\n") + 1, "line_to": text[:b].count("\n") + 1}


def serial_float(v16):
    text = v16.files["sec5_montecarlo.tex"]
    i = text.index("\\label{tab:serial}")
    a = text.rfind("\\begin{table}", 0, i)
    b = text.index("\\end{table}", i) + len("\\end{table}")
    return text[a:b] + "\n", {"file": "sec5_montecarlo.tex", "chars": [a, b], "line_from": text[:a].count("\n") + 1,
                              "line_to": text[:b].count("\n") + 1}


# ---------------------------------------------------------------------------
# Referencias cruzadas
# ---------------------------------------------------------------------------
TYPE_NAME = {"table": "Table", "figure": "Figure", "section": "Section", "subsection": "Section", "equation": "equation",
             "proposition": "Proposition", "remark": "Remark", "theorem": "Theorem", "definition": "Definition", "appendix": "Appendix"}


def body_labels(tmp):
    """Compila el v17 en tmp y devuelve {etiqueta: (tipo, numero)} desde main.aux."""
    v17 = C.v17()
    d = os.path.join(tmp, "v17")
    os.makedirs(d, exist_ok=True)
    import zipfile
    with zipfile.ZipFile(C.ZIP_V17) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            rel = n.split("/", 1)[1] if "/" in n else n
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(z.read(n))
    for _ in range(2):
        subprocess.run([PDFLATEX, "-interaction=nonstopmode", "main.tex"], cwd=d, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    aux = open(os.path.join(d, "main.aux"), encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}@]+)\}\{\{([^}]*)\}\{[^}]*\}\{(?:[^{}]|\{[^{}]*\})*\}\{([a-z]+)\.", aux):
        out[m.group(1)] = (m.group(3), m.group(2))
    log = open(os.path.join(d, "main.log"), encoding="utf-8", errors="replace").read()
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    return out, {"compiled": pages is not None, "pages": int(pages.group(1)) if pages else None, "v17_sha256": v17.sha256}


def render_body(label, body, cap):
    typ, num = body[label]
    name = TYPE_NAME.get(typ, typ.capitalize())
    if typ == "equation":
        s = "equation~(%s) of the main text" % num
    else:
        s = "%s~%s of the main text" % (name, num)
    return s[0].upper() + s[1:] if cap else s


def resolve_refs(tex, sup_labels, sec_map, body, extra, log):
    def repl(m):
        cmd, labels = m.group(1), [x.strip() for x in m.group(2).split(",")]
        cap = cmd == "Cref"
        internal = [l for l in labels if l in sup_labels]
        parts = []
        if internal:
            parts.append("\\%s{%s}" % ("Cref" if cap else "cref", ",".join(internal)) if cmd in ("cref", "Cref")
                         else "\\ref{%s}" % ",".join(internal))
        for l in labels:
            if l in internal:
                continue
            if l in sec_map:
                parts.append("Section~%s" % sec_map[l])
                how = "suplemento (seccion %s)" % sec_map[l]
            elif l in body:
                parts.append(render_body(l, body, cap and not parts))
                how = "cuerpo del v17 (%s %s)" % body[l]
            elif l in extra:
                parts.append(extra[l])
                how = "sustitucion explicita"
            else:
                parts.append("[%s]" % l)
                how = "SIN RESOLVER"
            log.append({"label": l, "cmd": cmd, "resolved_as": parts[-1], "how": how})
        for l in internal:
            log.append({"label": l, "cmd": cmd, "resolved_as": "\\%s interno" % cmd, "how": "suplemento (etiqueta)"})
        if cmd == "ref" and not internal:
            return parts[0] if len(parts) == 1 else " and ".join(parts)
        return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return re.sub(r"\\(cref|Cref|ref)\{([^}]*)\}", repl, tex)


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
PREFER_V17 = ("StatZero",)          # el estadistico sin ventana se escribe como en el cuerpo del v17 (S)


def macro_defs(src):
    out = {}
    for m in re.finditer(r"^\\(?:newcommand|renewcommand|DeclareMathOperator)\{?\\([A-Za-z]+)\}?.*$", src, flags=re.M):
        if m.group(1) not in ("supp", "supptab", "bibfont") and "@" not in m.group(0) and m.group(1) not in out:
            out[m.group(1)] = m.group(0)
    return out


def macros(v16, v17):
    """Union de macros; en conflicto gana la del v16 (el texto transcrito es del v16), salvo PREFER_V17. Devuelve lineas y conflictos."""
    d16, d17 = macro_defs(v16.files["main.tex"]), macro_defs(v17.files["main.tex"])
    conflicts = {k: {"v16": d16[k], "v17": d17[k], "used": "v17" if k in PREFER_V17 else "v16"} for k in d16 if k in d17 and d16[k] != d17[k]}
    names = list(d17) + [k for k in d16 if k not in d17]
    lines = [(d17[k] if k in PREFER_V17 or k not in d16 else d16[k]) for k in names]
    return lines, conflicts


def old_captions():
    return {b: cap for _, _, tabs in A15S.SECTIONS for b, cap in tabs}


def table_float(base, caption, label, note=None, note_file=None, resize=True):
    L = ["\\begin{table}[htbp]", "\\centering", "\\caption{%s}" % caption, "\\label{%s}" % label, "\\small"]
    L += ["\\begin{adjustbox}{max width=\\textwidth}", "\\input{tables/%s}" % base, "\\end{adjustbox}"] if resize else ["\\input{tables/%s}" % base]
    if note_file:
        L += ["\\par\\medskip\\begin{minipage}{\\textwidth}\\footnotesize", "\\input{tables/%s}" % note_file, "\\end{minipage}"]
    elif note:
        L += ["\\par\\medskip\\begin{minipage}{\\textwidth}\\footnotesize %s\\end{minipage}" % note]
    L += ["\\end{table}", ""]
    return "\n".join(L)


def swap_inputs(tex):
    for old, new in INPUT_SWAP.items():
        tex = tex.replace("\\input{tables/%s}" % old, "\\input{tables/%s}" % new)
    return tex


def subsection_star(tex, sid, sec_map):
    def repl(m):
        if m.group(2):
            sec_map[m.group(2)] = sid
        return "\\subsection*{%s}" % m.group(1)
    return re.sub(r"\\subsection\{([^}]*)\}(?:\\label\{([^}]*)\})?", repl, tex)


def sci(x):
    """x en notacion cientifica LaTeX con una cifra decimal: 1.7\\times10^{-14}."""
    m, e = ("%.1e" % x).split("e")
    return "%s\\times10^{%d}" % (m, int(e))


def paso0_text():
    p = C.read_json("b1_paso0_v2_audit15.json")
    cfg, cr, sp = p["config"], p["criteria"], p["size_paired"]

    def f(x, d):
        return A15S.TB.fdec(x, d, "binary")
    return ("The replication was checked against the package before any bootstrap result was computed. On %d series of length $n = %d$ "
            "with $B = %d$ bootstrap replications, the replicated statistic matched the package to a largest absolute difference of "
            "$%s$ and the selected lag in every series (SB and SWB). The mean signed difference between the replicated and the package "
            "$p$-values was $%s$ (standard error $%s$) for the SB and $%s$ (standard error $%s$) for the SWB, and the mean absolute "
            "difference, $%s$ and $%s$, was within the bound implied by two independent bootstrap draws ($%s$ and $%s$). On %d paired "
            "paths per case, the rejection rates of the replication and of the package were $%s$ and $%s$ (SB) and $%s$ and $%s$ (SWB) "
            "in the constant case, and $%s$ and $%s$ (SB) and $%s$ and $%s$ (SWB) in the trend case." % (
                cfg["series"], cfg["n"], cfg["B"], sci(max(cr["SB"]["a_max_abs_stat"], cr["SWB"]["a_max_abs_stat"])),
                f(cr["SB"]["b_mean_signed"], 4), f(cr["SB"]["b_se"], 4), f(cr["SWB"]["b_mean_signed"], 4), f(cr["SWB"]["b_se"], 4),
                f(cr["SB"]["c_mean_abs"], 4), f(cr["SWB"]["c_mean_abs"], 4), f(cr["SB"]["c_bound"], 4), f(cr["SWB"]["c_bound"], 4),
                cfg["size_paths_per_case"], f(sp["c"]["SB"]["size_py"], 4), f(sp["c"]["SB"]["size_bootur"], 4), f(sp["c"]["SWB"]["size_py"], 4),
                f(sp["c"]["SWB"]["size_bootur"], 4), f(sp["ct"]["SB"]["size_py"], 4), f(sp["ct"]["SB"]["size_bootur"], 4),
                f(sp["ct"]["SWB"]["size_py"], 4), f(sp["ct"]["SWB"]["size_bootur"], 4)))


SB_SWB_TEXT = (
    "Both calibrations follow bootUR~1.0.5 \\citep{smeekes2023bootur}. The augmented Dickey--Fuller regression of the "
    "OLS-detrended series is estimated without restriction, with the lag chosen by the modified Akaike criterion on the rescaled "
    "series of \\citet{perron2007simple}; its residuals are kept as they are, without trimming the first observations and without "
    "centring. The null hypothesis is imposed when the bootstrap series is generated: the coefficient on the lagged level is "
    "dropped, the bootstrap innovations are filtered through the estimated autoregression in first differences, started at zero, "
    "and the result is cumulated. The SB resamples the residuals independently and with replacement; as in the package, the draws "
    "are taken from all but the last $l - 1$ residuals, with $l$ the default block length. The SWB multiplies each residual by an "
    "independent standard Gaussian weight. On every bootstrap series we recompute MZ$_t$-GLS with its own lag selected by the "
    "modified Akaike criterion on GLS-detrended data, and the $p$-value is $(1 + \\#\\{T^{*(r)} \\leq T\\})/(R + 1)$, where the "
    "package uses $\\#\\{t^* < t\\}/B$.")


def t3_text():
    t = open(os.path.join(HERE, "protocol_audit15_amend1.md"), encoding="utf-8").read()
    m = re.search(r"Texto del parche T3[^«]*«(.*?)»", t, flags=re.S)
    return re.sub(r"\s*\n\s*", " ", m.group(1)).strip()


def build(v16, v17, body, W, renamed):
    caps = {renamed.get(b + ".tex", b + ".tex")[:-4]: c for b, c in old_captions().items()}
    sec_map, reflog, sources, edits = {}, [], {}, []

    def block(key, sid):
        if key == "S2_serial_table":
            tex, info = serial_float(v16)
        else:
            tex, info = extract(v16, key)
        for k, pat, rep in EDITS:
            if k == key:
                tex, n = re.subn(pat, rep, tex, flags=re.M)
                edits.append({"block": key, "pattern": pat, "replacement": rep, "count": n})
        tex = subsection_star(swap_inputs(tex), sid, sec_map)
        sources[key] = info
        return tex

    sec_map.update(SEC_LABELS_DROPPED)
    t = lambda base, label, note_file=None, note=None: table_float(base, caps.get(base, ""), label, note, note_file)   # noqa: E731
    S = []
    # S1
    S.append(("S1", "Power under i.i.d.\\ errors at equalized size",
              [RM_NOTE, block("S1_size", "S1"), block("S1_power", "S1"), block("S1_fig_lp", "S1")]))
    # S2
    S.append(("S2", "Serially correlated errors, cell by cell", [
        t3_text(), block("S2_serial_table", "S2"),
        table_float("tab_serial_asy_audit15", caps["tab_serial_asy_audit15"], "tab:serialasy",
                    note="Same paths as \\cref{tab:serial}; asymptotic critical values of \\citet{ng2001lag}."),
        table_float("tab_lag_audit15", caps["tab_lag_audit15"], "tab:lag"),
        table_float("tab_boot_audit15", "Size of MZ$_t$-GLS with five calibrations over the thirty-six designs, $\\alpha = 0.05$.",
                    "tab:boot", note_file="tab_boot_note_audit15"),
        "\\subsection*{The sieve bootstraps}", SB_SWB_TEXT, paso0_text(),
        table_float("tab_fixedb_size_audit15", caps["tab_fixedb_size_audit15"], "tab:fixedbsize", note_file="tab_fixedb_size_note_audit15"),
        block("S2_serialpower", "S2"),
        "\\subsection*{Scale diagnostics}",
        "\\Cref{tab:diagnull,tab:diagalt,tab:diagattrib} report, for the designs of \\cref{tab:serial,tab:serialpower} and of the "
        "attribution experiment, the medians of the Bartlett and autoregressive scale estimates relative to the long-run variance, "
        "with the selected bandwidth and lag.",
        table_float("s2_diag_a_diagnostics_null", caps["s2_diag_a_diagnostics_null"], "tab:diagnull"),
        table_float("s2_diag_b_diagnostics_alt", caps["s2_diag_b_diagnostics_alt"], "tab:diagalt"),
        table_float("s2_diag_c_attribution_diagnostics", caps["s2_diag_c_attribution_diagnostics"], "tab:diagattrib")]))
    # S3
    S.append(("S3", "The initial condition", [block("S3_initial", "S3")]))
    # S4
    S.append(("S4", "Mean breaks, variance breaks, heavy tails and GARCH", [block("S4_breaks", "S4"), SB_SWB_SENTENCE]))
    # S5
    s5 = [block("S5_def", "S5"), block("S5_theta", "S5"), block("S5_fig", "S5"), "\\subsection*{Tables with $\\theta = 0.02$}", RM_NOTE]
    twin = {"size": "tab:size", "calib": "tab:calib", "localpower": "tab:localpower", "dgp1": "tab:dgp1", "ctpower": "tab:ctpower",
            "dgp2": "tab:dgp2", "dgp3": "tab:dgp3", "misspec": "tab:misspec", "awb": "tab:awb", "dgp5": "tab:dgp5", "fp": "tab:fp"}
    for lab in [l for l, _ in A15S.S6_TABLES]:
        base = "s5_tab_%s_theta0p02" % lab
        if not os.path.exists(os.path.join(A15S.SUPP, "tables", base + ".tex")):
            continue
        nf = base + "_note" if os.path.exists(os.path.join(A15S.SUPP, "tables", base + "_note.tex")) else None
        s5.append(table_float(base, "As \\cref{%s}, computed with $\\theta = 0.02$. Bold entries follow the rule stated in its note." % twin[lab],
                              "tab:%s02" % lab, note_file=nf))
    S.append(("S5", "The smoothed family $S_\\theta$", s5))
    # S6
    S.append(("S6", "The two-channel construction and other negative results", [
        block("S6_twochannel", "S6"),
        t("s6_neg_a_variance_channel", "tab:negvariance"), t("s6_neg_b_adaptive_weight", "tab:negweight"),
        t("s6_neg_c_rebalancing", "tab:negrebal"), t("s6_neg_d_mean_anchor", "tab:neganchor")]))
    # S7
    S.append(("S7", "Rate of the HAC estimator and the trend case of the consistency theorem", [
        t("s7_hac_a_rates", "tab:hacrates"), t("s7_hac_b_hac_median", "tab:hacmedian"),
        "\\subsection*{The trend case of the consistency theorem}", block("S7_trend", "S7")]))
    # S8
    s8 = []
    for name in sorted(os.listdir(os.path.join(A15S.SUPP, "tables"))):
        if name.startswith("s8_critical_theta_"):
            base = name[:-4]
            th = base.split("_theta_")[1].replace("p", ".")
            s8.append(table_float(base, "Lower-tail critical values of $S_\\theta$, $\\theta = %s$%s." % (
                th, " (\\RMGLS{})" if th == "0" else ""), "tab:critB" if th == "0" else "tab:crit%s" % base.split("_theta_")[1]))
    s8.append(table_float("tab_critMSB_audit14", "Critical values of MSB-GLS and MZ$_t$-GLS with Monte Carlo standard errors.",
                          "tab:critMSBse", note_file="tab_critMSB_note_audit14"))
    S.append(("S8", "Critical values", s8))
    # S9
    S.append(("S9", "The pre-registered monitoring application", [
        block("S9_application", "S9"), "\\subsection*{Details}",
        t("s9_app_a_oos_size", "tab:oos"), t("s9_app_b_adverse_cells", "tab:adverse"), t("s9_app_c_fp_by_cell", "tab:fpcell"),
        t("s9_app_d_latency_by_event", "tab:latency")]))
    # S10
    S.append(("S10", "Protocols, amendments and predictions", [
        "The protocols, amendments and predictions are in \\texttt{protocols/}, in the order in which they were committed."]))
    return S, sec_map, reflog, sources, edits


def doc(S, v16, v17):
    L = ["\\documentclass[11pt]{article}", "\\usepackage[margin=2cm]{geometry}",
         "\\usepackage{booktabs,graphicx,amsmath,amssymb,amsthm,placeins,adjustbox,threeparttable,multirow,array}",
         "\\usepackage[round,authoryear]{natbib}", "\\usepackage[capitalise,noabbrev]{cleveref}", "\\graphicspath{{figures/}}",
         "\\renewcommand\\thesection{S\\arabic{section}}", "\\counterwithin{table}{section}", "\\counterwithin{figure}{section}",
         "\\counterwithin{equation}{section}", "\\renewcommand\\thetable{\\thesection.\\arabic{table}}",
         "\\renewcommand\\thefigure{\\thesection.\\arabic{figure}}", "\\renewcommand\\theequation{\\thesection.\\arabic{equation}}"]
    L += macros(v16, v17)[0]
    L += ["\\title{Supplementary material}", "\\date{}", "\\begin{document}", "\\maketitle",
          "Sections, tables and figures are numbered S$k$ and S$k.j$. Every table is generated from the machine-readable files in "
          "\\texttt{data/}; \\texttt{README.md} maps each table to its source. References to the main text give the number of the "
          "table, section or equation there.", ""]
    for sid, title, items in S:
        L += ["\\FloatBarrier", "\\section{%s}\\label{supp:%s}" % (title, sid.lower()), ""]
        L += [x if x.endswith("\n") else x + "\n" for x in items]
    L += ["\\FloatBarrier", "\\bibliographystyle{plainnat}", "\\bibliography{references}", "\\end{document}", ""]
    return "\n".join(L)


def bib(v16, v17):
    entries, order = {}, []
    for src in (v17.files.get("references.bib", ""), v16.files.get("references.bib", "")):
        for m in re.finditer(r"@\w+\{([^,]+),.*?\n\}", src, flags=re.S):
            if m.group(1) not in entries:
                entries[m.group(1)] = m.group(0)
                order.append(m.group(1))
    return "\n\n".join(entries[k] for k in order) + "\n", len(order)


def readme(W, S):
    L = ["# Supplementary material", "", "Generated by `experiments/audit16_supplement.py` (audit A16, amendment 6) from the result files "
         "in `data/`, the tabulars exported by earlier audits and the text of the previous manuscript version. Do not edit by hand.", "",
         "Sections: " + "; ".join("%s %s" % (s, re.sub(r"[$\\]", "", t)) for s, t, _ in S) + ".", "",
         "| File | Source |", "|---|---|"]
    for rel, v in sorted(W.files.items()):
        if rel.startswith(("tables/", "figures/")):
            L.append("| `%s` | %s |" % (rel, ", ".join("`%s`" % x for x in v["sources"])))
    L += ["", "`protocols/`: protocols, amendments and predictions. `MANIFEST.sha256`: sha256 of every file.", ""]
    return "\n".join(L)


def compile_check(supp):
    tmp = tempfile.mkdtemp(prefix="a16_supp_")
    dst = os.path.join(tmp, "supplementary")
    shutil.copytree(supp, dst)
    runs = []
    for exe in (PDFLATEX, BIBTEX, PDFLATEX, PDFLATEX):
        args = [exe, "-interaction=nonstopmode", "supplement.tex"] if exe == PDFLATEX else [exe, "supplement"]
        r = subprocess.run(args, cwd=dst, capture_output=True, text=True, encoding="utf-8", errors="replace")
        runs.append(r.returncode)
    log = open(os.path.join(dst, "supplement.log"), encoding="utf-8", errors="replace").read()
    blg = open(os.path.join(dst, "supplement.blg"), encoding="utf-8", errors="replace").read() if os.path.exists(os.path.join(dst, "supplement.blg")) else ""
    aux = open(os.path.join(dst, "supplement.aux"), encoding="utf-8", errors="replace").read()
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    labels = {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{([^}@]+)\}\{\{([^}]*)\}", aux)}
    res = {"compiled": os.path.exists(os.path.join(dst, "supplement.pdf")), "errors": len(re.findall(r"^! ", log, flags=re.M)),
           "first_errors": re.findall(r"^! .*$", log, flags=re.M)[:5],
           "undefined_references": len(re.findall(r"Reference `[^']*' on page \d+ undefined", log)),
           "undefined_citations": len(re.findall(r"Citation `[^']*' on page \d+ undefined", log)),
           "undefined_list": sorted(set(re.findall(r"(?:Reference|Citation) `([^']*)' on page \d+ undefined", log)))[:20],
           "bibtex_warnings": len(re.findall(r"^Warning--", blg, flags=re.M)),
           "overfull": len(re.findall(r"Overfull \\hbox", log)), "pages": int(pages.group(1)) if pages else None, "labels": labels,
           "returncodes": runs}
    keep = os.path.join(C.RESULTS, "_tmp_supplement_pdf_audit16")
    if os.environ.get("A16_KEEP_PDF"):
        os.makedirs(keep, exist_ok=True)
        shutil.copy2(os.path.join(dst, "supplement.pdf"), os.path.join(keep, "supplement.pdf"))
    shutil.rmtree(tmp, ignore_errors=True)
    return res


def sec6_integrity(v16, supp_tex):
    """E6.6.4: todo el texto de la sec6 del v16 esta en S9, salvo las referencias cruzadas reescritas."""
    def norm(s):
        s = re.sub(r"\\(cref|Cref|ref)\{[^}]*\}", " ", s)
        s = re.sub(r"(Table|Section|Figure|Definition|Proposition|Remark|Theorem|equation|Equation)~\S+ of the main text", " ", s)
        s = re.sub(r"Section~S\d+", " ", s)
        s = re.sub(r"\\subsection\*?\{", r"\\subsection{", s)
        s = re.sub(r"\\label\{[^}]*\}", " ", s)
        return re.sub(r"\s+", " ", s).strip()
    src, _ = extract(v16, "S9_application")
    a = supp_tex.index("\\label{supp:s9}")
    b = supp_tex.index("\\subsection*{Details}", a)
    got = supp_tex[a:b]
    sw = [w for w in norm(src).split(" ") if w]
    gw = " " + norm(got) + " "
    missing = []
    for i in range(0, len(sw) - 7, 8):
        chunk = " ".join(sw[i:i + 8])
        if chunk not in gw:
            missing.append(chunk)
    nums_src = re.findall(r"(?<![\w.])\d+(?:\.\d+)?", norm(src))
    nums_got = re.findall(r"(?<![\w.])\d+(?:\.\d+)?", norm(got))
    return {"chunks_checked": len(range(0, len(sw) - 7, 8)), "chunks_missing": missing[:10], "n_missing": len(missing),
            "numbers_src": len(nums_src), "numbers_equal": nums_src == nums_got}


def main():
    args = sys.argv[1:]
    trial = "--out" in args
    supp = os.path.abspath(args[args.index("--out") + 1]) if trial else SUPP_REAL
    if trial and os.path.normcase(supp) == os.path.normcase(SUPP_REAL):
        raise SystemExit("--out no puede ser supplementary/")
    v16, v17 = C.v16(), C.v17()
    tmp = tempfile.mkdtemp(prefix="a16_v17_")
    body, v17c = body_labels(tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    if os.path.exists(supp):
        shutil.rmtree(supp)
    A15S.SUPP = supp
    W = A15S.Writer()
    res = {"S1": A15S.s1(W), "S2": A15S.s2(W), "S3": A15S.s3(W), "S4": A15S.s4(W), "S5": A15S.s5(W), "S6": A15S.s6(W),
           "S7": A15S.s7(W), "S8": A15S.s8(W), "S9": A15S.s9(W)}
    renamed = {}
    for rel in list(W.files):
        base = os.path.basename(rel)
        if not rel.startswith("tables/"):
            continue
        for old, new in RENAME:
            if base.startswith(old):
                nb = new + base[len(old):]
                os.replace(os.path.join(supp, rel), os.path.join(supp, "tables", nb))
                W.files["tables/" + nb] = W.files.pop(rel)
                renamed[base] = nb
                break
    same_v16 = {}
    for name in A13_TABLES:
        W.copy("tables/%s.tex" % name, os.path.join(T13, name + ".tex"))
        try:
            same_v16[name] = v16.read_bytes("tables/%s.tex" % name).decode("utf-8").replace("\r", "") == \
                open(os.path.join(supp, "tables", name + ".tex"), encoding="utf-8").read().replace("\r", "")
        except KeyError:
            same_v16[name] = None
    for name in ("tab_serial_asy_audit15", "tab_lag_audit15", "tab_boot_audit15", "tab_boot_note_audit15", "tab_fixedb_size_audit15",
                 "tab_fixedb_size_note_audit15"):
        W.copy("tables/%s.tex" % name, os.path.join(T15, name + ".tex"))
    for name in ("tab_critMSB_audit14", "tab_critMSB_note_audit14"):
        W.copy("tables/%s.tex" % name, os.path.join(C.C15.C14.TABLES, name + ".tex"))
    for name in A15S.DATA:
        W.copy("data/" + name, os.path.join(C.RESULTS, name))
    for name, folder in A15S.DATA_EXTRA.items():
        W.copy("data/" + name, os.path.join(folder, name))
    for name in ("code_check_audit16.json", "literals_v17b_audit16.json", "b1_paso0_v2_audit15.json", "b0_t3_audit15.json"):
        if C.have(name):
            W.copy("data/" + name, os.path.join(C.RESULTS, name))
    os.makedirs(os.path.join(supp, "figures"), exist_ok=True)
    for fg in FIGS:
        p = os.path.join(supp, "figures", fg + ".pdf")
        with open(p, "wb") as fh:
            fh.write(v16.read_bytes("figures/%s.pdf" % fg))
        W.files["figures/%s.pdf" % fg] = {"sources": ["paper_latex_v16.zip:figures/%s.pdf" % fg], "source_sha256": C.sha256_file(p)}
    btxt, nbib = bib(v16, v17)
    W.text("references.bib", btxt, ["paper_latex_v17.zip:references.bib", "paper_latex_v16.zip:references.bib"])
    S, sec_map, reflog, sources, edits = build(v16, v17, body, W, renamed)
    raw = doc(S, v16, v17)
    sup_labels = set(re.findall(r"\\label\{([^}]*)\}", raw))
    extra = {"app:tables": "Section~S2", "sec:negative": "Section~S6", "sec:implementation": "the main text"}
    tex = resolve_refs(raw, sup_labels, sec_map, body, extra, reflog)
    W.text("supplement.tex", tex, ["generado"])
    for rel in sorted(W.files):
        if rel.startswith("tables/") and rel.endswith(".tex"):
            p = os.path.join(supp, rel)
            src = open(p, encoding="utf-8").read()
            if re.search(r"\\(cref|Cref|ref)\{", src):
                n0 = len(reflog)
                new = resolve_refs(src, sup_labels, sec_map, body, extra, reflog)
                for r in reflog[n0:]:
                    r["file"] = rel
                with open(p, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)
                W.files[rel]["refs_rewritten"] = len(reflog) - n0
    W.text("README.md", readme(W, S), ["generado"])
    man = []
    for dp, _, fs in os.walk(supp):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            man.append("%s  %s" % (C.sha256_file(p), os.path.relpath(p, supp).replace("\\", "/")))
    W.text("MANIFEST.sha256", "\n".join(sorted(man, key=lambda s: s.split("  ", 1)[1])) + "\n", ["generado"])
    A15S.SUPP = supp
    sc = A15S.scan()
    comp = compile_check(supp)
    lab = comp.pop("labels")
    numbering = {"S2": {l: lab.get(l) for l in MAP_S2},
                 "S2_matches_map": [lab.get(l) for l in MAP_S2] == ["S2.%d" % i for i in range(1, len(MAP_S2) + 1)],
                 "tables": {k: v for k, v in lab.items() if k.startswith("tab:")},
                 "figures": {k: v for k, v in lab.items() if k.startswith("fig:")},
                 "sections": {k: v for k, v in lab.items() if k.startswith("supp:")}}
    main_refs = re.findall(r"(Table|Section|Figure|Definition|Proposition|Remark|Theorem|equation|Equation|Appendix)~(\S+) of the main text", tex)
    body_nums = {(TYPE_NAME.get(t, t).lower(), n) for t, n in body.values()}
    bad_main = [x for x in main_refs if (x[0].lower(), x[1].strip("()")) not in body_nums]
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 6, lectura E6.6", "trial": trial,
           "inputs": {"v16_zip_sha256": v16.sha256, "v17_zip_sha256": v17.sha256, "map": "SUPPLEMENT_MAP_v17.md (zip del v17)"},
           "v17_control_compile": v17c, "body_labels": {k: list(v) for k, v in body.items()},
           "sections": [{"id": s, "title": t} for s, t, _ in S], "generated": res, "renamed": renamed,
           "a13_tables_identical_to_v16": same_v16, "transcribed_blocks": sources, "editorial_edits": edits,
           "section_label_map": sec_map, "references": reflog, "macro_conflicts": macros(v16, v17)[1],
           "unresolved": [r for r in reflog if r["how"] == "SIN RESOLVER"],
           "main_text_refs": {"count": len(main_refs), "not_in_v17_body": bad_main}, "numbering": numbering,
           "sec6_integrity": sec6_integrity(v16, tex), "bib_entries": nbib, "files": {k: v for k, v in sorted(W.files.items())},
           "n_files": len(W.files), "anonymization_scan": sc, "compile": comp}
    C.write_result(OUT_TRIAL if trial else OUT, out, __file__)
    print("archivos:", len(W.files), "| aciertos no-hash:", sc["non_hash_hits"], "| compilacion:", comp)
    print("S2:", numbering["S2"], "coincide con el mapa:", numbering["S2_matches_map"])
    print("sin resolver:", out["unresolved"], "| refs al cuerpo fuera del v17:", bad_main)
    print("sec6:", out["sec6_integrity"], "| v16 identicos:", same_v16)
    print("ediciones:", edits)
    return 0


if __name__ == "__main__":
    sys.exit(main())
