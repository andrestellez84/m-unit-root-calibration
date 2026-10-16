# Auditoría A18 — reporte (enmienda 8, reempaquetado final sobre el v18b)

Enmienda 8 commiteada antes de empezar (§3). Sin simulación ni cifras nuevas. No se editó ningún `.tex` del manuscrito ni `src/`.

**Paquete: `submission_v18b.zip`, 771460 bytes, sha256 `f4519199d01d807174498576fbe0c758af6557e6427e70459c52378663e525f4`** (136 archivos; no se commitea).

## 1. Resultados

### B18.1 — sec3_theory.tex del v18b (lectura E8.1)

Miembros del zip que difieren entre v18 y v18b: main.pdf, sec3_theory.tex; solo en v18: ninguno; solo en v18b: ninguno. El único cambio de texto es sec3_theory.tex:176: sí.

| Archivo | Líneas | v18 | v18b |
|---|---|---|---|
| sec3_theory.tex | 176–176 | parameter, $\eta = 0.01^{1/l}$ with $l = \mathrm{round}(1.75\,n^{1/3})$, | parameter, $\eta = 0.01^{1/l}$ with $l = \mathrm{round}(1.75\,T^{1/3})$ and $T = n + 1$, |

La línea nueva escribe l = round(1.75 T^{1/3}): sí; y T = n + 1: sí. Es la regla del código (l = round(1.75 T^(1/3)), T = n + 1 (boot35_v18_audit17.json eta.<n>.l_code; audit9_engine.awb_gamma)), con l = 8, 10, 14 en n = 100, 200, 500.

### B18.2 — Nota de S4.3 (lectura E8.2)

Frase añadida al final de la nota de tab:awb (bloque S4_breaks, ancla `(region \$\[0\.0405, 0\.0600\]\$ for 2000 paths\.)`, veces 1): «The AWB p-value here is $\#\{S^{*} \leq S\}/R$, not the $(1 + \#)/(R + 1)$ of Section~3.5 of the main text.». Está en la nota de S4.3: sí; apariciones en el suplemento: 1. sec:bootdef es la sección 3.5 del v18b (sí). El p-valor registrado del AWB de A13 es `#{stat* <= stat} / B` con 399 réplicas.

### B18.3 — Fechas de los PDF (lectura E8.3)

| Origen | PDF | Claves eliminadas | Contenido idéntico | Raster idéntico (72 ppp) | Sin fecha en los bytes | Líneas de fecha en pdfinfo | sha256 nuevo (16) |
|---|---|---|---|---|---|---|---|
| suplemento | figures/fig_dgp3_audit13q.pdf | CreationDate | sí | sí | sí | 0 | `aba83b6f83a0f413` |
| suplemento | figures/fig_local_power_audit13q.pdf | CreationDate | sí | sí | sí | 0 | `14d7c049b6ebba43` |
| suplemento | figures/fig_power_equalized_audit13q.pdf | CreationDate | sí | sí | sí | 0 | `0d286cdeee41ba64` |
| suplemento | figures/fig_size_shift_audit13q.pdf | CreationDate | sí | sí | sí | 0 | `9ec255aee91335e6` |
| suplemento | figures/fig_theta_ladder_audit13q.pdf | CreationDate | sí | sí | sí | 0 | `d8ac7550f0f028c0` |
| cuerpo | figures/fig_calibration_gain_audit13q.pdf | CreationDate | sí | sí | sí | 0 | `c83852d49197ed8e` |

Comprobación final sobre los 6 PDF del paquete: sin clave ni valor de fecha y sin líneas de fecha en pdfinfo: sí.

### B18.4 — MANIFEST, compilación e identificadores (lectura E8.4)

- `supplementary/MANIFEST.sha256` regenerado: 110 entradas; todas coinciden con los archivos del paquete: sí.
- Cuerpo (v18b): 0 errores, 0 referencias y 0 citas indefinidas, 20 páginas; el .bbl coincide con el de bibtex: sí.
- Suplemento: 0 errores, 0 referencias y 0 citas indefinidas, 36 páginas.
- Identificadores: 0 aciertos que identifican al autor; otros: hash_de_commit (hashes de commit en `supplementary/data/`, conservados desde B15.5). Metadatos de PDF presentes: creator, format, producer.

### B18.5 — Paquete (lectura E8.5)

`submission_v18b.zip`: 771460 bytes, sha256 **`f4519199d01d807174498576fbe0c758af6557e6427e70459c52378663e525f4`**. Incluye 136 archivos; del zip del v18b se excluyen CHANGELOG_v17.md, CHANGELOG_v18.md, SUPPLEMENT_MAP_v17.md, cover_letter.md, main.pdf, tables/tab_boot_audit15.tex, tables/tab_boot_note_audit15.tex, tables/tab_fixedb_size_audit15.tex, tables/tab_fixedb_size_note_audit15.tex, tables/tab_lag_audit15.tex, tables/tab_serial_asy_audit15.tex.

