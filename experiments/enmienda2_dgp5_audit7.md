# Segunda enmienda al pre-registro — DGP 5 (desviación mixta)

- Fecha de generación (UTC): 2026-09-14T21:04:21.832080+00:00
- Predicción registrada: commit `62216ee3f51f800bbf643a43cf7343d46952a18d`.
- Primera enmienda (`experiments/enmienda_dgp5_audit7.md`): commit `187300be8883991191864c5c805319163140e33c`.
- Generada por `experiments/audit7_write_amendment2.py` en el commit `59e1bb2d53a641122e98d5e144016a5abef2e260`.
- Precede a cualquier cómputo del test propuesto, del bootstrap DF-GLS y de ADF, PP y DF-GLS asintóticos sobre las series de DGP 5, y a cualquier cómputo sobre las series de la extensión. Comprobado en disco al generar: 0 checkpoints de DGP 5 en el directorio del runner y 0 de la extensión en el de la medición del handicap. Sobre las series de la rejilla registrada sólo se ha calculado κ₂, en la medición prevista en la sección 6 de la primera enmienda.

**El texto de las predicciones 1, 2 y 3 y el de la condición de falsación no se modifican.** Esta enmienda añade celdas a la rejilla, retira las de n = 1000 y registra cómo se leen las celdas añadidas y qué veredicto gobierna la consecuencia registrada.

## 1. Motivo de la extensión

Los quiebres de la rejilla registrada, r ∈ {2, 3, 4}, multiplican la varianza de las innovaciones por ×4, ×9, ×16. En datos financieros diarios, desplazamientos de esa magnitud corresponden a episodios de crisis. Los quiebres r ∈ {1.1, 1.25, 1.5} la multiplican por ×1.21, ×1.56, ×2.25, el rango de los desplazamientos rutinarios de régimen de volatilidad. La rejilla registrada cubría lo extremo y omitía lo común.

## 2. Conocimiento disponible al fijar la extensión

Se declara para que el lector juzgue la secuencia.

- **Medición del handicap de κ₂** (`kappa2_handicap_audit7.json`, commit `ceb29c93642c8da301588ce5271e6b1766cf22c0`): handicap no declarado en ningún n. En las celdas con r ∈ {2, 3, 4} y n ∈ {200, 500}, la potencia de κ₂ al valor crítico simulado del 5% está entre 0.9995 y 1.0000 bajo el AR y entre 0.9995 y 1.0000 bajo el paseo aleatorio con el mismo quiebre; su mínimo en el interior registrado de la predicción 1 es 0.9995.
- Consecuencia que ya se conocía: en el interior registrado cabe esperar que la unión calibrada conjuntamente rechace casi siempre por su componente κ₂, de modo que un empate o una derrota del test propuesto ahí puede reflejar el techo de la unión y no el coste de multiplicidad.
- Los valores r ∈ {1.1, 1.25, 1.5} se fijaron sin calcular ningún procedimiento sobre series con esos quiebres (comprobación en disco del encabezado). No se midió de antemano la potencia de κ₂ ni la de ningún otro procedimiento en ellos.
- Lo que ya se sabía de DGP 3 (sección 3 de la primera enmienda) sigue vigente. Expectativa declarada, no predicción: en quiebres débiles el canal de varianza pesa menos que en los fuertes, de modo que la extensión hace menos probable que la cuota de g₂ sea sustancial.

## 3. Celdas añadidas

- ρ ∈ {0.90, 0.93, 0.95} × r ∈ {1.1, 1.25, 1.5} × n ∈ {200, 500}: 18 celdas, 2000 réplicas por celda, B = 399, el mismo generador de DGP 5.
- Semillas: familia 60, índices de celda 27 a 44, a continuación de las 27 celdas de la especificación revisada; ninguna celda registrada cambia de semilla. La disjunción, incluida la de las semillas de R del bootstrap, se verifica en el Paso 0 del Bloque 1.
- La calibración bajo la nula compuesta es la misma (paseo aleatorio homoscedástico, 5000 réplicas por n): mismos umbrales a tamaño igualado y mismo α\* de la unión.
- El handicap de κ₂ por persistencia se mide en la extensión con el mismo script y el mismo criterio (sección 6 de la primera enmienda), después del commit de esta enmienda y antes del análisis. Se declara por n sobre la extensión de la predicción 1 y va a la tabla como advertencia.

