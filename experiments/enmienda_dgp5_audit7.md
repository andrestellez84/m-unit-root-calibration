# Enmienda al pre-registro — DGP 5 (desviación mixta)

- Fecha de generación (UTC): 2026-09-13T19:54:34.611787+00:00
- Predicción registrada que se enmienda: commit `62216ee3f51f800bbf643a43cf7343d46952a18d`.
- Generada por `experiments/audit7_write_amendment.py` en el commit `b99e6ce4a3d58225a1868ca8cca157671f508063`.
- Precede a cualquier cómputo sobre las series de DGP 5.

**Las predicciones 1, 2 y 3 no se modifican.** Esta enmienda registra el motivo de las decisiones de diseño tomadas después del Bloque 1a, lo que ya se sabía antes de correr DGP 5, y las reglas con las que se leerá el resultado.

## 1. Motivo: la compuerta nominal de κ₂ falló

Validación de κ₂ al valor crítico asintótico 1.358 sobre dos nulas sin quiebre de varianza, 5000 réplicas, región exigida [0.0440, 0.0562]:

| Nula | n | Tamaño al 5% | IC 95% |
|---|---|---|---|
| rw | 200 | 0.0310 | [0.0264, 0.0362] |
| rw | 500 | 0.0382 | [0.0331, 0.0439] |
| rw | 1000 | 0.0422 | [0.0368, 0.0481] |
| ar093 | 200 | 0.0210 | [0.0172, 0.0254] |
| ar093 | 500 | 0.0392 | [0.0340, 0.0450] |
| ar093 | 1000 | 0.0430 | [0.0375, 0.0490] |

Veredicto: FALLA, 6 de 6 celdas fuera de la región.

Diagnóstico por descomposición (`kappa2_diagnosis_audit7.json`, 20000 réplicas por celda). El supremo discreto de un puente de sumas parciales con varianza conocida rechaza 0.0401 a T=200 y 0.0478 a T=5000; κ₂ completo sobre ruido iid, 0.0305 a T=200 y 0.0473 a T=5000. El valor crítico asintótico es conservador a muestra finita, y la tasa converge hacia 0.05 al crecer T. Tres cálculos independientes de κ₂ a T=200 coinciden. **La caída adicional bajo AR(0.93) a n=200 no está diagnosticada** y no se le atribuye causa.

## 2. Decisiones de diseño tomadas antes del cómputo

**2.1 Nula compuesta y tamaño igualado.** H₀ para todo el Bloque 1 es raíz unitaria *y* homoscedasticidad (Ec. 3 del manuscrito: innovaciones iid). Cada procedimiento se calibra sobre 5000 réplicas de un paseo aleatorio gaussiano homoscedástico, una calibración por n ∈ [200, 500, 1000]. Toda la rejilla de DGP 5 es potencia.

- **Umbral a tamaño igualado:** el cuantil empírico al 5% de la cola de rechazo de cada procedimiento sobre ese conjunto de calibración (cola inferior del estadístico propuesto y de los p-valores; cola superior de κ₂).
- **Empates:** los p-valores del bootstrap con B = 399 están en una rejilla discreta. Para que el tamaño igualado sea exacto se desempatan con una uniforme por serie, de un flujo de semillas propio (familia 69), fijo e independiente de los datos.
- **Versiones nominales**, reportadas junto a las de tamaño igualado: cada procedimiento a su propia regla del 5%. El test con R = 0.50 usa la nula de `power_comparison.py` (50000 réplicas, semilla 42); el test con R̂ usa la nula de A5 (50000 paseos aleatorios, semillas 42 + i, σ HAC).

**2.2 κ₂ con valor crítico simulado.** Se aplica al comparador la misma metodología que la Definición 1 aplica al estadístico propuesto:

