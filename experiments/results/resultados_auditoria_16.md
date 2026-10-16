# Auditoría A16 — reporte (enmienda 6, v17)

Enmienda 6 commiteada antes de generar nada (§3). No se editó ningún `.tex` del manuscrito ni `src/`; `supplementary/` se reconstruyó según `SUPPLEMENT_MAP_v17.md`.

## 1. Resultados

### B16.1 — Generadores (lectura E6.1)

- tab_summary (`tables_audit16/tab_summary_audit16.tex` y nota): la potencia de la fila 1 (MSB-B con Andrews) es 0.9944, desde `b3_fixedb_audit15.json power.pw3_rho0p9_n200_c.rates.gls_t0`; es el mismo valor que tab_fixedb: sí. En A15 era 0.9966 (A12). La nota agrupa las filas por fuente de potencia.
- tab_fixedb (`tables_audit16/tab_fixedb_audit16.tex` y nota): tabular idéntico al de A15: sí. Sustituciones de `\cref{tab:serial}` por «Table S2.1 of the supplement» en la nota: 2. Los archivos de `tables_audit15/` no se tocan.

| Fila | Valor crítico | Auditoría (tamaño) | N tamaño | D | M | mín | máx | iid en región | Potencia | N potencia | Fuente de la potencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MSB-B | Andrews | A12 | 20000 | 0.0828 | 0.5195 | 0.004 | 0.570 | 6/6 | 0.994 | 5000 | `b3_fixedb_audit15.json power.pw3_rho0p9_n200_c.rates.gls_t0` |
| MSB-B | fixed-b, b = 0.3 | A15 | 20000 | 0.0075 | 0.0354 | 0.015 | 0.059 | 6/6 | 0.187 | 5000 | `b3_fixedb_audit15.json power.pw3_rho0p9_n200_c.rates.b=0.3` |
| MSB-GLS | iid | A12 | 20000 | 0.0150 | 0.0471 | 0.013 | 0.097 | 5/6 | 0.933 | 5000 | `bA_ma_audit12.json power.pwr_ma_0_rho0p9_n200_c.adjusted.msb` |
| MZ_t-GLS | asymptotic | A15 | 5000 | 0.0134 | 0.0408 | 0.009 | 0.083 | 3/6 | 0.922 | 2000 | `b1_boot_audit15.json power.pw1_ma_0_rho0p9_n200_c.adjusted.i` |
| MZ_t-GLS | iid | A15 | 5000 | 0.0135 | 0.0576 | 0.017 | 0.108 | 6/6 | 0.922 | 2000 | `b1_boot_audit15.json power.pw1_ma_0_rho0p9_n200_c.adjusted.ii` |
| MZ_t-GLS | SB (bootUR) | A15 | 5000 | 0.0074 | 0.0382 | 0.035 | 0.088 | 6/6 | 0.890 | 2000 | `b1_boot_audit15.json power.pw1_ma_0_rho0p9_n200_c.adjusted.iii` |
| MZ_t-GLS | SWB (bootUR) | A15 | 5000 | 0.0072 | 0.0354 | 0.033 | 0.085 | 5/6 | 0.900 | 2000 | `b1_boot_audit15.json power.pw1_ma_0_rho0p9_n200_c.adjusted.v_prime` |
| MZ_t-GLS | AWB | A15 | 5000 | 0.0117 | 0.0408 | 0.013 | 0.091 | 4/6 | 0.906 | 2000 | `b1_boot_audit15.json power.pw1_ma_0_rho0p9_n200_c.adjusted.iv` |
| DF-GLS | iid | A12 | 20000 | 0.0152 | 0.0917 | 0.036 | 0.142 | 5/6 | 0.931 | 5000 | `bA_ma_audit12.json power.pwr_ma_0_rho0p9_n200_c.adjusted.dfgls` |
| ADF | iid | A12 | 20000 | 0.0731 | 0.6286 | 0.047 | 0.679 | 6/6 | 0.802 | 5000 | `bA_ma_audit12.json power.pwr_ma_0_rho0p9_n200_c.adjusted.adf` |

### B16.2 — Verificación contra el código (lecturas E6.2–E6.4)

**(a) eq:mstats y su entorno** (`sec2_statistics.tex` del v17) frente a `audit8_unitroot.np_statistics` y `arch.DFGLS`:

| Punto | Texto (archivo:línea) | Código (archivo:línea) | Veredicto | Detalle |
|---|---|---|---|---|
| MSB, MZ_alpha y MZ_t: forma | sec2_statistics.tex:35; sec2_statistics.tex:37; sec2_statistics.tex:39 | experiments/audit8_unitroot.py:134; experiments/audit8_unitroot.py:135; experiments/audit8_unitroot.py:136; experiments/audit8_unitroot.py:137; experiments/audit8_unitroot.py:138 | coincide | MSB = (S/s2)^(1/2), MZ_alpha = (T^-1 u_n^2 - s2)/(2S), MZ_t = MZ_alpha x MSB, con S la suma de u_{t-1}^2, t = 1..n. |
| MSB, MZ_alpha y MZ_t: normalizacion | sec2_statistics.tex:35; sec2_statistics.tex:37 | experiments/audit8_unitroot.py:62; experiments/audit8_unitroot.py:134; experiments/audit8_unitroot.py:135 | difiere, sin efecto en el tamano de los brazos calibrados | El texto normaliza con n (n^-2 y n^-1). El codigo usa T = len(y) = n + 1 ((n+1)^-2 y (n+1)^-1). MSB del codigo = MSB del texto x n/(n+1). El brazo con valores criticos asintoticos publicados si depende de ello (control numerico abajo). |
| Convencion T_n del detrending GLS | sec2_statistics.tex:26 | experiments/audit8_unitroot.py:64; experiments/audit8_unitroot.py:62; arch 8.0.0, arch/unitroot/unitroot.py:941; arch 8.0.0, arch/unitroot/unitroot.py:942; src/stationarity_test/rm_core.py:67; src/stationarity_test/deterministics.py:57 | difiere para MSB-GLS, MZ_t-GLS y DF-GLS en el caso constante | El texto dice T_n = n (constante) y T_n = n + 1 (tendencia), 'the convention of the replication code'. Es la de MSB-B (src/). np_statistics y arch.DFGLS usan a = 1 + cbar/(n + 1) en los dos casos. |
| Regresion de s2_AR: deterministas | sec2_statistics.tex:43 | experiments/audit8_unitroot.py:91; experiments/audit8_unitroot.py:92 | coincide | Sin constante: la matriz tiene u_{t-1} y k diferencias retardadas sobre el residuo GLS. |
| Regresion de s2_AR: muestra e indices | sec2_statistics.tex:43; sec2_statistics.tex:42 | experiments/audit8_unitroot.py:90; experiments/audit8_unitroot.py:133 | no especificado en el texto | Muestra comun t = kmax+1..n (n - kmax observaciones) para todo k, tambien para el s2_AR final (no se reestima con t = k+1..n); sigma2_k = SSR_k/(n - kmax). |
| Formula de s2_AR | sec2_statistics.tex:42 | experiments/audit8_unitroot.py:133 | coincide | s2_AR = sigma2_k/(1 - sum b_j)^2. |
| MAIC | sec2_statistics.tex:44 | experiments/audit8_unitroot.py:128; experiments/audit8_unitroot.py:127; experiments/audit8_unitroot.py:105; experiments/audit8_unitroot.py:51 | coincide | MAIC(k) = ln sigma2_k + 2(tau(k) + k)/(n - kmax), tau(k) = b0^2 sum u_{t-1}^2/sigma2_k en la muestra comun, kmax = floor(12((n+1)/100)^(1/4)): la forma de Ng y Perron (2001) con T - kmax observaciones de la regresion. |
| DF-GLS 'in the same regression' | sec2_statistics.tex:45 | experiments/audit8_unitroot.py:150; arch 8.0.0, arch/unitroot/unitroot.py:968 | difiere (muestra) | DF-GLS es arch.DFGLS con el k de la MAIC: mismo detrending y mismo k, pero regresion sobre t = k+1..n, no sobre la muestra comun t = kmax+1..n de la MAIC. |

