"""
Auditoria A11 - generador de experiments/results/resultados_auditoria_11.md.

Regla de A8 (regla 3): ningun numero de resultado se escribe a mano; todo valor se
lee de un JSON o log de experiments/results. Las citas del manuscrito v12 salen de
t5_claims_audit11.json, que las lee del zip. Si falta una clave, el script falla con
KeyError. tests/test_no_literals_audit11.py recorre este archivo.

Estructura: encabezado; 1 resultados (T0-T5); 2 criterios y compuertas; 3
procedencia; 4 desviaciones; 5 no ejecutado; 6 conclusiones; 7 anomalias y frases
del manuscrito; anexo (tabla maestra de los numeros nuevos).

Uso: python experiments/audit11_generate_report.py
"""
import datetime
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402
import audit11_design as D                                         # noqa: E402
from audit8_generate_report import table as _table                  # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_11.md")
PROTOCOL = "experiments/protocol_audit11.md"
F = {"T0": "t0_protocol_audit11.json", "T1": "figures_audit11.json", "T2": "t2_dgp2_audit11.json",
     "T3": "t3_anchor_audit11.json", "T4": "t4_trend_audit11.json", "T5": "t5_claims_audit11.json"}
SCRIPTS = {"T0": "experiments/audit11_t0_protocol.py", "T1": "experiments/make_figures_audit11.py",
           "T2": "experiments/audit11_t2_dgp2.py", "T3": "experiments/audit11_t3_anchor.py --run --cores 14; --analyze",
           "T4": "experiments/audit11_t4_trend.py --run --cores 14; --analyze", "T5": "experiments/audit11_t5_claims.py"}
QN = {"resid_ms": "n⁻¹Σû_t²", "sigma2_hac": "σ̂²_HAC", "statistic": "RM-GLS (θ = 0.02, tendencia)"}
TAB_LABEL = {"prim": "RM-GLS", "rm": "RM", "adf": "ADF-sim", "pp": "PP-sim", "dfgls": "DF-GLS-sim", "mzt": "MZ_t-GLS-sim",
             "msb": "MSB-GLS-sim", "za": "ZA"}


def J(key):
    return C.read_json(F[key])


def table(header, rows):
    def esc(x):
        return str(x).replace("|", "\\|")
    return _table([esc(h) for h in header], [[esc(x) for x in r] for r in rows])


def f(x, d=4):
    return "%.*f" % (d, x)


def yn(b):
    return "sí" if b else "no"


def T(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def pytest_summary():
    name = "pytest_audit11.log"
    if not os.path.exists(os.path.join(C.RESULTS, name)):
        return None
    text = T(name)
    summary, secs = re.findall(r"=+ (.*?) in ([0-9.]+)s", text)[-1]
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|errors?)", summary)}
    coll = re.search(r"collected (\d+) items", text)
    lit = re.findall(r"tests[\\/]test_no_literals_audit11\.py::(\S+) (PASSED|FAILED|SKIPPED)", text)
    return {"seconds": float(secs), "collected": int(coll.group(1)) if coll else None, "counts": counts, "literals": lit}


def cite(q):
    return "`%s:%d`" % (q["file"], q["line"])


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------
def sec_t0(w, L):
    b = J("T0")
    p, s, m = b["protocol"], b["seed_map"], b["manuscript"]
    w("### T0 — Protocolo y semillas")
    w("")
    w("- Protocolo `%s`: sha256 en disco `%s`, commiteado `%s` (%s), introducido en `%s`." % (
        p["path"], p["sha256_disk"], p["sha256_committed"], "iguales" if p["sha256_disk"] == p["sha256_committed"] else "DISTINTOS",
        p["commit_added"][:7]))
    w("- Manuscrito de referencia `%s` (fuera del repositorio, solo lectura): sha256 `%s`, %d bytes. Los %d `.tex` de `paper/` (v11) no se tocan; su sha256 queda en `%s`." % (
        m["zip"], m["zip_sha256"], m["zip_bytes"], len(m["paper_tex_v11"]), F["T0"]))
    w("- Equivalencia `SeedSequence(familia).spawn` ↔ `spawn_key = (celda, i)`: %d streams comprobados, %d discrepancias." % (
        b["spawn_equivalence"]["streams_checked"], b["spawn_equivalence"]["mismatches"]))
    w("- Colisiones: %d streams nuevos (%s) frente a %d previos (%d semillas enteras y las familias %s): %d colisiones con los previos, %d dentro de A11 (%s)." % (
        s["new_streams_total"], ", ".join("familia %s: %d" % (k, v["replicate_streams"]) for k, v in s["new_families"].items() if v["replicate_streams"]),
        s["prior_streams_total"], s["prior_integer_seeds"], ", ".join(sorted(s["prior_family_streams"], key=int)),
        s["collisions_new_vs_prior"], s["collisions_within_new"], s["method"]))
    w("- Familias: %s. Sin trayectorias: %s." % (", ".join("%s = %d" % kv for kv in b["families"].items()),
                                                 ", ".join(str(x) for x in s["families_without_cells"])))
    w("")


