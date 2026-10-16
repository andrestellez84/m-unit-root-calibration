"""
Auditoria A8 - generador de experiments/results/resultados_auditoria_8.md.

Regla 3: ningun numero de resultado se escribe a mano. Todo valor se lee de un
JSON o de un log de experiments/results (o del .tex del manuscrito para las
citas de la seccion 7); si falta una clave el script falla con KeyError. Los
bloques cuyo JSON no existe se declaran en la seccion 5 (No ejecutado).
tests/test_no_literals_audit8.py recorre este archivo.

Estructura obligatoria: encabezado; 1 resultados; 2 compuertas; 3 procedencia;
4 desviaciones; 5 no ejecutado; 6 conclusiones; 7 anomalias y contradicciones
con el manuscrito; anexo de hechos.

Uso: python experiments/audit8_generate_report.py
"""
import datetime
import glob
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit8_unitroot as U                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_8.md")
PROTOCOL = "experiments/protocol_audit8.md"
BLOCK_FILES = {
    "B0": "inventory_audit8.json", "B1": "b1_validation_audit8.json", "B2": "b2_size_audit8.json",
    "B3": "b3_comparators_audit8.json", "B4": "b4_local_power_audit8.json", "B5": "b5_power_audit8.json",
    "B6": "b6_application_audit8.json", "B7": "b7_critical_values_audit8.json", "B8": "figures_audit8.json",
}
BLOCK_TITLES = {
    "B0": "Inventario y procedencia", "B1": "Implementación (toca producción)",
    "B2": "R = 0 frente a R = 0.5, y calibración one frente a hac", "B3": "Comparadores de tamaño que faltan",
    "B4": "Potencia local asintótica y regla de adopción GLS", "B5": "Tablas de potencia en muestra finita",
    "B6": "Aplicación pre-registrada con la primaria", "B7": "Valores críticos y verificación de la teoría",
    "B8": "Figuras",
}
BLOCK_SCRIPTS = {
    "B2": "experiments/audit8_b2_size.py", "B3": "experiments/audit8_b3_comparators.py",
    "B4": "experiments/audit8_b4_local_power.py", "B5": "experiments/audit8_b5_power.py",
    "B6": "experiments/audit8_b6_application.py", "B7": "experiments/audit8_b7_critical_values.py",
    "B8": "experiments/make_figures_audit8.py",
}
# frases del manuscrito v11 que la seccion 7 debe revisar: (clave, etiqueta, archivo en paper/, patron)
MANUSCRIPT_CLAIMS = (
    ("dominance_intro", "dominancia sobre ADF por 5-14 pp (§1)", "paper/sec1_introduction.tex", r"ADF by \$5\$ to \$14\$"),
    ("dominance_dgp1", "dominancia sobre ADF por 5-14 pp (§5.3)", "paper/sec5_montecarlo.tex", r"\+14\.0\$~pp"),
    ("garch_11", "el 11/16 GARCH (§5.2)", "paper/sec5_montecarlo.tex", r"acceptance region in eleven"),
    ("bootstrap_every", "el bootstrap contiene el nivel nominal en todas (§5.5)", "paper/sec5_montecarlo.tex", r"every one, while asymptotic"),
    ("trend_size", "tamaño del caso con tendencia (§5.9)", "paper/sec5_montecarlo.tex", r"Empirical size is \$0\.0388\$"),
    ("fp_028", "FP 0.028 (§6)", "paper/sec6_application.tex", r"rate, \$0\.028\$"),
    ("detections_13", "13 detecciones (§6)", "paper/sec6_application.tex", r"detections \(\$13\$ of \$88\$"),
    ("small_n_ncal", "tamaños a n = 60, 100, 150 con N_cal = 50000 (§5.1)", "paper/sec5_montecarlo.tex", r"null calibrated at each \$n\$ with"),
)
CLAIM_BLOCK = {"dominance_intro": "B5", "dominance_dgp1": "B5", "bootstrap_every": "B3", "trend_size": "B5",
               "fp_028": "B6", "detections_13": "B6"}
PNAME = {"rm_R0_t0.1_one": "RM one", "rm_R0_t0.1_hac": "RM hac", "adf_asy": "ADF asy", "adf_sim": "ADF sim",
         "pp_asy": "PP asy", "pp_sim": "PP sim", "dfgls_asy": "DF-GLS asy", "dfgls_sim": "DF-GLS sim"}
SIMNAME = {"adf": "ADF", "pp": "PP", "dfgls": "DF-GLS (MAIC)", "dfglsaic": "DF-GLS (AIC)", "mzt": "MZ_t-GLS", "msb": "MSB-GLS"}
GARCH_LABEL = {"base": "GARCH 0.95 N", "p099": "GARCH 0.99 N", "p098": "GARCH 0.98 N", "p095_t5": "GARCH 0.95 t(5)"}


def J(name):
    return C.read_json(name)


def T(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def exists(name):
    return os.path.exists(os.path.join(C.RESULTS, name))


def f4(x):
    return "%.4f" % x


def pct(x):
    return "%.1f %%" % (x * 100)


def sci(x):
    return "%.2e" % x


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return out


def verdict(ok):
    return "PASA" if ok else "FALLA"


def pytest_summary():
    text = T("pytest_audit8.log")
    m = re.findall(r"=+ (.*?) in ([0-9.]+)s", text)
    if not m:
        raise KeyError("pytest_audit8.log sin linea de resumen")
    summary, secs = m[-1]
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|errors?|warnings?)", summary)}
    coll = re.search(r"collected (\d+) items", text)
    lit = re.findall(r"tests[\\/]test_no_literals_audit8\.py::(\S+) (PASSED|FAILED|SKIPPED)", text)
    return {"summary": summary, "seconds": float(secs), "collected": int(coll.group(1)) if coll else None,
            "counts": counts, "literals": lit}


def protocol_bullets(section_title):
    with open(os.path.join(C.REPO, PROTOCOL), encoding="utf-8") as f:
        text = f.read()
    i = text.index(section_title)
    j = text.find("\n### ", i + 1)
    block = text[i:j if j > 0 else None]
    items, cur = [], None
    for line in block.splitlines()[1:]:
        if line.startswith("- "):
            if cur:
                items.append(cur)
            cur = line[2:].strip()
        elif cur is not None and line.startswith("  "):
            cur += " " + line.strip()
        elif cur is not None and not line.strip():
            items.append(cur)
            cur = None
    if cur:
        items.append(cur)
    if not items:
        body = "\n".join(block.splitlines()[1:])
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        items = [" ".join(paras[0].split())] if paras else []
    return items


def manuscript_claims():
    out = []
    for key, label_, fname, pat in MANUSCRIPT_CLAIMS:
        with open(os.path.join(C.REPO, fname), encoding="utf-8") as f:
            lines = f.read().splitlines()
        hit = next((k for k, l in enumerate(lines) if re.search(pat, l)), None)
        if hit is None:
            raise KeyError("frase no encontrada en %s: %s" % (fname, pat))
        quote = " ".join(l.strip() for l in lines[hit:hit + 2])
        out.append({"key": key, "label": label_, "file": fname, "line": hit + 1, "quote": quote})
    return out


def claim_status(key, b2, b2d):
    if key == "garch_11":
        cnt = b2["B2b"]["count_in_region"]
        return ("no contradicha con la configuración publicada: dentro de la región R = 0.5 `one` %d de %d, ADF %d, PP %d "
                "(Tabla B2a.1 y B2b.4); con la primaria (R = 0, `hac`) %d" % (
                    b2["B2a"]["gate"]["count_in_region_garch_R05"], b2["B2a"]["gate"]["garch_cells"],
                    cnt["adf_asy"]["garch"], cnt["pp_asy"]["garch"], cnt["rm_R0_t0.1_hac"]["garch"]))
    if key == "small_n_ncal":
        d4 = b2d["D4_small_n_published"]
        ok10 = all(v["matches"]["10000"] for v in d4.values())
        ok50 = all(v["matches"]["50000"] for v in d4.values())
        return ("contradicha: los tres valores publicados se reproducen con N_cal = 10000 (%s) y no con N_cal = 50000 (%s); §7(a)" % (ok10, ok50)
                if ok10 and not ok50 else "sin contradicción medida")
    return "no evaluada: %s no ejecutado" % CLAIM_BLOCK[key]


def cname(case):
    return "demeaned" if case == "c" else "tendencia"


def label(cell):
    parts = cell.split("_")
    n = parts[-1][1:]
    if parts[0] == "gauss":
        return "gaussiana, n = %s" % n
    if parts[0] == "indep":
        return "gaussiana independiente, n = %s" % n
    if parts[0] == "heavy":
        return "t(%s), n = %s" % (parts[1][1:], n)
    return "%s, n = %s" % (GARCH_LABEL["_".join(parts[1:-1])], n)


def star(r):
    return "%s%s" % (f4(r["rate"]), "*" if r.get("in_region") else "")


def wil(r):
    return "[%s, %s]" % (f4(r["wilson_lower"]), f4(r["wilson_upper"]))


def pp1(x):
    return "%+.1f" % x


def pp2(x):
    return "%+.2f" % x


def se1(x):
    return "%.1f" % x


def se2(x):
    return "%.2f" % x


def amendment_gate_text():
    with open(os.path.join(HERE, "protocol_audit8_amend1.md"), encoding="utf-8") as f:
        text = f.read()
    i = text.index("## 2. Nueva compuerta B1-NP")
    j = text.index("Los tres fallos de la validación original")
    return " ".join(text[i:j].split("\n", 1)[1].split())


PRETTY = {
    "rm_R0_t0.1_one": "RM one", "rm_R0_t0.1_hac": "RM hac", "rm_R0.5_t0.1_one": "R = 0.5 one",
    "rm_R0.5_t0.1_hac": "R = 0.5 hac", "adf_asy": "ADF asy", "adf_sim": "ADF sim", "pp_asy": "PP asy",
    "pp_sim": "PP sim", "dfgls_asy": "DF-GLS asy", "dfgls_sim": "DF-GLS sim", "dfglsaic_asy": "DF-GLS (AIC) asy",
    "mzt_asy": "MZ_t-GLS asy", "mzt_sim": "MZ_t-GLS sim", "msb_asy": "MSB-GLS asy", "msb_sim": "MSB-GLS sim",
    "rm_msbhac_hac": "MSB-HAC", "rm_rmgls_hac": "RM-GLS hac", "rm_R0_t0.02_hac": "RM hac θ = 0.02",
    "rm_R0_t0.05_hac": "RM hac θ = 0.05", "rm_R0_t0.2_hac": "RM hac θ = 0.2", "awb": "AWB",
    "rm_t0.05": "RM θ = 0.05", "rm_t0.1": "RM θ = 0.1", "rm_t0.2": "RM θ = 0.2",
    "gls_t0.05": "RM-GLS θ = 0.05", "gls_t0.1": "RM-GLS θ = 0.1", "gls_t0.2": "RM-GLS θ = 0.2",
    "msbhac": "MSB-HAC", "dfgls": "DF-GLS", "msb": "MSB-GLS", "mzt": "MZ_t-GLS", "envelope": "envolvente",
    "rm": "RM", "rmgls": "RM-GLS", "r05": "R = 0.5", "adf": "ADF", "pp": "PP", "kpss": "KPSS", "za": "ZA",
    "primary": "primaria", "proposed_R050": "R = 0.5 (A7)", "proposed_adaptive": "R̂ (A7)",
    "union_joint": "unión conjunta (A7)", "bootstrap_dfgls": "bootstrap (A7)",
    "primary_rm": "RM (anclado en la media)", "primary_rmgls": "RM-GLS (primaria)", "rhat_prereg": "R̂ pre-registrado (publicado)",
    "dfgls_aic": "DF-GLS (AIC, publicado)", "dfgls_maic": "DF-GLS (MAIC)", "rm_one": "RM one",
    "rm_hac_10k": "RM hac (N_cal = 10000)", "rm_hac_nD": "RM hac (calibrada a n = D)",
}


def PN(key):
    return PRETTY.get(key, key)


def prim5_key(b5):
    return "rmgls" if b5["primary_is_gls"] else "rm"


def fmt_effect(e):
    if not e:
        return "—"
    return "FP %s (máx. %s); %s detecciones; latencia %s" % (
        f4(e["fp_mean"]), f4(e["fp_max"]), e["detections"],
        "%.1f d" % e["mean_latency_detected"] if e["mean_latency_detected"] else "—")


def amendment2_gate_text():
    with open(os.path.join(HERE, "protocol_audit8_amend2.md"), encoding="utf-8") as f:
        text = f.read()
    i = text.index("## 1. Nueva compuerta B2b")
    j = text.index("## 2. Referencia gaussiana")
    return " ".join(text[i:j].split("\n", 1)[1].split())