Control numérico: evaluación literal de eq:mstats (con la convención T_n del texto y normalización por n, el k del código) frente a `np_statistics`, en los caminos de E6.4:

| Celda | mediana \|Δ\| rel. MSB | máx \|Δ\| rel. MSB | 1/n | mediana \|Δ\| MZ_t | máx \|Δ\| MZ_t |
|---|---|---|---|---|---|
| n100_c | 7.5e-03 | 1.0e-02 | 1.0e-02 | 0.0076 | 0.0268 |
| n100_ct | 1.0e-02 | 1.0e-02 | 1.0e-02 | 0.0180 | 0.0503 |
| n200_c | 4.0e-03 | 5.0e-03 | 5.0e-03 | 0.0041 | 0.0185 |
| n200_ct | 5.0e-03 | 5.0e-03 | 5.0e-03 | 0.0089 | 0.0190 |
| n500_c | 1.8e-03 | 2.0e-03 | 2.0e-03 | 0.0017 | 0.0074 |
| n500_ct | 2.0e-03 | 2.0e-03 | 2.0e-03 | 0.0035 | 0.0086 |

**(b) §3.5 (SB/SWB) frente a bootUR 1.0.5** (tarball con sha256 `34ba4c50648b15ec98d68552efcdd520a5b458341bcf30854e6fb032f41e4a4a`):

| Pregunta | Texto del v17 | bootUR (archivo:línea) | Respuesta | Veredicto |
|---|---|---|---|---|
| Como se impone la nula | sec3_theory.tex:155; sec3_theory.tex:156 | bootUR/R/bootURtests.R:37; bootUR/R/auxiliary.R:93; bootUR/src/bootURfunctions.cpp:158; bootUR/R/auxiliary.R:99; bootUR/src/bootURfunctions.cpp:516; bootUR/src/bootURfunctions.cpp:519 | La regresion ADF se estima sin restringir, con rho estimado ('residual bootstrap (under the alternative)'). La nula se impone al generar: se descarta el coeficiente de y_{t-1} (par[-1]), las innovaciones se filtran por el AR de las diferencias y la serie se acumula (raiz unitaria). | matiz: 'regression with the null imposed' describe la generacion, no la estimacion |
| Autorregresion en diferencias; detrending y criterio | sec3_theory.tex:155 | bootUR/R/auxiliary.R:93; bootUR/src/bootURfunctions.cpp:158; bootUR/R/bootURtests.R:87; bootUR/src/bootURfunctions.cpp:254; bootUR/src/bootURfunctions.cpp:260 | Si: u*_t = Delta y*_t sigue el AR(p) de los coeficientes de las diferencias retardadas de la regresion ADF. La regresion del DGP usa detrending MCO (QD = FALSE) y la muestra sin recortar (trim = FALSE); p se elige con la MAIC reescalada de Perron y Qu (criterion_scale = TRUE por defecto) sobre datos detrendidos por MCO. | coincide; el texto no menciona el detrending MCO ni el reescalado de Perron-Qu |
| Pesos del SWB | sec3_theory.tex:158 | bootUR/src/bootURfunctions.cpp:619; bootUR/src/bootURfunctions.cpp:526 | Gaussianos N(0, 1) independientes (Rcpp::rnorm), multiplicados por los residuos. | coincide; el texto no dice que sean gaussianos |
| Centrado de residuos | sec3_theory.tex:157; sec3_theory.tex:158 | bootUR/src/bootURfunctions.cpp:172; bootUR/R/auxiliary.R:98; bootUR/src/bootURfunctions.cpp:618 | No se centran: los residuos de la regresion ADF pasan tal cual al remuestreo (SB) y a la multiplicacion (SWB). | el texto no lo dice |
| Indices del SB | sec3_theory.tex:157 | bootUR/src/bootURfunctions.cpp:626; bootUR/src/bootURfunctions.cpp:629; bootUR/src/bootURfunctions.cpp:512 | Remuestreo iid de residuos individuales con indices 0..T - l, l = longitud de bloque por defecto: los ultimos l - 1 residuos no se sortean nunca. | detalle no descrito en el texto |
| Residuos sin recortar y valor inicial | sec3_theory.tex:159 | bootUR/R/auxiliary.R:93; bootUR/src/bootURfunctions.cpp:67; bootUR/src/bootURfunctions.cpp:172; bootUR/R/auxiliary.R:101; bootUR/src/bootURfunctions.cpp:516 | Con trim = FALSE, los retardos iniciales se rellenan con ceros, asi que los primeros p + 1 residuos entran en el remuestreo con regresores nulos (el primero es el nivel detrendido). El AR arranca en cero y y*_0 = 0. | detalle no descrito en el texto |
| p-valor de bootUR | — | bootUR/src/bootURfunctions.cpp:807 | #{t* < t}/B en bootUR; nuestros brazos usan (1 + #{T* <= T})/(R + 1), declarado en la enmienda 3. | declarado |

**(c) prop:invariance para los tests con s²_AR** (`appA_proofs.tex:21`: «penalty that is a ratio of quadratic forms in $\uhat$, so the selected lag»). Argumento sobre el código: En el codigo, u = M y con MD = 0, asi que u(aY + D delta) = a u(Y). La regresion ADF-GLS sobre a u deja los coeficientes igual y multiplica SSR_k por a^2 para todo k (misma muestra comun). tau(k) = b0^2 sum u^2 / sigma2_k es invariante, y MAIC(k) se desplaza en ln a^2 para todo k: el argmin no cambia (salvo empates exactos). s2_AR se multiplica por a^2, y MSB, MZ_t y el t de DF-GLS no cambian. El suelo 1e-300 del SSR no actua en caminos no degenerados.

