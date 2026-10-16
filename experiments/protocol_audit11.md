# Protocolo de la auditoría A11: cierre para el manuscrito v12

Se registra en T0 antes de cualquier cómputo de A11. A11 no cambia ninguna
regla de decisión de A10: el θ primario sigue siendo 0.02
(`b101_theta_audit10.json`). Hay tareas cortas que solo leen JSON (T1, T2, T5) y
dos simulaciones nuevas (T3, T4).

Las tareas se copian literalmente del encargo. La sección «Lecturas operativas»
fija, antes de ver datos, cómo aplico cada tarea cuando el encargo admite más de
una lectura. Cualquier enmienda posterior va en un archivo propio
(`protocol_audit11_amendN.md`), con commit propio y fila en §4 del reporte.

## Tareas copiadas literalmente

### T1. Figuras en inglés (mismos nombres de archivo)

Regenera las seis figuras de A10 **desde los mismos JSON**, cambiando solo el texto:

| Archivo | Cambios |
|---|---|
| `fig_calibration_gain_audit10.pdf` | Paneles «Constant» y «Trend»; eje y «Empirical size»; leyenda: «Exact region (N at each point)», «RM-GLS, critical value at n», «RM-GLS, critical value at n = 20,000», «MSB-GLS, published asymptotic critical value». Evita el solapamiento de las etiquetas 150 y 200 del eje x (rota o elimina 150). |
| `fig_dgp3_audit10.pdf` | Eje y «Rejection rate (null true)»; leyenda «RM-GLS», «RM», «ADF-sim», «DF-GLS-sim», «RM-GLS, AWB», «AWB DF-GLS». |
| `fig_power_equalized_audit10.pdf` | Títulos «Constant, n = …» y «Trend, n = …»; eje y «Power (equalized size)»; «primaria» → «RM-GLS». |
| `fig_size_shift_audit10.pdf` | Títulos «Persistence 0.99, normal» y «Persistence 0.95, t(5)»; eje y «Size shift (pp)»; «primaria» → «RM-GLS». |
| `fig_local_power_audit10.pdf` | Paneles «Constant», «Trend»; eje y «Power (n = 2000)»; leyenda «Envelope (P_T)», «RM-GLS (θ = 0.02)», «RM-GLS (θ = 0)». |
| `fig_theta_ladder_audit10.pdf` | Paneles «Constant», «Trend»; eje y «Distance to envelope (pp)»; separa las etiquetas 0.00 y 0.02 del eje x. |

Conserva los nombres de archivo con sufijo `_audit10` (el `.tex` los referencia así). Reporta el sha256 nuevo de cada PDF y confirma que los datos graficados son bit a bit los mismos (compara los arrays leídos).

### T2. DGP 2 con θ = 0.02 para el manuscrito

"Del JSON que alimentó la Tabla B10.3.1.dgp2, exporta en Markdown y en un fragmento LaTeX (`tab_dgp2_audit11.tex`, solo el `tabular`) la tabla con columnas: δ, n, RM-GLS (θ = 0.02), RM, ADF-sim, PP-sim, DF-GLS-sim, MZ_t-GLS-sim, MSB-GLS-sim, ZA, McNemar p frente a DF-GLS-sim; filas δ ∈ {0, 0.5, 1, 2, 3, 5} × n ∈ {200, 500, 1000}. Si ZA no está en ese JSON, tómalo de A8/A9 sobre las mismas trayectorias y decláralo. Añade el tamaño de ZA bajo paseo aleatorio y bajo paseo con quiebre Δμ = 1 si existe en algún JSON previo."

### T3. Reproducir el sesgo del ancla (Observación 1 del manuscrito)

"Reproduce ambos con la rutina de producción (anclaje GLS, σ = 1 fijo en lugar de σ̂_HAC), N = 40 000 por n, n ∈ {200, 500, 1000, 2000, 5000, 20 000}, θ ∈ {0, 0.02, 0.1}, familia 123, y reporta media y EE. Criterio: la fila n = 20 000 debe quedar a menos de 3 EE de (1−θ)/2 + θ/3 − 39.67/n para θ = 0; para θ > 0 solo reporta. Si algún número del manuscrito no se reproduce a 3 EE, dilo en §7."

### T4. Consistencia con tendencia

