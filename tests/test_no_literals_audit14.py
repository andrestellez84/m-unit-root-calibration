"""
A8 - regla 3 aplicada a A14: cero literales numericos de resultados en los generadores
(tabular y CSV de valores criticos, fuentes de las cifras, verificacion del v15 y reporte).

Recorre con ast los scripts y falla si encuentra un literal de punto flotante fuera de la
lista blanca de constantes de configuracion. Los enteros no se examinan.
"""
import ast
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("experiments/audit14_common.py",
              "experiments/audit14_b0_inventory.py",
              "experiments/audit14_b1_critical.py",
              "experiments/audit14_exact_bootstrap.py",
              "experiments/audit14_tables.py",
              "experiments/audit14_b2_sources.py",
              "experiments/audit14_b3_verify.py",
              "experiments/audit14_generate_report.py")

WHITELIST = {
    0.0, 1.0, 2.0, 0.5,                      # neutros y mitades
    0.05, 0.1, 0.02,                         # alfa y theta
    100.0,                                   # conversion a puntos porcentuales
}
# Claves de diseno por script (no son resultados):
DESIGN = {
    "audit14_b1_critical.py": {0.01, 0.025},     # niveles del suplemento (lectura 4)
    "audit14_b3_verify.py": {0.99},              # umbral de la definicion de sec4 del v15 (lectura 9)
}


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
    allowed = WHITELIST | DESIGN.get(os.path.basename(rel), set())
    bad = float_literals(path, allowed)
    assert not bad, "literales de punto flotante fuera de la lista blanca en %s: %s" % (rel, bad)


def test_detector_catches_a_literal(tmp_path):
    p = tmp_path / "gen.py"
    p.write_text("x = 0.0366\ny = 0.05\n", encoding="utf-8")
    assert float_literals(str(p), WHITELIST) == [(1, 0.0366)]
