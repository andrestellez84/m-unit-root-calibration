"""
A8 - regla 3 aplicada a A18 (enmienda 8, lectura E8.5): cero literales numericos de resultados en los scripts de A18.

Recorre con ast los scripts y falla si encuentra un literal de punto flotante fuera de la lista blanca de constantes
de configuracion. Los enteros no se examinan.
"""
import ast
import glob
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = sorted(os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, "experiments", "audit18_*.py")))

WHITELIST = {
    0.0, 1.0, 2.0, 0.5,                      # neutros y mitades
    0.05, 0.1, 0.02,                         # alfa y theta
    100.0,                                   # conversion a puntos porcentuales
}
# Constantes de diseno por script (no son resultados):
DESIGN = {}


def float_literals(path, allowed):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant) \
                and isinstance(node.operand.value, float):
            if -node.operand.value not in allowed and node.operand.value not in allowed:
                out.append((node.lineno, -node.operand.value))
            node.operand._seen = True
        elif isinstance(node, ast.Constant) and isinstance(node.value, float) and not getattr(node, "_seen", False) \
                and node.value not in allowed:
            out.append((node.lineno, node.value))
    return out


def test_generators_found():
    assert GENERATORS, "no hay scripts audit18_*.py"


@pytest.mark.parametrize("rel", GENERATORS)
def test_generator_has_no_result_literals(rel):
    path = os.path.join(ROOT, rel)
    allowed = WHITELIST | DESIGN.get(os.path.basename(rel), set())
    bad = float_literals(path, allowed)
    assert not bad, "literales de punto flotante fuera de la lista blanca en %s: %s" % (rel, bad)


def test_detector_catches_a_literal(tmp_path):
    p = tmp_path / "gen.py"
    p.write_text("x = 0.0366\ny = 0.05\n", encoding="utf-8")
    assert float_literals(str(p), WHITELIST) == [(1, 0.0366)]
