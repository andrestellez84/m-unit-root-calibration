"""
Auditoria A10 - generador de experiments/results/resultados_auditoria_10.md.

Regla de A8 (regla 3): ningun numero de resultado se escribe a mano; todo valor se
lee de un JSON o log de experiments/results (o del .tex de paper/ para las citas
de la seccion 7). Si falta una clave, el script falla con KeyError. Los bloques
cuyo JSON no existe se declaran en la seccion 5 (No ejecutado). Cuando un numero
sigue viniendo de A8 o A9, la tabla y la tabla maestra lo indican con su archivo.
tests/test_no_literals_audit10.py recorre este archivo.

Estructura: encabezado; 1 resultados; 2 compuertas; 3 procedencia; 4 desviaciones;
5 no ejecutado; 6 conclusiones; 7 anomalias y frases del manuscrito; anexo
(tabla maestra del manuscrito).

Uso: python experiments/audit10_generate_report.py
"""
import datetime
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_design as D                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
from audit8_generate_report import (f4, sci, table as _table, star, wil, pp1, pp2, se1, se2, label, verdict, fmt_effect)  # noqa: E402
from audit9_generate_report import (PN, CASE, APP, CLAIMS, rr, mp, dse, dse1, mse)  # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_10.md")
PROTOCOL = "experiments/protocol_audit10.md"
F10 = {"B10.0": "b100_protocol_audit10.json", "PROBE": "b101_timing_audit10.json",
       "COLD": "b101_timing_coldstart_audit10.json", "B10.1": "b101_theta_audit10.json",
       "B10.2": "b102_identity_audit10.json", "EQ": "b103_equalized_audit10.json", "DGP5": "b103_dgp5_audit10.json",
       "FIN": "b103_finite_audit10.json", "AWBB": "b103_awb_budget_audit10.json", "AWB": "b103_awb_audit10.json",
       "APP": "b103_application_audit10.json", "CV": "b103_cv_audit10.json", "LOW": "b103_lown_audit10.json",
       "B10.4": "b104_cv5000_audit10.json", "FIG": "figures_audit10.json"}
F9 = {"B91": "b91_equalized_audit9.json", "B92": "b92_theta_audit9.json", "B93": "b93_attribution_audit9.json",
      "B94": "b94_finite_sample_audit9.json", "B95": "b95_awb_audit9.json", "B96": "b96_application_audit9.json",
      "B97": "b97_critical_values_audit9.json", "FIG": "figures_audit9.json"}
SCRIPTS = {"B10.1": "experiments/audit10_b101_theta.py", "B10.2": "experiments/audit10_b102_identity.py",
           "EQ": "experiments/audit10_b103_equalized.py", "DGP5": "experiments/audit10_b103_dgp5.py --cores 14",
           "FIN": "experiments/audit10_b103_finite.py", "AWB": "experiments/audit10_b103_awb.py --run --cores 14",
           "APP": "experiments/audit10_b103_application.py --cores 14", "CV": "experiments/audit10_b103_cv.py --cores 14",
           "LOW": "experiments/audit10_b103_lown.py --run --cores 14", "B10.4": "experiments/audit10_b104_cv5000.py --cores 14",
           "FIG": "experiments/make_figures_audit10.py"}
TITLES = {"B10.0": "Protocolo", "B10.1": "Decisión limpia de θ (DURA)", "B10.2": "Identidad del estadístico con θ = 0",
          "B10.3": "Consolidación con el θ final (condicional)", "B10.4": "Cierre de la anomalía de valores críticos a n = 5000",
          "B10.5": "Figuras finales"}
PROCS101 = tuple(E.tname(t) for t in E.THETAS) + ("rm_t0.1", "msbhac", "glsb_t0", "adf", "dfgls", "mzt", "msb")
THETA_KEYS = tuple(E.tname(t) for t in E.THETAS)
GAP_C = ("5.0", "10.0", "20.0")


def J(name):
    return C.read_json(name)


def table(header, rows):
    """Tabla markdown; las barras dentro de una celda se escapan."""
    def esc(x):
        return str(x).replace("|", "\\|")
    return _table([esc(h) for h in header], [[esc(x) for x in r] for r in rows])


def have(key):
    return os.path.exists(os.path.join(C.RESULTS, F10[key]))


def T(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def pname(p):
    return PN.get(p, p) + ("" if p in E.RM_LIKE or p not in ("adf", "pp", "dfgls", "mzt", "msb") else "-sim")


def note(json_name, n_sim, n_cal, family, region, extra=""):
    return ("*Fuente: `%s`; N_sim = %s; N_cal = %s; familia %s; región exacta %s.%s*" % (
        json_name, n_sim, n_cal, family, region, (" " + extra) if extra else ""))


def protocol_text(title):
    with open(os.path.join(C.REPO, PROTOCOL), encoding="utf-8") as f:
        text = f.read()
    i = text.index(title)
    ends = [x for x in (text.find("\n### ", i + 1), text.find("\n## ", i + 1)) if x > 0]
    return " ".join(l.strip() for l in text[i:min(ends) if ends else None].splitlines()[1:] if l.strip())


def theta():
    return J(F10["B10.1"])["primary_theta"]


def prim():
    return E.tname(theta())


def b103_ran():
    return have("B10.1") and theta() is not None and theta() != E.THETA_A8


# fuentes vigentes (A10 si existe; si no, A9)
def src_eq():
    return (F10["EQ"], J(F10["EQ"])) if have("EQ") else None


def src_fin():
    return (F10["FIN"], J(F10["FIN"])) if have("FIN") else (F9["B94"], J(F9["B94"]))


def src_awb():
    return (F10["AWB"], J(F10["AWB"])) if have("AWB") else (F9["B95"], J(F9["B95"]))


def src_app():
    return (F10["APP"], J(F10["APP"])) if have("APP") else (F9["B96"], J(F9["B96"]))


def src_cv():
    return (F10["CV"], J(F10["CV"])) if have("CV") else (F9["B97"], J(F9["B97"]))


def manuscript_claims():
    out = []
    for key, lab, fname, pat in CLAIMS:
        with open(os.path.join(C.REPO, fname), encoding="utf-8") as f:
            lines = f.read().splitlines()
        hit = next((k for k, l in enumerate(lines) if re.search(pat, l)), None)
        if hit is None:
            raise KeyError("frase no encontrada en %s: %s" % (fname, pat))
        out.append({"key": key, "label": lab, "file": fname, "line": hit + 1,
                    "quote": " ".join(l.strip() for l in lines[hit:hit + 2])})
    return out


def pytest_summary():
    name = "pytest_audit10.log"
    if not os.path.exists(os.path.join(C.RESULTS, name)):
        return None
    text = T(name)
    m = re.findall(r"=+ (.*?) in ([0-9.]+)s", text)
    summary, secs = m[-1]
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|errors?)", summary)}
    coll = re.search(r"collected (\d+) items", text)
    lit = re.findall(r"tests[\\/]test_no_literals_audit10\.py::(\S+) (PASSED|FAILED|SKIPPED)", text)
    return {"seconds": float(secs), "collected": int(coll.group(1)) if coll else None, "counts": counts, "literals": lit}


# ---------------------------------------------------------------------------
# B10.0
# ---------------------------------------------------------------------------
def sec_b100(w, L):
    b = J(F10["B10.0"])
    p = b["protocol"]
    w("### B10.0 — %s" % TITLES["B10.0"])
    w("")
    w("`%s`: sha256 `%s` (contenido commiteado `%s`), introducido en el commit `%s`. Es una enmienda declarada a la regla del θ de A9 (A1 → A1′). Familias: %s." % (
        p["path"], p["sha256_disk"], p["sha256_committed"], p["commit_added"][:7],
        ", ".join("%s = %s" % (k, v) for k, v in b["families"].items())))
    w("")
    w("Motivo (literal): %s" % protocol_text("## Motivo de la enmienda (literal)"))
    w("")
    w("**Tabla B10.0.1. JSON de A9 reutilizados.**")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "mtime (UTC)"],
                   [[k, "`%s`" % v["sha256"], v["bytes"], v["mtime_utc"]] for k, v in b["a9_inventory"].items()]))
    w("")
    w("**Tabla B10.0.2. Checkpoints de A9 reutilizados** (no se commitean; sha256 agregado de los sha256 ordenados).")
    w("")
    L.extend(table(["Carpeta", "Archivos", "Bytes", "sha256 agregado", "Última modificación (UTC)"],
                   [[k, v["files"], v["bytes"], "`%s`" % v["aggregate_sha256"], v["last_mtime_utc"]]
                    for k, v in b["a9_checkpoints"].items()]))
    w("")
    sp, s = b["spawn_equivalence"], b["seed_map"]
    w("Esquema de semillas: `SeedSequence(familia).spawn(celdas)[c].spawn(réplicas)[i]` frente a `SeedSequence(familia, spawn_key = (c, i))`: %d streams comparados (primeras %d réplicas de cada celda), discrepancias %d (**%s**)." % (
        sp["streams_checked"], sp["reps_checked_per_cell"], sp["mismatches"], "equivalentes" if sp["equivalent"] else "NO equivalentes"))
    w("")
    w("**Tabla B10.0.3. Colisión de semillas** (%s)." % s["method"])
    w("")
    L.extend(table(["Familia", "Celdas", "Streams de réplica", "Distintos"],
                   [[f, v["cells"], v["replicate_streams"], v["distinct"]] for f, v in s["new_families"].items()]))
    w("")
    w("Streams previos comparados: %d (enteros de A5–A7: %d; familias de A8 y A9: %s). Colisiones nuevas frente a previas: **%d**; dentro de A10: **%d**. Familias sin celdas: %s." % (
        s["prior_streams_total"], s["prior_integer_seeds"],
        ", ".join("%s: %d" % (k, v) for k, v in s["prior_family_streams"].items()),
        s["collisions_new_vs_prior"], s["collisions_within_new"], s["families_without_cells"]))
    w("")


