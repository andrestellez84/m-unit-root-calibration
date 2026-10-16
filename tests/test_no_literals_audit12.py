"""
A8 - regla 3 aplicada a A12: cero literales numericos de resultados en los
generadores (reporte y localizador de frases del v12).

Recorre con ast los generadores y falla si encuentra un literal de punto flotante
fuera de la lista blanca de constantes de configuracion. Los enteros no se
examinan.
"""
import ast
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("experiments/audit12_generate_report.py",
              "experiments/audit12_claims.py")

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
