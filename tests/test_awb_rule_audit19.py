"""
A19, P2 (protocol_audit19.md, L2): con R = 399 y alpha = 0.05, #/R < alpha, #/R <= alpha y (1+#)/(R+1) <= alpha dan la misma
decision para todo # en 0..R, y rechazan si y solo si # <= 19. Camino independiente de audit19_awb_rule.py.
"""
import json
import os
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "experiments", "results")


def load(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        pytest.skip("%s aun no existe" % name)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("R", [399])
def test_three_rules_agree_exact_and_float(R):
    a = Fraction(5, 100)
    for k in range(R + 1):
        exact = {Fraction(k, R) < a, Fraction(k, R) <= a, Fraction(k + 1, R + 1) <= a}
        flt = {k / R < 0.05, k / R <= 0.05, (1.0 + k) / (R + 1.0) <= 0.05}
        assert len(exact) == 1 and exact == flt, k
        assert exact == {k <= 19}, k


def test_r_of_the_code_that_produced_the_figures_is_399():
    assert load("b1_boot_audit15.json")["config"]["R"] == 399
    assert load("e_awb_audit13.json")["config"]["B"] == 399


def test_registered_result():
    d = load("awb_rule_audit19.json")
    assert d["p2_holds"]
    assert d["implementations"]["a15_mzt_gls"]["operator"] == "<=" and d["implementations"]["a13_msb_b"]["operator"] == "<"
    assert "\\# \\leq 19" in d["s43_sentence"]