Control numérico, determinista (familia 160; colisiones con 90–159: 0). Parámetros: n ∈ [100, 200, 500], casos ['c', 'ct'], 1000 caminos por celda, a ∈ [-3.0, 0.01, 1000.0], b = 5.0, c = 0.1. Criterio registrado: 0 cambios de k y |Δ| relativo ≤ 1.0e-10 en MSB y MZ_t.

| Celda | cambios de k | máx rel. MSB | máx rel. MZ_t | máx rel. s²_AR/a² | máx rel. DF-GLS | margen MAIC mín. | máx \|Δ\| abs. MZ_t (diag.) | MZ_t del peor camino (diag.) | Cumple |
|---|---|---|---|---|---|---|---|---|---|
| n100_c | 0 | 3.8e-13 | 2.7e-10 | 2.6e-13 | 3.3e-12 | 3.6e-05 | 6.1e-13 | -3.1e-04 | no |
| n100_ct | 0 | 1.8e-13 | 3.5e-11 | 3.5e-13 | 9.5e-12 | 2.0e-05 | 8.5e-13 | 5.3e-03 | sí |
| n200_c | 0 | 1.8e-13 | 3.0e-11 | 5.6e-14 | 1.3e-11 | 4.0e-05 | 4.6e-13 | 8.5e-04 | sí |
| n200_ct | 0 | 1.7e-13 | 5.1e-10 | 1.1e-13 | 2.4e-12 | 1.3e-05 | 3.3e-13 | -1.1e-04 | no |
| n500_c | 0 | 1.6e-13 | 2.8e-11 | 1.4e-14 | 6.3e-11 | 2.4e-06 | 4.5e-13 | -1.9e-03 | sí |
| n500_ct | 0 | 1.9e-13 | 3.2e-12 | 1.6e-13 | 3.0e-12 | 5.6e-06 | 3.9e-13 | -4.3e-02 | sí |

Diagnostico anadido tras ver el resultado (declarado): |Delta| absoluto de MZ_t y, en el camino con mayor |Delta| relativo, MZ_t y (T^-1 u_n^2)/s2_AR - 1, el factor que se cancela en el numerador de MZ_alpha. El veredicto registrado no cambia.

### B16.3 — Literales del v17 (lectura E6.5; test independiente `tests/test_literals_v17b_audit16.py`)

| Literal | Impreso | v17 (archivo:línea) | Valor | Redondeo binario | Veredicto | Fuente |
|---|---|---|---|---|---|---|
| N1 | the simulated values give rejection rates between $0.059$ and $0.093$ | sec4_montecarlo.tex:220 | 0.0592, 0.0934 | 0.059, 0.093; hacia afuera 0.059 to 0.094 | confirma | b1_boot_audit15.json size.<sz_ma_0p5_n100_ct\|sz_ma_0p5_n200_ct\|sz_ar_0p5_n100_ct\|sz_ar_0p5_n200_ct>.rates.ii |
| N2 | the asymptotic ones between $0.036$ and $0.054$ | sec4_montecarlo.tex:221 | 0.036, 0.054 | 0.036, 0.054; hacia afuera 0.036 to 0.054 | confirma | b1_boot_audit15.json size.<sz_ma_0p5_n100_ct\|sz_ma_0p5_n200_ct\|sz_ar_0p5_n100_ct\|sz_ar_0p5_n200_ct>.rates.i |
| N3 | in all thirty-six designs | sec4_montecarlo.tex:214; sec1_introduction.tex:48 | rate(ii) > rate(i) en 36 de 36 (empates 0) | — | confirma | b1_boot_audit15.json size.<celda>.rates.<ii\|i> |
| N4 | which the MAIC selects one lag reject $0.103$ with the simulated critical value, against $0.039$ for the i.i.d.\ null paths | sec4_montecarlo.tex:226 | 0.102727, 0.0390794 | 0.103, 0.039 | confirma | b0b_lag_audit15.json cells.sz_ar_0p5_n100_ct.procs.mzt.by_k.1.iid.rate; a10_null.100\|ct.procs.mzt.by_k.1.iid.rate |
| N5a | under-reject more mildly, between $0.0417$ and $0.0502$ | sec4_montecarlo.tex:63 | 0.0417, 0.0502 | 0.0417, 0.0502; hacia afuera 0.0417 to 0.0502 | confirma | e_calib_audit13.json cases_by_theta.gls_t0.c.approximation_cost_comparators.<n>.msb.size_published_asymptotic |
| N5b | DF-GLS over-reject at small $n$ ($0.0660$ at $n = 60$) | sec4_montecarlo.tex:64 | 0.06605 | 0.0660 | confirma | e_calib_audit13.json ...c.approximation_cost_comparators.60.dfgls.size_published_asymptotic |
| N7 | gives mean absolute deviations of $0.0142$ and $0.0130$ | sec4_montecarlo.tex:223 | 0.0141667, 0.0129883 | 0.0142, 0.0130 | confirma | b0_iidasy_audit15.json b_abs_dev.mzt.both.<iid\|asy>.mean |
| N8 | the SWB and the AWB lose comparable amounts | sec4_montecarlo.tex:257 | SWB: 6 de 8 celdas, 1.55–3.80 pp; AWB: 5 de 8, 1.15–3.25 pp; SB: 6, 1.65–4.20 pp | — | se reportan los rangos; 'comparable' no se juzga (E6.5) | b1_boot_audit15.json power.<celda>.vs_ii.<v_prime\|iv> (McNemar p < 0.05) |

N5b: el valor exacto es 1321/20000 y cae en la mitad de la última cifra impresa. «0.0660» sale del redondeo binario del flotante; con mitad hacia arriba sobre el valor exacto sería 0.0661.

**N6** (sec1 y sec4 del v17): 45 frases del registro, 0 no encontradas. De las cifras que ya estaban en el v16, 95 de 96 confirman. Barrido de números con decimales: 156 cubiertos por una frase, 39 de diseño y 0 sin verificar.

| Frase | Archivo:línea | Impreso | Valor | Convenciones | Cota | Correcto |
|---|---|---|---|---|---|---|
| m_lp_ct | sec4_montecarlo.tex:105 | 1.2 | 1.225 | binaria, mitad hacia arriba | upper | 1.3 |

Cifras del grupo v16 que no están en el texto del v16: 0.05305 (m_regions), 0.05305 (m_note_calib) (es el extremo de la región, que el v17 escribe con cinco decimales).

### B15.7c — Suplemento reconstruido (lectura E6.6)

`supplementary/` reconstruido: 107 archivos; 0 aciertos identificadores fuera de los hashes de commit. Compilación de control (pdflatex, bibtex, pdflatex ×2): compila sí, 0 errores, 0 referencias y 0 citas indefinidas, 0 cajas desbordadas, 36 páginas. Compilación de control del v17 para numerar las remisiones al cuerpo: 19 páginas.