def sec_t1(w, L):
    b = J("T1")
    w("### T1 — Figuras en inglés (mismos nombres de archivo)")
    w("")
    w("Código de referencia: %s. Se interceptaron `Axes.plot`, `Axes.fill_between` y `Axes.axhline` en las dos corridas y se compararon los arrays float64 llamada a llamada (`np.array_equal`, sin tolerancia). θ graficado: %g. Datos idénticos en las seis figuras: **%s**." % (
        b["reference_code"], b["primary_theta"], yn(b["all_bitwise_identical"])))
    w("")
    w("**Tabla T1.1. sha256 antes y después, e igualdad de los datos graficados.**")
    w("")
    rows = []
    for name, v in b["figures"].items():
        d = v["data"]
        rows.append([name, "`%s`" % v["before"]["sha256_figures_audit10"], "`%s`" % v["sha256"], "`%s`" % v["paper_copy_sha256"],
                     "%d / %d" % (d["calls_a10"], d["calls_a11"]), "%d / %d" % (d["values_a10"], d["values_a11"]),
                     yn(d["same_call_sequence"]), "**%s**" % yn(d["bitwise_identical"]), "`%s`" % d["sha256_a11"][:16]])
    L.extend(table(["Archivo", "sha256 A10 (`figures_audit10.json`)", "sha256 nuevo", "sha256 copia en `paper/figures`",
                    "Llamadas A10 / A11", "Valores A10 / A11", "Misma secuencia", "Bit a bit", "sha256 de los datos (16)"], rows))
    w("")
    w("*Fuente: `%s`. Las fuentes de datos son las de A10: %s.*" % (F["T1"], ", ".join("`%s`" % s for s in b["sources"])))
    w("")
    w("Cambios de texto (lectura operativa 4): paneles «Constant»/«Trend»; ejes y leyendas del encargo; «AWB DF-GLS (A8)» → «AWB DF-GLS» en `fig_size_shift`; MSB-GLS, DF-GLS y MZ_t-GLS conservan su nombre en `fig_local_power`; etiqueta 150 eliminada en `fig_calibration_gain` (la marca se conserva) y leyenda en dos columnas; en `fig_theta_ladder`, etiquetas con dos decimales y 0.00 alineada a la derecha de su marca (desviación en §4).")
    w("")


def sec_t2(w, L):
    b = J("T2")
    cfg = b["config_source"]
    w("### T2 — DGP 2 con θ = %g para el manuscrito" % b["primary_theta"])
    w("")
    w("Fuente: `%s` (sha256 `%s`), celdas `dgp2_*`, `rates_sim`; RM = `%s`; ZA en el propio JSON: %s → columna %s. Trayectorias: %s. Regla: %s. N_sim = %d; N_cal = %d (n ∈ {200, 500, 1000}; KPSS y ZA con 50 000 de A9)." % (
        b["source"], b["source_sha256"], b["rm_column"], yn(b["za_in_source"]), b["za_column"], cfg["trajectories"], cfg["rule_sim"],
        cfg["N_sim"], cfg["N_cal"]))
    w("")
    w("**Tabla T2.1. Potencia bajo DGP 2 (AR(0.95) con quiebre de media δ), tasas con umbral simulado; McNemar exacto de RM-GLS frente a DF-GLS-sim.** Exportada como `%s` y `%s` (solo el `tabular`)." % (b["markdown"], b["latex"]))
    w("")
    L.extend(T(os.path.basename(b["markdown"])).rstrip("\n").splitlines())
    w("")
    w("ZA con p-valor asintótico en las mismas celdas (informativa, `rates_asy.za`): %s." % "; ".join(
        "δ = %g, n = %d: %s" % (r["delta"], r["n"], f(r["za_asy"], 3)) for r in b["rows"]))
    w("")
    w("**Tabla T2.2. Tamaño de ZA bajo paseo aleatorio y bajo paseo con quiebre de media Δμ = 1.**")
    w("")
    rows = []
    for k, v in b["za_size_a8"].items():
        a6 = b["za_size_a6"][k]
        rows.append([v["kind"], v["n"], f(v["rate"]), "[%s, %s]" % (f(v["wilson"][0]), f(v["wilson"][1])), yn(v["in_region"]), v["N"],
                     f(a6["rate"]), "[%s, %s]" % (f(a6["ci"][0]), f(a6["ci"][1])), a6["N"]])
    L.extend(table(["Proceso", "n", "ZA (A8)", "Wilson 95%", "En región exacta", "N (A8)", "ZA (A6)", "IC (A6)", "N (A6)"], rows))
    w("")
    w("*Fuentes: `b5_power_audit8.json` (`za_size.za_<rw|rwbreak>_n<n>.rates.za`, p-valor asintótico de ZA, región exacta de N = 5000 %s) y `dgp2_break_tests_audit6.json` (`size_control.<pure_rw|break_rw>.<n>`).*" % (b["exact_region_5000"],))
    w("")


