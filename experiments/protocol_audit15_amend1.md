# Enmienda 1 al protocolo de A15: decisiones del autor

Se commitea antes de seguir con cualquier cómputo de A15. Completa `protocol_audit15.md` (commit `be2280c`).

## 1. Decisiones del autor (literal)

```
Decisiones del autor para A15 (enmienda 1 al protocolo; commitear antes de
seguir):

1. Predicción. prediccion_boot_audit15.md se commitea con las definiciones
   numéricas de A/B/C (B15.1) y de «fixed-b controla el tamaño» (B15.3),
   y con el pronóstico del autor en el mismo commit, o con la línea
   «sin pronóstico del autor». Nada se computa antes de ese commit.

2. Permiso de descarga:
   (a) bootUR_1.0.5.tar.gz desde cran.r-project.org; registra su tamaño y
       sha256.
   (b) https://ebenlazarus.github.io/HARRecommendations.pdf; extrae la
       regla de truncamiento de Newey–West con tabla y ecuación. Si no
       aparece de forma explícita, «No ejecutado».

3. Brazo (v) sustituido por (v′): el SWB de bootUR 1.0.5, replicado desde
   el código fuente y aplicado a MZ_t-GLS.
   - Paso 0 contra boot_adf(detrend = "QD", bootstrap = "SWB") sobre
     DF-GLS, con los mismos criterios que (iii).
   - Etiqueta en todo el reporte: «SWB (bootUR)». No lo llames
     «Cavaliere–Taylor recoloreado».
   - El brazo (v) original queda «No ejecutado: sin el PDF».

4. Orden: commit de la predicción → Paso 0 → sondas (familias 151 y 158)
   → proyección de horas-núcleo → confirmación escrita del autor → B15.1
   y B15.3.
   Las sondas reportan SOLO tiempos. Sus conteos de rechazo se guardan en
   el JSON bajo la clave "sealed" y no se imprimen ni se resumen hasta el
   reporte final.

5. Texto del parche T3 (para fijar las asignaciones del literal):
   «The simulated critical values of MSB-GLS and MZ$_t$-GLS are exact only
   under \cref{eq:null}. On the paths of \cref{tab:serial}, replacing them
   by the published asymptotic critical values of \citet{ng2001lag} lowers
   the rejection rate of both tests in all $36$ cells, by at most $0.6$
   points in the constant case and by $0.4$ to $4.2$ points in the trend
   case. Over the $30$ cells with serial correlation the mean absolute
   deviation of MZ$_t$-GLS from the nominal level is $0.0142$ with
   simulated and $0.0130$ with asymptotic critical values. In the trend
   case with positive dependence and $n \leq 200$, MZ$_t$-GLS rejects
   between $0.062$ and $0.092$ with simulated critical values, against
   $0.036$ to $0.050$ with the asymptotic ones and with DF-GLS; under
   moving-average errors of $-0.8$ the ordering reverses, DF-GLS rejecting
   up to $0.142$. No test in the table controls size across the six error
   processes.»
   Asignaciones:
   - «0.4 to 4.2»: rango de iid − asy en pp, MSB-GLS y MZ_t-GLS, caso
     tendencia, 36 celdas (antes decía 4.3; corregido a redondeo binario).
   - «0.062 to 0.092»: MZ_t-GLS iid, tendencia, ψ = +0.5 o φ = +0.5,
     n ∈ {100, 200} (cuatro celdas).
   - «0.036 to 0.050»: dos rangos sobre esas MISMAS cuatro celdas:
     (a) MZ_t-GLS con valor asintótico;
     (b) DF-GLS con valor iid.
     Tu asignación actual usa también n = 500; corrígela a n ≤ 200 y
     verifica ambos rangos por separado.
   - «up to 0.142»: DF-GLS iid, máximo sobre las celdas con ψ = −0.8.
   - «0.6»: máximo de iid − asy en pp, caso constante, MSB-GLS y MZ_t-GLS.
   - «36», «30», «0.0142», «0.0130»: como los asignaste.

6. B15.2: la cifra 0.333 se retira del manuscrito. No hace falta nada más.

7. B15.5:
   - El repositorio pasará a privado durante la revisión: CONSERVA los
     hashes de commit en la propuesta (sin anonNNN).
   - Excluye del paquete b5_anon_audit15.json, audit15_b5_anon.py y la
     línea 314 de protocol_audit15.md.
   - Sin URL externa: el suplemento irá como archivos a la revista.
   - Identifica la cadena exacta del residuo «correo». Si es el marcador
     anonymous@example.org, exclúyelo del detector y repite la
     construcción de prueba.
   - Aclara la contradicción entre tu mensaje («queda limpia») y el
     reporte («Limpia: no»).
   - No anonimices supplementary/: se rehará según SUPPLEMENT_PLAN.md
     (bloque aparte, después de B15.1).

8. B15.0b: exporta la tabla por k (celdas de A12 y nula de A10) como
   tabular para el suplemento S5, con un generador que lea solo el JSON.
```

## 2. Lecturas operativas

**E1.1. Predicción.** `prediccion_boot_audit15.md` se commitea con las definiciones de A/B/C, las de «fixed-b controla el
tamaño», el brazo (v′) y la línea «sin pronóstico del autor». El autor no dio pronóstico en esta enmienda. Nada de
B15.1 ni de B15.3 (Paso 0, sondas o corridas) se computa antes de ese commit.