Numeración: S2.1–S2.9 coincide con el mapa: sí. Tablas por sección:

| Sección | Título | Tablas (número compilado y etiqueta) |
|---|---|---|
| S1 | Power under i.i.d.\ errors at equalized size | S1.1 tab:size, S1.2 tab:dgp1, S1.3 tab:ctpower |
| S2 | Serially correlated errors, cell by cell | S2.1 tab:serial, S2.2 tab:serialasy, S2.3 tab:lag, S2.4 tab:boot, S2.5 tab:fixedbsize, S2.6 tab:serialpower, S2.7 tab:diagnull, S2.8 tab:diagalt, S2.9 tab:diagattrib |
| S3 | The initial condition | S3.1 tab:initial |
| S4 | Mean breaks, variance breaks, heavy tails and GARCH | S4.1 tab:dgp2, S4.2 tab:dgp3, S4.3 tab:awb, S4.4 tab:misspec |
| S5 | The smoothed family S_\theta | S5.1 tab:size02, S5.2 tab:calib02, S5.3 tab:localpower02, S5.4 tab:dgp102, S5.5 tab:ctpower02, S5.6 tab:dgp202, S5.7 tab:dgp302, S5.8 tab:misspec02, S5.9 tab:awb02, S5.10 tab:dgp502, S5.11 tab:fp02 |
| S6 | The two-channel construction and other negative results | S6.1 tab:dgp5, S6.2 tab:negvariance, S6.3 tab:negweight, S6.4 tab:negrebal, S6.5 tab:neganchor |
| S7 | Rate of the HAC estimator and the trend case of the consistency theorem | S7.1 tab:hacrates, S7.2 tab:hacmedian |
| S8 | Critical values | S8.1 tab:critB, S8.2 tab:crit0p02, S8.3 tab:crit0p05, S8.4 tab:crit0p1, S8.5 tab:crit0p2, S8.6 tab:critMSBse |
| S9 | The pre-registered monitoring application | S9.1 tab:fp, S9.2 tab:deviations, S9.3 tab:oos, S9.4 tab:adverse, S9.5 tab:fpcell, S9.6 tab:latency |
| S10 | Protocols, amendments and predictions | — |

Figuras: S1.1 fig:powereq, S1.2 fig:localpower, S4.1 fig:dgp3, S4.2 fig:sizeshift, S5.1 fig:thetaladder.

| Bloque transcrito del v16 | Origen (archivo:líneas) |
|---|---|
| S1_size | sec5_montecarlo.tex:23–48 |
| S1_power | sec5_montecarlo.tex:165–230 |
| S1_fig_lp | sec5_montecarlo.tex:147–154 |
| S2_serial_table | sec5_montecarlo.tex:317–336 |
| S2_serialpower | appC_tables.tex:5–21 |
| S3_initial | sec5_montecarlo.tex:338–372 |
| S4_breaks | sec5_montecarlo.tex:372–542 |
| S5_def | sec2_statistic.tex:36–47 |
| S5_theta | sec4_implementation.tex:23–69 |
| S5_fig | sec5_montecarlo.tex:156–163 |
| S6_twochannel | sec5_montecarlo.tex:542–611 |
| S7_trend | sec3_theory.tex:149–159 |
| S9_application | sec6_application.tex:2–162 |

Referencias cruzadas reescritas: 66 (suplemento: 46, cuerpo del v17: 20); sin resolver: 0; remisiones «of the main text» que no apuntan al cuerpo del v17: 0.

Sección 6 del v16 en S9: 143 fragmentos de 8 palabras comprobados, 0 ausentes; las 134 cifras aparecen iguales y en el mismo orden: sí.

Tabulares de A13 idénticos a los del zip del v16: tab_size_audit13 sí, tab_serial_audit13 sí, tab_serialpower_audit13 sí, tab_initial_audit13 sí, tab_dgp2_audit13 sí, tab_dgp3_audit13 sí, tab_awb_audit13 sí, tab_misspec_audit13 sí, tab_fp_audit13 sí.

| Bloque | Edición declarada | Sustitución | Veces |
|---|---|---|---|
| S1_power | `\s*Rows in which every procedure exceeds \$0\.99\$\s+are omitted; they are in the\s+supplement\.` | (se elimina) | 1 |
| S1_power | `\s*Rows in which every procedure exceeds \$0\.99\$\s+are omitted\.` | (se elimina) | 1 |
| S3_initial | `^\\subsection\{The initial condition\}\\label\{sec:initial\}\s*` | (se elimina) | 1 |
| S6_twochannel | `\$\^\\dagger\$Registered interior\.\s*` | (se elimina) | 1 |
| S6_twochannel | `\s*Rows with \$\\rho = 0\.90\$ and the weak-break\s+extension \$r = 1\.1\$ are in the supplement\.` | (se elimina) | 1 |
| S6_twochannel | `The supplement reports these experiments in full\.` | `\\Cref{tab:negvariance,tab:negweight,tab:negrebal,tab:neganchor} report these experiments in full.` | 1 |
| S7_trend | `^And in the trend case` | `In the trend case` | 1 |

Macros en conflicto entre v16 y v17: \Stat: v16 `\newcommand{\Stat}{S_\theta}`, v17 `\newcommand{\Stat}{S}`, se usa v16; \StatZero: v16 `\newcommand{\StatZero}{S_0}`, v17 `\newcommand{\StatZero}{S}`, se usa v17.

### B15.4 — Pasada de coherencia sobre el v17 y el suplemento (lectura E6.7)

**(a) Resumen y conclusión.**

| Cifra | Archivo:línea | Impreso → veredicto | Contrapartidas (P1–P3, §4, §5) | Veredicto |
|---|---|---|---|---|
| abs_msb | main.tex:93 | 0.026 → confirma | sec1_introduction.tex:44; sec4_montecarlo.tex:59 | confirma |
| abs_boot | main.tex:97 | 0.0135 → confirma, 0.0074 → confirma, 4.2 → confirma | sec1_introduction.tex:51; sec1_introduction.tex:53; sec4_montecarlo.tex:236 | confirma |
| abs_ma | main.tex:101 | 0.42 → confirma | sec1_introduction.tex:68; sec4_montecarlo.tex:191; sec5_conclusion.tex:31 | confirma |
| concl_underreject | sec5_conclusion.tex:15 | 2.4 → confirma, 3.3 → confirma | sec1_introduction.tex:44 | confirma |

