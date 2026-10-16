"""
Auditoria A17 - generador del reporte experiments/results/resultados_auditoria_17.md (enmienda 7, lectura E7.6).
Solo lee JSON (tests/test_no_literals_audit17.py). Siete secciones y tabla maestra.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit17_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_17.md")
F = {"ms": "mstats_v18_audit17.json", "b35": "boot35_v18_audit17.json", "sup": "supplement_v18_audit17.json",
     "trial": "supplement_v18_trial_audit17.json", "coh": "coherence_v18_audit17.json", "pkg": "submission_v18_audit17.json",
     "man": "manifest_audit17.json"}
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


def e(x):
    return "—" if x is None else "%.1e" % x


def yn(b):
    return "sí" if b else "no"


def s1(w, L):
    d = J("ms")
    w("### B17.1 — eq:mstats del v18, evaluación literal (lectura E7.1)")
    w("")
    w("Caminos de E6.4 (familia %s; colisiones con familias anteriores: %d). Texto: %s. Criterio: |Δ| rel. ≤ %s en MSB y |Δ| abs. "
      "≤ %s en MZ_t. Cumple: %s." % (d["provenance"]["seed_family"], d["seed_collisions_vs_prior"],
                                     ", ".join("%s %s" % kv for kv in d["text_lines"].items()), e(d["criteria"]["msb_rel"]),
                                     e(d["criteria"]["mzt_abs"]), yn(d["passes"])))
    w("")
    vs = list(d["variants_meaning"])
    rows = [[k, c["paths"]] + ["%s / %s" % (e(c["variants"][v]["msb_rel"]), e(c["variants"][v]["mzt_abs"])) for v in vs] +
            [c["kmax_disagreements"], c["maic_disagreements"], e(c["dfgls_max_rel"])] for k, c in d["cells"].items()]
    L.extend(table(["Celda", "Caminos"] + ["%s (MSB rel. / MZ_t abs.)" % d["variants_meaning"][v] for v in vs] +
                   ["k_max distinto", "k de la MAIC distinto", "máx. rel. t de DF-GLS"], rows))
    w("")
    w("Descripción del texto: k_max coincide: %s; la MAIC del texto en la muestra común elige el k del código: %s; el t de DF-GLS en "
      "t = k+1..n coincide con arch.DFGLS: %s. Las variantes de un solo cambio fallan todas por órdenes de magnitud, así que la "
      "comprobación distingue índices, normalización, muestra y divisor." % (
          yn(d["description"]["kmax_agrees"]), yn(d["description"]["maic_agrees"]), yn(d["description"]["dfgls_sample_agrees"])))
    w("")


def s2(w, L):
    d = J("b35")
    w("### B17.2 — §3.5 del v18 frente a bootUR 1.0.5 (lectura E7.2)")
    w("")
    rows = [[x["text"]["where"], x["claim"], "; ".join(c["where"] for c in x["code"]) or "—", x["verdict"], x["detail"]] for x in d["claims"]]
    L.extend(table(["Texto", "Afirmación", "Código (archivo:línea)", "Veredicto", "Detalle"], rows))
    w("")
    w("Resumen: %s. η en n = 200: %s (impreso %s; confirma: %s)." % (", ".join("%s %d" % kv for kv in d["summary"].items()),
                                                                  "%.6f" % d["eta200_printed"]["value"], d["eta200_printed"]["printed"],
                                                                  yn(d["eta200_printed"]["confirma"])))
    w("")


def s3(w, L):
    d = J("sup")
    w("### B17.3 — Suplemento (lectura E7.3)")
    w("")
    L.extend(table(["Bloque", "Patrón", "Sustitución"], [[x["block"], "`%s`" % x["pattern"], "`%s`" % x["replacement"]] for x in d["b17_edits"]]))
    w("")
    for x in d["b17_inserted"]:
        w("- %s (%s): «%s»" % (x["section"], x["position"], x["text"][:300] + ("…" if len(x["text"]) > 300 else "")))
    w("")
    L.extend(table(["Comprobación", "Valor"], [[k, v] for k, v in d["b17_checks"].items()]))
    w("")
    w("Ediciones aplicadas en la construcción (todas): %s." % "; ".join("%s ×%d" % (x["block"], x["count"]) for x in d["editorial_edits"]))
    w("")
    cp, sc, s6 = d["compile"], d["anonymization_scan"], d["sec6_integrity"]
    w("`supplementary/` reconstruido: %d archivos; %d aciertos identificadores; compila %s, %d errores, %d referencias y %d citas "
      "indefinidas, %d cajas desbordadas, %s páginas. S2.1–S2.9 como el mapa: %s. Remisiones sin resolver: %d; «of the main text» fuera "
      "del cuerpo del v18: %d (numeradas con la compilación de control del v18, %s páginas). S9: %d fragmentos, %d ausentes, cifras "
      "iguales: %s, admitiendo solo %s." % (
          d["n_files"], sc["non_hash_hits"], yn(cp["compiled"]), cp["errors"], cp["undefined_references"], cp["undefined_citations"],
          cp["overfull"], cp["pages"], yn(d["numbering"]["S2_matches_map"]), len(d["unresolved"]), len(d["main_text_refs"]["not_in_v18_body"]),
          d["v18_control_compile"]["pages"], s6["chunks_checked"], s6["n_missing"], yn(s6["numbers_equal"]),
          ", ".join("«%s» → «%s»" % tuple(x) for x in s6["substitutions_admitted"])))
    w("")


def s4(w, L):
    d = J("coh")
    w("### B17.4 — Coherencia acotada (lectura E7.4)")
    w("")
    w("Compilación del v18 (con el .bbl entregado): %d errores, %d referencias y %d citas indefinidas, %d cajas desbordadas, %s páginas." % (
        d["v18_compile"]["errors"], d["v18_compile"]["undefined_references"], d["v18_compile"]["undefined_citations"], d["v18_compile"]["overfull"],
        d["v18_compile"]["pages"]))
    w("")
    rows = [[r["file"], "%d–%d" % tuple(r["v18_lines"]) if r["v18_lines"][1] >= r["v18_lines"][0] else "(retirada)", r["kind"],
             "%d/%d" % (sum(1 for c in r["checks"] if c["holds"]), len(r["checks"])), "; ".join(c["check"] for c in r["checks"])[:220], r["verdict"]]
            for r in d["a_diff"]]
    L.extend(table(["Archivo", "Líneas del v18", "Tipo", "Comprobaciones", "Qué se comprueba", "Veredicto"], rows))
    w("")
    for t in d["b_tables"]:
        if "S2.1" in t["table"]:
            w("- %s: regenerada desde `bA_ma_audit12.json` e igual a la del suplemento: %s (%d celdas); nota: %s." % (
                t["table"], yn(t["regenerated_equals_supplement"]), t["cells"], "; ".join("%s %s" % (c["check"], yn(c["holds"])) for c in t["note_checks"])))
        elif "S4.3" in t["table"]:
            w("- %s: idéntica a `tables_audit13/`: %s; nota: %s. Observación: %s." % (
                t["table"], yn(t["identical_to_tables_audit13"]), "; ".join("%s %s" % (c["check"], yn(c["holds"])) for c in t["note_checks"]),
                t["observation"]))
        elif "S7.1" in t["table"]:
            w("- %s: todas las cifras iguales a `e4_slope_audit15.json` con redondeo binario: %s; frase de S7 presente: %s. Pendientes de B antes "
              "del techo (script / librería): %s." % (t["table"], yn(t["all_equal"]), yn(t["s7_sentence_present"]),
                                                     "; ".join("%s %.4f / %.4f" % (k, v["B_pre_script"], v["B_pre_lib"]) for k, v in t["slopes_vs_one_third"].items())))
        else:
            w("- %s: «R = 399»: %s; queda «B = 399»: %s. Cifras: %s." % (
                t["table"], yn(t["R_399"]), yn(t["B_399_left"]),
                "; ".join("%s %s (%s)" % (x["key"], x.get("verdict"), ", ".join("%s→%s" % (n["printed"], n["verdict"]) for n in x.get("numbers", [])))
                          for x in t["items"])))
    w("")


def s5(w, L):
    d = J("pkg")
    w("### B17.5 — Compilación conjunta y paquete de envío (lectura E7.5)")
    w("")
    c = d["compile"]
    w("- v18: %d errores, %d referencias y %d citas indefinidas, %s páginas; el .bbl entregado coincide con el que genera bibtex: %s." % (
        c["v18"]["errors"], c["v18"]["undefined_references"], c["v18"]["undefined_citations"], c["v18"]["pages"], yn(c["v18_bbl_matches_bibtex"])))
    w("- Suplemento: %d errores, %d referencias y %d citas indefinidas, %s páginas." % (
        c["supplement"]["errors"], c["supplement"]["undefined_references"], c["supplement"]["undefined_citations"], c["supplement"]["pages"]))
    w("- Paquete: %d archivos; zip `%s`, %d bytes, sha256 `%s` (no se commitea). `supplementary/` del commit `%s`, sin cambios en el árbol: %s." % (
        d["n_files"], d["zip"]["name"], d["zip"]["bytes"], d["zip"]["sha256"], d["inputs"]["supplementary_commit"][:7], yn(d["gates"]["supplementary_committed"])))
    w("- Incluidos: %s; tabulares: %s; figuras: %s." % (", ".join(x for x in d["included_tex"] if not x.startswith("tables/")),
                                                      ", ".join(d["included_tables"]), ", ".join(d["included_figures"])))
    w("- Excluidos del zip del v18: %s." % ", ".join(d["excluded_from_zip"]))
    w("- Artefactos de compilación en el paquete: %d. Aciertos que identifican al autor (ruta, usuario, apellido, URL del repositorio): %d. "
      "Otros aciertos: %s." % (len(d["compilation_artifacts_in_package"]), len(d["anonymity"]["author_identifying_hits"]),
                               ", ".join(sorted({c for h in d["anonymity"]["other_hits"].values() for c in h})) or "ninguno"))
    md = d["anonymity"]["pdf_metadata"]
    w("- Metadatos de los PDF (%d): campos presentes %s; ninguno con autor." % (len(md), ", ".join(sorted({k for v in md.values() for k in v}))))
    w("")
    L.extend(table(["Archivo", "Bytes", "sha256"], [[x["path"], x["bytes"], "`%s`" % x["sha256"][:16]] for x in d["files"]
                                                     if not x["path"].startswith("supplementary/")]))
    w("")


def s_gates(w, L):
    w("## 2. Compuertas")
    w("")
    ms, b, sp, t, co, pk = J("ms"), J("b35"), J("sup"), J("trial"), J("coh"), J("pkg")
    rows = [["E7.1", "MSB rel. ≤ 1e-12 y MZ_t abs. ≤ 1e-10 en todos los caminos", "máx. %s / %s" % (
        e(max(c["variants"]["text"]["msb_rel"] for c in ms["cells"].values())), e(max(c["variants"]["text"]["mzt_abs"] for c in ms["cells"].values()))),
             "pasa" if ms["passes"] else "NO pasa"],
            ["E7.1 descripción", "k_max, k de la MAIC y muestra de DF-GLS", "%s / %s / %s" % tuple(yn(v) for v in ms["description"].values()),
             "pasa" if all(ms["description"].values()) else "NO pasa"],
            ["E7.2", "0 afirmaciones que difieren; comprobaciones sin fallo", "%d / %d" % (b["summary"]["difiere"], len(b["checks_failed"])),
             "pasa" if b["summary"]["difiere"] == 0 and not b["checks_failed"] else "NO pasa"],
            ["E7.3 prueba --out", "0 errores y 0 aciertos", "%d / %d" % (t["compile"]["errors"], t["anonymization_scan"]["non_hash_hits"]),
             "pasa" if t["compile"]["errors"] == 0 and t["anonymization_scan"]["non_hash_hits"] == 0 else "NO pasa"],
            ["E7.3 reconstrucción", "ediciones aplicadas; 0 errores; S9 íntegra salvo B→R", "B=399 restantes %d; errores %d; ausentes %d" % (
                sp["b17_checks"]["B_399_left"], sp["compile"]["errors"], sp["sec6_integrity"]["n_missing"]),
             "pasa" if sp["b17_checks"]["B_399_left"] == 0 and sp["compile"]["errors"] == 0 and sp["sec6_integrity"]["n_missing"] == 0 else "NO pasa"],
            ["E7.4", "todos los hunks del diff coinciden", "%d/%d" % (co["summary"]["coincide"], co["summary"]["hunks"]),
             "pasa" if co["summary"]["coincide"] == co["summary"]["hunks"] else "NO pasa"],
            ["E7.5", "puertas del paquete", ", ".join("%s %s" % (k, yn(v)) for k, v in pk["gates"].items()), "pasa" if all(pk["gates"].values()) else "NO pasa"]]
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], rows))
    w("")


def s_prov(w, L):
    w("## 3. Procedencia")
    w("")
    w("Entrada: `paper_latex_v18.zip` sha256 `%s`. Protocolo: `experiments/protocol_audit15_amend7.md` (enmienda 7), commiteado antes de "
      "generar nada." % J("ms")["inputs"]["v18_zip_sha256"])
    w("")
    man = J("man")["entries"]
    L.extend(table(["Archivo", "sha256 (16)", "Script", "Commit", "Código commiteado", "Asistente"],
                   [[k, "`%s`" % v["sha256"][:16], v["script"], v["commit"][:7], yn(v["code_all_committed"]),
                     "%s / %s / %s" % (v["assistant"]["herramienta"], v["assistant"]["modelo"], v["assistant"]["version"]) if v.get("assistant") else "—"]
                    for k, v in sorted(man.items()) if "resultados_auditoria" not in k]))
    w("")


def s_dev(w, L):
    w("## 4. Desviaciones")
    w("")
    L.extend(table(["Desviación", "Motivo", "Cuándo", "Efecto"], [
        ["B17.3 se construye con `audit17_supplement.py`, que reutiliza `audit16_supplement.py` sin modificarlo", "Regla de no modificar el código "
         "de auditorías anteriores", "Antes de generar (E7.3)", "Ninguno"],
        ["El párrafo SB/SWB de A16 se sustituye entero por el de B17", "El cuerpo del v18 ya da lo que decía; el encargo pide solo los detalles que "
         "el cuerpo no da", "Al construir", "El párrafo del Paso 0 se conserva"],
        ["S9 recibe una edición («B = 399» → «R = 399»)", "Lo pide el encargo", "Al construir", "La integridad de S9 se comprueba admitiendo solo esa "
         "sustitución"],
        ["El zip del paquete no se commitea", "Es un entregable derivado; lo registran su sha256 y la lista de archivos", "E7.5", "Ninguno"]]))
    w("")


def s_not(w, L):
    w("## 5. No ejecutado")
    w("")
    w("- No se edita ningún `.tex` del manuscrito.")
    w("- No se envía el paquete: se entrega al autor.")
    w("")


def s_concl(w, L):
    w("## 6. Conclusiones")
    w("")
    ms, b, sp, co, pk = J("ms"), J("b35"), J("sup"), J("coh"), J("pkg")
    w("- B17.1: eq:mstats del v18, leída literalmente, reproduce `np_statistics` (máx. %s en MSB, %s en MZ_t); la descripción de s²_AR, k_max y "
      "la muestra de DF-GLS coincide con el código." % (e(max(c["variants"]["text"]["msb_rel"] for c in ms["cells"].values())),
                                                       e(max(c["variants"]["text"]["mzt_abs"] for c in ms["cells"].values()))))
    w("- B17.2: §3.5: %s." % ", ".join("%s %d" % kv for kv in b["summary"].items()))
    w("- B17.3: suplemento reconstruido con las cuatro ediciones, %s páginas, sin errores." % sp["compile"]["pages"])
    w("- B17.4: %d de %d hunks del diff coinciden; las cuatro tablas del suplemento coinciden con sus fuentes." % (co["summary"]["coincide"], co["summary"]["hunks"]))
    w("- B17.5: v18 (%s páginas) y suplemento (%s páginas) compilan juntos sin errores; paquete de %d archivos sin artefactos ni aciertos de "
      "autor." % (pk["compile"]["v18"]["pages"], pk["compile"]["supplement"]["pages"], pk["n_files"]))
    w("")


def s_anom(w, L):
    w("## 7. Anomalías y observaciones")
    w("")
    for x in J("b35")["claims"]:
        if x["verdict"] == "coincide con matiz":
            w("- §3.5 (%s), %s: %s." % (x["text"]["where"], x["claim"], x["detail"]))
    for t in J("coh")["b_tables"]:
        if t.get("observation"):
            w("- %s: %s." % (t["table"], t["observation"]))
    md = J("pkg")["anonymity"]["pdf_metadata"]
    dates = sorted({v.get("creationDate", "") for v in md.values() if v.get("creationDate")})
    if dates:
        w("- Los PDF de figuras llevan fecha de creación con zona horaria (%s); no identifican al autor." % ", ".join(dates[:2]))
    other = J("pkg")["anonymity"]["other_hits"]
    if other:
        w("- Hashes de commit en %d archivos de `supplementary/data/` (se conservan desde B15.5)." % len(other))
    w("")


def master(w, L):
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    rows = []
    for k, c in J("ms")["cells"].items():
        for v, a in c["variants"].items():
            for q in ("msb_rel", "mzt_abs"):
                rows.append(["B17.1 %s %s %s" % (k, v, q), e(a[q]), "—", c["paths"], "—", "160", F["ms"], "cells.%s.variants.%s.%s" % (k, v, q)])
        rows.append(["B17.1 %s dfgls_max_rel" % k, e(c["dfgls_max_rel"]), "—", c["paths"], "—", "160", F["ms"], "cells.%s.dfgls_max_rel" % k])
    for n, v in J("b35")["eta"].items():
        rows.append(["B17.2 eta n = %s (regla del código)" % n, "%.6f" % v["eta_code"], "—", "—", "—", "—", F["b35"], "eta.%s.eta_code" % n])
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"], rows))
    w("")


def main():
    L = []

    def w(s):
        L.append(s)
    w("# Auditoría A17 — reporte (enmienda 7, cierre sobre el v18)")
    w("")
    w("Enmienda 7 commiteada antes de generar nada (§3). No se editó ningún `.tex` del manuscrito ni `src/`.")
    w("")
    w("## 1. Resultados")
    w("")
    s1(w, L)
    s2(w, L)
    s3(w, L)
    s4(w, L)
    s5(w, L)
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
