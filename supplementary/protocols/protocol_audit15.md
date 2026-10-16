# Protocolo de A15

Se registra y se commitea antes de cualquier cómputo de A15. La predicción (`prediccion_boot_audit15.md`), con el
pronóstico del autor, se commitea en un commit propio antes de B15.1 y B15.3; ninguno de esos dos bloques corre sin
ese commit ni sin la confirmación escrita del autor tras la sonda.

## 1. Encargo (literal)

```
AUDITORÍA 15 — sufijo _audit15. Convenciones de A12–A14 sin excepción.

REGLAS
- protocol_audit15.md y prediccion_boot_audit15.md commiteados ANTES de
  B15.1 y B15.3; hashes de ambos commits en el reporte.
- Familias 151–159. La 150 sigue reservada sin uso (A14); decláralo.
  Comprueba que 151–159 no colisionan con 90–150.
  Asignación:
    151  sonda B15.1
    152  tamaño B15.1
    153  potencia B15.1
    154  series del Paso 0 contra bootUR
    155  calibración B15.3
    156  tamaño B15.3
    157  potencia B15.3
    158–159  reserva
- Paso 0 (regla de A13): |Δ| = 0 en las columnas usadas; ≤ 1e-12, con
  declaración, en las demás.
- Generadores que solo leen JSON; test_no_literals_audit15.py.
- src/ no se toca sin control de regresión.
- Compuerta numérica y sonda de presupuesto antes de cada bloque caro.
  El autor confirma por escrito antes de lanzar B15.1 y B15.3.
- NUEVO: cada JSON de A15 lleva provenance.assistant = {herramienta,
  modelo, versión} del agente que lo produjo.
- Reporte resultados_auditoria_15.md con las siete secciones y tabla maestra.

B15.0 — Comparación iid/asintótico desde bA_ma_audit12.json (sin simulación)
- Verifica el sha256 de bA_ma_audit12.json contra manifest_audit12.json.
- Para las 36 celdas y los procedimientos msb, mzt, msb_pq, mzt_pq y dfgls,
  toma iid.rate y asy.rate y calcula:
  (a) número de celdas con iid > asy;
  (b) media y máximo de |rate − 0.05| sobre las 30 celdas con ψ ≠ 0, por
      procedimiento y caso;
  (c) conteo «más cerca de 0.05» por grupo (ψ = −0.8; {ψ = −0.5, φ = −0.5};
      ψ = 0; {+0.5}) × caso;
  (d) rangos de iid − asy por caso.
- Salidas: b0_iidasy_audit15.json y tables/tab_serial_asy_audit15.tex.
- Confirma o corrige con su valor exacto cada literal del parche T3:
  0.6; 0.4–4.3; 0.0142; 0.0130; 0.062–0.092; 0.036–0.050; 0.142; 36; 30.
  Si alguno no coincide, va a Anomalías; NO edites el .tex.

B15.0b — Tamaño condicionado al retardo elegido (checkpoints de A12; sin
números aleatorios)
- Celdas sz_ar_0p5_n100_ct, sz_ma_0p5_n100_ct, sz_ma_m0p8_n200_c y
  sz_ma_0_n100_ct: tasa iid y asy de mzt y msb por k ∈ {0, 1, 2, ≥3}, con
  Wilson y el número de caminos por k.
- La misma tabla bajo la nula iid de A10, si hay filas por camino con k.
  Si no las hay, «No ejecutado».
- Solo descriptivo.

B15.1 — Bootstrap de MZ_t-GLS bajo correlación serial (caro)
Brazos, todos sobre los mismos caminos:
  (i)   valor asintótico NP2001;
  (ii)  valor iid de b1_critical_audit14.json;
  (iii) sieve bootstrap basado en diferencias con la nula impuesta:
        AR(p) sobre Δy centrado, p por AIC con pmax = ⌊12(n/100)^{1/4}⌋;
        residuos centrados remuestreados iid; y* acumulado; MZ_t-GLS* con la
        MAIC GLS (sin Perron–Qu) re-elegida en cada réplica;
  (iv)  AWB de def:awb aplicado a MZ_t-GLS;
  (v)   sieve wild bootstrap de Cavaliere–Taylor (2009, Econometric Reviews
        28(5), 393–421), con recoloreado si el artículo lo especifica.
        Requiere el PDF. Sin el PDF: «No ejecutado», sin improvisar.
  R = 399 réplicas; p-valor por rango.

Paso 0:
- (iii) contra bootUR::boot_adf(detrend = "QD", bootstrap = "SB",
  criterion = "MAIC", criterion_scale = FALSE).
- (v) contra bootstrap = "SWB".
- Sobre 200 series de la familia 154, replicando la corrección de
  Perron–Qu que bootUR aplica:
    estadístico |Δ| ≤ 1e-10; retardo |Δ| = 0;
    media de |Δp| ≤ 0.02;
    tamaño sobre 2000 caminos iid dentro de la región exacta.
- Compuerta: si falla (iii), se detiene B15.1; si falla (v), solo se
  detiene (v).
- Declara como desviación que los brazos principales usan la MAIC GLS sin
  Perron–Qu, igual que tab:serial.

Diseño:
- Tamaño: 36 celdas × N = 5000.
- Potencia: n = 200, casos c y ct; ρ ∈ {0.90, 0.95} con errores iid y con
  MA(−0.5); N = 2000.
- Reporta potencia bruta y ajustada; umbral = cuantil 5 % del p-valor en la
  celda nula del mismo proceso de error.

Sonda:
- Familia 151: celda MA −0.8, n = 500, ct; 100 caminos por brazo.
- Proyecta horas-núcleo.
- Reducciones, en este orden y escritas en el protocolo antes de computar:
  (1) R = 199;
  (2) 18 celdas (ψ ∈ {−0.8, +0.5}, φ = +0.5; todas las n; ambos casos);
  (3) sin (iv).

PREDICCIÓN (definiciones commiteadas antes de computar):
- D(arm) = media de |size − 0.05| sobre las celdas con ψ ≠ 0;
  M(arm) = máximo de esa desviación.
- «Domina en tamaño» si se cumplen las tres:
  D ≤ D(ii) − 0.005,  M ≤ M(ii) − 0.010,
  y el brazo en la región exacta en las 6 celdas iid.
- «Sin costo» si, en toda celda de potencia, la potencia ajustada es
  ≥ la de (ii) − 1.0 pp, o McNemar exacto p ≥ 0.05.
- Se evalúa por separado para (iii) y (v).
- Desenlaces: A = algún brazo domina y sin costo; C = domina con costo;
  B = ninguno domina.
- El autor registra su pronóstico en el mismo commit.

B15.2 — Pendientes
(a) Commitear experiments/audit5_tarea5.py y experiments/audit4_tarea_E.py
    con los sha256 que registró A14 (§7(c)); si difieren, Anomalías.
(b) audit4_tarea_E.py: recalcular la pendiente de B antes del techo con el ρ̂
    de la librería (divisor n en γ0 y γ1) frente al ρ̂ en línea (np.var y
    np.cov con ddof = 1). Reporta ambas y |Δ|. Guarda e4_slope_audit15.json
    con semilla 42, 500 réplicas y medias por n.
(c) Nada más: A14 ya localizó 0.003 y 0.333.

B15.3 — Fixed-b sobre MSB-B (caro; confirmación del autor)
- MSB-B con Bartlett y B = ⌈b·n⌉, b ∈ {0.1, 0.3, 1.0}.
- Si puedes extraer de Lazarus–Lewis–Stock–Watson (2018, JBES 36(4)) su
  regla de truncamiento para Newey–West, añádela como cuarta configuración,
  citando tabla y ecuación; si no, no la inventes.
- Autocovarianzas por FFT; Paso 0: FFT frente a suma directa, |Δ| ≤ 1e-12
  sobre 100 series.
- Calibración iid dentro del bucle, familia 155, N_cal = 1e5 por
  (n, caso, b); declara la cota DKW.
- Tamaño: 36 celdas de tab:serial, N = 2e4, familia 156.
- Potencia ajustada: 7 AR de DGP 1, n = 200, caso constante, N = 5000,
  familia 157.
- Sonda y compuerta como en B15.1.
- Predicción registrada: «fixed-b controla el tamaño» si, para algún b,
  M(b) ≤ 0.02 sobre las celdas con ψ ≠ 0; costo de potencia medido frente a
  MSB-B con Andrews y frente a (b).

B15.4 — Coherencia (tipo B13.Q Q3) sobre el v17, cuando exista, incluyendo:
- en cada nota de tabla de potencia, el error Monte Carlo máximo;
- que no reaparezcan las cifras 6.9 % y 0.6 %.

B15.5 — Anonimización para revisión doble anónima
- Inventario de todo lo que identifica al autor en el paquete de
  replicación y en el suplemento: rutas, nombres de usuario, URLs de
  repositorio, hashes que enlacen a un repositorio público, metadatos de PDF.
- Propón la versión anonimizada, sin tocar el repositorio original.
```

