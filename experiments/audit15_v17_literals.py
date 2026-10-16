"""
Auditoria A15 - B15.6(5): literales del v17 (enmienda 4, lectura 6.7). Solo lee JSON.

Para cada literal L1-L20 del encargo: magnitud, valor exacto desde b1_boot_audit15.json y
b3_fixedb_audit15.json, redondeo binario a los decimales impresos (rangos: minimo y maximo; se
registra tambien el hacia afuera), cotas como desigualdad mas redondeo hacia afuera, recuentos y
palabras-numero por igualdad. Veredicto: confirma o corrige (con el valor correcto).

Salida: experiments/results/literals_v17_audit15.json.
"""
import decimal
from fractions import Fraction
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "literals_v17_audit15.json")
SRC_B1, SRC_B3 = "b1_boot_audit15.json", "b3_fixedb_audit15.json"
WORDS = {"two": 2, "six": 6, "eight": 8}
EPS_DEC = 10                       # decimales a los que se estabiliza un valor antes del redondeo hacia afuera
ONE_POINT = 1                      # "less than one point"
ARMS5 = ("i", "ii", "iii", "iv", "v_prime")


def dec(s):
    return len(s.split(".")[1]) if "." in s else 0


def binr(x, d):
    return TB.fdec(x, d, "binary")


def outward(x, d, up):
    q = decimal.Decimal(1).scaleb(-d)
    v = decimal.Decimal(repr(round(float(x), EPS_DEC)))
    return str(v.quantize(q, rounding=decimal.ROUND_CEILING if up else decimal.ROUND_FLOOR))


def value(lit, printed, x, what, src):
    got = binr(x, dec(printed))
    return {"id": lit, "printed": printed, "what": what, "source": src, "value": x, "binary": got,
            "verdict": "confirma" if got == printed else "corrige", "correct": got}


def rng(lit, printed, lo, hi, what, src):
    a, b = printed
    got = "%s to %s" % (binr(lo, dec(a)), binr(hi, dec(b)))
    out = "%s to %s" % (outward(lo, dec(a), False), outward(hi, dec(b), True))
    want = "%s to %s" % (a, b)
    return {"id": lit, "printed": want, "what": what, "source": src, "value": [lo, hi], "binary": got, "outward": out,
            "verdict": "confirma" if got == want else "corrige", "correct": got}


def pair(lit, printed, x, y, what, src, sep=" against "):
    a, b = printed
    got = "%s%s%s" % (binr(x, dec(a)), sep, binr(y, dec(b)))
    want = "%s%s%s" % (a, sep, b)
    return {"id": lit, "printed": want, "what": what, "source": src, "value": [x, y], "binary": got,
            "verdict": "confirma" if got == want else "corrige", "correct": got}


def count(lit, printed, k, what, src):
    inv = {v: w for w, v in WORDS.items()}
    ok = WORDS.get(printed) == k
    return {"id": lit, "printed": printed, "what": what, "source": src, "value": k, "verdict": "confirma" if ok else "corrige",
            "correct": inv.get(k, "%d" % k)}


