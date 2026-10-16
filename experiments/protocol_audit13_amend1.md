# Enmienda 1 al protocolo de A13: B13.Q (coherencia final sobre v14, tab:attrib y leyendas)

Se registra antes de correr cualquier parte de B13.Q. Completa la lectura 16 de
`protocol_audit13.md`, que dejaba B13.Q pendiente del v14. B13.Q no hace ninguna
simulación nueva. La familia 144 queda reservada y sin uso.

## 1. Encargo (literal)

```
B13.Q — Coherencia final sobre v14, tab:attrib y leyendas
(continúa A13; mismo sufijo _audit13; familia 144 si hiciera falta
aleatoriedad, que no debería). Protocolo: enmienda commiteada a
protocol_audit13.md antes de correr. Ninguna simulación nueva.

REGLA DE PASO 0 (corrección del encargo, registrar en la enmienda):
|Δ| = 0 en las columnas que el bloque usa; en el resto de columnas
comunes, ≤ 1e-12 con declaración de cuál difiere.

Q0. Entrada: paper_latex_v14.zip (reporta su sha256). Sólo lectura. Está en escritorio

Q1. tab:attrib. Exporta desde bB_attrib_audit12.json el tabular con la
    disposición exacta de v14/sec5_montecarlo.tex (bloque marcado
    "TRANSCRIBED"): columnas (a), (b), (b'), (c), (a)-(b'), (b')-(b),
    (b')-(c); filas rho ∈ {0.80, 0.90, 0.93, 0.95, 0.97} a n = 200, las
    cinco medias con EE, las tres filas de potencia local; y la nota con las
    medias de (a)-(b) y (b)-(c). Compara celda por celda con la
    transcripción de v14 y lista toda diferencia. Salida:
    tables_audit13/tab_attrib_audit13.tex, con test de literales.

Q2. Figuras. Regenera las seis figuras _audit13 cambiando sólo rótulos:
    "RM-GLS" → "MSB-B"; en fig_size_shift elimina la serie rotulada
    "MSB-HAC" (es el estadístico anclado en la media, tau = 0, que el texto
    no discute). Paso 0: los datos graficados de las series que quedan son
    idénticos bit a bit a los de A13. Nombres: *_audit13q.pdf.

Q3. Coherencia. Como T5 de A11 y la tabla de cifras de A13: toda cifra de
    v14 (main, sec1-7, appA-C, highlights, cover_letter.md) contra su JSON,
    con archivo:línea, valor impreso, valor recalculado y convención de
    redondeo. Atención especial a la lista de CHANGELOG_v14.md §3 (cifras
    que no venían de la tabla de A13), incluidos 12/23, 2, 0.4 pp, 5/12
    (b103_equalized_audit10.json, McNemar gls_t0 vs gls_t0.02 al 5 %);
    5.4 con B = 8, 1.13 y 0.85 (bA_ma_audit12.json); 5.4e-4 y λ ≈ 1192
    (bF_anchor_audit12.json). Marca "no reproduce" con la cifra correcta.

Q4. Frases prohibidas (búsqueda literal, sin contar las secciones de
    resultados negativos ni la tabla de desviaciones): "collapses faster",
    "does not collapse as fast", "no cost in size", "no effect on size",
    "RM-GLS", "rolling means" fuera de sec2 §2.2, sec4 §4.2, sec5 §5.12 y
    notas de columna RM, "theta = 0.02" fuera de sec4 §4.2, sec5 y
    tab:deviations, "two-channel" fuera de §5.11, §6 y conclusión.

Q5. Suplemento. Confirma que existen, con N_cal = 5e5, valores críticos
    simulados de MSB-GLS y MZ_t-GLS a n ∈ {100, 200, 500, 1000} en ambos
    casos (App. B de v14 los promete). Si faltan, lístalos en «No
    ejecutado»; no los calcules.

Reporte: sección nueva «B13.Q» en resultados_auditoria_13.md regenerado,
con las siete secciones habituales actualizadas y la tabla maestra.
```

## 2. Lecturas operativas (fijadas antes de correr)

1. **Paso 0 (corrección del encargo).** A partir de esta enmienda, en todo
   B13.Q:
   - las columnas que un bloque usa deben coincidir con máx. |Δ| = 0;
   - el resto de columnas comunes puede diferir hasta 1e-12, declarando cuál
     difiere y en cuánto.

   Los Paso 0 de B13.E ya registrados no se tocan: todos dieron |Δ| = 0.
2. **Q0.**
   - Manuscrito de referencia de B13.Q: `../paper_latex_v14.zip`, leído
     dentro del zip sin extraerlo; se reporta su sha256.
   - Además se comparan byte a byte los tabulares `v14/tables/*_audit13.tex`
     y las figuras `v14/figures/*_audit13.pdf` con los exportados por A13.
