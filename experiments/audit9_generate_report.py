"""
Auditoria A9 - generador de experiments/results/resultados_auditoria_9.md.

Regla de A8 (regla 3): ningun numero de resultado se escribe a mano; todo valor se
lee de un JSON o log de experiments/results (o del .tex de paper/ para las citas
de la seccion 7). Si falta una clave, el script falla con KeyError. Los bloques
cuyo JSON no existe se declaran en la seccion 5 (No ejecutado).
tests/test_no_literals_audit9.py recorre este archivo.

Estructura: encabezado; 1 resultados (tablas listas para transcribir, cada una
con su JSON, N_sim, N_cal, familia, region exacta y nota); 2 compuertas;
3 procedencia; 4 desviaciones; 5 no ejecutado; 6 conclusiones; 7 anomalias y
contradicciones con el manuscrito; anexo de hechos.

Uso: python experiments/audit9_generate_report.py
"""
import datetime
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
from audit8_generate_report import (f4, pct, sci, table, star, wil, pp1, pp2, se1, se2, label, verdict, fmt_effect)  # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_9.md")
PROTOCOL = "experiments/protocol_audit9.md"
FILES = {"B9.0": "b90_protocol_audit9.json", "B9.1": "b91_equalized_audit9.json", "B9.2": "b92_theta_audit9.json",
         "B9.3": "b93_attribution_audit9.json", "B9.4": "b94_finite_sample_audit9.json", "B9.5": "b95_awb_audit9.json",
         "B9.6": "b96_application_audit9.json", "B9.7": "b97_critical_values_audit9.json",
         "FIG": "figures_audit9.json"}
TITLES = {"B9.0": "Protocolo", "B9.1": "Potencia a tamaño igualado", "B9.2": "Escalera de θ, incluido θ = 0",
          "B9.3": "De dónde viene la ganancia en muestra finita", "B9.4": "Qué compra la calibración de muestra finita",
          "B9.5": "Sonda: calibración por bootstrap salvaje del propio estadístico",
          "B9.6": "Aplicación con la configuración final", "B9.7": "Valores críticos finales y figuras"}
SCRIPTS = {"B9.1": "experiments/audit9_b91_equalized.py", "B9.2": "experiments/audit9_b92_theta.py",
           "B9.3": "experiments/audit9_b93_attribution.py", "B9.4": "experiments/audit9_b94_finite_sample.py",
           "B9.5": "experiments/audit9_b95_awb.py", "B9.6": "experiments/audit9_b96_application.py",
           "B9.7": "experiments/audit9_b97_critical_values.py"}
PN = {"gls_t0": "RM-GLS θ = 0", "gls_t0.02": "RM-GLS θ = 0.02", "gls_t0.05": "RM-GLS θ = 0.05",
      "gls_t0.1": "RM-GLS θ = 0.1", "gls_t0.2": "RM-GLS θ = 0.2", "rm_t0.1": "RM", "msbhac": "MSB-HAC",
      "glsb_t0": "(b) θ = 0 con s²_AR", "adf": "ADF", "pp": "PP", "dfgls": "DF-GLS", "mzt": "MZ_t-GLS", "msb": "MSB-GLS",
      "kpss": "KPSS", "za": "ZA", "envelope": "envolvente", "msb_asy": "MSB-GLS asy", "a": "(a)", "b": "(b)", "c": "(c)",
      "msb_sim": "MSB-GLS sim"}
CASE = {"c": "demeaned", "ct": "tendencia", "dm": "demeaned"}
APP = {"final": "primaria final (simulada)", "final_awb": "primaria final, calibración AWB", "primary_rmgls": "primaria de A8 (RM-GLS θ = 0.1)",
       "primary_rm": "RM (A8)", "rhat_prereg": "R̂ pre-registrado (publicado)", "adf": "ADF", "pp": "PP",
       "dfgls_aic": "DF-GLS (AIC, publicado)", "dfgls_maic": "DF-GLS (MAIC)", "mzt": "MZ_t-GLS", "kpss": "KPSS"}
# frases del manuscrito v11 (clave, etiqueta, archivo, patron)
CLAIMS = (
    ("dominance_intro", "dominancia sobre ADF (§1)", "paper/sec1_introduction.tex", r"ADF by \$5\$ to \$14\$"),
    ("dominance_dgp1", "dominancia sobre ADF (§5.3)", "paper/sec5_montecarlo.tex", r"\+14\.0\$~pp"),
    ("garch_11", "el 11 de 16 GARCH (§5.2)", "paper/sec5_montecarlo.tex", r"acceptance region in eleven"),
    ("exact_intro", "tamaño exacto por construcción (§1)", "paper/sec1_introduction.tex", r"size is exact by construction"),
    ("exact_p1", "tamaño exacto por construcción (P1)", "paper/sec1_introduction.tex", r"so that size is exact for"),
    ("trend_size", "caso con tendencia (§5.9)", "paper/sec5_montecarlo.tex", r"Empirical size is \$0\.0388\$"),
    ("fp_028", "tasa de falsas alarmas (§6)", "paper/sec6_application.tex", r"rate, \$0\.028\$"),
    ("detections_13", "13 detecciones (§6)", "paper/sec6_application.tex", r"detections \(\$13\$ of \$88\$"),
)


def J(name):
    return C.read_json(name)


def have(block):
    return os.path.exists(os.path.join(C.RESULTS, FILES[block]))


def T(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def pname(p):
    return PN.get(p, p)


def rr(r):
    return f4(r["rate"])


def mp(m):
    return f4(m["p_value"])


def dse(d, scale=100):
    return "%s (%s)" % (pp2(d["delta"] * scale), se2(d["se"] * scale))


def dse1(d, scale=100):
    return "%s (%s)" % (pp1(d["delta"] * scale), se1(d["se"] * scale))


def mse(d, scale=100):
    return "%s (%s)" % (pp2(d["mean"] * scale), se2(d["se"] * scale))


def note(json_name, n_sim, n_cal, family, region, extra):
    return ("*Fuente: `%s`; N_sim = %s; N_cal = %s; familia %s; región exacta %s.%s*" % (
        json_name, n_sim, n_cal, family, region, (" " + extra) if extra else ""))


def protocol_section(title):
    with open(os.path.join(C.REPO, PROTOCOL), encoding="utf-8") as f:
        text = f.read()
    i = text.index(title)
    j = text.find("\n### ", i + 1)
    k = text.find("\n## ", i + 1)
    ends = [x for x in (j, k) if x > 0]
    return " ".join(l.strip() for l in text[i:min(ends) if ends else None].splitlines()[1:] if l.strip())


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
    name = "pytest_audit9.log"
    if not os.path.exists(os.path.join(C.RESULTS, name)):
        return None
    text = T(name)
    m = re.findall(r"=+ (.*?) in ([0-9.]+)s", text)
    summary, secs = m[-1]
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|errors?)", summary)}
    coll = re.search(r"collected (\d+) items", text)
    lit = re.findall(r"tests[\\/]test_no_literals_audit9\.py::(\S+) (PASSED|FAILED|SKIPPED)", text)
    return {"seconds": float(secs), "collected": int(coll.group(1)) if coll else None, "counts": counts, "literals": lit}


# ---------------------------------------------------------------------------
# Secciones por bloque
# ---------------------------------------------------------------------------
def sec_b90(w, L):
    b = J(FILES["B9.0"])
    w("### B9.0 — %s" % TITLES["B9.0"])
    w("")
    p = b["protocol"]
    w("`%s`: sha256 `%s` (contenido commiteado `%s`), introducido en el commit `%s`. Familias: %s." % (
        p["path"], p["sha256_disk"], p["sha256_committed"], p["commit_added"][:7],
        ", ".join("%s = %s" % (k, v) for k, v in b["families"].items())))
    w("")
    w("**Tabla B9.0.1. JSON de A8 (y de A7) reutilizados.**")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "mtime (UTC)"],
                   [[k, "`%s`" % v["sha256"], v["bytes"], v["mtime_utc"]] for k, v in b["a8_inventory"].items()]))
    w("")
    w("**Tabla B9.0.2. Checkpoints de A8 de los que se regeneran y comparan trayectorias.**")
    w("")
    L.extend(table(["Carpeta", "Lotes JSON", "sha256 agregado", "Última modificación (UTC)"],
                   [[k, v["json_batches"], "`%s`" % v["aggregate_sha256"], v["last_mtime_utc"]]
                    for k, v in b["a8_checkpoints"].items()]))
    w("")
    s = b["seed_map"]
    w("**Tabla B9.0.3. Colisión de semillas** (%s)." % s["method"])
    w("")
    L.extend(table(["Familia", "Celdas", "Streams de réplica", "Distintos"],
                   [[f, v["cells"], v["replicate_streams"], v["distinct"]] for f, v in s["new_families"].items()]))
    w("")
    w("Streams previos comparados: %d (enteros de A5–A7: %d; familias de A8: %s). Colisiones nuevas frente a previas: **%d**; dentro de A9: **%d**. Familias sin celdas: %s." % (
        s["prior_streams_total"], s["prior_integer_seeds"],
        ", ".join("%s: %d" % (k, v) for k, v in s["prior_a8_family_streams"].items()),
        s["collisions_new_vs_prior"], s["collisions_within_new"], s["families_without_cells"]))
    w("")


B91_PROCS = ("gls_t0.1", "rm_t0.1", "msbhac", "adf", "pp", "dfgls", "mzt", "msb")