## 2. Lecturas operativas

### Generales

**G1. Sufijo, familias y archivos intocables.** Todo archivo nuevo lleva `_audit15`. Familias: 151 sonda B15.1; 152
tamaño B15.1; 153 potencia B15.1; 154 Paso 0 contra bootUR; 155 calibración B15.3; 156 tamaño B15.3; 157 potencia
B15.3; 158 sonda de B15.3 (el encargo no asigna familia a esa sonda; se toma de la reserva y se declara); 159 reserva.
La 150 sigue reservada y sin uso. Semillas: `SeedSequence(familia, spawn_key=(celda, i))`, como en A8–A14. La
comprobación de colisiones (palabra 0 de `generate_state`, método de A8–A13) compara todos los streams de 151–158
frente a los de las familias 90–150 que tienen streams, las semillas enteras de A5–A7 y la 42 de producción; corre en
el inventario B15.I, antes de B15.1. Son de sólo lectura: los `.tex`, `src/`, `experiments/data/*.csv`,
`experiments/protocol.md`, `experiments/results/real_data_results.json` y los JSON de auditorías anteriores.

**G2. Procedencia del asistente.** Cada JSON de A15 lleva `provenance.assistant = {"herramienta": "Claude Code",
"modelo": "claude-opus-5-5", "version": <salida de "claude --version">}`. Si la versión no se puede leer, el campo
dice `null` y se declara.

