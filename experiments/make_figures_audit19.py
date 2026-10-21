"""
Auditoria A19 - punto 1 (protocol_audit19.md, L1): Figura 1 (fig:calibgain) en caminos comunes.

Los tres trazos salen solo de e_calib_audit13.json (cases_by_theta.gls_t0, 2x10^4 caminos comunes por celda), la misma fuente
que la Tabla 1 (audit13_tables.build_calib):
  cv_at_n  <- approximation_cost.<n>.size_with_cv_at_n                              (Tabla 1: «at q(n)»)
  cv_big   <- approximation_cost.<n>.size_with_cv_n20000                            (Tabla 1: «at q(20 000)»)
  msb_pub  <- approximation_cost_comparators.<n>.msb.size_published_asymptotic      (Tabla 1: MSB-GLS «asy.»)
Se dibuja con make_figures_audit11.fig_calibration_gain sin modificarlo y con la etiqueta «MSB-B» (como make_figures_audit13q).
Si falta algun n de F.GAIN_N, se detiene sin dibujar (L1.1). Las fechas del PDF se quitan (E8.3 de A18).

Salidas: experiments/figures/fig_calibration_gain_audit19.pdf, experiments/results/figures_audit19.json.
"""
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402
import numpy as np                                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit19_common as C                                         # noqa: E402
import audit11_figconfig as F                                      # noqa: E402
import make_figures_audit10 as M10                                 # noqa: E402
import make_figures_audit11 as M11                                 # noqa: E402

SRC = "e_calib_audit13.json"
PRIM = "gls_t0"
LABEL = "MSB-B"
NAME = "fig_calibration_gain_audit19.pdf"
OUT = os.path.join(C.RESULTS, "figures_audit19.json")
TABLE1 = os.path.join(C.RESULTS, "tables_audit13", "tab_calib_audit13.tex")
TRACES = (("cv_at_n", "approximation_cost", "size_with_cv_at_n", 2),
          ("cv_big", "approximation_cost", "size_with_cv_n20000", 3),
          ("msb_pub", "approximation_cost_comparators", "msb.size_published_asymptotic", 6))
CASE_DET = dict(M11.CASES)            # {"dm": "c", "ct": "ct"}
CASE_ROW = {"c": "Constant", "ct": "Trend"}


def dig(d, dotted):
    for k in dotted.split("."):
        d = d[k]
    return d


def points():
    fin = C.read_json(SRC)["cases_by_theta"][PRIM]
    missing = [(det, n, block) for det in CASE_DET.values() for n in F.GAIN_N for _, block, _, _ in TRACES
               if str(n) not in fin[det][block]]
    if missing:
        raise SystemExit("e_calib_audit13.json no cubre %s: se detiene sin dibujar (L1.1)" % missing)
    out = {}
    for case, det in M11.CASES:
        pts = {}
        for key, block, field, _ in TRACES:
            pts[key] = {}
            for n in F.GAIN_N:
                rec = dig(fin[det][block][str(n)], field)
                path = "cases_by_theta.%s.%s.%s.%d.%s" % (PRIM, det, block, n, field)
                pts[key][n] = M10.point(rec, rec["n"], SRC, path)
        out[case] = pts
    return out


def table1():
    """Celdas impresas de la Tabla 1, {det: {n: [8 columnas como texto]}}."""
    rows, det = {}, None
    for line in open(TABLE1, encoding="utf-8").read().splitlines():
        if "\\emph{Constant}" in line:
            det = "c"
        elif "\\emph{Trend}" in line:
            det = "ct"
        elif det and re.match(r"^\d+ &", line):
            cells = [re.sub(r"\\textbf\{([^}]*)\}", r"\1", c).strip() for c in line.rstrip("\\ ").split("&")]
            rows.setdefault(det, {})[int(cells[0])] = cells
    return rows


def main():
    os.makedirs(C.FIGURES, exist_ok=True)
    pts = points()
    path = os.path.join(C.FIGURES, NAME)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    saved = F.PRIMARY_LABEL
    F.PRIMARY_LABEL = LABEL
    try:
        with M11.recording() as rec:
            M11.fig_calibration_gain(pts, path)
    finally:
        F.PRIMARY_LABEL = saved
    # lo dibujado: cada plot de un trazo debe ser exactamente la lista de tasas del JSON
    plotted = [arrs for kind, arrs in rec.calls if kind == "plot"]
    expected = [np.asarray([pts[case][key][n]["rate"] for n in sorted(pts[case][key])], dtype=float)
                for case, _ in M11.CASES for key, _, _, _ in TRACES]
    plotted_ok = len(plotted) == len(expected) and all(np.array_equal(np.asarray(p[1], dtype=float), e)
                                                       for p, e in zip(plotted, expected))
    dates = C.strip_pdf_dates(path)
    # tabla viejo/nuevo y comparacion con la Tabla 1 al digito impreso (P1)
    old = C.read_json("figures_audit13.json")["calibration_gain_points"]
    t1 = table1()
    rows, p1 = [], True
    for case, det in M11.CASES:
        for key, _, _, col in TRACES:
            for n in F.GAIN_N:
                new = pts[case][key][n]
                o = old[case][key][str(n)]
                printed = t1[det][n][col]
                match = "%.4f" % new["rate"] == printed
                p1 = p1 and match
                rows.append({"case": det, "trace": key, "n": n, "old_rate": o["rate"], "old_N": o["N"], "old_source": o["source"],
                             "old_path": o["path"], "new_rate": new["rate"], "new_N": new["N"], "new_path": new["path"],
                             "new_region": new["region"], "delta_pp": (new["rate"] - o["rate"]) * 100,
                             "table1_printed": printed, "table1_column": col, "matches_table1": match})
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit19.md, L1",
           "source": "experiments/results/" + SRC, "primary": PRIM, "label": LABEL, "n_grid": list(F.GAIN_N),
           "traces": {k: {"block": b, "field": f, "table1_column": c} for k, b, f, c in TRACES},
           "table1": C.rel(TABLE1), "table1_sha256": C.sha256_file(TABLE1),
           "figure": {"path": C.rel(path), "sha256": C.sha256_file(path), "bytes": os.path.getsize(path),
                      "data_sha256": M11.digest(rec.calls), "plotted_equal_json": bool(plotted_ok), "pdf_dates": dates},
           "points": {case: {k: {str(n): v for n, v in d.items()} for k, d in pp.items()} for case, pp in pts.items()},
           "old_vs_new": rows, "n_points": len(rows), "n_sources_new": len({r["new_path"].split(".")[0] for r in rows}),
           "old_sources": sorted({r["old_source"] for r in rows}),
           "p1_all_match_table1": bool(p1), "n_match_table1": sum(r["matches_table1"] for r in rows)}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, [path], out["provenance"])
    print("puntos:", len(rows), "| coinciden con la Tabla 1:", out["n_match_table1"], "| P1:", p1, "| dibujado == JSON:", plotted_ok,
          "| fechas PDF:", dates["ok"])
    return 0 if (p1 and plotted_ok and dates["ok"]) else 1


if __name__ == "__main__":
    sys.exit(main())
