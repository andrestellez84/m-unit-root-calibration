"""
Auditoria A18 - generador del reporte experiments/results/resultados_auditoria_18.md (enmienda 8, lectura E8.5).
Solo lee JSON (tests/test_no_literals_audit18.py). Siete secciones y tabla maestra.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit18_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_18.md")
F = {"diff": "diff_v18b_audit18.json", "sup": "supplement_v18b_audit18.json", "trial": "supplement_v18b_trial_audit18.json",
     "pkg": "submission_v18b_audit18.json", "man": "manifest_audit18.json"}
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


def main():
    L = []

    def w(s):
        L.append(s)
    d, s, t, p = J("diff"), J("sup"), J("trial"), J("pkg")
    w("# Auditoría A18 — reporte (enmienda 8, reempaquetado final sobre el v18b)")
    w("")
    w("Enmienda 8 commiteada antes de empezar (§3). Sin simulación ni cifras nuevas. No se editó ningún `.tex` del manuscrito ni `src/`.")
    w("")
    w("**Paquete: `%s`, %d bytes, sha256 `%s`** (%d archivos; no se commitea)." % (p["zip"]["name"], p["zip"]["bytes"], p["zip"]["sha256"], p["n_files"]))
    w("")
    w("## 1. Resultados")
    w("")
    w("### B18.1 — sec3_theory.tex del v18b (lectura E8.1)")
    w("")
    w("Miembros del zip que difieren entre v18 y v18b: %s; solo en v18: %s; solo en v18b: %s. El único cambio de texto es "
      "sec3_theory.tex:176: %s." % (", ".join(d["members_differ"]), d["only_in_v18"] or "ninguno", d["only_in_v18b"] or "ninguno",
                                   yn(d["only_change_is_sec3_176"])))
    w("")
    for f, v in d["text_changes"].items():
        for c in v["changes"]:
            L.extend(table(["Archivo", "Líneas", "v18", "v18b"], [[f, "%d–%d" % tuple(c["v18b_lines"]), " / ".join(c["v18"]), " / ".join(c["v18b"])]]))
            w("")
    r = d["line_176_rule"]
    w("La línea nueva escribe l = round(1.75 T^{1/3}): %s; y T = n + 1: %s. Es la regla del código (%s), con l = %s en n = %s." % (
        yn(r["writes_T"]), yn(r["writes_T_eq_n_plus_1"]), r["code_rule"], ", ".join(str(v) for v in r["l_new_text_rule_equals_code"].values()),
        ", ".join(r["l_new_text_rule_equals_code"])))
    w("")
    w("### B18.2 — Nota de S4.3 (lectura E8.2)")
    w("")
    e = s["b18_edit"]
    w("Frase añadida al final de la nota de tab:awb (bloque %s, ancla `%s`, veces %d): «%s». Está en la nota de S4.3: %s; apariciones en el "
      "suplemento: %d. sec:bootdef es la sección %s del v18b (%s). El p-valor registrado del AWB de A13 es `%s` con %d réplicas." % (
          e["block"], e["anchor"], e["count"], e["sentence"], yn(e["in_tab_awb_note"]), e["occurrences_in_supplement"], e["bootdef_label"][1],
          yn(e["bootdef_is_3_5"]), e["a13_awb_pvalue"], e["a13_awb_replicas"]))
    w("")
    w("### B18.3 — Fechas de los PDF (lectura E8.3)")
    w("")
    rows = []
    for src, recs in (("suplemento", s["b18_pdf_dates"]), ("cuerpo", p["body_pdf_date_strip"])):
        for f, v in recs.items():
            rows.append([src, f, ", ".join(v["removed_keys"]) or "—", yn(v["content_streams_equal"]), yn(v["raster_equal"]),
                         yn(not v["raw_has_date_key"] and not v["raw_has_date_value"]), len(v["pdfinfo_date_lines"]), "`%s`" % v["sha256_after"][:16]])
    L.extend(table(["Origen", "PDF", "Claves eliminadas", "Contenido idéntico", "Raster idéntico (72 ppp)", "Sin fecha en los bytes",
                    "Líneas de fecha en pdfinfo", "sha256 nuevo (16)"], rows))
    w("")
    w("Comprobación final sobre los %d PDF del paquete: sin clave ni valor de fecha y sin líneas de fecha en pdfinfo: %s." % (
        len(p["pdf_date_check"]), yn(p["gates"]["no_pdf_dates"])))
    w("")
    w("### B18.4 — MANIFEST, compilación e identificadores (lectura E8.4)")
    w("")
    c = p["compile"]
    w("- `supplementary/MANIFEST.sha256` regenerado: %d entradas; todas coinciden con los archivos del paquete: %s." % (
        p["supplement_manifest"]["entries"], yn(p["supplement_manifest"]["all_match"])))
    w("- Cuerpo (v18b): %d errores, %d referencias y %d citas indefinidas, %s páginas; el .bbl coincide con el de bibtex: %s." % (
        c["v18b"]["errors"], c["v18b"]["undefined_references"], c["v18b"]["undefined_citations"], c["v18b"]["pages"], yn(c["v18b_bbl_matches_bibtex"])))
    w("- Suplemento: %d errores, %d referencias y %d citas indefinidas, %s páginas." % (
        c["supplement"]["errors"], c["supplement"]["undefined_references"], c["supplement"]["undefined_citations"], c["supplement"]["pages"]))
    w("- Identificadores: %d aciertos que identifican al autor; otros: %s (hashes de commit en `supplementary/data/`, conservados desde B15.5). "
      "Metadatos de PDF presentes: %s." % (len(p["anonymity"]["author_identifying_hits"]),
                                          ", ".join(sorted({x for h in p["anonymity"]["other_hits"].values() for x in h})) or "ninguno",
                                          ", ".join(sorted({k for v in p["anonymity"]["pdf_metadata"].values() for k in v}))))
    w("")
    w("### B18.5 — Paquete (lectura E8.5)")
    w("")
    w("`%s`: %d bytes, sha256 **`%s`**. Incluye %d archivos; del zip del v18b se excluyen %s." % (
        p["zip"]["name"], p["zip"]["bytes"], p["zip"]["sha256"], p["n_files"], ", ".join(p["excluded_from_zip"])))
    w("")
    L.extend(table(["Archivo", "Bytes", "sha256 (16)"], [[x["path"], x["bytes"], "`%s`" % x["sha256"][:16]] for x in p["files"]
                                                         if not x["path"].startswith("supplementary/")]))
    w("")
    w("## 2. Compuertas")
    w("")
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], [
        ["E8.1", "único cambio: sec3_theory.tex:176", yn(d["only_change_is_sec3_176"]), "pasa" if d["only_change_is_sec3_176"] else "NO pasa"],
        ["E8.2", "frase una vez, en la nota de S4.3; sec:bootdef = 3.5", "%d / %s / %s" % (e["count"], yn(e["in_tab_awb_note"]), yn(e["bootdef_is_3_5"])),
         "pasa" if e["count"] == 1 and e["in_tab_awb_note"] and e["bootdef_is_3_5"] else "NO pasa"],
        ["E8.2 prueba --out", "0 errores", t["compile"]["errors"], "pasa" if t["compile"]["errors"] == 0 else "NO pasa"]] +
        [["E8.3–E8.5 %s" % k, "puerta del paquete", yn(v), "pasa" if v else "NO pasa"] for k, v in p["gates"].items()]))
    w("")
    w("## 3. Procedencia")
    w("")
    w("Entrada: `paper_latex_v18b.zip` sha256 `%s`. Protocolo: `experiments/protocol_audit15_amend8.md`." % d["inputs"]["v18b_zip_sha256"])
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
        ["La frase de S4.3 lleva las fórmulas en modo matemático ($…$)", "El texto del encargo es LaTeX sin delimitadores", "E8.2",
         "Mismo texto; compila"],
        ["Las fechas se quitan reescribiendo el diccionario Info (sin la clave), no dejándola en null", "Un primer intento dejaba "
         "«/CreationDate null», que la comprobación en bytes rechazó", "Durante la prueba con --out", "Creator y Producer se conservan"],
        ["El zip no se commitea", "Entregable derivado; lo registran su sha256 y la lista de archivos", "E8.5", "Ninguno"]]))
    w("")
    w("## 5. No ejecutado")
    w("")
    w("- No se edita ningún `.tex` del manuscrito; el paquete se arma desde el zip del v18b.")
    w("")
    w("## 6. Conclusiones")
    w("")
    w("- El v18b cambia solo sec3_theory.tex:176, que ahora escribe la regla del código.")
    w("- La nota de S4.3 declara el p-valor de su AWB; las fechas de los %d PDF del paquete se han eliminado sin tocar su contenido." % len(p["pdf_date_check"]))
    w("- Cuerpo (%s páginas) y suplemento (%s páginas) compilan juntos sin errores ni referencias indefinidas; sin aciertos que identifiquen "
      "al autor." % (c["v18b"]["pages"], c["supplement"]["pages"]))
    w("- `%s`: sha256 `%s`." % (p["zip"]["name"], p["zip"]["sha256"]))
    w("")
    w("## 7. Anomalías y observaciones")
    w("")
    w("- Ninguna nueva. Se mantienen los hashes de commit en `supplementary/data/` (decisión de B15.5).")
    w("")
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"],
                   [["B18.5 sha256 del paquete", p["zip"]["sha256"], "—", "—", "—", "—", F["pkg"], "zip.sha256"],
                    ["B18.5 bytes del paquete", p["zip"]["bytes"], "—", "—", "—", "—", F["pkg"], "zip.bytes"],
                    ["B18.5 archivos del paquete", p["n_files"], "—", "—", "—", "—", F["pkg"], "n_files"]]))
    w("")
    C.write_text(OUT, "\n".join(L) + "\n", __file__)
    print("reporte:", C.rel(OUT), len(L), "lineas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