# ---------------------------------------------------------------------------
# B10.1
# ---------------------------------------------------------------------------
def sec_b101(w, L):
    pr, cold = J(F10["PROBE"]), J(F10["COLD"])
    w("### B10.1 — %s" % TITLES["B10.1"])
    w("")
    w("**Tabla B10.1.t. Tiempo de calibración por configuración a n = %d** (N_cal = %d, %d núcleos; %s). Sonda con calentamiento (vigente) y la primera sonda sin calentamiento (registro)." % (
        pr["n"], pr["N_cal"], pr["cores"], pr["rule"]))
    w("")
    mins, mc = pr["projected_minutes_per_configuration"], cold["projected_minutes_per_configuration"]
    L.extend(table(["Configuración", "Minutos proyectados (vigente)", "Minutos (sonda en frío)"],
                   [[k, "%.1f" % v, "%.1f" % mc[k]] for k, v in mins.items()]))
    w("")
    w("Peor configuración: %s, %.1f min (compuerta %.0f min; en frío %s, %.1f min). Todas las configuraciones a n = %d en una pasada: %.1f min proyectados. %s." % (
        pr["worst_configuration"], pr["worst_minutes"], pr["gate_minutes"], cold["worst_configuration"], cold["worst_minutes"],
        pr["n"], pr["projected_minutes_all_configurations_n1000"], pr["attribution_note"]))
    w("")
    if not have("B10.1"):
        w("B10.1 sin analizar (§5).")
        w("")
        return
    b = J(F10["B10.1"])
    cfg = b["config"]
    w("**Tabla B10.1.cal. Calibración (caminos de producción, semilla %d).**" % cfg["cal_seed"])
    w("")
    L.extend(table(["n", "N_cal", "Filas reutilizadas de A9", "Paso 0 (máx. |Δ|)", "Tiempo real de pared de las filas nuevas (min)",
                    "Control de producción (máx. |Δ|)"],
                   [[n, v["N_cal"], v["reused_rows"], sci(v["paso0_max_abs_diff"]), "%.1f" % (v["wall_new_sec"] / 60),
                     sci(max(b["production_control"][n].values()))] for n, v in b["calibration"].items()]))
    w("")
    reg, reg1 = b["exact_region_100000"], b["exact_region_50000"]
    for case in D.CASES:
        w("**Tabla B10.1.A1′.%s. Tamaño gaussiano agregado (N = %d), caso %s** (entre corchetes el IC de Wilson; ✓ = |tamaño − 0.05| ≤ %s; * = dentro de la región exacta %s, informativa)." % (
            case, cfg["N_pooled"], CASE[case], cfg["tolerance"], reg))
        w("")
        rows = []
        for p in PROCS101:
            r = [pname(p)]
            for n in D.A1_N:
                v = b["cells"]["%s|%d" % (case, n)]["rates"][p]["pooled"]
                r.append("%s %s %s" % (star(v), wil(v), "✓" if v["within_tolerance"] else "✗"))
            rows.append(r)
        L.extend(table(["Procedimiento"] + ["n = %d" % n for n in D.A1_N], rows))
        w("")
        w("**Tabla B10.1.s.%s. Las dos muestras por separado (N = %d cada una; * = dentro de %s) y su diferencia (pp; EE).**" % (
            case, cfg["N_per_sample"], reg1))
        w("")
        rows = []
        for p in PROCS101:
            r = [pname(p)]
            for n in D.A1_N:
                v = b["cells"]["%s|%d" % (case, n)]["rates"][p]
                r.append("%s / %s; %s" % (star(v["sample_1"]), star(v["sample_2"]), dse(v["samples_diff"])))
            rows.append(r)
        L.extend(table(["Procedimiento"] + ["n = %d (muestra 1 / muestra 2; diferencia)" % n for n in D.A1_N], rows))
        w("")
        w(note(F10["B10.1"], "%d × %d" % (len(D.A1_SAMPLES), cfg["N_per_sample"]), cfg["N_cal"],
               "111 (celdas a1_%s_n<n>_s<k>, hijos distintos por caso y por muestra)" % case, reg,
               "RM-GLS, RM, MSB-HAC y (b): p = F̂(stat) < 0.05 con la ECDF de N_cal; el resto: stat < cuantil 5%."))
        w("")
    w("**Tabla B10.1.thr. Valores críticos simulados al 5%% (N_cal = %d).**" % cfg["N_cal"])
    w("")
    sp = ("adf", "dfgls", "mzt", "msb")
    L.extend(table(["Caso | n"] + [pname(p) for p in sp],
                   [[k] + ["%.4f" % v["sim_thresholds"][p] for p in sp] for k, v in b["cells"].items()]))
    w("")
    reuse, dec = b["reused_from_a9"], b["decision"]
    w("**Tabla B10.1.rule. Regla del θ primario, término a término** (A2 y P(θ) reutilizados de `%s`, sha256 `%s`, rutas `%s` y `%s`; no se recalculan)." % (
        reuse["source"], reuse["source_sha256"], reuse["A2_path"], reuse["P_path"]))
    w("")
    rows = []
    for t in THETA_KEYS:
        a1 = b["A1prime"][t]
        rows.append([pname(t), "%d de %d" % (sum(v["within_tolerance"] for v in a1.values()), len(a1)),
                     f4(max(v["abs_dev_from_alpha"] for v in a1.values())), b["A1prime_ok"][t],
                     mse(reuse["A2_mean_delta"][t]), reuse["A2_ok"][t], f4(reuse["P"][t]), t in dec["admissible"]])
    L.extend(table(["θ", "Celdas con |tamaño − 0.05| ≤ tolerancia", "Máx. |tamaño − 0.05|", "A1′", "A2: media Δ (pp; EE; A9)",
                    "A2 (A9)", "P(θ) (A9)", "Admisible"], rows))
    w("")
    w("Admisibles: %s. Mayor P entre ellos: %s. Grupo de empate (P a menos de %s pp del máximo): %s. **θ primario: %s.**" % (
        [pname(t) for t in dec["admissible"]] or "ninguno", pname(dec["top_P"]) if dec["top_P"] else "—", dec["tie_pp"],
        [pname(t) for t in dec["tie_group"]], "ninguno (la compuerta detiene)" if dec["winner"] is None else "%g" % dec["winner_theta"]))
    w("")
    w("Comparadores frente a A1′ (informativo; no deciden): %s." % ", ".join(
        "%s %s" % (pname(p), "✓" if b["A1prime_ok"][p] else "✗") for p in PROCS101 if p not in THETA_KEYS))
    w("")
    an = b["anomaly_ct200"]
    w("**Tabla B10.1.ct200. Cierre de la anomalía de A9: celda tendencia, n = 200** (marca %s; A9: las mismas trayectorias para los dos casos, N = %d)." % (
        an["mark"], D9.N_INDEP))
    w("")
    L.extend(table(["Procedimiento", "Agregada (N = %d)" % cfg["N_pooled"], "IC", "Muestra 1", "Muestra 2", "A9"],
                   [[pname(p), f4(v["pooled"]), "[%s, %s]" % (f4(v["wilson"][0]), f4(v["wilson"][1])), f4(v["sample_1"]),
                     f4(v["sample_2"]), f4(an["a9_rates_same_cell"][p]) if p in an["a9_rates_same_cell"] else "—"]
                    for p, v in an["rates"].items()]))
    w("")
    g9 = {q: v for q, v in J(F9["B92"])["gaussian_size"]["ct|200"].items() if not q.endswith("_asy")}
    w("Por debajo de %s: %d de %d (%s); en A9, sobre estos mismos %d procedimientos, %d; sobre los %d de la tabla de tamaño de B9.2 (incluye PP-sim), %d. ¿Se repite el patrón (≥ 7 de 12)? **%s**." % (
        an["mark"], an["count_below"], an["procedures"], [pname(p) for p in an["below_mark"]] or "ninguno",
        len(an["a9_rates_same_cell"]), an["a9_count_below"], len(g9), sum(v["rate"] < an["mark"] for v in g9.values()),
        "sí" if an["pattern_repeats"] else "no"))
    w("")


# ---------------------------------------------------------------------------
# B10.2
# ---------------------------------------------------------------------------
def sec_b102(w, L):
    b = J(F10["B10.2"])
    cfg = b["config"]
    w("### B10.2 — %s" % TITLES["B10.2"])
    w("")
    w("Relación algebraica (notación del proyecto: Y₀, …, Y_n; σ̂² = σ̂²_HAC de ΔY; û_k el residuo GLS del caso, ā = 1 + c̄/n en el caso c y ā = 1 + c̄/(n + 1) en el caso ct):")
    w("")
    w("    %s" % b["relation"]["same_convention"])
    w("    %s" % b["relation"]["exact_relation"])
    w("")
    w("Es decir: con la misma convención de índices y divisores RM-GLS(0) es el MSB construido sobre û con σ̂²_HAC en lugar de s²_AR, salvo el factor n/(n + 1) sobre MSB² y el término del extremo û_n²/(n(n + 1)σ̂²), que la forma de Ng–Perron (suma hasta n − 1, divisor n²) no incluye.")
    w("")
    w("**Tabla B10.2.1. Verificación numérica** (%d series por celda, familia 112; umbral %s; diferencias relativas)." % (cfg["reps"], sci(cfg["threshold"])))
    w("")
    L.extend(table(["Caso | n", "(i) producción frente a la misma convención (máx.)", "(ii) frente a la relación exacta (máx.)",
                    "Peso del término del extremo en RM-GLS(0)² (mediana; máx.)", "√(n/(n + 1))",
                    "MSB de A8 con σ̂²_HAC frente a MSB_HAC (mediana; máx.)", "Pasa"],
                   [[k, sci(v["i_production_vs_same_convention"]["max"]), sci(v["ii_production_vs_exact_relation_with_msb_hac"]["max"]),
                     "%s; %s" % (sci(v["endpoint_term_share_of_rm2"]["median"]), sci(v["endpoint_term_share_of_rm2"]["max"])),
                     "%.6f" % v["factor_sqrt_n_over_n_plus_1"],
                     "%s; %s" % (sci(v["info_msb_a8_with_sigma_hac_vs_msb_hac"]["median"]), sci(v["info_msb_a8_with_sigma_hac_vs_msb_hac"]["max"])),
                     v["pass"]] for k, v in b["cells"].items()]))
    w("")
    w("**Tabla B10.2.2. RM-GLS(θ) frente a RM-GLS(0) con τ = round(θn) pequeño, n = %d** (diferencia relativa sobre las mismas series)." % cfg["small_n"])
    w("")
    rows = []
    for k, v in b["cells"].items():
        for t, s in v.get("small_theta_vs_theta0", {}).items():
            rows.append([k, t, s["tau"], sci(s["mean"]), sci(s["median"]), sci(s["max"])])
    L.extend(table(["Caso | n", "θ", "τ", "Media", "Mediana", "Máx."], rows))
    w("")
    w(note(F10["B10.2"], cfg["reps"], "—", "112 (celdas id_<caso>_n<n>)", "—",
           "Peor (i): %s; peor (ii): %s; veredicto: %s. La columna «MSB de A8» difiere por convención: ā = 1 + c̄/T con T = n + 1 en el caso c y divisor T² en ambos casos." % (
               sci(b["worst_i"]), sci(b["worst_ii"]), "PASA" if b["pass"] else "FALLA")))
    w("")


# ---------------------------------------------------------------------------
# B10.3
# ---------------------------------------------------------------------------
EQ_PROCS = ("rm_t0.1", "msbhac", "adf", "pp", "dfgls", "mzt", "msb")


def eq_table(w, L, b, prefix, key_col, extra, p):
    cells = {k: v for k, v in b["cells"].items() if k.startswith(prefix)}
    procs = [p, "gls_t0.1"] + list(EQ_PROCS) + list(extra)
    L.extend(table([key_col, "n"] + [pname(q) for q in procs] + ["McNemar p vs DF-GLS-sim", "McNemar p vs θ = 0.1"],
                   [[v.get(key_col), v["n"]] + [star(v["rates_sim"][q]) for q in procs]
                    + [mp(v["mcnemar_primary_vs_sim"]["dfgls"]), mp(v["mcnemar_primary_vs_sim"]["gls_t0.1"])]
                    for v in sorted(cells.values(), key=lambda v: (v["n"], v.get(key_col, 0)))]))
    w("")