def sec_t3(w, L):
    b = J("T3")
    cfg = b["config"]
    w("### T3 — Sesgo del ancla (Observación del manuscrito)")
    w("")
    w("Estadístico: `%s`; σ² = %g fijo; caso %s, ancla %s, c̄ = %g, κ(c̄) = 2|c̄|(1/2 + |c̄|/3) = %s (literal del encargo: %s). Trayectorias: %s; N = %d por n; los tres θ sobre las mismas trayectorias. τ₁ por (n, θ): %s." % (
        cfg["statistic"], cfg["sigma_sq"], cfg["case"], cfg["anchor"], cfg["cbar"], f(cfg["kappa"], 6), cfg["kappa_literal"], cfg["paths"],
        cfg["N"], "; ".join("n = %s: %s" % (n, ", ".join("θ = %s → %d" % kv for kv in v.items())) for n, v in cfg["tau_1"].items())))
    w("")
    w("**Tabla T3.1. E[S_θ²] simulado (media ± EE) frente a (1−θ)/2 + θ/3 y a la aproximación de primer orden (1−θ)/2 + θ/3 − κ/n.**")
    w("")
    rows = []
    for n, c in b["cells"].items():
        for t, v in c["by_theta"].items():
            rows.append([n, t, f(v["mean"], 5), f(v["se"], 5), f(v["limit"], 5), f(v["limit_minus_kappa_over_n"], 5),
                         f(v["z_vs_first_order"], 2), f(v["z_vs_limit"], 2)])
    L.extend(table(["n", "θ", "Media", "EE", "(1−θ)/2 + θ/3", "… − κ/n", "z frente a primer orden", "z frente al límite"], rows))
    w("")
    w("*Fuente: `%s` (`cells.<n>.by_theta.<θ>`); N_sim = %d; sin calibración; familia %d.*" % (F["T3"], cfg["N"], C.FAMILY["T3"]))
    w("")
    cr = b["criterion_n20000_theta0"]
    w("Paso 0 (identidad S₀² = (n+1)⁻¹Σ(Y_t − β̂_GLS)²/n en las 100 primeras trayectorias de cada n): peor |Δ| = %s; pasa en todas: %s." % (
        "%.2e" % max(c["paso0"]["max_abs_diff"] for c in b["cells"].values()), yn(b["paso0_all_pass"])))
    w("")


def sec_t4(w, L):
    b = J("T4")
    cfg = b["config"]
    w("### T4 — Consistencia con tendencia")
    w("")
    w("DGP: Y_t = %g + %g t + x_t, t = 0, …, n; x_t AR(ρ) estacionario. %d réplicas por (ρ, n); %s. Cantidades: %s. Pendiente: MCO de log(mediana) sobre log n; IC %g%% bootstrap percentil con B = %d. Regla de «acotado» (lectura 7): %s." % (
        cfg["intercept"], cfg["trend_slope"], cfg["N"], cfg["paths"], "; ".join("%s = %s" % (QN[k], v) for k, v in cfg["quantities"].items()),
        cfg["ci_level"] * 100, cfg["bootstrap_B"], cfg["bounded_rule"]))
    w("")
    w("**Tabla T4.1. Medianas por n y pendientes log–log.**")
    w("")
    rows = []
    for rho, v in b["by_rho"].items():
        for q, x in v["quantities"].items():
            rows.append([rho, f(v["stationary_variance"], 4), QN[q]] + [f(x["median"][str(n)], 4) for n in cfg["n"]]
                        + [f(x["slope"], 3), "[%s, %s]" % (f(x["slope_ci95"][0], 3), f(x["slope_ci95"][1], 3)), yn(x["ci_contains_zero"]),
                           f(x["ratio_last_first"], 3)])
    L.extend(table(["ρ", "1/(1−ρ²)", "Cantidad"] + ["n = %d" % n for n in cfg["n"]] + ["Pendiente", "IC 95%", "IC contiene 0",
                                                                                         "Cociente n = %d / n = %d" % (max(cfg["n"]), min(cfg["n"]))], rows))
    w("")
    w("*Fuente: `%s` (`by_rho.<ρ>.quantities.<cantidad>`); N_sim = %d por celda; sin calibración; familia %d.*" % (F["T4"], cfg["N"], C.FAMILY["T4"]))
    w("")
    w("**¿n⁻¹Σû_t² queda acotado?** %s." % "; ".join("ρ = %s: %s (límite superior del IC de la pendiente %s frente a %g)" % (
        rho, "sí" if v["quantities"]["resid_ms"]["bounded"] else "no", f(v["quantities"]["resid_ms"]["slope_ci95"][1], 3), cfg["bounded_slope_upper"])
        for rho, v in b["by_rho"].items()))
    nan = sum(n for v in b["by_rho"].values() for x in v["quantities"].values() for n in x["nan"].values())
    w("Valores no finitos: %d." % nan)
    w("")


