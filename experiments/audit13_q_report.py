"""
Auditoria A13 - B13.Q: bloques del reporte (seccion B13.Q de §1 y sus filas en §2-§7 y en la
tabla maestra). Solo lee JSON; lo usa audit13_generate_report.py y lo recorre
tests/test_no_literals_audit13.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402

FQ = {"inv": "q_inventory_audit13.json", "attrib": "q_attrib_audit13.json", "figs": "figures_audit13q.json",
      "claims": "q_claims_audit13.json", "phrases": "q_phrases_audit13.json", "supp": "q_supplement_audit13.json"}
_C = {}


def have():
    return all(C.have(v) for v in FQ.values())


def J(k):
    if k not in _C:
        _C[k] = C.read_json(FQ[k])
    return _C[k]


def fmt(x):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "sí" if x else "no"
    if isinstance(x, int):
        return "%d" % x
    if isinstance(x, float):
        return "%.3e" % x if x and abs(x) < 10 ** -3 else "%.6g" % x
    return str(x)


def section(w, L, table, md_cell):
    inv, at, fg, cl, ph, sp = J("inv"), J("attrib"), J("figs"), J("claims"), J("phrases"), J("supp")
    w("### B13.Q — Coherencia final sobre v14, tab:attrib y leyendas")
    w("")
    a = inv["amendment"]
    w("Enmienda `%s` (commit `%s`, %s; sha256 en disco `%s`, commiteado `%s`). Sin simulaciones nuevas; la familia 144 no se usa." % (
        a["path"], a["commit_added"][:7], a["commit_time"], a["sha256_disk"], a["sha256_committed"]))
    w("")
    w("**Q0. Entrada.** `%s`, sha256 `%s` (%d bytes), leído dentro del zip. Tabulares y figuras del v14 frente a los exportados por "
      "A13: %d archivos, %s." % (inv["manuscript"]["path"], inv["manuscript"]["sha256"], inv["manuscript"]["bytes"], len(inv["files_vs_a13"]),
                                 "todos idénticos byte a byte" if inv["all_identical"] else "HAY DIFERENCIAS"))
    w("")
    diffs = [k for k, v in inv["files_vs_a13"].items() if not v["identical"]]
    if diffs:
        L.extend(table(["Archivo del v14", "sha256 v14", "sha256 A13"], [[k, inv["files_vs_a13"][k]["sha256_v14"],
                                                                          inv["files_vs_a13"][k]["sha256_local"]] for k in diffs]))
        w("")
    tr = at["comparison_v14"]
    w("**Q1. tab:attrib.** Fuente `%s` (sha256 `%s`). Redondeo: %s (convenciones probadas: %s). Comparación con el bloque TRANSCRIBED "
      "de `%s`: %d celdas; %d distintas; %d dobles redondeos del v14. Nota: %s." % (
          at["source"], at["source_sha256"], at["rounding"], "; ".join("%s → %d distintas, %d dobles redondeos" % (m, v["number_mismatches"],
                                                                                                              v["double_rounding"])
                                                                        for m, v in at["rounding_trials"].items()),
          at["v14_file"], tr["cells_compared"], len(tr["number_mismatches"]), len(tr["double_rounding_in_v13"]),
          "coincide cifra a cifra" if at["note"]["all_equal"] else "HAY DIFERENCIAS"))
    w("")
    heads = ["Fila", "(a) HAC", "(b) s²_AR", "(b′) s²_AR, PQ", "(c) MSB-GLS asint.", "(a)−(b′)", "(b′)−(b)", "(b′)−(c)"]
    rows = []
    last = None
    for r in at["rows"]:
        if r["section"] != last:
            rows.append(["*%s*" % md_cell(r["section"])] + [""] * (len(heads) - 1))
            last = r["section"]
        rows.append([md_cell(r["keys"][0])] + [md_cell(c) for c in r["mine"]])
    L.extend(table(heads, rows))
    w("")
    for m in tr["number_mismatches"]:
        w("- Celda distinta: %s." % m)
    for m in tr["double_rounding_in_v13"]:
        w("- Fila %s, columna %d: el v14 imprime %s; el JSON da %s, que a %d decimales es %s. El impreso es un doble redondeo." % (
            md_cell(m["row"][0]), m["col"], m["printed"], fmt(m["value"]), len(m["printed"].split(".")[1]), md_cell(m["mine"])))
    p0 = at["paso0"]
    w("- Paso 0: tasas = rejections/n, máx. |Δ| = %s (columnas usadas); diferencias frente a diferencia de tasas, máx. %s, y medias de "
      "`by_n` frente a la media de sus celdas, máx. %s (columnas no usadas; %d valores no nulos, todos ≤ %s)." % (
          fmt(p0["rates_vs_rejections_over_n"]), fmt(p0["diff_vs_rate_difference"]), fmt(p0["by_n_mean_vs_cells"]),
          len(p0["nonzero_other_columns"]), fmt(p0["tolerance_other_columns"])))
    w("- Salidas: `%s` (sha256 `%s`) y `%s` (sha256 `%s`, la nota con las medias de (a)−(b) y (b)−(c))." % (
        at["tex"], at["tex_sha256"], at["note_tex"], at["note_sha256"]))
    w("")
    w("**Q2. Figuras con rótulos del v14.** Etiqueta «%s» → «%s»; en `%s` se omite la serie «%s» (`%s`). Paso 0 frente a "
      "`figures_audit13.json`: %s." % (fg["label_change"][0], fg["label_change"][1], fg["dropped_series"]["figure"],
                                       fg["dropped_series"]["label"], fg["dropped_series"]["key"], "pasa" if fg["paso0_passes"] else "FALLA"))
    w("")
    L.extend(table(["Figura", "sha256", "Llamadas A13 → Q", "Eliminadas", "Resto idéntico bit a bit", "Eliminadas = msbhac",
                    "Sin «RM-GLS»", "Rótulos"],
                   [[k, "`%s`" % v["sha256"], "%d → %d" % (v["calls_a13"], v["calls_q"]), v["removed_calls"],
                     fmt(v["remaining_identical_to_a13"]), fmt(v["removed_are_msbhac"]), fmt(v["old_label_absent"]),
                     "; ".join(v["texts"])] for k, v in fg["figures"].items()]))
    w("")
    nums = [(k, c, r) for k, c in cl["claims"].items() if c.get("found") for r in c["numbers"]]
    counts = {}
    for _, _, r in nums:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    sw = cl["sweep"]["counts"]
    w("**Q3. Coherencia del v14.** %d frases localizadas (%d sin localizar), %d cifras recalculadas: %s. Comprobaciones "
      "cualitativas: %d, de las cuales %d no se cumplen. Barrido de los %d números con decimales del texto: %s." % (
          sum(1 for c in cl["claims"].values() if c.get("found")), len(cl["templates_not_found"]), len(nums),
          "; ".join("%s %d" % kv for kv in sorted(counts.items())),
          sum(len(c["checks"]) for c in cl["claims"].values() if c.get("found")), len(cl["failed_checks"]), sum(sw.values()),
          "; ".join("%s %d" % kv for kv in sw.items())))
    w("")
    t = cl["theta_vs_v13"]
    w("Lista del CHANGELOG_v14 §3: frases %s. Definición usada para «12 de 23»: %s; θ = 0 más potente en %d de %d, menos en %d "
      "(máx. %s pp); en DGP 3 menos distorsionado en %d de %d y más en %d." % (
          ", ".join("`%s`" % k for k in cl["changelog_s3_claims"]), t["definition"], len(t["higher"]), len(t["unsaturated"]),
          len(t["lower"]), fmt(t["max_lower_pp"]), len(t["less_distorted"]), len(t["dgp3"]), len(t["more_distorted"])))
    w("")
    rows = []
    for k, c, r in nums:
        rows.append(["`%s:%d`" % (c["file"], c["line"]), k, r["printed"], fmt(r["value"]), ", ".join(r["conventions"]) or "—",
                     r["verdict"] if r["verdict"] != "no reproduce" else "**no reproduce → %s**" % r["correct"]])
    L.extend(table(["Archivo:línea", "Frase", "Impreso", "Recalculado", "Convención", "Veredicto"], rows))
    w("")
    rows = [["`%s:%d`" % (c["file"], c["line"]), k, x["check"], "sí" if x["holds"] else "**no**"]
            for k, c in cl["claims"].items() if c.get("found") for x in c["checks"]]
    w("Comprobaciones cualitativas (frases sin cifra o con condición):")
    w("")
    L.extend(table(["Archivo:línea", "Frase", "Comprobación", "¿Se cumple?"], rows))
    w("")
    w("Fuentes por frase:")
    w("")
    L.extend(table(["Frase", "Archivo:línea", "Fuente"], [[k, "`%s:%s`" % (c["file"], c.get("line")), c.get("source", "—")]
                                                         for k, c in cl["claims"].items()]))
    w("")
    w("**Q4. Frases prohibidas.** Búsqueda literal en la fuente del v14, fuera de §5.11, §5.12 y tab:deviations. Resumen: %s. "
      "Total de apariciones prohibidas: %d." % ("; ".join("«%s»: %s" % (k, ", ".join("%s %d" % sv for sv in v.items()))
                                                         for k, v in ph["summary"].items()), ph["forbidden_total"]))
    w("")
    L.extend(table(["Patrón", "Archivo:línea", "Zona", "Estado", "Contexto"],
                   [[h["pattern"], "`%s:%d`" % (h["file"], h["line"]), h["zone"], ("**%s**" % h["status"]) if h["status"] == "prohibida"
                     else h["status"], h["context"]] for h in ph["hits"]]))
    w("")
    w("**Q5. Suplemento: valores críticos de MSB-GLS y MZ_t-GLS con N_cal = 5·10⁵.** Presentes: %d; faltan: %d. Muestras de "
      "calibración de A10: %s." % (len(sp["present"]), len(sp["missing"]), "; ".join(
          "n = %s: %d filas, columnas %s" % (n, v["rows"], "todas" if all(v["has_columns"].values()) else "INCOMPLETAS")
          for n, v in sp["calibration_samples"].items())))
    w("")
    rows = []
    for k, v in sp["found"].items():
        s = v["sources"]
        rows.append([v["case"], v["n"], v["proc"], v["level"], "; ".join("%s (`%s`, N_cal %d)" % (fmt(x["value"]), x["json"], x["N_cal"])
                                                                        for x in s) or "**falta**",
                     fmt(v["sources_agree"]) if s else "—"])
    L.extend(table(["Caso", "n", "Test", "Nivel", "Valor crítico (fuente)", "Fuentes coinciden"], rows))
    w("")


def paso0_rows():
    at, fg = J("attrib"), J("figs")
    p0 = at["paso0"]
    return [["B13.Q Q0", "tabulares y figuras del v14 = exportados por A13", "%d archivos" % len(J("inv")["files_vs_a13"]),
             "pasa" if J("inv")["all_identical"] else "FALLA"],
            ["B13.Q Q1 (columnas usadas)", "tasas = rejections/n", "máx. |Δ| = %s" % fmt(p0["rates_vs_rejections_over_n"]),
             "pasa" if p0["rates_vs_rejections_over_n"] == 0 else "FALLA"],
            ["B13.Q Q1 (resto)", "diferencias y medias recompuestas ≤ 1e-12 (regla corregida de la enmienda)",
             "máx. %s; %d valores no nulos declarados" % (fmt(max(p0["diff_vs_rate_difference"], p0["by_n_mean_vs_cells"])),
                                                          len(p0["nonzero_other_columns"])), "pasa" if p0["passes"] else "FALLA"],
            ["B13.Q Q2", "series restantes idénticas bit a bit a A13; eliminadas = msbhac",
             "%d figuras" % len(fg["figures"]), "pasa" if fg["paso0_passes"] else "FALLA"]]


def dev_rows():
    t = J("claims")["theta_vs_v13"]
    return [["Q1: la nota de tab:attrib se exporta como fragmento aparte (`tab_attrib_note_audit13.tex`)", "La nota va fuera del tabular en el v14",
             "Antes de correr (lectura 3)", "Ninguno"],
            ["Q3: definición de «no saturada»: %s" % t["definition"], "Es la definición que reproduce «23» del v14; la de la lectura 5 (sólo min < 0.99) da %d"
             % t["unsaturated_reading5"], "Después de ver el recuento", "Ninguno sobre 12, 2 y 0.4"],
            ["Q3: las cotas del texto («within», «at most», «below», «at least») se comprueban como desigualdades además del redondeo",
             "Una cota puede redondear bien y ser falsa", "Al escribir el registro", "Tres cifras marcadas en §7(d)"],
            ["Q4: «rolling means» y «two-channel» se buscan sin distinguir mayúsculas; las formas con guion («rolling-means») no cuentan",
             "Búsqueda literal", "Antes de correr (lectura 6)", "Ninguno"]]


def not_executed(w):
    sp = J("supp")
    w("- **Q5 (suplemento)**: faltan en los JSON %d valores críticos de MSB-GLS y MZ_t-GLS (niveles %s; los del 5 %% están). Las "
      "muestras de calibración de A10 (N_cal = 500 000) tienen las columnas; no se calcularon, por el encargo." % (
          len(sp["missing"]), ", ".join(sorted({sp["found"][k]["level"] for k in sp["missing"]}))))
    cl = J("claims")
    w("- **Q3**: cifras del v14 sin JSON localizado: %s." % "; ".join("`%s:%s` %s (%s)" % (x["file"], x["line"], x["printed"], x["claim"])
                                                                     for x in cl["without_json"]))


def conclusions(w):
    cl, ph, sp = J("claims"), J("phrases"), J("supp")
    nums = [r for c in cl["claims"].values() if c.get("found") for r in c["numbers"]]
    w("- B13.Q: tab:attrib exportado desde JSON; %d de %d celdas del bloque TRANSCRIBED coinciden y la única distinta es un doble "
      "redondeo del v14." % (J("attrib")["comparison_v14"]["cells_compared"] - len(J("attrib")["comparison_v14"]["double_rounding_in_v13"])
                             - len(J("attrib")["comparison_v14"]["number_mismatches"]), J("attrib")["comparison_v14"]["cells_compared"]))
    w("- B13.Q: %d cifras del v14 recalculadas; %d no se reproducen y %d comprobaciones cualitativas no se cumplen (§7(d)); %d cifras "
      "sin JSON localizado." % (len(nums), len(cl["not_reproduced"]), len(cl["failed_checks"]), len(cl["without_json"])))
    w("- B13.Q: %d apariciones prohibidas de las frases de Q4; seis figuras `_audit13q` con «MSB-B»; faltan %d valores críticos del "
      "suplemento prometido." % (ph["forbidden_total"], len(sp["missing"])))


def anomalies(w):
    cl, ph = J("claims"), J("phrases")
    w("### (d) B13.Q: cifras y frases del v14 que no se sostienen")
    w("")
    for x in cl["not_reproduced"]:
        extra = (" (%s)" % ", ".join(c for c in x["conventions"] if "cota" in c)) if x["conventions"] else ""
        w("- `%s:%s` (`%s`): impreso %s; recalculado %s; cifra correcta %s%s." % (x["file"], x["line"], x["claim"], x["printed"],
                                                                               fmt(x["value"]), x["correct"], extra))
    for x in cl["failed_checks"]:
        w("- `%s:%s` (`%s`): no se cumple «%s»." % (x["file"], x["line"], x["claim"], x["check"]))
    for m in J("attrib")["comparison_v14"]["double_rounding_in_v13"]:
        w("- tab:attrib (bloque TRANSCRIBED del v14), fila %s: impreso %s, correcto %s (doble redondeo)." % (m["row"][0], m["printed"], m["mine"]))
    for h in ph["hits"]:
        if h["status"] == "prohibida":
            w("- Frase prohibida «%s» en `%s:%d` (zona %s)." % (h["pattern"], h["file"], h["line"], h["zone"]))
    w("")


def master_rows(f):
    at = J("attrib")
    rows = []
    for r in at["rows"]:
        for lab, v in zip(("(a)", "(b)", "(b′)", "(c)", "(a)−(b′)", "(b′)−(b)", "(b′)−(c)"), r["values"]):
            if v is not None:
                rows.append(["tab:attrib %s %s" % (r["json_key"], lab), f(v), "—", "—", "—", "95 / 102 / 136", at["source"],
                             "cells|by_n.%s" % r["json_key"]])
    for x in J("claims")["not_reproduced"]:
        rows.append(["v14 corregida `%s:%s` (%s)" % (x["file"], x["line"], x["claim"]), x["correct"], "recalculado %s" % fmt(x["value"]),
                     "—", "—", "—", FQ["claims"], "not_reproduced"])
    return rows