"Bajo Y_t = 1 + 0.1 t + x_t con x_t AR(ρ) estacionario (ρ ∈ {0.5, 0.9}) alrededor de tendencia lineal, n ∈ {200, 500, 1000, 2000, 5000}, 2000 réplicas: mediana de n⁻¹Σû_t² (residuo QD con c̄ = −13.5), de σ̂²_HAC y del estadístico, con pendientes log–log. Reporta si n⁻¹Σû_t² queda acotado. Solo reporta; no interpretes."

### T5. Cifras citadas del manuscrito que conviene confirmar

Confirma contra los JSON, y corrige en §7 si no coinciden:
1. §5.10: «dropping the variance channel changes size by at most 0.1 points in any null cell» (A8 B2a).
2. §5.10: «rebalancing lowered power by 14 to 28 points» (v11/A5).
3. §1 y §5.10: «centering at the sample mean costs about thirty points of local power at c = 10» (A8 B4: RM +33.4 pp frente a RM-GLS).
4. §6: la fila «Registered statistic» de la Tabla 12 a tasa igualada (11 episodios, 199.6 días, 109.3).

## Lecturas operativas (fijadas antes de ver datos)

1. **Familias.** T0 = 120 (protocolo y mapa de semillas), T1 = 121, T2 = 122,
   T3 = 123, T4 = 124, T5 = 125; 126–129 quedan para enmiendas. Solo T3 y T4
   generan trayectorias. Las semillas siguen el esquema de A10:
   `SeedSequence(familia, spawn_key = (celda, i))`, que equivale a un hijo de
   `SeedSequence(familia).spawn` por celda y un nieto por réplica. T0 verifica
   esa equivalencia y que no hay colisiones con las familias previas (90–98 de
   A8, 100–107 de A9, 110–115 de A10, las semillas enteras de A5–A7 y la
   semilla 42 de producción).
2. **Manuscrito de referencia.** Es `paper_latex_v12.zip`, extraído fuera del
   repositorio y solo para leer. Las citas `archivo:línea` de §7 apuntan a ese
   árbol. No se edita ningún `.tex`, ni en `paper/` ni en el zip.
3. **T1: dónde se escribe.** Los seis PDF se reescriben con el mismo nombre en
   `experiments/figures/` y `paper/figures/`. Los JSON de A10
   (`figures_audit10.json`, `manifest_audit10.json`) no se tocan y conservan el
   sha256 anterior. El nuevo queda en `figures_audit11.json` y en
   `manifest_audit11.json`, con la tabla antes/después.
4. **T1: igualdad de datos.** Se interceptan todas las llamadas a
   `Axes.plot`, `Axes.fill_between` y `Axes.axhline` en dos corridas:
   - el código de A10 (`make_figures_audit10`, que dibuja en una carpeta
     temporal);
   - el código nuevo.

   Se exigen el mismo número de llamadas, en el mismo orden, y arrays float64
   idénticos elemento a elemento (`np.array_equal`, sin tolerancia). Se reporta
   también un sha256 de los bytes concatenados de cada corrida. El texto cambia
   solo donde el encargo lo pide, más tres cambios:
   - «AWB DF-GLS (A8)» en `fig_size_shift` pasa a «AWB DF-GLS», igual que en
     `fig_dgp3`.
   - Las curvas de `fig_local_power` que el encargo no nombra (MSB-GLS, DF-GLS,
     MZ_t-GLS) conservan su nombre, que ya está en inglés.
   - En `fig_calibration_gain` se quita la etiqueta 150 del eje x; la marca
     queda.

   En `fig_theta_ladder`, 0.00 se alinea a la derecha de su marca y 0.02 a la
   izquierda; las etiquetas usan dos decimales.
5. **T2: fuente.** Es `b103_equalized_audit10.json`, celdas `dgp2_*`,
   `rates_sim`.
   - Las columnas «-sim» usan el umbral simulado que declara el propio JSON
     (`config.calibration_source`).
   - RM es `rm_t0.1`, la configuración de RM de A8–A10.
   - ZA está en ese JSON (`rates_sim.za`, valor crítico simulado con la
     calibración de A9, N_cal = 50 000). Esa es la columna ZA. `rates_asy.za`
     se reporta aparte en Markdown.
   - McNemar p es `mcnemar_primary_vs_sim.dfgls.p_value` (exacto).
   - El tamaño de ZA bajo paseo aleatorio y bajo paseo con quiebre Δμ = 1 se
     toma de `b5_power_audit8.json` (`za_size`, p-valor asintótico, N = 5000), y
     como segunda fuente de `dgp2_break_tests_audit6.json` (`size_control`).
   - El fragmento LaTeX se escribe en `experiments/results/tab_dgp2_audit11.tex`,
     fuera de `paper/`.
