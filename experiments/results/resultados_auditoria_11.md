# Auditoría A11 — cierre para el manuscrito v12

Generado por `experiments/audit11_generate_report.py` el 2026-09-21 18:26 UTC desde los JSON de `experiments/results`. Commit de HEAD: `5b93502`. Protocolo: `experiments/protocol_audit11.md`.

Reglas de A10 con sufijo `_audit11` y familias 120–129. No se edita ningún `.tex`: el fragmento de T2 se escribe en `experiments/results/` y las citas son al manuscrito v12 del zip.

## 1. Resultados

### T0 — Protocolo y semillas

- Protocolo `experiments/protocol_audit11.md`: sha256 en disco `30606dd224a998a6290cb60fe3d3c1e341c0c7d5963f97fded6a5b823f50e175`, commiteado `30606dd224a998a6290cb60fe3d3c1e341c0c7d5963f97fded6a5b823f50e175` (iguales), introducido en `b193027`.
- Manuscrito de referencia `paper_latex_v12.zip` (fuera del repositorio, solo lectura): sha256 `236cbb6580dd85fbd16de6b63a7a8d6788fc74569c3df2fd04116f57123887c3`, 141491 bytes. Los 11 `.tex` de `paper/` (v11) no se tocan; su sha256 queda en `t0_protocol_audit11.json`.
- Equivalencia `SeedSequence(familia).spawn` ↔ `spawn_key = (celda, i)`: 50 streams comprobados, 0 discrepancias.
- Colisiones: 260002 streams nuevos (familia 123: 240000, familia 124: 20002) frente a 14830400 previos (2450600 semillas enteras y las familias 90, 91, 92, 93, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 110, 111, 112, 113, 114, 115): 0 colisiones con los previos, 0 dentro de A11 (palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8-A10)).
- Familias: T0 = 120, T1 = 121, T2 = 122, T3 = 123, T4 = 124, T5 = 125, AMEND1 = 126, AMEND2 = 127, AMEND3 = 128, AMEND4 = 129. Sin trayectorias: 120, 121, 122, 125.

### T1 — Figuras en inglés (mismos nombres de archivo)

Código de referencia: experiments/make_figures_audit10.py (corrida en carpeta temporal). Se interceptaron `Axes.plot`, `Axes.fill_between` y `Axes.axhline` en las dos corridas y se compararon los arrays float64 llamada a llamada (`np.array_equal`, sin tolerancia). θ graficado: 0.02. Datos idénticos en las seis figuras: **sí**.

**Tabla T1.1. sha256 antes y después, e igualdad de los datos graficados.**

| Archivo | sha256 A10 (`figures_audit10.json`) | sha256 nuevo | sha256 copia en `paper/figures` | Llamadas A10 / A11 | Valores A10 / A11 | Misma secuencia | Bit a bit | sha256 de los datos (16) |
|---|---|---|---|---|---|---|---|---|
| fig_local_power_audit10.pdf | `0f20a38f51063f6537623ef30fee11d81761a7b4ff9ee2cadca219ceea23bdb1` | `08a73351b893727f3debc8716286cceea1a58e72df973de28e4b04baae569809` | `08a73351b893727f3debc8716286cceea1a58e72df973de28e4b04baae569809` | 14 / 14 | 770 / 770 | sí | **sí** | `acb4f703180a81d2` |
| fig_theta_ladder_audit10.pdf | `6c3350c76b48b34b2a1870ae9c899068c64a64d61ad4c2cbd464639a7071554b` | `88d5d92abc9d4fc3dfea7aec7a5d8550cb5fce4d83964922d2b77d97721debcc` | `88d5d92abc9d4fc3dfea7aec7a5d8550cb5fce4d83964922d2b77d97721debcc` | 6 / 6 | 60 / 60 | sí | **sí** | `9ad255ec09d049ac` |
| fig_power_equalized_audit10.pdf | `37bea833a020f0ce54e750cfd19e5e28f8e9225592a381cf975044fe53aa076c` | `6741dec11c644b846255e265c2def35d40f56b33594416f4bcae379b4c6ef974` | `6741dec11c644b846255e265c2def35d40f56b33594416f4bcae379b4c6ef974` | 42 / 42 | 462 / 462 | sí | **sí** | `546fef0e16e339bf` |
| fig_size_shift_audit10.pdf | `ef725f2995e8e69235710ef818daa16c8ade1213ad47b61840f23c317196cb23` | `32152038aceeda699150737d019a2aaa1e70cffd5d62ccd29f5470366163aa0b` | `32152038aceeda699150737d019a2aaa1e70cffd5d62ccd29f5470366163aa0b` | 30 / 30 | 332 / 332 | sí | **sí** | `c281e776a675f131` |
| fig_dgp3_audit10.pdf | `ab00f247d9e4ea52229905f3b3b2fa71582fe498e43177e6ec87f3b8e26db51e` | `baa63ae0b1971c5638963199e9245c70de662a4acf55cc94fcdbe0ff12a75b08` | `baa63ae0b1971c5638963199e9245c70de662a4acf55cc94fcdbe0ff12a75b08` | 21 / 21 | 153 / 153 | sí | **sí** | `091842f4b550254c` |
| fig_calibration_gain_audit10.pdf | `abb5a978d74e02084dbd18cb011c980a88931dbef20f34dc4768923bbd4d8676` | `81d8bebb810b194931cc1a595fb772c98358381efdd2ad7c932b28837d8aba35` | `81d8bebb810b194931cc1a595fb772c98358381efdd2ad7c932b28837d8aba35` | 10 / 10 | 146 / 146 | sí | **sí** | `6d6231443218c944` |

*Fuente: `figures_audit11.json`. Las fuentes de datos son las de A10: `b92_theta_audit9.json`, `b103_equalized_audit10.json`, `b103_awb_audit10.json`, `b3_comparators_audit8.json`, `b5_power_audit8.json`, `b101_theta_audit10.json`, `b103_lown_audit10.json`, `b103_finite_audit10.json`.*

Cambios de texto (lectura operativa 4): paneles «Constant»/«Trend»; ejes y leyendas del encargo; «AWB DF-GLS (A8)» → «AWB DF-GLS» en `fig_size_shift`; MSB-GLS, DF-GLS y MZ_t-GLS conservan su nombre en `fig_local_power`; etiqueta 150 eliminada en `fig_calibration_gain` (la marca se conserva) y leyenda en dos columnas; en `fig_theta_ladder`, etiquetas con dos decimales y 0.00 alineada a la derecha de su marca (desviación en §4).

