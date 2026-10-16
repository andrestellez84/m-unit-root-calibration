"""
Auditoria A14 - B14.1: exportador del CSV y del tabular de valores criticos de MSB-GLS y
MZ_t-GLS (protocol_audit14.md, lectura 7). Solo lee b1_critical_audit14.json; lo recorre
tests/test_no_literals_audit14.py.

Salidas (experiments/results/tables_audit14/):
  - crit_msb_mzt_audit14.csv: una fila por valor critico, con su EE bootstrap exacto;
  - tab_critMSB_audit14.tex: disposicion de tab:critB, paneles MSB-GLS (4 decimales) y
    MZ_t-GLS (3 decimales), redondeo binario;
  - tab_critMSB_note_audit14.tex: fragmento de nota (N_cal y EE maximo por estadistico,
    redondeado hacia arriba a dos cifras significativas).
y experiments/results/tables_audit14.json con los sha256 y las cifras de la nota.
"""
import csv
import decimal
import io
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402

SRC = "b1_critical_audit14.json"
OUT_JSON = os.path.join(C.RESULTS, "tables_audit14.json")
CSV = os.path.join(C.TABLES, "crit_msb_mzt_audit14.csv")
TEX = os.path.join(C.TABLES, "tab_critMSB_audit14.tex")
NOTE = os.path.join(C.TABLES, "tab_critMSB_note_audit14.tex")
DECIMALS = {"msb": 4, "mzt": 3}
PANEL = {"msb": "MSB-GLS", "mzt": "MZ$_t$-GLS"}
CASE_HEAD = {"c": "Constant", "ct": "Trend"}
SIG = 2                                            # cifras significativas de la cota del EE en la nota


def level_label(a):
    s = repr(float(a))
    d = max(2, len(s.split(".")[1]))
    return "$" + TB.fdec(a, d, "binary") + "$"


def signed(s):
    """Signo menos tipografico, como en tab:attrib (B13.Q Q1)."""
    return "$-$" + s[1:] if s.startswith("-") else s


def ceil_sig(x, sig=SIG):
    """x redondeado hacia arriba a sig cifras significativas (texto decimal)."""
    e = int(math.floor(math.log10(abs(x)))) - sig + 1
    q = decimal.Decimal(1).scaleb(e)
    return str(decimal.Decimal(repr(float(x))).quantize(q, rounding=decimal.ROUND_CEILING))


def tex_power(N):
    e = int(round(math.log10(N)))
    m = N / 10 ** e
    while m != int(m) or m >= 10:
        e -= 1
        m = N / 10 ** e
    return "%d\\times10^{%d}" % (int(m), e) if int(m) != 1 else "10^{%d}" % e


def build_tex(d):
    cfg = d["config"]
    levels, cases, ns = cfg["levels"], cfg["cases"], cfg["n"]
    V = {(v["stat"], v["case"], v["n"], v["alpha"]): v for v in d["values"]}
    k = len(levels)
    ncol = 1 + k * len(cases)
    L = ["% Generado por experiments/audit14_tables.py desde " + SRC + " (no editar a mano)",
         "\\begin{tabular}{r" + "c" * (ncol - 1) + "}", "\\toprule",
         "& " + " & ".join("\\multicolumn{%d}{c}{%s}" % (k, CASE_HEAD[c]) for c in cases) + "\\\\",
         "".join("\\cmidrule(lr){%d-%d}" % (2 + i * k, 1 + (i + 1) * k) for i in range(len(cases))),
         "$n$ & " + " & ".join(level_label(a) for _ in cases for a in levels) + "\\\\"]
    for s in cfg["stats"]:
        L.append("\\midrule")
        L.append("\\multicolumn{%d}{l}{\\emph{%s}}\\\\" % (ncol, PANEL[s]))
        for n in ns:
            cells = [signed(TB.fdec(V[(s, c, n, a)]["critical_value"], DECIMALS[s], "binary")) for c in cases for a in levels]
            L.append("%d & " % n + " & ".join(cells) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def note_values(d):
    return {s: max(v["bootstrap_se"] for v in d["values"] if v["stat"] == s) for s in d["config"]["stats"]}


def build_note(d):
    mx = note_values(d)
    N = d["config"]["N_cal"]
    return ("% Generado por experiments/audit14_tables.py desde " + SRC + " (no editar a mano)\n"
            "Lower-tail critical values: $H_0$ is rejected at level $\\alpha$ when the statistic is below $q_\\alpha$. "
            "Each entry is the empirical quantile, with linear interpolation, of $\\ncal = %s$ paths simulated under "
            "\\cref{eq:null}, with the lag chosen in each path by the MAIC of Ng and Perron on GLS residuals. Exact "
            "bootstrap standard errors are at most $%s$ for MSB-GLS and $%s$ for MZ$_t$-GLS; the machine-readable file "
            "gives each value with its standard error.\n" % (tex_power(N), ceil_sig(mx["msb"]), ceil_sig(mx["mzt"])))


def build_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["statistic", "case", "n", "alpha", "critical_value", "bootstrap_se", "maritz_jarrett_se", "N_cal", "nan",
                "sample_file", "sample_sha256"])
    for v in sorted(d["values"], key=lambda v: (v["stat"], v["case"], v["n"], v["alpha"])):
        w.writerow([v["stat_label"], v["case"], v["n"], repr(v["alpha"]), repr(v["critical_value"]), repr(v["bootstrap_se"]),
                    repr(v["se_maritz_jarrett"]), v["N_cal"], v["nan"], v["sample"], d["samples"][str(v["n"])]["sha256"]])
    return buf.getvalue()


def main():
    d = C.read_json(SRC)
    prov = C.provenance(__file__, seed_family=None)
    C.write_text(TEX, build_tex(d), __file__, prov)
    C.write_text(NOTE, build_note(d), __file__, prov)
    C.write_text(CSV, build_csv(d), __file__, prov)
    mx = note_values(d)
    out = {"provenance": prov, "reading": "protocol_audit14.md, lectura 7", "source": SRC,
           "source_sha256": C.sha256_file(os.path.join(C.RESULTS, SRC)),
           "outputs": {C.rel(p): C.sha256_file(p) for p in (TEX, NOTE, CSV)},
           "decimals": DECIMALS, "rounding": "binary",
           "note": {"max_bootstrap_se": mx, "printed_bound": {s: ceil_sig(x) for s, x in mx.items()},
                    "N_cal_tex": tex_power(d["config"]["N_cal"])},
           "csv_rows": len(d["values"])}
    C.write_result(OUT_JSON, out, __file__)
    print(build_tex(d))
    print(build_note(d))
    print(out["outputs"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
