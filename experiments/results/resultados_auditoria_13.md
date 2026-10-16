# Auditoría A13 — Regeneración con θ = 0 y cierre

Protocolo `experiments/protocol_audit13.md` (commit `57b2b32`). Manuscrito de referencia: `paper_latex_v13.zip` (sha256 `fae1334ba259fc359db4c7922b48a926a8aaf713f37d92e26d1435d8b7109dac`), de sólo lectura; no se editó ningún `.tex`. Orden del encargo: B13.0 → E(1) → E(2) → E(3) → T. B13.Q se ejecutó sobre `paper_latex_v14.zip` (sha256 `3b21e2250002dee66780027d49ea3458d33f4ee481f042b4fe6a43a301d7a12b`) según la enmienda `experiments/protocol_audit13_amend1.md` (commit `490e01a`); ese manuscrito tampoco se editó.

## 1. Resultados

### B13.0 — Protocolo, inventario y semillas

- Protocolo `experiments/protocol_audit13.md`: commit `57b2b32` (2026-09-22T16:50:20-06:00); sha256 en disco `ffe3c068db891dcc3b083e517e862fd712c565fcb7e8df613aa0bd091affc575`, commiteado `ffe3c068db891dcc3b083e517e862fd712c565fcb7e8df613aa0bd091affc575` → coinciden.
- Manuscrito de referencia `paper_latex_v13.zip`: sha256 `fae1334ba259fc359db4c7922b48a926a8aaf713f37d92e26d1435d8b7109dac` (147313 bytes).
- Familias: E = 140, TAB = 141, AWB = 142, APP = 143, AMEND1 = 144, AMEND2 = 145, AMEND3 = 146, AMEND4 = 147, AMEND5 = 148, AMEND6 = 149. Celdas: 141: 6; 142: 16; 143: 20.
- Equivalencia `spawn_key` ↔ `.spawn`: 126 flujos comprobados, 0 discrepancias.
- Colisiones (palabra 0 de SeedSequence.generate_state(uint64) (metodo de A8-A12)): 528000 flujos nuevos frente a 18581102 previos (familias 90–137, 2450600 semillas enteras de A5–A7 y la 42): 0 colisiones con las previas, 0 dentro de A13.

| JSON reutilizado | sha256 | Bytes |
|---|---|---|
| b101_theta_audit10.json | `c3e72c4e00cdb606bcf61fb8d21360b97186c29aed2f539faf7bd0fda1e71ef2` | 158704 |
| b103_equalized_audit10.json | `052b49ba21718a17a581787afc026b5aa5b6c50d579821c50146434bc2e85a70` | 579987 |
| b103_finite_audit10.json | `d077de0e884fc5498eb8c9b41d9a17b6b54e2db1bf2fe96c24ea631cfd0ba06d` | 61633 |
| b103_lown_audit10.json | `caaf78815285b72aa1be3eb7ca3e7674188034c977349fc02e5ac3b5c93790a9` | 47295 |
| b103_cv_audit10.json | `f5e5fdccaa48db5334ed3709dcf99350c1f5916be764620902784b32af86d1cd` | 48053 |
| b103_awb_audit10.json | `23924c3c0ba694bca40f55b37c9ceaec949b43945adee90b03099de5c1dec1dc` | 26757 |
| b103_dgp5_audit10.json | `e7c6aa5904fa50423a85b3d3991357e69d0683f32261477159cfa3d266579a4a` | 62457 |
| b103_application_audit10.json | `b02ff88b479e7bbe2159e6e376449c289fa6ebf433fbe48d7e201554b4d70396` | 82996 |
| b92_theta_audit9.json | `c959a4451b2e637b0768498c9bcb951d1313711de4e7773cf1697659acea1355` | 740444 |
| b97_critical_values_audit9.json | `58473d073aeb9a574a92b0668af24a61853ab19ea50ef5ef0b47c633d9cd9336` | 44792 |
| b95_awb_audit9.json | `8036cc846411da3e79a6623f883c290874d3905ad8d3ffae30ef0e73b87518e2` | 23909 |
| b96_application_audit9.json | `a42f0bc8b83bf44d3b4b4000e69c4c1fe6fa01bf02981d733ec6984d8cdc1aa5` | 80185 |
| b5_power_audit8.json | `768742d56f1048b8fcf724ff355ab3dcc921dfc19489ab69a6402a969e1c3d52` | 351136 |
| b3_comparators_audit8.json | `adbd76d47755b1c280cd7d9230c852423978b343b4af98f241f0a7b0987dbb7e` | 158517 |
| dgp5_mixed_audit7.json | `17ddf6cd5fd57d82e126ab09bb97b27733c64992e6686531d7bbdfe71dbfb7d6` | 293734 |
| bA_ma_audit12.json | `663c563b9dd84a8e16a35b2117ab03dac10f06ea34290a690b2aa2593c2543b1` | 695138 |
| bC_initial_audit12.json | `cf5b196e6f73cecf81babdd6fecd75913d2ff5c5e808815f04ee94645ba19161` | 80946 |
| figures_audit11.json | `8f675819c92ef5a117e569609b62f813e031df3baaac47f2941922c5c6e88552` | 14073 |

| Checkpoints reutilizados | Archivos | sha256 agregado |
|---|---|---|
| audit10_cal | 6 | `8b748cca48be31a51479f08cecffdc5d8007f61e3be1e60dfaf229f376430569` |
| audit9_cal | 8 | `6fac4c6df54bb74572027f83990333407f4e072d4ce5909da8028a2a399bf415` |
| audit9_b91 | 106 | `7eae3c467a2c9f5ca74e212d2d3ba05aad2d80166a68f21a45f7ecdf46950c06` |
| audit9_b92 | 223 | `1ae8859c625bd5773d467c4155b221f749c9b07bbb95c1bb16605998977875ad` |
| audit9_b94 | 15 | `447ec2d071937952fc338874e87b8d1e7ade106caa741bd66f0dc5e5821ff3da` |
| audit9_b95 | 34 | `1ef24fe6c610ec243f7af914a0ae1dd546abfa26835ed3862ea7a14c70f7dbc6` |
| audit10_b103 | 81 | `823b2711bff4a7816ff40097ca590a10b366ac4fb36c1d30ee18ff0e2074b5fe` |
| audit10_b103_app | 36 | `87a7d2e498b6758c95d724888dbcf96d9a2b696579ec645751f711e721f35f5b` |
| audit8_b5 | 327 | `eaa47ce59bdcc010491a658f20f333db6d6ff52374378b33fb26ed62ceb8d754` |
| audit8_b6 | 16 | `730f55704d9816d69d3a4e7569d68db4a2d64231b031c44620936483319eaafe` |
| audit7_block1 | 342 | `1030c2536864018313afa4cdf98c28a9571e75b09ec8e9065b122344062e8d24` |

### B13.E(1) — Tablas desde JSON existentes, con θ = 0

tab:size en n ∈ {60, 100, 150}: familia 141, N = 50000 por (caso, n), calibración de A10 (n = 60: N_cal 500000; n = 100: N_cal 500000; n = 150: N_cal 500000). Contraste informativo con B10.3.7 (familia 113, independiente) y diferencia pareada θ = 0 − θ = 0.02 sobre los caminos nuevos:

| Celda | θ = 0, familia 141 | θ = 0, B10.3.7 | θ = 0.02, familia 141 | θ = 0.02, B10.3.7 (v13) | θ = 0 − θ = 0.02 pareada (pp, EE) | θ = 0 con el VC de n = 20 000 |
|---|---|---|---|---|---|---|
| dm\|60 | 0.0507 | 0.0493 | 0.0505 | 0.0496 | +0.02 (0.04) | 0.0577 |
| ct\|60 | 0.0503 | 0.0489 | 0.0505 | 0.0489 | -0.02 (0.05) | 0.0191 |
| dm\|100 | 0.0501 | 0.0511 | 0.0497 | 0.0510 | +0.04 (0.03) | 0.0573 |
| ct\|100 | 0.0524 | 0.0493 | 0.0526 | 0.0496 | -0.02 (0.03) | 0.0356 |
| dm\|150 | 0.0487 | 0.0474 | 0.0493 | 0.0476 | -0.05 (0.02) | 0.0553 |
| ct\|150 | 0.0494 | 0.0505 | 0.0490 | 0.0506 | +0.03 (0.02) | 0.0396 |

**Tabla tab:size — tamaño de RM-GLS bajo el paseo aleatorio gaussiano, con θ = 0.**

| n | Constant | Trend |
|---|---|---|
| 60 | 0.0507 [0.0488, 0.0526] | 0.0503 [0.0484, 0.0523] |
| 100 | 0.0501 [0.0482, 0.0520] | 0.0524 [0.0504, 0.0543] |
| 150 | 0.0487 [0.0469, 0.0507] | 0.0494 [0.0475, 0.0513] |
| 200 | 0.0502 [0.0489, 0.0516] | 0.0499 [0.0486, 0.0513] |
| 500 | 0.0492 [0.0478, 0.0505] | 0.0502 [0.0489, 0.0516] |
| 1000 | 0.0491 [0.0478, 0.0505] | 0.0505 [0.0492, 0.0519] |

