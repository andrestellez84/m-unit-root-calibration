# Enmienda 6 (auditoría A16): B16 — v17, sin simulación

Se commitea antes de generar nada. Continúa la numeración de enmiendas de A15; los productos llevan el sufijo `_audit16`.

## 1. Encargo (literal)

```
B16 — v17 (sin simulación). Enmienda 6 commiteada antes de generar nada.

1. Generadores:
   a. tab_summary: fila 1 (MSB-B con Andrews), potencia desde
      b3_fixedb_audit15.json (gls_t0, ρ = 0.90), igual que tab_fixedb.
      Actualiza la nota.
   b. tab_fixedb_note: sustituye \cref{tab:serial} por el texto
      «Table S2.1 of the supplement». Después quitaré el stub de etiqueta
      de main.tex.

2. Verificación contra el código (reporta; no edites el .tex):
   a. eq:mstats de sec2_statistics.tex frente a np_statistics:
      - definición de MSB, MZ_α y MZ_t;
      - regresión de s²_AR (con o sin constante, índices);
      - fórmula de s²_AR;
      - MAIC.
   b. §3.5 de sec3_theory.tex (SB/SWB): cómo impone bootUR 1.0.5 la nula
      en el DGP bootstrap, si la autorregresión se ajusta en diferencias,
      qué pesos usa el SWB (Rademacher, gaussianos u otros) y si los
      residuos se centran. Cita archivo:línea del código fuente de bootUR.
   c. La prueba de prop:invariance en appA_proofs.tex para los tests con
      s²_AR: ¿el MAIC implementado cumple lo que afirma la prueba?

3. Literales nuevos del v17 → literals_v17b_audit16.json con test
   independiente:
   - N1  «between 0.059 and 0.093»: (ii) MZ_t-GLS, tendencia, ψ = +0.5 o
         φ = +0.5, n ∈ {100, 200} (A15).
   - N2  «between 0.036 and 0.054»: (i) en las mismas cuatro celdas.
   - N3  «in all thirty-six designs»: (ii) > (i) en A15.
   - N4  «0.103» y «0.039»: tab_lag, φ = 0.5, n = 100, tendencia, k = 1,
         y la nula iid de A10, n = 100, tendencia, k = 1 (MZ_t, iid).
   - N5  «between 0.0417 and 0.0502»: MSB-GLS asy, caso constante,
         tab_calib; y «0.0660»: DF-GLS asy, n = 60, constante.
   - N6  Todas las cifras de sec4_montecarlo.tex y sec1_introduction.tex
         que ya estaban en el v16: igualdad con su fuente.
   - N7  «0.0142 and 0.0130»: A12, desde B15.0.
   - N8  «the SWB and the AWB lose comparable amounts»: reporta los rangos
         de sus diferencias ajustadas significativas.

4. B15.7c — Reconstrucción única del suplemento según
   SUPPLEMENT_MAP_v17.md (en el zip del v17):
   - secciones S1–S10;
   - tablas numeradas Sk.j, con S2.1–S2.4 exactamente como en el mapa;
   - «of the main text» apuntando solo a las tablas que siguen en el
     cuerpo;
   - la sección 6 del v16 íntegra en S9;
   - anonimizado; compilación de control.

5. B15.4 — Pasada de coherencia (tipo B13.Q Q3) sobre el v17 y el
   suplemento reconstruido:
   - cifras del resumen frente a P1–P3, §4 y §5;
   - cada \supp y \supptab del cuerpo apunta a la sección o tabla que
     dice;
   - ninguna cifra retirada reaparece (0.333, 6.9 %, 0.6 %, «doubles»).

Reporte: resultados_auditoria_16.md con las siete secciones.
Commits por ruta explícita.
```

## 2. Estado de las entradas

**E6.0.** Entradas:
- `paper_latex_v17.zip` (escritorio), sha256 `ab84cc28a4862023ed652f01f6cdedab16cf12ad9d6af49ddedc3fe1f76d650d`. Contiene
  `SUPPLEMENT_MAP_v17.md`, `CHANGELOG_v17.md`, `main.tex`, `sec1`–`sec5`, `appA`, `appB` y 21 tabulares. Se extrae en el
  directorio temporal y no se commitea (NO se edita ningún `.tex`).
- `paper_latex_v16.zip`, de donde salen los textos que el mapa manda al suplemento (sec6, sec:theta, tab:initial, tab:deviations y
  la verificación de sec3) y las figuras.

Los scripts leen los zips directamente y registran su sha256.

## 3. Lecturas operativas