| Afirmación | Dónde | Valores | Se cumple |
|---|---|---|---|
| los valores simulados de MZ_t-GLS no estan, en promedio, mas cerca del nivel que los asintoticos (treinta disenos) | main.tex (resumen) y sec5_conclusion.tex | D_ii = 0.01347, D_i = 0.01339 | sí |
| el SB 'nearly halves' la distorsion media | sec5_conclusion.tex | ratio_D_iii_over_D_ii = 0.549 | — |
| 'most of which survive' la modificacion de Perron y Qu | sec5_conclusion.tex | a_minus_b_pp = 4.586, a_minus_bp_pp = 4.063, share = 0.886 | sí |
| ningun procedimiento controla el tamano con MA -0.8, n = 100, tendencia | sec5_conclusion.tex | procedures = 21, inside_region = [] | sí |

**(b) Remisiones al suplemento**: 18 `\supp`/`\supptab` en el cuerpo; 18 entradas del registro, 18 coinciden; 0 sin registrar.

| Archivo:línea | Destino | Qué afirma | Comprobaciones | Veredicto |
|---|---|---|---|---|
| sec1_introduction.tex:100 | S5 | la ventana (S_theta), medida y retirada | 3/3 | coincide |
| sec1_introduction.tex:100 | S6 | el segundo canal y el peso adaptativo, medidos y retirados | 4/4 | coincide |
| sec3_theory.tex:119 | S7 | verificacion numerica del caso con tendencia de la consistencia | 6/6 | coincide |
| sec3_theory.tex:161 | S2 | comprobacion de la replica de SB/SWB frente a bootUR | 2/2 | coincide |
| appA_proofs.tex:142 | S7 | la comprobacion anterior de la mediana del HAC con otro piloto | 3/3 | coincide |
| appB_critical_values.tex:13 | S8 | valores criticos de MSB-B (y de S_theta) | 3/3 | coincide |
| sec4_montecarlo.tex:23 | S10 | protocolos, enmiendas y predicciones | 2/2 | coincide |
| sec4_montecarlo.tex:110 | S1 | potencia a tamano igualado con ADF y PP | 5/5 | coincide |
| sec4_montecarlo.tex:124 | S5 | la familia suavizada con theta = 0.02 | 3/3 | coincide |
| sec4_montecarlo.tex:174 | S2 | tablas celda por celda de correlacion serial | 5/5 | coincide |
| sec4_montecarlo.tex:199 | S2 | potencia ajustada de MSB-B bajo correlacion serial | 2/2 | coincide |
| sec4_montecarlo.tex:223 | S2.2 | la comparacion iid/asintotica en caminos independientes (A12) | 2/2 | coincide |
| sec4_montecarlo.tex:228 | S2.3 | tasa por retardo elegido por la MAIC (0.103 y 0.039) | 4/4 | coincide |
| sec4_montecarlo.tex:238 | S2.4 | tamano de MZ_t-GLS con las cinco calibraciones, celda por celda | 2/2 | coincide |
| sec4_montecarlo.tex:319 | S4 | SB y SWB no evaluados bajo quiebres de varianza | 4/4 | coincide |
| sec4_montecarlo.tex:326 | S3 | condicion inicial (0.818 frente a 0.643) | 4/4 | coincide |
| sec4_montecarlo.tex:335 | S4 | quiebres de media y ZA | 3/3 | coincide |
| sec4_montecarlo.tex:340 | S9 | la aplicacion completa | 5/5 | coincide |

Stub de etiqueta `tab:serial` (S2.1) en `main.tex`: presente: sí. La nota de tab_fixedb del v17 (A15) usa `\cref{tab:serial}`: sí; la nota de A16 ya no lo usa (B16.1).

**(c) Cifras retiradas** en texto o tabulares del v17 y del suplemento: 0.333: 1, 6.9 %: 0, 0.6 %: 0, doubles: 0. Además hay 25 apariciones en protocolos y en el changelog (registro histórico).

| Cifra | Dónde | Archivo:línea | Contexto |
|---|---|---|---|
| 0.333 | supplementary | tables/s7_hac_a_rates.tex:8 |  AR 0.95 & 0.1649 & 0.8781 & 0.1295 & 0.8735 & 0.1668 & $-$0.8121 & $-$0.9413 \\ AR 0.5 & 0.3332 & 0.9999 & 0.3120 & 1.0000 & 0.3354 & $-$0.8460 & $-$1.1711 \\ \botto |

**Incoherencias que arrastran los textos del v16 transcritos** (sin editar: S9 va íntegra y las notas son literales):

| Incoherencia | Dónde | Contexto |
|---|---|---|
| extremo superior de la region para 2x10^4 caminos escrito 0.0531; el v17 usa 0.05305 | supplement.tex:169 | t at the median bandwidth $B$ (in parentheses). Bold: outside the exact region $[0.0470, 0.0531]$ for $2\times10^4$  |
| replicas del AWB escritas B = 399; def:awb del v17 usa R (la B es el ancho de banda de Bartlett) | supplement.tex:421 | awb_audit13} \begin{tablenotes}\footnotesize \item 2000 common paths per cell; $B = 399$. Bold: outside the |
| replicas del AWB escritas B = 399; def:awb del v17 usa R (la B es el ancho de banda de Bartlett) | supplement.tex:1027 |  \addlinespace Calibration variant & -- & AWB (Definition~2 of the main text), $B = 399$ & Mean FP $0.022 |

## 2. Compuertas

| Bloque | Criterio | Resultado | Veredicto |
|---|---|---|---|
| E6.4 semillas | 0 colisiones de la familia 160 con 90–159 | 0 | pasa |
| E6.4 invariancia | 0 cambios de k y \|Δ\| rel. ≤ 1e-10 en MSB y MZ_t | cambios de k 0; máx. MSB 3.8e-13; máx. MZ_t 5.1e-10 | NO pasa (MZ_t en n100_c, n200_ct; ver §7) |
| E6.6 prueba con --out | compila sin errores; 0 aciertos identificadores | 0 errores, 0 aciertos | pasa |
| E6.6 reconstrucción | 0 errores, 0 referencias y citas indefinidas, 0 aciertos | 0 / 0 / 0 / 0 | pasa |
| E6.6.1 numeración | S2.1–S2.9 como el mapa | sí | pasa |
| E6.6.3 referencias | 0 sin resolver; «of the main text» sólo al cuerpo del v17 | 0 / 0 | pasa |
| E6.6.4 sec6 íntegra | 0 fragmentos ausentes y cifras iguales | 0 / sí | pasa |

## 3. Procedencia

Entradas: `paper_latex_v17.zip` sha256 `ab84cc28a4862023ed652f01f6cdedab16cf12ad9d6af49ddedc3fe1f76d650d`; `paper_latex_v16.zip` sha256 `7a71eabe0cfa003c4c009b418e84f23ff6799cbdc5a5cd45dc925e90fdc22d7d`. Protocolo: `experiments/protocol_audit15_amend6.md` (enmienda 6), commiteado antes de generar nada.

