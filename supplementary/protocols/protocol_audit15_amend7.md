# Enmienda 7 (auditoría A17): B17 — cierre sobre el v18

Se commitea antes de generar nada. Continúa la numeración de enmiendas; los productos llevan el sufijo `_audit17`. Sin simulación.

## 1. Encargo (literal)

```
B17 — Cierre sobre el v18 (paper_latex_v18.zip, en el escritorio). Sin simulación.
Enmienda 7 commiteada antes de generar nada.

1. eq:mstats reescrita (sec2_statistics.tex del v18):
   - Evaluación literal (T = n + 1, las sumas e índices tal como están
     escritos, k del código) frente a np_statistics, en los caminos de E6.4.
     Criterio: |Δ| relativo ≤ 1e-12 en MSB y absoluto ≤ 1e-10 en MZ_t.
     Si falla, reporta qué índice o suma difiere; no edites el .tex.
   - Verifica también la descripción de s²_AR, k_max y la muestra de
     DF-GLS.
2. §3.5 del v18 frente a bootUR 1.0.5: cada afirmación con archivo:línea.
3. Suplemento:
   - «B = 399» → «R = 399» en S4.3 y S9.2;
   - nota de S2.1 → [0.0470, 0.05305];
   - en S7, frase: «The slope of 1/3 follows from the Andrews rule once
     \hat a settles; it says nothing about the stochastic part»;
   - en S2, un párrafo con los detalles del SB y el SWB que el cuerpo no
     da (índices 0..T−l, relleno inicial con ceros, p-valor de bootUR
     frente al nuestro) y el resultado de invariancia de MZ_t con su causa.
   Registra cada edición en el JSON. Reconstruye y compila.
4. Coherencia (tipo B13.Q Q3) SOLO sobre las líneas que cambiaron de v17 a
   v18 (el diff) y sobre las tablas S2.1, S4.3, S7.1 y S9.2.
5. Compilación de control del v18 y del suplemento juntos; 0 errores.
   Lista para envío: main.tex, secciones, tables/ (solo los archivos que
   se usan con \input), figures/, interact.cls, tfnlm.bst, references.bib,
   el .bbl y supplementary/. Sin artefactos de compilación ni archivos
   que identifiquen al autor.

Reporte: resultados_auditoria_17.md. Commits por ruta explícita.
```

## 2. Entradas

**E7.0.** `paper_latex_v18.zip` (escritorio), sha256 `b78cf82e25631a7dbcb004041eaffa02f3fab68c622e135f780f54b3c721a653`, leído sin
extraerlo al repositorio. Frente al v17 cambian `main.tex` (se retira el stub de `tab:serial`), `sec2_statistics.tex`,
`sec3_theory.tex`, `sec4_montecarlo.tex` y los `\input` de tab_summary y tab_fixedb (de `_audit15` a `_audit16`), y se añade
`CHANGELOG_v18.md`. No se edita ningún `.tex` del manuscrito.

## 3. Lecturas operativas

**E7.1 (1). eq:mstats literal.** `audit17_mstats.py`:
- **Caminos.** Los de E6.4: familia 160, las mismas claves de semilla, n ∈ {100, 200, 500}, dos casos y 1000 caminos por celda.
  No se crea ninguna familia nueva.
- **Evaluación literal.** Implementación propia, independiente de `audit8_unitroot`, de lo que dicen el texto y la ecuación del v18:
  - û por GLS con T_n = T = n + 1;
  - la regresión sin intercepto de Δû_t sobre û_{t−1} y Δû_{t−1}, …, Δû_{t−k} en t = k_max+1..n;
  - σ̂²_k = SSR/(n − k_max) y k_max = ⌊12(T/100)^{1/4}⌋;
  - s²_AR = σ̂²_k/(1 − Σb̂_j)²;
  - MSB y MZ_α con T^{-2} Σ_{t=1}^{n} û²_{t−1} y T^{-1} û_n²;
  - k = el del código.
- **Criterio.** |Δ| relativo ≤ 1e-12 en MSB y |Δ| absoluto ≤ 1e-10 en MZ_t, en todos los caminos.
- **Si falla,** se evalúan variantes de un solo cambio (índice de la suma, normalización, muestra, divisor), y se reporta la que
  reproduce el código.
- **Descripción.** Se verifica además:
  - k_max del texto = k_max del código;
  - la MAIC del texto en la misma muestra elige el mismo k que el código (se cuentan los desacuerdos);
  - el t de DF-GLS por MCO propio en t = k+1..n coincide con `arch.DFGLS` (|Δ| relativo ≤ 1e-10).