| n | VC simulado | Tamaño en muestra | AR(0.93) fuera de muestra | IC 95% | ¿En región? | RW independiente |
|---|---|---|---|---|---|---|
| 200 | 1.2842 | 0.0500 | 0.0416 | [0.0362, 0.0475] | **no** | 0.0488 |
| 500 | 1.3090 | 0.0500 | 0.0512 | [0.0453, 0.0577] | sí | 0.0526 |
| 1000 | 1.3266 | 0.0500 | 0.0504 | [0.0445, 0.0568] | sí | 0.0526 |

Bajo la nula compuesta el AR(0.93) homoscedástico es una alternativa, no H₀: el tamaño de la unión es exacto por construcción sobre el paseo aleatorio y el desvío a n=200 no toca la validez del experimento. κ₂ se mantiene en toda la rejilla. El riesgo de que la persistencia deprima su **potencia** se mide antes de DGP 5 (sección 6).

**2.3 Unión calibrada conjuntamente.** Competidor principal: el nivel común α\* que da P(bootstrap DF-GLS rechaza a α\* **o** κ₂ rechaza a α\*) = 0.05 sobre el conjunto de calibración, hallado por bisección. La unión Bonferroni, con cada componente a α/2 sobre su propia ley nula calibrada, se reporta como columna secundaria con su tamaño empírico real. El coste de multiplicidad no está en el tamaño, que se calibra, sino en la potencia: una unión combina dos estadísticos por un máximo.

**2.4 Rejilla y semillas.** ρ ∈ [0.9, 0.93, 0.95]; r ∈ [1.0, 2.0, 3.0, 4.0] (r = 1.5 eliminado); n ∈ [200, 500], más las celdas de confirmación n=1000 [[1000, 0.93, 2.0], [1000, 0.93, 3.0], [1000, 0.95, 3.0]]; 2000 réplicas por celda; B = 399 en toda la rejilla (0.05·(399+1) es entero y el error Monte Carlo de la tasa lo domina el número de réplicas). Semillas `familia·10⁸ + celda·10⁵`, sin solape entre celdas.

## 3. Añadido 1 — lo que ya se sabía de DGP 3 antes de correr DGP 5

Del reencuadre de DGP 3 bajo la nula compuesta (`dgp3_recast_composite_null_audit7.json`):

- La elevación del rechazo del test propuesto viaja por el **canal de media** en 15 de 15 celdas con r > 1: el cambio de E[g1_std]² respecto de r = 1 supera en magnitud al de E[g2_std]². E[g1_std] es menor que a r = 1 en 15 de 15 de esas celdas.
- La cuota de g₂ en el estadístico con R = 0.50 no supera **0.47%** en ninguna celda.
- DF-GLS asintótico rechaza más que el test propuesto en 6 de 6 celdas con r > 1.

En consecuencia el reencuadre de DGP 3 no respalda la arquitectura dual y la expectativa sobre la predicción 1 es baja.

## 4. Añadido 2 — cuota de energía de g₂ y desdoblamiento de la predicción 1

En cada serie de cada celda de DGP 5 se registra, para R = 0.50 y para R̂:

    cuota_g2 = R^2 · g2_std^2 / ( (1-R)^2 · g1_std^2 + R^2 · g2_std^2 )

con θ = (0.1, 0.1) y piloto α(1). g1_std y g2_std se calculan por el mismo camino que las columnas publicadas (`run_experiment_cell` de `power_comparison.py`); su equivalencia con `compute_statistic`, que usó A5 para el test adaptativo, se verifica en el Paso 0 del Bloque 1. R̂ = g2_std² / (g1_std² + g2_std²). La celda se resume por la mediana sobre sus series.

Hecho algebraico registrado antes de los datos: con R = 0.50 la cuota es g2²/(g1²+g2²), numéricamente igual a R̂; con R̂ la cuota es g2⁶/(g1⁶+g2⁶). El peso adaptativo amplifica al canal que ya domina: sólo da a g₂ más peso que R = 0.50 en las series donde g2_std > g1_std.