def b91_table(w, L, b, prefix, key_col, extra):
    cells = {k: v for k, v in b["cells"].items() if k.startswith(prefix)}
    procs = list(B91_PROCS) + list(extra)
    rows = []
    for k, v in sorted(cells.items(), key=lambda kv: (kv[1]["n"], kv[1].get(key_col, 0))):
        r = [v.get(key_col), v["n"]]
        for p in procs:
            if p in v["rates_asy"]:
                r.append("%s → %s" % (rr(v["rates_asy"][p]), rr(v["rates_sim"][p])))
            else:
                r.append(rr(v["rates_sim"][p]))
        r.append(f4(v["awb_carried_from_a8"]["rate"]) if "awb_carried_from_a8" in v else "—")
        rows.append(r)
    L.extend(table([key_col, "n"] + [pname(p) for p in procs] + ["AWB (A8)"], rows))
    w("")
    rows = []
    for k, v in sorted(cells.items(), key=lambda kv: (kv[1]["n"], kv[1].get(key_col, 0))):
        rows.append([v.get(key_col), v["n"]] + [mp(v["mcnemar_primary_vs_sim"][p]) for p in procs if p != "gls_t0.1"])
    w("McNemar exacto (p) de la primaria frente a cada comparador, versión simulada:")
    w("")
    L.extend(table([key_col, "n"] + [pname(p) for p in procs if p != "gls_t0.1"], rows))
    w("")


def sec_b91(w, L):
    b = J(FILES["B9.1"])
    cfg = b["config"]
    w("### B9.1 — %s" % TITLES["B9.1"])
    w("")
    w("Trayectorias: %s. Primaria: RM-GLS θ = 0.1 (la de A8). Regla simulada: %s. Paso 0 (primeras 50 réplicas de cada celda frente a los checkpoints de B5, columnas comunes): peor máx. |Δ| = %s. Control de la calibración frente a producción (RM-GLS θ = 0.1 y θ = 0, `hac`): peor máx. |Δ| = %s." % (
        cfg["trajectories"], cfg["rule_sim"], sci(b["paso0_worst"]),
        sci(max(v for c in b["production_control"].values() for v in c.values()))))
    w("")
    nt = note(FILES["B9.1"], cfg["N_sim"], cfg["N_cal"], "95 (trayectorias de A8); calibración: caminos de producción, semilla %d" % cfg["cal_seed"],
              b["exact_region_5000"], "Celdas «asy → sim»: tasa con el valor crítico asintótico (convención de A8) y con el simulado; "
              "RM, RM-GLS y MSB-HAC tienen solo la simulada. KPSS: la asintótica rechaza la estacionariedad; la simulada rechaza la raíz unitaria (protocolo, lectura 4). AWB: %s." % cfg["awb"])
    for prefix, key, extra, title in (("dgp1_", "rho", ("kpss",), "DGP 1 (AR(1), demeaned)"),
                                      ("dgp2_", "delta", ("za",), "DGP 2 (AR(0.95) con quiebre de media)"),
                                      ("ct_power_", "rho", (), "caso con tendencia (AR(1) alrededor de una tendencia)")):
        w("**Tabla B9.1.%s. %s: tasas «asy → sim».**" % (prefix.rstrip("_"), title))
        w("")
        b91_table(w, L, b, prefix, key, extra)
        w(nt)
        w("")
    w("**Tabla B9.1.thr. Valores críticos simulados al 5%%** (cuantil 5%% bajo la Ec. (3), N_cal = %d)." % cfg["N_cal"])
    w("")
    procs = ("adf", "pp", "dfgls", "mzt", "msb", "kpss", "za")
    L.extend(table(["Caso | n"] + [pname(p) for p in procs],
                   [[k] + ["%.4f" % v[p] if p in v else "—" for p in procs] for k, v in b["sim_thresholds"].items()]))
    w("")
    for e, name in (("E1", "E1"), ("E2", "E2")):
        x = b[e]
        w("**Tabla B9.1.%s. Clasificación %s.**" % (name, name))
        w("")
        if e == "E1":
            L.extend(table(["Celda", "Primaria", "DF-GLS-sim", "MZ_t-GLS-sim", "p vs DF-GLS", "p vs MZ_t", "Supera a ambos", "…con p < 0.05"],
                           [[k, f4(v["primary"]), f4(v["dfgls_sim"]), f4(v["mzt_sim"]), f4(v["p_dfgls"]), f4(v["p_mzt"]),
                             v["wins_both"], v["wins_both_mcnemar"]] for k, v in x["cells"].items()]))
        else:
            L.extend(table(["Celda", "ρ", "Primaria", "DF-GLS-sim", "p", "Supera", "…con p < 0.05"],
                           [[k, v["rho"], f4(v["primary"]), f4(v["dfgls_sim"]), f4(v["p"]), v["wins"], v["wins_sig"]]
                            for k, v in x["cells"].items()]))
        w("")
        w("%s: supera en %d de %d; con McNemar p < 0.05 en %d. Veredicto: **%s**." % (
            name, x["wins"], x["of"], x["wins_with_mcnemar"], "sí" if x["holds"] else "no"))
        if e == "E2":
            w("Lectura alternativa («al menos 3 de las 4 con p < 0.05»): %s." % ("sí" if x["holds_alternative_reading"] else "no"))
        w("")


THETA_KEYS = tuple(E.tname(t) for t in E.THETAS)
REPORT_C = ("0.0", "2.0", "5.0", "10.0", "13.5", "15.0", "20.0", "30.0")


def sec_b92(w, L):
    b = J(FILES["B9.2"])
    cfg = b["config"]
    bud = J("b92_budget_audit9.json")
    rule = b["theta_rule"]
    w("### B9.2 — %s" % TITLES["B9.2"])
    w("")
    w("Presupuesto (CARO, %.0f h): %s; proyección %.2f h; dentro: %s. Control de la calibración frente a producción: peor máx. |Δ| = %s. Paso 0 de las trayectorias reutilizadas (mala especificación frente a B2/B5 de A8; DGP 3 frente a B5): peor máx. |Δ| = %s." % (
        bud["budget_hours"], bud["rule"], bud["projected_total_hours"], bud["within_budget"],
        sci(max(v for c in b["production_control"].values() for v in c.values())), sci(b["paso0_worst"])))
    w("")
    # 1. potencia local
    procs = THETA_KEYS + ("dfgls", "mzt", "msb", "msb_asy", "envelope")
    for case in ("dm", "ct"):
        lp = b["local_power"][case]
        w("**Tabla B9.2.lp.%s. Potencia local asintótica, caso %s** (n = %d, N = %d por c)." % (case, CASE[case], cfg["n_local"], cfg["N_power"]))
        w("")
        L.extend(table(["c"] + [pname(p) + (" sim" if p in ("dfgls", "mzt", "msb") else "") for p in procs],
                       [[c] + [f4(lp["power"][c][p]) for p in procs] for c in REPORT_C]))
        w("")
        w("Brecha a la envolvente (pp):")
        w("")
        gp = lp["gap_to_envelope"]
        L.extend(table(["Procedimiento"] + ["c = %s" % c for c in next(iter(gp.values()))],
                       [[pname(p)] + [pp1(v * 100) for v in gp[p].values()] for p in gp]))
        w("")
        w(note(FILES["B9.2"], cfg["N_power"], cfg["N_cal"], "102 (potencia); calibración: caminos de producción, semilla %d" % cfg["cal_seed"],
               "—", "Envolvente recalculada sobre las trayectorias de la familia 102 (protocolo, lectura 10); máx. |envolvente A9 − A8| = %s. En c = 0 (N = %d, informativo) las tasas son: %s." % (
                   f4(lp["envelope_max_abs_diff_vs_a8"]), next(iter(lp["c0_test_informative"].values()))["n"],
                   ", ".join("%s %s" % (pname(p), star(r)) for p, r in lp["c0_test_informative"].items()))))
        w("")
    # 2. tamano gaussiano
    procs = THETA_KEYS + ("glsb_t0", "rm_t0.1", "msbhac", "adf", "dfgls", "mzt", "msb")
    for case in E.CASES:
        w("**Tabla B9.2.size.%s. Tamaño gaussiano sobre trayectorias independientes, caso %s** (* = dentro de %s)." % (
            case, CASE[case], b["exact_region_20000"]))
        w("")
        L.extend(table(["n"] + [pname(p) + ("" if p in E.RM_LIKE else " sim") for p in procs],
                       [[n] + [star(b["gaussian_size"]["%s|%d" % (case, n)][p]) for p in procs] for n in D.N_ALL]))
        w("")
        w(note(FILES["B9.2"], cfg["N_indep"], cfg["N_cal"], "102 (una celda por n; las mismas trayectorias en los dos casos)",
               b["exact_region_20000"], "RM-like con la nula hac de producción; el resto con el cuantil simulado."))
        w("")
    # 3. mala especificacion
    for case in E.CASES:
        mis = {k: v for k, v in b["misspec"].items() if v["case"] == case}
        w("**Tabla B9.2.mis.%s. Mala especificación, caso %s: tasa y Δ frente a la gaussiana independiente (pp; EE).**" % (case, CASE[case]))
        w("")
        L.extend(table(["Celda"] + [pname(p) for p in THETA_KEYS] + ["Δ " + pname(p) for p in THETA_KEYS],
                       [[label(v["cell"])] + [star(v["rates"][p]) for p in THETA_KEYS]
                        + [dse1(v["delta_vs_independent"][p]) for p in THETA_KEYS]
                        for v in sorted(mis.values(), key=lambda v: (v["kind"], v["n"]))]))
        w("")
        w(note(FILES["B9.2"], cfg["N_sim"], cfg["N_cal"], "trayectorias de A8 (colas pesadas publicadas y GARCH de A7)",
               b["exact_region_5000"], "Δ = tasa mal especificada − tasa gaussiana independiente (N = %d) al mismo n y caso; EE de proporciones independientes." % cfg["N_indep"]))
        w("")
    # 4. tamano igualado por theta
    for pref, lab in (("dgp1_", "DGP 1"), ("ct_power_", "caso con tendencia")):
        eq = {k: v for k, v in b["equalized_power"].items() if k.startswith(pref)}
        w("**Tabla B9.2.eq.%s. %s a tamaño igualado por θ.**" % (pref.rstrip("_"), lab))
        w("")
        cols = THETA_KEYS + ("dfgls", "mzt", "msb")
        L.extend(table(["ρ", "n"] + [pname(p) + ("" if p in E.RM_LIKE else " sim") for p in cols],
                       [[v["rho"], v["n"]] + [rr(v["rates"][p]) for p in cols]
                        for v in sorted(eq.values(), key=lambda v: (v["n"], v["rho"]))]))
        w("")
        w(note(FILES["B9.2"], cfg["N_sim"], cfg["N_cal"], "95 (trayectorias de B5 de A8)", b["exact_region_5000"], "Filas de B9.1."))
        w("")
    # 5. DGP 3
    w("**Tabla B9.2.dgp3. DGP 3 (quiebre de varianza; todas son tasas de tamaño con la nula verdadera).**")
    w("")
    cols = THETA_KEYS + ("rm_t0.1", "adf", "pp", "dfgls", "mzt")
    L.extend(table(["r", "n"] + [pname(p) + ("" if p in E.RM_LIKE else " sim") for p in cols] + ["ADF asy", "DF-GLS asy"],
                   [[v["r"], v["n"]] + [star(v["rates"][p]) for p in cols] + [star(v["rates_asy"]["adf"]), star(v["rates_asy"]["dfgls"])]
                    for v in sorted(b["dgp3"].values(), key=lambda v: (v["n"], v["r"]))]))
    w("")
    w(note(FILES["B9.2"], cfg["N_sim"], cfg["N_cal"], "95 (trayectorias de B5 de A8)", b["exact_region_5000"], "Paso 0 frente a B5."))
    w("")
    # regla
    w("**Tabla B9.2.rule. Regla del θ primario, término a término.**")
    w("")
    rows = []
    for t in THETA_KEYS:
        a1 = rule["A1"][t]
        rows.append([pname(t)] + [star(a1["%s|%d" % (c, n)]) for c in E.CASES for n in (200, 500, 1000)]
                    + [rule["A1_ok"][t], mse(rule["A2_mean_delta"][t]), rule["A2_ok"][t], f4(rule["P"][t]),
                       t in rule["admissible"]])
    L.extend(table(["θ"] + ["A1 %s n = %d" % (CASE[c], n) for c in E.CASES for n in (200, 500, 1000)]
                   + ["A1", "A2 media Δ (pp; EE)", "A2", "P(θ)", "Admisible"], rows))
    w("")
    w("A1: región %s. A2: media de Δ sobre %d celda-caso GARCH con n ≤ 500 (%s); mejor media %s pp; umbral %s pp. P(θ): media de la potencia local demeaned en c ∈ %s. Grupo de empate (a menos de %s pp del máximo): %s. **θ primario: %s** (%s)." % (
        rule["A1_region"], rule["A2_cell_cases"], ", ".join(rule["A2_cells"]), pp2(rule["A2_best_mean"] * 100),
        pp2(rule["A2_threshold_pp"]), rule["P_c"], rule["tie_pp"], [pname(t) for t in rule["tie_group"]],
        "ninguno admisible" if rule["winner"] is None else "%g" % rule["winner_theta"], b["primary_final"]))
    alt = rule["alternative_readings"]
    w("Lecturas alternativas de A2 (solo se reportan): solo demeaned → ganador %s; |media Δ| → ganador %s." % (
        pname(alt["winner_only_demeaned"]) if alt["winner_only_demeaned"] else "ninguno",
        pname(alt["winner_abs_mean"]) if alt["winner_abs_mean"] else "ninguno"))
    w("")
    w("Coste de la construcción (DGP 3, r = 4, n = 200): %s." % ", ".join(
        "%s %s %s" % (pname(t), star(r), wil(r)) for t, r in b["dgp3_cost_r4_n200"].items()))
    w("")


