"""
Auditoria A16 - B15.4 (enmienda 6, lectura E6.7): pasada de coherencia tipo B13.Q Q3 sobre el v17 y el suplemento
reconstruido. Solo lee JSON, el zip del v17 y supplementary/.

(a) Cifras del resumen (main.tex) y de la conclusion (sec5_conclusion.tex): cada una frente a su JSON y frente a su
    contrapartida en P1-P3 (sec1), sec. 4 o sec. 5; y las afirmaciones cualitativas con cifra implicita, con comprobacion.
(b) Cada \\supp{k} y \\supptab{k.j} del cuerpo: registro manual de lo que afirma la frase y de lo que debe haber en el
    suplemento (etiquetas y textos/cifras); se comprueba sobre supplementary/supplement.tex, sus tabulares y la numeracion
    compilada (supplement_v17_audit16.json).
(c) Cifras retiradas (0.333, 6.9 %, 0.6 %, "doubles"): busqueda en el v17 y en el suplemento, con contexto y clasificacion.
Ademas registra las incoherencias de notacion o de region que arrastran los textos del v16 transcritos (para el reporte).
Salida: experiments/results/coherence_v17_audit16.json.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C                                         # noqa: E402
import audit16_literals as L                                       # noqa: E402

OUT = os.path.join(C.RESULTS, "coherence_v17_audit16.json")
SUPP = os.path.join(C.REPO, "supplementary")
QC = L.QC


# ---------------------------------------------------------------------------
# (a) resumen y conclusion
# ---------------------------------------------------------------------------
def abstract_claims():
    calc, ss, sz = QC.calc, L.ss, QC.sz
    msb200 = calc("ct", 200, "msb")["rate"]
    msb60 = calc("ct", 60, "msb")["rate"]
    iii = L.sig_cells("iii")
    return [
        ("abs_msb", "main.tex", "critical values of MSB-GLS reject $<>$ at $n = 200$ in the trend case", [msb200],
         [("sec1_introduction.tex", "values of MSB-GLS reject $<>$ at $n = 200$"), ("sec4_montecarlo.tex", "$<>$ at $n = 200$ and $0.0394$")]),
        ("abs_boot", "main.tex", "over thirty designs from $<>$ to $<>$, at a cost of up to $<>$ points", [ss("ii", "D"), ss("iii", "D"), max(iii.values())],
         [("sec1_introduction.tex", "distortion from $<>$ to $<>$"), ("sec1_introduction.tex", "costs between $1.6$ and $<>$ points"),
          ("sec4_montecarlo.tex", "is $<>$ with the SB")]),
        ("abs_ma", "main.tex", "rejecting $<>$ at $n = 200$ with moving-average errors of $-0.8$", [sz("ma_m0p8", 200, "c")],
         [("sec1_introduction.tex", "the calibrated test then rejects $<>$"), ("sec4_montecarlo.tex", "over-rejects heavily: $<>$"),
          ("sec5_conclusion.tex", "calibrated test rejects $<>$ at $n = 200$")]),
        ("concl_underreject", "sec5_conclusion.tex", "trend case by $<>$ percentage points at $n = 200$ and $<>$ at $n = 60$",
         [(C.ALPHA - msb200) * C.PP, (C.ALPHA - msb60) * C.PP],
         [("sec1_introduction.tex", "values of MSB-GLS reject $<>$ at $n = 200$ and $<>$ at $n = 60$")]),
    ]


def qualitative():
    ss = L.ss
    a12 = L.a12()["size"]["sz_ma_m0p8_n100_ct"]["iid"]
    b3 = L.b3()["size"]["sz_ma_m0p8_n100_ct"]["rates"]
    b1 = L.b1()["size"]["sz_ma_m0p8_n100_ct"]["rates"]
    inside = [k for k, v in list(a12.items()) + list(b3.items()) + list(b1.items()) if v["in_region"]]
    at = L.att()["by_n"]["c|200"] if hasattr(L, "att") else QC.attrib()["by_n"]["c|200"]
    return [
        {"where": "main.tex (resumen) y sec5_conclusion.tex", "claim": "los valores simulados de MZ_t-GLS no estan, en promedio, mas cerca del nivel que "
         "los asintoticos (treinta disenos)", "value": {"D_ii": ss("ii", "D"), "D_i": ss("i", "D")}, "holds": ss("ii", "D") >= ss("i", "D")},
        {"where": "sec5_conclusion.tex", "claim": "el SB 'nearly halves' la distorsion media", "value": {"ratio_D_iii_over_D_ii": ss("iii", "D") / ss("ii", "D")},
         "holds": None, "note": "cualitativa: se reporta el cociente"},
        {"where": "sec5_conclusion.tex", "claim": "'most of which survive' la modificacion de Perron y Qu", "value":
         {"a_minus_b_pp": at["a_minus_b"]["mean"] * C.PP, "a_minus_bp_pp": at["a_minus_bp"]["mean"] * C.PP,
          "share": at["a_minus_bp"]["mean"] / at["a_minus_b"]["mean"]}, "holds": at["a_minus_bp"]["mean"] > at["a_minus_b"]["mean"] / 2},
        {"where": "sec5_conclusion.tex", "claim": "ningun procedimiento controla el tamano con MA -0.8, n = 100, tendencia", "value":
         {"procedures": len(a12) + len(b3) + len(b1), "inside_region": inside}, "holds": not inside},
    ]


def find(v17, fname, tpl):
    text = v17.files[fname]
    m = re.search(QC.pattern(tpl), text)
    if m is None:
        return None
    return {"line": text[:m.start()].count("\n") + 1, "printed": list(m.groups()), "quote": re.sub(r"\s+", " ", m.group(0))}


def part_a(v17):
    out = []
    for key, fname, tpl, vals, counterparts in abstract_claims():
        hit = find(v17, fname, tpl)
        rec = {"id": key, "file": fname, "found": hit is not None, "values": vals}
        if hit:
            rec.update(line=hit["line"], quote=hit["quote"],
                       numbers=[{"printed": p, "value": x, "conventions": QC.conventions(p, x, False),
                                 "verdict": "confirma" if QC.conventions(p, x, False) else "corrige",
                                 "correct": None if QC.conventions(p, x, False) else QC.correct(p, x)} for p, x in zip(hit["printed"], vals)])
        cps = []
        for f, t in counterparts:
            h = find(v17, f, t)
            cps.append({"file": f, "found": h is not None, **(h or {"template": t})})
        rec["counterparts"] = cps
        rec["verdict"] = "confirma" if hit and all(n["verdict"] == "confirma" for n in rec["numbers"]) and all(c["found"] for c in cps) else "revisar"
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# (b) remisiones al suplemento
# ---------------------------------------------------------------------------
REG = [
    # (archivo, patron de la frase, seccion, afirmacion, etiquetas que deben estar en la seccion, textos que deben estar en la seccion)
    ("sec1_introduction.tex", r"We report those results in \\supp\{5\} and \\supp\{6\}", ("S5",),
     "la ventana (S_theta), medida y retirada", ("tab:localpower02",), ("The smoothing window",)),
    ("sec1_introduction.tex", r"We report those results in \\supp\{5\} and \\supp\{6\}", ("S6",),
     "el segundo canal y el peso adaptativo, medidos y retirados", ("tab:dgp5", "tab:negweight"),
     ("A pre-registered test of a two-channel extension",)),
    ("sec3_theory.tex", r"verified numerically \(\\supp\{7\}\)", ("S7",), "verificacion numerica del caso con tendencia de la consistencia", (),
     ("In the trend case the same argument requires", "0.011", "0.057", "-0.56", "-0.64")),
    ("sec3_theory.tex", r"the replication against the package \(\\supp\{2\}\)", ("S2",), "comprobacion de la replica de SB/SWB frente a bootUR", (),
     ("The replication was checked against the package",)),
    ("appA_proofs.tex", r"\\supp\{7\} reports it", ("S7",), "la comprobacion anterior de la mediana del HAC con otro piloto", ("tab:hacmedian",),
     ("previous bandwidth pilot",)),
    ("appB_critical_values.tex", r"critical values of \\RMGLS\{\} \(\\supp\{8\}\)", ("S8",), "valores criticos de MSB-B (y de S_theta)",
     ("tab:critB", "tab:critMSBse"), ()),
    ("sec4_montecarlo.tex", r"registered predictions are in \\supp\{10\}", ("S10",), "protocolos, enmiendas y predicciones", (), ("protocols/",)),
    ("sec4_montecarlo.tex", r"full comparison, with ADF and PP, is in \\supp\{1\}", ("S1",), "potencia a tamano igualado con ADF y PP",
     ("tab:dgp1", "tab:ctpower"), ("ADF", "PP")),
    ("sec4_montecarlo.tex", r"statistic of \\supp\{5\}", ("S5",), "la familia suavizada con theta = 0.02", ("tab:localpower02",), ("For a window fraction",)),
    ("sec4_montecarlo.tex", r"tables are in \\supp\{2\}", ("S2",), "tablas celda por celda de correlacion serial",
     ("tab:serial", "tab:serialasy", "tab:boot", "tab:fixedbsize"), ()),
    ("sec4_montecarlo.tex", r"other GLS tests \(\\supp\{2\}\)", ("S2",), "potencia ajustada de MSB-B bajo correlacion serial", ("tab:serialpower",), ()),
    ("sec4_montecarlo.tex", r"\\supptab\{2\.2\} gives mean absolute deviations", ("S2.2",), "la comparacion iid/asintotica en caminos independientes (A12)",
     ("tab:serialasy",), ()),
    ("sec4_montecarlo.tex", r"\(\\supptab\{2\.3\}\)", ("S2.3",), "tasa por retardo elegido por la MAIC (0.103 y 0.039)", ("tab:lag",), ()),
    ("sec4_montecarlo.tex", r"cell by cell in \\supptab\{2\.4\}", ("S2.4",), "tamano de MZ_t-GLS con las cinco calibraciones, celda por celda",
     ("tab:boot",), ()),
    ("sec4_montecarlo.tex", r"variance breaks \(\\supp\{4\}\)", ("S4",), "SB y SWB no evaluados bajo quiebres de varianza", ("tab:dgp3", "tab:awb"),
     ("were not evaluated under variance breaks",)),
    ("sec4_montecarlo.tex", r"for DF-GLS \(\\supp\{3\}\)", ("S3",), "condicion inicial (0.818 frente a 0.643)", ("tab:initial",), ("0.818", "0.643")),
    ("sec4_montecarlo.tex", r"preferable to every test considered here\s*\(\\supp\{4\}\)", ("S4",), "quiebres de media y ZA", ("tab:dgp2",), ("endogenous-break test",)),
    ("sec4_montecarlo.tex", r"detections and latency \(\\supp\{9\}\)", ("S9",), "la aplicacion completa", ("tab:fp", "tab:deviations"), ("Design", "Results")),
]
TABLE_NUMBERS = {"tab:serialasy": "S2.2", "tab:lag": "S2.3", "tab:boot": "S2.4"}
LAG_TABLE_VALUES = ("0.103", "0.039")


def supp_sections(tex):
    pos = [(m.start(), m.group(1)) for m in re.finditer(r"\\section\{[^}]*\}\\label\{supp:(s\d+)\}", tex)]
    out = {}
    for i, (a, sid) in enumerate(pos):
        b = pos[i + 1][0] if i + 1 < len(pos) else len(tex)
        out[sid.upper()] = tex[a:b]
    return out


def part_b(v17, supp_json):
    tex = open(os.path.join(SUPP, "supplement.tex"), encoding="utf-8").read()
    secs = supp_sections(tex)
    labels = supp_json["numbering"]["tables"]
    all_refs = []
    for fname, t in v17.files.items():
        if not fname.endswith(".tex") or fname == "main.tex":
            continue
        for m in re.finditer(r"\\supp(tab)?\{([\d.]+)\}", t):
            all_refs.append({"file": fname, "line": t[:m.start()].count("\n") + 1, "ref": ("S" + m.group(2))})
    rows, used = [], set()
    for fname, rx, targets, claim, need_labels, need_text in REG:
        text = v17.files[fname]
        m = re.search(rx, text)
        line = None if m is None else text[:m.start()].count("\n") + 1
        checks = []
        for tgt in targets:
            sid = tgt.split(".")[0]
            body = secs.get(sid, "")
            checks.append({"check": "existe %s" % tgt, "holds": (sid in secs) if "." not in tgt else (tgt in labels.values())})
            for lab in need_labels:
                num = labels.get(lab)
                if "." in tgt:
                    checks.append({"check": "%s es %s" % (lab, tgt), "holds": num == tgt})
                elif num:
                    checks.append({"check": "%s (%s) en %s" % (lab, num, sid), "holds": num.split(".")[0] == sid})
            for s in need_text:
                if "." not in tgt:
                    checks.append({"check": "texto '%s' en %s" % (s, sid), "holds": s in body or s.replace("-", "$-$") in body or
                                   any(s in open(os.path.join(SUPP, "tables", f), encoding="utf-8").read()
                                       for f in re.findall(r"\\input\{tables/([^}]*)\}", body) for f in [f + ".tex"])})
        if "tab:lag" in need_labels:
            lag = open(os.path.join(SUPP, "tables", "tab_lag_audit15.tex"), encoding="utf-8").read()
            checks += [{"check": "S2.3 contiene %s" % v, "holds": v in lag} for v in LAG_TABLE_VALUES]
        if m is not None:
            used.update((fname, line + k) for k in range(0, 2))
        rows.append({"file": fname, "line": line, "found": m is not None, "targets": list(targets), "claim": claim, "checks": checks,
                     "verdict": "coincide" if m is not None and all(c["holds"] for c in checks) else "revisar"})
    covered = {(r["file"], r["line"]) for r in rows if r["line"]}
    unregistered = [r for r in all_refs if not any(r["file"] == f and abs(r["line"] - l) <= 1 for f, l in covered)]
    stub = re.search(r"\\def\\@currentlabel\{S2\.1\}", v17.files["main.tex"])
    return {"refs_in_body": all_refs, "registry": rows, "unregistered": unregistered,
            "tab_serial_stub_in_main": stub is not None,
            "tab_fixedb_note_uses_cref": "\\cref{tab:serial}" in v17.files.get("tables/tab_fixedb_note_audit15.tex", "")}


# ---------------------------------------------------------------------------
# (c) cifras retiradas
# ---------------------------------------------------------------------------
RETIRED = (("0.333", r"(?<![\d.])0\.333\d*"), ("6.9 %", r"(?<![\d.])6\.9(?![\d])"), ("0.6 %", r"(?<![\d.])0\.6\s*(?:\\?%|per\s*cent)"),
           ("doubles", r"\bdoubl(?:es|ed|ing)\b"))


def part_c(v17):
    files = {("v17", k): t for k, t in v17.files.items() if k.endswith((".tex", ".md"))}
    for dp, _, fs in os.walk(SUPP):
        for fn in fs:
            if fn.endswith((".tex", ".md")):
                p = os.path.join(dp, fn)
                files[("supplementary", os.path.relpath(p, SUPP).replace("\\", "/"))] = open(p, encoding="utf-8").read()
    hits = []
    for (where, name), text in sorted(files.items()):
        for lab, rx in RETIRED:
            for m in re.finditer(rx, text):
                ln = text[:m.start()].count("\n") + 1
                if name.startswith("protocols/"):
                    kind = "protocolo (registro historico)"
                elif name.startswith("CHANGELOG"):
                    kind = "changelog del v17 (registra la retirada)"
                else:
                    kind = "texto o tabular"
                hits.append({"figure": lab, "where": where, "file": name, "line": ln, "match": m.group(0), "kind": kind,
                             "context": re.sub(r"\s+", " ", text[max(0, m.start() - 90):m.end() + 70])})
    body = [h for h in hits if h["kind"] == "texto o tabular"]
    return {"hits": hits, "in_text_or_tables": body,
            "counts": {lab: sum(1 for h in body if h["figure"] == lab) for lab, _ in RETIRED}}


# ---------------------------------------------------------------------------
# Incoherencias arrastradas por los textos del v16
# ---------------------------------------------------------------------------
def carried(v17):
    tex = open(os.path.join(SUPP, "supplement.tex"), encoding="utf-8").read()
    tabs = {f: open(os.path.join(SUPP, "tables", f), encoding="utf-8").read() for f in os.listdir(os.path.join(SUPP, "tables"))}
    out = []
    reg2 = L.a12()["exact_region_20000"]
    upper = QC.TB.fdec(reg2[1], 5, "binary")
    for m in re.finditer(r"\[0\.0470, 0\.0531\]", tex):
        out.append({"issue": "extremo superior de la region para 2x10^4 caminos escrito 0.0531; el v17 usa %s" % upper,
                    "where": "supplement.tex:%d" % (tex[:m.start()].count("\n") + 1),
                    "context": re.sub(r"\s+", " ", tex[max(0, m.start() - 80):m.end() + 20])})
    for m in re.finditer(r"B = 399", tex):
        out.append({"issue": "replicas del AWB escritas B = 399; def:awb del v17 usa R (la B es el ancho de banda de Bartlett)",
                    "where": "supplement.tex:%d" % (tex[:m.start()].count("\n") + 1), "context": re.sub(r"\s+", " ", tex[max(0, m.start() - 80):m.end() + 20])})
    for f, t in sorted(tabs.items()):
        for m in re.finditer(r"B = 399", t):
            out.append({"issue": "replicas del AWB escritas B = 399 (tabular)", "where": "tables/%s" % f,
                        "context": re.sub(r"\s+", " ", t[max(0, m.start() - 60):m.end() + 20])})
    for m in re.finditer(r"\\gamma = 0\.01", tex):
        out.append({"issue": "parametro del AWB escrito gamma; el v17 usa eta", "where": "supplement.tex:%d" % (tex[:m.start()].count("\n") + 1),
                    "context": re.sub(r"\s+", " ", tex[max(0, m.start() - 80):m.end() + 30])})
    return out


def main():
    v17 = C.v17()
    sj = C.read_json("supplement_v17_audit16.json")
    a, q = part_a(v17), qualitative()
    b = part_b(v17, sj)
    c = part_c(v17)
    d = carried(v17)
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 6, lectura E6.7",
           "inputs": {"v17_zip_sha256": v17.sha256, "supplement_tex_sha256": C.sha256_file(os.path.join(SUPP, "supplement.tex")),
                      "supplement_json_commit": sj["provenance"]["commit"]},
           "a_abstract": a, "a_qualitative": q, "b_supp_refs": b, "c_retired": c, "carried_from_v16": d,
           "summary": {"a_confirma": sum(1 for x in a if x["verdict"] == "confirma"), "a_total": len(a),
                       "qualitative_fail": [x["claim"] for x in q if x["holds"] is False],
                       "b_refs": len(b["refs_in_body"]), "b_registered": len(b["registry"]),
                       "b_coincide": sum(1 for x in b["registry"] if x["verdict"] == "coincide"), "b_unregistered": len(b["unregistered"]),
                       "c_counts": c["counts"], "carried": len(d)}}
    C.write_result(OUT, out, __file__)
    for x in a:
        print("(a)", x["id"], x["verdict"], [(n["printed"], n["verdict"]) for n in x.get("numbers", [])], [c["found"] for c in x["counterparts"]])
    for x in q:
        print("(a*)", x["claim"], x["holds"], x["value"])
    for x in b["registry"]:
        print("(b)", x["file"], x["line"], x["targets"], x["verdict"], [c["check"] for c in x["checks"] if not c["holds"]])
    print("(b) sin registrar:", b["unregistered"], "| stub tab:serial en main.tex:", b["tab_serial_stub_in_main"])
    for h in c["in_text_or_tables"]:
        print("(c)", h["figure"], h["where"], h["file"], h["line"], "|", h["context"][:160])
    print("(c) otras (protocolos/changelog):", sum(1 for h in c["hits"] if h["kind"] != "texto o tabular"))
    for x in d:
        print("(v16)", x["issue"], x["where"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
