# Enmienda 2 al protocolo de A15: reglas leídas de bootUR 1.0.5 y de LLSW (2018), semillas por brazo

Se commitea después de la predicción (`14cbca7`) y antes del Paso 0. Sólo registra reglas leídas de las fuentes; no se ha
calculado nada con ellas. Las fuentes están en `experiments/external_audit15/`, sin commitear:

| Archivo | Origen | Bytes | sha256 |
|---|---|---|---|
| `bootUR_1.0.5.tar.gz` | cran.r-project.org/src/contrib | 142134 | `34ba4c50648b15ec98d68552efcdd520a5b458341bcf30854e6fb032f41e4a4a` |
| `HARRecommendations.pdf` | ebenlazarus.github.io | 3849550 | `10427d45bece5c4a3c08943a7c1fde899e18c4551f6a48ccc10610e9d2c9ae05` |

## 1. bootUR 1.0.5: `boot_adf(detrend = "QD", bootstrap = "SB" | "SWB", criterion = "MAIC", criterion_scale = FALSE)`

Los números de línea son de `R/auxiliary.R` (A) y `src/bootURfunctions.cpp` (C). T = número de observaciones de la serie que
se pasa (aquí n + 1 valores, con y₀ = 0).

**R1. Estadístico sobre los datos** (A:110 → C:312–368 → C:248–266, C:145–185).
- La MAIC elige el retardo sobre la serie **sin tendencia por MCO** (`QD = false`) y con muestra común recortada en pmax
  (`trim_ic = pmax`): IC = ln s²_k + 2(k + τ_k)/(T − pmax − 1), con s²_k = e'e/(T − pmax − 1) y τ_k = b₀² Σ ỹ²_{t−1}/s²_k
  sobre ỹ sin tendencia por MCO (C:218–223). Esta es la corrección de Perron–Qu (2007).
- El estadístico es el t del ADF sobre la serie **QD** con c̄ = 7 (constante) o 13.5 (tendencia), c_n = 1 − c̄/T, con la
  primera fila de la cuasi-diferencia sin diferenciar (C:109–125).
- Usa el retardo elegido, la muestra desde p + 1 y s² = e'e/(número de filas), sin corrección de grados de libertad
  (C:145–185).

**R2. DGP del bootstrap** (A:92 → C:402–427).
- Se usa la misma selección MAIC (R1) sobre la serie sin tendencia por MCO. La regresión ADF final (`QD = false`,
  `trim = false`) usa **todas** las filas, con los retardos rellenados con ceros.
- Los residuos e_t = Δỹ_t − x_t'b (T valores) no se centran. Los coeficientes γ̂_1…γ̂_p de los retardos de Δỹ son los del
  AR del sieve (`ar_est`), y quedan con ceros hasta pmax.

**R3. SB** (C:508–521, C:605–631). Se remuestrean los índices con reemplazo en {0, …, T − l}, con l = round(1.75 T^{1/3})
(A:265). No es {0, …, T − 1}: con SB, `ub = l` (C:622–627). Después:
- e*_t = e_{i_t};
- u*_t = e*_t + Σ_j γ̂_j u*_{t−j}, con u* = 0 antes del inicio;
- y* = acumulado de u* (y*_1 = u*_1; y₀ = 0 no se antepone, C:517–520).

**R4. SWB** (C:523–535). e*_t = z_t e_t con z_t iid N(0, 1) (`Rcpp::rnorm`, C:619); la misma recursión AR y el mismo
acumulado que R3.

**R5. Réplica.** En y* se recalcula R1: retardo MAIC re-elegido y t del ADF-QD (C:551–556).

**R6. p-valor** (C:803–810): p = #{t* < t}/B.

**R7. pmax.** Por defecto `round(12(T/100)^{1/4})` (A:324). En el Paso 0 se pasa `max_lag = ⌊12(T/100)^{1/4}⌋`
explícitamente, la regla de `audit8_unitroot.kmax_rule` y del encargo, a los dos lados. `min_lag = 0`.

## 2. Consecuencias para los brazos

**B1. Paso 0 (familia 154).** La réplica en Python sigue R1–R7 exactamente, con el estadístico ADF-QD (DF-GLS con la MAIC de
Perron–Qu), y se compara con `boot_adf` con los criterios de la lectura 1.7. El SB se compara con `bootstrap = "SB"` y el
SWB con `"SWB"`.