DIFFS = ("a_minus_b", "b_minus_c", "b_minus_msb_sim")
DIFF_LABEL = {"a_minus_b": "(a) − (b): escala", "b_minus_c": "(b) − (c): calibración", "b_minus_msb_sim": "(b) − MSB-GLS sim (control)"}
VARS = ("a", "b", "c", "msb_sim")


def sec_b93(w, L):
    b = J(FILES["B9.3"])
    cfg = b["config"]
    w("### B9.3 — %s" % TITLES["B9.3"])
    w("")
    w("(a) %s; (b) %s; (c) %s; control: %s. Regla: %s. EE: %s." % (cfg["a"], cfg["b"], cfg["c"], cfg["control"], cfg["rule"], cfg["se"]))
    w("")
    w("**Tabla B9.3.size. Tamaño gaussiano (trayectorias independientes de B9.2) y diferencias pareadas (pp; EE).**")
    w("")
    L.extend(table(["Caso", "n"] + [pname(x) for x in VARS] + [DIFF_LABEL[d] for d in DIFFS],
                   [[CASE[v["case"]], v["n"]] + [star(v["rates"][x]) for x in VARS] + [dse(v["diffs"][d]) for d in DIFFS]
                    for v in b["gaussian_size"].values()]))
    w("")
    w(note(FILES["B9.3"], D.N_INDEP, E.N_CAL, "102", b["exact_region_20000"], "Mismas trayectorias para las cuatro columnas."))
    w("")
    w("**Tabla B9.3.mis. Mala especificación: Δ de cada variante (pp; EE) y diferencias de Δ entre variantes.**")
    w("")
    L.extend(table(["Caso", "Celda"] + ["Δ " + pname(x) for x in VARS] + [DIFF_LABEL[d] for d in DIFFS],
                   [[CASE[v["case"]], label(v["cell"])] + [dse1(v["delta_vs_gauss"][x]) for x in VARS]
                    + [dse(v["diffs_of_delta"][d]) for d in DIFFS] for v in b["misspec"].values()]))
    w("")
    w("Media por n de las diferencias de Δ (pp; EE):")
    w("")
    L.extend(table(["Caso", "n", "Celdas"] + [DIFF_LABEL[d] for d in DIFFS],
                   [[CASE[case], n, len(v["cells"])] + [mse(v[d]) for d in DIFFS]
                    for case, byn in b["misspec_by_n"].items() for n, v in byn.items()]))
    w("")
    w(note(FILES["B9.3"], D.N_SIM, E.N_CAL, "trayectorias de A8", b["exact_region_5000"],
           "Diferencia de Δ = diferencia pareada en la celda − diferencia pareada en la gaussiana del mismo n y caso; EE en cuadratura."))
    w("")
    w("**Tabla B9.3.pow. DGP 1 (demeaned) y caso con tendencia: potencia de cada variante y diferencias pareadas (pp; EE).**")
    w("")
    L.extend(table(["Caso", "ρ", "n"] + [pname(x) for x in VARS] + [DIFF_LABEL[d] for d in DIFFS],
                   [[CASE[v["case"]], v["rho"], v["n"]] + [rr(v["rates"][x]) for x in VARS] + [dse(v["diffs"][d]) for d in DIFFS]
                    for v in sorted(b["power"].values(), key=lambda v: (v["case"], v["n"], v["rho"]))]))
    w("")
    w("Media por n (pp; EE):")
    w("")
    L.extend(table(["Caso", "n", "Celdas"] + [DIFF_LABEL[d] for d in DIFFS],
                   [[CASE[case], n, len(v["cells"])] + [mse(v[d]) for d in DIFFS]
                    for case, byn in b["power_by_n"].items() for n, v in byn.items()]))
    w("")
    w(note(FILES["B9.3"], D.N_SIM, E.N_CAL, "95 (trayectorias de B5 de A8)", b["exact_region_5000"], "(c) no está a tamaño igualado por definición."))
    w("")
    w("**Tabla B9.3.lp. Potencia local (n = %d) y diferencias pareadas (pp; EE).**" % D.N_LP)
    w("")
    L.extend(table(["Caso", "c"] + [pname(x) for x in VARS] + [DIFF_LABEL[d] for d in DIFFS],
                   [[CASE[v["case"]], v["c"]] + [f4(v["power"][x]) for x in VARS] + [dse(v["diffs"][d]) for d in DIFFS]
                    for v in b["local_power"].values()]))
    w("")
    w(note(FILES["B9.3"], D.N_POWER, E.N_CAL, "102", "—", ""))
    w("")