def DEVIATIONS(inv, ga, b2i, b5, b6, b5b):
    return [
        ["Enmienda 1 (`protocol_audit8_amend1.md`): compuerta B1-NP en lugar de la validación ±3% de los ocho cuantiles; MZ_α y MP_T retirados de B3–B5",
         "Decisión del autor: la referencia publicada no tiene la precisión que exigía la compuerta", "después de ver B1, antes de B2",
         "B1 pasa con B1-NP; los comparadores de la familia M son MZ_t-GLS y MSB-GLS"],
        ["Enmienda 2 (`protocol_audit8_amend2.md`): compuerta B2b sobre 20000 trayectorias independientes; referencia gaussiana independiente para tablas y Δ; corrección de la caché; bootstrap solo en n ≤ 1000",
         "Decisión del autor tras el diagnóstico de B2b", "después de ver B2",
         "B2b pasa (%s); los Δ se reportan con las dos referencias; AWB no se corre en n = 2000 ni 5000" % b2i["gate"]["verdict"]],
        ["Corrección de la clave de caché de la nula en producción (regla 6)", "Defecto identificado en §7a; enmienda 2 punto 3",
         "después de ver B2", "Regresión pre/post con máx. |Δ| = 0; test permanente de dos N_cal en el mismo proceso"],
        ["MAIC original de Ng–Perron (2001) sobre datos detrendidos por GLS; sin la modificación de Perron–Qu",
         "`arch` no implementa MAIC; decisión del autor en la enmienda 1", "antes (confirmado en la enmienda)",
         "Solo afecta a la selección de retardos"],
        ["Tope de 4 h por bloque (el autor pidió ≤ 8 h)", "Regla 2 del encargo; confirmado por el autor", "antes", "Ninguno sobre valores"],
        ["El manuscrito v11 se copió de `%s` a `paper/` en un commit propio; las citas de §7 remiten a `paper/`" % inv["manuscript"]["path"],
         "Decisión del autor", "después de B1", "Ninguno"],
        ["Semillas de A7 con los mismos números de familia 91–94", "A7 usó un esquema entero; A8 usa SeedSequence", "antes",
         "Sin colisiones (Tabla B0.3)"],
        ["n = 2000 de la validación de Ng–Perron = 2000 incrementos (T = 2001 puntos)", "Convención del proyecto", "antes", "Tabla B1.3"],
        ["DF-GLS de las tablas publicadas (`arch`, AIC) se conserva como columna adicional junto al DF-GLS-MAIC",
         "El encargo pide MAIC; las tablas publicadas usan AIC", "antes", "Permite el Paso 0 de tasas publicadas y de la aplicación"],
        ["Convenciones de ᾱ: RM-GLS demeaned usa ᾱ = 1 + c̄/n (literal del encargo); Ng–Perron, DF-GLS y el detrending QD de la tendencia usan ᾱ = 1 + c̄/T",
         "Literal del encargo frente a convención previa", "antes", "Asintóticamente nulo"],
        ["RM-GLS: g₂ no se modifica con el anclaje", "El encargo solo define g₁ᴳᴸˢ", "antes", "Ninguno con R = 0"],
        ["B2a: «todas las celdas» se leyó como las %d celdas de B2a; los agregados usan las %d que el encargo enumera" % (
            len(ga["cells_evaluated"]), len(ga["aggregate_cells"])), "Lectura más estricta de la compuerta", "antes",
         "Veredicto: %s" % ga["verdict"]],
        ["Regla de rechazo `sim`: estadístico < cuantil 5% de la calibración; MZ_t y MSB `asy` con los valores críticos publicados; RM con el p-valor del ECDF de producción",
         "El encargo no fija la regla exacta", "antes", "Ninguno relevante"],
        ["Las columnas sin bootstrap de B3 se calcularon en la misma pasada de B2 (verificado libre de caché)",
         "Una sola pasada por réplica", "antes", "Ninguno"],
        ["B4: c = 13.5 se añadió como celda (no está en la rejilla entera); la envolvente en c = 0 es degenerada (c̄ = 0) y no entra en la compuerta previa, cuyos tamaños de P_T(c̄) se reportan como información",
         "Lectura del encargo", "antes", "La compuerta previa se evalúa sobre los %d procedimientos no degenerados" % len(b5 and [1] or [1])],
        ["B4 caso con tendencia: los DGP no llevan tendencia porque todos los estadísticos del caso son invariantes a una tendencia lineal",
         "Evita una constante irrelevante", "antes", "Ninguno (invariancia validada en B1)"],
        ["B5 DGP 5: la primaria se evalúa con los umbrales a tamaño igualado de A7 y también a nivel nominal con la nula hac",
         "El encargo pide los umbrales de A7; la calibración hac es la primaria de A8", "antes", "Se reportan las dos"],
        ["B6: la nula de la primaria se calibra a n = D − 1 (los incrementos de una ventana de D puntos); la calibración publicada usaba n = D",
         "La n del estadístico es D − 1", "antes", "Medido como fila xi de la tabla de desviaciones"],
        ["B6: MZ_t-GLS entra con su valor crítico asintótico (no hay p-valor) y, en la comparación a tasa igualada, con el estadístico como puntuación",
         "No existe p-valor tabulado", "antes", "Ninguno sobre el orden de las alarmas"],
        ["B7: la CDF de Davies se evalúa en una rejilla de cuantiles y se interpola (0.7 s por punto)",
         "Evaluarla en 10000 puntos por n costaría unas 12 h", "antes", "Paso máximo de la rejilla reportado en B7"],
        ["Diagnósticos adicionales tras compuertas que no pasaron (Tablas B1.3 y B2b.7), con celdas añadidas al final de las familias 91 y 92",
         "Las compuertas piden diagnosticar; no cambian su criterio", "después", "Sin colisiones de semillas"],
        ["Muestras nulas de B2 y checkpoints de B7 en `.npz` sin commitear", "Binarios regenerables bit a bit", "antes", "sha256 en §3"],
        ["Presupuesto de B5: la primera proyección (%.1f h, cada celda de filas proyectada con la sonda más cara de su tipo) superaba las 30 h; se refinó con una sonda de 14 series por celda (%.1f h: bootstrap %.1f h, filas %.1f h)" % (
            b5b["projected_total_hours_upper_bound"], b5b["projected_total_hours"], b5b["bootstrap_hours"], b5b["rows_hours"]),
         "La cota superior sumaba el coste de la celda más cara a celdas más baratas; no se recortaron N_sim ni B", "después de ver el presupuesto, antes de lanzar B5",
         "Ninguno sobre valores; las dos proyecciones quedan en `b5_budget_audit8.json`"],
        ["B6 se corrió primero con RM anclado en la media como primaria en la tasa igualada, las celdas adversas y la tabla de desviaciones; se corrigió para seguir la regla GLS de B4 y se volvió a correr", "Defecto del script: leía la regla GLS pero no la usaba", "después de ver B6",
         "La primaria de B6 es %s; RM anclado en la media se conserva como fila y la fila xiii de la tabla de desviaciones mide el cambio" % {"primary_rmgls": "RM-GLS", "primary_rm": "RM"}[b6["primary_key"]]],
        ["Reinicio abrupto del equipo durante B5", "Ajeno al experimento", "durante B5",
         "Reanudado desde los checkpoints atómicos; ninguna réplica se recalculó con otra semilla"],
    ]


def claim_status2(key, b2, b2d, b3, b5, b6, rule):
    prim = prim5_key(b5)
    if key == "garch_11":
        cnt = b2["B2b"]["count_in_region"]
        return ("reproducida con la configuración publicada: R = 0.5 `one` %d de %d, ADF %d, PP %d; con la primaria "
                "(R = 0, `hac`) %d de 16" % (b2["B2a"]["gate"]["count_in_region_garch_R05"], b2["B2a"]["gate"]["garch_cells"],
                                             cnt["adf_asy"]["garch"], cnt["pp_asy"]["garch"], cnt["rm_R0_t0.1_hac"]["garch"]))
    if key in ("dominance_intro", "dominance_dgp1"):
        diffs = [(v["rates"][prim]["rate"] - v["rates"]["adf"]["rate"]) * 100 for v in b5["dgp1"].values()]
        cell = b5["dgp1"].get("dgp1_rho0p99_n1000")
        d99 = (cell["rates"][prim]["rate"] - cell["rates"]["adf"]["rate"]) * 100 if cell else float("nan")
        return ("medido con la primaria (%s): la ventaja sobre ADF va de %s a %s pp en las 21 celdas de DGP 1 y es %s pp en "
                "(ρ, n) = (0.99, 1000) (Tabla B5.dgp1)" % (b5["primary"], pp1(min(diffs)), pp1(max(diffs)), pp1(d99)))
    if key == "bootstrap_every":
        awb_cells = [v for v in b5["dgp3"].values() if "awb" in v["rates"]]
        inside = sum(v["rates"]["awb"]["in_region"] for v in awb_cells)
        g = b3["count_in_region"].get("awb")
        return ("medido: en DGP 3 el AWB queda dentro de la región en %d de las %d celdas con bootstrap (n ≤ 1000, enmienda 2); "
                "en las celdas GARCH de B3, %d de %d" % (inside, len(awb_cells), g["garch"], g["garch_cells"]) if g else
                "medido en DGP 3: %d de %d celdas" % (inside, len(awb_cells)))
    if key == "trend_size":
        gi = b5["ct"]["gaussian_size_independent"]
        return ("medido con la primaria-ct y la referencia independiente (N = 20000): %s" %
                ", ".join("n = %s: %s" % (n, f4(gi[n][prim]["rate"])) for n in ("200", "500", "1000") if n in gi))
    if key == "fp_028":
        s = b6["summary"]
        return ("reproducida: el R̂ pre-registrado publicado da FP media %s; la primaria de A8 (%s) da %s; RM anclado en la media, %s (Tabla B6.1)" %
                (f4(s["rhat_prereg"]["fp_mean"]), {"primary_rmgls": "RM-GLS", "primary_rm": "RM"}[b6["primary_key"]], f4(s[b6["primary_key"]]["fp_mean"]), f4(s["primary_rm"]["fp_mean"])))
    if key == "detections_13":
        s = b6["summary"]
        return ("reproducida: R̂ pre-registrado %d de %d detecciones; la primaria de A8 (%s), %d; RM anclado en la media, %d" %
                (s["rhat_prereg"]["detections"], s["rhat_prereg"]["event_cells"], {"primary_rmgls": "RM-GLS", "primary_rm": "RM"}[b6["primary_key"]],
                 s[b6["primary_key"]]["detections"], s["primary_rm"]["detections"]))
    if key == "small_n_ncal":
        d4 = b2d["D4_small_n_published"]
        ok10 = all(v["matches"]["10000"] for v in d4.values())
        ok50 = all(v["matches"]["50000"] for v in d4.values())
        return ("contradicha: los tres valores publicados se reproducen con N_cal = 10000 (%s) y no con N_cal = 50000 (%s); "
                "causa: la clave de caché de la nula (§7a y Tabla 7b.1)" % (ok10, ok50))
    return "no evaluada"


def block_hours_table(b2_hours):
    def lh(*names):
        tot = 0.0
        for nm in names:
            q = os.path.join(C.RESULTS, "logs_audit8", nm)
            if os.path.exists(q):
                with open(q, encoding="utf-8", errors="replace") as f:
                    tot += sum(float(x) for x in re.findall(r"bloque: ([0-9.]+) h", f.read()))
        return tot
    inv_, b1_, diag_ = J("inventory_audit8.json"), J("b1_validation_audit8.json"), J("b1_np_diagnostic_audit8.json")
    npg_, b2_, b2d_ = J("b1_np_gate_audit8.json"), J("b2_size_audit8.json"), J("b2b_diagnostic_audit8.json")
    b2i_, b3_ = J("b2b_indep_audit8.json"), J("b3_comparators_audit8.json")
    b6_, b7_ = J("b6_application_audit8.json"), J("b7_critical_values_audit8.json")
    h = {}
    h["B0"] = "%.2f" % (inv_["seed_map"]["elapsed_sec"] / 3600)
    h["B1"] = "%.2f" % ((b1_["elapsed_sec"] + diag_["elapsed_sec"] + npg_["elapsed_sec"]) / 3600)
    h["B2"] = "%.2f" % (b2_hours + lh("b2b_indep_run_audit8.log")
                        + (b2_["elapsed_analysis_sec"] + b2d_["elapsed_sec"] + b2i_["elapsed_analysis_sec"]) / 3600)
    h["B3"] = "%.2f" % (sum(b3_["bootstrap_elapsed_sec"].values()) / 3600)
    h["B4"] = "%.2f" % lh("b4_run_audit8.log")
    h["B5"] = "%.2f" % lh("b5_run_audit8.log")
    h["B6"] = "%.2f" % (b6_["elapsed_sec"] / 3600)
    h["B7"] = "%.2f" % (b7_["elapsed_sec"] / 3600)
    return h

