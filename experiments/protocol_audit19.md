# Auditoría A19: correcciones de figura y suplemento antes del envío (sin simulación nueva)

Se commitea antes de empezar. Los productos llevan el sufijo `_audit19`. No se corre ninguna simulación ni se genera ninguna cifra nueva
de resultados. Se siguen las convenciones de siempre:
- generadores que solo leen JSON;
- commits por ruta explícita;
- `provenance.assistant` en cada JSON;
- manifiesto `experiments/results/manifest_audit19.json`;
- reporte `experiments/results/resultados_auditoria_19.md`, generado por `audit19_generate_report.py` y recorrido por
  `tests/test_no_literals_audit19.py`.

**Ubicación.** El encargo pide `protocols/A19.md`. El protocolo va en `experiments/protocol_audit19.md`, donde están todos los
anteriores (A8–A18). Ahí lo buscan `PROTOCOLS.md` del paquete, la lista de protocolos de S10 y los manifiestos. No se crea otra copia.

## 1. Encargo (literal)

Archivo `PROMPT_agente_A19.md` (escritorio), sha256 `12dd72ff885d5376c1851915101b2dc12b7e40b7038165e364ba9b94642592d0`.

```
# A19 — correcciones de figura y suplemento antes del envío (sin simulación nueva)

Contexto: el manuscrito pasó a v25 (cambios solo de texto y demostraciones; no toca código ni resultados). Dos revisiones externas
encontraron tres defectos en la figura y el suplemento. Esta auditoría los corrige y produce la versión v1.0.1 del paquete de
replicación. No se corre ninguna simulación nueva. Las convenciones de siempre: sufijo _audit19, protocolo commiteado antes de tocar
nada, commits por ruta explícita, campo provenance.assistant, generadores que solo leen JSON.

## Paso 0 — protocolo
Commitea protocols/A19.md con esta lista y las predicciones de abajo antes de editar nada.

## 1. Figura 1 (fig:calibgain) en caminos comunes
make_figures_audit13.py::gain_points13 mezcla cuatro fuentes: e_size_audit13.json (n ≤ 1000, 5×10⁴/10⁵ caminos),
b103_lown_audit10.json, b92_theta_audit9.json y e_calib_audit13.json. El texto de §4.2 dice «Table 1 and Figure 1 compare, on
common paths». Eso solo es cierto para la Tabla 1.
- Escribe make_figures_audit19.py, que genere la Figura 1 solo desde e_calib_audit13.json (2×10⁴ caminos comunes, la misma fuente
  que la Tabla 1). Mismo estilo, mismo nombre de salida con sufijo _audit19.
- Predicción: cada punto de la figura coincide con la celda correspondiente de la Tabla 1 al dígito impreso. Añade una prueba que
  lo verifique.
- Si e_calib_audit13.json no cubre todos los n de la figura actual, no inventes puntos ni mezcles fuentes. Para y repórtalo:
  cambiaré el texto de §4.2 en vez de la figura.
- Entrega el PDF de la figura y una tabla con los puntos viejos frente a los nuevos.

## 2. Regla de rechazo del AWB (A15)
La nota de S4 (supplement.tex:424) dice que el p-valor del AWB es #{S* ≤ S}/R. audit10_b103_awb.py:124 rechaza con p < C.ALPHA.
- Confirma, para el código que produjo las cifras de A15 citadas en §4.8 y S4, el valor de R y el operador (< o ≤).
- Predicción: con R = 399 y α = 0.05, #/R < α, #/R ≤ α y (1+#)/(R+1) ≤ α llevan a la misma decisión (# ≤ 19). Verifícalo con una
  prueba. Si R no es 399, calcula si las reglas coinciden y reporta.
- Añade una oración a la nota de la tabla S4.3: con ese R, la regla da la misma decisión que (1+#)/(R+1) ≤ α.

## 3. Suplemento (solo forma; ningún número cambia)
a. Quita «Bold entries follow the rule stated in its note.» de las leyendas de las 7 tablas que no tienen negritas (size02,
   localpower02, dgp1-02, ctpower02, dgp2-02, dgp5-02, fp02). Verifica con el PDF compilado que esas tablas no tienen negritas; si
   alguna sí las tiene, déjala y repórtalo.
b. Mueve la definición «RM: the centred rolling-means statistic…» (líneas ~50 y ~564) a la nota de cada tabla que tiene columna RM
   (S1 dgp1/ctpower; S5 dgp1/ctpower/dgp2/dgp3).
c. Saca de la subsección «The sieve bootstraps» (S2) el párrafo de invariancia y ponlo en su propia subsección o al inicio de S2.
d. Mueve la oración de SB/SWB (S4, línea ~489) del final de la subsección GARCH al final de la subsección de quiebres de varianza.
e. S7: la frase «it says nothing about the stochastic part» y la nota de que el teorema supone σ̂² = Θ_p(n^{-1/3}) ya no
   corresponden. En v25 el Apéndice A.5 demuestra (B+1)σ̂² →_p 2γ(0) con la identidad muestral exacta
   σ̂² = 2(Ĉ(0) − Ĉ(B+1))/(B+1). Cambia la frase por: «Appendix A.5 of the main text proves $(B+1)\hat\sigma^2 \to_p 2\gamma(0)$;
   the slope of 1/3 is that of the Andrews bandwidth.»
f. Recompila el suplemento: 0 errores, 0 avisos de referencias. Reporta el número de páginas antes y después.

## 4. Pruebas literales para el manuscrito v25
Añade a la batería de pruebas de números del paper:
- λ(−7) = 1225 exacto, con λ(c̄) = c̄²(c̄² + 3|c̄| + 5)/3;
- E[S²] exacto 0.360459, 0.431812 y 0.480933 en n = 200, 500 y 2000, usando E[YₙȲ] = (n−1)/2 y E[Ȳ²] = (n−1)(2n−1)/(6n), y su
  coincidencia con la fórmula tr Σ − 2·1′Σw + (n+1)w′Σw;
- |1/2 − κ/m + λ/m² − E[S²]| ≤ 4.8×10⁻⁶ para n ∈ {200, 500, 1000, 2000}, con m = n + 49;
- la identidad σ̂² = 2(Ĉ(0) − Ĉ(B+1))/(B+1) contra hac_newey_west, en B ∈ {0, 3, 7, 20, n−1}, con tolerancia 1e-12.

## 5. Paquete v1.0.1
- Revisa si el zip v1.0.0 (sha256 e990…bc08) incluye el manuscrito (main.tex o una carpeta del paper). Si lo incluye, sustitúyelo
  por las fuentes de v25 (paper_latex_v25.zip, que te paso aparte); si no, no lo agregues.
- Regenera MANIFEST.sha256 y el MANIFEST del suplemento.
- Sube la versión a 1.0.1 en CITATION.cff y el README. No cambies el DOI: 10.5281/zenodo.23424031 sigue siendo el mismo.
- Corre todas las pruebas (369 más las nuevas). Ninguna puede fallar.
- Reconstruye paper_estabilidad_replication.zip y reporta el sha256 nuevo y el número de archivos.
- En el repositorio público andrestellez84/m-unit-root-calibration: commit, tag y release v1.0.1, con el mismo zip byte por byte.
  Usa el correo noreply de GitHub.
- No hagas público el repositorio privado paper_estabilidad. No actives la integración GitHub–Zenodo. No toques Zenodo: el archivo
  del borrador lo reemplaza el autor.

## Entrega
Tabla con cada punto (hecho / no hecho / se detuvo, y por qué); figura vieja frente a nueva; R y el operador del AWB; páginas del
suplemento; pruebas (cuántas, todas en verde); sha256 y número de archivos del zip v1.0.1; enlace del release. Si un punto exige
cambiar una cifra del manuscrito, para y repórtalo antes de seguir.
```