def sec_b94(w, L):
    b = J(FILES["B9.4"])
    cfg = b["config"]
    w("### B9.4 — %s" % TITLES["B9.4"])
    w("")
    w("Estadístico: %s (θ primario de B9.2). Muestra de %d réplicas a n = %d (familia 104). KS: %s (umbral %s)." % (
        pname(cfg["statistic"]), cfg["N_big"], cfg["n_big"], cfg["ks_rule"], f4(cfg["ks_threshold"])))
    w("")
    for case in E.CASES:
        r = b["cases"][case]
        w("**Tabla B9.4.ks.%s. KS de dos muestras frente a n = %d, caso %s.**" % (case, cfg["n_big"], CASE[case]))
        w("")
        L.extend(table(["n", "D", "p", "Umbral", "¿Por debajo?"],
                       [[n, f4(v["D"]), sci(v["p_value"]), f4(v["threshold"]), v["below_threshold"]] for n, v in r["ks"].items()]))
        w("")
        w("**Tabla B9.4.cost.%s. Coste de aproximar, caso %s** (tamaño sobre las %d trayectorias independientes de cada n; * = dentro de %s)." % (
            case, CASE[case], cfg["N_indep"], b["exact_region_20000"]))
        w("")
        L.extend(table(["n", "Valor crítico de n = %d" % cfg["n_big"], "Tamaño con él", "Valor crítico en n", "Tamaño con él"],
                       [[n, f4(v["cv_n20000"]), star(v["size_with_cv_n20000"]), f4(v["cv_at_n"]), star(v["size_with_cv_at_n"])]
                        for n, v in r["approximation_cost"].items()]))
        w("")
        cs = r["approximation_cost_comparators"]
        L.extend(table(["n"] + ["%s %s" % (pname(p), k) for p in ("dfgls", "msb") for k in ("asintótico publicado", "simulado en n")],
                       [[n] + [("%s (%s)" % (star(v[p]["size_published_asymptotic"]), "%.3f" % v[p]["published_cv"])) if k == 0 else
                               ("%s (%s)" % (star(v[p]["size_simulated_at_n"]), "%.4f" % v[p]["simulated_cv"]))
                               for p in ("dfgls", "msb") for k in (0, 1)] for n, v in cs.items()]))
        w("")
        w("**Tabla B9.4.mom.%s. E[stat²] por n, caso %s (EE).**" % (case, CASE[case]))
        w("")
        L.extend(table(["n", "σ = 1", "σ̂_HAC"],
                       [[n, "%s (%s)" % (f4(v["E_stat2_sigma1"]), f4(v["se_sigma1"])), "%s (%s)" % (f4(v["E_stat2_hac"]), f4(v["se_hac"]))]
                        for n, v in r["moments"].items()]))
        w("")
        w(note(FILES["B9.4"], cfg["N_indep"], E.N_CAL, "102 (n de la rejilla) y 104 (n = %d)" % cfg["n_big"], b["exact_region_20000"],
               "Entre paréntesis en la tabla de comparadores: el valor crítico usado."))
        w("")


def sec_b95(w, L):
    bud = J("b95_budget_audit9.json")
    w("### B9.5 — %s" % TITLES["B9.5"])
    w("")
    w("Presupuesto (CARO, %.0f h): %s; sondas (s/serie): %s; proyección %.2f h; dentro: %s." % (
        bud["budget_hours"], bud["rule"], ", ".join("n = %s: %.3f" % (k, v) for k, v in bud["probe_sec_per_series"].items()),
        bud["projected_total_hours"], bud["within_budget"]))
    w("")
    if not have("B9.5"):
        w("B9.5 no se ejecutó (§5).")
        w("")
        return
    b = J(FILES["B9.5"])
    cfg = b["config"]
    w("Estadístico: %s; B = %d; residuos: %s; %s; %s; p-valor: %s; semilla: %s." % (
        pname(cfg["statistic"]), cfg["B"], cfg["residuals"], cfg["bootUR_default"],
        "; ".join("n = %s: l = %d, γ = %.4f" % (k, v["l"], v["gamma"]) for k, v in cfg["ar_AWB"].items()), cfg["pvalue"], cfg["seed"]))
    w("")
    w("**Tabla B9.5.1. Calibración AWB frente a la simulada, mismas trayectorias** (* = dentro de %s)." % b["exact_region_2000"])
    w("")
    L.extend(table(["Celda", "n", "AWB", "IC", "Simulada", "IC", "McNemar p", "Pérdida de potencia (pp)"],
                   [[label(k) if k.startswith(("garch", "heavy", "indep")) else k, v["n"], star(v["awb"]), wil(v["awb"]),
                     star(v["sim"]), wil(v["sim"]), mp(v["mcnemar_awb_vs_sim"]), pp2(v["power_loss_pp"])]
                    for k, v in b["cells"].items()]))
    w("")
    w(note(FILES["B9.5"], cfg["N_sim"], E.N_CAL, "105 (remuestreo); trayectorias de A8 (B5, GARCH) y de B9.2 (gaussianas)",
           b["exact_region_2000"], "Máx. |estadístico observado − fila de B9.1/B9.2| = %s." % sci(
               max(v["max_abs_diff_stat_vs_rows"] for v in b["cells"].values()))))
    w("")



def b96_needed():
    b92 = J(FILES["B9.2"])
    theta_changed = b92["primary_theta"] != E.THETA_A8
    awb = have("B9.5") and J(FILES["B9.5"])["rule"]["recommend_awb"]
    return theta_changed, awb


def sec_b96(w, L):
    w("### B9.6 — %s" % TITLES["B9.6"])
    w("")
    changed, awb = b96_needed()
    w("Condición del encargo: θ primario distinto de 0.1 (%s) o variante AWB recomendada (%s)." % (changed, awb))
    w("")
    if have("B9.6"):
        b = J(FILES["B9.6"])
        s = b["summary"]
        w("Datos congelados verificados: %s; `experiments/protocol.md`: %s. θ = %g; variante AWB: %s. La primaria simulada de A9 (θ = %g) frente a la primaria de A8: máx. |Δ p| = %s." % (
            "; ".join("%s %s" % (k, v["match"]) for k, v in b["data_hashes"].items()), b["protocol_hash"]["match"], b["theta"],
            b["awb_variant"], b["theta"], sci(b["final_vs_a8_primary_max_abs_diff_p"])))
        if b["seed_map_after_append"]:
            sm = b["seed_map_after_append"]
            w("Celdas de remuestreo añadidas al final de la familia 106; mapa de semillas recalculado: %d streams nuevos, colisiones con los previos %d, dentro de A9 %d." % (
                sm["new_streams_total"], sm["collisions_new_vs_prior"], sm["collisions_within_new"]))
        w("")
        w("**Tabla B9.6.1. Falsos positivos, detecciones y latencia** (%d celdas de control; %d de evento; α = %s)." % (
            next(iter(s.values()))["fp_cells"], next(iter(s.values()))["event_cells"], b["config"]["alpha"]))
        w("")
        L.extend(table(["Test", "FP media", "FP máxima", "Detecciones", "Latencia media condicional (días)"],
                       [[APP.get(t, t), f4(v["fp_mean"]), f4(v["fp_max"]), "%d de %d" % (v["detections"], v["event_cells"]),
                         "%.1f" % v["mean_latency_detected"] if v["mean_latency_detected"] else "—"] for t, v in s.items()]))
        w("")
        mt = b["matched_rate"]
        w("**Tabla B9.6.2. A tasa de falsas alarmas igualada** (objetivo %s, la tasa agrupada de la primaria simulada; tolerancia %d días; latencia censurada a %d días)." % (
            f4(mt["target_fpr_pooled_primary"]), mt["gap_tolerance"], mt["censor_days"]))
        w("")
        L.extend(table(["Test", "Umbral", "Tasa alcanzada", "Episodios", "Racha media (días)", "Latencia censurada (días)"],
                       [[APP.get(t, t), "%.6f" % v["threshold"], f4(v["achieved_fpr"]), v["false_alarm_episodes"],
                         "%.1f" % v["mean_run_length"], "%.1f" % v["censored_latency_mean"]] for t, v in mt["tests"].items()]))
        w("")
        adv = b["adverse_cells_primary"]
        w("Celdas adversas bajo la regla pre-registrada (primaria simulada frente a %s): %d de %d." % (
            b["config"]["prereg_baselines_for_adverse_rule"], len(adv), s["final"]["fp_cells"]))
        w("")
        w("**Tabla B9.6.3. Tamaño fuera de muestra por D** (N = %d, familia %s; región %s)." % (
            b["oos_size"]["N"], b["oos_size"]["family"], b["oos_size"]["region"]))
        w("")
        L.extend(table(["D", "Primaria simulada", "IC"] + (["AWB", "IC"] if b["oos_size_awb"] else []),
                       [[d, star(v), wil(v)] + ([star(b["oos_size_awb"]["by_D"][d]), wil(b["oos_size_awb"]["by_D"][d])] if b["oos_size_awb"] else [])
                        for d, v in b["oos_size"]["by_D"].items()]))
        w("")
        w("**Tabla B9.6.4. Filas nuevas de la tabla de desviaciones del registro.**")
        w("")
        L.extend(table(["Id", "Auditoría", "Elemento", "Pre-registrado / anterior", "Desplegado", "Efecto antes", "Efecto después"],
                       [[r["id"], r["audit"], r["element"], r["preregistered_value"], r["deployed_value"],
                         fmt_effect(r["effect_before"]), fmt_effect(r["effect_after"])] for r in b["deviation_rows"]]))
        w("")
        w(note(FILES["B9.6"], b["oos_size"]["N"], b["config"]["N_cal"], "106", b["oos_size"]["region"],
               "Comparadores: %s." % b["config"]["comparators"]))
        w("")
        return
    b6 = J("b6_application_audit8.json")
    s = b6["summary"][b6["primary_key"]]
    w("No se repite B6 (§5): se reutiliza B6 de A8 con la primaria RM-GLS θ = 0.1 y se arrastran sus números: FP media %s (máx. %s), %d detecciones de %d, latencia media %s días; a tasa igualada (%s), %d episodios de falsa alarma (`b6_application_audit8.json`)." % (
        f4(s["fp_mean"]), f4(s["fp_max"]), s["detections"], s["event_cells"], "%.1f" % s["mean_latency_detected"],
        f4(b6["matched_rate"]["target_fpr_pooled_primary"]), b6["matched_rate"]["tests"][b6["primary_key"]]["false_alarm_episodes"]))
    w("")