**E6.1 (1a, 1b).** No se modifica ningún JSON ni tabular de A15. Los nuevos tabulares se generan en
`experiments/results/tables_audit16/` con `audit16_v17_tables.py`, que reutiliza las funciones de `audit15_v17_tables.py`:
- `tab_summary_audit16.tex` y su nota. El tamaño de la fila 1 sigue viniendo de A12. La potencia de la fila 1 sale de
  `b3_fixedb_audit15.json` `power.pw3_rho0p9_n200_c.rates.gls_t0`, con N = 5000 y valores críticos simulados bajo iid, como
  en tab_fixedb. La nota agrupa las filas por fuente de potencia.
- `tab_fixedb_audit16.tex` y `tab_fixedb_note_audit16.tex`. El tabular es idéntico al de A15. En la nota, cada `\cref{tab:serial}`
  pasa a «Table S2.1 of the supplement».

Redondeo binario.

**E6.2 (2a).** Código de referencia: `experiments/audit8_unitroot.py` (`gls_detrend`, `adf_gls_path`, `np_statistics`). Es el que
usaron A10, A12 y A15; `audit15_boot_engine.mzt_gls` lo replica. Por cada punto se registra lo que hace el código, con
archivo:línea: definiciones de MSB, MZ_α y MZ_t; regresión de s²_AR (deterministas, muestra, índices, T frente a n); fórmula de
s²_AR; MAIC (τ_T, divisor, muestra común, kmax). Se contrasta frase a frase con `eq:mstats`, con el texto que la rodea
(convención T_n, «same regression» de DF-GLS) y con Ng y Perron (2001). Cada punto recibe un veredicto:
- «coincide»;
- «difiere, sin efecto en el tamaño», cuando todos los brazos se calibran con el mismo código;
- «difiere».

Se añade un control numérico: `np_statistics` frente a una evaluación literal de `eq:mstats`, sobre los mismos caminos del
control de E6.4.

**E6.3 (2b).** Fuente: `experiments/external_audit15/bootUR_1.0.5.tar.gz`, con el sha256 registrado en la enmienda 2, y los
archivos `R/auxiliary.R`, `R/bootURtests.R` y `src/bootURfunctions.cpp`. Se responden con archivo:línea:
1. cómo se impone la nula (integración de u*, sin el término ρ̂);
2. si la autorregresión se ajusta en diferencias y con qué detrending y criterio;
3. los pesos del SWB;
4. si los residuos se centran;
5. los índices del SB;
6. el valor inicial;
7. el p-valor.

**E6.4 (2c).** Argumento analítico sobre el código: el efecto de y → a y + b (+ c t) sobre el residuo GLS, sobre la regresión
ADF-GLS, sobre τ_T y sobre MAIC(k). Se completa con un control numérico determinista. No es una simulación de resultados.
- Familia de semillas **160**, nueva, con control de colisiones frente a 90–159.
- n ∈ {100, 200, 500}, casos constante y tendencia, 1000 caminos iid por celda.
- Transformaciones a ∈ {−3, 10⁻², 10³}, b = 5, c = 0.1.
- Se registran:
  - los cambios de k;
  - el máximo |Δ| relativo de MSB, MZ_t y s²_AR/a²;
  - el margen mínimo entre el primer y el segundo mínimo de la MAIC.

Criterio de «cumple»: 0 cambios de k, y |Δ| relativo ≤ 1e-10 en MSB y MZ_t.

**E6.5 (3).** Script `audit16_literals.py`, que sólo lee JSON y escribe `literals_v17b_audit16.json`. El test independiente
`tests/test_literals_v17b_audit16.py` recalcula cada valor por otro camino. Reglas:
- Valores: redondeo binario a los decimales impresos.
- Rangos: mínimo y máximo con redondeo binario; se registra también el redondeo hacia afuera.
- Conteos: igualdad.
- Si el valor exacto cae en la mitad, se marca como sensible al redondeo.

Fuentes:
- N1, N2: `b1_boot_audit15.json` `size.sz_{ma_0p5,ar_0p5}_n{100,200}_ct.rates.{ii,i}.rate`.
- N3: número de celdas, de las 36, con rate(ii) > rate(i); los empates se cuentan aparte.
- N4: `b0b_lag_audit15.json` `cells.sz_ar_0p5_n100_ct.procs.mzt.by_k.1.iid.rate` y `a10_null.100|ct.procs.mzt.by_k.1.iid.rate`.
- N5: `e_calib_audit13.json` `cases_by_theta.gls_t0.c.approximation_cost_comparators.<n>.msb.size_published_asymptotic.rate`
  (rango sobre n), y `....60.dfgls.size_published_asymptotic.rate`.