### T2 — DGP 2 con θ = 0.02 para el manuscrito

Fuente: `b103_equalized_audit10.json` (sha256 `052b49ba21718a17a581787afc026b5aa5b6c50d579821c50146434bc2e85a70`), celdas `dgp2_*`, `rates_sim`; RM = `rm_t0.1`; ZA en el propio JSON: sí → columna rates_sim.za (valor critico simulado; calibracion de A9, N_cal = 50 000). Trayectorias: B5 de A8 (familia 95): filas de audit9_b91 (DGP 1, DGP 2, tendencia) y audit9_b92 (DGP 3). Regla: RM-like: p = F_null(stat) < 0.05; resto: stat < cuantil 5% bajo la Ec. (3). N_sim = 5000; N_cal = 500000 (n ∈ {200, 500, 1000}; KPSS y ZA con 50 000 de A9).

**Tabla T2.1. Potencia bajo DGP 2 (AR(0.95) con quiebre de media δ), tasas con umbral simulado; McNemar exacto de RM-GLS frente a DF-GLS-sim.** Exportada como `experiments/results/tab_dgp2_audit11.md` y `experiments/results/tab_dgp2_audit11.tex` (solo el `tabular`).

| δ | n | RM-GLS (θ = 0.02) | RM | ADF-sim | PP-sim | DF-GLS-sim | MZ_t-GLS-sim | MSB-GLS-sim | ZA | McNemar p vs DF-GLS-sim |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 200 | 0.706 | 0.432 | 0.299 | 0.322 | 0.695 | 0.689 | 0.658 | 0.119 | 0.057 |
| 0 | 500 | 1.000 | 0.980 | 0.938 | 0.949 | 0.994 | 0.995 | 0.994 | 0.454 | 3.7e-09 |
| 0 | 1000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.970 | 1.000 |
| 0.5 | 200 | 0.635 | 0.396 | 0.269 | 0.290 | 0.620 | 0.613 | 0.594 | 0.119 | 0.017 |
| 0.5 | 500 | 1.000 | 0.959 | 0.903 | 0.914 | 0.983 | 0.983 | 0.987 | 0.456 | 4.4e-24 |
| 0.5 | 1000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.971 | 1.000 |
| 1 | 200 | 0.474 | 0.288 | 0.196 | 0.198 | 0.445 | 0.444 | 0.439 | 0.124 | 3.9e-06 |
| 1 | 500 | 0.990 | 0.865 | 0.784 | 0.766 | 0.931 | 0.935 | 0.941 | 0.439 | 1.6e-71 |
| 1 | 1000 | 1.000 | 1.000 | 0.995 | 1.000 | 0.997 | 0.997 | 0.998 | 0.966 | 3.1e-05 |
| 2 | 200 | 0.094 | 0.080 | 0.053 | 0.048 | 0.083 | 0.083 | 0.093 | 0.104 | 0.002 |
| 2 | 500 | 0.573 | 0.329 | 0.266 | 0.212 | 0.441 | 0.442 | 0.479 | 0.397 | 9.0e-78 |
| 2 | 1000 | 1.000 | 0.953 | 0.915 | 0.857 | 0.870 | 0.882 | 0.900 | 0.962 | 2.1e-196 |
| 3 | 200 | 0.004 | 0.006 | 0.004 | 0.003 | 0.001 | 0.001 | 0.005 | 0.088 | 0.017 |
| 3 | 500 | 0.024 | 0.018 | 0.015 | 0.008 | 0.017 | 0.017 | 0.023 | 0.378 | 7.7e-04 |
| 3 | 1000 | 0.637 | 0.279 | 0.328 | 0.127 | 0.376 | 0.378 | 0.456 | 0.954 | 1.9e-233 |
| 5 | 200 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.092 | 1.000 |
| 5 | 500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.497 | 1.000 |
| 5 | 1000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.986 | 1.000 |

ZA con p-valor asintótico en las mismas celdas (informativa, `rates_asy.za`): δ = 0, n = 200: 0.130; δ = 0, n = 500: 0.456; δ = 0, n = 1000: 0.970; δ = 0.5, n = 200: 0.133; δ = 0.5, n = 500: 0.458; δ = 0.5, n = 1000: 0.970; δ = 1, n = 200: 0.135; δ = 1, n = 500: 0.441; δ = 1, n = 1000: 0.966; δ = 2, n = 200: 0.114; δ = 2, n = 500: 0.399; δ = 2, n = 1000: 0.961; δ = 3, n = 200: 0.097; δ = 3, n = 500: 0.380; δ = 3, n = 1000: 0.954; δ = 5, n = 200: 0.099; δ = 5, n = 500: 0.498; δ = 5, n = 1000: 0.986.

**Tabla T2.2. Tamaño de ZA bajo paseo aleatorio y bajo paseo con quiebre de media Δμ = 1.**

| Proceso | n | ZA (A8) | Wilson 95% | En región exacta | N (A8) | ZA (A6) | IC (A6) | N (A6) |
|---|---|---|---|---|---|---|---|---|
| random_walk | 200 | 0.0542 | [0.0483, 0.0608] | sí | 5000 | 0.0548 | [0.0487, 0.0615] | 5000 |
| random_walk | 500 | 0.0472 | [0.0417, 0.0534] | sí | 5000 | 0.0520 | [0.0460, 0.0585] | 5000 |
| random_walk | 1000 | 0.0522 | [0.0464, 0.0587] | sí | 5000 | 0.0488 | [0.0430, 0.0551] | 5000 |
| random_walk_break_mu1 | 200 | 0.0558 | [0.0498, 0.0625] | sí | 5000 | 0.0558 | [0.0496, 0.0625] | 5000 |
| random_walk_break_mu1 | 500 | 0.0464 | [0.0409, 0.0526] | sí | 5000 | 0.0442 | [0.0387, 0.0503] | 5000 |
| random_walk_break_mu1 | 1000 | 0.0458 | [0.0403, 0.0520] | sí | 5000 | 0.0490 | [0.0432, 0.0554] | 5000 |

*Fuentes: `b5_power_audit8.json` (`za_size.za_<rw|rwbreak>_n<n>.rates.za`, p-valor asintótico de ZA, región exacta de N = 5000 [0.044, 0.0562]) y `dgp2_break_tests_audit6.json` (`size_control.<pure_rw|break_rw>.<n>`).*

### T3 — Sesgo del ancla (Observación del manuscrito)