**B2. Brazo (iii).** El encargo lo define como AR(p) sobre Δy centrado, p por AIC con pmax = ⌊12(n/100)^{1/4}⌋, residuos
centrados remuestreados iid. Eso **no** es el SB de bootUR. Se declara la diferencia y el brazo (iii) sigue la definición
del encargo:
- **Estimación.** AR por MCO sobre la muestra común de pmax retardos y AIC = ln(e'e/N_eff) + 2p/N_eff, frente a la regresión
  ADF con MAIC de R2.
- **Residuos.** Se centran; en bootUR no.
- **Índices.** Van de 0 a n − 1; en bootUR, de 0 a T − l.
- **Resto.** La recursión AR con u* = 0 antes del inicio es la de R3. y* = (0, acumulado de u*), con los n + 1 valores de la
  trayectoria original.

Lo que el Paso 0 valida y comparten los dos es la recursión AR, el acumulado, el remuestreo iid, la cuasi-diferencia y la
MAIC. El estadístico del brazo es MZ_t-GLS con la MAIC GLS de `audit8_unitroot.np_statistics`, sin Perron–Qu (lectura
1.11). El p-valor es (1 + #{T* ≤ T})/(R + 1) (lectura 1.6).

**B3. Brazo (v′) «SWB (bootUR)».** DGP exactamente R2 + R4 sobre la trayectoria de n + 1 valores con `dc` del caso y
pmax = ⌊12(T/100)^{1/4}⌋. Estadístico MZ_t-GLS con la MAIC GLS re-elegida (como (iii)). p-valor (1 + #{T* ≤ T})/(R + 1).

**B4. Brazo (iv), AWB.** El de B9.5 (`audit9_engine.awb_pvalue`, def:awb): u_t = Δy_t − media(Δy), ξ_1 = ν_1,
ξ_t = γξ_{t−1} + (1 − γ²)^{1/2}ν_t, Δy*_t = ξ_t u_t, y*_0 = 0 e y* acumulado. γ sale de `audit9_engine.awb_gamma`:
γ = 0.01^{1/l}, l = round(1.75 (n + 1)^{1/3}). Se aplica a MZ_t-GLS con la MAIC GLS re-elegida.

## 3. Semillas por brazo

La trayectoria (celda c, camino i) usa `SeedSequence(familia, spawn_key=(c, i))`, como en A8–A14. Las extracciones del
bootstrap del brazo a usan `SeedSequence(familia, spawn_key=(c, i, a))`, con a = 3 para (iii), 4 para (iv) y 5 para (v′). Así
el orden de ejecución de los brazos no afecta a los resultados. La comprobación de colisiones (palabra 0 de
`generate_state(uint64)`, método de A8–A13) cubre las trayectorias y los streams por brazo de 151–158, frente a las familias
de A8–A13 (90–149, las que tienen streams), las semillas enteras de A5–A7 y la 42.

En el Paso 0, las 200 series de la familia 154 son las celdas 0–3: iid c, iid ct, MA(−0.5) c y MA(−0.5) ct, con n = 200 y 50
series cada una. Del lado de R, `set.seed(154000 + j)` antes de cada `boot_adf`, con j = 0…199. Los 2000 caminos iid del
tamaño son las celdas 4 y 5 (c y ct, n = 200); sus bootstraps usan a = 6 (SB) y a = 7 (SWB).

## 4. LLSW (2018): cuarta configuración de B15.3

La regla es explícita:
- **Ecuación (3).** p. 542: «S = 1.3T^{1/2} (loss-minimizing rule, NW)».
- **Redondeo.** Nota 3 de p. 542: «Our rounding convention is to round up S for NW».
- **Tabla 1.** Fila 2, p. 543: NW, S = 1.3T^{1/2}, fixed-b.
- **Pesos.** Ecuación (6), p. 543: Bartlett k(v) = (1 − |v|)·1(|v| ≤ 1) con v = j/S, así que el retardo S tiene peso 0.

Nuestros pesos son 1 − j/(B + 1), así que B = S − 1. Cuarta configuración: B = ⌈1.3 n^{1/2}⌉ − 1, con n el número de
diferencias, calibrada dentro del bucle como las otras tres (lectura 3.3). Es la regla de truncamiento, no el valor crítico
fixed-b de LLSW: aquí el valor crítico es el simulado.

## 5. Sondas (sellado)

- **Sonda 151.** Celda MA(−0.8), n = 500, ct; 100 caminos; brazos (iii), (iv) y (v′) con R = 399.
- **Sonda 158.** La misma celda, 1000 caminos, cuatro configuraciones de B15.3.
- **Qué se registra.** El tiempo de pared por camino y brazo, los núcleos usados y la proyección de horas-núcleo para el
  diseño completo y tras cada reducción acumulada.
- **Sellado.** Los conteos de rechazo van bajo `"sealed"`. Los scripts de sonda no los imprimen, y ni los logs ni el
  reporte los leen hasta los JSON finales.
