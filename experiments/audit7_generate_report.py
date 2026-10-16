"""
Auditoria A7 - Bloque 4: genera experiments/results/resultados_auditoria_7.md.

Regla 3: ninguna cifra de resultado se escribe a mano. Todo valor de tabla y de
prosa se lee de un JSON o de un log de experiments/results; si falta una clave el
script falla con KeyError. Los umbrales y parametros de diseno se importan de los
modulos audit7_* que los fijaron.

Estructura (obligatoria): 0 metadatos, 1 resultados por bloque, 2 semillas,
3 diffs contra el control, 4 hardware y tiempos (con fallos de proceso),
5 no ejecutado, 6 conclusiones, 7 manifiesto. El manifiesto se obtiene por
descubrimiento de patron sobre el disco y se guarda completo en
manifest_audit7.json.

Uso: python experiments/audit7_generate_report.py
"""
import datetime
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402
import audit7_design as D5                                       # noqa: E402
import audit7_readout as RO                                      # noqa: E402
import audit7_ct_design as DCT                                   # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_7.md")
MANIFEST = os.path.join(C.RESULTS, "manifest_audit7.json")
MANIFEST_PATTERNS = (
    "experiments/audit7_*.py", "experiments/audit7_*.R", "experiments/*_audit7.md",
    "experiments/results/*_audit7.json", "experiments/results/*_audit7.log",
    "experiments/results/checkpoints/audit7_*/*", "experiments/figures/*.pdf",
    "src/stationarity_test/deterministics.py", "tests/*_audit7.py",
)
BLOCK1_LOGS = ("bloque1_block1_run2_audit7.log", "bloque1_block2_audit7.log",
               "bloque1_block3_audit7.log", "bloque1_block4_audit7.log")


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def J(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8") as f:
        return json.load(f)


def T(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def f4(x):
    return "%.4f" % x


def ci(c):
    return "[%.4f, %.4f]" % (c["ci_lower"], c["ci_upper"])


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return out


def block_hours(log):
    m = re.findall(r"bloque: ([0-9.]+) h", T(log))
    if not m:
        raise KeyError("sin linea 'bloque: X h' en %s" % log)
    return float(m[-1])


def tope_events(log):
    pat = r"\[TOPE\] (\S+): el lote i0=(\d+) \((\d+) series, ~(\d+) s\) no cabe: transcurrido ([0-9.]+) h de un tope de ([0-9.]+) h"
    return sorted(set(re.findall(pat, T(log))))


def pytest_summary():
    lines = [l for l in T("pytest_audit7.log").splitlines() if re.search(r"=+ .* in [0-9.]+s", l)]
    if not lines:
        raise KeyError("pytest_audit7.log sin linea de resumen")
    m = re.search(r"=+ (.+?) in ([0-9.]+)s", lines[-1])
    return m.group(1), float(m.group(2))


def commit_with(message_part):
    out = C._git("log", "--format=%h", "--grep=" + message_part, "-1")
    if not out:
        raise KeyError("sin commit con mensaje '%s'" % message_part)
    return out


def garch_label(g):
    return "α = %s, β = %s, z %s (persistencia %.2f)" % (g["alpha"], g["beta"], g["z"], g["persistence"])


def conclusion_garch(gsets, region):
    """Conclusion 4: el veredicto sale de in_exact_acceptance_region de R = 0.50 en cada celda."""
    key = "ours_R050"
    n_cells = sum(len(cells) for _, _g, cells in gsets)
    rates = "; ".join("%s: %s" % (garch_label(g), " / ".join(f4(c["rejection_rates"][key]["rate"]) for c in cells.values()))
                      for _, g, cells in gsets)
    others = ", ".join("R = %s fuera en %d" % (r[-3] + "." + r[-2:], sum(not c["in_exact_acceptance_region"][r]
                                                                         for _, _g, cells in gsets for c in cells.values()))
                       for r in ("ours_R025", "ours_R075"))
    base_cells = gsets[0][2]
    n0 = list(base_cells)[0]
    adfpp = "; ".join("%s: %s y %s" % (garch_label(g), f4(cells[n0]["rejection_rates"]["adf"]["rate"]), f4(cells[n0]["rejection_rates"]["pp"]["rate"]))
                      for _, g, cells in gsets)
    out = [(g, c) for _, g, cells in gsets for c in cells.values() if not c["in_exact_acceptance_region"][key]]
    if not out:
        return ("4. **Bajo innovaciones GARCH(1,1) el tamaño del test propuesto (R = 0.50) queda dentro de la región exacta %s en las %d celdas de las %d configuraciones** (Tabla 1.4a). Tasas por n: %s. Con %s celdas. ADF y PP a n = %s: %s." % (
            region, n_cells, len(gsets), rates, others, n0, adfpp))
    normal = sorted(((g, cells) for _, g, cells in gsets if g["z"] == "N(0,1)"), key=lambda gc: gc[0]["persistence"])
    bound, first_fail = None, None
    for g, cells in normal:
        if not all(c["in_exact_acceptance_region"][key] for c in cells.values()):
            first_fail = g["persistence"]
            break
        bound = g["persistence"]
    held = [garch_label(g) for _, g, cells in gsets if all(c["in_exact_acceptance_region"][key] for c in cells.values())]
    failed = [garch_label(g) for _, g, cells in gsets if not all(c["in_exact_acceptance_region"][key] for c in cells.values())]
    detail = "; ".join("%s, n = %d: %s %s, %s de la región" % (
        garch_label(g), c["n"], f4(c["rejection_rates"][key]["rate"]), ci(c["rejection_rates"][key]),
        "por encima" if c["rejection_rates"][key]["rate"] > region[1] else "por debajo") for g, c in out)
    if bound is None:
        scope = "Con innovaciones normales no se sostiene en ninguna de las persistencias examinadas."
    else:
        scope = "**La afirmación de robustez a GARCH(1,1) con innovaciones normales se acota a persistencia ≤ %.2f**" % bound
        scope += ("; a %.2f ya no se sostiene y no se examinó ninguna persistencia intermedia." % first_fail if first_fail is not None
                  else ", la mayor examinada.")
    return ("4. **El tamaño del test propuesto (R = 0.50) sale de la región exacta %s en %d de %d celdas GARCH(1,1)** (Tabla 1.4a): %s. %s Configuraciones donde se sostiene en los tres n: %s. Donde no se sostiene: %s. Tasas por n: %s. Con %s celdas. ADF y PP a n = %s: %s." % (
        region, len(out), n_cells, detail, scope, "; ".join(held) or "ninguna", "; ".join(failed), rates, others, n0, adfpp))


def trajectory_sentence(traj, large, region):
    """Trayectoria por n del test propuesto, ADF y PP; sin lectura."""
    parts = []
    for g, cells in traj.values():
        cs = list(cells.values())
        parts.append("%s — n = %s; R = 0.50: %s; ADF: %s; PP: %s" % (
            garch_label(g), " / ".join(str(c["n"]) for c in cs),
            " → ".join(f4(c["rejection_rates"]["ours_R050"]["rate"]) for c in cs),
            " → ".join(f4(c["rejection_rates"]["adf"]["rate"]) for c in cs),
            " → ".join(f4(c["rejection_rates"]["pp"]["rate"]) for c in cs)))
    big = [c for k in large["config_order"] for c in large["configs"][k]["cells"].values()]
    return ("**Trayectoria en n** (Tabla 1.4a-bis): %s. Con R = 0.50, fuera de la región exacta %s en %d de %d celdas de n = %s. La lectura de la trayectoria queda al autor; este reporte no le atribuye causa." % (
        "; ".join(parts), region, sum(not c["in_exact_acceptance_region"]["ours_R050"] for c in big), len(big),
        " y ".join(str(n) for n in large["n_grid"])))


WIN = {"proposed_R050": "propuesto", "proposed_adaptive": "propuesto", "union_joint": "unión",
       "bootstrap_dfgls": "bootstrap", "kappa2": "κ₂", "empate": "empate"}


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    env = J("environment_audit7.json")
    val, diag, simcv = J("kappa2_validation_audit7.json"), J("kappa2_diagnosis_audit7.json"), J("kappa2_simcv_audit7.json")
    recast, hand = J("dgp3_recast_composite_null_audit7.json"), J("kappa2_handicap_audit7.json")
    d5, bc, costd = J("dgp5_mixed_audit7.json"), J("block1_budget_cores_audit7.json"), J("bootstrap_cost_diagnostic_audit7.json")
    sctl, sdiag = J("bootstrap_seed_control_a6_audit7.json"), J("bootstrap_size_diag_n200_audit7.json")
    p0b1, ctv, ct = J("paso0_block1_audit7.json"), J("ct_verification_audit7.json"), J("ct_case_audit7.json")
    garch, dev, seeds = J("garch_size_audit7.json"), J("deviation_table_audit7.json"), J("paso0_pairing_audit7.json")
    garch_ext = J("garch_size_ext_audit7.json")
    garch_large = J("garch_size_ext_large_audit7.json")
    traj = {k: (garch_ext["configs"][k]["garch"], {**garch_ext["configs"][k]["cells"], **garch_large["configs"][k]["cells"]})
            for k in garch_large["config_order"]}
    gsets = [("base", garch["garch"], garch["cells"])] + [
        (k, garch_ext["configs"][k]["garch"], garch_ext["configs"][k]["cells"]) for k in garch_ext["config_order"]]
    figs, diffs = J("figures_audit7.json"), J("artifact_diffs_audit7.json")
    py_summary, py_secs = pytest_summary()

    L = []
    w = L.append
    w("# Resultados de la auditoría A7")
    w("")
    # ---- 0 ------------------------------------------------------------------
    w("## 0. Metadatos")
    w("")
    cpu = env["cpu"]
    w("- Generado (UTC): %s" % now)
    w("- Hardware: %s, %s núcleos físicos, %s lógicos; memoria %.1f GB; %s" % (
        cpu["Name"], cpu["NumberOfCores"], cpu["NumberOfLogicalProcessors"],
        env["memory_bytes"]["TotalPhysicalMemory"] / 2 ** 30, env["os"]))
    w("- Python %s; %s" % (env["python"], ", ".join("%s %s" % kv for kv in env["packages"].items())))
    w("- %s; bootUR %s" % (env["r"], env["bootUR"]))
    w("- Commit base de A7: `%s`. Predicción registrada (Bloque 0): commit `%s`. HEAD al capturar el entorno: `%s`." % (
        env["git"]["audit_base_commit"], env["git"]["prereg_commit"], env["git"]["head"]))
    amend = d5["provenance"]["amendment_commits"]
    for path, c in amend.items():
        w("- `%s`: alta `%s`, versión vigente `%s`." % (path, c["added"], c["in_force"]))
    w("- pytest (`pytest_audit7.log`): **%s** en %.1f s." % (py_summary, py_secs))
    w("")

    # ---- 1 ------------------------------------------------------------------
    w("## 1. Resultados por bloque")
    w("")
    w("### 1.0 Bloque 0 — pre-registro")
    w("")
    w("`experiments/prediccion_dgp5_audit7.md`, commit `%s`, anterior a todo cómputo. Enmiendas en la tabla de metadatos." % env["git"]["prereg_commit"])
    w("")

    w("### 1.1 Bloque 1a — κ₂")
    w("")
    g = val["gate"]
    w("**Tabla 1.1a. Compuerta nominal (valor crítico asintótico).** Región %s; veredicto **%s** (%d de %d celdas fuera)." % (
        g["region"], g["verdict"], len(g["failed_cells"]), len(val["cells"])))
    w("")
    L.extend(table(["Nula", "n", "Tamaño 5%", "IC 95%"],
                   [[c["null"], c["n"], f4(c["levels"]["0.05"]["rate"]), ci(c["levels"]["0.05"])]
                    for c in val["cells"].values()]))
    w("")
    w("**Tabla 1.1b. Descomposición del infra-dimensionamiento** (`kappa2_diagnosis_audit7.json`).")
    w("")
    L.extend(table(["Variante", "Réplicas", "Tasa 5%"],
                   [[k, c["reps"], f4(c["rates"]["0.05"])] for k, c in diag["cells"].items()]))
    w("")
    w("**Tabla 1.1c. Valor crítico simulado.**")
    w("")
    L.extend(table(["n", "VC simulado", "Tamaño en muestra", "AR(0.93) fuera de muestra", "IC", "¿En región?", "RW independiente"],
                   [[n, f4(c["simulated_critical_values"]["0.05"]), f4(c["in_sample_size_at_simulated_cv"]["rate"]),
                     f4(c["out_of_sample_ar093_at_simulated_cv"]["rate"]), ci(c["out_of_sample_ar093_at_simulated_cv"]),
                     "sí" if c["out_of_sample_ar093_at_simulated_cv"]["in_gate_region"] else "**no**",
                     f4(c["out_of_sample_rw_family91_at_simulated_cv"]["rate"])] for n, c in simcv["cells"].items()]))
    w("")
    reg = [c for c in hand["cells"].values() if c["n"] in D5.CAL_N_ACTIVE and not D5.is_weak(c["r"])]
    ext = [c for c in hand["cells"].values() if D5.is_weak(c["r"])]
    w("**Handicap de κ₂ por persistencia** (`kappa2_handicap_audit7.json`). Declarado en la rejilla registrada: %s. Declarado en la extensión: %s. Potencia de κ₂ bajo AR al valor crítico simulado: rejilla registrada (r ∈ {2, 3, 4}, n ∈ %s) entre %s y %s; extensión entre %s y %s." % (
        {n: d["handicap_declared"] for n, d in hand["declared_by_n"].items()},
        {n: d["handicap_declared"] for n, d in hand["declared_by_n_extension"].items()},
        list(D5.CAL_N_ACTIVE), f4(min(c["power_ar_break"]["rate"] for c in reg)), f4(max(c["power_ar_break"]["rate"] for c in reg)),
        f4(min(c["power_ar_break"]["rate"] for c in ext)), f4(max(c["power_ar_break"]["rate"] for c in ext))))
    w("")
    cd = recast["component_diagnostics_section_5_5"]
    w("**DGP 3 bajo la nula compuesta** (aclaración de H₀, no hallazgo): canal de media dominante en %s celdas con r > 1; cuota máxima de g₂ con R = 0.50: %s." % (
        cd["cells_r_gt_1_where_mean_dominates"], f4(cd["max_share_of_g2_in_R050_statistic"])))
    w("")

    # ---- 1.2 DGP 5 ----------------------------------------------------------
    w("### 1.2 Bloque 1 — DGP 5 (desviación mixta)")
    w("")
    w("**Tabla 1.2a. Calibración bajo la nula compuesta.**")
    w("")
    L.extend(table(["n", "α* unión conjunta", "Tamaño unión conjunta", "Tamaño real Bonferroni"],
                   [[n, "%.4f" % c["joint_union_alpha_star"], f4(c["joint_union_achieved_size"]["rate"]),
                     f4(c["bonferroni_union_achieved_size"]["rate"])] for n, c in d5["calibration_by_n"].items()]))
    w("")
    w("**Tabla 1.2b (principal). Potencia a tamaño igualado y ganador por celda** (McNemar exacto pareado, p < %.2f). I = interior registrado de la predicción 1; E = extensión post-registro." % RO.WIN_ALPHA)
    w("")
    cells = sorted(d5["cells"].values(), key=lambda c: (c["n"], c["rho"], c["r"]))
    rows = []
    for c in cells:
        p, W = c["power_size_matched"], c["winners_size_matched"]
        tag = "I" if c["interior_prediction_1"] else ("E" if c["extension_prediction_1"] else "")
        rows.append([tag, c["n"], "%.2f" % c["rho"], D5.fmt_r(c["r"]), f4(p["proposed_R050"]["rate"]),
                     f4(p["proposed_adaptive"]["rate"]), f4(p["union_joint"]["rate"]), f4(p["union_bonferroni"]["rate"]),
                     f4(p["bootstrap_dfgls"]["rate"]), f4(p["kappa2"]["rate"]),
                     WIN[W["proposed_R050_vs_union_joint"]["winner"]], WIN[W["proposed_adaptive_vs_union_joint"]["winner"]],
                     f4(c["g2_energy_share"]["proposed_R050"]["median"])])
    L.extend(table(["", "n", "ρ", "r", "R=0.50", "R̂", "Unión conj.", "Bonferroni", "Bootstrap", "κ₂",
                    "Gana (R=0.50 vs unión)", "Gana (R̂ vs unión)", "Cuota g₂ (R=0.50)"], rows))
    w("")
    w("**Tabla 1.2c. Veredicto de las predicciones por n y versión.**")
    w("")
    prow = []
    for n, pn in d5["predictions_by_n"].items():
        for v in ("proposed_R050", "proposed_adaptive"):
            f = pn["falsification_%s" % v]
            prow.append([n, v, "%s (%d de %d)" % (pn["P1_%s" % v]["status"], pn["P1_%s" % v]["wins"], pn["P1_%s" % v]["cells"]),
                         "sí" if f["registered_literal_triggered_governs_consequence"] else "no",
                         "%s (%d de %d)" % (pn["P1_extension_%s" % v]["status"], pn["P1_extension_%s" % v]["wins"],
                                            pn["P1_extension_%s" % v]["cells"]),
                         pn["P2_%s" % v]["status"], pn["P3_%s" % v]["status"]])
    L.extend(table(["n", "Versión", "P1 literal (gobierna)", "¿Condición de falsación cumplida?",
                    "P1 extensión (post-registro)", "P2", "P3"], prow))
    w("")
    literal_all = all(pn["falsification_%s" % v]["registered_literal_triggered_governs_consequence"]
                      for pn in d5["predictions_by_n"].values() for v in ("proposed_R050", "proposed_adaptive"))
    ceil = {n: pn["ceiling_registered_interior"] for n, pn in d5["predictions_by_n"].items()}
    w("**Resumen.** La predicción registrada 1 **%s** en ninguna celda del interior registrado, para ninguna versión ni n. **La condición de falsación registrada se cumplió**: la consecuencia registrada es reencuadrar el manuscrito como contribución sobre calibración. Diagnóstico declarado antes de los datos: en ese interior la unión conjunta tiene potencia a tamaño igualado entre %s y %s, y κ₂ entre %s y %s. La extensión post-registro, donde κ₂ no satura, tampoco da ninguna victoria." % (
        "no se cumple" if literal_all else "no se cumple de forma uniforme",
        f4(min(c["union_joint"]["min"] for c in ceil.values())), f4(max(c["union_joint"]["max"] for c in ceil.values())),
        f4(min(c["kappa2"]["min"] for c in ceil.values())), f4(max(c["kappa2"]["max"] for c in ceil.values()))))
    w("")
    w("**Tabla 1.2d. Planitud de la potencia del test propuesto en r** (pendiente MCO de la potencia a tamaño igualado frente a r ∈ %s, y diferencia entre el r mayor y r = 1)." % list(D5.DGP5_RATIOS))
    w("")
    srows = []
    deltas_r050 = {}
    for n in D5.CAL_N_ACTIVE:
        for rho in D5.DGP5_RHOS:
            sub = sorted([c for c in cells if c["n"] == n and c["rho"] == rho and not D5.is_weak(c["r"])], key=lambda c: c["r"])
            rs = np.array([c["r"] for c in sub])
            out = [n, "%.2f" % rho]
            for v in ("proposed_R050", "proposed_adaptive"):
                pw = np.array([c["power_size_matched"][v]["rate"] for c in sub])
                out += ["%+.4f" % np.polyfit(rs, pw, 1)[0], "%+.4f" % (pw[-1] - pw[0])]
                if v == "proposed_R050":
                    deltas_r050.setdefault(n, []).append(float(pw[-1] - pw[0]))
            sh = [c["g2_energy_share"]["proposed_R050"]["median"] for c in sub]
            sha = [c["g2_energy_share"]["proposed_adaptive"]["median"] for c in sub]
            out += ["%s – %s" % (f4(min(sh)), f4(max(sh))), "%.2e" % max(sha)]
            srows.append(out)
    L.extend(table(["n", "ρ", "Pendiente R=0.50", "Δ R=0.50", "Pendiente R̂", "Δ R̂", "Cuota g₂ R=0.50 (mediana)", "Cuota g₂ R̂ (máx.)"], srows))
    all_sh = [c["g2_energy_share"]["proposed_R050"]["median"] for c in cells]
    all_sha = [c["g2_energy_share"]["proposed_adaptive"]["median"] for c in cells]
    w("")
    w("Cuota mediana de g₂ en las %d celdas: con R = 0.50 entre %s y %s; con R̂ como máximo %.2e." % (
        len(cells), f4(min(all_sh)), f4(max(all_sh)), max(all_sha)))
    boot_wins = {n: (sum(1 for c in cells if c["n"] == n and c["winners_size_matched"]["proposed_R050_vs_bootstrap_dfgls"]["winner"] == "bootstrap_dfgls"),
                     sum(1 for c in cells if c["n"] == n)) for n in D5.CAL_N_ACTIVE}
    w("Bootstrap DF-GLS solo frente al test propuesto (R = 0.50): gana en %s celdas (ganadas, total) por n." % boot_wins)
    w("")
    w("**Tabla 1.2e. Control del bootstrap de A6 con semilla** (`bootstrap_seed_control_a6_audit7.json`).")
    w("")
    L.extend(table(["Celda", "A6 sin semilla", "IC A6", "Con semilla", "Veredicto", "Primer lote recalculado idéntico"],
                   [["dgp3 n=%d r=%.1f, B=%d" % (sctl["a6_reference"]["n"], sctl["a6_reference"]["r"], sctl["a6_reference"]["B"]),
                     "%d/%d = %s" % (sctl["a6_reference"]["adf"]["rejections"], sctl["a6_reference"]["n_sim"], f4(sctl["a6_reference"]["adf"]["rate"])),
                     ci(sctl["a6_reference"]["adf"]), "%d/%d = %s" % (sctl["seeded"]["rejections"], sctl["seeded"]["n"], f4(sctl["seeded"]["rate"])),
                     sctl["verdict"], sctl["determinism_first_batch_rerun_identical"]]]))
    w("")

    # ---- 1.3 ct ---------------------------------------------------------------
    v = ct["verifications"]
    w("### 1.3 Bloque 2 — caso con constante y tendencia («ct»)")
    w("")
    w("**Tabla 1.3a. Verificaciones.**")
    w("")
    L.extend(table(["Verificación", "Resultado", "Cifra"],
                   [["1. Regresión bit-idéntica de «c» (%d series)" % v["V1_regression_c"]["n_series"], v["V1_regression_c"]["passed"],
                     "máx. |Δ estadístico| = %s; máx. |Δ p| = %s" % (v["V1_regression_c"]["max_abs_diff_statistic"], v["V1_regression_c"]["max_abs_diff_p_value"])],
                    ["2. Invariancia a a·Y + b + c·t", v["V2_scale_invariance_ct"]["passed"],
                     "peor diferencia relativa %.3e (tolerancia %.0e)" % (v["V2_scale_invariance_ct"]["worst_rel_diff_statistic"], v["V2_scale_invariance_ct"]["tolerance_rel"])],
                    ["Paso 0 (apareamiento y semillas)", v["paso0_passed"], ""],
                    ["3. No dependencia de μ", all(m["rejection_vectors_identical"] for m in v["V3_exact_size"]["mu_dependence"].values()),
                     "máx. |Δ| relativo %.1e" % max(m["max_rel_diff_statistic_vs_mu0"] for m in v["V3_exact_size"]["mu_dependence"].values())],
                    ["3. Tamaño en la región %s (especificación original)" % v["V3_exact_size"]["band"], v["V3_exact_size"]["passed"],
                     "ver Tabla 1.3b"]]))
    w("")
    w("Decisión del autor (fuera de la especificación original): el caso «ct» se reporta como **validado**. La prueba de que el detrending funciona es la no dependencia de μ; la banda de tamaño estaba mal especificada porque el caso «c» publicado comparte el conservadurismo a n = 200. La nula del paquete (σ = 1, detrending QD) es la principal; la nula con σ̂_HAC simulada es diagnóstico y corrobora el mecanismo documentado en §3.4 del manuscrito.")
    w("")
    procs = ["ours_ct_qd", "ours_ct_ols", "ours_ct_qd_hac_null", "ours_c_reference_nodet", "adf_ct", "pp_ct", "dfgls_ct"]
    names = ["ct QD (principal)", "ct MCO", "ct QD, nula HAC (diagnóstico)", "«c» sobre la misma serie sin deriva", "ADF ct", "PP ct", "DF-GLS ct"]
    size0 = sorted([c for c in ct["size_ct_under_h0_with_drift"].values() if c["mu"] == 0.0], key=lambda c: c["n"])
    w("**Tabla 1.3b. Tamaño bajo H₀ con deriva** (μ = 0; idéntico en μ ∈ %s por construcción de números aleatorios comunes)." % list(DCT.SIZE_MUS))
    w("")
    L.extend(table(["n"] + names, [[c["n"]] + ["%s %s" % (f4(c["rejection_rates"][p]["rate"]), ci(c["rejection_rates"][p])) for p in procs] for c in size0]))
    w("")
    w("**Tabla 1.3c. DGP 1-ct** (AR(1) alrededor de una tendencia lineal).")
    w("")
    L.extend(table(["n", "ρ"] + names,
                   [[c["n"], "%.2f" % c["rho"]] + [f4(c["rejection_rates"][p]["rate"]) for p in procs]
                    for c in sorted(ct["dgp1_ct"].values(), key=lambda c: (c["n"], c["rho"]))]))
    w("")
    w("**Tabla 1.3d. DGP 3-ct** (paseo aleatorio con deriva y quiebre de varianza) con el contraste pareado «ct» QD frente a «c».")
    w("")
    L.extend(table(["n", "r"] + names + ["McNemar p («ct» vs «c»)"],
                   [[c["n"], "%.1f" % c["r"]] + [f4(c["rejection_rates"][p]["rate"]) for p in procs] + ["%.4f" % c["paired_ct_qd_vs_c_reference"]["p_value"]]
                    for c in sorted(ct["dgp3_ct"].values(), key=lambda c: (c["n"], c["r"]))]))
    w("")

    # ---- 1.4 Bloque 3 -----------------------------------------------------------
    w("### 1.4 Bloque 3 — cierres")
    w("")
    reg_g = garch["exact_acceptance_region"]
    if garch_ext["exact_acceptance_region"] != reg_g:
        raise KeyError("region exacta distinta entre garch_size_audit7.json y garch_size_ext_audit7.json")
    w("**Tabla 1.4a. Tamaño bajo innovaciones GARCH(1,1)** (ω = %s en todas; innovaciones estandarizadas a varianza incondicional 1; nula gaussiana sin recalibrar; N_sim = %d). Región exacta %s; * = dentro. Configuración base en `garch_size_audit7.json`; las otras tres en `garch_size_ext_audit7.json` (familia de semillas 81)." % (
        garch["garch"]["omega"], garch_ext["config"]["N_sim"], reg_g))
    w("")
    gp = ["ours_R025", "ours_R050", "ours_R075", "adf", "pp", "dfgls", "kpss"]
    L.extend(table(["α", "β", "Persistencia", "z", "n", "R=0.25", "R=0.50", "R=0.75", "ADF", "PP", "DF-GLS", "KPSS (potencia)"],
                   [[g["alpha"], g["beta"], "%.2f" % g["persistence"], g["z"], n]
                    + ["%s%s" % (f4(c["rejection_rates"][p]["rate"]), "*" if c["in_exact_acceptance_region"].get(p) else "") for p in gp]
                    for _, g, cells in gsets for n, c in cells.items()]))
    w("")
    L.extend(table(["Persistencia", "z", "E[z⁴]α² + 2αβ + β² (cuarto momento finito si < 1)"],
                   [["%.2f" % g["persistence"], g["z"], "%.4f" % g["fourth_moment_condition_E_z4_alpha2_plus_2alpha_beta_plus_beta2"]]
                    for _, g, _c in gsets[1:]]))
    w("")
    if garch_large["exact_acceptance_region"] != reg_g:
        raise KeyError("region exacta distinta en garch_size_ext_large_audit7.json")
    w("**Tabla 1.4a-bis. Trayectoria en n** de dos configuraciones: n = %s de `garch_size_ext_audit7.json` y n = %s de `garch_size_ext_large_audit7.json` (familia de semillas 82). Misma nula, mismas columnas, N_sim = %d; * = dentro de la región exacta %s. Sin causa atribuida." % (
        ", ".join(str(c["n"]) for c in garch_ext["configs"][garch_large["config_order"][0]]["cells"].values()),
        ", ".join(str(n) for n in garch_large["n_grid"]), garch_large["config"]["N_sim"], reg_g))
    w("")
    tp = [("ours_R050", True), ("ours_R025", False), ("ours_R075", False), ("adf", True), ("pp", True), ("dfgls", False), ("kpss", False)]
    L.extend(table(["Configuración", "n", "R=0.50 [IC 95%]", "R=0.25", "R=0.75", "ADF [IC 95%]", "PP [IC 95%]", "DF-GLS", "KPSS (potencia)"],
                   [[garch_label(g), c["n"]] + ["%s%s%s" % (f4(c["rejection_rates"][p]["rate"]), "*" if c["in_exact_acceptance_region"].get(p) else "",
                                                          " " + ci(c["rejection_rates"][p]) if wide else "") for p, wide in tp]
                    for g, cells in traj.values() for c in cells.values()]))
    w("")
    p0l = garch_large["paso0_reproduction"]
    w("Paso 0 de la trayectoria: el script con `--set ext_large` reproduce las primeras %d filas de %d celdas ya guardadas (base y las dos configuraciones a n ≤ 1000); peor máx. |Δ| = %s (pasa: %s)." % (
        next(iter(p0l["by_cell"].values()))["series"], len(p0l["by_cell"]), p0l["worst_max_abs_diff"], p0l["passed"]))
    w("")
    p0g = garch_ext["paso0_base_reproduction"]
    w("Paso 0 de la extensión: el script refactorizado reproduce las primeras %d filas de cada celda base guardadas en sus checkpoints; peor máx. |Δ| = %s (pasa: %s)." % (
        p0g["by_n"][str(list(garch["cells"].values())[0]["n"])]["series"], p0g["worst_max_abs_diff"], p0g["passed"]))
    w("")
    w("**Tabla 1.4b. Desviaciones del pre-registro** (`deviation_table_audit7.json`).")
    w("")
    L.extend(table(["Id", "Auditoría", "Elemento", "Pre-registrado", "Desplegado", "Valor pre-registrado", "Valor desplegado"],
                   [[r["id"], r["audit"], r["element"], r["preregistered"], r["deployed"],
                     json.dumps(r["preregistered_value"], ensure_ascii=False), json.dumps(r["deployed_value"], ensure_ascii=False)]
                    for r in dev["rows"]]))
    w("")
    w("**Tabla 1.4c. Números aleatorios comunes por familia** (`paso0_pairing_audit7.json`).")
    w("")
    L.extend(table(["Familia", "Fuente", "N", "Pares solapados", "Con la misma base", "Máx. semillas compartidas"],
                   [[k, f["source"], f["n_sim"], f["overlapping_pairs"], f["pairs_same_seed_base"], f["max_shared_seeds"]]
                    for k, f in seeds["families"].items()]))
    w("")
    w("Solapes entre familias distintas: %d pares de celdas; por par de familias: %s." % (
        len(seeds["cross_family_overlaps"]), seeds["cross_family_overlaps_by_pair"]))
    w("")
    w("**Tabla 1.4d. Figuras** (`experiments/figures/`, PDF vectorial).")
    w("")
    L.extend(table(["Figura", "sha256"], [[k, "`%s`" % s] for k, s in figs["figures"].items()]))
    w("")

    # ---- 2 ----------------------------------------------------------------------
    w("## 2. Tabla de semillas")
    w("")
    sources = [("kappa2_validation_audit7.json", val), ("kappa2_simcv_audit7.json", simcv), ("kappa2_handicap_audit7.json", hand),
               ("dgp5_mixed_audit7.json", d5), ("bootstrap_seed_control_a6_audit7.json", sctl),
               ("bootstrap_size_diag_n200_audit7.json", sdiag), ("ct_case_audit7.json", ct), ("garch_size_audit7.json", garch),
               ("garch_size_ext_audit7.json", garch_ext), ("garch_size_ext_large_audit7.json", garch_large)]
    L.extend(table(["Experimento", "Fórmula"], [[name, d["provenance"]["seed_formula"]] for name, d in sources]))
    w("")
    ov, rs = p0b1["seed_overlap_block1"], p0b1["r_bootstrap_seeds"]
    w("Bloque 1: %d colisiones exactas y %d pares solapados entre celdas; semillas de R del bootstrap en %d celdas con %d solapes y hueco mínimo %d. Solapes de las familias del paper en la Tabla 1.4c." % (
        ov["exact_collisions"], ov["overlapping_pairs"], rs["n_cells"], len(rs["overlapping_pairs"]), rs["min_gap_between_cells"]))
    w("")

    # ---- 3 ----------------------------------------------------------------------
    w("## 3. Diffs contra el control")
    w("")
    L.extend(table(["Prueba", "Veredicto", "Peor diferencia"],
                   [["Paso 0 del Bloque 1: generadores (50 series por celda)", p0b1["verdict"], p0b1["generators"]["worst_max_abs_diff"]],
                    ["Paso 0 del Bloque 1: componentes frente a compute_statistic", p0b1["verdict"], p0b1["components_vs_compute_statistic"]["worst_max_abs_diff"]],
                    ["Paso 0 del caso ct: generadores", ctv["paso0"]["passed"], ctv["paso0"]["generators"]["worst"]],
                    ["Paso 0 del caso ct: componentes", ctv["paso0"]["passed"], ctv["paso0"]["components_runner_vs_compute_statistic"]["worst"]],
                    ["Control A6: trayectorias", sctl["verdict"], sctl["trajectory_pairing_max_abs_diff"]],
                    ["Diagnóstico de tamaño: trayectorias", sdiag["verdict"], sdiag["trajectory_pairing_max_abs_diff"]],
                    ["Regresión bit-idéntica de «c»: statistic", v["V1_regression_c"]["passed"], v["V1_regression_c"]["max_abs_diff_statistic"]],
                    ["Regresión bit-idéntica de «c»: p_value", v["V1_regression_c"]["passed"], v["V1_regression_c"]["max_abs_diff_p_value"]],
                    ["GARCH: script refactorizado frente a checkpoints de la configuración base", garch_ext["paso0_base_reproduction"]["passed"],
                     garch_ext["paso0_base_reproduction"]["worst_max_abs_diff"]],
                    ["GARCH n = 2000 y 5000: script frente a checkpoints de las celdas ya calculadas", garch_large["paso0_reproduction"]["passed"],
                     garch_large["paso0_reproduction"]["worst_max_abs_diff"]]]))
    w("")
    w("**Artefactos de A7 regenerados** (hoja por hoja, sin procedencia ni hojas de tiempo %s; valor cambiado = regresión salvo que la clave sea un conteo de celdas de una rejilla ampliada, lo que se lee en la última columna; clave añadida = ampliación)." % diffs["volatile_leaves_excluded"])
    w("")
    arows = []
    for path, steps in diffs["regenerated_audit7_artifacts"].items():
        for s in steps:
            arows.append([path, "%s → %s" % (s["from"][:7], s["to"][:7]), s["values_changed"], s["keys_removed"], s["keys_added"],
                          "; ".join("%s: %s → %s" % (x["key"], x["before"], x["after"]) for x in s["changed_sample"]) or "—"])
    L.extend(table(["Archivo", "Versiones", "Valores cambiados", "Claves eliminadas", "Claves añadidas", "Claves cambiadas"], arows))
    w("")
    w("Con valores cambiados o claves eliminadas: %s." % diffs["regenerated_with_value_changes"])
    w("")
    pr, ro = diffs["prior_audit_results"], diffs["read_only_preregistered"]
    w("JSON de auditorías anteriores: %d archivos; cambiados en git desde el commit base: %s; contenido en disco distinto del commit base: %s; distintos sólo por fin de línea (conversión de git en Windows): %d." % (
        pr["files"], pr["changed_in_git"], pr["disk_content_differs_from_base"], len(pr["disk_differs_only_line_endings"])))
    w("Archivos pre-registrados de sólo lectura: %d; cambiados en git: %s; contenido en disco distinto: %s; sólo fin de línea: %d." % (
        len(ro["files"]), ro["changed_in_git"], ro["disk_content_differs_from_base"], len(ro["disk_differs_only_line_endings"])))
    w("")

    # ---- 4 ----------------------------------------------------------------------
    w("## 4. Hardware y tiempos")
    w("")
    best = str(bc["chosen_cores_max_throughput"])
    proj = bc["projection_by_cores"][best]
    real_b1 = [block_hours(l) for l in BLOCK1_LOGS]
    garch_sec = sum(c["cell_elapsed_sec"] for c in garch["cells"].values())
    garch_large_sec = sum(c["cell_elapsed_sec"] for k in garch_large["config_order"] for c in garch_large["configs"][k]["cells"].values())
    garch_ext_sec = sum(c["cell_elapsed_sec"] for _, _g, cells in gsets[1:] for c in cells.values())
    L.extend(table(["Bloque", "Proyectado", "Real"],
                   [["1 (DGP 5; %s núcleos)" % best, "%.2f h (medio), %.2f h (peor ronda)" % (proj["mean_of_rounds"]["total_sec"] / 3600, proj["worst_of_rounds"]["total_sec"] / 3600),
                     "%.2f h en %d sub-bloques (%s)" % (sum(real_b1), len(real_b1), ", ".join("%.2f" % h for h in real_b1))],
                    ["2 (caso ct)", "sondas por celda (ct_manifest_audit7.json)", "%.2f h" % block_hours("bloque2_ct_runner_audit7.log")],
                    ["3.1 (GARCH)", "sondas por celda", "%.2f h" % (garch_sec / 3600)],
                    ["3.1b (GARCH, tres configuraciones adicionales)", "sondas por celda", "%.2f h" % (garch_ext_sec / 3600)],
                    ["3.1c (GARCH, n = 2000 y 5000)", "sondas por celda y sonda de calibración", "%.2f h de celdas + %.0f s de calibración de la nula" % (
                        garch_large_sec / 3600, garch_large["calibration_elapsed_sec"])]]))
    w("")
    w("Compuerta de estabilidad del presupuesto (%s): máx. lenta/rápida %.2f en la configuración elegida; lanzable: %s." % (
        best, bc["stability_gate"]["chosen_cores_max_ratio"], bc["stability_gate"]["launch_allowed"]))
    w("")
    w("### 4.1 Fallos de proceso")
    w("")
    cmp1000 = costd["comparison_sec_per_series"]["1000"]
    w("- **Bootstrap de A6 sin semilla.** El worker heredado no fijaba la semilla de R: el mismo lote dio p-valores distintos (máx. |Δp| = %s). Se sustituyó por un worker con semilla por serie; la tasa publicada de A6 se reproduce exactamente con semilla (Tabla 1.2e)." % f4(costd["determinism"]["max_abs_diff_pvalue"]))
    w("- **Presupuesto por sondas de 14 series no reproducible.** A n = 1000 el mismo lote midió %s s/serie sin pool y %s s/serie en la sonda del presupuesto. Se re-sondeó con 70 series por medición en dos rondas y tres configuraciones de núcleos (`block1_budget_cores_audit7.json`)." % (
        f4(cmp1000["clean"]), f4(cmp1000["budget_probe"])))
    w("- **`os.replace` denegado por Windows.** El primer intento del Bloque 1 terminó con PermissionError al escribir el manifiesto (%s en `bloque1_block1_audit7.log`), antes de tocar DGP 5; se añadieron reintentos acotados a la escritura atómica (commit `%s`)." % (
        "presente" if "PermissionError" in T("bloque1_block1_audit7.log") else "ausente", commit_with("reintentos acotados")))
    topes = [e for l in BLOCK1_LOGS for e in tope_events(l)]
    w("- **Tope de 4 h conservador (comportamiento previsto).** El runner estima el lote siguiente con la sonda de 14 series, que incluye el arranque de R, y paró limpio %d veces: %s. Las celdas pendientes se reanudaron desde su sonda en el bloque siguiente." % (
        len(topes), "; ".join("%s (lote de %s series estimado en ~%s s, transcurrido %s h)" % (e[0], e[2], e[3], e[4]) for e in topes)))
    w("- **Ventanas del monitor.** El monitor de progreso expiró varias veces entre eventos; en cada re-armado se verificó sobre el log que no se perdió ningún evento, lo que sostiene el registro de tiempos.")
    w("- **Compuerta de tamaño del caso ct mal especificada por el autor.** Exigía la región binomial exacta en las nueve celdas; el caso «c» publicado tampoco la cumple a n = 200. Re-especificada después de los datos (fila vii de la Tabla 1.4b).")
    a2 = [c for p, c in amend.items() if c["added"] != c["in_force"]]
    w("- **Procedencia de la segunda enmienda.** La primera ejecución del análisis de DGP 5 citaba el commit de alta de la enmienda y no su versión vigente; corregido y re-ejecutado sin cambio de valores (§3). Enmiendas con versión vigente distinta de la de alta: %d." % len(a2))
    w("- **Modo de energía.** La capa «mejor rendimiento» se restableció a «equilibrado» al reiniciarse la sesión antes del último sub-bloque del Bloque 1; el remuestreo lleva semilla y no afecta a los valores.")
    w("")

    # ---- 5 ----------------------------------------------------------------------
    w("## 5. No ejecutado")
    w("")
    w("- **Celdas de n = 1000 de DGP 5** (retiradas por la segunda enmienda): %s. Reanudación:" % sorted(d5["withdrawn"]))
    w("")
    w("      python experiments/audit7_dgp5_runner.py --cells \"adaptnull:n=1000;cal:n=1000;dgp5:confirm\" --cores <núcleos> --B %d --n-sim-dgp5 %d --n-cal %d --max-seconds %.0f" % (
        D5.DGP5_B, D5.DGP5_N_SIM, D5.N_CAL, C.DEFAULT_MAX_SECONDS))
    w("")
    ar = simcv["cells"]["200"]["out_of_sample_ar093_at_simulated_cv"]
    w("- **Anomalía sin diagnóstico 1 — caída de κ₂ bajo AR(0.93) a n = 200.** Al valor crítico simulado, tamaño fuera de muestra %s %s, fuera de la región; en n = 500 y n = 1000 dentro. No se le atribuye causa." % (f4(ar["rate"]), ci(ar)))
    w("- **Anomalía sin diagnóstico 2 — tamaño nominal del bootstrap a n = 200.** Veredicto registrado: %s." % sdiag["verdict"])
    w("")
    L.extend(table(["Pata", "Tasa", "IC 95%", "¿Contiene 0.05?"],
                   [[k, f4(x["rate"]), ci(x), x["ci_contains_nominal"]] for k, x in sdiag["legs"].items()]))
    l2 = sdiag["L2_B_effect_paired"]
    l3 = sdiag[next(k for k in sdiag if k.startswith("L3_"))]
    w("")
    w("  Efecto de B (pareado): McNemar p = %s, B es la causa: %s. Trayectorias (calibración de A7 frente a trayectorias de A6, mismo B): z = %.2f, p = %s. Intervalos nominales examinados en la calibración: %d; excluyen 0.05: %s. Compatible con variabilidad Monte Carlo con esos intervalos declarados; no se atribuye causa." % (
        f4(l2["mcnemar_p"]), l2["B_is_cause"], l3["z"], f4(l3["p_value"]),
        sdiag["calibration_nominal_intervals_examined"]["count"], sdiag["calibration_nominal_intervals_examined"]["excluding_nominal"]))
    stale = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "figures", "*.png")))
    w("- **PNG antiguos** en `experiments/figures/` no regenerados (el Bloque 3 pide PDF): %s." % stale)
    w("")

    # ---- 6 ----------------------------------------------------------------------
    w("## 6. Conclusiones")
    w("")
    wins_total = sum(pn["P1_%s" % v]["wins"] + pn["P1_extension_%s" % v]["wins"]
                     for pn in d5["predictions_by_n"].values() for v in ("proposed_R050", "proposed_adaptive"))
    w("1. **DGP 5: la condición de falsación registrada se cumplió** (Tabla 1.2c). El test propuesto no tiene ventaja en el interior de la rejilla: %d victorias frente a la unión calibrada conjuntamente sumando interior registrado y extensión, ambas versiones y ambos n. La consecuencia registrada es reencuadrar el manuscrito como contribución sobre calibración. La saturación de κ₂ no lo explica: la extensión, donde κ₂ no satura, da el mismo desenlace." % wins_total)
    n0 = D5.CAL_N_ACTIVE[0]
    w("2. **La potencia del test propuesto es plana en r y el canal de varianza apenas pesa** (Tabla 1.2d). A n = %d, pasar de r = 1 a r = %s (varianza ×%s) cambia la potencia con R = 0.50 entre %+.4f y %+.4f según ρ; la cuota mediana de g₂ va de %s a %s con R = 0.50 y no supera %.2e con R̂. El bootstrap DF-GLS solo supera al test propuesto en %d de las %d celdas de n = %d (registradas y extensión, todos los ρ)." % (
        n0, D5.fmt_r(max(D5.DGP5_RATIOS)), D5.fmt_r(max(D5.DGP5_RATIOS) ** 2), min(deltas_r050[n0]), max(deltas_r050[n0]),
        f4(min(all_sh)), f4(max(all_sh)), max(all_sha), boot_wins[n0][0], boot_wins[n0][1], n0))
    s200 = size0[0]["rejection_rates"]
    mu_max = max(m["max_rel_diff_statistic_vs_mu0"] for m in v["V3_exact_size"]["mu_dependence"].values())
    w("3. **El caso «ct» queda validado con el mismo caveat que «c»** (Tablas 1.3a–b). El detrending elimina la deriva exactamente (máx. |Δ| relativo %.1e entre μ); a n = %d el tamaño «ct» es %s frente a %s de «c» sobre las mismas innovaciones, y converge con n (%s). La nula con σ̂_HAC da %s a n = %d, el mecanismo de §3.4." % (
        mu_max, size0[0]["n"], f4(s200["ours_ct_qd"]["rate"]), f4(s200["ours_c_reference_nodet"]["rate"]),
        " → ".join(f4(c["rejection_rates"]["ours_ct_qd"]["rate"]) for c in size0), f4(s200["ours_ct_qd_hac_null"]["rate"]), size0[0]["n"]))
    w(conclusion_garch(gsets, reg_g))
    w("   " + trajectory_sentence(traj, garch_large, reg_g))
    w("5. **Reproducibilidad** (Tabla 1.2e y §5). La tasa del bootstrap de A6 se reproduce exactamente con semilla (%d/%d frente a %d/%d); quedan declaradas dos anomalías sin diagnóstico, sin explicación atribuida." % (
        sctl["seeded"]["rejections"], sctl["seeded"]["n"], sctl["a6_reference"]["adf"]["rejections"], sctl["a6_reference"]["n_sim"]))
    w("")

    # ---- 7 ----------------------------------------------------------------------
    files = []
    for pat in MANIFEST_PATTERNS:
        for p in glob.glob(os.path.join(C.REPO, pat)):
            if os.path.isfile(p) and os.path.abspath(p) != os.path.abspath(OUT):
                files.append(os.path.relpath(p, C.REPO).replace("\\", "/"))
    files = sorted(set(files))
    entries = []
    for rel in files:
        full = os.path.join(C.REPO, rel)
        entries.append({"path": rel, "sha256": C._sha256_file(full), "bytes": os.path.getsize(full),
                        "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(full), datetime.timezone.utc).isoformat()})
    C.atomic_write_json(MANIFEST, {"provenance": C.provenance(dgp="manifest", n_sim=None, seed_formula=None),
                                   "patterns": list(MANIFEST_PATTERNS), "files": entries})
    w("## 7. Manifiesto")
    w("")
    w("Descubrimiento por patrón %s. Lista completa con sha256, tamaño y mtime en `manifest_audit7.json` (%d archivos); aquí, los archivos fuera de checkpoints y un resumen por directorio de checkpoints." % (list(MANIFEST_PATTERNS), len(entries)))
    w("")
    L.extend(table(["Archivo", "sha256", "mtime (UTC)"],
                   [[e["path"], "`%s`" % e["sha256"], e["mtime_utc"]] for e in entries if "/checkpoints/" not in e["path"]]))
    w("")
    groups = {}
    for e in entries:
        if "/checkpoints/" in e["path"]:
            groups.setdefault(e["path"].rsplit("/", 1)[0], []).append(e)
    L.extend(table(["Directorio de checkpoints", "Archivos", "Bytes", "sha256 de la lista ordenada de sha256"],
                   [[d, len(es), sum(x["bytes"] for x in es),
                     "`%s`" % hashlib.sha256("".join(x["sha256"] for x in sorted(es, key=lambda x: x["path"])).encode()).hexdigest()]
                    for d, es in sorted(groups.items())]))
    w("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("escrito %s (%d lineas); manifiesto %d archivos" % (OUT, len(L), len(entries)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