def sec_b103(w, L):
    w("### B10.3 — %s" % TITLES["B10.3"])
    w("")
    w("Condición (literal): %s" % protocol_text("### CONDICIÓN B10.3"))
    w("")
    if not b103_ran():
        w("θ final = %g: B10.3 no se ejecuta; todo lo de A9 sigue vigente (§5)." % theta())
        w("")
        return
    p = prim()
    w("θ final = %g ≠ 0.1: se ejecuta. Cada subbloque tiene su propio tope de 4 h; 3.4 es CARO (8 h)." % theta())
    w("")
    if have("EQ"):
        b = J(F10["EQ"])
        cfg = b["config"]
        w("#### 3.1 DGP 2 (y DGP 1, tendencia y DGP 3) a tamaño igualado con el θ final")
        w("")
        w("Trayectorias: %s. Regla: %s. Paso 0 frente a B5 de A8: peor máx. |Δ| = %s. Fuente de la calibración por procedimiento: %s." % (
            cfg["trajectories"], cfg["rule_sim"], sci(b["paso0_worst"]),
            "; ".join("%s: 500 000 → %s, 50 000 (A9) → %s" % (k, v["N_cal_500000"], v["N_cal_50000_a9"]) for k, v in cfg["calibration_source"].items())))
        w("")
        for prefix, key, extra, title in (("dgp2_", "delta", ("za",), "DGP 2 (AR(0.95) con quiebre de media)"),
                                          ("dgp1_", "rho", ("kpss",), "DGP 1 (AR(1), demeaned)"),
                                          ("ct_power_", "rho", (), "caso con tendencia"),
                                          ("dgp3_", "r", (), "DGP 3 (quiebre de varianza; tasas de tamaño con la nula verdadera)")):
            w("**Tabla B10.3.1.%s. %s** (* = dentro de %s)." % (prefix.rstrip("_"), title, b["exact_region_5000"]))
            w("")
            eq_table(w, L, b, prefix, key, extra, p)
            w(note(F10["EQ"], cfg["N_sim"], "%d (n ∈ {200, 500, 1000}); KPSS y ZA: 50 000 (A9)" % cfg["N_cal"],
                   "95 (trayectorias de B5 de A8)", b["exact_region_5000"]))
            w("")
        e1, e2 = b["E1_informative"], b["E2_informative"]
        w("E1 y E2 recalculados con la primaria final (informativos): E1 supera en %d de %d, con McNemar en %d (%s); E2 supera en %d de %d, con McNemar en %d (%s)." % (
            e1["wins"], e1["of"], e1["wins_with_mcnemar"], "sí" if e1["holds"] else "no", e2["wins"], e2["of"],
            e2["wins_with_mcnemar"], "sí" if e2["holds"] else "no"))
        w("")
    if have("DGP5"):
        b = J(F10["DGP5"])
        cfg = b["config"]
        w("#### 3.2 DGP 5 a n = %d con la primaria final" % cfg["n"])
        w("")
        w("Celda de calibración de A7 `%s` (N_cal = %d); umbral igualado de la primaria %s; umbrales de A7: %s; α* conjunto de A7: %s. Paso 0 de las componentes (R = 0.5) frente a A7: %s; control θ = 0.1 frente a la caché de A8: %s." % (
            b["calibration_cell"], cfg["N_cal_equalized"], f4(b["threshold_primary"]),
            ", ".join("%s %s" % (k, f4(v) if isinstance(v, float) else v) for k, v in b["a7_thresholds"].items()),
            f4(b["a7_joint_alpha_star"]) if isinstance(b["a7_joint_alpha_star"], float) else b["a7_joint_alpha_star"],
            sci(b["paso0"]["max_abs_diff_components"]),
            sci(b["control_theta01_vs_a8"]["max_abs_diff"]) if b["control_theta01_vs_a8"]["max_abs_diff"] is not None else "—"))
        w("")
        w("**Tabla B10.3.2. DGP 5: potencia a tamaño igualado y a nivel nominal (nula `hac`).**")
        w("")
        keys = ("primary", "proposed_R050", "proposed_adaptive", "union_joint", "bootstrap_dfgls")
        lab = {"primary": "primaria θ = %g" % theta(), "proposed_R050": "R = 0.5", "proposed_adaptive": "R̂",
               "union_joint": "unión conjunta", "bootstrap_dfgls": "bootstrap DF-GLS"}
        L.extend(table(["ρ", "r"] + ["%s (igualado)" % lab[k] for k in keys] + ["primaria nominal", "R = 0.5 nominal",
                                                                                 "Cuota mediana de g₂ (R = 0.5)", "McNemar p vs R = 0.5",
                                                                                 "McNemar p vs bootstrap"],
                       [[v["rho"], v["r"]] + [rr(v["size_matched"][k]) for k in keys]
                        + [rr(v["nominal_hac"]["primary_hac"]), rr(v["nominal_hac"]["r05_hac"]), f4(v["g2_share_R050_median"]),
                           mp(v["mcnemar_primary_vs_R050"]), mp(v["mcnemar_primary_vs_bootstrap"])]
                        for v in sorted(b["cells"].values(), key=lambda v: (v["rho"], v["r"]))]))
        w("")
        w(note(F10["DGP5"], cfg["N_sim"], "%d (igualado, A7) y %d (nominal de la primaria)" % (cfg["N_cal_equalized"], cfg["N_cal_nominal_primary"]),
               "60 (trayectorias de A7)", "—", "Columnas de A7 leídas de sus checkpoints (sha256 del JSON de A7 `%s`)." % b["a7_source_sha256"]))
        w("")
    if have("FIN"):
        sec_finite(w, L, F10["FIN"], J(F10["FIN"]), "B10.3.3", "3.3 B9.4 con el θ final")
    if have("AWBB"):
        bud = J(F10["AWBB"])
        w("#### 3.4 Sonda AWB con el θ final")
        w("")
        w("Presupuesto (CARO, %.0f h): %s; sondas (s/serie): %s; proyección %.2f h; dentro: %s." % (
            bud["budget_hours"], bud["rule"], ", ".join("n = %s: %.3f" % (k, v) for k, v in bud["probe_sec_per_series"].items()),
            bud["projected_total_hours"], bud["within_budget"]))
        w("")
        if have("AWB"):
            sec_awb(w, L, F10["AWB"], J(F10["AWB"]), "B10.3.4")
    if have("APP"):
        sec_app(w, L, F10["APP"], J(F10["APP"]), "B10.3.5", "3.5 Aplicación con el θ final")
    if have("CV"):
        sec_cv(w, L, F10["CV"], J(F10["CV"]), "B10.3.6", "3.6 Valores críticos con el θ final")
    if have("LOW"):
        b = J(F10["LOW"])
        cfg = b["config"]
        w("#### 3.7 Tamaño gaussiano en el dominio bajo")
        w("")
        w("**Tabla B10.3.7. Tamaño gaussiano, n ∈ %s** (N = %d por (caso, n); * = dentro de %s)." % (cfg["n"], cfg["N"], b["exact_region_50000"]))
        w("")
        cols = (cfg["primary"], cfg["reference"], "rm_t0.1", "msbhac", "adf", "dfgls", "mzt", "msb")
        L.extend(table(["Caso", "n"] + [pname(q) for q in cols] + ["IC primaria", "MSB-GLS publicado"],
                       [[CASE[v["case"]], v["n"]] + [star(v["rates"][q]) for q in cols] + [wil(v["rates"][cfg["primary"]]), star(v["msb_published_cv"])]
                        for v in b["cells"].values()]))
        w("")
        w(note(F10["LOW"], cfg["N"], cfg["N_cal"], "113 (celdas low_<caso>_n<n>, hijos distintos por caso)", b["exact_region_50000"],
               "Calibración: %s." % "; ".join("n = %s: N_cal %d, reutilizadas %d, Paso 0 %s" % (
                   k, v["N_cal"], v["reused_rows"], sci(v["paso0_max_abs_diff"]) if v["reused_rows"] else
                   "no aplica (el troceo de A9 en n = %s no divide las filas reutilizables; calibración completa nueva)" % k)
                   for k, v in b["calibration"].items())))
        w("")


def sec_finite(w, L, name, b, tag, title):
    cfg = b["config"]
    w("#### %s" % title)
    w("")
    w("Estadístico: %s. Muestra de %d réplicas a n = %d (familia 104). KS: %s (umbral %s). Calibración por n: %s." % (
        pname(cfg["statistic"]), cfg["N_big"], cfg["n_big"], cfg["ks_rule"], f4(cfg["ks_threshold"]),
        "; ".join("%s: %s" % (k, v) for k, v in cfg.get("calibration_by_n", {}).items()) or "A9 (N_cal = %d)" % E.N_CAL))
    w("")
    for case in E.CASES:
        r = b["cases"][case]
        w("**Tabla %s.ks.%s. KS frente a n = %d, caso %s.**" % (tag, case, cfg["n_big"], CASE[case]))
        w("")
        L.extend(table(["n", "D", "p", "Umbral", "¿Por debajo?"],
                       [[n, f4(v["D"]), sci(v["p_value"]), f4(v["threshold"]), v["below_threshold"]] for n, v in r["ks"].items()]))
        w("")
        w("**Tabla %s.cost.%s. Coste de aproximar, caso %s** (N = %d independientes por n; * = dentro de %s)." % (
            tag, case, CASE[case], cfg["N_indep"], b["exact_region_20000"]))
        w("")
        cs = r["approximation_cost_comparators"]
        L.extend(table(["n", "VC n = %d" % cfg["n_big"], "Tamaño", "VC en n", "Tamaño", "DF-GLS publicado", "DF-GLS sim",
                        "MSB-GLS publicado", "MSB-GLS sim"],
                       [[n, f4(v["cv_n20000"]), star(v["size_with_cv_n20000"]), f4(v["cv_at_n"]), star(v["size_with_cv_at_n"]),
                         star(cs[n]["dfgls"]["size_published_asymptotic"]), star(cs[n]["dfgls"]["size_simulated_at_n"]),
                         star(cs[n]["msb"]["size_published_asymptotic"]), star(cs[n]["msb"]["size_simulated_at_n"])]
                        for n, v in r["approximation_cost"].items()]))
        w("")
        w("**Tabla %s.mom.%s. E[stat²] por n (EE).**" % (tag, case))
        w("")
        L.extend(table(["n", "σ = 1", "σ̂_HAC"],
                       [[n, "%s (%s)" % (f4(v["E_stat2_sigma1"]), f4(v["se_sigma1"])), "%s (%s)" % (f4(v["E_stat2_hac"]), f4(v["se_hac"]))]
                        for n, v in r["moments"].items()]))
        w("")
    w(note(name, cfg["N_indep"], "véase la calibración por n", "102 (n de la rejilla) y 104 (n = %d)" % cfg["n_big"], b["exact_region_20000"],
           "Valores publicados: DF-GLS %s; MSB %s." % (cfg["published_cv"]["dfgls"], cfg["published_cv"]["msb"])))
    w("")