Estadístico: `audit9_engine.rmgls(Y, n, theta, 1.0, 'c') ** 2`; σ² = 1 fijo; caso c, ancla gls, c̄ = -7, κ(c̄) = 2|c̄|(1/2 + |c̄|/3) = 39.666667 (literal del encargo: 39.67). Trayectorias: audit8_design.gauss_rw (Y_0 = 0), familia 123, celda t3_n<n>; N = 40000 por n; los tres θ sobre las mismas trayectorias. τ₁ por (n, θ): n = 200: θ = 0 → 0, θ = 0.02 → 4, θ = 0.1 → 20; n = 500: θ = 0 → 0, θ = 0.02 → 10, θ = 0.1 → 50; n = 1000: θ = 0 → 0, θ = 0.02 → 20, θ = 0.1 → 100; n = 2000: θ = 0 → 0, θ = 0.02 → 40, θ = 0.1 → 200; n = 5000: θ = 0 → 0, θ = 0.02 → 100, θ = 0.1 → 500; n = 20000: θ = 0 → 0, θ = 0.02 → 400, θ = 0.1 → 2000.

**Tabla T3.1. E[S_θ²] simulado (media ± EE) frente a (1−θ)/2 + θ/3 y a la aproximación de primer orden (1−θ)/2 + θ/3 − κ/n.**

| n | θ | Media | EE | (1−θ)/2 + θ/3 | … − κ/n | z frente a primer orden | z frente al límite |
|---|---|---|---|---|---|---|---|
| 200 | 0 | 0.36029 | 0.00192 | 0.50000 | 0.30167 | 30.55 | -72.81 |
| 200 | 0.02 | 0.35567 | 0.00191 | 0.49667 | 0.29833 | 29.96 | -73.68 |
| 200 | 0.1 | 0.33987 | 0.00189 | 0.48333 | 0.28500 | 28.99 | -75.80 |
| 500 | 0 | 0.43039 | 0.00241 | 0.50000 | 0.42067 | 4.04 | -28.90 |
| 500 | 0.02 | 0.42647 | 0.00241 | 0.49667 | 0.41733 | 3.80 | -29.17 |
| 500 | 0.1 | 0.41204 | 0.00240 | 0.48333 | 0.40400 | 3.35 | -29.74 |
| 1000 | 0 | 0.46318 | 0.00263 | 0.50000 | 0.46033 | 1.08 | -13.98 |
| 1000 | 0.02 | 0.45958 | 0.00263 | 0.49667 | 0.45700 | 0.98 | -14.09 |
| 1000 | 0.1 | 0.44586 | 0.00263 | 0.48333 | 0.44367 | 0.84 | -14.26 |
| 2000 | 0 | 0.48346 | 0.00275 | 0.50000 | 0.48017 | 1.19 | -6.01 |
| 2000 | 0.02 | 0.48000 | 0.00275 | 0.49667 | 0.47683 | 1.15 | -6.06 |
| 2000 | 0.1 | 0.46655 | 0.00275 | 0.48333 | 0.46350 | 1.11 | -6.11 |
| 5000 | 0 | 0.49365 | 0.00283 | 0.50000 | 0.49207 | 0.56 | -2.24 |
| 5000 | 0.02 | 0.49024 | 0.00283 | 0.49667 | 0.48873 | 0.53 | -2.27 |
| 5000 | 0.1 | 0.47671 | 0.00283 | 0.48333 | 0.47540 | 0.46 | -2.34 |
| 20000 | 0 | 0.49218 | 0.00281 | 0.50000 | 0.49802 | -2.08 | -2.79 |
| 20000 | 0.02 | 0.48880 | 0.00281 | 0.49667 | 0.49468 | -2.10 | -2.80 |
| 20000 | 0.1 | 0.47526 | 0.00280 | 0.48333 | 0.48135 | -2.17 | -2.88 |

*Fuente: `t3_anchor_audit11.json` (`cells.<n>.by_theta.<θ>`); N_sim = 40000; sin calibración; familia 123.*

Paso 0 (identidad S₀² = (n+1)⁻¹Σ(Y_t − β̂_GLS)²/n en las 100 primeras trayectorias de cada n): peor |Δ| = 8.88e-16; pasa en todas: sí.

### T4 — Consistencia con tendencia

DGP: Y_t = 1 + 0.1 t + x_t, t = 0, …, n; x_t AR(ρ) estacionario. 2000 réplicas por (ρ, n); audit11_design.t4_path, familia 124, celda t4_rho<rho>_n<n>; bootstrap: celda t4boot_rho<rho>. Cantidades: n⁻¹Σû_t² = n^-1 sum_{t=0}^{n} u_t^2, u = detrend_qd(Y) (cbar = -13.5); σ̂²_HAC = rm_core.hac_sigma_sq(Y); RM-GLS (θ = 0.02, tendencia) = audit9_engine.rmgls(Y, n, 0.02, sigma2_hac, 'ct'). Pendiente: MCO de log(mediana) sobre log n; IC 95% bootstrap percentil con B = 2000. Regla de «acotado» (lectura 7): limite superior del IC de la pendiente de resid_ms < 0.5.

**Tabla T4.1. Medianas por n y pendientes log–log.**

| ρ | 1/(1−ρ²) | Cantidad | n = 200 | n = 500 | n = 1000 | n = 2000 | n = 5000 | Pendiente | IC 95% | IC contiene 0 | Cociente n = 5000 / n = 200 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1.3333 | n⁻¹Σû_t² | 1.4556 | 1.4847 | 1.5029 | 1.5039 | 1.5091 | 0.011 | [0.007, 0.015] | no | 1.037 |
| 0.5 | 1.3333 | σ̂²_HAC | 0.4496 | 0.3560 | 0.2978 | 0.2440 | 0.1868 | -0.273 | [-0.276, -0.270] | no | 0.415 |
| 0.5 | 1.3333 | RM-GLS (θ = 0.02, tendencia) | 0.0886 | 0.0506 | 0.0332 | 0.0229 | 0.0148 | -0.559 | [-0.571, -0.545] | no | 0.167 |
| 0.9 | 5.2632 | n⁻¹Σû_t² | 4.9232 | 5.6303 | 5.8491 | 5.9595 | 5.9627 | 0.057 | [0.051, 0.062] | no | 1.211 |
| 0.9 | 5.2632 | σ̂²_HAC | 0.9460 | 0.9356 | 0.9091 | 0.8798 | 0.8305 | -0.041 | [-0.043, -0.038] | no | 0.878 |
| 0.9 | 5.2632 | RM-GLS (θ = 0.02, tendencia) | 0.1482 | 0.0947 | 0.0621 | 0.0381 | 0.0192 | -0.638 | [-0.644, -0.632] | no | 0.129 |

