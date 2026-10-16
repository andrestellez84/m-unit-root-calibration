# Enmienda 4 al protocolo de A15: B15.6 (tabulares y literales del v17) y B15.7 (suplemento)

Se commitea antes de generar nada de lo que regula. Sin simulación: todo sale de JSON ya commiteados (resultados finales
de A15 en `e3975c0`).

## 1. Encargo (literal)

```
B15.6 — Tabulares y literales para el v17 (sin simulación; generadores que
solo leen JSON; sufijo _audit15; redondeo binario; cotas hacia afuera).

1. tables/tab_boot_audit15.tex
   - Tamaño de MZ_t-GLS en las 36 celdas × 5 brazos, desde
     b1_boot_audit15.json.
   - Negrita fuera de la región exacta de 5000 caminos.
   - Nota con N, R = 399 y la región.

2. tables/tab_bootpower_audit15.tex
   - Las 8 celdas de potencia: potencia bruta y ajustada por brazo, más la
     diferencia ajustada frente a (ii) en pp con el p de McNemar.

3. tables/tab_fixedb_audit15.tex (cuerpo)
   - Por configuración (Andrews desde A12, s²_AR (b) desde A12, b = 0.1,
     LLSW, b = 0.3, b = 1): tamaño mínimo y máximo sobre las 36 celdas, D, M,
     y potencia ajustada a ρ ∈ {0.80, 0.90, 0.95}, n = 200, caso constante.
   - Declara de qué JSON sale cada columna.

4. tables/tab_fixedb_size_audit15.tex (suplemento): las 36 celdas × 4
   configuraciones fixed-b.

5. literals_v17_audit15.json y un test con las asignaciones siguientes.
   Confirma cada una o corrígela con su valor exacto; no edites el .tex.
   L1  0.0135  D(ii)          L2  0.0074  D(iii)
   L3  0.0072  D(v′)          L4  0.0117  D(iv)
   L5  0.0134  D(i)           L6  0.0576  M(ii)
   L7  0.0382  M(iii)
   L8  «1.6 to 4.2»: diferencias ajustadas (iii) − (ii), en pp, en las
       celdas con p < 0.05 (valor absoluto).
   L9  «six of eight»: número de esas celdas.
   L10 «less than one point» en las otras dos: |dif| < 1.0 y p ≥ 0.05.
   L11 «between 0.083 and 0.108»: los 5 brazos en sz_ma_m0p8_n100_ct.
   L12 «0.052 against 0.093»: (iii) y (ii) en sz_ar_0p5_n100_ct.
   L13 «0.066»: (iii) en sz_ma_m0p8_n500_c.
   L14 «0.0438 against 0.0440»: (v′) en sz_ma_0_n500_ct y límite inferior
       de la región.
   L15 «in two»: número de celdas iid fuera de la región para (iv).
   L16 «between 0.015 and 0.059»: fixed-b b = 0.3, mínimo y máximo sobre
       las 36 celdas.
   L17 «0.187», «0.994», «0.901»: potencia ajustada a ρ = 0.90, n = 200,
       caso constante, para b = 0.3, Andrews y LLSW.
   L18 «0.214»: LLSW en sz_ma_m0p8_n100_c.
   L19 «up to 4.2»: el máximo de L8.
   L20 «0.0576 to 0.0382»: M(ii) y M(iii).

6. Reporte: añade B15.6 a resultados_auditoria_15.md y corrige en §6
   cualquier frase que diga que McNemar fue significativo en las 8 celdas:
   son 6 de 8.

Luego, sin simulación: B15.7 — reconstruir supplementary/ según
SUPPLEMENT_PLAN.md (S1–S9) para el artículo actual, incluidos
tab_lag_audit15, tab_fixedb_size_audit15 y tab_serial_asy_audit15.
Anonimizado según B15.5.
```

## 2. Lecturas operativas: B15.6

**6.1. Carpeta y formato.** Los tabulares van a `experiments/results/tables_audit15/`. Cada uno lleva un fragmento de nota
`*_note_audit15.tex`, generado desde JSON como en A14. Los genera `audit15_v17_tables.py`, bajo
`test_no_literals_audit15.py`. El redondeo es binario. Las tasas llevan 3 decimales; D y M, 4; las diferencias, 1 decimal en
pp.

**6.2. p de McNemar.** Es el bilateral exacto de `b1_boot_audit15.json`. Se imprime «$<$0.001» si p < 0.001, y si no, a 3
decimales con redondeo binario.

**6.3. tab_boot.** Filas de tab:serial (error, n, caso), en el orden de A12. Las columnas son los 5 brazos (i), (ii),
(iii) «SB (bootUR)», (iv) AWB y (v′) «SWB (bootUR)». La negrita marca lo que queda fuera de `exact_region` del JSON. La
nota da N = 5000, R = 399, la región y la regla del p-valor.

**6.4. tab_bootpower.** Filas: las 8 celdas (error, ρ, caso). Columnas: para cada brazo, bruta y ajustada. Para (iii), (iv)
y (v′), la diferencia ajustada frente a (ii) en pp con el p de McNemar entre paréntesis.

**6.5. tab_fixedb.** Una fila por configuración, en el orden del encargo.
- **Andrews y (b).** Tamaño de `bA_ma_audit12.json` `size.<celda>.iid.<gls_t0|glsb_t0>.rate` (A12, N = 2×10⁴, caminos de
  A12). Potencia de `b3_fixedb_audit15.json` `power.<celda>.rates.<gls_t0|glsb_t0>.rate` (A15, familia 157).