**G3. Paso 0.** Regla de A13: |Δ| = 0 en las columnas que el bloque usa; ≤ 1e-12, con declaración, en las demás.

**G4. Generadores.** Tabulares, reporte y cualquier texto con cifras se generan sólo desde JSON, bajo
`tests/test_no_literals_audit15.py`. No se toca `src/`: todo el código nuevo va en `experiments/`.

### B15.0

**0.1.** Se verifica el sha256 de `bA_ma_audit12.json` contra `manifest_audit12.json`
(`entries."experiments/results/bA_ma_audit12.json".sha256`). Si difiere, B15.0 se detiene.

**0.2.** «ψ ≠ 0» son las 30 celdas cuyo error no es `ma_0` (incluye AR(±0.5)); 15 por caso. (a) cuenta, por
procedimiento, las celdas con iid.rate > asy.rate (y aparte las iguales). (b) media y máximo de |rate − 0.05| sobre
esas 15 celdas por procedimiento, caso y bloque (iid y asy). (c) por procedimiento, grupo × caso, cuántas celdas
tienen iid más cerca de 0.05 que asy, cuántas al revés y cuántas empatan; grupos: {ma_m0p8}; {ma_m0p5, ar_m0p5};
{ma_0}; {ma_0p5, ar_0p5}. (d) mínimo y máximo de iid.rate − asy.rate por procedimiento y caso.