*Fuente: `t4_trend_audit11.json` (`by_rho.<ρ>.quantities.<cantidad>`); N_sim = 2000 por celda; sin calibración; familia 124.*

**¿n⁻¹Σû_t² queda acotado?** ρ = 0.5: sí (límite superior del IC de la pendiente 0.015 frente a 0.5); ρ = 0.9: sí (límite superior del IC de la pendiente 0.062 frente a 0.5).
Valores no finitos: 0.

### T5 — Cifras citadas del manuscrito

Frases leídas de `paper_latex_v12.zip` (sha256 `236cbb6580dd85fbd16de6b63a7a8d6788fc74569c3df2fd04116f57123887c3`); regla de confirmación de la lectura 8.

| Ítem | Manuscrito | Cifra impresa | Valor en el JSON | Fuente | Confirmada |
|---|---|---|---|---|---|
| 1 | `v12/sec5_montecarlo.tex:664` | at most 0.1 points | máx. \|Δ\| = 0.10 pp (celda `garch_p095_t5_n1000`; 28 celdas: garch, gauss, heavy; R = 0 frente a R = 0.5, RM theta = 0.1 (A8 B2a)) | `b2_size_audit8.json` · `B2a.cells.<celda>.delta_pp (max \|.\| sobre B2a.gate.cells_evaluated); B2a.gate.max_abs_delta_pp` | **sí** |
| 2 | `v12/sec5_montecarlo.tex:668` | 14 to 28 points | DGP1_rho095_n200: 15.48, DGP1_rho097_n500: 27.74, DGP1_rho099_n1000: 14.36 pp (alpha1_hac_Ncal50000) | `adaptive_size_power_audit5b.json` · `alpha1_hac_Ncal50000.<celda>.adaptive - rebalanced` | **sí** |
| 3 | `v12/sec1_introduction.tex:40`, `v12/sec2_statistic.tex:51`, `v12/sec5_montecarlo.tex:670`, `v12/sec7_conclusion.tex:37` | more than 30; more than 30; about 30; about 30 | coste de centrar (potencia RM-GLS − RM, demeaned, n = 2000, c = 10, θ = 0.1) = 24.78 pp (0.6859 − 0.4380); brecha de RM a la envolvente = 33.35 pp; de RM-GLS = 8.57 pp | `b4_local_power_audit8.json` · `cases.<caso>.power.10.0 y gap_to_envelope; gls_rule.G1` | **no** |
| 4 | `v12/sec6_application.tex:87` | 0.0277 & 0.437 & 13 & 33.8 & 11 & 199.6 & 109.3 | 0.0277 & 0.4367 & 13 & 33.8462 & 11 & 199.5593 & 109.2614 (fp_mean, fp_max, detections, mean_latency_detected, false_alarm_episodes, mean_run_length, censored_latency_mean) | `b103_application_audit10.json` · `summary.rhat_prereg.fp_mean`, `summary.rhat_prereg.fp_max`, `summary.rhat_prereg.detections`, `summary.rhat_prereg.mean_latency_detected`, `matched_rate.tests.rhat_prereg.false_alarm_episodes`, `matched_rate.tests.rhat_prereg.mean_run_length`, `matched_rate.tests.rhat_prereg.censored_latency_mean` | **sí** |

Detalle del ítem 2 (todas las configuraciones de `adaptive_size_power_audit5b.json`): sigma_known_Ncal10000: 10.44–24.98 pp; alpha1_hac_Ncal10000: 14.32–27.20 pp; alpha2_hac_Ncal10000: 14.32–27.22 pp; sigma_known_Ncal50000: 10.94–25.44 pp; alpha1_hac_Ncal50000: 14.36–27.74 pp; alpha2_hac_Ncal50000: 14.34–27.82 pp.

Detalle del ítem 3 (coste de centrar a c = 10 y su máximo sobre c, por θ de A8 B4; θ = 0.02 no está en B4): θ = 0.05: 22.78 pp (máx. 23.96 pp en c = 11.0); θ = 0.1: 24.78 pp (máx. 26.79 pp en c = 12.0); θ = 0.2: 26.23 pp (máx. 29.52 pp en c = 12.0). Tendencia: θ = 0.05: 1.76 pp; θ = 0.1: 3.07 pp; θ = 0.2: 4.88 pp. Regla G1 de A8: brecha RM-GLS 8.57 pp, brecha RM 33.355 pp, reducción 24.785 pp.

Detalle del ítem 4: tasa común del pie de tabla 0.0227 (`v12/sec6_application.tex:56`) frente a 0.022742 en `b103_application_audit10.json` → sí. Referencia: A9 0.0277 & 0.4367 & 13 & 33.8462 & 11 & 199.2203 & 109.1932 y A8 0.0277 & 0.4367 & 13 & 33.8462 & 11 & 199.2203 & 109.1932 coinciden en 5 de 7 campos (las columnas a tasa común se recalcularon en A10 con la primaria θ = 0.02, que fija la tasa objetivo).

## 2. Criterios y compuertas

| Criterio | Regla | Medido | Veredicto |
|---|---|---|---|
| T0 colisiones | 0 colisiones con los streams previos y dentro de A11 | 0 / 0 | pasa |
| T1 datos | arrays graficados idénticos bit a bit en las seis figuras | 6 de 6 | pasa |
| T3 criterio (literal) | fila n = 20000 a menos de 3 EE de (1−θ)/2 + θ/3 − 39.67/n para θ = 0 | media 0.49218, EE 0.00281, objetivo 0.49802 → z = -2.08 (con κ exacto: objetivo 0.49802, z = -2.08) | pasa |
| T3 Paso 0 | identidad S₀² frente a la fórmula de la Observación ≤ 1e-12 | 8.88e-16 | pasa |
| T4 acotado (informativo) | limite superior del IC de la pendiente de resid_ms < 0.5 | ρ = 0.5: 0.015; ρ = 0.9: 0.062 | ρ = 0.5 acotado, ρ = 0.9 acotado |

## 3. Procedencia

**Archivos que alimentan este reporte** (`manifest_audit11.json`; el reporte se registra después de escribirse).

