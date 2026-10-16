# Enmienda 3 al protocolo de A15: decisiones del autor tras el Paso 0 de B15.1 con B = 399

Se commitea antes de computar nada de lo que regula. Los datos del Paso 0 con B = 399 (`b1_paso0_audit15.json`, commit
`75b8092`) quedan como diagnóstico y no se reevalúan con los criterios nuevos.

## 1. Decisiones del autor (literal)

```
Decisiones del autor (enmienda 3; commitear antes de computar nada):

E3.1  Paso 0 de B15.1: criterios nuevos. Se aplican SOLO a una corrida nueva.
      - Se repite con streams nuevos: familia 159 (reserva), B = 999 en R y
        en Python, las mismas 4 celdas × 50 series.
      - Pasa si se cumplen las tres:
        (a) estadístico |Δ| ≤ 1e-10 y retardo |Δ| = 0 (sin cambios);
        (b) sesgo: |media(p_py − p_R)| ≤ 2.58·EE;
        (c) ruido: media|Δp| ≤ 1.15 × media|Δp| esperada para dos réplicas
            exactas independientes (tu fórmula E|X−Y|/B, calculada antes de
            ver los datos nuevos).
      - Los datos de la corrida con B = 399 quedan en el JSON como
        diagnóstico y no se reevalúan con estos criterios.

E3.2  Fidelidad del tamaño, en pareado:
      - Corre bootUR (SB y SWB, B = 999) sobre los MISMOS 2000 caminos iid
        por caso que usa la réplica.
      - Pasa si |size_py − size_R| ≤ 2.58 × EE pareado (a partir de los pares
        discordantes).
      - El tamaño de bootUR en sí NO es compuerta: se reporta como resultado,
        con Wilson.
      - Declara en Anomalías si bootUR da en el caso constante un valor fuera
        de [0.0405, 0.060].

E3.3  Brazo (iii) = el SB de bootUR 1.0.5, replicado (regresión ADF con MAIC,
      residuos sin centrar, índices 0..T−l), aplicado a MZ_t-GLS con la MAIC
      GLS re-elegida en cada réplica.
      - Se retira la definición anterior (AR sobre Δy centrado, AIC).
      - Etiqueta: «SB (bootUR)».
      - Desviación declarada: el cambio se decide tras ver el Paso 0 con
        B = 399 sobre DF-GLS y antes de computar cualquier dato de B15.1.
      - Los criterios de desenlace de 14cbca7 NO cambian.

E3.4  Autorización de B15.1, condicionada a que pase E3.1–E3.2:
      - Se corre la sonda 151, que reporta solo tiempos, con conteos sellados.
      - Si la proyección es ≤ 50 horas-núcleo: lanzar sin nueva confirmación.
      - Si es mayor: aplicar en orden R = 199, luego 18 celdas, luego sin
        (iv), hasta ≤ 50, e informar ANTES de lanzar.
      - Si E3.1 o E3.2 fallan: B15.1 queda detenido y se reporta; no hay
        otra enmienda.

E3.5  B15.3: confirmado por escrito. Lánzalo ya, en paralelo al Paso 0 nuevo.

E3.6  Descargas: no se commitean los archivos; basta con los sha256 de la
      enmienda 2.

Reporte: una sección «Paso 0 de B15.1 (enmienda 3)» que distinga entre
fidelidad de la réplica y tamaño de bootUR, y otra con B15.3 completo.
```

## 2. Lecturas operativas

**E3.1-a. Familia 159 y series.** La familia 159 pasa de reserva a uso. Celdas 0–3: las mismas cuatro (iid c, iid ct,
MA(−0.5) c, MA(−0.5) ct), n = 200, 50 series cada una. Celdas 4 y 5: 2000 caminos iid de n = 200, caso c y ct (E3.2).
Trayectoria (celda, i) con `SeedSequence(159, spawn_key=(celda, i))`; bootstrap de la réplica con
`spawn_key=(celda, i, 6)` para SB y `(celda, i, 7)` para SWB. Del lado de R: `set.seed(159000 + j)` para SB y
`set.seed(159500 + j)` para SWB en las 200 series (j = 0…199); en los caminos de tamaño, `set.seed(1590000 + 10000·c + i)`
para SB y `set.seed(1595000 + 10000·c + i)` para SWB, con c ∈ {4, 5} el índice de celda e i ∈ {0, …, 1999}. B = 999 en los
dos lados. La familia 159 entra en la comprobación de colisiones, que se repite antes de computar.

