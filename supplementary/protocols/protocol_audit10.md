# Protocolo de la auditoría A10: decisión limpia de θ y consolidación

Se registra en B10.0, antes de cualquier cómputo de A10. Es una **enmienda
declarada a la regla del θ primario de A9** (`experiments/protocol_audit9.md`,
REGLA B9.2): el criterio A1 se sustituye por A1′. Todo lo demás de la regla
queda igual.

Copio literalmente la regla de B10.1 y la condición de B10.3 del encargo. La
sección «Lecturas operativas» fija, antes de ver datos, cómo aplico cada regla
cuando el encargo admite más de una lectura. Cualquier enmienda posterior va en
un archivo propio (`protocol_audit10_amendN.md`), con commit propio y fila en §4
del reporte.

## Motivo de la enmienda (literal)

"La regla del θ primario de A9 se evaluó con N = 20 000 y una región binomial exacta, sobre muestras compartidas entre el caso demeaned y el caso con tendencia y con la ley nula calibrada con N_cal = 50 000. Con esa N_cal el error de simulación del cuantil desplazado es del orden de 0.1 pp en probabilidad, comparable al ancho de la región, de modo que la compuerta mezcla el error de calibración con el de muestreo. A10 la reevalúa con N_cal = 500 000, muestras independientes por caso y un criterio de equivalencia en lugar de una región de significancia."

## Reglas copiadas literalmente

### REGLA B10.1 (DURA)

Configuraciones: RM-GLS con θ ∈ {0, 0.02, 0.05, 0.10, 0.20}, casos demeaned y con tendencia. Comparadores en la misma tabla (para poder leer si una celda es baja para todo el mundo): RM (anclado en la media), MSB-HAC, la variante (b) de B9.3 (θ = 0 con s²_AR), ADF-sim, DF-GLS-sim, MZ_t-GLS-sim, MSB-GLS-sim.

Diseño:

* n ∈ {200, 500, 1000}, ambos casos, hijos de semilla distintos por caso.
* Dos muestras independientes de N = 50 000 cada una por (θ o comparador, caso, n), familia 111, con hijos independientes entre muestras.
* Calibración con N_cal = 500 000 para todos los procedimientos calibrados por simulación (DKW ε = 0.0019). Declara el tiempo que toma; si a n = 1000 supera 20 minutos por configuración, detente y reporta antes de lanzar la rejilla completa.

Criterio A1′ (equivalencia, sustituye a A1): con las dos muestras agregadas (N = 100 000 por celda), la configuración pasa A1′ si en las seis celdas (caso × n) se cumple
|tamaño − 0.05| ≤ 0.0025 (es decir, 0.25 puntos porcentuales).
Reporta además, por celda: las dos tasas por separado, la agregada, su IC de Wilson, y si cae dentro de la región binomial exacta de N = 100 000 (que se reporta pero no decide).

A2 se mantiene sin cambios y se reutiliza de A9 (Tabla B9.2.rule): media de Δ en las 16 celda-caso GARCH con n ≤ 500, no peor que el mejor θ en más de 0.30 pp. No recalcules.

P(θ) se mantiene sin cambios y se reutiliza de A9 (media de la potencia local demeaned en c ∈ {5, 10, 15}).

Regla de decisión (idéntica a la de A9 salvo A1′): entre los θ que cumplen A1′ y A2, el primario es el de mayor P(θ); si dos quedan a menos de 1 pp de P, gana el θ mayor. Aplícala mecánicamente y reporta cada término.

Compuerta B10.1 (DURA): si ningún θ cumple A1′, detente y reporta la tabla completa: significaría que la calibración no alcanza el nivel nominal dentro de 0.25 pp en alguna celda y eso hay que diagnosticarlo antes de seguir.

### CONDICIÓN B10.3

Condición: ejecuta este bloque solo si el θ de B10.1 es distinto de 0.1. Si sale 0.1, decláralo en §5, no recalcules nada y salta a B10.4: todo lo de A9 sigue vigente.

## Lecturas operativas (fijadas antes de ver datos)

