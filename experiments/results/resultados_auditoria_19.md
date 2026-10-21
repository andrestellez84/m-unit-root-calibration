# Auditoría A19 — reporte (Figura 1, regla del AWB, forma del suplemento, literales del v25)

Protocolo `experiments/protocol_audit19.md` commiteado antes de cualquier edición o cálculo. Sin simulación nueva. No se editó ningún `.tex` del manuscrito ni `src/`. Entrada: `paper_latex_v25.zip`, sha256 `7e5273a76bc2fa163290fcb588d6354a3f2deed738cbbfdf4c98e10a6d913728`.

## 1. Resultados

### Punto 1 — Figura 1 en caminos comunes (L1)

`experiments/figures/fig_calibration_gain_audit19.pdf` se genera solo desde `experiments/results/e_calib_audit13.json` (`gls_t0`), con 48 puntos y una sola fuente: sí. Lo dibujado es exactamente lo registrado: sí. Fechas del PDF eliminadas: sí. sha256 `fdb34dd7dcb3287a63b7e1846594a6cd031d6a39b4931747d6d49d2a1e9c71f7`.

**P1.** Puntos que coinciden con la Tabla 1 al dígito impreso: 48 de 48 (pasa). Fuentes de la figura vieja: `experiments/results/b101_theta_audit10.json`, `experiments/results/b103_lown_audit10.json`, `experiments/results/b92_theta_audit9.json`, `experiments/results/e_calib_audit13.json`, `experiments/results/e_size_audit13.json`.

