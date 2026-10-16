"""
Auditoria A15 - exportador de tabulares (protocol_audit15.md, lectura 0.3). Solo lee JSON; lo
recorre tests/test_no_literals_audit15.py.

tab_serial_asy_audit15.tex: filas de tab:serial (error, n, caso); para MSB-GLS, MZ_t-GLS,
MSB-GLS (PQ), MZ_t-GLS (PQ) y DF-GLS, el tamano con el valor critico iid y con el asintotico,
a 3 decimales (redondeo binario); negrita fuera de la region exacta de la N de la celda, como
en tab:serial. Fuente: b0_iidasy_audit15.json (que copia bA_ma_audit12.json).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402
import audit13_t_tables as T13                                     # noqa: E402

SRC = "b0_iidasy_audit15.json"
OUT_JSON = os.path.join(C.RESULTS, "tables_audit15.json")
TEX = os.path.join(C.TABLES, "tab_serial_asy_audit15.tex")
SRC_LAG = "b0b_lag_audit15.json"
TEX_LAG = os.path.join(C.TABLES, "tab_lag_audit15.tex")
LAG_PROCS = (("mzt", "MZ$_t$-GLS"), ("msb", "MSB-GLS"))
PROCS = (("msb", "MSB-GLS"), ("mzt", "MZ$_t$-GLS"), ("msb_pq", "MSB-GLS (PQ)"), ("mzt_pq", "MZ$_t$-GLS (PQ)"), ("dfgls", "DF-GLS"))
BLOCKS = (("iid", "iid"), ("asy", "asy."))


def build(d, order):
    err_of = {T13_tag(e): e for e in order["errors"]}
    rows = sorted(d["cells"], key=lambda r: ([T13_tag(e) for e in order["errors"]].index(r["err_tag"]), r["n"],
                                             order["cases"].index(r["case"])))
    k = len(BLOCKS)
    L = ["% Generado por experiments/audit15_tables.py desde " + SRC + " (no editar a mano)",
         "\\begin{tabular}{lrl" + "c" * (k * len(PROCS)) + "}", "\\toprule",
         "& & & " + " & ".join("\\multicolumn{%d}{c}{%s}" % (k, lab) for _, lab in PROCS) + "\\\\",
         "".join("\\cmidrule(lr){%d-%d}" % (4 + i * k, 3 + (i + 1) * k) for i in range(len(PROCS))),
         "Errors & $n$ & Case & " + " & ".join(b for _ in PROCS for _, b in BLOCKS) + "\\\\", "\\midrule"]
    last = None
    for r in rows:
        if last is not None and r["err_tag"] != last:
            L.append("\\addlinespace")
        last = r["err_tag"]
        cells = [TB.bold(TB.fdec(r["rates"][p][b], 3, "binary"), not r["in_region"][p][b]) for p, _ in PROCS for b, _ in BLOCKS]
        L.append(" & ".join([T13.err_tex(err_of[r["err_tag"]]), "%d" % r["n"], T13.CASE[r["case"]]] + cells) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def cell_label(key, r, order):
    if "err_tag" in r:
        err = {T13_tag(e): e for e in order["errors"]}[r["err_tag"]]
        return "%s, $n = %d$, %s" % (T13.err_tex(err), r["n"], T13.CASE[r["case"]])
    n, case = key.split("|")
    return "iid null (A10), $n = %s$, %s" % (n, T13.CASE[case])


def fmt_rate(x):
    return "--" if x is None else TB.fdec(x, 3, "binary")


def build_lag(d, order):
    """Tamano por retardo k de la MAIC GLS: celdas de A12 y nula iid de A10 (enmienda 1, E1.8)."""
    blocks = list(d["cells"].items()) + [(k, v) for k, v in d["a10_null"].items() if v.get("executed")]
    L = ["% Generado por experiments/audit15_tables.py desde " + SRC_LAG + " (no editar a mano)",
         "\\begin{tabular}{lrr" + "cc" * len(LAG_PROCS) + "}", "\\toprule",
         "& & & " + " & ".join("\\multicolumn{2}{c}{%s}" % lab for _, lab in LAG_PROCS) + "\\\\",
         "".join("\\cmidrule(lr){%d-%d}" % (4 + 2 * i, 5 + 2 * i) for i in range(len(LAG_PROCS))),
         "Cell & $k$ & Paths & " + " & ".join("iid & asy." for _ in LAG_PROCS) + "\\\\", "\\midrule"]
    first = True
    for key, r in blocks:
        if not first:
            L.append("\\addlinespace")
        first = False
        lab = cell_label(key, r, order)
        for i, kb in enumerate(d["k_bins"]):
            by = {p: r["procs"][p]["by_k"][kb] for p, _ in LAG_PROCS}
            kl = "$\\geq 3$" if kb.startswith(">=") else kb
            cells = [fmt_rate(by[p][b]["rate"]) for p, _ in LAG_PROCS for b in ("iid", "asy")]
            L.append(" & ".join([lab if i == 0 else "", kl, "%d" % by[LAG_PROCS[0][0]]["paths"]] + cells) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def T13_tag(err):
    kind, v = err
    return "%s_%s" % (kind, ("%g" % v).replace("-", "m").replace(".", "p"))


def main():
    d = C.read_json(SRC)
    a = C.read_json(d["source"])["config"]
    order = {"errors": [tuple(e) for e in a["errors"]], "cases": list(a["cases"])}
    prov = C.provenance(__file__)
    tex = build(d, order)
    C.write_text(TEX, tex, __file__, prov)
    lag = C.read_json(SRC_LAG)
    tex_lag = build_lag(lag, order)
    C.write_text(TEX_LAG, tex_lag, __file__, prov)
    out = {"provenance": prov, "reading": "protocol_audit15.md, lectura 0.3", "source": SRC,
           "source_sha256": C.sha256_file(os.path.join(C.RESULTS, SRC)), "outputs": {C.rel(TEX): C.sha256_file(TEX)},
           "lag_table": {"source": SRC_LAG, "source_sha256": C.sha256_file(os.path.join(C.RESULTS, SRC_LAG)),
                         "output": C.rel(TEX_LAG), "sha256": C.sha256_file(TEX_LAG), "decimals": 3, "rounding": "binary",
                         "reading": "enmienda 1, E1.8"},
           "rounding": "binary", "decimals": 3, "bold": "fuera de la region exacta de 2e4 caminos (in_region de bA_ma_audit12.json)",
           "exact_region": d["exact_region_20000"]}
    C.write_result(OUT_JSON, out, __file__)
    print(tex)
    print(tex_lag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