def sec_awb(w, L, name, b, tag):
    cfg = b["config"]
    w("Estadístico: %s; B = %d; residuos: %s; %s; p-valor: %s; semilla: %s; calibración simulada: %s." % (
        pname(cfg["statistic"]), cfg["B"], cfg["residuals"],
        "; ".join("n = %s: l = %d, γ = %.4f" % (k, v["l"], v["gamma"]) for k, v in cfg["ar_AWB"].items()), cfg["pvalue"], cfg["seed"],
        cfg.get("sim_calibration", "A9 (N_cal = %d)" % E.N_CAL)))
    w("")
    w("**Tabla %s. Calibración AWB frente a la simulada, mismas trayectorias** (* = dentro de %s)." % (tag, b["exact_region_2000"]))
    w("")
    L.extend(table(["Celda", "n", "AWB", "IC", "Simulada", "IC", "McNemar p", "Pérdida de potencia (pp)"],
                   [[label(k) if k.startswith(("garch", "heavy", "indep")) else k, v["n"], star(v["awb"]), wil(v["awb"]),
                     star(v["sim"]), wil(v["sim"]), mp(v["mcnemar_awb_vs_sim"]), pp2(v["power_loss_pp"])]
                    for k, v in b["cells"].items()]))
    w("")
    r = b["rule"]
    w("Regla (A9, REGLA B9.5): (i) %d de %d celdas de DGP 3 dentro (mínimo %d): %s; (ii) pérdida de potencia en DGP 1 %s pp (umbral %s): %s. **Recomendar AWB: %s.**" % (
        r["i_in_region_dgp3"], r["i_of"], r["i_min"], r["i_holds"], ", ".join(pp2(x) for x in r["ii_power_loss_pp"].values()),
        pp2(r["ii_threshold_pp"]), r["ii_holds"], "sí" if r["recommend_awb"] else "no"))
    w("")
    w(note(name, cfg["N_sim"], "—", cfg["seed"], b["exact_region_2000"], "Máx. |estadístico observado − fila de B9.1/B9.2| = %s." % sci(
        max(v["max_abs_diff_stat_vs_rows"] for v in b["cells"].values()))))
    w("")


def sec_app(w, L, name, b, tag, title):
    s = b["summary"]
    w("#### %s" % title)
    w("")
    w("Datos congelados verificados: %s; `experiments/protocol.md`: %s. θ = %g; variante AWB: %s. Nula: %s." % (
        "; ".join("%s %s" % (k, v["match"]) for k, v in b["data_hashes"].items()), b["protocol_hash"]["match"], b["theta"],
        b["awb_variant"], b["config"].get("null", "producción")))
    w("")
    first = next(iter(s.values()))
    w("**Tabla %s.1. Falsos positivos, detecciones y latencia** (%d celdas de control; %d de evento; α = %s)." % (
        tag, first["fp_cells"], first["event_cells"], b["config"]["alpha"]))
    w("")
    L.extend(table(["Test", "FP media", "FP máxima", "Detecciones", "Latencia media condicional (días)"],
                   [[APP.get(t, t), f4(v["fp_mean"]), f4(v["fp_max"]), "%d de %d" % (v["detections"], v["event_cells"]),
                     "%.1f" % v["mean_latency_detected"] if v["mean_latency_detected"] else "—"] for t, v in s.items()]))
    w("")
    mt = b["matched_rate"]
    w("**Tabla %s.2. A tasa de falsas alarmas igualada** (objetivo %s; tolerancia %d días; latencia censurada a %d días)." % (
        tag, f4(mt["target_fpr_pooled_primary"]), mt["gap_tolerance"], mt["censor_days"]))
    w("")
    L.extend(table(["Test", "Umbral", "Tasa alcanzada", "Episodios", "Racha media (días)", "Latencia censurada (días)"],
                   [[APP.get(t, t), "%.6f" % v["threshold"], f4(v["achieved_fpr"]), v["false_alarm_episodes"],
                     "%.1f" % v["mean_run_length"], "%.1f" % v["censored_latency_mean"]] for t, v in mt["tests"].items()]))
    w("")
    adv = b["adverse_cells_primary"]
    w("Celdas adversas bajo la regla pre-registrada (primaria final frente a %s): %d de %d." % (
        b["config"]["prereg_baselines_for_adverse_rule"], len(adv), s["final"]["fp_cells"]))
    w("")
    oo, oa = b["oos_size"], b["oos_size_awb"]
    w("**Tabla %s.3. Tamaño fuera de muestra por D** (N = %d; región %s)." % (tag, oo["N"], oo["region"]))
    w("")
    L.extend(table(["D", "Primaria simulada", "IC"] + (["AWB", "IC"] if oa else []),
                   [[d, star(v), wil(v)] + ([star(oa["by_D"][d]), wil(oa["by_D"][d])] if oa else []) for d, v in oo["by_D"].items()]))
    w("")
    w("**Tabla %s.4. Filas nuevas de la tabla de desviaciones del registro.**" % tag)
    w("")
    L.extend(table(["Id", "Auditoría", "Elemento", "Pre-registrado / anterior", "Desplegado", "Efecto antes", "Efecto después"],
                   [[r["id"], r["audit"], r["element"], r["preregistered_value"], r["deployed_value"],
                     fmt_effect(r["effect_before"]), fmt_effect(r["effect_after"])] for r in b["deviation_rows"]]))
    w("")
    w(note(name, oo["N"], b["config"]["N_cal"], "%s (caminos fuera de muestra); remuestreo AWB %s" % (
        oo.get("family_paths", oo.get("family")), (oa or {}).get("family_resampling", "—")), oo["region"],
        "Comparadores: %s." % b["config"]["comparators"]))
    w("")


def sec_cv(w, L, name, b, tag, title):
    cfg = b["config"]
    tp = b["primary_theta"]
    w("#### %s" % title)
    w("")
    w("CSV: `%s` (sha256 `%s`); N_cal = %d por (caso, n); calibración %s; anclaje %s; EE del cuantil por bootstrap (%d remuestreos). Máx. |valor − tabla de A9| = %s." % (
        b["csv"], b["csv_sha256"], cfg["N_cal"], cfg["calibration"], cfg["anchor"], cfg["bootstrap_se"],
        sci(b.get("max_abs_diff_vs_a9_table", float("nan")))))
    w("")
    w("**Tabla %s.1. Valores críticos del θ final (θ = %g) y EE.**" % (tag, tp))
    w("")
    L.extend(table(["Caso", "n"] + ["α = %g" % a for a in cfg["alphas"]],
                   [[CASE[case], n] + ["%s (%s)" % (f4(b["table"]["%s|%g|%d" % (case, tp, n)]["cv"]["%g" % a]),
                                                    f4(b["table"]["%s|%g|%d" % (case, tp, n)]["se"]["%g" % a])) for a in cfg["alphas"]]
                    for case in ("dm", "ct") for n in cfg["n"]]))
    w("")
    w("**Tabla %s.2. Sensibilidad: valor crítico al 5%% por θ.**" % tag)
    w("")
    L.extend(table(["Caso", "n"] + ["θ = %g" % t for t in cfg["thetas"]],
                   [[CASE[case], n] + [f4(b["table"]["%s|%g|%d" % (case, t, n)]["cv"]["0.05"]) for t in cfg["thetas"]]
                    for case in ("dm", "ct") for n in cfg["n"]]))
    w("")
    au = b["cross_seed_audit"]
    w("Auditoría de semilla cruzada (%s; %d celdas): desviación máxima %s (%.1f EE). Por celda: %s." % (
        au["ranking"], len(au["cells"]), f4(au["max_abs_deviation"]), au["max_abs_deviation_in_se"],
        "; ".join("%s: %s (%.1f EE; %s)" % (k, f4(v["max_abs_deviation"]), v["max_abs_deviation_in_se"], v.get("source", "A9"))
                  for k, v in au["by_cell"].items())))
    w("")
    w(note(name, "—", cfg["N_cal"], "107 (tabla); cruzada: 107 o 113", "—"))
    w("")


# ---------------------------------------------------------------------------
# B10.4 y B10.5
# ---------------------------------------------------------------------------
PREV_LABEL = {"b97_cv": "B9.7, tabla (familia 107)", "b97_cvx": "B9.7, auditoría cruzada (familia 107)",
              "a9_seed42": "A9, semilla 42 (N_cal = 50 000)", "a8_b7": "B7 de A8 (familia 97)"}


def sec_b104(w, L):
    b = J(F10["B10.4"])
    cfg = b["config"]
    w("### B10.4 — %s" % TITLES["B10.4"])
    w("")
    w("Celda: %s, n = %d, α = %s, RM-GLS θ ∈ %s, calibración %s; %d réplicas independientes de N_cal = %d (familia 114). Regla: %s." % (
        CASE[cfg["case"]], cfg["n"], cfg["alpha"], cfg["thetas"], cfg["calibration"], cfg["replicas"], cfg["N_cal"], cfg["rule"]))
    w("")
    for t, v in b["by_theta"].items():
        w("**Tabla B10.4.θ%s. θ = %s: las cinco réplicas.**" % (t, t))
        w("")
        L.extend(table(list(v["replicas"]) + ["Media", "DT", "Mín.", "Máx."],
                       [[f4(x) for x in v["replicas"].values()] + [f4(v["mean"]), f4(v["sd"]), f4(v["min"]), f4(v["max"])]]))
        w("")
        L.extend(table(["Valor previo", "Valor", "N_cal", "¿En [mín., máx.]?", "Desviación (DT de las réplicas)", "Consistente", "Fuente"],
                       [[PREV_LABEL[k], f4(p["value"]), p.get("N_cal", "—"), p["in_range"], "%+.1f" % p["dev_in_sd"], p["consistent"],
                         "`%s` (%s)" % (p["source"], p["path"])] for k, p in v["previous"].items()]))
        w("")
    w("**Anomalía de B9.7 a n = 5000: %s.**" % ("cerrada" if b["anomaly_closed"] else "abierta"))
    w("")
    w(note(F10["B10.4"], "—", cfg["N_cal"], "114 (celdas cv5000_r<k>)", "—"))
    w("")


