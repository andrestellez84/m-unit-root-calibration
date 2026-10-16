"""
A8 - regla 3 aplicada a A11: cero literales numericos de resultados en los
generadores (reporte, figuras, tabla de T2 y comprobacion de T5).

Recorre con ast los generadores y falla si encuentra un literal de punto flotante
fuera de la lista blanca de constantes de configuracion. Los enteros no se
examinan. Las constantes de maquetacion viven en experiments/audit11_figconfig.py,
que no es un generador. Incluye un control negativo del comparador de datos de
T1 (make_figures_audit11.compare debe detectar un solo valor cambiado).
"""
import ast
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("experiments/audit11_generate_report.py", "experiments/make_figures_audit11.py",
              "experiments/audit11_t2_dgp2.py", "experiments/audit11_t5_claims.py")

WHITELIST = {
    0.0, 1.0, 2.0, 0.5,                      # neutros y mitades
    0.05, 0.1, 0.02,                         # alfa y theta
    100.0,                                   # conversion a puntos porcentuales
}


def float_literals(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float) and node.value not in WHITELIST]


@pytest.mark.parametrize("rel", GENERATORS)
def test_generator_has_no_result_literals(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        pytest.skip("%s aun no existe" % rel)
    bad = float_literals(path)
    assert not bad, "literales de punto flotante fuera de la lista blanca en %s: %s" % (rel, bad)


def test_detector_catches_a_literal(tmp_path):
    p = tmp_path / "gen.py"
    p.write_text("x = 0.0366\ny = 0.05\n", encoding="utf-8")
    assert float_literals(str(p)) == [(1, 0.0366)]


def test_figure_data_comparator_detects_one_changed_value():
    sys.path.insert(0, os.path.join(ROOT, "experiments"))
    import make_figures_audit11 as M
    base = [("plot", [np.array([1.0, 2.0]), np.array([0.3, 0.4])]), ("axhline", [np.array(0.05)])]
    same = {n: [(k, [a.copy() for a in arrs]) for k, arrs in base] for n in M.ORDER}
    old = {n: base for n in M.ORDER}
    assert all(v["bitwise_identical"] for v in M.compare(old, same).values())
    changed = dict(same)
    changed[M.ORDER[0]] = [("plot", [np.array([1.0, 2.0]), np.nextafter(np.array([0.3, 0.4]), 1)]), ("axhline", [np.array(0.05)])]
    res = M.compare(old, changed)
    assert not res[M.ORDER[0]]["bitwise_identical"]
    assert all(res[n]["bitwise_identical"] for n in M.ORDER[1:])
