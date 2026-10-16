# Auditoría A17 — reporte (enmienda 7, cierre sobre el v18)

Enmienda 7 commiteada antes de generar nada (§3). No se editó ningún `.tex` del manuscrito ni `src/`.

## 1. Resultados

### B17.1 — eq:mstats del v18, evaluación literal (lectura E7.1)

Caminos de E6.4 (familia 160; colisiones con familias anteriores: 0). Texto: eq_msb sec2_statistics.tex:38, eq_mza sec2_statistics.tex:40, T sec2_statistics.tex:44, common sec2_statistics.tex:48, kmax sec2_statistics.tex:50, dfgls sec2_statistics.tex:53, Tn sec2_statistics.tex:27. Criterio: |Δ| rel. ≤ 1.0e-12 en MSB y |Δ| abs. ≤ 1.0e-10 en MZ_t. Cumple: sí.

| Celda | Caminos | literal del v18 (MSB rel. / MZ_t abs.) | normalizacion por n en lugar de T (MSB rel. / MZ_t abs.) | regresion de s2 en t = k+1..n (MSB rel. / MZ_t abs.) | suma de u_t^2 en t = 0..n (MSB rel. / MZ_t abs.) | sigma2 = SSR/(N - k - 1) (MSB rel. / MZ_t abs.) | k_max distinto | k de la MAIC distinto | máx. rel. t de DF-GLS |
|---|---|---|---|---|---|---|---|---|---|
| n100_c | 1000 | 5.8e-15 / 1.0e-14 | 1.0e-02 / 2.7e-02 | 3.0e-01 / 4.9e-01 | 6.1e-02 / 1.0e-01 | 7.7e-02 / 1.9e-01 | 0 | 0 | 2.0e-13 |
| n100_ct | 1000 | 6.2e-15 / 2.8e-14 | 1.0e-02 / 5.0e-02 | 2.6e-01 / 6.3e-01 | 4.1e-02 / 1.6e-01 | 7.7e-02 / 3.8e-01 | 0 | 0 | 1.2e-13 |
| n200_c | 1000 | 1.1e-15 / 2.4e-15 | 5.0e-03 / 1.8e-02 | 1.8e-01 / 3.0e-01 | 3.8e-02 / 6.1e-02 | 4.1e-02 / 9.5e-02 | 0 | 0 | 8.9e-14 |
| n200_ct | 1000 | 3.8e-15 / 9.3e-15 | 5.0e-03 / 1.9e-02 | 2.4e-01 / 3.9e-01 | 2.4e-02 / 3.3e-02 | 4.1e-02 / 8.4e-02 | 0 | 0 | 2.1e-14 |
| n500_c | 1000 | 2.2e-15 / 2.2e-15 | 2.0e-03 / 7.6e-03 | 6.2e-02 / 1.1e-01 | 1.3e-02 / 2.5e-02 | 1.9e-02 / 3.6e-02 | 0 | 0 | 2.5e-12 |
| n500_ct | 1000 | 2.9e-15 / 7.5e-15 | 2.0e-03 / 8.6e-03 | 4.9e-02 / 1.3e-01 | 7.6e-03 / 1.5e-02 | 1.9e-02 / 4.5e-02 | 0 | 0 | 8.6e-14 |

Descripción del texto: k_max coincide: sí; la MAIC del texto en la muestra común elige el k del código: sí; el t de DF-GLS en t = k+1..n coincide con arch.DFGLS: sí. Las variantes de un solo cambio fallan todas por órdenes de magnitud, así que la comprobación distingue índices, normalización, muestra y divisor.

### B17.2 — §3.5 del v18 frente a bootUR 1.0.5 (lectura E7.2)