def sec_t5(w, L):
    b = J("T5")
    c = b["claims"]
    w("### T5 — Cifras citadas del manuscrito")
    w("")
    w("Frases leídas de `%s` (sha256 `%s`); regla de confirmación de la lectura 8." % (b["manuscript"]["zip"], b["manuscript"]["sha256"]))
    w("")
    c1, c2, c3, c4 = c["1"], c["2"], c["3"], c["4"]
    op = c2["operative"]
    m3 = c3["by_case"]["dm"]["%g" % c3["theta_a8"]]
    rows = [
        ["1", cite(c1["quote"]), "at most %s points" % c1["printed"],
         "máx. |Δ| = %s pp (celda `%s`; %d celdas: %s; %s)" % (f(c1["max_abs_delta_pp"], 2), c1["cell"], c1["cells_evaluated"],
                                                              ", ".join(c1["kinds"]), c1["comparison"]),
         "`%s` · `%s`" % (c1["json"], c1["json_path"]), "**%s**" % yn(c1["confirmed"])],
        ["2", cite(c2["quote"]), "%s to %s points" % tuple(c2["printed"]),
         "%s pp (%s)" % (", ".join("%s: %s" % (k, f(v, 2)) for k, v in op["diff_pp"].items()), c2["operative_config"]),
         "`%s` · `%s`" % (c2["json"], c2["json_path"]), "**%s**" % yn(c2["confirmed"])],
        ["3", ", ".join(cite(q) for q in c3["quotes"]), "; ".join("%s %s" % (v["kind"], v["number"]) for v in c3["verdicts"]),
         "coste de centrar (potencia RM-GLS − RM, demeaned, n = %d, c = %g, θ = %g) = %s pp (%s − %s); brecha de RM a la envolvente = %s pp; de RM-GLS = %s pp" % (
             c3["n"], c3["c"], c3["theta_a8"], f(m3["cost_pp"], 2), f(m3["power_rmgls"]), f(m3["power_rm"]), f(m3["gap_rm_pp"], 2), f(m3["gap_rmgls_pp"], 2)),
         "`%s` · `%s`" % (c3["json"], c3["json_path"]), "**%s**" % yn(c3["confirmed"])],
        ["4", cite(c4["quote"]), " & ".join(c4["printed"]),
         "%s (%s)" % (" & ".join(str(round(v, 4)) if isinstance(v, float) else str(v) for v in c4["by_audit"]["A10"]["values"]),
                      ", ".join(c4["fields"])),
         "`%s` · %s" % (c4["by_audit"]["A10"]["json"], ", ".join("`%s`" % p for p in c4["json_paths"])), "**%s**" % yn(c4["confirmed"])],
    ]
    L.extend(table(["Ítem", "Manuscrito", "Cifra impresa", "Valor en el JSON", "Fuente", "Confirmada"], rows))
    w("")
    w("Detalle del ítem 2 (todas las configuraciones de `%s`): %s." % (c2["json"], "; ".join(
        "%s: %s–%s pp" % (k, f(v["min"], 2), f(v["max"], 2)) for k, v in c2["all_configs"].items())))
    w("")
    w("Detalle del ítem 3 (coste de centrar a c = %g y su máximo sobre c, por θ de A8 B4; θ = 0.02 no está en B4): %s. Tendencia: %s. Regla G1 de A8: brecha RM-GLS %s pp, brecha RM %s pp, reducción %s pp." % (
        c3["c"], "; ".join("θ = %s: %s pp (máx. %s pp en c = %s)" % (t, f(v["cost_pp"], 2), f(v["max_cost_pp_over_c"], 2), v["c_at_max_cost"])
                          for t, v in c3["by_case"]["dm"].items()),
        "; ".join("θ = %s: %s pp" % (t, f(v["cost_pp"], 2)) for t, v in c3["by_case"]["ct"].items()),
        f(c3["G1"]["gap_rmgls_pp"], 2), f(c3["G1"]["gap_rm_pp"], 3), f(c3["G1"]["reduction_pp"], 3)))
    w("")
    w("Detalle del ítem 4: tasa común del pie de tabla %s (%s) frente a %s en `%s` → %s. Referencia: A9 %s y A8 %s coinciden en %s de 7 campos (las columnas a tasa común se recalcularon en A10 con la primaria θ = 0.02, que fija la tasa objetivo)." % (
        c4["printed_rate"], cite(c4["rate_quote"]), f(c4["by_audit"]["A10"]["target_fpr"], 6), c4["by_audit"]["A10"]["json"], yn(c4["rate_confirmed"]),
        " & ".join(str(round(v, 4)) if isinstance(v, float) else str(v) for v in c4["by_audit"]["A9"]["values"]),
        " & ".join(str(round(v, 4)) if isinstance(v, float) else str(v) for v in c4["by_audit"]["A8"]["values"]),
        sum(c4["by_audit"]["A9"]["match"])))
    w("")


