# Enmienda 5 al protocolo de A15: B15.8 (mantenimiento), B15.7b (correcciones del generador del suplemento) y B15.9

Se commitea antes de ejecutar nada de lo que regula. Sin simulación.

## 1. Encargo (literal)

```
B15.8 — Mantenimiento del repositorio (confirmado por el autor)
1. git bundle create ../backup_pre_gc.bundle --all ; verifica el bundle
   (git bundle verify).
2. git reflog expire --expire-unreachable=now --all ; git gc --prune=now.
   Reporta el tamaño de .git antes y después (git count-objects -vH).
3. Añade a .gitignore los checkpoints *.npz de experiments/results/ y las
   muestras de calibración de A10. Commitea el .gitignore. Comprueba con
   git status que ningún resultado versionado queda ignorado.

B15.7b — Correcciones del generador del suplemento (NO reconstruir aún)
a. Tablas 3 y 26: cabecera de 6 columnas frente a 5 valores por fila.
   Diagnostica y corrige.
b. Tablas 5 y 6: etiquetas legibles en lugar de las claves internas.
c. S6: títulos descriptivos, no «Table <clave> of the main text».
d. Elimina la tabla 24 (duplica la 11).
e. Define RM en las notas de S1 y S6 (estadístico centrado de medias
   rodantes, θ = 0.1).
f. p-valores con un solo formato: <0.001 por debajo de 0.001; tres
   decimales en el resto.
g. Tabla 23: «N» → «normal».
h. Tabla 27: comprueba que existe la nota de la marca «a» de KPSS.
La reconstrucción completa se hace después del v17, con la lista de tablas
que pasan del cuerpo al suplemento (sigue abajo).

B15.9 — Tabulares para el v17 (solo lectura de JSON; redondeo binario)
1. tables/tab_summary_audit15.tex, más su nota.
   Filas: MSB-B con Andrews (A12); MSB-B fixed-b con b = 0.3 (A15);
   MSB-GLS iid (A12); MZ_t-GLS asintótico, iid, SB (bootUR), SWB (bootUR) y
   AWB (A15); DF-GLS iid (A12); ADF iid (A12).
   Columnas: D y M sobre las 30 celdas con ψ ≠ 0; mínimo y máximo sobre
   las 36; celdas iid dentro de la región exacta de su N;
   potencia ajustada a ρ = 0.90, n = 200, caso constante, errores iid.
   Declara la fuente de cada celda de potencia. Si una fila no tiene
   potencia medida en esa celda, pon «–» y explícalo en la nota; no la
   estimes.
   Nota: N por fila (2×10⁴ en A12, 5000 en A15) y la región de cada N.
2. Lista de tablas que pasan al suplemento en la reconstrucción:
   tab:serial, tab:boot, tab_serial_asy, tab_fixedb_size, tab_lag,
   tab:size, tab:dgp1, tab:ctpower, tab:dgp2, tab:dgp3, tab:misspec,
   tab:awb, tab:dgp5, tab:initial, tab:serialpower, tab:critB y las seis
   figuras; más el texto de sec:theta con tab:deviations, y la aplicación
   completa (sec6 y tab:fp).
3. Descarga la plantilla LaTeX oficial de Taylor & Francis para Journal of
   Statistical Computation and Simulation (Interact). Registra la URL, la
   versión y el sha256, e indica qué estilo de referencias pide.

Envíame: los tabulares de tables_audit15/ (tab_boot, tab_bootpower,
tab_fixedb, tab_fixedb_size, tab_summary y sus notas) y la plantilla.
```

## 2. Lecturas operativas

### B15.8

**8.1.** El bundle va a `../backup_pre_gc.bundle` (el escritorio, fuera del repositorio). `git bundle verify` debe terminar sin
error. Si falla, no se ejecuta el paso 2. `audit15_maintenance.py` registra el tamaño y el sha256 del bundle en
`maintenance_audit15.json`.

**8.2.** `git count-objects -vH` se registra antes y después. Los objetos que se eliminan son los que quedaron sin referencia al
deshacer el commit local `151154b` (checkpoints npz) y los de los reflogs vencidos. Ningún archivo del árbol de trabajo se
toca.

**8.3.** Se crea `.gitignore` (no existía) con `experiments/results/**/*.npz`, que cubre los checkpoints y las muestras de
`audit10_cal`, y con `experiments/external_audit15/`, las descargas de A15 que no se commitean. Control:
- `git ls-files -ci --exclude-standard` debe salir vacío, es decir, ningún archivo versionado queda ignorado;
- `git ls-files '*.npz'` debe dar 0.

### B15.7b

