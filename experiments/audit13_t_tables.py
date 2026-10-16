"""
Auditoria A13 - B13.T: tablas nuevas para el manuscrito desde los JSON de A12.

Solo lee JSON (protocol_audit13.md, lectura 14):
  - tab:serial: tamano al valor critico iid (bloque "iid" de las 36 celdas sz_* de
    bA_ma_audit12.json) de RM-GLS theta = 0, (b), (b'), MSB-GLS NP, MZ_t-GLS NP,
    DF-GLS, ADF y PP, con el factor poblacional del Bartlett en la mediana de B de
    la celda (bartlett_factor_at_median_B); negrita (tambien en el Markdown): fuera
    de la region exacta de la N de la celda.
  - tab:serialpower: potencia ajustada al tamano (bloque "adjusted" de las 36
    celdas pw_*), con su rho.
  - tab:initial: B12.C completa (bC_initial_audit12.json): potencia de los nueve
    procedimientos en las 15 celdas, diferencia de RM-GLS theta = 0 frente a
    DF-GLS (pp, EE pareado) y su McNemar exacto.
Salidas: experiments/results/t_tables_audit13.json y los tabulares
tables_audit13/tab_{serial,serialpower,initial}_audit13.tex.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "t_tables_audit13.json")
SRC_A = "bA_ma_audit12.json"
SRC_C = "bC_initial_audit12.json"
PROCS = (("gls_t0", "\\RMGLS{}", "RM-GLS θ=0"), ("glsb_t0", "(b)", "(b) s²_AR MAIC-GLS"),
         ("glsbp_t0", "(b$'$)", "(b′) s²_AR MAIC-MCO"), ("msb", "MSB-GLS", "MSB-GLS NP"),
         ("mzt", "MZ$_t$-GLS", "MZ_t-GLS NP"), ("dfgls", "DF-GLS", "DF-GLS MAIC-GLS"), ("adf", "ADF", "ADF (AIC)"),
         ("pp", "PP", "PP"))
INIT_PROCS = (("gls_t0", "\\RMGLS{}", "RM-GLS θ=0"), ("gls_t0.02", "$\\theta = 0.02$", "RM-GLS θ=0.02"),
              ("glsb_t0", "(b)", "(b) s²_AR MAIC-GLS"), ("glsbp_t0", "(b$'$)", "(b′) s²_AR MAIC-MCO"),
              ("dfgls", "DF-GLS", "DF-GLS MAIC-GLS"), ("mzt", "MZ$_t$-GLS", "MZ_t-GLS NP"),
              ("msb", "MSB-GLS", "MSB-GLS NP"), ("adf", "ADF", "ADF (AIC)"), ("pp", "PP", "PP"))
CASE = {"c": "Constant", "ct": "Trend"}
CASE_ES = {"c": "constante", "ct": "tendencia"}


def signed(x):
    s = "%+.1f" % x
    return "$-$" + s[1:] if s.startswith("-") else s


def err_tex(err):
    kind, v = err
    return ("MA, $\\psi = %g$" if kind == "ma" else "AR, $\\phi = %g$") % v


def err_md(err):
    kind, v = err
    return ("MA ψ = %g" if kind == "ma" else "AR φ = %g") % v


def ordered(cells):
    a = C.read_json(SRC_A)
    order = [tuple(e) for e in a["config"]["errors"]]
    return sorted(cells.items(), key=lambda kv: (order.index(tuple(kv[1]["err"])), kv[1]["n"],
                                                 a["config"]["cases"].index(kv[1]["case"])))


def tabular(colspec, heads, rows, groups):
    t = ["\\begin{tabular}{%s}" % colspec, "\\toprule", " & ".join(heads) + " \\\\", "\\midrule"]
    last = None
    for g, r in zip(groups, rows):
        if last is not None and g != last:
            t.append("\\addlinespace")
        last = g
        t.append(" & ".join(r) + " \\\\")
    t += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(t)


def md(heads, rows):
    return "\n".join(["| " + " | ".join(heads) + " |", "|" + "---|" * len(heads)] + ["| " + " | ".join(r) + " |" for r in rows])


def serial():
    a = C.read_json(SRC_A)
    rows_tex, rows_md, groups, recs = [], [], [], []
    for name, c in ordered(a["size"]):
        bf = c["bartlett_factor_at_median_B"]
        vals = {p: c["iid"][p] for p, _, _ in PROCS}
        cells = [TB.bold(TB.f3(vals[p]["rate"]), not vals[p]["in_region"]) for p, _, _ in PROCS]
        rows_tex.append([err_tex(c["err"]), "%d" % c["n"], CASE[c["case"]]] + cells + ["%.2f (%d)" % (bf["factor"], bf["B"])])
        rows_md.append([err_md(c["err"]), "%d" % c["n"], CASE_ES[c["case"]]]
                       + [("%s" if vals[p]["in_region"] else "**%s**") % TB.f3(vals[p]["rate"]) for p, _, _ in PROCS]
                       + ["%.2f (B = %d)" % (bf["factor"], bf["B"])])
        groups.append(tuple(c["err"]))
        recs.append({"cell": name, "err": c["err"], "n": c["n"], "case": c["case"], "N": vals["gls_t0"]["n"],
                     "rates": {p: vals[p] for p, _, _ in PROCS}, "bartlett": bf, "path": "size.%s.iid" % name})
    heads_tex = ["Errors", "$n$", "Case"] + [t for _, t, _ in PROCS] + ["Bartlett (B)"]
    heads_md = ["Error", "n", "Caso"] + [m for _, _, m in PROCS] + ["Factor Bartlett (B)"]
    region = a["exact_region_20000"]
    return recs, tabular("lrl" + "c" * (len(PROCS) + 1), heads_tex, rows_tex, groups), md(heads_md, rows_md), region


def serialpower():
    a = C.read_json(SRC_A)
    cells = {k: v for k, v in a["power"].items() if k.startswith("pw_")}
    rows_tex, rows_md, groups, recs = [], [], [], []
    for name, c in ordered(cells):
        vals = {p: c["adjusted"][p] for p, _, _ in PROCS}
        rows_tex.append([err_tex(c["err"]), "%d" % c["n"], CASE[c["case"]], TB.f3(c["rho"])]
                        + [TB.f3(vals[p]["rate"]) for p, _, _ in PROCS])
        rows_md.append([err_md(c["err"]), "%d" % c["n"], CASE_ES[c["case"]], TB.f3(c["rho"])]
                       + [TB.f3(vals[p]["rate"]) for p, _, _ in PROCS])
        groups.append(tuple(c["err"]))
        recs.append({"cell": name, "err": c["err"], "n": c["n"], "case": c["case"], "rho": c["rho"], "size_cell": c["size_cell"],
                     "N": vals["gls_t0"]["n"], "rates": vals, "path": "power.%s.adjusted" % name})
    heads_tex = ["Errors", "$n$", "Case", "$\\rho$"] + [t for _, t, _ in PROCS]
    heads_md = ["Error", "n", "Caso", "ρ"] + [m for _, _, m in PROCS]
    return recs, tabular("lrlc" + "c" * len(PROCS), heads_tex, rows_tex, groups), md(heads_md, rows_md)


def initial():
    b = C.read_json(SRC_C)
    order = b["config"]["variants"]
    cells = sorted(b["cells"].items(), key=lambda kv: (kv[1]["rho"], order.index(kv[1]["variant"])))
    rows_tex, rows_md, groups, recs = [], [], [], []
    for name, c in cells:
        u0_tex = "random" if c["variant"] == "random" else "$\\alpha = %g$" % c["alpha"]
        u0_md = "aleatoria" if c["variant"] == "random" else "α = %g" % c["alpha"]
        d = c["diff_vs_dfgls"]["gls_t0"]
        mc = c["mcnemar_vs_dfgls"]["gls_t0"]
        pw = [TB.f3(c["power"][p]["rate"]) for p, _, _ in INIT_PROCS]
        rows_tex.append([TB.f3(c["rho"]), u0_tex] + pw + ["%s (%.1f)" % (signed(d["delta"] * C.PP), d["se"] * C.PP),
                                                          TB.p_sci(mc["p_value"])])
        rows_md.append([TB.f3(c["rho"]), u0_md] + pw + ["%+.2f (%.2f)" % (d["delta"] * C.PP, d["se"] * C.PP),
                                                        "%.2g" % mc["p_value"]])
        groups.append(c["rho"])
        recs.append({"cell": name, "rho": c["rho"], "variant": c["variant"], "alpha": c["alpha"], "N": c["power"]["gls_t0"]["n"],
                     "power": {p: c["power"][p] for p, _, _ in INIT_PROCS}, "diff_rmgls0_vs_dfgls": d, "mcnemar_rmgls0_vs_dfgls": mc,
                     "path": "cells.%s" % name})
    heads_tex = ["$\\rho$", "$u_0$"] + [t for _, t, _ in INIT_PROCS] + ["\\RMGLS{} $-$ DF-GLS (pp)", "McNemar $p$"]
    heads_md = ["ρ", "u₀"] + [m for _, _, m in INIT_PROCS] + ["RM-GLS θ=0 − DF-GLS (pp, EE)", "McNemar p"]
    return recs, tabular("cl" + "c" * (len(INIT_PROCS) + 2), heads_tex, rows_tex, groups), md(heads_md, rows_md), b["config"]


def main():
    TB.ROUNDING["mode"] = "binary"
    s_recs, s_tex, s_md, region = serial()
    p_recs, p_tex, p_md = serialpower()
    i_recs, i_tex, i_md, i_cfg = initial()
    prov = C.provenance(__file__, seed_family=None)
    paths = {}
    for name, tex, src in (("serial", s_tex, SRC_A), ("serialpower", p_tex, SRC_A), ("initial", i_tex, SRC_C)):
        path = os.path.join(C.TABLES, "tab_%s_audit13.tex" % name)
        C.write_text(path, "%% Generado por experiments/audit13_t_tables.py desde experiments/results/%s (no editar a mano)\n%s\n"
                     % (src, tex), __file__, prov)
        paths[name] = {"tex": C.rel(path), "tex_sha256": C.sha256_file(path)}
    out = {"provenance": prov, "sources": {SRC_A: C.sha256_file(os.path.join(C.RESULTS, SRC_A)),
                                           SRC_C: C.sha256_file(os.path.join(C.RESULTS, SRC_C))},
           "reading": "protocol_audit13.md, lectura 14", "rounding": "binary (%.3f)",
           "serial": {"rows": s_recs, "markdown": s_md, "exact_region_20000": region, **paths["serial"]},
           "serialpower": {"rows": p_recs, "markdown": p_md, **paths["serialpower"]},
           "initial": {"rows": i_recs, "markdown": i_md, "config": i_cfg, **paths["initial"]}}
    C.write_result(OUT, out, __file__)
    print(s_md, "\n")
    print(p_md, "\n")
    print(i_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