# ---------------------------------------------------------------------------
# Criterios, procedencia, desviaciones
# ---------------------------------------------------------------------------
def gates(L):
    t0, t1, t3, t4 = J("T0"), J("T1"), J("T3"), J("T4")
    cr = t3["criterion_n20000_theta0"]
    rows = [
        ["T0 colisiones", "0 colisiones con los streams previos y dentro de A11", "%d / %d" % (
            t0["seed_map"]["collisions_new_vs_prior"], t0["seed_map"]["collisions_within_new"]),
         "pasa" if t0["seed_map"]["collisions_new_vs_prior"] == 0 and t0["seed_map"]["collisions_within_new"] == 0 else "FALLA"],
        ["T1 datos", "arrays graficados idénticos bit a bit en las seis figuras", "%d de %d" % (
            sum(v["data"]["bitwise_identical"] for v in t1["figures"].values()), len(t1["figures"])),
         "pasa" if t1["all_bitwise_identical"] else "FALLA"],
        ["T3 criterio (literal)", "fila n = %d a menos de %g EE de (1−θ)/2 + θ/3 − 39.67/n para θ = 0" % (cr["n"], cr["threshold_se"]),
         "media %s, EE %s, objetivo %s → z = %s (con κ exacto: objetivo %s, z = %s)" % (
             f(cr["mean"], 5), f(cr["se"], 5), f(cr["target_literal"], 5), f(cr["z_literal"], 2), f(cr["target"], 5), f(cr["z"], 2)),
         "pasa" if cr["passes_literal"] and cr["passes"] else "FALLA"],
        ["T3 Paso 0", "identidad S₀² frente a la fórmula de la Observación ≤ 1e-12", "%.2e" % max(
            c["paso0"]["max_abs_diff"] for c in t3["cells"].values()), "pasa" if t3["paso0_all_pass"] else "FALLA"],
        ["T4 acotado (informativo)", t4["config"]["bounded_rule"], "; ".join("ρ = %s: %s" % (r, f(v["quantities"]["resid_ms"]["slope_ci95"][1], 3))
                                                                            for r, v in t4["by_rho"].items()),
         ", ".join("ρ = %s %s" % (r, "acotado" if v["quantities"]["resid_ms"]["bounded"] else "no acotado") for r, v in t4["by_rho"].items())],
    ]
    L.extend(table(["Criterio", "Regla", "Medido", "Veredicto"], rows))


def provenance_section(w, L):
    man = C.read_json("manifest_audit11.json")
    w("**Archivos que alimentan este reporte** (`manifest_audit11.json`; el reporte se registra después de escribirse).")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "Script", "Commit", "Árbol limpio", "Código commiteado"],
                   [[k, "`%s`" % e["sha256"], e["bytes"], e["script"], e["commit"][:7], yn(not e["worktree_dirty"]), yn(e["code_all_committed"])]
                    for k, e in sorted(man["entries"].items()) if not k.endswith("resultados_auditoria_11.md")]))
    w("")
    w("Comandos: %s." % "; ".join("%s: `%s`" % kv for kv in SCRIPTS.items()))
    w("")
    for key in ("T3", "T4"):
        b = J(key)
        el = b["compute_elapsed_sec_by_n"] if key == "T3" else b["compute_elapsed_sec"]
        w("- %s: tiempo de cómputo por celda (s): %s; total %.1f s." % (key, ", ".join("%s: %.1f" % kv for kv in el.items()), sum(el.values())))
    py = pytest_summary()
    if py is not None:
        c = py["counts"]
        w("- Suite completa (`pytest_audit11.log`): collected %s; passed %d; failed %d; skipped %d; %.1f s." % (
            py["collected"], c.get("passed", 0), c.get("failed", 0), c.get("skipped", 0), py["seconds"]))
        w("- Test de literales (`tests/test_no_literals_audit11.py`): %s." % "; ".join("%s %s" % t for t in py["literals"]))
    w("- Checkpoints de T3 y T4 (`checkpoints/audit11_t3`, `checkpoints/audit11_t4`) sin commitear; se regeneran bit a bit desde la familia y el índice de réplica.")
    w("")


