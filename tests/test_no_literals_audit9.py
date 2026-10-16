"""
A8 - regla 3: cero literales numericos de resultados en los generadores de reporte
y de figuras.

Recorre con ast los generadores (experiments/audit9_generate_report.py y
experiments/make_figures_audit9.py) y falla si encuentra un literal de punto
flotante fuera de la lista blanca de constantes de configuracion (niveles alfa,
theta, R, limites de la region exacta, umbrales del protocolo y conversiones de
unidad). Los enteros no se examinan (n, conteos, indices). Las constantes de
maquetacion de las figuras viven en experiments/audit9_figconfig.py, que no es un
generador.
"""
import ast
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("experiments/audit9_generate_report.py", "experiments/make_figures_audit9.py")

WHITELIST = {
    0.0, 1.0, 2.0, 0.5,                      # neutros y mitades
    0.01, 0.025, 0.05, 0.1,                  # niveles alfa
    0.02, 0.15, 0.2, 0.3, 0.25, 0.75,       # theta y R
    0.044, 0.0562,                           # region exacta con N_sim = 5000
    3.0,                                     # umbral de la regla B9.5 en pp
    0.30,                                    # umbrales del protocolo en pp
    100.0,                                   # conversion a puntos porcentuales
    1.96,                                    # bandas +-1.96 EE (B8)
    13.5, 7.0,                               # cbar
}


def float_literals(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float) and node.value not in WHITELIST:
            bad.append((node.lineno, node.value))
    return bad


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
