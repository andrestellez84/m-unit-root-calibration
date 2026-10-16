"""
Auditoria A14 - generador del reporte experiments/results/resultados_auditoria_14.md
(protocol_audit14.md, lectura 11).

Solo lee JSON (regla 3 de A8; lo comprueba tests/test_no_literals_audit14.py). Siete
secciones y la tabla maestra de los numeros nuevos.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_14.md")
F = {"b0": "b0_inventory_audit14.json", "b1": "b1_critical_audit14.json", "tab": "tables_audit14.json",
     "b2": "b2_sources_audit14.json", "b3": "b3_verify_audit14.json", "man": "manifest_audit14.json",
     "q13": "q_claims_audit13.json"}
LABEL = {"msb": "MSB-GLS", "mzt": "MZ_t-GLS"}
CASE = {"c": "constante", "ct": "tendencia"}
_C = {}


def J(k):
    if k not in _C:
        _C[k] = C.read_json(F[k])
    return _C[k]


def esc(c):
    return str(c).replace("|", "\\|")


def table(heads, rows):
    L = ["| " + " | ".join(esc(h) for h in heads) + " |", "|" + "---|" * len(heads)]
    L += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return L


def g(x, d=4):
    return "—" if x is None else "%.*f" % (d, x)


def e(x):
    return "%.2e" % x


def v6(x):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "sí" if x else "no"
    if isinstance(x, int):
        return "%d" % x
    return "%.6g" % x


def yn(b):
    return "sí" if b else "no"


def short(h):
    return (h or "—")[:7]


# ---------------------------------------------------------------------------
# 1. Resultados
# ---------------------------------------------------------------------------
def s_b0(w, L):
    b = J("b0")
    w("### B14.0 — Entrada v15")
    w("")
    m = b["manuscript"]
    w("`%s`, sha256 `%s` (%d bytes), leído dentro del zip sin extraerlo. La familia %d queda reservada y sin uso "
      "(colisión con las familias %d–%d: %s)." % (m["path"], m["sha256"], m["bytes"], b["family"]["reserved"],
                                                 b["family"]["prior_range"][0], b["family"]["prior_range"][1],
                                                 yn(b["family"]["collides_with_prior"])))
    w("")
    w("Tabulares: %d archivos en `v15/tables/` (%d tabulares y la nota de tab:attrib). Figuras: %d. "
      "Idénticos byte a byte a los exportados por A13 y B13.Q: **%s**." % (
          b["n_tables_dir_files"], b["n_tabulars"], b["n_figures"], "sí, todos" if b["all_identical"] else "NO"))
    w("")
    rows = [[k, x["local"], "`%s`" % x["sha256_v15"], yn(x["identical"])] for k, x in b["files_vs_exports"].items()]
    L.extend(table(["Archivo del v15", "Exportado", "sha256", "Idéntico"], rows))
    w("")
    w("Extensión declarada: %d referencias `\\input{tables/…}` e `\\includegraphics` en el texto; todas apuntan a un archivo "
      "del zip: %s. Archivos de tablas o figuras sin referencia: %s. Figuras `*_audit13.pdf` sin la q en el zip: %s." % (
          len(b["references"]), yn(b["references_all_in_zip"]), ", ".join(b["unreferenced_zip_files"]) or "ninguno",
          ", ".join(b["old_figures_audit13_in_zip"]) or "ninguna"))
    w("")


def s_b1(w, L):
    d = J("b1")
    t = J("tab")
    cfg = d["config"]
    w("### B14.1 — Valores críticos de MSB-GLS y MZ_t-GLS (suplemento S5)")
    w("")
    w("Cuantil de cola inferior: %s. Se rechaza cuando el estadístico es menor que q_α. Retardo: %s. EE: %s. "
      "No se usan números aleatorios." % (cfg["quantile"], cfg["lag_selection"], cfg["bootstrap"]))
    w("")
    rows = [[n, s["path"], "`%s`" % s["sha256"], s["rows"], ", ".join("%s %d" % kv for kv in s["nan"].items())]
            for n, s in d["samples"].items()]
    L.extend(table(["n", "Muestra", "sha256", "Filas", "NaN por columna"], rows))
    w("")
    V = {(v["stat"], v["case"], v["n"], v["alpha"]): v for v in d["values"]}
    heads = ["Estadístico", "Caso", "n"] + ["q_%g (EE)" % a for a in cfg["levels"]]
    rows = []
    for s in cfg["stats"]:
        dec = t["decimals"][s]
        for c in cfg["cases"]:
            for n in cfg["n"]:
                rows.append([LABEL[s], CASE[c], n] + ["%s (%s)%s" % (g(V[(s, c, n, a)]["critical_value"], dec + 2),
                                                                    e(V[(s, c, n, a)]["bootstrap_se"]),
                                                                    "" if V[(s, c, n, a)]["new"] else " ᵉ")
                                                     for a in cfg["levels"]])
    L.extend(table(heads, rows))
    w("")
    w("ᵉ: ya existía (Paso 0). Los %d valores restantes son nuevos. Tabla con dos decimales más que el tabular; EE bootstrap "
      "exacto entre paréntesis." % d["checks"]["n_new"])
    w("")
    ratios = [v["se_ratio_mj"] for v in d["values"]]
    w("Controles:")
    w("")
    w("- EE de Maritz–Jarrett / EE exacto: entre %s y %s." % (g(min(ratios), 4), g(max(ratios), 4)))
    w("- Masa de las marginales y residuo del truncamiento dentro de tolerancia: %s." % yn(d["checks"]["truncation_ok"]))
    w("- El cuantil de la función del EE coincide con `nanquantile` en los %d valores: %s." % (
        d["checks"]["n_values"], yn(d["checks"]["quantile_eb_equals_nanquantile"])))
    w("- NaN en las columnas usadas: %s." % ("ninguno" if d["checks"]["no_nan"] else "sí"))
    w("- Validación de las fórmulas por enumeración exhaustiva de N^N remuestras con N ≤ 6: "
      "`tests/test_audit14_exact_bootstrap.py`.")
    w("")
    rows = [[k, "`%s`" % h] for k, h in t["outputs"].items()]
    L.extend(table(["Salida (desde `%s`)" % t["source"], "sha256"], rows))
    w("")
    w("Nota del tabular: EE máximo de MSB-GLS %s (impreso como cota %s) y de MZ_t-GLS %s (impreso %s); N_cal = `%s`. "
      "Redondeo %s, con %d decimales para MSB-GLS y %d para MZ_t-GLS." % (
          e(t["note"]["max_bootstrap_se"]["msb"]), t["note"]["printed_bound"]["msb"], e(t["note"]["max_bootstrap_se"]["mzt"]),
          t["note"]["printed_bound"]["mzt"], t["note"]["N_cal_tex"], {"binary": "binario"}.get(t["rounding"], t["rounding"]), t["decimals"]["msb"], t["decimals"]["mzt"]))
    w("")


def s_b2(w, L):
    d = J("b2")
    s = d["search"]
    w("### B14.2 — Las cinco cifras sin fuente")
    w("")
    w("Búsqueda literal con fronteras de dígito en %d archivos de texto del repositorio (%s). Incluye "
      "`experiments/results/`, sus checkpoints y `paper/`, que es la fuente del v11. No se recalculó nada." % (
          s["scanned_text_files"], ", ".join(s["extensions"])))
    w("")
    rows = [[k, t["files_with_hits"], t["total_hits"], t["checkpoint_files"], len(t["audit_references"]), len(t["other_files"])]
            for k, t in s["by_token"].items()]
    L.extend(table(["Token", "Archivos con aciertos", "Aciertos", "Checkpoints", "Referencias de A13/A14", "Otros archivos"], rows))
    w("")
    w("Un token de pocos dígitos aparece en muchos contextos ajenos, así que el recuento no identifica la fuente. La fuente se "
      "identificó por contexto (qué magnitud, qué configuración) leyendo los archivos, y el script registra y comprueba cada "
      "una:")
    w("")
    rows = []
    for k, f in d["figures"].items():
        vals = f.get("values", []) + f.get("inputs", [])
        for x in vals:
            rows.append([f["figure"], f["status"], x["file"], x["key"], v6(x["value"]), x["printed"], yn(x["rounds_to_printed"]),
                         f["script"]["path"], "sí (%s)" % short(f["script"]["last_commit"]) if f["script"]["tracked"] else "NO (sin commitear)",
                         yn(f["script"]["writes_file"]), short(f["result"]["commit_added"])])
    L.extend(table(["Cifra", "Estado", "Archivo", "Clave", "Valor", "Impresa", "Redondea a la impresa", "Script",
                    "Script en git", "El script escribe el archivo", "Commit del resultado"], rows))
    w("")
    fi, fii, fiii, fiv = (d["figures"][k] for k in ("i", "ii", "iii", "iv"))
    w("Detalle:")
    w("")
    w("- **(i)** Las tres medias con el piloto α(1) redondean a 0.003. También las %d concordantes: el piloto α(2) del mismo "
      "archivo y `%s` (script `%s`, en git: %s). Todas redondean: %s. Rastro en el manuscrito: %s." % (
          len(fi["concordant"]), fi["concordant_result"]["path"], fi["concordant_script"]["path"],
          yn(fi["concordant_script"]["tracked"]), yn(fi["all_round_to_printed"]), "; ".join(fi["manuscript_trail"])))
    w("- **(ii)** Configuración: %s. Detecciones por configuración: %s. Hay una copia concordante en `%s` (`%s` = %s). "
      "Rastro: %s." % (
          fii["configuration"], ", ".join("%s %d" % kv for kv in fii["detections_by_configuration"].items()),
          fii["concordant"][0]["file"], fii["concordant"][0]["key"], v6(fii["concordant"][0]["value"]),
          "; ".join(fii["manuscript_trail"])))
    w("- **(iii)** %s. Insumos almacenados: medianas observadas de σ̂²_HAC (%s) y ancho de banda mediano (%s). %s. "
      "El archivo se generó el %s, antes del commit `%s` (%s) que corrigió el piloto de Andrews: %s. El propio script calcula el "
      "ancho de banda con el piloto %s. Rastro: %s." % (
          fiii["status"], ", ".join("n = %s: %s → %s" % (x["key"].split("/")[3], v6(x["value"]), x["printed"]) for x in fiii["inputs"]),
          ", ".join("n = %s: %s" % (n, v6(b)) for n, b in fiii["bw_median"].items()), fiii["inputs_note"],
          fiii["result_timestamp"], fiii["hac_fix_commit"], fiii["hac_fix_time"], yn(fiii["result_before_hac_fix"]),
          fiii["script_bandwidth_pilot"], "; ".join(fiii["manuscript_trail"])))
    w("- **(iv)** Fila AR 0.5 de la tabla: %s. Piloto del script: %s. Agregación: %s. Rastro: %s." % (
        ", ".join("%s %s" % kv for kv in fiv["row"].items()), fiv["script_bandwidth_pilot"], fiv["aggregation"],
        "; ".join(fiv["manuscript_trail"])))
    w("")


def s_b3(w, L):
    d = J("b3")
    w("### B14.3 — Verificación del v15")
    w("")
    w("**Q3 sobre las frases que cambiaron.** Registro, plantillas y convenciones de Q3 de B13.Q (`audit13_q_claims`). Cubre las "
      "7 filas de la tabla «Cifras» y, por extensión declarada, las 3 frases de reemplazo de «Cifras retiradas». Texto: `%s` "
      "(sha256 `%s`); referencia v14 `%s`." % (d["manuscript"]["path"], d["manuscript"]["sha256"], d["reference_v14"]["sha256"]))
    w("")
    rows = []
    for k, c in d["claims"].items():
        if not c["found"]:
            rows.append([k, c["changelog_row"], c["file"], "plantilla no encontrada", "", "", "", ""])
            continue
        if not c["numbers"]:
            rows.append([k, c["changelog_row"], "%s:%d" % (c["file"], c["line"]), "(sin cifra)", "—", "—", "frase localizada", "—"])
        for r in c["numbers"]:
            rows.append([k, c["changelog_row"], "%s:%d" % (c["file"], c["line"]), r["printed"], v6(r["value"]),
                         ", ".join(r["conventions"]) or "—", r["verdict"], r["correct"] or "—"])
    L.extend(table(["Frase", "Fila del changelog", "Archivo:línea", "Impresa", "Recalculada", "Convención", "Veredicto", "Correcta"], rows))
    w("")
    ck = [[k, x["check"], yn(x["holds"])] for k, c in d["claims"].items() if c.get("found") for x in c["checks"]]
    if ck:
        L.extend(table(["Frase", "Comprobación", "Se cumple"], ck))
        w("")
    s = d["sec42"]
    w("**Definición de sec4 §4.2.** Literal del v15: %s. Da %d celdas; el conjunto es el mismo que con la definición de B13.Q: "
      "%s (sólo v15: %s; sólo B13.Q: %s). Con ella: más potencia en %d, menos en %d (máx. %s pp)." % (
          s["definition"], len(s["cells"]), yn(s["same_cells_as_b13q"]), ", ".join(s["only_v15"]) or "ninguna",
          ", ".join(s["only_b13q"]) or "ninguna", len(s["higher"]), len(s["lower"]), g(s["max_lower_pp"], 2)))
    w("")
    a = d["attrib"]
    w("**tab:attrib.** El v15 hace `\\input` del tabular (línea %s) y de la nota (línea %s); los dos son idénticos a la exportación "
      "de B13.Q: %s. Queda algún bloque TRANSCRIBED: %s. Pasa: **%s**." % (
          a["tab_attrib_audit13"]["input_line"], a["tab_attrib_note_audit13"]["input_line"],
          yn(a["tab_attrib_audit13"]["identical"] and a["tab_attrib_note_audit13"]["identical"]), yn(a["transcribed_block_left"]),
          yn(a["passes"])))
    w("")
    w("**Completitud del changelog.** Filas de «Cifras» y «Cifras retiradas» sin frase verificada: %s. Bloques del diff v14 → v15 "
      "en los archivos de texto: %d; sin asignar a una fila o a una figura: %d." % (
          len(d["changelog"]["rows_without_claim"]), len(d["hunks"]), len(d["hunks_unassigned"])))
    w("")
    rows = [[h["file"], "%d–%d" % tuple(h["v14_lines"]), "%d–%d" % tuple(h["v15_lines"]), h["assigned"] or "SIN ASIGNAR"] for h in d["hunks"]]
    L.extend(table(["Archivo", "Líneas v14", "Líneas v15", "Asignado a"], rows))
    w("")
    cv = d["coverage"]["counts"]
    w("**Cobertura de las líneas cambiadas.** Números con decimales: %d cubiertos por una frase verificada, %d de diseño, %d sin "
      "verificar." % (cv["cubierta"], cv["diseno"], cv["no verificada"]))
    w("")
    w("**Cifras retiradas.** Ninguna aparece en el texto del v15: **%s**." % yn(d["retired_absent"]))
    w("")
    rows = [[k, len(h), "; ".join("%s:%d «%s»" % (x["file"], x["line"], x["context"]) for x in h) or "—"] for k, h in d["retired"].items()]
    L.extend(table(["Búsqueda", "Apariciones", "Dónde"], rows))
    w("")
    w("La única aparición del token 0.6 es la cota nueva «within 0.6 points» de sec5 §5.6, no el 0.6 % retirado.")
    w("")
    ph = d["phrases"]
    w("**Q4 con la regla corregida.** Estos patrones siguen con las zonas de B13.Q: «collapses faster», «does not collapse as "
      "fast», «no cost in size», «no effect on size», «RM-GLS» y «theta = 0.02». Las apariciones de «rolling means» y "
      "«two-channel» se clasifican por la frase que las contiene (%s). Registro: %d entradas; sin usar: %d." % (
          "; ".join("%s = %s" % kv for kv in ph["classes"].items()), ph["registry_entries"], len(ph["registry_unused"])))
    w("")
    rows = [[k] + [x[s] for s in ("prohibida", "permitida", "excluida", "informar", "sin clasificar", "clasificacion ambigua")]
            for k, x in ph["summary"].items()]
    L.extend(table(["Patrón", "Prohibida", "Permitida", "Excluida", "Informar (M)", "Sin clasificar", "Ambigua"], rows))
    w("")
    w("A informar (afirman algo sobre MSB-B): %d." % len(ph["to_report"]))
    w("")
    rows = [[h["file"], h["line"], h["pattern"], h["status"], h.get("justification") or "—", "«%s»" % h["context"]] for h in ph["to_report"]]
    if rows:
        L.extend(table(["Archivo", "Línea", "Patrón", "Estado", "Justificación", "Contexto"], rows))
        w("")
    rows = [[h["file"], h["line"], h["pattern"], h["cls"], h["justification"]] for h in ph["hits"] if h["rule"] == "corregida"]
    w("Clasificación completa:")
    w("")
    L.extend(table(["Archivo", "Línea", "Patrón", "Clase", "Justificación"], rows))
    w("")


# ---------------------------------------------------------------------------
# 2-7
# ---------------------------------------------------------------------------
def s_gates(w, L):
    w("## 2. Compuertas")
    w("")
    d = J("b1")["paso0"]
    b0 = J("b0")
    b3 = J("b3")
    w("**Paso 0.** Regla del encargo: |Δ| = 0 en las columnas que el bloque usa; en el resto de columnas comunes, ≤ 1e-12 con "
      "declaración.")
    w("")
    rows = [["B14.0", "tabulares y figuras del v15 = exportados por A13 y B13.Q (byte a byte)",
             "%d archivos" % len(b0["files_vs_exports"]), "pasa" if b0["all_identical"] else "NO pasa"],
            ["B14.1 (columnas usadas)", "q_0.05 de c|msb, c|mzt, ct|msb, ct|mzt = b101 sim_thresholds y bA_ma iid_quantiles",
             "%d comparaciones; máx. |Δ| = %s" % (d["used_n"], e(d["used_max_abs_diff"])), "pasa" if d["used_max_abs_diff"] == 0 else "NO pasa"],
            ["B14.1 (resto de columnas comunes)", "q_0.05 de dfgls, adf, pp y cuantiles RM de bA_ma, ≤ 1e-12",
             "%d comparaciones; máx. |Δ| = %s; distintos de 0: %d" % (d["other_n"], e(d["other_max_abs_diff"]), len(d["other_nonzero"])),
             "pasa" if d["passes"] else "NO pasa"],
            ["B14.1 (cobertura)", "los 16 valores al 5 % que ya existían quedan cubiertos por el Paso 0",
             yn(d["all_used_5pct_covered"]), "pasa" if d["all_used_5pct_covered"] else "NO pasa"],
            ["B14.3 tab:attrib", "tabular y nota del v15 = exportación de B13.Q", yn(b3["attrib"]["passes"]),
             "pasa" if b3["attrib"]["passes"] else "NO pasa"]]
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], rows))
    w("")
    nc = d["not_common"]
    w("Entradas guardadas sin columna común en las muestras de A10 (no entran en el Paso 0): %s." % (
        ", ".join(sorted({"%s|%s" % (x["case"], x["column"]) for x in nc})) or "ninguna"))
    w("")


def s_prov(w, L):
    w("## 3. Procedencia")
    w("")
    man = J("man")["entries"]
    rows = [[k, "`%s`" % v["sha256"], v["script"], short(v["commit"]), yn(v["code_all_committed"])]
            for k, v in sorted(man.items()) if "resultados_auditoria" not in k]
    L.extend(table(["Archivo", "sha256", "Script", "Commit", "Código commiteado"], rows))
    w("")
    p = J("b0")["protocol"]
    w("Protocolo `%s`: commit `%s` (%s), sha256 en disco `%s`, commiteado `%s`." % (
        p["path"], short(p["commit_added"]), p["commit_time"], p["sha256_disk"], p["sha256_committed"]))
    w("")
    v = J("b1")["provenance"]["versions"]
    w("Versiones: %s." % ", ".join("%s %s" % kv for kv in v.items()))
    w("")


def s_dev(w, L):
    w("## 4. Desviaciones")
    w("")
    rows = [["B14.3: en las cotas inferiores («at least») se acepta también el redondeo hacia abajo, simétrico del «hacia arriba» "
             "de Q3 en las superiores", "Q3 sólo tenía la convención de cota superior; sin la simétrica marcaba como incorrecta la "
             "cifra que su propia función `correct(…, \"lower\")` propone", "Después de ver el resultado de sec5_dgp5b",
             "sec5_dgp5b: 7.9 pasa de «no reproduce» a «reproduce como cota»; la desigualdad se comprueba igual"],
            ["B14.2: los archivos de las propias auditorías A13/A14 que citan las cifras se separan como «referencias», no como "
             "fuentes", "Citan el manuscrito, no lo producen", "Al escribir la búsqueda", "Sólo presentación del recuento"]]
    L.extend(table(["Desviación", "Motivo", "Cuándo", "Efecto"], rows))
    w("")
    w("Decisiones tomadas en el protocolo, antes de calcular (no son desviaciones): EE bootstrap exacto sin aleatoriedad (lectura 5); "
      "fragmento de nota del tabular (lectura 7); extensiones de B14.0 y B14.3 (lecturas 2 y 9); registro de clasificación de Q4 "
      "(lectura 10).")
    w("")


def s_not(w, L):
    w("## 5. No ejecutado")
    w("")
    f3 = J("b2")["figures"]["iii"]
    w("- **B14.2 (iii)**: 6.9 %% y 0.6 %% no están almacenados como tales. No se calcularon a partir de los insumos almacenados (%s) "
      "porque el encargo dice «no recalcules». Tampoco se reprodujeron con el piloto α(1)." % ", ".join(x["key"] for x in f3["inputs"]))
    w("- **Familia 150**: reservada, sin uso; ningún bloque necesitó números aleatorios.")
    w("- **B12.D**: sigue cancelado.")
    w("")


def s_concl(w, L):
    w("## 6. Conclusiones")
    w("")
    b0, b1, b2, b3 = J("b0"), J("b1"), J("b2"), J("b3")
    bad = b3["not_reproduced"]
    w("- B14.0: los %d archivos de tablas y las %d figuras del v15 son idénticos byte a byte a los exportados: %s." % (
        b0["n_tables_dir_files"], b0["n_figures"], yn(b0["all_identical"])))
    w("- B14.1: %d valores críticos, %d nuevos, con EE bootstrap exacto; Paso 0 con máx. |Δ| = %s en %d comparaciones de las "
      "columnas usadas y %s en %d del resto. Salidas: CSV, tabular y nota en `tables_audit14/`." % (
          b1["checks"]["n_values"], b1["checks"]["n_new"], e(b1["paso0"]["used_max_abs_diff"]), b1["paso0"]["used_n"],
          e(b1["paso0"]["other_max_abs_diff"]), b1["paso0"]["other_n"]))
    loc = [k for k, f in b2["figures"].items() if f["stored_as_such"]]
    w("- B14.2: localizadas con archivo, clave, valor y script: %s. %s: %s." % (
        ", ".join("(%s)" % k for k in loc), ", ".join("(%s)" % k for k, f in b2["figures"].items() if not f["stored_as_such"]),
        b2["figures"]["iii"]["status"]))
    w("- B14.3: %d frases verificadas; cifras que no se reproducen: %d%s. Frases de Q4 a informar: %d. Cifras retiradas "
      "ausentes: %s. Changelog completo: %s." % (
          sum(1 for c in b3["claims"].values() if c["found"]), len(bad),
          (" (" + "; ".join("%s:%d %s → %s" % (x["file"], x["line"], x["printed"], x["correct"]) for x in bad) + ")") if bad else "",
          len(b3["phrases"]["to_report"]), yn(b3["retired_absent"]),
          yn(not b3["hunks_unassigned"] and not b3["changelog"]["rows_without_claim"])))
    w("")


def s_anom(w, L):
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    b3, b2 = J("b3"), J("b2")
    q13 = J("q13")["claims"]
    w("### (a) Cifras del v15 que no se sostienen")
    w("")
    for x in b3["not_reproduced"]:
        prev = q13.get(x["claim"], {}).get("numbers", [])
        pv = ("; en B13.Q la cifra del v14 (%s) tenía el veredicto «%s»" % (prev[0]["printed"], prev[0]["verdict"])) if prev else ""
        w("- `%s:%d` (%s): impresa %s, valor %s; %s. Cifra correcta: **%s**%s." % (
            x["file"], x["line"], x["claim"], x["printed"], v6(x["value"]), ", ".join(x["conventions"]), x["correct"], pv))
    if not b3["not_reproduced"]:
        w("- Ninguna.")
    w("")
    w("### (b) Frases de Q4 que afirman algo sobre MSB-B")
    w("")
    for h in b3["phrases"]["to_report"]:
        w("- `%s:%d` («%s»): %s. Contexto: «%s»." % (h["file"], h["line"], h["pattern"], h.get("justification") or h["status"], h["context"]))
    if not b3["phrases"]["to_report"]:
        w("- Ninguna.")
    w("")
    w("### (c) Fuentes de B14.2: advertencias")
    w("")
    f = b2["figures"]
    for k in ("i", "ii", "iii", "iv"):
        s = f[k]["script"]
        if not s["tracked"]:
            w("- (%s) El script productor `%s` no está en git (sha256 `%s`, modificado %s); el resultado sí (commit `%s`)." % (
                k, s["path"], s["sha256"], s["mtime_utc"], short(f[k]["result"]["commit_added"])))
    w("- (iii) Los insumos de 6.9 %% y 0.6 %% se produjeron antes de la corrección del piloto (%s) y con el piloto %s en el propio "
      "script. Si el v16 reintroduce esas cifras, describen el estimador registrado, no el de la ecuación del artículo." % (
          f["iii"]["hac_fix_commit"], f["iii"]["script_bandwidth_pilot"]))
    w("- (iv) %s." % f["iv"]["aggregation"])
    w("")
    w("### (d) B13.Q: cifras que declaró sin JSON y sí tenían fuente")
    w("")
    wj = [x for x in J("q13")["without_json"]]
    loc = ", ".join("(%s)" % k for k, f in b2["figures"].items() if f["stored_as_such"])
    w("B13.Q listó sin JSON: %s. B14.2 localiza %s en archivos del repositorio. El v15 retiró esas cifras por ese motivo y "
      "podría reintroducirlas en el v16 con la fuente de la tabla de B14.2." % ("; ".join(
          "%s:%d %s" % (x["file"], x["line"], x["printed"]) for x in wj), loc))
    w("")


def master(w, L):
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    b1 = J("b1")
    rows = []
    for v in b1["values"]:
        rows.append(["%s %s n=%d α=%g" % (LABEL[v["stat"]], v["case"], v["n"], v["alpha"]), v6(v["critical_value"]),
                     "EE %s" % e(v["bootstrap_se"]), "—", v["N_cal"], "— (semilla de calibración %d)" % b1["config"]["cal_seed"],
                     F["b1"], "values[stat=%s, case=%s, n=%d, alpha=%g].critical_value" % (v["stat"], v["case"], v["n"], v["alpha"])])
    for k, f in J("b2")["figures"].items():
        for x in f.get("values", []) + f.get("inputs", []):
            rows.append(["B14.2 (%s) %s" % (k, x["key"]), v6(x["value"]), "—", "—", "—", "—", x["file"].split("/")[-1], x["key"]])
    for k, c in J("b3")["claims"].items():
        if c.get("found"):
            for i, r in enumerate(c["numbers"]):
                rows.append(["B14.3 %s #%d (%s:%d)" % (k, i, c["file"], c["line"]), v6(r["value"]), "—", "—", "—", "—", F["b3"],
                             "claims.%s.numbers[%d].value" % (k, i)])
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"], rows))
    w("")


def main():
    L = []

    def w(s):
        L.append(s)
    b0 = J("b0")
    w("# Auditoría A14 — Valores críticos del suplemento, fuentes pendientes y verificación de v15")
    w("")
    w("Protocolo `%s` (commit `%s`). Manuscrito: `%s` (sha256 `%s`), de sólo lectura; no se editó ningún `.tex`. Ninguna "
      "simulación nueva; la familia %d no se usa." % (b0["protocol"]["path"], short(b0["protocol"]["commit_added"]),
                                                      b0["manuscript"]["path"], b0["manuscript"]["sha256"], b0["family"]["reserved"]))
    w("")
    w("## 1. Resultados")
    w("")
    s_b0(w, L)
    s_b1(w, L)
    s_b2(w, L)
    s_b3(w, L)
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