| Archivo | sha256 | Bytes | Script | Commit | Árbol limpio | Código commiteado |
|---|---|---|---|---|---|---|
| experiments/figures/fig_calibration_gain_audit10.pdf | `81d8bebb810b194931cc1a595fb772c98358381efdd2ad7c932b28837d8aba35` | 16645 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/figures/fig_dgp3_audit10.pdf | `baa63ae0b1971c5638963199e9245c70de662a4acf55cc94fcdbe0ff12a75b08` | 18773 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/figures/fig_local_power_audit10.pdf | `08a73351b893727f3debc8716286cceea1a58e72df973de28e4b04baae569809` | 21533 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/figures/fig_power_equalized_audit10.pdf | `6741dec11c644b846255e265c2def35d40f56b33594416f4bcae379b4c6ef974` | 28267 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/figures/fig_size_shift_audit10.pdf | `32152038aceeda699150737d019a2aaa1e70cffd5d62ccd29f5470366163aa0b` | 19876 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/figures/fig_theta_ladder_audit10.pdf | `88d5d92abc9d4fc3dfea7aec7a5d8550cb5fce4d83964922d2b77d97721debcc` | 13228 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/results/figures_audit11.json | `8f675819c92ef5a117e569609b62f813e031df3baaac47f2941922c5c6e88552` | 14073 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| experiments/results/t0_protocol_audit11.json | `c5f90cb94232226ceb74c2b20fb7b2f1704a3149f6d8638165bef2f08c4efbfb` | 10142 | experiments/audit11_t0_protocol.py | 5b93502 | no | sí |
| experiments/results/t2_dgp2_audit11.json | `faedbc13b4b90ef78e7a5cf13af4df784628a72f0fa1f734b42b0b977b04b142` | 50735 | experiments/audit11_t2_dgp2.py | 5b93502 | no | sí |
| experiments/results/t3_anchor_audit11.json | `0431b4356a090f8e858cc1350121f23a3c708491008e12d78becab25f701e0b8` | 19571 | experiments/audit11_t3_anchor.py | 5b93502 | no | sí |
| experiments/results/t4_trend_audit11.json | `1398c44d5b285c04ea1f6d70c7d7e8f6bcc1551f755b28fa62f834daa5a07629` | 12534 | experiments/audit11_t4_trend.py | 5b93502 | no | sí |
| experiments/results/t5_claims_audit11.json | `8a8e93edf0951ff6883d06e859bc16773c74aa929837c0f53cef728f88fda6b1` | 23822 | experiments/audit11_t5_claims.py | 5b93502 | no | sí |
| experiments/results/tab_dgp2_audit11.md | `9640bd530c98ea3b06f90166dc2d2ff1d927c9eb67221706379ef337e7133246` | 1719 | experiments/audit11_t2_dgp2.py | 5b93502 | no | sí |
| experiments/results/tab_dgp2_audit11.tex | `c487945d8a3f27355e2bba173bb54cb4497b9c96e33325c5e9ba7f1e4960e80f` | 2037 | experiments/audit11_t2_dgp2.py | 5b93502 | no | sí |
| paper/figures/fig_calibration_gain_audit10.pdf | `81d8bebb810b194931cc1a595fb772c98358381efdd2ad7c932b28837d8aba35` | 16645 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| paper/figures/fig_dgp3_audit10.pdf | `baa63ae0b1971c5638963199e9245c70de662a4acf55cc94fcdbe0ff12a75b08` | 18773 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| paper/figures/fig_local_power_audit10.pdf | `08a73351b893727f3debc8716286cceea1a58e72df973de28e4b04baae569809` | 21533 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| paper/figures/fig_power_equalized_audit10.pdf | `6741dec11c644b846255e265c2def35d40f56b33594416f4bcae379b4c6ef974` | 28267 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| paper/figures/fig_size_shift_audit10.pdf | `32152038aceeda699150737d019a2aaa1e70cffd5d62ccd29f5470366163aa0b` | 19876 | experiments/make_figures_audit11.py | 5b93502 | no | sí |
| paper/figures/fig_theta_ladder_audit10.pdf | `88d5d92abc9d4fc3dfea7aec7a5d8550cb5fce4d83964922d2b77d97721debcc` | 13228 | experiments/make_figures_audit11.py | 5b93502 | no | sí |

Comandos: T0: `experiments/audit11_t0_protocol.py`; T1: `experiments/make_figures_audit11.py`; T2: `experiments/audit11_t2_dgp2.py`; T3: `experiments/audit11_t3_anchor.py --run --cores 14; --analyze`; T4: `experiments/audit11_t4_trend.py --run --cores 14; --analyze`; T5: `experiments/audit11_t5_claims.py`.

- T3: tiempo de cómputo por celda (s): 200: 10.7, 500: 1.7, 1000: 3.5, 2000: 7.3, 5000: 16.3, 20000: 47.8; total 87.3 s.
- T4: tiempo de cómputo por celda (s): 0.5|200: 7.3, 0.5|500: 0.2, 0.5|1000: 0.5, 0.5|2000: 0.6, 0.5|5000: 0.9, 0.9|200: 0.1, 0.9|500: 0.2, 0.9|1000: 0.4, 0.9|2000: 0.6, 0.9|5000: 1.0; total 11.9 s.
- Suite completa (`pytest_audit11.log`): collected 256; passed 256; failed 0; skipped 0; 758.7 s.
- Test de literales (`tests/test_no_literals_audit11.py`): test_generator_has_no_result_literals[experiments/audit11_generate_report.py] PASSED; test_generator_has_no_result_literals[experiments/make_figures_audit11.py] PASSED; test_generator_has_no_result_literals[experiments/audit11_t2_dgp2.py] PASSED; test_generator_has_no_result_literals[experiments/audit11_t5_claims.py] PASSED; test_detector_catches_a_literal PASSED; test_figure_data_comparator_detects_one_changed_value PASSED.
- Checkpoints de T3 y T4 (`checkpoints/audit11_t3`, `checkpoints/audit11_t4`) sin commitear; se regeneran bit a bit desde la familia y el índice de réplica.

## 4. Desviaciones