1. **Familias.** Una por bloque: B10.0 = 110, B10.1 = 111, B10.2 = 112,
   B10.3 = 113, B10.4 = 114, B10.5 = 115; 116–119 quedan para enmiendas. B10.0 y
   B10.5 no generan trayectorias. El esquema `SeedSequence(familia).spawn`, con un
   hijo por celda y un nieto por réplica, produce el mismo estado que
   `SeedSequence(familia, spawn_key = (celda, i))`, que es el esquema de A8 y A9.
   B10.0 verifica esa igualdad. Cada lista de celdas está ordenada y solo se
   amplía por el final.
2. **Muestras de B10.1.** Hay 12 celdas: `a1_<caso>_n<n>_s<k>`, con caso ∈ {dm,
   ct}, n ∈ {200, 500, 1000} y k ∈ {1, 2}. Cada celda tiene 50 000 paseos
   aleatorios gaussianos (Y₀ = 0, Y = cumsum ε, ε iid N(0, 1), como
   `gauss_rw` de A8). Los dos casos y las dos muestras usan hijos distintos de la
   familia 111. En cada celda solo se calcula su caso. Dentro de una celda, las
   configuraciones (los 5 θ y los 7 comparadores) se evalúan sobre las mismas
   trayectorias. Esa es la lectura de «por (θ o comparador, caso, n)»: la tabla
   compara procedimientos sobre la misma muestra, como en A9, y la independencia
   que pide el encargo es entre casos y entre muestras.
3. **Calibración de B10.1.** Uso los caminos de producción: semilla 42, un
   `standard_normal(n)` por camino, Y₀ = 0 y Y = cumsum, con N_cal = 500 000 por
   n. Todos los procedimientos se calibran sobre los mismos caminos y los dos
   casos comparten la muestra de calibración, como en producción; la
   independencia entre casos se refiere a las muestras de tamaño. La selección de
   retardos va dentro del bucle. Los primeros 50 000 caminos del flujo son los de
   la calibración de A9 (`audit9_cal/cal_n<n>.npz`). Reutilizo sus filas tras un
   Paso 0: recalculo las primeras 50 filas y exijo máx |Δ| = 0. Calculo nuevos
   solo los caminos 50 000–499 999, continuando el mismo flujo. Como control de
   producción, RM-GLS θ = 0.1 y θ = 0 se comparan con `_simulate_null_statistics`
   de producción (N_cal = 500 000, semilla 42) y se exige máx |Δ| = 0.
   Reglas de rechazo, las mismas que en A9: RM-GLS, RM, MSB-HAC y la variante
   (b) rechazan con p = F̂(stat) < 0.05, donde F̂ es la ECDF de producción
   (`cdf_from_null_stats`); ADF, DF-GLS, MZ_t-GLS y MSB-GLS rechazan con stat <
   cuantil 5% (cola inferior).
4. **Tiempo y compuerta de los 20 minutos.** Una «configuración» es un par
   (procedimiento, caso). Antes de la rejilla, una sonda a n = 1000 mide el coste
   por camino de cada componente sobre 14 × 20 caminos: σ̂_HAC, RM-GLS de cada θ,
   RM, MSB-HAC, Ng–Perron (MAIC, que comparten MZ_t, MSB y la variante (b)),
   DF-GLS y ADF (AIC). El tiempo de una configuración es su componente más los
   componentes que necesita (σ̂_HAC para las basadas en HAC; Ng–Perron para
   DF-GLS, MZ_t, MSB y la variante (b)) × 500 000 / 14 núcleos. Si alguna supera
   20 minutos, me detengo y lo reporto antes de lanzar la rejilla. Además declaro
   el tiempo real de pared de cada calibración.
5. **A1′.** La regla es |tasa agregada − 0.05| ≤ 0.0025, con el límite incluido,
   sobre N = 100 000 (dos muestras de 50 000) en las seis celdas (caso × n). Se
   aplica a los 5 θ. Los comparadores se reportan en la misma tabla pero no
   deciden. La región exacta de N = 100 000 es la de A8 y A9
   (`exact_region(100000)`) y se reporta como información.