| Archivo | sha256 (16) | Script | Commit | Código commiteado | Asistente |
|---|---|---|---|---|---|
| experiments/results/code_check_audit16.json | `a650a857d22d99ac` | experiments/audit16_code_check.py | 9c05dd1 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/coherence_v17_audit16.json | `815e47ffe599b2b5` | experiments/audit16_coherence.py | 7a1c852 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/literals_v17b_audit16.json | `a9c538dc70a45fc1` | experiments/audit16_literals.py | 5957172 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v17_audit16.json | `0e95006bf5788536` | experiments/audit16_supplement.py | c659ed3 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v17_trial_audit16.json | `6d964f99a03ae23d` | experiments/audit16_supplement.py | c659ed3 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/tables_audit16/tab_fixedb_audit16.tex | `68180de1225d485c` | experiments/audit16_v17_tables.py | 0cfcc93 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/tables_audit16/tab_fixedb_note_audit16.tex | `1445c70246a88ec2` | experiments/audit16_v17_tables.py | 0cfcc93 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/tables_audit16/tab_summary_audit16.tex | `42ea673a2a0d8218` | experiments/audit16_v17_tables.py | 0cfcc93 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/tables_audit16/tab_summary_note_audit16.tex | `3af9d034cb912f3c` | experiments/audit16_v17_tables.py | 0cfcc93 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/v17_tables_audit16.json | `d0a02c6aad905d8c` | experiments/audit16_v17_tables.py | 0cfcc93 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |

## 4. Desviaciones

| Desviación | Motivo | Cuándo | Efecto |
|---|---|---|---|
| B16.1: los tabulares nuevos van a `tables_audit16/` con sufijo _audit16; `tables_audit15/` y `v17_tables_audit15.json` no se tocan | Regla de no modificar resultados de auditorías anteriores | Antes de generar (E6.1) | El v17 debe cambiar el \input a _audit16 |
| B16.2(c): diagnóstico del \|Δ\| absoluto de MZ_t añadido después de ver que la compuerta no pasaba | Explicar la causa (cancelación) | Tras la primera corrida | El veredicto registrado no cambia |
| B15.7c: ediciones declaradas en los textos transcritos (notas de tablas que pasan completas, título repetido, «And» inicial, autorremisiones «in the supplement») | Las tablas completas invalidan las frases de omisión | Al construir (E6.6) | Registradas una a una en el JSON; S9 sin ediciones |
| B15.7c: macros en conflicto v16/v17 (\Stat, \StatZero) | El texto transcrito es del v16 | Al construir | \Stat = S_θ (v16) en S5; \StatZero = S (v17) |
| B15.7c: texto nuevo en S2 (SB/SWB, Paso 0) y en S4 (frase SB/SWB) | Lo pide el mapa | Al construir | Sólo hechos de E6.3 y cifras del JSON del Paso 0 |
| B15.7c: bibliografía propia del suplemento (natbib, plainnat) con la unión de references.bib del v16 y del v17 | Los textos del v16 citan con \citet/\citep | Al construir | Ninguno sobre las cifras |
| B16.3 N3: se localiza con una expresión propia, no con plantilla | «thirty-six» lleva guion | Al ejecutar | Ninguno |

## 5. No ejecutado

- No se edita ningún `.tex` del manuscrito: el stub de `tab:serial` en `main.tex` lo quita el autor, y el v17 debe pasar a `\input{tables/tab_summary_audit16}` y `tab_fixedb_note_audit16`.
- No se juzga «comparable» (N8), ni «nearly halves» (conclusión): se dan las cifras.

## 6. Conclusiones

- B16.1: tab_summary usa ya la misma potencia de Andrews que tab_fixedb (0.994); la nota de tab_fixedb remite a «Table S2.1 of the supplement».
- B16.2(a): 4 de 8 puntos coinciden con el código; difieren la normalización (n frente a n + 1), la convención T_n para los tests M y DF-GLS en el caso constante, y la muestra de la regresión de DF-GLS.
- B16.2(b): bootUR estima la regresión ADF sin restringir e impone la nula al generar; pesos del SWB gaussianos; residuos sin centrar.
- B16.2(c): el MAIC implementado cumple lo que afirma la prueba: 0 cambios de k en 18000 transformaciones. La compuerta numérica registrada no pasa en MZ_t por cancelación cerca de cero (§7), no por un cambio de ley.
- B16.3: N1–N7: 7 confirman y 0 corrigen; N8 se reporta sin veredicto. N6: 95 de 96 cifras del v16 confirman.
- B15.7c: suplemento reconstruido según el mapa, 36 páginas, sin errores ni referencias indefinidas.
- B15.4: resumen y conclusión 4/4; remisiones 18/18; cifras retiradas en texto o tabulares: 0.333 1, 6.9 % 0, 0.6 % 0, doubles 0.

## 7. Anomalías y contradicciones con el manuscrito

- eq:mstats, MSB, MZ_alpha y MZ_t: normalizacion (sec2_statistics.tex:35; sec2_statistics.tex:37): difiere, sin efecto en el tamano de los brazos calibrados — El texto normaliza con n (n^-2 y n^-1). El codigo usa T = len(y) = n + 1 ((n+1)^-2 y (n+1)^-1). MSB del codigo = MSB del texto x n/(n+1). El brazo con valores criticos asintoticos publicados si depende de ello (control numerico abajo).
- eq:mstats, Convencion T_n del detrending GLS (sec2_statistics.tex:26): difiere para MSB-GLS, MZ_t-GLS y DF-GLS en el caso constante — El texto dice T_n = n (constante) y T_n = n + 1 (tendencia), 'the convention of the replication code'. Es la de MSB-B (src/). np_statistics y arch.DFGLS usan a = 1 + cbar/(n + 1) en los dos casos.
- eq:mstats, Regresion de s2_AR: muestra e indices (sec2_statistics.tex:43; sec2_statistics.tex:42): no especificado en el texto — Muestra comun t = kmax+1..n (n - kmax observaciones) para todo k, tambien para el s2_AR final (no se reestima con t = k+1..n); sigma2_k = SSR_k/(n - kmax).
- eq:mstats, DF-GLS 'in the same regression' (sec2_statistics.tex:45): difiere (muestra) — DF-GLS es arch.DFGLS con el k de la MAIC: mismo detrending y mismo k, pero regresion sobre t = k+1..n, no sobre la muestra comun t = kmax+1..n de la MAIC.
- §3.5 (sec3_theory.tex:155; sec3_theory.tex:156): matiz: 'regression with the null imposed' describe la generacion, no la estimacion
- Compuerta de invariancia no superada en n100_c, n200_ct: el |Δ| relativo de MZ_t llega a 5.1e-10, en caminos con MZ_t = -3.1e-04, -1.1e-04 (numerador de MZ_α casi nulo); el |Δ| absoluto máximo es 8.5e-13 y el k no cambia nunca.
- N6, sec4_montecarlo.tex:105: «1.2» es 1.225; como redondeo confirma, como cota («within») no se cumple; la cota hacia afuera es 1.3.
- Cifra retirada 0.333 en supplementary tables/s7_hac_a_rates.tex:8: `0.3332`. Es la Tabla S7.1 (antigua S4a): pendiente de B antes del techo con el ρ̂ del script (0.3332), la cifra retirada en B15.2; la misma fila da 0.3354 con el ρ̂ de la librería.
- Arrastrado del v16 en el suplemento (supplement.tex:169): extremo superior de la region para 2x10^4 caminos escrito 0.0531; el v17 usa 0.05305.
- Arrastrado del v16 en el suplemento (supplement.tex:421): replicas del AWB escritas B = 399; def:awb del v17 usa R (la B es el ancho de banda de Bartlett).
- Arrastrado del v16 en el suplemento (supplement.tex:1027): replicas del AWB escritas B = 399; def:awb del v17 usa R (la B es el ancho de banda de Bartlett).
- `main.tex` del v17 conserva el stub de etiqueta `tab:serial` (S2.1); con la nota de A16 ya no hace falta.

