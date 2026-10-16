"""
Auditoria A11 - T2: tabla de DGP 2 con el theta final (0.02) para el manuscrito.

Solo lee JSON (protocolo_audit11, lectura 5):
  - b103_equalized_audit10.json, celdas dgp2_*: rates_sim (RM-GLS theta final, RM =
    rm_t0.1, ADF, PP, DF-GLS, MZt-GLS, MSB-GLS, ZA con valor critico simulado de A9),
    rates_asy.za (informativa) y McNemar exacto de la primaria frente a DF-GLS-sim;
  - tamano de ZA bajo paseo aleatorio y bajo paseo con quiebre de media 1:
    b5_power_audit8.json (za_size, p-valor asintotico, N = 5000) y, como segunda
    fuente, dgp2_break_tests_audit6.json (size_control).

Salidas: experiments/results/t2_dgp2_audit11.json, tab_dgp2_audit11.md y
tab_dgp2_audit11.tex (solo el tabular).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402

SRC = "b103_equalized_audit10.json"
OUT = os.path.join(C.RESULTS, "t2_dgp2_audit11.json")
OUT_MD = os.path.join(C.RESULTS, "tab_dgp2_audit11.md")
OUT_TEX = os.path.join(C.RESULTS, "tab_dgp2_audit11.tex")
DELTAS = (0, 0.5, 1, 2, 3, 5)
NS = (200, 500, 1000)
PROCS = (("prim", None), ("rm", "rm_t0.1"), ("adf", "adf"), ("pp", "pp"), ("dfgls", "dfgls"), ("mzt", "mzt"),
         ("msb", "msb"), ("za", "za"))
RATE_DEC = 3
P_DEC = 3


def cell_key(delta, n):
    return "dgp2_delta%s_n%d" % (("%g" % delta).replace(".", "p"), n)


def fmt_rate(x):
    return "%.*f" % (RATE_DEC, x)


def fmt_p_md(p):
    if p >= 10 ** -P_DEC:
        return "%.*f" % (P_DEC, p)
    return "%.1e" % p


def fmt_p_tex(p):
    if p >= 10 ** -P_DEC:
        return "%.*f" % (P_DEC, p)
    e = int(math.floor(math.log10(p)))
    return "$%.1f\\times10^{%d}$" % (p / 10 ** e, e)


def main():
    b = C.read_json(SRC)
    theta = C.read_json("b101_theta_audit10.json")["primary_theta"]
    prim = b["config"]["primary"]
    rows = []
    for delta in DELTAS:
        for n in NS:
            k = cell_key(delta, n)
            c = b["cells"][k]
            if c["n"] != n or c["delta"] != delta:
                raise KeyError("celda %s inconsistente" % k)
            rates = {lab: c["rates_sim"][prim if proc is None else proc] for lab, proc in PROCS}
            mc = c["mcnemar_primary_vs_sim"]["dfgls"]
            rows.append({"cell": k, "delta": delta, "n": n,
                         "rates": {lab: {"rate": r["rate"], "rejections": r["rejections"], "n": r["n"],
                                         "wilson": [r["wilson_lower"], r["wilson_upper"]]} for lab, r in rates.items()},
                         "za_asy": c["rates_asy"]["za"]["rate"],
                         "mcnemar_vs_dfgls": {"p_value": mc["p_value"], "only_primary": mc["only_first"],
                                              "only_dfgls": mc["only_second"]},
                         "source_path": "cells.%s" % k})
    a8 = C.read_json("b5_power_audit8.json")
    za_size = {}
    for kind, lab in (("rw", "random_walk"), ("rwbreak", "random_walk_break_mu1")):
        for n in NS:
            r = a8["za_size"]["za_%s_n%d" % (kind, n)]["rates"]["za"]
            za_size["%s|%d" % (lab, n)] = {"kind": lab, "n": n, "rate": r["rate"], "rejections": r["rejections"],
                                          "N": r["n"], "wilson": [r["wilson_lower"], r["wilson_upper"]],
                                          "in_region": r["in_region"], "source": "b5_power_audit8.json",
                                          "path": "za_size.za_%s_n%d.rates.za" % (kind, n)}
    a6 = C.read_json("dgp2_break_tests_audit6.json")["size_control"]
    za_a6 = {}
    for kind, lab in (("pure_rw", "random_walk"), ("break_rw", "random_walk_break_mu1")):
        for n in NS:
            r = a6[kind][str(n)]
            za_a6["%s|%d" % (lab, n)] = {"kind": lab, "n": n, "rate": r["za_size"], "ci": r["za_ci"],
                                        "N": r["ours_n_sim"], "source": "dgp2_break_tests_audit6.json",
                                        "path": "size_control.%s.%s.za_size" % (kind, n)}
    heads = ["δ", "n", "RM-GLS (θ = %g)" % theta, "RM", "ADF-sim", "PP-sim", "DF-GLS-sim", "MZ_t-GLS-sim",
             "MSB-GLS-sim", "ZA", "McNemar p vs DF-GLS-sim"]
    md = ["| " + " | ".join(heads) + " |", "|" + "---|" * len(heads)]
    for r in rows:
        md.append("| " + " | ".join(["%g" % r["delta"], "%d" % r["n"]] + [fmt_rate(r["rates"][lab]["rate"]) for lab, _ in PROCS]
                                    + [fmt_p_md(r["mcnemar_vs_dfgls"]["p_value"])]) + " |")
    tex_heads = ["$\\delta$", "$n$", "\\RMGLS{} ($\\theta = %g$)" % theta, "RM", "ADF-sim", "PP-sim", "DF-GLS-sim",
                 "MZ$_t$-GLS-sim", "MSB-GLS-sim", "ZA", "McNemar $p$"]
    tex = ["\\begin{tabular}{r r " + "c " * (len(tex_heads) - 2) + "}", "\\toprule", " & ".join(tex_heads) + " \\\\",
           "\\midrule"]
    for j, r in enumerate(rows):
        if j and r["n"] == NS[0]:
            tex.append("\\addlinespace")
        tex.append(" & ".join(["%g" % r["delta"], "%d" % r["n"]] + [fmt_rate(r["rates"][lab]["rate"]) for lab, _ in PROCS]
                              + [fmt_p_tex(r["mcnemar_vs_dfgls"]["p_value"])]) + " \\\\")
    tex += ["\\bottomrule", "\\end{tabular}"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    with open(OUT_TEX, "w", encoding="utf-8", newline="\n") as f:
        f.write("%% Generado por experiments/audit11_t2_dgp2.py desde experiments/results/%s (no editar a mano)\n" % SRC)
        f.write("\n".join(tex) + "\n")
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["T2"]), "source": SRC,
           "source_sha256": C.sha256_file(os.path.join(C.RESULTS, SRC)), "primary_theta": theta, "primary_key": prim,
           "config_source": {k: b["config"][k] for k in ("N_sim", "N_cal", "trajectories", "rule_sim", "calibration_source")},
           "exact_region_5000": b["exact_region_5000"], "za_in_source": True,
           "za_column": "rates_sim.za (valor critico simulado; calibracion de A9, N_cal = 50 000)",
           "rm_column": "rm_t0.1", "rows": rows, "za_size_a8": za_size, "za_size_a6": za_a6,
           "markdown": C.rel(OUT_MD), "markdown_sha256": C.sha256_file(OUT_MD),
           "latex": C.rel(OUT_TEX), "latex_sha256": C.sha256_file(OUT_TEX)}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, [OUT_MD, OUT_TEX], out["provenance"])
    print("\n".join(md))
    print("\n".join(tex))
    return 0


if __name__ == "__main__":
    sys.exit(main())