| Texto | Afirmación | Código (archivo:línea) | Veredicto | Detalle |
|---|---|---|---|---|
| sec3_theory.tex:151 | R = 399 replicas | experiments/audit15_design.py:36; experiments/audit15_b1_boot.py:97 | coincide | b1_boot_audit15.json config.R = 399 |
| sec3_theory.tex:152 | p-valor (1 + #{T* <= T})/(R + 1) | experiments/audit15_boot_engine.py:372; experiments/audit15_boot_engine.py:374 | coincide | rechazo p <= 0.05 (config.pvalue: (1 + #{T* <= T})/(R + 1); rechazo p <= 0.05) |
| sec3_theory.tex:154 | SB y SWB son los de bootUR 1.0.5 | — | coincide | Paso 0 de A15 (enmienda 3): SB True, SWB True |
| sec3_theory.tex:154 | regresion ADF estimada sin restringir | bootUR/R/bootURtests.R:37; bootUR/src/bootURfunctions.cpp:158 | coincide | la regresion incluye y_{t-1}; su coeficiente se estima |
| sec3_theory.tex:155 | sobre datos detrendidos por MCO | bootUR/R/auxiliary.R:93; bootUR/src/bootURfunctions.cpp:260 | coincide | QD = FALSE en el DGP y en la seleccion del retardo |
| sec3_theory.tex:156 | retardo por la MAIC con el reescalado de Perron y Qu | bootUR/R/bootURtests.R:87; bootUR/src/bootURfunctions.cpp:254; bootUR/src/bootURfunctions.cpp:240 | coincide | valores por defecto de boot_ur |
| sec3_theory.tex:157 | nula impuesta al generar, descartando el coeficiente del nivel retardado | bootUR/R/auxiliary.R:99 | coincide | par[-1] quita el coeficiente de y_{t-1} |
| sec3_theory.tex:159 | incrementos = AR de las diferencias retardadas; serie acumulada bajo raiz unitaria | bootUR/src/bootURfunctions.cpp:516; bootUR/src/bootURfunctions.cpp:519 | coincide | SB_cpp y SWB_cpp |
| sec3_theory.tex:160 | residuos sin centrar | bootUR/src/bootURfunctions.cpp:172; bootUR/R/auxiliary.R:98 | coincide | no hay resta de la media en el camino de e |
| sec3_theory.tex:161 | SB: remuestreo independiente | bootUR/src/bootURfunctions.cpp:629; bootUR/src/bootURfunctions.cpp:512 | coincide con matiz | con reposicion, indices 0..T - l (los ultimos l - 1 residuos no se sortean); el detalle va a S2 |
| sec3_theory.tex:162 | SWB: pesos gaussianos estandar independientes | bootUR/src/bootURfunctions.cpp:619; bootUR/src/bootURfunctions.cpp:526 | coincide | N(0, 1) |
| sec3_theory.tex:163 | replica propia con MZ_t-GLS y su MAIC recalculados en cada serie bootstrap | experiments/audit15_boot_engine.py:354; experiments/audit15_boot_engine.py:62 | coincide | mzt_gls selecciona k por la MAIC GLS en cada ys |
| sec3_theory.tex:164 | la replica se contrasta con el paquete (S2) | — | coincide | Paso 0 con B = 999 (familia 159) y texto en S2 |
| sec3_theory.tex:164 | SWB disenado para choques heterocedasticos | — | cita | afirmacion bibliografica; no es codigo |
| sec3_theory.tex:169 | def:awb: e_t = Delta Y_t - media | experiments/audit15_boot_engine.py:322 | coincide | centrado de los incrementos |
| sec3_theory.tex:170 | def:awb: xi_t = eta xi_{t-1} + (1 - eta^2)^{1/2} nu_t | experiments/audit15_boot_engine.py:333; experiments/audit15_boot_engine.py:323 | coincide | xi_1 = nu_1 (arranque estacionario) |
| sec3_theory.tex:171 | def:awb: eps* = xi e, Y* = suma acumulada | experiments/audit15_boot_engine.py:334 | coincide | Y*_0 = 0 |
| sec3_theory.tex:176 | eta = 0.01^{1/l}, l = round(1.75 n^{1/3}) por defecto de bootUR; eta = 0.631 en n = 200 | bootUR/R/auxiliary.R:265; bootUR/R/auxiliary.R:269; experiments/audit9_engine.py:303; experiments/audit15_b1_boot.py:72 | coincide con matiz | bootUR y nuestro codigo usan T = n + 1 observaciones (nrow(data)); el texto escribe n^{1/3}. En n = 100, 200, 500 dan la misma l: n = 100: l(n) = 8, l(T) = 8; n = 200: l(n) = 10, l(T) = 10; n = 500: l(n) = 14, l(T) = 14 |

Resumen: coincide 15, coincide con matiz 2, difiere 0, cita 1. η en n = 200: 0.630957 (impreso 0.631; confirma: sí).

### B17.3 — Suplemento (lectura E7.3)

| Bloque | Patrón | Sustitución |
|---|---|---|
| S2_serial_table | `\[0\.0470, \d\.\d+\]` | `[0.0470, 0.05305]` |
| S4_breaks | `B = 399` | `R = 399` |
| S9_application | `B = 399` | `R = 399` |

- S2 (sustituye el parrafo SB/SWB de A16): «Three details of the package are not in the main text. First, the SB draws the residuals with replacement from positions $0, \dots, T - l$ only, with $l = \mathrm{round}(1.75\,T^{1/3})$ the default block length, so the last $l - 1$ residuals are never drawn. Second, the regression that defines the b…»
- S7 (despues de tab:hacmedian): «The slope of 1/3 follows from the Andrews rule once $\hat a$ settles; it says nothing about the stochastic part.»

| Comprobación | Valor |
|---|---|
| B_399_left | 0 |
| R_399 | 2 |
| region_old_left | 0 |
| region_new | 1 |
| s7_sentence | 1 |
| s2_details | 1 |

Ediciones aplicadas en la construcción (todas): S1_power ×1; S1_power ×1; S2_serial_table ×1; S3_initial ×1; S4_breaks ×1; S6_twochannel ×1; S6_twochannel ×1; S6_twochannel ×1; S7_trend ×1; S9_application ×1.

`supplementary/` reconstruido: 110 archivos; 0 aciertos identificadores; compila sí, 0 errores, 0 referencias y 0 citas indefinidas, 0 cajas desbordadas, 36 páginas. S2.1–S2.9 como el mapa: sí. Remisiones sin resolver: 0; «of the main text» fuera del cuerpo del v18: 0 (numeradas con la compilación de control del v18, 20 páginas). S9: 143 fragmentos, 0 ausentes, cifras iguales: sí, admitiendo solo «B = 399» → «R = 399».

### B17.4 — Coherencia acotada (lectura E7.4)

Compilación del v18 (con el .bbl entregado): 0 errores, 0 referencias y 0 citas indefinidas, 0 cajas desbordadas, 20 páginas.

| Archivo | Líneas del v18 | Tipo | Comprobaciones | Qué se comprueba | Veredicto |
|---|---|---|---|---|---|
| main.tex | (retirada) | stub | 3/3 | stub de tab:serial retirado de main.tex; compilacion del v18 sin referencias indefinidas; compilacion del v18 sin errores | coincide |
| sec2_statistics.tex | 26–32 | Tn | 2/2 | M y DF-GLS con T_n = n + 1 (experiments/audit8_unitroot.py:64; arch 8.0.0, arch/unitroot/unitroot.py:942); MSB-B: T_n = n (constante, src/stationarity_test/rm_core.py:67) y n + 1 (tendencia, src/stationarity_test/determi | coincide |
| sec2_statistics.tex | 38–38 | mstats | 4/4 | evaluacion literal de eq:mstats (E7.1): MSB rel <= 1e-12 y MZ_t abs <= 1e-10; k_max del texto = codigo; MAIC del texto en la muestra comun = k del codigo; t de DF-GLS en t = k+1..n = arch.DFGLS | coincide |
| sec2_statistics.tex | 40–40 | mstats | 4/4 | evaluacion literal de eq:mstats (E7.1): MSB rel <= 1e-12 y MZ_t abs <= 1e-10; k_max del texto = codigo; MAIC del texto en la muestra comun = k del codigo; t de DF-GLS en t = k+1..n = arch.DFGLS | coincide |
| sec2_statistics.tex | 44–53 | mstats | 4/4 | evaluacion literal de eq:mstats (E7.1): MSB rel <= 1e-12 y MZ_t abs <= 1e-10; k_max del texto = codigo; MAIC del texto en la muestra comun = k del codigo; t de DF-GLS en t = k+1..n = arch.DFGLS | coincide |
| sec3_theory.tex | 154–162 | boot35 | 2/2 | afirmaciones de la seccion 3.5 frente a bootUR y al motor: 0 'difiere' (E7.2); comprobaciones de la seccion 3.5 sin fallos | coincide |
| sec4_montecarlo.tex | 105–105 | within | 1/1 | 'within 1.3' como cota del maximo 1.225 | coincide |
| sec4_montecarlo.tex | 183–183 | inputs | 1/1 | tables/tab_summary_audit16.tex del v18 = tables_audit16/tab_summary_audit16.tex | coincide |
| sec4_montecarlo.tex | 185–185 | inputs | 1/1 | tables/tab_summary_note_audit16.tex del v18 = tables_audit16/tab_summary_note_audit16.tex | coincide |
| sec4_montecarlo.tex | 302–302 | inputs | 1/1 | tables/tab_fixedb_audit16.tex del v18 = tables_audit16/tab_fixedb_audit16.tex | coincide |
| sec4_montecarlo.tex | 304–304 | inputs | 1/1 | tables/tab_fixedb_note_audit16.tex del v18 = tables_audit16/tab_fixedb_note_audit16.tex | coincide |
| tables/tab_fixedb_audit15.tex | (retirada) | table_removed | 1/1 | tables/tab_fixedb_audit15.tex ya no se usa en el v18 | coincide |
| tables/tab_fixedb_audit16.tex | 1–15 | table_added | 1/1 | tables/tab_fixedb_audit16.tex del v18 = tables_audit16/tab_fixedb_audit16.tex | coincide |
| tables/tab_fixedb_note_audit15.tex | (retirada) | table_removed | 1/1 | tables/tab_fixedb_note_audit15.tex ya no se usa en el v18 | coincide |
| tables/tab_fixedb_note_audit16.tex | 1–2 | table_added | 1/1 | tables/tab_fixedb_note_audit16.tex del v18 = tables_audit16/tab_fixedb_note_audit16.tex | coincide |
| tables/tab_summary_audit15.tex | (retirada) | table_removed | 1/1 | tables/tab_summary_audit15.tex ya no se usa en el v18 | coincide |
| tables/tab_summary_audit16.tex | 1–23 | table_added | 1/1 | tables/tab_summary_audit16.tex del v18 = tables_audit16/tab_summary_audit16.tex | coincide |
| tables/tab_summary_note_audit15.tex | (retirada) | table_removed | 1/1 | tables/tab_summary_note_audit15.tex ya no se usa en el v18 | coincide |
| tables/tab_summary_note_audit16.tex | 1–2 | table_added | 1/1 | tables/tab_summary_note_audit16.tex del v18 = tables_audit16/tab_summary_note_audit16.tex | coincide |

- S2.1 (tab:serial): regenerada desde `bA_ma_audit12.json` e igual a la del suplemento: sí (36 celdas); nota: region [0.0470, 0.05305] en la nota sí; 2x10^4 caminos (config.N_size = 20000) sí; N_cal = 5x10^5 (config.N_cal = 500000) sí.
- S4.3 (tab:awb): idéntica a `tables_audit13/`: sí; nota: 2000 caminos comunes (config.N_sim) sí; R = 399 replicas (config.B) sí; sin 'B = 399' sí; region [0.0405, 0.0600] para 2000 caminos sí. Observación: el p-valor del AWB de A13 es #{stat* <= stat} / B; la seccion 3.5 da (1 + #{T* <= T})/(R + 1) para las tres calibraciones de MZ_t.
- S7.1 (tab:hacrates): todas las cifras iguales a `e4_slope_audit15.json` con redondeo binario: sí; frase de S7 presente: sí. Pendientes de B antes del techo (script / librería): RW 0.0090 / 0.0109; AR 0.95 0.1649 / 0.1668; AR 0.5 0.3332 / 0.3354.
- S9.2 (tab:deviations): «R = 399»: sí; queda «B = 399»: no. Cifras: pilot confirma (0.02770→confirma, 0.02786→confirma); stat_window confirma (0.0277→confirma, 0.0224→confirma, 13→confirma, 17→confirma, 33.8→confirma, 29.7→confirma, 0.0229→confirma, 0.0224→confirma, 17→confirma, 17→confirma, 29.6→confirma, 29.7→confirma); dkw confirma (0.0061→confirma); awb confirma (0.0224→confirma, 0.0217→confirma, 17→confirma, 13→confirma, 29.7→confirma, 40.3→confirma); ncal confirma (0.0301→confirma, 13→confirma).

### B17.5 — Compilación conjunta y paquete de envío (lectura E7.5)

- v18: 0 errores, 0 referencias y 0 citas indefinidas, 20 páginas; el .bbl entregado coincide con el que genera bibtex: sí.
- Suplemento: 0 errores, 0 referencias y 0 citas indefinidas, 36 páginas.
- Paquete: 135 archivos; zip `submission_v18.zip`, 769135 bytes, sha256 `300179c8b6fd0a662ee14a6329fbd971f94b560a56477888fd7531b0b83fe805` (no se commitea). `supplementary/` del commit `246ccfe`, sin cambios en el árbol: sí.
- Incluidos: appA_proofs.tex, appB_critical_values.tex, main.tex, sec1_introduction.tex, sec2_statistics.tex, sec3_theory.tex, sec4_montecarlo.tex, sec5_conclusion.tex; tabulares: tables/tab_attrib_audit13.tex, tables/tab_attrib_note_audit13.tex, tables/tab_bootpower_audit15.tex, tables/tab_bootpower_note_audit15.tex, tables/tab_calib_audit13.tex, tables/tab_critMSB_audit14.tex, tables/tab_critMSB_note_audit14.tex, tables/tab_fixedb_audit16.tex, tables/tab_fixedb_note_audit16.tex, tables/tab_localpower_audit13.tex, tables/tab_summary_audit16.tex, tables/tab_summary_note_audit16.tex; figuras: figures/fig_calibration_gain_audit13q.pdf.
- Excluidos del zip del v18: CHANGELOG_v17.md, CHANGELOG_v18.md, SUPPLEMENT_MAP_v17.md, cover_letter.md, main.pdf, tables/tab_boot_audit15.tex, tables/tab_boot_note_audit15.tex, tables/tab_fixedb_size_audit15.tex, tables/tab_fixedb_size_note_audit15.tex, tables/tab_lag_audit15.tex, tables/tab_serial_asy_audit15.tex.
- Artefactos de compilación en el paquete: 0. Aciertos que identifican al autor (ruta, usuario, apellido, URL del repositorio): 0. Otros aciertos: hash_de_commit.
- Metadatos de los PDF (6): campos presentes creationDate, creator, format, producer; ninguno con autor.

| Archivo | Bytes | sha256 |
|---|---|---|
| appA_proofs.tex | 7437 | `5a57f0b156fa72aa` |
| appB_critical_values.tex | 1171 | `7783dddc0167c115` |
| figures/fig_calibration_gain_audit13q.pdf | 16399 | `84f209f72dbedf1e` |
| interact.cls | 25198 | `d9603354ce657c99` |
| main.bbl | 6677 | `f2bc8ef7d289027d` |
| main.tex | 4452 | `099a75c840196336` |
| references.bib | 18322 | `0a9c0d95dd0c842e` |
| sec1_introduction.tex | 8689 | `c65133b6548f7298` |
| sec2_statistics.tex | 5576 | `052b9038552a2201` |
| sec3_theory.tex | 9600 | `897160dad81b3997` |
| sec4_montecarlo.tex | 18210 | `a0a7ca6d839b1cc2` |
| sec5_conclusion.tex | 3308 | `0f8a9e87677229e2` |
| tables/tab_attrib_audit13.tex | 1523 | `d9ae3a12499055b4` |
| tables/tab_attrib_note_audit13.tex | 610 | `c3a62c51726a082a` |
| tables/tab_bootpower_audit15.tex | 1790 | `70b6156c41a3def6` |
| tables/tab_bootpower_note_audit15.tex | 352 | `f3b80a69738cdaf6` |
| tables/tab_calib_audit13.tex | 1918 | `50386f28974cec10` |
| tables/tab_critMSB_audit14.tex | 1128 | `152b4ec3ad2b01ae` |
| tables/tab_critMSB_note_audit14.tex | 572 | `e4853481d5431451` |
| tables/tab_fixedb_audit16.tex | 860 | `68180de1225d485c` |
| tables/tab_fixedb_note_audit16.tex | 737 | `1445c70246a88ec2` |
| tables/tab_localpower_audit13.tex | 1194 | `a0a939eb090ae819` |
| tables/tab_summary_audit16.tex | 1099 | `42ea673a2a0d8218` |
| tables/tab_summary_note_audit16.tex | 1084 | `3af9d034cb912f3c` |
| tfnlm.bst | 40233 | `cf9cf80f3eae980d` |

## 2. Compuertas

| Bloque | Criterio | Resultado | Veredicto |
|---|---|---|---|
| E7.1 | MSB rel. ≤ 1e-12 y MZ_t abs. ≤ 1e-10 en todos los caminos | máx. 6.2e-15 / 2.8e-14 | pasa |
| E7.1 descripción | k_max, k de la MAIC y muestra de DF-GLS | sí / sí / sí | pasa |
| E7.2 | 0 afirmaciones que difieren; comprobaciones sin fallo | 0 / 0 | pasa |
| E7.3 prueba --out | 0 errores y 0 aciertos | 0 / 0 | pasa |
| E7.3 reconstrucción | ediciones aplicadas; 0 errores; S9 íntegra salvo B→R | B=399 restantes 0; errores 0; ausentes 0 | pasa |
| E7.4 | todos los hunks del diff coinciden | 19/19 | pasa |
| E7.5 | puertas del paquete | v18_clean sí, supplement_clean sí, no_artifacts sí, no_author_hits sí, supplementary_committed sí | pasa |

## 3. Procedencia

Entrada: `paper_latex_v18.zip` sha256 `b78cf82e25631a7dbcb004041eaffa02f3fab68c622e135f780f54b3c721a653`. Protocolo: `experiments/protocol_audit15_amend7.md` (enmienda 7), commiteado antes de generar nada.

| Archivo | sha256 (16) | Script | Commit | Código commiteado | Asistente |
|---|---|---|---|---|---|
| experiments/results/boot35_v18_audit17.json | `deba18219f140c2d` | experiments/audit17_boot35.py | 63d7313 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/coherence_v18_audit17.json | `d9b545db9ee25b67` | experiments/audit17_coherence.py | 21ebdd4 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/mstats_v18_audit17.json | `8b21ef76daa765f0` | experiments/audit17_mstats.py | 310f241 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/submission_v18_audit17.json | `9ffbe320bf8a8f8d` | experiments/audit17_package.py | f706961 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v18_audit17.json | `70f6a0941451094b` | experiments/audit17_supplement.py | 91ce91c | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v18_trial_audit17.json | `66d164473cf023e2` | experiments/audit17_supplement.py | 91ce91c | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |

## 4. Desviaciones

| Desviación | Motivo | Cuándo | Efecto |
|---|---|---|---|
| B17.3 se construye con `audit17_supplement.py`, que reutiliza `audit16_supplement.py` sin modificarlo | Regla de no modificar el código de auditorías anteriores | Antes de generar (E7.3) | Ninguno |
| El párrafo SB/SWB de A16 se sustituye entero por el de B17 | El cuerpo del v18 ya da lo que decía; el encargo pide solo los detalles que el cuerpo no da | Al construir | El párrafo del Paso 0 se conserva |
| S9 recibe una edición («B = 399» → «R = 399») | Lo pide el encargo | Al construir | La integridad de S9 se comprueba admitiendo solo esa sustitución |
| El zip del paquete no se commitea | Es un entregable derivado; lo registran su sha256 y la lista de archivos | E7.5 | Ninguno |

## 5. No ejecutado

- No se edita ningún `.tex` del manuscrito.
- No se envía el paquete: se entrega al autor.

## 6. Conclusiones

- B17.1: eq:mstats del v18, leída literalmente, reproduce `np_statistics` (máx. 6.2e-15 en MSB, 2.8e-14 en MZ_t); la descripción de s²_AR, k_max y la muestra de DF-GLS coincide con el código.
- B17.2: §3.5: coincide 15, coincide con matiz 2, difiere 0, cita 1.
- B17.3: suplemento reconstruido con las cuatro ediciones, 36 páginas, sin errores.
- B17.4: 19 de 19 hunks del diff coinciden; las cuatro tablas del suplemento coinciden con sus fuentes.
- B17.5: v18 (20 páginas) y suplemento (36 páginas) compilan juntos sin errores; paquete de 135 archivos sin artefactos ni aciertos de autor.

## 7. Anomalías y observaciones

- §3.5 (sec3_theory.tex:161), SB: remuestreo independiente: con reposicion, indices 0..T - l (los ultimos l - 1 residuos no se sortean); el detalle va a S2.
- §3.5 (sec3_theory.tex:176), eta = 0.01^{1/l}, l = round(1.75 n^{1/3}) por defecto de bootUR; eta = 0.631 en n = 200: bootUR y nuestro codigo usan T = n + 1 observaciones (nrow(data)); el texto escribe n^{1/3}. En n = 100, 200, 500 dan la misma l: n = 100: l(n) = 8, l(T) = 8; n = 200: l(n) = 10, l(T) = 10; n = 500: l(n) = 14, l(T) = 14.
- S4.3 (tab:awb): el p-valor del AWB de A13 es #{stat* <= stat} / B; la seccion 3.5 da (1 + #{T* <= T})/(R + 1) para las tres calibraciones de MZ_t.
- Los PDF de figuras llevan fecha de creación con zona horaria (D:20260923133836-06'00', D:20260923133837-06'00'); no identifican al autor.
- Hashes de commit en 22 archivos de `supplementary/data/` (se conservan desde B15.5).

## Anexo: tabla maestra de los números nuevos

| Clave | Valor | IC/EE | N_sim | N_cal | Familia | JSON | Ruta |
|---|---|---|---|---|---|---|---|
| B17.1 n100_c text msb_rel | 5.8e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.text.msb_rel |
| B17.1 n100_c text mzt_abs | 1.0e-14 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.text.mzt_abs |
| B17.1 n100_c norm_n msb_rel | 1.0e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.norm_n.msb_rel |
| B17.1 n100_c norm_n mzt_abs | 2.7e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.norm_n.mzt_abs |
| B17.1 n100_c sample_k1 msb_rel | 3.0e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.sample_k1.msb_rel |
| B17.1 n100_c sample_k1 mzt_abs | 4.9e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.sample_k1.mzt_abs |
| B17.1 n100_c sum_t0_n msb_rel | 6.1e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.sum_t0_n.msb_rel |
| B17.1 n100_c sum_t0_n mzt_abs | 1.0e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.sum_t0_n.mzt_abs |
| B17.1 n100_c divisor_dof msb_rel | 7.7e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.divisor_dof.msb_rel |
| B17.1 n100_c divisor_dof mzt_abs | 1.9e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.variants.divisor_dof.mzt_abs |
| B17.1 n100_c dfgls_max_rel | 2.0e-13 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_c.dfgls_max_rel |
| B17.1 n100_ct text msb_rel | 6.2e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.text.msb_rel |
| B17.1 n100_ct text mzt_abs | 2.8e-14 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.text.mzt_abs |
| B17.1 n100_ct norm_n msb_rel | 1.0e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.norm_n.msb_rel |
| B17.1 n100_ct norm_n mzt_abs | 5.0e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.norm_n.mzt_abs |
| B17.1 n100_ct sample_k1 msb_rel | 2.6e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.sample_k1.msb_rel |
| B17.1 n100_ct sample_k1 mzt_abs | 6.3e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.sample_k1.mzt_abs |
| B17.1 n100_ct sum_t0_n msb_rel | 4.1e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.sum_t0_n.msb_rel |
| B17.1 n100_ct sum_t0_n mzt_abs | 1.6e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.sum_t0_n.mzt_abs |
| B17.1 n100_ct divisor_dof msb_rel | 7.7e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.divisor_dof.msb_rel |
| B17.1 n100_ct divisor_dof mzt_abs | 3.8e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.variants.divisor_dof.mzt_abs |
| B17.1 n100_ct dfgls_max_rel | 1.2e-13 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n100_ct.dfgls_max_rel |
| B17.1 n200_c text msb_rel | 1.1e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.text.msb_rel |
| B17.1 n200_c text mzt_abs | 2.4e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.text.mzt_abs |
| B17.1 n200_c norm_n msb_rel | 5.0e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.norm_n.msb_rel |
| B17.1 n200_c norm_n mzt_abs | 1.8e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.norm_n.mzt_abs |
| B17.1 n200_c sample_k1 msb_rel | 1.8e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.sample_k1.msb_rel |
| B17.1 n200_c sample_k1 mzt_abs | 3.0e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.sample_k1.mzt_abs |
| B17.1 n200_c sum_t0_n msb_rel | 3.8e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.sum_t0_n.msb_rel |
| B17.1 n200_c sum_t0_n mzt_abs | 6.1e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.sum_t0_n.mzt_abs |
| B17.1 n200_c divisor_dof msb_rel | 4.1e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.divisor_dof.msb_rel |
| B17.1 n200_c divisor_dof mzt_abs | 9.5e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.variants.divisor_dof.mzt_abs |
| B17.1 n200_c dfgls_max_rel | 8.9e-14 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_c.dfgls_max_rel |
| B17.1 n200_ct text msb_rel | 3.8e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.text.msb_rel |
| B17.1 n200_ct text mzt_abs | 9.3e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.text.mzt_abs |
| B17.1 n200_ct norm_n msb_rel | 5.0e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.norm_n.msb_rel |
| B17.1 n200_ct norm_n mzt_abs | 1.9e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.norm_n.mzt_abs |
| B17.1 n200_ct sample_k1 msb_rel | 2.4e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.sample_k1.msb_rel |
| B17.1 n200_ct sample_k1 mzt_abs | 3.9e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.sample_k1.mzt_abs |
| B17.1 n200_ct sum_t0_n msb_rel | 2.4e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.sum_t0_n.msb_rel |
| B17.1 n200_ct sum_t0_n mzt_abs | 3.3e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.sum_t0_n.mzt_abs |
| B17.1 n200_ct divisor_dof msb_rel | 4.1e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.divisor_dof.msb_rel |
| B17.1 n200_ct divisor_dof mzt_abs | 8.4e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.variants.divisor_dof.mzt_abs |
| B17.1 n200_ct dfgls_max_rel | 2.1e-14 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n200_ct.dfgls_max_rel |
| B17.1 n500_c text msb_rel | 2.2e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.text.msb_rel |
| B17.1 n500_c text mzt_abs | 2.2e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.text.mzt_abs |
| B17.1 n500_c norm_n msb_rel | 2.0e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.norm_n.msb_rel |
| B17.1 n500_c norm_n mzt_abs | 7.6e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.norm_n.mzt_abs |
| B17.1 n500_c sample_k1 msb_rel | 6.2e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.sample_k1.msb_rel |
| B17.1 n500_c sample_k1 mzt_abs | 1.1e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.sample_k1.mzt_abs |
| B17.1 n500_c sum_t0_n msb_rel | 1.3e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.sum_t0_n.msb_rel |
| B17.1 n500_c sum_t0_n mzt_abs | 2.5e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.sum_t0_n.mzt_abs |
| B17.1 n500_c divisor_dof msb_rel | 1.9e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.divisor_dof.msb_rel |
| B17.1 n500_c divisor_dof mzt_abs | 3.6e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.variants.divisor_dof.mzt_abs |
| B17.1 n500_c dfgls_max_rel | 2.5e-12 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_c.dfgls_max_rel |
| B17.1 n500_ct text msb_rel | 2.9e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.text.msb_rel |
| B17.1 n500_ct text mzt_abs | 7.5e-15 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.text.mzt_abs |
| B17.1 n500_ct norm_n msb_rel | 2.0e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.norm_n.msb_rel |
| B17.1 n500_ct norm_n mzt_abs | 8.6e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.norm_n.mzt_abs |
| B17.1 n500_ct sample_k1 msb_rel | 4.9e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.sample_k1.msb_rel |
| B17.1 n500_ct sample_k1 mzt_abs | 1.3e-01 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.sample_k1.mzt_abs |
| B17.1 n500_ct sum_t0_n msb_rel | 7.6e-03 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.sum_t0_n.msb_rel |
| B17.1 n500_ct sum_t0_n mzt_abs | 1.5e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.sum_t0_n.mzt_abs |
| B17.1 n500_ct divisor_dof msb_rel | 1.9e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.divisor_dof.msb_rel |
| B17.1 n500_ct divisor_dof mzt_abs | 4.5e-02 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.variants.divisor_dof.mzt_abs |
| B17.1 n500_ct dfgls_max_rel | 8.6e-14 | — | 1000 | — | 160 | mstats_v18_audit17.json | cells.n500_ct.dfgls_max_rel |
| B17.2 eta n = 100 (regla del código) | 0.562341 | — | — | — | — | boot35_v18_audit17.json | eta.100.eta_code |
| B17.2 eta n = 200 (regla del código) | 0.630957 | — | — | — | — | boot35_v18_audit17.json | eta.200.eta_code |
| B17.2 eta n = 500 (regla del código) | 0.719686 | — | — | — | — | boot35_v18_audit17.json | eta.500.eta_code |

