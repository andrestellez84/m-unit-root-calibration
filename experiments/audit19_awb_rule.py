"""
Auditoria A19 - punto 2 (protocol_audit19.md, L2): R y operador de rechazo del AWB, y coincidencia de las tres reglas (P2).

Lee R, el p-valor y la regla de los JSON que produjeron las cifras del v25:
  (a) A15, MZ_t-GLS, brazo (iv): b1_boot_audit15.json (§4.8 del v25 y tab:boot del suplemento);
  (b) A13, MSB-B (RM-GLS):        e_awb_audit13.json   (tab:awb, S4.3, y §4.9 del v25).
Cita las lineas del codigo que implementan el p-valor y el rechazo (con el sha256 de cada archivo) y enumera # = 0..R con las
reglas #/R < alpha, #/R <= alpha y (1+#)/(R+1) <= alpha, en aritmetica exacta y en coma flotante.
Salida: experiments/results/awb_rule_audit19.json.
"""
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit19_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "awb_rule_audit19.json")
CODE = {
    "a15": [("audit15_boot_engine.py", r"^def pvalue_awb", r"return \(1\.0 \+ cnt\) / \(R \+ 1\.0\), t_obs$"),
            ("audit15_boot_engine.py", r"^def pvalue_awb", r"if mzt_gls\(ys, ct, cbar, kmax\)\[0\] <= t_obs:"),
            ("audit15_b1_boot.py", None, r"dec\[a\] = rows\[:, COLS\.index\(\"p_\" \+ a\)\] <= C\.ALPHA"),
            ("audit15_design.py", None, r"^R = 399$")],
    "a13": [("audit13_e_awb.py", None, r"r_awb = p < C\.ALPHA"),
            ("audit13_e_awb.py", None, r"\"pvalue\": \"#\{stat\* <= stat\} / B\"")],
    "a10_cited_in_assignment": [("audit10_b103_awb.py", None, r"r_awb = p < C\.ALPHA")],
}
SENTENCE = ("With $R = %d$, rejecting when $\\#/R < %s$ gives the same decision as $(1 + \\#)/(R + 1) \\leq %s$: "
            "both reject exactly when $\\# \\leq %d$.")


def cite(fn, after, pat):
    path = os.path.join(HERE, fn)
    lines = open(path, encoding="utf-8").read().splitlines()
    start = 0
    if after:
        start = next(i for i, l in enumerate(lines) if re.search(after, l))
    hits = [i for i, l in enumerate(lines) if i >= start and re.search(pat, l.strip())]
    if not hits:
        raise SystemExit("no se encuentra %r en %s" % (pat, fn))
    i = hits[0]
    return {"file": "experiments/" + fn, "line": i + 1, "text": lines[i].strip(), "sha256": C.sha256_file(path)}


def rules(R, alpha):
    a = Fraction(alpha).limit_denominator(10 ** 6)
    rows = []
    for k in range(R + 1):
        ex = (Fraction(k, R) < a, Fraction(k, R) <= a, Fraction(1 + k, R + 1) <= a)
        fl = (k / R < alpha, k / R <= alpha, (1.0 + k) / (R + 1.0) <= alpha)
        rows.append({"count": k, "exact": ex, "float": fl})
    same = all(len(set(r["exact"])) == 1 and r["exact"] == r["float"] for r in rows)
    rej = [r["count"] for r in rows if r["exact"][0]]
    first_disagreement = next((r for r in rows if len(set(r["exact"])) > 1 or r["exact"] != r["float"]), None)
    return {"R": R, "alpha": alpha, "all_rules_agree": same, "max_count_rejecting": max(rej) if rej else None,
            "reject_iff_count_le": max(rej) if same and rej == list(range(max(rej) + 1)) else None,
            "first_disagreement": first_disagreement,
            "rules": ["#/R < alpha", "#/R <= alpha", "(1+#)/(R+1) <= alpha"]}


def main():
    b1 = C.read_json("b1_boot_audit15.json")["config"]
    aw = C.read_json("e_awb_audit13.json")["config"]
    impl = {
        "a15_mzt_gls": {"used_for": ["§4.8 del v25 (AWB, brazo iv)", "tab:boot del suplemento"],
                        "json": "experiments/results/b1_boot_audit15.json", "R": b1["R"],
                        "chosen_configuration": b1["chosen_configuration"], "pvalue": b1["pvalue"],
                        "operator": "<=", "pvalue_form": "(1+#)/(R+1)", "code": [cite(*c) for c in CODE["a15"]]},
        "a13_msb_b": {"used_for": ["tab:awb (S4.3) del suplemento", "§4.9 del v25"],
                      "json": "experiments/results/e_awb_audit13.json", "R": aw["B"], "pvalue": aw["pvalue"],
                      "operator": "<", "pvalue_form": "#/R", "code": [cite(*c) for c in CODE["a13"]]},
        "a10_cited_in_assignment": {"note": "version de A10; mismo operador; no produce cifras del v25",
                                    "code": [cite(*c) for c in CODE["a10_cited_in_assignment"]]},
    }
    checks = {k: rules(v["R"], C.ALPHA) for k, v in impl.items() if "R" in v}
    r13 = checks["a13_msb_b"]
    sentence = SENTENCE % (impl["a13_msb_b"]["R"], "%g" % C.ALPHA, "%g" % C.ALPHA, r13["reject_iff_count_le"]) \
        if r13["all_rules_agree"] else None
    p2 = all(c["all_rules_agree"] for c in checks.values()) and all(v["R"] == 399 for k, v in impl.items() if "R" in v) \
        and all(c["reject_iff_count_le"] == 19 for c in checks.values())
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit19.md, L2",
           "implementations": impl, "checks": checks, "p2_holds": bool(p2), "s43_sentence": sentence}
    C.write_result(OUT, out, __file__)
    for k, v in impl.items():
        if "R" in v:
            print(k, "R =", v["R"], "operador", v["operator"], "| reglas coinciden:", checks[k]["all_rules_agree"],
                  "| rechaza si # <=", checks[k]["reject_iff_count_le"])
    print("P2:", p2)
    print("oracion S4.3:", sentence)
    return 0 if p2 else 1


if __name__ == "__main__":
    sys.exit(main())
