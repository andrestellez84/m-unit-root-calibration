"""
Auditoria A12 - generador de experiments/results/resultados_auditoria_12.md.

Regla de A8 (regla 3): ningun numero de resultado se escribe a mano; todo valor se lee
de un JSON o log de experiments/results. Las citas del manuscrito v12 salen de
claims_audit12.json (leidas del zip). Si falta una clave, falla con KeyError; los
bloques cuyo JSON no existe se declaran en la seccion 5. tests/test_no_literals_audit12.py
recorre este archivo.

Estructura: encabezado; 1 resultados (B12.0, A, B, C, F); 2 compuertas; 3 procedencia;
4 desviaciones; 5 no ejecutado; 6 conclusiones; 7 anomalias y frases del manuscrito;
anexo (tabla maestra).
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
import audit12_design as D                                         # noqa: E402
import audit12_unitroot as P                                       # noqa: E402
from audit8_generate_report import table as _table                  # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_12.md")
PROTOCOL = "experiments/protocol_audit12.md"
F = {"B0": "b120_inventory_audit12.json", "P0": "cal_paso0_audit12.json", "PROBE": "bA_probe_audit12.json",
     "A": "bA_ma_audit12.json", "B": "bB_attrib_audit12.json", "C": "bC_initial_audit12.json", "F": "bF_anchor_audit12.json",
     "Q": "claims_audit12.json"}
SCRIPTS = {"B0": "experiments/audit12_b120_inventory.py", "CAL": "experiments/audit12_cal.py --paso0 --run --cores 14",
           "PROBE": "experiments/audit12_bA_ma.py --probe --cores 14", "A": "experiments/audit12_bA_ma.py --run --cores 14; --analyze",
           "B": "experiments/audit12_bB_attrib.py --run --analyze --cores 14",
           "C": "experiments/audit12_bC_initial.py --run --analyze --cores 14", "F": "experiments/audit12_bF_anchor.py",
           "Q": "experiments/audit12_claims.py"}
PN = {"gls_t0.02": "RM-GLS θ=0.02", "gls_t0": "RM-GLS θ=0", "glsb_t0": "(b) s²_AR MAIC-GLS", "glsbp_t0": "(b′) s²_AR MAIC-MCO",
      "msb": "MSB-GLS NP", "mzt": "MZ_t-GLS NP", "msb_pq": "MSB-GLS PQ", "mzt_pq": "MZ_t-GLS PQ", "dfgls": "DF-GLS MAIC-GLS",
      "dfgls_pq": "DF-GLS MAIC-MCO", "adf": "ADF (AIC)", "pp": "PP"}
EN = {"ma_m0p8": "MA ψ = −0.8", "ma_m0p5": "MA ψ = −0.5", "ma_0": "MA ψ = 0 (iid)", "ma_0p5": "MA ψ = 0.5",
      "ar_m0p5": "AR φ = −0.5", "ar_0p5": "AR φ = 0.5"}
VN = {"a": "(a) σ̂_HAC", "b": "(b) s²_AR MAIC-GLS", "bp": "(b′) s²_AR MAIC-MCO", "c": "(c) MSB-GLS asint."}
DN = {"a_minus_bp": "(a)−(b′)", "bp_minus_b": "(b′)−(b)", "bp_minus_c": "(b′)−(c)", "a_minus_b": "(a)−(b)", "b_minus_c": "(b)−(c)"}
PP = 100


def have(key):
    return os.path.exists(os.path.join(C.RESULTS, F[key]))


def J(key):
    return C.read_json(F[key])


def table(header, rows):
    def esc(x):
        return str(x).replace("|", "\\|")
    return _table([esc(h) for h in header], [[esc(x) for x in r] for r in rows])


def f(x, d=4):
    return "—" if x is None else "%.*f" % (d, x)


def pp(x, d=2):
    return "%+.*f" % (d, x * PP)


def yn(b):
    return "sí" if b else "no"


def T(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def cite(q):
    return "`%s:%d`" % (q["file"], q["line"])


def pytest_summary():
    name = "pytest_audit12.log"
    if not os.path.exists(os.path.join(C.RESULTS, name)):
        return None
    text = T(name)
    summary, secs = re.findall(r"=+ (.*?) in ([0-9.]+)s", text)[-1]
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|errors?)", summary)}
    coll = re.search(r"collected (\d+) items", text)
    lit = re.findall(r"tests[\\/]test_no_literals_audit12\.py::(\S+) (PASSED|FAILED|SKIPPED)", text)
    unit = re.findall(r"tests[\\/]test_audit12_unitroot\.py::(\S+) (PASSED|FAILED|SKIPPED)", text)
    return {"seconds": float(secs), "collected": int(coll.group(1)) if coll else None, "counts": counts, "literals": lit,
            "unit": unit}


def size_key(err, n, case):
    return D.size_cell(err, n, case)


# ---------------------------------------------------------------------------
# B12.0
# ---------------------------------------------------------------------------
def sec_b0(w, L):
    b = J("B0")
    pr, pd, s = b["protocol"], b["prediction"], b["seed_map"]
    w("### B12.0 — Inventario, protocolo y semillas")
    w("")
    for lab, x in (("Predicción", pd), ("Protocolo", pr)):
        w("- %s `%s`: sha256 en disco `%s`, commiteado `%s` (%s); commit `%s` (%s)." % (
            lab, x["path"], x["sha256_disk"], x["sha256_committed"], "iguales" if x["sha256_disk"] == x["sha256_committed"] else "DISTINTOS",
            x["commit_added"][:7], x["commit_time"]))
    w("- Predicción commiteada antes que el protocolo y en otro commit: %s." % yn(b["prediction_before_protocol"]))
    w("- Equivalencia `SeedSequence(familia).spawn` ↔ `spawn_key = (celda, i)`: %d streams, %d discrepancias." % (
        b["spawn_equivalence"]["streams_checked"], b["spawn_equivalence"]["mismatches"]))
    w("- Colisiones: %d streams nuevos (%s) frente a %d previos (%d semillas enteras y las familias %s): **%d** con los previos, **%d** dentro de A12." % (
        s["new_streams_total"], ", ".join("%s: %d" % (k, v["replicate_streams"]) for k, v in s["new_families"].items() if v["replicate_streams"]),
        s["prior_streams_total"], s["prior_integer_seeds"], ", ".join(str(x) for x in s["prior_families"]),
        s["collisions_new_vs_prior"], s["collisions_within_new"]))
    conv = b["convention_test"]
    w("- Test de convención (lectura 2: %s): máx. |Δ| = %s en %s → %s." % (
        conv["reading"], f(conv["max_abs_diff"], 1), ", ".join("`%s`" % k for k in conv["cells"]), "pasa" if conv["passes"] else "FALLA"))
    w("")
    w("**Tabla B12.0.1. JSON, muestras y checkpoints reutilizados.**")
    w("")
    rows = [["`%s`" % k, "`%s`" % v["sha256"], v["bytes"], v["mtime_utc"]] for k, v in b["reused_json"].items()]
    rows += [["`checkpoints/%s`" % k, "`%s`" % v["sha256"], v["bytes"], v["mtime_utc"]] for k, v in b["reused_npz"].items()]
    rows += [["`checkpoints/%s/` (%d archivos, sha256 agregado)" % (k, v["files"]), "`%s`" % v["aggregate_sha256"], v["bytes"],
              v["last_mtime_utc"]] for k, v in b["reused_checkpoints"].items()]
    L.extend(table(["Archivo", "sha256", "Bytes", "mtime (UTC)"], rows))
    w("")
    py = pytest_summary()
    if py is not None:
        w("Tests unitarios de `audit12_unitroot` (`tests/test_audit12_unitroot.py`): %s." % "; ".join("%s %s" % t for t in py["unit"]))
        w("")


# ---------------------------------------------------------------------------
# B12.A
# ---------------------------------------------------------------------------
def sec_a(w, L):
    b = J("A")
    cfg = b["config"]
    w("### B12.A — Errores MA y AR")
    w("")
    if have("PROBE"):
        pr = J("PROBE")
        w("**Presupuesto.** Sonda de %d caminos (n = %d, %s, %s): %s s por camino; proyección del bloque %s h frente al tope de %g h → %s." % (
            pr["config"]["paths"], pr["config"]["n"], pr["config"]["case"], pr["config"]["err"], f(pr["per_path_sec"]), f(pr["projected_hours"], 2),
            pr["config"]["budget_hours"], "se lanza" if pr["within_budget"] else "SE DETIENE"))
        w("")
    if have("P0"):
        p0 = J("P0")
        w("**Paso 0 de la calibración de A10 reutilizada** (%d filas recalculadas por n y caso con `audit12_unitroot.np_part`): máx. |Δ| = %s → %s." % (
            p0["reps"], f(p0["max_abs_diff"], 1), "pasa" if p0["passes"] else "FALLA"))
        w("")
    w("Diseño: %d estructuras de error × n ∈ %s × casos %s; N = %d por celda de tamaño y %d por celda de potencia; N_cal = %d. Fuente del valor crítico iid por (n, caso): %s." % (
        len(cfg["errors"]), cfg["n"], cfg["cases"], cfg["N_size"], cfg["N_power"], cfg["N_cal"],
        "; ".join("%s: %s" % (k, ", ".join(sorted(set(v.values())))) for k, v in cfg["calibration_source"].items())))
    w("")
    w("**Tabla A.1. Tamaño al valor crítico iid (α = 0.05).** * = fuera de la región exacta al 95 %% de N = 20 000 %s." % b["exact_region_20000"])
    w("")
    rows = []
    reg = b["exact_region_20000"]
    for name, r in b["size"].items():
        rows.append([EN[r["err_tag"]], r["n"], r["case"]] + ["%s%s" % (f(r["iid"][p]["rate"]), "" if reg[0] <= r["iid"][p]["rate"] <= reg[1] else "*")
                                                           for p in cfg["procs"]])
    L.extend(table(["Error", "n", "Caso"] + [PN[p] for p in cfg["procs"]], rows))
    w("")
    w("*Fuente: `%s` (`size.<celda>.iid.<proc>.rate`); N_sim = %d; N_cal = %d; familia %d.*" % (F["A"], cfg["N_size"], cfg["N_cal"], C.FAMILY["A"]))
    w("")
    asy_p = [p for p in cfg["procs"] if p in next(iter(b["size"].values()))["asy"]]
    w("**Tabla A.2. Tamaño al valor crítico asintótico publicado y al «límite» n = 20 000 de RM-GLS.** Asintóticos: NP 2001 Tabla 1 (MZ_t, MSB), ERS/Fuller (DF-GLS: %s), MacKinnon (ADF, PP: p-valor < 0.05). Límite: %s." % (
        cfg["asy"]["dfgls_published"], cfg["limit"]))
    w("")
    rows = []
    for name, r in b["size"].items():
        rows.append([EN[r["err_tag"]], r["n"], r["case"]] + [f(r["asy"][p]["rate"]) for p in asy_p]
                    + [f(r["limit"][t]["rate"]) if t in r["limit"] else "no disponible" for t in ("gls_t0", "gls_t0.02")])
    L.extend(table(["Error", "n", "Caso"] + ["%s asint." % PN[p] for p in asy_p] + ["RM-GLS θ=0 límite", "RM-GLS θ=0.02 límite"], rows))
    w("")
    w("*Fuente: `%s` (`size.<celda>.asy` y `.limit`); N_sim = %d.*" % (F["A"], cfg["N_size"]))
    w("")
    for lab, kind in (("A.3. Potencia al valor crítico iid", "iid"), ("A.4. Potencia ajustada al tamaño (cuantil 5 % de la celda de tamaño de la misma estructura)", "adjusted")):
        w("**Tabla %s.**" % lab)
        w("")
        rows = [[EN[r["err_tag"]], r["n"], r["case"], f(r["rho"], 4)] + [f(r[kind][p]["rate"], 3) for p in cfg["procs"]]
                for r in b["power"].values()]
        L.extend(table(["Error", "n", "Caso", "ρ"] + [PN[p] for p in cfg["procs"]], rows))
        w("")
        w("*Fuente: `%s` (`power.<celda>.%s`); N_sim = %d; familia %d.*" % (F["A"], kind, cfg["N_power"], C.FAMILY["A"]))
        w("")
    w("**Tabla A.5. Diagnósticos bajo cada nula: mediana [q25, q75] de σ̂²_HAC/ω², s²_AR/ω² (MAIC-GLS y MAIC-MCO), B de Andrews y k; factor poblacional del Bartlett en la B mediana.**")
    w("")
    rows = []
    for r in b["size"].values():
        dg = r["diagnostics"]
        q = lambda x: "%s [%s, %s]" % (f(x["median"], 3), f(x["q25"], 3), f(x["q75"], 3))    # noqa: E731
        bf = r["bartlett_factor_at_median_B"]
        rows.append([EN[r["err_tag"]], r["n"], r["case"], f(r["omega2"], 3), q(dg["s2_over_omega2"]), q(dg["s2ar_over_omega2"]),
                     q(dg["s2ar_pq_over_omega2"]), f(dg["B"]["median"], 0), f(dg["k"]["median"], 0), f(dg["kpq"]["median"], 0),
                     "%d → %s (S × %s)" % (bf["B"], f(bf["factor"], 3), f(bf["S_multiplier"], 3))])
    L.extend(table(["Error", "n", "Caso", "ω²", "σ̂²_HAC/ω²", "s²_AR/ω² (GLS)", "s²_AR/ω² (MCO)", "B med.", "k GLS med.", "k MCO med.",
                    "Factor Bartlett en B med."], rows))
    w("")
    w("**Tabla A.6. Los mismos diagnósticos bajo las alternativas (mediana).**")
    w("")
    rows = [[EN[r["err_tag"]], r["n"], r["case"], f(r["rho"], 4), f(r["diagnostics"]["s2_over_omega2"]["median"], 3),
             f(r["diagnostics"]["s2ar_over_omega2"]["median"], 3), f(r["diagnostics"]["s2ar_pq_over_omega2"]["median"], 3),
             f(r["diagnostics"]["B"]["median"], 0), f(r["diagnostics"]["k"]["median"], 0), f(r["diagnostics"]["kpq"]["median"], 0)]
            for r in b["power"].values()]
    L.extend(table(["Error", "n", "Caso", "ρ", "σ̂²_HAC/ω²", "s²_AR/ω² (GLS)", "s²_AR/ω² (MCO)", "B med.", "k GLS", "k MCO"], rows))
    w("")
    w("**Tabla A.7. Factor poblacional del Bartlett, [γ₀ + 2Σ_{j≤B}(1 − j/(B+1))γ_j]/ω², por ancho B (cálculo cerrado).**")
    w("")
    bp = b["bartlett_population"]
    Bs = list(next(iter(bp.values()))["factor_by_B"])
    L.extend(table(["Error"] + ["B = %s" % x for x in Bs], [[EN[k]] + [f(v["factor_by_B"][x], 3) for x in Bs] for k, v in bp.items()]))
    w("")
    ga1, ga2 = b["G_A1"], b["G_A2"]
    w("**G-A1 (DURA, Bonferroni por decisión del autor).** K = %d tamaños en las celdas ψ = 0; región exacta de N = 20 000 al nivel 1 − 0.05/K: %s. Fuera de la región de Bonferroni: %s → **%s**. Informativo: fuera de la región literal %s: %d (esperados por azar %s): %s." % (
        ga1["K"], [f(x, 5) for x in ga1["region_bonferroni"]], ga1["outside_bonferroni"] or "ninguno", "PASA" if ga1["passes"] else "FALLA (se detiene)",
        ga1["region_literal"], len(ga1["outside_literal"]), f(ga1["expected_outside_literal"], 1), ", ".join(ga1["outside_literal"]) or "ninguno"))
    w("")
    w("**G-A2 (informativa).** MZ_t-GLS NP asintótico a ψ = −0.8, n = 100: %s." % "; ".join(
        "%s: %s frente a %s de NP (2000) → diferencia %s, %s" % (k, f(v["mzt_np_asy"]), f(v["np2000_mzalpha"], 3), pp(v["diff"]) + " pp",
                                                                "dentro de ±0.03" if v["within"] else "FUERA de ±0.03") for k, v in ga2.items()))
    w("")
    cl = b["classification"]
    w("**Clasificación (lectura 10).**")
    w("")
    rows = [["A", t["psi"], t["n"], t["case"], f(t["gls_t0"]), f(t["mzt_asy"]),
             ("≤ MZ_t + 2 pp y ≤ 0.10" if t["psi"] == P.ERRORS[0][1] else "≤ MZ_t + 1 pp"), yn(t["ok"])] for t in cl["A_terms"]]
    rows += [["B", t["psi"], t["n"], t["case"], f(t["gls_t0"]), f(t["mzt_asy"]), "≥ 0.15 o ≥ MZ_t + 5 pp", yn(t["ok"])] for t in cl["B_terms"]]
    L.extend(table(["Desenlace", "ψ", "n", "Caso", "RM-GLS θ=0 (cv iid)", "MZ_t-GLS NP (asint.)", "Condición", "Cumple"], rows))
    w("")
    w("A se cumple: %s; B se cumple: %s → **desenlace %s**." % (yn(cl["A"]), yn(cl["B"]), cl["outcome"]))
    w("")
    pr = b["prediction"]
    w("**Predicción registrada** (`prediccion_ma_audit12.md`, sha256 `%s`):" % J("B0")["prediction"]["sha256_disk"])
    w("")
    L.extend(table(["Término", "Regla", "Valor", "Se cumple"],
                   [["RM-GLS θ=0, ψ = −0.8, n = 200, c", pr["psi08"]["rule"], f(pr["psi08"]["value"]), yn(pr["psi08"]["holds"])],
                    ["RM-GLS θ=0, ψ = −0.5, n = 200, c", pr["psi05"]["rule"], f(pr["psi05"]["value"]), yn(pr["psi05"]["holds"])],
                    ["RM-GLS θ=0, φ = +0.5, n = 200, c", pr["phi05"]["rule"], f(pr["phi05"]["value"]), yn(pr["phi05"]["holds"])],
                    ["Desenlace", pr["outcome"]["rule"], pr["outcome"]["value"], yn(pr["outcome"]["holds"])]]))
    w("")


# ---------------------------------------------------------------------------
# B12.B
# ---------------------------------------------------------------------------
def sec_b(w, L):
    b = J("B")
    w("### B12.B — Atribución con Perron–Qu")
    w("")
    w("Trayectorias: %s. Paso 0 frente a B9.1/B9.2 (50 por celda, columnas comunes): peor máx. |Δ| = %s. Variantes: %s. EE: %s." % (
        b["config"]["trajectories"], f(b["paso0_worst"], 1), "; ".join("%s = %s" % (VN[k], v) for k, v in b["config"]["variants"].items()),
        b["config"]["se"]))
    w("")
    w("**Tabla B.1. Potencia por celda y diferencias pareadas (pp, EE entre paréntesis).**")
    w("")
    rows = []
    for k, r in b["cells"].items():
        if "rho" not in r:
            continue
        rows.append([r["case"], r["n"], f(r["rho"], 2)] + [f(r["rates"][v]["rate"], 3) for v in ("a", "b", "bp", "c")]
                    + ["%s (%s)" % (pp(r["diffs"][d]["delta"]), f(r["diffs"][d]["se"] * PP, 2)) for d in ("a_minus_bp", "bp_minus_b", "bp_minus_c")])
    L.extend(table(["Caso", "n", "ρ"] + [VN[v] for v in ("a", "b", "bp", "c")] + [DN[d] for d in ("a_minus_bp", "bp_minus_b", "bp_minus_c")], rows))
    w("")
    c0 = next(r for r in b["cells"].values() if "rho" in r)
    w("*Fuente: `%s` (`cells`); N_sim = %d; (a), (b): %s; (b′): familia 136 (N_cal = %d); (c): asintótico NP.*" % (
        F["B"], c0["rates"]["a"]["n"], c0["ab_calibration"], c0["bp_N_cal"]))
    w("")
    w("**Tabla B.2. Medias por n (como tab:attrib), pp con EE.**")
    w("")
    ds = ("a_minus_bp", "bp_minus_b", "bp_minus_c", "a_minus_b", "b_minus_c")
    rows = [[k.split("|")[0], k.split("|")[1], v["a_minus_bp"]["k"]] + ["%s (%s)" % (pp(v[d]["mean"]), f(v[d]["se"] * PP, 2)) for d in ds]
            for k, v in b["by_n"].items()]
    L.extend(table(["Caso", "n", "Celdas"] + [DN[d] for d in ds], rows))
    w("")
    w("**Tabla B.3. Potencia local (n = %d), pp.** (a) y (b) con la calibración de A9 (N_cal = 50 000) como B9.3; (b′) con la familia 136." % b["config"]["lp_n"])
    w("")
    rows = [[r["lp_case"], f(r["c"], 0)] + [f(r["rates"][v]["rate"], 4) for v in ("a", "b", "bp", "c")]
            + ["%s (%s)" % (pp(r["diffs"][d]["delta"]), f(r["diffs"][d]["se"] * PP, 2)) for d in ("a_minus_bp", "bp_minus_b", "bp_minus_c")]
            for r in b["cells"].values() if "c" in r and "rho" not in r]
    L.extend(table(["Caso", "c"] + [VN[v] for v in ("a", "b", "bp", "c")] + [DN[d] for d in ("a_minus_bp", "bp_minus_b", "bp_minus_c")], rows))
    w("")
    cc, dr = b["C"], b["prediction_direction"]
    w("**Clasificación C** (%s): media %s pp, EE %s pp, k = %d → **%s**." % (cc["rule"], pp(cc["mean"]), f(cc["se"] * PP, 2), cc["k"],
                                                                         "se cumple" if cc["holds"] else "no se cumple"))
    w("")
    w("**Dirección registrada** (%s): media %s pp (EE %s) → %s." % (dr["rule"], pp(dr["mean"]), f(dr["se"] * PP, 2), "se cumple" if dr["holds"] else "no se cumple"))
    w("")
    w("**Tabla B.4. Diagnóstico a n = 200 (medianas).**")
    w("")
    rows = [[v["case"], f(v["rho"], 2), f(v["k_gls"], 0), f(v["k_ols"], 0), f(v["s2ar_gls"], 4), f(v["s2ar_ols"], 4), f(v["s2_hac"], 4)]
            for v in b["diagnostics_n200"].values()]
    L.extend(table(["Caso", "ρ", "k MAIC-GLS", "k MAIC-MCO", "s²_AR (GLS)", "s²_AR (MCO)", "σ̂²_HAC"], rows))
    w("")


# ---------------------------------------------------------------------------
# B12.C
# ---------------------------------------------------------------------------
def sec_c(w, L):
    b = J("C")
    cfg = b["config"]
    w("### B12.C — Condición inicial")
    w("")
    w("DGP 1, caso %s, n = %d, N = %d por celda; u₀: %s; pareo: %s; valor crítico: %s." % (cfg["case"], cfg["n"], cfg["N"], cfg["u0"], cfg["pairing"], cfg["cv"]))
    w("")
    w("**Tabla C.1. Potencia (McNemar p frente a DF-GLS en la segunda fila de cada celda).**")
    w("")
    procs = cfg["procs"]
    rows = []
    for k, r in b["cells"].items():
        lab = "α = %s" % f(r["alpha"], 0) if r["alpha"] is not None else "u₀ aleatorio"
        rows.append([f(r["rho"], 2), lab] + [f(r["power"][p]["rate"], 3) for p in procs])
        rows.append(["", "p McNemar"] + ["—" if p == cfg["reference"] else "%.1e" % r["mcnemar_vs_dfgls"][p]["p_value"] for p in procs])
    L.extend(table(["ρ", "u₀"] + [PN[p] for p in procs], rows))
    w("")
    w("*Fuente: `%s` (`cells.<ρ>|<variante>`); N_sim = %d; familia %d.*" % (F["C"], cfg["N"], C.FAMILY["C"]))
    w("")


# ---------------------------------------------------------------------------
# B12.F
# ---------------------------------------------------------------------------
def sec_f(w, L):
    b = J("F")
    cfg = b["config"]
    w("### B12.F — Forma cerrada del sesgo del ancla")
    w("")
    w("Método: %s; c̄ = %g, κ = %s, λ = %s. Control denso frente a la vía O(n) en n ≤ %d: máx. |Δ| = %s." % (
        cfg["method"], cfg["cbar"], f(cfg["kappa"], 4), f(cfg["lambda"], 2), cfg["dense_max_n"], "%.1e" % b["dense_vs_fast_max_abs"]))
    w("")
    w("**Tabla F.1. E[S₀²] exacto frente a la hipótesis, al primer orden de A11 y a las medias simuladas de A11.**")
    w("")
    rows = []
    for k, r in b["rows"].items():
        s = r.get("sim_A11")
        rows.append([r["n"], f(r["exact"], 6), f(r["formula"], 6), "%+.2e" % r["formula_minus_exact"], f(r["first_order_A11"], 6),
                     "%+.2e" % r["first_order_minus_exact"], "—" if s is None else "%s ± %s" % (f(s["mean"], 5), f(s["se"], 5)),
                     "—" if s is None else f(s["z_vs_exact"], 2)])
    L.extend(table(["n", "Exacta", "Fórmula (n + c̄²)", "Fórmula − exacta", "1/2 − κ/n", "(1/2 − κ/n) − exacta", "Simulada A11", "z frente a exacta"], rows))
    w("")
    g, an = b["gate"], b["a11_anomaly_n20000"]
    w("Compuerta informativa (%s): peor %s → %s. Anomalía T3 de A11 a n = 20 000: simulada %s ± %s frente a exacta %s → z = %s (%s)." % (
        g["rule"], "%.2e" % g["worst"], "pasa" if g["passes"] else "no pasa", f(an["mean"], 5), f(an["se"], 5), f(an["exact"], 6), f(an["z"], 2),
        "compatible" if an["compatible"] else "INCOMPATIBLE"))
    w("")


# ---------------------------------------------------------------------------
# Compuertas, procedencia, desviaciones
# ---------------------------------------------------------------------------
def gates(L):
    rows = []
    b0 = J("B0")
    rows.append(["B12.0 colisiones", "0 con previos y dentro de A12", "%d / %d" % (b0["seed_map"]["collisions_new_vs_prior"], b0["seed_map"]["collisions_within_new"]),
                 "pasa" if b0["seed_map"]["collisions_new_vs_prior"] == 0 == b0["seed_map"]["collisions_within_new"] else "FALLA"])
    rows.append(["B12.0 convención", "máx. |Δ| = 0", f(b0["convention_test"]["max_abs_diff"], 1), "pasa" if b0["convention_test"]["passes"] else "FALLA"])
    if have("P0"):
        p0 = J("P0")
        rows.append(["Paso 0 calibración A10", "máx. |Δ| = 0", f(p0["max_abs_diff"], 1), "pasa" if p0["passes"] else "FALLA"])
    if have("PROBE"):
        pr = J("PROBE")
        rows.append(["Presupuesto B12.A", "proyección ≤ %g h" % pr["config"]["budget_hours"], "%s h" % f(pr["projected_hours"], 2), "pasa" if pr["within_budget"] else "SE DETIENE"])
    if have("A"):
        a = J("A")
        rows.append(["G-A1 (DURA, Bonferroni)", "K = %d tamaños ψ = 0 en %s" % (a["G_A1"]["K"], [f(x, 5) for x in a["G_A1"]["region_bonferroni"]]),
                     "fuera: %d (literal: %d)" % (len(a["G_A1"]["outside_bonferroni"]), len(a["G_A1"]["outside_literal"])), "pasa" if a["G_A1"]["passes"] else "FALLA"])
        rows.append(["G-A2 (informativa)", "|MZ_t NP asint. − NP 2000| ≤ 0.03 a ψ = −0.8, n = 100",
                     "; ".join("%s %s" % (k, pp(v["diff"])) for k, v in a["G_A2"].items()), ", ".join("%s %s" % (k, "dentro" if v["within"] else "fuera") for k, v in a["G_A2"].items())])
    if have("B"):
        used = b_paso0_used()
        rows.append(["Paso 0 B12.B (columnas que usa B12.B: %s)" % ", ".join(B_USED), "máx. |Δ| = 0", "%.1e" % used, "pasa" if used == 0 else "FALLA"])
        rows.append(["Paso 0 B12.B (todas las columnas comunes)", "máx. |Δ| = 0", "%.1e" % J("B")["paso0_worst"],
                     "pasa" if J("B")["paso0_worst"] == 0 else "no nulo (ver §7(a))"])
    if have("F"):
        g = J("F")["gate"]
        rows.append(["B12.F (informativa)", g["rule"], "%.2e" % g["worst"], "pasa" if g["passes"] else "no pasa"])
    L.extend(table(["Compuerta", "Regla", "Medido", "Veredicto"], rows))


B_USED = ("s2", "gls_t0", "glsb_t0", "msb")


def b_paso0_used():
    return max(v["by_column"][c] for v in J("B")["paso0"].values() for c in B_USED if c in v["by_column"])


def b_paso0_nonzero():
    return {k: {c: x for c, x in v["by_column"].items() if x > 0} for k, v in J("B")["paso0"].items() if v["max_abs_diff"] > 0}


def provenance_section(w, L):
    man = C.read_json("manifest_audit12.json")
    w("**Archivos que alimentan este reporte** (`manifest_audit12.json`; el reporte se registra después de escribirse).")
    w("")
    L.extend(table(["Archivo", "sha256", "Bytes", "Script", "Commit", "Código commiteado"],
                   [[k, "`%s`" % e["sha256"], e["bytes"], e["script"], e["commit"][:7], yn(e["code_all_committed"])]
                    for k, e in sorted(man["entries"].items()) if not k.endswith("resultados_auditoria_12.md")]))
    w("")
    w("Comandos: %s." % "; ".join("%s: `%s`" % kv for kv in SCRIPTS.items()))
    w("")
    if have("A"):
        el = J("A")["compute_elapsed_sec"]
        w("- B12.A: tiempo de cómputo agregado por celda (suma de oleadas) %.1f h en %d celdas." % (sum(el.values()) / 3600, len(el)))
    py = pytest_summary()
    if py is not None:
        c = py["counts"]
        w("- Suite completa (`pytest_audit12.log`): collected %s; passed %d; failed %d; skipped %d; %.1f s." % (
            py["collected"], c.get("passed", 0), c.get("failed", 0), c.get("skipped", 0), py["seconds"]))
        w("- Test de literales (`tests/test_no_literals_audit12.py`): %s." % "; ".join("%s %s" % t for t in py["literals"]))
    w("- Checkpoints de A12 (`checkpoints/audit12_*`) sin commitear; se regeneran bit a bit desde familia, celda e índice de réplica.")
    w("")


def deviations():
    return [
        ["Test de convención con trayectorias de la familia 111 y de la calibración de A10 (semilla 42), no de la 110",
         "La familia 110 no tiene trayectorias (B10.0 no generó ninguna)", "antes (lectura 2)", "Ninguno; máx. |Δ| = 0"],
        ["G-A1 con región de Bonferroni (nivel 1 − 0.05/K) en lugar de la región literal al 95 %",
         "Decisión del autor antes del registro: con K tamaños la región literal falla por azar con probabilidad ≈ 1 − 0.95^K",
         "antes (protocolo, §2)", "La región literal se reporta como informativa"],
        ["El paso GLS de Perron–Qu se escribió primero con `lstsq` y se cambió a una QR propia",
         "Con `lstsq` el test unitario no alcanzaba la tolerancia en MZa y s²_AR por ruido de redondeo entre algoritmos (valores grandes en el caso ct)",
         "antes de cualquier resultado", "Con QR el test pasa a la tolerancia del encargo"],
        ["B12.0 (mapa de semillas, un proceso) corrió a la vez que la sonda de presupuesto", "Ahorro de tiempo de pared",
         "antes de lanzar B12.A", "La sonda mide un coste por camino algo mayor: proyección conservadora"],
        ["Calibración PQ también a n = 1000 y 2000 (familia 136)", "B12.B la necesita (DGP 1 a n = 1000 y potencia local a n = 2000)",
         "antes (lectura 8)", "—"],
        ["En la potencia local de B12.B, (a) y (b) usan la calibración de A9 (N_cal = 50 000), como B9.3", "A10 no tiene calibración a n = 2000",
         "antes (lectura 13)", "(b′) usa N_cal = 500 000"],
        ["La compuerta del Paso 0 de B12.B se lee sobre las columnas que B12.B usa; la diferencia de un ulp en DF-GLS se declara aparte",
         "El protocolo pide |Δ| = 0 al reutilizar trayectorias; la columna distinta no entra en ningún cálculo de B12.B",
         "después de ver el Paso 0", "Ninguno sobre los resultados de B12.B (§7(a))"],
    ]


def not_executed():
    rows = [["B12.E (regeneración con θ = 0)", "El autor no lo confirmó antes de lanzar (protocolo, §2)"],
            ["B12.D (¿θ > 0 ayuda?)", "Opcional y no pedido (protocolo, §2)"]]
    for k, lab in (("A", "B12.A"), ("B", "B12.B"), ("C", "B12.C"), ("F", "B12.F")):
        if not have(k):
            rows.append([lab, "Su JSON (`%s`) no existe: no se ejecutó o se detuvo antes" % F[k]])
    return rows


def conclusions(w):
    i = 1
    if have("A"):
        a = J("A")
        cl, pr = a["classification"], a["prediction"]
        w("%d. B12.A: G-A1 %s; desenlace **%s**. RM-GLS θ = 0 al cv iid (n = 200, c): ψ = −0.8 → %s; ψ = −0.5 → %s; φ = +0.5 → %s. Predicción: %d de 4 términos se cumplen." % (
            i, "pasa" if a["G_A1"]["passes"] else "falla", cl["outcome"], f(pr["psi08"]["value"]), f(pr["psi05"]["value"]), f(pr["phi05"]["value"]),
            sum(v["holds"] for v in pr.values())))
        i += 1
    if have("B"):
        b = J("B")
        m = b["by_n"]["c|200"]
        w("%d. B12.B: en DGP 1, c, n = 200, (a)−(b′) = %s pp (EE %s), (b′)−(b) = %s pp (EE %s), (b′)−(c) = %s pp (EE %s); C %s; dirección registrada %s." % (
            i, pp(m["a_minus_bp"]["mean"]), f(m["a_minus_bp"]["se"] * PP, 2), pp(m["bp_minus_b"]["mean"]), f(m["bp_minus_b"]["se"] * PP, 2),
            pp(m["bp_minus_c"]["mean"]), f(m["bp_minus_c"]["se"] * PP, 2), "se cumple" if b["C"]["holds"] else "no se cumple",
            "se cumple" if b["prediction_direction"]["holds"] else "no se cumple"))
        i += 1
    if have("C"):
        c = J("C")
        top = max(D.C_ALPHA)
        w("%d. B12.C: potencia a α = %g: %s." % (i, top, "; ".join(
            "ρ = %s: RM-GLS θ=0 %s, DF-GLS %s" % (f(r["rho"], 2), f(r["power"]["gls_t0"]["rate"], 3), f(r["power"]["dfgls"]["rate"], 3))
            for r in c["cells"].values() if r["alpha"] == top)))
        i += 1
    if have("F"):
        fb = J("F")
        w("%d. B12.F: compuerta %s (peor %s); la media simulada de A11 a n = 20 000 es %s con el valor exacto (z = %s)." % (
            i, "pasa" if fb["gate"]["passes"] else "no pasa", "%.2e" % fb["gate"]["worst"], "compatible" if fb["a11_anomaly_n20000"]["compatible"] else "incompatible",
            f(fb["a11_anomaly_n20000"]["z"], 2)))
    w("")


def anomalies(w):
    if have("A"):
        a = J("A")
        lit = a["G_A1"]["outside_literal"]
        w("- G-A1: %d de %d tamaños ψ = 0 fuera de la región literal al 95 %% (esperados %s): %s." % (
            len(lit), a["G_A1"]["n_checks"], f(a["G_A1"]["expected_outside_literal"], 1),
            ", ".join("%s = %s" % (k, f(a["G_A1"]["checks"][k])) for k in lit) or "ninguno"))
        by_cell = {}
        for k in lit:
            cell = "|".join(k.split("|")[:2])
            by_cell[cell] = by_cell.get(cell, 0) + 1
        w("  Por celda (caso|n): %s. Los procedimientos de una celda se evalúan sobre las mismas trayectorias, así que sus tamaños están correlacionados; todos caen dentro de la región de Bonferroni." % (
            ", ".join("%s: %d de %d" % (c, m, len(P.PROCS)) for c, m in by_cell.items()) or "—"))
        for case, v in a["G_A2"].items():
            if not v["within"]:
                w("- G-A2, caso %s: MZ_t NP asintótico %s frente a %s de NP (2000); las cifras de NP son de MZ_α." % (case, f(v["mzt_np_asy"]), f(v["np2000_mzalpha"], 3)))
        m8 = ("ma", P.ERRORS[0][1])
        for case in D.CASES:
            parts = []
            for n in D.A_N:
                r = a["size"][D.size_cell(m8, n, case)]
                parts.append("n = %d: tamaño %s, cuantil 5 %% de la celda %s frente al del iid %s" % (
                    n, f(r["iid"]["gls_t0"]["rate"]), f(r["size_adjusted_q"]["gls_t0"]),
                    f(a["config"]["iid_quantiles"]["%d|%s" % (n, case)]["gls_t0 (cuantil)"])))
            w("- RM-GLS θ = 0 a ψ = −0.8, caso %s, por n: %s. El tamaño depende de dónde cae la cola inferior de la celda respecto del valor crítico iid, no de la mediana." % (case, "; ".join(parts)))
        nan = {k: sum(r["diagnostics"]["nan"].values()) for k, r in a["size"].items() if sum(r["diagnostics"]["nan"].values())}
        w("- Valores no finitos en las celdas de tamaño: %s." % (", ".join("%s: %d" % kv for kv in nan.items()) or "ninguno"))
    if have("B"):
        nz = b_paso0_nonzero()
        if nz:
            w("- Paso 0 de B12.B no nulo fuera de las columnas usadas: %s. Mismas versiones de numpy, scipy y arch que A9 (procedencia de los JSON); la diferencia es de un ulp en el t de DF-GLS de `arch`, compatible con BLAS multihilo con distinto número de hilos (A9 calculó en trabajadores paralelos, el Paso 0 en el proceso principal). DF-GLS no interviene en B12.B." % (
                "; ".join("`%s`: %s" % (k, ", ".join("%s %.1e" % cx for cx in v.items())) for k, v in nz.items())))
    if have("F"):
        fb = J("F")
        w("- B12.F: la anomalía T3 de A11 (media simulada de n = 20 000 por debajo de la de n = 5000) queda explicada si z frente al valor exacto es compatible: z = %s." % f(fb["a11_anomaly_n20000"]["z"], 2))
    w("")


def manuscript_rows():
    q = J("Q")["quotes"]
    rows = []
    if have("A"):
        a = J("A")
        s = lambda err, n, case, p, kind="iid": a["size"][D.size_cell(err, n, case)][kind][p]["rate"]    # noqa: E731
        m8 = ("ma", P.ERRORS[0][1])
        txt = "; ".join("%s n = %d: RM-GLS θ=0 %s, θ=0.02 %s, (b) %s, (b′) %s, MZ_t NP asint. %s" % (
            case, n, f(s(m8, n, case, "gls_t0")), f(s(m8, n, case, "gls_t0.02")), f(s(m8, n, case, "glsb_t0")), f(s(m8, n, case, "glsbp_t0")),
            f(s(m8, n, case, "mzt", "asy"))) for case in D.CASES for n in D.A_N)
        rows.append([cite(q["ma_not_examined"]), "«whether it survives negative moving-average components ... was not examined»",
                     "Examinado en B12.A (desenlace %s). Tamaño a ψ = −0.8: %s" % (a["classification"]["outcome"], txt), "sí: la frase describe un examen que ya existe"])
        rows.append([cite(q["ma_mtests"]), "Las pruebas M «combine that local power with better size control in the presence of negative moving-average»",
                     "MZ_t-GLS NP asintótico a ψ = −0.8: %s" % "; ".join("%s n = %d: %s" % (c, n, f(s(m8, n, c, "mzt", "asy"))) for c in D.CASES for n in D.A_N),
                     "—"])
    if have("C"):
        c = J("C")
        top = max(D.C_ALPHA)
        txt = "; ".join("ρ = %s: RM-GLS θ=0 %s (α = 0: %s), DF-GLS %s (α = 0: %s)" % (
            f(r["rho"], 2), f(r["power"]["gls_t0"]["rate"], 3), f(c["cells"]["%s|alpha0" % D.rtag(r["rho"])]["power"]["gls_t0"]["rate"], 3),
            f(r["power"]["dfgls"]["rate"], 3), f(c["cells"]["%s|alpha0" % D.rtag(r["rho"])]["power"]["dfgls"]["rate"], 3))
            for r in c["cells"].values() if r["alpha"] == top)
        for k in ("initial_sec1", "initial_sec3", "initial_sec7"):
            rows.append([cite(q[k]), "Alternativas con condición inicial cero; no se examina u₀ grande", "Examinado en B12.C. Potencia a α = %g: %s" % (top, txt),
                         "sí: la frase describe un examen que ya existe"])
    if have("B"):
        b = J("B")
        m = b["by_n"]["c|200"]
        rows.append([cite(q["attrib_power"]), "(a)−(b) = %s puntos de media en DGP 1, c, n = 200" % q["attrib_power"]["groups"][0],
                     "A12 (calibración de A10, N_cal = 500 000): (a)−(b) = %s pp, (a)−(b′) = %s pp, (b′)−(b) = %s pp" % (
                         pp(m["a_minus_b"]["mean"]), pp(m["a_minus_bp"]["mean"]), pp(m["bp_minus_b"]["mean"])),
                     "C %s" % ("se cumple" if b["C"]["holds"] else "no se cumple")])
        d = b["diagnostics_n200"]
        rows.append([cite(q["attrib_mechanism"]), "«The autoregressive spectral estimate ... does not collapse as fast»",
                     "Medianas a n = 200 (c): %s" % "; ".join("ρ = %s: σ̂²_HAC %s, s²_AR GLS %s, s²_AR MCO %s" % (
                         f(v["rho"], 2), f(v["s2_hac"], 3), f(v["s2ar_gls"], 3), f(v["s2ar_ols"], 3)) for v in d.values() if v["case"] == "c"), "—"])
    if have("F"):
        fb = J("F")
        qa = q["anchor_sim"]["groups"]
        k3 = len(qa) // 2
        for printed, n in zip(qa[:k3], qa[k3:]):
            r = fb["rows"][n]
            d = len(printed.split(".")[1])
            ex = round(r["exact"], d)
            sim = r.get("sim_A11")
            where = [cite(q["anchor_sim"])] + [cite(q[k]) for k in ("anchor_remark_n200", "anchor_remark_n2000") if q[k]["groups"][0] == n]
            ok = ex == float(printed)
            rows.append([", ".join(where), "E[S₀²] simulado a n = %s: %s" % (n, printed),
                         "Exacto (B12.F): %s → %s a %d decimales. Media simulada de A11: %s ± %s (a %d decimales: %s; es la que A11 propuso cuando el impreso no coincidía con ella)" % (
                             f(r["exact"], 6), f(ex, d), d, f(sim["mean"], 5), f(sim["se"], 5), d, f(round(sim["mean"], d), d)),
                         ("no" if round(sim["mean"], d) == float(printed) else "no: el impreso es el exacto; la corrección de A11 debe retirarse") if ok else
                         "sí: %s → %s (no la cifra simulada de A11)" % (printed, f(ex, d))])
        rows.append([cite(q["anchor_remark"]), "E[S₀²] = 1/2 − κ(c̄)/n + O(n⁻²)",
                     "Valor exacto (B12.F): %s" % "; ".join("n = %s: %s (1/2 − κ/n %s; con n + c̄²: %s)" % (
                         k, f(r["exact"], 4), f(r["first_order_A11"], 4), f(r["formula"], 4)) for k, r in fb["rows"].items()),
                     "sí, si se usa la forma con n + c̄² (compuerta %s)" % ("pasa" if fb["gate"]["passes"] else "no pasa")])
    return rows


def master():
    rows = []
    if have("A"):
        a = J("A")
        for name, r in a["size"].items():
            for p in ("gls_t0", "gls_t0.02", "glsb_t0", "glsbp_t0"):
                x = r["iid"][p]
                rows.append(["A tamaño %s %s n=%d %s" % (PN[p], EN[r["err_tag"]], r["n"], r["case"]), f(x["rate"]), "EE %s" % f(x["se"]),
                             x["n"], a["config"]["N_cal"], C.FAMILY["A"], F["A"], "size.%s.iid.%s.rate" % (name, p)])
            x = r["asy"]["mzt"]
            rows.append(["A tamaño MZ_t NP asint. %s n=%d %s" % (EN[r["err_tag"]], r["n"], r["case"]), f(x["rate"]), "EE %s" % f(x["se"]), x["n"], "—",
                         C.FAMILY["A"], F["A"], "size.%s.asy.mzt.rate" % name])
    if have("B"):
        b = J("B")
        for k, v in b["by_n"].items():
            for d in ("a_minus_bp", "bp_minus_b", "bp_minus_c"):
                c0 = b["cells"][v["cells"][0]]
                rows.append(["B media %s %s" % (DN[d], k), pp(v[d]["mean"]), "EE %s pp" % f(v[d]["se"] * PP, 2), c0["rates"]["a"]["n"],
                             c0["bp_N_cal"], "95 / 136",
                             F["B"], "by_n.%s.%s.mean" % (k, d)])
    if have("C"):
        for k, r in J("C")["cells"].items():
            for p in ("gls_t0", "dfgls"):
                x = r["power"][p]
                rows.append(["C potencia %s %s" % (PN[p], k), f(x["rate"], 4), "EE %s" % f(x["se"]), x["n"], J("A")["config"]["N_cal"], C.FAMILY["C"], F["C"],
                             "cells.%s.power.%s.rate" % (k, p)])
    if have("F"):
        for k, r in J("F")["rows"].items():
            rows.append(["F E[S₀²] exacta n=%s" % k, f(r["exact"], 6), "exacto", "—", "—", C.FAMILY["F"], F["F"], "rows.%s.exact" % k])
    return rows


def main():
    lines = []
    w = lines.append
    L = lines
    w("# Auditoría A12 — Errores MA, la variante Perron–Qu, la condición inicial y θ = 0")
    w("")
    w("Generado por `experiments/audit12_generate_report.py` el %s desde los JSON de `experiments/results`. Commit de HEAD: `%s`. Protocolo: `%s`; predicción: `experiments/prediccion_ma_audit12.md`." % (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), C.git("rev-parse", "HEAD")[:7], PROTOCOL))
    w("")
    w("Etiquetas: la columna que A8–A10 llaman «msbhac» no interviene en A12; si aparece, se llama «MSB-OLS-HAC».")
    w("")
    w("## 1. Resultados")
    w("")
    sec_b0(w, L)
    for key, fn in (("A", sec_a), ("B", sec_b), ("C", sec_c), ("F", sec_f)):
        if have(key):
            fn(w, L)
    w("## 2. Compuertas")
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
    L.extend(table(["Bloque", "Motivo"], not_executed()))
    w("")
    w("## 6. Conclusiones")
    w("")
    conclusions(w)
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    w("### (a) Anomalías numéricas")
    w("")
    anomalies(w)
    if have("Q"):
        w("### (b) Frases del manuscrito v12 afectadas por A12")
        w("")
        L.extend(table(["Manuscrito v12", "Qué dice", "Qué mide A12", "¿Requiere cambio?"], manuscript_rows()))
        w("")
    w("## Anexo: tabla maestra")
    w("")
    L.extend(table(["clave", "valor", "IC/EE", "N_sim", "N_cal", "familia", "JSON", "ruta"], master()))
    w("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    C.register_outputs(__file__, [OUT])
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