**E3.1-b. Criterios.** Por método (SB, SWB), sobre las 200 series:
- (a) máx. |Δ estadístico| ≤ 1e-10 y máx. |Δ retardo| = 0.
- (b) |media(p_py − p_R)| ≤ 2.58·EE, con EE = desviación típica muestral de (p_py − p_R) (ddof = 1) / √200.
- (c) media|p_py − p_R| ≤ 1.15 × media sobre las series de E|X − Y|/B, con X, Y ~ Bin(B, p) independientes, B = 999 y p
  = (p_py + p_R)/2 de cada serie. La fórmula queda fijada en esta enmienda, antes de ver los datos nuevos. Es la de
  `audit15_b1_paso0.noise_benchmark` del commit `6c938d8`, con B como parámetro.

**E3.2. Tamaño pareado.** En cada camino de las celdas 4 y 5, por método:
- **Rechazos.** Rechaza la réplica si p_py < 0.05, y rechaza bootUR si su p < 0.05 (la regla de `boot_adf`: p = #{t* <
  t}/B y rechazo con p < nivel).
- **Pares discordantes.** b = #(réplica rechaza, bootUR no) y c = #(bootUR rechaza, réplica no).
- **Diferencia.** size_py − size_R = (b − c)/N, con EE pareado = [b + c − (b − c)²/N]^{1/2}/N.
- **Criterio.** |size_py − size_R| ≤ 2.58·EE.
- **Resultado.** El tamaño de bootUR, con Wilson al 95 %, se reporta como resultado y no es compuerta. Si en el caso
  constante queda fuera de [0.0405, 0.060], se declara en Anomalías.

**E3.1–E3.2. Compuerta.** Por método: (a), (b), (c) y E3.2 en los dos casos. El brazo (iii) «SB (bootUR)» depende del SB;
(v′) «SWB (bootUR)» depende del SWB. Si falla el SB, B15.1 se detiene (lectura 1.7, E3.4); si sólo falla el SWB, se detiene
(v′).

**E3.3. Brazo (iii) «SB (bootUR)».**
- **DGP.** El de la enmienda 2 (R2 + R3): regresión ADF sobre la serie sin tendencia por MCO, MAIC de Perron–Qu, todas las
  filas, residuos sin centrar, coeficientes γ̂; remuestreo de índices en {0, …, T − l}, recursión AR con ceros e y* =
  acumulado.
- **Estadístico.** MZ_t-GLS con la MAIC GLS re-elegida en cada réplica.
- **p-valor.** Por rango (lectura 1.6).
- **Lo que se retira.** La lectura 1.3 y el punto B2 de la enmienda 2. El Paso 0 valida el DGP que usa el brazo.
- **Lo que no cambia.** Los streams (a = 3) y los criterios de desenlace de `14cbca7`.

**E3.4. Sonda y lanzamiento.**
- **Sonda.** La 151 (lectura 1.9, enmienda 2 §5), con los brazos (iii) «SB (bootUR)», (iv) y (v′).
- **Proyección.** Se usa la escalada por n; la conservadora se reporta.
- **Lanzamiento.** Si la proyección es ≤ 50 horas-núcleo, se lanza el diseño completo. Si no, se aplican en orden R = 199,
  18 celdas y sin (iv) hasta ≤ 50, y se informa antes de lanzar.
- **Si (v′) no pasa.** Se lanza sin (v′), y la proyección se recalcula sin ese brazo.

**E3.5. B15.3.** Se lanza en paralelo al Paso 0 nuevo, con el diseño de las lecturas 3.1–3.7 y la regla de LLSW (enmienda 2
§4). La predicción se evalúa en b ∈ {0.1, 0.3, 1.0}, como dice `14cbca7`; LLSW se reporta aparte. Las corridas en paralelo
alteran los tiempos, que no son resultados.

**E3.6.** Sin cambios: las descargas no se commitean.
