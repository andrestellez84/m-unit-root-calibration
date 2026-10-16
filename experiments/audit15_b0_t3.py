"""
Auditoria A15 - B15.0: literales del parche T3 (protocol_audit15.md, lectura 0.4).

Asignaciones fijas del autor (enmienda 1, E1.5), sobre b0_iidasy_audit15.json; redondeo binario
(en los rangos se registra tambien el hacia afuera, solo informativo). Solo lee JSON.

Salida: experiments/results/b0_t3_audit15.json.
"""
import decimal
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402

SRC = "b0_iidasy_audit15.json"
N_MAX_T3 = 200                  # "n <= 200" del texto del parche T3
OUT = os.path.join(C.RESULTS, "b0_t3_audit15.json")


def dec(printed):
    return len(printed.split(".")[1]) if "." in printed else 0


def outward(x, d, mode):
    q = decimal.Decimal(1).scaleb(-d)
    return str(decimal.Decimal(repr(float(x))).quantize(q, rounding=mode))


def check_value(printed, value):
    d = dec(printed)
    got = TB.fdec(value, d, "binary") if d else "%d" % round(value)
    return {"printed": printed, "value": value, "binary": got, "verdict": "coincide" if got == printed else "no coincide",
            "correct": got}


def check_range(printed, lo, hi):
    a, b = printed.split("–")
    d = max(dec(a), dec(b))
    binr = "%s–%s" % (TB.fdec(lo, d, "binary"), TB.fdec(hi, d, "binary"))
    outr = "%s–%s" % (outward(lo, d, decimal.ROUND_FLOOR), outward(hi, d, decimal.ROUND_CEILING))
    verdict = "coincide" if binr == printed else ("coincide con redondeo hacia afuera" if outr == printed else "no coincide")
    return {"printed": printed, "value": [lo, hi], "binary": binr, "outward": outr, "verdict": verdict, "correct": binr}


def main():
    d = C.read_json(SRC)
    b, dd, gr = d["b_abs_dev"], d["d_diff_range"], d["group_ranges"]
    cells = d["cells"]
    four = [r for r in cells if r["case"] == "ct" and r["err_tag"] in ("ma_0p5", "ar_0p5") and r["n"] <= N_MAX_T3]
    m08 = [r for r in cells if r["err_tag"] == "ma_m0p8"]
    all36 = {p: sum(1 for r in cells if r["rates"][p]["iid"] > r["rates"][p]["asy"]) for p in ("msb", "mzt")}
    reg = [
        ("36", "celdas de tab:serial en las que la tasa baja al pasar al valor asintotico, MSB-GLS y MZ_t-GLS",
         "a_iid_gt_asy.<msb|mzt>.iid_gt_asy (minimo)", check_value("36", min(all36.values()))),
        ("30", "celdas con correlacion serial (psi != 0)", "n_cells_psi_nonzero", check_value("30", d["n_cells_psi_nonzero"])),
        ("0.0142", "MZ_t-GLS iid: media de |tasa - 0.05| sobre las 30 celdas con psi != 0 (dos casos)",
         "b_abs_dev.mzt.both.iid.mean", check_value("0.0142", b["mzt"]["both"]["iid"]["mean"])),
        ("0.0130", "MZ_t-GLS asintotico: la misma media", "b_abs_dev.mzt.both.asy.mean",
         check_value("0.0130", b["mzt"]["both"]["asy"]["mean"])),
        ("0.6", "maximo de iid - asy en pp, caso constante, MSB-GLS y MZ_t-GLS", "d_diff_range.<msb|mzt>.c.max x 100",
         check_value("0.6", max(dd["msb"]["c"]["max"], dd["mzt"]["c"]["max"]) * C.PP)),
        ("0.4–4.2", "rango de iid - asy en pp, MSB-GLS y MZ_t-GLS, caso tendencia", "d_diff_range.<msb|mzt>.ct x 100",
         check_range("0.4–4.2", min(dd["msb"]["ct"]["min"], dd["mzt"]["ct"]["min"]) * C.PP,
                     max(dd["msb"]["ct"]["max"], dd["mzt"]["ct"]["max"]) * C.PP)),
        ("0.062–0.092", "MZ_t-GLS iid, tendencia, psi = +0.5 o phi = +0.5, n <= 200 (cuatro celdas)",
         "cells[ct, ma_0p5|ar_0p5, n<=200].rates.mzt.iid", check_range("0.062–0.092", min(r["rates"]["mzt"]["iid"] for r in four),
                                                                        max(r["rates"]["mzt"]["iid"] for r in four))),
        ("0.036–0.050 (a)", "MZ_t-GLS asintotico en esas cuatro celdas", "cells[...].rates.mzt.asy",
         check_range("0.036–0.050", min(r["rates"]["mzt"]["asy"] for r in four), max(r["rates"]["mzt"]["asy"] for r in four))),
        ("0.036–0.050 (b)", "DF-GLS iid en esas cuatro celdas", "cells[...].rates.dfgls.iid",
         check_range("0.036–0.050", min(r["rates"]["dfgls"]["iid"] for r in four), max(r["rates"]["dfgls"]["iid"] for r in four))),
        ("up to 0.142", "DF-GLS iid, maximo sobre las celdas con psi = -0.8", "cells[ma_m0p8].rates.dfgls.iid (max)",
         check_value("0.142", max(r["rates"]["dfgls"]["iid"] for r in m08))),
    ]
    rows = []
    for lit, what, key, res in reg:
        if what is None:
            rows.append({"literal": lit, "assignment": None, "key": None, "status": "sin asignar",
                         "note": "ninguna magnitud de B15.0 lo reproduce sin conocer la frase del parche"})
        else:
            rows.append(dict(res, literal=lit, assignment=what, key=key, status="asignacion fija (enmienda 1, E1.5)"))
    out = {"provenance": C.provenance(__file__), "reading": "protocol_audit15.md, lectura 0.4; enmienda 1, E1.5", "source": SRC,
           "patch_text_available": True, "four_cells": sorted(r["cell"] for r in four), "literals": rows,
           "summary": {"coinciden": sum(1 for r in rows if r.get("verdict") == "coincide"),
                       "coinciden_hacia_afuera": sum(1 for r in rows if r.get("verdict") == "coincide con redondeo hacia afuera"),
                       "no_coinciden": sum(1 for r in rows if r.get("verdict") == "no coincide"),
                       "sin_asignar": sum(1 for r in rows if r["status"] == "sin asignar")}}
    C.write_result(OUT, out, __file__)
    for r in rows:
        print(r["literal"], "|", r["status"], "|", r.get("assignment"), "|", r.get("verdict"), r.get("binary"), r.get("outward", ""))
    print(out["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