**E1.2. Descargas.**
- **Destino.** Los dos archivos van a `experiments/external_audit15/` y no se commitean: uno es código de terceros y el
  otro un artículo con derechos de autor.
- **Registro.** El inventario `audit15_ext_inventory.py` registra la URL, el tamaño en bytes y el sha256 de cada uno.
- **bootUR.** Del tarball se leen, sin compilarlos, los archivos de `src/` y `R/` que implementan `boot_adf` con
  `bootstrap = "SB"` y `"SWB"`, y se citan por archivo y línea en la enmienda 2.
- **LLSW.** Del PDF se extrae la regla de truncamiento de Newey–West sólo si aparece de forma explícita, citando la tabla y
  la ecuación. Si no aparece, «No ejecutado».

**E1.3. Brazo (v′).**
- **Qué es.** El SWB de bootUR 1.0.5, replicado desde el código fuente y aplicado a MZ_t-GLS con la MAIC GLS re-elegida en
  cada réplica, igual que (iii).
- **Paso 0.** Contra `boot_adf(detrend = "QD", bootstrap = "SWB", criterion = "MAIC", criterion_scale = FALSE)` sobre el
  estadístico de bootUR, con los criterios de la lectura 1.7 y la familia 154.
- **Compuerta.** Si falla, sólo se detiene (v′).
- **Etiqueta.** «SWB (bootUR)» en todo JSON y reporte.
- **Brazo (v) original.** Queda «No ejecutado: sin el PDF».
- **Predicción.** El desenlace se evalúa por separado para (iii) y (v′).

**E1.4. Orden y sellado.**
- **Orden.** Commit de la predicción → enmienda 2 (reglas leídas de bootUR, sin calcular) → Paso 0 → sondas 151 y 158 →
  proyección de horas-núcleo → confirmación escrita del autor → B15.1 y B15.3.
- **Qué reportan las sondas.** Sólo tiempos: por camino y brazo, y la proyección.
- **Sellado.** Los conteos de rechazo de las sondas se guardan bajo la clave `"sealed"` del JSON de la sonda. Ni los
  scripts, ni los logs, ni el reporte los imprimen ni los resumen hasta el reporte final. El generador del reporte sólo lee
  `"sealed"` cuando existan los JSON finales de B15.1 y B15.3.

**E1.5. Parche T3.** Las asignaciones pasan de tentativas a fijas, con el texto del autor. Todas las comparaciones usan
redondeo binario.

| Literal | Magnitud |
|---|---|
| «0.4 to 4.2» | min y max de iid − asy en pp, MSB-GLS y MZ_t-GLS, caso tendencia, 18 celdas del caso (las 36 celdas son de los dos casos) |
| «0.062 to 0.092» | MZ_t-GLS iid, tendencia, errores ma_0p5 y ar_0p5, n ∈ {100, 200} (cuatro celdas) |
| «0.036 to 0.050» (a) | MZ_t-GLS asintótico en esas cuatro celdas |
| «0.036 to 0.050» (b) | DF-GLS iid en esas cuatro celdas; (a) y (b) se verifican por separado |
| «up to 0.142» | DF-GLS iid, máximo sobre las celdas ma_m0p8 |
| «0.6» | máximo de iid − asy en pp, caso constante, MSB-GLS y MZ_t-GLS |
| «36», «30», «0.0142», «0.0130» | como en el reporte parcial |

«In all 36 cells» se verifica además como: iid > asy en las 36 celdas para MSB-GLS y para MZ_t-GLS.

**E1.6. B15.2.** Nada más. La cifra 0.333 se retira del manuscrito.

**E1.7. B15.5.**
- **Alcance.** Se excluyen `supplementary/`, porque se rehará en un bloque aparte después de B15.1,
  `experiments/results/b5_anon_audit15.json` y `experiments/audit15_b5_anon.py`. Todo archivo cuyo contenido sea el
  propio inventario de B15.5 queda fuera. De `experiments/protocol_audit15.md` se excluye la línea 314 del archivo del
  commit `be2280c`, la que describe los patrones de ruta y usuario; en la copia se elimina esa línea.
- **Hashes.** Los hashes de commit se conservan: no hay marcadores anonNNN.
- **URL.** No hay URL de reemplazo. La URL del repositorio se sustituye por el texto «[supplementary files provided to the
  journal]».
- **Detector.** El detector de correos excluye el marcador `anonymous@example.org`.
- **Construcción de prueba.** Se repite; se registran la cadena exacta del residuo anterior y la aclaración.

**E1.8. B15.0b.**
- **Exportador.** `audit15_tables.py` exporta, sólo desde `b0b_lag_audit15.json`, `tab_lag_audit15.tex` para el suplemento
  S5.
- **Filas.** Celda, o (n, caso) de la nula de A10, × k ∈ {0, 1, 2, ≥3}.
- **Columnas.** Caminos, fracción, y tasa iid y asintótica de MZ_t-GLS y de MSB-GLS, a 3 decimales con redondeo binario.
- **Nota.** Wilson va en el JSON y en el reporte, no en el tabular.