## 2. Entradas

**E0.**
- `paper_latex_v25.zip` (escritorio), sha256 `7e5273a76bc2fa163290fcb588d6354a3f2deed738cbbfdf4c98e10a6d913728`.
- Su `supplementary/` es idéntico, archivo por archivo, al `supplementary/` del repositorio en `8688722`, el que dejó A18.
  `supplementary/supplement.tex` tiene sha256 `0b6e45cd754df554b5c0f258dc556dde0d9da2dcfc6be15a8e5c38ee808b3b91`.
- No se edita ningún `.tex` del manuscrito.

## 3. Lecturas operativas

### L1. Figura 1

**L1.1. Fuente única.** `make_figures_audit19.py` toma los tres trazos de `e_calib_audit13.json`, `cases_by_theta.gls_t0` (θ = 0, la
primaria y la misma clave que usa la Tabla 1 en `audit13_tables.py`), casos `c` y `ct`, para cada n de `F.GAIN_N`
(60, 100, 150, 200, 500, 1000, 2000, 5000):

| Trazo | Campo de `e_calib_audit13.json` | Columna de la Tabla 1 |
|---|---|---|
| `cv_at_n` | `approximation_cost.<n>.size_with_cv_at_n` | «at q(n)» |
| `cv_big` | `approximation_cost.<n>.size_with_cv_n20000` | «at q(20 000)» |
| `msb_pub` | `approximation_cost_comparators.<n>.msb.size_published_asymptotic` | MSB-GLS «asy.» |