| Qué | Motivo | Cuándo | Efecto |
|---|---|---|---|
| `fig_theta_ladder`: 0.02 queda centrada en su marca (no alineada a la izquierda como fijaba la lectura 4); solo 0.00 se alinea a la derecha | Con 0.02 alineada a la izquierda chocaba con 0.05 (comprobado en el PDF) | después de ver la figura | Ninguno sobre los datos |
| `fig_calibration_gain`: leyenda en dos columnas y bajada | En una fila era más ancha que los paneles; en dos pisaba la etiqueta «n» | después de ver la figura | Ninguno sobre los datos |
| Los seis PDF se sobrescriben con el mismo nombre; `figures_audit10.json` y `manifest_audit10.json` conservan los sha256 anteriores | El encargo pide conservar los nombres y la regla prohíbe modificar JSON de auditorías previas | antes (lectura 3) | Los sha256 vigentes están en `figures_audit11.json` y `manifest_audit11.json` |
| T0 se ejecutó dos veces: en la primera el protocolo en disco tenía finales CRLF (el commit, LF) y los sha256 diferían; se normalizó a LF sin cambiar el contenido | Final de línea | antes de cualquier cómputo | Ninguno; sha256 en disco = commiteado (T0) |
| T2 falló dos veces antes de escribir su JSON (un `%` sin escapar en el comentario del `.tex` y la consola cp1252 al imprimir δ); se corrigió y se reejecutó | Errores de programación y de consola | durante T2 | Ninguno sobre valores |
| T5: la localización de líneas se corrigió para citar la línea donde empieza la frase (no el inicio de la ventana de dos líneas) y un patrón de T3 que tomaba la cita equivocada | Error de programación | durante T5 | Ninguno sobre valores |
| Las cifras impresas del manuscrito para T3 están escritas en `audit11_t3_anchor.py`; el generador comprueba que coinciden con las que T5 lee del zip | T3 se ejecutó antes que T5 | antes | Comprobación en §7(b) |

## 5. No ejecutado

Nada: T0–T5 se ejecutaron completas. No se editó el manuscrito (ni `paper/*.tex` ni el zip v12).

## 6. Conclusiones

1. T1: las seis figuras están en inglés, con los mismos nombres; datos graficados idénticos bit a bit en las seis: sí.
2. T2: tabla de DGP 2 con θ = 0.02 exportada en Markdown y LaTeX; ZA estaba en el JSON de A10 (valor crítico simulado).
3. T3: criterio de la fila n = 20000 con θ = 0: z = -2.08 (pasa). Cifras simuladas del manuscrito: n = 200: impresa 0.360, simulada 0.3603 ± 0.0019, z = 0.15 (se reproduce); n = 500: impresa 0.438, simulada 0.4304 ± 0.0024, z = -3.16 (NO se reproduce); n = 2000: impresa 0.481, simulada 0.4835 ± 0.0028, z = 0.89 (se reproduce).
4. T4: pendiente log–log de la mediana de n⁻¹Σû_t²: ρ = 0.5: 0.011 [0.007, 0.015]; ρ = 0.9: 0.057 [0.051, 0.062]; acotado según la lectura 7: ρ = 0.5 sí, ρ = 0.9 sí.
5. T5: confirmadas 3 de 4 (ítem 1 sí, ítem 2 sí, ítem 3 no, ítem 4 sí).

## 7. Anomalías y contradicciones con el manuscrito

### (a) Anomalías numéricas

- T3: la media de S₀² baja de n = 5000 (0.49365 ± 0.00283) a n = 20000 (0.49218 ± 0.00281); la diferencia es -0.37 EE combinados. Mismo patrón con θ = 0.02 y 0.1, porque se evalúan sobre las mismas trayectorias.
- T4, ρ = 0.5: la mediana de n⁻¹Σû_t² en n = 5000 es 1.5091 y la varianza estacionaria del DGP, 1/(1−ρ²), es 1.3333. El IC de la pendiente contiene 0: no.
- T4, ρ = 0.9: la mediana de n⁻¹Σû_t² en n = 5000 es 5.9627 y la varianza estacionaria del DGP, 1/(1−ρ²), es 5.2632. El IC de la pendiente contiene 0: no.

Cifras impresas en `audit11_t3_anchor.py` frente a las leídas del zip (`v12/appA_proofs.tex:77`): coinciden.

### (b) Frases del manuscrito v12 revisadas

| Manuscrito v12 | Frase / cifra | Valor de A11 | z | Se confirma | Corrección sugerida |
|---|---|---|---|---|---|
| `v12/appA_proofs.tex:77`, `v12/sec3_theory.tex:66` | E[S₀²] simulado a n = 200: 0.360 | 0.3603 ± 0.0019 | 0.15 | sí | — |
| `v12/appA_proofs.tex:77` | E[S₀²] simulado a n = 500: 0.438 | 0.4304 ± 0.0024 | -3.16 | **no** | 0.430 (simulado de A11 a tres decimales) |
| `v12/appA_proofs.tex:77`, `v12/sec3_theory.tex:65` | E[S₀²] simulado a n = 2000: 0.481 | 0.4835 ± 0.0028 | 0.89 | sí | 0.483 (simulado de A11 a tres decimales) |
| `v12/appA_proofs.tex:78` | primer orden 1/2 − κ/n a n = 200: 0.302 | 0.30167 | — | sí (aritmética) | — |
| `v12/appA_proofs.tex:78` | primer orden 1/2 − κ/n a n = 500: 0.421 | 0.42067 | — | sí (aritmética) | — |
| `v12/appA_proofs.tex:78` | primer orden 1/2 − κ/n a n = 2000: 0.480 | 0.48017 | — | sí (aritmética) | — |
| `v12/sec3_theory.tex:65` | κ(−7) ≈ 39.7 | 39.666667 | — | sí | — |
| `v12/sec1_introduction.tex:40` | «more than 30 points» de potencia local al centrar en la media | 24.78 pp (θ = 0.1, c = 10, n = 2000) | — | **no** | «about 25 points»: coste de centrar 24.8 pp (máx. sobre c: 26.8 pp en c = 12.0); los 33.4 pp son la brecha de RM a la envolvente, no el coste |
| `v12/sec2_statistic.tex:51` | «more than 30 points» de potencia local al centrar en la media | 24.78 pp (θ = 0.1, c = 10, n = 2000) | — | **no** | «about 25 points»: coste de centrar 24.8 pp (máx. sobre c: 26.8 pp en c = 12.0); los 33.4 pp son la brecha de RM a la envolvente, no el coste |
| `v12/sec5_montecarlo.tex:670` | «about 30 points» de potencia local al centrar en la media | 24.78 pp (θ = 0.1, c = 10, n = 2000) | — | **no** | «about 25 points»: coste de centrar 24.8 pp (máx. sobre c: 26.8 pp en c = 12.0); los 33.4 pp son la brecha de RM a la envolvente, no el coste |
| `v12/sec7_conclusion.tex:37` | «about 30 points» de potencia local al centrar en la media | 24.78 pp (θ = 0.1, c = 10, n = 2000) | — | **no** | «about 25 points»: coste de centrar 24.8 pp (máx. sobre c: 26.8 pp en c = 12.0); los 33.4 pp son la brecha de RM a la envolvente, no el coste |
| `v12/sec5_montecarlo.tex:664` | ítem 1 de T5 | ver Tabla T5 | — | sí | — |
| `v12/sec5_montecarlo.tex:668` | ítem 2 de T5 | ver Tabla T5 | — | sí | — |
| `v12/sec6_application.tex:87` | ítem 4 de T5 | ver Tabla T5 | — | sí | — |