*Fuentes: `e_size_audit13.json`, `b101_theta_audit10.json`, `b103_lown_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_size_audit13.tex` (sha256 `8b57a3f1289301aad0bba50c6c2af2bca994b00070f78aafbab364d6eab3698b`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.2780 pp en `ct|100` (con signo 0.2780). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:calib — tamaño con valores críticos límite y de muestra finita, con θ = 0.**

| Caso | n | RM-GLS q_0.05(n) | RM-GLS at q(n) | RM-GLS at q(20\,000) | DF-GLS asy. | DF-GLS sim. | MSB-GLS asy. | MSB-GLS sim. |
|---|---|---|---|---|---|---|---|---|
| Constant | 60 | 0.2328 | **0.0544** | **0.0607** | **0.0660** | 0.0520 | 0.0502 | 0.0503 |
| Constant | 100 | 0.2321 | 0.0516 | **0.0588** | **0.0568** | 0.0520 | 0.0496 | 0.0527 |
| Constant | 150 | 0.2321 | 0.0496 | **0.0563** | **0.0536** | 0.0516 | **0.0442** | 0.0486 |
| Constant | 200 | 0.2331 | 0.0514 | **0.0556** | 0.0513 | 0.0503 | **0.0460** | 0.0509 |
| Constant | 500 | 0.2357 | 0.0473 | 0.0484 | **0.0452** | **0.0459** | **0.0417** | 0.0471 |
| Constant | 1000 | 0.2362 | 0.0510 | 0.0518 | 0.0498 | 0.0510 | **0.0461** | 0.0508 |
| Constant | 2000 | 0.2360 | 0.0470 | 0.0478 | 0.0478 | 0.0481 | **0.0430** | **0.0467** |
| Constant | 5000 | 0.2370 | 0.0490 | 0.0488 | 0.0498 | 0.0505 | **0.0449** | 0.0487 |
| Trend | 60 | 0.1847 | 0.0520 | **0.0199** | **0.0534** | 0.0517 | **0.0169** | 0.0513 |
| Trend | 100 | 0.1780 | 0.0481 | **0.0323** | **0.0420** | 0.0496 | **0.0225** | 0.0485 |
| Trend | 150 | 0.1755 | 0.0507 | **0.0412** | **0.0386** | 0.0493 | **0.0261** | 0.0504 |
| Trend | 200 | 0.1740 | 0.0480 | **0.0413** | **0.0350** | 0.0474 | **0.0260** | 0.0474 |
| Trend | 500 | 0.1722 | 0.0490 | 0.0472 | **0.0381** | 0.0486 | **0.0336** | 0.0484 |
| Trend | 1000 | 0.1715 | 0.0512 | 0.0508 | **0.0413** | 0.0495 | **0.0394** | 0.0503 |
| Trend | 2000 | 0.1710 | 0.0478 | 0.0486 | **0.0411** | 0.0484 | **0.0398** | 0.0482 |
| Trend | 5000 | 0.1717 | 0.0517 | 0.0510 | **0.0440** | 0.0524 | **0.0428** | 0.0522 |

*Fuentes: `e_calib_audit13.json`. Tabular: `experiments/results/tables_audit13/tab_calib_audit13.tex` (sha256 `50386f28974cec10a0339f3f584d60ae53b063011c41030857cbc146ba2b2c24`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 3.2400 q: unidades del estadistico; tamanos: pp en `ct|60|size_q_20000` (con signo -3.2400). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:localpower — potencia local, n = 2000, con θ = 0.**

| Caso | c | Envelope | RM-GLS | θ = 0.02 | DF-GLS | MZ_t-GLS | MSB-GLS | MSB-GLS asy. |
|---|---|---|---|---|---|---|---|---|
| Constant | 2 | 0.118 | 0.111 | 0.110 | 0.115 | 0.115 | 0.109 | 0.103 |
| Constant | 5 | 0.313 | 0.295 | 0.290 | 0.311 | 0.312 | 0.290 | 0.274 |
| Constant | 7 | 0.497 | 0.464 | 0.458 | 0.494 | 0.495 | 0.460 | 0.438 |
| Constant | 10 | 0.750 | 0.724 | 0.716 | 0.751 | 0.752 | 0.720 | 0.695 |
| Constant | 13.5 | 0.930 | 0.919 | 0.915 | 0.927 | 0.927 | 0.915 | 0.901 |
| Constant | 15 | 0.965 | 0.958 | 0.955 | 0.962 | 0.963 | 0.955 | 0.947 |
| Constant | 20 | 0.998 | 0.998 | 0.997 | 0.996 | 0.996 | 0.997 | 0.996 |
| Trend | 2 | 0.060 | 0.061 | 0.061 | 0.060 | 0.061 | 0.060 | 0.049 |
| Trend | 5 | 0.115 | 0.112 | 0.113 | 0.117 | 0.116 | 0.114 | 0.093 |
| Trend | 7 | 0.175 | 0.171 | 0.170 | 0.175 | 0.175 | 0.171 | 0.144 |
| Trend | 10 | 0.309 | 0.296 | 0.295 | 0.307 | 0.306 | 0.297 | 0.256 |
| Trend | 13.5 | 0.506 | 0.498 | 0.495 | 0.506 | 0.506 | 0.495 | 0.437 |
| Trend | 15 | 0.591 | 0.588 | 0.584 | 0.591 | 0.591 | 0.582 | 0.526 |
| Trend | 20 | 0.846 | 0.846 | 0.843 | 0.846 | 0.846 | 0.839 | 0.793 |

*Fuentes: `b92_theta_audit9.json`. Tabular: `experiments/results/tables_audit13/tab_localpower_audit13.tex` (sha256 `a0a939eb090ae819641ea658e7642ac22f0732d432af54af6b080671615dce6e`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.8700 pp en `dm|c10.0` (con signo 0.8700). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:dgp1 — potencia frente a AR(1), caso constante, tamaño igualado, con θ = 0.**

| ρ | n | RM-GLS | RM | ADF | PP | DF-GLS | MZ_t | MSB | p |
|---|---|---|---|---|---|---|---|---|---|
| 0.85 | 200 | 1.000 | 0.994 | 0.958 | 0.995 | 0.953 | 0.944 | 0.941 | <0.001 |
| 0.90 | 200 | 0.993 | 0.896 | 0.798 | 0.850 | 0.926 | 0.928 | 0.922 | <0.001 |
| 0.93 | 200 | 0.910 | 0.647 | 0.491 | 0.538 | 0.854 | 0.856 | 0.835 | <0.001 |
| 0.95 | 200 | 0.708 | 0.426 | 0.291 | 0.313 | 0.690 | 0.691 | 0.654 | 0.002 |
| 0.97 | 200 | 0.386 | 0.233 | 0.147 | 0.150 | 0.397 | 0.393 | 0.365 | 0.045 |
| 0.99 | 200 | 0.115 | 0.092 | 0.067 | 0.066 | 0.111 | 0.112 | 0.113 | 0.244 |
| 0.95 | 500 | 1.000 | 0.980 | 0.939 | 0.955 | 0.992 | 0.993 | 0.992 | <0.001 |
| 0.97 | 500 | 0.955 | 0.726 | 0.577 | 0.604 | 0.939 | 0.940 | 0.934 | <0.001 |
| 0.99 | 500 | 0.301 | 0.187 | 0.119 | 0.127 | 0.316 | 0.313 | 0.295 | 0.001 |
| 0.99 | 1000 | 0.737 | 0.434 | 0.303 | 0.318 | 0.755 | 0.755 | 0.728 | <0.001 |

*Fuentes: `e_equalized_audit13.json`, `b103_equalized_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_dgp1_audit13.tex` (sha256 `1d37d8f8166edb48b3bafb4aa0e3cc51a0d677844e997b8dfb2ee420d22a8cdd`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.8400 pp en `dgp1_rho0p99_n1000` (con signo 0.8400). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:ctpower — potencia frente a AR(1) con tendencia, tamaño igualado, con θ = 0.**

| ρ | n | RM-GLS | RM | ADF | PP | DF-GLS | MZ_t | MSB | p |
|---|---|---|---|---|---|---|---|---|---|
| 0.90 | 200 | 0.819 | 0.740 | 0.556 | 0.630 | 0.720 | 0.742 | 0.734 | <0.001 |
| 0.95 | 200 | 0.297 | 0.257 | 0.175 | 0.189 | 0.290 | 0.290 | 0.284 | 0.124 |
| 0.97 | 200 | 0.132 | 0.122 | 0.098 | 0.096 | 0.130 | 0.132 | 0.130 | 0.555 |
| 0.99 | 200 | 0.062 | 0.060 | 0.058 | 0.060 | 0.062 | 0.064 | 0.062 | 1.000 |
| 0.95 | 500 | 0.960 | 0.913 | 0.782 | 0.815 | 0.899 | 0.911 | 0.910 | <0.001 |
| 0.97 | 500 | 0.589 | 0.515 | 0.355 | 0.380 | 0.575 | 0.578 | 0.563 | 0.004 |
| 0.99 | 500 | 0.099 | 0.089 | 0.072 | 0.075 | 0.102 | 0.103 | 0.100 | 0.311 |
| 0.97 | 1000 | 0.994 | 0.977 | 0.913 | 0.923 | 0.975 | 0.980 | 0.980 | <0.001 |
| 0.99 | 1000 | 0.305 | 0.270 | 0.195 | 0.198 | 0.304 | 0.305 | 0.303 | 0.657 |

*Fuentes: `e_equalized_audit13.json`, `b103_equalized_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_ctpower_audit13.tex` (sha256 `afc906a11671c33110ae3fdf366775bcbdd8af626fc55b0aed79d41efbfbb7ac`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.4000 pp en `ct_power_rho0p9_n200` (con signo -0.4000). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:dgp2 — potencia con quiebre de media, tamaño igualado, con θ = 0.**

| δ | n | RM-GLS (θ = 0) | RM | ADF-sim | PP-sim | DF-GLS-sim | MZ_t-GLS-sim | MSB-GLS-sim | ZA | McNemar p |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 200 | 0.713 | 0.432 | 0.299 | 0.322 | 0.695 | 0.689 | 0.658 | 0.119 | 0.002 |
| 0 | 500 | 1.000 | 0.980 | 0.938 | 0.949 | 0.994 | 0.995 | 0.994 | 0.454 | 3.7×10^-9 |
| 0 | 1000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.970 | 1.000 |
| 0.5 | 200 | 0.640 | 0.396 | 0.269 | 0.290 | 0.620 | 0.613 | 0.594 | 0.119 | 0.001 |
| 0.5 | 500 | 1.000 | 0.959 | 0.903 | 0.914 | 0.983 | 0.983 | 0.987 | 0.456 | 2.2×10^-24 |
| 0.5 | 1000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.971 | 1.000 |
| 1 | 200 | 0.477 | 0.288 | 0.196 | 0.198 | 0.445 | 0.444 | 0.439 | 0.124 | 1.4×10^-7 |
| 1 | 500 | 0.990 | 0.865 | 0.784 | 0.766 | 0.931 | 0.935 | 0.941 | 0.439 | 6.3×10^-73 |
| 1 | 1000 | 1.000 | 1.000 | 0.995 | 1.000 | 0.997 | 0.997 | 0.998 | 0.966 | 3.1×10^-5 |
| 2 | 200 | 0.093 | 0.080 | 0.053 | 0.048 | 0.083 | 0.083 | 0.093 | 0.104 | 0.005 |
| 2 | 500 | 0.578 | 0.329 | 0.266 | 0.212 | 0.441 | 0.442 | 0.479 | 0.397 | 1.5×10^-87 |
| 2 | 1000 | 1.000 | 0.953 | 0.915 | 0.857 | 0.870 | 0.882 | 0.900 | 0.962 | 2.1×10^-196 |
| 3 | 200 | 0.003 | 0.006 | 0.004 | 0.003 | 0.001 | 0.001 | 0.005 | 0.088 | 0.064 |
| 3 | 500 | 0.023 | 0.018 | 0.015 | 0.008 | 0.017 | 0.017 | 0.023 | 0.378 | 0.007 |
| 3 | 1000 | 0.656 | 0.279 | 0.328 | 0.127 | 0.376 | 0.378 | 0.456 | 0.954 | 4.1×10^-272 |
| 5 | 200 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.092 | 1.000 |
| 5 | 500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.497 | 1.000 |
| 5 | 1000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.986 | 1.000 |

*Fuentes: `e_equalized_audit13.json`, `b103_equalized_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_dgp2_audit13.tex` (sha256 `82820f35e76b9b476ce42e276bcfed9e9d97d40220c078d283fa4558904d06cc`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 1.9000 pp en `dgp2_delta3_n1000` (con signo 1.9000). Transcripción del v13 (`tab_dgp2_audit11.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:dgp3 — rechazos con quiebre de varianza (nula verdadera), con θ = 0.**

| r | n | RM-GLS | RM | ADF | PP | DF-GLS | MZ_t | MSB |
|---|---|---|---|---|---|---|---|---|
| 1 | 200 | 0.046 | 0.048 | 0.047 | **0.041** | 0.049 | 0.047 | 0.047 |
| 1.5 | 200 | **0.065** | **0.059** | **0.040** | **0.041** | **0.057** | **0.063** | **0.064** |
| 2 | 200 | **0.076** | **0.065** | **0.043** | **0.038** | **0.056** | **0.070** | **0.080** |
| 3 | 200 | **0.100** | **0.082** | 0.049 | **0.038** | **0.073** | **0.099** | **0.116** |
| 4 | 200 | **0.123** | **0.097** | 0.053 | 0.047 | **0.080** | **0.117** | **0.130** |
| 2 | 500 | **0.074** | **0.059** | **0.039** | **0.036** | **0.064** | **0.071** | **0.078** |
| 4 | 500 | **0.127** | **0.095** | 0.050 | 0.050 | **0.098** | **0.119** | **0.135** |
| 2 | 1000 | **0.072** | **0.061** | **0.036** | **0.037** | **0.064** | **0.067** | **0.074** |
| 4 | 1000 | **0.125** | **0.090** | 0.046 | 0.044 | **0.095** | **0.109** | **0.131** |

*Fuentes: `e_equalized_audit13.json`, `b103_equalized_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_dgp3_audit13.tex` (sha256 `50447ad976cf25c02d6dcce3fffeffcb78410b18e9033f1653556f7bd34d510f`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.5200 pp en `dgp3_r4_n200` (con signo -0.5200). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:misspec — tamaño con colas pesadas y GARCH, con θ = 0.**

| Innovations | n | RM-GLS | ADF-sim | ADF | PP | DF-GLS | MZ_t | MSB |
|---|---|---|---|---|---|---|---|---|
| t(5) | 200 | **0.0438** | 0.0528 | **0.0628** | **0.0584** | **0.0438** | 0.0440 | 0.0442 |
| t(5) | 500 | 0.0510 | 0.0522 | 0.0552 | **0.0614** | 0.0496 | 0.0504 | 0.0502 |
| t(5) | 1000 | 0.0486 | 0.0496 | 0.0500 | 0.0540 | 0.0466 | 0.0468 | 0.0488 |
| t(3) | 200 | **0.0428** | 0.0520 | **0.0624** | **0.0612** | **0.0414** | **0.0422** | 0.0446 |
| t(3) | 500 | 0.0502 | 0.0488 | 0.0528 | **0.0590** | 0.0520 | 0.0520 | 0.0498 |
| t(3) | 1000 | 0.0470 | 0.0524 | 0.0528 | **0.0600** | 0.0502 | 0.0496 | 0.0474 |
| G 0.95, N | 200 | 0.0500 | **0.0630** | **0.0724** | **0.0736** | **0.0430** | 0.0454 | **0.0432** |
| G 0.95, N | 500 | 0.0554 | **0.0576** | **0.0612** | **0.0610** | 0.0480 | 0.0516 | 0.0504 |
| G 0.95, N | 1000 | 0.0480 | 0.0490 | 0.0494 | 0.0520 | 0.0462 | 0.0470 | 0.0496 |
| G 0.98, N | 200 | **0.0606** | 0.0536 | **0.0648** | **0.0688** | 0.0556 | **0.0572** | **0.0606** |
| G 0.98, N | 500 | **0.0576** | **0.0622** | **0.0640** | **0.0708** | 0.0514 | 0.0550 | 0.0538 |
| G 0.98, N | 1000 | 0.0514 | **0.0640** | **0.0644** | **0.0654** | 0.0484 | 0.0504 | 0.0496 |
| G 0.99, N | 200 | **0.0602** | **0.0600** | **0.0730** | **0.0736** | **0.0616** | **0.0626** | **0.0622** |
| G 0.99, N | 500 | **0.0596** | **0.0584** | **0.0620** | **0.0672** | **0.0572** | **0.0580** | **0.0588** |
| G 0.99, N | 1000 | **0.0614** | **0.0642** | **0.0654** | **0.0696** | **0.0584** | **0.0598** | **0.0626** |
| G 0.99, N | 2000 | 0.0548 | 0.0544 | 0.0544 | **0.0578** | 0.0518 | 0.0530 | 0.0540 |
| G 0.99, N | 5000 | 0.0546 | 0.0546 | 0.0546 | 0.0556 | 0.0534 | 0.0538 | 0.0538 |
| G 0.95, t(5) | 200 | 0.0550 | **0.0724** | **0.0832** | **0.0784** | 0.0498 | 0.0526 | 0.0518 |
| G 0.95, t(5) | 500 | **0.0604** | **0.0644** | **0.0690** | **0.0702** | **0.0582** | **0.0596** | **0.0590** |
| G 0.95, t(5) | 1000 | **0.0576** | **0.0576** | **0.0580** | **0.0618** | 0.0528 | 0.0562 | **0.0566** |
| G 0.95, t(5) | 2000 | 0.0560 | 0.0502 | 0.0504 | **0.0564** | 0.0516 | 0.0538 | 0.0512 |
| G 0.95, t(5) | 5000 | 0.0534 | 0.0560 | **0.0566** | **0.0570** | 0.0512 | 0.0516 | 0.0496 |
| *Mean shift relative to Gaussian size, GARCH cells, percentage points (s.e.)* |  |  |  |  |  |  |  |  |
| n = 200 (4) |  | +0.63 (0.18) | +1.47 (0.19) | +1.61 (0.20) | +1.61 (0.20) | +0.28 (0.18) | +0.39 (0.18) | +0.42 (0.18) |
| n = 500 (4) |  | +1.12 (0.18) | +1.27 (0.18) | +1.20 (0.19) | +1.15 (0.19) | +0.84 (0.18) | +1.04 (0.18) | +0.82 (0.18) |
| n = 1000 (4) |  | +0.33 (0.18) | +0.85 (0.18) | +0.82 (0.18) | +0.78 (0.19) | +0.04 (0.17) | +0.21 (0.18) | +0.40 (0.18) |
| n = 2000 (2) |  | +0.84 (0.25) | +0.23 (0.25) | +0.24 (0.25) | +0.37 (0.26) | +0.36 (0.25) | +0.57 (0.25) | +0.59 (0.25) |
| n = 5000 (2) |  | +0.51 (0.25) | +0.29 (0.25) | +0.29 (0.25) | +0.22 (0.26) | +0.18 (0.25) | +0.24 (0.25) | +0.30 (0.25) |

*Fuentes: `b92_theta_audit9.json`. Tabular: `experiments/results/tables_audit13/tab_misspec_audit13.tex` (sha256 `4c3f8474263c0243cc663446931ce3d79ac3810ec443d9839d96b11bd3ec1dcf`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.1400 pp en `c|garch_base_n1000` (con signo -0.1400). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Tabla tab:critB — valores críticos de cola inferior, con θ = 0.**

| n | Constant 0.01 | Constant 0.025 | Constant 0.05 | Constant 0.10 | Trend 0.01 | Trend 0.025 | Trend 0.05 | Trend 0.10 |
|---|---|---|---|---|---|---|---|---|
| 100 | 0.1907 | 0.2111 | 0.2321 | 0.2623 | 0.1569 | 0.1676 | 0.1782 | 0.1925 |
| 200 | 0.1868 | 0.2089 | 0.2328 | 0.2678 | 0.1498 | 0.1621 | 0.1739 | 0.1898 |
| 500 | 0.1863 | 0.2102 | 0.2352 | 0.2727 | 0.1461 | 0.1592 | 0.1719 | 0.1892 |
| 1000 | 0.1859 | 0.2109 | 0.2362 | 0.2736 | 0.1452 | 0.1582 | 0.1713 | 0.1891 |
| 2000 | 0.1863 | 0.2103 | 0.2374 | 0.2760 | 0.1440 | 0.1581 | 0.1717 | 0.1893 |
| 5000 | 0.1844 | 0.2087 | 0.2361 | 0.2753 | 0.1451 | 0.1580 | 0.1709 | 0.1886 |

*Fuentes: `b103_cv_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_critB_audit13.tex` (sha256 `55d2a2727db124002a31f4148eb7cc21b7b5d8fbbd49d73e4672ab1003b470af`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.0153 unidades del estadistico en `ct|100|0.01` (con signo 0.0153). Transcripción del v13 (`appB_critical_values.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

Notas de tab:calib: q(20 000) = 0.2370 (constante) y 0.1714 (tendencia) con θ = 0; con θ = 0.02, 0.2297 y 0.1624. KS frente a n = 20 000 con θ = 0 (umbral 0.0136), caso constante: n = 60: D 0.2210; n = 100: D 0.1598; n = 200: D 0.0963; n = 500: D 0.0436; n = 1000: D 0.0153; n = 2000: D 0.0163; n = 5000: D 0.0146; tendencia: n = 60: D 0.1470; n = 100: D 0.1109; n = 200: D 0.0625; n = 500: D 0.0250; n = 1000: D 0.0137; n = 2000: D 0.0097; n = 5000: D 0.0071.

Desplazamiento medio GARCH de RM-GLS (pp, EE): n = 200: θ = 0 +0.63 (0.18), θ = 0.02 +0.63 (0.18), 4 celdas; n = 500: θ = 0 +1.12 (0.18), θ = 0.02 +1.10 (0.18), 4 celdas; n = 1000: θ = 0 +0.33 (0.18), θ = 0.02 +0.36 (0.18), 4 celdas; n = 2000: θ = 0 +0.84 (0.25), θ = 0.02 +0.92 (0.25), 2 celdas; n = 5000: θ = 0 +0.51 (0.25), θ = 0.02 +0.48 (0.25), 2 celdas.

tab:critB: EE bootstrap máximo de los cuantiles: θ = 0 0.0008; θ = 0.02 0.0008.

### B13.E(2) — AWB, DGP 5 y aplicación con θ = 0

**AWB (familia 142).** Presupuesto: 8.0 h; sonda (s/serie): n = 200: 0.6791, n = 500: 0.0062; proyección 3.79 h → se lanza. Estadístico gls_t0; B = 399; dY - media(dY), retardo 0; semilla SeedSequence(142, spawn_key = (awb_<celda>, i)); columna simulada: A10, N_cal = 500000.

**Tabla tab:awb — calibración AWB frente a la simulada, con θ = 0.**

| Design | n | AWB | Simulated | McNemar p | Power loss (pp) |
|---|---|---|---|---|---|
| Random walk, r = 1 | 200 | **0.040** | 0.042 | 0.289 |  |
| Random walk, r = 1 | 500 | 0.042 | 0.052 | <0.001 |  |
| Random walk, r = 2 | 200 | 0.052 | **0.080** | <0.001 |  |
| Random walk, r = 2 | 500 | 0.051 | **0.089** | <0.001 |  |
| Random walk, r = 4 | 200 | 0.041 | **0.118** | <0.001 |  |
| Random walk, r = 4 | 500 | **0.040** | **0.117** | <0.001 |  |
| GARCH 0.95, normal | 200 | 0.042 | 0.051 | 0.002 |  |
| GARCH 0.98, normal | 200 | 0.053 | 0.060 | 0.003 |  |
| GARCH 0.99, normal | 200 | 0.052 | **0.061** | 0.006 |  |
| GARCH 0.95, t(5) | 200 | 0.043 | 0.052 | <0.001 |  |
| Gaussian random walk | 200 | 0.053 | 0.054 | 0.839 |  |
| Gaussian random walk | 500 | 0.045 | 0.047 | 0.359 |  |
| AR(0.95) | 200 | 0.677 | 0.706 | <0.001 | 2.9 |
| AR(0.95) | 500 | 1.000 | 1.000 | 1.000 | 0.0 |
| AR(0.99) | 200 | 0.098 | 0.102 | 0.332 | 0.4 |
| AR(0.99) | 500 | 0.295 | 0.313 | <0.001 | 1.8 |

*Fuentes: `e_awb_audit13.json`, `b103_awb_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_awb_audit13.tex` (sha256 `2953b2372b26706d6f7e0499c71aa792ce712595b4cbdd47b9675d824efe7452`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.9500 pp en `dgp1_rho0p95_n200|awb` (con signo 0.9500). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

Regla B9.5 (informativa): (i) 4 de 6 celdas de DGP 3 dentro (mínimo 4): sí; (ii) pérdida de potencia dgp1_rho0p95_n200 2.90, dgp1_rho0p95_n500 0.00, dgp1_rho0p99_n200 0.40, dgp1_rho0p99_n500 1.80 pp (umbral 3.0): sí. Recomendar AWB: sí.

**DGP 5.** Trayectorias: A7 (familia 60), regeneradas con sus semillas; umbral igualado de RM-GLS θ = 0: -0.2324 (θ = 0.02: -0.2235); celda de calibración `cal_rw_n200`; N = 2000, B = 399.

**Tabla tab:dgp5 — experimento pre-registrado de dos canales, con θ = 0.**

| ρ | r | RM-GLS | Two-channel | Union | Bootstrap DF-GLS | g_2 share |
|---|---|---|---|---|---|---|
| 0.93 | 1 | 0.914 | 0.658 | 0.807 | 0.924 | 0.48% |
| 0.93 | 1.25 | 0.905 | 0.658 | 0.856 | 0.906 | 0.54% |
| 0.93 | 1.5 | 0.916 | 0.685 | 0.970 | 0.889 | 0.65% |
| 0.93 | 2† | 0.913 | 0.677 | 0.999 | 0.850 | 0.96% |
| 0.93 | 3† | 0.894 | 0.697 | 1.000 | 0.768 | 1.38% |
| 0.93 | 4 | 0.881 | 0.687 | 1.000 | 0.704 | 1.65% |
| 0.95 | 1 | 0.702 | 0.449 | 0.540 | 0.730 | 0.43% |
| 0.95 | 1.25 | 0.721 | 0.438 | 0.684 | 0.707 | 0.47% |
| 0.95 | 1.5 | 0.713 | 0.427 | 0.926 | 0.685 | 0.53% |
| 0.95 | 2† | 0.734 | 0.498 | 0.999 | 0.639 | 0.79% |
| 0.95 | 3† | 0.721 | 0.470 | 1.000 | 0.523 | 1.14% |
| 0.95 | 4 | 0.723 | 0.496 | 1.000 | 0.501 | 1.38% |

*Fuentes: `e_dgp5_audit13.json`, `b103_dgp5_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_dgp5_audit13.tex` (sha256 `cbfd0696261fecf92a3d2f6f04ee468324b6edab60d5cb93c802a3f7325e503d`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 0.8000 pp en `dgp5_n200_rho0.95_r1.0` (con signo 0.8000). Transcripción del v13 (`sec5_montecarlo.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

**Aplicación (familia 143).** Hashes de los datos congelados: SP500 coincide, FTSE coincide, NIKKEI coincide, DAX coincide; `experiments/protocol.md`: coincide. Nula: build_null_cdf de produccion (semilla 42, N_cal = 50000, tau_mode = zero).

**Tabla tab:fp — aplicación pre-registrada, con θ = 0.**

| Test | Nominal level FP mean | Nominal level FP max | Nominal level Detections | Nominal level Latency | Common rate Episodes | Common rate Run | Common rate Latency^c |
|---|---|---|---|---|---|---|---|
| RM-GLS | 0.0224 | 0.216 | 17 | 29.7 | 33 | 144.8 | 102.6 |
| RM-GLS, AWB | 0.0217 | 0.229 | 13 | 40.3 | 43 | 129.2 | 108.2 |
| Registered statistic | 0.0277 | 0.437 | 13 | 33.8 | 11 | 199.7 | 109.3 |
| ADF | 0.0535 | 0.269 | 26 | 33.7 | 48 | 122.2 | 107.4 |
| PP | 0.0532 | 0.380 | 23 | 33.4 | 56 | 112.9 | 109.4 |
| DF-GLS (AIC) | 0.0323 | 0.269 | 28 | 30.6 | 32 | 146.8 | 93.6 |
| DF-GLS (MAIC) | 0.0210 | 0.273 | 23 | 33.8 | 35 | 141.3 | 96.8 |
| MZ_t-GLS | 0.0173 | 0.237 | 36 | 22.1 | 36 | 139.7 | 79.7 |
| KPSSᵃ | 0.9354 | 1.000 | 87 | 1.2 | -- | -- | -- |

*Fuentes: `e_application_audit13.json`, `b103_application_audit10.json`. Tabular: `experiments/results/tables_audit13/tab_fp_audit13.tex` (sha256 `b76b26cd4e462328e66c46a12fa0790c23f606a67dec9f5551d0f16e45364e89`). Compuerta informativa: máx. |θ = 0 − θ = 0.02| = 7.5077 FP: pp; detecciones y episodios: numero; latencias: dias en `final_awb|latency` (con signo 7.5077). Transcripción del v13 (`sec6_application.tex`): reproduce. Negrita: fuera de la región exacta de la N de la celda.*

Tamaño fuera de muestra (N = 5000, región [0.044, 0.0562]):

| D | RM-GLS θ = 0 | RM-GLS θ = 0.02 (v13) | RM-GLS θ = 0, AWB |
|---|---|---|---|
| 150 | 0.0472 | 0.0468 | 0.0460 |
| 200 | 0.0482 | 0.0478 | 0.0452 |
| 250 | 0.0468 | 0.0478 | 0.0432 (fuera) |
| 300 | 0.0482 | 0.0490 | 0.0488 |

Tasa común (mecanismo registrado): objetivo 0.0222 (FP agregada de RM-GLS θ = 0). Informativo, al objetivo del v13 (0.0227): final: 35 episodios, latencia censurada 101.7; final_awb: 43 episodios, latencia censurada 108.2; v13: 33 episodios, latencia censurada 102.5; v13_awb: 41 episodios, latencia censurada 105.1; primary_rmgls: 38 episodios, latencia censurada 103.4; rhat_prereg: 11 episodios, latencia censurada 109.3; adf: 49 episodios, latencia censurada 107.4; pp: 55 episodios, latencia censurada 109.4; dfgls_aic: 33 episodios, latencia censurada 93.6; dfgls_maic: 35 episodios, latencia censurada 96.8; mzt: 38 episodios, latencia censurada 79.7.

Celdas adversas bajo la regla registrada: θ = 0 7; θ = 0.02 7.

Filas para tab:deviations:

| Id | Elemento | Antes | Después | Efecto antes | Efecto después |
|---|---|---|---|---|---|
| xvi | theta del estadistico primario (B13.E, confirmado por el autor) | 0.02 (primaria de A10-A12) | 0 | FP 0.0229 (máx. 0.2122); 17 detecciones; latencia 29.6 | FP 0.0224 (máx. 0.2163); 17 detecciones; latencia 29.7 |
| xvii | calibracion AWB con theta = 0 | nula hac simulada | AWB del propio estadistico (B = 399) | FP 0.0224 (máx. 0.2163); 17 detecciones; latencia 29.7 | FP 0.0217 (máx. 0.2286); 13 detecciones; latencia 40.3 |
| statistic | estadistico registrado frente a RM-GLS theta = 0 | R-hat registrado | RM-GLS theta = 0 | FP 0.0277 (máx. 0.4367); 13 detecciones; latencia 33.8 | FP 0.0224 (máx. 0.2163); 17 detecciones; latencia 29.7 |

### B13.E(3) — Figuras `_audit13`

| Figura | sha256 | Bytes | Copia | sha256 de datos | Paso 0 |
|---|---|---|---|---|---|
| fig_local_power_audit13.pdf | `7a4c78c66e8fbed74d5bc5a34d888282501d91ffe960072b0c3d20b94b70489d` | 19963 | paper/figures/fig_local_power_audit13.pdf | `40341b6fdb0167f89ce24f810a26148abac3370263ab742bc1d7e4c576769073` | idéntica a A11 |
| fig_theta_ladder_audit13.pdf | `4ceb42115502f2c3318637b6cfe59eb2cce1d8c58802598c50ae72fac84f0b9e` | 13228 | paper/figures/fig_theta_ladder_audit13.pdf | `9ad255ec09d049acdc2e7d7cc92dfab9de18f0956097d2c78a565912a32327b6` | idéntica a A11 |
| fig_power_equalized_audit13.pdf | `254d762be3f7f2412e8f6ab1a0d05f74b88538cd64808684ce3e968ec5d4a7ff` | 28265 | paper/figures/fig_power_equalized_audit13.pdf | `788e60968a0aad9af1f00a2f0eba478c6354204121f1fa6f03aa72b3aa4700cc` | idéntica a A11 |
| fig_size_shift_audit13.pdf | `a128a601ad2f6c0fbb174daf81f2b2d48733bd6c1468b257269a36367eff6c11` | 19867 | paper/figures/fig_size_shift_audit13.pdf | `e3e5bbe00f37b8503b2cbaaf27cb99dcb95c6b016948d3860a8162c8b7c9cd2c` | idéntica a A11 |
| fig_dgp3_audit13.pdf | `2048a77850ec3eb3785a314177ae0274db452d5807dcb80a47d12974b216669f` | 18777 | paper/figures/fig_dgp3_audit13.pdf | `3ac8236f904d2cfb410a81f41255e21f8cd20d18d91e6682aea3fb1b3cd57e1b` | idéntica a A11 |
| fig_calibration_gain_audit13.pdf | `39b3d33229372bf1e5110f42a5921eb2c8a772d1c33f66b7cdd3663e0ff9508f` | 16656 | paper/figures/fig_calibration_gain_audit13.pdf | `84927e0e54d353d41428e46d6c791b191c7cd08d501fde66ee281edb597cef7d` | idéntica a A11 |

*Fuentes que dependen de θ: `e_equalized_audit13.json`, `e_awb_audit13.json`, `e_size_audit13.json`, `e_calib_audit13.json`, `b101_theta_audit10.json`, `b92_theta_audit9.json`; sin dependencia de θ: `b3_comparators_audit8.json`, `b5_power_audit8.json`, `b103_lown_audit10.json`. Puntos de la figura de ganancia de calibración en `figures_audit13.json` (`calibration_gain_points`).*

### B13.T — Tablas nuevas desde JSON de A12

**tab:serial — tamaño al valor crítico iid por estructura de error.** Negrita: fuera de la región exacta [0.047, 0.05305] (N = 20 000).

| Error | n | Caso | RM-GLS θ=0 | (b) s²_AR MAIC-GLS | (b′) s²_AR MAIC-MCO | MSB-GLS NP | MZ_t-GLS NP | DF-GLS MAIC-GLS | ADF (AIC) | PP | Factor Bartlett (B) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MA ψ = -0.8 | 100 | constante | **0.336** | **0.042** | **0.073** | **0.041** | **0.046** | **0.099** | **0.426** | **0.997** | 6.00 (B = 7) |
| MA ψ = -0.8 | 100 | tendencia | **0.047** | **0.098** | **0.168** | **0.097** | **0.101** | **0.142** | **0.679** | **1.000** | 6.00 (B = 7) |
| MA ψ = -0.8 | 200 | constante | **0.420** | **0.026** | **0.031** | **0.025** | **0.030** | **0.090** | **0.247** | **0.994** | 5.44 (B = 8) |
| MA ψ = -0.8 | 200 | tendencia | **0.361** | **0.032** | 0.047 | **0.032** | **0.035** | **0.089** | **0.415** | **1.000** | 5.44 (B = 8) |
| MA ψ = -0.8 | 500 | constante | **0.397** | **0.033** | **0.032** | **0.033** | **0.038** | **0.085** | **0.132** | **0.985** | 4.33 (B = 11) |
| MA ψ = -0.8 | 500 | tendencia | **0.570** | **0.013** | **0.016** | **0.013** | **0.015** | **0.080** | **0.210** | **1.000** | 4.33 (B = 11) |
| MA ψ = -0.5 | 100 | constante | **0.079** | **0.054** | **0.059** | **0.053** | **0.058** | **0.067** | **0.112** | **0.575** | 1.57 (B = 6) |
| MA ψ = -0.5 | 100 | tendencia | **0.026** | **0.070** | **0.083** | **0.069** | **0.072** | **0.074** | **0.184** | **0.854** | 1.57 (B = 6) |
| MA ψ = -0.5 | 200 | constante | **0.096** | **0.058** | **0.057** | **0.057** | **0.061** | **0.065** | **0.085** | **0.517** | 1.50 (B = 7) |
| MA ψ = -0.5 | 200 | tendencia | **0.071** | **0.058** | **0.063** | **0.057** | **0.059** | **0.064** | **0.116** | **0.816** | 1.50 (B = 7) |
| MA ψ = -0.5 | 500 | constante | **0.090** | **0.056** | **0.055** | **0.055** | **0.058** | **0.060** | **0.066** | **0.402** | 1.40 (B = 9) |
| MA ψ = -0.5 | 500 | tendencia | **0.097** | **0.057** | **0.057** | **0.057** | **0.056** | **0.059** | **0.078** | **0.709** | 1.40 (B = 9) |
| MA ψ = 0 | 100 | constante | 0.052 | 0.052 | 0.052 | 0.051 | **0.053** | 0.053 | 0.052 | 0.051 | 1.00 (B = 2) |
| MA ψ = 0 | 100 | tendencia | 0.049 | 0.048 | 0.048 | 0.047 | 0.048 | 0.047 | 0.050 | 0.050 | 1.00 (B = 2) |
| MA ψ = 0 | 200 | constante | 0.050 | 0.050 | 0.050 | 0.050 | 0.050 | 0.050 | 0.048 | 0.049 | 1.00 (B = 2) |
| MA ψ = 0 | 200 | tendencia | 0.048 | **0.046** | **0.046** | **0.046** | **0.046** | **0.046** | 0.050 | 0.049 | 1.00 (B = 2) |
| MA ψ = 0 | 500 | constante | 0.050 | 0.050 | 0.049 | 0.050 | 0.049 | 0.049 | 0.051 | 0.051 | 1.00 (B = 2) |
| MA ψ = 0 | 500 | tendencia | 0.052 | 0.052 | 0.052 | 0.052 | 0.053 | 0.052 | 0.051 | 0.051 | 1.00 (B = 2) |
| MA ψ = 0.5 | 100 | constante | **0.027** | **0.063** | **0.061** | **0.063** | **0.063** | **0.043** | **0.056** | **0.024** | 0.93 (B = 5) |
| MA ψ = 0.5 | 100 | tendencia | **0.011** | **0.086** | **0.078** | **0.086** | **0.084** | **0.036** | **0.063** | **0.009** | 0.93 (B = 5) |
| MA ψ = 0.5 | 200 | constante | **0.032** | 0.053 | 0.051 | **0.053** | 0.052 | **0.043** | 0.050 | **0.024** | 0.94 (B = 7) |
| MA ψ = 0.5 | 200 | tendencia | **0.019** | **0.063** | **0.060** | **0.064** | **0.062** | **0.036** | 0.052 | **0.009** | 0.94 (B = 7) |
| MA ψ = 0.5 | 500 | constante | **0.040** | **0.056** | **0.055** | **0.056** | **0.053** | 0.049 | 0.050 | **0.033** | 0.96 (B = 9) |
| MA ψ = 0.5 | 500 | tendencia | **0.029** | **0.058** | **0.056** | **0.058** | **0.056** | **0.045** | 0.050 | **0.018** | 0.96 (B = 9) |
| AR φ = -0.5 | 100 | constante | **0.035** | **0.041** | **0.041** | **0.041** | **0.040** | **0.045** | 0.050 | **0.375** | 1.17 (B = 7) |
| AR φ = -0.5 | 100 | tendencia | **0.005** | **0.033** | **0.033** | **0.034** | **0.034** | **0.044** | **0.053** | **0.645** | 1.17 (B = 7) |
| AR φ = -0.5 | 200 | constante | **0.043** | **0.042** | **0.042** | **0.042** | **0.043** | **0.046** | 0.048 | **0.308** | 1.13 (B = 9) |
| AR φ = -0.5 | 200 | tendencia | **0.021** | **0.038** | **0.039** | **0.038** | **0.040** | **0.047** | **0.047** | **0.562** | 1.13 (B = 9) |
| AR φ = -0.5 | 500 | constante | **0.054** | 0.048 | 0.048 | 0.048 | 0.047 | 0.049 | 0.052 | **0.227** | 1.11 (B = 11) |
| AR φ = -0.5 | 500 | tendencia | **0.042** | **0.044** | **0.044** | **0.044** | **0.045** | 0.049 | 0.047 | **0.420** | 1.11 (B = 11) |
| AR φ = 0.5 | 100 | constante | **0.017** | **0.070** | **0.068** | **0.071** | **0.067** | 0.048 | 0.053 | **0.022** | 0.83 (B = 7) |
| AR φ = 0.5 | 100 | tendencia | **0.004** | **0.096** | **0.092** | **0.097** | **0.092** | **0.044** | 0.049 | **0.007** | 0.83 (B = 7) |
| AR φ = 0.5 | 200 | constante | **0.026** | **0.059** | **0.058** | **0.058** | **0.060** | 0.052 | 0.051 | **0.022** | 0.85 (B = 8) |
| AR φ = 0.5 | 200 | tendencia | **0.010** | **0.073** | **0.073** | **0.074** | **0.073** | 0.050 | 0.050 | **0.006** | 0.85 (B = 8) |
| AR φ = 0.5 | 500 | constante | **0.031** | **0.055** | **0.055** | **0.054** | 0.052 | 0.049 | 0.049 | **0.027** | 0.89 (B = 11) |
| AR φ = 0.5 | 500 | tendencia | **0.021** | **0.060** | **0.061** | **0.060** | **0.060** | 0.053 | 0.051 | **0.012** | 0.89 (B = 11) |

*Fuente: `bA_ma_audit12.json` (`size.<celda>.iid`, `bartlett_factor_at_median_B`). Tabular: `experiments/results/tables_audit13/tab_serial_audit13.tex` (sha256 `cd6a1d7ade12ea0784c217dada4aa82b92c37a7ba66bafeecaceb1ae8d9ad66b`).*

**tab:serialpower — potencia ajustada al tamaño en las mismas celdas.**

| Error | n | Caso | ρ | RM-GLS θ=0 | (b) s²_AR MAIC-GLS | (b′) s²_AR MAIC-MCO | MSB-GLS NP | MZ_t-GLS NP | DF-GLS MAIC-GLS | ADF (AIC) | PP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MA ψ = -0.8 | 100 | constante | 0.930 | 0.296 | 0.294 | 0.273 | 0.293 | 0.291 | 0.331 | 0.226 | 0.164 |
| MA ψ = -0.8 | 100 | tendencia | 0.865 | 0.145 | 0.308 | 0.312 | 0.308 | 0.308 | 0.322 | 0.252 | 0.231 |
| MA ψ = -0.8 | 200 | constante | 0.965 | 0.407 | 0.295 | 0.294 | 0.293 | 0.303 | 0.382 | 0.229 | 0.215 |
| MA ψ = -0.8 | 200 | tendencia | 0.932 | 0.289 | 0.270 | 0.281 | 0.269 | 0.272 | 0.307 | 0.307 | 0.137 |
| MA ψ = -0.8 | 500 | constante | 0.986 | 0.468 | 0.373 | 0.379 | 0.372 | 0.389 | 0.437 | 0.242 | 0.320 |
| MA ψ = -0.8 | 500 | tendencia | 0.973 | 0.463 | 0.312 | 0.316 | 0.312 | 0.317 | 0.398 | 0.295 | 0.293 |
| MA ψ = -0.5 | 100 | constante | 0.930 | 0.435 | 0.327 | 0.344 | 0.324 | 0.345 | 0.369 | 0.223 | 0.297 |
| MA ψ = -0.5 | 100 | tendencia | 0.865 | 0.292 | 0.285 | 0.305 | 0.284 | 0.290 | 0.309 | 0.275 | 0.330 |
| MA ψ = -0.5 | 200 | constante | 0.965 | 0.441 | 0.375 | 0.385 | 0.373 | 0.396 | 0.408 | 0.206 | 0.337 |
| MA ψ = -0.5 | 200 | tendencia | 0.932 | 0.426 | 0.351 | 0.358 | 0.349 | 0.354 | 0.372 | 0.281 | 0.379 |
| MA ψ = -0.5 | 500 | constante | 0.986 | 0.483 | 0.453 | 0.455 | 0.452 | 0.467 | 0.471 | 0.205 | 0.337 |
| MA ψ = -0.5 | 500 | tendencia | 0.973 | 0.482 | 0.419 | 0.422 | 0.420 | 0.431 | 0.432 | 0.292 | 0.425 |
| MA ψ = 0 | 100 | constante | 0.930 | 0.441 | 0.404 | 0.413 | 0.397 | 0.425 | 0.441 | 0.161 | 0.157 |
| MA ψ = 0 | 100 | tendencia | 0.865 | 0.459 | 0.434 | 0.453 | 0.429 | 0.446 | 0.446 | 0.263 | 0.293 |
| MA ψ = 0 | 200 | constante | 0.965 | 0.461 | 0.442 | 0.444 | 0.438 | 0.476 | 0.476 | 0.174 | 0.183 |
| MA ψ = 0 | 200 | tendencia | 0.932 | 0.499 | 0.468 | 0.483 | 0.469 | 0.477 | 0.469 | 0.271 | 0.302 |
| MA ψ = 0 | 500 | constante | 0.986 | 0.465 | 0.459 | 0.464 | 0.456 | 0.495 | 0.494 | 0.177 | 0.187 |
| MA ψ = 0 | 500 | tendencia | 0.973 | 0.487 | 0.465 | 0.467 | 0.463 | 0.465 | 0.458 | 0.295 | 0.307 |
| MA ψ = 0.5 | 100 | constante | 0.930 | 0.438 | 0.329 | 0.349 | 0.323 | 0.361 | 0.398 | 0.168 | 0.033 |
| MA ψ = 0.5 | 100 | tendencia | 0.865 | 0.423 | 0.238 | 0.251 | 0.235 | 0.245 | 0.288 | 0.193 | 0.084 |
| MA ψ = 0.5 | 200 | constante | 0.965 | 0.473 | 0.413 | 0.423 | 0.412 | 0.447 | 0.453 | 0.173 | 0.093 |
| MA ψ = 0.5 | 200 | tendencia | 0.932 | 0.432 | 0.344 | 0.365 | 0.341 | 0.362 | 0.379 | 0.231 | 0.163 |
| MA ψ = 0.5 | 500 | constante | 0.986 | 0.465 | 0.433 | 0.433 | 0.434 | 0.467 | 0.471 | 0.168 | 0.130 |
| MA ψ = 0.5 | 500 | tendencia | 0.973 | 0.466 | 0.425 | 0.433 | 0.424 | 0.442 | 0.447 | 0.268 | 0.222 |
| AR φ = -0.5 | 100 | constante | 0.930 | 0.408 | 0.389 | 0.391 | 0.380 | 0.423 | 0.436 | 0.172 | 0.319 |
| AR φ = -0.5 | 100 | tendencia | 0.865 | 0.273 | 0.369 | 0.391 | 0.366 | 0.376 | 0.404 | 0.232 | 0.356 |
| AR φ = -0.5 | 200 | constante | 0.965 | 0.462 | 0.448 | 0.453 | 0.446 | 0.477 | 0.484 | 0.184 | 0.328 |
| AR φ = -0.5 | 200 | tendencia | 0.932 | 0.404 | 0.421 | 0.434 | 0.418 | 0.427 | 0.439 | 0.288 | 0.411 |
| AR φ = -0.5 | 500 | constante | 0.986 | 0.467 | 0.466 | 0.471 | 0.464 | 0.486 | 0.489 | 0.165 | 0.308 |
| AR φ = -0.5 | 500 | tendencia | 0.973 | 0.464 | 0.467 | 0.466 | 0.466 | 0.478 | 0.476 | 0.293 | 0.412 |
| AR φ = 0.5 | 100 | constante | 0.930 | 0.413 | 0.323 | 0.339 | 0.317 | 0.353 | 0.388 | 0.150 | 0.012 |
| AR φ = 0.5 | 100 | tendencia | 0.865 | 0.400 | 0.255 | 0.266 | 0.252 | 0.268 | 0.305 | 0.192 | 0.031 |
| AR φ = 0.5 | 200 | constante | 0.965 | 0.417 | 0.392 | 0.403 | 0.388 | 0.417 | 0.425 | 0.155 | 0.053 |
| AR φ = 0.5 | 200 | tendencia | 0.932 | 0.419 | 0.370 | 0.380 | 0.369 | 0.379 | 0.397 | 0.241 | 0.093 |
| AR φ = 0.5 | 500 | constante | 0.986 | 0.464 | 0.446 | 0.452 | 0.442 | 0.483 | 0.489 | 0.182 | 0.111 |
| AR φ = 0.5 | 500 | tendencia | 0.973 | 0.449 | 0.448 | 0.448 | 0.446 | 0.453 | 0.449 | 0.281 | 0.196 |

*Fuente: `bA_ma_audit12.json` (`power.pw_*.adjusted`). Tabular: `experiments/results/tables_audit13/tab_serialpower_audit13.tex` (sha256 `89c7c311f5e3b04a7ee9492ca8cb7ed1589e5ee4a27541279f04d91104439db7`).*

**tab:initial — condición inicial (B12.C completa).** u₀ = α/√(1−ρ²); «aleatoria»: z₀/√(1−ρ²).

| ρ | u₀ | RM-GLS θ=0 | RM-GLS θ=0.02 | (b) s²_AR MAIC-GLS | (b′) s²_AR MAIC-MCO | DF-GLS MAIC-GLS | MZ_t-GLS NP | MSB-GLS NP | ADF (AIC) | PP | RM-GLS θ=0 − DF-GLS (pp, EE) | McNemar p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.900 | α = 0 | 0.994 | 0.994 | 0.923 | 0.936 | 0.928 | 0.929 | 0.922 | 0.796 | 0.847 | +6.62 (0.37) | 5.4e-80 |
| 0.900 | α = 1 | 0.818 | 0.813 | 0.613 | 0.714 | 0.643 | 0.639 | 0.606 | 0.813 | 0.856 | +17.46 (0.71) | 7.3e-127 |
| 0.900 | α = 2 | 0.044 | 0.043 | 0.038 | 0.058 | 0.046 | 0.039 | 0.037 | 0.855 | 0.888 | -0.16 (0.32) | 0.66 |
| 0.900 | α = 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.958 | 0.977 | +0.00 (0.00) | 1 |
| 0.900 | aleatoria | 0.778 | 0.775 | 0.653 | 0.703 | 0.678 | 0.675 | 0.650 | 0.814 | 0.859 | +10.02 (0.57) | 8.8e-70 |
| 0.950 | α = 0 | 0.711 | 0.705 | 0.663 | 0.672 | 0.701 | 0.699 | 0.658 | 0.304 | 0.321 | +1.02 (0.58) | 0.085 |
| 0.950 | α = 1 | 0.292 | 0.289 | 0.266 | 0.279 | 0.286 | 0.279 | 0.262 | 0.318 | 0.334 | +0.66 (0.57) | 0.26 |
| 0.950 | α = 2 | 0.007 | 0.006 | 0.007 | 0.007 | 0.007 | 0.007 | 0.008 | 0.373 | 0.378 | -0.08 (0.10) | 0.54 |
| 0.950 | α = 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.625 | 0.645 | +0.00 (0.00) | 1 |
| 0.950 | aleatoria | 0.434 | 0.429 | 0.399 | 0.413 | 0.432 | 0.429 | 0.396 | 0.316 | 0.337 | +0.18 (0.54) | 0.77 |
| 0.970 | α = 0 | 0.378 | 0.374 | 0.356 | 0.363 | 0.382 | 0.379 | 0.353 | 0.149 | 0.157 | -0.40 (0.55) | 0.49 |
| 0.970 | α = 1 | 0.152 | 0.151 | 0.147 | 0.148 | 0.158 | 0.158 | 0.146 | 0.156 | 0.153 | -0.60 (0.40) | 0.14 |
| 0.970 | α = 2 | 0.009 | 0.009 | 0.008 | 0.009 | 0.009 | 0.008 | 0.008 | 0.180 | 0.182 | -0.02 (0.13) | 1 |
| 0.970 | α = 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.351 | 0.371 | +0.00 (0.00) | 1 |
| 0.970 | aleatoria | 0.221 | 0.219 | 0.212 | 0.211 | 0.228 | 0.225 | 0.210 | 0.157 | 0.157 | -0.64 (0.46) | 0.17 |

*Fuente: `bC_initial_audit12.json` (`cells`); N = 5000 por celda; valores críticos iid de n = 200. Tabular: `experiments/results/tables_audit13/tab_initial_audit13.tex` (sha256 `4dcfc29ddf0bd2b42164cd0075a19a909c4505b8b51524c9b04fd1c58bcee695`).*

### Cifras del texto del v13 que dependen de θ

Cada cifra se recalcula desde JSON con las fuentes del v13 (θ = 0.02) y con las de A13 (θ = 0). No se reescribe ninguna frase.

| Clave | Archivo:línea | Impreso | θ = 0.02 recalculado | ¿Reproduce? | θ = 0 | Datos adicionales (θ = 0) |
|---|---|---|---|---|---|---|
| size_max | `v13/sec5_montecarlo.tex:23` | 0.24, 150, 0.0476 | 0.2360, 150, 0.0476 | sí | 0.2360, 100, 0.0524 | cell: ct\|100; all_within_A1prime_tolerance: sí; outside_exact_region: [ct\|100] |
| calib_limit | `v13/sec5_montecarlo.tex:63` | 0.0785, 0.0638, 0.0574, 0.0541, 0.0517, 0.0510 | 0.0785, 0.0638, 0.0574, 0.0541, 0.0517, 0.0510 | sí | 0.0607, 0.0588, 0.0556, 0.0544, 0.0516, 0.0514 | — |
| calib_ks | `v13/sec5_montecarlo.tex:70` | 0.097, 0.016 | 0.0973, 0.0157 | sí | 0.0963, 0.0153 | below_threshold_c: {60: no, 100: no, 200: no, 500: no, 1000: no, 2000: no, 5000: no}; below_threshold_ct: {60: no, 100: no, 200: no, 500: no, 1000: no, 2000: sí, 5000: sí} |
| calib_trend | `v13/sec5_montecarlo.tex:70` | — | — | sí | — | trend_size_with_cv_n20000: {60: 0.0199, 100: 0.0323, 150: 0.0412, 200: 0.0413, 500: 0.0472, 1000: 0.0508, 2000: 0.0486, 5000: 0.0510}; trend_outside_exact_region: [60, 100, 150, 200]; cv_n20000: {c: 0.2370, ct: 0.1714} |
| intro_limit | `v13/sec1_introduction.tex:56` | 0.0574, 0.0510 | 0.0574, 0.0510 | sí | 0.0556, 0.0514 | — |
| abstract_limit | `v13/main.tex:88` | 0.057 | 0.0574 | sí | 0.0556 | — |
| lp_gap | `v13/sec5_montecarlo.tex:143` | 2.3, 3.5, 1.0 | 2.2900, 3.4900, 0.9650 | sí | 1.8350, 2.6200, 0.6850 | msb_gap: [2.3050, 3.0700, 1.0000]; primary_minus_msb_pp: [0.4700, 0.4500, 0.3150] |
| lp_trend | `v13/sec5_montecarlo.tex:147` | 1.4 | 1.4000 | sí | 1.2250 | c_values: [2.0000, 5.0000, 7.0000, 10.0000, 13.5000, 15.0000, 20.0000] |
| lp_theta | `v13/sec5_montecarlo.tex:148` | 0.3, 0.9 | 0.2800, 0.8700 | sí | 0.2800, 0.8700 | c_values: [5.0000, 7.0000, 10.0000, 13.5000, 15.0000]; theta0_minus_theta002_pp: [0.4550, 0.5550, 0.8700, 0.4150, 0.2800] |
| intro_lp | `v13/sec1_introduction.tex:76` | 3.5 | 3.4900 | sí | 2.6200 | — |
| abstract_lp | `v13/main.tex:90` | 3.5 | 3.4900 | sí | 2.6200 | — |
| highlights_lp | `v13/highlights.tex:5` | 3.5 | 3.4900 | sí | 2.6200 | — |
| power_n200 | `v13/sec5_montecarlo.tex:218` | 6.7, 0.993, 0.926, 5.1, 3.5, 4.7, 0.057, 1.7, 0.003 | 6.7400, 0.9930, 0.9256, 5.1400, 3.4600, 4.6800, 0.0565, 1.6600, 0.0029 | sí | 6.7800, 0.9934, 0.9256, 5.6200, 3.4600, 4.6800, 0.0020, 1.1000, 0.0445 | p_rho090: 1.93e-84; p_rho093: 3.30e-30; p_rho080: 1.67e-52; p_rho085: 7.24e-71 |
| intro_power | `v13/sec1_introduction.tex:73` | 6.7, 5.1, 1.7 | 6.7400, 5.1400, 1.6600 | sí | 6.7800, 5.6200, 1.1000 | p_rho095: 0.0020 |
| abstract_power | `v13/main.tex:92` | 6.7, 2.6 | 6.7400, 2.6000 | sí | 6.7800, 1.7600 | max_gain_cell_n200: dgp1_rho0p9_n200; max_loss_cell: dgp1_rho0p99_n1000 |
| power_n500 | `v13/sec5_montecarlo.tex:224` | 1.1, 2.0, 2.6 | 1.1200, 2.0000, 2.6000 | sí | 1.5600, 1.5000, 1.7600 | — |
| power_adf | `v13/sec5_montecarlo.tex:226` | 42 | 41.0600 | **no** | 41.9000 | max_margin_cell: dgp1_rho0p99_n1000; max_margin_pp: 41.9000; minus_adf_pp: 43.3600; minus_pp_pp: 41.9000 |
| power_trend | `v13/sec5_montecarlo.tex:227` | 10.3, 5.9, five | 10.3400, 5.9400, 5 | sí | 9.9400, 6.1600, 5 | level_cells: [ct_power_rho0p95_n200, ct_power_rho0p97_n200, ct_power_rho0p99_n200, ct_power_rho0p99_n500, ct_power_rho0p99_n1000] |
| dgp2 | `v13/sec5_montecarlo.tex:378` | 0.706, 0.695, 0.057, 0.017, 0.474, 0.445, 0.573, 0.441, 1.000, 0.870, 0.637, 0.376 | 0.7060, 0.6946, 0.0568, 0.0175, 0.4738, 0.4452, 0.5728, 0.4406, 0.9998, 0.8696, 0.6370, 0.3758 | sí | 0.7126, 0.6946, 0.0020, 0.0636, 0.4770, 0.4452, 0.5780, 0.4406, 0.9998, 0.8696, 0.6560, 0.3758 | unsaturated_cells: [dgp2_delta0p5_n200, dgp2_delta0p5_n500, dgp2_delta1_n200, dgp2_delta1_n500, dgp2_delta2_n1000, dgp2_delta2_n200, dgp2_delta2_n500, dgp2_delta3_n1000, dgp2_delta3_n200, dgp2_delta3_n500]; cells_where_primary_leads: [dgp2_delta0p5_n200, dgp2_delta0p5_n500, dgp2_delta1_n200, dgp2_delta1_n500, dgp2_delta2_n1000, dgp2_delta2_n200, dgp2_delta2_n500, dgp2_delta3_n1000, dgp2_delta3_n200, dgp2_delta3_n500]; leads_in_every_unsaturated_cell: sí |
| za_exceeds | `v13/sec5_montecarlo.tex:389` | — | — | sí | — | cells_where_za_exceeds_primary: [dgp2_delta2_n200, dgp2_delta3_n1000, dgp2_delta3_n200, dgp2_delta3_n500, dgp2_delta5_n1000, dgp2_delta5_n200, dgp2_delta5_n500] |
| za_delta0 | `v13/sec5_montecarlo.tex:387` | 0.119, 0.706 | 0.1186, 0.7060 | sí | 0.1186, 0.7126 | — |
| dgp3 | `v13/sec5_montecarlo.tex:425` | 0.128, 0.131, 0.127 | 0.1278, 0.1306, 0.1272 | sí | 0.1226, 0.1268, 0.1252 | rm_below_primary_r4_n200: sí; msb_r4: [0.1296, 0.1346, 0.1310] |
| intro_dgp3 | `v13/sec1_introduction.tex:81` | 0.128, 0.040, 3 | 0.1278, 0.0395, 3.0000 | sí | 0.1226, 0.0405, 2.9000 | — |
| awb_rates | `v13/sec5_montecarlo.tex:436` | 0.054, 0.057, 0.082, 0.087, 0.040, 0.124, 0.118 | 0.0535, 0.0565, 0.0820, 0.0870, 0.0395, 0.1240, 0.1175 | sí | 0.0520, 0.0505, 0.0795, 0.0885, 0.0405, 0.1175, 0.1170 | awb_r4_n500: 0.0400; garch_awb_at_or_below_sim_all: sí |
| awb_homosk | `v13/sec5_montecarlo.tex:440` | 0.052, 0.043 | 0.0520, 0.0430 | sí | 0.0525, 0.0445 | — |
| awb_cost | `v13/sec5_montecarlo.tex:441` | 3.0, 1.3 | 3.0000, 1.3000 | sí | 2.9000, 1.8000 | — |
| awb_rule | `v13/sec5_montecarlo.tex:445` | — | — | sí | — | i_in_region_dgp3: 4; i_min: 4; i_equality: sí; max_power_loss_pp: 2.9000; ii_threshold_pp: 3.0000; ii_equality: no; recommend_awb: sí |
| misspec_heavy | `v13/sec5_montecarlo.tex:535` | 0.043, 0.042 | 0.0430, 0.0422 | sí | 0.0438, 0.0428 | — |
| misspec_shift200 | `v13/sec5_montecarlo.tex:539` | 0.63 | 0.6350 | sí | 0.6300 | — |
| misspec_shift1000 | `v13/sec5_montecarlo.tex:541` | 0.36 | 0.3600 | sí | 0.3250 | — |
| misspec_inside | `v13/sec5_montecarlo.tex:542` | nine | 9 | sí | 9 | garch_cells: 16; inside: [c\|garch_base_n1000, c\|garch_base_n200, c\|garch_base_n500, c\|garch_p095_t5_n200, c\|garch_p095_t5_n2000, c\|garch_p095_t5_n5000, c\|garch_p098_n1000, c\|garch_p099_n2000, c\|garch_p099_n5000] |
| dgp5 | `v13/sec5_montecarlo.tex:644` | 10, 29 | 7.8500, 28.5000 | **no** | 7.9500, 28.5500 | cells: 21; exceeds_bootstrap_r_ge_1.5: sí; exceeds_union_r_le_1.25: sí; union_dominates_interior: sí; min_table_rows_pp: 19.4000; max_table_rows_pp: 28.5500; table_rows: 12; min_cell: dgp5_n200_rho0.90_r1.1 |
| appB_cv | `v13/appB_critical_values.tex:10` | 0.222, 0.229 | 0.2219, 0.2290 | sí | 0.2321, 0.2362 | — |
| appB_se | `v13/appB_critical_values.tex:8` | 0.001 | 7.93e-04 | sí | 7.96e-04 | — |
| app_oos | `v13/sec6_application.tex:40` | 0.0468, 0.0478, 0.0478, 0.0490 | 0.0468, 0.0478, 0.0478, 0.0490 | sí | 0.0472, 0.0482, 0.0468, 0.0482 | in_region: {150: sí, 200: sí, 250: sí, 300: sí}; awb: {150: 0.0460, 200: 0.0452, 250: 0.0432, 300: 0.0488} |
| app_fp | `v13/sec6_application.tex:48` | 0.0229 | 0.0229 | sí | 0.0224 | — |
| app_detections | `v13/sec6_application.tex:50` | 17 | 17 | sí | 17 | — |
| app_mzt | `v13/sec6_application.tex:52` | 22.1, 29.6 | 22.1389, 29.5882 | sí | 22.1389, 29.7059 | mzt_dominates_all_three: sí |
| app_awb | `v13/sec6_application.tex:53` | 0.0220, 15 | 0.0220, 15 | sí | 0.0217, 13 | — |
| app_target | `v13/sec6_application.tex:56` | 0.0227 | 0.0227 | sí | 0.0222 | — |
| app_episodes | `v13/sec6_application.tex:57` | 33 | 33 | sí | 33 | dfgls_aic: 32; adf: 48; pp: 56 |
| app_latency_c | `v13/sec6_application.tex:59` | 102.5, 93.6, 79.7 | 102.5341, 93.6477, 79.7386 | sí | 102.5568, 93.6477, 79.7386 | — |
| app_adverse | `v13/sec6_application.tex:62` | 7 | 7 | sí | 7 | — |
| app_registered | `v13/sec6_application.tex:63` | 11, 13 | 11, 13 | sí | 11, 13 | — |
| dev_statistic | `v13/sec6_application.tex:129` | 0.0277, 0.0229, 13, 17, 33.8, 29.6 | 0.0277, 0.0229, 13, 17, 33.8462, 29.5882 | sí | 0.0277, 0.0224, 13, 17, 33.8462, 29.7059 | — |
| dev_awb | `v13/sec6_application.tex:137` | 0.0229, 0.0220, 17, 15, 29.6, 32.8 | 0.0229, 0.0220, 17, 15, 29.5882, 32.8000 | sí | 0.0224, 0.0217, 17, 13, 29.7059, 40.3077 | — |

Menciones literales de θ = 0.02 en el texto: `v13/sec5_montecarlo.tex:5`; `v13/sec1_introduction.tex:29`; `v13/sec6_application.tex:37`.

### B13.Q — Coherencia final sobre v14, tab:attrib y leyendas

Enmienda `experiments/protocol_audit13_amend1.md` (commit `490e01a`, 2026-09-23T13:18:05-06:00; sha256 en disco `0d048db6106824b243ba8fda1336ad0dd4a0e556ba2f72b1099764863ab113d9`, commiteado `0d048db6106824b243ba8fda1336ad0dd4a0e556ba2f72b1099764863ab113d9`). Sin simulaciones nuevas; la familia 144 no se usa.

**Q0. Entrada.** `paper_latex_v14.zip`, sha256 `3b21e2250002dee66780027d49ea3458d33f4ee481f042b4fe6a43a301d7a12b` (157334 bytes), leído dentro del zip. Tabulares y figuras del v14 frente a los exportados por A13: 21 archivos, todos idénticos byte a byte.

**Q1. tab:attrib.** Fuente `bB_attrib_audit12.json` (sha256 `5a517678b80735806f534f3286b5c09ca7519bd7f5590b57b85c189828b72183`). Redondeo: binary (convenciones probadas: binary → 0 distintas, 1 dobles redondeos; half_up → 3 distintas, 1 dobles redondeos). Comparación con el bloque TRANSCRIBED de `sec5_montecarlo.tex`: 91 celdas; 0 distintas; 1 dobles redondeos del v14. Nota: coincide cifra a cifra.

| Fila | (a) HAC | (b) s²_AR | (b′) s²_AR, PQ | (c) MSB-GLS asint. | (a)−(b′) | (b′)−(b) | (b′)−(c) |
|---|---|---|---|---|---|---|---|
| *Power, constant case, n = 200* |  |  |  |  |  |  |  |
| ρ = 0.80 | 1.000 | 0.947 | 0.954 | 0.941 | +4.64 | +0.62 | +1.22 |
| ρ = 0.90 | 0.993 | 0.924 | 0.931 | 0.914 | +6.22 | +0.72 | +1.70 |
| ρ = 0.93 | 0.910 | 0.840 | 0.847 | 0.816 | +6.32 | +0.72 | +3.08 |
| ρ = 0.95 | 0.708 | 0.659 | 0.668 | 0.628 | +4.04 | +0.90 | +3.96 |
| ρ = 0.97 | 0.386 | 0.367 | 0.373 | 0.345 | +1.34 | +0.62 | +2.76 |
| *Mean over the values of ρ, percentage points (s.e.)* |  |  |  |  |  |  |  |
| Constant, n = 200 (7) |  |  |  |  | +4.06 (0.14) | +0.52 (0.08) | +2.09 (0.09) |
| Constant, n = 500 (7) |  |  |  |  | +0.45 (0.06) | +0.07 (0.03) | +0.69 (0.05) |
| Constant, n = 1000 (7) |  |  |  |  | +0.10 (0.04) | +0.03 (0.02) | +0.51 (0.04) |
| Trend, n = 200 (4) |  |  |  |  | +1.68 (0.19) | +0.74 (0.12) | +8.12 (0.19) |
| Trend, n = 500 (4) |  |  |  |  | +1.86 (0.15) | +0.30 (0.07) | +4.56 (0.15) |
| *Local power, constant case, n = 2000* |  |  |  |  |  |  |  |
| c = 5 | 0.295 | 0.290 | 0.298 | 0.274 | -0.33 | +0.80 | +2.38 |
| c = 10 | 0.724 | 0.720 | 0.729 | 0.695 | -0.43 | +0.86 | +3.33 |
| c = 15 | 0.958 | 0.955 | 0.958 | 0.947 | +0.01 | +0.30 | +1.13 |

- Fila c = 5, columna 3: el v14 imprime 0.275; el JSON da 0.27445, que a 3 decimales es 0.274. El impreso es un doble redondeo.
- Paso 0: tasas = rejections/n, máx. |Δ| = 0 (columnas usadas); diferencias frente a diferencia de tasas, máx. 9.714e-17, y medias de `by_n` frente a la media de sus celdas, máx. 0 (columnas no usadas; 124 valores no nulos, todos ≤ 1.000e-12).
- Salidas: `experiments/results/tables_audit13/tab_attrib_audit13.tex` (sha256 `d9ae3a12499055b4b47746dad621701853ee22c1a908d5d8d8c6a65c5117beaf`) y `experiments/results/tables_audit13/tab_attrib_note_audit13.tex` (sha256 `c3a62c51726a082a221460b2d5f734b8a78ca46c50c850b4add5df55b132c41c`, la nota con las medias de (a)−(b) y (b)−(c)).

**Q2. Figuras con rótulos del v14.** Etiqueta «RM-GLS» → «MSB-B»; en `fig_size_shift_audit13q.pdf` se omite la serie «MSB-HAC» (`msbhac`). Paso 0 frente a `figures_audit13.json`: pasa.

| Figura | sha256 | Llamadas A13 → Q | Eliminadas | Resto idéntico bit a bit | Eliminadas = msbhac | Sin «RM-GLS» | Rótulos |
|---|---|---|---|---|---|---|---|
| fig_local_power_audit13q.pdf | `6741bcddfd4d973c4e3216a9ebdd035eb5d793583180f2a1d20d4500751743a2` | 12 → 12 | 0 | sí | sí | sí | Constant; DF-GLS; Envelope (P_T); MSB-B (θ = 0); MSB-GLS; MZ_t-GLS; Power (n = 2000); Trend; c |
| fig_theta_ladder_audit13q.pdf | `40d01b8b3282157eff8f5785aa9170f1f25911148651dc960e265c84faeb7669` | 6 → 6 | 0 | sí | sí | sí | Constant; Distance to envelope (pp); Trend; c = 10; c = 15; c = 5; θ |
| fig_power_equalized_audit13q.pdf | `b742a8c2b3b8ec1b7535e3825584cc84753ab95c40c5c31346b72546121bc8ad` | 42 → 42 | 0 | sí | sí | sí | ADF-sim; Constant, n = 1000; Constant, n = 200; Constant, n = 500; DF-GLS-sim; MSB-B; MSB-GLS-sim; MZ_t-GLS-sim; PP-sim; Power (equalized size); RM; Trend, n = 1000; Trend, n = 200; Trend, n = 500; ρ |
| fig_size_shift_audit13q.pdf | `aaeb311b9112183849aa4fe51a74c932052e86f709dd411d228f0fbee04d3001` | 30 → 26 | 4 | sí | sí | sí | ADF-sim; AWB DF-GLS; DF-GLS-sim; MSB-B; MSB-GLS-sim; MZ_t-GLS-sim; Persistence 0.95, t(5); Persistence 0.99, normal; Size shift (pp); n |
| fig_dgp3_audit13q.pdf | `d51a8eda794c53e058e7c87b1e0da2ddbd74d20e0376ab55dccf869385d2a4d3` | 21 → 21 | 0 | sí | sí | sí | ADF-sim; AWB DF-GLS; DF-GLS-sim; MSB-B; MSB-B, AWB; RM; Rejection rate (null true); n = 1000; n = 200; n = 500; r |
| fig_calibration_gain_audit13q.pdf | `84f209f72dbedf1e5cd6ccaa8c449310eba9c1b765405f9fced375f812d595ef` | 10 → 10 | 0 | sí | sí | sí | Constant; Empirical size; Exact region (N at each point); MSB-B, critical value at n; MSB-B, critical value at n = 20,000; MSB-GLS, published asymptotic critical value; Trend; n |

**Q3. Coherencia del v14.** 90 frases localizadas (0 sin localizar), 373 cifras recalculadas: no reproduce 3; reproduce 364; reproduce como cota 1; sin fuente JSON 5. Comprobaciones cualitativas: 40, de las cuales 1 no se cumplen. Barrido de los 554 números con decimales del texto: cubierta 357; diseno 100; tabular 97; no verificada 0.

Lista del CHANGELOG_v14 §3: frases `sec4_mcnemar`, `sec4_ma`, `sec4_a2`, `sec3_mabias`, `sec3_ar_factors`, `sec3_within`, `sec3_kappa_lambda`, `sec5_attrib`, `sec5_attrib_diag`, `attrib_note`, `sec5_serial1`, `sec5_serial2`, `sec5_serial3`, `sec5_initial`, `sec5_calib_out`, `sec5_ks`, `sec5_power500`, `appA_factor`. Definición usada para «12 de 23»: no saturada: min(theta 0, theta 0.02) < 0.99 y max > 0 (excluye las 3 celdas delta = 5 con potencia nula); θ = 0 más potente en 12 de 23, menos en 2 (máx. 0.4 pp); en DGP 3 menos distorsionado en 5 de 12 y más en 0.

| Archivo:línea | Frase | Impreso | Recalculado | Convención | Veredicto |
|---|---|---|---|---|---|
| `v14/main.tex:86` | abstract_limit | 0.056 | 0.05555 | binaria, mitad hacia arriba | reproduce |
| `v14/main.tex:86` | abstract_limit | 0.020 | 0.01995 | binaria, mitad hacia arriba | reproduce |
| `v14/main.tex:88` | abstract_msb | 0.026 | 0.026 | binaria, mitad hacia arriba | reproduce |
| `v14/main.tex:93` | abstract_attrib | 4.6 | 4.58571 | binaria, mitad hacia arriba | reproduce |
| `v14/main.tex:93` | abstract_attrib | 4.1 | 4.06286 | binaria, mitad hacia arriba | reproduce |
| `v14/main.tex:97` | abstract_ma | 0.42 | 0.42005 | binaria, mitad hacia arriba | reproduce |
| `v14/main.tex:97` | abstract_ma | 0.03 | 0.0257 | binaria, mitad hacia arriba | reproduce |
| `v14/cover_letter.md:11` | cover_msb | 2.6 | 2.6 | binaria, mitad hacia arriba | reproduce |
| `v14/cover_letter.md:13` | cover_attrib | 4.6 | 4.58571 | binaria, mitad hacia arriba | reproduce |
| `v14/cover_letter.md:13` | cover_ma | 0.42 | 0.42005 | binaria, mitad hacia arriba | reproduce |
| `v14/cover_letter.md:13` | cover_ma | 0.03 | 0.0257 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:44` | intro_248 | 24.8 | 24.785 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:60` | intro_kappa | 39.7 | 39.6667 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:61` | intro_exact | 0.360 | 0.360459 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:63` | intro_limit | 0.0556 | 0.05555 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:63` | intro_limit | 0.0199 | 0.01995 | binaria | reproduce |
| `v14/sec1_introduction.tex:63` | intro_limit | 0.0514 | 0.0514 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:63` | intro_limit | 0.0520 | 0.05205 | binaria | reproduce |
| `v14/sec1_introduction.tex:68` | intro_pub | 0.0260 | 0.026 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:68` | intro_pub | 0.0169 | 0.0169 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:68` | intro_pub | 0.0350 | 0.035 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:76` | intro_attrib | 4.6 | 4.58571 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:76` | intro_attrib | 4.1 | 4.06286 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:84` | intro_factor | 5.4 | 5.44444 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:85` | intro_ma | 0.420 | 0.42005 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:85` | intro_ma | 0.026 | 0.0257 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:89` | intro_ar05 | 0.010 | 0.01035 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:95` | intro_dgp3 | 0.123 | 0.1226 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:95` | intro_dgp3 | 0.080 | 0.0804 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:95` | intro_dgp3 | 0.053 | 0.0528 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:95` | intro_dgp3 | 0.041 | 0.0405 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:95` | intro_dgp3 | 3 | 2.9 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:103` | intro_initial | 0.06 | 0.0576 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:103` | intro_initial | 0.86 | 0.8552 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:103` | intro_initial | 0.818 | 0.8178 | binaria, mitad hacia arriba | reproduce |
| `v14/sec1_introduction.tex:103` | intro_initial | 0.643 | 0.6432 | binaria, mitad hacia arriba | reproduce |
| `v14/sec2_statistic.tex:61` | sec2_248 | 24.8 | 24.785 | binaria, mitad hacia arriba | reproduce |
| `v14/sec2_statistic.tex:93` | sec2_invariance | 5 | 5.19834 | binaria, mitad hacia arriba | reproduce |
| `v14/sec2_statistic.tex:93` | sec2_invariance | 3 | 2.7246 | binaria, mitad hacia arriba | reproduce |
| `v14/sec2_statistic.tex:110` | sec2_endpoint | 0.8 | 0.835254 | binaria, mitad hacia arriba | reproduce |
| `v14/sec2_statistic.tex:110` | sec2_endpoint | 0.16 | 0.161258 | binaria, mitad hacia arriba | reproduce |
| `v14/sec2_statistic.tex:112` | sec2_identity | 1.6 | 1.64164 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:67` | sec3_kappa_lambda | 39.7 | 39.6667 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:67` | sec3_kappa_lambda | 1192 | 1192.33 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:68` | sec3_exact | 0.360 | 0.360459 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:68` | sec3_exact | 0.432 | 0.431812 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:68` | sec3_exact | 0.481 | 0.480933 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:70` | sec3_within | 5.4 | 5.31645 | hacia arriba (cota) | reproduce como cota |
| `v14/sec3_theory.tex:70` | sec3_within | 0.302 | 0.301667 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:99` | sec3_mabias | 8 | 8 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:99` | sec3_mabias | 5.4 | 5.44444 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:104` | sec3_ar_factors | 1.13 | 1.1332 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:104` | sec3_ar_factors | 0.85 | 0.852141 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:156` | sec3_slopes | 0.011 | 0.010903 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:156` | sec3_slopes | 0.057 | 0.0566137 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:156` | sec3_slopes | -0.56 | -0.559025 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:156` | sec3_slopes | -0.64 | -0.638326 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:181` | sec3_dkw | 0.0043 | 0.00429469 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:181` | sec3_dkw | 0.0019 | 0.00192065 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:192` | sec3_mismatch | 0.037 | 0.0366 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:214` | sec3_gamma | 0.631 | 0.630957 | binaria, mitad hacia arriba | reproduce |
| `v14/sec3_theory.tex:214` | sec3_gamma | 0.720 | 0.719686 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:35` | sec4_P | 0.659 | 0.659083 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:35` | sec4_P | 0.654 | 0.653733 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:35` | sec4_P | 0.645 | 0.644817 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:35` | sec4_P | 0.631 | 0.631133 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:35` | sec4_P | 0.601 | 0.600983 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:35` | sec4_worst | 0.10 | 0.102 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:42` | sec4_amend | four | 4 | palabra | reproduce |
| `v14/sec4_implementation.tex:42` | sec4_amend | 0.0494 | 0.04943 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:42` | sec4_amend | 0.0503 | 0.05027 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:52` | sec4_a2 | 0.01 | 0.0125 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | 12 | 12 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | 23 | 23 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | 2 | 2 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | 0.4 | 0.4 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | 5 | 5 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | 12 | 12 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:60` | sec4_ma | 0.420 | 0.42005 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:60` | sec4_ma | 0.361 | 0.3611 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:60` | sec4_ma | 0.531 | 0.5308 | binaria, mitad hacia arriba | reproduce |
| `v14/sec4_implementation.tex:60` | sec4_ma | 0.781 | 0.7814 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:21` | sec5_region | 0.0440 | 0.044 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:21` | sec5_region | 0.0562 | 0.0562 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:26` | sec5_size | 0.24 | 0.236 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:26` | sec5_size | 100 | 100 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:26` | sec5_size | 0.0524 | 0.05236 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:26` | sec5_size | 0.0526 | 0.0526 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:26` | sec5_size | 0.0493 | 0.04928 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0607 | 0.06065 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0588 | 0.05885 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0556 | 0.05555 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0544 | 0.05445 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0516 | 0.0516 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0514 | 0.0514 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0199 | 0.01995 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0323 | 0.0323 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0413 | 0.04135 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0520 | 0.05205 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0481 | 0.04805 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:57` | sec5_calib | 0.0480 | 0.048 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:65` | sec5_ks | 0.096 | 0.09625 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:65` | sec5_ks | 0.015 | 0.0153 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:65` | sec5_ks | 1000 | 1000 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:68` | sec5_pub | 0.0169 | 0.0169 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:68` | sec5_pub | 0.0260 | 0.026 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:68` | sec5_pub | 0.0394 | 0.0394 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:68` | sec5_pub | 0.0350 | 0.035 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:75` | sec5_calib_out | 0.0544 | 0.05445 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:75` | sec5_calib_out | 0.13 | 0.14 | — | **no reproduce → 0.14** |
| `v14/sec5_montecarlo.tex:88` | sec5_calib_note | 0.0470 | 0.047 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:88` | sec5_calib_note | 0.0531 | 0.05305 | mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:88` | sec5_calib_note | 0.2370 | 0.23697 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:88` | sec5_calib_note | 0.1714 | 0.171374 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 1.8 | 1.835 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 2.6 | 2.62 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 0.7 | 0.685 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 2.3 | 2.305 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 3.1 | 3.07 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 1.0 | 1 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 1.2 | 1.225 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 0.3 | 0.28 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 0.9 | 0.87 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 2.6 | 2.62 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 3.5 | 3.49 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 4.9 | 4.88 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 7.1 | 7.065 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 11.2 | 11.205 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:141` | sec5_lp_se | 0.0035 | 0.00353551 | binaria, mitad hacia arriba, cota superior incumplida | **no reproduce → 0.0036** |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 6.8 | 6.78 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 0.993 | 0.9934 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 0.926 | 0.9256 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 5.6 | 5.62 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 3.5 | 3.46 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 4.7 | 4.68 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 1.8 | 1.82 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 0.002 | 0.00201682 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 1.1 | 1.1 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | 0.045 | 0.0445387 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:179` | sec5_power500 | 1.6 | 1.56 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:179` | sec5_power500 | 1.5 | 1.5 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:179` | sec5_power500 | 1.8 | 1.76 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:179` | sec5_power500 | 43 | 43.36 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:179` | sec5_power500 | 42 | 41.9 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:183` | sec5_power_trend | 9.9 | 9.94 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:183` | sec5_power_trend | 6.2 | 6.16 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:183` | sec5_power_trend | five | 5 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 4.59 | 4.58571 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 0.52 | 0.52 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 0.13 | 0.128571 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 2.43 | 2.425 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 0.52 | 0.522857 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 4.06 | 4.06286 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | -0.43 | -0.435 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | +0.01 | 0.015 | binaria | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 2.1 | 2.14 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:241` | sec5_attrib | 7.4 | 7.375 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:257` | sec5_attrib_diag | 0.884 | 0.883598 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:257` | sec5_attrib_diag | 0.913 | 0.913357 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:257` | sec5_attrib_diag | 0.937 | 0.937496 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:257` | sec5_attrib_diag | 0.961 | 0.961096 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.420 | 0.42005 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.361 | 0.3611 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.397 | 0.39685 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.570 | 0.56955 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.071 | 0.07135 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.097 | 0.097 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 5.31 | 5.30677 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 5.44 | 5.44444 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.019 | 0.0193 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.010 | 0.01035 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.004 | 0.00415 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:316` | sec5_serial1 | 0.047 | 0.04685 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 36 | 36 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.013 | 0.01335 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.098 | 0.09805 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.004 | 0.00415 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.570 | 0.56955 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.026 | 0.0257 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.032 | 0.032 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.142 | 0.14175 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | 0.679 | 0.6786 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:340` | sec5_serial3 | 7 | 7 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:340` | sec5_serial3 | 1.73 | 1.73192 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:340` | sec5_serial3 | 0.531 | 0.5308 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:340` | sec5_serial3 | 0.781 | 0.7814 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.058 | 0.0576 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.855 | 0.8552 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.958 | 0.9582 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.888 | 0.8876 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.977 | 0.9772 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.818 | 0.8178 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.643 | 0.6432 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.613 | 0.6128 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.606 | 0.6056 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.778 | 0.7778 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | 0.678 | 0.6776 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.713 | 0.7126 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.695 | 0.6946 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.002 | 0.00203932 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.477 | 0.477 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.445 | 0.4452 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.578 | 0.578 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.441 | 0.4406 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 1.000 | 0.9998 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.870 | 0.8696 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.656 | 0.656 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | 0.376 | 0.3758 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.119 | 0.1186 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.713 | 0.7126 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.092 | 0.0922 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.497 | 0.4966 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.986 | 0.9858 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.0542 | 0.0542 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.0472 | 0.0472 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.0522 | 0.0522 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.0558 | 0.0558 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.0464 | 0.0464 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:417` | sec5_za | 0.0458 | 0.0458 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | 0.123 | 0.1226 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | 0.127 | 0.1268 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | 0.125 | 0.1252 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | 0.117 | 0.1166 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | 0.080 | 0.0804 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | 0.097 | 0.0966 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.052 | 0.052 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.051 | 0.0505 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.080 | 0.0795 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.089 | 0.0885 | mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.041 | 0.0405 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.040 | 0.04 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.118 | 0.1175 | mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.117 | 0.117 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.053 | 0.0525 | mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.045 | 0.0445 | mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 2.9 | 2.9 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 1.8 | 1.8 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.1 | 0.1 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.045 | 0.045 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | 0.056 | 0.0555 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | 0.044 | 0.0438 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | 0.043 | 0.0428 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.63 | 0.63 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.28 | 0.285 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.39 | 0.395 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +1.47 | 1.47 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.33 | 0.325 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.04 | 0.04 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.21 | 0.215 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | +0.85 | 0.855 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | nine | 9 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | eleven | 11 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | nine | 9 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | six | 6 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | four | 4 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | two | 2 | palabra | reproduce |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | 0.9985 | 0.9985 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | 1.0000 | 1 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | 0.47 | 0.47 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | 0.90 | 0.9025 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | 0.4 | 0.432296 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | 2.0 | 1.97627 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:602` | sec5_dgp5b | 19 | 19.4 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:602` | sec5_dgp5b | 29 | 28.55 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:602` | sec5_dgp5b | 8 | 7.95 | binaria, mitad hacia arriba, cota inferior incumplida | **no reproduce → 7** |
| `v14/sec5_montecarlo.tex:620` | sec5_dgp5_alpha | 0.0256 | 0.0256 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:631` | sec5_negative | 0.1 | 0.1 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:631` | sec5_negative | 0.003 | — | — | sin fuente JSON |
| `v14/sec5_montecarlo.tex:631` | sec5_negative | 14 | 14.36 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:631` | sec5_negative | 28 | 27.74 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:631` | sec5_negative | 24.8 | 24.785 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:631` | sec5_negative | 33.4 | 33.355 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:41` | app_oos | 0.0472 | 0.0472 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:41` | app_oos | 0.0482 | 0.0482 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:41` | app_oos | 0.0468 | 0.0468 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:41` | app_oos | 0.0482 | 0.0482 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:41` | app_oos | 0.0432 | 0.0432 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:31` | app_cells | 48 | 48 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:31` | app_cells | 88 | 88 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 0.0224 | 0.0224423 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 0.0535 | 0.0535311 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 0.0532 | 0.053201 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 0.0210 | 0.0209694 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 17 | 17 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 26 | 26 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 23 | 23 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 23 | 23 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 0.0173 | 0.0173423 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 36 | 36 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 22.1 | 22.1389 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 29.7 | 29.7059 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 0.0217 | 0.0217213 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:50` | app_results | 13 | 13 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 0.0222 | 0.0222444 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 33 | 33 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | one | 1 | palabra | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 48 | 48 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 56 | 56 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 102.6 | 102.557 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 93.6 | 93.6477 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 79.7 | 79.7386 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 7 | 7 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 11 | 11 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:59` | app_matched | 13 | 13 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:81` | app_caption | 0.0222 | 0.0222444 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:89` | app_note | 0.0222 | 0.0222444 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:115` | dev_pilot | 0.02770 | 0.0276957 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:115` | dev_pilot | 0.02786 | 0.0278587 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 0.0277 | 0.0276957 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 0.0224 | 0.0224423 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 13 | 13 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 17 | 17 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 33.8 | 33.8462 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 29.7 | 29.7059 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 0.0229 | 0.0229471 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 0.0224 | 0.0224423 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 17 | 17 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 17 | 17 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 29.6 | 29.5882 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:120` | dev_stat | 29.7 | 29.7059 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:129` | dev_cal | 0.0061 | 0.00607361 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:132` | dev_awb | 0.0224 | 0.0224423 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:132` | dev_awb | 0.0217 | 0.0217213 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:132` | dev_awb | 17 | 17 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:132` | dev_awb | 13 | 13 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:132` | dev_awb | 29.7 | 29.7059 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:132` | dev_awb | 40.3 | 40.3077 | binaria, mitad hacia arriba | reproduce |
| `v14/sec6_application.tex:146` | dev_ncal | 0.0301 | — | — | sin fuente JSON |
| `v14/sec6_application.tex:146` | dev_ncal | 13 | 13 | binaria, mitad hacia arriba | reproduce |
| `v14/sec7_conclusion.tex:16` | concl_pub | 2.4 | 2.4 | binaria, mitad hacia arriba | reproduce |
| `v14/sec7_conclusion.tex:16` | concl_pub | 3.3 | 3.31 | binaria, mitad hacia arriba | reproduce |
| `v14/sec7_conclusion.tex:33` | concl_ma | 0.42 | 0.42005 | binaria, mitad hacia arriba | reproduce |
| `v14/sec7_conclusion.tex:49` | concl_25 | 25 | 24.785 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:89` | appA_factor | 0.80 | 0.803213 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:93` | appA_exact | 0.360 | 0.360459 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:93` | appA_exact | 0.432 | 0.431812 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:93` | appA_exact | 0.481 | 0.480933 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:93` | appA_exact | 0.302 | 0.301667 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:93` | appA_exact | 0.421 | 0.420667 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:93` | appA_exact | 0.480 | 0.480167 | binaria, mitad hacia arriba | reproduce |
| `v14/appA_proofs.tex:148` | appA_hacrate | 6.9 | — | — | sin fuente JSON |
| `v14/appA_proofs.tex:148` | appA_hacrate | 0.6 | — | — | sin fuente JSON |
| `v14/appA_proofs.tex:148` | appA_hacrate | 0.333 | — | — | sin fuente JSON |
| `v14/appB_critical_values.tex:8` | appB | 0.001 | 7.956e-04 | binaria, mitad hacia arriba | reproduce |
| `v14/appB_critical_values.tex:8` | appB | 0.232 | 0.232078 | binaria, mitad hacia arriba | reproduce |
| `v14/appB_critical_values.tex:8` | appB | 0.236 | 0.236213 | binaria, mitad hacia arriba | reproduce |
| `v14/appB_critical_values.tex:8` | appB | 0.178 | 0.178237 | binaria, mitad hacia arriba | reproduce |
| `v14/appB_critical_values.tex:8` | appB | 0.171 | 0.171299 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 4.59 | 4.58571 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.15 | 0.147243 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.52 | 0.52 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.06 | 0.0624338 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.13 | 0.128571 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.04 | 0.0406715 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 2.43 | 2.425 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.20 | 0.203423 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 2.16 | 2.16 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.16 | 0.155235 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 1.57 | 1.56571 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.61 | 0.614286 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 0.48 | 0.48 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 7.38 | 7.375 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:296` | attrib_note | 4.26 | 4.26 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:362` | note_region_serial | 0.0470 | 0.047 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:362` | note_region_serial | 0.0531 | 0.05305 | mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:443` | note_region_dgp2 | 0.0440 | 0.044 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:443` | note_region_dgp2 | 0.0562 | 0.0562 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:490` | note_region_dgp3 | 0.0440 | 0.044 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:490` | note_region_dgp3 | 0.0562 | 0.0562 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:505` | note_region_awb | 0.0405 | 0.0405 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:505` | note_region_awb | 0.0600 | 0.06 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:555` | note_region_misspec | 0.0440 | 0.044 | binaria, mitad hacia arriba | reproduce |
| `v14/sec5_montecarlo.tex:555` | note_region_misspec | 0.0562 | 0.0562 | binaria, mitad hacia arriba | reproduce |

Comprobaciones cualitativas (frases sin cifra o con condición):

| Archivo:línea | Frase | Comprobación | ¿Se cumple? |
|---|---|---|---|
| `v14/sec3_theory.tex:67` | sec3_kappa_lambda | kappa del JSON = formula | sí |
| `v14/sec3_theory.tex:67` | sec3_kappa_lambda | lambda del JSON = formula | sí |
| `v14/sec3_theory.tex:104` | sec3_ar_factors | igual en c y ct | sí |
| `v14/sec4_implementation.tex:42` | sec4_amend | todas las fallas en una sola celda (ct\|200) | sí |
| `v14/sec4_implementation.tex:42` | sec4_amend | margen < 0.001 | sí |
| `v14/sec4_implementation.tex:56` | sec4_mcnemar | ninguna celda de DGP 3 mas distorsionada | sí |
| `v14/sec5_montecarlo.tex:26` | sec5_size | celda de tendencia a n = 100 | sí |
| `v14/sec5_montecarlo.tex:26` | sec5_size | fuera de la region de 5e4 | sí |
| `v14/sec5_montecarlo.tex:26` | sec5_size | todas dentro de 0.25 pp | sí |
| `v14/sec5_montecarlo.tex:65` | sec5_ks | constante: por encima del umbral en todo n hasta 5000 | sí |
| `v14/sec5_montecarlo.tex:65` | sec5_ks | tendencia: por encima del umbral exactamente hasta 1000 | sí |
| `v14/sec5_montecarlo.tex:68` | sec5_pub | con cv simulado, ambos dentro en todo n | sí |
| `v14/sec5_montecarlo.tex:75` | sec5_calib_out | unica celda calibrada fuera | sí |
| `v14/sec5_montecarlo.tex:116` | sec5_lp | 'about half a point': media de MSB - primaria en c = 5, 10, 15 = 0.41 pp (redondea a medio punto si round(2 x) = 1) | sí |
| `v14/sec5_montecarlo.tex:173` | sec5_power200 | p < 1e-4 en rho = 0.90 y 0.93 | sí |
| `v14/sec5_montecarlo.tex:257` | sec5_attrib_diag | MAIC sin retardos en la mediana para rho >= 0.90 | sí |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | MSB-GLS y MZ_t-GLS a menos de medio punto de (b) en todas las celdas (max 0.57 pp, celda ma_m0p8 n = 500 c) | **no** |
| `v14/sec5_montecarlo.tex:329` | sec5_serial2 | PP rechaza casi siempre a psi = -0.8 (min 0.985) | sí |
| `v14/sec5_montecarlo.tex:376` | sec5_initial | a alpha = 4 todos los GLS rechazan 0.000 (max 0.0000) | sí |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | lidera en toda celda no saturada con 0.5 <= delta <= 3 | sí |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | p < 0.01 salvo (3, 200): ['dgp2_delta3_n200'] | sí |
| `v14/sec5_montecarlo.tex:407` | sec5_dgp2 | en (3, 200) ambos por debajo de 0.01 | sí |
| `v14/sec5_montecarlo.tex:417` | sec5_za | ZA supera a la primaria en delta = 3 (todo n) y (2, 200): ['dgp2_delta2_n200', 'dgp2_delta3_n1000', 'dgp2_delta3_n200', 'dgp2_delta3_n500', 'dgp2_delta5_n1000', 'dgp2_delta5_n200', 'dgp2_delta5_n500'] | sí |
| `v14/sec5_montecarlo.tex:453` | sec5_dgp3 | RM menos distorsionado que la primaria | sí |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | GARCH: AWB <= simulada en las cuatro | sí |
| `v14/sec5_montecarlo.tex:464` | sec5_awb | primera condicion con igualdad | sí |
| `v14/sec5_montecarlo.tex:529` | sec5_misspec | DF-GLS y MZ_t-GLS con el mismo recuento | sí |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | supera al bootstrap para r >= 1.5 | sí |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | supera a la union para r <= 1.25 | sí |
| `v14/sec5_montecarlo.tex:589` | sec5_dgp5 | la union domina en el interior | sí |
| `v14/sec5_montecarlo.tex:602` | sec5_dgp5b | supera al bootstrap para r >= 1.5 | sí |
| `v14/sec5_montecarlo.tex:602` | sec5_dgp5b | supera a la union para r <= 1.25 | sí |
| `v14/sec5_montecarlo.tex:602` | sec5_dgp5b | la union domina en el interior | sí |
| `v14/sec6_application.tex:41` | app_oos | theta 0: las cuatro dentro | sí |
| `v14/sec6_application.tex:41` | app_oos | AWB D = 250 por debajo de la region | sí |
| `v14/sec1_introduction.tex:45` | intro_window | potencia local media decreciente en theta (0.6591, 0.6537, 0.6448, 0.6311, 0.6010) | sí |
| `v14/sec1_introduction.tex:45` | intro_window | 'dobla': cociente de distorsiones medias theta 0.02 / theta 0 = 1.97 (redondea a 2 si esta en [1.5, 2.5)); por celda con distorsion positiva, de 1.12 a 4.15 | sí |
| `v14/sec7_conclusion.tex:41` | concl_window | potencia local media decreciente en theta (0.6591, 0.6537, 0.6448, 0.6311, 0.6010) | sí |
| `v14/sec7_conclusion.tex:41` | concl_window | 'dobla': cociente de distorsiones medias theta 0.02 / theta 0 = 1.97 (redondea a 2 si esta en [1.5, 2.5)); por celda con distorsion positiva, de 1.12 a 4.15 | sí |
| `v14/sec5_montecarlo.tex:443` | note_region_dgp2 | ZA dentro de la region en las seis celdas | sí |

Fuentes por frase:

| Frase | Archivo:línea | Fuente |
|---|---|---|
| abstract_limit | `v14/main.tex:86` | e_calib_audit13.json cases_by_theta.gls_t0.<c\|ct>.approximation_cost.<n>.size_with_cv_n20000 |
| abstract_msb | `v14/main.tex:88` | e_calib_audit13.json ...ct.approximation_cost_comparators.200.msb.size_published_asymptotic |
| abstract_attrib | `v14/main.tex:93` | bB_attrib_audit12.json by_n.c\|200.<a_minus_b\|a_minus_bp>.mean |
| abstract_ma | `v14/main.tex:97` | bA_ma_audit12.json size.sz_ma_m0p8_n200_c.iid.<gls_t0\|glsb_t0> |
| cover_msb | `v14/cover_letter.md:11` | e_calib_audit13.json ...ct.200.msb.size_published_asymptotic (x100) |
| cover_attrib | `v14/cover_letter.md:13` | bB_attrib_audit12.json by_n.c\|200.<a_minus_b\|a_minus_bp>.mean |
| cover_ma | `v14/cover_letter.md:13` | bA_ma_audit12.json size.sz_ma_m0p8_n200_c.iid.<gls_t0\|glsb_t0> |
| intro_248 | `v14/sec1_introduction.tex:44` | t5_claims_audit11.json claims.3.by_case.dm.0.1.cost_pp (A8 B4) |
| intro_kappa | `v14/sec1_introduction.tex:60` | formula kappa = 2\|c\|(1/2 + \|c\|/3), c = -7 |
| intro_exact | `v14/sec1_introduction.tex:61` | bF_anchor_audit12.json rows.200.exact |
| intro_limit | `v14/sec1_introduction.tex:63` | e_calib_audit13.json approximation_cost.<n>.<size_with_cv_n20000\|size_with_cv_at_n> |
| intro_pub | `v14/sec1_introduction.tex:68` | e_calib_audit13.json approximation_cost_comparators (publicado) |
| intro_attrib | `v14/sec1_introduction.tex:76` | bB_attrib_audit12.json by_n.c\|200.<a_minus_b\|a_minus_bp>.mean |
| intro_factor | `v14/sec1_introduction.tex:84` | bA_ma_audit12.json size.sz_ma_m0p8_n200_c.bartlett_factor_at_median_B.factor (B = 8) |
| intro_ma | `v14/sec1_introduction.tex:85` | bA_ma_audit12.json size.sz_ma_m0p8_n200_c.iid |
| intro_ar05 | `v14/sec1_introduction.tex:89` | bA_ma_audit12.json size.sz_ar_0p5_n200_ct.iid.gls_t0 |
| intro_dgp3 | `v14/sec1_introduction.tex:95` | e_equalized_audit13.json dgp3_r4_n200; e_awb_audit13.json |
| intro_initial | `v14/sec1_introduction.tex:103` | bC_initial_audit12.json cells.0.9\|<alpha2\|alpha1>.power |
| sec2_248 | `v14/sec2_statistic.tex:61` | t5_claims_audit11.json claims.3.by_case.dm.0.1.cost_pp (A8 B4) |
| sec2_invariance | `v14/sec2_statistic.tex:93` | b1_validation_audit8.json V4_gls.invariance.worst_rel_diff (max c, ct); V4_gls.drift.worst_rel_diff_rm_gls_ct |
| sec2_endpoint | `v14/sec2_statistic.tex:110` | b102_identity_audit10.json cells.dm\|<200\|1000>.endpoint_term_share_of_rm2.median (x100) |
| sec2_identity | `v14/sec2_statistic.tex:112` | b102_identity_audit10.json worst_ii |
| sec3_kappa_lambda | `v14/sec3_theory.tex:67` | formulas kappa y lambda con c = -7; bF_anchor_audit12.json config.<kappa\|lambda> |
| sec3_exact | `v14/sec3_theory.tex:68` | bF_anchor_audit12.json rows.<n>.exact |
| sec3_within | `v14/sec3_theory.tex:70` | bF_anchor_audit12.json gate.worst (max \|formula - exacta\|, n >= 200); rows.200.first_order_A11 |
| sec3_mabias | `v14/sec3_theory.tex:99` | bA_ma_audit12.json size.sz_ma_m0p8_n200_c.bartlett_factor_at_median_B |
| sec3_ar_factors | `v14/sec3_theory.tex:104` | bA_ma_audit12.json size.sz_ar_<m0p5\|0p5>_n200_c.bartlett_factor_at_median_B.factor |
| sec3_slopes | `v14/sec3_theory.tex:156` | t4_trend_audit11.json by_rho.<0.5\|0.9>.quantities.<resid_ms\|statistic>.slope |
| sec3_dkw | `v14/sec3_theory.tex:181` | formula DKW-Massart: eps = sqrt(ln(2/0.05)/(2 N_cal)) |
| sec3_mismatch | `v14/sec3_theory.tex:192` | b2_size_audit8.json paso0.cells.gauss_n200.published_rates.rm_R0.5_t0.1_one (calibracion sigma = 1) |
| sec3_gamma | `v14/sec3_theory.tex:214` | formula gamma = 0.01^(1/l), l = round(1.75 (n+1)^(1/3)) (audit9_engine.awb_gamma) |
| sec4_P | `v14/sec4_implementation.tex:35` | b92_theta_audit9.json theta_rule.P |
| sec4_worst | `v14/sec4_implementation.tex:35` | b101_theta_audit10.json A1prime.<theta>.<celda>.abs_dev_from_alpha (max, x100) |
| sec4_amend | `v14/sec4_implementation.tex:42` | b92_theta_audit9.json theta_rule.A1; b101_theta_audit10.json A1prime.<proc>.ct\|200 |
| sec4_a2 | `v14/sec4_implementation.tex:52` | b92_theta_audit9.json theta_rule.A2_mean_delta (\|theta 0 - theta 0.02\|, x100) |
| sec4_mcnemar | `v14/sec4_implementation.tex:56` | b103_equalized_audit10.json cells.<celda>.mcnemar_primary_vs_sim.gls_t0 (primaria theta 0.02) y rates_sim; no saturada: min(theta 0, theta 0.02) < 0.99 y max > 0 (excluye las 3 celdas delta = 5 con potencia nula) |
| sec4_ma | `v14/sec4_implementation.tex:60` | bA_ma_audit12.json size.sz_ma_m0p8_n200_<c\|ct>.iid.<gls_t0\|gls_t0.02> |
| sec5_region | `v14/sec5_montecarlo.tex:21` | formula: region binomial exacta de N = 5000 (audit9_common.exact_region) |
| sec5_size | `v14/sec5_montecarlo.tex:26` | e_size_audit13.json cells.ct\|100 |
| sec5_calib | `v14/sec5_montecarlo.tex:57` | e_calib_audit13.json approximation_cost |
| sec5_ks | `v14/sec5_montecarlo.tex:65` | e_calib_audit13.json cases_by_theta.gls_t0.<c\|ct>.ks |
| sec5_pub | `v14/sec5_montecarlo.tex:68` | e_calib_audit13.json approximation_cost_comparators (tendencia) |
| sec5_calib_out | `v14/sec5_montecarlo.tex:75` | e_calib_audit13.json approximation_cost.60.size_with_cv_at_n; exact_region_20000 |
| sec5_calib_note | `v14/sec5_montecarlo.tex:88` | formula exact_region(20000); e_calib_audit13.json cv_n20000 |
| sec5_lp | `v14/sec5_montecarlo.tex:116` | b92_theta_audit9.json local_power.<dm\|ct>.power |
| sec5_lp_se | `v14/sec5_montecarlo.tex:141` | b92_theta_audit9.json local_power (EE binomial con N = 2e4) |
| sec5_power200 | `v14/sec5_montecarlo.tex:173` | e_equalized_audit13.json dgp1_rho<rho>_n200 |
| sec5_power500 | `v14/sec5_montecarlo.tex:179` | e_equalized_audit13.json dgp1 |
| sec5_power_trend | `v14/sec5_montecarlo.tex:183` | e_equalized_audit13.json ct_power; filas de tab:ctpower |
| sec5_attrib | `v14/sec5_montecarlo.tex:241` | bB_attrib_audit12.json by_n y lp_dm_c<c>; tamano: e_calib_audit13.json ct.200 msb (simulado - publicado) |
| sec5_attrib_diag | `v14/sec5_montecarlo.tex:257` | bB_attrib_audit12.json diagnostics_n200 (medianas) |
| sec5_serial1 | `v14/sec5_montecarlo.tex:316` | bA_ma_audit12.json size.<celda>.iid.gls_t0; diagnostics; bartlett_factor_at_median_B |
| sec5_serial2 | `v14/sec5_montecarlo.tex:329` | bA_ma_audit12.json size (36 celdas, bloque iid) |
| sec5_serial3 | `v14/sec5_montecarlo.tex:340` | bA_ma_audit12.json size.sz_ma_m0p8_n200_c.diagnostics; iid.gls_t0.02 |
| sec5_initial | `v14/sec5_montecarlo.tex:376` | bC_initial_audit12.json cells.0.9\|<variante>.power |
| sec5_dgp2 | `v14/sec5_montecarlo.tex:407` | e_equalized_audit13.json dgp2 |
| sec5_za | `v14/sec5_montecarlo.tex:417` | e_equalized_audit13.json dgp2 (za); b5_power_audit8.json za_size.<za_rw\|za_rwbreak>_n<n>.rates.za |
| sec5_dgp3 | `v14/sec5_montecarlo.tex:453` | e_equalized_audit13.json dgp3_r4_n<n> |
| sec5_awb | `v14/sec5_montecarlo.tex:464` | e_awb_audit13.json cells y rule; dgp3_recast_composite_null_audit7.json cells.<celda>.bootstrap_dfgls (experimento aparte, A7) |
| sec5_misspec | `v14/sec5_montecarlo.tex:529` | b92_theta_audit9.json misspec (16 celdas GARCH, caso constante) |
| sec5_dgp5 | `v14/sec5_montecarlo.tex:589` | e_dgp5_audit13.json cells; a7_joint_alpha_star |
| sec5_dgp5b | `v14/sec5_montecarlo.tex:602` | e_dgp5_audit13.json cells; a7_joint_alpha_star |
| sec5_dgp5_alpha | `v14/sec5_montecarlo.tex:620` | e_dgp5_audit13.json cells; a7_joint_alpha_star |
| sec5_negative | `v14/sec5_montecarlo.tex:631` | t5_claims_audit11.json claims.1 (b2_size_audit8), claims.2 (adaptive_size_power_audit5b), claims.3 (A8 B4); la media 0.003 del peso no tiene JSON localizado |
| app_oos | `v14/sec6_application.tex:41` | e_application_audit13.json oos_size y oos_size_awb |
| app_cells | `v14/sec6_application.tex:31` | e_application_audit13.json fp_cells.final; summary.final.event_cells |
| app_results | `v14/sec6_application.tex:50` | e_application_audit13.json summary |
| app_matched | `v14/sec6_application.tex:59` | e_application_audit13.json matched_rate, adverse_cells_primary, summary |
| app_caption | `v14/sec6_application.tex:81` | e_application_audit13.json matched_rate.target_fpr_pooled_primary |
| app_note | `v14/sec6_application.tex:89` | e_application_audit13.json matched_rate.target_fpr_pooled_primary |
| dev_pilot | `v14/sec6_application.tex:115` | deviation_table_audit8.json rows[0] (i, A5bis) |
| dev_stat | `v14/sec6_application.tex:120` | e_application_audit13.json summary; b103_application_audit10.json summary.final (theta 0.02) |
| dev_cal | `v14/sec6_application.tex:129` | formula DKW con N_cal = 5e4 (deviation_table_audit8.json rows[1]) |
| dev_awb | `v14/sec6_application.tex:132` | e_application_audit13.json summary |
| dev_ncal | `v14/sec6_application.tex:146` | detecciones: deviation_table_audit8.json rows[7]; la FP 0.0301 no tiene JSON localizado |
| concl_pub | `v14/sec7_conclusion.tex:16` | e_calib_audit13.json comparadores publicados (tendencia); bA_ma_audit12.json |
| concl_ma | `v14/sec7_conclusion.tex:33` | e_calib_audit13.json comparadores publicados (tendencia); bA_ma_audit12.json |
| concl_25 | `v14/sec7_conclusion.tex:49` | t5_claims_audit11.json claims.3 |
| appA_factor | `v14/appA_proofs.tex:89` | formula (1 + c^2/n)^-1; bF_anchor_audit12.json rows |
| appA_exact | `v14/appA_proofs.tex:93` | formula (1 + c^2/n)^-1; bF_anchor_audit12.json rows |
| appA_hacrate | `v14/appA_proofs.tex:148` | sin JSON localizado (Observacion rem:hacrate; el v14 remite al suplemento) |
| appB | `v14/appB_critical_values.tex:8` | b103_cv_audit10.json table.<caso>\|0\|<n> |
| intro_window | `v14/sec1_introduction.tex:45` | b92_theta_audit9.json theta_rule.P; bA_ma_audit12.json size (12 celdas MA con psi < 0, iid) |
| concl_window | `v14/sec7_conclusion.tex:41` | b92_theta_audit9.json theta_rule.P; bA_ma_audit12.json size (12 celdas MA con psi < 0, iid) |
| attrib_note | `v14/sec5_montecarlo.tex:296` | bB_attrib_audit12.json by_n.<celda>.<a_minus_b\|b_minus_c> |
| note_region_serial | `v14/sec5_montecarlo.tex:362` | formula exact_region(20000) |
| note_region_dgp2 | `v14/sec5_montecarlo.tex:443` | formula exact_region(5000); tamanos de ZA en sec5_za |
| note_region_dgp3 | `v14/sec5_montecarlo.tex:490` | formula exact_region(5000) |
| note_region_awb | `v14/sec5_montecarlo.tex:505` | formula exact_region(2000) |
| note_region_misspec | `v14/sec5_montecarlo.tex:555` | formula exact_region(5000) |

**Q4. Frases prohibidas.** Búsqueda literal en la fuente del v14, fuera de §5.11, §5.12 y tab:deviations. Resumen: «collapses faster»: prohibida 0, permitida 0, excluida 0; «does not collapse as fast»: prohibida 0, permitida 0, excluida 0; «no cost in size»: prohibida 0, permitida 0, excluida 0; «no effect on size»: prohibida 0, permitida 0, excluida 0; «RM-GLS»: prohibida 0, permitida 0, excluida 0; «rolling means»: prohibida 5, permitida 1, excluida 1; «theta = 0.02»: prohibida 0, permitida 9, excluida 1; «two-channel»: prohibida 4, permitida 3, excluida 7. Total de apariciones prohibidas: 9.

| Patrón | Archivo:línea | Zona | Estado | Contexto |
|---|---|---|---|---|
| two-channel | `v14/main.tex:103` | main | **prohibida** |  critical values. A smoothed variant of the statistic and a two-channel extension, both evaluated under pre-registered rules, are r |
| rolling means | `v14/sec1_introduction.tex:38` | 1 | **prohibida** | ts removed. An earlier design measured the second moment of rolling means of the detrended series over a window of fraction $\theta$  |
| rolling means | `v14/sec1_introduction.tex:41` | 1 | **prohibida** | ng variances, weighted the two adaptively, and anchored the rolling means at the sample mean rather than at the GLS estimate. A pre-r |
| two-channel | `v14/sec1_introduction.tex:43` | 1 | **prohibida** | gistered experiment returned its falsifying outcome for the two-channel design (\cref{sec:dgp5}); the adaptive weight concentrated  |
| rolling means | `v14/sec2_statistic.tex:37` | 2.2 | permitida |  1/2]$ let $\tau = \mathrm{round}(\theta n)$ and define the rolling means of the detrended series, \begin{equation}\label{eq:rollmean |
| rolling means | `v14/sec3_theory.tex:130` | 3.3 | **prohibida** |  under stationarity, so the uncentered second moment of the rolling means is bounded by $2(\rw_0 - \mu)^2$ plus the mean-square fluct |
| rolling means | `v14/sec3_theory.tex:132` | 3.3 | **prohibida** | _0 - \mu)^2$ plus the mean-square fluctuation of stationary rolling means. The denominator diverges: the first differences of a stati |
| theta = 0.02 | `v14/sec4_implementation.tex:37` | 4.2 | permitida |  for the five values in increasing order; $\theta = 0$ and $\theta = 0.02$ tied, and the rule selected $\theta = 0.02$. The rule was |
| theta = 0.02 | `v14/sec4_implementation.tex:38` | 4.2 | permitida | theta = 0$ and $\theta = 0.02$ tied, and the rule selected $\theta = 0.02$. The rule was amended once, and we report the amendment.  |
| theta = 0.02 | `v14/sec4_implementation.tex:56` | 4.2 | permitida | :power,sec:meanbreaks}, $\theta = 0$ has higher power than $\theta = 0.02$ (McNemar $p < 0.05$) in 12 of the 23 cells in which power  |
| theta = 0.02 | `v14/sec4_implementation.tex:62` | 4.2 | permitida | constant and trend cases, against $0.531$ and $0.781$ with $\theta = 0.02$. We therefore report the statistic without a window. This  |
| theta = 0.02 | `v14/sec4_implementation.tex:64` | 4.2 | permitida | istered rule, not a change of the rule: the rule's output, $\theta = 0.02$, is reported here, lies within the rule's own tie margin o |
| rolling means | `v14/sec5_montecarlo.tex:636` | 5.12 | excluida |  lowered power by $14$ to $28$ points. Third, measuring the rolling means from their own average rather than from the GLS anchor cost |
| theta = 0.02 | `v14/sec5_montecarlo.tex:29` | 5.1 | permitida | gion for $5\times 10^4$ paths; the smoothed statistic with $\theta = 0.02$ gives $0.0526$ on the same paths and an independent replic |
| theta = 0.02 | `v14/sec5_montecarlo.tex:122` | 5.3 | permitida | ts of the envelope throughout. The smoothed statistic with $\theta = 0.02$ is lower by $0.3$ to $0.9$ points, and \cref{fig:thetaladd |
| theta = 0.02 | `v14/sec5_montecarlo.tex:140` | 5.3 | permitida | t uses the asymptotic critical value of \citet{ng2001lag}. $\theta = 0.02$: the smoothed statistic of \cref{sec:theta}. Monte Carlo s |
| theta = 0.02 | `v14/sec5_montecarlo.tex:343` | 5.6 | permitida | thrm{AR}}/\omega^2$ is $1.73$. The smoothed statistic with $\theta = 0.02$ is worse still ($0.531$ and $0.781$ at $\psi = -0.8$ and $ |
| two-channel | `v14/sec5_montecarlo.tex:571` | 5.11 | excluida | shift} \end{figure} \subsection{A pre-registered test of a two-channel extension}\label{sec:dgp5} The statistic was originally on |
| two-channel | `v14/sec5_montecarlo.tex:573` | 5.11 | excluida | el{sec:dgp5} The statistic was originally one channel of a two-channel construction whose second channel measured the variability  |
| two-channel | `v14/sec5_montecarlo.tex:585` | 5.11 | excluida |  calibrated jointly. The registered prediction was that the two-channel statistic would exceed the union in the interior of the gri |
| two-channel | `v14/sec5_montecarlo.tex:591` | 5.11 | excluida | 0.9985$ to $1.0000$ there, against $0.47$ to $0.90$ for the two-channel statistic. The variance channel carried between $0.4$ and $ |
| two-channel | `v14/sec5_montecarlo.tex:602` | 5.11 | excluida |  changes the magnitudes but not the verdict. It exceeds the two-channel statistic by $19$ to $29$ points in the rows of \cref{tab:d |
| two-channel | `v14/sec5_montecarlo.tex:617` | 5.11 | excluida | enotes}\footnotesize \item $^\dagger$Registered interior. ``Two-channel'': the original construction with fixed weight $0.5$ on eac |
| theta = 0.02 | `v14/sec6_application.tex:123` | 6.2 | excluida | \\ \addlinespace Window & -- & $\theta = 0$ instead of the $\theta = 0.02$ selected by the registered rule of \cref{sec:theta} & Me |
| two-channel | `v14/sec6_application.tex:34` | 6.1 | permitida | cells and 88 event cells. The registered statistic was the two-channel construction with an adaptive weight. \RMGLS{} was not in t |
| two-channel | `v14/sec6_application.tex:66` | 6.2 | permitida | tered baseline in 7 of the 48 control cells. The registered two-channel statistic had fewer false-alarm episodes (11) and fewer det |
| two-channel | `v14/sec6_application.tex:93` | 6.2 | permitida | ys over all 88 event cells. The registered statistic is the two-channel construction with adaptive weight of the protocol. \item[$a |
| two-channel | `v14/sec6_application.tex:119` | 6.2 | excluida |  detection shifts by one day \\ \addlinespace Statistic & Two-channel statistic, windows $(0.1, 0.1)$, adaptive weight & \RMGLS |
| rolling means | `v14/appA_proofs.tex:11` | A.1 | **prohibida** |  in the constant case and $b + c\,t$ in the trend case. The rolling means are linear in $\uhat$, so the numerator of \cref{eq:stat} i |
| two-channel | `v14/highlights.tex:7` | highlights | **prohibida** | ize under serial correlation \item A smoothed variant and a two-channel extension are reported as negative results \end{itemize}  |
| two-channel | `v14/cover_letter.md:15` | cover_letter | **prohibida** | ger construction: a smoothed version of the statistic and a two-channel extension were evaluated under pre-registered rules, and bo |

**Q5. Suplemento: valores críticos de MSB-GLS y MZ_t-GLS con N_cal = 5·10⁵.** Presentes: 16; faltan: 48. Muestras de calibración de A10: n = 100: 500000 filas, columnas todas; n = 200: 500000 filas, columnas todas; n = 500: 500000 filas, columnas todas; n = 1000: 500000 filas, columnas todas.

| Caso | n | Test | Nivel | Valor crítico (fuente) | Fuentes coinciden |
|---|---|---|---|---|---|
| c | 100 | msb | 0.01 | **falta** | — |
| c | 100 | msb | 0.025 | **falta** | — |
| c | 100 | msb | 0.05 | 0.235577 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| c | 100 | msb | 0.1 | **falta** | — |
| c | 100 | mzt | 0.01 | **falta** | — |
| c | 100 | mzt | 0.025 | **falta** | — |
| c | 100 | mzt | 0.05 | -1.95277 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| c | 100 | mzt | 0.1 | **falta** | — |
| ct | 100 | msb | 0.01 | **falta** | — |
| ct | 100 | msb | 0.025 | **falta** | — |
| ct | 100 | msb | 0.05 | 0.181441 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| ct | 100 | msb | 0.1 | **falta** | — |
| ct | 100 | mzt | 0.01 | **falta** | — |
| ct | 100 | mzt | 0.025 | **falta** | — |
| ct | 100 | mzt | 0.05 | -2.66552 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| ct | 100 | mzt | 0.1 | **falta** | — |
| c | 200 | msb | 0.01 | **falta** | — |
| c | 200 | msb | 0.025 | **falta** | — |
| c | 200 | msb | 0.05 | 0.236918 (`b101_theta_audit10.json`, N_cal 500000); 0.236918 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| c | 200 | msb | 0.1 | **falta** | — |
| c | 200 | mzt | 0.01 | **falta** | — |
| c | 200 | mzt | 0.025 | **falta** | — |
| c | 200 | mzt | 0.05 | -1.94606 (`b101_theta_audit10.json`, N_cal 500000); -1.94606 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| c | 200 | mzt | 0.1 | **falta** | — |
| ct | 200 | msb | 0.01 | **falta** | — |
| ct | 200 | msb | 0.025 | **falta** | — |
| ct | 200 | msb | 0.05 | 0.178323 (`b101_theta_audit10.json`, N_cal 500000); 0.178323 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| ct | 200 | msb | 0.1 | **falta** | — |
| ct | 200 | mzt | 0.01 | **falta** | — |
| ct | 200 | mzt | 0.025 | **falta** | — |
| ct | 200 | mzt | 0.05 | -2.7214 (`b101_theta_audit10.json`, N_cal 500000); -2.7214 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| ct | 200 | mzt | 0.1 | **falta** | — |
| c | 500 | msb | 0.01 | **falta** | — |
| c | 500 | msb | 0.025 | **falta** | — |
| c | 500 | msb | 0.05 | 0.237642 (`b101_theta_audit10.json`, N_cal 500000); 0.237642 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| c | 500 | msb | 0.1 | **falta** | — |
| c | 500 | mzt | 0.01 | **falta** | — |
| c | 500 | mzt | 0.025 | **falta** | — |
| c | 500 | mzt | 0.05 | -1.94187 (`b101_theta_audit10.json`, N_cal 500000); -1.94187 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| c | 500 | mzt | 0.1 | **falta** | — |
| ct | 500 | msb | 0.01 | **falta** | — |
| ct | 500 | msb | 0.025 | **falta** | — |
| ct | 500 | msb | 0.05 | 0.175104 (`b101_theta_audit10.json`, N_cal 500000); 0.175104 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| ct | 500 | msb | 0.1 | **falta** | — |
| ct | 500 | mzt | 0.01 | **falta** | — |
| ct | 500 | mzt | 0.025 | **falta** | — |
| ct | 500 | mzt | 0.05 | -2.77621 (`b101_theta_audit10.json`, N_cal 500000); -2.77621 (`bA_ma_audit12.json`, N_cal 500000) | sí |
| ct | 500 | mzt | 0.1 | **falta** | — |
| c | 1000 | msb | 0.01 | **falta** | — |
| c | 1000 | msb | 0.025 | **falta** | — |
| c | 1000 | msb | 0.05 | 0.237512 (`b101_theta_audit10.json`, N_cal 500000) | sí |
| c | 1000 | msb | 0.1 | **falta** | — |
| c | 1000 | mzt | 0.01 | **falta** | — |
| c | 1000 | mzt | 0.025 | **falta** | — |
| c | 1000 | mzt | 0.05 | -1.94169 (`b101_theta_audit10.json`, N_cal 500000) | sí |
| c | 1000 | mzt | 0.1 | **falta** | — |
| ct | 1000 | msb | 0.01 | **falta** | — |
| ct | 1000 | msb | 0.025 | **falta** | — |
| ct | 1000 | msb | 0.05 | 0.173389 (`b101_theta_audit10.json`, N_cal 500000) | sí |
| ct | 1000 | msb | 0.1 | **falta** | — |
| ct | 1000 | mzt | 0.01 | **falta** | — |
| ct | 1000 | mzt | 0.025 | **falta** | — |
| ct | 1000 | mzt | 0.05 | -2.80406 (`b101_theta_audit10.json`, N_cal 500000) | sí |
| ct | 1000 | mzt | 0.1 | **falta** | — |

## 2. Compuertas

**Compuerta informativa de B13.E (no detiene nada).** Máxima diferencia entre la versión con θ = 0 y la publicada con θ = 0.02:

| Tabla | máx. \|Δ\| | Unidades | Celda | Δ con signo | Celdas comparadas |
|---|---|---|---|---|---|
| tab:size | 0.2780 | pp | ct\|100 | 0.2780 | 12 |
| tab:calib | 3.2400 | q: unidades del estadistico; tamanos: pp | ct\|60\|size_q_20000 | -3.2400 | 48 |
| tab:localpower | 0.8700 | pp | dm\|c10.0 | 0.8700 | 14 |
| tab:dgp1 | 0.8400 | pp | dgp1_rho0p99_n1000 | 0.8400 | 10 |
| tab:ctpower | 0.4000 | pp | ct_power_rho0p9_n200 | -0.4000 | 9 |
| tab:dgp2 | 1.9000 | pp | dgp2_delta3_n1000 | 1.9000 | 18 |
| tab:dgp3 | 0.5200 | pp | dgp3_r4_n200 | -0.5200 | 9 |
| tab:misspec | 0.1400 | pp | c\|garch_base_n1000 | -0.1400 | 27 |
| tab:critB | 0.0153 | unidades del estadistico | ct\|100\|0.01 | 0.0153 | 48 |
| tab:awb | 0.9500 | pp | dgp1_rho0p95_n200\|awb | 0.9500 | 32 |
| tab:dgp5 | 0.8000 | pp | dgp5_n200_rho0.95_r1.0 | 0.8000 | 12 |
| tab:fp | 7.5077 | FP: pp; detecciones y episodios: numero; latencias: dias | final_awb\|latency | 7.5077 | 12 |

**Paso 0 (máx. |Δ| = 0).**

| Bloque | Criterio | Resultado | Veredicto |
|---|---|---|---|
| tab:size n ≤ 150 (familia 141) | fila ligera = audit9_engine.row, 50 caminos por celda | máx. \|Δ\| = 0.0e+00 | pasa |
| Tamaño igualado (dgp1, ctpower, dgp2, dgp3) | (a) filas frente a B5 de A8 | 0.0e+00 | pasa |
|  | (b) 1266 tasas frente a b103_equalized | 0.0e+00 | pasa |
|  | (c) 831 McNemar con θ = 0.02 frente a b103_equalized | 0.0e+00 | pasa |
| tab:calib | θ = 0.02 frente a b103_finite (974 hojas; 0 diferencias de estructura) | 0.0e+00 | pasa |
| DGP 5 | (a) g1/g2 frente a A7 (50 series por celda) | 0.0e+00 | pasa |
|  | (b) θ = 0.02 frente a la caché de A10 | 0.0e+00 | pasa |
|  | (c) tabla θ = 0.02 frente a b103_dgp5 | 0.0e+00 | pasa |
| AWB | estadístico observado frente a B9.1/B9.2 | 0.0e+00 | pasa |
|  | columna simulada θ = 0.02 frente a b103_awb | 0.0e+00 | pasa |
| Aplicación | (a) θ = 0.02 en las 50 primeras ventanas frente a A10 | 0.0e+00 | pasa |
|  | (b) resumen θ = 0.02 (con y sin AWB) frente a A10 | 0.0e+00 | pasa |
|  | (c) tamaño fuera de muestra θ = 0.02 frente a A10 | 0.0e+00 | pasa |
|  | (d) episodios a tasa común θ = 0.02 frente a A10 | 0 | pasa |
| Figuras | datos con θ = 0.02 y fuentes del v13 = datos de A11, llamada a llamada | 6 de 6 idénticas | pasa |
| Transcripción tab:size | θ = 0.02 desde JSON = tabular del v13 (12 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:calib | θ = 0.02 desde JSON = tabular del v13 (112 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 2 negritas del v13 | pasa |
| Transcripción tab:localpower | θ = 0.02 desde JSON = tabular del v13 (98 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:dgp1 | θ = 0.02 desde JSON = tabular del v13 (80 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:ctpower | θ = 0.02 desde JSON = tabular del v13 (72 celdas; redondeo binary) | 0 distintas; 1 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:dgp2 | θ = 0.02 desde JSON = tabular del v13 (162 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:dgp3 | θ = 0.02 desde JSON = tabular del v13 (63 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:misspec | θ = 0.02 desde JSON = tabular del v13 (189 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:critB | θ = 0.02 desde JSON = tabular del v13 (48 celdas; redondeo binary) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:awb | θ = 0.02 desde JSON = tabular del v13 (64 celdas; redondeo half_up) | 0 distintas; 1 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:dgp5 | θ = 0.02 desde JSON = tabular del v13 (60 celdas; redondeo half_up) | 0 distintas; 0 doble redondeo del v13; 0 negritas del v13 | pasa |
| Transcripción tab:fp | θ = 0.02 desde JSON = tabular del v13 (63 celdas; redondeo binary) | 0 distintas; 1 doble redondeo del v13; 0 negritas del v13 | pasa |
| B13.Q Q0 | tabulares y figuras del v14 = exportados por A13 | 21 archivos | pasa |
| B13.Q Q1 (columnas usadas) | tasas = rejections/n | máx. \|Δ\| = 0 | pasa |
| B13.Q Q1 (resto) | diferencias y medias recompuestas ≤ 1e-12 (regla corregida de la enmienda) | máx. 9.714e-17; 124 valores no nulos declarados | pasa |
| B13.Q Q2 | series restantes idénticas bit a bit a A13; eliminadas = msbhac | 6 figuras | pasa |

## 3. Procedencia

| Archivo | sha256 | Script | Commit | Código commiteado |
|---|---|---|---|---|
| experiments/results/b130_inventory_audit13.json | `e20ca99490af8b17e366219e38407675a05bc56ef421484c1d58308a50b1ba86` | experiments/audit13_b130_inventory.py | 2db4c12 | sí |
| experiments/results/claims_audit13.json | `f6eeea21569730153ca6830642d144b3d95c246e742d34a254d73c403f22400b` | experiments/audit13_claims.py | 2db4c12 | sí |
| experiments/results/e_application_audit13.json | `c8562d1881fbbe4430395eb82fab531e5e609ca708164f5d72f58cc7a281f335` | experiments/audit13_e_application.py | 2db4c12 | sí |
| experiments/results/e_awb_audit13.json | `b8d953bd51e8f918021826ea72928881e8c18498636eb898b2b735a140e66e7c` | experiments/audit13_e_awb.py | 2db4c12 | sí |
| experiments/results/e_awb_budget_audit13.json | `674df8c2572f5b9787541df90005482dec1e4fe62ca0c67c7a7b850fe834f1e9` | experiments/audit13_e_awb.py | 2db4c12 | sí |
| experiments/results/e_calib_audit13.json | `017f5eabb93f3fb54e5255b7d76aca994cc70ce6df8be12c5ca2c24febe7272a` | experiments/audit13_e_calib.py | 2db4c12 | sí |
| experiments/results/e_dgp5_audit13.json | `bb0982d5ffe450046aac8b4b9b93beca197a0d82fefa4500cbc9d6f81503f3d4` | experiments/audit13_e_dgp5.py | 2db4c12 | sí |
| experiments/results/e_equalized_audit13.json | `9bf392e2656dc3278af24c39c6aa6d6cbdefc1903f39b47582cd0d408e9b2a0e` | experiments/audit13_e_equalized.py | 2db4c12 | sí |
| experiments/results/e_size_audit13.json | `e462426175afb7a767da7e26c9f985f434c5a945cc5d6b1e72d9d7e90182a281` | experiments/audit13_e_size.py | 2db4c12 | sí |
| experiments/results/figures_audit13.json | `7af979a409bed0a263aa9ffc8cb884b3707cbbe23fdc2d7d439d88248ac4d2d3` | experiments/make_figures_audit13.py | 2db4c12 | sí |
| experiments/results/figures_audit13q.json | `3f453197cd9ff9b761e1eef4b182701b4cdc2d8af2fa74f5c92fd99de228a245` | experiments/make_figures_audit13q.py | 3862690 | sí |
| experiments/results/q_attrib_audit13.json | `f79d59cd104e94c0b859712d4ab2dd83537e1714e49e0e3d0ff74b7a1270842a` | experiments/audit13_q_attrib.py | 3862690 | sí |
| experiments/results/q_claims_audit13.json | `33dd5741998761e652255b64061d30eaaa30a3ad63f26617a30c819ef476eec9` | experiments/audit13_q_claims.py | 3862690 | sí |
| experiments/results/q_inventory_audit13.json | `b38893dff4e96ce9ebe29851759c2fc7dfc62d5e20c43e8dc54c1f94e47c2353` | experiments/audit13_q_inventory.py | 3862690 | sí |
| experiments/results/q_phrases_audit13.json | `7ae57d2d55a9cd5ac44c1fcdc33a45946ea6c53d628cefef6bf79c7d2ca1b8d3` | experiments/audit13_q_phrases.py | 3862690 | sí |
| experiments/results/q_supplement_audit13.json | `098a4e3f66ce6216e740232fe6198a3510e6e84a341ac1b7aa08575d704ffd7f` | experiments/audit13_q_supplement.py | 3862690 | sí |
| experiments/results/t_tables_audit13.json | `f10560e2f6e8ff24ffe0fbb1d1dcb99e4be57ff3628c0e97e59cd06a1353f403` | experiments/audit13_t_tables.py | 2db4c12 | sí |
| experiments/results/tables_audit13.json | `545e58ba690436a14e6cb0ad81e1a4c3f9308541051d145d28a282d10f8546a7` | experiments/audit13_tables.py | 2db4c12 | sí |

| Tabular o figura | sha256 |
|---|---|
| experiments/figures/fig_calibration_gain_audit13.pdf | `39b3d33229372bf1e5110f42a5921eb2c8a772d1c33f66b7cdd3663e0ff9508f` |
| experiments/figures/fig_calibration_gain_audit13q.pdf | `84f209f72dbedf1e5cd6ccaa8c449310eba9c1b765405f9fced375f812d595ef` |
| experiments/figures/fig_dgp3_audit13.pdf | `2048a77850ec3eb3785a314177ae0274db452d5807dcb80a47d12974b216669f` |
| experiments/figures/fig_dgp3_audit13q.pdf | `d51a8eda794c53e058e7c87b1e0da2ddbd74d20e0376ab55dccf869385d2a4d3` |
| experiments/figures/fig_local_power_audit13.pdf | `7a4c78c66e8fbed74d5bc5a34d888282501d91ffe960072b0c3d20b94b70489d` |
| experiments/figures/fig_local_power_audit13q.pdf | `6741bcddfd4d973c4e3216a9ebdd035eb5d793583180f2a1d20d4500751743a2` |
| experiments/figures/fig_power_equalized_audit13.pdf | `254d762be3f7f2412e8f6ab1a0d05f74b88538cd64808684ce3e968ec5d4a7ff` |
| experiments/figures/fig_power_equalized_audit13q.pdf | `b742a8c2b3b8ec1b7535e3825584cc84753ab95c40c5c31346b72546121bc8ad` |
| experiments/figures/fig_size_shift_audit13.pdf | `a128a601ad2f6c0fbb174daf81f2b2d48733bd6c1468b257269a36367eff6c11` |
| experiments/figures/fig_size_shift_audit13q.pdf | `aaeb311b9112183849aa4fe51a74c932052e86f709dd411d228f0fbee04d3001` |
| experiments/figures/fig_theta_ladder_audit13.pdf | `4ceb42115502f2c3318637b6cfe59eb2cce1d8c58802598c50ae72fac84f0b9e` |
| experiments/figures/fig_theta_ladder_audit13q.pdf | `40d01b8b3282157eff8f5785aa9170f1f25911148651dc960e265c84faeb7669` |
| experiments/results/tables_audit13/tab_attrib_audit13.tex | `d9ae3a12499055b4b47746dad621701853ee22c1a908d5d8d8c6a65c5117beaf` |
| experiments/results/tables_audit13/tab_attrib_note_audit13.tex | `c3a62c51726a082a221460b2d5f734b8a78ca46c50c850b4add5df55b132c41c` |
| experiments/results/tables_audit13/tab_awb_audit13.tex | `2953b2372b26706d6f7e0499c71aa792ce712595b4cbdd47b9675d824efe7452` |
| experiments/results/tables_audit13/tab_calib_audit13.tex | `50386f28974cec10a0339f3f584d60ae53b063011c41030857cbc146ba2b2c24` |
| experiments/results/tables_audit13/tab_critB_audit13.tex | `55d2a2727db124002a31f4148eb7cc21b7b5d8fbbd49d73e4672ab1003b470af` |
| experiments/results/tables_audit13/tab_ctpower_audit13.tex | `afc906a11671c33110ae3fdf366775bcbdd8af626fc55b0aed79d41efbfbb7ac` |
| experiments/results/tables_audit13/tab_dgp1_audit13.tex | `1d37d8f8166edb48b3bafb4aa0e3cc51a0d677844e997b8dfb2ee420d22a8cdd` |
| experiments/results/tables_audit13/tab_dgp2_audit13.tex | `82820f35e76b9b476ce42e276bcfed9e9d97d40220c078d283fa4558904d06cc` |
| experiments/results/tables_audit13/tab_dgp3_audit13.tex | `50447ad976cf25c02d6dcce3fffeffcb78410b18e9033f1653556f7bd34d510f` |
| experiments/results/tables_audit13/tab_dgp5_audit13.tex | `cbfd0696261fecf92a3d2f6f04ee468324b6edab60d5cb93c802a3f7325e503d` |
| experiments/results/tables_audit13/tab_fp_audit13.tex | `b76b26cd4e462328e66c46a12fa0790c23f606a67dec9f5551d0f16e45364e89` |
| experiments/results/tables_audit13/tab_initial_audit13.tex | `4dcfc29ddf0bd2b42164cd0075a19a909c4505b8b51524c9b04fd1c58bcee695` |
| experiments/results/tables_audit13/tab_localpower_audit13.tex | `a0a939eb090ae819641ea658e7642ac22f0732d432af54af6b080671615dce6e` |
| experiments/results/tables_audit13/tab_misspec_audit13.tex | `4c3f8474263c0243cc663446931ce3d79ac3810ec443d9839d96b11bd3ec1dcf` |
| experiments/results/tables_audit13/tab_serial_audit13.tex | `cd6a1d7ade12ea0784c217dada4aa82b92c37a7ba66bafeecaceb1ae8d9ad66b` |
| experiments/results/tables_audit13/tab_serialpower_audit13.tex | `89c7c311f5e3b04a7ee9492ca8cb7ed1589e5ee4a27541279f04d91104439db7` |
| experiments/results/tables_audit13/tab_size_audit13.tex | `8b57a3f1289301aad0bba50c6c2af2bca994b00070f78aafbab364d6eab3698b` |
| paper/figures/fig_calibration_gain_audit13.pdf | `39b3d33229372bf1e5110f42a5921eb2c8a772d1c33f66b7cdd3663e0ff9508f` |
| paper/figures/fig_calibration_gain_audit13q.pdf | `84f209f72dbedf1e5cd6ccaa8c449310eba9c1b765405f9fced375f812d595ef` |
| paper/figures/fig_dgp3_audit13.pdf | `2048a77850ec3eb3785a314177ae0274db452d5807dcb80a47d12974b216669f` |
| paper/figures/fig_dgp3_audit13q.pdf | `d51a8eda794c53e058e7c87b1e0da2ddbd74d20e0376ab55dccf869385d2a4d3` |
| paper/figures/fig_local_power_audit13.pdf | `7a4c78c66e8fbed74d5bc5a34d888282501d91ffe960072b0c3d20b94b70489d` |
| paper/figures/fig_local_power_audit13q.pdf | `6741bcddfd4d973c4e3216a9ebdd035eb5d793583180f2a1d20d4500751743a2` |
| paper/figures/fig_power_equalized_audit13.pdf | `254d762be3f7f2412e8f6ab1a0d05f74b88538cd64808684ce3e968ec5d4a7ff` |
| paper/figures/fig_power_equalized_audit13q.pdf | `b742a8c2b3b8ec1b7535e3825584cc84753ab95c40c5c31346b72546121bc8ad` |
| paper/figures/fig_size_shift_audit13.pdf | `a128a601ad2f6c0fbb174daf81f2b2d48733bd6c1468b257269a36367eff6c11` |
| paper/figures/fig_size_shift_audit13q.pdf | `aaeb311b9112183849aa4fe51a74c932052e86f709dd411d228f0fbee04d3001` |
| paper/figures/fig_theta_ladder_audit13.pdf | `4ceb42115502f2c3318637b6cfe59eb2cce1d8c58802598c50ae72fac84f0b9e` |
| paper/figures/fig_theta_ladder_audit13q.pdf | `40d01b8b3282157eff8f5785aa9170f1f25911148651dc960e265c84faeb7669` |

Versiones: python 3.11.0, platform Windows-10-10.0.26200-SP0, numpy 2.2.4, scipy 1.15.2, numba 0.65.0, statsmodels 0.14.6, arch 8.0.0, pandas 2.2.3, joblib 1.4.2, matplotlib 3.10.1, pytest 9.0.3.

## 4. Desviaciones

| Desviación | Motivo | Cuándo | Efecto |
|---|---|---|---|
| Convención de redondeo por tabla: la que reproduce el v13 (binario de Python en size, calib, localpower, dgp1, ctpower, dgp2, dgp3, misspec, critB, fp; mitad hacia arriba sobre el decimal en awb, dgp5) | El v13 no usa una convención única: las tablas de N = 2000 se transcribieron desde el reporte de A10 a 4 decimales | Después de ver el Paso 0 de transcripción | Sólo formato; las celdas con θ = 0 usan la misma convención que su tabla |
| La negrita del tabular con θ = 0 sigue la regla de cada nota (fuera de la región exacta), también donde el v13 la omitió | Regla escrita en la nota de la tabla | Al construir el exportador | Negritas nuevas listadas en §7(b) |
| tab:size en n ≤ 150: la versión con θ = 0 usa caminos nuevos (familia 141) y la publicada los de B10.3.7 (familia 113) | Encargo literal (lectura 4) | Antes de calcular | La compuerta en esas celdas mezcla ruido independiente; la diferencia pareada va en §1 |
| Las figuras van a `experiments/figures/` (la carpeta de A11) y a `paper/figures/`; la lectura 12 decía `figures/` | Convención de A11 | Antes de dibujar | Ninguno |
| El mismo exportador escribe también los tabulares de tab:awb, tab:dgp5 y tab:fp (bloque E(2)) | Lectura 15 | Antes de calcular | Ninguno |
| Q1: la nota de tab:attrib se exporta como fragmento aparte (`tab_attrib_note_audit13.tex`) | La nota va fuera del tabular en el v14 | Antes de correr (lectura 3) | Ninguno |
| Q3: definición de «no saturada»: no saturada: min(theta 0, theta 0.02) < 0.99 y max > 0 (excluye las 3 celdas delta = 5 con potencia nula) | Es la definición que reproduce «23» del v14; la de la lectura 5 (sólo min < 0.99) da 26 | Después de ver el recuento | Ninguno sobre 12, 2 y 0.4 |
| Q3: las cotas del texto («within», «at most», «below», «at least») se comprueban como desigualdades además del redondeo | Una cota puede redondear bien y ser falsa | Al escribir el registro | Tres cifras marcadas en §7(d) |
| Q4: «rolling means» y «two-channel» se buscan sin distinguir mayúsculas; las formas con guion («rolling-means») no cuentan | Búsqueda literal | Antes de correr (lectura 6) | Ninguno |

## 5. No ejecutado

- **Q5 (suplemento)**: faltan en los JSON 48 valores críticos de MSB-GLS y MZ_t-GLS (niveles 0.01, 0.025, 0.1; los del 5 % están). Las muestras de calibración de A10 (N_cal = 500 000) tienen las columnas; no se calcularon, por el encargo.
- **Q3**: cifras del v14 sin JSON localizado: `v14/sec5_montecarlo.tex:631` 0.003 (sec5_negative); `v14/sec6_application.tex:146` 0.0301 (dev_ncal); `v14/appA_proofs.tex:148` 6.9 (appA_hacrate); `v14/appA_proofs.tex:148` 0.6 (appA_hacrate); `v14/appA_proofs.tex:148` 0.333 (appA_hacrate).
- **B12.D**: sigue cancelado por el encargo.
- **tab:deviations** no se exporta como tabular porque sus celdas son texto. Las cifras están en §1 (aplicación) y en la tabla de cifras del texto.

## 6. Conclusiones

- Todos los Paso 0 se cumplen: sí.
- Las 12 tablas regeneradas reproducen el v13 con θ = 0.02 desde JSON en todas sus celdas numéricas, salvo las erratas del v13 listadas en §7(b).
- La mayor diferencia en pp entre θ = 0 y θ = 0.02 es 1.90 pp (tab:dgp2, `dgp2_delta3_n1000`).
- AWB con θ = 0: la regla B9.5 sí recomienda la variante (4 de 6 celdas de DGP 3 dentro; pérdida máxima 2.90 pp).
- De las 46 cifras del texto del v13 localizadas, 44 se reproducen desde JSON con θ = 0.02; las demás están en §7(b).
- B13.T: tres tabulares nuevos (tab:serial, tab:serialpower, tab:initial) sólo desde JSON de A12.
- B13.Q: tab:attrib exportado desde JSON; 90 de 91 celdas del bloque TRANSCRIBED coinciden y la única distinta es un doble redondeo del v14.
- B13.Q: 373 cifras del v14 recalculadas; 3 no se reproducen y 1 comprobaciones cualitativas no se cumplen (§7(d)); 5 cifras sin JSON localizado.
- B13.Q: 9 apariciones prohibidas de las frases de Q4; seis figuras `_audit13q` con «MSB-B»; faltan 48 valores críticos del suplemento prometido.

## 7. Anomalías y contradicciones con el manuscrito

### (a) Anomalías numéricas

- tab:size con θ = 0, celda `ct|100`: 0.0524 [0.0504, 0.0543], fuera de la región exacta de N = 50000.
- Con θ = 0, en el caso de tendencia el valor crítico de n = 20 000 da estos tamaños: n = 60: 0.0199; n = 100: 0.0323; n = 150: 0.0412; n = 200: 0.0413; n = 500: 0.0472; n = 1000: 0.0508; n = 2000: 0.0486; n = 5000: 0.0510. Con θ = 0.02 se quedaban dentro o cerca de la región (tab:calib).
- Aplicación, tamaño fuera de muestra de RM-GLS θ = 0, AWB a D = 250: 0.0432, fuera de la región [0.044, 0.0562] (N = 5000).

### (b) Erratas del v13 halladas en la transcripción

- tab:calib, fila Constant / 60, columna 1: el v13 imprime 0.0541 sin negrita, pero la cifra está fuera de la región de la nota.
- tab:calib, fila Trend / 60, columna 3: el v13 imprime 0.0534 sin negrita, pero la cifra está fuera de la región de la nota.
- tab:ctpower, fila 0.95 / 200, columna 7: impreso 0.151; el valor del JSON es 0.150461 y a 3 decimales da 0.150. El impreso es un doble redondeo.
- tab:awb, fila Gaussian random walk / 500, columna 2: impreso 0.119; el valor del JSON es 0.118469 y a 3 decimales da 0.118. El impreso es un doble redondeo.
- tab:fp, fila DF-GLS (MAIC), columna 1: impreso 0.274; el valor del JSON es 0.273469 y a 3 decimales da 0.273. El impreso es un doble redondeo.
- Texto `v13/sec5_montecarlo.tex:226` (`power_adf`): impreso 42; recalculado con θ = 0.02: 41.0600 (max_margin_cell: dgp1_rho0p99_n1000; max_margin_pp: 41.0600; minus_adf_pp: 42.5200; minus_pp_pp: 41.0600).
- Texto `v13/sec5_montecarlo.tex:644` (`dgp5`): impreso 10, 29; recalculado con θ = 0.02: 7.8500, 28.5000 (cells: 21; exceeds_bootstrap_r_ge_1.5: sí; exceeds_union_r_le_1.25: sí; union_dominates_interior: sí; min_table_rows_pp: 19.5000; max_table_rows_pp: 28.5000; table_rows: 12; min_cell: dgp5_n200_rho0.90_r1.1).

### (c) Frases del v13 cuya cifra cambia con θ = 0

| Archivo:línea | Clave | Impreso (θ = 0.02) | Con θ = 0, mismos decimales |
|---|---|---|---|
| `v13/sec5_montecarlo.tex:23` | size_max | 0.24, 150, 0.0476 | 0.24, 100, 0.0524 |
| `v13/sec5_montecarlo.tex:63` | calib_limit | 0.0785, 0.0638, 0.0574, 0.0541, 0.0517, 0.0510 | 0.0607, 0.0588, 0.0556, 0.0544, 0.0516, 0.0514 |
| `v13/sec5_montecarlo.tex:70` | calib_ks | 0.097, 0.016 | 0.096, 0.015 |
| `v13/sec1_introduction.tex:56` | intro_limit | 0.0574, 0.0510 | 0.0556, 0.0514 |
| `v13/main.tex:88` | abstract_limit | 0.057 | 0.056 |
| `v13/sec5_montecarlo.tex:143` | lp_gap | 2.3, 3.5, 1.0 | 1.8, 2.6, 0.7 |
| `v13/sec5_montecarlo.tex:147` | lp_trend | 1.4 | 1.2 |
| `v13/sec1_introduction.tex:76` | intro_lp | 3.5 | 2.6 |
| `v13/main.tex:90` | abstract_lp | 3.5 | 2.6 |
| `v13/highlights.tex:5` | highlights_lp | 3.5 | 2.6 |
| `v13/sec5_montecarlo.tex:218` | power_n200 | 6.7, 0.993, 0.926, 5.1, 3.5, 4.7, 0.057, 1.7, 0.003 | 6.8, 0.993, 0.926, 5.6, 3.5, 4.7, 0.002, 1.1, 0.045 |
| `v13/sec1_introduction.tex:73` | intro_power | 6.7, 5.1, 1.7 | 6.8, 5.6, 1.1 |
| `v13/main.tex:92` | abstract_power | 6.7, 2.6 | 6.8, 1.8 |
| `v13/sec5_montecarlo.tex:224` | power_n500 | 1.1, 2.0, 2.6 | 1.6, 1.5, 1.8 |
| `v13/sec5_montecarlo.tex:227` | power_trend | 10.3, 5.9, five | 9.9, 6.2, five |
| `v13/sec5_montecarlo.tex:378` | dgp2 | 0.706, 0.695, 0.057, 0.017, 0.474, 0.445, 0.573, 0.441, 1.000, 0.870, 0.637, 0.376 | 0.713, 0.695, 0.002, 0.064, 0.477, 0.445, 0.578, 0.441, 1.000, 0.870, 0.656, 0.376 |
| `v13/sec5_montecarlo.tex:387` | za_delta0 | 0.119, 0.706 | 0.119, 0.713 |
| `v13/sec5_montecarlo.tex:425` | dgp3 | 0.128, 0.131, 0.127 | 0.123, 0.127, 0.125 |
| `v13/sec1_introduction.tex:81` | intro_dgp3 | 0.128, 0.040, 3 | 0.123, 0.041, 3 |
| `v13/sec5_montecarlo.tex:436` | awb_rates | 0.054, 0.057, 0.082, 0.087, 0.040, 0.124, 0.118 | 0.052, 0.051, 0.080, 0.088, 0.041, 0.117, 0.117 |
| `v13/sec5_montecarlo.tex:440` | awb_homosk | 0.052, 0.043 | 0.052, 0.044 |
| `v13/sec5_montecarlo.tex:441` | awb_cost | 3.0, 1.3 | 2.9, 1.8 |
| `v13/sec5_montecarlo.tex:535` | misspec_heavy | 0.043, 0.042 | 0.044, 0.043 |
| `v13/sec5_montecarlo.tex:541` | misspec_shift1000 | 0.36 | 0.33 |
| `v13/sec5_montecarlo.tex:644` | dgp5 | 10, 29 | 8, 29 |
| `v13/appB_critical_values.tex:10` | appB_cv | 0.222, 0.229 | 0.232, 0.236 |
| `v13/sec6_application.tex:40` | app_oos | 0.0468, 0.0478, 0.0478, 0.0490 | 0.0472, 0.0482, 0.0468, 0.0482 |
| `v13/sec6_application.tex:48` | app_fp | 0.0229 | 0.0224 |
| `v13/sec6_application.tex:52` | app_mzt | 22.1, 29.6 | 22.1, 29.7 |
| `v13/sec6_application.tex:53` | app_awb | 0.0220, 15 | 0.0217, 13 |
| `v13/sec6_application.tex:56` | app_target | 0.0227 | 0.0222 |
| `v13/sec6_application.tex:59` | app_latency_c | 102.5, 93.6, 79.7 | 102.6, 93.6, 79.7 |
| `v13/sec6_application.tex:129` | dev_statistic | 0.0277, 0.0229, 13, 17, 33.8, 29.6 | 0.0277, 0.0224, 13, 17, 33.8, 29.7 |
| `v13/sec6_application.tex:137` | dev_awb | 0.0229, 0.0220, 17, 15, 29.6, 32.8 | 0.0224, 0.0217, 17, 13, 29.7, 40.3 |

### (d) B13.Q: cifras y frases del v14 que no se sostienen

- `v14/sec5_montecarlo.tex:75` (`sec5_calib_out`): impreso 0.13; recalculado 0.14; cifra correcta 0.14.
- `v14/sec5_montecarlo.tex:141` (`sec5_lp_se`): impreso 0.0035; recalculado 0.00353551; cifra correcta 0.0036 (cota superior incumplida).
- `v14/sec5_montecarlo.tex:602` (`sec5_dgp5b`): impreso 8; recalculado 7.95; cifra correcta 7 (cota inferior incumplida).
- `v14/sec5_montecarlo.tex:329` (`sec5_serial2`): no se cumple «MSB-GLS y MZ_t-GLS a menos de medio punto de (b) en todas las celdas (max 0.57 pp, celda ma_m0p8 n = 500 c)».
- tab:attrib (bloque TRANSCRIBED del v14), fila $c = 5$: impreso 0.275, correcto 0.274 (doble redondeo).
- Frase prohibida «two-channel» en `v14/main.tex:103` (zona main).
- Frase prohibida «rolling means» en `v14/sec1_introduction.tex:38` (zona 1).
- Frase prohibida «rolling means» en `v14/sec1_introduction.tex:41` (zona 1).
- Frase prohibida «two-channel» en `v14/sec1_introduction.tex:43` (zona 1).
- Frase prohibida «rolling means» en `v14/sec3_theory.tex:130` (zona 3.3).
- Frase prohibida «rolling means» en `v14/sec3_theory.tex:132` (zona 3.3).
- Frase prohibida «rolling means» en `v14/appA_proofs.tex:11` (zona A.1).
- Frase prohibida «two-channel» en `v14/highlights.tex:7` (zona highlights).
- Frase prohibida «two-channel» en `v14/cover_letter.md:15` (zona cover_letter).

## Anexo: tabla maestra de los números nuevos

| Clave | Valor | IC/EE | N_sim | N_cal | Familia | JSON | Ruta |
|---|---|---|---|---|---|---|---|
| tab:size dm\|60 | 0.0507 | [0.0488, 0.0526] | 50000 | 500000 | 141 | e_size_audit13.json | cells.dm\|60.rates.gls_t0 |
| tab:size ct\|60 | 0.0503 | [0.0484, 0.0523] | 50000 | 500000 | 141 | e_size_audit13.json | cells.ct\|60.rates.gls_t0 |
| tab:size dm\|100 | 0.0501 | [0.0482, 0.0520] | 50000 | 500000 | 141 | e_size_audit13.json | cells.dm\|100.rates.gls_t0 |
| tab:size ct\|100 | 0.0524 | [0.0504, 0.0543] | 50000 | 500000 | 141 | e_size_audit13.json | cells.ct\|100.rates.gls_t0 |
| tab:size dm\|150 | 0.0487 | [0.0469, 0.0507] | 50000 | 500000 | 141 | e_size_audit13.json | cells.dm\|150.rates.gls_t0 |
| tab:size ct\|150 | 0.0494 | [0.0475, 0.0513] | 50000 | 500000 | 141 | e_size_audit13.json | cells.ct\|150.rates.gls_t0 |
| tab:size dm\|200 | 0.0502 | [0.0489, 0.0516] | 100000 | 500000 | 111 | e_size_audit13.json | cells.dm\|200.rates.gls_t0 |
| tab:size ct\|200 | 0.0499 | [0.0486, 0.0513] | 100000 | 500000 | 111 | e_size_audit13.json | cells.ct\|200.rates.gls_t0 |
| tab:size dm\|500 | 0.0492 | [0.0478, 0.0505] | 100000 | 500000 | 111 | e_size_audit13.json | cells.dm\|500.rates.gls_t0 |
| tab:size ct\|500 | 0.0502 | [0.0489, 0.0516] | 100000 | 500000 | 111 | e_size_audit13.json | cells.ct\|500.rates.gls_t0 |
| tab:size dm\|1000 | 0.0491 | [0.0478, 0.0505] | 100000 | 500000 | 111 | e_size_audit13.json | cells.dm\|1000.rates.gls_t0 |
| tab:size ct\|1000 | 0.0505 | [0.0492, 0.0519] | 100000 | 500000 | 111 | e_size_audit13.json | cells.ct\|1000.rates.gls_t0 |
| tab:calib c n=60 tamaño en q(n) | 0.0544 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.60.size_with_cv_at_n |
| tab:calib c n=60 tamaño en q(20 000) | 0.0607 | EE 0.0017 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.60.size_with_cv_n20000 |
| tab:calib c n=60 q_0.05(n) | 0.2328 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.60.cv_at_n |
| tab:calib c n=100 tamaño en q(n) | 0.0516 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.100.size_with_cv_at_n |
| tab:calib c n=100 tamaño en q(20 000) | 0.0588 | EE 0.0017 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.100.size_with_cv_n20000 |
| tab:calib c n=100 q_0.05(n) | 0.2321 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.100.cv_at_n |
| tab:calib c n=150 tamaño en q(n) | 0.0496 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.150.size_with_cv_at_n |
| tab:calib c n=150 tamaño en q(20 000) | 0.0563 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.150.size_with_cv_n20000 |
| tab:calib c n=150 q_0.05(n) | 0.2321 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.150.cv_at_n |
| tab:calib c n=200 tamaño en q(n) | 0.0514 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.200.size_with_cv_at_n |
| tab:calib c n=200 tamaño en q(20 000) | 0.0556 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.200.size_with_cv_n20000 |
| tab:calib c n=200 q_0.05(n) | 0.2331 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.200.cv_at_n |
| tab:calib c n=500 tamaño en q(n) | 0.0473 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.500.size_with_cv_at_n |
| tab:calib c n=500 tamaño en q(20 000) | 0.0484 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.500.size_with_cv_n20000 |
| tab:calib c n=500 q_0.05(n) | 0.2357 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.500.cv_at_n |
| tab:calib c n=1000 tamaño en q(n) | 0.0510 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.1000.size_with_cv_at_n |
| tab:calib c n=1000 tamaño en q(20 000) | 0.0518 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.1000.size_with_cv_n20000 |
| tab:calib c n=1000 q_0.05(n) | 0.2362 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.1000.cv_at_n |
| tab:calib c n=2000 tamaño en q(n) | 0.0470 | EE 0.0015 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.2000.size_with_cv_at_n |
| tab:calib c n=2000 tamaño en q(20 000) | 0.0478 | EE 0.0015 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.2000.size_with_cv_n20000 |
| tab:calib c n=2000 q_0.05(n) | 0.2360 | — | — | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.2000.cv_at_n |
| tab:calib c n=5000 tamaño en q(n) | 0.0490 | EE 0.0015 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.5000.size_with_cv_at_n |
| tab:calib c n=5000 tamaño en q(20 000) | 0.0488 | EE 0.0015 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.5000.size_with_cv_n20000 |
| tab:calib c n=5000 q_0.05(n) | 0.2370 | — | — | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.c.approximation_cost.5000.cv_at_n |
| tab:calib ct n=60 tamaño en q(n) | 0.0520 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.60.size_with_cv_at_n |
| tab:calib ct n=60 tamaño en q(20 000) | 0.0199 | EE 0.0010 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.60.size_with_cv_n20000 |
| tab:calib ct n=60 q_0.05(n) | 0.1847 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.60.cv_at_n |
| tab:calib ct n=100 tamaño en q(n) | 0.0481 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.100.size_with_cv_at_n |
| tab:calib ct n=100 tamaño en q(20 000) | 0.0323 | EE 0.0013 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.100.size_with_cv_n20000 |
| tab:calib ct n=100 q_0.05(n) | 0.1780 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.100.cv_at_n |
| tab:calib ct n=150 tamaño en q(n) | 0.0507 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.150.size_with_cv_at_n |
| tab:calib ct n=150 tamaño en q(20 000) | 0.0412 | EE 0.0014 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.150.size_with_cv_n20000 |
| tab:calib ct n=150 q_0.05(n) | 0.1755 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.150.cv_at_n |
| tab:calib ct n=200 tamaño en q(n) | 0.0480 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.200.size_with_cv_at_n |
| tab:calib ct n=200 tamaño en q(20 000) | 0.0413 | EE 0.0014 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.200.size_with_cv_n20000 |
| tab:calib ct n=200 q_0.05(n) | 0.1740 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.200.cv_at_n |
| tab:calib ct n=500 tamaño en q(n) | 0.0490 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.500.size_with_cv_at_n |
| tab:calib ct n=500 tamaño en q(20 000) | 0.0472 | EE 0.0015 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.500.size_with_cv_n20000 |
| tab:calib ct n=500 q_0.05(n) | 0.1722 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.500.cv_at_n |
| tab:calib ct n=1000 tamaño en q(n) | 0.0512 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.1000.size_with_cv_at_n |
| tab:calib ct n=1000 tamaño en q(20 000) | 0.0508 | EE 0.0016 | 20000 | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.1000.size_with_cv_n20000 |
| tab:calib ct n=1000 q_0.05(n) | 0.1715 | — | — | audit10_cal (N_cal = 500000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.1000.cv_at_n |
| tab:calib ct n=2000 tamaño en q(n) | 0.0478 | EE 0.0015 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.2000.size_with_cv_at_n |
| tab:calib ct n=2000 tamaño en q(20 000) | 0.0486 | EE 0.0015 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.2000.size_with_cv_n20000 |
| tab:calib ct n=2000 q_0.05(n) | 0.1710 | — | — | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.2000.cv_at_n |
| tab:calib ct n=5000 tamaño en q(n) | 0.0517 | EE 0.0016 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.5000.size_with_cv_at_n |
| tab:calib ct n=5000 tamaño en q(20 000) | 0.0510 | EE 0.0016 | 20000 | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.5000.size_with_cv_n20000 |
| tab:calib ct n=5000 q_0.05(n) | 0.1717 | — | — | audit9_cal (N_cal = 50000) | 102 / 104 | e_calib_audit13.json | cases_by_theta.gls_t0.ct.approximation_cost.5000.cv_at_n |
| tab:localpower dm c=0.0 | 0.0488 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.0.0.gls_t0 |
| tab:localpower dm c=1.0 | 0.0732 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.1.0.gls_t0 |
| tab:localpower dm c=2.0 | 0.1108 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.2.0.gls_t0 |
| tab:localpower dm c=3.0 | 0.1624 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.3.0.gls_t0 |
| tab:localpower dm c=4.0 | 0.2215 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.4.0.gls_t0 |
| tab:localpower dm c=5.0 | 0.2949 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.5.0.gls_t0 |
| tab:localpower dm c=6.0 | 0.3702 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.6.0.gls_t0 |
| tab:localpower dm c=7.0 | 0.4640 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.7.0.gls_t0 |
| tab:localpower dm c=8.0 | 0.5561 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.8.0.gls_t0 |
| tab:localpower dm c=9.0 | 0.6399 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.9.0.gls_t0 |
| tab:localpower dm c=10.0 | 0.7243 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.10.0.gls_t0 |
| tab:localpower dm c=11.0 | 0.7931 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.11.0.gls_t0 |
| tab:localpower dm c=12.0 | 0.8470 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.12.0.gls_t0 |
| tab:localpower dm c=13.0 | 0.9010 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.13.0.gls_t0 |
| tab:localpower dm c=13.5 | 0.9195 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.13.5.gls_t0 |
| tab:localpower dm c=14.0 | 0.9373 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.14.0.gls_t0 |
| tab:localpower dm c=15.0 | 0.9580 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.15.0.gls_t0 |
| tab:localpower dm c=16.0 | 0.9722 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.16.0.gls_t0 |
| tab:localpower dm c=17.0 | 0.9849 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.17.0.gls_t0 |
| tab:localpower dm c=18.0 | 0.9910 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.18.0.gls_t0 |
| tab:localpower dm c=19.0 | 0.9960 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.19.0.gls_t0 |
| tab:localpower dm c=20.0 | 0.9977 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.20.0.gls_t0 |
| tab:localpower dm c=21.0 | 0.9991 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.21.0.gls_t0 |
| tab:localpower dm c=22.0 | 0.9993 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.22.0.gls_t0 |
| tab:localpower dm c=23.0 | 0.9998 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.23.0.gls_t0 |
| tab:localpower dm c=24.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.24.0.gls_t0 |
| tab:localpower dm c=25.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.25.0.gls_t0 |
| tab:localpower dm c=26.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.26.0.gls_t0 |
| tab:localpower dm c=27.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.27.0.gls_t0 |
| tab:localpower dm c=28.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.28.0.gls_t0 |
| tab:localpower dm c=29.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.29.0.gls_t0 |
| tab:localpower dm c=30.0 | 1.0000 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.dm.power.30.0.gls_t0 |
| tab:localpower ct c=0.0 | 0.0493 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.0.0.gls_t0 |
| tab:localpower ct c=1.0 | 0.0515 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.1.0.gls_t0 |
| tab:localpower ct c=2.0 | 0.0609 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.2.0.gls_t0 |
| tab:localpower ct c=3.0 | 0.0746 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.3.0.gls_t0 |
| tab:localpower ct c=4.0 | 0.0877 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.4.0.gls_t0 |
| tab:localpower ct c=5.0 | 0.1124 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.5.0.gls_t0 |
| tab:localpower ct c=6.0 | 0.1373 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.6.0.gls_t0 |
| tab:localpower ct c=7.0 | 0.1706 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.7.0.gls_t0 |
| tab:localpower ct c=8.0 | 0.2119 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.8.0.gls_t0 |
| tab:localpower ct c=9.0 | 0.2478 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.9.0.gls_t0 |
| tab:localpower ct c=10.0 | 0.2964 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.10.0.gls_t0 |
| tab:localpower ct c=11.0 | 0.3555 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.11.0.gls_t0 |
| tab:localpower ct c=12.0 | 0.4111 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.12.0.gls_t0 |
| tab:localpower ct c=13.0 | 0.4646 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.13.0.gls_t0 |
| tab:localpower ct c=13.5 | 0.4984 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.13.5.gls_t0 |
| tab:localpower ct c=14.0 | 0.5292 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.14.0.gls_t0 |
| tab:localpower ct c=15.0 | 0.5877 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.15.0.gls_t0 |
| tab:localpower ct c=16.0 | 0.6523 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.16.0.gls_t0 |
| tab:localpower ct c=17.0 | 0.7009 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.17.0.gls_t0 |
| tab:localpower ct c=18.0 | 0.7577 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.18.0.gls_t0 |
| tab:localpower ct c=19.0 | 0.7978 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.19.0.gls_t0 |
| tab:localpower ct c=20.0 | 0.8464 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.20.0.gls_t0 |
| tab:localpower ct c=21.0 | 0.8814 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.21.0.gls_t0 |
| tab:localpower ct c=22.0 | 0.9104 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.22.0.gls_t0 |
| tab:localpower ct c=23.0 | 0.9323 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.23.0.gls_t0 |
| tab:localpower ct c=24.0 | 0.9503 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.24.0.gls_t0 |
| tab:localpower ct c=25.0 | 0.9636 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.25.0.gls_t0 |
| tab:localpower ct c=26.0 | 0.9747 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.26.0.gls_t0 |
| tab:localpower ct c=27.0 | 0.9847 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.27.0.gls_t0 |
| tab:localpower ct c=28.0 | 0.9888 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.28.0.gls_t0 |
| tab:localpower ct c=29.0 | 0.9915 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.29.0.gls_t0 |
| tab:localpower ct c=30.0 | 0.9954 | — | 20000 | 50000 | 102 | b92_theta_audit9.json | local_power.ct.power.30.0.gls_t0 |
| dgp1_rho0p8_n200 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1.67e-52 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p8_n200.rates_sim.gls_t0 |
| dgp1_rho0p8_n500 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p8_n500.rates_sim.gls_t0 |
| dgp1_rho0p8_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p8_n1000.rates_sim.gls_t0 |
| dgp1_rho0p85_n200 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 7.24e-71 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p85_n200.rates_sim.gls_t0 |
| dgp1_rho0p85_n500 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p85_n500.rates_sim.gls_t0 |
| dgp1_rho0p85_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p85_n1000.rates_sim.gls_t0 |
| dgp1_rho0p9_n200 RM-GLS θ=0 | 0.9934 | EE 0.0011; McNemar p vs DF-GLS 1.93e-84 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p9_n200.rates_sim.gls_t0 |
| dgp1_rho0p9_n500 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 0.25 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p9_n500.rates_sim.gls_t0 |
| dgp1_rho0p9_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p9_n1000.rates_sim.gls_t0 |
| dgp1_rho0p93_n200 RM-GLS θ=0 | 0.9102 | EE 0.0040; McNemar p vs DF-GLS 3.3e-30 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p93_n200.rates_sim.gls_t0 |
| dgp1_rho0p93_n500 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 3.05e-05 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p93_n500.rates_sim.gls_t0 |
| dgp1_rho0p93_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p93_n1000.rates_sim.gls_t0 |
| dgp1_rho0p95_n200 RM-GLS θ=0 | 0.7080 | EE 0.0064; McNemar p vs DF-GLS 0.00202 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p95_n200.rates_sim.gls_t0 |
| dgp1_rho0p95_n500 RM-GLS θ=0 | 0.9998 | EE 0.0002; McNemar p vs DF-GLS 9.09e-13 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p95_n500.rates_sim.gls_t0 |
| dgp1_rho0p95_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p95_n1000.rates_sim.gls_t0 |
| dgp1_rho0p97_n200 RM-GLS θ=0 | 0.3864 | EE 0.0069; McNemar p vs DF-GLS 0.0445 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p97_n200.rates_sim.gls_t0 |
| dgp1_rho0p97_n500 RM-GLS θ=0 | 0.9550 | EE 0.0029; McNemar p vs DF-GLS 1.82e-06 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p97_n500.rates_sim.gls_t0 |
| dgp1_rho0p97_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p97_n1000.rates_sim.gls_t0 |
| dgp1_rho0p99_n200 RM-GLS θ=0 | 0.1148 | EE 0.0045; McNemar p vs DF-GLS 0.244 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p99_n200.rates_sim.gls_t0 |
| dgp1_rho0p99_n500 RM-GLS θ=0 | 0.3008 | EE 0.0065; McNemar p vs DF-GLS 0.00104 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p99_n500.rates_sim.gls_t0 |
| dgp1_rho0p99_n1000 RM-GLS θ=0 | 0.7370 | EE 0.0062; McNemar p vs DF-GLS 0.000162 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp1_rho0p99_n1000.rates_sim.gls_t0 |
| dgp2_delta0_n200 RM-GLS θ=0 | 0.7126 | EE 0.0064; McNemar p vs DF-GLS 0.00204 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta0_n200.rates_sim.gls_t0 |
| dgp2_delta0_n500 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 3.73e-09 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta0_n500.rates_sim.gls_t0 |
| dgp2_delta0_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta0_n1000.rates_sim.gls_t0 |
| dgp2_delta0p5_n200 RM-GLS θ=0 | 0.6396 | EE 0.0068; McNemar p vs DF-GLS 0.00118 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta0p5_n200.rates_sim.gls_t0 |
| dgp2_delta0p5_n500 RM-GLS θ=0 | 0.9998 | EE 0.0002; McNemar p vs DF-GLS 2.25e-24 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta0p5_n500.rates_sim.gls_t0 |
| dgp2_delta0p5_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta0p5_n1000.rates_sim.gls_t0 |
| dgp2_delta1_n200 RM-GLS θ=0 | 0.4770 | EE 0.0071; McNemar p vs DF-GLS 1.36e-07 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta1_n200.rates_sim.gls_t0 |
| dgp2_delta1_n500 RM-GLS θ=0 | 0.9904 | EE 0.0014; McNemar p vs DF-GLS 6.29e-73 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta1_n500.rates_sim.gls_t0 |
| dgp2_delta1_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 3.05e-05 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta1_n1000.rates_sim.gls_t0 |
| dgp2_delta2_n200 RM-GLS θ=0 | 0.0930 | EE 0.0041; McNemar p vs DF-GLS 0.00477 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta2_n200.rates_sim.gls_t0 |
| dgp2_delta2_n500 RM-GLS θ=0 | 0.5780 | EE 0.0070; McNemar p vs DF-GLS 1.47e-87 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta2_n500.rates_sim.gls_t0 |
| dgp2_delta2_n1000 RM-GLS θ=0 | 0.9998 | EE 0.0002; McNemar p vs DF-GLS 2.14e-196 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta2_n1000.rates_sim.gls_t0 |
| dgp2_delta3_n200 RM-GLS θ=0 | 0.0030 | EE 0.0008; McNemar p vs DF-GLS 0.0636 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta3_n200.rates_sim.gls_t0 |
| dgp2_delta3_n500 RM-GLS θ=0 | 0.0228 | EE 0.0021; McNemar p vs DF-GLS 0.00721 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta3_n500.rates_sim.gls_t0 |
| dgp2_delta3_n1000 RM-GLS θ=0 | 0.6560 | EE 0.0067; McNemar p vs DF-GLS 4.12e-272 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta3_n1000.rates_sim.gls_t0 |
| dgp2_delta5_n200 RM-GLS θ=0 | 0.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta5_n200.rates_sim.gls_t0 |
| dgp2_delta5_n500 RM-GLS θ=0 | 0.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta5_n500.rates_sim.gls_t0 |
| dgp2_delta5_n1000 RM-GLS θ=0 | 0.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp2_delta5_n1000.rates_sim.gls_t0 |
| ct_power_rho0p9_n200 RM-GLS θ=0 | 0.8194 | EE 0.0054; McNemar p vs DF-GLS 7.74e-64 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p9_n200.rates_sim.gls_t0 |
| ct_power_rho0p9_n500 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 6.62e-24 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p9_n500.rates_sim.gls_t0 |
| ct_power_rho0p9_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p9_n1000.rates_sim.gls_t0 |
| ct_power_rho0p95_n200 RM-GLS θ=0 | 0.2974 | EE 0.0065; McNemar p vs DF-GLS 0.124 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p95_n200.rates_sim.gls_t0 |
| ct_power_rho0p95_n500 RM-GLS θ=0 | 0.9602 | EE 0.0028; McNemar p vs DF-GLS 4.44e-57 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p95_n500.rates_sim.gls_t0 |
| ct_power_rho0p95_n1000 RM-GLS θ=0 | 1.0000 | EE 0.0000; McNemar p vs DF-GLS 0.00391 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p95_n1000.rates_sim.gls_t0 |
| ct_power_rho0p97_n200 RM-GLS θ=0 | 0.1324 | EE 0.0048; McNemar p vs DF-GLS 0.555 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p97_n200.rates_sim.gls_t0 |
| ct_power_rho0p97_n500 RM-GLS θ=0 | 0.5894 | EE 0.0070; McNemar p vs DF-GLS 0.00401 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p97_n500.rates_sim.gls_t0 |
| ct_power_rho0p97_n1000 RM-GLS θ=0 | 0.9942 | EE 0.0011; McNemar p vs DF-GLS 2.31e-21 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p97_n1000.rates_sim.gls_t0 |
| ct_power_rho0p99_n200 RM-GLS θ=0 | 0.0618 | EE 0.0034; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p99_n200.rates_sim.gls_t0 |
| ct_power_rho0p99_n500 RM-GLS θ=0 | 0.0994 | EE 0.0042; McNemar p vs DF-GLS 0.311 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p99_n500.rates_sim.gls_t0 |
| ct_power_rho0p99_n1000 RM-GLS θ=0 | 0.3054 | EE 0.0065; McNemar p vs DF-GLS 0.657 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.ct_power_rho0p99_n1000.rates_sim.gls_t0 |
| dgp3_r1_n200 RM-GLS θ=0 | 0.0462 | EE 0.0030; McNemar p vs DF-GLS 0.327 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r1_n200.rates_sim.gls_t0 |
| dgp3_r1_n500 RM-GLS θ=0 | 0.0472 | EE 0.0030; McNemar p vs DF-GLS 1 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r1_n500.rates_sim.gls_t0 |
| dgp3_r1_n1000 RM-GLS θ=0 | 0.0482 | EE 0.0030; McNemar p vs DF-GLS 0.213 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r1_n1000.rates_sim.gls_t0 |
| dgp3_r1p5_n200 RM-GLS θ=0 | 0.0650 | EE 0.0035; McNemar p vs DF-GLS 0.00317 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r1p5_n200.rates_sim.gls_t0 |
| dgp3_r1p5_n500 RM-GLS θ=0 | 0.0606 | EE 0.0034; McNemar p vs DF-GLS 0.0111 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r1p5_n500.rates_sim.gls_t0 |
| dgp3_r1p5_n1000 RM-GLS θ=0 | 0.0580 | EE 0.0033; McNemar p vs DF-GLS 0.00246 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r1p5_n1000.rates_sim.gls_t0 |
| dgp3_r2_n200 RM-GLS θ=0 | 0.0764 | EE 0.0038; McNemar p vs DF-GLS 5.36e-12 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r2_n200.rates_sim.gls_t0 |
| dgp3_r2_n500 RM-GLS θ=0 | 0.0738 | EE 0.0037; McNemar p vs DF-GLS 0.000389 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r2_n500.rates_sim.gls_t0 |
| dgp3_r2_n1000 RM-GLS θ=0 | 0.0722 | EE 0.0037; McNemar p vs DF-GLS 0.00125 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r2_n1000.rates_sim.gls_t0 |
| dgp3_r3_n200 RM-GLS θ=0 | 0.1004 | EE 0.0043; McNemar p vs DF-GLS 1.25e-15 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r3_n200.rates_sim.gls_t0 |
| dgp3_r3_n500 RM-GLS θ=0 | 0.1016 | EE 0.0043; McNemar p vs DF-GLS 2.14e-08 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r3_n500.rates_sim.gls_t0 |
| dgp3_r3_n1000 RM-GLS θ=0 | 0.1044 | EE 0.0043; McNemar p vs DF-GLS 1.67e-12 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r3_n1000.rates_sim.gls_t0 |
| dgp3_r4_n200 RM-GLS θ=0 | 0.1226 | EE 0.0046; McNemar p vs DF-GLS 6.16e-29 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r4_n200.rates_sim.gls_t0 |
| dgp3_r4_n500 RM-GLS θ=0 | 0.1268 | EE 0.0047; McNemar p vs DF-GLS 7.27e-16 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r4_n500.rates_sim.gls_t0 |
| dgp3_r4_n1000 RM-GLS θ=0 | 0.1252 | EE 0.0047; McNemar p vs DF-GLS 3.32e-18 | 5000 | 500000 | 95 | e_equalized_audit13.json | cells.dgp3_r4_n1000.rates_sim.gls_t0 |
| tab:misspec c\|heavy_t5_n200 | 0.0438 | EE 0.0029 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|heavy_t5_n200.rates.gls_t0 |
| tab:misspec c\|heavy_t5_n500 | 0.0510 | EE 0.0031 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|heavy_t5_n500.rates.gls_t0 |
| tab:misspec c\|heavy_t5_n1000 | 0.0486 | EE 0.0030 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|heavy_t5_n1000.rates.gls_t0 |
| tab:misspec c\|heavy_t3_n200 | 0.0428 | EE 0.0029 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|heavy_t3_n200.rates.gls_t0 |
| tab:misspec c\|heavy_t3_n500 | 0.0502 | EE 0.0031 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|heavy_t3_n500.rates.gls_t0 |
| tab:misspec c\|heavy_t3_n1000 | 0.0470 | EE 0.0030 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|heavy_t3_n1000.rates.gls_t0 |
| tab:misspec c\|garch_base_n200 | 0.0500 | EE 0.0031 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_base_n200.rates.gls_t0 |
| tab:misspec c\|garch_base_n500 | 0.0554 | EE 0.0032 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_base_n500.rates.gls_t0 |
| tab:misspec c\|garch_base_n1000 | 0.0480 | EE 0.0030 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_base_n1000.rates.gls_t0 |
| tab:misspec c\|garch_p099_n200 | 0.0602 | EE 0.0034 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p099_n200.rates.gls_t0 |
| tab:misspec c\|garch_p099_n500 | 0.0596 | EE 0.0033 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p099_n500.rates.gls_t0 |
| tab:misspec c\|garch_p099_n1000 | 0.0614 | EE 0.0034 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p099_n1000.rates.gls_t0 |
| tab:misspec c\|garch_p099_n2000 | 0.0548 | EE 0.0032 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p099_n2000.rates.gls_t0 |
| tab:misspec c\|garch_p099_n5000 | 0.0546 | EE 0.0032 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p099_n5000.rates.gls_t0 |
| tab:misspec c\|garch_p098_n200 | 0.0606 | EE 0.0034 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p098_n200.rates.gls_t0 |
| tab:misspec c\|garch_p098_n500 | 0.0576 | EE 0.0033 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p098_n500.rates.gls_t0 |
| tab:misspec c\|garch_p098_n1000 | 0.0514 | EE 0.0031 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p098_n1000.rates.gls_t0 |
| tab:misspec c\|garch_p095_t5_n200 | 0.0550 | EE 0.0032 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p095_t5_n200.rates.gls_t0 |
| tab:misspec c\|garch_p095_t5_n500 | 0.0604 | EE 0.0034 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p095_t5_n500.rates.gls_t0 |
| tab:misspec c\|garch_p095_t5_n1000 | 0.0576 | EE 0.0033 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p095_t5_n1000.rates.gls_t0 |
| tab:misspec c\|garch_p095_t5_n2000 | 0.0560 | EE 0.0033 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p095_t5_n2000.rates.gls_t0 |
| tab:misspec c\|garch_p095_t5_n5000 | 0.0534 | EE 0.0032 | 5000 | 50000 | A7/A8 | b92_theta_audit9.json | misspec.c\|garch_p095_t5_n5000.rates.gls_t0 |
| tab:critB dm\|0\|100 α=0.01 | 0.1907 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|100.cv.0.01 |
| tab:critB dm\|0\|100 α=0.025 | 0.2111 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|100.cv.0.025 |
| tab:critB dm\|0\|100 α=0.05 | 0.2321 | EE 0.0005 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|100.cv.0.05 |
| tab:critB dm\|0\|100 α=0.1 | 0.2623 | EE 0.0005 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|100.cv.0.1 |
| tab:critB dm\|0\|200 α=0.01 | 0.1868 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|200.cv.0.01 |
| tab:critB dm\|0\|200 α=0.025 | 0.2089 | EE 0.0005 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|200.cv.0.025 |
| tab:critB dm\|0\|200 α=0.05 | 0.2328 | EE 0.0005 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|200.cv.0.05 |
| tab:critB dm\|0\|200 α=0.1 | 0.2678 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|200.cv.0.1 |
| tab:critB dm\|0\|500 α=0.01 | 0.1863 | EE 0.0008 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|500.cv.0.01 |
| tab:critB dm\|0\|500 α=0.025 | 0.2102 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|500.cv.0.025 |
| tab:critB dm\|0\|500 α=0.05 | 0.2352 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|500.cv.0.05 |
| tab:critB dm\|0\|500 α=0.1 | 0.2727 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|500.cv.0.1 |
| tab:critB dm\|0\|1000 α=0.01 | 0.1859 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|1000.cv.0.01 |
| tab:critB dm\|0\|1000 α=0.025 | 0.2109 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|1000.cv.0.025 |
| tab:critB dm\|0\|1000 α=0.05 | 0.2362 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|1000.cv.0.05 |
| tab:critB dm\|0\|1000 α=0.1 | 0.2736 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|1000.cv.0.1 |
| tab:critB dm\|0\|2000 α=0.01 | 0.1863 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|2000.cv.0.01 |
| tab:critB dm\|0\|2000 α=0.025 | 0.2103 | EE 0.0005 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|2000.cv.0.025 |
| tab:critB dm\|0\|2000 α=0.05 | 0.2374 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|2000.cv.0.05 |
| tab:critB dm\|0\|2000 α=0.1 | 0.2760 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|2000.cv.0.1 |
| tab:critB dm\|0\|5000 α=0.01 | 0.1844 | EE 0.0006 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|5000.cv.0.01 |
| tab:critB dm\|0\|5000 α=0.025 | 0.2087 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|5000.cv.0.025 |
| tab:critB dm\|0\|5000 α=0.05 | 0.2361 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|5000.cv.0.05 |
| tab:critB dm\|0\|5000 α=0.1 | 0.2753 | EE 0.0007 | — | 100000 | 107 | b103_cv_audit10.json | table.dm\|0\|5000.cv.0.1 |
| tab:critB ct\|0\|100 α=0.01 | 0.1569 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|100.cv.0.01 |
| tab:critB ct\|0\|100 α=0.025 | 0.1676 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|100.cv.0.025 |
| tab:critB ct\|0\|100 α=0.05 | 0.1782 | EE 0.0002 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|100.cv.0.05 |
| tab:critB ct\|0\|100 α=0.1 | 0.1925 | EE 0.0002 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|100.cv.0.1 |
| tab:critB ct\|0\|200 α=0.01 | 0.1498 | EE 0.0004 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|200.cv.0.01 |
| tab:critB ct\|0\|200 α=0.025 | 0.1621 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|200.cv.0.025 |
| tab:critB ct\|0\|200 α=0.05 | 0.1739 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|200.cv.0.05 |
| tab:critB ct\|0\|200 α=0.1 | 0.1898 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|200.cv.0.1 |
| tab:critB ct\|0\|500 α=0.01 | 0.1461 | EE 0.0004 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|500.cv.0.01 |
| tab:critB ct\|0\|500 α=0.025 | 0.1592 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|500.cv.0.025 |
| tab:critB ct\|0\|500 α=0.05 | 0.1719 | EE 0.0002 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|500.cv.0.05 |
| tab:critB ct\|0\|500 α=0.1 | 0.1892 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|500.cv.0.1 |
| tab:critB ct\|0\|1000 α=0.01 | 0.1452 | EE 0.0004 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|1000.cv.0.01 |
| tab:critB ct\|0\|1000 α=0.025 | 0.1582 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|1000.cv.0.025 |
| tab:critB ct\|0\|1000 α=0.05 | 0.1713 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|1000.cv.0.05 |
| tab:critB ct\|0\|1000 α=0.1 | 0.1891 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|1000.cv.0.1 |
| tab:critB ct\|0\|2000 α=0.01 | 0.1440 | EE 0.0005 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|2000.cv.0.01 |
| tab:critB ct\|0\|2000 α=0.025 | 0.1581 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|2000.cv.0.025 |
| tab:critB ct\|0\|2000 α=0.05 | 0.1717 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|2000.cv.0.05 |
| tab:critB ct\|0\|2000 α=0.1 | 0.1893 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|2000.cv.0.1 |
| tab:critB ct\|0\|5000 α=0.01 | 0.1451 | EE 0.0004 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|5000.cv.0.01 |
| tab:critB ct\|0\|5000 α=0.025 | 0.1580 | EE 0.0004 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|5000.cv.0.025 |
| tab:critB ct\|0\|5000 α=0.05 | 0.1709 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|5000.cv.0.05 |
| tab:critB ct\|0\|5000 α=0.1 | 0.1886 | EE 0.0003 | — | 100000 | 107 | b103_cv_audit10.json | table.ct\|0\|5000.cv.0.1 |
| tab:awb dgp3_r1_n200 awb | 0.0400 | [0.0323, 0.0495] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp3_r1_n200.awb |
| tab:awb dgp3_r1_n200 sim | 0.0420 | [0.0341, 0.0517] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp3_r1_n200.sim |
| tab:awb dgp3_r1_n500 awb | 0.0420 | [0.0341, 0.0517] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp3_r1_n500.awb |
| tab:awb dgp3_r1_n500 sim | 0.0515 | [0.0426, 0.0621] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp3_r1_n500.sim |
| tab:awb dgp3_r2_n200 awb | 0.0520 | [0.0431, 0.0626] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp3_r2_n200.awb |
| tab:awb dgp3_r2_n200 sim | 0.0795 | [0.0684, 0.0922] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp3_r2_n200.sim |
| tab:awb dgp3_r2_n500 awb | 0.0505 | [0.0417, 0.0610] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp3_r2_n500.awb |
| tab:awb dgp3_r2_n500 sim | 0.0885 | [0.0768, 0.1017] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp3_r2_n500.sim |
| tab:awb dgp3_r4_n200 awb | 0.0405 | [0.0327, 0.0501] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp3_r4_n200.awb |
| tab:awb dgp3_r4_n200 sim | 0.1175 | [0.1041, 0.1324] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp3_r4_n200.sim |
| tab:awb dgp3_r4_n500 awb | 0.0400 | [0.0323, 0.0495] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp3_r4_n500.awb |
| tab:awb dgp3_r4_n500 sim | 0.1170 | [0.1036, 0.1318] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp3_r4_n500.sim |
| tab:awb garch_base_n200 awb | 0.0420 | [0.0341, 0.0517] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.garch_base_n200.awb |
| tab:awb garch_base_n200 sim | 0.0505 | [0.0417, 0.0610] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.garch_base_n200.sim |
| tab:awb garch_p099_n200 awb | 0.0520 | [0.0431, 0.0626] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.garch_p099_n200.awb |
| tab:awb garch_p099_n200 sim | 0.0610 | [0.0513, 0.0724] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.garch_p099_n200.sim |
| tab:awb garch_p098_n200 awb | 0.0525 | [0.0436, 0.0632] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.garch_p098_n200.awb |
| tab:awb garch_p098_n200 sim | 0.0600 | [0.0504, 0.0713] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.garch_p098_n200.sim |
| tab:awb garch_p095_t5_n200 awb | 0.0425 | [0.0345, 0.0523] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.garch_p095_t5_n200.awb |
| tab:awb garch_p095_t5_n200 sim | 0.0515 | [0.0426, 0.0621] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.garch_p095_t5_n200.sim |
| tab:awb dgp1_rho0p95_n200 awb | 0.6765 | [0.6557, 0.6966] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp1_rho0p95_n200.awb |
| tab:awb dgp1_rho0p95_n200 sim | 0.7055 | [0.6851, 0.7251] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp1_rho0p95_n200.sim |
| tab:awb dgp1_rho0p95_n500 awb | 1.0000 | [0.9981, 1.0000] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp1_rho0p95_n500.awb |
| tab:awb dgp1_rho0p95_n500 sim | 1.0000 | [0.9981, 1.0000] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp1_rho0p95_n500.sim |
| tab:awb dgp1_rho0p99_n200 awb | 0.0980 | [0.0857, 0.1118] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp1_rho0p99_n200.awb |
| tab:awb dgp1_rho0p99_n200 sim | 0.1020 | [0.0895, 0.1160] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp1_rho0p99_n200.sim |
| tab:awb dgp1_rho0p99_n500 awb | 0.2950 | [0.2754, 0.3154] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.dgp1_rho0p99_n500.awb |
| tab:awb dgp1_rho0p99_n500 sim | 0.3130 | [0.2931, 0.3337] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.dgp1_rho0p99_n500.sim |
| tab:awb indep_n200 awb | 0.0525 | [0.0436, 0.0632] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.indep_n200.awb |
| tab:awb indep_n200 sim | 0.0535 | [0.0445, 0.0642] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.indep_n200.sim |
| tab:awb indep_n500 awb | 0.0445 | [0.0363, 0.0544] | 2000 | B = 399 | 142 | e_awb_audit13.json | cells.indep_n500.awb |
| tab:awb indep_n500 sim | 0.0470 | [0.0386, 0.0572] | 2000 | 500000 | 95 | e_awb_audit13.json | cells.indep_n500.sim |
| tab:dgp5 dgp5_n200_rho0.90_r1.0 | 0.9915 | EE 0.0021 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r1.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.90_r2.0 | 0.9850 | EE 0.0027 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r2.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.90_r3.0 | 0.9865 | EE 0.0026 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r3.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.90_r4.0 | 0.9740 | EE 0.0036 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r4.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r1.0 | 0.9135 | EE 0.0063 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r1.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r2.0 | 0.9125 | EE 0.0063 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r2.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r3.0 | 0.8940 | EE 0.0069 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r3.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r4.0 | 0.8810 | EE 0.0072 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r4.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r1.0 | 0.7020 | EE 0.0102 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r1.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r2.0 | 0.7335 | EE 0.0099 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r2.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r3.0 | 0.7205 | EE 0.0100 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r3.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r4.0 | 0.7225 | EE 0.0100 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r4.0.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.90_r1.1 | 0.9910 | EE 0.0021 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r1.1.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.90_r1.25 | 0.9905 | EE 0.0022 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r1.25.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.90_r1.5 | 0.9920 | EE 0.0020 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.90_r1.5.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r1.1 | 0.9120 | EE 0.0063 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r1.1.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r1.25 | 0.9050 | EE 0.0066 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r1.25.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.93_r1.5 | 0.9160 | EE 0.0062 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.93_r1.5.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r1.1 | 0.7205 | EE 0.0100 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r1.1.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r1.25 | 0.7205 | EE 0.0100 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r1.25.size_matched.primary |
| tab:dgp5 dgp5_n200_rho0.95_r1.5 | 0.7125 | EE 0.0101 | 2000 | 5000 | 60 | e_dgp5_audit13.json | cells.dgp5_n200_rho0.95_r1.5.size_matched.primary |
| tab:fp final fp_mean | 0.0224 | — | — | 50000 | — | e_application_audit13.json | summary.final.fp_mean |
| tab:fp final fp_max | 0.2163 | — | — | 50000 | — | e_application_audit13.json | summary.final.fp_max |
| tab:fp final detections | 17 | — | — | 50000 | — | e_application_audit13.json | summary.final.detections |
| tab:fp final mean_latency_detected | 29.7059 | — | — | 50000 | — | e_application_audit13.json | summary.final.mean_latency_detected |
| tab:fp final false_alarm_episodes | 33 | — | — | 50000 | — | e_application_audit13.json | matched_rate.tests.final.false_alarm_episodes |
| tab:fp final mean_run_length | 144.8025 | — | — | 50000 | — | e_application_audit13.json | matched_rate.tests.final.mean_run_length |
| tab:fp final censored_latency_mean | 102.5568 | — | — | 50000 | — | e_application_audit13.json | matched_rate.tests.final.censored_latency_mean |
| tab:fp final_awb fp_mean | 0.0217 | — | — | 50000 | 143 | e_application_audit13.json | summary.final_awb.fp_mean |
| tab:fp final_awb fp_max | 0.2286 | — | — | 50000 | 143 | e_application_audit13.json | summary.final_awb.fp_max |
| tab:fp final_awb detections | 13 | — | — | 50000 | 143 | e_application_audit13.json | summary.final_awb.detections |
| tab:fp final_awb mean_latency_detected | 40.3077 | — | — | 50000 | 143 | e_application_audit13.json | summary.final_awb.mean_latency_detected |
| tab:fp final_awb false_alarm_episodes | 43 | — | — | 50000 | 143 | e_application_audit13.json | matched_rate.tests.final_awb.false_alarm_episodes |
| tab:fp final_awb mean_run_length | 129.1978 | — | — | 50000 | 143 | e_application_audit13.json | matched_rate.tests.final_awb.mean_run_length |
| tab:fp final_awb censored_latency_mean | 108.2273 | — | — | 50000 | 143 | e_application_audit13.json | matched_rate.tests.final_awb.censored_latency_mean |
| aplicación tamaño fuera de muestra D=150 | 0.0472 | EE 0.0030 | 5000 | 50000 | 106 | e_application_audit13.json | oos_size.by_D.150 |
| aplicación tamaño fuera de muestra D=200 | 0.0482 | EE 0.0030 | 5000 | 50000 | 106 | e_application_audit13.json | oos_size.by_D.200 |
| aplicación tamaño fuera de muestra D=250 | 0.0468 | EE 0.0030 | 5000 | 50000 | 106 | e_application_audit13.json | oos_size.by_D.250 |
| aplicación tamaño fuera de muestra D=300 | 0.0482 | EE 0.0030 | 5000 | 50000 | 106 | e_application_audit13.json | oos_size.by_D.300 |
| tab:attrib dgp1_rho0p8_n200 (a) | 1.0000 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p8_n200 (b) | 0.9474 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p8_n200 (b′) | 0.9536 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p8_n200 (c) | 0.9414 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p8_n200 (a)−(b′) | 4.6400 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p8_n200 (b′)−(b) | 0.6200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p8_n200 (b′)−(c) | 1.2200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p8_n200 |
| tab:attrib dgp1_rho0p9_n200 (a) | 0.9934 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p9_n200 (b) | 0.9240 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p9_n200 (b′) | 0.9312 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p9_n200 (c) | 0.9142 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p9_n200 (a)−(b′) | 6.2200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p9_n200 (b′)−(b) | 0.7200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p9_n200 (b′)−(c) | 1.7000 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p9_n200 |
| tab:attrib dgp1_rho0p93_n200 (a) | 0.9102 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p93_n200 (b) | 0.8398 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p93_n200 (b′) | 0.8470 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p93_n200 (c) | 0.8162 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p93_n200 (a)−(b′) | 6.3200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p93_n200 (b′)−(b) | 0.7200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p93_n200 (b′)−(c) | 3.0800 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p93_n200 |
| tab:attrib dgp1_rho0p95_n200 (a) | 0.7080 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p95_n200 (b) | 0.6586 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p95_n200 (b′) | 0.6676 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p95_n200 (c) | 0.6280 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p95_n200 (a)−(b′) | 4.0400 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p95_n200 (b′)−(b) | 0.9000 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p95_n200 (b′)−(c) | 3.9600 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p95_n200 |
| tab:attrib dgp1_rho0p97_n200 (a) | 0.3864 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib dgp1_rho0p97_n200 (b) | 0.3668 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib dgp1_rho0p97_n200 (b′) | 0.3730 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib dgp1_rho0p97_n200 (c) | 0.3454 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib dgp1_rho0p97_n200 (a)−(b′) | 1.3400 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib dgp1_rho0p97_n200 (b′)−(b) | 0.6200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib dgp1_rho0p97_n200 (b′)−(c) | 2.7600 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.dgp1_rho0p97_n200 |
| tab:attrib c\|200 (a)−(b′) | 4.0629 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|200 |
| tab:attrib c\|200 (b′)−(b) | 0.5229 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|200 |
| tab:attrib c\|200 (b′)−(c) | 2.0886 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|200 |
| tab:attrib c\|500 (a)−(b′) | 0.4457 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|500 |
| tab:attrib c\|500 (b′)−(b) | 0.0743 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|500 |
| tab:attrib c\|500 (b′)−(c) | 0.6886 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|500 |
| tab:attrib c\|1000 (a)−(b′) | 0.0971 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|1000 |
| tab:attrib c\|1000 (b′)−(b) | 0.0314 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|1000 |
| tab:attrib c\|1000 (b′)−(c) | 0.5114 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.c\|1000 |
| tab:attrib ct\|200 (a)−(b′) | 1.6800 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.ct\|200 |
| tab:attrib ct\|200 (b′)−(b) | 0.7450 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.ct\|200 |
| tab:attrib ct\|200 (b′)−(c) | 8.1200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.ct\|200 |
| tab:attrib ct\|500 (a)−(b′) | 1.8600 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.ct\|500 |
| tab:attrib ct\|500 (b′)−(b) | 0.3000 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.ct\|500 |
| tab:attrib ct\|500 (b′)−(c) | 4.5600 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.ct\|500 |
| tab:attrib lp_dm_c5 (a) | 0.2949 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c5 (b) | 0.2902 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c5 (b′) | 0.2982 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c5 (c) | 0.2745 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c5 (a)−(b′) | -0.3300 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c5 (b′)−(b) | 0.8000 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c5 (b′)−(c) | 2.3750 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c5 |
| tab:attrib lp_dm_c10 (a) | 0.7243 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c10 (b) | 0.7200 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c10 (b′) | 0.7287 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c10 (c) | 0.6953 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c10 (a)−(b′) | -0.4350 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c10 (b′)−(b) | 0.8600 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c10 (b′)−(c) | 3.3350 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c10 |
| tab:attrib lp_dm_c15 (a) | 0.9580 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| tab:attrib lp_dm_c15 (b) | 0.9549 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| tab:attrib lp_dm_c15 (b′) | 0.9579 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| tab:attrib lp_dm_c15 (c) | 0.9466 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| tab:attrib lp_dm_c15 (a)−(b′) | 0.0150 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| tab:attrib lp_dm_c15 (b′)−(b) | 0.3000 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| tab:attrib lp_dm_c15 (b′)−(c) | 1.1300 | — | — | — | 95 / 102 / 136 | bB_attrib_audit12.json | cells\|by_n.lp_dm_c15 |
| v14 corregida `v14/sec5_montecarlo.tex:75` (sec5_calib_out) | 0.14 | recalculado 0.14 | — | — | — | q_claims_audit13.json | not_reproduced |
| v14 corregida `v14/sec5_montecarlo.tex:141` (sec5_lp_se) | 0.0036 | recalculado 0.00353551 | — | — | — | q_claims_audit13.json | not_reproduced |
| v14 corregida `v14/sec5_montecarlo.tex:602` (sec5_dgp5b) | 7 | recalculado 7.95 | — | — | — | q_claims_audit13.json | not_reproduced |