- **Fixed-b.** Tamaño y potencia de `b3_fixedb_audit15.json`.
- **Estadísticos.** D y M sobre las 30 celdas con ψ ≠ 0; mínimo y máximo sobre las 36.
- **Nota.** Declara la fuente de cada columna y que Andrews y (b) comparan caminos de A12 (tamaño) y de A15 (potencia).

**6.6. tab_fixedb_size.** 36 celdas × 4 configuraciones fixed-b, con negrita fuera de la región exacta de 2×10⁴.

**6.7. Literales.** `audit15_v17_literals.py` escribe `literals_v17_audit15.json`, con L1–L20 como están en el encargo.
- **Valores sueltos.** Se comparan con redondeo binario a los decimales impresos.
- **Rangos.** Redondeo binario de mínimo y máximo; el redondeo hacia afuera se registra como información.
- **Cotas.** «less than», «up to»: se comprueba la desigualdad y el redondeo hacia afuera (techo en «up to»).
- **Recuentos y palabras-número.** Igualdad.
- **Veredicto.** «confirma» o «corrige», con el valor correcto.

`tests/test_literals_v17_audit15.py` recalcula cada magnitud desde `b1_boot_audit15.json` y `b3_fixedb_audit15.json`,
por un camino independiente del generador, y exige igualdad con el JSON de literales y cobertura de L1–L20. El test no exige
que el literal impreso coincida: una discrepancia es un hallazgo del reporte.

**6.8. Reporte.** Se añade una sección B15.6, y §6 dice explícitamente que McNemar es significativo en 6 de las 8 celdas.
El reporte vigente no contiene la frase de «8 celdas»; esa frase estaba en un mensaje del agente.

## 3. Lecturas operativas: B15.7

**7.1. Destino.** Se reconstruye `supplementary/` en el repositorio. El paquete anterior, del estadístico original de dos
canales, se retira del árbol de trabajo con `git rm` y queda en la historia de git. Se registra el commit que lo contiene.

**7.2. Estructura.**
- `supplement.tex`: documento con las secciones S1–S9, que hace `\input` de los tabulares. Sólo tiene texto descriptivo
  neutro; toda cifra está en tabulares generados desde JSON.
- `tables/`: tabulares copiados de las exportaciones de A13–A15 y tabulares nuevos generados para el suplemento.
- `data/`: los JSON y CSV fuente de cada sección.
- `protocols/`: protocolos, enmiendas y predicciones.
- `README.md`: índice y correspondencia sección → fuente.
- `MANIFEST.sha256`: sha256 de todos los archivos.

**7.3. Secciones** (las de `SUPPLEMENT_PLAN.md` del v16, con las fuentes que ese plan nombra):

| Sección | Contenido |
|---|---|
| S1 | tab:dgp1 y tab:ctpower completos, todas las celdas de `e_equalized_audit13.json` |
| S2 | DGP 5 completo (`e_dgp5_audit13.json`) |
| S3 | resultados negativos: canal de varianza (`b2_size_audit8.json` vía `t5_claims_audit11.json`), peso adaptativo (`rhat_distribution_audit5.json` y `_audit5b.json`), rebalanceo (`adaptive_size_power_audit5b.json`), anclaje en la media (`t5_claims_audit11.json`) |
| S4 | tasa del HAC (`resultados_auditoria_4_E.md`, `audit2_results_audit2.json`, `e4_slope_audit15.json`), con la nota de que el chequeo de la mediana usó el piloto α(2) |
| S5 | valores críticos: S_θ (`b103_cv_audit10.json`), MSB-GLS y MZ_t-GLS (`crit_msb_mzt_audit14.csv`, `tab_critMSB_audit14`) |
| S6 | tablas con θ = 0.02: los valores θ = 0.02 que `tables_audit13.json` guarda en cada fila (`v13`), re-exportados con la disposición de A13 |
| S7 | aplicación (`e_application_audit13.json`): celdas adversas, tamaño fuera de muestra por D (con AWB), resultados por índice y evento |
| S8 | protocolos, enmiendas, predicciones y manifiestos |
| S9 | diagnósticos de escala: A.5, A.6 y B.4 de A12, desde `bA_ma_audit12.json` y `bB_attrib_audit12.json` |

Además: `tab_lag_audit15`, `tab_fixedb_size_audit15`, `tab_serial_asy_audit15`, y `tab_boot`/`tab_bootpower` si el v17
no los lleva en el cuerpo.

Si una sección no puede generarse sólo desde JSON sin decisiones nuevas de contenido, se reporta como pendiente y no se
improvisa.

**7.4. Anonimización.** Se aplica B15.5 con la enmienda 1, E1.7:
- sin rutas de usuario, nombres de usuario, apellido, correo ni URL;
- los hashes de commit se conservan;
- los metadatos de los PDF se vacían;
- no hay URL externa.

La comprobación final repasa `supplementary/` con los patrones de B15.5 y debe dar cero aciertos fuera de los hashes.

**7.5. Compilación.** `supplement.tex` se compila con pdflatex (MiKTeX local), como control. El PDF no se commitea; se
reportan los errores y las referencias indefinidas.