N es el campo `n` de cada registro (2×10⁴), y la región sombreada es `exact_region(N)`. Si falta algún n, el script se detiene sin
dibujar y se reporta.

**L1.2. Estilo.** Se dibuja con `make_figures_audit11.fig_calibration_gain`, sin modificarlo, con la etiqueta de la primaria «MSB-B»,
como en `make_figures_audit13q.py`.
- **Salida.** `experiments/figures/fig_calibration_gain_audit19.pdf`. El PDF se limpia de fechas con `audit18_common.strip_pdf_dates`
  (E8.3).
- **JSON.** `experiments/results/figures_audit19.json` lleva los puntos nuevos con su ruta en el JSON, los puntos viejos (los de
  `figures_audit13.json`, `calibration_gain_points` de `gls_t0`, con su fuente original) y la tabla viejo/nuevo.
- `paper/` no se toca. La figura se entrega al autor, que cambia `\includegraphics` en el manuscrito.

**P1 (predicción).** Cada punto de la figura nueva, redondeado a 4 decimales, coincide con la celda correspondiente de
`experiments/results/tables_audit13/tab_calib_audit13.tex` (la Tabla 1 del v25, idéntica a `tables/tab_calib_audit13.tex` del zip).
Lo verifica `tests/test_figure1_audit19.py`.

### L2. Regla del AWB

