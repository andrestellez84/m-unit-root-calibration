# Auditoría A14 — Valores críticos del suplemento, fuentes pendientes y verificación de v15

Protocolo `experiments/protocol_audit14.md` (commit `b079b8d`). Manuscrito: `paper_latex_v15.zip` (sha256 `1d52f85a9aeed19b08f5c9e4fc69ff34ce4f39cacfef703314dcc55d2786144b`), de sólo lectura; no se editó ningún `.tex`. Ninguna simulación nueva; la familia 150 no se usa.

## 1. Resultados

### B14.0 — Entrada v15

`paper_latex_v15.zip`, sha256 `1d52f85a9aeed19b08f5c9e4fc69ff34ce4f39cacfef703314dcc55d2786144b` (155686 bytes), leído dentro del zip sin extraerlo. La familia 150 queda reservada y sin uso (colisión con las familias 90–149: no).

Tabulares: 17 archivos en `v15/tables/` (16 tabulares y la nota de tab:attrib). Figuras: 6. Idénticos byte a byte a los exportados por A13 y B13.Q: **sí, todos**.

| Archivo del v15 | Exportado | sha256 | Idéntico |
|---|---|---|---|
| figures/fig_calibration_gain_audit13q.pdf | paper/figures/fig_calibration_gain_audit13q.pdf | `84f209f72dbedf1e5cd6ccaa8c449310eba9c1b765405f9fced375f812d595ef` | sí |
| figures/fig_dgp3_audit13q.pdf | paper/figures/fig_dgp3_audit13q.pdf | `d51a8eda794c53e058e7c87b1e0da2ddbd74d20e0376ab55dccf869385d2a4d3` | sí |
| figures/fig_local_power_audit13q.pdf | paper/figures/fig_local_power_audit13q.pdf | `6741bcddfd4d973c4e3216a9ebdd035eb5d793583180f2a1d20d4500751743a2` | sí |
| figures/fig_power_equalized_audit13q.pdf | paper/figures/fig_power_equalized_audit13q.pdf | `b742a8c2b3b8ec1b7535e3825584cc84753ab95c40c5c31346b72546121bc8ad` | sí |
| figures/fig_size_shift_audit13q.pdf | paper/figures/fig_size_shift_audit13q.pdf | `aaeb311b9112183849aa4fe51a74c932052e86f709dd411d228f0fbee04d3001` | sí |
| figures/fig_theta_ladder_audit13q.pdf | paper/figures/fig_theta_ladder_audit13q.pdf | `40d01b8b3282157eff8f5785aa9170f1f25911148651dc960e265c84faeb7669` | sí |
| tables/tab_attrib_audit13.tex | experiments/results/tables_audit13/tab_attrib_audit13.tex | `d9ae3a12499055b4b47746dad621701853ee22c1a908d5d8d8c6a65c5117beaf` | sí |
| tables/tab_attrib_note_audit13.tex | experiments/results/tables_audit13/tab_attrib_note_audit13.tex | `c3a62c51726a082a221460b2d5f734b8a78ca46c50c850b4add5df55b132c41c` | sí |
| tables/tab_awb_audit13.tex | experiments/results/tables_audit13/tab_awb_audit13.tex | `2953b2372b26706d6f7e0499c71aa792ce712595b4cbdd47b9675d824efe7452` | sí |
| tables/tab_calib_audit13.tex | experiments/results/tables_audit13/tab_calib_audit13.tex | `50386f28974cec10a0339f3f584d60ae53b063011c41030857cbc146ba2b2c24` | sí |
| tables/tab_critB_audit13.tex | experiments/results/tables_audit13/tab_critB_audit13.tex | `55d2a2727db124002a31f4148eb7cc21b7b5d8fbbd49d73e4672ab1003b470af` | sí |
| tables/tab_ctpower_audit13.tex | experiments/results/tables_audit13/tab_ctpower_audit13.tex | `afc906a11671c33110ae3fdf366775bcbdd8af626fc55b0aed79d41efbfbb7ac` | sí |
| tables/tab_dgp1_audit13.tex | experiments/results/tables_audit13/tab_dgp1_audit13.tex | `1d37d8f8166edb48b3bafb4aa0e3cc51a0d677844e997b8dfb2ee420d22a8cdd` | sí |
| tables/tab_dgp2_audit13.tex | experiments/results/tables_audit13/tab_dgp2_audit13.tex | `82820f35e76b9b476ce42e276bcfed9e9d97d40220c078d283fa4558904d06cc` | sí |
| tables/tab_dgp3_audit13.tex | experiments/results/tables_audit13/tab_dgp3_audit13.tex | `50447ad976cf25c02d6dcce3fffeffcb78410b18e9033f1653556f7bd34d510f` | sí |
| tables/tab_dgp5_audit13.tex | experiments/results/tables_audit13/tab_dgp5_audit13.tex | `cbfd0696261fecf92a3d2f6f04ee468324b6edab60d5cb93c802a3f7325e503d` | sí |
| tables/tab_fp_audit13.tex | experiments/results/tables_audit13/tab_fp_audit13.tex | `b76b26cd4e462328e66c46a12fa0790c23f606a67dec9f5551d0f16e45364e89` | sí |
| tables/tab_initial_audit13.tex | experiments/results/tables_audit13/tab_initial_audit13.tex | `4dcfc29ddf0bd2b42164cd0075a19a909c4505b8b51524c9b04fd1c58bcee695` | sí |
| tables/tab_localpower_audit13.tex | experiments/results/tables_audit13/tab_localpower_audit13.tex | `a0a939eb090ae819641ea658e7642ac22f0732d432af54af6b080671615dce6e` | sí |
| tables/tab_misspec_audit13.tex | experiments/results/tables_audit13/tab_misspec_audit13.tex | `4c3f8474263c0243cc663446931ce3d79ac3810ec443d9839d96b11bd3ec1dcf` | sí |
| tables/tab_serial_audit13.tex | experiments/results/tables_audit13/tab_serial_audit13.tex | `cd6a1d7ade12ea0784c217dada4aa82b92c37a7ba66bafeecaceb1ae8d9ad66b` | sí |
| tables/tab_serialpower_audit13.tex | experiments/results/tables_audit13/tab_serialpower_audit13.tex | `89c7c311f5e3b04a7ee9492ca8cb7ed1589e5ee4a27541279f04d91104439db7` | sí |
| tables/tab_size_audit13.tex | experiments/results/tables_audit13/tab_size_audit13.tex | `8b57a3f1289301aad0bba50c6c2af2bca994b00070f78aafbab364d6eab3698b` | sí |

Extensión declarada: 23 referencias `\input{tables/…}` e `\includegraphics` en el texto; todas apuntan a un archivo del zip: sí. Archivos de tablas o figuras sin referencia: ninguno. Figuras `*_audit13.pdf` sin la q en el zip: ninguna.

### B14.1 — Valores críticos de MSB-GLS y MZ_t-GLS (suplemento S5)

Cuantil de cola inferior: numpy.nanquantile(x, alpha), metodo lineal (audit9_engine.rejector). Se rechaza cuando el estadístico es menor que q_α. Retardo: MAIC de Ng-Perron (audit8_unitroot.np_statistics), residuos GLS. EE: EE bootstrap exacto (B -> infinito) del cuantil lineal; audit14_exact_bootstrap. No se usan números aleatorios.