**0.3. Tabular.** `results/tables_audit15/tab_serial_asy_audit15.tex`, con las filas de tab:serial (error, n, caso)
y, para MSB-GLS, MZ_t-GLS, MSB-GLS (PQ), MZ_t-GLS (PQ) y DF-GLS, dos columnas: valor crítico iid y asintótico, a 3
decimales con redondeo binario; negrita fuera de la región exacta de 2×10⁴ caminos, como en tab:serial.

**0.4. Parche T3.** El texto del parche no está en ningún archivo entregado (ni en el v16 ni en los traspasos). Sin
él, cada literal se compara con la magnitud de B15.0 a la que razonablemente se refiere, y la asignación se declara
en el reporte; si el autor entrega el texto, la asignación se fija en una enmienda antes de comparar. Un literal sin
magnitud asignable va a Anomalías como «sin asignar», no se inventa.

### B15.0b

**0b.1.** Filas por camino de `checkpoints/audit12_bA/<celda>_i*.npz` (columnas `COLS_A` de `audit12_unitroot`,
incluida `k`, el retardo de la MAIC GLS). Decisión iid: `mzt < q`, `msb < q` con q de
`bA_ma_audit12.json config.iid_quantiles.<n>|<caso>`; asintótica: `NP_CV5` de `audit8_unitroot` (la regla de
`audit9_engine.reject_asy`). Paso 0: la tasa agregada sobre todos los k es igual (|Δ| = 0) a `iid.rate` y `asy.rate`
de `bA_ma_audit12.json`. Wilson al 95 %.

**0b.2. Nula iid de A10.** `audit10_cal/cal_n<n>.npz` tiene `c|k` y `ct|k` por camino; se hace la misma tabla con
n = 100 (caso ct) y n = 200 (caso c), que son los (n, caso) de las cuatro celdas. Umbral iid: el mismo q; su tasa
agregada es 0.05 por construcción.

### B15.1

**1.1. Trayectorias.** Las de A12 (`audit12_unitroot.null_path` y `alt_path`, con e₀ = 0 en el MA, AR estacionario
en el arranque, y₀ = 0), con familias nuevas: 152 para las 36 celdas de tamaño (N = 5000) y 153 para las 8 de
potencia (n = 200; c y ct; ρ ∈ {0.90, 0.95}; errores `ma_0` y `ma_m0p5`; N = 2000). Los cinco brazos se evalúan
sobre los mismos caminos.

**1.2. Brazos (i) y (ii).** (i) rechaza si MZ_t-GLS < `NP_CV5[caso]["MZt"]` (−1.98 y −2.91; Ng–Perron 2001). (ii)
rechaza si MZ_t-GLS < q_0.05 de `b1_critical_audit14.json` para (n, caso). MZ_t-GLS con la MAIC GLS de
`audit8_unitroot.np_statistics` (sin Perron–Qu), como en tab:serial.

**1.3. Brazo (iii), sieve.** Sobre Δy (n valores) centrado, AR(p) por MCO sobre la muestra común de pmax =
⌊12(n/100)^{1/4}⌋ retardos, p ∈ {0, …, pmax} por AIC; residuos centrados remuestreados iid; u* por la recursión
AR y y* = acumulado, con la inicialización del SB de bootUR 1.0.5. Las reglas exactas (estimador del AR,
arranque, quemado) se leen del código fuente de bootUR 1.0.5 y se registran en una enmienda antes del Paso 0, sin
calcular nada con ellas antes. En cada réplica se recalcula MZ_t-GLS* con la MAIC GLS re-elegida.

**1.4. Brazo (iv), AWB.** El de def:awb sobre MZ_t-GLS: ê_t = Δy_t − media, ξ_t AR(1) gaussiano con γ = 0.01^{1/l},
l = round(1.75 n^{1/3}), ε*_t = ξ_t ê_t, y* acumulado, MZ_t-GLS* con la MAIC GLS re-elegida.

**1.5. Brazo (v).** Sólo si el autor entrega el PDF de Cavaliere–Taylor (2009). Sin él: «No ejecutado». Con él, sus
reglas se registran en una enmienda antes de computar.

