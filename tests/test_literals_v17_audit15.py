"""
A15, B15.6(5) (enmienda 4, lectura 6.7): cada literal de literals_v17_audit15.json se recalcula aqui por un camino
independiente del generador, desde b1_boot_audit15.json y b3_fixedb_audit15.json, y debe coincidir; L1-L20 cubiertos.
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


def test_literals_recomputed_independently():
    lit = {x["id"]: x for x in load("literals_v17_audit15.json")["literals"]}
    b1, b3 = load("b1_boot_audit15.json"), load("b3_fixedb_audit15.json")
    size = b1["size"]
    nz = [k for k, v in size.items() if v["err_tag"] != "ma_0"]

    def D(a):
        return sum(abs(size[k]["rates"][a]["rate"] - 0.05) for k in nz) / len(nz)

    def M(a):
        return max(abs(size[k]["rates"][a]["rate"] - 0.05) for k in nz)
    for i, a in (("L1", "ii"), ("L2", "iii"), ("L3", "v_prime"), ("L4", "iv"), ("L5", "i")):
        assert lit[i]["value"] == pytest.approx(D(a), abs=1e-15)
    assert lit["L6"]["value"] == pytest.approx(M("ii"), abs=1e-15)
    assert lit["L7"]["value"] == pytest.approx(M("iii"), abs=1e-15)
    diffs, others = [], []
    for v in b1["power"].values():
        m = v["vs_ii"]["iii"]["mcnemar"]
        d = abs(v["adjusted"]["iii"]["rate"] - v["adjusted"]["ii"]["rate"]) * 100
        (diffs if m["p_value"] < 0.05 else others).append(d)
    assert lit["L8"]["value"] == pytest.approx([min(diffs), max(diffs)], abs=1e-9)
    assert lit["L9"]["value"] == len(diffs)
    assert lit["L10"]["cells"] == len(others)
    c11 = [size["sz_ma_m0p8_n100_ct"]["rates"][a]["rate"] for a in ("i", "ii", "iii", "iv", "v_prime")]
    assert lit["L11"]["value"] == pytest.approx([min(c11), max(c11)])
    assert lit["L12"]["value"] == pytest.approx([size["sz_ar_0p5_n100_ct"]["rates"]["iii"]["rate"],
                                                 size["sz_ar_0p5_n100_ct"]["rates"]["ii"]["rate"]])
    assert lit["L13"]["value"] == pytest.approx(size["sz_ma_m0p8_n500_c"]["rates"]["iii"]["rate"])
    assert lit["L14"]["value"] == pytest.approx([size["sz_ma_0_n500_ct"]["rates"]["v_prime"]["rate"], b1["exact_region"][0]])
    iid = [k for k, v in size.items() if v["err_tag"] == "ma_0"]
    assert lit["L15"]["value"] == sum(1 for k in iid if not size[k]["rates"]["iv"]["in_region"])
    fb = [v["rates"]["b=0.3"]["rate"] for v in b3["size"].values()]
    assert lit["L16"]["value"] == pytest.approx([min(fb), max(fb)])
    p90 = b3["power"]["pw3_rho0p9_n200_c"]["rates"]
    assert lit["L17a"]["value"] == pytest.approx(p90["b=0.3"]["rate"])
    assert lit["L17b"]["value"] == pytest.approx(p90["gls_t0"]["rate"])
    assert lit["L17c"]["value"] == pytest.approx(p90["LLSW"]["rate"])
    assert lit["L18"]["value"] == pytest.approx(b3["size"]["sz_ma_m0p8_n100_c"]["rates"]["LLSW"]["rate"])
    assert lit["L19"]["value"] == pytest.approx(max(diffs), abs=1e-9)
    assert lit["L20"]["value"] == pytest.approx([M("ii"), M("iii")])


def test_all_literals_covered():
    ids = {x["id"] for x in load("literals_v17_audit15.json")["literals"]}
    want = {"L%d" % i for i in range(1, 21) if i != 17} | {"L17a", "L17b", "L17c"}
    assert want <= ids


def test_tab_summary_recomputed_independently():
    """A15, B15.9.1 (enmienda 5, lectura 9.1): filas de tab_summary frente a los JSON de origen."""
    rows = load("v17_tables_audit15.json")["summary_rows"]
    b1, b3, a12 = load("b1_boot_audit15.json"), load("b3_fixedb_audit15.json"), load("bA_ma_audit12.json")
    assert len(rows) == 10
    ss = b1["size_summary"]
    for r, arm in zip(rows[3:8], ("i", "ii", "iii", "v_prime", "iv")):
        assert r["D"] == pytest.approx(ss[arm]["D"], abs=1e-15)
        assert r["M"] == pytest.approx(ss[arm]["M"], abs=1e-15)
        assert r["power"] == b1["power"]["pw1_ma_0_rho0p9_n200_c"]["adjusted"][arm]["rate"]
    for r, proc in zip([rows[0], rows[2], rows[8], rows[9]], ("gls_t0", "msb", "dfgls", "adf")):
        rates = [v["iid"][proc]["rate"] for v in a12["size"].values()]
        assert (r["min"], r["max"]) == (min(rates), max(rates))
        assert r["power"] == a12["power"]["pwr_ma_0_rho0p9_n200_c"]["adjusted"][proc]["rate"]
    fb = [v["rates"]["b=0.3"]["rate"] for v in b3["size"].values()]
    assert (rows[1]["min"], rows[1]["max"]) == (min(fb), max(fb))
    assert rows[1]["power"] == b3["power"]["pw3_rho0p9_n200_c"]["rates"]["b=0.3"]["rate"]
    assert all(r["cells"] == 36 and r["cells_psi_nonzero"] == 30 and r["iid_cells"] == 6 for r in rows)