Lectura de la predicción 1 en las celdas donde el test propuesto gana:

| Mediana de la cuota de g₂ | Lectura |
|---|---|
| < 1% | La victoria es de la agregación cuadrática de un canal de media dominante frente a una unión, no del segundo canal. Resultado publicable, pero el argumento pasa a ser sobre cómo combinar, no sobre qué medir. |
| ≥ 10% | Evidencia de la arquitectura dual. |
| entre ambos | Indeterminado; se reporta como tal. |

## 5. Reglas operativas de lectura (aclaración, no modificación)

- **Quién gana en una celda:** contraste pareado sobre las mismas series con los rechazos a tamaño igualado; McNemar exacto sobre los pares discordantes. Si p < 0.05 gana el de más rechazos; si no, empate.
- **Versiones del test propuesto:** R = 0.50 y R̂ se evalúan por separado; la predicción registrada no distingue entre ellas.
- **Interior de la predicción 1:** (ρ, r) ∈ [[0.93, 2.0], [0.93, 3.0], [0.95, 2.0], [0.95, 3.0]]. La condición de falsación se evalúa por versión: si ninguna celda del interior es victoria del test propuesto frente a la unión calibrada conjuntamente, la predicción 1 falla para esa versión.
- **Predicción 2:** celdas r = 1.0, bootstrap DF-GLS solo contra el test propuesto. **Predicción 3:** celda (ρ, r) = [0.95, 4.0], κ₂ solo contra el test propuesto.
- Las cifras por n se reportan por separado; ninguna se agrega entre n.

## 6. Handicap de κ₂ por persistencia — medición previa a DGP 5

Si la persistencia deprime la potencia de κ₂, la unión tendría un handicap justo en el interior de la predicción 1 y el test propuesto podría ganar por un artefacto del comparador. Se mide antes de DGP 5 (`experiments/audit7_kappa2_handicap.py`):

- Para cada celda (n, ρ, r) con r > 1 se compara la potencia de κ₂ al valor crítico simulado bajo el AR(ρ) con quiebre r (la celda de DGP 5) y bajo el paseo aleatorio con el mismo quiebre (DGP 3), **con la misma semilla**: las innovaciones son idénticas y sólo cambia ρ. Contraste pareado.
- Alcance: n = 200 con ρ ∈ [0.9, 0.93, 0.95] y r ∈ {2, 3, 4}; como extensión, la misma rejilla a n = 500 y las celdas de confirmación a n = 1000.
- **Handicap en una celda:** McNemar exacto p < 0.05 con la potencia bajo paseo aleatorio por encima, y déficit relativo ≥ 10%. **Declarado para un n** si ocurre en al menos una celda del interior de la predicción 1.
- **Consecuencia registrada:** si el handicap se declara a n = 200, la predicción 1 a n = 200 no es un contraste limpio y la lectura honesta descansa en n = 500 y n = 1000. Si también se declara a n = 500, se dice así y la lectura limpia se restringe a los n donde no se declara. El resultado va a la tabla como advertencia, gane o pierda.

## 7. Procedencia de las cifras

| Fuente | sha256 |
|---|---|
| `experiments/results/kappa2_validation_audit7.json` | `2630cc7c991c8498368f33477714e3c0d1af49a12cfd0c2e121cf50783f6b720` |
| `experiments/results/kappa2_diagnosis_audit7.json` | `f3e5090d84bb2cf7832bf8e1603a2106a6ade639f0f053bececa235546579a4a` |
| `experiments/results/kappa2_simcv_audit7.json` | `1f1ef5468c15fe7c71310b733ab601280c2c995febd28a087f8475a7928cb7a7` |
| `experiments/results/dgp3_recast_composite_null_audit7.json` | `ea386ab89f3df185c02cdc16ae4123773a4aae70b3e40c7bff03f4bcbf8892cd` |