**E7.2 (2). §3.5 frente a bootUR.** Cada afirmación de §3.5 del v18 (archivo:línea) se empareja con el código que la sustenta
(archivo:línea, localizado por expresión regular):
- bootUR 1.0.5, para SB y SWB;
- `audit15_boot_engine.py`, para lo que es nuestro (R, p-valor, recálculo de MZ_t y su MAIC, AWB);
- las cifras (η = 0.631 en n = 200) se recalculan con la regla del texto y con la de bootUR.

Veredictos:
- «coincide»;
- «coincide con matiz»;
- «difiere».

**E7.3 (3). Suplemento.** `audit17_supplement.py` reutiliza `audit16_supplement.py` sin modificarlo y añade las ediciones del
encargo. Cada edición queda registrada en el JSON (bloque, patrón, sustitución, veces):
- «B = 399» → «R = 399», en la nota de tab:awb (S4.3) y en tab:deviations (S9.2). Es la única edición dentro de S9. La
  comprobación de integridad de S9 (E6.6.4) se repite admitiendo solo esa sustitución.
- La nota de S2.1: el extremo superior pasa a 0.05305, tomado de `bA_ma_audit12.json exact_region_20000` y escrito sin redondear.
- En S7 se inserta la frase literal del encargo después de las tablas del HAC.
- En S2, el párrafo sobre SB y SWB se sustituye por uno con los detalles que el cuerpo del v18 no da:
  - índices 0..T−l;
  - relleno inicial con ceros y arranque en cero;
  - el p-valor de bootUR frente al nuestro;
  - el resultado de invariancia de MZ_t de E6.4 con su causa (cancelación en el numerador de MZ_α).

  Las cifras salen de `code_check_audit16.json` y la descripción de E6.3. El párrafo del Paso 0 se conserva.
- Las remisiones «of the main text» se numeran con la compilación de control del v18.

Luego se reconstruye `supplementary/`, primero con una prueba en `--out`, y se compila.

**E7.4 (4). Coherencia acotada.** `audit17_coherence.py`:
- **(a) Diff v17 → v18.** Cada línea cambiada se lista, y cada afirmación o cifra que contiene se verifica frente al código o el
  JSON (E7.1 y E7.2 para sec2 y sec3). Además:
  - «within 1.3» frente a su valor, como cota;
  - los `\input` nuevos, byte a byte frente a `tables_audit16/`;
  - la retirada del stub, sin referencias indefinidas en la compilación del v18.
- **(b) Tablas S2.1, S4.3, S7.1 y S9.2 del suplemento reconstruido.**
  - Cada cifra se compara con su JSON, con las funciones de fuente de A13/A14/A16.
  - Se comprueban las ediciones de E7.3.
  - En S9.2, las cifras de tab:deviations frente a sus fuentes (A13 B13.Q, frases dev_*).

**E7.5 (5). Compilación y paquete.** `audit17_package.py`:
- **Paquete.** Arma en un directorio temporal:
  - `main.tex` y las secciones que `main.tex` incluye;
  - `tables/`, con solo los archivos alcanzados por `\input` desde el texto;
  - `figures/`, con solo las usadas por `\includegraphics`;
  - `interact.cls`, `tfnlm.bst`, `references.bib` y `main.bbl`;
  - `supplementary/`, tal como está commiteado.
- **Exclusiones.** Quedan fuera `main.pdf`, los `CHANGELOG`, `SUPPLEMENT_MAP`, `cover_letter.md` y todo artefacto de compilación
  (.aux, .log, .out, .blg, .synctex, .toc).
- **Compilación.**
  - El v18: pdflatex ×2 con el .bbl entregado. Además, bibtex en una copia, para comprobar que el .bbl coincide.
  - El suplemento: pdflatex, bibtex y pdflatex ×2.
  - Criterio: 0 errores y 0 referencias o citas indefinidas en los dos.
- **Anonimato.**
  - Patrones de B15.5 sobre todos los archivos de texto.
  - Metadatos /Author, /Creator y /Producer de los PDF de figuras.
  - Nombres de archivo.
- **Salida.**
  - La lista con el sha256 de cada archivo va en `submission_v18_audit17.json`.
  - El zip del paquete va al directorio temporal de la sesión, no se commitea, y se envía al autor.

**E7.6 (reporte).** `audit17_generate_report.py`:
- Solo lee JSON y lo recorre `tests/test_no_literals_audit17.py`.
- Test independiente de E7.1 en `tests/test_mstats_audit17.py`: recalcula con su propio código, en una submuestra de caminos de
  cada celda, la evaluación literal, y comprueba que no supera los máximos declarados en el JSON.
- `resultados_auditoria_17.md`, con las siete secciones y la tabla maestra. Manifiesto `manifest_audit17.json`.
- Commits por ruta explícita.