| Archivo | Bytes | sha256 (16) |
|---|---|---|
| appA_proofs.tex | 7437 | `5a57f0b156fa72aa` |
| appB_critical_values.tex | 1171 | `7783dddc0167c115` |
| figures/fig_calibration_gain_audit13q.pdf | 16080 | `c83852d49197ed8e` |
| interact.cls | 25198 | `d9603354ce657c99` |
| main.bbl | 6677 | `f2bc8ef7d289027d` |
| main.tex | 4452 | `099a75c840196336` |
| references.bib | 18322 | `0a9c0d95dd0c842e` |
| sec1_introduction.tex | 8689 | `c65133b6548f7298` |
| sec2_statistics.tex | 5576 | `052b9038552a2201` |
| sec3_theory.tex | 9616 | `e99a209a12765cec` |
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
| E8.1 | único cambio: sec3_theory.tex:176 | sí | pasa |
| E8.2 | frase una vez, en la nota de S4.3; sec:bootdef = 3.5 | 1 / sí / sí | pasa |
| E8.2 prueba --out | 0 errores | 0 | pasa |
| E8.3–E8.5 v18b_clean | puerta del paquete | sí | pasa |
| E8.3–E8.5 supplement_clean | puerta del paquete | sí | pasa |
| E8.3–E8.5 no_artifacts | puerta del paquete | sí | pasa |
| E8.3–E8.5 no_author_hits | puerta del paquete | sí | pasa |
| E8.3–E8.5 no_pdf_dates | puerta del paquete | sí | pasa |
| E8.3–E8.5 body_pdf_content_preserved | puerta del paquete | sí | pasa |
| E8.3–E8.5 manifest_ok | puerta del paquete | sí | pasa |
| E8.3–E8.5 supplementary_committed | puerta del paquete | sí | pasa |

## 3. Procedencia

Entrada: `paper_latex_v18b.zip` sha256 `31b4cda1c6427eb06a545981a2af16ca6ef0a9507f46167e5e2bb41eeebff221`. Protocolo: `experiments/protocol_audit15_amend8.md`.

| Archivo | sha256 (16) | Script | Commit | Código commiteado | Asistente |
|---|---|---|---|---|---|
| experiments/results/diff_v18b_audit18.json | `350abfb1562cdcd7` | experiments/audit18_diff.py | ce940b0 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/submission_v18b_audit18.json | `ab40f2354b568cb2` | experiments/audit18_package.py | 7c4892e | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v18b_audit18.json | `f7db9a3cb35f9ed1` | experiments/audit18_supplement.py | ce940b0 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |
| experiments/results/supplement_v18b_trial_audit18.json | `cd0093a0d0560c08` | experiments/audit18_supplement.py | ce940b0 | sí | Claude Code / claude-opus-5-5 / 2.1.265 (Claude Code) |

## 4. Desviaciones

| Desviación | Motivo | Cuándo | Efecto |
|---|---|---|---|
| La frase de S4.3 lleva las fórmulas en modo matemático ($…$) | El texto del encargo es LaTeX sin delimitadores | E8.2 | Mismo texto; compila |
| Las fechas se quitan reescribiendo el diccionario Info (sin la clave), no dejándola en null | Un primer intento dejaba «/CreationDate null», que la comprobación en bytes rechazó | Durante la prueba con --out | Creator y Producer se conservan |
| El zip no se commitea | Entregable derivado; lo registran su sha256 y la lista de archivos | E8.5 | Ninguno |

## 5. No ejecutado

- No se edita ningún `.tex` del manuscrito; el paquete se arma desde el zip del v18b.

## 6. Conclusiones

- El v18b cambia solo sec3_theory.tex:176, que ahora escribe la regla del código.
- La nota de S4.3 declara el p-valor de su AWB; las fechas de los 6 PDF del paquete se han eliminado sin tocar su contenido.
- Cuerpo (20 páginas) y suplemento (36 páginas) compilan juntos sin errores ni referencias indefinidas; sin aciertos que identifiquen al autor.
- `submission_v18b.zip`: sha256 `f4519199d01d807174498576fbe0c758af6557e6427e70459c52378663e525f4`.

## 7. Anomalías y observaciones

- Ninguna nueva. Se mantienen los hashes de commit en `supplementary/data/` (decisión de B15.5).

## Anexo: tabla maestra de los números nuevos

| Clave | Valor | IC/EE | N_sim | N_cal | Familia | JSON | Ruta |
|---|---|---|---|---|---|---|---|
| B18.5 sha256 del paquete | f4519199d01d807174498576fbe0c758af6557e6427e70459c52378663e525f4 | — | — | — | — | submission_v18b_audit18.json | zip.sha256 |
| B18.5 bytes del paquete | 771460 | — | — | — | — | submission_v18b_audit18.json | zip.bytes |
| B18.5 archivos del paquete | 136 | — | — | — | — | submission_v18b_audit18.json | n_files |