| n | Muestra | sha256 | Filas | NaN por columna |
|---|---|---|---|---|
| 100 | experiments/results/checkpoints/audit10_cal/cal_n100.npz | `a9450094bbdac8dedc43b4a2848d56137d764ca38a5c9438bf57447eb8caf2c2` | 500000 | c\|msb 0, c\|mzt 0, ct\|msb 0, ct\|mzt 0 |
| 200 | experiments/results/checkpoints/audit10_cal/cal_n200.npz | `f697a626f39496f819879fda8a852d577d24d334d533261e7b9d1fb6e667586e` | 500000 | c\|msb 0, c\|mzt 0, ct\|msb 0, ct\|mzt 0 |
| 500 | experiments/results/checkpoints/audit10_cal/cal_n500.npz | `53b7f83c019b6732fb2659cb468c79afd1cd6d106cc8ae3c91b1dff63d104219` | 500000 | c\|msb 0, c\|mzt 0, ct\|msb 0, ct\|mzt 0 |
| 1000 | experiments/results/checkpoints/audit10_cal/cal_n1000.npz | `15ee7be326f76af4fcde57b51763a8b19876a9042c5f36792c878c43696ca14b` | 500000 | c\|msb 0, c\|mzt 0, ct\|msb 0, ct\|mzt 0 |

| Estadístico | Caso | n | q_0.01 (EE) | q_0.025 (EE) | q_0.05 (EE) | q_0.1 (EE) |
|---|---|---|---|---|---|---|
| MSB-GLS | constante | 100 | 0.192702 (2.78e-04) | 0.213716 (2.49e-04) | 0.235577 (2.26e-04) ᵉ | 0.266037 (2.32e-04) |
| MSB-GLS | constante | 200 | 0.190504 (2.64e-04) | 0.213073 (2.58e-04) | 0.236918 (2.26e-04) ᵉ | 0.270337 (2.41e-04) |
| MSB-GLS | constante | 500 | 0.188828 (3.15e-04) | 0.212555 (2.82e-04) | 0.237642 (2.68e-04) ᵉ | 0.273924 (2.81e-04) |
| MSB-GLS | constante | 1000 | 0.186863 (3.37e-04) | 0.211669 (2.88e-04) | 0.237512 (2.77e-04) ᵉ | 0.274843 (2.91e-04) |
| MSB-GLS | tendencia | 100 | 0.157479 (2.05e-04) | 0.169702 (1.31e-04) | 0.181441 (1.29e-04) ᵉ | 0.197150 (1.17e-04) |
| MSB-GLS | tendencia | 200 | 0.153539 (1.74e-04) | 0.166045 (1.27e-04) | 0.178323 (1.22e-04) ᵉ | 0.194715 (1.16e-04) |
| MSB-GLS | tendencia | 500 | 0.149385 (1.77e-04) | 0.162368 (1.50e-04) | 0.175104 (1.28e-04) ᵉ | 0.192140 (1.17e-04) |
| MSB-GLS | tendencia | 1000 | 0.147214 (1.88e-04) | 0.160427 (1.58e-04) | 0.173389 (1.35e-04) ᵉ | 0.190787 (1.27e-04) |
| MZ_t-GLS | constante | 100 | -2.45111 (3.64e-03) | -2.18102 (2.73e-03) | -1.95277 (2.24e-03) ᵉ | -1.68934 (1.88e-03) |
| MZ_t-GLS | constante | 200 | -2.48907 (3.88e-03) | -2.19711 (3.03e-03) | -1.94606 (2.47e-03) ᵉ | -1.65953 (1.82e-03) |
| MZ_t-GLS | constante | 500 | -2.52178 (4.40e-03) | -2.20836 (3.03e-03) | -1.94187 (2.42e-03) ᵉ | -1.63748 (2.14e-03) |
| MZ_t-GLS | constante | 1000 | -2.54353 (4.60e-03) | -2.22050 (3.59e-03) | -1.94169 (2.71e-03) ᵉ | -1.62808 (2.08e-03) |
| MZ_t-GLS | tendencia | 100 | -3.09856 (3.42e-03) | -2.86586 (2.48e-03) | -2.66552 (1.80e-03) ᵉ | -2.43643 (1.52e-03) |
| MZ_t-GLS | tendencia | 200 | -3.18843 (3.86e-03) | -2.93491 (2.64e-03) | -2.72140 (2.09e-03) ᵉ | -2.47601 (1.62e-03) |
| MZ_t-GLS | tendencia | 500 | -3.28514 (4.33e-03) | -3.00910 (2.42e-03) | -2.77621 (2.16e-03) ᵉ | -2.51319 (1.68e-03) |
| MZ_t-GLS | tendencia | 1000 | -3.33176 (3.91e-03) | -3.04719 (2.89e-03) | -2.80406 (2.22e-03) ᵉ | -2.52993 (1.79e-03) |

ᵉ: ya existía (Paso 0). Los 48 valores restantes son nuevos. Tabla con dos decimales más que el tabular; EE bootstrap exacto entre paréntesis.

Controles:

- EE de Maritz–Jarrett / EE exacto: entre 0.9992 y 1.0010.
- Masa de las marginales y residuo del truncamiento dentro de tolerancia: sí.
- El cuantil de la función del EE coincide con `nanquantile` en los 64 valores: sí.
- NaN en las columnas usadas: ninguno.
- Validación de las fórmulas por enumeración exhaustiva de N^N remuestras con N ≤ 6: `tests/test_audit14_exact_bootstrap.py`.

| Salida (desde `b1_critical_audit14.json`) | sha256 |
|---|---|
| experiments/results/tables_audit14/tab_critMSB_audit14.tex | `152b4ec3ad2b01ae67020547dd2f2a471f3a626439330103af0f8802dc22aed3` |
| experiments/results/tables_audit14/tab_critMSB_note_audit14.tex | `e4853481d5431451dccb35619d7be71865f964544f0aed5746731eb2cc7be693` |
| experiments/results/tables_audit14/crit_msb_mzt_audit14.csv | `75f18a32f49f5ad00fcad8732eff1e1529c583794da7e893eb71e73687205d9e` |

Nota del tabular: EE máximo de MSB-GLS 3.37e-04 (impreso como cota 0.00034) y de MZ_t-GLS 4.60e-03 (impreso 0.0046); N_cal = `5\times10^{5}`. Redondeo binario, con 4 decimales para MSB-GLS y 3 para MZ_t-GLS.

### B14.2 — Las cinco cifras sin fuente

Búsqueda literal con fronteras de dígito en 3018 archivos de texto del repositorio (.json, .csv, .md, .log, .tex, .txt, .py, .bib). Incluye `experiments/results/`, sus checkpoints y `paper/`, que es la fuente del v11. No se recalculó nada.

| Token | Archivos con aciertos | Aciertos | Checkpoints | Referencias de A13/A14 | Otros archivos |
|---|---|---|---|---|---|
| i_0.003 | 44 | 242 | 0 | 10 | 34 |
| ii_0.0301 | 17 | 44 | 0 | 8 | 9 |
| iii_6.9% | 9 | 24 | 0 | 4 | 5 |
| iii_0.6% | 11 | 31 | 0 | 5 | 6 |
| iv_0.333 | 16 | 51 | 0 | 7 | 9 |