def sec_b97(w, L):
    w("### B9.7 — %s" % TITLES["B9.7"])
    w("")
    if have("B9.7"):
        b = J(FILES["B9.7"])
        cfg = b["config"]
        tp = b["primary_theta"]
        w("CSV completo: `%s` (sha256 `%s`); N_cal = %d por (caso, n), familia 107, calibración %s, anclaje %s, cola %s; EE del cuantil por bootstrap (%d remuestreos)." % (
            b["csv"], b["csv_sha256"], cfg["N_cal"], cfg["calibration"], cfg["anchor"], cfg["tail"], cfg["bootstrap_se"]))
        w("")
        w("**Tabla B9.7.1. Valores críticos del θ primario (θ = %g) y EE.**" % tp)
        w("")
        rows = []
        for case in ("dm", "ct"):
            for n in cfg["n"]:
                v = b["table"]["%s|%g|%d" % (case, tp, n)]
                rows.append([CASE[case], n] + ["%s (%s)" % (f4(v["cv"]["%g" % a]), f4(v["se"]["%g" % a])) for a in cfg["alphas"]])
        L.extend(table(["Caso", "n"] + ["α = %g" % a for a in cfg["alphas"]], rows))
        w("")
        w("**Tabla B9.7.2. Sensibilidad: valor crítico al 5% por θ.**")
        w("")
        L.extend(table(["Caso", "n"] + ["θ = %g" % t for t in cfg["thetas"]],
                       [[CASE[case], n] + [f4(b["table"]["%s|%g|%d" % (case, t, n)]["cv"]["0.05"]) for t in cfg["thetas"]]
                        for case in ("dm", "ct") for n in cfg["n"]]))
        w("")
        au = b["cross_seed_audit"]
        w("Auditoría de semilla cruzada (%s; %d celdas): desviación máxima %s (%s EE). Por celda: %s." % (
            au["ranking"], len(au["cells"]), f4(au["max_abs_deviation"]), "%.1f" % au["max_abs_deviation_in_se"],
            "; ".join("%s: %s (%.1f EE)" % (k, f4(v["max_abs_deviation"]), v["max_abs_deviation_in_se"]) for k, v in au["by_cell"].items())))
        w("")
        w(note(FILES["B9.7"], "—", cfg["N_cal"], "107", "—", "Caminos independientes por caso."))
        w("")
    if have("FIG"):
        f = J(FILES["FIG"])
        w("**Tabla B9.7.3. Figuras** (generador `experiments/make_figures_audit9.py`; fuentes: %s)." % ", ".join("`%s`" % s for s in f["sources"]))
        w("")
        L.extend(table(["Figura", "sha256", "Bytes", "Copia", "sha256 de la copia"],
                       [[k, "`%s`" % v["sha256"], v["bytes"], v["paper_copy"], "`%s`" % v["paper_copy_sha256"]] for k, v in f["figures"].items()]))
        w("")
        for k, v in f["notes"].items():
            w("- %s: %s." % (k, v))
        w("")


def paso0_rows():
    rows = []
    if have("B9.1"):
        b = J(FILES["B9.1"])
        rows.append(["B9.1", "trayectorias de B5 (51 celdas, 50 réplicas): columnas comunes con los checkpoints de A8", sci(b["paso0_worst"])])
    if have("B9.2"):
        b = J(FILES["B9.2"])
        rows.append(["B9.2", "mala especificación (22 celdas; demeaned frente a B2, tendencia frente a B5 ct_garch) y DGP 3 (15 celdas)",
                     sci(b["paso0_worst"])])
        rows.append(["B9.1–B9.4", "calibración: RM-GLS θ = 0.1 y θ = 0 (`hac`) frente a `_simulate_null_statistics` de producción, 8 n × 2 casos",
                     sci(max(v for c in b["production_control"].values() for v in c.values()))])
    if have("B9.5"):
        b = J(FILES["B9.5"])
        rows.append(["B9.5", "estadístico observado frente a las filas de B9.1/B9.2", sci(max(v["max_abs_diff_stat_vs_rows"] for v in b["cells"].values()))])
    return rows


def deviations():
    rows = [
        ["Familia de B9.2 = 102 (el texto de B9.2 dice 101)", "Una familia por bloque (sustituciones del encargo)", "antes", "Ninguno; sin colisiones (Tabla B9.0.3)"],
        ["Calibración de todos los procedimientos sobre los caminos de producción (semilla 42), no sobre una familia nueva",
         "La nula de la primaria es la de producción; (a) y (b) de B9.3 comparten la muestra de calibración", "antes",
         "La columna RM-GLS θ = 0.1 reproduce la nula de producción bit a bit (§3)"],
        ["Familias 100, 101 y 103 sin celdas", "B9.0 y B9.3 no simulan; B9.1 usa trayectorias de A8 y la calibración de producción", "antes", "Ninguno"],
        ["KPSS simulado como contraste de raíz unitaria (cola inferior) y ZA simulado en la cola inferior", "El encargo no fija la regla", "antes", "Se reportan también las columnas asintóticas de A8"],
        ["E1: cada celda debe superar a DF-GLS-sim y a MZ_t-GLS-sim, y la cuenta de McNemar exige p < 0.05 frente a ambos con la primaria mayor",
         "Lectura conservadora", "antes", "Se reportan los p de cada comparación"],
        ["E2: supera en las cuatro ρ y con p < 0.05 en al menos 3", "Lectura conservadora", "antes", "Se reporta también la lectura alternativa"],
        ["A2: «las 16 celdas GARCH con n ≤ 500» = 8 celdas × 2 casos; «peor» = media de Δ mayor", "Solo hay 8 celdas GARCH con n ≤ 500",
         "antes", "Se reportan las lecturas alternativas y su ganador (Tabla B9.2.rule)"],
        ["Desempate: grupo de admisibles a menos de 1 pp del máximo de P; gana el mayor θ del grupo", "Lectura literal", "antes", "—"],
        ["Tamaño gaussiano de B9.2 con las mismas trayectorias para los dos casos", "Los estadísticos del caso con tendencia son invariantes a la tendencia; ahorro de cómputo",
         "antes", "Las tasas de los dos casos no son independientes entre sí"],
        ["Envolvente recalculada sobre la familia 102 (umbral en la calibración de producción, N = 50000)",
         "La de A8 no es reutilizable bit a bit", "antes", "Diferencia con A8 en las tablas B9.2.lp"],
        ["(b) de B9.3 = el mismo estadístico con s²_AR; (c) = MSB-GLS de Ng–Perron; MSB-GLS sim como control de la diferencia de convención",
         "(b) y (c) difieren también en ᾱ e índices", "antes", "Columna de control en B9.3"],
        ["B9.4: DF-GLS con −1.95 / −2.89 (ERS 1996) y MSB con 0.233 / 0.168 (Ng–Perron 2001)", "«valores críticos asintóticos publicados»", "antes",
         "La columna asintótica de A8 (p-valor de `arch`) se reporta en B9.1"],
        ["B9.5: AWB con residuos de retardo 0 e intercepto, ξ₁ estacionario", "Esquema de `boot_adf` usado en A6–A8", "antes", "—"],
        ["B9.7: auditoría cruzada sobre las celdas de mayor EE absoluto (A8 usó el relativo)", "Literal del encargo", "antes", "—"],
        ["B9.1 se lanzó primero suelto y se detuvo para pasar a la cadena reanudable; la cadena reutilizó los trozos ya escritos",
         "Ejecución", "durante B9.1", "Ninguno: los trozos son deterministas por índice"],
    ]
    rows.append(["`b92_budget_audit9.json` registra `code_all_committed = False`: el único archivo sin commitear al escribirlo era el generador del reporte (`audit9_generate_report.py`)",
                 "El generador se escribía mientras corría la cadena; no interviene en ningún cálculo", "durante B9.2",
                 "Ninguno sobre valores; no se regenera porque repetir la sonda con las calibraciones ya escritas cambiaría la proyección registrada"])
    rows.append(["Checkpoints JSON de B9.1 y B9.2 sin commitear (y las muestras npz de calibración y de B9.7)", "Tamaño (del orden de GB)", "después",
                 "Número de lotes y sha256 agregado en §3; se regeneran bit a bit desde sus semillas"])
    if have("B9.6") and J(FILES["B9.6"])["awb_variant"]:
        rows.append(["B9.6: celdas de remuestreo AWB (aplicación y tamaño fuera de muestra) añadidas al final de la familia 106 y script de B9.6 ampliado con la variante AWB",
                     "B9.5 recomendó la variante AWB, lo que activa B9.6", "después de ver B9.5",
                     "Mapa de semillas recalculado y guardado en `b96_application_audit9.json`"])
    return rows


def gates(L):
    rows = []
    if have("B9.1"):
        b = J(FILES["B9.1"])
        rows.append(["Paso 0 de B9.1 (máx. |Δ| = 0)", "Primeras 50 réplicas frente a los checkpoints de A8", sci(b["paso0_worst"]),
                     verdict(b["paso0_worst"] == 0), "—"])
        for e in ("E1", "E2"):
            x = b[e]
            rows.append(["%s (INFORMATIVA)" % e, protocol_section("### COMPUERTA B9.1").split("* %s" % e)[1].split("* E")[0].strip()
                         if e == "E1" else protocol_section("### COMPUERTA B9.1").split("* E2")[1].split("No detiene")[0].strip(),
                         "supera en %d de %d; con McNemar p < 0.05 en %d" % (x["wins"], x["of"], x["wins_with_mcnemar"]),
                         "sí" if x["holds"] else "no", "No detiene"])
    if have("B9.2"):
        b = J(FILES["B9.2"])
        bud = J("b92_budget_audit9.json")
        rule = b["theta_rule"]
        rows.append(["Presupuesto de B9.2 (CARO, %.0f h)" % bud["budget_hours"], bud["rule"], "%.2f h" % bud["projected_total_hours"],
                     "dentro" if bud["within_budget"] else "EXCEDE", "Ejecutado" if bud["within_budget"] else "No se lanza"])
        rows.append(["Paso 0 de B9.2 (máx. |Δ| = 0)", "Mala especificación y DGP 3 frente a A8", sci(b["paso0_worst"]),
                     verdict(b["paso0_worst"] == 0), "—"])
        rows.append(["Regla del θ primario (DURA)", protocol_section("### REGLA B9.2"),
                     "; ".join("θ = %s: A1 %s, A2 %s (media Δ %s pp), P %s" % (
                         t.replace("gls_t", ""), rule["A1_ok"][t], rule["A2_ok"][t], pp2(rule["A2_mean_delta"][t]["mean"] * 100),
                         f4(rule["P"][t])) for t in THETA_KEYS),
                     "θ = %s" % ("—" if rule["winner"] is None else "%g" % rule["winner_theta"]),
                     "Continuar con B9.3" if rule["winner"] is not None else "Detiene: ningún θ admisible"])
    if os.path.exists(os.path.join(C.RESULTS, "b95_budget_audit9.json")):
        bud = J("b95_budget_audit9.json")
        rows.append(["Presupuesto de B9.5 (CARO, %.0f h)" % bud["budget_hours"], bud["rule"], "%.2f h" % bud["projected_total_hours"],
                     "dentro" if bud["within_budget"] else "EXCEDE", "Ejecutado" if bud["within_budget"] else "No se lanza"])
    if have("B9.5"):
        r = J(FILES["B9.5"])["rule"]
        rows.append(["Regla B9.5 (INFORMATIVA)", protocol_section("### REGLA B9.5"),
                     "(i) %d de %d dentro (mínimo %d); (ii) pérdida de potencia (pp): %s (umbral %s)" % (
                         r["i_in_region_dgp3"], r["i_of"], r["i_min"],
                         ", ".join("%s %s" % (k, pp2(v)) for k, v in r["ii_power_loss_pp"].items()), pp2(r["ii_threshold_pp"])),
                     "recomendar AWB: %s" % ("sí" if r["recommend_awb"] else "no"), "No detiene"])
    L.extend(table(["Compuerta", "Criterio (literal del protocolo)", "Medido", "Veredicto", "Acción"], rows))