## 4. Retirada de n = 1000

- Se retiran las celdas de confirmación [[1000, 0.93, 2.0], [1000, 0.93, 3.0], [1000, 0.95, 3.0]] y, con ellas, la calibración y la nula nominal del test adaptativo a n = 1000, que sólo servían a esas celdas.
- Motivo: confirman en vez de discriminar, y su costo no se puede presupuestar con fiabilidad. El presupuesto por sondas (`block1_budget_audit7.json`) proyectó 29.7 h para las tres celdas y 24.8 h para la calibración de n = 1000, pero el mismo lote no reproduce su tiempo (`bootstrap_cost_diagnostic_audit7.json`: a n = 1000, 7.440 s/serie sin pool frente a 17.796 en la sonda del presupuesto).
- Pasan a «No ejecutado» con este comando de reanudación:

      python experiments/audit7_dgp5_runner.py --cells "adaptnull:n=1000;cal:n=1000;dgp5:confirm" --cores <nucleos> --B 399 --n-sim-dgp5 2000 --n-cal 5000 --max-seconds 14400

- Consecuencia sobre la sección 6 de la primera enmienda: si el handicap se declarara a n = 200, la lectura limpia descansa sólo en n = 500.

## 5. Veredicto que gobierna la consecuencia y lectura de la extensión

- **Resultado primario: el veredicto literal.** La condición de falsación registrada se evalúa literalmente sobre el interior registrado [[0.93, 2.0], [0.93, 3.0], [0.95, 2.0], [0.95, 3.0]], por versión del test propuesto y por n. **Ese veredicto gobierna la consecuencia registrada** y se reporta como resultado primario.
- **Diagnóstico, declarado antes de los datos.** El veredicto literal se evalúa en condiciones en que κ₂ tiene potencia ≥ 0.9995 en el interior registrado (sección 2). Esa cifra procede de la medición del handicap, prevista en la sección 6 de la primera enmienda y ejecutada antes de cualquier cómputo del test propuesto o del bootstrap sobre DGP 5. En esas condiciones la unión calibrada conjuntamente puede rechazar casi siempre por κ₂, y el veredicto literal **no es informativo sobre la hipótesis**. Si se dispara, se reporta que la condición de falsación registrada se cumplió y, junto a ello, que el diseño no podía discriminar, con la potencia de κ₂ de la medición del handicap y la potencia a tamaño igualado de la unión, de κ₂ y del bootstrap DF-GLS en esas celdas de DGP 5.
- **Contraste post-registro: la extensión.** (ρ, r) ∈ [[0.93, 1.1], [0.93, 1.25], [0.93, 1.5], [0.95, 1.1], [0.95, 1.25], [0.95, 1.5]], etiquetado como post-registro en toda tabla y todo texto. Usa la misma regla por celda (McNemar exacto pareado, a tamaño igualado, frente a la unión calibrada conjuntamente), por versión y por n, el mismo desdoblamiento por la cuota de energía de g₂ (sección 4 de la primera enmienda) y la advertencia del handicap de κ₂ medida sobre la extensión. Tiene veredicto propio y **no anula ni sustituye al veredicto registrado**.
- La decisión de extender se tomó después de conocer la saturación de κ₂ (sección 2). Por eso la extensión no puede gobernar la consecuencia, aunque sus valores de r se fijaran sin mirar ningún procedimiento sobre ellos.
- Las celdas de la extensión con ρ = 0.90 se reportan con las mismas columnas y no entran en ninguna predicción.
- Las predicciones 2 y 3 se evalúan sin cambios, a n ∈ {200, 500}.

## 6. Procedencia de las cifras

| Fuente | sha256 |
|---|---|
| `experiments/results/kappa2_handicap_audit7.json` | `680eb9c2278a8f797cddd342167bcee1cfa49a1ae80d7f77463411229f7a8410` |
| `experiments/results/block1_budget_audit7.json` | `114d9ae7afbadd9ec88f20775928bcb6c344ca1c1883f8246ef38ebacddd3ad7` |
| `experiments/results/bootstrap_cost_diagnostic_audit7.json` | `bf16da7f68ee5ff9687178470be73381ce6ccb7e2ecb0d97b9f32283e780542f` |