def main():
    b1, b3 = C.read_json(SRC_B1), C.read_json(SRC_B3)
    ss = b1["size_summary"]
    sz = b1["size"]
    pw = b1["power"]
    sig = {k: abs(v["vs_ii"]["iii"]["diff_pp"]) for k, v in pw.items() if v["vs_ii"]["iii"]["mcnemar"]["p_value"] < C.ALPHA}
    rest = {k: v["vs_ii"]["iii"] for k, v in pw.items() if v["vs_ii"]["iii"]["mcnemar"]["p_value"] >= C.ALPHA}
    iid = [k for k, v in sz.items() if v["err_tag"] == "ma_0"]
    fb03 = [v["rates"]["b=0.3"]["rate"] for v in b3["size"].values()]
    p90 = b3["power"]["pw3_rho0p9_n200_c"]["rates"]
    cell11 = [sz["sz_ma_m0p8_n100_ct"]["rates"][a]["rate"] for a in ARMS5]
    lits = [
        value("L1", "0.0135", ss["ii"]["D"], "D(ii)", SRC_B1 + " size_summary.ii.D"),
        value("L2", "0.0074", ss["iii"]["D"], "D(iii)", SRC_B1 + " size_summary.iii.D"),
        value("L3", "0.0072", ss["v_prime"]["D"], "D(v')", SRC_B1 + " size_summary.v_prime.D"),
        value("L4", "0.0117", ss["iv"]["D"], "D(iv)", SRC_B1 + " size_summary.iv.D"),
        value("L5", "0.0134", ss["i"]["D"], "D(i)", SRC_B1 + " size_summary.i.D"),
        value("L6", "0.0576", ss["ii"]["M"], "M(ii)", SRC_B1 + " size_summary.ii.M"),
        value("L7", "0.0382", ss["iii"]["M"], "M(iii)", SRC_B1 + " size_summary.iii.M"),
        rng("L8", ("1.6", "4.2"), min(sig.values()), max(sig.values()), "|diferencia ajustada (iii) - (ii)| en pp, celdas con McNemar p < 0.05",
            SRC_B1 + " power.<celda>.vs_ii.iii"),
        count("L9", "six", len(sig), "numero de celdas con McNemar p < 0.05 para (iii) frente a (ii)", SRC_B1 + " power.<celda>.vs_ii.iii"),
    ]
    exact = {}
    for k in sig:
        m = pw[k]["vs_ii"]["iii"]["mcnemar"]
        exact[k] = Fraction(abs(m["only_first"] - m["only_second"]) * int(C.PP), pw[k]["adjusted"]["iii"]["n"])
    lo, hi = min(exact.values()), max(exact.values())
    lits[7]["exact_from_counts"] = {"min": str(lo), "max": str(hi), "min_decimal": float(lo), "max_decimal": float(hi)}
    # sensible al redondeo: el valor exacto cae justo en la mitad entre dos cifras de 1 decimal
    lits[7]["rounding_sensitive"] = {str(x): (x * 10).denominator == 2 for x in (lo, hi)}
    l10 = {"id": "L10", "printed": "less than one point", "what": "en las otras celdas: |dif| < 1.0 pp y p >= 0.05",
           "source": SRC_B1 + " power.<celda>.vs_ii.iii", "value": {k: [v["diff_pp"], v["mcnemar"]["p_value"]] for k, v in rest.items()},
           "cells": len(rest)}
    ok10 = len(rest) == len(pw) - len(sig) and all(abs(v["diff_pp"]) < ONE_POINT and v["mcnemar"]["p_value"] >= C.ALPHA for v in rest.values())
    l10.update(verdict="confirma" if ok10 else "corrige", correct=None if ok10 else "max |dif| %s pp" % binr(max(abs(v["diff_pp"]) for v in rest.values()), 1))
    lits.append(l10)
    lits += [
        rng("L11", ("0.083", "0.108"), min(cell11), max(cell11), "los 5 brazos en sz_ma_m0p8_n100_ct", SRC_B1 + " size.sz_ma_m0p8_n100_ct.rates"),
        pair("L12", ("0.052", "0.093"), sz["sz_ar_0p5_n100_ct"]["rates"]["iii"]["rate"], sz["sz_ar_0p5_n100_ct"]["rates"]["ii"]["rate"],
             "(iii) y (ii) en sz_ar_0p5_n100_ct", SRC_B1 + " size.sz_ar_0p5_n100_ct.rates.<iii|ii>"),
        value("L13", "0.066", sz["sz_ma_m0p8_n500_c"]["rates"]["iii"]["rate"], "(iii) en sz_ma_m0p8_n500_c",
              SRC_B1 + " size.sz_ma_m0p8_n500_c.rates.iii"),
        pair("L14", ("0.0438", "0.0440"), sz["sz_ma_0_n500_ct"]["rates"]["v_prime"]["rate"], b1["exact_region"][0],
             "(v') en sz_ma_0_n500_ct y limite inferior de la region exacta", SRC_B1 + " size.sz_ma_0_n500_ct.rates.v_prime; exact_region[0]"),
        count("L15", "two", sum(1 for k in iid if not sz[k]["rates"]["iv"]["in_region"]), "celdas iid fuera de la region para (iv)",
              SRC_B1 + " size.<sz_ma_0_*>.rates.iv.in_region"),
        rng("L16", ("0.015", "0.059"), min(fb03), max(fb03), "fixed-b b = 0.3: minimo y maximo sobre las 36 celdas",
            SRC_B3 + " size.<celda>.rates.b=0.3"),
        value("L17a", "0.187", p90["b=0.3"]["rate"], "potencia ajustada rho = 0.90, n = 200, c: b = 0.3", SRC_B3 + " power.pw3_rho0p9_n200_c.rates.b=0.3"),
        value("L17b", "0.994", p90["gls_t0"]["rate"], "idem, Andrews", SRC_B3 + " power.pw3_rho0p9_n200_c.rates.gls_t0"),
        value("L17c", "0.901", p90["LLSW"]["rate"], "idem, LLSW", SRC_B3 + " power.pw3_rho0p9_n200_c.rates.LLSW"),
        value("L18", "0.214", b3["size"]["sz_ma_m0p8_n100_c"]["rates"]["LLSW"]["rate"], "LLSW en sz_ma_m0p8_n100_c",
              SRC_B3 + " size.sz_ma_m0p8_n100_c.rates.LLSW"),
    ]
    mx = max(sig.values())
    got = outward(mx, 1, True)
    p19 = "up to 4.2"
    bound = p19.split()[-1]
    holds = round(mx, EPS_DEC) <= float(bound) + 10 ** -EPS_DEC
    lits.append({"id": "L19", "printed": p19, "what": "maximo de L8 (cota superior)", "source": SRC_B1 + " power.<celda>.vs_ii.iii",
                 "value": mx, "bound_holds": holds, "outward": got,
                 "verdict": "confirma" if got == bound and holds else "corrige", "correct": got})
    lits.append(pair("L20", ("0.0576", "0.0382"), ss["ii"]["M"], ss["iii"]["M"], "M(ii) y M(iii)", SRC_B1 + " size_summary.<ii|iii>.M", sep=" to "))
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 4, lectura 6.7",
           "sources": {k: C.sha256_file(os.path.join(C.RESULTS, k)) for k in (SRC_B1, SRC_B3)},
           "literals": lits, "summary": {"confirma": sum(1 for x in lits if x["verdict"] == "confirma"),
                                         "corrige": sum(1 for x in lits if x["verdict"] == "corrige")}}
    C.write_result(OUT, out, __file__)
    for x in lits:
        print("%-5s %-22s %-9s %s" % (x["id"], x["printed"], x["verdict"], "" if x["verdict"] == "confirma" else "-> %s" % x["correct"]))
    print(out["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