def deviations():
    return [
        ["`fig_theta_ladder`: 0.02 queda centrada en su marca (no alineada a la izquierda como fijaba la lectura 4); solo 0.00 se alinea a la derecha",
         "Con 0.02 alineada a la izquierda chocaba con 0.05 (comprobado en el PDF)", "después de ver la figura", "Ninguno sobre los datos"],
        ["`fig_calibration_gain`: leyenda en dos columnas y bajada", "En una fila era más ancha que los paneles; en dos pisaba la etiqueta «n»",
         "después de ver la figura", "Ninguno sobre los datos"],
        ["Los seis PDF se sobrescriben con el mismo nombre; `figures_audit10.json` y `manifest_audit10.json` conservan los sha256 anteriores",
         "El encargo pide conservar los nombres y la regla prohíbe modificar JSON de auditorías previas", "antes (lectura 3)",
         "Los sha256 vigentes están en `figures_audit11.json` y `manifest_audit11.json`"],
        ["T0 se ejecutó dos veces: en la primera el protocolo en disco tenía finales CRLF (el commit, LF) y los sha256 diferían; se normalizó a LF sin cambiar el contenido",
         "Final de línea", "antes de cualquier cómputo", "Ninguno; sha256 en disco = commiteado (T0)"],
        ["T2 falló dos veces antes de escribir su JSON (un `%` sin escapar en el comentario del `.tex` y la consola cp1252 al imprimir δ); se corrigió y se reejecutó",
         "Errores de programación y de consola", "durante T2", "Ninguno sobre valores"],
        ["T5: la localización de líneas se corrigió para citar la línea donde empieza la frase (no el inicio de la ventana de dos líneas) y un patrón de T3 que tomaba la cita equivocada",
         "Error de programación", "durante T5", "Ninguno sobre valores"],
        ["Las cifras impresas del manuscrito para T3 están escritas en `audit11_t3_anchor.py`; el generador comprueba que coinciden con las que T5 lee del zip",
         "T3 se ejecutó antes que T5", "antes", "Comprobación en §7(b)"],
    ]


def conclusions(w):
    t1, t3, t4, t5 = J("T1"), J("T3"), J("T4"), J("T5")
    cr = t3["criterion_n20000_theta0"]
    ms = t3["manuscript_simulated"]
    c = t5["claims"]
    w("1. T1: las seis figuras están en inglés, con los mismos nombres; datos graficados idénticos bit a bit en las seis: %s." % yn(t1["all_bitwise_identical"]))
    w("2. T2: tabla de DGP 2 con θ = %g exportada en Markdown y LaTeX; ZA estaba en el JSON de A10 (valor crítico simulado)." % J("T2")["primary_theta"])
    w("3. T3: criterio de la fila n = %d con θ = 0: z = %s (%s). Cifras simuladas del manuscrito: %s." % (
        cr["n"], f(cr["z_literal"], 2), "pasa" if cr["passes_literal"] else "no pasa",
        "; ".join("n = %s: impresa %s, simulada %s ± %s, z = %s (%s)" % (n, f(v["printed"], 3), f(v["mean"], 4), f(v["se"], 4), f(v["z"], 2),
                                                                         "se reproduce" if v["reproduced"] else "NO se reproduce")
                  for n, v in ms.items())))
    w("4. T4: pendiente log–log de la mediana de n⁻¹Σû_t²: %s; acotado según la lectura 7: %s." % (
        "; ".join("ρ = %s: %s [%s, %s]" % (r, f(v["quantities"]["resid_ms"]["slope"], 3), f(v["quantities"]["resid_ms"]["slope_ci95"][0], 3),
                                          f(v["quantities"]["resid_ms"]["slope_ci95"][1], 3)) for r, v in t4["by_rho"].items()),
        ", ".join("ρ = %s %s" % (r, yn(v["quantities"]["resid_ms"]["bounded"])) for r, v in t4["by_rho"].items())))
    w("5. T5: confirmadas %s de 4 (%s)." % (sum(v["confirmed"] for v in c.values()),
                                           ", ".join("ítem %s %s" % (k, "sí" if v["confirmed"] else "no") for k, v in c.items())))
    w("")