def provenance_section(w, L):
    man = J("manifest_audit9.json")
    w("**Archivos que alimentan las tablas** (`manifest_audit9.json`; el propio reporte se registra después de escribirse).")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "mtime (UTC)", "Script", "Commit", "Código commiteado"],
                   [[k, "`%s`" % e["sha256"], e["bytes"], e["mtime_utc"], e["script"], e["commit"][:7], e["code_all_committed"]]
                    for k, e in sorted(man["entries"].items()) if not k.endswith("resultados_auditoria_9.md")]))
    w("")
    npz = sorted(glob.glob(os.path.join(C.CKPT_ROOT, "audit9_cal", "cal_n*.npz")))
    w("Muestras de calibración (npz, no se commitean; se regeneran bit a bit desde la semilla 42 de producción):")
    w("")
    L.extend(table(["Archivo", "sha256"], [[C.rel(p), "`%s`" % C.sha256_file(p)] for p in npz]))
    w("")
    import audit9_b90_protocol as B90
    w("Carpetas de checkpoints JSON de A9 (las de B9.1 y B9.2 no se commitean por tamaño; se regeneran bit a bit desde sus semillas):")
    w("")
    L.extend(table(["Carpeta", "Lotes JSON", "sha256 agregado"],
                   [[d, r["json_batches"], "`%s`" % r["aggregate_sha256"]] for d, r in
                    ((d, B90.ckpt_record(d)) for d in ("audit9_b91", "audit9_b92", "audit9_b94", "audit9_b95", "audit9_b96"))]))
    w("")
    w("**Paso 0 y controles.**")
    w("")
    L.extend(table(["Bloque", "Qué se compara", "Peor máx. |Δ|"], paso0_rows()))
    w("")
    py = pytest_summary()
    if py is not None:
        c = py["counts"]
        w("- Suite completa (`pytest_audit9.log`): collected %s; passed %d; failed %d; skipped %d; %.1f s." % (
            py["collected"], c.get("passed", 0), c.get("failed", 0), c.get("skipped", 0), py["seconds"]))
        w("- Test de literales (`tests/test_no_literals_audit9.py`): %s." % ("; ".join("%s %s" % t for t in py["literals"])))
        w("")


def not_executed():
    rows = []
    for blk in ("B9.1", "B9.2", "B9.3", "B9.4", "B9.5", "B9.7"):
        if not have(blk):
            rows.append([blk + " — " + TITLES[blk], "Sin JSON de resultados", "`python %s --cores 14`" % SCRIPTS[blk]])
    if have("B9.2") and not have("B9.6"):
        changed, awb = b96_needed()
        if not changed and not awb:
            rows.append(["B9.6 — %s" % TITLES["B9.6"], "θ = 0.1 sobrevive y no se recomienda AWB: se reutiliza B6 de A8 y se arrastran sus números",
                         "—"])
        else:
            rows.append(["B9.6 — %s" % TITLES["B9.6"], "Pendiente", "`python %s --cores 14`" % SCRIPTS["B9.6"]])
    rows.append(["MZ_α y MP_T como comparadores", "Retirados en A8 (enmienda 1); A9 no los reincorpora", "—"])
    rows.append(["AWB DF-GLS en B9.1", "Se arrastra de A8 sin recalcular (encargo, B9.1 punto 3)", "—"])
    return rows


def claim_status(c):
    k = c["key"]
    if k in ("dominance_intro", "dominance_dgp1") and have("B9.1"):
        b = J(FILES["B9.1"])
        cells = {kk: v for kk, v in b["cells"].items() if kk.startswith("dgp1_")}
        d_asy = [(v["rates_sim"]["gls_t0.1"]["rate"] - v["rates_asy"]["adf"]["rate"]) * 100 for v in cells.values()]
        d_sim = [(v["rates_sim"]["gls_t0.1"]["rate"] - v["rates_sim"]["adf"]["rate"]) * 100 for v in cells.values()]
        v = cells["dgp1_rho0p99_n1000"]
        return ("medido con la primaria RM-GLS θ = 0.1 en las %d celdas de DGP 1: ventaja sobre ADF asintótico de %s a %s pp; sobre ADF simulado (tamaño igualado) de %s a %s pp; en (0.99, 1000): %s (asy) y %s (sim) pp (Tabla B9.1.dgp1)" % (
            len(cells), pp1(min(d_asy)), pp1(max(d_asy)), pp1(min(d_sim)), pp1(max(d_sim)),
            pp1((v["rates_sim"]["gls_t0.1"]["rate"] - v["rates_asy"]["adf"]["rate"]) * 100),
            pp1((v["rates_sim"]["gls_t0.1"]["rate"] - v["rates_sim"]["adf"]["rate"]) * 100)))
    if k == "garch_11" and have("B9.2"):
        b = J(FILES["B9.2"])
        p = E.tname(b["primary_theta"])
        g = [v for v in b["misspec"].values() if v["kind"] == "garch" and v["case"] == "c"]
        return ("con la configuración final (%s, demeaned) %d de %d GARCH dentro de la región; ADF asy %d, PP asy %d, ADF sim %d (Tabla B9.2.mis.c)" % (
            pname(p), sum(v["rates"][p]["in_region"] for v in g), len(g), sum(v["rates"]["adf_asy"]["in_region"] for v in g),
            sum(v["rates"]["pp_asy"]["in_region"] for v in g), sum(v["rates"]["adf"]["in_region"] for v in g)))
    if k in ("exact_intro", "exact_p1") and have("B9.2"):
        b = J(FILES["B9.2"])
        p = E.tname(b["primary_theta"])
        gs = [(key, v[p]) for key, v in b["gaussian_size"].items()]
        out_ = [key for key, v in gs if not v["in_region"]]
        g = [v for v in b["misspec"].values() if v["case"] == "c"]
        txt = "tamaño gaussiano de %s dentro de la región exacta de N = %d en %d de %d (caso, n); fuera: %s; en la mala especificación demeaned, %d de %d celdas dentro de la región de N = %d" % (
            pname(p), D.N_INDEP, len(gs) - len(out_), len(gs), out_ or "ninguno", sum(v["rates"][p]["in_region"] for v in g), len(g), D.N_SIM)
        if have("B9.4"):
            b4 = J(FILES["B9.4"])
            v = b4["cases"]["c"]["approximation_cost"]["200"]
            txt += "; a n = 200 con el valor crítico de n = %d el tamaño es %s (Tabla B9.4.cost.c)" % (D.N_BIG_N, f4(v["size_with_cv_n20000"]["rate"]))
        return txt
    if k == "trend_size" and have("B9.2"):
        b = J(FILES["B9.2"])
        p = E.tname(b["primary_theta"])
        return "con la configuración final (%s, tendencia) y N = %d independientes: %s" % (
            pname(p), D.N_INDEP, ", ".join("n = %d: %s" % (n, f4(b["gaussian_size"]["ct|%d" % n][p]["rate"])) for n in (200, 500, 1000)))
    if k in ("fp_028", "detections_13"):
        if have("B9.6"):
            s = J(FILES["B9.6"])["summary"]
            if k == "fp_028":
                return "el R̂ publicado da FP media %s; la configuración final da %s (simulada)%s (Tabla B9.6.1)" % (
                    f4(s["rhat_prereg"]["fp_mean"]), f4(s["final"]["fp_mean"]),
                    " y %s (AWB)" % f4(s["final_awb"]["fp_mean"]) if "final_awb" in s else "")
            return "el R̂ publicado da %d de %d; la configuración final, %d (simulada)%s (Tabla B9.6.1)" % (
                s["rhat_prereg"]["detections"], s["rhat_prereg"]["event_cells"], s["final"]["detections"],
                " y %d (AWB)" % s["final_awb"]["detections"] if "final_awb" in s else "")
        b6 = J("b6_application_audit8.json")
        s = b6["summary"]
        pk = b6["primary_key"]
        if k == "fp_028":
            return "el R̂ publicado da FP media %s; la configuración final (B6 de A8 arrastrado, RM-GLS θ = 0.1) da %s" % (
                f4(s["rhat_prereg"]["fp_mean"]), f4(s[pk]["fp_mean"]))
        return "el R̂ publicado da %d de %d; la configuración final (B6 de A8 arrastrado), %d" % (
            s["rhat_prereg"]["detections"], s["rhat_prereg"]["event_cells"], s[pk]["detections"])
    return "no evaluada: bloque no ejecutado"