6. **A2 y P(θ), reutilizados sin recalcular.** Salen de
   `experiments/results/b92_theta_audit9.json`: A2 en `theta_rule.A2_ok` (con
   `theta_rule.A2_mean_delta`) y P(θ) en `theta_rule.P`. Registro el sha256 del
   archivo en B10.0.
7. **Desempate.** Sea θ* el θ admisible de mayor P. El grupo de empate lo forman
   los admisibles con P(θ) > P(θ*) − 1 pp, y gana el mayor θ del grupo (lectura 9
   de A9).
8. **Cierre de la anomalía de la celda tendencia n = 200.** Para cada uno de los
   12 procedimientos (5 θ y 7 comparadores) reporto la tasa agregada y la de cada
   muestra, y cuento cuántas tasas agregadas quedan por debajo de 0.047. Digo que
   «el patrón se repite» si la mayoría estricta (≥ 7 de 12) queda por debajo de
   0.047, como en A9 (8 de 12).
9. **B10.2.** Uso la notación del proyecto: Y₀, …, Y_n; σ̂²_HAC de ΔY;
   û_k = residuo GLS (caso c: Y_k − μ̂_GLS con ā = 1 + c̄/n, c̄ = −7; caso ct:
   detrend QD con ā = 1 + c̄/(n + 1), c̄ = −13.5, t = 1, …, n + 1).
   Implementación independiente: μ̂_GLS y el detrend QD se reescriben con
   mínimos cuadrados propios (sin llamar a producción), y
   MSB_HAC = [ n⁻² Σ_{k=0}^{n−1} û_k² / σ̂²_HAC ]^{1/2} es la forma de Ng–Perron
   (Σ_{t=1}^{T} ỹ²_{t−1} / T², con T = n incrementos). Verifico por separado, con
   1000 series por caso y n ∈ {200, 1000}:
   (i) RM-GLS(θ = 0) de producción frente a
       [ (n + 1)⁻¹ Σ_{k=0}^{n} û_k² / (n σ̂²_HAC) ]^{1/2}
       (misma convención de índices y divisores);
   (ii) la relación exacta con MSB_HAC. Para la peor diferencia relativa el
       umbral es 1e-12.
   Como información reporto también la diferencia con el MSB de A8
   (`audit8_unitroot.np_statistics`, con ā = 1 + c̄/T y T = n + 1) cuando se
   sustituye s²_AR por σ̂²_HAC. En la parte 3 comparo RM-GLS con τ = round(θn)
   (acotado a [2, n/2] como en producción) frente a τ = 0, con θ ∈ {0.005,
   0.002} y n = 1000 (τ = 5 y τ = 2), sobre las mismas 1000 series por caso.
   Reporto la diferencia relativa media, mediana y máxima. Las series salen de
   la familia 112, con hijos distintos por (caso, n).