def anomalies(w):
    t3, t4 = J("T3"), J("T4")
    cells = t3["cells"]
    ns = [str(n) for n in D.T3_N]
    drops = [(a, b) for a, b in zip(ns, ns[1:]) if cells[b]["by_theta"]["0"]["mean"] < cells[a]["by_theta"]["0"]["mean"]]
    for a, b in drops:
        x, y = cells[a]["by_theta"]["0"], cells[b]["by_theta"]["0"]
        w("- T3: la media de S₀² baja de n = %s (%s ± %s) a n = %s (%s ± %s); la diferencia es %s EE combinados. Mismo patrón con θ = 0.02 y 0.1, porque se evalúan sobre las mismas trayectorias." % (
            a, f(x["mean"], 5), f(x["se"], 5), b, f(y["mean"], 5), f(y["se"], 5),
            f((y["mean"] - x["mean"]) / math.sqrt(x["se"] ** 2 + y["se"] ** 2), 2)))
    for r, v in t4["by_rho"].items():
        q = v["quantities"]["resid_ms"]
        w("- T4, ρ = %s: la mediana de n⁻¹Σû_t² en n = %d es %s y la varianza estacionaria del DGP, 1/(1−ρ²), es %s. El IC de la pendiente contiene 0: %s." % (
            r, max(D.T4_N), f(q["median"][str(max(D.T4_N))], 4), f(v["stationary_variance"], 4), yn(q["ci_contains_zero"])))
    w("")


def manuscript_section(w):
    t3, t5 = J("T3"), J("T5")
    q3 = t5["t3_quotes"]
    printed_zip = {"200": q3["appendix"]["groups"][0], "500": q3["appendix"]["groups"][1], "2000": q3["appendix"]["groups"][2]}
    fo_zip = dict(zip(printed_zip, q3["appendix_first_order"]["groups"]))
    agree = (all(float(printed_zip[n]) == v["printed"] for n, v in t3["manuscript_simulated"].items())
             and all(float(fo_zip[n]) == v["printed"] for n, v in t3["manuscript_first_order"].items()))
    w("Cifras impresas en `audit11_t3_anchor.py` frente a las leídas del zip (%s): %s." % (
        cite(q3["appendix"]), "coinciden" if agree else "NO COINCIDEN"))
    w("")
    rows = []
    for n, v in t3["manuscript_simulated"].items():
        where = [cite(q3["appendix"])] + [cite(q3[k]) for k in ("remark_n200", "remark_n2000") if q3[k]["groups"][0] == n]
        rows.append([", ".join(where), "E[S₀²] simulado a n = %s: %s" % (n, printed_zip[n]), "%s ± %s" % (f(v["mean"], 4), f(v["se"], 4)),
                     f(v["z"], 2), "sí" if v["reproduced"] else "**no**",
                     "—" if v["rounds_to_printed"] else "%s (simulado de A11 a tres decimales)" % f(v["mean"], 3)])
    for n, v in t3["manuscript_first_order"].items():
        rows.append([cite(q3["appendix_first_order"]), "primer orden 1/2 − κ/n a n = %s: %s" % (n, fo_zip[n]), f(v["value"], 5), "—",
                     "sí (aritmética)" if v["rounds_to_printed"] else "**no**", "—"])
    k = q3["remark_kappa"]
    rows.append([cite(k), "κ(−7) ≈ %s" % k["groups"][0], f(t3["config"]["kappa"], 6), "—",
                 "sí" if round(t3["config"]["kappa"], len(k["groups"][0].split(".")[1])) == float(k["groups"][0]) else "**no**", "—"])
    c = t5["claims"]
    c3 = c["3"]
    m3 = c3["by_case"]["dm"]["%g" % c3["theta_a8"]]
    for v, q in zip(c3["verdicts"], c3["quotes"]):
        rows.append([cite(q), "«%s %s points» de potencia local al centrar en la media" % (v["kind"], v["number"]),
                     "%s pp (θ = %g, c = %g, n = %d)" % (f(m3["cost_pp"], 2), c3["theta_a8"], c3["c"], c3["n"]), "—",
                     "sí" if v["confirmed"] else "**no**",
                     "«about %d points»: coste de centrar %s pp (máx. sobre c: %s pp en c = %s); los %s pp son la brecha de RM a la envolvente, no el coste" % (
                         int(round(m3["cost_pp"] / 5) * 5), f(m3["cost_pp"], 1), f(m3["max_cost_pp_over_c"], 1), m3["c_at_max_cost"], f(m3["gap_rm_pp"], 1))])
    for key in ("1", "2", "4"):
        x = c[key]
        rows.append([cite(x["quote"]), "ítem %s de T5" % key, "ver Tabla T5", "—", "sí" if x["confirmed"] else "**no**", "—"])
    w("### (b) Frases del manuscrito v12 revisadas")
    w("")
    return rows