6. **T3: definición.**
   - Estadístico: S_θ = `audit9_engine.rmgls(Y, n, θ, 1.0, "c")`, que llama a
     `rm_core.path_statistic` con anchor = "gls", R = 0 y σ² = 1 fijo. Se
     promedia S_θ².
   - Trayectorias: paseos gaussianos de A8 (`gauss_rw`: Y₀ = 0, Y = cumsum ε,
     n + 1 puntos). Hay una celda `t3_n<n>` por n con 40 000 réplicas; los tres θ
     se evalúan sobre las mismas trayectorias.
   - EE = desviación típica / √N.
   - κ(c̄) = 2|c̄|(1/2 + |c̄|/3) con c̄ = −7, en precisión doble (≈ 39.667).
     El criterio se evalúa con ese κ y, además, con el literal 39.67.
   - Paso 0: en las 100 primeras trayectorias de cada n, S₀² debe coincidir con
     (n+1)⁻¹ Σ_t (Y_t − β̂_GLS)² / n de la Observación hasta 1e-12.
   - Un número del manuscrito se reproduce si |media − valor citado| < 3 EE.
     El valor citado se toma tal como está impreso (tres decimales). La
     aproximación de primer orden (0.302, 0.421, 0.480) se comprueba como
     aritmética, redondeando 1/2 − κ/n a tres decimales.
   - E[𝒢_θ(W)] = (1−θ)/2 + θ/3 se contrasta con la fila n = 20 000 corregida
     por −κ/n. Para θ > 0 solo se reporta.
7. **T4: definición.**
   - DGP: Y_t = 1 + 0.1 t + x_t, t = 0, …, n (n + 1 puntos, como las
     trayectorias de producción). x₀ ~ N(0, 1/(1−ρ²)) y
     x_t = ρ x_{t−1} + ε_t con ε iid N(0, 1). Hay una celda `t4_rho<ρ>_n<n>`
     con 2000 réplicas.
   - Por réplica se calculan tres cantidades:
     - A = n⁻¹ Σ_{t=0}^{n} û_t², con û = `detrend_qd(Y)` (c̄ = −13.5);
     - B = σ̂²_HAC = `rm_core.hac_sigma_sq(Y)`, la rutina de producción;
     - S = RM-GLS con el θ final 0.02, caso con tendencia, con σ̂_HAC
       (`audit9_engine.rmgls(Y, n, 0.02, B, "ct")`).
   - Pendiente log–log: MCO de log(mediana) sobre log n con los cinco n.
   - IC 95%: bootstrap percentil con 2000 remuestras de las réplicas dentro de
     cada n. Su semilla sale de la celda `t4boot_rho<ρ>` de la familia 124,
     distinta de las celdas de trayectorias.
   - **«Queda acotado» (lectura operativa):** el límite superior del IC 95% de
     la pendiente de A es < 0.5. Ese valor es el punto medio entre 0 (acotado)
     y 1 (crecimiento O_p(n) bajo raíz unitaria). Se reporta también si el IC
     contiene 0 y el cociente de medianas entre n = 5000 y n = 200.
8. **T5: regla de confirmación.**
   - Una cifra del manuscrito se confirma si el valor del JSON, redondeado a la
     precisión impresa, coincide con ella.
   - Un rango «a a b» se confirma si el mínimo y el máximo de las diferencias
     citadas redondean a a y b.
   - «about thirty» se confirma si la cantidad redondeada a la decena es 30.
     «more than thirty» se confirma si la cantidad es > 30.
   - Para T5.3 se reportan tres cantidades:
     - la brecha de RM a la envolvente;
     - la de RM-GLS;
     - su diferencia (RM-GLS − RM en potencia).

     Se declara cuál corresponde a «centering at the sample mean costs».
   - Para T5.4 la fuente es la configuración final
     (`b103_application_audit10.json`, `rhat_prereg`). A8 y A9 se muestran como
     referencia.
9. **Tope.** 4 h por tarea. T3 y T4 checkpointean por celda y se pueden
   reanudar.