**1.6. p-valor.** p = (1 + #{T* ≤ T})/(R + 1), cola inferior; se rechaza si p ≤ 0.05 (con R = 399, nivel exacto 20/400).
Desviación declarada frente a def:awb, que define B⁻¹#{T* ≤ T}.

**1.7. Paso 0 contra bootUR (familia 154).** 200 series de n = 200: 100 bajo la nula iid y 100 bajo la nula MA(−0.5),
50 de cada caso (c, ct) en cada grupo. Nuestra réplica del SB aplica el estadístico ADF sobre datos QD con la MAIC
de Perron–Qu como hace bootUR (`criterion_scale = FALSE`). Criterios:

- estadístico |Δ| ≤ 1e-10;
- retardo |Δ| = 0;
- media de |Δp| ≤ 0.02, con B = 399 en los dos lados; los remuestreos de R y de Python no son los mismos, por eso
  hay tolerancia;
- tamaño de nuestra réplica sobre 2000 caminos iid de n = 200, por caso, dentro de la región binomial exacta de 2000.

Compuerta: si falla (iii), B15.1 se detiene; (v) sólo con el PDF.

**1.8. Potencia ajustada.** Para (iii)–(v), el umbral es el cuantil 5 % (`numpy.quantile`, lineal) de los p-valores
del brazo en la celda nula del mismo error, n = 200 y caso: `sz_ma_0_n200_<caso>` para errores iid y
`sz_ma_m0p5_n200_<caso>` para MA(−0.5). Para (i) y (ii), el cuantil 5 % de MZ_t-GLS en esa celda. Se reporta la
potencia bruta y la ajustada.

**1.9. Sonda (familia 151).** Celda MA(−0.8), n = 500, ct; 100 caminos por brazo con R = 399; se mide el tiempo de
pared por camino y brazo y se proyectan horas-núcleo para el diseño completo y tras cada reducción acumulada en el
orden del encargo: (1) R = 199; (2) 18 celdas: errores ma_m0p8, ma_0p5 y ar_0p5, todas las n, ambos casos; (3) sin
(iv). El autor elige la configuración al confirmar por escrito.

**1.10. Predicción.** Definiciones del encargo, en `prediccion_boot_audit15.md`. «Celdas iid» son las 6 celdas
`ma_0`; «región exacta» es la binomial exacta de N = 5000 (o del N que quede tras las reducciones). McNemar exacto
bilateral, pareado sobre los caminos, brazo frente a (ii), con la decisión ajustada. Si la reducción (2) deja fuera
celdas `ma_0`, la condición de región exacta se evalúa sobre las `ma_0` que queden, y se declara.

**1.11. Desviación declarada.** Los brazos principales usan la MAIC GLS sin Perron–Qu, igual que tab:serial; sólo el
Paso 0 usa la de Perron–Qu que aplica bootUR.

### B15.2

**2.1.** (a) El sha256 en disco de `audit5_tarea5.py` y `audit4_tarea_E.py` se compara con el que registró A14
(`b2_sources_audit14.json figures.<i|iv>.script.sha256`); se commitean tal cual. Si difieren, Anomalías.

**2.2.** (b) Se replica `audit4_tarea_E.py` sin editarlo: `default_rng(42)`, los tres procesos en su orden (RW, AR
0.95, AR 0.5), n ∈ {200, 500, 1000, 2000, 5000}, 500 réplicas, la misma secuencia de extracciones. En cada camino
se calcula B_pre con dos ρ̂: (1) el del script, tal como está escrito (`np.var(diffs)`, que usa ddof = 0, y
`np.cov(diffs[:-1], diffs[1:])[0, 1]`, que usa ddof = 1 y medias separadas); el encargo describe los dos con ddof =
1, y se declara la diferencia; (2) el de la librería (`hac_estimator.hac_newey_west`: serie centrada con la media
completa, γ0 y γ1 con divisor n). Paso 0: el ρ̂ del script reproduce las columnas de `resultados_auditoria_4_E.md` a
los 4 decimales publicados (slope_B_pre, R2_B_pre, slope_B_ceil y R2_B_ceil en las columnas usadas; slope_g1_std y
slope_g2_std, recalculadas con las funciones de `src` sin tocarlas, en las demás). Salida `e4_slope_audit15.json`:
medias por n de B_pre y B_ceil, pendientes y R² con los dos ρ̂, y |Δ| entre ellos.

### B15.3

**3.1. Estadístico.** MSB-B (S₀ de eq:statzero) con σ̂² el Bartlett de las primeras diferencias centradas de
`hac_estimator.hac_newey_west`, con ancho fijo B = min(⌈b·n⌉, n − 1), n el número de diferencias, b ∈ {0.1, 0.3, 1.0}.
Autocovarianzas por FFT (con relleno de ceros a ≥ 2n). Paso 0 (compuerta numérica): sobre las 100 primeras series de
calibración de la familia 155 con n = 200, σ̂² por FFT frente a la suma directa, |Δ| ≤ 1e-12 relativo a σ̂², en los
tres b y con el ancho de Andrews, que debe reproducir `hac_sigma_sq`.

**3.2. LLSW (2018).** Sin el PDF de Lazarus–Lewis–Stock–Watson no se añade la cuarta configuración: la regla debe
citarse con tabla y ecuación y no se reconstruye de memoria.

**3.3. Calibración (familia 155).** Paseo aleatorio gaussiano (y₀ = 0), N_cal = 10⁵ caminos por n ∈ {100, 200, 500};
los mismos caminos sirven a los dos casos y a los tres b (números aleatorios comunes). σ̂ dentro del bucle. Rechazo por
la FDA empírica de la calibración (`cdf_from_null_stats`, la regla de MSB-B en A12). Cota DKW: ε = [ln(2/0.05)/(2
N_cal)]^{1/2} con probabilidad 0.95. En n = 200 caso c se calculan también MSB-B con Andrews y la variante (b) sobre
los mismos caminos, para la potencia ajustada.

**3.4. Tamaño (familia 156).** Las 36 celdas de tab:serial (errores, n y casos de A12), N = 2×10⁴.

**3.5. Potencia ajustada (familia 157).** DGP 1: AR(1) con errores iid gaussianos, ρ ∈ {0.80, 0.85, 0.90, 0.93, 0.95,
0.97, 0.99}, n = 200, caso constante, N = 5000. La nula iid es la de la calibración, así que la potencia calibrada es
la ajustada. Se compara con MSB-B con Andrews y con (b), con diferencias pareadas y McNemar exacto.

**3.6. Sonda (familia 158) y compuerta.** 1000 caminos de la celda MA(−0.8), n = 500, ct, con los tres b; se proyectan
horas-núcleo. La compuerta es el Paso 0 de 3.1. El autor confirma por escrito.

**3.7. Predicción.** «Fixed-b controla el tamaño» si, para algún b, M(b) ≤ 0.02 sobre las 30 celdas con ψ ≠ 0.

### B15.4 y B15.5

**4.1.** B15.4 espera al v17; no se ejecuta en A15 si el v17 no existe.

**5.1. Alcance de B15.5.** El paquete de replicación es `supplementary/`, más los archivos del repositorio que
necesita `supplementary/reproduce.ps1`; el suplemento es lo que lista `SUPPLEMENT_PLAN.md` del v16. Se inventarían,
con archivo y línea:

- nombres y correos del autor, incluidos `CITATION.cff` y `pyproject.toml`;
- URLs de repositorios;
- hashes de commit que enlacen a un repositorio;
- metadatos de los PDF (autor, creador, productor, fechas).

**5.2.** La propuesta anonimizada es un mapa de reemplazos más un script que construye una copia anonimizada fuera del
repositorio. La construcción de prueba se hace en el directorio temporal de la sesión y se verifica que no queden
aciertos. El repositorio original no se modifica.

### Reporte

**R1.** `resultados_auditoria_15.md` con las siete secciones y la tabla maestra; incluye los hashes del commit de este
protocolo y del de la predicción.