def sec_b105(w, L):
    w("### B10.5 — %s" % TITLES["B10.5"])
    w("")
    if not have("FIG"):
        w("Figuras no generadas (§5).")
        w("")
        return
    f = J(F10["FIG"])
    if f["a9_figures_remain_valid"]:
        w("θ final = %g: las cinco figuras de A9 siguen vigentes (`figures_audit9.json`): %s. Solo se genera la figura nueva." % (
            f["primary_theta"], ", ".join("%s (`%s`)" % (k, v["sha256"]) for k, v in f["a9_figures"].items())))
    else:
        w("θ final = %g: las cinco figuras se regeneran con sufijo `_audit10`." % f["primary_theta"])
    w("")
    w("**Tabla B10.5.1. Figuras** (generador `experiments/make_figures_audit10.py`; fuentes: %s)." % ", ".join("`%s`" % s for s in f["sources"]))
    w("")
    L.extend(table(["Figura", "sha256", "Bytes", "Copia", "sha256 de la copia"],
                   [[k, "`%s`" % v["sha256"], v["bytes"], v["paper_copy"], "`%s`" % v["paper_copy_sha256"]] for k, v in f["figures"].items()]))
    w("")
    w("**Tabla B10.5.2. Puntos de `fig_calibration_gain_audit10.pdf`** (tamaño; * = dentro de la región exacta de la N del punto).")
    w("")
    rows = []
    for case, pts in f["calibration_gain_points"].items():
        for n in pts["cv_at_n"]:
            a, bb, c = pts["cv_at_n"][n], pts["cv_big"][n], pts["msb_pub"][n]

            def s(x):
                return "%s%s" % (f4(x["rate"]), "*" if x["region"][0] <= x["rate"] <= x["region"][1] else "")
            rows.append([CASE[case], n, a["N"], s(a), s(bb), s(c), "`%s`" % os.path.basename(a["source"]), "`%s`" % os.path.basename(bb["source"])])
    L.extend(table(["Caso", "n", "N", "Primaria, VC en n", "Primaria, VC de n = 20 000", "MSB-GLS publicado", "Fuente (VC en n, MSB)",
                    "Fuente (VC n = 20 000)"], rows))
    w("")


# ---------------------------------------------------------------------------
# Compuertas, procedencia, desviaciones, no ejecutado
# ---------------------------------------------------------------------------
def gates(L):
    rows = []
    pr = J(F10["PROBE"])
    rows.append(["Tiempo de calibración a n = %d (lectura 4)" % pr["n"], "si a n = 1000 supera 20 minutos por configuración, detente y reporta",
                 "peor %s: %.1f min" % (pr["worst_configuration"], pr["worst_minutes"]), "dentro" if pr["within_gate"] else "EXCEDE",
                 "Rejilla lanzada" if pr["within_gate"] else "Detiene"])
    if have("B10.1"):
        b = J(F10["B10.1"])
        dec = b["decision"]
        rows.append(["Regla B10.1 (DURA)", protocol_text("### REGLA B10.1 (DURA)"),
                     "; ".join("θ = %s: A1′ %s, A2 %s, P %s" % (t.replace("gls_t", ""), b["A1prime_ok"][t], b["reused_from_a9"]["A2_ok"][t],
                                                              f4(b["reused_from_a9"]["P"][t])) for t in THETA_KEYS),
                     "θ = %s" % ("—" if dec["winner"] is None else "%g" % dec["winner_theta"]),
                     "Detiene" if b["gate_stop"] else "Continuar"])
    if have("B10.2"):
        b = J(F10["B10.2"])
        rows.append(["Identidad B10.2", "peor diferencia relativa ≤ %s" % sci(b["config"]["threshold"]),
                     "(i) %s; (ii) %s" % (sci(b["worst_i"]), sci(b["worst_ii"])), verdict(b["pass"]), "—"])
    if have("B10.1"):
        rows.append(["Condición B10.3", protocol_text("### CONDICIÓN B10.3"), "θ final = %g" % theta(),
                     "se ejecuta" if b103_ran() else "no se ejecuta", "—"])
    if have("AWBB"):
        bud = J(F10["AWBB"])
        rows.append(["Presupuesto de B10.3.4 (CARO, %.0f h)" % bud["budget_hours"], bud["rule"], "%.2f h" % bud["projected_total_hours"],
                     "dentro" if bud["within_budget"] else "EXCEDE", "Ejecutado" if bud["within_budget"] else "No se lanza"])
    if have("AWB"):
        r = J(F10["AWB"])["rule"]
        rows.append(["Regla AWB (INFORMATIVA, la de B9.5)", "(i) ≥ %d de %d celdas de DGP 3 dentro; (ii) pérdida ≤ %s pp en DGP 1" % (
            r["i_min"], r["i_of"], pp2(r["ii_threshold_pp"])),
                     "(i) %d; (ii) máx. %s pp" % (r["i_in_region_dgp3"], pp2(max(r["ii_power_loss_pp"].values()))),
                     "recomendar AWB: %s" % ("sí" if r["recommend_awb"] else "no"), "No detiene"])
    if have("B10.4"):
        b = J(F10["B10.4"])
        rows.append(["Cierre de la anomalía a n = 5000 (lectura 11)", b["config"]["rule"],
                     "; ".join("θ = %s: %s" % (t, ", ".join("%s %s" % (k, "✓" if p["consistent"] else "✗") for k, p in v["previous"].items()))
                               for t, v in b["by_theta"].items()),
                     "cerrada" if b["anomaly_closed"] else "abierta", "—"])
    L.extend(table(["Compuerta", "Criterio (literal del protocolo)", "Medido", "Veredicto", "Acción"], rows))


def paso0_rows():
    rows = []
    if have("B10.1"):
        b = J(F10["B10.1"])
        rows.append(["B10.1", "calibración: primeras 50 filas recalculadas frente a `audit9_cal` (filas reutilizadas)",
                     sci(max(v["paso0_max_abs_diff"] for v in b["calibration"].values()))])
        rows.append(["B10.1", "calibración: RM-GLS θ = 0.1 y θ = 0 (`hac`) frente a `_simulate_null_statistics` de producción (N_cal = 500 000)",
                     sci(max(v for c in b["production_control"].values() for v in c.values()))])
    if have("EQ"):
        rows.append(["B10.3.1", "trayectorias de B5 de A8: columnas comunes con los checkpoints de A8", sci(J(F10["EQ"])["paso0_worst"])])
    if have("DGP5"):
        b = J(F10["DGP5"])
        rows.append(["B10.3.2", "componentes g₁/g₂ (R = 0.5) frente a los checkpoints de A7", sci(b["paso0"]["max_abs_diff_components"])])
        if b["control_theta01_vs_a8"]["max_abs_diff"] is not None:
            rows.append(["B10.3.2", "RM-GLS θ = 0.1 recalculado frente a la caché de A8", sci(b["control_theta01_vs_a8"]["max_abs_diff"])])
    if have("AWB"):
        rows.append(["B10.3.4", "estadístico observado frente a las filas de B9.1/B9.2",
                     sci(max(v["max_abs_diff_stat_vs_rows"] for v in J(F10["AWB"])["cells"].values()))])
    if have("CV"):
        rows.append(["B10.3.6", "tabla de valores críticos frente a la de A9", sci(J(F10["CV"])["max_abs_diff_vs_a9_table"])])
    return rows


def provenance_section(w, L):
    man = J("manifest_audit10.json")
    w("**Archivos que alimentan las tablas** (`manifest_audit10.json`; el propio reporte se registra después de escribirse).")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "mtime (UTC)", "Script", "Commit", "Código commiteado"],
                   [[k, "`%s`" % e["sha256"], e["bytes"], e["mtime_utc"], e["script"], e["commit"][:7], e["code_all_committed"]]
                    for k, e in sorted(man["entries"].items()) if not k.endswith("resultados_auditoria_10.md")]))
    w("")
    npz = sorted(glob.glob(os.path.join(C.CKPT_ROOT, "audit10_cal", "cal_n*.npz")))
    w("Muestras de calibración de A10 (npz, no se commitean; se regeneran bit a bit desde la semilla 42 de producción):")
    w("")
    L.extend(table(["Archivo", "sha256"], [[C.rel(p), "`%s`" % C.sha256_file(p)] for p in npz]))
    w("")
    import audit10_b100_protocol as B100
    dirs = [d for d in ("audit10_b101", "audit10_b103", "audit10_b103_awb", "audit10_b103_app", "audit10_b103_cv", "audit10_b104")
            if os.path.isdir(os.path.join(C.CKPT_ROOT, d))]
    w("Carpetas de checkpoints de A10 (no se commitean por tamaño; se regeneran bit a bit desde sus semillas):")
    w("")
    L.extend(table(["Carpeta", "Archivos", "Bytes", "sha256 agregado"],
                   [[d, r["files"], r["bytes"], "`%s`" % r["aggregate_sha256"]] for d, r in ((d, B100.ckpt_record(d)) for d in dirs)]))
    w("")
    w("**Paso 0 y controles.**")
    w("")
    L.extend(table(["Bloque", "Qué se compara", "Peor máx. |Δ|"], paso0_rows()))
    w("")
    py = pytest_summary()
    if py is not None:
        c = py["counts"]
        w("- Suite completa (`pytest_audit10.log`): collected %s; passed %d; failed %d; skipped %d; %.1f s." % (
            py["collected"], c.get("passed", 0), c.get("failed", 0), c.get("skipped", 0), py["seconds"]))
        w("- Test de literales (`tests/test_no_literals_audit10.py`): %s." % ("; ".join("%s %s" % t for t in py["literals"])))
        w("")


def deviations():
    rows = [
        ["Configuración = (procedimiento, caso) en la compuerta de 20 min; su tiempo = coste por camino de sus componentes × N_cal / núcleos",
         "El encargo no define «configuración» ni cómo se mide su tiempo", "antes", "Tabla B10.1.t"],
        ["La primera sonda de tiempo no calentaba las rutinas (importación de `arch` y compilación dentro del cronómetro); se repitió con calentamiento y la primera queda como registro (`b101_timing_coldstart_audit10.json`)",
         "Error de medición: c|DF-GLS salía a 110 ms por camino frente a 1.4 ms en régimen", "antes de lanzar la rejilla",
         "La sonda en frío superaba la compuerta; la vigente no (Tabla B10.1.t)"],
        ["Las muestras de B10.1 evalúan los 12 procedimientos sobre las mismas trayectorias de cada (caso, n, muestra)",
         "Lectura de «por (θ o comparador, caso, n)»: la tabla compara procedimientos sobre la misma muestra (lectura 2)", "antes", "—"],
        ["Calibración compartida por los dos casos y por todos los procedimientos (caminos de producción, semilla 42); las primeras 50 000 filas son las de A9",
         "La nula de producción es la de la semilla 42; la independencia entre casos del encargo se refiere a las muestras de tamaño (lectura 3)",
         "antes", "Paso 0 y control de producción en §3"],
        ["Checkpoints y muestras npz de A10 sin commitear", "Tamaño", "después", "sha256 agregado en §3"],
    ]
    if have("CV"):
        rows.append(["B10.3.6 falló en la cadena al escribir el JSON (error de tipo en la desviación en EE); se corrigió el script, se commiteó y se reejecutó aparte (`--cores 2`, en paralelo con B10.3.5), reutilizando las filas nuevas ya escritas en `audit10_b103_cv`",
                     "Error de programación en el cálculo de la auditoría cruzada", "después de ver B10.3.1–3.3",
                     "Ninguno sobre valores: las filas son deterministas por índice; el log del primer intento es `logs_audit10/b103_cv_first_attempt_audit10.log`"])
    if have("FIG"):
        rows.append(["`fig_calibration_gain_audit10.pdf` se regeneró tras la suite para quitar las marcas menores del eje logarítmico y girar las etiquetas (se solapaban 150 y 200); las seis figuras se reescribieron (el PDF incluye la fecha de creación, así que cambia su sha256)",
                     "Legibilidad", "después", "Ninguno sobre los datos; sha256 vigentes en la Tabla B10.5.1; la suite (`pytest_audit10.log`) es anterior a ese cambio de maquetación"])
    if have("B10.1"):
        b = J(F10["B10.1"])
        pr = J(F10["PROBE"])
        real = b["calibration"]["1000"]["wall_new_sec"] / 60
        rows.append(["El tiempo real de pared de la calibración a n = 1000 (%.1f min para %d filas nuevas, todas las configuraciones) supera la proyección de la sonda (%.1f min para N_cal completo)" % (
            real, b["calibration"]["1000"]["N_cal"] - b["calibration"]["1000"]["reused_rows"], pr["projected_minutes_all_configurations_n1000"]),
                     "La sonda mide el coste por camino en un proceso por núcleo; la ejecución real pierde eficiencia paralela", "durante B10.1",
                     "Ninguno sobre valores; la compuerta se evaluó con la sonda, como fija la lectura 4"])
    if b103_ran():
        rows += [
            ["B10.3: cada subbloque con su propio tope de 4 h; 3.4 (AWB) CARO con 8 h", "B10.3 agrupa siete experimentos", "antes de ver B10.1", "—"],
            ["B10.3.1: KPSS y ZA simulados con la calibración de A9 (N_cal = 50 000)", "La calibración de 500 000 no incluye esas columnas", "antes de ver B10.1",
             "Solo afecta a las columnas KPSS-sim y ZA-sim"],
            ["B10.3.5: nula de la aplicación = la de producción (semilla 42, N_cal = 50 000) calibrada a n = D − 1, como B9.6",
             "La aplicación usa `build_null_cdf` de producción; B10.1 no cubre n = D − 1", "antes de ver B10.1", "—"],
            ["B10.3.2: R = 0.5 nominal con la nula `hac` de A8", "Columna de A7/A8; solo la primaria se recalcula", "antes de ver B10.1", "—"],
        ]
    return rows