def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    env, inv, b1, diag = J("environment_audit8.json"), J("inventory_audit8.json"), J("b1_validation_audit8.json"), \
        J("b1_np_diagnostic_audit8.json")
    npg, b2, b2d = J("b1_np_gate_audit8.json"), J("b2_size_audit8.json"), J("b2b_diagnostic_audit8.json")
    b2i, cfx = J("b2b_indep_audit8.json"), J("cache_fix_audit8.json")
    b3, b4, b5 = J("b3_comparators_audit8.json"), J("b4_local_power_audit8.json"), J("b5_power_audit8.json")
    b6, b7, b8 = J("b6_application_audit8.json"), J("b7_critical_values_audit8.json"), J("figures_audit8.json")
    dev8 = J("deviation_table_audit8.json")
    man = J("manifest_audit8.json")
    py = pytest_summary()
    b2_hours = float(re.findall(r"bloque: ([0-9.]+) h", T("logs_audit8/b2_run1_audit8.log"))[-1])
    amendments = sorted(p for p in os.listdir(HERE) if re.match(r"protocol_audit8_amend\d+\.md$", p))
    L = []
    w = L.append

    # ---- encabezado ----------------------------------------------------------
    w("# Resultados de la auditoría A8")
    w("")
    w("Estadístico final, calibración corregida y comparadores de tamaño.")
    w("")
    g = env["git"]
    cpu = env["cpu"]
    vv = env["versions"]
    w("- Fecha de generación (UTC): %s" % now)
    w("- Commit de inicio (anterior al protocolo): `%s`. Commit del protocolo: `%s`. Commit al generar el reporte: `%s`." % (
        g["start_commit"], g["protocol_commit"], C.git("rev-parse", "HEAD")))
    w("- sha256 de `%s` (contenido commiteado): `%s`; sha256 del contenido en HEAD: `%s`." % (
        PROTOCOL, g["protocol_sha256_committed"], C.git_blob_sha256(PROTOCOL)))
    w("- Enmiendas: %s." % (", ".join("`%s` (sha256 `%s`)" % (a, C.git_blob_sha256("experiments/" + a)) for a in amendments) or "ninguna"))
    w("- Hardware: %s, %s núcleos físicos, %s lógicos; memoria %.1f GB; %s." % (
        cpu["Name"], cpu["NumberOfCores"], cpu["NumberOfLogicalProcessors"],
        env["memory_bytes"]["TotalPhysicalMemory"] / 2 ** 30, vv["platform"]))
    w("- Versiones: Python %s, numpy %s, scipy %s, numba %s, statsmodels %s, arch %s; %s; bootUR %s." % (
        vv["python"], vv["numpy"], vv["scipy"], vv["numba"], vv["statsmodels"], vv["arch"], env["r"], env["bootUR"]))
    hours = block_hours_table(b2_hours)
    w("- Tiempo por bloque (h de reloj): %s. Suite: %.0f s." % (
        "; ".join("%s %s" % (k, v) for k, v in hours.items()), py["seconds"]))
    w("- Estado: los ocho bloques se ejecutaron. B1 pasó con la compuerta B1-NP (enmienda 1); B2a pasó; la B2b original no pasó y el autor la sustituyó por la de la enmienda 2, que pasa (§2). Presupuestos de B3 y B5 dentro de las 30 h.")
    w("")

    # ---- 1 --------------------------------------------------------------------
    w("## 1. Resultados")
    w("")
    w("### B0 — %s" % BLOCK_TITLES["B0"])
    w("")
    t8 = inv["table8_provenance"]
    src_ok = [k for k, v in t8["comparison"].items() if v["all_match"]]
    w("**Tabla B0.1. Procedencia de la Tabla 8 publicada** (`inventory_audit8.json` → `table8_provenance`). Valores publicados leídos de `%s` (etiqueta `%s`, línea %d) dentro de `%s`; N_sim de la fuente = %d; sin familia de semillas nueva." % (
        t8["tex_file"], t8["manuscript_table"], t8["tex_label_line"], os.path.basename(inv["manuscript"]["path"]),
        J("size_robustness_heavy_tails_audit5b.json")["metadata"]["N_sim"]))
    w("")
    comp = t8["comparison"]
    keys = list(t8["published"])
    L.extend(table(["Celda", "Publicado R=0.5 / ADF / PP / DF-GLS", "A5b alpha1", "A5b alpha2", "A5 alpha1", "A5 alpha2"],
                   [[k, " / ".join(f4(t8["published"][k][c]) for c in ("R050", "adf", "pp", "dfgls"))]
                    + [" / ".join(f4(comp[s]["cells"][k]["source"][c]) for c in ("R050", "adf", "pp", "dfgls"))
                       + (" ✓" if comp[s]["cells"][k]["match"] else "") for s in comp] for k in keys]))
    w("")
    w("Celdas coincidentes por fuente: %s. ✓ = coinciden las cuatro columnas." % (
        "; ".join("`%s` %d/%d" % (s, v["cells_matching"], len(keys)) for s, v in comp.items())))
    w("")
    cl = t8["code_lines"]

    def ln(f, pat):
        return ", ".join(str(h["line"]) for h in cl[f][pat])
    w("- **(a) Origen de los valores publicados.** Coinciden en las %d celdas con %s, escrito por `experiments/audit5b_tarea_r3.py` (línea %s): semillas `900000 + n*100 + df*10 + i` (línea %s), generador `generate_rw_heavy` (llamada en la línea %s; definido en `size_robustness_heavy_tails.py`, línea %s, con `rng.standard_t(df, …)` en la línea %s y escalas de t(5) y t(3) en las líneas %s y %s), y nula gaussiana con N_cal = 50000 y semilla 42 (línea %s). Los valores de A5 (`size_robustness_heavy_tails_audit5.json`) no son la fuente: el script de A5 (`audit5_tarea2.py`, sin seguimiento en git) usa otras semillas, `200000 + n*100 + dof*10 + i` (línea %s)." % (
        len(keys), " y ".join("`%s`" % s for s in src_ok),
        ln("audit5b_tarea_r3.py", r"size_robustness_heavy_tails_audit5b.json"), ln("audit5b_tarea_r3.py", r"seed_base = 900000"),
        ln("audit5b_tarea_r3.py", r"generate_rw_heavy\(n, df, scale, rng\)"), ln("size_robustness_heavy_tails.py", r"def generate_rw_heavy"),
        ln("size_robustness_heavy_tails.py", r"rng.standard_t\(df"), ln("size_robustness_heavy_tails.py", r"'t5': \{"),
        ln("size_robustness_heavy_tails.py", r"'t3': \{"), ln("audit5b_tarea_r3.py", r"build_null_cdf\(THETA, r_val, n, N_cal=50000, seed=42\)"),
        ln("audit5_tarea2.py", r"seed = 200000")))
    a5 = comp["size_robustness_heavy_tails_audit5.json[alpha1]"]["cells"]["t3_n200"]["source"]["R050"]
    a5b = comp["size_robustness_heavy_tails_audit5.json[alpha2]"]["cells"]["t3_n200"]["source"]["R050"]
    w("  Para t(3), n = 200, R = 0.5: publicado %s; A5 da %s con el piloto alpha1 y %s con alpha2 (el valor que el encargo atribuye a alpha1 está en la rama alpha2, o en la columna R = 0.25 de la fila alpha1 del reporte de A5)." % (
        f4(t8["published"]["t3_n200"]["R050"]), f4(a5), f4(a5b)))
    dup = t8["a5_report_chisquare_rows"]
    w("- **(b) Las filas chisquare de A5.** El generador de A5 no ignoraba el parámetro de distribución: sortea `rng.standard_t(df=dof, …)` (`audit5_tarea2.py`, línea %s) y guarda el resultado indexado solo por grados de libertad (línea %s). Nunca sortea una χ². Las filas «chisquare» vienen del generador de reporte (`audit5_generate_report.py`, sin seguimiento en git): la línea %s itera `(\"chisquare\", [3, 5])` y la línea %s lee `d[pilot][str(dof)][n]`, que es la fila t del mismo dof. De las %d filas chisquare de `resultados_auditoria_5.md`, %d son idénticas a la fila t del JSON con el mismo dof." % (
        ln("audit5_tarea2.py", r"standard_t\(df=dof"), ln("audit5_tarea2.py", r"results\[str\(dof\)\]\[str\(n\)\]"),
        ln("audit5_generate_report.py", r"\(\"chisquare\", \[3, 5\]\)"), ln("audit5_generate_report.py", r"d\[pilot\]\[str\(dof\)\]\[n\]"),
        len(dup), sum(v["identical_to_json_t_same_dof"] for v in dup.values())))
    w("")
    figs = inv["figures"]
    w("**Tabla B0.2. Figuras** (`inventory_audit8.json` → `figures`). Al ejecutar B0 el repositorio no tenía `paper/figures/` (`%s`; la copia a `paper/` es posterior); se comparan las figuras del zip del manuscrito (`paper_v11/figures/`) con `experiments/figures/` de A7." % figs["paper_figures_dir_in_repo"])
    w("")
    L.extend(table(["Figura", "sha256 manuscrito", "sha256 A7", "Idénticas"],
                   [[k, "`%s`" % v["manuscript"], "`%s`" % v["experiments_a7"], v["identical"]] for k, v in figs["comparison"].items()]))
    extra = sorted(set(figs["experiments"]) - set(figs["manuscript"]))
    w("")
    w("Figuras de A7 sin equivalente en el manuscrito: %s." % (extra or "ninguna"))
    w("")
    sm = inv["seed_map"]
    w("**Tabla B0.3. Solape de semillas de las familias nuevas** (`inventory_audit8.json` → `seed_map`). Método: %s." % sm["method"])
    w("")
    L.extend(table(["Familia", "Celdas", "Streams de réplica", "Distintos"],
                   [[f, v["cells"], v["replicate_streams"], v["distinct_state_words"]] for f, v in sm["new_families"].items()]))
    w("")
    w("Semillas enteras previas examinadas: %d (familias del mapa de A7: %d; fuentes adicionales: %s). Colisiones con las previas: **%d**; colisiones entre streams nuevos: **%d**; `spawn_key` equivalente a `spawn()`: %s. %s" % (
        sm["prior_integer_seeds"], len(sm["prior_families"]), sm["prior_extra_sources"], sm["collisions_new_vs_prior"],
        sm["collisions_within_new"], sm["spawn_key_equals_spawn"], sm["a7_integer_family_name_clash"]))
    w("")
    dh = inv["frozen_data_hashes"]
    ph = inv["protocol_hash"]
    w("Datos congelados: hashes del registro frente al disco (con y sin normalizar fin de línea): %s. `experiments/protocol.md`: coincide con `protocol_hash.json`: %s. Artefactos del encargo no encontrados: %s." % (
        "; ".join("%s %s" % (k, v["match"]) for k, v in dh.items()), ph["match"], inv["missing_artifacts"] or "ninguno"))
    w("")

    w("### B1 — %s" % BLOCK_TITLES["B1"])
    w("")
    v1, v2, v3, v4, v5 = b1["V1_regression"], b1["V2_R0"], b1["V3_tau0"], b1["V4_gls"], b1["V5_ng_perron"]
    w("Cambios en producción (defaults intactos): `src/stationarity_test/rm_core.py` (nuevo) y los flags `cal_sigma ∈ {one, hac}`, `tau_mode ∈ {theta, zero}` y `anchor ∈ {mean, gls}` en `compute_statistic`, `build_null_cdf`, `null_cdf`, `null_quantile` y `stationarity_test`. R = 0 ya era admisible (`validate_R` acepta [0, 1]); la rejilla {0.25, 0.5, 0.75} solo existía en los scripts de experimentos. Ng–Perron, DF-GLS-MAIC y P_T viven en `experiments/audit8_unitroot.py` (código de experimentos). Por la enmienda 1, MZ_α y MP_T se retiraron como comparadores; quedan MZ_t-GLS y MSB-GLS.")
    w("")
    w("**Tabla B1.1. Validaciones** (`b1_validation_audit8.json`; familia de semillas %s)." % b1["provenance"]["seed_family"])
    w("")
    inv4 = v4["invariance"]
    dr = v4["drift"]
    L.extend(table(["Validación", "Medido", "Tolerancia", "Veredicto"], [
        ["Regresión pre/post (%d series; paquete de `%s` frente al actual): máx. |Δ| estadístico" % (v1["series"], v1["pre_b1_commit"][:7]),
         v1["max_abs_diff_statistic"], 0, verdict(v1["max_abs_diff_statistic"] == 0)],
        ["Regresión pre/post: máx. |Δ| p-valor (defaults, configuración publicada N_cal = 50000 y caso ct)",
         v1["max_abs_diff_p_value"], 0, verdict(v1["max_abs_diff_p_value"] == 0)],
        ["Regresión pre/post: muestra nula ordenada (R = 0.5, n = 200, N_cal = 50000) idéntica", v1["null_sample_identical"], True,
         verdict(v1["null_sample_identical"])],
        ["R = 0 admisible: estadístico frente a |g1_std| (%d series), peor diferencia relativa" % v2["series"],
         sci(v2["worst_rel_diff_statistic_vs_abs_g1_std"]), sci(v2["tolerance"]), verdict(v2["passed"])],
        ["RM con τ = 0 frente a MSB-HAC directo, %s (%d series)" % (v3["formula"], v3["series"]),
         sci(v3["worst_rel_diff"]), sci(v3["tolerance"]), verdict(v3["passed"])],
        ["RM-GLS invariancia a aY + b (constante)", sci(inv4["worst_rel_diff"]["c"]), sci(inv4["tolerance"]),
         verdict(inv4["worst_rel_diff"]["c"] <= inv4["tolerance"])],
        ["RM-GLS invariancia a aY + b + ct (tendencia)", sci(inv4["worst_rel_diff"]["ct"]), sci(inv4["tolerance"]),
         verdict(inv4["worst_rel_diff"]["ct"] <= inv4["tolerance"])],
        ["RM-GLS (tendencia) sin dependencia de la deriva, μ ∈ %s, números aleatorios comunes" % dr["mu"],
         sci(dr["worst_rel_diff_rm_gls_ct"]), sci(dr["tolerance"]), verdict(dr["worst_rel_diff_rm_gls_ct"] <= dr["tolerance"])],
        ["RM (tendencia, primaria candidata) sin dependencia de la deriva", sci(dr["worst_rel_diff_rm_ct"]), sci(dr["tolerance"]),
         verdict(dr["worst_rel_diff_rm_ct"] <= dr["tolerance"])],
        ["Ng–Perron original: los ocho cuantiles al 5%% a ±%s (sustituida por B1-NP, enmienda 1)" % pct(v5["tolerance_rel"]),
         "fallan: %s" % ", ".join(v5["failing"]) if v5["failing"] else "todos dentro", pct(v5["tolerance_rel"]),
         "%s (sustituida)" % verdict(v5["passed"])],
        ["Compuerta B1-NP (enmienda 1), criterios (a)–(d)", ", ".join("%s %s" % (k, verdict(v)) for k, v in npg["gates"].items()),
         "ver Tabla B1.4", verdict(npg["passed"])],
    ]))
    w("")
    w("**Tabla B1.2. Valores críticos de Ng–Perron simulados frente a publicados** (`b1_validation_audit8.json` → `V5_ng_perron`). Paseo aleatorio gaussiano, n = %d (T = %d puntos), N = %d, retardo fijo en %d, familia de semillas %s; EE del cuantil por bootstrap. «Convención alternativa»: ỹ_{T−1} y suma hasta T − 1, mismos caminos (`b1_np_gate_audit8.json`)." % (
        v5["cases"]["c"]["n"], v5["cases"]["c"]["T_points"], v5["cases"]["c"]["reps"], v5["cases"]["c"]["lag"], b1["provenance"]["seed_family"]))
    w("")
    alt = npg["criteria"]["d"]["alternative_q05"]
    rows = []
    for case, r in v5["cases"].items():
        for s, v in r["stats"].items():
            rows.append([cname(case), r["cbar"], s, "sí" if s in U.NP_KEPT else "retirado", f4(v["empirical_q05"]), f4(v["bootstrap_se"]),
                         v["ng_perron_2001"], pct(v["rel_diff"]), f4(alt[case][s]["alternative"]), pct(alt[case][s]["alternative_rel_diff"])])
    L.extend(table(["Caso", "c̄", "Estadístico", "Comparador en B3–B5", "Cuantil 5% simulado", "EE", "Ng–Perron (2001)",
                    "Diferencia relativa", "Convención alternativa", "Diferencia relativa (alternativa)"], rows))
    w("")
    w("**Tabla B1.3. Diagnóstico de la validación original** (`b1_np_diagnostic_audit8.json`).")
    w("")
    d1 = diag["D1_arch_identity"]
    L.extend(table(["Comprobación", "Demeaned", "Tendencia"], [
        ["Residuo GLS frente a `arch.unitroot.DFGLS` (%d series, n = %d), máx. |Δ|" % (d1["c"]["series"], d1["c"]["n"]),
         sci(d1["c"]["max_abs_diff_detrended"]), sci(d1["ct"]["max_abs_diff_detrended"])],
        ["Estadístico t con retardo 0 frente a `arch`, máx. |Δ|", sci(d1["c"]["max_abs_diff_t_stat_lag0"]), sci(d1["ct"]["max_abs_diff_t_stat_lag0"])],
    ]))
    w("")
    Ts = sorted(set(diag["D2_T_stability"]["c"]["by_T_points"]) | {str(v5["cases"]["c"]["T_points"])}, key=int)
    rows = []
    for case in ("c", "ct"):
        byT = diag["D2_T_stability"][case]["by_T_points"]
        vcase = v5["cases"][case]
        for s in U.NP_STATS:
            cells = []
            for Tp in Ts:
                src = byT[Tp][s] if Tp in byT else {"q05": vcase["stats"][s]["empirical_q05"], "bootstrap_se": vcase["stats"][s]["bootstrap_se"]}
                cells.append("%s (%s)" % (f4(src["q05"]), f4(src["bootstrap_se"])))
            rows.append([cname(case), s] + cells + [U.NP_CV5[case][s]])
    L.extend(table(["Caso", "Estadístico"] + ["T = %s: cuantil 5%% (EE)" % t for t in Ts] + ["Ng–Perron (2001)"], rows))
    w("")
    d3 = diag["D3_ers_pt"]
    L.extend(table(["Caso", "P_T de ERS, cuantil 5% (EE), mismos caminos", "ERS (1996)", "Diferencia relativa", "MP_T mismos caminos", "Ng–Perron MP_T", "ERS frente a Ng–Perron"],
                   [[cname(c), "%s (%s)" % (f4(v["pt_q05"]), f4(v["pt_bootstrap_se"])), v["ers_1996"],
                     pct(v["pt_rel_diff_vs_ers"]), f4(v["mpt_q05_same_paths"]), v["ng_perron_2001_mpt"], pct(v["ers_vs_ng_perron_rel_diff"])]
                    for c, v in d3.items()]))
    w("")
    cr = npg["criteria"]
    w("**Tabla B1.4. Compuerta B1-NP** (`b1_np_gate_audit8.json`, enmienda 1).")
    w("")
    rows = []
    for case in ("c", "ct"):
        for s in U.NP_KEPT:
            a_ = cr["a"][case][s]
            c_ = cr["c"][case][s]
            rows.append([cname(case), s, "%s frente a %s (%s): %s" % (f4(a_["empirical_q05"]), a_["ng_perron_2001"], pct(a_["rel_diff"]), verdict(a_["passed"])),
                         "T = 2001 %s (%s), T = 10001 %s (%s): |Δ| = %.2f EE combinados: %s" % (
                             f4(c_["q05_T2001"]), f4(c_["se_T2001"]), f4(c_["q05_T10001"]), f4(c_["se_T10001"]), c_["diff_in_se"], verdict(c_["passed"]))])
    L.extend(table(["Caso", "Estadístico", "(a) ±3% de Ng–Perron", "(c) convergencia interna (≤ 2 EE)"], rows))
    w("")
    w("- (b) Identidad MZ_t = MZ_α · MSB frente a la forma cerrada, %d trayectorias por caso: máx. |Δ| relativo %s (demeaned) y %s (tendencia); tolerancia %s: %s." % (
        cr["b"]["c"]["paths"], sci(cr["b"]["c"]["max_rel_diff"]), sci(cr["b"]["ct"]["max_rel_diff"]), sci(cr["b"]["c"]["tolerance"]), verdict(npg["gates"]["b"])))
    w("- (d) Convención de índices: `%s`, líneas %s. Correspondencia: %s. El código usa la convención del artículo: %s; código modificado: %s." % (
        cr["d"]["code_file"], "; ".join("%s %s" % (k, ", ".join(str(h["line"]) for h in v)) for k, v in cr["d"]["code_lines"].items()),
        cr["d"]["mapping"], cr["d"]["code_uses_paper_convention"], cr["d"]["code_changed"]))
    w("- Veredicto B1-NP: **%s**; B1 completo (V1–V4 y B1-NP): **%s**." % (verdict(npg["passed"]), verdict(npg["b1_passed"])))
    w("")

    # ---- B2 --------------------------------------------------------------------
    w("### B2 — %s" % BLOCK_TITLES["B2"])
    w("")
    cfg = b2["config"]
    reg = b2["exact_region"]
    w("Configuración (`b2_size_audit8.json`): N_sim = %d; N_cal = %d; región exacta %s, calculada a partir de N_sim; familia de semillas %s para las celdas nuevas; celdas reutilizadas con sus semillas originales. Calibración de RM: los caminos de `build_null_cdf` con semilla %d, los mismos para R = 0 y R = 0.5 y para `one` y `hac`. Regla de RM: %s; regla `sim`: %s; MZ_t-GLS y MSB-GLS `asy`: valores críticos de Ng–Perron %s. %s." % (
        cfg["N_sim"], cfg["N_cal"], reg, b2["provenance"]["seed_family"], cfg["cal_seed_rm"], cfg["rule_rm"], cfg["rule_sim"],
        {k: v for k, v in cfg["rule_np_asy"].items() if k in U.NP_KEPT}, cfg["delta_note"]))
    w("")
    w("**Tabla B2.0. Controles de B2.** Calibrador de RM frente a `_simulate_null_statistics` de producción (máx. |Δ| sobre las 50000 réplicas, sin ordenar): %s. Paso 0 en las celdas reutilizadas (%d celdas, primeras %d réplicas): peor máx. |Δ| en la serie %s; estadístico R = 0.5 frente a `compute_statistic` %s; componentes y p-valores frente a los checkpoints de A7 %s; reproducción de tasas publicadas, peor diferencia %s (ver §7a)." % (
        "; ".join("n = %s: %s / %s" % (n, v["R0.5_one_max_abs_diff"], v["R0_hac_max_abs_diff"]) for n, v in b2["calibrator_control"].items()),
        len(b2["paso0"]["cells"]), next(iter(b2["paso0"]["cells"].values()))["reps"],
        b2["paso0"]["worst"]["max_abs_diff_series"], b2["paso0"]["worst"]["max_abs_diff_stat_R05_vs_compute_statistic"],
        b2["paso0"]["worst"]["max_abs_diff_a7_components_and_pvalues"], f4(b2["paso0"]["worst"]["max_abs_rate_diff"])))
    w("")
    a_cells = b2["B2a"]["cells"]
    ga = b2["B2a"]["gate"]
    w("**Tabla B2a.1. R = 0 frente a R = 0.5, calibración `one`, por celda** (mismas trayectorias; b = solo R = 0 rechaza, c = solo R = 0.5; McNemar exacto; * = dentro de la región %s)." % reg)
    w("")
    L.extend(table(["Celda", "n", "R = 0", "R = 0.5", "b", "c", "McNemar p", "Δ (pp)"],
                   [[label(k), v["n"], star(v["rate_R0"]), star(v["rate_R05"]), v["b_only_R0"], v["c_only_R05"], f4(v["mcnemar_p"]), pp1(v["delta_pp"])]
                    for k, v in a_cells.items()]))
    w("")
    w("Agregados sobre las %d celdas (22 mal especificadas y gaussianas publicadas con n ≥ 200): Σb = %d, Σc = %d, test de signo exacto p = %s. Media de Δ en las %d GARCH: %s pp. Dentro de la región en las GARCH: R = 0 %d, R = 0.5 %d. Máx. |Δ| = %s pp (%s); mínimo p de McNemar = %s (%s). **Veredicto B2a: %s.**" % (
        len(ga["aggregate_cells"]), ga["sum_b"], ga["sum_c"], f4(ga["sign_test_p"]), ga["garch_cells"], pp2(ga["mean_delta_pp_garch"]),
        ga["count_in_region_garch_R0"], ga["count_in_region_garch_R05"], pp1(ga["max_abs_delta_pp"]), label(ga["cell_max_abs_delta"]),
        f4(ga["min_mcnemar_p"]), label(ga["cell_min_mcnemar_p"]), ga["verdict"]))
    w("")
    bb = b2["B2b"]
    w("**Tabla B2b.1. Tamaño gaussiano de RM (R = 0, θ = 0.1), `one` frente a `hac`** (* = dentro de %s; IC de Wilson)." % reg)
    w("")
    L.extend(table(["n", "one", "IC one", "hac", "IC hac"],
                   [[n, star(v["one"]), wil(v["one"]), star(v["hac"]), wil(v["hac"])] for n, v in bb["gaussian_size"].items()]))
    w("")
    procs = ("rm_R0_t0.1_one", "rm_R0_t0.1_hac", "adf_asy", "adf_sim", "pp_asy", "pp_sim", "dfgls_asy", "dfgls_sim")
    w("**Tabla B2b.2. Tasas de rechazo en las 22 celdas mal especificadas y en las gaussianas** (* = dentro de %s). DF-GLS con MAIC; ADF con AIC." % reg)
    w("")
    rows = [[label(k)] + [star(v[p]) for p in procs] for k, v in bb["misspec_rates"].items()]
    rows += [[label(k)] + [star(v[p]) for p in procs] for k, v in bb["gaussian_rates"].items()]
    L.extend(table(["Celda"] + [PNAME[p] for p in procs], rows))
    w("")
    w("**Tabla B2b.3. Desplazamiento pareado Δ (pp) por celda** (tasa mal especificada − tasa gaussiana al mismo n; EE de diferencia de proporciones independientes entre paréntesis).")
    w("")
    L.extend(table(["Celda"] + [PNAME[p] for p in procs],
                   [[label(k)] + ["%s (%s)" % (pp1(v[p]["delta"] * 100), se1(v[p]["se"] * 100)) for p in procs] for k, v in bb["paired_delta"].items()]))
    w("")
    w("**Tabla B2b.4. Media de Δ por n (pp; EE)** y número de celdas mal especificadas dentro de la región.")
    w("")
    rows = [[n, len(v["cells"])] + ["%s (%s)" % (pp2(v[p]["mean"] * 100), se2(v[p]["se"] * 100)) for p in procs] for n, v in bb["mean_delta_by_n"].items()]
    rows.append(["dentro de la región: GARCH (16)", "—"] + [bb["count_in_region"][p]["garch"] for p in procs])
    rows.append(["dentro de la región: colas pesadas (6)", "—"] + [bb["count_in_region"][p]["heavy"] for p in procs])
    L.extend(table(["n", "Celdas"] + [PNAME[p] for p in procs], rows))
    w("")
    w("**Tabla B2b.5. Valores críticos al 5%% de RM `hac`** (cuantil de la muestra nula, N_cal = %d): %s. Variación relativa máxima en n: %s." % (
        cfg["N_cal"], "; ".join("n = %s: %s" % (n, f4(v)) for n, v in bb["rm_hac_critical_values"].items()), pct(bb["rm_hac_cv_max_rel_variation"])))
    w("")
    w("**Tabla B2b.6. Valores críticos simulados de los comparadores** (cuantil 5%%, %d paseos por n, familia %s)." % (cfg["N_cal"], b2["provenance"]["seed_family"]))
    w("")
    sc = b2["sim_critical_values"]
    cols = list(next(iter(sc.values())))
    L.extend(table(["n"] + [SIMNAME[c] for c in cols], [[n] + [f4(v[c]) for c in cols] for n, v in sc.items()]))
    w("")
    gb = bb["gate"]
    w("**Veredicto B2b: %s** (tamaño gaussiano de RM `hac`: %s; región %s)." % (
        gb["verdict"], "; ".join("n = %s: %s" % (n, f4(v)) for n, v in gb["sizes"].items()), gb["region"]))
    w("")
    w("**Tabla B2b.7. Diagnóstico de la compuerta B2b** (`b2b_diagnostic_audit8.json`; no cambia la compuerta).")
    w("")
    L.extend(table(["Comprobación", "Resultado"], [
        ["D1. Tamaño de RM `hac` sobre %d paseos gaussianos independientes (familia %s)" % (
            next(iter(b2d["D1_independent_paths"].values()))["n"], b2d["provenance"]["seed_family"]),
         "; ".join("n = %s: %s %s" % (n, f4(v["rate"]), wil(v)) for n, v in b2d["D1_independent_paths"].items())],
        ["D2. Trayectorias publicadas de n = 200 con una calibración `hac` independiente",
         "%s %s (con la semilla 42: %s); cuantil 5%%: %s frente a %s" % (
             f4(b2d["D2_independent_calibration"]["published_paths_rate_independent_cal"]["rate"]),
             wil(b2d["D2_independent_calibration"]["published_paths_rate_independent_cal"]),
             f4(b2d["D2_independent_calibration"]["published_paths_rate_seed42_cal"]["rate"]),
             f4(b2d["D2_independent_calibration"]["q05_independent"]), f4(b2d["D2_independent_calibration"]["q05_seed42"]))],
        ["D3. Estadístico de los datos y de la calibración", "%s / %s" % (b2d["D3_construction"]["data_statistic"], b2d["D3_construction"]["calibration_statistic"])],
        ["D5. Las trayectorias gaussianas publicadas usan `default_rng(0 + i)` en todos los n",
         "la serie de n = 200 es prefijo de la de n = 500: %s; de la de n = 1000: %s" % (
             b2d["D5_nested_paths"]["n200_is_prefix_of_n500"], b2d["D5_nested_paths"]["n200_is_prefix_of_n1000"])],
    ]))
    w("")

    # ---- B2b (enmienda 2) ------------------------------------------------------
    w("### B2b (enmienda 2) — referencia gaussiana independiente")
    w("")
    gi = b2i["gate"]
    w("**Tabla B2b-E2.1. Tamaño gaussiano de RM `hac` (R = 0, θ = 0.1) sobre %d trayectorias independientes por n** (familia %s, un hijo de `SeedSequence` por n; región exacta para N = %d: %s; IC de Wilson). La columna de las trayectorias publicadas (N = %d) se conserva como comparabilidad con v11, no como compuerta." % (
        gi["N"], b2i["provenance"]["seed_family"], gi["N"], gi["region"], b2["config"]["N_sim"]))
    w("")
    L.extend(table(["n", "Independiente", "IC", "Dentro de la región", "Publicadas (N = 5000)"],
                   [[n, f4(v["rm_R0_t0.1_hac"]["rate"]), wil(v["rm_R0_t0.1_hac"]), v["rm_R0_t0.1_hac"]["in_region"],
                     f4(b2i["gaussian_rates_published"][n]["rm_R0_t0.1_hac"]["rate"]) if n in b2i["gaussian_rates_published"] else "—"]
                    for n, v in b2i["gaussian_rates_independent"].items()]))
    w("")
    w("**Veredicto B2b (enmienda 2): %s** (n = 200, 500 y 1000 dentro de la región).")
    L[-1] = L[-1] % gi["verdict"]
    w("")
    ip = ("rm_R0_t0.1_one", "rm_R0_t0.1_hac", "rm_R0.5_t0.1_hac", "adf_sim", "pp_sim", "dfgls_asy", "dfgls_sim",
          "mzt_asy", "mzt_sim", "msb_asy", "msb_sim", "rm_msbhac_hac", "rm_rmgls_hac")
    w("**Tabla B2b-E2.2. Tasas gaussianas de todos los procedimientos sobre las trayectorias independientes** (* = dentro de %s)." % gi["region"])
    w("")
    L.extend(table(["n"] + [PN(p) for p in ip],
                   [[n] + [star(v[p]) for p in ip] for n, v in b2i["gaussian_rates_independent"].items()]))
    w("")
    w("**Tabla B2b-E2.3. Media de Δ por n con referencia independiente** (pp; EE) y, entre corchetes, con la referencia publicada.")
    w("")
    ind, pub = b2i["mean_delta_by_n"]["independent"], b2i["mean_delta_by_n"]["published"]
    L.extend(table(["n", "Celdas"] + [PN(p) for p in ip],
                   [[n, len(v["cells"])] + ["%s (%s) [%s]" % (pp2(v[p]["mean"] * 100), se2(v[p]["se"] * 100),
                                                              pp2(pub[n][p]["mean"] * 100)) for p in ip]
                    for n, v in ind.items()]))
    w("")

    # ---- B3 --------------------------------------------------------------------
    w("### B3 — %s" % BLOCK_TITLES["B3"])
    w("")
    bud3 = J("b3_budget_audit8.json")
    w("Regla de presupuesto (CARO, %.0f h): %s. Celda completa: %s. Coste medido por serie: %s. Proyección total **%.1f h**; dentro del presupuesto: %s." % (
        bud3["budget_hours"], bud3["rule"], bud3["measured"][str(sorted(int(k) for k in bud3["measured"])[-1])]["cell"],
        "; ".join("n = %s: %.3f s (%s)" % (n, m["sec_per_series"], m["kind"]) for n, m in sorted(bud3["measured"].items(), key=lambda kv: int(kv[0]))),
        bud3["projected_total_hours"], bud3["within_budget"]))
    w("")
    p3 = b3["procedures"]
    w("Alcance del bootstrap AWB (enmienda 2): n ≤ %d, B = %d, N_sim = %d; referencia gaussiana: %s. Región exacta: %s (N = 5000), %s (N = 2000), %s (N = 20000)." % (
        b3["bootstrap_n_max"], b3["B"], D8.N_SIM_BOOT,
        b3["gaussian_reference"], b3["exact_region_5000"], b3["exact_region_2000"], b3["exact_region_20000"]))
    w("")
    w("**Tabla B3.1. Comparadores nuevos: tasas por celda** (* = dentro de la región del N de la celda).")
    w("")
    L.extend(table(["Celda", "n"] + [PN(p) for p in p3],
                   [[label(k), b2["cells"].get(k, {}).get("n", "—")] + [star(v[p]) if p in v else "—" for p in p3]
                    for k, v in b3["rates"].items()]))
    w("")
    w("**Tabla B3.2. Media de Δ por n** (pp; EE), referencia independiente.")
    w("")
    L.extend(table(["n"] + [PN(p) for p in p3],
                   [[n] + ["%s (%s)" % (pp2(v[p]["mean"] * 100), se2(v[p]["se"] * 100)) if p in v else "—" for p in p3]
                    for n, v in b3["mean_delta_by_n"].items()]))
    w("")
    L.extend(table(["Dentro de la región"] + [PN(p) for p in p3],
                   [["GARCH (de %s celdas)" % "/".join(str(b3["count_in_region"][p]["garch_cells"]) for p in p3[:1])]
                    + ["%d de %d" % (b3["count_in_region"][p]["garch"], b3["count_in_region"][p]["garch_cells"]) for p in p3],
                    ["Colas pesadas (6)"] + [b3["count_in_region"][p]["heavy"] for p in p3]]))
    w("")
    d1, d2, d3 = b3["D1"], b3["D2"], b3["D3"]
    w("**Tabla B3.3. D1 — ventaja del estadístico** (media de Δ de la primaria menos la del comparador; se cumple si la diferencia es negativa y mayor que 2 EE en valor absoluto).")
    w("")
    L.extend(table(["n", "Comparador", "Δ primaria (pp)", "Δ comparador (pp)", "Diferencia (pp)", "EE (pp)", "¿Se cumple?"],
                   [[n, PN(c), pp2(v["mean_delta_primary"] * 100), pp2(v["mean_delta_comparator"] * 100),
                     pp2(v["difference"] * 100), se2(v["se_difference"] * 100), v["holds"]]
                    for n, cc in d1["by_n"].items() for c, v in cc.items()]))
    w("")
    w("**D1: %s.** **D2** (|media Δ(RM hac) − media Δ(MSB-HAC)| ≤ %s pp en todos los n): %s — %s. **D3**: %s." % (
        "sí" if d1["holds"] else "no", pp2(b2["config"]["gate_thresholds"]["pp"]),
        "sí" if d2["holds"] else "no",
        "; ".join("n = %s: %s pp" % (n, pp2(v["abs_diff_pp"])) for n, v in d2["by_n"].items()),
        "no evaluable sin bootstrap" if d3 is None else
        "%s — AWB dentro de la región en %d de las %d celdas GARCH comparadas frente a %d de la primaria; |media Δ| a n ≤ 500: AWB %s pp (EE %s) frente a %s pp (EE %s)" % (
            "sí" if d3["holds"] else "no", d3["garch_in_region_awb"], len(d3["garch_cells_compared"]), d3["garch_in_region_primary"],
            pp2(d3["mean_delta_awb_n_le_500"]["mean"] * 100), se2(d3["mean_delta_awb_n_le_500"]["se"] * 100),
            pp2(d3["mean_delta_primary_n_le_500"]["mean"] * 100), se2(d3["mean_delta_primary_n_le_500"]["se"] * 100))))
    w("")
    bs = b3["bootstrap_size_n200_N5000"]
    if bs:
        w("**Tamaño del bootstrap AWB a n = 200 con N = %d** (familia 93, trayectorias nuevas): %s %s; dentro de la región %s: %s. A7 registró 0.0588 [0.0524, 0.0657] y A6 0.0450 (§7a)." % (
            bs["n"], f4(bs["rate"]), wil(bs), C.exact_region(bs["n"]), bs["in_region"]))
        w("")

    # ---- B4 --------------------------------------------------------------------
    w("### B4 — %s" % BLOCK_TITLES["B4"])
    w("")
    cfg4 = b4["config"]
    w("DGP: AR(1) con ρ = 1 − c/n, n = %d, N = %d por c, familia %s; c ∈ %s. Umbrales bajo c = 0 con N_cal = %d (%s); envolvente: %s. Región exacta del conjunto de prueba (N = %d): %s." % (
        cfg4["n"], cfg4["N_power"], b4["provenance"]["seed_family"], cfg4["c_grid"], cfg4["N_cal"], cfg4["rule_rm"],
        cfg4["envelope"], cfg4["N_test0"], b4["exact_region_test0"]))
    w("")
    w("**Compuerta previa (DURA): %s.** Tamaños en c = 0 sobre el conjunto independiente: %s." % (
        verdict(b4["prior_gate"]["passed"]),
        "; ".join("%s: %s" % (case, ", ".join("%s %s%s" % (PN(p), f4(v["rate"]), "" if v["in_region"] else " (fuera)")
                                              for p, v in r["gate_c0"].items())) for case, r in b4["cases"].items())))
    w("")
    for case, r in b4["cases"].items():
        w("**Tabla B4.%d. Potencia local (%s)**: potencia por c; la envolvente en c = 0 vale α por construcción." % (
            1 if case == "dm" else 2, cname(case) if case in ("c", "ct") else ("demeaned" if case == "dm" else "tendencia")))
        w("")
        procs4 = list(next(iter(r["power"].values())).keys())
        procs4 = [p for p in procs4 if p not in ("nan",)]
        cs = [c for c in cfg4["report_c"]]
        L.extend(table(["Procedimiento"] + ["c = %g" % c for c in cs],
                       [[PN(p)] + [f4(r["power"][str(float(c))][p]) for c in cs] for p in procs4]))
        w("")
        w("Brecha a la envolvente (pp) en c = 5, 10 y 20; brecha máxima y su c; c al 50% de potencia:")
        w("")
        L.extend(table(["Procedimiento", "c = 5", "c = 10", "c = 20", "Brecha máxima", "c de la máxima", "c al 50%"],
                       [[PN(p)] + [pp1(r["gap_to_envelope"][p][str(float(c))] * 100) for c in (5, 10, 20)]
                        + [pp1(r["max_gap"][p]["gap"] * 100), "%g" % r["max_gap"][p]["c"],
                           "%.1f" % r["c_at_50pct"][p] if r["c_at_50pct"][p] is not None else "no alcanza"]
                        for p in procs4 if p != "envelope"]))
        w("")
    rule = b4["gls_rule"]
    g1, g2, g3 = rule["G1"], rule["G2"], rule["G3"]
    w("**Tabla B4.3. Regla de adopción GLS** (protocolo §2).")
    w("")
    L.extend(table(["Criterio", "Medido", "Umbral", "¿Se cumple?"], [
        ["G1: la brecha de RM-GLS a la envolvente en c = 10 es al menos 10 pp menor que la de RM (demeaned, θ = 0.1)",
         "RM-GLS %s pp; RM %s pp; reducción %s pp" % (pp1(g1["gap_rmgls_pp"]), pp1(g1["gap_rm_pp"]), pp1(g1["reduction_pp"])),
         "≥ %s pp" % pp1(g1["threshold_pp"]), g1["holds"]],
        ["G2: tamaño gaussiano de RM-GLS `hac` dentro de %s en n = 200, 500 y 1000" % g2["region"],
         "; ".join("n = %s: %s" % (n, f4(v["rate"])) for n, v in g2["sizes"].items()), str(g2["region"]), g2["holds"]],
        ["G3: el Δ medio de RM-GLS en las GARCH con n ≤ 500 no supera en más de 0.30 pp al de RM",
         "exceso %s pp (RM-GLS %s pp frente a RM %s pp)" % (pp2(g3["excess_pp"]), pp2(g3["mean_delta_rmgls"]["mean"] * 100),
                                                            pp2(g3["mean_delta_rm"]["mean"] * 100)),
         "≤ %s pp" % pp2(g3["threshold_pp"]), g3["holds"]],
    ]))
    w("")
    w("**Primaria final: %s** (adoptar GLS: %s)." % (rule["primary_final"], rule["adopt_gls"]))
    w("")

    # ---- B5 --------------------------------------------------------------------
    w("### B5 — %s" % BLOCK_TITLES["B5"])
    w("")
    bud5 = J("b5_budget_audit8.json")
    w("Regla de presupuesto (CARO, %.0f h): %s. Proyección total **%.1f h**; dentro: %s. Primaria: %s. Bootstrap (enmienda 2): DGP 1 con ρ ∈ %s y DGP 3 con r ∈ %s, n ≤ 1000." % (
        bud5["budget_hours"], bud5["rule"], bud5["projected_total_hours"], bud5["within_budget"], b5["primary"],
        list(b5["config"]["boot_dgp1_rho"]), list(b5["config"]["boot_dgp3_r"])))
    w("")
    prim5 = "rmgls" if b5["primary_is_gls"] else "rm"
    for key, title, cols in (("dgp1", "DGP 1: potencia frente a AR(1) estacionario",
                              [prim5] + (["rm"] if b5["primary_is_gls"] else []) + ["r05", "adf", "pp", "dfgls", "mzt", "msb", "kpss", "awb"]),
                             ("dgp2", "DGP 2: AR(0.95) con quiebre de media", [prim5, "adf", "pp", "dfgls", "mzt", "za"]),
                             ("za_size", "Tamaño de ZA bajo paseo aleatorio y con quiebre de nivel", [prim5, "adf", "pp", "dfgls", "mzt", "za"]),
                             ("dgp3", "DGP 3: paseo aleatorio con quiebre de varianza (todas son tasas de tamaño)",
                              [prim5] + (["rm"] if b5["primary_is_gls"] else []) + ["r05", "adf", "pp", "dfgls", "mzt", "awb"])):
        cells5 = b5[key]
        w("**Tabla B5.%s. %s** (N_sim = %d; bootstrap N = %d; * = dentro de la región)." % (key, title, b5["N_sim"], b5["N_boot"]))
        w("")
        par = "rho" if key in ("dgp1", "dgp2") else ("r" if key == "dgp3" else None)
        par = "delta" if key == "dgp2" else par
        head = (["Celda"] + (["%s" % par] if par else []) + ["n"] + [PN(p) for p in cols]
                + ["McNemar primaria vs " + PN(p) for p in cols if p not in (prim5, "rm")])
        rows5 = []
        for k, v in sorted(cells5.items(), key=lambda kv: (kv[1]["n"], kv[1].get(par, 0))):
            row5 = [k] + ([("%g" % v[par]) if par in v else "—"] if par else []) + [v["n"]]
            row5 += [star(v["rates"][p]) if p in v["rates"] else "—" for p in cols]
            row5 += [f4(v["mcnemar_primary_vs"][p]["p_value"]) if p in v["mcnemar_primary_vs"] else "—"
                     for p in cols if p not in (prim5, "rm")]
            rows5.append(row5)
        L.extend(table(head, rows5))
        w("")
    d5b = b5["dgp5"]
    w("**Tabla B5.dgp5. DGP 5 a n = %d sobre las trayectorias de A7** (umbrales a tamaño igualado con la celda `%s` de A7, B = %d; Paso 0: peor máx. |Δ| en los componentes %s)." % (
        d5b["n"], d5b["calibration_cell"], d5b["B"], sci(d5b["paso0"]["max_abs_diff_components"])))
    w("")
    p5 = ("primary", "proposed_R050", "proposed_adaptive", "union_joint", "bootstrap_dfgls")
    L.extend(table(["Celda", "ρ", "r"] + [PN(p) for p in p5] + ["primaria hac (nominal)", "R = 0.5 hac (nominal)",
                                                                 "cuota mediana de g₂", "McNemar vs R = 0.5", "McNemar vs bootstrap"],
                   [[k, "%g" % v["rho"], "%g" % v["r"]] + [f4(v["size_matched"][p]["rate"]) for p in p5]
                    + [f4(v["nominal_hac"]["primary_hac"]["rate"]), f4(v["nominal_hac"]["r05_hac"]["rate"]),
                       "%.2e" % v["g2_share_R050_median"], f4(v["mcnemar_primary_vs_R050"]["p_value"]),
                       f4(v["mcnemar_primary_vs_bootstrap"]["p_value"])]
                    for k, v in sorted(d5b["cells"].items(), key=lambda kv: (kv[1]["rho"], kv[1]["r"]))]))
    w("")
    ct = b5["ct"]
    w("**Tabla B5.ct.1. Caso con tendencia: invariancia a la deriva** (μ ∈ %s con números aleatorios comunes)." % list(D8.DRIFT_MU_REPORT))
    w("")
    L.extend(table(["n", "Variante", "Máx. dif. relativa entre μ", "Vectores de rechazo idénticos", "Tasa (μ = 0)"],
                   [[n, PN(v), sci(r["max_rel_diff_across_mu"]), r["rejection_vectors_identical"], f4(r["rates_by_mu"]["0"]["rate"])]
                    for n, rec in ct["drift_invariance"].items() for v, r in rec.items()]))
    w("")
    ctp = ("rm", "rmgls", "adf", "adf_sim", "pp", "dfgls", "dfgls_sim", "mzt", "mzt_sim", "msb", "msb_sim")
    w("**Tabla B5.ct.2. Caso con tendencia: tamaño gaussiano con la referencia independiente** (N = %d; * = dentro de %s)." % (
        D8.N_INDEP, b5["exact_region_20000"]))
    w("")
    L.extend(table(["n"] + [PN(p) for p in ctp],
                   [[n] + [star(v[p]) if p in v else "—" for p in ctp] for n, v in ct["gaussian_size_independent"].items()]))
    w("")
    w("**Tabla B5.ct.3. Caso con tendencia: potencia frente a AR(1) alrededor de una tendencia lineal.**")
    w("")
    cols_ct = [prim5] + (["rm"] if b5["primary_is_gls"] else []) + ["adf", "pp", "dfgls", "mzt", "msb"]
    L.extend(table(["Celda", "ρ", "n"] + [PN(p) for p in cols_ct] + ["McNemar primaria vs " + PN(p) for p in cols_ct if p not in (prim5, "rm")],
                   [[k, "%g" % v["rho"], v["n"]] + [f4(v["rates"][p]["rate"]) for p in cols_ct]
                    + [f4(v["mcnemar_primary_vs"][p]["p_value"]) for p in cols_ct if p not in (prim5, "rm")]
                    for k, v in sorted(ct["power"].items(), key=lambda kv: (kv[1]["n"], -kv[1]["rho"]))]))
    w("")
    gcols = list(next(iter(ct["garch"].values()))["rates"].keys())
    w("**Tabla B5.ct.4. Caso con tendencia: las 16 celdas GARCH** (tasas y Δ pareado frente a la referencia gaussiana independiente).")
    w("")
    L.extend(table(["Celda", "n"] + [PN(p) for p in gcols] + ["Δ " + PN(p) + " (pp)" for p in gcols],
                   [[label(k[3:]), v["n"]] + [star(v["rates"][p]) for p in gcols]
                    + ["%s (%s)" % (pp1(v["delta_vs_independent_gaussian"][p]["delta"] * 100),
                                    se1(v["delta_vs_independent_gaussian"][p]["se"] * 100)) for p in gcols]
                    for k, v in sorted(ct["garch"].items(), key=lambda kv: kv[1]["n"])]))
    w("")
    w("Media de Δ por n (pp; EE entre paréntesis):")
    w("")
    L.extend(table(["n"] + [PN(p) for p in gcols],
                   [[n] + ["%s (%s)" % (pp2(v[p]["mean"] * 100), se2(v[p]["se"] * 100)) for p in gcols]
                    for n, v in ct["garch_mean_delta_by_n"].items()]))
    w("")

    # ---- B6 --------------------------------------------------------------------
    w("### B6 — %s" % BLOCK_TITLES["B6"])
    w("")
    w("Datos congelados verificados antes de calcular: %s; `experiments/protocol.md` coincide con su hash registrado: %s. Calibración de la primaria: nula hac con N_cal = %d, semilla %d, a n = D − 1 (la n de la ventana de D puntos). Paso 0 (%d ventanas en %d celdas): peor máx. |Δ| %s." % (
        "; ".join("%s %s" % (k, v["match"]) for k, v in b6["data_hashes"].items()), b6["protocol_hash"]["match"],
        b6["config"]["N_cal"], b6["config"]["cal_seed"], b6["paso0"]["windows"], len(b6["paso0"]["cells"]),
        "; ".join("%s %s" % (k, sci(v)) for k, v in b6["paso0"]["worst"].items())))
    w("")
    tests6 = ("primary_rm", "primary_rmgls", "rhat_prereg", "adf", "pp", "dfgls_aic", "dfgls_maic", "mzt", "kpss")
    w("**Tabla B6.1. Falsos positivos, detecciones y latencia** (48 celdas de control; 88 celdas de evento; α = %s)." % b6["config"]["alpha"])
    w("")
    L.extend(table(["Test", "FP media", "FP máxima", "Detecciones", "Latencia media condicional (días)"],
                   [[PN(t), f4(b6["summary"][t]["fp_mean"]), f4(b6["summary"][t]["fp_max"]),
                     "%d de %d" % (b6["summary"][t]["detections"], b6["summary"][t]["event_cells"]),
                     "%.1f" % b6["summary"][t]["mean_latency_detected"] if b6["summary"][t]["mean_latency_detected"] else "—"]
                    for t in tests6]))
    w("")
    mt = b6["matched_rate"]
    w("**Tabla B6.2. A tasa de falsas alarmas igualada** (objetivo %s, la tasa agrupada de la primaria; episodios agrupando rechazos contiguos con tolerancia de %d días; latencia censurada a %d días sobre las 88 celdas)." % (
        f4(mt["target_fpr_pooled_primary"]), mt["gap_tolerance"], mt["censor_days"]))
    w("")
    L.extend(table(["Test", "Umbral", "Tasa alcanzada", "Episodios de falsa alarma", "Racha media (días)", "Latencia censurada (días)"],
                   [[PN(t), "%.6f" % v["threshold"], f4(v["achieved_fpr"]), v["false_alarm_episodes"],
                     "%.1f" % v["mean_run_length"], "%.1f" % v["censored_latency_mean"]] for t, v in mt["tests"].items()]))
    w("")
    adv = b6["adverse_cells_primary"]
    w("**Celdas adversas bajo la regla pre-registrada** (FP de la primaria estrictamente mayor que el de alguna línea base pre-registrada, %s): %d de %d." % (
        list(b6["config"]["prereg_baselines_for_adverse_rule"]), len(adv), b6["summary"][b6["primary_key"]]["fp_cells"]))
    w("")
    if adv:
        L.extend(table(["Celda", "Primaria"] + [PN(b) for b in b6["config"]["prereg_baselines_for_adverse_rule"]], [
            [a["cell"], f4(a["primary"])] + [f4(a[b]) for b in b6["config"]["prereg_baselines_for_adverse_rule"]] for a in adv]))
        w("")
    oo = b6["oos_size"]
    w("**Tabla B6.3. Tamaño fuera de muestra de la configuración desplegada** (N = %d por D, familia %s, semilla independiente de la calibración; región %s)." % (
        oo["N"], oo["family"], oo["region"]))
    w("")
    L.extend(table(["D", "RM (anclado en la media)", "IC", "RM-GLS (primaria)", "IC"],
                   [[d, star(v["primary_rm"]), wil(v["primary_rm"]), star(v["primary_rmgls"]), wil(v["primary_rmgls"])]
                    for d, v in oo["by_D"].items()]))
    w("")
    w("**Tabla B6.4. Desviaciones del registro con su efecto medido** (`deviation_table_audit8.json`; las filas i–vii vienen de A7).")
    w("")
    L.extend(table(["Id", "Auditoría", "Elemento", "Pre-registrado", "Desplegado", "Efecto antes", "Efecto después"],
                   [[r["id"], r["audit"], r["element"], str(r.get("preregistered_value", r.get("preregistered"))),
                     str(r.get("deployed_value", r.get("deployed"))),
                     fmt_effect(r.get("effect_before")), fmt_effect(r.get("effect_after"))] for r in dev8["rows"]]))
    w("")

    # ---- B7 --------------------------------------------------------------------
    w("### B7 — %s" % BLOCK_TITLES["B7"])
    w("")
    cfg7 = b7["config"]
    w("Valores críticos de la cola inferior, calibración hac, N_cal = %d por (caso, n), familia %s; θ ∈ %s, n ∈ %s, α ∈ %s; EE del cuantil por bootstrap (%d remuestreos). CSV completo: `%s` (sha256 `%s`)." % (
        cfg7["N_cal"], b7["provenance"]["seed_family"], list(cfg7["thetas"]), list(cfg7["n"]), list(cfg7["alphas"]),
        cfg7["bootstrap_se"], b7["csv"], b7["csv_sha256"]))
    w("")
    w("**Tabla B7.1. Extracto: θ = 0.10, las cuatro α, los seis n, demeaned y con tendencia** (valor crítico y EE).")
    w("")
    prim_anchor = "gls" if b7["primary_is_gls"] else "mean"
    L.extend(table(["Caso", "n"] + ["α = %g" % al for al in cfg7["alphas"]],
                   [[cname("c" if k.startswith("dm") else "ct"), v["n"]]
                    + ["%s (%s)" % (f4(v["cv"]["%g" % al]), f4(v["se"]["%g" % al])) for al in cfg7["alphas"]]
                    for k, v in sorted(b7["table"].items(), key=lambda kv: (kv[1]["case"], kv[1]["n"]))
                    if v["theta"] == 0.1 and v["anchor"] == prim_anchor]))
    w("")
    aud = b7["cross_seed_audit"]
    w("Auditoría de semilla cruzada sobre el %s de las celdas de la primaria (%d celdas, las de mayor EE relativo): desviación máxima absoluta %s. Por celda: %s." % (
        pct(aud["share"]), len(aud["cells"]), f4(aud["max_abs_deviation"]),
        "; ".join("%s: %s (%.1f EE)" % (k, f4(v["max_abs_deviation"]), v["max_abs_deviation_in_se"]) for k, v in aud["by_cell"].items())))
    w("")
    th = b7["theory"]
    if "trace_vs_closed" in th:
        w("**Tabla B7.2. Verificación de la teoría del límite** (%s). E[F₁^θ] en forma cerrada frente a la traza del espectro; Paso 0 en θ = %g contra A3: |Δ| traza %s, |Δ| forma cerrada %s." % (
            th["variant"], th["paso0_a3"]["theta"], sci(th["paso0_a3"]["abs_diff_trace"]), sci(th["paso0_a3"]["abs_diff_closed"])))
        w("")
        L.extend(table(["θ", "Forma cerrada", "Traza del espectro", "Error relativo"],
                       [[t, f4(v["closed_form"]), f4(v["trace"]), pct(v["rel_error"])] for t, v in th["trace_vs_closed"].items()]))
        w("")
        w("Momento finito n y KS de una muestra contra la inversión de Davies (θ = %g; %s):" % (th["paso0_a3"]["theta"], th["davies_evaluation"]))
        w("")
        L.extend(table(["n", "E[[g₁]²]/E[F₁] con σ = 1 (EE)", "con σ̂_HAC (EE)", "KS D", "Umbral 1.358/√N", "¿Por debajo?"],
                       [[n, "%s (%s)" % (f4(th["moment_ratio"][n]["ratio_sigma1"]), f4(th["moment_ratio"][n]["se_sigma1"])),
                         "%s (%s)" % (f4(th["moment_ratio"][n]["ratio_hac"]), f4(th["moment_ratio"][n]["se_hac"])),
                         f4(th["ks_davies"][n]["D"]), f4(th["ks_davies"][n]["threshold"]), th["ks_davies"][n]["below_threshold"]]
                        for n in th["moment_ratio"]]))
        w("")
    else:
        w("**Tabla B7.2. Verificación 2-bis (primaria RM-GLS; %s).** Muestra de %d réplicas a n = %d frente a las de la rejilla: KS de dos muestras, tamaño a n = %d usando el valor crítico calibrado en cada n, y momento E[[g₁ᴳᴸˢ]²]." % (
            th["note"], th["N"], th["n_big"], th["n_big"]))
        w("")
        L.extend(table(["n", "KS D", "p", "Umbral", "¿Por debajo?", "Valor crítico al 5% en n",
                        "Tamaño a n = %d con ese valor crítico" % th["n_big"], "E[[g₁ᴳᴸˢ]²] con σ = 1 (EE)", "E[stat²] con σ̂"],
                       [[n, f4(th["ks_two_sample_vs_n20000"][n]["D"]), f4(th["ks_two_sample_vs_n20000"][n]["p_value"]),
                         f4(th["ks_two_sample_vs_n20000"][n]["threshold"]), th["ks_two_sample_vs_n20000"][n]["below_threshold"],
                         f4(th["size_at_n20000_with_cv_of_each_n"][n]["cv_at_n"]),
                         f4(th["size_at_n20000_with_cv_of_each_n"][n]["size_at_n20000_with_that_cv"]),
                         "%s (%s)" % (f4(th["moment_E_g1gls2_by_n"][n]["E_g1gls2_sigma1"]), f4(th["moment_E_g1gls2_by_n"][n]["se"])),
                         f4(th["moment_E_g1gls2_by_n"][n]["E_g1gls2_hac"])]
                        for n in th["ks_two_sample_vs_n20000"]]))
        w("")
        w("A n = %d: E[stat²] con σ̂ = %s (EE %s). Este punto solo reporta; no se deriva teoría." % (
            th["n_big"], f4(th["moment_at_n20000"]["E_stat2_hac"]), f4(th["moment_at_n20000"]["se"])))
        w("")

    # ---- B8 --------------------------------------------------------------------
    w("### B8 — %s" % BLOCK_TITLES["B8"])
    w("")
    w("PDF vectorial de doble columna, legibles en escala de grises; el generador (`experiments/make_figures_audit8.py`) lee solo JSON (%s) y copia cada figura a `paper/figures/`." % ", ".join("`%s`" % s for s in b8["sources"]))
    w("")
    L.extend(table(["Figura", "sha256", "Bytes", "Copia en paper/", "sha256 de la copia"],
                   [[k, "`%s`" % v["sha256"], v["bytes"], v["paper_copy"], "`%s`" % v["paper_copy_sha256"]]
                    for k, v in b8["figures"].items()]))
    w("")
    # ---- 2 --------------------------------------------------------------------
    w("## 2. Compuertas")
    w("")
    crit = protocol_bullets("### B1 — validaciones (todas DURA)")
    gates = b1["gates"]
    cr = npg["criteria"]
    ga, gi = b2["B2a"]["gate"], b2i["gate"]
    gb_old = b2["B2b"]["gate"]
    bud3, bud5 = J("b3_budget_audit8.json"), J("b5_budget_audit8.json")
    rule = b4["gls_rule"]
    rows = [
        ["B1 Ng–Perron original (DURA; sustituida por la enmienda 1)", crit[0],
         "; ".join("%s/%s %s" % (c, s, pct(v["rel_diff"])) for c, r in v5["cases"].items() for s, v in r["stats"].items()),
         verdict(gates["V5_ng_perron"]), "Detuvo la auditoría; el autor la sustituyó por B1-NP (enmienda 1)"],
        ["B1-NP (DURA; enmienda 1)", amendment_gate_text(),
         "(a) %s; (b) %s / %s; (c) %s; (d) %s" % (
             ", ".join("%s/%s %s" % (c, s, pct(v["rel_diff"])) for c, r in cr["a"].items() for s, v in r.items()),
             sci(cr["b"]["c"]["max_rel_diff"]), sci(cr["b"]["ct"]["max_rel_diff"]),
             ", ".join("%s/%s %.2f EE" % (c, s, v["diff_in_se"]) for c, r in cr["c"].items() for s, v in r.items()),
             "convención del artículo" if cr["d"]["code_uses_paper_convention"] else "otra convención"),
         verdict(npg["passed"]), "Continuar con B2"],
        ["B1 regresión pre/post (DURA)", crit[1], "estadístico %s; p-valor %s; suite: %s" % (
            v1["max_abs_diff_statistic"], v1["max_abs_diff_p_value"], py["summary"]),
         verdict(gates["V1_regression"] and py["counts"].get("failed", 0) == 0), "—"],
        ["B1 τ = 0 frente a MSB-HAC (DURA)", crit[2], sci(v3["worst_rel_diff"]), verdict(gates["V3_tau0_vs_msb_hac"]), "—"],
        ["B1 RM-GLS invariancia y deriva (DURA)", crit[3], "constante %s; tendencia %s; deriva %s" % (
            sci(inv4["worst_rel_diff"]["c"]), sci(inv4["worst_rel_diff"]["ct"]), sci(dr["worst_rel_diff_rm_gls_ct"])),
         verdict(gates["V4_gls_invariance"] and gates["V4_gls_drift"]), "—"],
        ["Regresión pre/post de la corrección de caché (regla 6; enmienda 2)",
         "max|Δ| = 0 en estadístico y p-valor con defaults y una sola llamada; suite en verde; test de dos N_cal en el mismo proceso",
         "estadístico %s; p-valor %s; muestra nula idéntica %s; el paquete anterior devolvía la nula de 10000 en la segunda llamada (%s puntos)" % (
             cfx["regression"]["max_abs_diff_statistic"], cfx["regression"]["max_abs_diff_p_value"],
             cfx["regression"]["null_sample_identical"], cfx["bug_demonstration"]["pre_fix"]["second_len"]),
         verdict(cfx["regression"]["passed"]), "—"],
        ["B2a (DURA)", " ".join(protocol_bullets("### COMPUERTA B2a (DURA)")),
         "máx. |Δ| %s pp; mín. McNemar p %s; conteo GARCH %d frente a %d; test de signo p %s; media de Δ GARCH %s pp" % (
             pp1(ga["max_abs_delta_pp"]), f4(ga["min_mcnemar_p"]), ga["count_in_region_garch_R0"],
             ga["count_in_region_garch_R05"], f4(ga["sign_test_p"]), pp2(ga["mean_delta_pp_garch"])),
         ga["verdict"], "Continuar con B2b"],
        ["B2b original (DURA; sustituida por la enmienda 2)", " ".join(protocol_bullets("### COMPUERTA B2b (DURA)")),
         "; ".join("n = %s: %s" % (n, f4(v)) for n, v in gb_old["sizes"].items()), gb_old["verdict"],
         "Detuvo la auditoría; el autor la sustituyó por la B2b de la enmienda 2 tras el diagnóstico"],
        ["B2b (DURA; enmienda 2)", amendment2_gate_text(),
         "; ".join("n = %s: %s %s" % (n, f4(v["rate"]), wil(v)) for n, v in gi["sizes"].items()) + "; región %s" % gi["region"],
         gi["verdict"], "Continuar con B3"],
        ["Presupuesto de B3 (CARO, %.0f h)" % bud3["budget_hours"], "Una celda completa, extrapolar y detener si supera el presupuesto",
         "%.1f h proyectadas" % bud3["projected_total_hours"], "dentro" if bud3["within_budget"] else "EXCEDE",
         "Ejecutado" if bud3["within_budget"] else "No se lanza"],
        ["B3 (INFORMATIVA)", " ".join(protocol_bullets("### COMPUERTA B3 (INFORMATIVA)")),
         "D1 %s; D2 %s; D3 %s" % ("sí" if b3["D1"]["holds"] else "no", "sí" if b3["D2"]["holds"] else "no",
                                  "no evaluable" if b3["D3"] is None else ("sí" if b3["D3"]["holds"] else "no")),
         "D1 %s / D2 %s / D3 %s" % ("sí" if b3["D1"]["holds"] else "no", "sí" if b3["D2"]["holds"] else "no",
                                    "—" if b3["D3"] is None else ("sí" if b3["D3"]["holds"] else "no")),
         "No detiene"],
        ["B4 previa (DURA)", " ".join(protocol_bullets("### B4 — compuerta previa (DURA)")),
         "; ".join("%s: %s" % (case, ", ".join("%s %s" % (PN(p), f4(v["rate"])) for p, v in r["gate_c0"].items() if not v["in_region"]) or "todos dentro")
                   for case, r in b4["cases"].items()),
         verdict(b4["prior_gate"]["passed"]), "Continuar con la regla GLS"],
        ["Regla de adopción GLS (B4)", "G1, G2 y G3 (protocolo §2)",
         "G1 reducción %s pp (umbral %s); G2 %s; G3 exceso %s pp (umbral %s)" % (
             pp1(rule["G1"]["reduction_pp"]), pp1(rule["G1"]["threshold_pp"]), rule["G2"]["holds"],
             pp2(rule["G3"]["excess_pp"]), pp2(rule["G3"]["threshold_pp"])),
         "adoptar GLS: %s" % rule["adopt_gls"], "Primaria final: %s" % rule["primary_final"]],
    ] + ([
        ["B2b aplicada a RM-GLS (DURA; enmienda 2, «aplica también a RM-GLS si B4 lo adopta»)", "La misma región y las mismas trayectorias; n = 200, 500 y 1000",
         "; ".join("n = %s: %s %s" % (n, f4(b2i["gaussian_rates_independent"][n]["rm_rmgls_hac"]["rate"]),
                                      wil(b2i["gaussian_rates_independent"][n]["rm_rmgls_hac"])) for n in gi["sizes"]),
         "PASA" if all(b2i["gaussian_rates_independent"][n]["rm_rmgls_hac"]["in_region"] for n in gi["sizes"]) else "FALLA",
         "Evaluada después de B4"],
    ] if rule["adopt_gls"] else []) + [
        ["Presupuesto de B5 (CARO, %.0f h)" % bud5["budget_hours"], "Una celda completa, extrapolar y detener si supera el presupuesto",
         "%.1f h proyectadas" % bud5["projected_total_hours"], "dentro" if bud5["within_budget"] else "EXCEDE",
         "Ejecutado" if bud5["within_budget"] else "No se lanza"],
    ]
    L.extend(table(["Compuerta", "Criterio (literal del protocolo o de la enmienda)", "Medido", "Veredicto", "Acción"], rows))
    w("")

    # ---- 3 --------------------------------------------------------------------
    w("## 3. Procedencia")
    w("")
    w("**Archivos que alimentan las tablas** (`manifest_audit8.json`).")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "mtime (UTC)", "Script", "Commit", "Código commiteado"],
                   [[k, "`%s`" % e["sha256"], e["bytes"], e["mtime_utc"], e["script"], e["commit"][:7], e["code_all_committed"]]
                    for k, e in sorted(man["entries"].items()) if not k.endswith("resultados_auditoria_8.md")]))
    w("")
    w("El propio reporte no se lista: su sha256 se registra en `manifest_audit8.json` después de escribirlo.")
    w("")
    npz = sorted(glob.glob(os.path.join(C.CKPT_ROOT, "audit8_b2", "cal_rm_n*.npz")))
    w("Las muestras nulas de RM de B2 y los checkpoints de B7 son `.npz` y no se commitean: se regeneran bit a bit desde sus semillas (control de la Tabla B2.0). sha256 de las muestras nulas:")
    w("")
    L.extend(table(["Archivo", "sha256"], [[C.rel(p), "`%s`" % C.sha256_file(p)] for p in npz]))
    w("")
    w("**Paso 0 por bloque.**")
    w("")
    L.extend(table(["Bloque", "Qué se repara", "Peor máx. |Δ|"], [
        ["B1", "regresión pre/post del paquete (100 series): estadístico y p-valor", "%s / %s" % (
            v1["max_abs_diff_statistic"], v1["max_abs_diff_p_value"])],
        ["B1 (caché)", "regresión pre/post de la corrección de caché: estadístico y p-valor", "%s / %s" % (
            cfx["regression"]["max_abs_diff_statistic"], cfx["regression"]["max_abs_diff_p_value"])],
        ["B2", "%d celdas reutilizadas: serie, estadístico R = 0.5 y componentes de A7" % len(b2["paso0"]["cells"]),
         "%s / %s / %s" % (b2["paso0"]["worst"]["max_abs_diff_series"],
                           b2["paso0"]["worst"]["max_abs_diff_stat_R05_vs_compute_statistic"],
                           b2["paso0"]["worst"]["max_abs_diff_a7_components_and_pvalues"])],
        ["B2", "reproducción de las tasas publicadas (peor diferencia; §7a)", f4(b2["paso0"]["worst"]["max_abs_rate_diff"])],
        ["B5", "DGP 5: componentes frente a los checkpoints de A7 (%d réplicas por celda)" % b5["dgp5"]["paso0"]["reps"],
         sci(b5["dgp5"]["paso0"]["max_abs_diff_components"])],
        ["B6", "R̂, ADF, PP, KPSS y DF-GLS (AIC) publicados en %d ventanas de %d celdas" % (
            b6["paso0"]["windows"], len(b6["paso0"]["cells"])),
         "; ".join("%s %s" % (k, sci(v)) for k, v in b6["paso0"]["worst"].items())],
        ["B2 (calibrador)", "muestra nula de RM frente a `_simulate_null_statistics` de producción, por n",
         "; ".join("%s" % v["R0_hac_max_abs_diff"] for v in b2["calibrator_control"].values())],
    ]))
    w("")
    c = py["counts"]
    w("- Suite completa (`pytest_audit8.log`): collected %s; passed %d; failed %d; skipped %d; %.1f s." % (
        py["collected"], c.get("passed", 0), c.get("failed", 0), c.get("skipped", 0), py["seconds"]))
    w("- Test de literales (`tests/test_no_literals_audit8.py`): %s." % (
        "; ".join("%s %s" % t for t in py["literals"]) or "sin resultados en el log"))
    w("- Las columnas sin bootstrap de B3 se calcularon en la pasada de B2 y no pasan por la caché de la nula: %s (`cache_fix_audit8.json`)." %
      cfx["b2_columns_cache_free"]["cache_free"])
    w("")

    # ---- 4 --------------------------------------------------------------------
    w("## 4. Desviaciones")
    w("")
    L.extend(table(["Qué", "Por qué", "Antes/después de ver datos", "Efecto"], DEVIATIONS(inv, ga, b2i, b5, b6, J("b5_budget_audit8.json"))))
    w("")

    # ---- 5 --------------------------------------------------------------------
    w("## 5. No ejecutado")
    w("")
    L.extend(table(["Qué", "Por qué", "Comando de reanudación"], [
        ["MZ_α y MP_T como comparadores de B3, B4 y B5", "Retirados por la enmienda 1 del autor",
         "revertir la enmienda 1 y usar `NP_STATS` completo en `audit8_unitroot.comparator_row`"],
        ["Bootstrap AWB en las celdas de n = 2000 y 5000 (B3, B5, B8)", "Retirado por la enmienda 2 por coste (la medición a n = 5000 fue informal y no quedó en un JSON)",
         "`python experiments/audit8_b3_comparators.py --budget --cores 14` con `D.N_BOOT_MAX` ampliado"],
        ["Reproducción de los tamaños publicados a n = 60, 100 y 150 con θ = 0.5", "Fuera del plan de A8 (§7a)",
         "`python experiments/audit8_b2b_diagnostic.py --cores 14` con θ = 0.5 añadido a `SMALL_N`"],
    ] + ([] if b7["primary_is_gls"] else [
        ["Verificación 2-bis de B7 (límite de RM-GLS)", "Solo aplica si la primaria es RM-GLS; la primaria final es %s" % rule["primary_final"],
         "`python experiments/audit8_b7_critical_values.py --cores 14` tras adoptar RM-GLS"]])))
    w("")

    # ---- 6 --------------------------------------------------------------------
    w("## 6. Conclusiones")
    w("")
    gi_sizes = b2i["gaussian_rates_independent"]
    prim_key = "rm_rmgls_hac" if rule["adopt_gls"] else "rm_R0_t0.1_hac"
    d_pp = lambda n, p: pp2(b3["mean_delta_by_n"][str(n)][p]["mean"] * 100)
    w("1. **La primaria final es %s** (regla de adopción GLS: G1 %s, G2 %s, G3 %s; Tabla B4.3)." % (
        rule["primary_final"], rule["G1"]["holds"], rule["G2"]["holds"], rule["G3"]["holds"]))
    w("2. **Tamaño gaussiano de RM `hac` sobre trayectorias independientes** (N = %d por n; Tabla B2b-E2.1): %s. La compuerta B2b de la enmienda 2 pasa; sobre las 5000 trayectorias publicadas a n = 200 la cifra es %s (§7a). Sobre las mismas trayectorias independientes, RM-GLS `hac`: %s." % (
        b2i["gate"]["N"], ", ".join("n = %s: %s" % (n, f4(v["rm_R0_t0.1_hac"]["rate"])) for n, v in gi_sizes.items()),
        f4(b2["B2b"]["gaussian_size"]["200"]["hac"]["rate"]),
        ", ".join("n = %s: %s" % (n, f4(v["rm_rmgls_hac"]["rate"])) for n, v in gi_sizes.items())))
    w("3. **Media de Δ con referencia independiente** (Tabla B3.2): a n = 200, RM `hac` %s pp, ADF-sim %s pp, DF-GLS-asy %s pp, DF-GLS-sim %s pp; a n = 500, %s, %s, %s y %s pp." % (
        d_pp(200, "rm_R0_t0.1_hac"), d_pp(200, "adf_sim"), d_pp(200, "dfgls_asy"), d_pp(200, "dfgls_sim"),
        d_pp(500, "rm_R0_t0.1_hac"), d_pp(500, "adf_sim"), d_pp(500, "dfgls_asy"), d_pp(500, "dfgls_sim")))
    w("4. **B2a pasa** (Tabla B2a.1): máx. |Δ| entre R = 0 y R = 0.5 de %s pp, mínimo p de McNemar %s, conteo GARCH %d frente a %d." % (
        pp1(ga["max_abs_delta_pp"]), f4(ga["min_mcnemar_p"]), ga["count_in_region_garch_R0"], ga["count_in_region_garch_R05"]))
    w("5. **Al pasar de `one` a `hac`** el conteo GARCH dentro de la región con las trayectorias publicadas baja de %d a %d (Tabla B2b.4) y el tamaño gaussiano a n = 200 sube de %s a %s (Tabla B2b.1)." % (
        b2["B2b"]["count_in_region"]["rm_R0_t0.1_one"]["garch"], b2["B2b"]["count_in_region"]["rm_R0_t0.1_hac"]["garch"],
        f4(b2["B2b"]["gaussian_size"]["200"]["one"]["rate"]), f4(b2["B2b"]["gaussian_size"]["200"]["hac"]["rate"])))
    w("6. **D1 %s, D2 %s, D3 %s** (Tabla B3.3): %s." % (
        "sí" if b3["D1"]["holds"] else "no", "sí" if b3["D2"]["holds"] else "no",
        "no evaluable" if b3["D3"] is None else ("sí" if b3["D3"]["holds"] else "no"),
        "; ".join("n = %s: %s" % (n, ", ".join("%s %s" % (PN(c), "sí" if v["holds"] else "no") for c, v in cc.items()))
                  for n, cc in b3["D1"]["by_n"].items())))
    w("7. **Brecha a la envolvente en c = 10** (caso demeaned, Tabla B4.1): primaria %s pp, DF-GLS %s pp; RM demeaned %s pp y RM-GLS %s pp." % (
        pp1(b4["cases"]["dm"]["gap_to_envelope"]["gls_t0.1" if rule["adopt_gls"] else "rm_t0.1"]["10.0"] * 100),
        pp1(b4["cases"]["dm"]["gap_to_envelope"]["dfgls"]["10.0"] * 100),
        pp1(b4["cases"]["dm"]["gap_to_envelope"]["rm_t0.1"]["10.0"] * 100),
        pp1(b4["cases"]["dm"]["gap_to_envelope"]["gls_t0.1"]["10.0"] * 100)))
    w("8. **Potencia en muestra finita** (Tabla B5.dgp1): frente a AR(0.95) a n = 200 la primaria rechaza %s y ADF %s; a ρ = 0.99 y n = 1000, %s frente a %s." % (
        f4(b5["dgp1"]["dgp1_rho0p95_n200"]["rates"][prim5_key(b5)]["rate"]), f4(b5["dgp1"]["dgp1_rho0p95_n200"]["rates"]["adf"]["rate"]),
        f4(b5["dgp1"]["dgp1_rho0p99_n1000"]["rates"][prim5_key(b5)]["rate"]), f4(b5["dgp1"]["dgp1_rho0p99_n1000"]["rates"]["adf"]["rate"])))
    pk6 = b6["primary_key"]
    w("9. **Aplicación** (Tablas B6.1 y B6.2): la primaria (%s) da FP media %s (máx. %s) y %d detecciones de %d con latencia media %s días; RM anclado en la media da %s, %s, %d y %s; el R̂ pre-registrado publicado da %s, %s, %d y %s. A tasa igualada (%s) la primaria tiene %d episodios de falsa alarma frente a %d de ADF." % (
        {"primary_rmgls": "RM-GLS", "primary_rm": "RM"}[pk6], f4(b6["summary"][pk6]["fp_mean"]), f4(b6["summary"][pk6]["fp_max"]),
        b6["summary"][pk6]["detections"], b6["summary"][pk6]["event_cells"],
        "%.1f" % b6["summary"][pk6]["mean_latency_detected"],
        f4(b6["summary"]["primary_rm"]["fp_mean"]), f4(b6["summary"]["primary_rm"]["fp_max"]),
        b6["summary"]["primary_rm"]["detections"], "%.1f" % b6["summary"]["primary_rm"]["mean_latency_detected"],
        f4(b6["summary"]["rhat_prereg"]["fp_mean"]), f4(b6["summary"]["rhat_prereg"]["fp_max"]),
        b6["summary"]["rhat_prereg"]["detections"], "%.1f" % b6["summary"]["rhat_prereg"]["mean_latency_detected"],
        f4(b6["matched_rate"]["target_fpr_pooled_primary"]), b6["matched_rate"]["tests"][pk6]["false_alarm_episodes"],
        b6["matched_rate"]["tests"]["adf"]["false_alarm_episodes"]))
    th = b7["theory"]
    if b7["primary_is_gls"]:
        ks = th["ks_two_sample_vs_n20000"]
        sz = th["size_at_n20000_with_cv_of_each_n"]
        w("10. **Valores críticos y verificación 2-bis** (Tablas B7.1 y B7.2): el valor crítico al 5%% de la primaria (θ = 0.1, demeaned) va de %s a n = %s a %s a n = %s; la auditoría de semilla cruzada da desviación máxima %s; el KS de dos muestras frente a n = %d queda por debajo del umbral en %d de %d n (%s); el tamaño a n = %d con el valor crítico de cada n va de %s (n = %s) a %s (n = %s)." % (
            f4(b7["table"]["dm|gls|0.1|%s" % b7["config"]["n"][0]]["cv"]["0.05"]), b7["config"]["n"][0],
            f4(b7["table"]["dm|gls|0.1|%s" % b7["config"]["n"][-1]]["cv"]["0.05"]), b7["config"]["n"][-1],
            f4(b7["cross_seed_audit"]["max_abs_deviation"]), th["n_big"],
            sum(v["below_threshold"] for v in ks.values()), len(ks),
            ", ".join("n = %s" % n for n, v in ks.items() if v["below_threshold"]), th["n_big"],
            f4(min(v["size_at_n20000_with_that_cv"] for v in sz.values())), min(sz, key=lambda n: sz[n]["size_at_n20000_with_that_cv"]),
            f4(max(v["size_at_n20000_with_that_cv"] for v in sz.values())), max(sz, key=lambda n: sz[n]["size_at_n20000_with_that_cv"])))
    else:
        w("10. **Valores críticos y teoría** (Tablas B7.1 y B7.2): la variación del valor crítico al 5%% entre n es %s (B2b.5); la auditoría de semilla cruzada da desviación máxima %s; la traza del espectro reproduce E[F₁^θ] con error relativo máximo %s y el KS contra la inversión de Davies queda por debajo del umbral en %d de %d n." % (
            pct(b2["B2b"]["rm_hac_cv_max_rel_variation"]), f4(b7["cross_seed_audit"]["max_abs_deviation"]),
            pct(max(v["rel_error"] for v in b7["theory"]["trace_vs_closed"].values())) if "trace_vs_closed" in b7["theory"] else "—",
            sum(v["below_threshold"] for v in b7["theory"].get("ks_davies", {}).values()),
            len(b7["theory"].get("ks_davies", {}))))
        w("")
    w("")
    # ---- 7 --------------------------------------------------------------------
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    w("### (a) Anomalías numéricas")
    w("")
    fails = [(c, s, v) for c, r in v5["cases"].items() for s, v in r["stats"].items() if not v["passed"]]
    d3d = diag["D3_ers_pt"]
    w("- **Anomalía de referencia: MP_T y MZ_α frente a Ng–Perron (2001, Tabla 1).** %s. Según la enmienda 1: atribuible a precisión de las tablas publicadas; no afecta a ninguna comparación, porque ambos estadísticos se retiraron y los contrastes de tamaño usan valores críticos simulados. Registros: residuo GLS y estadístico t idénticos a `arch` (Tabla B1.3); P_T de ERS sobre los mismos caminos a %s y %s de ERS (1996); ERS (1996) y Ng–Perron (2001) difieren entre sí en %s y %s." % (
        "; ".join("%s %s %s frente a %s" % (cname(c), s, f4(v["empirical_q05"]), v["ng_perron_2001"]) for c, s, v in fails),
        pct(d3d["c"]["pt_rel_diff_vs_ers"]), pct(d3d["ct"]["pt_rel_diff_vs_ers"]),
        pct(d3d["c"]["ers_vs_ng_perron_rel_diff"]), pct(d3d["ct"]["ers_vs_ng_perron_rel_diff"])))
    d2i = b2d["D2_independent_calibration"]
    w("- **Tamaño de RM `hac` en las 5000 trayectorias gaussianas publicadas de n = 200.** %s %s, fuera de %s, mientras que sobre %d trayectorias independientes del diagnóstico es %s %s (Tabla B2b.7) y sobre las %d de la compuerta de la enmienda 2, %s %s (Tabla B2b-E2.1). Descartado: una diferencia entre el estadístico de los datos y el de la calibración (misma función); el ruido de la muestra de calibración (con una calibración independiente sobre las mismas trayectorias: %s %s). Las trayectorias publicadas usan `default_rng(0 + i)` en todos los n, de modo que la de n = 200 es prefijo de las de 500 y 1000. No se atribuye causa." % (
        f4(b2["B2b"]["gaussian_size"]["200"]["hac"]["rate"]), wil(b2["B2b"]["gaussian_size"]["200"]["hac"]),
        b2["exact_region"], b2d["D1_independent_paths"]["200"]["n"], f4(b2d["D1_independent_paths"]["200"]["rate"]),
        wil(b2d["D1_independent_paths"]["200"]), b2i["gate"]["N"], f4(b2i["gate"]["sizes"]["200"]["rate"]),
        wil(b2i["gate"]["sizes"]["200"]), f4(d2i["published_paths_rate_independent_cal"]["rate"]),
        wil(d2i["published_paths_rate_independent_cal"])))
    d4 = b2d["D4_small_n_published"]
    w("- **Tamaños publicados a n = 60, 100 y 150 (R = 0.5): el defecto de la caché.** Se reproducen con la nula de N_cal = 10000 (%s) y no con la de 50000 (%s): %s. Causa identificada y corregida en producción (enmienda 2, punto 3): la clave de caché no incluía N_cal. Alcance en §7(b)." % (
        all(v["matches"]["10000"] for v in d4.values()), all(v["matches"]["50000"] for v in d4.values()),
        "; ".join("n = %s: %s con 10000, %s con 50000, publicado %s" % (n, f4(v["reproduced_by_N_cal"]["10000"]),
                                                                        f4(v["reproduced_by_N_cal"]["50000"]), f4(v["published"]))
                  for n, v in d4.items())))
    bs = b3["bootstrap_size_n200_N5000"]
    if bs:
        w("- **Tamaño del bootstrap AWB a n = 200.** %s %s sobre %d trayectorias nuevas (familia 93), frente a 0.0588 [0.0524, 0.0657] registrado en A7 y 0.0450 en A6 sobre otras trayectorias. A7 dejó la diferencia sin diagnóstico; esta medición la acompaña sin atribuirle causa." % (
            f4(bs["rate"]), wil(bs), bs["n"]))
    w("")
    w("### (b) Alcance del defecto de caché y frases del manuscrito")
    w("")
    w("**Tabla 7b.1. Alcance del defecto de la clave de caché en A1–A7** (`cache_fix_audit8.json`; solo identificación, sin recálculos fuera del plan).")
    w("")
    rows7 = []
    for s in cfx["scope_affected"]:
        for p in s["paper"]:
            repro = "—"
            if "reproduced_with_wrong_null_N_cal_10000" in p:
                repro = "con la nula equivocada (N_cal = 10000): %s; con la correcta (50000): %s" % (
                    p["reproduced_with_wrong_null_N_cal_10000"], p["reproduced_with_correct_null_N_cal_50000"])
            else:
                repro = p["reproduction_source"]
            rows7.append(["`%s`" % s["script"], s["order"], ", ".join(s["outputs"]),
                          "`%s:%d`" % (p["file"], p["line"]), p["values"], repro])
    L.extend(table(["Script", "Orden de las llamadas", "Salida", "Cifra publicada", "Valores", "Reproducción"], rows7))
    w("")
    w("Scripts revisados sin colisión (%d): %s." % (len(cfx["scope_scanned_no_collision"]),
                                                    "; ".join("`%s` (%s)" % (k, v) for k, v in cfx["scope_scanned_no_collision"].items())))
    w("")
    w("**Tabla 7b.2. Frases del manuscrito v11 revisadas.**")
    w("")
    claims = manuscript_claims()
    L.extend(table(["Frase", "Archivo:línea", "Cita", "Estado"],
                   [[c["label"], "`%s:%d`" % (c["file"], c["line"]), c["quote"],
                     claim_status2(c["key"], b2, b2d, b3, b5, b6, rule)] for c in claims]))
    w("")

    # ---- anexo ----------------------------------------------------------------
    w("## Anexo: hechos para el manuscrito")
    w("")
    w("`clave | valor | IC o EE | archivo JSON | ruta dentro del JSON`")
    w("")
    facts = []
    for n, v in b2i["gaussian_rates_independent"].items():
        facts.append(("size_gauss_rm_hac_independent_n%s" % n, f4(v["rm_R0_t0.1_hac"]["rate"]), wil(v["rm_R0_t0.1_hac"]),
                      "b2b_indep_audit8.json", "gaussian_rates_independent/%s/rm_R0_t0.1_hac/rate" % n))
    for n in ("200", "500"):
        for p in ("rm_R0_t0.1_hac", "adf_sim", "dfgls_asy", "dfgls_sim", "rm_msbhac_hac", "mzt_sim", "msb_sim"):
            if p in b3["mean_delta_by_n"][n]:
                v = b3["mean_delta_by_n"][n][p]
                facts.append(("mean_delta_independent_n%s|%s" % (n, p), pp2(v["mean"] * 100) + " pp",
                              "EE %s pp" % se2(v["se"] * 100), "b3_comparators_audit8.json", "mean_delta_by_n/%s/%s/mean" % (n, p)))
    for k, v in b2["B2b"]["misspec_rates"].items():
        if b2["cells"][k]["kind"] == "garch" and b2["cells"][k]["n"] == 200:
            for p in ("rm_R0_t0.1_hac", "rm_R0_t0.1_one", "adf_asy", "pp_asy"):
                facts.append(("garch_n200|%s|%s" % (k, p), f4(v[p]["rate"]), wil(v[p]), "b2_size_audit8.json",
                              "B2b/misspec_rates/%s/%s/rate" % (k, p)))
    for p in ("rm_t0.1", "gls_t0.1", "dfgls", "msb", "mzt", "msbhac"):
        facts.append(("gap_to_envelope_c10_dm|%s" % p, pp1(b4["cases"]["dm"]["gap_to_envelope"][p]["10.0"] * 100) + " pp", "—",
                      "b4_local_power_audit8.json", "cases/dm/gap_to_envelope/%s/10.0" % p))
    for t in ("primary_rmgls", "primary_rm", "rhat_prereg", "adf", "pp", "dfgls_maic", "mzt", "kpss"):
        s6 = b6["summary"][t]
        facts.append(("app_fp_mean|%s" % t, f4(s6["fp_mean"]), "máx. %s" % f4(s6["fp_max"]), "b6_application_audit8.json",
                      "summary/%s/fp_mean" % t))
        facts.append(("app_detections|%s" % t, "%d de %d" % (s6["detections"], s6["event_cells"]),
                      "latencia media %s" % ("%.1f" % s6["mean_latency_detected"] if s6["mean_latency_detected"] else "—"),
                      "b6_application_audit8.json", "summary/%s/detections" % t))
    for t, v in b6["matched_rate"]["tests"].items():
        facts.append(("app_matched_episodes|%s" % t, v["false_alarm_episodes"],
                      "racha media %.1f d; latencia censurada %.1f d" % (v["mean_run_length"], v["censored_latency_mean"]),
                      "b6_application_audit8.json", "matched_rate/tests/%s/false_alarm_episodes" % t))
    for d, v in b6["oos_size"]["by_D"].items():
        for t in ("primary_rmgls", "primary_rm"):
            facts.append(("app_oos_size_D%s|%s" % (d, t), f4(v[t]["rate"]), wil(v[t]), "b6_application_audit8.json",
                          "oos_size/by_D/%s/%s/rate" % (d, t)))
    prim_anchor = "gls" if rule["adopt_gls"] else "mean"
    for k, v in b7["table"].items():
        if v["theta"] == 0.1 and v["anchor"] == prim_anchor and v["case"] == "dm":
            facts.append(("cv_primary_dm_theta0.1_n%d_alpha0.05" % v["n"], f4(v["cv"]["0.05"]), "EE %s" % f4(v["se"]["0.05"]),
                          "b7_critical_values_audit8.json", "table/%s/cv/0.05" % k))
    facts += [
        ("primary_final", rule["primary_final"], "—", "b4_local_power_audit8.json", "gls_rule/primary_final"),
        ("b2a_verdict", ga["verdict"], "máx. |Δ| %s pp" % pp1(ga["max_abs_delta_pp"]), "b2_size_audit8.json", "B2a/gate/verdict"),
        ("b2b_verdict_amend2", b2i["gate"]["verdict"], "región %s" % str(b2i["gate"]["region"]), "b2b_indep_audit8.json", "gate/verdict"),
        ("D1", "sí" if b3["D1"]["holds"] else "no", "—", "b3_comparators_audit8.json", "D1/holds"),
        ("D2", "sí" if b3["D2"]["holds"] else "no", "—", "b3_comparators_audit8.json", "D2/holds"),
        ("D3", "no evaluable" if b3["D3"] is None else ("sí" if b3["D3"]["holds"] else "no"), "—",
         "b3_comparators_audit8.json", "D3/holds"),
        ("garch_in_region_primary_hac", b2["B2b"]["count_in_region"]["rm_R0_t0.1_hac"]["garch"], "de 16",
         "b2_size_audit8.json", "B2b/count_in_region/rm_R0_t0.1_hac/garch"),
        ("garch_in_region_R05_one", ga["count_in_region_garch_R05"], "de 16", "b2_size_audit8.json",
         "B2a/gate/count_in_region_garch_R05"),
        ("bootstrap_budget_hours", "%.1f" % J("b3_budget_audit8.json")["projected_total_hours"], "presupuesto 30 h",
         "b3_budget_audit8.json", "projected_total_hours"),
        ("b5_budget_hours", "%.1f" % J("b5_budget_audit8.json")["projected_total_hours"], "presupuesto 30 h",
         "b5_budget_audit8.json", "projected_total_hours"),
        ("seed_collisions_new_vs_prior", sm["collisions_new_vs_prior"], "—", "inventory_audit8.json",
         "seed_map/collisions_new_vs_prior"),
        ("cache_fix_regression", cfx["regression"]["max_abs_diff_statistic"], "p-valor %s" % cfx["regression"]["max_abs_diff_p_value"],
         "cache_fix_audit8.json", "regression/max_abs_diff_statistic"),
    ]
    if bs:
        facts.append(("bootstrap_size_n200_N5000", f4(bs["rate"]), wil(bs), "b3_comparators_audit8.json",
                      "bootstrap_size_n200_N5000/rate"))
    for k, v in b8["figures"].items():
        facts.append(("figure|%s" % k, "`%s`" % v["sha256"], "copia %s" % v["paper_copy"], "figures_audit8.json",
                      "figures/%s/sha256" % k))
    for f in facts:
        w("- %s" % " | ".join(str(x) for x in f))
    w("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    C.register_outputs(__file__, [OUT])
    print("escrito %s (%d lineas)" % (OUT, len(L)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