| Caso | Trazo | n | Viejo | N viejo | Fuente vieja | Nuevo | N nuevo | Δ (pp) | Tabla 1 | Coincide |
|---|---|---|---|---|---|---|---|---|---|---|
| c | cv_at_n | 60 | 0.0507 | 50000 | e_size_audit13.json | 0.0544 | 20000 | +0.38 | 0.0544 | sí |
| c | cv_at_n | 100 | 0.0501 | 50000 | e_size_audit13.json | 0.0516 | 20000 | +0.15 | 0.0516 | sí |
| c | cv_at_n | 150 | 0.0487 | 50000 | e_size_audit13.json | 0.0496 | 20000 | +0.09 | 0.0496 | sí |
| c | cv_at_n | 200 | 0.0502 | 100000 | b101_theta_audit10.json | 0.0514 | 20000 | +0.12 | 0.0514 | sí |
| c | cv_at_n | 500 | 0.0492 | 100000 | b101_theta_audit10.json | 0.0473 | 20000 | -0.19 | 0.0473 | sí |
| c | cv_at_n | 1000 | 0.0491 | 100000 | b101_theta_audit10.json | 0.0510 | 20000 | +0.18 | 0.0510 | sí |
| c | cv_at_n | 2000 | 0.0470 | 20000 | b92_theta_audit9.json | 0.0470 | 20000 | +0.00 | 0.0470 | sí |
| c | cv_at_n | 5000 | 0.0490 | 20000 | b92_theta_audit9.json | 0.0490 | 20000 | +0.00 | 0.0490 | sí |
| c | cv_big | 60 | 0.0577 | 50000 | e_size_audit13.json | 0.0607 | 20000 | +0.30 | 0.0607 | sí |
| c | cv_big | 100 | 0.0573 | 50000 | e_size_audit13.json | 0.0588 | 20000 | +0.16 | 0.0588 | sí |
| c | cv_big | 150 | 0.0553 | 50000 | e_size_audit13.json | 0.0563 | 20000 | +0.10 | 0.0563 | sí |
| c | cv_big | 200 | 0.0549 | 100000 | b101_theta_audit10.json | 0.0556 | 20000 | +0.07 | 0.0556 | sí |
| c | cv_big | 500 | 0.0506 | 100000 | b101_theta_audit10.json | 0.0484 | 20000 | -0.22 | 0.0484 | sí |
| c | cv_big | 1000 | 0.0500 | 100000 | b101_theta_audit10.json | 0.0518 | 20000 | +0.18 | 0.0518 | sí |
| c | cv_big | 2000 | 0.0478 | 20000 | e_calib_audit13.json | 0.0478 | 20000 | +0.00 | 0.0478 | sí |
| c | cv_big | 5000 | 0.0488 | 20000 | e_calib_audit13.json | 0.0488 | 20000 | +0.00 | 0.0488 | sí |
| c | msb_pub | 60 | 0.0484 | 50000 | b103_lown_audit10.json | 0.0502 | 20000 | +0.18 | 0.0502 | sí |
| c | msb_pub | 100 | 0.0469 | 50000 | b103_lown_audit10.json | 0.0496 | 20000 | +0.28 | 0.0496 | sí |
| c | msb_pub | 150 | 0.0438 | 50000 | b103_lown_audit10.json | 0.0442 | 20000 | +0.04 | 0.0442 | sí |
| c | msb_pub | 200 | 0.0453 | 100000 | b101_theta_audit10.json | 0.0460 | 20000 | +0.07 | 0.0460 | sí |
| c | msb_pub | 500 | 0.0432 | 100000 | b101_theta_audit10.json | 0.0417 | 20000 | -0.15 | 0.0417 | sí |
| c | msb_pub | 1000 | 0.0446 | 100000 | b101_theta_audit10.json | 0.0461 | 20000 | +0.15 | 0.0461 | sí |
| c | msb_pub | 2000 | 0.0430 | 20000 | e_calib_audit13.json | 0.0430 | 20000 | +0.00 | 0.0430 | sí |
| c | msb_pub | 5000 | 0.0449 | 20000 | e_calib_audit13.json | 0.0449 | 20000 | +0.00 | 0.0449 | sí |
| ct | cv_at_n | 60 | 0.0503 | 50000 | e_size_audit13.json | 0.0520 | 20000 | +0.17 | 0.0520 | sí |
| ct | cv_at_n | 100 | 0.0524 | 50000 | e_size_audit13.json | 0.0481 | 20000 | -0.43 | 0.0481 | sí |
| ct | cv_at_n | 150 | 0.0494 | 50000 | e_size_audit13.json | 0.0507 | 20000 | +0.13 | 0.0507 | sí |
| ct | cv_at_n | 200 | 0.0499 | 100000 | b101_theta_audit10.json | 0.0480 | 20000 | -0.19 | 0.0480 | sí |
| ct | cv_at_n | 500 | 0.0502 | 100000 | b101_theta_audit10.json | 0.0490 | 20000 | -0.13 | 0.0490 | sí |
| ct | cv_at_n | 1000 | 0.0505 | 100000 | b101_theta_audit10.json | 0.0512 | 20000 | +0.07 | 0.0512 | sí |
| ct | cv_at_n | 2000 | 0.0478 | 20000 | b92_theta_audit9.json | 0.0478 | 20000 | +0.00 | 0.0478 | sí |
| ct | cv_at_n | 5000 | 0.0517 | 20000 | b92_theta_audit9.json | 0.0517 | 20000 | +0.00 | 0.0517 | sí |
| ct | cv_big | 60 | 0.0191 | 50000 | e_size_audit13.json | 0.0199 | 20000 | +0.08 | 0.0199 | sí |
| ct | cv_big | 100 | 0.0356 | 50000 | e_size_audit13.json | 0.0323 | 20000 | -0.33 | 0.0323 | sí |
| ct | cv_big | 150 | 0.0396 | 50000 | e_size_audit13.json | 0.0412 | 20000 | +0.16 | 0.0412 | sí |
| ct | cv_big | 200 | 0.0432 | 100000 | b101_theta_audit10.json | 0.0413 | 20000 | -0.18 | 0.0413 | sí |
| ct | cv_big | 500 | 0.0485 | 100000 | b101_theta_audit10.json | 0.0472 | 20000 | -0.13 | 0.0472 | sí |
| ct | cv_big | 1000 | 0.0501 | 100000 | b101_theta_audit10.json | 0.0508 | 20000 | +0.07 | 0.0508 | sí |
| ct | cv_big | 2000 | 0.0486 | 20000 | e_calib_audit13.json | 0.0486 | 20000 | +0.00 | 0.0486 | sí |
| ct | cv_big | 5000 | 0.0510 | 20000 | e_calib_audit13.json | 0.0510 | 20000 | +0.00 | 0.0510 | sí |
| ct | msb_pub | 60 | 0.0157 | 50000 | b103_lown_audit10.json | 0.0169 | 20000 | +0.12 | 0.0169 | sí |
| ct | msb_pub | 100 | 0.0218 | 50000 | b103_lown_audit10.json | 0.0225 | 20000 | +0.06 | 0.0225 | sí |
| ct | msb_pub | 150 | 0.0254 | 50000 | b103_lown_audit10.json | 0.0261 | 20000 | +0.06 | 0.0261 | sí |
| ct | msb_pub | 200 | 0.0285 | 100000 | b101_theta_audit10.json | 0.0260 | 20000 | -0.25 | 0.0260 | sí |
| ct | msb_pub | 500 | 0.0349 | 100000 | b101_theta_audit10.json | 0.0336 | 20000 | -0.13 | 0.0336 | sí |
| ct | msb_pub | 1000 | 0.0388 | 100000 | b101_theta_audit10.json | 0.0394 | 20000 | +0.06 | 0.0394 | sí |
| ct | msb_pub | 2000 | 0.0398 | 20000 | e_calib_audit13.json | 0.0398 | 20000 | +0.00 | 0.0398 | sí |
| ct | msb_pub | 5000 | 0.0428 | 20000 | e_calib_audit13.json | 0.0428 | 20000 | +0.00 | 0.0428 | sí |

