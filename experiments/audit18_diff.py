"""
Auditoria A18 - B18.1 (enmienda 8, lectura E8.1): diff completo entre paper_latex_v18.zip y paper_latex_v18b.zip.
Criterio: el unico archivo de texto distinto es sec3_theory.tex y en el la unica linea cambiada es la 176, que escribe
l = round(1.75 T^{1/3}) y T = n + 1 (la regla del codigo registrada en boot35_v18_audit17.json).
Salida: experiments/results/diff_v18b_audit18.json.
"""
import difflib
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit18_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "diff_v18b_audit18.json")
TEXT = (".tex", ".bib", ".bbl", ".bst", ".cls", ".md")
TARGET = ("sec3_theory.tex", 176)


def load(path):
    with zipfile.ZipFile(path) as z:
        return {(n.split("/", 1)[1] if "/" in n else n): z.read(n) for n in z.namelist() if not n.endswith("/")}


def main():
    a, b = load(C.ZIP_V18), load(C.ZIP_V18B)
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    differ, text_changes = [], {}
    for k in sorted(set(a) & set(b)):
        if a[k] == b[k]:
            continue
        differ.append(k)
        if k.endswith(TEXT):
            la = a[k].decode("utf-8").replace("\r\n", "\n").splitlines()
            lb = b[k].decode("utf-8").replace("\r\n", "\n").splitlines()
            if la == lb:
                text_changes[k] = {"only_line_endings": True, "changes": []}
                continue
            ch = []
            for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=la, b=lb, autojunk=False).get_opcodes():
                if tag != "equal":
                    ch.append({"tag": tag, "v18_lines": [i1 + 1, i2], "v18b_lines": [j1 + 1, j2], "v18": la[i1:i2], "v18b": lb[j1:j2]})
            text_changes[k] = {"only_line_endings": False, "changes": ch}
    real = {k: v for k, v in text_changes.items() if not v["only_line_endings"]}
    f, ln = TARGET
    only_target = list(real) == [f] and len(real[f]["changes"]) == 1 and real[f]["changes"][0]["v18b_lines"] == [ln, ln] \
        and real[f]["changes"][0]["v18_lines"] == [ln, ln]
    new_line = real.get(f, {"changes": [{"v18b": [""]}]})["changes"][0]["v18b"][0]
    boot = C.read_json("boot35_v18_audit17.json")
    rule = {"writes_T": "1.75\\,T^{1/3}" in new_line, "writes_T_eq_n_plus_1": "T = n + 1" in new_line,
            "l_new_text_rule_equals_code": {n: v["l_code"] for n, v in boot["eta"].items()},
            "code_rule": "l = round(1.75 T^(1/3)), T = n + 1 (boot35_v18_audit17.json eta.<n>.l_code; audit9_engine.awb_gamma)"}
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 8, lectura E8.1",
           "inputs": {"v18_zip_sha256": C.sha256_file(C.ZIP_V18), "v18b_zip_sha256": C.sha256_file(C.ZIP_V18B)},
           "only_in_v18": only_a, "only_in_v18b": only_b, "members_differ": differ, "text_changes": text_changes,
           "non_text_differ": [k for k in differ if not k.endswith(TEXT)], "only_change_is_sec3_176": only_target and not only_a and not only_b,
           "line_176": new_line, "line_176_rule": rule}
    C.write_result(OUT, out, __file__)
    print("distintos:", differ, "| solo sec3:176:", out["only_change_is_sec3_176"], "| regla:", rule)
    print(new_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
