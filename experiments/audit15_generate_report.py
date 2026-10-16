"""
Auditoria A15 - generador del reporte experiments/results/resultados_auditoria_15.md
(protocol_audit15.md, lectura R1).

Solo lee JSON (tests/test_no_literals_audit15.py). Siete secciones y tabla maestra. Los bloques
cuyo JSON aun no existe (B15.1, B15.3) aparecen como pendientes.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "resultados_auditoria_15.md")
F = {"b0": "b0_iidasy_audit15.json", "t3": "b0_t3_audit15.json", "b0b": "b0b_lag_audit15.json", "tab": "tables_audit15.json",
     "b2": "e4_slope_audit15.json", "b5": "b5_anon_audit15.json", "man": "manifest_audit15.json",
     "b1": "b1_boot_audit15.json", "b3": "b3_fixedb_audit15.json", "inv": "inventory_audit15.json",
     "p0": "b1_paso0_audit15.json", "p3": "b3_paso0_audit15.json", "probe": "probes_audit15.json",
     "p0v2": "b1_paso0_v2_audit15.json", "v17": "v17_tables_audit15.json", "lit": "literals_v17_audit15.json",
     "supp": "supplement_audit15.json", "mnt": "maintenance_audit15.json", "fix": "supplement_fix_audit15.json",
     "plan": "supplement_plan_v17_audit15.json", "tpl": "template_audit15.json"}
ARM_LAB3 = {"SB": "SB de bootUR (brazo (iii) «SB (bootUR)»)", "SWB": "SWB de bootUR (brazo (v′) «SWB (bootUR)»)"}
D_M = (0.005, 0.01)              # margenes de la prediccion 14cbca7
ARM_LAB = {"SB": "SB de bootUR (referencia del brazo (iii))", "SWB": "SWB (bootUR)"}
LAB = {"msb": "MSB-GLS", "mzt": "MZ_t-GLS", "msb_pq": "MSB-GLS (PQ)", "mzt_pq": "MZ_t-GLS (PQ)", "dfgls": "DF-GLS"}
CASE = {"c": "constante", "ct": "tendencia", "both": "ambos"}
GROUP = {"psi_m0p8": "ψ = −0.8", "m0p5": "{ψ = −0.5, φ = −0.5}", "psi_0": "ψ = 0", "p0p5": "{ψ = +0.5, φ = +0.5}"}
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


def yn(b):
    return "sí" if b else "no"


def short(h):
    return (h or "—")[:7]


def s_b0(w, L):
    d = J("b0")
    w("### B15.0 — Comparación iid / asintótico (desde `bA_ma_audit12.json`)")
    w("")
    s = d["sha_check"]
    w("sha256 de `%s` en disco `%s`; en `manifest_audit12.json` `%s`: coinciden **%s**. Celdas: %d; con ψ ≠ 0: %d. Región "
      "exacta de 2×10⁴ caminos: [%s, %s]." % (d["source"], s["sha256_disk"], s["sha256_manifest"], yn(s["matches"]), d["n_cells"],
                                             d["n_cells_psi_nonzero"], g(d["exact_region_20000"][0]), g(d["exact_region_20000"][1])))
    w("")
    w("**(a) y (d).** Celdas con tasa iid mayor que la asintótica y rango de iid − asy (pp) por caso:")
    w("")
    rows = [[LAB[p], "%d de %d" % (d["a_iid_gt_asy"][p]["iid_gt_asy"], d["a_iid_gt_asy"][p]["cells"]),
             d["a_iid_gt_asy"][p]["iid_lt_asy"]] + ["%s a %s" % (g(d["d_diff_range"][p][c]["min"] * C.PP, 2),
                                                               g(d["d_diff_range"][p][c]["max"] * C.PP, 2)) for c in ("c", "ct")]
            for p in d["procs"]]
    L.extend(table(["Procedimiento", "iid > asy", "iid < asy", "iid − asy, constante (pp)", "iid − asy, tendencia (pp)"], rows))
    w("")
    w("**(b).** Media y máximo de |tasa − 0.05| sobre las celdas con ψ ≠ 0 (15 por caso):")
    w("")
    rows = []
    for p in d["procs"]:
        for c in ("c", "ct", "both"):
            x = d["b_abs_dev"][p][c]
            rows.append([LAB[p], CASE[c], g(x["iid"]["mean"]), g(x["iid"]["max"]), g(x["asy"]["mean"]), g(x["asy"]["max"])])
    L.extend(table(["Procedimiento", "Caso", "iid: media", "iid: máx.", "asy: media", "asy: máx."], rows))
    w("")
    w("**(c).** Celdas en que cada valor crítico queda más cerca de 0.05 (iid / asy / empate), por grupo × caso:")
    w("")
    rows = []
    for p in d["procs"]:
        for c in ("c", "ct"):
            rows.append([LAB[p], CASE[c]] + ["%d / %d / %d" % (x["iid_closer"], x["asy_closer"], x["tie"])
                                              for x in (d["c_closer"][p][c][gk] for gk in GROUP)])
    L.extend(table(["Procedimiento", "Caso"] + list(GROUP.values()), rows))
    w("")
    t = J("tab")
    w("Tabular: %s (sha256 %s), %d decimales, redondeo %s; negrita: %s." % (
        ", ".join("`%s`" % k for k in t["outputs"]), ", ".join("`%s`" % v for v in t["outputs"].values()), t["decimals"],
        "binario" if t["rounding"] == "binary" else t["rounding"], t["bold"]))
    w("")
    t3 = J("t3")
    w("**Literales del parche T3.** Asignaciones fijas del autor (enmienda 1, E1.5), redondeo binario; las cuatro celdas de "
      "«0.062 to 0.092» y «0.036 to 0.050» son %s. Resumen: %d coinciden, %d no coinciden, %d sin asignar." % (
          ", ".join(t3["four_cells"]), t3["summary"]["coinciden"], t3["summary"]["no_coinciden"], t3["summary"]["sin_asignar"]))
    w("")
    rows = []
    for r in t3["literals"]:
        val = r.get("value")
        vs = "—" if val is None else (", ".join(g(v, 5) for v in val) if isinstance(val, list) else g(val, 5))
        rows.append([r["literal"], r["status"], r.get("assignment") or "—", r.get("key") or "—", vs, r.get("binary") or "—",
                     r.get("outward") or "—", r.get("verdict") or r.get("note")])
    L.extend(table(["Literal", "Estado", "Magnitud asignada", "Clave", "Valor", "Binario", "Hacia afuera", "Veredicto"], rows))
    w("")


def s_b0b(w, L):
    d = J("b0b")
    w("### B15.0b — Tamaño condicionado al retardo de la MAIC GLS (descriptivo)")
    w("")
    w("Paso 0: la tasa agregada sobre k reproduce `iid.rate` y `asy.rate` de `bA_ma_audit12.json`: máx. |Δ| = %.1e (%s)." % (
        d["paso0"]["max_abs_diff"], "pasa" if d["paso0"]["passes"] else "NO pasa"))
    w("")

    def block(title, src):
        rows = []
        for key, r in src.items():
            for p, x in r["procs"].items():
                for lab, v in x["by_k"].items():
                    rows.append([key, LAB[p], lab, v["paths"], g(v["share"], 3),
                                 "—" if v["iid"]["rate"] is None else "%s [%s, %s]" % (g(v["iid"]["rate"]), g(v["iid"]["wilson_lower"]), g(v["iid"]["wilson_upper"])),
                                 "—" if v["asy"]["rate"] is None else "%s [%s, %s]" % (g(v["asy"]["rate"]), g(v["asy"]["wilson_lower"]), g(v["asy"]["wilson_upper"]))])
        w(title)
        w("")
        L.extend(table(["Celda", "Procedimiento", "k", "Caminos", "Fracción", "Tasa iid [Wilson]", "Tasa asy [Wilson]"], rows))
        w("")
    block("Celdas de A12 (N = 2×10⁴):", {k: v for k, v in d["cells"].items()})
    ex = {k: v for k, v in d["a10_null"].items() if v.get("executed")}
    if ex:
        block("Nula iid de A10 (N_cal = 5×10⁵; la tasa iid agregada es 0.05 por construcción):", ex)
    for k, v in d["a10_null"].items():
        if not v.get("executed"):
            w("- A10 %s: no ejecutado (%s)." % (k, v["reason"]))
    lt = J("tab")["lag_table"]
    w("Tabular para el suplemento S5: `%s` (sha256 `%s`), desde `%s`, %d decimales, redondeo %s (%s)." % (
        lt["output"], lt["sha256"], lt["source"], lt["decimals"], "binario" if lt["rounding"] == "binary" else lt["rounding"], lt["reading"]))
    w("")


def s_b2(w, L):
    d = J("b2")
    w("### B15.2 — Pendientes")
    w("")
    rows = [[s["path"], "`%s`" % s["sha256_a14"], "`%s`" % s["sha256_disk"], "`%s`" % s["sha256_committed"],
             short(s["last_commit"]["last_commit"]), yn(s["matches"])] for s in d["a_scripts"].values()]
    w("**(a)** Scripts commiteados con el sha256 que registró A14:")
    w("")
    L.extend(table(["Script", "sha256 A14", "sha256 en disco", "sha256 commiteado", "Commit", "Coinciden"], rows))
    w("")
    cfg = d["config"]
    w("**(b)** Réplica de `audit4_tarea_E.py`: semilla %d, %d réplicas, n ∈ {%s}, agregación por %s. ρ̂ del script: %s. ρ̂ de la "
      "librería: %s. (El encargo describe el del script como «%s».)" % (
          cfg["seed"], cfg["reps"], ", ".join("%d" % n for n in cfg["n_grid"]), cfg["aggregation"], cfg["rho_script"],
          cfg["rho_library"], cfg["assignment_says"]))
    w("")
    p0 = d["paso0"]
    w("Paso 0 (a %s): columnas usadas iguales: %s; resto: %s." % (p0["precision"], yn(p0["used_all_equal"]), yn(p0["other_all_equal"])))
    w("")
    rows = []
    for lab, r in d["b"].items():
        rows.append([lab, g(r["slope_B_pre_script"], 6), g(r["slope_B_pre_lib"], 6), "%.2e" % abs(r["slope_diff_B_pre"]),
                     g(r["R2_B_pre_script"], 4), g(r["R2_B_pre_lib"], 4), g(r["slope_B_ceil_script"], 6), g(r["slope_B_ceil_lib"], 6),
                     "%.2e" % r["max_abs_rho_diff"]])
    L.extend(table(["Proceso", "Pendiente B_pre (script)", "Pendiente B_pre (librería)", "|Δ|", "R² script", "R² librería",
                    "Pendiente B_ceil (script)", "Pendiente B_ceil (librería)", "máx. |Δρ̂| por camino"], rows))
    w("")
    rows = []
    for lab, r in d["b"].items():
        m = r["means_by_n"]
        for n in m["B_pre_script"]:
            rows.append([lab, n, g(m["B_pre_script"][n], 4), g(m["B_pre_lib"][n], 4), g(m["B_ceil_script"][n], 3), g(m["B_ceil_lib"][n], 3)])
    w("Medias por n:")
    w("")
    L.extend(table(["Proceso", "n", "B_pre script", "B_pre librería", "B_ceil script", "B_ceil librería"], rows))
    w("")


def s_b5(w, L):
    d = J("b5")
    w("### B15.5 — Anonimización (inventario y propuesta)")
    w("")
    w("Alcance: %d archivos (%s)." % (d["scope"]["files"], ", ".join("%s %d" % kv for kv in d["scope"]["by_top_dir"].items())))
    w("")
    rows = [[cat, x["files"], x["hits"]] for cat, x in d["totals"].items()]
    L.extend(table(["Categoría", "Archivos", "Aciertos"], rows))
    w("")
    rows = []
    for f, h in d["inventory"].items():
        for cat, x in h.items():
            if cat == "hash_de_commit":
                continue
            rows.append([f, cat, x["count"], "; ".join("l. %d «%s»" % (s["line"], s["match"]) for s in x["samples"])])
    L.extend(table(["Archivo", "Categoría", "Aciertos", "Muestras"], rows))
    w("")
    hc = sorted(((f, h["hash_de_commit"]["count"]) for f, h in d["inventory"].items() if "hash_de_commit" in h), key=lambda x: -x[1])
    w("Hashes de commit (40 hex): %d aciertos en %d archivos; los que más: %s." % (
        d["totals"]["hash_de_commit"]["hits"], d["totals"]["hash_de_commit"]["files"],
        ", ".join("`%s` (%d)" % x for x in hc[:5])))
    w("")
    w("Metadatos de PDF: %d archivos; campos presentes: %s." % (len(d["pdf_metadata"]), ", ".join(d["pdf_fields_present"])))
    w("Identidades en la historia de git: %s." % ", ".join(d["git_history_identities"]))
    w("")
    p = d["proposal"]
    w("**Propuesta.** Reemplazos: %s. Hashes: %s. PDF: %s. Git: %s. Cita: %s." % (
        "; ".join("%s → «%s»" % kv for kv in p["replacements"].items()), p["commit_hashes"], p["pdf"], p["git"], p["citation"]))
    w("")
    t = d["trial_build"]
    w("Excluidos del paquete: %s; líneas eliminadas en la copia: %s; %s." % (
        ", ".join("`%s`" % x for x in p["excluded_files"]), "; ".join("`%s` l. %s" % (k, ", ".join("%d" % i for i in v))
                                                                    for k, v in p["dropped_lines"].items()), p["supplementary"]))
    w("")
    w("**Construcción de prueba** (%s): %d archivos, %d PDF reescritos, %d hashes de commit conservados; campos de PDF tras limpiar: "
      "%s; residuo: %s. Limpia: **%s**." % (t["location"], t["files"], t["pdf_rewritten"], t["hashes_kept"],
                                            ", ".join(t["pdf_fields_after"]) or "ninguno",
                                            ", ".join(t["residual_non_hash"]) or "ninguno", yn(t["clean"])))
    w("")
    pr = d["previous_residue"]
    w("**Residuo «correo» del reporte parcial (commit `%s`).** Cadena exacta: `%s`. %s" % (pr["commit"], pr["string"], pr["cause"]))
    w("")


def s_inv(w, L):
    d = J("inv")
    w("### Inventario, documentos y descargas")
    w("")
    rows = [[k, short(v["commit_added"]), v["commit_time"], "`%s`" % v["sha256_committed"]] for k, v in d["documents"].items()]
    L.extend(table(["Documento", "Commit", "Fecha", "sha256 commiteado"], rows))
    w("")
    rows = [[k, v["url"], v["bytes"], "`%s`" % v["sha256"], yn(v["committed"])] for k, v in d["external_files"].items()]
    L.extend(table(["Descarga", "URL", "Bytes", "sha256", "Commiteado"], rows))
    w("")
    sm = d["seed_map"]
    w("Semillas (%s): %d streams nuevos (trayectorias y brazos) frente a %d previos (%d familias de A8–A13 y %d semillas enteras). "
      "Colisiones con los previos: **%d**; dentro de A15: **%d**. Familia %d reservada sin uso." % (
          sm["method"], sm["new_streams_total"], sm["prior_streams_total"], len(sm["prior_families"]), sm["prior_integer_seeds"],
          sm["collisions_new_vs_prior"], sm["collisions_within_new"], d["families"]["reserved_unused"]))
    w("")
    rows = [[f, x["cells"], x["path_streams"], x["arm_streams"]] for f, x in sm["new_families"].items()]
    L.extend(table(["Familia", "Celdas", "Streams de trayectoria", "Streams por brazo"], rows))
    w("")


def s_b1p0(w, L):
    d = J("p0")
    cfg = d["config"]
    w("### B15.1 — Paso 0 contra bootUR 1.0.5 con B = 399 (familia %s; diagnóstico, no se reevalúa)" % d["provenance"]["seed_family"])
    w("")
    w("%d series de n = %d (%s; %d por celda), T = %d, pmax = %d, B = %d en los dos lados. %s. Semillas: R %s; Python %s." % (
        len(d["series"]), cfg["n"], "; ".join("%s %s" % (e, c) for e, c in cfg["cells"]), cfg["per_cell"], cfg["T"], cfg["pmax"],
        cfg["B"], cfg["bootur_version"], cfg["r_seeds"], cfg["python_streams"]))
    w("")
    rows = []
    for m, c in d["criteria"].items():
        nb = d["noise_benchmark"][m]
        rows.append([ARM_LAB[m], "%.1e" % c["max_abs_stat"], c["max_abs_lag"], g(c["mean_abs_p"]), g(c["max_abs_p"]),
                     g(nb["expected_mean_abs_p_if_exact"]), "%s (EE %s)" % (g(nb["signed_mean_p_py_minus_r"]), g(nb["signed_mean_se"])),
                     "; ".join("%s %s%s" % (cs, g(d["size_replica"][cs][m]["rate"]), "" if d["size_replica"][cs][m]["in_region"] else " FUERA")
                               for cs in d["size_replica"])])
    L.extend(table(["Método", "máx. |Δ| estadístico", "máx. |Δ| retardo", "media |Δp|", "máx. |Δp|",
                    "media |Δp| esperada si la réplica es exacta", "media de p_py − p_R", "tamaño de la réplica (2000 caminos)"], rows))
    w("")
    reg = list(d["size_replica"].values())[0]["SB"]["region"]
    w("Criterios registrados (lectura 1.7): estadístico ≤ %s, retardo = 0, media de |Δp| ≤ %s, tamaño en la región exacta [%s, %s]. "
      "MZ_t-GLS de numba frente a `np_statistics`: máx. |Δ| = %.1e." % (
          cfg["tolerances"]["stat"], cfg["tolerances"]["mean_abs_p"], g(reg[0]), g(reg[1]), d["mzt_numba_vs_np_statistics"]["max_abs"]))
    w("")
    w("**Compuerta de la lectura 1.7 con B = 399 (diagnóstico; sustituida por la enmienda 3):** SB %s; SWB %s." % (
        "pasa" if d["gate"]["iii_sieve_SB"] else "no pasa",
        "pasa" if d["gate"]["v_prime_SWB_bootUR"] else "NO pasa"))
    w("")
    w("La columna «esperada» es un diagnóstico que no cambia la compuerta: E|X − Y|/B con X, Y ~ Bin(B, p) independientes, la "
      "discrepancia que producirían dos réplicas exactas con remuestreos distintos.")
    w("")


def s_b3p0(w, L):
    d = J("p3")
    w("### B15.3 — Paso 0 (FFT frente a suma directa) y regla de LLSW")
    w("")
    w("%d series de calibración de n = %d (familia %s). Anchos: %s. máx. |Δ| relativo: %s (tolerancia %s). Pasa: **%s**." % (
        d["series"], d["n"], d["provenance"]["seed_family"], ", ".join("%s B = %d" % kv for kv in d["bandwidths_n200"].items()),
        ", ".join("%s %.1e" % kv for kv in d["max_rel_diff"].items()), "%.0e" % d["tolerance"], yn(d["passes"])))
    w("")
    r = d["llsw_rule"]
    w("Regla de LLSW extraída del PDF: %s; %s; redondeo: %s; %s; %s. Es la cuarta configuración (enmienda 2, sección 4)." % (
        r["source"], r["equation"], r["rounding"], r["table"], r["kernel"]))
    w("")


def s_b1p0v2(w, L):
    d = J("p0v2")
    cfg = d["config"]
    w("### Paso 0 de B15.1 (enmienda 3): fidelidad de la réplica y tamaño de bootUR")
    w("")
    w("Familia %s, n = %d, T = %d, pmax = %d, B = %d en R y en Python; %d series (4 celdas × 50) y %d caminos iid por caso. %s. Semillas R: "
      "%s; Python: %s. Rechazo: %s." % (d["provenance"]["seed_family"], cfg["n"], cfg["T"], cfg["pmax"], cfg["B"], cfg["series"],
                                         cfg["size_paths_per_case"], cfg["bootur_version"], "; ".join("%s: %s" % kv for kv in cfg["r_seeds"].items()),
                                         cfg["python_streams"], cfg["rejection"]))
    w("")
    w("**Fidelidad de la réplica** (E3.1 y E3.2; esto es la compuerta):")
    w("")
    rows = []
    for m, c in d["criteria"].items():
        rows.append([ARM_LAB3[m], "%.1e / %d" % (c["a_max_abs_stat"], c["a_max_abs_lag"]),
                     "%s (EE %s; cota %s)" % (g(c["b_mean_signed"]), g(c["b_se"]), g(cfg["z"] * c["b_se"])),
                     "%s (esperada %s; cota %s)" % (g(c["c_mean_abs"]), g(c["c_expected_exact"]), g(c["c_bound"])),
                     "; ".join("%s: %s (EE %s)" % (cs, g(d["size_paired"][cs][m]["diff"]), g(d["size_paired"][cs][m]["se_paired"]))
                               for cs in d["size_paired"]),
                     yn(c["a_ok"] and c["b_ok"] and c["c_ok"] and all(d["size_paired"][cs][m]["ok"] for cs in d["size_paired"]))])
    L.extend(table(["Método", "(a) máx. |Δ| estadístico / retardo", "(b) media de p_py − p_R", "(c) media |Δp|",
                    "E3.2 tamaño py − bootUR (pareado)", "Pasa"], rows))
    w("")
    w("**Compuerta:** (iii) «SB (bootUR)» %s; (v′) «SWB (bootUR)» %s." % (
        "pasa" if d["gate"]["iii_SB_bootUR"] else "NO pasa", "pasa" if d["gate"]["v_prime_SWB_bootUR"] else "NO pasa"))
    w("")
    w("**Tamaño de bootUR** (resultado, no compuerta; B = %d, %d caminos iid de n = %d por caso):" % (cfg["B"], cfg["size_paths_per_case"], cfg["n"]))
    w("")
    rows = []
    for cs, x in d["size_paired"].items():
        for m, v in x.items():
            rows.append([CASE[cs], m, g(v["size_bootur"]), "[%s, %s]" % (g(v["bootur_wilson"][0]), g(v["bootur_wilson"][1])),
                         "[%s, %s]" % (g(v["region"][0]), g(v["region"][1])), yn(v["bootur_in_region"]), g(v["size_py"]),
                         "%d / %d" % (v["discordant_b"], v["discordant_c"])])
    L.extend(table(["Caso", "Método", "Tamaño bootUR", "Wilson 95 %", "Región exacta", "Dentro", "Tamaño réplica",
                    "Discordantes (réplica sola / bootUR sola)"], rows))
    w("")


def s_b3(w, L):
    d = J("b3")
    cfg = d["config"]
    w("### B15.3 — Fixed-b sobre MSB-B (completo)")
    w("")
    w("Configuraciones: %s. N_cal = %d por n (%s); tamaño N = %d; potencia N = %d. Rechazo: %s. Cota DKW: ε = %s (probabilidad 0.95)." % (
        "; ".join("%s: B = %s" % kv for kv in cfg["configs"].items()), cfg["N_cal"], ", ".join("%d" % n for n in cfg["cal_n"]),
        cfg["N_size"], cfg["N_power"], cfg["rejection"], g(d["dkw_eps"])))
    w("")
    rows = [[k, g(v["D"]), g(v["M"]), v["argmax"], "%d/%d" % (v["iid_in_region"], v["iid_cells"])] for k, v in d["size_summary"].items()]
    L.extend(table(["Configuración", "D (media |tamaño − 0.05|, ψ ≠ 0)", "M (máximo)", "Celda del máximo", "Celdas iid en la región"], rows))
    w("")
    pr = d["prediction"]
    w("**Predicción registrada** (%s): M por b: %s. Controla el tamaño: **%s**%s. LLSW, aparte: D = %s, M = %s." % (
        pr["rule"], ", ".join("%s %s" % (k, g(v)) for k, v in pr["M_by_b"].items()), "sí" if pr["outcome"] else "no",
        (" (%s)" % ", ".join(pr["controls"])) if pr["controls"] else "", g(pr["llsw_reported_apart"]["D"]), g(pr["llsw_reported_apart"]["M"])))
    w("")
    names = list(d["size_summary"])
    rows = []
    for k, v in d["size"].items():
        rows.append([v["err_tag"], v["n"], CASE[v["case"]]] + ["%s%s" % (g(v["rates"][c]["rate"], 3), "" if v["rates"][c]["in_region"] else "*")
                                                               for c in names])
    w("Tamaño por celda (* fuera de la región exacta de %d caminos):" % cfg["N_size"])
    w("")
    L.extend(table(["Error", "n", "Caso"] + names, rows))
    w("")
    rows = []
    for k, v in d["power"].items():
        rows.append([g(v["rho"], 2)] + [g(v["rates"][c]["rate"], 3) for c in v["rates"]]
                    + ["; ".join("%s %s (p %s)" % (c, g(x["diff_pp"], 1), "%.2g" % x["mcnemar"]["p_value"]) for c, x in v["vs_andrews"].items())])
    heads = ["ρ"] + list(next(iter(d["power"].values()))["rates"]) + ["fixed-b − Andrews, pp (McNemar)"]
    w("Potencia ajustada (DGP 1, n = 200, caso constante; la nula iid es la de la calibración):")
    w("")
    L.extend(table(heads, rows))
    w("")
    rows = [[g(v["rho"], 2)] + ["%s (p %s)" % (g(x["diff_pp"], 1), "%.2g" % x["mcnemar"]["p_value"]) for x in v["vs_b"].values()]
            for v in d["power"].values()]
    w("Frente a la variante (b) (s²_AR de la MAIC GLS), en pp:")
    w("")
    L.extend(table(["ρ"] + list(next(iter(d["power"].values()))["vs_b"]), rows))
    w("")


def s_b1(w, L):
    d = J("b1")
    cfg = d["config"]
    w("### B15.1 — Bootstrap de MZ_t-GLS bajo correlación serial")
    w("")
    w("Configuración: %s (R = %d; brazos bootstrap %s; N tamaño = %d, N potencia = %d; %s; %d núcleos)." % (
        cfg["chosen_configuration"], cfg["R"], ", ".join(cfg["arm_labels"][a] for a in cfg["boot_arms"]), cfg["N_size"], cfg["N_power"],
        cfg["pvalue"], cfg["cores"]))
    w("")
    arms = list(d["size_summary"])
    rows = [[cfg["arm_labels"][a], g(v["D"]), g(v["M"]), v["argmax"], "%d/%d" % (v["iid_in_region"], v["iid_cells"])]
            for a, v in d["size_summary"].items()]
    L.extend(table(["Brazo", "D (ψ ≠ 0)", "M", "Celda del máximo", "Celdas iid en la región"], rows))
    w("")
    rows = []
    for a, v in d["prediction"]["by_arm"].items():
        rows.append([cfg["arm_labels"][a], "%s ≤ %s − 0.005: %s" % (g(v["D"]), g(v["D_ii"]), yn(v["D"] <= v["D_ii"] - D_M[0])),
                     "%s ≤ %s − 0.010: %s" % (g(v["M"]), g(v["M_ii"]), yn(v["M"] <= v["M_ii"] - D_M[1])),
                     yn(v["dominates_size"]), yn(v["no_cost"]), v["outcome"]])
    L.extend(table(["Brazo", "D", "M", "Domina en tamaño", "Sin costo", "Desenlace"], rows))
    w("")
    w("**Desenlace global (14cbca7, A > C > B): %s.**" % d["prediction"]["overall"])
    w("")
    rows = []
    for k, v in d["size"].items():
        rows.append([v["err_tag"], v["n"], CASE[v["case"]]] + ["%s%s" % (g(v["rates"][a]["rate"], 3), "" if v["rates"][a]["in_region"] else "*")
                                                               for a in arms])
    w("Tamaño por celda (* fuera de la región exacta de %d caminos):" % cfg["N_size"])
    w("")
    L.extend(table(["Error", "n", "Caso"] + [cfg["arm_labels"][a] for a in arms], rows))
    w("")
    rows = []
    for k, v in d["power"].items():
        rows.append([v["err_tag"], g(v["rho"], 2), CASE[v["case"]]]
                    + ["%s / %s" % (g(v["raw"][a]["rate"], 3), g(v["adjusted"][a]["rate"], 3)) for a in arms]
                    + ["; ".join("%s %s pp (p %s)%s" % (cfg["arm_labels"][a], g(x["diff_pp"], 1), "%.2g" % x["mcnemar"]["p_value"],
                                                        "" if x["no_cost"] else " COSTO") for a, x in v["vs_ii"].items())])
    w("Potencia bruta / ajustada (n = 200):")
    w("")
    L.extend(table(["Error", "ρ", "Caso"] + [cfg["arm_labels"][a] for a in arms] + ["Frente a (ii), ajustada"], rows))
    w("")


def s_b156(w, L):
    t, lt = J("v17"), J("lit")
    w("### B15.6 — Tabulares y literales para el v17")
    w("")
    rows = [[k, "`%s`" % v] for k, v in t["outputs"].items()]
    L.extend(table(["Tabular o nota (desde JSON; redondeo %s)" % ("binario" if t["rounding"] == "binary" else t["rounding"]), "sha256"], rows))
    w("")
    w("Fuentes de las columnas de tab:fixedb:")
    w("")
    L.extend(table(["Configuración", "Tamaño", "Potencia"], [[k, v["size"], v["power"]] for k, v in t["column_sources"].items()]))
    w("")
    w("**Literales** (`literals_v17_audit15.json`; test independiente `tests/test_literals_v17_audit15.py`): %d confirman, %d se corrigen." % (
        lt["summary"]["confirma"], lt["summary"]["corrige"]))
    w("")
    rows = []
    for x in lt["literals"]:
        v = x["value"]
        vs = (", ".join("%.6g" % a for a in v) if isinstance(v, list) else
              ("; ".join("%s: %.3g pp, p %.3g" % (k, a[0], a[1]) for k, a in v.items()) if isinstance(v, dict) else "%.6g" % v))
        rows.append([x["id"], x["printed"], x["what"], vs, x.get("binary") or x.get("outward") or "—", x["verdict"], x.get("correct") or "—"])
    L.extend(table(["Literal", "Impreso", "Magnitud", "Valor", "Redondeo", "Veredicto", "Correcto"], rows))
    w("")
    l8 = [x for x in lt["literals"] if x["id"] == "L8"][0]
    if any(l8["rounding_sensitive"].values()):
        w("L8: extremos exactos desde los pares discordantes %s pp y %s pp. El mínimo cae justo en la mitad (%s): «1.6» sale del "
          "redondeo binario del flotante; redondeado hacia arriba sobre el valor exacto sería el siguiente decimal." % (
              l8["exact_from_counts"]["min"], l8["exact_from_counts"]["max"],
              ", ".join(k for k, v in l8["rounding_sensitive"].items() if v)))
        w("")


def s_b157(w, L):
    d = J("supp")
    w("### B15.7 — Suplemento reconstruido (`supplementary/`)")
    w("")
    op = d["old_package"]
    w("Paquete anterior (estadístico de dos canales) retirado del árbol de trabajo; su último commit es `%s` (marcador `%s`)." % (
        short(op["last_commit_with_it"]), op["marker"]))
    w("")
    rows = []
    for sid in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"):
        v = d["sections"][sid]
        rows.append([sid, "; ".join("%s: %s" % (k, x if not isinstance(x, dict) else ("sí" if x.get("written") else "NO"))
                                   for k, x in v.items()) if isinstance(v, dict) else str(v)])
    L.extend(table(["Sección", "Contenido generado"], rows))
    w("")
    tabs = sorted(k for k in d["files"] if k.startswith("tables/"))
    w("Archivos: %d (%d tabulares, %d en `data/`, %d en `protocols/`), más `supplement.tex`, `README.md` y `MANIFEST.sha256`." % (
        d["n_files"], len(tabs), sum(1 for k in d["files"] if k.startswith("data/")), sum(1 for k in d["files"] if k.startswith("protocols/"))))
    w("")
    sc, cp = d["anonymization_scan"], d["compile"]
    w("Anonimización (patrones de B15.5 sobre todo `supplementary/`): %d aciertos fuera de los hashes de commit, que se conservan (%d). "
      "Compilación de control con pdflatex: compila %s, %d errores, %d referencias indefinidas, %d cajas desbordadas, %s páginas "
      "(el PDF no se guarda)." % (sc["non_hash_hits"], sc["totals"]["hash_de_commit"]["hits"], yn(cp["compiled"]), cp["errors"],
                                  cp["undefined_references"], cp["overfull"], cp["pages"]))
    w("")
    if d["pending"]:
        w("Pendiente (no se improvisa): %s." % ", ".join(d["pending"]))
        w("")


def s_b158(w, L):
    d = J("mnt")
    gc, gi = d["gc"], d["gitignore"]
    w("### B15.8 — Mantenimiento del repositorio (enmienda 5, lecturas 8.1–8.3)")
    w("")
    b = gc["bundle"]
    w("Bundle `%s`: %d bytes, sha256 `%s`, `git bundle verify` sin error: %s. El paso 2 sólo corre si el bundle verifica." % (
        b["path"], b["bytes"], b["sha256"], yn(b["verified"])))
    w("")
    keys = ("count", "size", "in-pack", "packs", "size-pack", "garbage")
    rows = [[k, gc["count_objects_before"].get(k, "—"), (gc["count_objects_after"] or {}).get(k, "—")] for k in keys]
    L.extend(table(["`git count-objects -vH`", "Antes", "Después"], rows))
    w("")
    w("`.gitignore` (commit aparte): %s. Archivos versionados que quedan ignorados: %d; `*.npz` versionados: %d; control: %s." % (
        "; ".join("`%s`" % l for l in gi["content"].splitlines() if l and not l.startswith("#")), len(gi["tracked_but_ignored"]),
        len(gi["tracked_npz"]), "pasa" if gi["ok"] else "NO pasa"))
    w("")


def s_b157b(w, L):
    d = J("fix")
    w("### B15.7b — Correcciones del generador del suplemento (enmienda 5, lecturas 7b.1–7b.9)")
    w("")
    w("Generación de control con `--out` en un directorio temporal; `supplementary/` no se reconstruye (sigue el de B15.7).")
    w("")
    rows = [["`%s`" % x["file"], "`%s`" % x["colspec"], x["colspec_columns"], ", ".join("%d" % h for h in x["header_columns"]),
             ", ".join("%d" % r for r in x["row_columns"]), x["rows"], yn(x["consistent"])] for x in d["column_diagnosis"]]
    L.extend(table(["(a) Tabla", "colspec", "Columnas del colspec", "Columnas de la cabecera", "Celdas por fila", "Filas", "Cuadra"], rows))
    w("")
    if all(x["consistent"] for x in d["column_diagnosis"]):
        nc = d["column_diagnosis"][0]["colspec_columns"]
        w("(a) Sin descuadre en el tabular: colspec, cabecera y filas tienen el mismo número de columnas (%d). Sin ρ quedan %d rótulos "
          "(r y las columnas de resultados) y %d valores de resultados por fila, que es la cuenta «6 frente a 5». No se cambia nada." % (
              nc, nc - 1, nc - 2))
        w("")
    s6 = d["sections"]["S6"]
    w("(b) S3b y S3c con etiquetas legibles (mapa fijo del script). (c) S6 con títulos descriptivos. (d) critB en S6: %s. "
      "(e) Nota de RM en S1 y S6. (f) p-valores en notación científica sustituidos: %d; formato único «<0.001» o tres decimales. "
      "(g) «N» → «normal» en misspec: %d filas. (h) Marca «a» de KPSS en el tabular: %s; archivo de nota: %s; la nota contiene «a»: %s; "
      "la nota entra en `supplement.tex`: %s. Notas de marcas del v13 añadidas: %s." % (
          "presente" if d["critB_in_S6"] else "eliminada", sum(v.get("p_scientific_replaced", 0) for v in s6.values()),
          sum(v.get("normal_replaced", 0) for v in s6.values()), yn(d["kpss_mark"]["in_tabular"]), yn(d["kpss_mark"]["note_file"]),
          yn(d["kpss_mark"]["note_has_a"]), yn(d["kpss_mark"]["note_in_supplement_tex"]),
          ", ".join("%s (%d)" % (k, v["mark_notes"]) for k, v in s6.items() if v.get("mark_notes"))))
    w("")
    sc, cp = d["anonymization_scan"], d["compile"]
    w("Control: %d archivos; %d aciertos identificadores fuera de hashes; compila %s, %d errores, %d referencias indefinidas, "
      "%d cajas desbordadas, %s páginas." % (d["n_files"], sc["non_hash_hits"], yn(cp["compiled"]), cp["errors"], cp["undefined_references"],
                                            cp["overfull"], cp["pages"]))
    w("")


def plain(s):
    return s.replace("\\RMGLS{}", "MSB-B").replace("$", "")


def s_b159(w, L):
    t, pl, tp = J("v17"), J("plan"), J("tpl")
    w("### B15.9 — Tabulares para el v17, plan del suplemento y plantilla (enmienda 5, lecturas 9.1–9.3)")
    w("")
    w("**tab_summary** (`tables_audit15/tab_summary_audit15.tex` y su nota; redondeo binario):")
    w("")
    rows = [[plain(r["label"]), plain(r["cv"]), r["audit"], r["N_size"], g(r["D"]), g(r["M"]), g(r["min"], 3), g(r["max"], 3),
             "%d/%d" % (r["iid_in_region"], r["iid_cells"]), g(r["power"], 3), "—" if r["N_power"] is None else r["N_power"],
             "`%s`" % r["power_source"] if r["power_source"] else "— (no medida)"] for r in t["summary_rows"]]
    L.extend(table(["Fila", "Valor crítico", "Auditoría", "N tamaño", "D", "M", "mín", "máx", "iid en región", "Potencia", "N potencia",
                    "Fuente de la potencia"], rows))
    w("")
    w("**Lista para la reconstrucción del suplemento** (`%s`, sin ejecutar): %d tablas (%s), más: %s." % (
        F["plan"], pl["n_tables"], ", ".join(pl["tables_to_supplement"]), "; ".join(pl["also"])))
    w("")
    rs = tp["reference_style"]
    w("**Plantilla**: `%s`, %d bytes, sha256 `%s`, `interact.cls` «%s» (sin commitear). Estilos .bst del paquete: %s; "
      "`\\bibliographystyle` en el ejemplo: %s. La página de instrucciones de la revista no se pudo leer (%s); evidencia indirecta: "
      "el enlace de Overleaf de JSCS redirige a «%s». Estilo de referencias: NLM (`tfnlm`), a confirmar por el autor en las "
      "instrucciones de la revista." % (
          tp["url"], tp["bytes"], tp["sha256"], tp["provides_class"], ", ".join(tp["bst_files"]),
          ", ".join("`%s`" % x for v in tp["bibliographystyle_in_tex"].values() for x in v), rs["journal_instructions"],
          rs["indirect_evidence"]["redirects_to"]))
    w("")


def s_probe(w, L):
    d = J("probe")
    w("### Sondas (tiempos; %s)" % ("conteos desellados en este reporte final" if C.have(F["b1"]) else "conteos sellados hasta el reporte final"))
    w("")
    w("Núcleos: %d." % d["cores"])
    w("")
    b1 = d["b15_1"]
    if not b1.get("executed"):
        w("- Sonda de B15.1 (familia 151): no ejecutada. %s." % b1["reason"])
    else:
        w("- Sonda de B15.1 (%s, %d caminos, R = %d): segundos por camino y brazo: %s. Configuración elegida por la regla de E3.4 "
          "(≤ %d horas-núcleo): %s." % (b1["cell"], b1["paths"], b1["R"], ", ".join("%s %s" % (k, g(v, 3)) for k, v in b1["seconds_per_path"].items()),
                                         b1["budget_core_hours"], b1["chosen_configuration"]))
        rows = [[k, g(v["core_hours_scaled"], 1), g(v["core_hours_conservative"], 1), g(v["wall_hours_scaled"], 1),
                 g(v["wall_hours_conservative"], 1)] for k, v in b1["projection"].items()]
        L.extend(table(["Configuración", "horas-núcleo (escalado por n)", "horas-núcleo (conservador)", "pared (escalado)",
                        "pared (conservador)"], rows))
        w("")
        if C.have(F["b1"]):
            s = b1["sealed"]
            w("- Conteos sellados de la sonda 151 (desellados con el JSON final de B15.1): %d caminos; rechazos (i) %d, (ii) %d, %s." % (
                s["paths"], s["rejections_i"], s["rejections_ii"], ", ".join("%s %d" % kv for kv in s["rejections"].items())))
    b3 = d["b15_3"]
    if b3.get("executed"):
        pj, pc = b3["projection"], b3["projection_conservative"]
        w("- Sonda de B15.3 (%s, %d caminos): %s s por camino; proyección %s horas-núcleo (conservadora %s)." % (
            b3["cell"], b3["paths"], "%.2e" % b3["seconds_per_path_4_configs"], g(pj["total_core_hours"], 2), g(pc["total_core_hours"], 2)))
        if C.have(F["b3"]):
            st = b3["sealed"]["statistics"]
            w("- Estadísticos sellados de la sonda 158 (desellados): mediana por configuración %s." % (
                ", ".join("%s %s" % (k, g(float(sorted(v)[len(v) // 2]))) for k, v in st.items())))
    w("")


def s_gates(w, L):
    w("## 2. Compuertas")
    w("")
    p2 = J("p0v2")
    rows = [["B15.0", "sha256 de bA_ma_audit12.json = manifest_audit12.json", yn(J("b0")["sha_check"]["matches"]),
             "pasa" if J("b0")["sha_check"]["matches"] else "NO pasa"],
            ["B15.0b Paso 0", "tasa agregada sobre k = iid.rate y asy.rate de A12", "máx. |Δ| = %.1e" % J("b0b")["paso0"]["max_abs_diff"],
             "pasa" if J("b0b")["paso0"]["passes"] else "NO pasa"],
            ["B15.2(a)", "sha256 en disco y commiteado = A14", yn(J("b2")["a_all_match"]), "pasa" if J("b2")["a_all_match"] else "NO pasa"],
            ["B15.2(b) Paso 0", "ρ̂ del script reproduce resultados_auditoria_4_E.md (%s)" % J("b2")["paso0"]["precision"],
             "usadas %s; resto %s" % (yn(J("b2")["paso0"]["used_all_equal"]), yn(J("b2")["paso0"]["other_all_equal"])),
             "pasa" if J("b2")["paso0"]["used_all_equal"] and J("b2")["paso0"]["other_all_equal"] else "NO pasa"],
            ["Semillas", "0 colisiones de 151–159 (trayectorias y brazos) frente a 90–150",
             "%d / %d" % (J("inv")["seed_map"]["collisions_new_vs_prior"], J("inv")["seed_map"]["collisions_within_new"]),
             "pasa" if J("inv")["seed_map"]["collisions_new_vs_prior"] == 0 and J("inv")["seed_map"]["collisions_within_new"] == 0 else "NO pasa"],
            ["B15.1 Paso 0, B = 399 (diagnóstico)", "criterios de la lectura 1.7", "(iii) %s; (v′) %s" % (
                yn(J("p0")["gate"]["iii_sieve_SB"]), yn(J("p0")["gate"]["v_prime_SWB_bootUR"])), "no se reevalúa (E3.1)"],
            ["B15.1 Paso 0, B = 999, (iii) SB (bootUR)", "E3.1 (a)–(c) y E3.2", yn(p2["gate"]["iii_SB_bootUR"]),
             "pasa" if p2["gate"]["iii_SB_bootUR"] else "NO pasa: B15.1 detenido"],
            ["B15.1 Paso 0, B = 999, (v′) SWB (bootUR)", "E3.1 (a)–(c) y E3.2", yn(p2["gate"]["v_prime_SWB_bootUR"]),
             "pasa" if p2["gate"]["v_prime_SWB_bootUR"] else "NO pasa: (v′) detenido"],
            ["B15.1 presupuesto", "proyección ≤ 50 horas-núcleo (E3.4)", J("probe")["b15_1"].get("chosen_configuration") or "—",
             "lanzado sin nueva confirmación" if J("probe")["b15_1"].get("launch_without_new_confirmation") else "—"],
            ["B15.3 Paso 0", "σ̂² por FFT = suma directa, |Δ| relativo ≤ 1e-12", "máx. %.1e" % max(J("p3")["max_rel_diff"].values()),
             "pasa" if J("p3")["passes"] else "NO pasa"]]
    if C.have(F["mnt"]):
        m = J("mnt")
        rows.append(["B15.8.1 bundle", "`git bundle verify` sin error antes del gc", yn(m["gc"]["bundle"]["verified"]),
                     "pasa" if m["gc"]["bundle"]["verified"] else "NO pasa: gc no ejecutado"])
        rows.append(["B15.8.3 .gitignore", "`git ls-files -ci --exclude-standard` vacío y 0 `*.npz` versionados",
                     "%d / %d" % (len(m["gitignore"]["tracked_but_ignored"]), len(m["gitignore"]["tracked_npz"])),
                     "pasa" if m["gitignore"]["ok"] else "NO pasa"])
    if C.have(F["fix"]):
        fx = J("fix")
        ok = fx["compile"]["compiled"] and fx["compile"]["errors"] == 0 and fx["anonymization_scan"]["non_hash_hits"] == 0
        rows.append(["B15.7b control", "compila sin errores y 0 aciertos identificadores", "%d errores, %d aciertos" % (
            fx["compile"]["errors"], fx["anonymization_scan"]["non_hash_hits"]), "pasa" if ok else "NO pasa"])
    L.extend(table(["Bloque", "Criterio", "Resultado", "Veredicto"], rows))
    w("")


def s_prov(w, L):
    w("## 3. Procedencia")
    w("")
    docs = J("inv")["documents"]
    w("Commits: %s." % "; ".join("`%s` `%s` (%s)" % (k, short(v["commit_added"]), v["commit_time"]) for k, v in docs.items()))
    w("")
    man = J("man")["entries"]
    rows = [[k, "`%s`" % v["sha256"], v["script"], short(v["commit"]), yn(v["code_all_committed"]),
             "%s / %s / %s" % (v["assistant"]["herramienta"], v["assistant"]["modelo"], v["assistant"]["version"]) if v.get("assistant") else "—"]
            for k, v in sorted(man.items()) if "resultados_auditoria" not in k]
    L.extend(table(["Archivo", "sha256", "Script", "Commit", "Código commiteado", "Asistente"], rows))
    w("")
    w("Familias: 151–158 asignadas (158: sonda de B15.3); 159: Paso 0 con B = 999 (enmienda 3); 150 reservada sin uso desde A14. "
      "Descargas sin commitear (E3.6); sus sha256 están en la enmienda 2 y en §1.")
    w("")


def s_dev(w, L):
    w("## 4. Desviaciones")
    w("")
    rows = [["B15.0: el tabular da el tamaño con el valor crítico iid y con el asintótico; la lectura 0.3 decía «valor crítico iid y "
             "asintótico»", "Errata de la lectura: el bloque compara tasas de rechazo", "Al escribir el exportador", "Ninguno sobre las cifras"],
            ["B15.2(b): el ρ̂ del script usa np.var con ddof = 0 (el encargo dice ddof = 1)", "Se replica el script tal como está escrito",
             "Antes de calcular (lectura 2.2)", "El Paso 0 confirma que es el ρ̂ que produjo 0.3332"],
            ["B15.5: la copia anonimizada de prueba se construye en el directorio temporal y se borra; no se registra su ruta",
             "La ruta contiene el nombre de usuario", "Al escribir el script", "Ninguno"],
            ["B15.1: el brazo (iii) pasa a ser «SB (bootUR)» (enmienda 3, E3.3); se retira la definición anterior (AR sobre Δy centrado, AIC)",
             "Decisión del autor", "Tras ver el Paso 0 con B = 399 sobre DF-GLS y antes de computar datos de B15.1",
             "El Paso 0 valida el DGP que usa el brazo; los criterios de desenlace de 14cbca7 no cambian"],
            ["B15.1: Paso 0 repetido con criterios nuevos, B = 999 y familia 159 (enmienda 3, E3.1–E3.2)", "Decisión del autor",
             "Tras la compuerta no superada con B = 399", "La corrida con B = 399 queda como diagnóstico"],
            ["B15.3: se lanzó a la vez que el Paso 0 nuevo y el JSON final se regeneró en la cadena final desde sus checkpoints",
             "E3.5; la procedencia del JSON corresponde al commit de la cadena final", "Durante la ejecución", "Ninguno sobre las cifras"],
            ["B15.3: la predicción se evalúa en b ∈ {0.1, 0.3, 1.0}; LLSW se reporta aparte", "Texto de 14cbca7", "Antes de calcular (E3.5)",
             "Ninguno"],
            ["B15.7b(a): no se corrige nada en las tablas dgp5", "El diagnóstico no encuentra descuadre (§1, B15.7b)", "Tras diagnosticar",
             "Ninguno"],
            ["B15.9: los extremos de la región exacta se escriben con los decimales necesarios, lo que cambia la nota de tab_fixedb_size "
             "(extremo superior para 2×10⁴ caminos)", "Con 4 decimales el extremo quedaba recortado", "Al generar tab_summary",
             "Sólo la nota; el tabular no cambia"],
            ["B15.9: la potencia de la fila fixed-b de tab_summary usa valores críticos simulados bajo iid, sin ajuste adicional",
             "Lectura 9.1: la fuente no tiene potencia ajustada aparte", "Antes de calcular", "Declarado en la nota"]]
    L.extend(table(["Desviación", "Motivo", "Cuándo", "Efecto"], rows))
    w("")
    w("Declaradas en el protocolo antes de calcular: p-valor por rango (1 + #{T* ≤ T})/(R + 1) frente a def:awb; MAIC GLS sin "
      "Perron–Qu en MZ_t-GLS (el DGP de (iii) y (v′) usa la MAIC de Perron–Qu de bootUR); familia 158 para la sonda de B15.3.")
    w("")


def s_not(w, L):
    w("## 5. No ejecutado")
    w("")
    w("- **B15.1 (v)**: No ejecutado: sin el PDF de Cavaliere–Taylor (2009); lo sustituye (v′) «SWB (bootUR)» (enmienda 1, E1.3).")
    if not C.have(F["b1"]):
        w("- **B15.1**: sin JSON final (%s)." % ("detenido por E3.4" if not J("p0v2")["gate"]["iii_SB_bootUR"] else "no terminado"))
    w("- **B15.4**: el v17 no existe.")
    if C.have(F["fix"]):
        w("- **Reconstrucción de `supplementary/`** con las correcciones de B15.7b y la lista de B15.9.2: después del v17 (encargo).")
    w("")


def s_concl(w, L):
    w("## 6. Conclusiones")
    w("")
    d, t3, b2, b5 = J("b0"), J("t3"), J("b2"), J("b5")
    w("- B15.0: con valores críticos iid, MSB-GLS y MZ_t-GLS rechazan más que con los asintóticos en %d y %d de %d celdas; DF-GLS en %d." % (
        d["a_iid_gt_asy"]["msb"]["iid_gt_asy"], d["a_iid_gt_asy"]["mzt"]["iid_gt_asy"], d["n_cells"], d["a_iid_gt_asy"]["dfgls"]["iid_gt_asy"]))
    w("- B15.0 (T3): %d de %d literales coinciden con las asignaciones fijas del autor (redondeo binario)." % (
        t3["summary"]["coinciden"], len(t3["literals"])))
    p2 = J("p0v2")
    w("- B15.1, Paso 0 con B = 999: la réplica es fiel a bootUR (SB %s, SWB %s); el tamaño de bootUR en el caso constante es %s (SB) y %s (SWB)." % (
        "pasa" if p2["gate"]["iii_SB_bootUR"] else "no pasa", "pasa" if p2["gate"]["v_prime_SWB_bootUR"] else "no pasa",
        g(p2["size_paired"]["c"]["SB"]["size_bootur"]), g(p2["size_paired"]["c"]["SWB"]["size_bootur"])))
    if C.have(F["b1"]):
        b1 = J("b1")
        w("- B15.1: desenlace %s (%s). D y M de (ii): %s y %s." % (
            b1["prediction"]["overall"], "; ".join("%s: %s" % (b1["config"]["arm_labels"][a], v["outcome"]) for a, v in b1["prediction"]["by_arm"].items()),
            g(b1["size_summary"]["ii"]["D"]), g(b1["size_summary"]["ii"]["M"])))
    if C.have(F["b1"]):
        sig = [v for v in J("b1")["power"].values() if v["vs_ii"]["iii"]["mcnemar"]["p_value"] < C.ALPHA]
        w("- B15.1: la potencia ajustada de (iii) frente a (ii) difiere con McNemar p < 0.05 en %d de las %d celdas de potencia (no en "
          "todas)." % (len(sig), len(J("b1")["power"])))
    b3 = J("b3")
    w("- B15.3: fixed-b controla el tamaño según la predicción registrada: %s (M mínimo %s en %s)." % (
        "sí" if b3["prediction"]["outcome"] else "no", g(min(b3["prediction"]["M_by_b"].values())),
        min(b3["prediction"]["M_by_b"], key=b3["prediction"]["M_by_b"].get)))
    ar = b2["b"]["AR 0.5"]
    w("- B15.2: scripts commiteados con los sha256 de A14: %s. Pendiente de B_pre en AR(0.5): %s con el ρ̂ del script y %s con el de "
      "la librería (|Δ| = %.2e)." % (yn(b2["a_all_match"]), g(ar["slope_B_pre_script"], 4), g(ar["slope_B_pre_lib"], 4), abs(ar["slope_diff_B_pre"])))
    w("- B15.5: %d aciertos identificadores fuera de hashes y %d hashes de commit (conservados) en el alcance; la copia de prueba queda limpia: %s." % (
        sum(x["hits"] for c, x in b5["totals"].items() if c != "hash_de_commit"), b5["totals"]["hash_de_commit"]["hits"],
        yn(b5["trial_build"]["clean"])))
    w("")


def s_anom(w, L):
    w("## 7. Anomalías y contradicciones con el manuscrito")
    w("")
    t3 = J("t3")
    for r in t3["literals"]:
        if r.get("verdict") == "no coincide":
            w("- Parche T3, «%s» (%s): no coincide; valor %s, correcto «%s»." % (r["literal"], r["assignment"], r["value"], r["correct"]))
    p0 = J("p0")
    w("- Paso 0 con B = 399 (diagnóstico): el umbral de media |Δp| ≤ 0.02 no era alcanzable; dos réplicas exactas darían %s (SB) y %s "
      "(SWB), y lo observado fue %s y %s." % (
          g(p0["noise_benchmark"]["SB"]["expected_mean_abs_p_if_exact"]), g(p0["noise_benchmark"]["SWB"]["expected_mean_abs_p_if_exact"]),
          g(p0["noise_benchmark"]["SB"]["observed_mean_abs_p"]), g(p0["noise_benchmark"]["SWB"]["observed_mean_abs_p"])))
    p2 = J("p0v2")
    for cs, x in p2["size_paired"].items():
        for m, v in x.items():
            if cs == "c" and not v["bootur_in_region"]:
                w("- E3.2: el tamaño de bootUR (%s) en el caso constante es %s, fuera de [%s, %s]." % (
                    m, g(v["size_bootur"]), g(v["region"][0]), g(v["region"][1])))
    old = p0["size_replica"]["c"]["SB"]
    w("- El tamaño de la réplica del SB en el caso constante con B = 399 y la familia 154 (%s, fuera de la región) no se repite con B = 999 "
      "y la familia 159 (réplica %s, bootUR %s)." % (g(old["rate"]), g(p2["size_paired"]["c"]["SB"]["size_py"]), g(p2["size_paired"]["c"]["SB"]["size_bootur"])))
    b5 = J("b5")
    w("- B15.5: %s; el paquete `supplementary/` no corresponde al artículo actual y se rehará (bloque aparte)." % b5["supplementary_describes"])
    if C.have(F["v17"]) and "summary_rows" in J("v17"):
        r0 = J("v17")["summary_rows"][0]
        a15 = J("b3")["power"]["pw3_rho0p9_n200_c"]["rates"]["gls_t0"]
        if g(r0["power"], 3) != g(a15["rate"], 3):
            w("- Potencia ajustada de MSB-B con Andrews en ρ = 0.90, n = 200, caso constante: tab_summary da %s (A12, `%s`); tab:fixedb "
              "y el literal L17b dan %s (A15, `%s power.pw3_rho0p9_n200_c.rates.gls_t0`). Son caminos distintos, con N = %d y %d. Si "
              "ambas tablas quedan en el v17, la misma magnitud aparece con dos valores." % (
                  g(r0["power"], 3), r0["power_source"], g(a15["rate"], 3), F["b3"], r0["N_power"], a15["n"]))
    b2 = J("b2")["b"]["AR 0.5"]
    w("- B15.2: la pendiente 0.333 (retirada del manuscrito) usaba el ρ̂ del script, no el de la librería que implementa eq:hac; con el de la "
      "librería es %s." % g(b2["slope_B_pre_lib"], 4))
    w("")


def master(w, L):
    w("## Anexo: tabla maestra de los números nuevos")
    w("")
    rows = []
    d = J("b0")
    for p in d["procs"]:
        for c in ("c", "ct", "both"):
            for blk in ("iid", "asy"):
                for s in ("mean", "max"):
                    rows.append(["B15.0 %s %s %s %s |tasa−0.05|" % (LAB[p], CASE[c], blk, s), g(d["b_abs_dev"][p][c][blk][s]), "—",
                                 "20000", "—", "130 (A12)", F["b0"], "b_abs_dev.%s.%s.%s.%s" % (p, c, blk, s)])
    for key, r in J("b0b")["cells"].items():
        for p, x in r["procs"].items():
            for lab, v in x["by_k"].items():
                for blk in ("iid", "asy"):
                    if v[blk]["rate"] is not None:
                        rows.append(["B15.0b %s %s k=%s %s" % (key, LAB[p], lab, blk), g(v[blk]["rate"]),
                                     "[%s, %s]" % (g(v[blk]["wilson_lower"]), g(v[blk]["wilson_upper"])), v["paths"], "—", "130 (A12)",
                                     F["b0b"], "cells.%s.procs.%s.by_k.%s.%s" % (key, p, lab, blk)])
    for lab, r in J("b2")["b"].items():
        for q in ("B_pre_script", "B_pre_lib"):
            rows.append(["B15.2 %s pendiente %s" % (lab, q), g(r["slope_" + q], 6), "R² %s" % g(r["R2_" + q], 4), "500 por n", "—",
                         "semilla 42", F["b2"], "b.%s.slope_%s" % (lab, q)])
    p2 = J("p0v2")
    for cs, x in p2["size_paired"].items():
        for m, v in x.items():
            rows.append(["Paso 0 E3.2 tamaño bootUR %s %s" % (m, cs), g(v["size_bootur"]), "[%s, %s]" % (g(v["bootur_wilson"][0]), g(v["bootur_wilson"][1])),
                         v["n"], "B = %d" % p2["config"]["B"], "159", F["p0v2"], "size_paired.%s.%s.size_bootur" % (cs, m)])
    b3 = J("b3")
    for k, v in b3["size"].items():
        for c, r in v["rates"].items():
            rows.append(["B15.3 tamaño %s %s" % (k, c), g(r["rate"]), "[%s, %s]" % (g(r["wilson_lower"]), g(r["wilson_upper"])), r["n"],
                         b3["config"]["N_cal"], "156 / 155", F["b3"], "size.%s.rates.%s" % (k, c)])
    for k, v in b3["power"].items():
        for c, r in v["rates"].items():
            rows.append(["B15.3 potencia %s %s" % (k, c), g(r["rate"]), "[%s, %s]" % (g(r["wilson_lower"]), g(r["wilson_upper"])), r["n"],
                         b3["config"]["N_cal"], "157 / 155", F["b3"], "power.%s.rates.%s" % (k, c)])
    if C.have(F["b1"]):
        b1 = J("b1")
        for k, v in b1["size"].items():
            for a, r in v["rates"].items():
                rows.append(["B15.1 tamaño %s %s" % (k, a), g(r["rate"]), "[%s, %s]" % (g(r["wilson_lower"]), g(r["wilson_upper"])), r["n"],
                             "R = %d" % b1["config"]["R"], "152", F["b1"], "size.%s.rates.%s" % (k, a)])
        for k, v in b1["power"].items():
            for a, r in v["adjusted"].items():
                rows.append(["B15.1 potencia ajustada %s %s" % (k, a), g(r["rate"]), "[%s, %s]" % (g(r["wilson_lower"]), g(r["wilson_upper"])),
                             r["n"], "R = %d" % b1["config"]["R"], "153", F["b1"], "power.%s.adjusted.%s" % (k, a)])
    if C.have(F["v17"]) and "summary_rows" in J("v17"):
        for i, r in enumerate(J("v17")["summary_rows"]):
            for q in ("D", "M", "min", "max"):
                rows.append(["B15.9 tab_summary %s %s %s" % (plain(r["label"]), plain(r["cv"]), q), g(r[q]), "—", r["N_size"], "—",
                             r["audit"], F["v17"], "summary_rows[%d].%s" % (i, q)])
    L.extend(table(["Clave", "Valor", "IC/EE", "N_sim", "N_cal", "Familia", "JSON", "Ruta"], rows))
    w("")


def main():
    L = []

    def w(s):
        L.append(s)
    final = C.have(F["b1"]) and C.have(F["b3"])
    w("# Auditoría A15 — %s" % ("reporte final" if final else "reporte parcial"))
    w("")
    w("Enmiendas 1–5 y predicción commiteadas (§3). B15.4 espera al v17. No se editó ningún `.tex` ni `src/`.")
    w("")
    w("## 1. Resultados")
    w("")
    s_b0(w, L)
    s_b0b(w, L)
    s_b2(w, L)
    s_b5(w, L)
    s_inv(w, L)
    s_b1p0(w, L)
    s_b1p0v2(w, L)
    s_b3p0(w, L)
    s_probe(w, L)
    if C.have(F["v17"]) and C.have(F["lit"]):
        s_b156(w, L)
    if C.have(F["supp"]):
        s_b157(w, L)
    if C.have(F["mnt"]):
        s_b158(w, L)
    if C.have(F["fix"]):
        s_b157b(w, L)
    if C.have(F["plan"]) and C.have(F["tpl"]):
        s_b159(w, L)
    if C.have(F["b3"]):
        s_b3(w, L)
    if C.have(F["b1"]):
        s_b1(w, L)
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