Un token de pocos dígitos aparece en muchos contextos ajenos, así que el recuento no identifica la fuente. La fuente se identificó por contexto (qué magnitud, qué configuración) leyendo los archivos, y el script registra y comprueba cada una:

| Cifra | Estado | Archivo | Clave | Valor | Impresa | Redondea a la impresa | Script | Script en git | El script escribe el archivo | Commit del resultado |
|---|---|---|---|---|---|---|---|---|---|---|
| (i) media 0.003 del peso adaptativo bajo la nula | localizada | experiments/results/rhat_distribution_audit5.json | alpha1/H0_n200/r_hat/mean | 0.00270735 | 0.003 | sí | experiments/audit5_tarea5.py | NO (sin commitear) | sí | 88a2e65 |
| (i) media 0.003 del peso adaptativo bajo la nula | localizada | experiments/results/rhat_distribution_audit5.json | alpha1/H0_n500/r_hat/mean | 0.00257693 | 0.003 | sí | experiments/audit5_tarea5.py | NO (sin commitear) | sí | 88a2e65 |
| (i) media 0.003 del peso adaptativo bajo la nula | localizada | experiments/results/rhat_distribution_audit5.json | alpha1/H0_n1000/r_hat/mean | 0.0025237 | 0.003 | sí | experiments/audit5_tarea5.py | NO (sin commitear) | sí | 88a2e65 |
| (ii) FP media 0.0301 del estadistico registrado con N_cal = 5e4 | localizada | experiments/results/real_data_comparison_audit5b.json | summary/a1_50k/mean_fp/ours | 0.030096 | 0.0301 | sí | experiments/audit5b_tarea_r5.py | sí (60b7764) | sí | 60b7764 |
| (iii) 6.9 % y 0.6 % de desviacion relativa de la mediana de sigma2_HAC frente a la identidad de Bartlett, AR(0.5), n = 200 y 5000 | no aparece como cifra almacenada; si sus insumos observados | experiments/results/audit2_results_audit2.json | task3/rho=0.5/by_n/200/sigma_hac_median | 0.552264 | 0.552 | sí | experiments/audit2_presend_audit2.py | sí (f7a4d31) | sí | f7a4d31 |
| (iii) 6.9 % y 0.6 % de desviacion relativa de la mediana de sigma2_HAC frente a la identidad de Bartlett, AR(0.5), n = 200 y 5000 | no aparece como cifra almacenada; si sus insumos observados | experiments/results/audit2_results_audit2.json | task3/rho=0.5/by_n/5000/sigma_hac_median | 0.2437 | 0.244 | sí | experiments/audit2_presend_audit2.py | sí (f7a4d31) | sí | f7a4d31 |
| (iv) pendiente 0.333 del ancho de banda en log n | localizada | experiments/results/resultados_auditoria_4_E.md | tabla markdown, fila 'AR 0.5', columna 'slope_B_pre' | 0.3332 | 0.333 | sí | experiments/audit4_tarea_E.py | NO (sin commitear) | sí | 88a2e65 |

Detalle:

- **(i)** Las tres medias con el piloto α(1) redondean a 0.003. También las 12 concordantes: el piloto α(2) del mismo archivo y `experiments/results/rhat_distribution_audit5b.json` (script `experiments/audit5b_tarea_r4.py`, en git: sí). Todas redondean: sí. Rastro en el manuscrito: paper/sec2_statistic.tex (v11): 'mean $0.003$, $95$th percentile below $0.008$'; v14 sec5_montecarlo.tex §5.12 '(mean $0.003$)'.
- **(ii)** Configuración: a1_50k: piloto alpha(1), N_cal = 50 000 (docstring de audit5b_tarea_r5.py). Detecciones por configuración: repro 13, a1_10k 13, a1_50k 13. Hay una copia concordante en `experiments/results/size_robustness_dkw_audit6.json` (`pilot_deviations/real_data/alpha1_50k/mean_fp` = 0.030096). Rastro: paper/sec6_application.tex (v11): 'moves it to $0.0301$, with the same $13$ detections'; deviation_table_audit8.json rows[0].sources cita el mismo archivo (summary/{repro,a1_10k}).
- **(iii)** no aparece como cifra almacenada; si sus insumos observados. Insumos almacenados: medianas observadas de σ̂²_HAC (n = 200: 0.552264 → 0.552, n = 5000: 0.2437 → 0.244) y ancho de banda mediano (n = 200: 4, n = 5000: 10). medianas observadas de sigma2_HAC (500 replicas por n); los valores predichos por la identidad (0.517 y 0.242) y las desviaciones (6.9 % y 0.6 %) solo aparecen en texto de manuscrito. El archivo se generó el 2026-09-03T17:16:26.056994+00:00, antes del commit `f78bc3f` (2026-09-04T16:48:35-06:00) que corrigió el piloto de Andrews: sí. El propio script calcula el ancho de banda con el piloto alpha(2). Rastro: paper/sec5_montecarlo.tex (v11), nota de tab:rates: predichos 0.517 y 0.242, observados 0.552 y 0.244, 'a relative deviation falling from $6.9\%$ to $0.6\%$'; paper/CHANGELOG_v8.md: 'desviacion 6.9%->0.6%'.
- **(iv)** Fila AR 0.5 de la tabla: Process AR 0.5, alpha_teo 0.2844, slope_B_pre 0.3332, R2_B_pre 0.9999, slope_B_ceil 0.3120, R2_B_ceil 1.0000, slope_g1_std -0.8460, slope_g2_std -1.1711. Piloto del script: alpha(1). Agregación: media de B antes del techo sobre 500 replicas por n (np.mean); la nota de tab:rates del v11 dice 'medians'. Rastro: paper/sec5_montecarlo.tex (v11), tab:rates: 'B, unrounded +0.333, R^2 1.000' y nota 'slope ... is $0.333$ with $R^{2} = 0.9999$'; paper/CHANGELOG_v8.md: '+0.333, R2=0.9999'.

### B14.3 — Verificación del v15

**Q3 sobre las frases que cambiaron.** Registro, plantillas y convenciones de Q3 de B13.Q (`audit13_q_claims`). Cubre las 7 filas de la tabla «Cifras» y, por extensión declarada, las 3 frases de reemplazo de «Cifras retiradas». Texto: `paper_latex_v15.zip` (sha256 `1d52f85a9aeed19b08f5c9e4fc69ff34ce4f39cacfef703314dcc55d2786144b`); referencia v14 `3b21e2250002dee66780027d49ea3458d33f4ee481f042b4fe6a43a301d7a12b`.

