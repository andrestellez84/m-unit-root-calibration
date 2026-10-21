"""
A19, P1 (protocol_audit19.md, L1): cada punto de la Figura 1 nueva coincide con la celda de la Tabla 1 al digito impreso.

Camino independiente del generador: se leen e_calib_audit13.json y tab_calib_audit13.tex directamente, sin los helpers de
make_figures_audit19, y se comparan con los puntos registrados en figures_audit19.json.
"""
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "experiments", "results")
NS = (60, 100, 150, 200, 500, 1000, 2000, 5000)
# columna de la Tabla 1 (0 = n) y campo de e_calib_audit13.json de cada trazo
TRACES = {"cv_at_n": (2, ("approximation_cost", "size_with_cv_at_n")),
          "cv_big": (3, ("approximation_cost", "size_with_cv_n20000")),
          "msb_pub": (6, ("approximation_cost_comparators", "msb", "size_published_asymptotic"))}
CASES = {"dm": "c", "ct": "ct"}


def load(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        pytest.skip("%s aun no existe" % name)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def table1():
    rows, det = {}, None
    with open(os.path.join(RES, "tables_audit13", "tab_calib_audit13.tex"), encoding="utf-8") as f:
        for line in f:
            if "Constant" in line:
                det = "c"
            elif "Trend" in line:
                det = "ct"
            elif det and re.match(r"^\d+ &", line):
                cells = [c.replace("\\textbf{", "").replace("}", "").strip() for c in line.strip().rstrip("\\").split("&")]
                rows.setdefault(det, {})[int(cells[0])] = cells
    return rows


def test_every_point_matches_table1_printed_digit():
    fig = load("figures_audit19.json")["points"]
    t1 = table1()
    checked = 0
    for case, det in CASES.items():
        for key, (col, _) in TRACES.items():
            for n in NS:
                assert "%.4f" % fig[case][key][str(n)]["rate"] == t1[det][n][col], (case, key, n)
                checked += 1
    assert checked == 48


def test_points_come_only_from_e_calib():
    fig = load("figures_audit19.json")
    src = load("e_calib_audit13.json")["cases_by_theta"]["gls_t0"]
    for case, det in CASES.items():
        for key, (_, path) in TRACES.items():
            for n in NS:
                p = fig["points"][case][key][str(n)]
                rec = src[det][path[0]][str(n)]
                for k in path[1:]:
                    rec = rec[k]
                assert p["source"] == "experiments/results/e_calib_audit13.json"
                assert p["rate"] == rec["rate"] and p["N"] == rec["n"] == 20000


def test_figure_is_the_registered_one_and_has_no_dates():
    fig = load("figures_audit19.json")
    assert fig["figure"]["plotted_equal_json"] and fig["figure"]["pdf_dates"]["ok"] and fig["p1_all_match_table1"]
    pdf = os.path.join(ROOT, fig["figure"]["path"])
    if not os.path.exists(pdf):
        pytest.skip("la figura no esta en esta copia")
    import hashlib
    with open(pdf, "rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == fig["figure"]["sha256"]