10. **B10.3 (condicional).** Solo se ejecuta si el θ de B10.1 ≠ 0.1. Si se
    ejecuta:
    * **3.1 DGP 2.** Las 18 celdas de B9.1 (trayectorias de B5 de A8). Las
      filas de los checkpoints de B9.1 ya contienen las columnas de los cinco θ
      (Paso 0 ya hecho en A9), así que la tabla B9.1.dgp2 se recalcula con el θ
      final sin simular trayectorias. Los umbrales simulados usan la
      calibración de 500 000 si n ∈ {200, 500, 1000} y la de A9 (50 000) en los
      demás n; la fuente se declara por celda.
    * **3.2 DGP 5.** Son las celdas de n = 200 de A7, con trayectorias de A7
      (familia 60) regeneradas con sus semillas y Paso 0 frente a los
      checkpoints de A7. Las columnas de A7 (R = 0.5, R̂, unión conjunta y
      bootstrap) se leen de sus checkpoints y sus umbrales a tamaño igualado son
      los de A7 (celda de calibración de A7, N_cal = 5000). La primaria final
      se calcula nueva sobre las trayectorias de A7 y sobre la celda de
      calibración de A7, con umbral igualado = cuantil 5% en esa celda, como
      en A8. A nivel nominal, la primaria usa la ECDF de la nula `hac` de B10.1
      (n = 200, N_cal = 500 000) y R = 0.5 usa la nula `hac` de A8. La cuota
      mediana de g₂ es la de A7 (R = 0.5).
    * **3.3 B9.4.** Las filas de B9.4 y de B9.2 de A9 ya contienen los cinco θ;
      el análisis se repite con el θ final sin simular.
    * **3.4 B9.5.** La sonda AWB se recalcula con el θ final sobre las mismas
      trayectorias de origen que en A9 (N = 2000, B = 399). Las semillas de
      remuestreo son de la familia 113 (celdas `awb_*`). Es CARO: presupuesto
      de 8 h, con una sonda de 14 series por celda y detención si la proyección
      lo excede. Rigen la regla de recomendación de A9 y su región exacta de
      N = 2000.
    * **3.5 B9.6.** Se repite el script de B9.6 de A9 con el θ final, con
      calibración simulada y con la variante AWB si 3.4 la recomienda. Las
      semillas de remuestreo AWB de la aplicación y del tamaño fuera de muestra
      son de la familia 113. Se verifican los hashes de los datos congelados.
    * **3.6 B9.7.** Las filas de B9.7 de A9 (N_cal = 100 000, familia 107)
      contienen los cinco θ. La tabla de valores críticos se reemite marcando
      el θ final. La auditoría de semilla cruzada se recalcula restringida a las
      12 celdas (caso, n) del θ final: audito las 6 de mayor EE (máximo sobre
      α), el mismo número de celdas que en A9 (10% de 60). Si A9 ya calibró de
      forma independiente un (caso, n) auditado
      (celdas `cvx`, que contienen los cinco θ), reutilizo esas filas. Si no, lo
      calibro nuevo en la familia 113 (celda `cvx_<caso>_n<n>`, N_cal =
      100 000).
    * **3.7 Tamaño en el dominio bajo.** Con n ∈ {60, 100, 150} y N = 50 000 por
      (caso, n), hijos distintos por caso (familia 113), y N_cal = 500 000 en los
      caminos de producción, calculo el θ final y θ = 0.1. Reporto la tasa, el
      IC de Wilson y la región exacta de N = 50 000.
11. **B10.4.** Una celda por réplica: `cv5000_r<k>` con k = 1, …, 5 (familia 114).
    Cada réplica tiene 100 000 paseos gaussianos a n = 5000, caso demeaned, y de
    ellos se toman los estadísticos RM-GLS con θ = 0.1 y θ = 0.2 (calibración
    `hac`). Valor crítico = `np.quantile(·, 0.05)`, la misma convención que B9.7.
    Por θ reporto los cinco valores, su media, su desviación típica (ddof = 1) y
    su rango [mín, máx]. También digo si caen dentro del rango, o a menos de 3
    desviaciones típicas de la media de las réplicas, cada uno de los valores
    previos de esa celda: el de la tabla de B9.7 (familia 107, celda `cv`), el
    independiente de la auditoría cruzada de B9.7 (celda `cvx`; 0.2052 es el de
    θ = 0.1), el de la calibración de A9 con semilla 42 (N_cal = 50 000) y el de
    B7 de A8, si existe. La anomalía se cierra si los dos valores de B9.7 (`cv`
    y `cvx`) cumplen una de las dos condiciones en los dos θ. Si no, sigue
    abierta.
12. **B10.5.** Si θ = 0.1, las figuras de A9 siguen vigentes. Se declara así y
    solo se genera la figura nueva. `fig_calibration_gain_audit10.pdf` usa n ∈
    {60, 100, 150, 200, 500, 1000, 2000, 5000}, con las muestras de tamaño
    independientes de mayor N disponibles en cada n: B10.1 (N = 100 000, n ∈
    {200, 500, 1000}), B10.3.7 si se ejecutó (N = 50 000, n ∈ {60, 100, 150}) y
    B9.2 de A9 (N = 20 000) en el resto. El valor crítico «calibrado en cada n»
    sale de la calibración de mayor N_cal disponible en ese n. El valor crítico
    de n = 20 000 es el cuantil 5% de la muestra de B9.4. MSB-GLS usa el valor
    asintótico publicado (Ng–Perron 2001: 0.233 / 0.168). La banda es la
    región exacta de la N de cada punto.
