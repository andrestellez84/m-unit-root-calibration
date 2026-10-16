"""
Auditoria A7 - genera experiments/enmienda2_dgp5_audit7.md (segunda enmienda).

Igual que la primera: ninguna cifra se escribe a mano. Salen de los JSON de
resultados y de las constantes de audit7_design.py y audit7_readout.py. Antes
de escribir comprueba en disco que no existe ningun checkpoint de DGP 5 en el
directorio del runner ni de la extension en el de la medicion del handicap; si
existe alguno, falla.

Uso: python experiments/audit7_write_amendment2.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                  # noqa: E402
import audit7_design as D                                  # noqa: E402
import audit7_dgp5_runner as RUN                           # noqa: E402
import audit7_readout as RO                                # noqa: E402

OUT = os.path.join(C.HERE, "enmienda2_dgp5_audit7.md")
PREREG_COMMIT = "62216ee3f51f800bbf643a43cf7343d46952a18d"
FIRST_AMENDMENT = "experiments/enmienda_dgp5_audit7.md"
HANDICAP_CKPT = os.path.join(C.CKPT_ROOT, "audit7_kappa2_handicap")
SOURCES = ("kappa2_handicap_audit7.json", "block1_budget_audit7.json",
           "bootstrap_cost_diagnostic_audit7.json")


def load(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8") as f:
        return json.load(f)


def git_one(*args):
    out = C._git(*args).splitlines()
    if not out:
        raise SystemExit("git no devolvio nada para %s" % (args,))
    return out


def mult(r):
    """Factor de varianza r^2 sin ceros de relleno: 4, 9, 1.21, 1.56."""
    return ("%.2f" % (r * r)).rstrip("0").rstrip(".")


def scan_checkpoints():
    runner = sorted(f for f in os.listdir(RUN.CKPT) if f.startswith("dgp5_")) \
        if os.path.isdir(RUN.CKPT) else []
    weak = {"k2h_%s_n%d_rho%.2f_r%s_i" % (k, n, rho, D.fmt_r(r))
            for k in ("ar", "rw") for (n, rho, r) in D.dgp5_cells_weak()}
    handicap = sorted(f for f in os.listdir(HANDICAP_CKPT) if any(f.startswith(t) for t in weak)) \
        if os.path.isdir(HANDICAP_CKPT) else []
    return runner, handicap


def main():
    runner_hits, handicap_hits = scan_checkpoints()
    if runner_hits or handicap_hits:
        raise SystemExit("ya hay computo sobre DGP 5 o sobre la extension: %s %s"
                         % (runner_hits[:5], handicap_hits[:5]))
    handicap, budget, diag = (load(s) for s in SOURCES)
    prov = C.provenance(dgp="amendment2", n_sim=None, seed_formula=None)
    first_commit = git_one("log", "--diff-filter=A", "--format=%H", "--", FIRST_AMENDMENT)[-1]
    handicap_commit = git_one("log", "-1", "--format=%H", "--",
                              "experiments/results/kappa2_handicap_audit7.json")[0]

    reg_ratios = [r for r in D.DGP5_RATIOS if r > 1.0]
    weak = list(D.DGP5_RATIOS_WEAK)
    weak_cells = D.dgp5_cells_weak()
    idx = [D.dgp5_cells().index(c) for c in weak_cells]
    hc = [v for v in handicap["cells"].values()
          if v["n"] in D.CAL_N_ACTIVE and not D.is_weak(v["r"])]
    ar = [v["power_ar_break"]["rate"] for v in hc]
    rw = [v["power_rw_break"]["rate"] for v in hc]
    ar_int = [v["power_ar_break"]["rate"] for v in hc if v["interior_prediction_1"]]
    declared_any = [n for n, d in handicap["declared_by_n"].items() if d["handicap_declared"]]
    confirm_sec = budget["subtotals_sec"]["dgp5_n1000"]
    cal1000_sec = budget["per_n"]["1000"]["calibration_cell_sec"]
    cmp1000 = diag["comparison_sec_per_series"]["1000"]
    resume = ('python experiments/audit7_dgp5_runner.py --cells "adaptnull:n=1000;cal:n=1000;dgp5:confirm" '
              '--cores <nucleos> --B %d --n-sim-dgp5 %d --n-cal %d --max-seconds %.0f'
              % (D.DGP5_B, D.DGP5_N_SIM, D.N_CAL, C.DEFAULT_MAX_SECONDS))

    L = []
    w = L.append
    w("# Segunda enmienda al pre-registro — DGP 5 (desviación mixta)")
    w("")
    w("- Fecha de generación (UTC): %s" % prov["generated_utc"])
    w("- Predicción registrada: commit `%s`." % PREREG_COMMIT)
    w("- Primera enmienda (`%s`): commit `%s`." % (FIRST_AMENDMENT, first_commit))
    w("- Generada por `experiments/audit7_write_amendment2.py` en el commit `%s`." % prov["commit"])
    w("- Precede a cualquier cómputo del test propuesto, del bootstrap DF-GLS y de ADF, PP y DF-GLS "
      "asintóticos sobre las series de DGP 5, y a cualquier cómputo sobre las series de la extensión. "
      "Comprobado en disco al generar: %d checkpoints de DGP 5 en el directorio del runner y %d de la "
      "extensión en el de la medición del handicap. Sobre las series de la rejilla registrada sólo se "
      "ha calculado κ₂, en la medición prevista en la sección 6 de la primera enmienda."
      % (len(runner_hits), len(handicap_hits)))
    w("")
    w("**El texto de las predicciones 1, 2 y 3 y el de la condición de falsación no se modifican.** "
      "Esta enmienda añade celdas a la rejilla, retira las de n = 1000 y registra cómo se leen las "
      "celdas añadidas y qué veredicto gobierna la consecuencia registrada.")
    w("")

    w("## 1. Motivo de la extensión")
    w("")
    w("Los quiebres de la rejilla registrada, r ∈ {%s}, multiplican la varianza de las innovaciones "
      "por %s. En datos financieros diarios, desplazamientos de esa magnitud corresponden a episodios "
      "de crisis. Los quiebres r ∈ {%s} la multiplican por %s, el rango de los desplazamientos "
      "rutinarios de régimen de volatilidad. La rejilla registrada cubría lo extremo y omitía lo común."
      % (", ".join("%g" % r for r in reg_ratios), ", ".join("×" + mult(r) for r in reg_ratios),
         ", ".join("%g" % r for r in weak), ", ".join("×" + mult(r) for r in weak)))
    w("")

    w("## 2. Conocimiento disponible al fijar la extensión")
    w("")
    w("Se declara para que el lector juzgue la secuencia.")
    w("")
    w("- **Medición del handicap de κ₂** (`kappa2_handicap_audit7.json`, commit `%s`): %s. "
      "En las celdas con r ∈ {%s} y n ∈ {%s}, la potencia de κ₂ al valor crítico "
      "simulado del 5%% está entre %.4f y %.4f bajo el AR y entre %.4f y %.4f bajo el paseo aleatorio "
      "con el mismo quiebre; su mínimo en el interior registrado de la predicción 1 es %.4f."
      % (handicap_commit,
         ("handicap declarado en n = " + ", ".join(declared_any)) if declared_any
         else "handicap no declarado en ningún n",
         ", ".join("%g" % r for r in reg_ratios), ", ".join(str(n) for n in D.CAL_N_ACTIVE),
         min(ar), max(ar), min(rw), max(rw), min(ar_int)))
    w("- Consecuencia que ya se conocía: en el interior registrado cabe esperar que la unión calibrada "
      "conjuntamente rechace casi siempre por su componente κ₂, de modo que un empate o una derrota del "
      "test propuesto ahí puede reflejar el techo de la unión y no el coste de multiplicidad.")
    w("- Los valores r ∈ {%s} se fijaron sin calcular ningún procedimiento sobre series con esos "
      "quiebres (comprobación en disco del encabezado). No se midió de antemano la potencia de κ₂ ni "
      "la de ningún otro procedimiento en ellos." % ", ".join("%g" % r for r in weak))
    w("- Lo que ya se sabía de DGP 3 (sección 3 de la primera enmienda) sigue vigente. Expectativa "
      "declarada, no predicción: en quiebres débiles el canal de varianza pesa menos que en los "
      "fuertes, de modo que la extensión hace menos probable que la cuota de g₂ sea sustancial.")
    w("")

    w("## 3. Celdas añadidas")
    w("")
    w("- ρ ∈ {%s} × r ∈ {%s} × n ∈ {%s}: %d celdas, %d réplicas por celda, B = %d, el mismo "
      "generador de DGP 5." % (", ".join("%.2f" % x for x in D.DGP5_RHOS),
                               ", ".join("%g" % r for r in weak),
                               ", ".join(str(n) for n in D.DGP5_N_MAIN), len(weak_cells),
                               D.DGP5_N_SIM, D.DGP5_B))
    w("- Semillas: familia %d, índices de celda %d a %d, a continuación de las %d celdas de la "
      "especificación revisada; ninguna celda registrada cambia de semilla. La disjunción, incluida "
      "la de las semillas de R del bootstrap, se verifica en el Paso 0 del Bloque 1."
      % (D.FAM_DGP5, min(idx), max(idx), len(D.dgp5_cells_registered())))
    w("- La calibración bajo la nula compuesta es la misma (paseo aleatorio homoscedástico, %d "
      "réplicas por n): mismos umbrales a tamaño igualado y mismo α\\* de la unión." % D.N_CAL)
    w("- El handicap de κ₂ por persistencia se mide en la extensión con el mismo script y el mismo "
      "criterio (sección 6 de la primera enmienda), después del commit de esta enmienda y antes del "
      "análisis. Se declara por n sobre la extensión de la predicción 1 y va a la tabla como advertencia.")
    w("")

    w("## 4. Retirada de n = 1000")
    w("")
    w("- Se retiran las celdas de confirmación %s y, con ellas, la calibración y la nula nominal del "
      "test adaptativo a n = 1000, que sólo servían a esas celdas." % [list(c) for c in D.DGP5_CONFIRM])
    w("- Motivo: confirman en vez de discriminar, y su costo no se puede presupuestar con fiabilidad. "
      "El presupuesto por sondas (`block1_budget_audit7.json`) proyectó %.1f h para las tres celdas y "
      "%.1f h para la calibración de n = 1000, pero el mismo lote no reproduce su tiempo "
      "(`bootstrap_cost_diagnostic_audit7.json`: a n = 1000, %.3f s/serie sin pool frente a %.3f en "
      "la sonda del presupuesto)." % (confirm_sec / 3600, cal1000_sec / 3600, cmp1000["clean"],
                                      cmp1000["budget_probe"]))
    w("- Pasan a «No ejecutado» con este comando de reanudación:")
    w("")
    w("      %s" % resume)
    w("")
    w("- Consecuencia sobre la sección 6 de la primera enmienda: si el handicap se declarara a "
      "n = 200, la lectura limpia descansa sólo en n = 500.")
    w("")

    w("## 5. Veredicto que gobierna la consecuencia y lectura de la extensión")
    w("")
    w("- **Resultado primario: el veredicto literal.** La condición de falsación registrada se evalúa "
      "literalmente sobre el interior registrado %s, por versión del test propuesto y por n. **Ese "
      "veredicto gobierna la consecuencia registrada** y se reporta como resultado primario."
      % sorted([list(x) for x in RO.INTERIOR_P1]))
    w("- **Diagnóstico, declarado antes de los datos.** El veredicto literal se evalúa en condiciones "
      "en que κ₂ tiene potencia ≥ %.4f en el interior registrado (sección 2). Esa cifra procede de la "
      "medición del handicap, prevista en la sección 6 de la primera enmienda y ejecutada antes de "
      "cualquier cómputo del test propuesto o del bootstrap sobre DGP 5. En esas condiciones la unión "
      "calibrada conjuntamente puede rechazar casi siempre por κ₂, y el veredicto literal **no es "
      "informativo sobre la hipótesis**. Si se dispara, se reporta que la condición de falsación "
      "registrada se cumplió y, junto a ello, que el diseño no podía discriminar, con la potencia de "
      "κ₂ de la medición del handicap y la potencia a tamaño igualado de la unión, de κ₂ y del "
      "bootstrap DF-GLS en esas celdas de DGP 5." % min(ar_int))
    w("- **Contraste post-registro: la extensión.** (ρ, r) ∈ %s, etiquetado como post-registro en "
      "toda tabla y todo texto. Usa la misma regla por celda (McNemar exacto pareado, a tamaño "
      "igualado, frente a la unión calibrada conjuntamente), por versión y por n, el mismo "
      "desdoblamiento por la cuota de energía de g₂ (sección 4 de la primera enmienda) y la "
      "advertencia del handicap de κ₂ medida sobre la extensión. Tiene veredicto propio y **no anula "
      "ni sustituye al veredicto registrado**." % sorted([list(x) for x in RO.EXTENSION_P1]))
    w("- La decisión de extender se tomó después de conocer la saturación de κ₂ (sección 2). Por eso "
      "la extensión no puede gobernar la consecuencia, aunque sus valores de r se fijaran sin mirar "
      "ningún procedimiento sobre ellos.")
    w("- Las celdas de la extensión con ρ = %.2f se reportan con las mismas columnas y no entran en "
      "ninguna predicción." % min(D.DGP5_RHOS))
    w("- Las predicciones 2 y 3 se evalúan sin cambios, a n ∈ {%s}." % ", ".join(str(n) for n in D.CAL_N_ACTIVE))
    w("")

    w("## 6. Procedencia de las cifras")
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
