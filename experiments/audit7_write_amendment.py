"""
Auditoria A7 - genera experiments/enmienda_dgp5_audit7.md.

Ninguna cifra de la enmienda se escribe a mano: todas se leen de los JSON de
resultados del Bloque 1a y del reencuadre de DGP 3, y las reglas de lectura
se importan de audit7_readout.py, que es el mismo modulo que usaran la
medicion del handicap, el runner de DGP 5 y el reporte. Si falta una clave,
el script falla. Las afirmaciones sobre los datos se cuentan en el JSON, no
se suponen.

Uso: python experiments/audit7_write_amendment.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                  # noqa: E402
import audit7_design as D                                  # noqa: E402
import audit7_dgp5_runner as RUN                           # noqa: E402
import audit7_readout as RO                                # noqa: E402

OUT = os.path.join(C.HERE, "enmienda_dgp5_audit7.md")
PREREG_COMMIT = "62216ee3f51f800bbf643a43cf7343d46952a18d"
SOURCES = ("kappa2_validation_audit7.json", "kappa2_diagnosis_audit7.json",
           "kappa2_simcv_audit7.json", "dgp3_recast_composite_null_audit7.json")


def load(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8") as f:
        return json.load(f)


def pct(x, d=2):
    return ("%." + str(d) + "f%%") % (100.0 * x)


def main():
    val, diag, simcv, recast = (load(s) for s in SOURCES)
    prov = C.provenance(dgp="amendment", n_sim=None, seed_formula=None)
    L = []
    w = L.append

    w("# Enmienda al pre-registro — DGP 5 (desviación mixta)")
    w("")
    w("- Fecha de generación (UTC): %s" % prov["generated_utc"])
    w("- Predicción registrada que se enmienda: commit `%s`." % PREREG_COMMIT)
    w("- Generada por `experiments/audit7_write_amendment.py` en el commit `%s`." % prov["commit"])
    w("- Precede a cualquier cómputo sobre las series de DGP 5.")
    w("")
    w("**Las predicciones 1, 2 y 3 no se modifican.** Esta enmienda registra el motivo de las "
      "decisiones de diseño tomadas después del Bloque 1a, lo que ya se sabía antes de correr "
      "DGP 5, y las reglas con las que se leerá el resultado.")
    w("")

    # ---- 1. motivo --------------------------------------------------------
    g = val["gate"]
    w("## 1. Motivo: la compuerta nominal de κ₂ falló")
    w("")
    w("Validación de κ₂ al valor crítico asintótico 1.358 sobre dos nulas sin quiebre de "
      "varianza, %d réplicas, región exigida [%.4f, %.4f]:" % (
          val["provenance"]["n_sim"], g["region"][0], g["region"][1]))
    w("")
    w("| Nula | n | Tamaño al 5% | IC 95% |")
    w("|---|---|---|---|")
    for tag, c in val["cells"].items():
        lv = c["levels"]["0.05"]
        w("| %s | %d | %.4f | [%.4f, %.4f] |" % (c["null"], c["n"], lv["rate"],
                                                 lv["ci_lower"], lv["ci_upper"]))
    w("")
    w("Veredicto: %s, %d de %d celdas fuera de la región." % (
        g["verdict"], len(g["failed_cells"]), len(val["cells"])))
    w("")
    dc = diag["cells"]
    w("Diagnóstico por descomposición (`kappa2_diagnosis_audit7.json`, %d réplicas por celda). "
      "El supremo discreto de un puente de sumas parciales con varianza conocida rechaza %.4f a "
      "T=200 y %.4f a T=5000; κ₂ completo sobre ruido iid, %.4f a T=200 y %.4f a T=5000. El "
      "valor crítico asintótico es conservador a muestra finita, y la tasa converge hacia 0.05 "
      "al crecer T. Tres cálculos independientes de κ₂ a T=200 coinciden. **La caída adicional "
      "bajo AR(0.93) a n=200 no está diagnosticada** y no se le atribuye causa." % (
          dc["V1_normal_known_var_T200"]["reps"],
          dc["V1_normal_known_var_T200"]["rates"]["0.05"],
          dc["V1_normal_known_var_T5000"]["rates"]["0.05"],
          dc["V4_kappa2_full_T200"]["rates"]["0.05"],
          dc["V4_kappa2_full_T5000"]["rates"]["0.05"]))
    w("")

    # ---- 2. decisiones de diseno -----------------------------------------
    w("## 2. Decisiones de diseño tomadas antes del cómputo")
    w("")
    w("**2.1 Nula compuesta y tamaño igualado.** H₀ para todo el Bloque 1 es raíz unitaria *y* "
      "homoscedasticidad (Ec. 3 del manuscrito: innovaciones iid). Cada procedimiento se "
      "calibra sobre %d réplicas de un paseo aleatorio gaussiano homoscedástico, una "
      "calibración por n ∈ %s. Toda la rejilla de DGP 5 es potencia." % (
          D.N_CAL, list(D.CAL_N_GRID)))
    w("")
    w("- **Umbral a tamaño igualado:** el cuantil empírico al 5% de la cola de rechazo de cada "
      "procedimiento sobre ese conjunto de calibración (cola inferior del estadístico propuesto "
      "y de los p-valores; cola superior de κ₂).")
    w("- **Empates:** los p-valores del bootstrap con B = %d están en una rejilla discreta. Para "
      "que el tamaño igualado sea exacto se desempatan con una uniforme por serie, de un flujo "
      "de semillas propio (familia %d), fijo e independiente de los datos." % (
          D.DGP5_B, RUN.FAM_TIEBREAK))
    w("- **Versiones nominales**, reportadas junto a las de tamaño igualado: cada procedimiento "
      "a su propia regla del 5%%. El test con R = 0.50 usa la nula de `power_comparison.py` "
      "(%d réplicas, semilla %d); el test con R̂ usa la nula de A5 (%d paseos aleatorios, "
      "semillas %d + i, σ HAC)." % (RUN.N_CAL_R050, RUN.CAL_SEED_R050, RUN.ADAPT_NULL_N,
                                     RUN.ADAPT_NULL_SEED))
    w("")
    w("**2.2 κ₂ con valor crítico simulado.** Se aplica al comparador la misma metodología que "
      "la Definición 1 aplica al estadístico propuesto:")
    w("")
    w("| n | VC simulado | Tamaño en muestra | AR(0.93) fuera de muestra | IC 95% | ¿En región? | RW independiente |")
    w("|---|---|---|---|---|---|---|")
    for n, c in simcv["cells"].items():
        ar = c["out_of_sample_ar093_at_simulated_cv"]
        w("| %s | %.4f | %.4f | %.4f | [%.4f, %.4f] | %s | %.4f |" % (
            n, c["simulated_critical_values"]["0.05"],
            c["in_sample_size_at_simulated_cv"]["rate"], ar["rate"],
            ar["ci_lower"], ar["ci_upper"], "sí" if ar["in_gate_region"] else "**no**",
            c["out_of_sample_rw_family91_at_simulated_cv"]["rate"]))
    w("")
    w("Bajo la nula compuesta el AR(0.93) homoscedástico es una alternativa, no H₀: el tamaño "
      "de la unión es exacto por construcción sobre el paseo aleatorio y el desvío a n=200 no "
      "toca la validez del experimento. κ₂ se mantiene en toda la rejilla. El riesgo de que la "
      "persistencia deprima su **potencia** se mide antes de DGP 5 (sección 6).")
    w("")
    w("**2.3 Unión calibrada conjuntamente.** Competidor principal: el nivel común α\\* que da "
      "P(bootstrap DF-GLS rechaza a α\\* **o** κ₂ rechaza a α\\*) = 0.05 sobre el conjunto de "
      "calibración, hallado por bisección. La unión Bonferroni, con cada componente a α/2 sobre "
      "su propia ley nula calibrada, se reporta como columna secundaria con su tamaño empírico "
      "real. El coste de multiplicidad no está en el tamaño, que se calibra, sino en la "
      "potencia: una unión combina dos estadísticos por un máximo.")
    w("")
    w("**2.4 Rejilla y semillas.** ρ ∈ %s; r ∈ %s (r = 1.5 eliminado); n ∈ %s, más las celdas "
      "de confirmación n=1000 %s; %d réplicas por celda; B = %d en toda la rejilla "
      "(0.05·(%d+1) es entero y el error Monte Carlo de la tasa lo domina el número de "
      "réplicas). Semillas `familia·10⁸ + celda·10⁵`, sin solape entre celdas." % (
          list(D.DGP5_RHOS), list(D.DGP5_RATIOS), list(D.DGP5_N_MAIN),
          [list(c) for c in D.DGP5_CONFIRM], D.DGP5_N_SIM, D.DGP5_B, D.DGP5_B))
    w("")

    # ---- 3. anadido 1: DGP 3 ----------------------------------------------
    cd = recast["component_diagnostics_section_5_5"]
    dcells = cd["cells"]
    r_gt_1 = [v for k, v in dcells.items() if not k.endswith("_r1.0")]
    g1_down = sum(1 for v in r_gt_1 if v["change_in_E_g1_sq_vs_r1"] < 0)
    cells = recast["cells"]
    power_cells = [c for c in cells.values() if c["role_under_composite_null"] == "power"]
    dfgls_wins = sum(1 for c in power_cells
                     if c["dfgls_asymptotic"]["rate"] > c["proposed_R050_alpha1"]["rate"])
    w("## 3. Añadido 1 — lo que ya se sabía de DGP 3 antes de correr DGP 5")
    w("")
    w("Del reencuadre de DGP 3 bajo la nula compuesta (`dgp3_recast_composite_null_audit7.json`):")
    w("")
    w("- La elevación del rechazo del test propuesto viaja por el **canal de media** en %s "
      "celdas con r > 1: el cambio de E[g1_std]² respecto de r = 1 supera en magnitud al de "
      "E[g2_std]². E[g1_std] es menor que a r = 1 en %d de %d de esas celdas." % (
          cd["cells_r_gt_1_where_mean_dominates"], g1_down, len(r_gt_1)))
    w("- La cuota de g₂ en el estadístico con R = 0.50 no supera **%s** en ninguna celda."
      % pct(cd["max_share_of_g2_in_R050_statistic"]))
    w("- DF-GLS asintótico rechaza más que el test propuesto en %d de %d celdas con r > 1." % (
        dfgls_wins, len(power_cells)))
    w("")
    w("En consecuencia el reencuadre de DGP 3 no respalda la arquitectura dual y la expectativa "
      "sobre la predicción 1 es baja.")
    w("")

    # ---- 4. anadido 2: cuota de energia ----------------------------------
    w("## 4. Añadido 2 — cuota de energía de g₂ y desdoblamiento de la predicción 1")
    w("")
    w("En cada serie de cada celda de DGP 5 se registra, para R = 0.50 y para R̂:")
    w("")
    w("    cuota_g2 = R^2 · g2_std^2 / ( (1-R)^2 · g1_std^2 + R^2 · g2_std^2 )")
    w("")
    w("con θ = (0.1, 0.1) y piloto α(1). g1_std y g2_std se calculan por el mismo camino que "
      "las columnas publicadas (`run_experiment_cell` de `power_comparison.py`); su "
      "equivalencia con `compute_statistic`, que usó A5 para el test adaptativo, se verifica "
      "en el Paso 0 del Bloque 1. R̂ = g2_std² / (g1_std² + g2_std²). La celda se resume por la "
      "mediana sobre sus series.")
    w("")
    w("Hecho algebraico registrado antes de los datos: con R = 0.50 la cuota es "
      "g2²/(g1²+g2²), numéricamente igual a R̂; con R̂ la cuota es g2⁶/(g1⁶+g2⁶). El peso "
      "adaptativo amplifica al canal que ya domina: sólo da a g₂ más peso que R = 0.50 en las "
      "series donde g2_std > g1_std.")
    w("")
    w("Lectura de la predicción 1 en las celdas donde el test propuesto gana:")
    w("")
    w("| Mediana de la cuota de g₂ | Lectura |")
    w("|---|---|")
    w("| < %s | La victoria es de la agregación cuadrática de un canal de media dominante frente a una unión, no del segundo canal. Resultado publicable, pero el argumento pasa a ser sobre cómo combinar, no sobre qué medir. |" % pct(RO.SHARE_LOW, 0))
    w("| ≥ %s | Evidencia de la arquitectura dual. |" % pct(RO.SHARE_HIGH, 0))
    w("| entre ambos | Indeterminado; se reporta como tal. |")
    w("")

    # ---- 5. reglas operativas --------------------------------------------
    w("## 5. Reglas operativas de lectura (aclaración, no modificación)")
    w("")
    w("- **Quién gana en una celda:** contraste pareado sobre las mismas series con los rechazos "
      "a tamaño igualado; McNemar exacto sobre los pares discordantes. Si p < %.2f gana el de "
      "más rechazos; si no, empate." % RO.WIN_ALPHA)
    w("- **Versiones del test propuesto:** R = 0.50 y R̂ se evalúan por separado; la predicción "
      "registrada no distingue entre ellas.")
    w("- **Interior de la predicción 1:** (ρ, r) ∈ %s. La condición de falsación se evalúa por "
      "versión: si ninguna celda del interior es victoria del test propuesto frente a la unión "
      "calibrada conjuntamente, la predicción 1 falla para esa versión." % sorted(
          [list(x) for x in RO.INTERIOR_P1]))
    w("- **Predicción 2:** celdas r = %.1f, bootstrap DF-GLS solo contra el test propuesto. "
      "**Predicción 3:** celda (ρ, r) = %s, κ₂ solo contra el test propuesto." % (
          RO.EXTREME_MEAN_P2_R, list(RO.EXTREME_VARIANCE_P3)))
    w("- Las cifras por n se reportan por separado; ninguna se agrega entre n.")
    w("")

    # ---- 6. handicap -----------------------------------------------------
    w("## 6. Handicap de κ₂ por persistencia — medición previa a DGP 5")
    w("")
    w("Si la persistencia deprime la potencia de κ₂, la unión tendría un handicap justo en el "
      "interior de la predicción 1 y el test propuesto podría ganar por un artefacto del "
      "comparador. Se mide antes de DGP 5 (`experiments/audit7_kappa2_handicap.py`):")
    w("")
    w("- Para cada celda (n, ρ, r) con r > 1 se compara la potencia de κ₂ al valor crítico "
      "simulado bajo el AR(ρ) con quiebre r (la celda de DGP 5) y bajo el paseo aleatorio con "
      "el mismo quiebre (DGP 3), **con la misma semilla**: las innovaciones son idénticas y sólo "
      "cambia ρ. Contraste pareado.")
    w("- Alcance: n = 200 con ρ ∈ %s y r ∈ {2, 3, 4}; como extensión, la misma rejilla a "
      "n = 500 y las celdas de confirmación a n = 1000." % list(D.DGP5_RHOS))
    w("- **Handicap en una celda:** McNemar exacto p < %.2f con la potencia bajo paseo "
      "aleatorio por encima, y déficit relativo ≥ %s. **Declarado para un n** si ocurre en al "
      "menos una celda del interior de la predicción 1." % (
          RO.HANDICAP_ALPHA, pct(RO.HANDICAP_REL_SHORTFALL_MIN, 0)))
    w("- **Consecuencia registrada:** si el handicap se declara a n = 200, la predicción 1 a "
      "n = 200 no es un contraste limpio y la lectura honesta descansa en n = 500 y n = 1000. "
      "Si también se declara a n = 500, se dice así y la lectura limpia se restringe a los n "
      "donde no se declara. El resultado va a la tabla como advertencia, gane o pierda.")
    w("")

    # ---- 7. procedencia ---------------------------------------------------
    w("## 7. Procedencia de las cifras")
    w("")
    w("| Fuente | sha256 |")
    w("|---|---|")
    for s in SOURCES:
        w("| `experiments/results/%s` | `%s` |" % (s, C._sha256_file(os.path.join(C.RESULTS, s))))
    w("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("escrito %s (%d lineas)" % (OUT, len(L)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