| Frase | Fila del changelog | Archivo:línea | Impresa | Recalculada | Convención | Veredicto | Correcta |
|---|---|---|---|---|---|---|---|
| sec5_calib_out | Cifras: sec5 §5.2 | v15/sec5_montecarlo.tex:75 | 0.0544 | 0.05445 | binaria | reproduce | — |
| sec5_calib_out | Cifras: sec5 §5.2 | v15/sec5_montecarlo.tex:75 | 0.14 | 0.14 | binaria, mitad hacia arriba | reproduce | — |
| sec5_lp_se | Cifras: sec5, nota de tab:localpower | v15/sec5_montecarlo.tex:141 | 0.0036 | 0.00353551 | hacia arriba (cota) | reproduce como cota | — |
| sec5_dgp5b | Cifras: sec5 §5.11 | v15/sec5_montecarlo.tex:573 | 19 | 19.4 | binaria, mitad hacia arriba | reproduce | — |
| sec5_dgp5b | Cifras: sec5 §5.11 | v15/sec5_montecarlo.tex:573 | 29 | 28.55 | binaria, mitad hacia arriba | reproduce | — |
| sec5_dgp5b | Cifras: sec5 §5.11 | v15/sec5_montecarlo.tex:573 | 7.9 | 7.95 | hacia abajo (cota) | reproduce como cota | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 36 | 36 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.013 | 0.01335 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.098 | 0.09805 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.004 | 0.00415 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.570 | 0.56955 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.026 | 0.0257 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.032 | 0.032 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.6 | 0.575 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.142 | 0.14175 | binaria, mitad hacia arriba | reproduce | — |
| sec5_serial2 | Cifras: sec5 §5.6 | v15/sec5_montecarlo.tex:300 | 0.679 | 0.6786 | binaria, mitad hacia arriba | reproduce | — |
| sec3_within | Cifras: sec3, Observación del ancla | v15/sec3_theory.tex:70 | 5.3 | 5.31645 | binaria, mitad hacia arriba, cota superior incumplida | no reproduce | 5.4 |
| sec3_within | Cifras: sec3, Observación del ancla | v15/sec3_theory.tex:70 | 0.302 | 0.301667 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 12 | 12 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 23 | 23 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 0 | 0 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 0.99 | 0.99 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 2 | 2 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 0.4 | 0.4 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 5 | 5 | binaria, mitad hacia arriba | reproduce | — |
| sec4_mcnemar | Cifras: sec4 §4.2 | v15/sec4_implementation.tex:56 | 12 | 12 | binaria, mitad hacia arriba | reproduce | — |
| sec5_negative | Cifras retiradas: sec5 §5.12 | v15/sec5_montecarlo.tex:602 | 0.1 | 0.1 | binaria, mitad hacia arriba | reproduce | — |
| sec5_negative | Cifras retiradas: sec5 §5.12 | v15/sec5_montecarlo.tex:602 | 14 | 14.36 | binaria, mitad hacia arriba | reproduce | — |
| sec5_negative | Cifras retiradas: sec5 §5.12 | v15/sec5_montecarlo.tex:602 | 28 | 27.74 | binaria, mitad hacia arriba | reproduce | — |
| sec5_negative | Cifras retiradas: sec5 §5.12 | v15/sec5_montecarlo.tex:602 | 24.8 | 24.785 | binaria, mitad hacia arriba | reproduce | — |
| sec5_negative | Cifras retiradas: sec5 §5.12 | v15/sec5_montecarlo.tex:602 | 33.4 | 33.355 | binaria, mitad hacia arriba | reproduce | — |
| dev_ncal | Cifras retiradas: sec6, nota de tab:deviations | v15/sec6_application.tex:146 | 13 | 13 | binaria, mitad hacia arriba | reproduce | — |
| appA_hacrate | Cifras retiradas: appA, rem:hacrate | v15/appA_proofs.tex:148 | (sin cifra) | — | — | frase localizada | — |

| Frase | Comprobación | Se cumple |
|---|---|---|
| sec5_calib_out | unica celda calibrada fuera | sí |
| sec5_dgp5b | supera al bootstrap para r >= 1.5 | sí |
| sec5_dgp5b | supera a la union para r <= 1.25 | sí |
| sec5_dgp5b | la union domina en el interior | sí |
| sec5_serial2 | PP rechaza casi siempre a psi = -0.8 (min 0.985) | sí |
| sec4_mcnemar | ninguna celda de DGP 3 mas distorsionada | sí |
| sec4_mcnemar | mismo conjunto de celdas que la definicion de B13.Q | sí |
| dev_ncal | detecciones sin cambio de N_cal 1e4 a 5e4 | sí |

**Definición de sec4 §4.2.** Literal del v15: al menos uno de theta 0 y theta 0.02 rechaza con probabilidad estrictamente entre 0 y 0.99. Da 23 celdas; el conjunto es el mismo que con la definición de B13.Q: sí (sólo v15: ninguna; sólo B13.Q: ninguna). Con ella: más potencia en 12, menos en 2 (máx. 0.40 pp).

**tab:attrib.** El v15 hace `\input` del tabular (línea 268) y de la nota (línea 270); los dos son idénticos a la exportación de B13.Q: sí. Queda algún bloque TRANSCRIBED: no. Pasa: **sí**.

**Completitud del changelog.** Filas de «Cifras» y «Cifras retiradas» sin frase verificada: 0. Bloques del diff v14 → v15 en los archivos de texto: 16; sin asignar a una fila o a una figura: 0.

| Archivo | Líneas v14 | Líneas v15 | Asignado a |
|---|---|---|---|
| sec3_theory.tex | 70–70 | 70–70 | sec3_within |
| sec4_implementation.tex | 57–57 | 57–58 | sec4_mcnemar |
| sec5_montecarlo.tex | 75–75 | 75–75 | sec5_calib_out |
| sec5_montecarlo.tex | 98–98 | 98–98 | Figuras |
| sec5_montecarlo.tex | 142–142 | 142–142 | sec5_lp_se |
| sec5_montecarlo.tex | 149–149 | 149–149 | Figuras |
| sec5_montecarlo.tex | 158–158 | 158–158 | Figuras |
| sec5_montecarlo.tex | 224–224 | 224–224 | Figuras |
| sec5_montecarlo.tex | 268–299 | 268–270 | tab:attrib |
| sec5_montecarlo.tex | 332–333 | 303–304 | sec5_serial2 |
| sec5_montecarlo.tex | 513–513 | 484–484 | Figuras |
| sec5_montecarlo.tex | 564–564 | 535–535 | Figuras |
| sec5_montecarlo.tex | 603–603 | 574–574 | sec5_dgp5b |
| sec5_montecarlo.tex | 634–634 | 605–605 | sec5_negative |
| sec6_application.tex | 146–147 | 146–147 | dev_ncal |
| appA_proofs.tex | 148–151 | 148–150 | appA_hacrate |

**Cobertura de las líneas cambiadas.** Números con decimales: 8 cubiertos por una frase verificada, 0 de diseño, 0 sin verificar.

**Cifras retiradas.** Ninguna aparece en el texto del v15: **sí**.

| Búsqueda | Apariciones | Dónde |
|---|---|---|
| mean $0.003$ | 0 | — |
| 0.003 | 0 | — |
| 0.0301 | 0 | — |
| 6.9 | 0 | — |
| 0.6 % | 0 | — |
| 0.333 | 0 | — |
| 0.6 (cualquier contexto) | 1 | v15/sec5_montecarlo.tex:303 «t$-GLS with their own simulated critical values are within $0.6$ points of it; DF-GLS over-rejects mode» |

La única aparición del token 0.6 es la cota nueva «within 0.6 points» de sec5 §5.6, no el 0.6 % retirado.