def not_executed():
    rows = []
    for key, lab in (("B10.1", "B10.1"), ("B10.2", "B10.2"), ("B10.4", "B10.4"), ("FIG", "B10.5")):
        if not have(key):
            rows.append([lab, "Sin JSON de resultados", "`python %s`" % SCRIPTS[key]])
    if have("B10.1") and not b103_ran():
        rows.append(["B10.3 completo", "θ final = %g: la condición de B10.3 no se cumple; todo lo de A9 sigue vigente y no se recalcula" % theta(), "—"])
    elif b103_ran():
        for key, lab in (("EQ", "3.1"), ("DGP5", "3.2"), ("FIN", "3.3"), ("AWB", "3.4"), ("APP", "3.5"), ("CV", "3.6"), ("LOW", "3.7")):
            if not have(key):
                rows.append(["B10.3.%s" % lab, "Sin JSON de resultados", "`python %s`" % SCRIPTS[key]])
    rows.append(["MZ_α y MP_T como comparadores", "Retirados en A8 (enmienda 1)", "—"])
    return rows


# ---------------------------------------------------------------------------
# Conclusiones, anomalias, frases
# ---------------------------------------------------------------------------
def dgp3_sim_rate(p):
    if have("EQ"):
        v = J(F10["EQ"])["cells"]["dgp3_r4_n200"]["rates_sim"][p]
        return v, F10["EQ"]
    return J(F9["B92"])["dgp3"]["dgp3_r4_n200"]["rates"][p], F9["B92"]


def conclusions(w):
    b = J(F10["B10.1"])
    p = prim()
    b92 = J(F9["B92"])
    i = [0]

    def item(text):
        i[0] += 1
        w("%d. %s" % (i[0], text))
    dec = b["decision"]
    item("**θ final: %g** (Tabla B10.1.rule): admisibles %s; P(θ) (A9): %s; grupo de empate %s." % (
        theta(), [pname(t) for t in dec["admissible"]],
        ", ".join("θ = %s: %s" % (t.replace("gls_t", ""), f4(v)) for t, v in b["reused_from_a9"]["P"].items()),
        [pname(t) for t in dec["tie_group"]]))
    item("**Tamaño agregado de la primaria en las seis celdas de A1′** (N = %d; Tablas B10.1.A1′): %s." % (
        b["config"]["N_pooled"], "; ".join("%s n = %s: %s %s" % (CASE[k.split("|")[0]], k.split("|")[1], f4(v["rate"]), wil(v))
                                           for k, v in b["A1prime"][p].items())))
    lp = b92["local_power"]
    item("**Brecha a la envolvente (pp) en c = 5, 10 y 20** (`%s`, Tablas B9.2.lp de A9): %s." % (F9["B92"], "; ".join(
        "%s — %s" % (CASE[case], ", ".join("%s %s" % (pname(q), "/".join(pp1(lp[case]["gap_to_envelope"][q][c] * 100) for c in GAP_C))
                                           for q in (p, "dfgls", "msb")))
        for case in ("dm", "ct"))))
    an, ab = src_awb()
    r = ab["rule"]
    item("**Regla AWB** (`%s`): (i) %d de %d celdas de DGP 3 dentro; (ii) pérdida máx. %s pp; recomendar AWB: **%s**." % (
        an, r["i_in_region_dgp3"], r["i_of"], pp2(max(r["ii_power_loss_pp"].values())), "sí" if r["recommend_awb"] else "no"))
    sv, sn = dgp3_sim_rate(p)
    c4 = ab["cells"]["dgp3_r4_n200"]
    item("**DGP 3, r = 4, n = 200**: primaria con calibración simulada %s %s (`%s`); con calibración AWB %s %s (`%s`, estadístico %s)." % (
        f4(sv["rate"]), wil(sv), sn, f4(c4["awb"]["rate"]), wil(c4["awb"]), an, pname(ab["config"]["statistic"])))
    fn, fb = src_fin()
    rows = []
    for case in E.CASES:
        v = fb["cases"][case]["approximation_cost"]["200"]
        cs = fb["cases"][case]["approximation_cost_comparators"]["200"]
        rows.append("%s — primaria %s (VC de n = %d) frente a %s (VC en n); DF-GLS %s (publicado) frente a %s (simulado); MSB-GLS %s frente a %s" % (
            CASE[case], f4(v["size_with_cv_n20000"]["rate"]), D9.N_BIG_N, f4(v["size_with_cv_at_n"]["rate"]),
            f4(cs["dfgls"]["size_published_asymptotic"]["rate"]), f4(cs["dfgls"]["size_simulated_at_n"]["rate"]),
            f4(cs["msb"]["size_published_asymptotic"]["rate"]), f4(cs["msb"]["size_simulated_at_n"]["rate"])))
    item("**Coste de aproximar a n = 200** (`%s`, estadístico %s): %s." % (fn, pname(fb["config"]["statistic"]), "; ".join(rows)))
    pn, pb = src_app()
    s = pb["summary"]
    item("**Aplicación** (`%s`, θ = %g): %s; a tasa igualada (objetivo %s) la primaria final tiene %d episodios de falsa alarma; celdas adversas %d; tamaño fuera de muestra %s." % (
        pn, pb["theta"], "; ".join("%s FP media %s (máx. %s), %d detecciones de %d" % (
            APP[t], f4(s[t]["fp_mean"]), f4(s[t]["fp_max"]), s[t]["detections"], s[t]["event_cells"]) for t in ("final", "final_awb", "rhat_prereg") if t in s),
        f4(pb["matched_rate"]["target_fpr_pooled_primary"]), pb["matched_rate"]["tests"]["final"]["false_alarm_episodes"],
        len(pb["adverse_cells_primary"]), ", ".join("D = %s: %s" % (d, star(v)) for d, v in pb["oos_size"]["by_D"].items())))
    if have("B10.2"):
        b2 = J(F10["B10.2"])
        item("**Identidad con θ = 0** (Tabla B10.2.1): peor diferencia relativa (i) %s, (ii) %s; %s." % (
            sci(b2["worst_i"]), sci(b2["worst_ii"]), "PASA" if b2["pass"] else "FALLA"))


def anomalies():
    out = []
    if have("B10.1"):
        an = J(F10["B10.1"])["anomaly_ct200"]
        out.append("**Celda tendencia, n = 200 (abierta en A9).** Con muestras independientes por caso, N = %d por procedimiento y N_cal = %d: %d de %d procedimientos por debajo de %s (%s); en A9, %d de %d. El patrón %s. Tasas agregadas: %s." % (
            J(F10["B10.1"])["config"]["N_pooled"], J(F10["B10.1"])["config"]["N_cal"], an["count_below"], an["procedures"], an["mark"],
            [pname(p) for p in an["below_mark"]] or "ninguno", an["a9_count_below"], len(an["a9_rates_same_cell"]),
            "se repite" if an["pattern_repeats"] else "no se repite",
            ", ".join("%s %s" % (pname(p), f4(v["pooled"])) for p, v in an["rates"].items())))
    if have("B10.4"):
        b = J(F10["B10.4"])
        out.append("**Valor crítico a n = 5000 (abierta en A9).** %s. Anomalía **%s**; no se atribuye causa." % (
            "; ".join("θ = %s: réplicas %s (media %s, DT %s); valores previos: %s" % (
                t, ", ".join(f4(x) for x in v["replicas"].values()), f4(v["mean"]), f4(v["sd"]),
                ", ".join("%s %s (%+.1f DT, %s)" % (PREV_LABEL[k], f4(p["value"]), p["dev_in_sd"], "consistente" if p["consistent"] else "no consistente")
                          for k, p in v["previous"].items())) for t, v in b["by_theta"].items()),
            "cerrada" if b["anomaly_closed"] else "abierta"))
    if have("B10.4"):
        b = J(F10["B10.4"])
        b97 = J(F9["B97"])["table"]
        out.append("**Dispersión entre semillas frente al EE bootstrap de B9.7 (demeaned, n = %d, α = 0.05).** %s. Se registra el cociente; no se atribuye causa." % (
            b["config"]["n"], "; ".join("θ = %s: DT de las %d réplicas %s, EE bootstrap de B9.7 %s (cociente %.2f)" % (
                t, len(v["replicas"]), f4(v["sd"]), f4(b97["dm|%s|%d" % (t, b["config"]["n"])]["se"]["0.05"]),
                v["sd"] / b97["dm|%s|%d" % (t, b["config"]["n"])]["se"]["0.05"]) for t, v in b["by_theta"].items())))
    if have("CV"):
        au = J(F10["CV"])["cross_seed_audit"]
        big = [(k, v) for k, v in au["by_cell"].items() if v["max_abs_deviation_in_se"] > 3]
        out.append("**Auditoría de semilla cruzada con el θ final (B10.3.6)**: máx. desviación %s = %.1f EE bootstrap; celdas por encima de 3 EE: %s. No se atribuye causa; es la misma celda (demeaned, n = 5000) que B10.4 examina para θ = 0.1 y 0.2." % (
            f4(au["max_abs_deviation"]), au["max_abs_deviation_in_se"],
            "; ".join("%s (%s, %.1f EE; fuente %s)" % (k, f4(v["max_abs_deviation"]), v["max_abs_deviation_in_se"], v["source"]) for k, v in big) or "ninguna"))
    if have("AWB"):
        ab = J(F10["AWB"])
        r = ab["rule"]
        d1 = {k: v for k, v in ab["cells"].items() if k.startswith("dgp1_")}
        out.append("**Regla AWB en el borde.** (i) %d de %d celdas de DGP 3 dentro de la región, con mínimo %d; (ii) la mayor pérdida de potencia es %s pp frente al umbral %s pp: %s (en rechazos: %s). La regla se cumple con igualdad en los dos términos; «a lo sumo» incluye la igualdad." % (
            r["i_in_region_dgp3"], r["i_of"], r["i_min"], pp2(max(r["ii_power_loss_pp"].values())), pp2(r["ii_threshold_pp"]),
            max(r["ii_power_loss_pp"], key=r["ii_power_loss_pp"].get),
            "; ".join("%s: simulada %d, AWB %d de %d" % (k, v["sim"]["rejections"], v["awb"]["rejections"], v["sim"]["n"]) for k, v in d1.items())))
    if have("AWBB") and have("AWB"):
        bud = J(F10["AWBB"])
        log = T("logs_audit10/b103_awb_run_audit10.log")
        m = re.findall(r"bloque: ([0-9.]+) h", log)
        out.append("**Proyección de presupuesto de la sonda AWB frente al tiempo real**: proyección %.2f h (sondas de %s s/serie, que incluyen el arranque de los procesos) frente a %s h reales (`logs_audit10/b103_awb_run_audit10.log`)." % (
            bud["projected_total_hours"], ", ".join("%.3f" % v for v in bud["probe_sec_per_series"].values()), m[-1] if m else "—"))
    if have("B10.1"):
        b = J(F10["B10.1"])
        fails = ["%s %s (%s)" % (pname(t), k, f4(v["rate"])) for t in THETA_KEYS for k, v in b["A1prime"][t].items() if not v["within_tolerance"]]
        out.append("**Celdas de A1′ fuera de la tolerancia (θ)**: %s." % ("; ".join(fails) or "ninguna"))
        outr = ["%s %s (%s)" % (pname(t), k, f4(v["rate"])) for t in THETA_KEYS for k, v in b["A1prime"][t].items() if not v["in_region"]]
        out.append("**Celdas de A1′ fuera de la región exacta de N = %d (informativo)**: %s." % (b["config"]["N_pooled"], "; ".join(outr) or "ninguna"))
    return out


