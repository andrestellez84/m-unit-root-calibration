"""
A16, B16.3 (enmienda 6, lectura E6.5): cada literal N1-N8 de literals_v17b_audit16.json se recalcula aqui por un camino
independiente del generador (lectura directa de los JSON, sin los helpers de A13 ni de audit16_literals), y debe coincidir.
No exige que el literal impreso coincida: eso es un hallazgo del reporte.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "experiments", "results")


def load(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        pytest.skip("%s aun no existe" % name)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def lit():
    return {x["id"]: x for x in load("literals_v17b_audit16.json")["N"]}


def values(x):
    return [n["value"] for n in x["numbers"]]


def test_all_n_literals_present():
    assert {"N1", "N2", "N3", "N4", "N5a", "N5b", "N7", "N8"} <= set(lit())


def test_n1_n2_n3():
    L, b1 = lit(), load("b1_boot_audit15.json")["size"]
    cells = [k for k, v in b1.items() if v["case"] == "ct" and v["n"] <= 200 and v["err_tag"] in ("ma_0p5", "ar_0p5")]
    assert len(cells) == 4
    ii = [b1[k]["rates"]["ii"]["rate"] for k in cells]
    i_ = [b1[k]["rates"]["i"]["rate"] for k in cells]
    assert values(L["N1"]) == pytest.approx([min(ii), max(ii)])
    assert values(L["N2"]) == pytest.approx([min(i_), max(i_)])
    gt = sum(1 for v in b1.values() if v["rates"]["ii"]["rate"] > v["rates"]["i"]["rate"])
    assert L["N3"]["value"]["ii_gt_i"] == gt
    assert L["N3"]["value"]["cells"] == len(b1)


def test_n4():
    d = load("b0b_lag_audit15.json")
    want = [d["cells"]["sz_ar_0p5_n100_ct"]["procs"]["mzt"]["by_k"]["1"]["iid"]["rejections"] /
            d["cells"]["sz_ar_0p5_n100_ct"]["procs"]["mzt"]["by_k"]["1"]["paths"],
            d["a10_null"]["100|ct"]["procs"]["mzt"]["by_k"]["1"]["iid"]["rejections"] /
            d["a10_null"]["100|ct"]["procs"]["mzt"]["by_k"]["1"]["paths"]]
    assert values(lit()["N4"]) == pytest.approx(want, abs=1e-12)


def test_n5():
    comp = load("e_calib_audit13.json")["cases_by_theta"]["gls_t0"]["c"]["approximation_cost_comparators"]
    msb = [v["msb"]["size_published_asymptotic"]["rejections"] / v["msb"]["size_published_asymptotic"]["n"] for v in comp.values()]
    assert values(lit()["N5a"]) == pytest.approx([min(msb), max(msb)], abs=1e-12)
    d = comp["60"]["dfgls"]["size_published_asymptotic"]
    assert values(lit()["N5b"]) == pytest.approx([d["rejections"] / d["n"]], abs=1e-12)


def test_n7():
    """Recalculo desde A12: media de |tasa - 0.05| de MZ_t sobre las 30 celdas con psi != 0, iid y asintotico."""
    size = load("bA_ma_audit12.json")["size"]
    nz = [v for v in size.values() if v["err_tag"] != "ma_0"]
    assert len(nz) == 30
    want = [sum(abs(v[blk]["mzt"]["rate"] - 0.05) for v in nz) / len(nz) for blk in ("iid", "asy")]
    assert values(lit()["N7"]) == pytest.approx(want, abs=1e-12)


def test_n8():
    pw = load("b1_boot_audit15.json")["power"]
    N8 = lit()["N8"]
    for arm, key in (("v_prime", "SWB"), ("iv", "AWB")):
        sig = [abs(v["adjusted"][arm]["rate"] - v["adjusted"]["ii"]["rate"]) * 100 for v in pw.values()
               if v["vs_ii"][arm]["mcnemar"]["p_value"] < 0.05]
        assert N8[key]["cells"] == len(sig)
        assert N8[key]["min_pp"] == pytest.approx(min(sig), abs=1e-9)
        assert N8[key]["max_pp"] == pytest.approx(max(sig), abs=1e-9)