**Q4 con la regla corregida.** Estos patrones siguen con las zonas de B13.Q: «collapses faster», «does not collapse as fast», «no cost in size», «no effect on size», «RM-GLS» y «theta = 0.02». Las apariciones de «rolling means» y «two-channel» se clasifican por la frase que las contiene (D = diseno original o estadistico registrado; G = prueba general en theta; N = resultados negativos; M = afirma algo sobre MSB-B). Registro: 21 entradas; sin usar: 0.

| Patrón | Prohibida | Permitida | Excluida | Informar (M) | Sin clasificar | Ambigua |
|---|---|---|---|---|---|---|
| collapses faster | 0 | 0 | 0 | 0 | 0 | 0 |
| does not collapse as fast | 0 | 0 | 0 | 0 | 0 | 0 |
| no cost in size | 0 | 0 | 0 | 0 | 0 | 0 |
| no effect on size | 0 | 0 | 0 | 0 | 0 | 0 |
| RM-GLS | 0 | 0 | 0 | 0 | 0 | 0 |
| rolling means | 0 | 7 | 0 | 0 | 0 | 0 |
| theta = 0.02 | 0 | 9 | 1 | 0 | 0 | 0 |
| two-channel | 0 | 13 | 0 | 1 | 0 | 0 |

A informar (afirman algo sobre MSB-B): 1.

| Archivo | Línea | Patrón | Estado | Justificación | Contexto |
|---|---|---|---|---|---|
| v15/sec5_montecarlo.tex | 573 | two-channel | informar | sujeto 'It' = 'The one-channel \RMGLS{}' de la frase anterior: afirma la ventaja de potencia de MSB-B sobre el estadistico de dos canales (dentro de §5.11) | «one-channel \RMGLS{} changes the magnitudes but not the verdict. It exceeds the two-channel statistic by $19$ to $29$ points in the rows of \cref{tab:dgp5} and by at least» |

Clasificación completa:

| Archivo | Línea | Patrón | Clase | Justificación |
|---|---|---|---|---|
| v15/main.tex | 103 | two-channel | N | resumen: la extension de dos canales se reporta como resultado negativo |
| v15/sec1_introduction.tex | 38 | rolling means | D | sujeto 'An earlier design' |
| v15/sec1_introduction.tex | 41 | rolling means | D | misma frase: el diseno anterior anclaba en la media |
| v15/sec1_introduction.tex | 43 | two-channel | N | experimento registrado con resultado falsador |
| v15/sec2_statistic.tex | 37 | rolling means | G | definicion de la familia S_theta, theta in [0, 1/2] (eq:rollmean, eq:stat) |
| v15/sec3_theory.tex | 130 | rolling means | G | argumento de consistencia del numerador de eq:stat (theta general) |
| v15/sec3_theory.tex | 132 | rolling means | G | misma frase del argumento general |
| v15/sec5_montecarlo.tex | 607 | rolling means | N | tercer resultado negativo de §5.12 |
| v15/sec5_montecarlo.tex | 542 | two-channel | N | titulo de §5.11 (resultado negativo registrado) |
| v15/sec5_montecarlo.tex | 544 | two-channel | D | sujeto 'The statistic was originally' |
| v15/sec5_montecarlo.tex | 556 | two-channel | N | prediccion registrada que fallo |
| v15/sec5_montecarlo.tex | 562 | two-channel | N | potencia del estadistico de dos canales |
| v15/sec5_montecarlo.tex | 573 | two-channel | M | sujeto 'It' = 'The one-channel \RMGLS{}' de la frase anterior: afirma la ventaja de potencia de MSB-B sobre el estadistico de dos canales (dentro de §5.11) |
| v15/sec5_montecarlo.tex | 588 | two-channel | D | nota de tab:dgp5: define la columna del diseno original |
| v15/sec6_application.tex | 34 | two-channel | D | estadistico registrado |
| v15/sec6_application.tex | 66 | two-channel | D | sujeto: el estadistico registrado; la comparacion con MSB-B es implicita |
| v15/sec6_application.tex | 93 | two-channel | D | nota de tab:fp: estadistico registrado |
| v15/sec6_application.tex | 119 | two-channel | D | tab:deviations, columna 'Registered' |
| v15/appA_proofs.tex | 11 | rolling means | G | prueba de prop:invariance para eq:stat (theta general) |
| v15/highlights.tex | 7 | two-channel | N | resaltado: resultados negativos |
| v15/cover_letter.md | 15 | two-channel | N | carta: ambas extensiones se reportan como resultados negativos |

## 2. Compuertas

**Paso 0.** Regla del encargo: |Δ| = 0 en las columnas que el bloque usa; en el resto de columnas comunes, ≤ 1e-12 con declaración.

| Bloque | Criterio | Resultado | Veredicto |
|---|---|---|---|
| B14.0 | tabulares y figuras del v15 = exportados por A13 y B13.Q (byte a byte) | 23 archivos | pasa |
| B14.1 (columnas usadas) | q_0.05 de c\|msb, c\|mzt, ct\|msb, ct\|mzt = b101 sim_thresholds y bA_ma iid_quantiles | 24 comparaciones; máx. \|Δ\| = 0.00e+00 | pasa |
| B14.1 (resto de columnas comunes) | q_0.05 de dfgls, adf, pp y cuantiles RM de bA_ma, ≤ 1e-12 | 54 comparaciones; máx. \|Δ\| = 0.00e+00; distintos de 0: 0 | pasa |
| B14.1 (cobertura) | los 16 valores al 5 % que ya existían quedan cubiertos por el Paso 0 | sí | pasa |
| B14.3 tab:attrib | tabular y nota del v15 = exportación de B13.Q | sí | pasa |

Entradas guardadas sin columna común en las muestras de A10 (no entran en el Paso 0): ct|dfgls_pq, ct|glsbp_t0, ct|msb_pq, ct|mzt_pq, c|dfgls_pq, c|glsbp_t0, c|msb_pq, c|mzt_pq.

## 3. Procedencia

| Archivo | sha256 | Script | Commit | Código commiteado |
|---|---|---|---|---|
| experiments/results/b0_inventory_audit14.json | `91c5e2d29841bb4c72eebdd331d15c6b9de009491490c7fb431dd02ae34499d6` | experiments/audit14_b0_inventory.py | c32f7ad | sí |
| experiments/results/b1_critical_audit14.json | `f51af944c07fcc830672b7ea72f27d1cdb2153c4155ecc8d5d000dee89b26913` | experiments/audit14_b1_critical.py | c32f7ad | sí |
| experiments/results/b2_sources_audit14.json | `e1a3079e0bfc1b275669eaeffcb261365c82a1c806f71e4d60dea47f60c3051d` | experiments/audit14_b2_sources.py | c32f7ad | sí |
| experiments/results/b3_verify_audit14.json | `6ec418b35ca637ec9d5689ca32b78c4ea904b27ab8cd80fd4b8e536b27b088e9` | experiments/audit14_b3_verify.py | c32f7ad | sí |
| experiments/results/tables_audit14.json | `cfe68a2cae3f259215b0da9bc21848711e97793445ad81d85d548e1fecc67c92` | experiments/audit14_tables.py | c32f7ad | sí |
| experiments/results/tables_audit14/crit_msb_mzt_audit14.csv | `75f18a32f49f5ad00fcad8732eff1e1529c583794da7e893eb71e73687205d9e` | experiments/audit14_tables.py | c32f7ad | sí |
| experiments/results/tables_audit14/tab_critMSB_audit14.tex | `152b4ec3ad2b01ae67020547dd2f2a471f3a626439330103af0f8802dc22aed3` | experiments/audit14_tables.py | c32f7ad | sí |
| experiments/results/tables_audit14/tab_critMSB_note_audit14.tex | `e4853481d5431451dccb35619d7be71865f964544f0aed5746731eb2cc7be693` | experiments/audit14_tables.py | c32f7ad | sí |