A8_KEY = {"gls_t0.1": "rmgls", "rm_t0.1": "rm", "adf": "adf", "pp": "pp", "dfgls": "dfgls", "mzt": "mzt", "msb": "msb",
          "kpss": "kpss", "za": "za"}


def anomalies():
    out = []
    if have("B9.1"):
        b = J(FILES["B9.1"])
        worst, where = 0.0, None
        for k, v in b["cells"].items():
            for p, a8k in A8_KEY.items():
                if a8k in v["a8_rates"]:
                    mine = v["rates_asy"][p]["rate"] if p in v["rates_asy"] else v["rates_sim"][p]["rate"]
                    d = abs(mine - v["a8_rates"][a8k])
                    if d > worst:
                        worst, where = d, "%s/%s" % (k, p)
        out.append("**Reproducción de las tasas de B5 de A8 con las filas recalculadas.** Máx. |tasa A9 − tasa A8| = %s (%s) sobre %d celdas; Paso 0 de filas: %s." % (
            f4(worst), where or "todas las celdas", len(b["cells"]), sci(b["paso0_worst"])))
    if have("B9.2"):
        b = J(FILES["B9.2"])
        rule = b["theta_rule"]
        fails = ["%s %s (%s)" % (pname(t), k, f4(r["rate"])) for t, a in rule["A1"].items() for k, r in a.items() if not r["in_region"]]
        out.append("**Tamaño gaussiano fuera de la región exacta de N = %d en los n de A1** (%s): %s." % (
            D.N_INDEP, rule["A1_region"], "; ".join(fails) if fails else "ninguno"))
        wkey = rule["winner"]
        if wkey is not None:
            lo = rule["A1_region"][0]
            k_min = min(rule["A1"][wkey], key=lambda k: rule["A1"][wkey][k]["rate"] - lo)
            r = rule["A1"][wkey][k_min]
            out.append("**Margen del θ ganador en A1.** La tasa más cercana al límite inferior de %s es %s (%s): %s por encima. Celdas de A1 donde fallan los demás θ: %s. N_cal de la calibración: %d; no se atribuye causa." % (
                pname(wkey), k_min, f4(r["rate"]), f4(r["rate"] - lo),
                sorted({k for t, a in rule["A1"].items() if t != wkey for k, v in a.items() if not v["in_region"]}), E.N_CAL))
        p = E.tname(b["primary_theta"])
        other = ["%s n = %s: %s" % (CASE[k.split("|")[0]], k.split("|")[1], f4(v[p]["rate"])) for k, v in b["gaussian_size"].items()
                 if not v[p]["in_region"] and int(k.split("|")[1]) not in (200, 500, 1000)]
        out.append("**Tamaño gaussiano de la primaria fuera de la región en los n fuera de A1**: %s." % ("; ".join(other) if other else "ninguno"))
        out.append("**Envolvente recalculada frente a la de A8** (misma definición, trayectorias distintas): máx. |Δ| %s (demeaned) y %s (tendencia)." % (
            f4(b["local_power"]["dm"]["envelope_max_abs_diff_vs_a8"]), f4(b["local_power"]["ct"]["envelope_max_abs_diff_vs_a8"])))
    if have("B9.4"):
        b = J(FILES["B9.4"])
        for case in E.CASES:
            ks = b["cases"][case]["ks"]
            out.append("**KS frente a n = %d, caso %s**: por encima del umbral en %s." % (
                D.N_BIG_N, CASE[case], ", ".join("n = %s (D = %s)" % (n, f4(v["D"])) for n, v in ks.items() if not v["below_threshold"]) or "ningún n"))
    if have("B9.7"):
        b97 = J(FILES["B9.7"])
        au = b97["cross_seed_audit"]
        big = [(k, v) for k, v in au["by_cell"].items() if v["max_abs_deviation_in_se"] > 3]
        txt = "**Auditoría de semilla cruzada de B9.7**: máx. desviación %s = %.1f EE del bootstrap; celdas por encima de 3 EE: %s." % (
            f4(au["max_abs_deviation"]), au["max_abs_deviation_in_se"],
            "; ".join("%s (%s, %.1f EE; valor crítico al 5%% %s, independiente %s)" % (
                k, f4(v["max_abs_deviation"]), v["max_abs_deviation_in_se"], f4(b97["table"][k]["cv"]["0.05"]), f4(v["cv_independent"]["0.05"]))
                for k, v in big) or "ninguna")
        tp = b97["primary_theta"]
        a8 = J("b7_critical_values_audit8.json")["table"].get("dm|gls|%g|5000" % tp)
        if a8 is not None and have("B9.4"):
            txt += " Mismo valor crítico (demeaned, θ = %g, n = 5000, α = 0.05) en otras muestras: A8 (familia 97) %s; calibración de producción (semilla 42, N_cal = %d) %s. No se atribuye causa." % (
                tp, f4(a8["cv"]["0.05"]), E.N_CAL, f4(J(FILES["B9.4"])["cases"]["c"]["approximation_cost"]["5000"]["cv_at_n"]))
        out.append(txt)
    return out


def conclusions(w):
    b91, b92, b93 = J(FILES["B9.1"]), J(FILES["B9.2"]), J(FILES["B9.3"])
    rule = b92["theta_rule"]
    p = E.tname(b92["primary_theta"])
    lp = b92["local_power"]
    i = [0]

    def item(text):
        i[0] += 1
        w("%d. %s" % (i[0], text))
    item("**θ primario: %g; P(θ) = %s** (Tabla B9.2.rule). P por θ: %s; admisibles: %s." % (
        b92["primary_theta"], f4(rule["P"][p]), ", ".join("θ = %s: %s" % (t.replace("gls_t", ""), f4(v)) for t, v in rule["P"].items()),
        ", ".join(t.replace("gls_t", "θ = ") for t in rule["admissible"])))
    item("**Brecha a la envolvente (pp) en c = 5, 10 y 20** (Tablas B9.2.lp): %s." % "; ".join(
        "%s — %s" % (CASE[case], ", ".join("%s %s" % (pname(q), "/".join(pp1(lp[case]["gap_to_envelope"][q][c] * 100) for c in ("5.0", "10.0", "20.0")))
                                           for q in (p, "dfgls", "msb")))
        for case in ("dm", "ct")))
    item("**E1 %s, E2 %s** (Tablas B9.1.E1 y B9.1.E2): E1, supera a DF-GLS-sim y a MZ_t-GLS-sim en %d de %d celdas con tendencia, con McNemar p < 0.05 en %d; E2, supera a DF-GLS-sim en %d de %d ρ, con p < 0.05 en %d." % (
        "sí" if b91["E1"]["holds"] else "no", "sí" if b91["E2"]["holds"] else "no", b91["E1"]["wins"], b91["E1"]["of"],
        b91["E1"]["wins_with_mcnemar"], b91["E2"]["wins"], b91["E2"]["of"], b91["E2"]["wins_with_mcnemar"]))
    g = b93["gaussian_size"]
    mb = b93["misspec_by_n"]["c"]
    item("**Atribución (B9.3), (a) − (b) escala y (b) − (c) calibración, en pp (EE)**: tamaño gaussiano n = 200 demeaned %s y %s, tendencia %s y %s; media de Δ en la mala especificación demeaned a n = 200 %s y %s; potencia local c = 10 demeaned %s y %s (Tablas B9.3)." % (
        dse(g["c|200"]["diffs"]["a_minus_b"]), dse(g["c|200"]["diffs"]["b_minus_c"]), dse(g["ct|200"]["diffs"]["a_minus_b"]),
        dse(g["ct|200"]["diffs"]["b_minus_c"]), mse(mb["200"]["a_minus_b"]), mse(mb["200"]["b_minus_c"]),
        dse(b93["local_power"]["dm|10"]["diffs"]["a_minus_b"]), dse(b93["local_power"]["dm|10"]["diffs"]["b_minus_c"])))
    cost = b92["dgp3_cost_r4_n200"]
    txt = "**DGP 3, r = 4, n = 200**: primaria con calibración simulada %s %s" % (f4(cost[p]["rate"]), wil(cost[p]))
    if have("B9.5"):
        b95 = J(FILES["B9.5"])
        c4 = b95["cells"]["dgp3_r4_n200"]
        txt += ", con calibración AWB %s %s" % (f4(c4["awb"]["rate"]), wil(c4["awb"]))
    if p != "gls_t0":
        txt += "; θ = 0 con calibración simulada %s" % f4(cost["gls_t0"]["rate"])
    item(txt + " (Tablas B9.2.dgp3 y B9.5.1).")
    if have("B9.4"):
        b94 = J(FILES["B9.4"])
        rows = []
        for case in E.CASES:
            v = b94["cases"][case]["approximation_cost"]["200"]
            cs = b94["cases"][case]["approximation_cost_comparators"]["200"]
            rows.append("%s — primaria %s (valor crítico de n = %d) frente a %s (valor crítico en n); DF-GLS %s (publicado) frente a %s (simulado); MSB-GLS %s frente a %s" % (
                CASE[case], f4(v["size_with_cv_n20000"]["rate"]), D.N_BIG_N, f4(v["size_with_cv_at_n"]["rate"]),
                f4(cs["dfgls"]["size_published_asymptotic"]["rate"]), f4(cs["dfgls"]["size_simulated_at_n"]["rate"]),
                f4(cs["msb"]["size_published_asymptotic"]["rate"]), f4(cs["msb"]["size_simulated_at_n"]["rate"])))
        item("**Coste de aproximar a n = 200** (Tablas B9.4.cost): %s." % "; ".join(rows))
    gs = b92["gaussian_size"]
    item("**Tamaño gaussiano de la primaria** (N = %d independientes; Tablas B9.2.size): %s." % (D.N_INDEP, "; ".join(
        "%s — %s" % (CASE[case], ", ".join("n = %d: %s" % (n, star(gs["%s|%d" % (case, n)][p])) for n in D.N_ALL)) for case in E.CASES)))
    v = b91["cells"]["dgp1_rho0p95_n200"]
    item("**DGP 1, ρ = 0.95, n = 200, tamaño igualado**: primaria θ = 0.1 %s, ADF-sim %s, DF-GLS-sim %s, MZ_t-GLS-sim %s; con valores asintóticos ADF %s y DF-GLS %s (Tabla B9.1.dgp1)." % (
        rr(v["rates_sim"]["gls_t0.1"]), rr(v["rates_sim"]["adf"]), rr(v["rates_sim"]["dfgls"]), rr(v["rates_sim"]["mzt"]),
        rr(v["rates_asy"]["adf"]), rr(v["rates_asy"]["dfgls"])))
    if have("B9.5"):
        r = J(FILES["B9.5"])["rule"]
        item("**Regla B9.5**: (i) %d de %d celdas de DGP 3 dentro de la región; (ii) pérdida de potencia en DGP 1 %s pp; recomendar AWB: %s." % (
            r["i_in_region_dgp3"], r["i_of"], ", ".join(pp2(x) for x in r["ii_power_loss_pp"].values()), "sí" if r["recommend_awb"] else "no"))
    changed, awb = b96_needed()
    if have("B9.6"):
        b6 = J(FILES["B9.6"])
        s = b6["summary"]
        item("**Aplicación con la configuración final** (Tablas B9.6): %s." % "; ".join(
            "%s FP media %s (máx. %s), %d detecciones de %d" % (APP[t], f4(s[t]["fp_mean"]), f4(s[t]["fp_max"]), s[t]["detections"], s[t]["event_cells"])
            for t in ("final", "final_awb", "rhat_prereg") if t in s))
    elif not changed and not awb:
        b6 = J("b6_application_audit8.json")
        s = b6["summary"][b6["primary_key"]]
        item("**Aplicación**: no se repite; B6 de A8 (RM-GLS θ = 0.1): FP media %s (máx. %s), %d detecciones de %d." % (
            f4(s["fp_mean"]), f4(s["fp_max"]), s["detections"], s["event_cells"]))


