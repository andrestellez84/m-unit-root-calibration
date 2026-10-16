"""
A8 - regla 3 aplicada a A13: cero literales numericos de resultados en los
generadores (tablas regeneradas con theta = 0, tablas de B13.T, cifras del texto,
figuras y reporte).

Recorre con ast los generadores y falla si encuentra un literal de punto flotante
fuera de la lista blanca de constantes de configuracion. Los enteros no se
examinan.
"""
import ast
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("experiments/audit13_tables.py",
              "experiments/audit13_t_tables.py",
              "experiments/audit13_claims.py",
              "experiments/audit13_generate_report.py",
              "experiments/make_figures_audit13.py",
              "experiments/audit13_q_attrib.py",
              "experiments/audit13_q_claims.py",
              "experiments/audit13_q_phrases.py",
              "experiments/audit13_q_supplement.py",
              "experiments/make_figures_audit13q.py",
              "experiments/audit13_q_report.py",
              "experiments/audit13_q_inventory.py")

WHITELIST = {
    0.0, 1.0, 2.0, 0.5,                      # neutros y mitades
    0.05, 0.1, 0.02,                         # alfa y theta
    100.0,                                   # conversion a puntos porcentuales
}
# Claves de diseno que nombran celdas o reglas de las frases del v13 (no son resultados):
# rejilla de rho de DGP 1, umbral de saturacion de 0.99 de las notas del v13 y valores
# de r de DGP 5 que citan las frases ("r >= 1.5", "r <= 1.25", interior {2, 3}).
DESIGN = {0.8, 0.85, 0.9, 0.93, 0.95, 0.97, 0.99, 1.25, 1.5, 3.0}


def float_literals(path, allowed):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float) and node.value not in allowed]


@pytest.mark.parametrize("rel", GENERATORS)
def test_generator_has_no_result_literals(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        pytest.skip("%s aun no existe" % rel)
    allowed = WHITELIST | (DESIGN if rel.endswith(("audit13_claims.py", "audit13_q_claims.py")) else set())
    bad = float_literals(path, allowed)
    assert not bad, "literales de punto flotante fuera de la lista blanca en %s: %s" % (rel, bad)


def test_detector_catches_a_literal(tmp_path):
    p = tmp_path / "gen.py"
    p.write_text("x = 0.0366\ny = 0.05\n", encoding="utf-8")
    assert float_literals(str(p), WHITELIST) == [(1, 0.0366)]