def master():
    t1, t3, t4, t5 = J("T1"), J("T3"), J("T4"), J("T5")
    rows = []
    for n, c in t3["cells"].items():
        for t, v in c["by_theta"].items():
            rows.append(["T3 E[S²] n = %s θ = %s" % (n, t), f(v["mean"], 5), "EE %s" % f(v["se"], 5), v["N"], "—", C.FAMILY["T3"],
                         F["T3"], "cells.%s.by_theta.%s.mean" % (n, t)])
    cr = t3["criterion_n20000_theta0"]
    rows.append(["T3 criterio z (39.67)", f(cr["z_literal"], 3), "—", t3["config"]["N"], "—", C.FAMILY["T3"], F["T3"],
                 "criterion_n20000_theta0.z_literal"])
    for n, v in t3["manuscript_simulated"].items():
        rows.append(["T3 z frente al manuscrito, n = %s" % n, f(v["z"], 3), "—", t3["config"]["N"], "—", C.FAMILY["T3"], F["T3"],
                     "manuscript_simulated.%s.z" % n])
    for r, v in t4["by_rho"].items():
        for q, x in v["quantities"].items():
            for n, m in x["median"].items():
                rows.append(["T4 mediana %s ρ = %s n = %s" % (QN[q], r, n), f(m, 5), "—", t4["config"]["N"], "—", C.FAMILY["T4"], F["T4"],
                             "by_rho.%s.quantities.%s.median.%s" % (r, q, n)])
            rows.append(["T4 pendiente %s ρ = %s" % (QN[q], r), f(x["slope"], 4), "IC [%s, %s]" % (f(x["slope_ci95"][0], 4), f(x["slope_ci95"][1], 4)),
                         t4["config"]["N"], "—", C.FAMILY["T4"], F["T4"], "by_rho.%s.quantities.%s.slope" % (r, q)])
    c = t5["claims"]
    rows.append(["T5.1 máx. |Δ| tamaño sin canal de varianza (pp)", f(c["1"]["max_abs_delta_pp"], 3), "—", c["1"]["N_sim"], c["1"]["N_cal"], "(A8)",
                 c["1"]["json"], "B2a.cells.%s.delta_pp" % c["1"]["cell"]])
    for k, v in c["2"]["operative"]["diff_pp"].items():
        rows.append(["T5.2 pérdida por rebalanceo %s (pp)" % k, f(v, 2), "—", "no registrado", c["2"]["N_cal"], "(A5)", c["2"]["json"],
                     "%s.%s" % (c["2"]["operative_config"], k)])
    c3 = c["3"]
    for t, v in c3["by_case"]["dm"].items():
        rows.append(["T5.3 coste de centrar, c = %g, θ = %s (pp)" % (c3["c"], t), f(v["cost_pp"], 3), "—", c3["N_sim"], c3["N_cal"], "(A8)",
                     c3["json"], "cases.dm.power.10.0.gls_t%s − rm_t%s" % (t, t)])
    for name, v in t1["figures"].items():
        rows.append(["T1 sha256 %s" % name, "`%s`" % v["sha256"], "—", "—", "—", C.FAMILY["T1"], F["T1"], "figures.%s.sha256" % name])
    return rows


def main():
    lines = []
    w = lines.append
    L = lines
    w("# Auditoría A11 — cierre para el manuscrito v12")
    w("")
    w("Generado por `experiments/audit11_generate_report.py` el %s desde los JSON de `experiments/results`. Commit de HEAD: `%s`. Protocolo: `%s`." % (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), C.git("rev-parse", "HEAD")[:7], PROTOCOL))
    w("")
    w("Reglas de A10 con sufijo `_audit11` y familias 120–129. No se edita ningún `.tex`: el fragmento de T2 se escribe en `experiments/results/` y las citas son al manuscrito v12 del zip.")
    w("")
    w("## 1. Resultados")
    w("")
    for fn in (sec_t0, sec_t1, sec_t2, sec_t3, sec_t4, sec_t5):
        fn(w, L)
    w("## 2. Criterios y compuertas")
    w("")
    gates(L)
    w("")
    w("## 3. Procedencia")
    w("")
    provenance_section(w, L)
    w("## 4. Desviaciones")
    w("")
    L.extend(table(["Qué", "Motivo", "Cuándo", "Efecto"], deviations()))
    w("")
    w("## 5. No ejecutado")
    w("")
    w("Nada: T0–T5 se ejecutaron completas. No se editó el manuscrito (ni `paper/*.tex` ni el zip v12).")
    w("")
    w("## 6. Conclusiones")
    w("")
    conclusions(w)
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    w("### (a) Anomalías numéricas")
    w("")
    anomalies(w)
    rows = manuscript_section(w)
    L.extend(table(["Manuscrito v12", "Frase / cifra", "Valor de A11", "z", "Se confirma", "Corrección sugerida"], rows))
    w("")
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    L.extend(table(["clave", "valor", "IC o EE", "N_sim", "N_cal", "familia", "archivo JSON", "ruta"], master()))
    w("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    C.register_outputs(__file__, [OUT])
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
