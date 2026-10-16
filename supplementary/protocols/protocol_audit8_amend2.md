# Enmienda 2 al protocolo de A8

**Momento:** después de ver datos de B2.

**Motivo (literal del autor):** "La compuerta B2b se evaluó sobre una única
muestra de 5000 trayectorias que además está anidada entre tamaños muestrales
(misma semilla en todos los n). Sobre 20 000 trayectorias independientes el
tamaño de RM `hac` a n = 200 es 0.0493 [0.0464, 0.0524], y una calibración
independiente sobre las trayectorias publicadas reproduce la cifra baja
(0.0420), lo que localiza la desviación en la muestra y no en la calibración. La
compuerta se re-evalúa sobre trayectorias independientes con precisión
suficiente."

## 1. Nueva compuerta B2b (DURA)

Sustituye a la compuerta B2b del protocolo.

- Tamaño gaussiano de RM `hac` (R = 0, θ = 0.1) sobre N = 20 000 trayectorias
  independientes, familia 92, un hijo de SeedSequence por n (no anidadas), en
  n ∈ {60, 100, 150, 200, 500, 1000, 2000, 5000}.
- Región exacta binomial para N = 20 000, calculada en el script.
- PASA si n = 200, 500 y 1000 están dentro. Los demás n se reportan.
- Aplica también a RM-GLS si B4 lo adopta.
- Las cifras sobre trayectorias publicadas se conservan en el reporte como
  columna de comparabilidad con v11, no como compuerta.

## 2. Referencia gaussiana de las tablas y de los Δ pareados

Todas las tasas gaussianas que entren en tablas o en Δ pareados de B2b, B3 y B5
salen de las trayectorias independientes de la familia 92 con N = 20 000 por n,
para todos los procedimientos (RM `one`/`hac`, R = 0.5, ADF/PP/DF-GLS `asy` y
`sim`, MZ_t-GLS, MSB-GLS, MSB-HAC). Los Δ pareados de B2b se recalculan con esa
referencia y se reportan las dos versiones (referencia publicada y referencia
independiente) en tablas separadas.

## 3. Caché de la nula (toca producción; regla 6)

- La clave de caché de la nula incluye N_cal, semilla de calibración,
  cal_sigma, R, θ, n, tau_mode, anchor y tratamiento determinista. Regresión
  pre/post con defaults y una sola llamada (máx. |Δ| = 0 en estadístico y
  p-valor), suite en verde, y un test que llama con N_cal = 10 000 y luego con
  50 000 en el mismo proceso y verifica nulas distintas.
- Auditoría de alcance sobre los scripts de A1–A7: cada proceso que construye la
  nula con parámetros no incluidos en la clave antigua, con las cifras
  publicadas en `paper/*.tex` que dependen de él (archivo y línea) y si se
  reproducen con la nula "equivocada" o con la correcta. Solo identificar; no se
  recalcula nada fuera del plan.
- Antes de B3 se verifica que las columnas sin bootstrap reutilizadas de B2 no se
  generaron con la clave antigua y dos N_cal distintos en el mismo proceso; si
  alguna lo fue, se recalcula.

## 4. Bootstrap AWB: alcance acotado

- Solo en n ≤ 1000. Se retira de las celdas de n = 2000 y 5000 en B3, B5 y B8;
  en la figura de desplazamientos la curva AWB termina en n = 1000.
- B3: N_sim = 2000, B = 399, en todas las celdas mal especificadas con n ≤ 1000
  más la gaussiana. La celda gaussiana de n = 200 con N = 5000 se mantiene.
- B5: bootstrap en DGP 1 con ρ ∈ {0.95, 0.99} × n ∈ {200, 500, 1000}; en DGP 3
  con r ∈ {1, 2, 4} × n ∈ {200, 500, 1000}. Se retira de las demás celdas.
- Se mantiene la regla de presupuesto de 30 h por bloque CARO. Si con este
  alcance aún se excede, se detiene y se reporta la extrapolación por celda.

## 5. Orden

Enmienda 2 → corrección de caché con su regresión → nueva B2b → B3 (--budget,
luego --run) → B4 → B5 → B6 → B7 → B8, respetando las compuertas duras y la
regla de presupuesto, sin volver a preguntar. Al final se regenera
`resultados_auditoria_8.md` completo; §6 incluye el tamaño de RM `hac` por n
sobre trayectorias independientes y la media de Δ a n = 200 y 500 de RM `hac`,
ADF-sim, DF-GLS-asy y DF-GLS-sim con referencia independiente.
