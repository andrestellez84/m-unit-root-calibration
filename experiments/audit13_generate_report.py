"""
Auditoria A13 - generador del reporte experiments/results/resultados_auditoria_13.md.

Solo lee JSON (regla 3 de A8: ningun numero de resultados escrito a mano; lo
comprueba tests/test_no_literals_audit13.py). Siete secciones y la tabla maestra de
los numeros nuevos.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402
import audit13_q_report as QR                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_13.md")
F = {"inv": "b130_inventory_audit13.json", "size": "e_size_audit13.json", "eq": "e_equalized_audit13.json",
     "calib": "e_calib_audit13.json", "dgp5": "e_dgp5_audit13.json", "awb": "e_awb_audit13.json",
     "awb_budget": "e_awb_budget_audit13.json", "app": "e_application_audit13.json", "tables": "tables_audit13.json",
     "t": "t_tables_audit13.json", "figs": "figures_audit13.json", "claims": "claims_audit13.json"}
TITLES = {"size": "tab:size — tamaño de RM-GLS bajo el paseo aleatorio gaussiano",
          "calib": "tab:calib — tamaño con valores críticos límite y de muestra finita",
          "localpower": "tab:localpower — potencia local, n = 2000",
          "dgp1": "tab:dgp1 — potencia frente a AR(1), caso constante, tamaño igualado",
          "ctpower": "tab:ctpower — potencia frente a AR(1) con tendencia, tamaño igualado",
          "dgp2": "tab:dgp2 — potencia con quiebre de media, tamaño igualado",
          "dgp3": "tab:dgp3 — rechazos con quiebre de varianza (nula verdadera)",
          "misspec": "tab:misspec — tamaño con colas pesadas y GARCH",
          "critB": "tab:critB — valores críticos de cola inferior",
          "awb": "tab:awb — calibración AWB frente a la simulada",
          "dgp5": "tab:dgp5 — experimento pre-registrado de dos canales",
          "fp": "tab:fp — aplicación pre-registrada"}
ORDER_E1 = ("size", "calib", "localpower", "dgp1", "ctpower", "dgp2", "dgp3", "misspec", "critB")
ORDER_E2 = ("awb", "dgp5", "fp")
_CACHE = {}


def J(k):
    name = F.get(k, k)
    if name not in _CACHE:
        _CACHE[name] = C.read_json(name)
    return _CACHE[name]


def f(x, d=4):
    return "—" if x is None else "%.*f" % (d, x)


def pp(x, d=2):
    return "%+.*f" % (d, x)


def src(name, path=""):
    return "`%s`%s" % (name, (" (`%s`)" % path) if path else "")


def md_cell(s):
    s = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", s)
    s = s.replace("\\RMGLS{}", "RM-GLS").replace("$<$", "<").replace("\\times10^{", "×10^").replace("\\%", "%")
    s = s.replace("$^\\dagger$", "†").replace("$^a$", "ᵃ").replace("MZ$_t$", "MZ_t").replace("$_t$", "_t")
    s = s.replace("\\multicolumn{2}{l}{", "").replace("\\theta", "θ").replace("\\rho", "ρ").replace("\\delta", "δ")
    s = s.replace("\\alpha", "α").replace("$", "").replace("{", "").replace("}", "").replace("|", "\\|")
    return s.strip()


def esc(c):
    return str(c).replace("\\|", "|").replace("|", "\\|")


def table(heads, rows):
    L = ["| " + " | ".join(esc(h) for h in heads) + " |", "|" + "---|" * len(heads)]
    L += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return L


def expand(cells):
    """Etiquetas por columna de una fila de encabezado con \\multicolumn."""
    out = []
    for c in cells:
        m = re.match(r"\\multicolumn\{(\d+)\}\{[a-z]\}\{(.*)\}$", c.strip())
        out += [md_cell(m.group(2))] * int(m.group(1)) if m else [md_cell(c)]
    return out


def tex_header(path):
    """Encabezado del tabular: filas antes de \\midrule, con los grupos de \\multicolumn antepuestos."""
    with open(os.path.join(C.REPO, path), encoding="utf-8") as fh:
        tex = fh.read()
    body = re.sub(r"\\begin\{tabular\}\{[^}]*\}", "", tex[tex.find("\\begin{tabular}"):])
    rows = []
    for pre, content, _ in TB.split_rows(body):
        if "\\midrule" in pre:
            break
        c = re.sub(r"\\(toprule|cmidrule\([a-z]*\)\{[^}]*\})", "", content).strip()
        if "&" in c:
            rows.append(expand(TB.cells_of(c)))
    if not rows:
        return []
    base = rows[-1]
    for g in rows[:-1]:
        base = [("%s %s" % (a, b)).strip() if a else b for a, b in zip(g + [""] * (len(base) - len(g)), base)]
    return base


# ---------------------------------------------------------------------------
# Seccion 1
# ---------------------------------------------------------------------------
def s_b130(w, L):
    inv = J("inv")
    p, sm = inv["protocol"], inv["seed_map"]
    w("### B13.0 — Protocolo, inventario y semillas")
    w("")
    w("- Protocolo `%s`: commit `%s` (%s); sha256 en disco `%s`, commiteado `%s` → %s." % (
        p["path"], p["commit_added"][:7], p["commit_time"], p["sha256_disk"], p["sha256_committed"],
        "coinciden" if p["sha256_disk"] == p["sha256_committed"] else "NO coinciden"))
    w("- Manuscrito de referencia `%s`: sha256 `%s` (%d bytes)." % (inv["manuscript"]["path"], inv["manuscript"]["sha256"],
                                                                 inv["manuscript"]["bytes"]))
    w("- Familias: %s. Celdas: %s." % (", ".join("%s = %d" % kv for kv in inv["families"].items()),
                                      "; ".join("%s: %d" % (k, len(v)) for k, v in inv["cells"].items() if v)))
    w("- Equivalencia `spawn_key` ↔ `.spawn`: %d flujos comprobados, %d discrepancias." % (
        inv["spawn_equivalence"]["streams_checked"], inv["spawn_equivalence"]["mismatches"]))
    w("- Colisiones (%s): %d flujos nuevos frente a %d previos (familias %d–%d, %d semillas enteras de A5–A7 y la 42): "
      "%d colisiones con las previas, %d dentro de A13." % (
          sm["method"], sm["new_streams_total"], sm["prior_streams_total"], min(sm["prior_families"]), max(sm["prior_families"]),
          sm["prior_integer_seeds"], sm["collisions_new_vs_prior"], sm["collisions_within_new"]))
    w("")
    L.extend(table(["JSON reutilizado", "sha256", "Bytes"], [[k, "`%s`" % v["sha256"], v["bytes"]] for k, v in inv["reused_json"].items()]))
    w("")
    L.extend(table(["Checkpoints reutilizados", "Archivos", "sha256 agregado"],
                   [[k, v["files"], "`%s`" % v["aggregate_sha256"]] for k, v in inv["reused_checkpoints"].items()]))
    w("")


def paso0_lines():
    """Filas (bloque, criterio, resultado, veredicto) de todos los Paso 0."""
    rows = []
    s = J("size")["paso0"]
    rows.append(["tab:size n ≤ 150 (familia 141)", "fila ligera = audit9_engine.row, %d caminos por celda" % s["reps"],
                 "máx. |Δ| = %.1e" % s["max_abs_diff"], "pasa" if s["max_abs_diff"] == 0 else "FALLA"])
    e = J("eq")["paso0"]
    rows.append(["Tamaño igualado (dgp1, ctpower, dgp2, dgp3)", "(a) filas frente a B5 de A8", "%.1e" % e["a_vs_a8_b5_worst"],
                 "pasa" if e["a_vs_a8_b5_worst"] == 0 else "FALLA"])
    rows.append(["", "(b) %d tasas frente a b103_equalized" % e["b_rates_compared"], "%.1e" % e["b_rates_vs_b103_max_abs_diff"],
                 "pasa" if e["b_rates_vs_b103_max_abs_diff"] == 0 else "FALLA"])
    rows.append(["", "(c) %d McNemar con θ = 0.02 frente a b103_equalized" % e["c_mcnemar_compared"],
                 "%.1e" % e["c_mcnemar_v13_vs_b103_max_abs_diff"], "pasa" if e["c_mcnemar_v13_vs_b103_max_abs_diff"] == 0 else "FALLA"])
    c = J("calib")["paso0"]
    rows.append(["tab:calib", "θ = 0.02 frente a b103_finite (%d hojas; %d diferencias de estructura)" % (
        c["leaves_compared"], c["structure_mismatches"]), "%.1e" % c["v13_vs_b103_finite_max_abs_diff"],
        "pasa" if c["passes"] else "FALLA"])
    d = J("dgp5")["paso0"]
    rows.append(["DGP 5", "(a) g1/g2 frente a A7 (%d series por celda)" % d["reps"], "%.1e" % d["a_components_max_abs_diff"],
                 "pasa" if d["a_components_max_abs_diff"] == 0 else "FALLA"])
    rows.append(["", "(b) θ = 0.02 frente a la caché de A10", "%.1e" % d["b_max_abs_diff"], "pasa" if d["b_max_abs_diff"] == 0 else "FALLA"])
    rows.append(["", "(c) tabla θ = 0.02 frente a b103_dgp5", "%.1e" % d["c_v13_table_vs_b103_max_abs_diff"],
                 "pasa" if d["c_v13_table_vs_b103_max_abs_diff"] == 0 else "FALLA"])
    a = J("awb")["paso0"]
    rows.append(["AWB", "estadístico observado frente a B9.1/B9.2", "%.1e" % a["stat_vs_rows_max_abs_diff"],
                 "pasa" if a["stat_vs_rows_max_abs_diff"] == 0 else "FALLA"])
    rows.append(["", "columna simulada θ = 0.02 frente a b103_awb", "%.1e" % a["sim_v13_vs_b103_awb_max_abs_diff"],
                 "pasa" if a["sim_v13_vs_b103_awb_max_abs_diff"] == 0 else "FALLA"])
    if C.have(F["app"]):
        ap = J("app")["paso0"]
        rows.append(["Aplicación", "(a) θ = 0.02 en las 50 primeras ventanas frente a A10", "%.1e" % ap["a_max_abs_diff"],
                     "pasa" if ap["a_max_abs_diff"] == 0 else "FALLA"])
        rows.append(["", "(b) resumen θ = 0.02 (con y sin AWB) frente a A10", "%.1e" % ap["b_summary_v13_vs_a10"],
                     "pasa" if ap["b_summary_v13_vs_a10"] == 0 else "FALLA"])
        rows.append(["", "(c) tamaño fuera de muestra θ = 0.02 frente a A10", "%.1e" % ap["c_oos_v13_vs_a10"],
                     "pasa" if ap["c_oos_v13_vs_a10"] == 0 else "FALLA"])
        rows.append(["", "(d) episodios a tasa común θ = 0.02 frente a A10", "%d" % ap["d_matched_episodes_v13_vs_a10"],
                     "pasa" if ap["d_matched_episodes_v13_vs_a10"] == 0 else "FALLA"])
    fg = J("figs")
    rows.append(["Figuras", "datos con θ = 0.02 y fuentes del v13 = datos de A11, llamada a llamada",
                 "%d de %d idénticas" % (sum(v["paso0_v13_data_identical_to_a11"] for v in fg["figures"].values()), len(fg["figures"])),
                 "pasa" if fg["paso0_all_identical"] else "FALLA"])
    for k, t in J("tables")["tables"].items():
        tr = t["transcription_v13"]
        rows.append(["Transcripción tab:%s" % k, "θ = 0.02 desde JSON = tabular del v13 (%d celdas; redondeo %s)" % (
            tr["cells_compared"], t["rounding"]), "%d distintas; %d doble redondeo del v13; %d negritas del v13" % (
            len(tr["number_mismatches"]), len(tr["double_rounding_in_v13"]), len(tr["bold_mismatches_in_v13"])),
            "pasa" if tr["passes"] else "FALLA"])
    if QR.have():
        rows += QR.paso0_rows()
    return rows


def table_block(w, L, key):
    tb = J("tables")["tables"][key]
    heads = tex_header(tb["tex"])
    rows = []
    as_column = all(r["section"] for r in tb["rows"])
    last = None
    for r in tb["rows"]:
        keys = [md_cell(k) for k in r["keys"]]
        span = re.match(r"\\multicolumn\{(\d+)\}", r["keys"][0])
        if span:
            keys += [""] * (int(span.group(1)) - 1)
        if as_column:
            keys = [md_cell(r["section"])] + keys
        elif r["section"] and r["section"] != last:
            rows.append(["*%s*" % md_cell(r["section"])] + [""] * (len(heads) - 1))
        last = r["section"]
        rows.append(keys + [md_cell(c) for c in r["theta0"]])
    if as_column:
        heads = ["Caso"] + heads
    w("**Tabla %s, con θ = 0.**" % TITLES[key])
    w("")
    L.extend(table(heads, rows))
    g = tb["gate"]
    tr = tb["transcription_v13"]
    w("")
    w("*Fuentes: %s. Tabular: `%s` (sha256 `%s`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = %s %s en `%s` "
      "(con signo %s). Transcripción del v13 (`%s`): %s. Negrita: fuera de la región exacta de la N de la celda.*" % (
          ", ".join("`%s`" % s for s in tb["sources"]), tb["tex"], tb["tex_sha256"], f(g["max_abs"], 4), g["units"], g["cell"],
          f(g["signed"], 4), tb["v13_file"], "reproduce" if tr["passes"] else "NO reproduce"))
    w("")


def s_e1(w, L):
    w("### B13.E(1) — Tablas desde JSON existentes, con θ = 0")
    w("")
    sz = J("size")
    w("tab:size en n ∈ {%s}: familia 141, N = %d por (caso, n), calibración de A10 (%s). Contraste informativo con B10.3.7 "
      "(familia 113, independiente) y diferencia pareada θ = 0 − θ = 0.02 sobre los caminos nuevos:" % (
          ", ".join(str(n) for n in sz["config"]["low_n"]), sz["config"]["N_low"],
          "; ".join("n = %s: N_cal %d" % (n, v["N_cal"]) for n, v in sz["calibration"].items())))
    w("")
    rows = []
    for k, v in sz["cells"].items():
        if "a10_lown" not in v:
            continue
        pdf = v["paired_theta0_minus_v13"]
        rows.append([k, f(v["rates"][C.PRIM]["rate"]), f(v["a10_lown"]["theta0"]["rate"]), f(v["rates"][C.PRIM_V13]["rate"]),
                     f(v["a10_lown"]["v13"]["rate"]), "%s (%s)" % (pp(pdf["delta"] * C.PP), f(pdf["se"] * C.PP, 2)),
                     f(v["size_with_cv_n20000"][C.PRIM]["rate"])])
    L.extend(table(["Celda", "θ = 0, familia 141", "θ = 0, B10.3.7", "θ = 0.02, familia 141", "θ = 0.02, B10.3.7 (v13)",
                    "θ = 0 − θ = 0.02 pareada (pp, EE)", "θ = 0 con el VC de n = 20 000"], rows))
    w("")
    for key in ORDER_E1:
        table_block(w, L, key)
    cal = J("calib")["cases_by_theta"]
    w("Notas de tab:calib: q(20 000) = %s (constante) y %s (tendencia) con θ = 0; con θ = 0.02, %s y %s. "
      "KS frente a n = 20 000 con θ = 0 (umbral %s), caso constante: %s; tendencia: %s." % (
          f(cal[C.PRIM]["c"]["cv_n20000"]), f(cal[C.PRIM]["ct"]["cv_n20000"]), f(cal[C.PRIM_V13]["c"]["cv_n20000"]),
          f(cal[C.PRIM_V13]["ct"]["cv_n20000"]), f(J("calib")["config"]["ks_threshold"]),
          "; ".join("n = %s: D %s" % (n, f(v["D"])) for n, v in cal[C.PRIM]["c"]["ks"].items()),
          "; ".join("n = %s: D %s" % (n, f(v["D"])) for n, v in cal[C.PRIM]["ct"]["ks"].items())))
    w("")
    ms = J("tables")["tables"]["misspec"]["mean_shift"]
    w("Desplazamiento medio GARCH de RM-GLS (pp, EE): %s." % "; ".join(
        "n = %s: θ = 0 %s (%s), θ = 0.02 %s (%s), %d celdas" % (n, pp(v["mean_pp"]), f(v["se_pp"], 2), pp(ms["v13"][n]["mean_pp"]),
                                                             f(ms["v13"][n]["se_pp"], 2), len(v["cells"])) for n, v in ms["theta0"].items()))
    w("")
    se = J("tables")["tables"]["critB"]["max_bootstrap_se"]
    w("tab:critB: EE bootstrap máximo de los cuantiles: θ = 0 %s; θ = 0.02 %s." % (f(se["%g" % C.THETA]), f(se["%g" % C.THETA_V13])))
    w("")


def s_e2(w, L):
    w("### B13.E(2) — AWB, DGP 5 y aplicación con θ = 0")
    w("")
    b = J("awb_budget")
    aw = J("awb")
    w("**AWB (familia 142).** Presupuesto: %s h; sonda (s/serie): %s; proyección %s h → %s. Estadístico %s; B = %d; %s; semilla %s; "
      "columna simulada: %s." % (f(b["budget_hours"], 1), ", ".join("n = %s: %s" % (k, f(v, 4)) for k, v in b["probe_sec_per_series"].items()),
                                 f(b["projected_total_hours"], 2), "se lanza" if b["within_budget"] else "NO se lanza",
                                 aw["config"]["statistic"], aw["config"]["B"], aw["config"]["residuals"], aw["config"]["seed"],
                                 aw["config"]["sim_calibration"]))
    w("")
    table_block(w, L, "awb")
    r = aw["rule"]
    w("Regla B9.5 (informativa): (i) %d de %d celdas de DGP 3 dentro (mínimo %d): %s; (ii) pérdida de potencia %s pp (umbral %s): %s. "
      "Recomendar AWB: %s." % (r["i_in_region_dgp3"], r["i_of"], r["i_min"], "sí" if r["i_holds"] else "no",
                               ", ".join("%s %s" % (k, f(v, 2)) for k, v in r["ii_power_loss_pp"].items()), f(r["ii_threshold_pp"], 1),
                               "sí" if r["ii_holds"] else "no", "sí" if r["recommend_awb"] else "no"))
    w("")
    d5 = J("dgp5")
    w("**DGP 5.** Trayectorias: %s; umbral igualado de RM-GLS θ = 0: %s (θ = 0.02: %s); celda de calibración `%s`; "
      "N = %d, B = %d." % (d5["config"]["trajectories"], f(d5["threshold_primary"]), f(d5["threshold_v13"]), d5["calibration_cell"],
                           d5["config"]["N_sim"], d5["config"]["B"]))
    w("")
    table_block(w, L, "dgp5")
    if not C.have(F["app"]):
        w("**Aplicación:** sin JSON (no ejecutada).")
        w("")
        return
    ap = J("app")
    w("**Aplicación (familia 143).** Hashes de los datos congelados: %s; `experiments/protocol.md`: %s. Nula: %s." % (
        ", ".join("%s %s" % (k, "coincide" if v["match"] else "NO coincide") for k, v in ap["data_hashes"].items()),
        "coincide" if ap["protocol_hash"]["match"] else "NO coincide", ap["config"]["null"]))
    w("")
    table_block(w, L, "fp")
    rows = []
    for D in ap["oos_size"]["by_D"]:
        a, v, x = ap["oos_size"]["by_D"][D], ap["oos_size_v13"]["by_D"][D], ap["oos_size_awb"]["by_D"][D]
        rows.append([D, f(a["rate"]) + ("" if a["in_region"] else " (fuera)"), f(v["rate"]), f(x["rate"]) + ("" if x["in_region"] else " (fuera)")])
    w("Tamaño fuera de muestra (N = %d, región %s):" % (ap["oos_size"]["N"], ap["oos_size"]["region"]))
    w("")
    L.extend(table(["D", "RM-GLS θ = 0", "RM-GLS θ = 0.02 (v13)", "RM-GLS θ = 0, AWB"], rows))
    w("")
    m, mv = ap["matched_rate"], ap["matched_rate_at_v13_target"]
    w("Tasa común (mecanismo registrado): objetivo %s (FP agregada de RM-GLS θ = 0). Informativo, al objetivo del v13 (%s): %s." % (
        f(m["target_fpr_pooled_primary"]), f(mv["target_fpr"]),
        "; ".join("%s: %d episodios, latencia censurada %s" % (k, v["false_alarm_episodes"], f(v["censored_latency_mean"], 1))
                  for k, v in mv["tests"].items())))
    w("")
    w("Celdas adversas bajo la regla registrada: θ = 0 %d; θ = 0.02 %d." % (len(ap["adverse_cells_primary"]), len(ap["adverse_cells_v13"])))
    w("")
    rows = [[d["id"], d["element"], d["preregistered_value"], d["deployed_value"],
             "FP %s (máx. %s); %d detecciones; latencia %s" % (f(d["effect_before"]["fp_mean"]), f(d["effect_before"]["fp_max"]),
                                                             d["effect_before"]["detections"], f(d["effect_before"]["mean_latency_detected"], 1)),
             "FP %s (máx. %s); %d detecciones; latencia %s" % (f(d["effect_after"]["fp_mean"]), f(d["effect_after"]["fp_max"]),
                                                             d["effect_after"]["detections"], f(d["effect_after"]["mean_latency_detected"], 1))]
            for d in ap["deviation_rows"]]
    w("Filas para tab:deviations:")
    w("")
    L.extend(table(["Id", "Elemento", "Antes", "Después", "Efecto antes", "Efecto después"], rows))
    w("")


def s_e3(w, L):
    fg = J("figs")
    w("### B13.E(3) — Figuras `_audit13`")
    w("")
    L.extend(table(["Figura", "sha256", "Bytes", "Copia", "sha256 de datos", "Paso 0"],
                   [[k, "`%s`" % v["sha256"], v["bytes"], v["paper_copy"], "`%s`" % v["data_sha256"],
                     "idéntica a A11" if v["paso0_v13_data_identical_to_a11"] else "DISTINTA"] for k, v in fg["figures"].items()]))
    w("")
    w("*Fuentes que dependen de θ: %s; sin dependencia de θ: %s. Puntos de la figura de ganancia de calibración en "
      "`figures_audit13.json` (`calibration_gain_points`).*" % (", ".join("`%s`" % s for s in fg["sources_theta_dependent"]),
                                                               ", ".join("`%s`" % s for s in fg["sources_theta_free"])))
    w("")


def s_t(w, L):
    t = J("t")
    w("### B13.T — Tablas nuevas desde JSON de A12")
    w("")
    w("**tab:serial — tamaño al valor crítico iid por estructura de error.** Negrita: fuera de la región exacta %s (N = 20 000)." %
      t["serial"]["exact_region_20000"])
    w("")
    L.extend(t["serial"]["markdown"].split("\n"))
    w("")
    w("*Fuente: `bA_ma_audit12.json` (`size.<celda>.iid`, `bartlett_factor_at_median_B`). Tabular: `%s` (sha256 `%s`).*" % (
        t["serial"]["tex"], t["serial"]["tex_sha256"]))
    w("")
    w("**tab:serialpower — potencia ajustada al tamaño en las mismas celdas.**")
    w("")
    L.extend(t["serialpower"]["markdown"].split("\n"))
    w("")
    w("*Fuente: `bA_ma_audit12.json` (`power.pw_*.adjusted`). Tabular: `%s` (sha256 `%s`).*" % (
        t["serialpower"]["tex"], t["serialpower"]["tex_sha256"]))
    w("")
    w("**tab:initial — condición inicial (B12.C completa).** u₀ = α/√(1−ρ²); «aleatoria»: z₀/√(1−ρ²).")
    w("")
    L.extend(t["initial"]["markdown"].split("\n"))
    w("")
    w("*Fuente: `bC_initial_audit12.json` (`cells`); N = %d por celda; valores críticos iid de n = %d. Tabular: `%s` (sha256 `%s`).*" % (
        t["initial"]["rows"][0]["N"], t["initial"]["config"]["n"], t["initial"]["tex"], t["initial"]["tex_sha256"]))
    w("")


def claim_value(v):
    if isinstance(v, bool):
        return "sí" if v else "no"
    if isinstance(v, int):
        return "%d" % v
    if isinstance(v, float):
        return "%.2e" % v if v and abs(v) < 10 ** -3 else f(v, 4)
    if isinstance(v, dict):
        return "{" + ", ".join("%s: %s" % (a, claim_value(b)) for a, b in v.items()) + "}"
    if isinstance(v, list):
        return "[" + ", ".join(claim_value(b) for b in v) + "]"
    return str(v)


def s_claims(w, L):
    cl = J("claims")
    w("### Cifras del texto del v13 que dependen de θ")
    w("")
    w("Cada cifra se recalcula desde JSON con las fuentes del v13 (θ = 0.02) y con las de A13 (θ = 0). No se reescribe ninguna frase.")
    w("")
    rows = []
    for k, v in cl["claims"].items():
        rows.append([k, "`%s:%d`" % (v["file"], v["line"]), ", ".join(v["printed"]) or "—",
                     ", ".join(claim_value(x) for x in v["v13"]) or "—",
                     "sí" if v["reproduced"] else "**no**", ", ".join(claim_value(x) for x in v["theta0"]) or "—",
                     "; ".join("%s: %s" % (a, claim_value(b)) for a, b in v["extra_theta0"].items()) or "—"])
    L.extend(table(["Clave", "Archivo:línea", "Impreso", "θ = 0.02 recalculado", "¿Reproduce?", "θ = 0", "Datos adicionales (θ = 0)"], rows))
    w("")
    w("Menciones literales de θ = 0.02 en el texto: %s." % "; ".join("`%s:%d`" % (v["file"], v["line"]) for v in cl["theta_mentions"].values()))
    w("")


# ---------------------------------------------------------------------------
# Secciones 2-7 y tabla maestra
# ---------------------------------------------------------------------------
def s_gates(w, L):
    w("## 2. Compuertas")
    w("")
    w("**Compuerta informativa de B13.E (no detiene nada).** Máxima diferencia entre la versión con θ = 0 y la publicada con θ = 0.02:")
    w("")
    rows = [["tab:%s" % k, f(t["gate"]["max_abs"], 4), t["gate"]["units"], t["gate"]["cell"], f(t["gate"]["signed"], 4), t["gate"]["cells"]]
            for k, t in J("tables")["tables"].items()]
    L.extend(table(["Tabla", "máx. |Δ|", "Unidades", "Celda", "Δ con signo", "Celdas comparadas"], rows))
    w("")
    w("**Paso 0 (máx. |Δ| = 0).**")
    w("")
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], paso0_lines()))
    w("")


def s_prov(w, L):
    w("## 3. Procedencia")
    w("")
    man = C.read_json("manifest_audit13.json")["entries"]
    rows = [[k, "`%s`" % v["sha256"], v["script"], v["commit"][:7], "sí" if v["code_all_committed"] else "no"]
            for k, v in sorted(man.items()) if k.endswith(".json") and "manifest" not in k]
    L.extend(table(["Archivo", "sha256", "Script", "Commit", "Código commiteado"], rows))
    w("")
    rows = [[k, "`%s`" % v["sha256"]] for k, v in sorted(man.items()) if k.endswith((".tex", ".pdf"))]
    L.extend(table(["Tabular o figura", "sha256"], rows))
    w("")
    v = J("inv")["provenance"]["versions"]
    w("Versiones: %s." % ", ".join("%s %s" % kv for kv in v.items()))
    w("")


def s_dev(w, L):
    w("## 4. Desviaciones")
    w("")
    rounding = {k: t["rounding"] for k, t in J("tables")["tables"].items()}
    half = [k for k, r in rounding.items() if r == "half_up"]
    rows = [["Convención de redondeo por tabla: la que reproduce el v13 (binario de Python en %s; mitad hacia arriba sobre el decimal en %s)" % (
        ", ".join(k for k, r in rounding.items() if r == "binary"), ", ".join(half) or "ninguna"),
             "El v13 no usa una convención única: las tablas de N = 2000 se transcribieron desde el reporte de A10 a 4 decimales",
             "Después de ver el Paso 0 de transcripción", "Sólo formato; las celdas con θ = 0 usan la misma convención que su tabla"],
            ["La negrita del tabular con θ = 0 sigue la regla de cada nota (fuera de la región exacta), también donde el v13 la omitió",
             "Regla escrita en la nota de la tabla", "Al construir el exportador", "Negritas nuevas listadas en §7(b)"],
            ["tab:size en n ≤ 150: la versión con θ = 0 usa caminos nuevos (familia 141) y la publicada los de B10.3.7 (familia 113)",
             "Encargo literal (lectura 4)", "Antes de calcular", "La compuerta en esas celdas mezcla ruido independiente; la diferencia pareada va en §1"],
            ["Las figuras van a `experiments/figures/` (la carpeta de A11) y a `paper/figures/`; la lectura 12 decía `figures/`",
             "Convención de A11", "Antes de dibujar", "Ninguno"],
            ["El mismo exportador escribe también los tabulares de tab:awb, tab:dgp5 y tab:fp (bloque E(2))",
             "Lectura 15", "Antes de calcular", "Ninguno"]]
    if QR.have():
        rows += QR.dev_rows()
    L.extend(table(["Desviación", "Motivo", "Cuándo", "Efecto"], rows))
    w("")


def s_not(w, L):
    w("## 5. No ejecutado")
    w("")
    if QR.have():
        QR.not_executed(w)
    else:
        w("- **B13.Q**: pendiente hasta que el autor entregue el `.tex` de v14 (lectura 16). No se usó ningún v14.")
    w("- **B12.D**: sigue cancelado por el encargo.")
    w("- **tab:deviations** no se exporta como tabular porque sus celdas son texto. Las cifras están en §1 (aplicación) y en la tabla de cifras del texto.")
    w("")


def s_concl(w, L):
    w("## 6. Conclusiones")
    w("")
    tabs = J("tables")["tables"]
    w("- Todos los Paso 0 se cumplen: %s." % ("sí" if all(r[3] == "pasa" for r in paso0_lines()) else "NO (ver §2)"))
    w("- Las %d tablas regeneradas reproducen el v13 con θ = 0.02 desde JSON en todas sus celdas numéricas, salvo las erratas del "
      "v13 listadas en §7(b)." % len(tabs))
    big = max(((k, t["gate"]) for k, t in tabs.items() if t["gate"]["units"] == "pp"), key=lambda kv: kv[1]["max_abs"])
    w("- La mayor diferencia en pp entre θ = 0 y θ = 0.02 es %s pp (tab:%s, `%s`)." % (f(big[1]["max_abs"], 2), big[0], big[1]["cell"]))
    r = J("awb")["rule"]
    w("- AWB con θ = 0: la regla B9.5 %s recomienda la variante (%d de %d celdas de DGP 3 dentro; pérdida máxima %s pp)." % (
        "sí" if r["recommend_awb"] else "no", r["i_in_region_dgp3"], r["i_of"], f(max(r["ii_power_loss_pp"].values()), 2)))
    cl = J("claims")
    w("- De las %d cifras del texto del v13 localizadas, %d se reproducen desde JSON con θ = 0.02; las demás están en §7(b)." % (
        len(cl["claims"]), len(cl["claims"]) - len(cl["not_reproduced"])))
    w("- B13.T: tres tabulares nuevos (tab:serial, tab:serialpower, tab:initial) sólo desde JSON de A12.")
    if QR.have():
        QR.conclusions(w)
    w("")


def s_anom(w, L):
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    w("### (a) Anomalías numéricas")
    w("")
    sz = J("size")
    out = [k for k, v in sz["cells"].items() if not v["rates"][C.PRIM]["in_region"]]
    for k in out:
        v = sz["cells"][k]["rates"][C.PRIM]
        w("- tab:size con θ = 0, celda `%s`: %s [%s, %s], fuera de la región exacta de N = %d." % (
            k, f(v["rate"]), f(v["wilson_lower"]), f(v["wilson_upper"]), v["n"]))
    ct = J("calib")["cases_by_theta"][C.PRIM]["ct"]["approximation_cost"]
    w("- Con θ = 0, en el caso de tendencia el valor crítico de n = 20 000 da estos tamaños: %s. Con θ = 0.02 se quedaban dentro o cerca "
      "de la región (tab:calib)." % "; ".join("n = %s: %s" % (n, f(v["size_with_cv_n20000"]["rate"])) for n, v in ct.items()))
    if C.have(F["app"]):
        ap = J("app")
        for lab, blk in (("RM-GLS θ = 0", "oos_size"), ("RM-GLS θ = 0, AWB", "oos_size_awb")):
            for D, v in ap[blk]["by_D"].items():
                if not v["in_region"]:
                    w("- Aplicación, tamaño fuera de muestra de %s a D = %s: %s, fuera de la región %s (N = %d)." % (
                        lab, D, f(v["rate"]), ap[blk]["region"], v["n"]))
    for k, v in J("claims")["claims"].items():
        for a, b in v["extra_theta0"].items():
            vb = v["extra_v13"].get(a)
            if isinstance(b, bool) and vb is not None and b != vb:
                w("- `%s` (`%s:%d`): «%s» vale %s con θ = 0.02 y %s con θ = 0." % (k, v["file"], v["line"], a, claim_value(vb), claim_value(b)))
    w("")
    w("### (b) Erratas del v13 halladas en la transcripción")
    w("")
    for k, t in J("tables")["tables"].items():
        tr = t["transcription_v13"]
        for m in tr["double_rounding_in_v13"]:
            w("- tab:%s, fila %s, columna %d: impreso %s; el valor del JSON es %s y a %d decimales da %s. El impreso es un doble redondeo." % (
                k, " / ".join(m["row"]), m["col"], m["printed"], f(m["value"], 6), TB.decimals(m["printed"]), md_cell(m["mine"])))
        for m in tr["bold_mismatches_in_v13"]:
            w("- tab:%s, fila %s%s, columna %d: el v13 imprime %s sin negrita, pero la cifra está fuera de la región de la nota." % (
                k, (m["section"] + " / ") if m["section"] else "", " / ".join(m["row"]), m["col"], md_cell(m["printed"])))
        for m in tr["number_mismatches"]:
            w("- tab:%s: celda no reproducida: %s." % (k, m))
    for k in J("claims")["not_reproduced"]:
        v = J("claims")["claims"][k]
        w("- Texto `%s:%d` (`%s`): impreso %s; recalculado con θ = 0.02: %s (%s)." % (
            v["file"], v["line"], k, ", ".join(v["printed"]), ", ".join(claim_value(x) for x in v["v13"]),
            "; ".join("%s: %s" % (a, claim_value(b)) for a, b in v["extra_v13"].items()) or "sin datos adicionales"))
    w("")
    w("### (c) Frases del v13 cuya cifra cambia con θ = 0")
    w("")
    rows = []
    for k, v in J("claims")["claims"].items():
        new = []
        for g, x, x13 in zip(v["printed"], v["theta0"], v["v13"]):
            if g in C8_WORDS():
                new.append({n: word for word, n in C8_WORDS().items()}.get(round(x), "%d" % round(x)))
                continue
            if re.fullmatch(r"\d+", g):
                new.append("%d" % round(x))
                continue
            d = TB.decimals(g)
            mode = "half_up" if TB.fdec(x13, d, "binary") != g and TB.fdec(x13, d, "half_up") == g else "binary"
            new.append(TB.fdec(x, d, mode))
        if new != v["printed"]:
            rows.append(["`%s:%d`" % (v["file"], v["line"]), k, ", ".join(v["printed"]), ", ".join(new)])
    L.extend(table(["Archivo:línea", "Clave", "Impreso (θ = 0.02)", "Con θ = 0, mismos decimales"], rows))
    w("")
    if QR.have():
        QR.anomalies(w)


def C8_WORDS():
    import audit13_claims as CL
    return CL.WORDS


def master(w, L):
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    rows = []
    sz = J("size")
    for k, v in sz["cells"].items():
        r = v["rates"][C.PRIM]
        fam = C.FAMILY["TAB"] if "a10_lown" in v else J("b101_theta_audit10.json")["provenance"]["seed_family"]
        ncal = sz["calibration"][str(v["n"])]["N_cal"] if str(v["n"]) in sz["calibration"] else J("b101_theta_audit10.json")["config"]["N_cal"]
        path = "cells.%s.rates.%s" % (k, C.PRIM)
        rows.append(["tab:size %s" % k, f(r["rate"]), "[%s, %s]" % (f(r["wilson_lower"]), f(r["wilson_upper"])), r["n"], ncal, fam,
                     F["size"], path])
    cal = J("calib")
    for case, c in cal["cases_by_theta"][C.PRIM].items():
        for n, v in c["approximation_cost"].items():
            for lab, leaf in (("tamaño en q(n)", "size_with_cv_at_n"), ("tamaño en q(20 000)", "size_with_cv_n20000")):
                rr = v[leaf]
                rows.append(["tab:calib %s n=%s %s" % (case, n, lab), f(rr["rate"]), "EE %s" % f(rr["se"]), rr["n"],
                             cal["config"]["calibration_by_n"][n], "102 / 104", F["calib"],
                             "cases_by_theta.%s.%s.approximation_cost.%s.%s" % (C.PRIM, case, n, leaf)])
            rows.append(["tab:calib %s n=%s q_0.05(n)" % (case, n), f(v["cv_at_n"]), "—", "—", cal["config"]["calibration_by_n"][n],
                         "102 / 104", F["calib"], "cases_by_theta.%s.%s.approximation_cost.%s.cv_at_n" % (C.PRIM, case, n)])
    b92 = J("b92_theta_audit9.json")
    for case, lp in b92["local_power"].items():
        for c, v in lp["power"].items():
            rows.append(["tab:localpower %s c=%s" % (case, c), f(v[C.PRIM]), "—", b92["config"]["N_power"], b92["config"]["N_cal"],
                         b92["provenance"]["seed_family"], "b92_theta_audit9.json", "local_power.%s.power.%s.%s" % (case, c, C.PRIM)])
    eq = J("eq")
    for k, v in eq["cells"].items():
        r = v["rates_sim"][C.PRIM]
        mc = v["mcnemar_primary_vs_sim"]["dfgls"]
        rows.append(["%s RM-GLS θ=0" % k, f(r["rate"]), "EE %s; McNemar p vs DF-GLS %s" % (f(r["se"]), "%.3g" % mc["p_value"]), r["n"],
                     "500000", 95, F["eq"], "cells.%s.rates_sim.%s" % (k, C.PRIM)])
    for k, v in b92["misspec"].items():
        if k.startswith("c|"):
            r = v["rates"][C.PRIM]
            rows.append(["tab:misspec %s" % k, f(r["rate"]), "EE %s" % f(r["se"]), r["n"], b92["config"]["N_cal"], "A7/A8",
                         "b92_theta_audit9.json", "misspec.%s.rates.%s" % (k, C.PRIM)])
    cvj = J("b103_cv_audit10.json")
    for k, v in cvj["table"].items():
        if v["theta"] == C.THETA:
            for a, x in v["cv"].items():
                rows.append(["tab:critB %s α=%s" % (k, a), f(x), "EE %s" % f(v["se"][a]), "—", cvj["config"]["N_cal"], 107,
                             "b103_cv_audit10.json", "table.%s.cv.%s" % (k, a)])
    aw = J("awb")
    for k, v in aw["cells"].items():
        for lab in ("awb", "sim"):
            rr = v[lab]
            rows.append(["tab:awb %s %s" % (k, lab), f(rr["rate"]), "[%s, %s]" % (f(rr["wilson_lower"]), f(rr["wilson_upper"])), rr["n"],
                         "B = %d" % aw["config"]["B"] if lab == "awb" else "500000", C.FAMILY["AWB"] if lab == "awb" else 95, F["awb"],
                         "cells.%s.%s" % (k, lab)])
    d5 = J("dgp5")
    for k, v in d5["cells"].items():
        rr = v["size_matched"]["primary"]
        rows.append(["tab:dgp5 %s" % k, f(rr["rate"]), "EE %s" % f(rr["se"]), rr["n"], d5["config"]["N_cal_equalized"], 60, F["dgp5"],
                     "cells.%s.size_matched.primary" % k])
    if C.have(F["app"]):
        ap = J("app")
        for t in ("final", "final_awb"):
            s = ap["summary"][t]
            for m in ("fp_mean", "fp_max", "detections", "mean_latency_detected"):
                rows.append(["tab:fp %s %s" % (t, m), claim_value(s[m]), "—", "—", ap["config"]["N_cal"],
                             C.FAMILY["APP"] if t == "final_awb" else "—", F["app"], "summary.%s.%s" % (t, m)])
            mt = ap["matched_rate"]["tests"][t]
            for m in ("false_alarm_episodes", "mean_run_length", "censored_latency_mean"):
                rows.append(["tab:fp %s %s" % (t, m), claim_value(mt[m]), "—", "—", ap["config"]["N_cal"],
                             C.FAMILY["APP"] if t == "final_awb" else "—", F["app"], "matched_rate.tests.%s.%s" % (t, m)])
        for D, v in ap["oos_size"]["by_D"].items():
            rows.append(["aplicación tamaño fuera de muestra D=%s" % D, f(v["rate"]), "EE %s" % f(v["se"]), v["n"], ap["config"]["N_cal"], 106,
                         F["app"], "oos_size.by_D.%s" % D])
    if QR.have():
        rows += QR.master_rows(f)
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"], rows))
    w("")


def main():
    L = []

    def w(s):
        L.append(s)
    inv = J("inv")
    w("# Auditoría A13 — Regeneración con θ = 0 y cierre")
    w("")
    w("Protocolo `%s` (commit `%s`). Manuscrito de referencia: `%s` (sha256 `%s`), de sólo lectura; no se editó ningún `.tex`. "
      "Orden del encargo: B13.0 → E(1) → E(2) → E(3) → T. %s" % (
          inv["protocol"]["path"], inv["protocol"]["commit_added"][:7], inv["manuscript"]["path"], inv["manuscript"]["sha256"],
          ("B13.Q se ejecutó sobre `%s` (sha256 `%s`) según la enmienda `%s` (commit `%s`); ese manuscrito tampoco se editó." % (
              QR.J("inv")["manuscript"]["path"], QR.J("inv")["manuscript"]["sha256"], QR.J("inv")["amendment"]["path"],
              QR.J("inv")["amendment"]["commit_added"][:7])) if QR.have() else "B13.Q queda pendiente de v14."))
    w("")
    w("## 1. Resultados")
    w("")
    s_b130(w, L)
    s_e1(w, L)
    s_e2(w, L)
    s_e3(w, L)
    s_t(w, L)
    s_claims(w, L)
    if QR.have():
        QR.section(w, L, table, md_cell)
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