### Punto 2 — Regla de rechazo del AWB (L2)

| Implementación | Cifras del v25 | R | p-valor | Operador | Código | Las tres reglas coinciden | Rechaza si # ≤ |
|---|---|---|---|---|---|---|---|
| a15_mzt_gls | §4.8 del v25 (AWB, brazo iv); tab:boot del suplemento | 399 | (1+#)/(R+1) | <= | experiments/audit15_boot_engine.py:338 | sí | 19 |
| a13_msb_b | tab:awb (S4.3) del suplemento; §4.9 del v25 | 399 | #/R | < | experiments/audit13_e_awb.py:121 | sí | 19 |

La línea citada en el encargo (`experiments/audit10_b103_awb.py:124`, `r_awb = p < C.ALPHA`) es la versión de A10: version de A10; mismo operador; no produce cifras del v25.

**P2.** Reglas comparadas: #/R < alpha, #/R <= alpha, (1+#)/(R+1) <= alpha, para # = 0…R, en aritmética exacta y en coma flotante: pasa.

Oración añadida a la nota de S4.3: «With $R = 399$, rejecting when $\#/R < 0.05$ gives the same decision as $(1 + \#)/(R + 1) \leq 0.05$: both reject exactly when $\# \leq 19$.»

### Punto 3 — Suplemento (L3)

**Remisiones al cuerpo (L3.g).** Compilación del v25: 19 páginas, 0 errores. Etiquetas del cuerpo con número distinto entre v18b y v25: 3; de ellas, con remisión desde el suplemento: 0. Las 21 remisiones se escriben igual con el v25: sí. La subsección A.5 del apéndice es la prueba de thm:consistency: sí; sec:bootdef = subsection 3.5.

| Etiqueta | v18b | v25 |
|---|---|---|
| app:critical | appendix B | — |
| eq:bartlettidentity | equation A1 | — |
| tab:critMSB | table B1 | — |

**L3.a. Negritas.** Detector validado en las tablas que sí tienen negritas: sí. Leyendas editadas: tab:size02, tab:localpower02, tab:dgp102, tab:ctpower02, tab:dgp202, tab:dgp502, tab:fp02; conservadas por tener negritas: ninguna.

| Tabla | Número | Página | \textbf en la fuente | Spans numéricos en negrita (PDF, antes) | Frase en la leyenda (después) |
|---|---|---|---|---|---|
| tab:size02 | S5.1 | 22 | 0 | 0 | no |
| tab:localpower02 | S5.3 | 22 | 0 | 0 | no |
| tab:dgp102 | S5.4 | 23 | 0 | 0 | no |
| tab:ctpower02 | S5.5 | 23 | 0 | 0 | no |
| tab:dgp202 | S5.6 | 23 | 0 | 0 | no |
| tab:dgp502 | S5.10 | 25 | 0 | 0 | no |
| tab:fp02 | S5.11 | 25 | 0 | 0 | no |
| tab:calib02 | S5.2 | 22 | 36 | 36 | sí |
| tab:dgp302 | S5.7 | 24 | 50 | 50 | sí |
| tab:misspec02 | S5.8 | 24 | 72 | 72 | sí |
| tab:awb02 | S5.9 | 25 | 6 | 6 | sí |

**L3.b. RM.** Definición quitada de S1 y S5 y añadida a la nota de 8 tablas (el encargo enumera 6):

| Tabla | Número | Tabla incluida | Nota | En la lista del encargo |
|---|---|---|---|---|
| tab:dgp1 | S1.2 | s1_tab_dgp1_full | tablenotes | sí |
| tab:ctpower | S1.3 | s1_tab_ctpower_full | tablenotes | sí |
| tab:dgp2 | S4.1 | tab_dgp2_audit13 | minipage | no |
| tab:dgp3 | S4.2 | tab_dgp3_audit13 | tablenotes | no |
| tab:dgp102 | S5.4 | s5_tab_dgp1_theta0p02 | nota nueva | sí |
| tab:ctpower02 | S5.5 | s5_tab_ctpower_theta0p02 | nota nueva | sí |
| tab:dgp202 | S5.6 | s5_tab_dgp2_theta0p02 | nota nueva | sí |
| tab:dgp302 | S5.7 | s5_tab_dgp3_theta0p02 | nota nueva | sí |

Definiciones de RM que quedan fuera de una nota: 0.

**L3.c–L3.e y L2.2.** Ediciones aplicadas (cada ancla, exactamente una vez):

| Edición | Veces |
|---|---|
| L3.a tab:size02 | 1 |
| L3.a tab:localpower02 | 1 |
| L3.a tab:dgp102 | 1 |
| L3.a tab:ctpower02 | 1 |
| L3.a tab:dgp202 | 1 |
| L3.a tab:dgp502 | 1 |
| L3.a tab:fp02 | 1 |
| L3.b quitar (S1) | 1 |
| L3.b quitar (S5) | 1 |
| L3.b nota tab:dgp1 | 1 |
| L3.b nota tab:ctpower | 1 |
| L3.b nota tab:dgp2 | 1 |
| L3.b nota tab:dgp3 | 1 |
| L3.b nota tab:dgp102 | 1 |
| L3.b nota tab:ctpower02 | 1 |
| L3.b nota tab:dgp202 | 1 |
| L3.b nota tab:dgp302 | 1 |
| L3.c quitar | 1 |
| L3.c subseccion | 1 |
| L3.d quitar | 1 |
| L3.d insertar | 1 |
| L3.e | 1 |
| L2.2 tab:awb | 1 |

S7: «The slope of 1/3 follows from the Andrews rule once $\hat a$ settles; it says nothing about the stochastic part.» → «Appendix A.5 of the main text proves $(B+1)\hat\sigma^2 \to_p 2\gamma(0)$; the slope of 1/3 is that of the Andrews bandwidth.». Patrones de la nota sobre Θ_p que quedan: \\Theta_p: 0, Theta_p: 0, n\^\{-1/3\}: 0, stochastic part: 0.

Números decimales del suplemento antes y después: 300 y 308; añadidos: ninguno; quitados: ninguno.

**L3.f.** Páginas antes y después: 36 y 36. Después: 0 errores, 0 referencias y 0 citas indefinidas, 0 avisos de «Rerun» (antes: 0 errores, 0 referencias indefinidas).

**L3.h.** `supplementary/MANIFEST.sha256`: 110 entradas, todas coinciden: sí. Búsqueda de identificadores: 0 aciertos fuera de hashes de commit.

### Punto 4 — Literales del v25 (L4)

κ(−7) = 119/3 = 39.6667 (texto: 39.7); λ(−7) = 1225 (texto: 1225).

| n | E[S²] exacto | 6 decimales | Texto | Expansión | \|expansión − exacto\| | ≤ cota | Primer orden | Texto |
|---|---|---|---|---|---|---|---|---|
| 200 | 0.360458635 | 0.360459 | 0.360 | 0.360453864 | 4.77e-06 | sí | 0.302 | 0.302 |
| 500 | 0.431812157 | 0.431812 | 0.432 | 0.431811772 | 3.85e-07 | sí | 0.421 | 0.421 |
| 1000 | 0.463299492 | 0.463299 | — | 0.463299440 | 5.23e-08 | sí | 0.460 | — |
| 2000 | 0.480932748 | 0.480933 | 0.481 | 0.480932741 | 6.83e-09 | sí | 0.480 | 0.480 |

Identidad de A.5 frente a `hac_newey_west` (n = 200, B ∈ {0, 3, 7, 20, 199}, ruido i.i.d., AR(0.5) y MA(−0.8)): máxima diferencia absoluta 2.2e-14 (tolerancia 1e-12).

Pruebas nuevas: `tests/test_figure1_audit19.py`, `tests/test_awb_rule_audit19.py`, `tests/test_literals_v25_audit19.py` y `tests/test_no_literals_audit19.py`. El recuento de la batería completa desde la copia limpia del paquete queda en `package_v101_audit19.json`.

### Punto 5 — Paquete v1.0.1 (L5)

El zip v1.0.0 no contiene el manuscrito; no se agrega. El sha256 del zip v1.0.1, el número de archivos, las pruebas desde la copia limpia y el release se registran en `package_v101_audit19.json`, que no puede ir dentro del zip que describe.

## 2. Compuertas

| Bloque | Criterio | Resultado | Veredicto |
|---|---|---|---|
| L1 / P1 | cada punto = celda de la Tabla 1 al dígito impreso | 48/48 | pasa |
| L1 | una sola fuente; dibujado = JSON; PDF sin fechas | sí / sí / sí | pasa |
| L2 / P2 | tres reglas iguales con R = 399; # ≤ 19 | sí | pasa |
| L3.g | ninguna remisión al cuerpo cambia | 0 cambiadas | pasa |
| L3 | 0 errores, 0 referencias indefinidas; anclas únicas; ningún número cambia | sí | pasa |
| L4 | todas las cifras del v25 se reproducen | sí | pasa |

## 3. Procedencia

| Archivo | sha256 (16) | Script | Commit | Código commiteado | Asistente |
|---|---|---|---|---|---|
| experiments/figures/fig_calibration_gain_audit19.pdf | `fdb34dd7dcb3287a` | experiments/make_figures_audit19.py | a4469fd | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/awb_rule_audit19.json | `6f3b7c2db0d98420` | experiments/audit19_awb_rule.py | 3158522 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/figures_audit19.json | `86c78747309dc5c1` | experiments/make_figures_audit19.py | a4469fd | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/literals_v25_audit19.json | `58aefda08e14f4c4` | experiments/audit19_literals.py | fcb8ad7 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v25_audit19.json | `eeabf879f3f31fa9` | experiments/audit19_supplement.py | 1af9b17 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| supplementary/MANIFEST.sha256 | `c9f18b7a19bac081` | experiments/audit19_supplement.py | 1af9b17 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| supplementary/supplement.tex | `9e6eb7bcf27c8746` | experiments/audit19_supplement.py | 1af9b17 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |

## 4. Desviaciones

| Desviación | Motivo | Cuándo | Efecto |
|---|---|---|---|
| El protocolo está en `experiments/protocol_audit19.md`, no en `protocols/A19.md` | Ahí están todos los protocolos (A8–A18) y los buscan PROTOCOLS.md, S10 y los manifiestos | Paso 0 | Ninguno |
| La definición de RM va a la nota de 8 tablas, no de 6 | El encargo pide «cada tabla que tiene columna RM»; la lista omite tab:dgp2 y tab:dgp3 (S4), que la tienen y quedarían sin definición | L3.b | Dos notas más |
| Las cifras del AWB de S4.3 y §4.9 son de A13, no de A15 | El encargo atribuye a A15 las de §4.8 y S4; se reportan las dos implementaciones | L2.1 | La oración de S4.3 se refiere a la regla de A13 |
| El suplemento se edita sobre la salida de A18, sin repetir la cadena A16–A18 | Anclas únicas registradas; Paso 0 por sha256 | L3.0 | Volver a correr audit18_supplement.py desharía estas ediciones |

## 5. No ejecutado

- No se edita el manuscrito: el autor debe cambiar `\includegraphics{fig_calibration_gain_audit13q}` por `fig_calibration_gain_audit19` en §4.2 del v25.
- No se encontró, aparte de la frase de S7, ninguna nota del suplemento que diga que el teorema supone σ̂² = Θ_p(n^{-1/3}); no hubo nada más que editar.

## 6. Conclusiones

- La Figura 1 sale ahora de los mismos caminos que la Tabla 1, y sus 48 puntos coinciden con ella; «on common paths» es cierto para las dos.
- Las dos implementaciones del AWB usan R = 399; con ese R las tres reglas dan la misma decisión.
- El suplemento cambia solo de forma: 23 ediciones, ningún número, 36 → 36 páginas.
- Las cifras nuevas del v25 (Remark 1, A.4 y A.5) se reproducen en aritmética exacta.

## 7. Anomalías y observaciones

- La cota «within 4.8×10⁻⁶ for n ≥ 200» se cumple con poco margen: la diferencia en n = 200 es 4.77e-06.
- En la figura nueva, el trazo de MSB-B con el valor crítico en n queda fuera de la región exacta para 2×10⁴ caminos en: c, n = 60 (la Tabla 1 lo marca en negrita). Es el mismo número que la Tabla 1; la figura vieja usaba otros caminos.
- El README del paquete v1.0.0 atribuía la Figura 1 a `e_calib_audit13.json`; no era exacto (mezclaba cuatro fuentes). Se corrige en el v1.0.1.

## Anexo: tabla maestra de los números nuevos

| Clave | Valor | IC/EE | N_sim | N_cal | Familia | JSON | Ruta |
|---|---|---|---|---|---|---|---|
| L1 puntos que coinciden con la Tabla 1 | 48 | — | 2×10⁴ por punto | — | — | figures_audit19.json | n_match_table1 |
| L2 R (A15, MZ_t-GLS) | 399 | — | — | — | — | awb_rule_audit19.json | implementations.a15_mzt_gls.R |
| L2 R (A13, MSB-B) | 399 | — | — | — | — | awb_rule_audit19.json | implementations.a13_msb_b.R |
| L2 umbral de # | 19 | — | — | — | — | awb_rule_audit19.json | checks.a13_msb_b.reject_iff_count_le |
| L3.f páginas antes | 36 | — | — | — | — | supplement_v25_audit19.json | pages.before |
| L3.f páginas después | 36 | — | — | — | — | supplement_v25_audit19.json | pages.after |
| L4 λ(−7) | 1225 | exacto | — | — | — | literals_v25_audit19.json | lambda |
| L4 E[S²] n = 200 | 0.360459 | exacto | — | — | — | literals_v25_audit19.json | by_n.200.exact |
| L4 \|expansión − exacto\| n = 200 | 4.77e-06 | exacto | — | — | — | literals_v25_audit19.json | by_n.200.abs_gap |
| L4 E[S²] n = 500 | 0.431812 | exacto | — | — | — | literals_v25_audit19.json | by_n.500.exact |
| L4 \|expansión − exacto\| n = 500 | 3.85e-07 | exacto | — | — | — | literals_v25_audit19.json | by_n.500.abs_gap |
| L4 E[S²] n = 1000 | 0.463299 | exacto | — | — | — | literals_v25_audit19.json | by_n.1000.exact |
| L4 \|expansión − exacto\| n = 1000 | 5.23e-08 | exacto | — | — | — | literals_v25_audit19.json | by_n.1000.abs_gap |
| L4 E[S²] n = 2000 | 0.480933 | exacto | — | — | — | literals_v25_audit19.json | by_n.2000.exact |
| L4 \|expansión − exacto\| n = 2000 | 6.83e-09 | exacto | — | — | — | literals_v25_audit19.json | by_n.2000.abs_gap |
| L4 identidad, máx. \|Δ\| | 2.2e-14 | — | — | — | — | literals_v25_audit19.json | identity.max_abs_gap |