**L2.1. Dos implementaciones.** El código contiene dos implementaciones del AWB.
- **(a) A15, MZ_t-GLS.**
  - Uso: brazo (iv); son las cifras del AWB en §4.8 del v25 y en `tab:boot` del suplemento.
  - Código: `audit15_boot_engine.pvalue_awb` devuelve (1 + #{T* ≤ T})/(R + 1), y `audit15_b1_boot.py` rechaza con `p <= C.ALPHA`.
  - R: R = 399 (`audit15_design.R`; `b1_boot_audit15.json` registra `config.R` = 399 y la configuración `full`).
- **(b) A13, RM-GLS (MSB-B).**
  - Uso: son las cifras de `tab:awb` (S4.3) y de §4.9 del v25.
  - Código: `audit13_e_awb.py` rechaza con `p < C.ALPHA`, con p = #{S* ≤ S}/B (`e_awb_audit13.json`, `config.pvalue`).
  - R: B = R = 399.
  - `audit10_b103_awb.py:124`, citado en el encargo, es la versión de A10 con el mismo operador. No produce cifras del v25.

`audit19_awb_rule.py` lee esos campos de los JSON y cita las líneas del código con su sha256. Salida: `awb_rule_audit19.json`.

**P2 (predicción).** Con R = 399 y α = 0.05, para todo # ∈ {0, …, 399} las tres reglas dan la misma decisión: #/R < α, #/R ≤ α y
(1+#)/(R+1) ≤ α. Las tres rechazan si y solo si # ≤ 19.
- Se verifica en aritmética exacta (`fractions`) y en coma flotante, como lo calcula el código.
- Lo comprueba `tests/test_awb_rule_audit19.py`.
- Si R no fuera 399, se calcula la coincidencia y se reporta.

**L2.2. Nota de S4.3.** Al final de la nota de `tab:awb` se añade:

«With $R = 399$, rejecting when $\#/R < 0.05$ gives the same decision as $(1 + \#)/(R + 1) \leq 0.05$: both reject exactly when
$\# \leq 19$.»

Los números R y 19 se leen de `awb_rule_audit19.json`.

### L3. Suplemento (`audit19_supplement.py`)

**L3.0. Paso 0.** El script parte de `supplementary/supplement.tex` tal como lo dejó A18 y exige que su sha256 sea el de E0. Cada
edición es una sustitución con un ancla que debe aparecer exactamente una vez, y queda registrada en
`experiments/results/supplement_v25_audit19.json`. No se vuelve a correr la cadena A16–A18.

**L3.a. Leyendas sin negritas.**
- Se quita « Bold entries follow the rule stated in its note.» de las leyendas de `tab:size02`, `tab:localpower02`, `tab:dgp102`,
  `tab:ctpower02`, `tab:dgp202`, `tab:dgp502` y `tab:fp02`.
- Primero se verifica:
  - en la fuente, que el `.tex` de cada tabla no contiene `\textbf`;
  - en el PDF compilado (PyMuPDF), que en la franja de la página de cada tabla, desde su leyenda hasta la siguiente leyenda o el
    pie, no hay ningún span numérico en negrita.
- Si una tabla tiene negritas, su leyenda se deja y se reporta.
- Las otras cuatro leyendas (`calib02`, `dgp302`, `misspec02`, `awb02`) no se tocan: sí tienen negritas.

**L3.b. Definición de RM.**
- Se quitan las dos líneas «RM: the centred rolling-means statistic with $\theta = 0.1$.» (inicio de S1 y de «Tables with
  θ = 0.02» en S5).
- La oración se añade a la nota de **cada** tabla que tiene una columna RM. Se detectan por el encabezado `& RM &` del `.tex` que
  incluyen.
- Son ocho: `tab:dgp1` y `tab:ctpower` (S1), `tab:dgp2` y `tab:dgp3` (S4), y `tab:dgp102`, `tab:ctpower02`, `tab:dgp202` y
  `tab:dgp302` (S5).
- **Lectura.** El encargo enumera seis y omite las dos de S4. Se aplica la regla («cada tabla que tiene columna RM»), porque sin la
  definición al inicio de S1 las tablas de S4 quedarían sin ella. Se reporta.
- Donde la tabla tiene nota, la oración se añade al final. Las cuatro tablas de S5 no tienen nota: se les añade una con el mismo
  formato que `tab:dgp502` (`\par\medskip\begin{minipage}{\textwidth}\footnotesize … \end{minipage}`).

**L3.c. Invariancia.** El párrafo «The invariance of Proposition~2 …» sale de «The sieve bootstraps». Va, sin cambios, en una
subsección propia, `\subsection*{A numerical check of invariance}`, inmediatamente antes de `\subsection*{The sieve bootstraps}`.

**L3.d. SB/SWB.** La oración «The sieve bootstrap (SB) and the sieve wild bootstrap (SWB) calibrations of MZ$_t$-GLS were not
evaluated under variance breaks.» sale del final de S4. Se inserta como párrafo propio al final de la subsección «Variance breaks and
the wild-bootstrap calibration», inmediatamente antes de `\subsection*{Heavy tails and conditional heteroskedasticity}`.

**L3.e. S7.**
- La oración «The slope of 1/3 follows from the Andrews rule once $\hat a$ settles; it says nothing about the stochastic part.» se
  sustituye entera por la del encargo.
- La búsqueda previa (`supplement.tex`, `tables/` y `README.md`) no encontró ninguna nota que diga que el teorema supone
  σ̂² = Θ_p(n^{-1/3}) aparte de esa oración. Se repite en el script, y si aparece se reporta sin editar.
- Se comprueba en la compilación del v25 que `thm:consistency` se demuestra en la subsección A.5 del apéndice.

**L3.f. Compilación.**
- Se usa `audit16_supplement.compile_check` (pdflatex, bibtex y pdflatex ×2), antes y después de las ediciones, en copias en el
  directorio temporal.
- Criterio: 0 errores, 0 referencias y 0 citas indefinidas.
- Se reportan las páginas antes y después.

**L3.g. Remisiones al cuerpo (control).**
- Se compila el v25 (pdflatex ×2 en una copia temporal) y se compara cada etiqueta de `body_labels` de
  `supplement_v18b_audit18.json` con su número en el `.aux` del v25.
- Si cambia alguna etiqueta a la que remite el suplemento, se detiene y se reporta antes de corregir.

**L3.h. Cierre.** Se regenera `supplementary/MANIFEST.sha256` y se repite la búsqueda de identificadores de A18.

### L4. Pruebas literales del v25

Las pruebas van en `tests/test_literals_v25_audit19.py`, en aritmética exacta (`fractions`).
- **λ(−7) = 1225**, y κ(−7) = 2·7·(1/2 + 7/3), que el texto redondea a 39.7.
- **E[S²] exacto.** Con Y₀ = 0, σ = 1 y c̄ = −7:
  - fórmula: E[S²] = 1/2 − 2E[β̂ ΣY]/(n(n+1)) + E[β̂²]/n;
  - momentos: E[YₙȲ] = (n−1)/2, E[Ȳ²] = (n−1)(2n−1)/(6n) y E[Yₙ²] = n;
  - control: debe dar 0.360459, 0.431812 y 0.480933 (6 decimales) en n = 200, 500 y 2000;
  - redondeo del texto: 0.360, 0.432 y 0.481;
  - comprobación independiente: la forma matricial (tr Σ − 2·1′Σw + (n+1)w′Σw)/(n(n+1)), con Σᵢⱼ = min(i, j) en t = 0…n y β̂ = w′Y,
    debe coincidir exactamente.
- **Cota de la expansión.** |1/2 − κ/m + λ/m² − E[S²]| ≤ 4.8×10⁻⁶ en n ∈ {200, 500, 1000, 2000}, con m = n + 49. Además, el primer
  orden 1/2 − κ/n da 0.302, 0.421 y 0.480 (texto de A.4).
- **Identidad de Bartlett.** σ̂² = 2(Ĉ(0) − Ĉ(B+1))/(B+1) frente a `hac_newey_west(Δx, bandwidth=B)`, con:
  - Ŝ_t = (x_t − x₀) − (t/n)(xₙ − x₀) y Ĉ(k) = n⁻¹ Σ_t Ŝ_t Ŝ_{t+k}, extendido por cero;
  - B ∈ {0, 3, 7, 20, n−1}, n = 200;
  - series con semilla fija dentro de la prueba: ruido i.i.d., AR(0.5) y MA(−0.8);
  - tolerancia absoluta 1e-12.

No hay predicción que pueda fallar sin indicar un error del texto. Si alguna falla, se detiene y se reporta: sería una cifra del
manuscrito.

### L5. Paquete v1.0.1

- **Manuscrito.** El zip v1.0.0 (sha256 `e990732841e200956a8b1fa3ec5a59d34956b20bab7599f27d4ca5cf4a69bc08`) no contiene el manuscrito:
  ni `main.tex` ni una carpeta del paper (comprobado con la lista del zip). No se agrega.
- **Partida.** El paquete v1.0.1 parte del v1.0.0 y se le añaden:
  - los scripts, pruebas, resultados y la figura de A19, el protocolo y el reporte;
  - el `supplementary/` actualizado.
- **README.**
  - Figura 1 → `make_figures_audit19.py`. La línea del v1.0.0 decía que la Figura 1 salía de `e_calib_audit13.json` con
    `make_figures_audit13q.py`, y eso no era exacto.
  - Versión 1.0.1.
- **Otros documentos.** Se actualizan `PROTOCOLS.md`, `SCRIPTS.md` y `CITATION.cff` (versión 1.0.1; el DOI no cambia).
- **MANIFEST.**
  - Se regenera `MANIFEST.sha256`.
  - Corrección: el raíz pasa a incluir `supplementary/MANIFEST.sha256`. El v1.0.0 lo omitía porque el script excluía cualquier
    archivo con ese nombre.
- **Pruebas.** Se corren todas las pruebas desde una copia limpia extraída del zip. Ninguna puede fallar.
- **Repositorio público.**
  - Commit con el correo noreply, tag y release v1.0.1.
  - El árbol del tag debe ser idéntico, byte por byte, al contenido del zip.
- **Prohibido.** No se toca el repositorio privado, ni la integración GitHub–Zenodo, ni Zenodo.

## 4. Condiciones de parada

Se detiene y se reporta antes de seguir si:
- `e_calib_audit13.json` no cubre algún n de la figura;
- falla P1, P2 o alguna prueba de L4;
- una edición del suplemento no encuentra su ancla exactamente una vez;
- cambia una remisión al cuerpo (L3.g);
- cualquier punto exige cambiar una cifra del manuscrito.
