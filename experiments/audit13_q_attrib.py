"""
Auditoria A13 - B13.Q, Q1: tab:attrib exportado desde bB_attrib_audit12.json.

Solo lee JSON (protocol_audit13_amend1.md, lectura 3). La disposicion (filas,
columnas y cabecera) es la del bloque TRANSCRIBED de v14/sec5_montecarlo.tex:
  (a) gls_t0, (b) glsb_t0, (b') glsbp_t0, (c) MSB-GLS asintotico; diferencias
  (a)-(b'), (b')-(b), (b')-(c) en pp; filas rho a n = 200 (dgp1_rho<rho>_n200),
  medias by_n con EE pareada y potencia local lp_dm_c<c>.
La nota lleva las medias de (a)-(b) con EE y de (b)-(c) sin EE.
Se prueban las dos convenciones de redondeo de A13 y se usa la que reproduce el
v14; toda celda distinta se lista.
Paso 0 (lectura 1 de la enmienda): tasas = rejections / n (|Delta| = 0);
diferencias = diferencia de tasas y medias by_n = media de las celdas, con
|Delta| <= 1e-12 declarado.

Salidas: tables_audit13/tab_attrib_audit13.tex, tab_attrib_note_audit13.tex,
experiments/results/q_attrib_audit13.json.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402
import audit13_q_common as Q                                       # noqa: E402

SRC = "bB_attrib_audit12.json"
OUT = os.path.join(C.RESULTS, "q_attrib_audit13.json")
TEX = os.path.join(C.TABLES, "tab_attrib_audit13.tex")
NOTE = os.path.join(C.TABLES, "tab_attrib_note_audit13.tex")
RATES = ("a", "b", "bp", "c")
DIFFS = ("a_minus_bp", "bp_minus_b", "bp_minus_c")
TOL = 10 ** -12
MEAN_ROWS = {"Constant": "c", "Trend": "ct"}


def signed(x, d=2):
    s = "%+.*f" % (d, x) if TB.ROUNDING["mode"] == "binary" else ("+" if x >= 0 else "-") + TB.fdec(abs(x), d)
    return "$-$" + s[1:] if s.startswith("-") else s


def f2(x):
    return TB.fdec(x, 2)


def build(rows, b):
    cells, vals, keys = [], [], []
    for _, _, k, _ in rows:
        key = TB.norm(k[0])[1]
        if key.startswith("\\rho="):
            name = "dgp1_rho%s_n200" % TB.rtag(TB.num(key))
            c = b["cells"][name]
            cells.append([TB.f3(c["rates"][v]["rate"]) for v in RATES] + [signed(c["diffs"][d]["delta"] * C.PP) for d in DIFFS])
            vals.append([c["rates"][v]["rate"] for v in RATES] + [c["diffs"][d]["delta"] * C.PP for d in DIFFS])
        elif key.startswith("c="):
            name = "lp_dm_c%g" % TB.num(key)
            c = b["cells"][name]
            cells.append([TB.f3(c["rates"][v]["rate"]) for v in RATES] + [signed(c["diffs"][d]["delta"] * C.PP) for d in DIFFS])
            vals.append([c["rates"][v]["rate"] for v in RATES] + [c["diffs"][d]["delta"] * C.PP for d in DIFFS])
        else:
            m = re.match(r"(Constant|Trend),n=(\d+)\((\d+)\)", key)
            name = "%s|%s" % (MEAN_ROWS[m.group(1)], m.group(2))
            v = b["by_n"][name]
            if v[DIFFS[0]]["k"] != int(m.group(3)):
                raise ValueError("k de %s: %d en el JSON, %s en el v14" % (name, v[DIFFS[0]]["k"], m.group(3)))
            cells.append([""] * len(RATES) + ["%s (%s)" % (signed(v[d]["mean"] * C.PP), f2(v[d]["se"] * C.PP)) for d in DIFFS])
            vals.append([None] * len(RATES) + [v[d]["mean"] * C.PP for d in DIFFS])
        keys.append(name)
    return cells, vals, keys


def note(b):
    ab = [b["by_n"][k]["a_minus_b"] for k in ("c|200", "c|500", "c|1000", "ct|200", "ct|500")]
    bc = [b["by_n"][k]["b_minus_c"] for k in ("c|200", "c|500", "c|1000", "ct|200", "ct|500")]

    def p(x):
        return "$%s$" % f2(x["mean"] * C.PP)

    def pse(x):
        return "%s (%s)" % (p(x), f2(x["se"] * C.PP))
    text = ("Power at $n = 200$\nand $500$: 5000 common paths per cell; local power: $2\\times10^4$ paths.\n"
            "PQ: lag selected on OLS-detrended data \\citep{perron2007simple}.\n"
            "Differences in percentage points; standard errors are for paired\n"
            "differences. Means of (a)$-$(b): %s, %s and %s in the constant case at $n = 200$, $500$ and $1000$; "
            "%s and %s in the trend case at $n = 200$ and $500$. Means of\n(b)$-$(c): %s, %s and %s; %s and %s.\n"
            % tuple([pse(x) for x in ab] + [p(x) for x in bc]))
    nums = [x["mean"] * C.PP for x in ab] + [x["se"] * C.PP for x in ab] + [x["mean"] * C.PP for x in bc]
    return text, nums


def note_numbers_v14(v):
    t = v.files["sec5_montecarlo.tex"]
    i = t.find("\\label{tab:attrib}")
    j = t.find("\\begin{minipage}", i)
    k = t.find("\\end{minipage}", j)
    block = t[j:k]
    s = re.sub(r"\s+", " ", block[block.find("Means of (a)"):])
    means_ab = re.findall(r"\$([0-9.]+)\$ \(([0-9.]+)\)", s.split("Means of")[1])
    means_bc = re.findall(r"\$([0-9.]+)\$", s.split("Means of")[2])
    return {"a_minus_b": means_ab, "b_minus_c": means_bc, "text": block}


def paso0(b):
    rate_diff, diff_cons, mean_cons, which = 0.0, 0.0, 0.0, []
    pairs = {"a_minus_bp": ("a", "bp"), "bp_minus_b": ("bp", "b"), "bp_minus_c": ("bp", "c"), "a_minus_b": ("a", "b"),
             "b_minus_c": ("b", "c")}
    for name, c in b["cells"].items():
        for v in RATES:
            r = c["rates"][v]
            rate_diff = max(rate_diff, abs(r["rate"] - r["rejections"] / r["n"]))
        for d, (x, y) in pairs.items():
            e = abs(c["diffs"][d]["delta"] - (c["rates"][x]["rate"] - c["rates"][y]["rate"]))
            if e > 0:
                which.append(["%s.diffs.%s" % (name, d), e])
            diff_cons = max(diff_cons, e)
    for k, v in b["by_n"].items():
        for d in pairs:
            m = sum(b["cells"][c]["diffs"][d]["delta"] for c in v["cells"]) / len(v["cells"])
            e = abs(m - v[d]["mean"])
            if e > 0:
                which.append(["by_n.%s.%s.mean" % (k, d), e])
            mean_cons = max(mean_cons, e)
    return {"rates_vs_rejections_over_n": rate_diff, "diff_vs_rate_difference": diff_cons, "by_n_mean_vs_cells": mean_cons,
            "nonzero_other_columns": which, "tolerance_other_columns": TOL,
            "passes": rate_diff == 0 and diff_cons <= TOL and mean_cons <= TOL}


def main():
    v = Q.V14()
    b = C.read_json(SRC)
    fname, tab = v.tabular("attrib")
    chunks, rows = TB.data_rows(tab, 1)
    trials = {}
    for mode in TB.MODES:
        TB.ROUNDING["mode"] = mode
        cells, vals, keys = build(rows, b)
        trials[mode] = (TB.transcription(rows, cells, vals), cells, vals, keys)
    mode = min(TB.MODES, key=lambda m: (len(trials[m][0]["number_mismatches"]) + len(trials[m][0]["double_rounding_in_v13"]),
                                        TB.MODES.index(m)))
    TB.ROUNDING["mode"] = mode
    tr, cells, vals, keys = trials[mode]
    text, note_vals = note(b)
    nv = note_numbers_v14(v)
    printed_note = [x for x, _ in nv["a_minus_b"]] + [y for _, y in nv["a_minus_b"]] + nv["b_minus_c"]
    mine_note = [f2(x) for x in note_vals]
    note_cmp = [{"printed": p, "mine": m, "value": x, "equal": p == m} for p, m, x in zip(printed_note, mine_note, note_vals)]
    tex = TB.rebuild(chunks, rows, cells)
    tex = "\n".join(l for l in tex.split("\n") if not l.lstrip().startswith("%"))
    prov = C.provenance(__file__, seed_family=None)
    C.write_text(TEX, "%% Generado por experiments/audit13_q_attrib.py desde experiments/results/%s (no editar a mano)\n%s\n"
                 % (SRC, tex), __file__, prov)
    C.write_text(NOTE, "%% Generado por experiments/audit13_q_attrib.py desde experiments/results/%s (no editar a mano)\n%s"
                 % (SRC, text), __file__, prov)
    p0 = paso0(b)
    out = {"provenance": prov, "manuscript": v.record(), "source": SRC,
           "source_sha256": C.sha256_file(os.path.join(C.RESULTS, SRC)), "v14_file": fname,
           "reading": "protocol_audit13_amend1.md, lectura 3", "rounding": mode,
           "rounding_trials": {m: {"number_mismatches": len(t[0]["number_mismatches"]),
                                   "double_rounding": len(t[0]["double_rounding_in_v13"])} for m, t in trials.items()},
           "rows": [{"keys": k, "json_key": jk, "section": s, "printed": p, "mine": c, "values": vv}
                    for (_, s, k, p), jk, c, vv in zip(rows, keys, cells, vals)],
           "comparison_v14": tr, "note": {"comparison": note_cmp, "all_equal": all(x["equal"] for x in note_cmp)},
           "paso0": p0, "tex": C.rel(TEX), "tex_sha256": C.sha256_file(TEX), "note_tex": C.rel(NOTE),
           "note_sha256": C.sha256_file(NOTE)}
    C.write_result(OUT, out, __file__)
    print("redondeo", mode, {m: out["rounding_trials"][m] for m in TB.MODES})
    print("tabla: %d celdas; numero %d; doble redondeo %d" % (tr["cells_compared"], len(tr["number_mismatches"]),
                                                            len(tr["double_rounding_in_v13"])))
    for m in tr["number_mismatches"] + tr["double_rounding_in_v13"]:
        print("   ", m)
    print("nota:", [(x["printed"], x["mine"]) for x in note_cmp if not x["equal"]] or "igual")
    print("Paso 0", p0)
    return 0 if p0["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