Protocolo `experiments/protocol_audit14.md`: commit `b079b8d` (2026-09-24T13:45:26-06:00), sha256 en disco `f4f71b81ae245add1c0732a4eb744bd89cd95a0b0083eddf7c80be92366f212d`, commiteado `f4f71b81ae245add1c0732a4eb744bd89cd95a0b0083eddf7c80be92366f212d`.

Versiones: python 3.11.0, platform Windows-10-10.0.26200-SP0, numpy 2.2.4, scipy 1.15.2, numba 0.65.0, statsmodels 0.14.6, arch 8.0.0, pandas 2.2.3, joblib 1.4.2, matplotlib 3.10.1, pytest 9.0.3.

## 4. Desviaciones

| Desviación | Motivo | Cuándo | Efecto |
|---|---|---|---|
| B14.3: en las cotas inferiores («at least») se acepta también el redondeo hacia abajo, simétrico del «hacia arriba» de Q3 en las superiores | Q3 sólo tenía la convención de cota superior; sin la simétrica marcaba como incorrecta la cifra que su propia función `correct(…, "lower")` propone | Después de ver el resultado de sec5_dgp5b | sec5_dgp5b: 7.9 pasa de «no reproduce» a «reproduce como cota»; la desigualdad se comprueba igual |
| B14.2: los archivos de las propias auditorías A13/A14 que citan las cifras se separan como «referencias», no como fuentes | Citan el manuscrito, no lo producen | Al escribir la búsqueda | Sólo presentación del recuento |

Decisiones tomadas en el protocolo, antes de calcular (no son desviaciones): EE bootstrap exacto sin aleatoriedad (lectura 5); fragmento de nota del tabular (lectura 7); extensiones de B14.0 y B14.3 (lecturas 2 y 9); registro de clasificación de Q4 (lectura 10).

## 5. No ejecutado

- **B14.2 (iii)**: 6.9 % y 0.6 % no están almacenados como tales. No se calcularon a partir de los insumos almacenados (task3/rho=0.5/by_n/200/sigma_hac_median, task3/rho=0.5/by_n/5000/sigma_hac_median) porque el encargo dice «no recalcules». Tampoco se reprodujeron con el piloto α(1).
- **Familia 150**: reservada, sin uso; ningún bloque necesitó números aleatorios.
- **B12.D**: sigue cancelado.

## 6. Conclusiones

- B14.0: los 17 archivos de tablas y las 6 figuras del v15 son idénticos byte a byte a los exportados: sí.
- B14.1: 64 valores críticos, 48 nuevos, con EE bootstrap exacto; Paso 0 con máx. |Δ| = 0.00e+00 en 24 comparaciones de las columnas usadas y 0.00e+00 en 54 del resto. Salidas: CSV, tabular y nota en `tables_audit14/`.
- B14.2: localizadas con archivo, clave, valor y script: (i), (ii), (iv). (iii): no aparece como cifra almacenada; si sus insumos observados.
- B14.3: 9 frases verificadas; cifras que no se reproducen: 1 (v15/sec3_theory.tex:70 5.3 → 5.4). Frases de Q4 a informar: 1. Cifras retiradas ausentes: sí. Changelog completo: sí.

## 7. Anomalías y contradicciones con el manuscrito

### (a) Cifras del v15 que no se sostienen

- `v15/sec3_theory.tex:70` (sec3_within): impresa 5.3, valor 5.31645; binaria, mitad hacia arriba, cota superior incumplida. Cifra correcta: **5.4**; en B13.Q la cifra del v14 (5.4) tenía el veredicto «reproduce como cota».

### (b) Frases de Q4 que afirman algo sobre MSB-B

- `v15/sec5_montecarlo.tex:573` («two-channel»): sujeto 'It' = 'The one-channel \RMGLS{}' de la frase anterior: afirma la ventaja de potencia de MSB-B sobre el estadistico de dos canales (dentro de §5.11). Contexto: «one-channel \RMGLS{} changes the magnitudes but not the verdict. It exceeds the two-channel statistic by $19$ to $29$ points in the rows of \cref{tab:dgp5} and by at least».

### (c) Fuentes de B14.2: advertencias

- (i) El script productor `experiments/audit5_tarea5.py` no está en git (sha256 `ae6a64da025e28ae63e398b5fb19cf7414d988ec2e7c874c1836370fcc24075f`, modificado 2026-09-05T22:22:32.253841+00:00); el resultado sí (commit `88a2e65`).
- (iv) El script productor `experiments/audit4_tarea_E.py` no está en git (sha256 `ac119be7e82257784bb5c8bf77bcca827197c8de3895d9a3ba8cf475154fd23d`, modificado 2026-09-04T22:56:10.172586+00:00); el resultado sí (commit `88a2e65`).
- (iii) Los insumos de 6.9 % y 0.6 % se produjeron antes de la corrección del piloto (f78bc3f) y con el piloto alpha(2) en el propio script. Si el v16 reintroduce esas cifras, describen el estimador registrado, no el de la ecuación del artículo.
- (iv) media de B antes del techo sobre 500 replicas por n (np.mean); la nota de tab:rates del v11 dice 'medians'.

### (d) B13.Q: cifras que declaró sin JSON y sí tenían fuente

B13.Q listó sin JSON: v14/sec5_montecarlo.tex:631 0.003; v14/sec6_application.tex:146 0.0301; v14/appA_proofs.tex:148 6.9; v14/appA_proofs.tex:148 0.6; v14/appA_proofs.tex:148 0.333. B14.2 localiza (i), (ii), (iv) en archivos del repositorio. El v15 retiró esas cifras por ese motivo y podría reintroducirlas en el v16 con la fuente de la tabla de B14.2.

## Anexo: tabla maestra de los números nuevos

