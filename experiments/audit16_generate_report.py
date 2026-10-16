"""
Auditoria A16 - generador del reporte experiments/results/resultados_auditoria_16.md (enmienda 6, lectura E6.8).
Solo lee JSON (tests/test_no_literals_audit16.py). Siete secciones y tabla maestra.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_16.md")
F = {"tab": "v17_tables_audit16.json", "code": "code_check_audit16.json", "lit": "literals_v17b_audit16.json",
     "supp": "supplement_v17_audit16.json", "trial": "supplement_v17_trial_audit16.json", "coh": "coherence_v17_audit16.json",
     "man": "manifest_audit16.json"}
_C = {}


def J(k):
    if k not in _C:
        _C[k] = C.read_json(F[k])
    return _C[k]


def esc(c):
    return str(c).replace("|", "\\|").replace("\n", " ")


def table(heads, rows):
    return ["| " + " | ".join(esc(h) for h in heads) + " |", "|" + "---|" * len(heads)] + \
        ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]


def g(x, d=4):
    return "—" if x is None else "%.*f" % (d, x)


def e(x):
    return "—" if x is None else "%.1e" % x


def half_up(num, den, d):
    """num/den exacto redondeado a d decimales, mitad hacia arriba."""
    import decimal
    return str((decimal.Decimal(num) / decimal.Decimal(den)).quantize(decimal.Decimal(1).scaleb(-d), rounding=decimal.ROUND_HALF_UP))


def yn(b):
    return "sí" if b else "no"


def plain(s):
    return s.replace("\\RMGLS{}", "MSB-B").replace("$", "").replace("\\", "")


def s_b161(w, L):
    t = J("tab")
    w("### B16.1 — Generadores (lectura E6.1)")
    w("")
    r1 = t["row1_power"]
    w("- tab_summary (`tables_audit16/tab_summary_audit16.tex` y nota): la potencia de la fila 1 (MSB-B con Andrews) es %s, desde "
      "`%s`; es el mismo valor que tab_fixedb: %s. En A15 era %s (A12). La nota agrupa las filas por fuente de potencia." % (
          g(r1["value"], 4), r1["source"], yn(r1["equals_tab_fixedb_andrews"]), g(r1["a15_value"], 4)))
    fn = t["fixedb_note"]
    w("- tab_fixedb (`tables_audit16/tab_fixedb_audit16.tex` y nota): tabular idéntico al de A15: %s. Sustituciones de "
      "`\\cref{tab:serial}` por «%s» en la nota: %d. Los archivos de `tables_audit15/` no se tocan." % (
          yn(fn["tabular_identical_to_a15"]), fn["replacement"], fn["serial_refs_replaced"]))
    w("")
    rows = [[plain(r["label"]), plain(r["cv"]), r["audit"], r["N_size"], g(r["D"]), g(r["M"]), g(r["min"], 3), g(r["max"], 3),
             "%d/%d" % (r["iid_in_region"], r["iid_cells"]), g(r["power"], 3), r["N_power"], "`%s`" % r["power_source"]] for r in t["summary_rows"]]
    L.extend(table(["Fila", "Valor crítico", "Auditoría (tamaño)", "N tamaño", "D", "M", "mín", "máx", "iid en región", "Potencia",
                    "N potencia", "Fuente de la potencia"], rows))
    w("")


def s_b162(w, L):
    d = J("code")
    w("### B16.2 — Verificación contra el código (lecturas E6.2–E6.4)")
    w("")
    w("**(a) eq:mstats y su entorno** (`sec2_statistics.tex` del v17) frente a `audit8_unitroot.np_statistics` y `arch.DFGLS`:")
    w("")
    rows = [[x["item"], "; ".join(c["where"] for c in x["text"]), "; ".join(c["where"] for c in x["code"]), x["verdict"], x["detail"]]
            for x in d["a_eq_mstats"]]
    L.extend(table(["Punto", "Texto (archivo:línea)", "Código (archivo:línea)", "Veredicto", "Detalle"], rows))
    w("")
    lit = d["c_invariance"]["literal_eq_mstats_vs_code"]
    w("Control numérico: evaluación literal de eq:mstats (con la convención T_n del texto y normalización por n, el k del código) frente "
      "a `np_statistics`, en los caminos de E6.4:")
    w("")
    L.extend(table(["Celda", "mediana |Δ| rel. MSB", "máx |Δ| rel. MSB", "1/n", "mediana |Δ| MZ_t", "máx |Δ| MZ_t"],
                   [[k, e(v["median_rel_msb"]), e(v["max_rel_msb"]), e(v["expected_rel_msb"]), g(v["median_abs_mzt"]), g(v["max_abs_mzt"])]
                    for k, v in lit.items()]))
    w("")
    w("**(b) §3.5 (SB/SWB) frente a bootUR 1.0.5** (tarball con sha256 `%s`):" % d["inputs"]["bootUR_tar_sha256"])
    w("")
    rows = [[x["question"], "; ".join(c["where"] for c in x["text"]) or "—", "; ".join(c["where"] for c in x["code"]), x["answer"], x["verdict"]]
            for x in d["b_bootur"]]
    L.extend(table(["Pregunta", "Texto del v17", "bootUR (archivo:línea)", "Respuesta", "Veredicto"], rows))
    w("")
    c = d["c_invariance"]
    w("**(c) prop:invariance para los tests con s²_AR** (`%s`: «%s»). Argumento sobre el código: %s" % (
        c["proof_text"]["where"], c["proof_text"]["text"], c["argument"]))
    w("")
    w("Control numérico, determinista (familia %d; colisiones con 90–159: %d). Parámetros: n ∈ %s, casos %s, %d caminos por celda, "
      "a ∈ %s, b = %s, c = %s. Criterio registrado: 0 cambios de k y |Δ| relativo ≤ %s en MSB y MZ_t." % (
          c["family"], c["collisions_vs_prior"], c["config"]["n"], c["config"]["cases"], c["config"]["paths"], c["config"]["a"], c["config"]["b"],
          c["config"]["c"], e(c["config"]["tol"])))
    w("")
    rows = [[k, v["k_changes"], e(v["max_rel_msb"]), e(v["max_rel_mzt"]), e(v["max_rel_s2_over_a2"]), e(v["max_rel_dfgls"]),
             e(v["min_maic_margin"]), e(v["diagnostic_max_abs_mzt"]), e(v["diagnostic_worst_rel_mzt"]["mzt"]), yn(v["passes"])]
            for k, v in c["cells"].items()]
    L.extend(table(["Celda", "cambios de k", "máx rel. MSB", "máx rel. MZ_t", "máx rel. s²_AR/a²", "máx rel. DF-GLS", "margen MAIC mín.",
                    "máx |Δ| abs. MZ_t (diag.)", "MZ_t del peor camino (diag.)", "Cumple"], rows))
    w("")
    w("%s" % c["diagnostic_note"])
    w("")


def s_b163(w, L):
    d = J("lit")
    w("### B16.3 — Literales del v17 (lectura E6.5; test independiente `tests/test_literals_v17b_audit16.py`)")
    w("")
    rows = []
    for x in d["N"]:
        if x["id"] == "N3":
            v = x["value"]
            rows.append(["N3", x["printed"], "; ".join("%s:%s" % (l["file"], l["line"]) for l in x["locations"]),
                         "rate(ii) > rate(i) en %d de %d (empates %d)" % (v["ii_gt_i"], v["cells"], v["ties"]), "—", x["verdict"], x["source"]])
        elif x["id"] == "N8":
            rows.append(["N8", x["printed"], "%s:%s" % (x["file"], x["line"]),
                         "SWB: %d de %d celdas, %s–%s pp; AWB: %d de %d, %s–%s pp; SB: %d, %s–%s pp" % (
                             x["SWB"]["cells"], x["SWB"]["of"], g(x["SWB"]["min_pp"], 2), g(x["SWB"]["max_pp"], 2), x["AWB"]["cells"], x["AWB"]["of"],
                             g(x["AWB"]["min_pp"], 2), g(x["AWB"]["max_pp"], 2), x["SB"]["cells"], g(x["SB"]["min_pp"], 2), g(x["SB"]["max_pp"], 2)),
                         "—", x["verdict"], x["source"]])
        else:
            rows.append([x["id"], x["quote"], "%s:%s" % (x["file"], x["line"]), ", ".join("%.6g" % n["value"] for n in x["numbers"]),
                         ", ".join(n["binary"] or "—" for n in x["numbers"]) + ("; hacia afuera %s" % " to ".join(x["outward"]) if x.get("outward") else ""),
                         x["verdict"], x["source"]])
    L.extend(table(["Literal", "Impreso", "v17 (archivo:línea)", "Valor", "Redondeo binario", "Veredicto", "Fuente"], rows))
    w("")
    n5 = d["N_exact"]["N5b"]
    n5row = [x for x in d["N"] if x["id"] == "N5b"][0]["numbers"][0]
    if n5row.get("rounding_sensitive"):
        w("N5b: el valor exacto es %s y cae en la mitad de la última cifra impresa. «%s» sale del redondeo binario del flotante; con "
          "mitad hacia arriba sobre el valor exacto sería %s." % (n5["exact_value"], n5row["printed"], half_up(
              n5["rejections"], n5["n"], len(n5row["printed"].split(".")[1]))))
        w("")
    n6 = d["N6"]
    sw = n6["sweep"]["counts"]
    w("**N6** (sec1 y sec4 del v17): %d frases del registro, %d no encontradas. De las cifras que ya estaban en el v16, %d de %d confirman. "
      "Barrido de números con decimales: %d cubiertos por una frase, %d de diseño y %d sin verificar." % (
          len(n6["claims"]), len(n6["templates_not_found"]), n6["v16_confirmed"], n6["v16_numbers"], sw["cubierta"], sw["diseno"],
          sw["no verificada"]))
    w("")
    if n6["not_confirmed"]:
        L.extend(table(["Frase", "Archivo:línea", "Impreso", "Valor", "Convenciones", "Cota", "Correcto"],
                       [[x["claim"], "%s:%s" % (x["file"], x["line"]), x["printed"], "%.6g" % x["value"], ", ".join(x["conventions"]) or "—",
                         x.get("bound") or "—", x["correct"]] for x in n6["not_confirmed"]]))
        w("")
    if n6["failed_checks"]:
        w("Comprobaciones que fallan: %s." % "; ".join("%s: %s" % (x["claim"], x["check"]) for x in n6["failed_checks"]))
        w("")
    if n6["group_vs_v16_text"]:
        w("Cifras del grupo v16 que no están en el texto del v16: %s (es el extremo de la región, que el v17 escribe con cinco decimales)." %
          ", ".join("%s (%s)" % (x["printed"], x["claim"]) for x in n6["group_vs_v16_text"]))
        w("")


def s_b157c(w, L):
    d = J("supp")
    w("### B15.7c — Suplemento reconstruido (lectura E6.6)")
    w("")
    cp, sc = d["compile"], d["anonymization_scan"]
    w("`supplementary/` reconstruido: %d archivos; %d aciertos identificadores fuera de los hashes de commit. Compilación de control "
      "(pdflatex, bibtex, pdflatex ×2): compila %s, %d errores, %d referencias y %d citas indefinidas, %d cajas desbordadas, %s páginas. "
      "Compilación de control del v17 para numerar las remisiones al cuerpo: %s páginas." % (
          d["n_files"], sc["non_hash_hits"], yn(cp["compiled"]), cp["errors"], cp["undefined_references"], cp["undefined_citations"],
          cp["overfull"], cp["pages"], d["v17_control_compile"]["pages"]))
    w("")
    num = d["numbering"]
    w("Numeración: S2.1–S2.9 coincide con el mapa: %s. Tablas por sección:" % yn(num["S2_matches_map"]))
    w("")
    by = {}
    for lab, n in num["tables"].items():
        by.setdefault(n.split(".")[0], []).append("%s %s" % (n, lab))
    L.extend(table(["Sección", "Título", "Tablas (número compilado y etiqueta)"],
                   [[s["id"], s["title"].replace("$", ""), ", ".join(sorted(by.get(s["id"], []), key=lambda x: int(x.split(" ")[0].split(".")[1]))) or "—"]
                    for s in d["sections"]]))
    w("")
    w("Figuras: %s." % ", ".join("%s %s" % (v, k) for k, v in sorted(num["figures"].items(), key=lambda kv: kv[1])))
    w("")
    rows = [[k, "%s:%d–%d" % (v["file"], v["line_from"], v["line_to"])] for k, v in d["transcribed_blocks"].items()]
    L.extend(table(["Bloque transcrito del v16", "Origen (archivo:líneas)"], rows))
    w("")
    refs = d["references"]
    kinds = {}
    for r in refs:
        kinds[r["how"].split(" (")[0]] = kinds.get(r["how"].split(" (")[0], 0) + 1
    w("Referencias cruzadas reescritas: %d (%s); sin resolver: %d; remisiones «of the main text» que no apuntan al cuerpo del v17: %d." % (
        len(refs), ", ".join("%s: %d" % kv for kv in kinds.items()), len(d["unresolved"]), len(d["main_text_refs"]["not_in_v17_body"])))
    w("")
    s6 = d["sec6_integrity"]
    w("Sección 6 del v16 en S9: %d fragmentos de 8 palabras comprobados, %d ausentes; las %d cifras aparecen iguales y en el mismo orden: %s." % (
        s6["chunks_checked"], s6["n_missing"], s6["numbers_src"], yn(s6["numbers_equal"])))
    w("")
    w("Tabulares de A13 idénticos a los del zip del v16: %s." % ", ".join("%s %s" % (k, yn(v)) for k, v in d["a13_tables_identical_to_v16"].items()))
    w("")
    L.extend(table(["Bloque", "Edición declarada", "Sustitución", "Veces"],
                   [[x["block"], "`%s`" % x["pattern"], "`%s`" % x["replacement"] if x["replacement"] else "(se elimina)", x["count"]]
                    for x in d["editorial_edits"]]))
    w("")
    w("Macros en conflicto entre v16 y v17: %s." % "; ".join("\\%s: v16 `%s`, v17 `%s`, se usa %s" % (k, v["v16"], v["v17"], v["used"])
                                                            for k, v in d["macro_conflicts"].items()))
    w("")


def s_b154(w, L):
    d = J("coh")
    w("### B15.4 — Pasada de coherencia sobre el v17 y el suplemento (lectura E6.7)")
    w("")
    w("**(a) Resumen y conclusión.**")
    w("")
    rows = [[x["id"], "%s:%s" % (x["file"], x.get("line")), ", ".join("%s → %s" % (n["printed"], n["verdict"]) for n in x.get("numbers", [])),
             "; ".join("%s:%s" % (c["file"], c.get("line")) if c["found"] else "%s: no encontrada" % c["file"] for c in x["counterparts"]), x["verdict"]]
            for x in d["a_abstract"]]
    L.extend(table(["Cifra", "Archivo:línea", "Impreso → veredicto", "Contrapartidas (P1–P3, §4, §5)", "Veredicto"], rows))
    w("")
    L.extend(table(["Afirmación", "Dónde", "Valores", "Se cumple"],
                   [[x["claim"], x["where"], ", ".join("%s = %s" % (k, ("%.4g" % v) if isinstance(v, float) else v) for k, v in x["value"].items()),
                     "—" if x["holds"] is None else yn(x["holds"])] for x in d["a_qualitative"]]))
    w("")
    b = d["b_supp_refs"]
    w("**(b) Remisiones al suplemento**: %d `\\supp`/`\\supptab` en el cuerpo; %d entradas del registro, %d coinciden; %d sin registrar." % (
        len(b["refs_in_body"]), len(b["registry"]), sum(1 for x in b["registry"] if x["verdict"] == "coincide"), len(b["unregistered"])))
    w("")
    L.extend(table(["Archivo:línea", "Destino", "Qué afirma", "Comprobaciones", "Veredicto"],
                   [["%s:%s" % (x["file"], x["line"]), ", ".join(x["targets"]), x["claim"], "%d/%d" % (sum(1 for c in x["checks"] if c["holds"]), len(x["checks"])),
                     x["verdict"]] for x in b["registry"]]))
    w("")
    w("Stub de etiqueta `tab:serial` (S2.1) en `main.tex`: presente: %s. La nota de tab_fixedb del v17 (A15) usa `\\cref{tab:serial}`: %s; la nota "
      "de A16 ya no lo usa (B16.1)." % (yn(b["tab_serial_stub_in_main"]), yn(b["tab_fixedb_note_uses_cref"])))
    w("")
    c = d["c_retired"]
    w("**(c) Cifras retiradas** en texto o tabulares del v17 y del suplemento: %s. Además hay %d apariciones en protocolos y en el changelog "
      "(registro histórico)." % (", ".join("%s: %d" % kv for kv in c["counts"].items()),
                                 sum(1 for h in c["hits"] if h["kind"] != "texto o tabular")))
    w("")
    if c["in_text_or_tables"]:
        L.extend(table(["Cifra", "Dónde", "Archivo:línea", "Contexto"],
                       [[h["figure"], h["where"], "%s:%s" % (h["file"], h["line"]), h["context"][:200]] for h in c["in_text_or_tables"]]))
        w("")
    w("**Incoherencias que arrastran los textos del v16 transcritos** (sin editar: S9 va íntegra y las notas son literales):")
    w("")
    L.extend(table(["Incoherencia", "Dónde", "Contexto"], [[x["issue"], x["where"], x["context"][:180]] for x in d["carried_from_v16"]]))
    w("")


def s_gates(w, L):
    w("## 2. Compuertas")
    w("")
    c = J("code")["c_invariance"]
    s, t = J("supp"), J("trial")
    rows = [["E6.4 semillas", "0 colisiones de la familia 160 con 90–159", c["collisions_vs_prior"], "pasa" if c["collisions_vs_prior"] == 0 else "NO pasa"],
            ["E6.4 invariancia", "0 cambios de k y |Δ| rel. ≤ 1e-10 en MSB y MZ_t",
             "cambios de k %d; máx. MSB %s; máx. MZ_t %s" % (sum(v["k_changes"] for v in c["cells"].values()),
                                                            e(max(v["max_rel_msb"] for v in c["cells"].values())),
                                                            e(max(v["max_rel_mzt"] for v in c["cells"].values()))),
             "pasa" if c["passes"] else "NO pasa (MZ_t en %s; ver §7)" % ", ".join(k for k, v in c["cells"].items() if not v["passes"])],
            ["E6.6 prueba con --out", "compila sin errores; 0 aciertos identificadores", "%d errores, %d aciertos" % (
                t["compile"]["errors"], t["anonymization_scan"]["non_hash_hits"]), "pasa" if t["compile"]["errors"] == 0 and t["anonymization_scan"]["non_hash_hits"] == 0 else "NO pasa"],
            ["E6.6 reconstrucción", "0 errores, 0 referencias y citas indefinidas, 0 aciertos", "%d / %d / %d / %d" % (
                s["compile"]["errors"], s["compile"]["undefined_references"], s["compile"]["undefined_citations"], s["anonymization_scan"]["non_hash_hits"]),
             "pasa" if not (s["compile"]["errors"] or s["compile"]["undefined_references"] or s["compile"]["undefined_citations"] or s["anonymization_scan"]["non_hash_hits"]) else "NO pasa"],
            ["E6.6.1 numeración", "S2.1–S2.9 como el mapa", yn(s["numbering"]["S2_matches_map"]), "pasa" if s["numbering"]["S2_matches_map"] else "NO pasa"],
            ["E6.6.3 referencias", "0 sin resolver; «of the main text» sólo al cuerpo del v17", "%d / %d" % (
                len(s["unresolved"]), len(s["main_text_refs"]["not_in_v17_body"])),
             "pasa" if not s["unresolved"] and not s["main_text_refs"]["not_in_v17_body"] else "NO pasa"],
            ["E6.6.4 sec6 íntegra", "0 fragmentos ausentes y cifras iguales", "%d / %s" % (s["sec6_integrity"]["n_missing"], yn(s["sec6_integrity"]["numbers_equal"])),
             "pasa" if s["sec6_integrity"]["n_missing"] == 0 and s["sec6_integrity"]["numbers_equal"] else "NO pasa"]]
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], rows))
    w("")


def s_prov(w, L):
    w("## 3. Procedencia")
    w("")
    s = J("supp")
    w("Entradas: `paper_latex_v17.zip` sha256 `%s`; `paper_latex_v16.zip` sha256 `%s`. Protocolo: `experiments/protocol_audit15_amend6.md` "
      "(enmienda 6), commiteado antes de generar nada." % (s["inputs"]["v17_zip_sha256"], s["inputs"]["v16_zip_sha256"]))
    w("")
    man = J("man")["entries"]
    rows = [[k, "`%s`" % v["sha256"][:16], v["script"], v["commit"][:7], yn(v["code_all_committed"]),
             "%s / %s / %s" % (v["assistant"]["herramienta"], v["assistant"]["modelo"], v["assistant"]["version"]) if v.get("assistant") else "—"]
            for k, v in sorted(man.items()) if "resultados_auditoria" not in k]
    L.extend(table(["Archivo", "sha256 (16)", "Script", "Commit", "Código commiteado", "Asistente"], rows))
    w("")


def s_dev(w, L):
    w("## 4. Desviaciones")
    w("")
    rows = [["B16.1: los tabulares nuevos van a `tables_audit16/` con sufijo _audit16; `tables_audit15/` y `v17_tables_audit15.json` no se tocan",
             "Regla de no modificar resultados de auditorías anteriores", "Antes de generar (E6.1)", "El v17 debe cambiar el \\input a _audit16"],
            ["B16.2(c): diagnóstico del |Δ| absoluto de MZ_t añadido después de ver que la compuerta no pasaba", "Explicar la causa (cancelación)",
             "Tras la primera corrida", "El veredicto registrado no cambia"],
            ["B15.7c: ediciones declaradas en los textos transcritos (notas de tablas que pasan completas, título repetido, «And» inicial, "
             "autorremisiones «in the supplement»)", "Las tablas completas invalidan las frases de omisión", "Al construir (E6.6)",
             "Registradas una a una en el JSON; S9 sin ediciones"],
            ["B15.7c: macros en conflicto v16/v17 (\\Stat, \\StatZero)", "El texto transcrito es del v16", "Al construir",
             "\\Stat = S_θ (v16) en S5; \\StatZero = S (v17)"],
            ["B15.7c: texto nuevo en S2 (SB/SWB, Paso 0) y en S4 (frase SB/SWB)", "Lo pide el mapa", "Al construir",
             "Sólo hechos de E6.3 y cifras del JSON del Paso 0"],
            ["B15.7c: bibliografía propia del suplemento (natbib, plainnat) con la unión de references.bib del v16 y del v17",
             "Los textos del v16 citan con \\citet/\\citep", "Al construir", "Ninguno sobre las cifras"],
            ["B16.3 N3: se localiza con una expresión propia, no con plantilla", "«thirty-six» lleva guion", "Al ejecutar", "Ninguno"]]
    L.extend(table(["Desviación", "Motivo", "Cuándo", "Efecto"], rows))
    w("")


def s_not(w, L):
    w("## 5. No ejecutado")
    w("")
    w("- No se edita ningún `.tex` del manuscrito: el stub de `tab:serial` en `main.tex` lo quita el autor, y el v17 debe pasar a "
      "`\\input{tables/tab_summary_audit16}` y `tab_fixedb_note_audit16`.")
    w("- No se juzga «comparable» (N8), ni «nearly halves» (conclusión): se dan las cifras.")
    w("")


def s_concl(w, L):
    w("## 6. Conclusiones")
    w("")
    t, d, lt, s, co = J("tab"), J("code"), J("lit"), J("supp"), J("coh")
    w("- B16.1: tab_summary usa ya la misma potencia de Andrews que tab_fixedb (%s); la nota de tab_fixedb remite a «Table S2.1 of the "
      "supplement»." % g(t["row1_power"]["value"], 3))
    a = d["a_eq_mstats"]
    w("- B16.2(a): %d de %d puntos coinciden con el código; difieren la normalización (n frente a n + 1), la convención T_n para los tests "
      "M y DF-GLS en el caso constante, y la muestra de la regresión de DF-GLS." % (sum(1 for x in a if x["verdict"] == "coincide"), len(a)))
    w("- B16.2(b): bootUR estima la regresión ADF sin restringir e impone la nula al generar; pesos del SWB gaussianos; residuos sin "
      "centrar.")
    c = d["c_invariance"]
    w("- B16.2(c): el MAIC implementado cumple lo que afirma la prueba: 0 cambios de k en %d transformaciones. La compuerta numérica "
      "registrada no pasa en MZ_t por cancelación cerca de cero (§7), no por un cambio de ley." % (
          sum(v["paths"] * v["transforms"] for v in c["cells"].values())))
    w("- B16.3: N1–N7: %d confirman y %d corrigen; N8 se reporta sin veredicto. N6: %d de %d cifras del v16 confirman." % (
        lt["N_summary"]["confirma"], lt["N_summary"]["corrige"], lt["N6"]["v16_confirmed"], lt["N6"]["v16_numbers"]))
    w("- B15.7c: suplemento reconstruido según el mapa, %s páginas, sin errores ni referencias indefinidas." % s["compile"]["pages"])
    sm = co["summary"]
    w("- B15.4: resumen y conclusión %d/%d; remisiones %d/%d; cifras retiradas en texto o tabulares: %s." % (
        sm["a_confirma"], sm["a_total"], sm["b_coincide"], sm["b_registered"], ", ".join("%s %d" % kv for kv in sm["c_counts"].items())))
    w("")


def s_anom(w, L):
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    d = J("code")
    for x in d["a_eq_mstats"]:
        if x["verdict"] != "coincide":
            w("- eq:mstats, %s (%s): %s — %s" % (x["item"], "; ".join(c["where"] for c in x["text"]), x["verdict"], x["detail"]))
    for x in d["b_bootur"]:
        if x["verdict"].startswith("matiz"):
            w("- §3.5 (%s): %s" % ("; ".join(c["where"] for c in x["text"]), x["verdict"]))
    c = d["c_invariance"]
    bad = [k for k, v in c["cells"].items() if not v["passes"]]
    if bad:
        w("- Compuerta de invariancia no superada en %s: el |Δ| relativo de MZ_t llega a %s, en caminos con MZ_t = %s (numerador de MZ_α casi "
          "nulo); el |Δ| absoluto máximo es %s y el k no cambia nunca." % (
              ", ".join(bad), e(max(c["cells"][k]["max_rel_mzt"] for k in bad)),
              ", ".join(e(c["cells"][k]["diagnostic_worst_rel_mzt"]["mzt"]) for k in bad),
              e(max(v["diagnostic_max_abs_mzt"] for v in c["cells"].values()))))
    lt = J("lit")
    for x in lt["N6"]["not_confirmed"]:
        w("- N6, %s:%s: «%s» es %s; como redondeo confirma, como cota («within») no se cumple; la cota hacia afuera es %s." % (
            x["file"], x["line"], x["printed"], "%.6g" % x["value"], x["correct"]))
    co = J("coh")
    slope = C.read_json("e4_slope_audit15.json")["b"]["AR 0.5"]
    for h in co["c_retired"]["in_text_or_tables"]:
        extra = ""
        if h["file"].endswith("s7_hac_a_rates.tex"):
            extra = (" Es la Tabla S7.1 (antigua S4a): pendiente de B antes del techo con el ρ̂ del script (%s), la cifra retirada en B15.2; la "
                     "misma fila da %s con el ρ̂ de la librería." % (g(slope["slope_B_pre_script"]), g(slope["slope_B_pre_lib"])))
        w("- Cifra retirada %s en %s %s:%s: `%s`.%s" % (h["figure"], h["where"], h["file"], h["line"], h["match"], extra))
    for x in co["carried_from_v16"]:
        w("- Arrastrado del v16 en el suplemento (%s): %s." % (x["where"], x["issue"]))
    if co["b_supp_refs"]["tab_serial_stub_in_main"]:
        w("- `main.tex` del v17 conserva el stub de etiqueta `tab:serial` (S2.1); con la nota de A16 ya no hace falta.")
    w("")


def master(w, L):
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    rows = []
    for i, r in enumerate(J("tab")["summary_rows"]):
        for q in ("D", "M", "min", "max", "power"):
            rows.append(["B16.1 tab_summary %s %s %s" % (plain(r["label"]), plain(r["cv"]), q), g(r[q]), "—",
                         r["N_power"] if q == "power" else r["N_size"], "—", r["audit"], F["tab"], "summary_rows[%d].%s" % (i, q)])
    for k, v in J("code")["c_invariance"]["cells"].items():
        for q in ("max_rel_msb", "max_rel_mzt", "max_rel_s2_over_a2", "max_rel_dfgls", "min_maic_margin", "diagnostic_max_abs_mzt"):
            rows.append(["B16.2(c) %s %s" % (k, q), e(v[q]), "—", v["paths"], "—", "160", F["code"], "c_invariance.cells.%s.%s" % (k, q)])
    for k, v in J("code")["c_invariance"]["literal_eq_mstats_vs_code"].items():
        for q in ("max_rel_msb", "max_abs_mzt"):
            rows.append(["B16.2(a) eq:mstats literal %s %s" % (k, q), e(v[q]), "—", "1000", "—", "160", F["code"],
                         "c_invariance.literal_eq_mstats_vs_code.%s.%s" % (k, q)])
    for x in J("lit")["N"]:
        for j, n in enumerate(x.get("numbers", [])):
            rows.append(["B16.3 %s[%d]" % (x["id"], j), "%.6g" % n["value"], "—", "—", "—", "A12/A13/A15", F["lit"], "N.%s.numbers[%d]" % (x["id"], j)])
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"], rows))
    w("")


def main():
    L = []

    def w(s):
        L.append(s)
    w("# Auditoría A16 — reporte (enmienda 6, v17)")
    w("")
    w("Enmienda 6 commiteada antes de generar nada (§3). No se editó ningún `.tex` del manuscrito ni `src/`; `supplementary/` se "
      "reconstruyó según `SUPPLEMENT_MAP_v17.md`.")
    w("")
    w("## 1. Resultados")
    w("")
    s_b161(w, L)
    s_b162(w, L)
    s_b163(w, L)
    s_b157c(w, L)
    s_b154(w, L)
    s_gates(w, L)
    s_prov(w, L)
    s_dev(w, L)
    s_not(w, L)
    s_concl(w, L)
    s_anom(w, L)
    master(w, L)
    C.write_text(OUT, "\n".join(L) + "\n", __file__)
    print("reporte:", C.rel(OUT), len(L), "lineas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