- N7: `b0_iidasy_audit15.json` `b_abs_dev.mzt.both.{iid,asy}.mean`.
- N8: `b1_boot_audit15.json` `power.<celda>.vs_ii.{iv,v_prime}` con McNemar p < 0.05. Se dan el mínimo y el máximo de
  |diferencia ajustada| en pp y el número de celdas; «comparable» no se juzga.
- N6: se extraen todas las cifras de `sec4_montecarlo.tex` y `sec1_introduction.tex` del v17 (incluidos sus tabulares
  `\input`). Se clasifican en tres grupos:
  - cifras que ya estaban en el v16: su fuente es la que registraron A13, A14 y A15 (B13.Q, A14 B3, A15 B15.6), y se comprueba
    la igualdad con esa fuente;
  - cifras nuevas del v17 (tabulares de A15 y literales L1–L20 y N1–N8): van a su propio control;
  - cifras que no son resultados (n, θ, niveles, años, números de sección).

  Cada cifra del primer grupo se compara con el valor de su JSON, con redondeo binario (o con la convención de la tabla de
  origen) a los decimales impresos. Veredicto: «confirma» o «corrige».
- Para N1–N8 se comprueba además que el literal aparece así impreso en el v17 (archivo:línea).

**E6.6 (4, B15.7c).** Reconstrucción única de `supplementary/` con `audit16_supplement.py`, que reutiliza los generadores de
`audit15_supplement.py` y se prueba antes con `--out`. Reglas:
1. **Numeración.** Secciones numeradas S1–S10. Tablas `Sk.j` con el contador reiniciado por sección
   (`\thetable = S\arabic{section}.\arabic{table}`), y lo mismo para las figuras. S2.1–S2.9 en el orden del mapa. El JSON de
   salida registra el número compilado de cada tabla (desde el `.aux`) y lo compara con el mapa.
2. **Contenido.**
   - Tabulares: desde JSON; los de A13 con la disposición del v16.
   - Textos del v16 que el mapa manda al suplemento: se transcriben literalmente desde el zip.
   - Figuras: desde `paper_latex_v16.zip`.
   - Texto de la S2 sobre SB/SWB: sólo hechos registrados en E6.3 y en el Paso 0 de A15 (JSON), sin cifras nuevas.
   - La frase explícita de S4 («SB and SWB were not evaluated under variance breaks») se escribe tal cual pide el mapa.
3. **Referencias cruzadas** de los textos transcritos:
   - si la etiqueta está en el suplemento, `\ref` interno;
   - si está en el cuerpo del v17, «Table/Section/Equation N of the main text», con N tomado de la compilación de control del v17
     (`main.aux`);
   - si no está en ninguno, la frase se describe sin número y se registra.

   «of the main text» sólo apunta a elementos del cuerpo del v17.
4. **Sección 6 del v16 íntegra en S9**: se comprueba por diferencias que todo su texto y todas sus cifras están en S9, salvo las
   referencias cruzadas reescritas por la regla 3.
5. **Anonimización** con los patrones de B15.5. Compilación de control: 0 errores y 0 referencias indefinidas; el PDF de control
   no se guarda.
6. El paquete de `491ed60` y la corrida de control de B15.7b se sustituyen. El commit del paquete va por ruta explícita
   (`supplementary/`).

**E6.7 (5, B15.4).** Pasada de coherencia tipo B13.Q Q3, con `audit16_coherence.py`, sobre el v17 y el suplemento
reconstruido:
- **(a) Resumen.** Cada cifra del resumen (`main.tex`) se empareja con las de P1–P3, §4 y §5, y cada cifra debe coincidir con
  al menos una de ellas y con su fuente JSON.
- **(b) Remisiones.** Cada `\supp{k}` y `\supptab{k.j}` del cuerpo se lista con su frase. Se comprueba que la sección o tabla Sk
  (Sk.j) del suplemento compilado existe y contiene lo que la frase dice, con un registro de clasificación manual (qué se afirma
  y qué hay), que queda en el JSON.
- **(c) Cifras retiradas.** Búsqueda de 0.333, 6.9 %, 0.6 % y «doubles» (y variantes: 0.33, 6.9\%, 0.6\%, «double») en el v17 y
  en el suplemento; cada aparición se reporta con archivo:línea.

**E6.8 (reporte).** `audit16_generate_report.py` sólo lee JSON y lo recorre `tests/test_no_literals_audit16.py`. El reporte
`resultados_auditoria_16.md` tiene las siete secciones y la tabla maestra. Manifiesto `manifest_audit16.json`; la procedencia
incluye `provenance.assistant`. Commits por ruta explícita.