**7b.1.** Se corrige `audit15_supplement.py` y se comprueba generando en un directorio temporal, con la opción `--out`.
`supplementary/` no se reconstruye: sigue siendo el de `491ed60` hasta la reconstrucción posterior al v17. La numeración de
tablas del encargo es la del PDF de control de `491ed60`: 3 = S2 dgp5, 5 = S3b, 6 = S3c, 11 = S5 θ = 0.02, 23 = S6
misspec, 24 = S6 critB, 26 = S6 dgp5, 27 = S6 fp.

**7b.2. (a)** Se cuentan las celdas por fila y las columnas de la cabecera y del colspec de las tablas 3 y 26, y se corrige lo
que no cuadre. El diagnóstico queda en el JSON.

**7b.3. (b)** Se sustituyen las claves internas por etiquetas legibles, con un mapa fijo en el script, que se declara:
- `sigma_known` → «σ known»; `alpha1_hac` → «HAC, pilot α(1)»; `alpha2_hac` → «HAC, pilot α(2)»;
- `H0_n200` → «H₀, n = 200»; `DGP3_r4_n1000` → «DGP 3, r = 4, n = 1000»;
- `Ncal10000` y `Ncal50000` → «N_cal = 10⁴» y «5×10⁴»;
- `DGP1_rho095_n200` → «ρ = 0.95, n = 200».

**7b.4. (c)** Títulos descriptivos por tabla de S6, escritos en el script (texto sin cifras de resultados).

**7b.5. (d)** Se elimina de S6 la tabla critB con θ = 0.02, que duplica la de S5.

**7b.6. (e)** Nota en S1 y en S6: «RM: the centred rolling-means statistic with θ = 0.1.»

**7b.7. (f)** p-valores: «<0.001» si p < 0.001; si no, 3 decimales con redondeo binario. Afecta a S1, S3a, S6 dgp2 (hoy en
notación científica) y S6 awb.

**7b.8. (g)** Las filas de misspec en S6: «, N» → «, normal».

**7b.9. (h)** Se comprueba que el tabular de fp lleva la marca a de KPSS y que S6 incluye su nota. Si no la incluye, se añaden
las notas de las marcas de tab:fp y tab:dgp5, extraídas literalmente de los `\item[...]` del v13.

### B15.9

**9.1. tab_summary.** `audit15_v17_tables.py` genera `tab_summary_audit15.tex` y su nota, sólo desde JSON:
- **Tamaño.**
  - Filas de A12: `bA_ma_audit12.json` `size.<celda>.iid.<proc>` (N = 2×10⁴), con proc = gls_t0, msb, dfgls, adf.
  - Fixed-b con b = 0.3: `b3_fixedb_audit15.json` (N = 2×10⁴).
  - Filas MZ_t-GLS: `b1_boot_audit15.json` (N = 5000).
  - D y M sobre las 30 celdas con ψ ≠ 0; mínimo y máximo sobre las 36; celdas iid (`ma_0`) dentro de la región exacta de
    su N.
- **Potencia** (ajustada, ρ = 0.90, n = 200, caso constante, errores iid):
  - A12: `bA_ma_audit12.json` `power.pwr_ma_0_rho0p9_n200_c.adjusted.<proc>`, N = 5000, caminos de A12;
  - fixed-b: `b3_fixedb_audit15.json` `power.pw3_rho0p9_n200_c.rates.b=0.3` (calibrada = ajustada);
  - MZ_t-GLS: `b1_boot_audit15.json` `power.pw1_ma_0_rho0p9_n200_c.adjusted.<brazo>`.

  Las tres fuentes usan caminos distintos, y la nota lo declara. Si una celda no existe en su JSON, se imprime «–».
- **Nota.** N por fila y la región de cada N.

**9.2. Lista de tablas para la reconstrucción del suplemento.** Se registra en `supplement_plan_v17_audit15.json` tal como la
da el encargo, sin ejecutar nada.

**9.3. Plantilla.** Se descarga `https://files.taylorandfrancis.com/InteractNLMLaTeX.zip` a `experiments/external_audit15/`,
sin commitear. Se registran la URL, el tamaño, el sha256 y la versión de `interact.cls` (su `\ProvidesClass`).
- **Estilo de referencias.** La página de instrucciones de la revista en tandfonline.com devuelve 403 desde este entorno. La
  evidencia es que el enlace de Overleaf para JSCS (`sharelatex.com/templates/journals/journal-of-statistical-computation-and-simulation`)
  redirige a «Taylor & Francis LaTeX template for authors (Interact layout + NLM reference style)». Se declara como evidencia
  indirecta, y el autor debe confirmarlo en las instrucciones de la revista.

### Reporte

**R5.** Secciones B15.8, B15.7b y B15.9 en `resultados_auditoria_15.md`.
