"""
Auditoria A15 - B15.6: tabulares para el v17 (enmienda 4, lecturas 6.1-6.6). Solo lee JSON; lo recorre
tests/test_no_literals_audit15.py. Redondeo binario.

Salidas (experiments/results/tables_audit15/):
  - tab_boot_audit15.tex (+ nota): tamano de MZ_t-GLS, 36 celdas x 5 brazos (b1_boot_audit15.json).
  - tab_bootpower_audit15.tex (+ nota): 8 celdas de potencia, bruta y ajustada por brazo, y diferencia
    ajustada frente a (ii) en pp con el p de McNemar.
  - tab_fixedb_audit15.tex (+ nota): por configuracion (Andrews y (b) desde A12; b = 0.1, LLSW, b = 0.3,
    b = 1 desde b3_fixedb_audit15.json): tamano minimo y maximo (36 celdas), D, M (30 celdas con psi != 0) y
    potencia ajustada a rho in {0.80, 0.90, 0.95}.
  - tab_fixedb_size_audit15.tex (+ nota): 36 celdas x 4 configuraciones fixed-b.
  - tab_summary_audit15.tex (+ nota) (enmienda 5, lectura 9.1): 10 filas; D y M (30 celdas psi != 0), minimo y
    maximo (36), celdas iid dentro de la region exacta de su N y potencia ajustada en rho = 0.90, n = 200,
    caso constante, errores iid, con la fuente de cada celda ("--" si no existe; no se estima).
y experiments/results/v17_tables_audit15.json (sha256, fuentes y valores de las notas).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402
import audit13_t_tables as T13                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "v17_tables_audit15.json")
SRC_B1, SRC_B3, SRC_A12 = "b1_boot_audit15.json", "b3_fixedb_audit15.json", "bA_ma_audit12.json"
ARMS = (("i", "(i)"), ("ii", "(ii)"), ("iii", "(iii)"), ("iv", "(iv)"), ("v_prime", "(v$'$)"))
FB_ROWS = (("andrews", "\\RMGLS{} (Andrews)"), ("b", "(b) $s^2_{\\mathrm{AR}}$"), ("b=0.1", "$b = 0.1$"), ("LLSW", "LLSW"),
           ("b=0.3", "$b = 0.3$"), ("b=1", "$b = 1$"))
FB_CONFIGS = ("b=0.1", "b=0.3", "b=1", "LLSW")
FB_LABEL = {"b=0.1": "$b = 0.1$", "b=0.3": "$b = 0.3$", "b=1": "$b = 1$", "LLSW": "LLSW"}
POW_RHO = ("0p8", "0p9", "0p95")
P_SMALL = 10 ** -3
REG_DEC = 4                        # decimales minimos de los extremos de la region exacta


def f(x, d):
    s = TB.fdec(x, d, "binary")
    return "$-$" + s[1:] if s.startswith("-") else s


def bound(x):
    """Extremo de una region exacta, con los decimales necesarios para escribirlo sin redondear (minimo REG_DEC)."""
    d = REG_DEC
    while round(x, d) != x:
        d += 1
    return TB.fdec(x, d, "binary")


def pval(p):
    return "$<$0.001" if p < P_SMALL else TB.fdec(p, 3, "binary")


def order():
    a = C.read_json(SRC_A12)["config"]
    return [tuple(e) for e in a["errors"]], list(a["cases"])


def tag(err):
    return T13_tag(err)


def T13_tag(err):
    kind, v = err
    return "%s_%s" % (kind, ("%g" % v).replace("-", "m").replace(".", "p"))


def sorted_cells(cells, errors, cases):
    tags = [T13_tag(e) for e in errors]
    return sorted(cells.items(), key=lambda kv: (tags.index(kv[1]["err_tag"]), kv[1]["n"], cases.index(kv[1]["case"])))


def err_of(tagv, errors):
    return {T13_tag(e): e for e in errors}[tagv]


def tabular(colspec, head_lines, rows, groups):
    L = ["\\begin{tabular}{%s}" % colspec, "\\toprule"] + head_lines + ["\\midrule"]
    last = None
    for gkey, r in zip(groups, rows):
        if last is not None and gkey != last:
            L.append("\\addlinespace")
        last = gkey
        L.append(" & ".join(r) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def header(src):
    return "% Generado por experiments/audit15_v17_tables.py desde " + src + " (no editar a mano)\n"


def tab_boot(b1, errors, cases):
    rows, groups = [], []
    for k, v in sorted_cells(b1["size"], errors, cases):
        e = err_of(v["err_tag"], errors)
        rows.append([T13.err_tex(e), "%d" % v["n"], T13.CASE[v["case"]]] +
                    [TB.bold(f(v["rates"][a]["rate"], 3), not v["rates"][a]["in_region"]) for a, _ in ARMS])
        groups.append(v["err_tag"])
    head = ["Errors & $n$ & Case & " + " & ".join(lab for _, lab in ARMS) + " \\\\"]
    reg = b1["exact_region"]
    note = ("Rejection rates of MZ$_t$-GLS with nominal level $0.05$ over $%d$ paths per cell. (i): asymptotic critical value of "
            "\\citet{ng2001lag}; (ii): critical value simulated under iid errors; (iii) SB (bootUR), (iv) AWB and (v$'$) SWB (bootUR): "
            "bootstrap $p$-value $(1 + \\#\\{T^* \\leq T\\})/(R + 1)$ with $R = %d$, rejection when $p \\leq 0.05$. Bold: outside the "
            "exact region $[%s, %s]$ for $%d$ paths.\n" % (b1["config"]["N_size"], b1["config"]["R"], bound(reg[0]),
                                                           bound(reg[1]), b1["config"]["N_size"]))
    return tabular("lrl" + "c" * len(ARMS), head, rows, groups), note


def power_n(b1):
    """n de las celdas de potencia, leido del nombre de su celda nula (sz_<error>_n<n>_<caso>)."""
    ns = {int(re.search(r"_n(\d+)_", v["null_cell"]).group(1)) for v in b1["power"].values()}
    return ns.pop()


def tab_bootpower(b1, errors, cases):
    rows, groups = [], []
    items = sorted(b1["power"].items(), key=lambda kv: ([T13_tag(e) for e in errors].index(kv[1]["err_tag"]), kv[1]["rho"],
                                                        cases.index(kv[1]["case"])))
    boot = [a for a, _ in ARMS if a in b1["prediction"]["by_arm"]]
    for k, v in items:
        e = err_of(v["err_tag"], errors)
        cells = [f(v["raw"][a]["rate"], 3) + " / " + f(v["adjusted"][a]["rate"], 3) for a, _ in ARMS]
        diffs = ["%s (%s)" % (f(v["vs_ii"][a]["diff_pp"], 1), pval(v["vs_ii"][a]["mcnemar"]["p_value"])) for a in boot]
        rows.append([T13.err_tex(e), TB.fdec(v["rho"], 2, "binary"), T13.CASE[v["case"]]] + cells + diffs)
        groups.append(v["err_tag"])
    lab = dict(ARMS)
    k1, k2 = len(ARMS), len(boot)
    head = ["& & & \\multicolumn{%d}{c}{Raw / size-adjusted power} & \\multicolumn{%d}{c}{Adjusted $-$ (ii), pp ($p$)} \\\\" % (k1, k2),
            "\\cmidrule(lr){4-%d}\\cmidrule(lr){%d-%d}" % (3 + k1, 4 + k1, 3 + k1 + k2),
            "Errors & $\\rho$ & Case & " + " & ".join(lab[a] for a, _ in ARMS) + " & " + " & ".join(lab[a] for a in boot) + " \\\\"]
    note = ("$n = %d$, $%d$ paths per cell. Size-adjusted threshold: $5\\%%$ quantile of the $p$-value (of MZ$_t$-GLS for (i) and "
            "(ii)) in the null cell with the same errors, $n$ and case. $p$: exact two-sided McNemar test on the adjusted decisions, "
            "paired over paths.\n" % (power_n(b1), b1["config"]["N_power"]))
    return tabular("lrl" + "c" * (k1 + k2), head, rows, groups), note


def fixedb_rows(b3, a12):
    size_a12 = a12["size"]
    nz = [k for k, v in size_a12.items() if v["err_tag"] != "ma_0"]
    src = {"andrews": "gls_t0", "b": "glsb_t0"}
    out = {}
    for key, _ in FB_ROWS:
        if key in src:
            rates = {k: size_a12[k]["iid"][src[key]]["rate"] for k in size_a12}
            pw = {r: b3["power"]["pw3_rho%s_n200_c" % r]["rates"][src[key]]["rate"] for r in POW_RHO}
            origin = {"size": "%s size.<celda>.iid.%s.rate (A12)" % (SRC_A12, src[key]),
                      "power": "%s power.<celda>.rates.%s.rate (A15, familia 157)" % (SRC_B3, src[key])}
        else:
            rates = {k: v["rates"][key]["rate"] for k, v in b3["size"].items()}
            pw = {r: b3["power"]["pw3_rho%s_n200_c" % r]["rates"][key]["rate"] for r in POW_RHO}
            origin = {"size": "%s size.<celda>.rates.%s.rate" % (SRC_B3, key), "power": "%s power.<celda>.rates.%s.rate" % (SRC_B3, key)}
        dev = [abs(rates[k] - C.ALPHA) for k in nz]
        out[key] = {"min": min(rates.values()), "max": max(rates.values()), "D": sum(dev) / len(dev), "M": max(dev),
                    "power": pw, "origin": origin, "cells": len(rates), "cells_psi_nonzero": len(nz)}
    return out


def tab_fixedb(b3, a12):
    fr = fixedb_rows(b3, a12)
    rows = [[lab, f(fr[k]["min"], 3), f(fr[k]["max"], 3), f(fr[k]["D"], 4), f(fr[k]["M"], 4)] + [f(fr[k]["power"][r], 3) for r in POW_RHO]
            for k, lab in FB_ROWS]
    head = ["& \\multicolumn{4}{c}{Size, serially correlated errors} & \\multicolumn{3}{c}{Size-adjusted power} \\\\",
            "\\cmidrule(lr){2-5}\\cmidrule(lr){6-8}",
            "Long-run variance & min & max & $D$ & $M$ & $\\rho = 0.80$ & $\\rho = 0.90$ & $\\rho = 0.95$ \\\\"]
    note = ("Size over the %d cells of \\cref{tab:serial}; $D$ and $M$: mean and maximum of $|\\text{size} - 0.05|$ over the %d cells "
            "with serially correlated errors. Power: AR(1) with iid errors, $n = 200$, constant case, %d paths, critical values "
            "simulated under iid errors (%d paths). Fixed-$b$: Bartlett with $B = \\lceil b n\\rceil$; LLSW: $B = \\lceil 1.3 n^{1/2}\\rceil - 1$ "
            "(Lazarus, Lewis, Stock and Watson, 2018, eq.~(3)). The size of \\RMGLS{} with the Andrews bandwidth and of (b) is taken from "
            "\\cref{tab:serial} ($%d$ paths per cell); all other entries use independent paths ($%d$ per cell).\n" % (
                fr["andrews"]["cells"], fr["andrews"]["cells_psi_nonzero"], b3["config"]["N_power"], b3["config"]["N_cal"],
                next(iter(a12["size"].values()))["iid"]["gls_t0"]["n"], b3["config"]["N_size"]))
    return tabular("lccccccc", head, rows, ["x"] * len(rows)), note, fr


def tab_fixedb_size(b3, errors, cases):
    rows, groups = [], []
    for k, v in sorted_cells(b3["size"], errors, cases):
        e = err_of(v["err_tag"], errors)
        rows.append([T13.err_tex(e), "%d" % v["n"], T13.CASE[v["case"]]] +
                    [TB.bold(f(v["rates"][c]["rate"], 3), not v["rates"][c]["in_region"]) for c in FB_CONFIGS])
        groups.append(v["err_tag"])
    head = ["Errors & $n$ & Case & " + " & ".join(FB_LABEL[c] for c in FB_CONFIGS) + " \\\\"]
    reg = b3["exact_region_20000"]
    note = ("Rejection rates of \\RMGLS{} with a fixed Bartlett bandwidth, nominal level $0.05$, $%d$ paths per cell, critical values "
            "simulated under iid errors ($%d$ paths per $n$). Bold: outside the exact region $[%s, %s]$.\n" % (
                b3["config"]["N_size"], b3["config"]["N_cal"], bound(reg[0]), bound(reg[1])))
    return tabular("lrl" + "c" * len(FB_CONFIGS), head, rows, groups), note


# B15.9.1 (enmienda 5, lectura 9.1): (etiqueta, critical value, fuente, clave)
SUM_ROWS = (("\\RMGLS{}", "Andrews", "a12", "gls_t0"), ("\\RMGLS{}", "fixed-$b$, $b = 0.3$", "b3", "b=0.3"),
            ("MSB-GLS", "iid", "a12", "msb"), ("MZ$_t$-GLS", "asymptotic", "b1", "i"), ("MZ$_t$-GLS", "iid", "b1", "ii"),
            ("MZ$_t$-GLS", "SB (bootUR)", "b1", "iii"), ("MZ$_t$-GLS", "SWB (bootUR)", "b1", "v_prime"), ("MZ$_t$-GLS", "AWB", "b1", "iv"),
            ("DF-GLS", "iid", "a12", "dfgls"), ("ADF", "iid", "a12", "adf"))
SUM_POWER = {"a12": "pwr_ma_0_rho0p9_n200_c", "b3": "pw3_rho0p9_n200_c", "b1": "pw1_ma_0_rho0p9_n200_c"}
SUM_AUDIT = {"a12": "A12", "b3": "A15", "b1": "A15"}
SUM_FILE = {"a12": SRC_A12, "b3": SRC_B3, "b1": SRC_B1}
DASH = "--"


def summary_rows(b1, b3, a12):
    """Una entrada por fila de tab_summary: tamano sobre 36 celdas, D y M sobre las 30 con psi != 0, celdas iid dentro de la
    region exacta de su N y potencia ajustada en rho = 0.90, n = 200, caso constante, errores iid (None si no existe)."""
    out = []
    for lab, cv, src, key in SUM_ROWS:
        if src == "a12":
            size = {k: v["iid"][key] for k, v in a12["size"].items()}
            tags = {k: v["err_tag"] for k, v in a12["size"].items()}
            reg = a12["exact_region_20000"]
            pw = a12["power"].get(SUM_POWER[src], {}).get("adjusted", {}).get(key)
            ppath = "%s power.%s.adjusted.%s" % (SRC_A12, SUM_POWER[src], key)
            spath = "%s size.<celda>.iid.%s" % (SRC_A12, key)
        elif src == "b3":
            size = {k: v["rates"][key] for k, v in b3["size"].items()}
            tags = {k: v["err_tag"] for k, v in b3["size"].items()}
            reg = b3["exact_region_20000"]
            pw = b3["power"].get(SUM_POWER[src], {}).get("rates", {}).get(key)
            ppath = "%s power.%s.rates.%s" % (SRC_B3, SUM_POWER[src], key)
            spath = "%s size.<celda>.rates.%s" % (SRC_B3, key)
        else:
            size = {k: v["rates"][key] for k, v in b1["size"].items()}
            tags = {k: v["err_tag"] for k, v in b1["size"].items()}
            reg = b1["exact_region"]
            pw = b1["power"].get(SUM_POWER[src], {}).get("adjusted", {}).get(key)
            ppath = "%s power.%s.adjusted.%s" % (SRC_B1, SUM_POWER[src], key)
            spath = "%s size.<celda>.rates.%s" % (SRC_B1, key)
        nz = [k for k in size if tags[k] != "ma_0"]
        iid = [k for k in size if tags[k] == "ma_0"]
        dev = [abs(size[k]["rate"] - C.ALPHA) for k in nz]
        ns = {v["n"] for v in size.values()}
        out.append({"label": lab, "cv": cv, "audit": SUM_AUDIT[src], "size_source": spath, "N_size": ns.pop() if len(ns) == 1 else sorted(ns),
                    "region": reg, "cells": len(size), "cells_psi_nonzero": len(nz), "D": sum(dev) / len(dev), "M": max(dev),
                    "min": min(v["rate"] for v in size.values()), "max": max(v["rate"] for v in size.values()),
                    "iid_in_region": sum(1 for k in iid if size[k]["in_region"]), "iid_cells": len(iid),
                    "power": None if pw is None else pw["rate"], "N_power": None if pw is None else pw["n"],
                    "power_source": ppath if pw is not None else None})
    return out


def tab_summary(b1, b3, a12):
    sr = summary_rows(b1, b3, a12)
    rows = [[r["label"], r["cv"], f(r["D"], 4), f(r["M"], 4), f(r["min"], 3), f(r["max"], 3),
             "%d/%d" % (r["iid_in_region"], r["iid_cells"]), DASH if r["power"] is None else f(r["power"], 3)] for r in sr]
    head = ["& & \\multicolumn{5}{c}{Size} & \\\\", "\\cmidrule(lr){3-7}",
            "Test & Critical value & $D$ & $M$ & min & max & iid in region & Power \\\\"]
    groups = [r["label"] for r in sr]
    by_n = {}
    for r in sr:
        by_n.setdefault(r["N_size"], r["region"])
    n_rows = {}
    for i, r in enumerate(sr, 1):
        n_rows.setdefault((r["audit"], r["N_size"]), []).append(i)
    pw_groups = {}
    for i, r in enumerate(sr, 1):
        pw_groups.setdefault((r["audit"], r["N_power"], r["power_source"].split(" ")[0] if r["power_source"] else None), []).append(i)
    missing = [i for i, r in enumerate(sr, 1) if r["power"] is None]

    def rows_txt(ix):
        return ("row " if len(ix) == 1 else "rows ") + ", ".join("%d" % i for i in ix)
    size_txt = "; ".join("%s: %s, $%d$ paths per cell" % (rows_txt(ix), a, n) for (a, n), ix in n_rows.items())
    reg_txt = "; ".join("$[%s, %s]$ for $%d$ paths" % (bound(reg[0]), bound(reg[1]), n)
                        for n, reg in sorted(by_n.items(), reverse=True))
    pw_desc = {SRC_A12: "size-adjusted in the null cell with the same errors, $n$ and case",
               SRC_B3: "critical values simulated under iid errors ($%d$ paths per $n$), no further size adjustment" % b3["config"]["N_cal"],
               SRC_B1: "size-adjusted in the null cell with the same errors, $n$ and case"}
    pw_txt = "; ".join("%s: %s, $%d$ paths, %s" % (rows_txt(ix), a, n, pw_desc[s]) for (a, n, s), ix in pw_groups.items()
                       if s is not None)
    note = ("Nominal level $0.05$. $D$ and $M$: mean and maximum of $|\\text{size} - 0.05|$ over the %d cells with serially "
            "correlated errors; min and max over all %d cells; iid in region: cells with iid errors whose rejection rate lies in the "
            "exact binomial region of its number of paths (%s). Size: %s. Power: AR(1) with $\\rho = 0.90$, iid errors, $n = 200$, "
            "constant case; %s. The three power experiments use different paths.%s\n" % (
                sr[0]["cells_psi_nonzero"], sr[0]["cells"], reg_txt, size_txt, pw_txt,
                "" if not missing else " %s: power not measured in this cell (--)." % rows_txt(missing).capitalize()))
    return tabular("llcccccc", head, rows, groups), note, sr


def main():
    b1, b3, a12 = C.read_json(SRC_B1), C.read_json(SRC_B3), C.read_json(SRC_A12)
    errors, cases = order()
    prov = C.provenance(__file__)
    outs = {}

    def put(name, tex, note, src):
        p = os.path.join(C.TABLES, name + ".tex")
        q = os.path.join(C.TABLES, name.replace("_audit15", "_note_audit15") + ".tex")
        C.write_text(p, header(src) + tex, __file__, prov)
        C.write_text(q, header(src) + note, __file__, prov)
        outs[C.rel(p)] = C.sha256_file(p)
        outs[C.rel(q)] = C.sha256_file(q)
    t, n = tab_boot(b1, errors, cases)
    put("tab_boot_audit15", t, n, SRC_B1)
    t, n = tab_bootpower(b1, errors, cases)
    put("tab_bootpower_audit15", t, n, SRC_B1)
    t, n, fr = tab_fixedb(b3, a12)
    put("tab_fixedb_audit15", t, n, "%s y %s" % (SRC_B3, SRC_A12))
    t, n = tab_fixedb_size(b3, errors, cases)
    put("tab_fixedb_size_audit15", t, n, SRC_B3)
    t, n, sr = tab_summary(b1, b3, a12)
    put("tab_summary_audit15", t, n, "%s, %s y %s" % (SRC_A12, SRC_B3, SRC_B1))
    out = {"provenance": prov, "reading": "enmienda 4, lecturas 6.1-6.6; enmienda 5, lectura 9.1 (tab_summary)",
           "summary_rows": sr,
           "sources": {k: {"file": k, "sha256": C.sha256_file(os.path.join(C.RESULTS, k))} for k in (SRC_B1, SRC_B3, SRC_A12)},
           "outputs": outs, "rounding": "binary", "fixedb_rows": fr,
           "column_sources": {k: v["origin"] for k, v in fr.items()}}
    C.write_result(OUT, out, __file__)
    for k, v in outs.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
