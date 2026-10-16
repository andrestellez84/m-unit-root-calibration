"""
A8 - regla 3 aplicada a A15: cero literales numericos de resultados en los scripts de A15
(B15.0, B15.0b, B15.2, B15.5, tabulares y reporte).

Recorre con ast los scripts y falla si encuentra un literal de punto flotante fuera de la
lista blanca de constantes de configuracion. Los enteros no se examinan.
"""
import ast
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("experiments/audit15_common.py",
              "experiments/audit15_b0_iidasy.py",
              "experiments/audit15_b0_t3.py",
              "experiments/audit15_b0b_lag.py",
              "experiments/audit15_b2_slope.py",
              "experiments/audit15_b5_anon.py",
              "experiments/audit15_tables.py",
              "experiments/audit15_generate_report.py",
              "experiments/audit15_design.py",
              "experiments/audit15_inventory.py",
              "experiments/audit15_boot_engine.py",
              "experiments/audit15_b1_paso0.py",
              "experiments/audit15_fixedb.py",
              "experiments/audit15_b3_paso0.py",
              "experiments/audit15_probes.py",
              "experiments/audit15_b3_fixedb.py",
              "experiments/audit15_b1_paso0_v2.py",
              "experiments/audit15_b1_boot.py",
              "experiments/audit15_v17_tables.py",
              "experiments/audit15_v17_literals.py",
              "experiments/audit15_supplement.py",
              "experiments/audit15_maintenance.py",
              "experiments/audit15_b9.py")

WHITELIST = {
    0.0, 1.0, 2.0, 0.5,                      # neutros y mitades
    0.05, 0.1, 0.02,                         # alfa y theta
    100.0,                                   # conversion a puntos porcentuales
}
# Constantes de diseno por script (no son resultados):
DESIGN = {
    # replica literal de audit4_tarea_E.py: constante de Andrews, recorte de rho-hat, AR(0.95), exponente 1/3
    "audit15_b2_slope.py": {1.1447, 0.99, 0.95, 3.0, 4.0},
    # c-barra de Ng-Perron y de bootUR, regla kmax 12 (T/100)^(1/4), l = round(1.75 T^(1/3)), pisos numericos
    "audit15_boot_engine.py": {7.0, 13.5, 12.0, 0.25, 1.75, 3.0, 1e-300, 1e308},
    # rejillas de diseno: errores MA/AR, rho de potencia de B15.1 y de DGP 1
    "audit15_design.py": {0.8, 0.85, 0.9, 0.93, 0.95, 0.97, 0.99},
    # b de fixed-b y constante 1.3 de LLSW (2018), ec. (3)
    "audit15_fixedb.py": {0.3, 1.3},
    # segundos por hora
    "audit15_probes.py": {3600.0},
    # criterios de la enmienda 3 (E3.1(b)-(c), E3.2): z = 2.58 y factor de ruido 1.15
    "audit15_b1_paso0_v2.py": {2.58, 1.15},
    # margenes de la prediccion 14cbca7 (D - 0.005, M - 0.010)
    "audit15_b1_boot.py": {0.005, 0.01},
    "audit15_generate_report.py": {0.005, 0.01},
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