## Anexo: tabla maestra de los números nuevos

| clave | valor | IC o EE | N_sim | N_cal | familia | archivo JSON | ruta |
|---|---|---|---|---|---|---|---|
| T3 E[S²] n = 200 θ = 0 | 0.36029 | EE 0.00192 | 40000 | — | 123 | t3_anchor_audit11.json | cells.200.by_theta.0.mean |
| T3 E[S²] n = 200 θ = 0.02 | 0.35567 | EE 0.00191 | 40000 | — | 123 | t3_anchor_audit11.json | cells.200.by_theta.0.02.mean |
| T3 E[S²] n = 200 θ = 0.1 | 0.33987 | EE 0.00189 | 40000 | — | 123 | t3_anchor_audit11.json | cells.200.by_theta.0.1.mean |
| T3 E[S²] n = 500 θ = 0 | 0.43039 | EE 0.00241 | 40000 | — | 123 | t3_anchor_audit11.json | cells.500.by_theta.0.mean |
| T3 E[S²] n = 500 θ = 0.02 | 0.42647 | EE 0.00241 | 40000 | — | 123 | t3_anchor_audit11.json | cells.500.by_theta.0.02.mean |
| T3 E[S²] n = 500 θ = 0.1 | 0.41204 | EE 0.00240 | 40000 | — | 123 | t3_anchor_audit11.json | cells.500.by_theta.0.1.mean |
| T3 E[S²] n = 1000 θ = 0 | 0.46318 | EE 0.00263 | 40000 | — | 123 | t3_anchor_audit11.json | cells.1000.by_theta.0.mean |
| T3 E[S²] n = 1000 θ = 0.02 | 0.45958 | EE 0.00263 | 40000 | — | 123 | t3_anchor_audit11.json | cells.1000.by_theta.0.02.mean |
| T3 E[S²] n = 1000 θ = 0.1 | 0.44586 | EE 0.00263 | 40000 | — | 123 | t3_anchor_audit11.json | cells.1000.by_theta.0.1.mean |
| T3 E[S²] n = 2000 θ = 0 | 0.48346 | EE 0.00275 | 40000 | — | 123 | t3_anchor_audit11.json | cells.2000.by_theta.0.mean |
| T3 E[S²] n = 2000 θ = 0.02 | 0.48000 | EE 0.00275 | 40000 | — | 123 | t3_anchor_audit11.json | cells.2000.by_theta.0.02.mean |
| T3 E[S²] n = 2000 θ = 0.1 | 0.46655 | EE 0.00275 | 40000 | — | 123 | t3_anchor_audit11.json | cells.2000.by_theta.0.1.mean |
| T3 E[S²] n = 5000 θ = 0 | 0.49365 | EE 0.00283 | 40000 | — | 123 | t3_anchor_audit11.json | cells.5000.by_theta.0.mean |
| T3 E[S²] n = 5000 θ = 0.02 | 0.49024 | EE 0.00283 | 40000 | — | 123 | t3_anchor_audit11.json | cells.5000.by_theta.0.02.mean |
| T3 E[S²] n = 5000 θ = 0.1 | 0.47671 | EE 0.00283 | 40000 | — | 123 | t3_anchor_audit11.json | cells.5000.by_theta.0.1.mean |
| T3 E[S²] n = 20000 θ = 0 | 0.49218 | EE 0.00281 | 40000 | — | 123 | t3_anchor_audit11.json | cells.20000.by_theta.0.mean |
| T3 E[S²] n = 20000 θ = 0.02 | 0.48880 | EE 0.00281 | 40000 | — | 123 | t3_anchor_audit11.json | cells.20000.by_theta.0.02.mean |
| T3 E[S²] n = 20000 θ = 0.1 | 0.47526 | EE 0.00280 | 40000 | — | 123 | t3_anchor_audit11.json | cells.20000.by_theta.0.1.mean |
| T3 criterio z (39.67) | -2.079 | — | 40000 | — | 123 | t3_anchor_audit11.json | criterion_n20000_theta0.z_literal |
| T3 z frente al manuscrito, n = 200 | 0.152 | — | 40000 | — | 123 | t3_anchor_audit11.json | manuscript_simulated.200.z |
| T3 z frente al manuscrito, n = 500 | -3.161 | — | 40000 | — | 123 | t3_anchor_audit11.json | manuscript_simulated.500.z |
| T3 z frente al manuscrito, n = 2000 | 0.892 | — | 40000 | — | 123 | t3_anchor_audit11.json | manuscript_simulated.2000.z |
| T4 mediana n⁻¹Σû_t² ρ = 0.5 n = 200 | 1.45562 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.resid_ms.median.200 |
| T4 mediana n⁻¹Σû_t² ρ = 0.5 n = 500 | 1.48474 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.resid_ms.median.500 |
| T4 mediana n⁻¹Σû_t² ρ = 0.5 n = 1000 | 1.50294 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.resid_ms.median.1000 |
| T4 mediana n⁻¹Σû_t² ρ = 0.5 n = 2000 | 1.50389 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.resid_ms.median.2000 |
| T4 mediana n⁻¹Σû_t² ρ = 0.5 n = 5000 | 1.50911 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.resid_ms.median.5000 |
| T4 pendiente n⁻¹Σû_t² ρ = 0.5 | 0.0109 | IC [0.0066, 0.0155] | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.resid_ms.slope |
| T4 mediana σ̂²_HAC ρ = 0.5 n = 200 | 0.44964 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.sigma2_hac.median.200 |
| T4 mediana σ̂²_HAC ρ = 0.5 n = 500 | 0.35597 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.sigma2_hac.median.500 |
| T4 mediana σ̂²_HAC ρ = 0.5 n = 1000 | 0.29779 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.sigma2_hac.median.1000 |
| T4 mediana σ̂²_HAC ρ = 0.5 n = 2000 | 0.24401 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.sigma2_hac.median.2000 |
| T4 mediana σ̂²_HAC ρ = 0.5 n = 5000 | 0.18680 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.sigma2_hac.median.5000 |
| T4 pendiente σ̂²_HAC ρ = 0.5 | -0.2728 | IC [-0.2764, -0.2696] | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.sigma2_hac.slope |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.5 n = 200 | 0.08855 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.statistic.median.200 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.5 n = 500 | 0.05062 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.statistic.median.500 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.5 n = 1000 | 0.03316 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.statistic.median.1000 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.5 n = 2000 | 0.02285 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.statistic.median.2000 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.5 n = 5000 | 0.01478 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.statistic.median.5000 |
| T4 pendiente RM-GLS (θ = 0.02, tendencia) ρ = 0.5 | -0.5590 | IC [-0.5712, -0.5449] | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.5.quantities.statistic.slope |
| T4 mediana n⁻¹Σû_t² ρ = 0.9 n = 200 | 4.92321 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.resid_ms.median.200 |
| T4 mediana n⁻¹Σû_t² ρ = 0.9 n = 500 | 5.63030 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.resid_ms.median.500 |
| T4 mediana n⁻¹Σû_t² ρ = 0.9 n = 1000 | 5.84913 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.resid_ms.median.1000 |
| T4 mediana n⁻¹Σû_t² ρ = 0.9 n = 2000 | 5.95950 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.resid_ms.median.2000 |
| T4 mediana n⁻¹Σû_t² ρ = 0.9 n = 5000 | 5.96268 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.resid_ms.median.5000 |
| T4 pendiente n⁻¹Σû_t² ρ = 0.9 | 0.0566 | IC [0.0507, 0.0616] | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.resid_ms.slope |
| T4 mediana σ̂²_HAC ρ = 0.9 n = 200 | 0.94601 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.sigma2_hac.median.200 |
| T4 mediana σ̂²_HAC ρ = 0.9 n = 500 | 0.93555 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.sigma2_hac.median.500 |
| T4 mediana σ̂²_HAC ρ = 0.9 n = 1000 | 0.90913 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.sigma2_hac.median.1000 |
| T4 mediana σ̂²_HAC ρ = 0.9 n = 2000 | 0.87983 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.sigma2_hac.median.2000 |
| T4 mediana σ̂²_HAC ρ = 0.9 n = 5000 | 0.83054 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.sigma2_hac.median.5000 |
| T4 pendiente σ̂²_HAC ρ = 0.9 | -0.0410 | IC [-0.0435, -0.0377] | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.sigma2_hac.slope |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.9 n = 200 | 0.14820 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.statistic.median.200 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.9 n = 500 | 0.09469 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.statistic.median.500 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.9 n = 1000 | 0.06214 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.statistic.median.1000 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.9 n = 2000 | 0.03815 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.statistic.median.2000 |
| T4 mediana RM-GLS (θ = 0.02, tendencia) ρ = 0.9 n = 5000 | 0.01919 | — | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.statistic.median.5000 |
| T4 pendiente RM-GLS (θ = 0.02, tendencia) ρ = 0.9 | -0.6383 | IC [-0.6442, -0.6318] | 2000 | — | 124 | t4_trend_audit11.json | by_rho.0.9.quantities.statistic.slope |
| T5.1 máx. \|Δ\| tamaño sin canal de varianza (pp) | 0.100 | — | 5000 | 50000 | (A8) | b2_size_audit8.json | B2a.cells.garch_p095_t5_n1000.delta_pp |
| T5.2 pérdida por rebalanceo DGP1_rho095_n200 (pp) | 15.48 | — | no registrado | 50000 | (A5) | adaptive_size_power_audit5b.json | alpha1_hac_Ncal50000.DGP1_rho095_n200 |
| T5.2 pérdida por rebalanceo DGP1_rho097_n500 (pp) | 27.74 | — | no registrado | 50000 | (A5) | adaptive_size_power_audit5b.json | alpha1_hac_Ncal50000.DGP1_rho097_n500 |
| T5.2 pérdida por rebalanceo DGP1_rho099_n1000 (pp) | 14.36 | — | no registrado | 50000 | (A5) | adaptive_size_power_audit5b.json | alpha1_hac_Ncal50000.DGP1_rho099_n1000 |
| T5.3 coste de centrar, c = 10, θ = 0.05 (pp) | 22.785 | — | 20000 | 50000 | (A8) | b4_local_power_audit8.json | cases.dm.power.10.0.gls_t0.05 − rm_t0.05 |
| T5.3 coste de centrar, c = 10, θ = 0.1 (pp) | 24.785 | — | 20000 | 50000 | (A8) | b4_local_power_audit8.json | cases.dm.power.10.0.gls_t0.1 − rm_t0.1 |
| T5.3 coste de centrar, c = 10, θ = 0.2 (pp) | 26.230 | — | 20000 | 50000 | (A8) | b4_local_power_audit8.json | cases.dm.power.10.0.gls_t0.2 − rm_t0.2 |
| T1 sha256 fig_local_power_audit10.pdf | `08a73351b893727f3debc8716286cceea1a58e72df973de28e4b04baae569809` | — | — | — | 121 | figures_audit11.json | figures.fig_local_power_audit10.pdf.sha256 |
| T1 sha256 fig_theta_ladder_audit10.pdf | `88d5d92abc9d4fc3dfea7aec7a5d8550cb5fce4d83964922d2b77d97721debcc` | — | — | — | 121 | figures_audit11.json | figures.fig_theta_ladder_audit10.pdf.sha256 |
| T1 sha256 fig_power_equalized_audit10.pdf | `6741dec11c644b846255e265c2def35d40f56b33594416f4bcae379b4c6ef974` | — | — | — | 121 | figures_audit11.json | figures.fig_power_equalized_audit10.pdf.sha256 |
| T1 sha256 fig_size_shift_audit10.pdf | `32152038aceeda699150737d019a2aaa1e70cffd5d62ccd29f5470366163aa0b` | — | — | — | 121 | figures_audit11.json | figures.fig_size_shift_audit10.pdf.sha256 |
| T1 sha256 fig_dgp3_audit10.pdf | `baa63ae0b1971c5638963199e9245c70de662a4acf55cc94fcdbe0ff12a75b08` | — | — | — | 121 | figures_audit11.json | figures.fig_dgp3_audit10.pdf.sha256 |
| T1 sha256 fig_calibration_gain_audit10.pdf | `81d8bebb810b194931cc1a595fb772c98358381efdd2ad7c932b28837d8aba35` | — | — | — | 121 | figures_audit11.json | figures.fig_calibration_gain_audit10.pdf.sha256 |