## Anexo: tabla maestra de los números nuevos

| Clave | Valor | IC/EE | N_sim | N_cal | Familia | JSON | Ruta |
|---|---|---|---|---|---|---|---|
| B16.1 tab_summary MSB-B Andrews D | 0.0828 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[0].D |
| B16.1 tab_summary MSB-B Andrews M | 0.5195 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[0].M |
| B16.1 tab_summary MSB-B Andrews min | 0.0042 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[0].min |
| B16.1 tab_summary MSB-B Andrews max | 0.5696 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[0].max |
| B16.1 tab_summary MSB-B Andrews power | 0.9944 | — | 5000 | — | A12 | v17_tables_audit16.json | summary_rows[0].power |
| B16.1 tab_summary MSB-B fixed-b, b = 0.3 D | 0.0075 | — | 20000 | — | A15 | v17_tables_audit16.json | summary_rows[1].D |
| B16.1 tab_summary MSB-B fixed-b, b = 0.3 M | 0.0354 | — | 20000 | — | A15 | v17_tables_audit16.json | summary_rows[1].M |
| B16.1 tab_summary MSB-B fixed-b, b = 0.3 min | 0.0146 | — | 20000 | — | A15 | v17_tables_audit16.json | summary_rows[1].min |
| B16.1 tab_summary MSB-B fixed-b, b = 0.3 max | 0.0593 | — | 20000 | — | A15 | v17_tables_audit16.json | summary_rows[1].max |
| B16.1 tab_summary MSB-B fixed-b, b = 0.3 power | 0.1868 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[1].power |
| B16.1 tab_summary MSB-GLS iid D | 0.0150 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[2].D |
| B16.1 tab_summary MSB-GLS iid M | 0.0471 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[2].M |
| B16.1 tab_summary MSB-GLS iid min | 0.0133 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[2].min |
| B16.1 tab_summary MSB-GLS iid max | 0.0972 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[2].max |
| B16.1 tab_summary MSB-GLS iid power | 0.9332 | — | 5000 | — | A12 | v17_tables_audit16.json | summary_rows[2].power |
| B16.1 tab_summary MZ_t-GLS asymptotic D | 0.0134 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[3].D |
| B16.1 tab_summary MZ_t-GLS asymptotic M | 0.0408 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[3].M |
| B16.1 tab_summary MZ_t-GLS asymptotic min | 0.0092 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[3].min |
| B16.1 tab_summary MZ_t-GLS asymptotic max | 0.0830 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[3].max |
| B16.1 tab_summary MZ_t-GLS asymptotic power | 0.9225 | — | 2000 | — | A15 | v17_tables_audit16.json | summary_rows[3].power |
| B16.1 tab_summary MZ_t-GLS iid D | 0.0135 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[4].D |
| B16.1 tab_summary MZ_t-GLS iid M | 0.0576 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[4].M |
| B16.1 tab_summary MZ_t-GLS iid min | 0.0170 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[4].min |
| B16.1 tab_summary MZ_t-GLS iid max | 0.1076 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[4].max |
| B16.1 tab_summary MZ_t-GLS iid power | 0.9225 | — | 2000 | — | A15 | v17_tables_audit16.json | summary_rows[4].power |
| B16.1 tab_summary MZ_t-GLS SB (bootUR) D | 0.0074 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[5].D |
| B16.1 tab_summary MZ_t-GLS SB (bootUR) M | 0.0382 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[5].M |
| B16.1 tab_summary MZ_t-GLS SB (bootUR) min | 0.0352 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[5].min |
| B16.1 tab_summary MZ_t-GLS SB (bootUR) max | 0.0882 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[5].max |
| B16.1 tab_summary MZ_t-GLS SB (bootUR) power | 0.8905 | — | 2000 | — | A15 | v17_tables_audit16.json | summary_rows[5].power |
| B16.1 tab_summary MZ_t-GLS SWB (bootUR) D | 0.0072 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[6].D |
| B16.1 tab_summary MZ_t-GLS SWB (bootUR) M | 0.0354 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[6].M |
| B16.1 tab_summary MZ_t-GLS SWB (bootUR) min | 0.0334 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[6].min |
| B16.1 tab_summary MZ_t-GLS SWB (bootUR) max | 0.0854 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[6].max |
| B16.1 tab_summary MZ_t-GLS SWB (bootUR) power | 0.9005 | — | 2000 | — | A15 | v17_tables_audit16.json | summary_rows[6].power |
| B16.1 tab_summary MZ_t-GLS AWB D | 0.0117 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[7].D |
| B16.1 tab_summary MZ_t-GLS AWB M | 0.0408 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[7].M |
| B16.1 tab_summary MZ_t-GLS AWB min | 0.0130 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[7].min |
| B16.1 tab_summary MZ_t-GLS AWB max | 0.0908 | — | 5000 | — | A15 | v17_tables_audit16.json | summary_rows[7].max |
| B16.1 tab_summary MZ_t-GLS AWB power | 0.9065 | — | 2000 | — | A15 | v17_tables_audit16.json | summary_rows[7].power |
| B16.1 tab_summary DF-GLS iid D | 0.0152 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[8].D |
| B16.1 tab_summary DF-GLS iid M | 0.0917 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[8].M |
| B16.1 tab_summary DF-GLS iid min | 0.0362 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[8].min |
| B16.1 tab_summary DF-GLS iid max | 0.1417 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[8].max |
| B16.1 tab_summary DF-GLS iid power | 0.9308 | — | 5000 | — | A12 | v17_tables_audit16.json | summary_rows[8].power |
| B16.1 tab_summary ADF iid D | 0.0731 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[9].D |
| B16.1 tab_summary ADF iid M | 0.6286 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[9].M |
| B16.1 tab_summary ADF iid min | 0.0466 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[9].min |
| B16.1 tab_summary ADF iid max | 0.6786 | — | 20000 | — | A12 | v17_tables_audit16.json | summary_rows[9].max |
| B16.1 tab_summary ADF iid power | 0.8020 | — | 5000 | — | A12 | v17_tables_audit16.json | summary_rows[9].power |
| B16.2(c) n100_c max_rel_msb | 3.8e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_c.max_rel_msb |
| B16.2(c) n100_c max_rel_mzt | 2.7e-10 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_c.max_rel_mzt |
| B16.2(c) n100_c max_rel_s2_over_a2 | 2.6e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_c.max_rel_s2_over_a2 |
| B16.2(c) n100_c max_rel_dfgls | 3.3e-12 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_c.max_rel_dfgls |
| B16.2(c) n100_c min_maic_margin | 3.6e-05 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_c.min_maic_margin |
| B16.2(c) n100_c diagnostic_max_abs_mzt | 6.1e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_c.diagnostic_max_abs_mzt |
| B16.2(c) n100_ct max_rel_msb | 1.8e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_ct.max_rel_msb |
| B16.2(c) n100_ct max_rel_mzt | 3.5e-11 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_ct.max_rel_mzt |
| B16.2(c) n100_ct max_rel_s2_over_a2 | 3.5e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_ct.max_rel_s2_over_a2 |
| B16.2(c) n100_ct max_rel_dfgls | 9.5e-12 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_ct.max_rel_dfgls |
| B16.2(c) n100_ct min_maic_margin | 2.0e-05 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_ct.min_maic_margin |
| B16.2(c) n100_ct diagnostic_max_abs_mzt | 8.5e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n100_ct.diagnostic_max_abs_mzt |
| B16.2(c) n200_c max_rel_msb | 1.8e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_c.max_rel_msb |
| B16.2(c) n200_c max_rel_mzt | 3.0e-11 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_c.max_rel_mzt |
| B16.2(c) n200_c max_rel_s2_over_a2 | 5.6e-14 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_c.max_rel_s2_over_a2 |
| B16.2(c) n200_c max_rel_dfgls | 1.3e-11 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_c.max_rel_dfgls |
| B16.2(c) n200_c min_maic_margin | 4.0e-05 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_c.min_maic_margin |
| B16.2(c) n200_c diagnostic_max_abs_mzt | 4.6e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_c.diagnostic_max_abs_mzt |
| B16.2(c) n200_ct max_rel_msb | 1.7e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_ct.max_rel_msb |
| B16.2(c) n200_ct max_rel_mzt | 5.1e-10 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_ct.max_rel_mzt |
| B16.2(c) n200_ct max_rel_s2_over_a2 | 1.1e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_ct.max_rel_s2_over_a2 |
| B16.2(c) n200_ct max_rel_dfgls | 2.4e-12 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_ct.max_rel_dfgls |
| B16.2(c) n200_ct min_maic_margin | 1.3e-05 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_ct.min_maic_margin |
| B16.2(c) n200_ct diagnostic_max_abs_mzt | 3.3e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n200_ct.diagnostic_max_abs_mzt |
| B16.2(c) n500_c max_rel_msb | 1.6e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_c.max_rel_msb |
| B16.2(c) n500_c max_rel_mzt | 2.8e-11 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_c.max_rel_mzt |
| B16.2(c) n500_c max_rel_s2_over_a2 | 1.4e-14 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_c.max_rel_s2_over_a2 |
| B16.2(c) n500_c max_rel_dfgls | 6.3e-11 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_c.max_rel_dfgls |
| B16.2(c) n500_c min_maic_margin | 2.4e-06 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_c.min_maic_margin |
| B16.2(c) n500_c diagnostic_max_abs_mzt | 4.5e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_c.diagnostic_max_abs_mzt |
| B16.2(c) n500_ct max_rel_msb | 1.9e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_ct.max_rel_msb |
| B16.2(c) n500_ct max_rel_mzt | 3.2e-12 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_ct.max_rel_mzt |
| B16.2(c) n500_ct max_rel_s2_over_a2 | 1.6e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_ct.max_rel_s2_over_a2 |
| B16.2(c) n500_ct max_rel_dfgls | 3.0e-12 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_ct.max_rel_dfgls |
| B16.2(c) n500_ct min_maic_margin | 5.6e-06 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_ct.min_maic_margin |
| B16.2(c) n500_ct diagnostic_max_abs_mzt | 3.9e-13 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.cells.n500_ct.diagnostic_max_abs_mzt |
| B16.2(a) eq:mstats literal n100_c max_rel_msb | 1.0e-02 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n100_c.max_rel_msb |
| B16.2(a) eq:mstats literal n100_c max_abs_mzt | 2.7e-02 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n100_c.max_abs_mzt |
| B16.2(a) eq:mstats literal n100_ct max_rel_msb | 1.0e-02 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n100_ct.max_rel_msb |
| B16.2(a) eq:mstats literal n100_ct max_abs_mzt | 5.0e-02 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n100_ct.max_abs_mzt |
| B16.2(a) eq:mstats literal n200_c max_rel_msb | 5.0e-03 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n200_c.max_rel_msb |
| B16.2(a) eq:mstats literal n200_c max_abs_mzt | 1.8e-02 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n200_c.max_abs_mzt |
| B16.2(a) eq:mstats literal n200_ct max_rel_msb | 5.0e-03 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n200_ct.max_rel_msb |
| B16.2(a) eq:mstats literal n200_ct max_abs_mzt | 1.9e-02 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n200_ct.max_abs_mzt |
| B16.2(a) eq:mstats literal n500_c max_rel_msb | 2.0e-03 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n500_c.max_rel_msb |
| B16.2(a) eq:mstats literal n500_c max_abs_mzt | 7.4e-03 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n500_c.max_abs_mzt |
| B16.2(a) eq:mstats literal n500_ct max_rel_msb | 2.0e-03 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n500_ct.max_rel_msb |
| B16.2(a) eq:mstats literal n500_ct max_abs_mzt | 8.6e-03 | — | 1000 | — | 160 | code_check_audit16.json | c_invariance.literal_eq_mstats_vs_code.n500_ct.max_abs_mzt |
| B16.3 N1[0] | 0.0592 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N1.numbers[0] |
| B16.3 N1[1] | 0.0934 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N1.numbers[1] |
| B16.3 N2[0] | 0.036 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N2.numbers[0] |
| B16.3 N2[1] | 0.054 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N2.numbers[1] |
| B16.3 N4[0] | 0.102727 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N4.numbers[0] |
| B16.3 N4[1] | 0.0390794 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N4.numbers[1] |
| B16.3 N5a[0] | 0.0417 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N5a.numbers[0] |
| B16.3 N5a[1] | 0.0502 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N5a.numbers[1] |
| B16.3 N5b[0] | 0.06605 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N5b.numbers[0] |
| B16.3 N7[0] | 0.0141667 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N7.numbers[0] |
| B16.3 N7[1] | 0.0129883 | — | — | — | A12/A13/A15 | literals_v17b_audit16.json | N.N7.numbers[1] |

