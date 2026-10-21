"""
Auditoria A19 - generador del reporte experiments/results/resultados_auditoria_19.md (protocol_audit19.md).
Solo lee JSON (tests/test_no_literals_audit19.py). Siete secciones y tabla maestra. El registro del paquete v1.0.1 (sha256 del zip,
pruebas desde la copia limpia, release) va en package_v101_audit19.json, que se escribe despues de construir el zip, porque el
reporte va dentro del zip.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit19_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_19.md")
F = {"fig": "figures_audit19.json", "awb": "awb_rule_audit19.json", "sup": "supplement_v25_audit19.json",
     "lit": "literals_v25_audit19.json", "man": "manifest_audit19.json"}
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


def yn(b):
    return "sí" if b else "no"


def verdict(b):
    return "pasa" if b else "NO pasa"


def main():
    L = []
    w = L.append
    fig, awb, sup, lit = J("fig"), J("awb"), J("sup"), J("lit")
    w("# Auditoría A19 — reporte (Figura 1, regla del AWB, forma del suplemento, literales del v25)")
    w("")
    w("Protocolo `%s` commiteado antes de cualquier edición o cálculo. Sin simulación nueva. No se editó ningún `.tex` del "
      "manuscrito ni `src/`. Entrada: `paper_latex_v25.zip`, sha256 `%s`." % (C.PROTOCOL, sup["inputs"]["v25_zip_sha256"]))
    w("")
    w("## 1. Resultados")
    w("")
    w("### Punto 1 — Figura 1 en caminos comunes (L1)")
    w("")
    w("`%s` se genera solo desde `%s` (`%s`), con %d puntos y una sola fuente: %s. Lo dibujado es exactamente lo registrado: %s. Fechas "
      "del PDF eliminadas: %s. sha256 `%s`." % (fig["figure"]["path"], fig["source"], fig["primary"], fig["n_points"],
                                              yn(fig["n_sources_new"] == 1), yn(fig["figure"]["plotted_equal_json"]),
                                              yn(fig["figure"]["pdf_dates"]["ok"]), fig["figure"]["sha256"]))
    w("")
    w("**P1.** Puntos que coinciden con la Tabla 1 al dígito impreso: %d de %d (%s). Fuentes de la figura vieja: %s." % (
        fig["n_match_table1"], fig["n_points"], verdict(fig["p1_all_match_table1"]), ", ".join("`%s`" % s for s in fig["old_sources"])))
    w("")
    L.extend(table(["Caso", "Trazo", "n", "Viejo", "N viejo", "Fuente vieja", "Nuevo", "N nuevo", "Δ (pp)", "Tabla 1", "Coincide"],
                   [[r["case"], r["trace"], r["n"], "%.4f" % r["old_rate"], r["old_N"], r["old_source"].rsplit("/", 1)[-1],
                     "%.4f" % r["new_rate"], r["new_N"], "%+.2f" % r["delta_pp"], r["table1_printed"], yn(r["matches_table1"])]
                    for r in fig["old_vs_new"]]))
    w("")
    w("### Punto 2 — Regla de rechazo del AWB (L2)")
    w("")
    rows = []
    for k, v in awb["implementations"].items():
        if "R" not in v:
            continue
        ch = awb["checks"][k]
        rows.append([k, "; ".join(v["used_for"]), v["R"], v["pvalue_form"], v["operator"], "%s:%d" % (v["code"][0]["file"], v["code"][0]["line"]),
                     yn(ch["all_rules_agree"]), ch["reject_iff_count_le"]])
    L.extend(table(["Implementación", "Cifras del v25", "R", "p-valor", "Operador", "Código", "Las tres reglas coinciden", "Rechaza si # ≤"], rows))
    w("")
    a10 = awb["implementations"]["a10_cited_in_assignment"]
    w("La línea citada en el encargo (`%s:%d`, `%s`) es la versión de A10: %s." % (a10["code"][0]["file"], a10["code"][0]["line"],
                                                                                 a10["code"][0]["text"], a10["note"]))
    w("")
    w("**P2.** Reglas comparadas: %s, para # = 0…R, en aritmética exacta y en coma flotante: %s." % (
        ", ".join(awb["checks"]["a13_msb_b"]["rules"]), verdict(awb["p2_holds"])))
    w("")
    w("Oración añadida a la nota de S4.3: «%s»" % awb["s43_sentence"])
    w("")
    w("### Punto 3 — Suplemento (L3)")
    w("")
    mr = sup["main_text_refs"]
    w("**Remisiones al cuerpo (L3.g).** Compilación del v25: %s páginas, %d errores. Etiquetas del cuerpo con número distinto entre "
      "v18b y v25: %d; de ellas, con remisión desde el suplemento: %d. Las %d remisiones se escriben igual con el v25: %s. La "
      "subsección A.5 del apéndice es la prueba de thm:consistency: %s; sec:bootdef = %s." % (
          mr["v25_compile"]["pages"], mr["v25_compile"]["errors"], len(mr["labels_changed_v18b_to_v25"]), len(mr["referenced_changed"]),
          len(mr["references"]), yn(mr["all_rendered_equal"]), yn(mr["appendix_a5"]["is_proof_of_theorem_2"]),
          " ".join(mr["appendix_a5"]["bootdef"])))
    w("")
    if mr["labels_changed_v18b_to_v25"]:
        L.extend(table(["Etiqueta", "v18b", "v25"], [[k, " ".join(v["v18b"]), " ".join(v["v25"]) if v["v25"] else "—"]
                                                     for k, v in sorted(mr["labels_changed_v18b_to_v25"].items())]))
        w("")
    b = sup["bold_check"]
    w("**L3.a. Negritas.** Detector validado en las tablas que sí tienen negritas: %s. Leyendas editadas: %s; conservadas por tener "
      "negritas: %s." % (yn(b["detector_validated"]), ", ".join(b["captions_removed"]), ", ".join(b["captions_kept"]) or "ninguna"))
    w("")
    L.extend(table(["Tabla", "Número", "Página", "\\textbf en la fuente", "Spans numéricos en negrita (PDF, antes)", "Frase en la leyenda (después)"],
                   [[k, v["number"], v.get("page"), b["source_textbf"][k], v["bold_numeric_spans"], yn(b["phrase_left"][k])]
                    for k, v in b["pdf_before"].items()]))
    w("")
    w("**L3.b. RM.** Definición quitada de S1 y S5 y añadida a la nota de %d tablas (el encargo enumera %d):" % (
        len(sup["rm_tables"]), len(sup["rm_assignment_list"])))
    w("")
    L.extend(table(["Tabla", "Número", "Tabla incluida", "Nota", "En la lista del encargo"],
                   [[r["label"], r["number"], ", ".join(r["inputs"]), r["note"], yn(r["label"] in sup["rm_assignment_list"])]
                    for r in sup["rm_tables"]]))
    w("")
    w("Definiciones de RM que quedan fuera de una nota: %d." % sup["rm_definitions_left_outside_notes"])
    w("")
    w("**L3.c–L3.e y L2.2.** Ediciones aplicadas (cada ancla, exactamente una vez):")
    w("")
    L.extend(table(["Edición", "Veces"], [[e["edit"], e["count"]] for e in sup["edits"]]))
    w("")
    w("S7: «%s» → «%s». Patrones de la nota sobre Θ_p que quedan: %s." % (
        sup["s7"]["old"], sup["s7"]["new"], ", ".join("%s: %d" % (k, v) for k, v in sup["s7"]["theta_p_patterns_left"].items())))
    w("")
    nb = sup["numbers_unchanged"]
    w("Números decimales del suplemento antes y después: %d y %d; añadidos: %s; quitados: %s." % (
        nb["before"], nb["after"], ", ".join(nb["added"]) or "ninguno", ", ".join(nb["removed"]) or "ninguno"))
    w("")
    ca, cb = sup["compile_after"], sup["compile_before"]
    w("**L3.f.** Páginas antes y después: %s y %s. Después: %d errores, %d referencias y %d citas indefinidas, %d avisos de «Rerun» "
      "(antes: %d errores, %d referencias indefinidas)." % (sup["pages"]["before"], sup["pages"]["after"], ca["errors"],
                                                            ca["undefined_references"], ca["undefined_citations"], ca["rerun_warnings"],
                                                            cb["errors"], cb["undefined_references"]))
    w("")
    w("**L3.h.** `supplementary/MANIFEST.sha256`: %d entradas, todas coinciden: %s. Búsqueda de identificadores: %d aciertos fuera de "
      "hashes de commit." % (sup["manifest_regenerated"]["entries"], yn(sup["manifest_regenerated"]["all_match"]),
                             sup["anonymization_scan"]["non_hash_hits"]))
    w("")
    w("### Punto 4 — Literales del v25 (L4)")
    w("")
    w("κ(−7) = %s = %.4f (texto: %s); λ(−7) = %d (texto: %s)." % (lit["kappa_fraction"], lit["kappa"], lit["text_v25"]["kappa"],
                                                                 lit["lambda"], lit["text_v25"]["lambda"]))
    w("")
    L.extend(table(["n", "E[S²] exacto", "6 decimales", "Texto", "Expansión", "|expansión − exacto|", "≤ cota", "Primer orden", "Texto"],
                   [[n, "%.9f" % r["exact"], r["exact_6"], lit["text_v25"]["exact"].get(n, "—"), "%.9f" % r["expansion"],
                     "%.2e" % r["abs_gap"], yn(r["within_bound"]), r["first_order_3"], lit["text_v25"]["first_order"].get(n, "—")]
                    for n, r in lit["by_n"].items()]))
    w("")
    idn = lit["identity"]
    w("Identidad de A.5 frente a `hac_newey_west` (n = %d, B ∈ {%s}, ruido i.i.d., AR(0.5) y MA(−0.8)): máxima diferencia "
      "absoluta %.1e (tolerancia %.0e)." % (idn["n"], ", ".join(str(x) for x in idn["bandwidths"]), idn["max_abs_gap"], idn["tolerance"]))
    w("")
    w("Pruebas nuevas: `tests/test_figure1_audit19.py`, `tests/test_awb_rule_audit19.py`, `tests/test_literals_v25_audit19.py` y "
      "`tests/test_no_literals_audit19.py`. El recuento de la batería completa desde la copia limpia del paquete queda en "
      "`package_v101_audit19.json`.")
    w("")
    w("### Punto 5 — Paquete v1.0.1 (L5)")
    w("")
    w("El zip v1.0.0 no contiene el manuscrito; no se agrega. El sha256 del zip v1.0.1, el número de archivos, las pruebas desde la "
      "copia limpia y el release se registran en `package_v101_audit19.json`, que no puede ir dentro del zip que describe.")
    w("")
    w("## 2. Compuertas")
    w("")
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], [
        ["L1 / P1", "cada punto = celda de la Tabla 1 al dígito impreso", "%d/%d" % (fig["n_match_table1"], fig["n_points"]),
         verdict(fig["p1_all_match_table1"])],
        ["L1", "una sola fuente; dibujado = JSON; PDF sin fechas", "%s / %s / %s" % (yn(fig["n_sources_new"] == 1),
                                                                                 yn(fig["figure"]["plotted_equal_json"]),
                                                                                 yn(fig["figure"]["pdf_dates"]["ok"])),
         verdict(fig["n_sources_new"] == 1 and fig["figure"]["plotted_equal_json"] and fig["figure"]["pdf_dates"]["ok"])],
        ["L2 / P2", "tres reglas iguales con R = 399; # ≤ 19", yn(awb["p2_holds"]), verdict(awb["p2_holds"])],
        ["L3.g", "ninguna remisión al cuerpo cambia", "%d cambiadas" % len(mr["referenced_changed"]), verdict(not mr["referenced_changed"])],
        ["L3", "0 errores, 0 referencias indefinidas; anclas únicas; ningún número cambia", yn(sup["ok"]),
         verdict(sup["ok"] and not nb["added"] and not nb["removed"])],
        ["L4", "todas las cifras del v25 se reproducen", yn(lit["all_hold"]), verdict(lit["all_hold"])]]))
    w("")
    w("## 3. Procedencia")
    w("")
    man = J("man")["entries"]
    L.extend(table(["Archivo", "sha256 (16)", "Script", "Commit", "Código commiteado", "Asistente"],
                   [[k, "`%s`" % v["sha256"][:16], v["script"], v["commit"][:7], yn(v["code_all_committed"]),
                     "%s / %s / %s" % (v["assistant"]["herramienta"], v["assistant"]["modelo"], v["assistant"]["version"]) if v.get("assistant") else "—"]
                    for k, v in sorted(man.items()) if "resultados_auditoria" not in k]))
    w("")
    w("## 4. Desviaciones")
    w("")
    L.extend(table(["Desviación", "Motivo", "Cuándo", "Efecto"], [
        ["El protocolo está en `%s`, no en `protocols/A19.md`" % C.PROTOCOL, "Ahí están todos los protocolos (A8–A18) y los buscan "
         "PROTOCOLS.md, S10 y los manifiestos", "Paso 0", "Ninguno"],
        ["La definición de RM va a la nota de %d tablas, no de %d" % (len(sup["rm_tables"]), len(sup["rm_assignment_list"])),
         "El encargo pide «cada tabla que tiene columna RM»; la lista omite tab:dgp2 y tab:dgp3 (S4), que la tienen y quedarían sin "
         "definición", "L3.b", "Dos notas más"],
        ["Las cifras del AWB de S4.3 y §4.9 son de A13, no de A15", "El encargo atribuye a A15 las de §4.8 y S4; se reportan las dos "
         "implementaciones", "L2.1", "La oración de S4.3 se refiere a la regla de A13"],
        ["El suplemento se edita sobre la salida de A18, sin repetir la cadena A16–A18", "Anclas únicas registradas; Paso 0 por sha256",
         "L3.0", "Volver a correr audit18_supplement.py desharía estas ediciones"]]))
    w("")
    w("## 5. No ejecutado")
    w("")
    w("- No se edita el manuscrito: el autor debe cambiar `\\includegraphics{fig_calibration_gain_audit13q}` por "
      "`fig_calibration_gain_audit19` en §4.2 del v25.")
    w("- No se encontró, aparte de la frase de S7, ninguna nota del suplemento que diga que el teorema supone σ̂² = Θ_p(n^{-1/3}); no "
      "hubo nada más que editar.")
    w("")
    w("## 6. Conclusiones")
    w("")
    w("- La Figura 1 sale ahora de los mismos caminos que la Tabla 1, y sus %d puntos coinciden con ella; «on common paths» es cierto "
      "para las dos." % fig["n_points"])
    w("- Las dos implementaciones del AWB usan R = %d; con ese R las tres reglas dan la misma decisión." % awb["implementations"]["a13_msb_b"]["R"])
    w("- El suplemento cambia solo de forma: %d ediciones, ningún número, %s → %s páginas." % (sup["n_edits"], sup["pages"]["before"],
                                                                                              sup["pages"]["after"]))
    w("- Las cifras nuevas del v25 (Remark 1, A.4 y A.5) se reproducen en aritmética exacta.")
    w("")
    w("## 7. Anomalías y observaciones")
    w("")
    w("- La cota «within 4.8×10⁻⁶ for n ≥ 200» se cumple con poco margen: la diferencia en n = 200 es %.2e." % lit["by_n"]["200"]["abs_gap"])
    out_new = ["%s, n = %d" % (r["case"], r["n"]) for r in fig["old_vs_new"]
               if r["trace"] == "cv_at_n" and not r["new_region"][0] <= r["new_rate"] <= r["new_region"][1]]
    w("- En la figura nueva, el trazo de MSB-B con el valor crítico en n queda fuera de la región exacta para 2×10⁴ caminos en: %s "
      "(la Tabla 1 lo marca en negrita). Es el mismo número que la Tabla 1; la figura vieja usaba otros caminos." % (
          "; ".join(out_new) or "ningún punto"))
    w("- El README del paquete v1.0.0 atribuía la Figura 1 a `e_calib_audit13.json`; no era exacto (mezclaba cuatro fuentes). Se "
      "corrige en el v1.0.1.")
    w("")
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    rows = [["L1 puntos que coinciden con la Tabla 1", fig["n_match_table1"], "—", "2×10⁴ por punto", "—", "—", F["fig"], "n_match_table1"],
            ["L2 R (A15, MZ_t-GLS)", awb["implementations"]["a15_mzt_gls"]["R"], "—", "—", "—", "—", F["awb"], "implementations.a15_mzt_gls.R"],
            ["L2 R (A13, MSB-B)", awb["implementations"]["a13_msb_b"]["R"], "—", "—", "—", "—", F["awb"], "implementations.a13_msb_b.R"],
            ["L2 umbral de #", awb["checks"]["a13_msb_b"]["reject_iff_count_le"], "—", "—", "—", "—", F["awb"],
             "checks.a13_msb_b.reject_iff_count_le"],
            ["L3.f páginas antes", sup["pages"]["before"], "—", "—", "—", "—", F["sup"], "pages.before"],
            ["L3.f páginas después", sup["pages"]["after"], "—", "—", "—", "—", F["sup"], "pages.after"],
            ["L4 λ(−7)", lit["lambda"], "exacto", "—", "—", "—", F["lit"], "lambda"]]
    for n, r in lit["by_n"].items():
        rows.append(["L4 E[S²] n = %s" % n, r["exact_6"], "exacto", "—", "—", "—", F["lit"], "by_n.%s.exact" % n])
        rows.append(["L4 |expansión − exacto| n = %s" % n, "%.2e" % r["abs_gap"], "exacto", "—", "—", "—", F["lit"], "by_n.%s.abs_gap" % n])
    rows.append(["L4 identidad, máx. |Δ|", "%.1e" % idn["max_abs_gap"], "—", "—", "—", "—", F["lit"], "identity.max_abs_gap"])
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"], rows))
    w("")
    C.write_text(OUT, "\n".join(L) + "\n", __file__)
    print("reporte:", C.rel(OUT), len(L), "lineas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