def claim_status(c):
    k = c["key"]
    p = prim()
    b92 = J(F9["B92"])
    if k in ("dominance_intro", "dominance_dgp1"):
        src, cells = (F10["EQ"], {kk: v for kk, v in J(F10["EQ"])["cells"].items() if kk.startswith("dgp1_")}) if have("EQ") else \
            (F9["B91"], {kk: v for kk, v in J(F9["B91"])["cells"].items() if kk.startswith("dgp1_")})
        d_asy = [(v["rates_sim"][p]["rate"] - v["rates_asy"]["adf"]["rate"]) * 100 for v in cells.values()]
        d_sim = [(v["rates_sim"][p]["rate"] - v["rates_sim"]["adf"]["rate"]) * 100 for v in cells.values()]
        v = cells["dgp1_rho0p99_n1000"]
        return "con la primaria %s en las %d celdas de DGP 1: ventaja sobre ADF asintótico de %s a %s pp; sobre ADF simulado de %s a %s pp; en (0.99, 1000): %s (asy) y %s (sim) pp (`%s`)" % (
            pname(p), len(cells), pp1(min(d_asy)), pp1(max(d_asy)), pp1(min(d_sim)), pp1(max(d_sim)),
            pp1((v["rates_sim"][p]["rate"] - v["rates_asy"]["adf"]["rate"]) * 100),
            pp1((v["rates_sim"][p]["rate"] - v["rates_sim"]["adf"]["rate"]) * 100), src)
    if k == "garch_11":
        g = [v for v in b92["misspec"].values() if v["kind"] == "garch" and v["case"] == "c"]
        return "con la primaria %s (demeaned) %d de %d GARCH dentro de la región de N = %d; ADF asy %d, PP asy %d, ADF sim %d (`%s`, misspec)" % (
            pname(p), sum(v["rates"][p]["in_region"] for v in g), len(g), D9.N_SIM, sum(v["rates"]["adf_asy"]["in_region"] for v in g),
            sum(v["rates"]["pp_asy"]["in_region"] for v in g), sum(v["rates"]["adf"]["in_region"] for v in g), F9["B92"])
    if k in ("exact_intro", "exact_p1"):
        b = J(F10["B10.1"])
        fn, fb = src_fin()
        v = fb["cases"]["c"]["approximation_cost"]["200"]
        a1 = b["A1prime"][p]
        g = [x for x in b92["misspec"].values() if x["case"] == "c"]
        return "con la primaria %s y N = %d por celda: |tamaño − 0.05| ≤ %s en %d de %d celdas (caso, n ∈ {200, 500, 1000}); máx. |tamaño − 0.05| = %s; en la mala especificación demeaned %d de %d celdas dentro de la región de N = %d (`%s`); a n = 200 con el valor crítico de n = %d el tamaño es %s (`%s`)" % (
            pname(p), b["config"]["N_pooled"], b["config"]["tolerance"], sum(x["within_tolerance"] for x in a1.values()), len(a1),
            f4(max(x["abs_dev_from_alpha"] for x in a1.values())), sum(x["rates"][p]["in_region"] for x in g), len(g), D9.N_SIM, F9["B92"],
            D9.N_BIG_N, f4(v["size_with_cv_n20000"]["rate"]), fn)
    if k == "trend_size":
        b = J(F10["B10.1"])
        return "con la primaria %s, tendencia, N = %d independientes por n: %s (`%s`)" % (
            pname(p), b["config"]["N_pooled"], ", ".join("n = %d: %s %s" % (n, f4(b["A1prime"][p]["ct|%d" % n]["rate"]), wil(b["A1prime"][p]["ct|%d" % n]))
                                                       for n in D.A1_N), F10["B10.1"])
    if k in ("fp_028", "detections_13"):
        pn, pb = src_app()
        s = pb["summary"]
        if k == "fp_028":
            return "R̂ publicado: FP media %s; primaria final (θ = %g): %s (simulada)%s (`%s`)" % (
                f4(s["rhat_prereg"]["fp_mean"]), pb["theta"], f4(s["final"]["fp_mean"]),
                " y %s (AWB)" % f4(s["final_awb"]["fp_mean"]) if "final_awb" in s else "", pn)
        return "R̂ publicado: %d de %d; primaria final (θ = %g): %d (simulada)%s (`%s`)" % (
            s["rhat_prereg"]["detections"], s["rhat_prereg"]["event_cells"], pb["theta"], s["final"]["detections"],
            " y %d (AWB)" % s["final_awb"]["detections"] if "final_awb" in s else "", pn)
    return "no evaluada"