def facts(b91, b92):
    out = []
    rule = b92["theta_rule"]
    p = E.tname(b92["primary_theta"])
    out.append(("primary_theta", "%g" % b92["primary_theta"], "—", FILES["B9.2"], "primary_theta"))
    for t, v in rule["P"].items():
        out.append(("P_theta|%s" % t, f4(v), "—", FILES["B9.2"], "theta_rule/P/%s" % t))
    for t, v in rule["A2_mean_delta"].items():
        out.append(("A2_mean_delta_garch_n_le_500|%s" % t, pp2(v["mean"] * 100) + " pp", "EE %s pp" % se2(v["se"] * 100), FILES["B9.2"],
                    "theta_rule/A2_mean_delta/%s/mean" % t))
    for case in ("dm", "ct"):
        for q in (p, "gls_t0", "dfgls", "msb", "mzt"):
            for c in ("5.0", "10.0", "20.0"):
                out.append(("gap_envelope|%s|%s|c%s" % (case, q, c), pp1(b92["local_power"][case]["gap_to_envelope"][q][c] * 100) + " pp", "—",
                            FILES["B9.2"], "local_power/%s/gap_to_envelope/%s/%s" % (case, q, c)))
    for case in E.CASES:
        for n in D.N_ALL:
            r = b92["gaussian_size"]["%s|%d" % (case, n)][p]
            out.append(("size_gauss_indep|%s|n%d" % (case, n), f4(r["rate"]), wil(r), FILES["B9.2"], "gaussian_size/%s|%d/%s/rate" % (case, n, p)))
    for e in ("E1", "E2"):
        x = b91[e]
        out.append((e, "sí" if x["holds"] else "no", "%d de %d; McNemar %d" % (x["wins"], x["of"], x["wins_with_mcnemar"]), FILES["B9.1"], "%s/holds" % e))
    for t, r in b92["dgp3_cost_r4_n200"].items():
        out.append(("dgp3_r4_n200|%s|sim" % t, f4(r["rate"]), wil(r), FILES["B9.2"], "dgp3_cost_r4_n200/%s/rate" % t))
    if have("B9.3"):
        b93 = J(FILES["B9.3"])
        for key, v in b93["gaussian_size"].items():
            for d in ("a_minus_b", "b_minus_c"):
                out.append(("attr_size|%s|%s" % (key, d), pp2(v["diffs"][d]["delta"] * 100) + " pp", "EE %s pp" % se2(v["diffs"][d]["se"] * 100),
                            FILES["B9.3"], "gaussian_size/%s/diffs/%s/delta" % (key, d)))
    if have("B9.4"):
        b94 = J(FILES["B9.4"])
        for case in E.CASES:
            v = b94["cases"][case]["approximation_cost"]["200"]
            out.append(("approx_cost_n200|%s|cv_n20000" % case, f4(v["size_with_cv_n20000"]["rate"]), wil(v["size_with_cv_n20000"]),
                        FILES["B9.4"], "cases/%s/approximation_cost/200/size_with_cv_n20000/rate" % case))
            out.append(("approx_cost_n200|%s|cv_at_n" % case, f4(v["size_with_cv_at_n"]["rate"]), wil(v["size_with_cv_at_n"]),
                        FILES["B9.4"], "cases/%s/approximation_cost/200/size_with_cv_at_n/rate" % case))
    if have("B9.5"):
        b95 = J(FILES["B9.5"])
        for k, v in b95["cells"].items():
            out.append(("awb|%s" % k, f4(v["awb"]["rate"]), wil(v["awb"]), FILES["B9.5"], "cells/%s/awb/rate" % k))
        out.append(("recommend_awb", "sí" if b95["rule"]["recommend_awb"] else "no", "—", FILES["B9.5"], "rule/recommend_awb"))
    if have("B9.6"):
        b96 = J(FILES["B9.6"])
        for t in ("final", "final_awb"):
            if t in b96["summary"]:
                v = b96["summary"][t]
                out.append(("app_fp_mean|%s" % t, f4(v["fp_mean"]), "máx. %s" % f4(v["fp_max"]), FILES["B9.6"], "summary/%s/fp_mean" % t))
                out.append(("app_detections|%s" % t, "%d de %d" % (v["detections"], v["event_cells"]),
                            "latencia media %s" % ("%.1f" % v["mean_latency_detected"] if v["mean_latency_detected"] else "—"),
                            FILES["B9.6"], "summary/%s/detections" % t))
    if have("B9.7"):
        b97 = J(FILES["B9.7"])
        for case in ("dm", "ct"):
            for n in b97["config"]["n"]:
                v = b97["table"]["%s|%g|%d" % (case, b97["primary_theta"], n)]
                out.append(("cv5|%s|n%d" % (case, n), f4(v["cv"]["0.05"]), "EE %s" % f4(v["se"]["0.05"]), FILES["B9.7"],
                            "table/%s|%g|%d/cv/0.05" % (case, b97["primary_theta"], n)))
    if have("FIG"):
        for k, v in J(FILES["FIG"])["figures"].items():
            out.append(("figure|%s" % k, "`%s`" % v["sha256"], "copia %s" % v["paper_copy"], FILES["FIG"], "figures/%s/sha256" % k))
    return out


def main():
    L = []
    w = L.append
    b90 = J(FILES["B9.0"])
    w("# Auditoría A9 — configuración final del estadístico primario")
    w("")
    w("Generado por `experiments/audit9_generate_report.py` el %s (UTC) desde los JSON de `experiments/results/`; commit `%s`." % (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"), C.git("rev-parse", "--short", "HEAD").strip()))
    w("")
    w("Protocolo: `%s`, sha256 `%s`, commit `%s` (registrado antes de cualquier cómputo)." % (
        b90["protocol"]["path"], b90["protocol"]["sha256_disk"], b90["protocol"]["commit_added"][:7]))
    w("")
    if have("B9.2"):
        w("Primaria final: **%s**." % J(FILES["B9.2"])["primary_final"])
        w("")
    w("## 1. Resultados")
    w("")
    sec_b90(w, L)
    for blk, fn in (("B9.1", sec_b91), ("B9.2", sec_b92), ("B9.3", sec_b93), ("B9.4", sec_b94)):
        if have(blk):
            fn(w, L)
    if os.path.exists(os.path.join(C.RESULTS, "b95_budget_audit9.json")):
        sec_b95(w, L)
    if have("B9.2"):
        sec_b96(w, L)
    sec_b97(w, L)
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
    if have("B9.1") and have("B9.2") and have("B9.3"):
        conclusions(w)
    else:
        w("Pendientes: faltan bloques (§5).")
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
    L.extend(table(["Frase", "Archivo:línea", "Cita", "Estado"],
                   [[c["label"], "`%s:%d`" % (c["file"], c["line"]), c["quote"], claim_status(c)] for c in manuscript_claims()]))
    w("")
    w("## Anexo: hechos para el manuscrito")
    w("")
    w("`clave | valor | IC o EE | archivo JSON | ruta dentro del JSON`")
    w("")
    if have("B9.1") and have("B9.2"):
        for f in facts(J(FILES["B9.1"]), J(FILES["B9.2"])):
            w("- " + " | ".join(str(x) for x in f))
    w("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    C.register_outputs(__file__, [OUT], C.provenance(__file__))
    print("escrito %s (%d lineas)" % (OUT, len(L)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