3. **Q1.** Fuente: `bB_attrib_audit12.json`. Correspondencia de columnas:

   | Columna | Estadístico y valor crítico |
   |---|---|
   | (a) | `gls_t0`, cv simulado |
   | (b) | `glsb_t0`, cv simulado |
   | (b′) | `glsbp_t0`, cv simulado (familia 136) |
   | (c) | MSB-GLS con el cv asintótico de NP 2001 |

   - **Filas de potencia:** celdas `dgp1_rho<ρ>_n200`,
     ρ ∈ {0.80, 0.90, 0.93, 0.95, 0.97}.
   - **Filas de medias:** `by_n` (c|200, c|500, c|1000, ct|200, ct|500), con
     el número de valores de ρ `k` entre paréntesis y la EE pareada de A12.
   - **Potencia local:** celdas `lp_dm_c5`, `lp_dm_c10` y `lp_dm_c15`.
   - **Formato:** tasas con 3 decimales; diferencias en pp con 2 decimales,
     signo explícito y `$-$` para los negativos; EE con 2 decimales.
   - **Nota:** medias de (a)−(b) con EE y de (b)−(c) sin EE, en el orden del
     v14.
   - **Redondeo:** se prueban las dos convenciones de A13 (binaria y mitad
     hacia arriba); se usa la que reproduce más celdas del v14 y se declara.
   - **Salidas:**
     - `tables_audit13/tab_attrib_audit13.tex` (sólo el tabular, con la
       disposición y la cabecera del bloque TRANSCRIBED);
     - `tables_audit13/tab_attrib_note_audit13.tex` (el texto de la nota con
       las medias);
     - `q_attrib_audit13.json`.
   - **Comparación:** celda por celda contra el bloque del v14, listando toda
     diferencia.
   - **Paso 0:** cada tasa y cada diferencia del JSON se recompone desde
     `rejections/n`; se exige máx. |Δ| = 0 en las columnas usadas.
4. **Q2.**
   - Mismo código de dibujo y mismas fuentes que `make_figures_audit13.py`.
   - La etiqueta de la primaria de A11 (`PRIMARY_LABEL`) pasa de «RM-GLS» a
     «MSB-B» sólo en tiempo de ejecución; no se tocan los archivos de
     configuración de A11.
   - `fig_size_shift` omite la serie `msbhac`.
   - **Paso 0:** los arrays graficados, llamada a llamada, son idénticos bit a
     bit a los guardados en `figures_audit13.json` (`data`), una vez quitadas
     las llamadas de la serie eliminada. Se comprueba además que esas llamadas
     eliminadas son exactamente las de `msbhac`.
   - **Salidas:** `experiments/figures/` y `paper/figures/fig_*_audit13q.pdf`,
     más `figures_audit13q.json`.
5. **Q3.**
   - **Registro de frases** (`audit13_q_claims.py`). Cada frase del v14 que
     cita una cifra de resultado se localiza por patrón, con archivo:línea, y
     se recalcula desde su JSON (de cualquier auditoría) o, si es una
     constante derivada, desde su fórmula con sus entradas. Se registran el
     impreso, el recalculado, la convención de redondeo que lo reproduce
     (binaria, mitad hacia arriba o truncamiento) y el veredicto. «No
     reproduce» va con la cifra correcta a los mismos decimales.
   - **Barrido de cobertura.** Se barren todos los números con decimales del
     texto, fuera de tabulares `\input`, comentarios y entornos matemáticos de
     definición. Cada uno queda en una de estas categorías:
     - cubierto por una frase del registro;
     - constante de diseño o de definición, con su motivo;
     - no verificado.

     Los enteros se verifican sólo cuando son resultados (recuentos,
     detecciones, episodios).
   - Las cifras sin JSON localizable se declaran como tales y no se inventa
     ninguna.
   - **Lista del CHANGELOG_v14.md §3:** cada ítem es una frase del registro.
     «12 de 23», «2», «0.4 pp» y «5 de 12» se recalculan desde
     `b103_equalized_audit10.json` con la McNemar exacta de `gls_t0` frente a
     `gls_t0.02` sobre las filas de B9.1/B9.2 (el JSON sólo guarda la
     McNemar; el sentido sale de las tasas).
     - «No saturada»: al menos uno de los dos por debajo de 0.99.
     - Las 23 celdas son DGP 1 constante, potencia con tendencia y DGP 2.
     - Las 12 celdas son las de DGP 3 con r > 1.
     - Si la definición que reproduce 23 y 12 es otra, se declara.
6. **Q4.**
   - La búsqueda literal se hace sobre la fuente del v14: los `.tex` y
     `cover_letter.md`.
   - Los cuatro primeros patrones no distinguen mayúsculas; «RM-GLS» se busca
     literal.
   - «theta = 0.02» se busca como `\theta = 0.02`, con cualquier espaciado
     alrededor de «=», y como «θ = 0.02» en los `.md`.
   - Zonas: cada línea recibe su sección y subsección por el orden de
     `\section` y `\subsection` de cada archivo (sec2 §2.2 = «The statistic
     and the smoothed family»; sec4 §4.2 = «The smoothing window»; sec5 §5.11 =
     dos canales; §5.12 = «Other negative results»).
   - «Notas de columna RM»: el párrafo de sec5 que define la columna RM y las
     notas de tabla que la mencionan.
   - Se excluyen para todos los patrones §5.11, §5.12 y el entorno de
     `tab:deviations`.
   - Se reportan todas las apariciones: las permitidas, marcadas como tales, y
     las prohibidas.
7. **Q5.** Sólo se lee lo existente:
   - calibraciones de A10 (`audit10_cal/cal_n<n>.npz`, N_cal = 500 000), sin
     cargar quantiles nuevos;
   - JSON que guardan cuantiles simulados de `msb` y `mzt`: `b101`
     (`sim_thresholds`, n ∈ {200, 500, 1000}) y `bA_ma_audit12`
     (`iid_quantiles`, n ∈ {100, 200, 500}).

   Se reporta, por (n, caso, nivel), si el valor crítico existe en un JSON,
   con qué N_cal y dónde. Los que falten (por ejemplo, niveles distintos del
   5 %) van a «No ejecutado» y no se calculan.
8. **Reporte.** Se regenera `resultados_auditoria_13.md` con la sección «B13.Q»
   dentro de §1. Las §2–§7 y la tabla maestra se actualizan: Paso 0 de Q1 y
   Q2, frases no reproducidas, frases prohibidas, faltantes del suplemento y
   filas de tab:attrib. Los generadores nuevos entran en
   `tests/test_no_literals_audit13.py`.