# ---------------------------------------------------------------------------
# Tabla maestra
# ---------------------------------------------------------------------------
def master():
    """(clave, valor, IC o EE, N_sim, N_cal, familia, archivo JSON, ruta)."""
    out = []
    p = prim()
    b = J(F10["B10.1"])
    b92 = J(F9["B92"])
    cal92 = b92["config"]["N_cal"]
    out.append(("theta_final", "%g" % theta(), "—", "—", "—", "—", F10["B10.1"], "primary_theta"))
    for t in THETA_KEYS:
        out.append(("A1prime_ok|%s" % t, str(b["A1prime_ok"][t]), "—", b["config"]["N_pooled"], b["config"]["N_cal"], 111, F10["B10.1"],
                    "A1prime_ok.%s" % t))
        out.append(("P_theta|%s" % t, f4(b["reused_from_a9"]["P"][t]), "—", b92["config"]["N_power"], cal92, 102, F9["B92"], "theta_rule.P.%s" % t))
    # tamano gaussiano por n y caso
    low = J(F10["LOW"]) if have("LOW") else None
    for case, det in (("dm", "c"), ("ct", "ct")):
        for n in D9.N_ALL:
            k = "%s|%d" % (case, n)
            if k in b["A1prime"][p]:
                r = b["A1prime"][p][k]
                out.append(("size_gauss|%s|n%d" % (case, n), f4(r["rate"]), wil(r), r["n"], b["config"]["N_cal"], 111, F10["B10.1"],
                            "A1prime.%s.%s" % (p, k)))
            elif low is not None and k in low["cells"]:
                r = low["cells"][k]["rates"][p]
                out.append(("size_gauss|%s|n%d" % (case, n), f4(r["rate"]), wil(r), r["n"], low["config"]["N_cal"], 113, F10["LOW"],
                            "cells.%s.rates.%s" % (k, p)))
            else:
                r = b92["gaussian_size"]["%s|%d" % (det, n)][p]
                out.append(("size_gauss|%s|n%d" % (case, n), f4(r["rate"]), wil(r), r["n"], cal92, 102, F9["B92"],
                            "gaussian_size.%s|%d.%s" % (det, n, p)))
    # mala especificacion
    for key, v in b92["misspec"].items():
        r, d = v["rates"][p], v["delta_vs_independent"][p]
        out.append(("misspec|%s" % key, f4(r["rate"]), "Δ %s pp (EE %s)" % (pp2(d["delta"] * 100), se2(d["se"] * 100)), r["n"], cal92,
                    "A8/A7 (trayectorias)", F9["B92"], "misspec.%s.rates.%s; delta_vs_independent.%s" % (key, p, p)))
    for det in E.CASES:
        g = [v for v in b92["misspec"].values() if v["case"] == det]
        out.append(("misspec_in_region_count|%s" % det, "%d de %d" % (sum(v["rates"][p]["in_region"] for v in g), len(g)), "región %s" % b92["exact_region_5000"],
                    D9.N_SIM, cal92, "A8/A7", F9["B92"], "misspec.*.rates.%s.in_region" % p))
        gg = [v for v in g if v["kind"] == "garch"]
        out.append(("garch_in_region_count|%s" % det, "%d de %d" % (sum(v["rates"][p]["in_region"] for v in gg), len(gg)), "región %s" % b92["exact_region_5000"],
                    D9.N_SIM, cal92, "A8/A7", F9["B92"], "misspec.*garch*.rates.%s.in_region" % p))
    for t in THETA_KEYS:
        v = b["A1prime"][t]
        out.append(("A1prime_within_tolerance_count|%s" % t, "%d de %d" % (sum(x["within_tolerance"] for x in v.values()), len(v)), "—",
                    b["config"]["N_pooled"], b["config"]["N_cal"], 111, F10["B10.1"], "A1prime.%s.*.within_tolerance" % t))
    # tamano igualado: DGP 1, DGP 2, DGP 3, tendencia
    if have("EQ"):
        eq, eqn, calq = J(F10["EQ"]), F10["EQ"], J(F10["EQ"])["config"]["N_cal"]
        for k, v in eq["cells"].items():
            r = v["rates_sim"][p]
            out.append(("equalized|%s" % k, f4(r["rate"]), wil(r), r["n"], calq, 95, eqn, "cells.%s.rates_sim.%s" % (k, p)))
    else:
        b91 = J(F9["B91"])
        for k, v in b91["cells"].items():
            r = v["rates_sim"][p]
            out.append(("equalized|%s" % k, f4(r["rate"]), wil(r), r["n"], b91["config"]["N_cal"], 95, F9["B91"], "cells.%s.rates_sim.%s" % (k, p)))
        for k, v in b92["dgp3"].items():
            r = v["rates"][p]
            out.append(("equalized|%s" % k, f4(r["rate"]), wil(r), r["n"], cal92, 95, F9["B92"], "dgp3.%s.rates.%s" % (k, p)))
    # DGP 5
    if have("DGP5"):
        d5 = J(F10["DGP5"])
        for k, v in d5["cells"].items():
            r = v["size_matched"]["primary"]
            out.append(("dgp5|%s|equalized" % k, f4(r["rate"]), wil(r), r["n"], d5["config"]["N_cal_equalized"], 60, F10["DGP5"],
                        "cells.%s.size_matched.primary" % k))
            r = v["nominal_hac"]["primary_hac"]
            out.append(("dgp5|%s|nominal" % k, f4(r["rate"]), wil(r), r["n"], d5["config"]["N_cal_nominal_primary"], 60, F10["DGP5"],
                        "cells.%s.nominal_hac.primary_hac" % k))
    else:
        b5 = J("b5_power_audit8.json")["dgp5"]
        for k, v in b5["cells"].items():
            r = v["size_matched"]["primary"]
            out.append(("dgp5|%s|equalized (A8, θ = 0.1)" % k, f4(r["rate"]), wil(r), r["n"], "5000 (A7)", 60, "b5_power_audit8.json",
                        "dgp5.cells.%s.size_matched.primary" % k))
    # potencia local
    for case in ("dm", "ct"):
        pw = b92["local_power"][case]["power"]
        for c in sorted(pw, key=float):
            out.append(("local_power|%s|c%s" % (case, c), f4(pw[c][p]), "envolvente %s" % f4(pw[c]["envelope"]), b92["config"]["N_power"], cal92,
                        102, F9["B92"], "local_power.%s.power.%s.%s" % (case, c, p)))
        for q in (p, "dfgls", "msb"):
            for c in GAP_C:
                out.append(("gap_envelope|%s|%s|c%s" % (case, q, c), pp1(b92["local_power"][case]["gap_to_envelope"][q][c] * 100) + " pp", "—",
                            b92["config"]["N_power"], cal92, 102, F9["B92"], "local_power.%s.gap_to_envelope.%s.%s" % (case, q, c)))
    # atribucion B9.3
    b93 = J(F9["B93"])
    for key, v in b93["gaussian_size"].items():
        for d in ("a_minus_b", "b_minus_c"):
            out.append(("attr_size|%s|%s" % (key, d), pp2(v["diffs"][d]["delta"] * 100) + " pp", "EE %s pp" % se2(v["diffs"][d]["se"] * 100),
                        D9.N_INDEP, E.N_CAL, 102, F9["B93"], "gaussian_size.%s.diffs.%s" % (key, d)))
    for key, v in b93["local_power"].items():
        for d in ("a_minus_b", "b_minus_c"):
            out.append(("attr_local_power|%s|%s" % (key, d), pp2(v["diffs"][d]["delta"] * 100) + " pp", "EE %s pp" % se2(v["diffs"][d]["se"] * 100),
                        D9.N_POWER, E.N_CAL, 102, F9["B93"], "local_power.%s.diffs.%s" % (key, d)))
    # coste de aproximar
    fn, fb = src_fin()
    for case in E.CASES:
        for n, v in fb["cases"][case]["approximation_cost"].items():
            for kk in ("size_with_cv_n20000", "size_with_cv_at_n"):
                r = v[kk]
                out.append(("approx_cost|%s|n%s|%s" % (case, n, kk), f4(r["rate"]), wil(r), r["n"], v.get("calibration", E.N_CAL), "102/104", fn,
                            "cases.%s.approximation_cost.%s.%s" % (case, n, kk)))
            cs = fb["cases"][case]["approximation_cost_comparators"][n]
            for q in ("dfgls", "msb"):
                for kk in ("size_published_asymptotic", "size_simulated_at_n"):
                    r = cs[q][kk]
                    out.append(("approx_cost|%s|n%s|%s|%s" % (case, n, q, kk), f4(r["rate"]), wil(r), r["n"], cs[q].get("calibration", E.N_CAL),
                                102, fn, "cases.%s.approximation_cost_comparators.%s.%s.%s" % (case, n, q, kk)))
    # AWB
    an, ab = src_awb()
    for k, v in ab["cells"].items():
        for kk in ("awb", "sim"):
            r = v[kk]
            out.append(("awb_probe|%s|%s" % (k, kk), f4(r["rate"]), wil(r), r["n"], "B = %d" % ab["config"]["B"] if kk == "awb" else "—",
                        113 if an == F10["AWB"] else 105, an, "cells.%s.%s" % (k, kk)))
    out.append(("awb_recommended", "sí" if ab["rule"]["recommend_awb"] else "no", "—", "—", "—", "—", an, "rule.recommend_awb"))
    # aplicacion
    pn, pb = src_app()
    for t in ("final", "final_awb", "rhat_prereg"):
        if t in pb["summary"]:
            v = pb["summary"][t]
            out.append(("app|%s|fp_mean" % t, f4(v["fp_mean"]), "máx. %s" % f4(v["fp_max"]), "—", pb["config"]["N_cal"], "—", pn, "summary.%s.fp_mean" % t))
            out.append(("app|%s|detections" % t, "%d de %d" % (v["detections"], v["event_cells"]),
                        "latencia %s" % ("%.1f" % v["mean_latency_detected"] if v["mean_latency_detected"] else "—"), "—", pb["config"]["N_cal"], "—", pn,
                        "summary.%s.detections" % t))
    out.append(("app|matched_target_fpr", f4(pb["matched_rate"]["target_fpr_pooled_primary"]), "—", "—", pb["config"]["N_cal"], "—", pn,
                "matched_rate.target_fpr_pooled_primary"))
    out.append(("app|adverse_cells", "%d" % len(pb["adverse_cells_primary"]), "—", "—", "—", "—", pn, "adverse_cells_primary"))
    for d, v in pb["oos_size"]["by_D"].items():
        out.append(("app|oos_size|D%s" % d, f4(v["rate"]), wil(v), v["n"], pb["config"]["N_cal"], pb["oos_size"].get("family_paths", pb["oos_size"].get("family")),
                    pn, "oos_size.by_D.%s" % d))
    # valores criticos al 5%
    cn, cb = src_cv()
    tp = cb["primary_theta"] if cn == F10["CV"] else theta()
    for case in ("dm", "ct"):
        for n in cb["config"]["n"]:
            v = cb["table"]["%s|%g|%d" % (case, tp, n)]
            out.append(("cv5|%s|n%d" % (case, n), f4(v["cv"]["0.05"]), "EE %s" % f4(v["se"]["0.05"]), "—", cb["config"]["N_cal"], 107, cn,
                        "table.%s|%g|%d.cv.0.05" % (case, tp, n)))
    if have("B10.4"):
        b4 = J(F10["B10.4"])
        for t, v in b4["by_theta"].items():
            out.append(("cv5_n5000_replicas|dm|%s" % t, f4(v["mean"]), "DT %s; rango [%s, %s]" % (f4(v["sd"]), f4(v["min"]), f4(v["max"])),
                        "—", b4["config"]["N_cal"], 114, F10["B10.4"], "by_theta.%s" % t))
    if have("B10.2"):
        b2 = J(F10["B10.2"])
        out.append(("identity_theta0_worst_rel", sci(max(b2["worst_i"], b2["worst_ii"])), "umbral %s" % sci(b2["config"]["threshold"]),
                    b2["config"]["reps"], "—", 112, F10["B10.2"], "worst_i; worst_ii"))
    return out


def main():
    L = []
    w = L.append
    b0 = J(F10["B10.0"])
    w("# Auditoría A10 — cierre: decisión limpia de θ y consolidación")
    w("")
    w("Generado por `experiments/audit10_generate_report.py` el %s (UTC) desde los JSON de `experiments/results/`; commit `%s`." % (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"), C.git("rev-parse", "--short", "HEAD").strip()))
    w("")
    w("Protocolo: `%s`, sha256 `%s`, commit `%s` (registrado antes de cualquier cómputo; enmienda declarada a la regla del θ de A9)." % (
        b0["protocol"]["path"], b0["protocol"]["sha256_disk"], b0["protocol"]["commit_added"][:7]))
    w("")
    if have("B10.1"):
        w("θ final: **%s**." % ("ninguno (la compuerta de B10.1 detiene)" if theta() is None else "RM-GLS, θ = %g" % theta()))
        w("")
    w("## 1. Resultados")
    w("")
    sec_b100(w, L)
    sec_b101(w, L)
    if have("B10.2"):
        sec_b102(w, L)
    if have("B10.1") and theta() is not None:
        sec_b103(w, L)
    if have("B10.4"):
        sec_b104(w, L)
    sec_b105(w, L)
    w("## 2. Compuertas")
    w("")
    gates(L)
    w("")
    w("## 3. Procedencia")
    w("")
    provenance_section(w, L)
    w("## 4. Desviaciones")
    w("")
    L.extend(table(["Qué", "Por qué", "Antes/después de ver datos", "Efecto"], deviations()))
    w("")
    w("## 5. No ejecutado")
    w("")
    L.extend(table(["Qué", "Por qué", "Comando de reanudación"], not_executed()))
    w("")
    w("## 6. Conclusiones")
    w("")
    if have("B10.1") and theta() is not None:
        conclusions(w)
    else:
        w("Pendientes: la compuerta de B10.1 detiene o falta el análisis (§5).")
    w("")
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    w("### (a) Anomalías numéricas")
    w("")
    for a in anomalies():
        w("- " + a)
    w("")
    w("### (b) Frases del manuscrito v11 revisadas con la configuración final")
    w("")
    if have("B10.1") and theta() is not None:
        L.extend(table(["Frase", "Archivo:línea", "Cita", "Estado con la configuración final"],
                       [[c["label"], "`%s:%d`" % (c["file"], c["line"]), c["quote"], claim_status(c)] for c in manuscript_claims()]))
    w("")
    w("## Anexo: tabla maestra del manuscrito")
    w("")
    w("`clave | valor | IC o EE | N_sim | N_cal | familia | archivo JSON | ruta dentro del JSON`")
    w("")
    if have("B10.1") and theta() is not None:
        for f in master():
            w("- " + " | ".join(str(x) for x in f))
    w("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    C.register_outputs(__file__, [OUT], C.provenance(__file__))
    print("escrito %s (%d lineas)" % (OUT, len(L)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