| Clave | Valor | IC/EE | N_sim | N_cal | Familia | JSON | Ruta |
|---|---|---|---|---|---|---|---|
| MSB-GLS c n=100 α=0.01 | 0.192702 | EE 2.78e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=100, alpha=0.01].critical_value |
| MSB-GLS c n=100 α=0.025 | 0.213716 | EE 2.49e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=100, alpha=0.025].critical_value |
| MSB-GLS c n=100 α=0.05 | 0.235577 | EE 2.26e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=100, alpha=0.05].critical_value |
| MSB-GLS c n=100 α=0.1 | 0.266037 | EE 2.32e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=100, alpha=0.1].critical_value |
| MZ_t-GLS c n=100 α=0.01 | -2.45111 | EE 3.64e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=100, alpha=0.01].critical_value |
| MZ_t-GLS c n=100 α=0.025 | -2.18102 | EE 2.73e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=100, alpha=0.025].critical_value |
| MZ_t-GLS c n=100 α=0.05 | -1.95277 | EE 2.24e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=100, alpha=0.05].critical_value |
| MZ_t-GLS c n=100 α=0.1 | -1.68934 | EE 1.88e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=100, alpha=0.1].critical_value |
| MSB-GLS ct n=100 α=0.01 | 0.157479 | EE 2.05e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=100, alpha=0.01].critical_value |
| MSB-GLS ct n=100 α=0.025 | 0.169702 | EE 1.31e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=100, alpha=0.025].critical_value |
| MSB-GLS ct n=100 α=0.05 | 0.181441 | EE 1.29e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=100, alpha=0.05].critical_value |
| MSB-GLS ct n=100 α=0.1 | 0.19715 | EE 1.17e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=100, alpha=0.1].critical_value |
| MZ_t-GLS ct n=100 α=0.01 | -3.09856 | EE 3.42e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=100, alpha=0.01].critical_value |
| MZ_t-GLS ct n=100 α=0.025 | -2.86586 | EE 2.48e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=100, alpha=0.025].critical_value |
| MZ_t-GLS ct n=100 α=0.05 | -2.66552 | EE 1.80e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=100, alpha=0.05].critical_value |
| MZ_t-GLS ct n=100 α=0.1 | -2.43643 | EE 1.52e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=100, alpha=0.1].critical_value |
| MSB-GLS c n=200 α=0.01 | 0.190504 | EE 2.64e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=200, alpha=0.01].critical_value |
| MSB-GLS c n=200 α=0.025 | 0.213073 | EE 2.58e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=200, alpha=0.025].critical_value |
| MSB-GLS c n=200 α=0.05 | 0.236918 | EE 2.26e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=200, alpha=0.05].critical_value |
| MSB-GLS c n=200 α=0.1 | 0.270337 | EE 2.41e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=200, alpha=0.1].critical_value |
| MZ_t-GLS c n=200 α=0.01 | -2.48907 | EE 3.88e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=200, alpha=0.01].critical_value |
| MZ_t-GLS c n=200 α=0.025 | -2.19711 | EE 3.03e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=200, alpha=0.025].critical_value |
| MZ_t-GLS c n=200 α=0.05 | -1.94606 | EE 2.47e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=200, alpha=0.05].critical_value |
| MZ_t-GLS c n=200 α=0.1 | -1.65953 | EE 1.82e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=200, alpha=0.1].critical_value |
| MSB-GLS ct n=200 α=0.01 | 0.153539 | EE 1.74e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=200, alpha=0.01].critical_value |
| MSB-GLS ct n=200 α=0.025 | 0.166045 | EE 1.27e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=200, alpha=0.025].critical_value |
| MSB-GLS ct n=200 α=0.05 | 0.178323 | EE 1.22e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=200, alpha=0.05].critical_value |
| MSB-GLS ct n=200 α=0.1 | 0.194715 | EE 1.16e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=200, alpha=0.1].critical_value |
| MZ_t-GLS ct n=200 α=0.01 | -3.18843 | EE 3.86e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=200, alpha=0.01].critical_value |
| MZ_t-GLS ct n=200 α=0.025 | -2.93491 | EE 2.64e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=200, alpha=0.025].critical_value |
| MZ_t-GLS ct n=200 α=0.05 | -2.7214 | EE 2.09e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=200, alpha=0.05].critical_value |
| MZ_t-GLS ct n=200 α=0.1 | -2.47601 | EE 1.62e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=200, alpha=0.1].critical_value |
| MSB-GLS c n=500 α=0.01 | 0.188828 | EE 3.15e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=500, alpha=0.01].critical_value |
| MSB-GLS c n=500 α=0.025 | 0.212555 | EE 2.82e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=500, alpha=0.025].critical_value |
| MSB-GLS c n=500 α=0.05 | 0.237642 | EE 2.68e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=500, alpha=0.05].critical_value |
| MSB-GLS c n=500 α=0.1 | 0.273924 | EE 2.81e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=500, alpha=0.1].critical_value |
| MZ_t-GLS c n=500 α=0.01 | -2.52178 | EE 4.40e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=500, alpha=0.01].critical_value |
| MZ_t-GLS c n=500 α=0.025 | -2.20836 | EE 3.03e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=500, alpha=0.025].critical_value |
| MZ_t-GLS c n=500 α=0.05 | -1.94187 | EE 2.42e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=500, alpha=0.05].critical_value |
| MZ_t-GLS c n=500 α=0.1 | -1.63748 | EE 2.14e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=500, alpha=0.1].critical_value |
| MSB-GLS ct n=500 α=0.01 | 0.149385 | EE 1.77e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=500, alpha=0.01].critical_value |
| MSB-GLS ct n=500 α=0.025 | 0.162368 | EE 1.50e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=500, alpha=0.025].critical_value |
| MSB-GLS ct n=500 α=0.05 | 0.175104 | EE 1.28e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=500, alpha=0.05].critical_value |
| MSB-GLS ct n=500 α=0.1 | 0.19214 | EE 1.17e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=500, alpha=0.1].critical_value |
| MZ_t-GLS ct n=500 α=0.01 | -3.28514 | EE 4.33e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=500, alpha=0.01].critical_value |
| MZ_t-GLS ct n=500 α=0.025 | -3.0091 | EE 2.42e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=500, alpha=0.025].critical_value |
| MZ_t-GLS ct n=500 α=0.05 | -2.77621 | EE 2.16e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=500, alpha=0.05].critical_value |
| MZ_t-GLS ct n=500 α=0.1 | -2.51319 | EE 1.68e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=500, alpha=0.1].critical_value |
| MSB-GLS c n=1000 α=0.01 | 0.186863 | EE 3.37e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=1000, alpha=0.01].critical_value |
| MSB-GLS c n=1000 α=0.025 | 0.211669 | EE 2.88e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=1000, alpha=0.025].critical_value |
| MSB-GLS c n=1000 α=0.05 | 0.237512 | EE 2.77e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=1000, alpha=0.05].critical_value |
| MSB-GLS c n=1000 α=0.1 | 0.274843 | EE 2.91e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=c, n=1000, alpha=0.1].critical_value |
| MZ_t-GLS c n=1000 α=0.01 | -2.54353 | EE 4.60e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=1000, alpha=0.01].critical_value |
| MZ_t-GLS c n=1000 α=0.025 | -2.2205 | EE 3.59e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=1000, alpha=0.025].critical_value |
| MZ_t-GLS c n=1000 α=0.05 | -1.94169 | EE 2.71e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=1000, alpha=0.05].critical_value |
| MZ_t-GLS c n=1000 α=0.1 | -1.62808 | EE 2.08e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=c, n=1000, alpha=0.1].critical_value |
| MSB-GLS ct n=1000 α=0.01 | 0.147214 | EE 1.88e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=1000, alpha=0.01].critical_value |
| MSB-GLS ct n=1000 α=0.025 | 0.160427 | EE 1.58e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=1000, alpha=0.025].critical_value |
| MSB-GLS ct n=1000 α=0.05 | 0.173389 | EE 1.35e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=1000, alpha=0.05].critical_value |
| MSB-GLS ct n=1000 α=0.1 | 0.190787 | EE 1.27e-04 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=msb, case=ct, n=1000, alpha=0.1].critical_value |
| MZ_t-GLS ct n=1000 α=0.01 | -3.33176 | EE 3.91e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=1000, alpha=0.01].critical_value |
| MZ_t-GLS ct n=1000 α=0.025 | -3.04719 | EE 2.89e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=1000, alpha=0.025].critical_value |
| MZ_t-GLS ct n=1000 α=0.05 | -2.80406 | EE 2.22e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=1000, alpha=0.05].critical_value |
| MZ_t-GLS ct n=1000 α=0.1 | -2.52993 | EE 1.79e-03 | — | 500000 | — (semilla de calibración 42) | b1_critical_audit14.json | values[stat=mzt, case=ct, n=1000, alpha=0.1].critical_value |
| B14.2 (i) alpha1/H0_n200/r_hat/mean | 0.00270735 | — | — | — | — | rhat_distribution_audit5.json | alpha1/H0_n200/r_hat/mean |
| B14.2 (i) alpha1/H0_n500/r_hat/mean | 0.00257693 | — | — | — | — | rhat_distribution_audit5.json | alpha1/H0_n500/r_hat/mean |
| B14.2 (i) alpha1/H0_n1000/r_hat/mean | 0.0025237 | — | — | — | — | rhat_distribution_audit5.json | alpha1/H0_n1000/r_hat/mean |
| B14.2 (ii) summary/a1_50k/mean_fp/ours | 0.030096 | — | — | — | — | real_data_comparison_audit5b.json | summary/a1_50k/mean_fp/ours |
| B14.2 (iii) task3/rho=0.5/by_n/200/sigma_hac_median | 0.552264 | — | — | — | — | audit2_results_audit2.json | task3/rho=0.5/by_n/200/sigma_hac_median |
| B14.2 (iii) task3/rho=0.5/by_n/5000/sigma_hac_median | 0.2437 | — | — | — | — | audit2_results_audit2.json | task3/rho=0.5/by_n/5000/sigma_hac_median |
| B14.2 (iv) tabla markdown, fila 'AR 0.5', columna 'slope_B_pre' | 0.3332 | — | — | — | — | resultados_auditoria_4_E.md | tabla markdown, fila 'AR 0.5', columna 'slope_B_pre' |
| B14.3 sec5_calib_out #0 (v15/sec5_montecarlo.tex:75) | 0.05445 | — | — | — | — | b3_verify_audit14.json | claims.sec5_calib_out.numbers[0].value |
| B14.3 sec5_calib_out #1 (v15/sec5_montecarlo.tex:75) | 0.14 | — | — | — | — | b3_verify_audit14.json | claims.sec5_calib_out.numbers[1].value |
| B14.3 sec5_lp_se #0 (v15/sec5_montecarlo.tex:141) | 0.00353551 | — | — | — | — | b3_verify_audit14.json | claims.sec5_lp_se.numbers[0].value |
| B14.3 sec5_dgp5b #0 (v15/sec5_montecarlo.tex:573) | 19.4 | — | — | — | — | b3_verify_audit14.json | claims.sec5_dgp5b.numbers[0].value |
| B14.3 sec5_dgp5b #1 (v15/sec5_montecarlo.tex:573) | 28.55 | — | — | — | — | b3_verify_audit14.json | claims.sec5_dgp5b.numbers[1].value |
| B14.3 sec5_dgp5b #2 (v15/sec5_montecarlo.tex:573) | 7.95 | — | — | — | — | b3_verify_audit14.json | claims.sec5_dgp5b.numbers[2].value |
| B14.3 sec5_serial2 #0 (v15/sec5_montecarlo.tex:300) | 36 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[0].value |
| B14.3 sec5_serial2 #1 (v15/sec5_montecarlo.tex:300) | 0.01335 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[1].value |
| B14.3 sec5_serial2 #2 (v15/sec5_montecarlo.tex:300) | 0.09805 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[2].value |
| B14.3 sec5_serial2 #3 (v15/sec5_montecarlo.tex:300) | 0.00415 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[3].value |
| B14.3 sec5_serial2 #4 (v15/sec5_montecarlo.tex:300) | 0.56955 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[4].value |
| B14.3 sec5_serial2 #5 (v15/sec5_montecarlo.tex:300) | 0.0257 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[5].value |
| B14.3 sec5_serial2 #6 (v15/sec5_montecarlo.tex:300) | 0.032 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[6].value |
| B14.3 sec5_serial2 #7 (v15/sec5_montecarlo.tex:300) | 0.575 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[7].value |
| B14.3 sec5_serial2 #8 (v15/sec5_montecarlo.tex:300) | 0.14175 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[8].value |
| B14.3 sec5_serial2 #9 (v15/sec5_montecarlo.tex:300) | 0.6786 | — | — | — | — | b3_verify_audit14.json | claims.sec5_serial2.numbers[9].value |
| B14.3 sec3_within #0 (v15/sec3_theory.tex:70) | 5.31645 | — | — | — | — | b3_verify_audit14.json | claims.sec3_within.numbers[0].value |
| B14.3 sec3_within #1 (v15/sec3_theory.tex:70) | 0.301667 | — | — | — | — | b3_verify_audit14.json | claims.sec3_within.numbers[1].value |
| B14.3 sec4_mcnemar #0 (v15/sec4_implementation.tex:56) | 12 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[0].value |
| B14.3 sec4_mcnemar #1 (v15/sec4_implementation.tex:56) | 23 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[1].value |
| B14.3 sec4_mcnemar #2 (v15/sec4_implementation.tex:56) | 0 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[2].value |
| B14.3 sec4_mcnemar #3 (v15/sec4_implementation.tex:56) | 0.99 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[3].value |
| B14.3 sec4_mcnemar #4 (v15/sec4_implementation.tex:56) | 2 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[4].value |
| B14.3 sec4_mcnemar #5 (v15/sec4_implementation.tex:56) | 0.4 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[5].value |
| B14.3 sec4_mcnemar #6 (v15/sec4_implementation.tex:56) | 5 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[6].value |
| B14.3 sec4_mcnemar #7 (v15/sec4_implementation.tex:56) | 12 | — | — | — | — | b3_verify_audit14.json | claims.sec4_mcnemar.numbers[7].value |
| B14.3 sec5_negative #0 (v15/sec5_montecarlo.tex:602) | 0.1 | — | — | — | — | b3_verify_audit14.json | claims.sec5_negative.numbers[0].value |
| B14.3 sec5_negative #1 (v15/sec5_montecarlo.tex:602) | 14.36 | — | — | — | — | b3_verify_audit14.json | claims.sec5_negative.numbers[1].value |
| B14.3 sec5_negative #2 (v15/sec5_montecarlo.tex:602) | 27.74 | — | — | — | — | b3_verify_audit14.json | claims.sec5_negative.numbers[2].value |
| B14.3 sec5_negative #3 (v15/sec5_montecarlo.tex:602) | 24.785 | — | — | — | — | b3_verify_audit14.json | claims.sec5_negative.numbers[3].value |
| B14.3 sec5_negative #4 (v15/sec5_montecarlo.tex:602) | 33.355 | — | — | — | — | b3_verify_audit14.json | claims.sec5_negative.numbers[4].value |
| B14.3 dev_ncal #0 (v15/sec6_application.tex:146) | 13 | — | — | — | — | b3_verify_audit14.json | claims.dev_ncal.numbers[0].value |

