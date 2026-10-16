# Protocolo de A14: valores críticos del suplemento, fuentes pendientes y verificación de v15

Se registra y se commitea antes de cualquier cómputo de A14. A14 no hace ninguna
simulación nueva ni usa números aleatorios. La familia 150 queda reservada y sin uso.
No hay predicción registrada.

## 1. Encargo (literal)

```
AUDITORÍA A14 — Valores críticos del suplemento, fuentes pendientes y
verificación de v15
Sufijo _audit14. Familia 150 reservada; no debería hacer falta
aleatoriedad. Protocolo commiteado antes de cualquier cómputo. Sin
predicción registrada. Ninguna simulación nueva.

REGLA DE PASO 0: |Δ| = 0 en las columnas que el bloque usa; en el resto de
columnas comunes, ≤ 1e-12 con declaración.

B14.0. Entrada: paper_latex_v15.zip (reporta su sha256), sólo lectura.
  Comprueba que los 16 tabulares y las 6 figuras son idénticos byte a byte
  a los exportados por A13 y B13.Q.

B14.1. Valores críticos para el suplemento (S5). Desde las muestras de
  calibración ya almacenadas (N_cal = 5e5, las que B13.Q Q5 localizó),
  calcula los cuantiles al 1 %, 2.5 %, 5 % y 10 % de MSB-GLS y MZ_t-GLS
  (MAIC de Ng–Perron), n ∈ {100, 200, 500, 1000}, casos constante y
  tendencia, con EE bootstrap de cada cuantil. Paso 0: el 5 % coincide
  con el que ya existe. Salida: CSV legible por máquina y un tabular
  tab_critMSB_audit14.tex, generado con test de literales.

B14.2. Cinco cifras sin fuente. Busca en todo el repositorio (incluidos
  resultados de A4–A7 y de v11) el origen de:
   (i) media 0.003 del peso adaptativo bajo la nula;
   (ii) FP media 0.0301 del estadístico registrado con N_cal = 5e4;
   (iii) 6.9 % y 0.6 % de desviación relativa de la mediana de
         sigma2_HAC frente a la identidad de Bartlett, AR(0.5), n = 200 y
         5000;
   (iv) pendiente 0.333 del ancho de banda en log n.
  Para cada una: archivo, clave, valor y script que lo produjo. Si no
  aparece, dilo; no recalcules.

B14.3. Verificación de v15. Repite Q3 de B13.Q sólo sobre las frases que
  cambiaron (CHANGELOG_v15.md, tabla «Cifras») y confirma que las cifras
  retiradas ya no aparecen. Repite Q4 con la regla corregida: las
  apariciones de «rolling means» y «two-channel» están permitidas cuando
  describen el diseño original, la prueba general en theta o los
  resultados negativos; informa sólo las que afirmen algo sobre MSB-B.

Reporte resultados_auditoria_14.md con las siete secciones habituales y
la tabla maestra.
```

## 2. Lecturas operativas

**1. Sufijo, familias y entradas.** Todo archivo nuevo lleva el sufijo `_audit14`. La familia 150
queda reservada y no se usa, porque ningún bloque necesita números aleatorios. La comprobación de
colisión se reduce a registrar que 150 no está entre las familias previas (90–149). La entrada es
`../paper_latex_v15.zip`, que se lee dentro del zip sin extraerlo y cuyo sha256 se registra. Son de
sólo lectura: los `.tex`, `src/`, `experiments/data/*.csv`, `experiments/protocol.md`,
`experiments/results/real_data_results.json` y todos los JSON de auditorías anteriores. La
infraestructura de A13 se reutiliza sin modificarla. A14 tiene su propio manifiesto
(`manifest_audit14.json`), su carpeta de logs (`logs_audit14`) y su carpeta de tabulares
(`tables_audit14`).

**2. B14.0.** El zip del v15 trae 17 archivos en `v15/tables/`: los 16 tabulares y el fragmento de
nota `tab_attrib_note_audit13.tex`. Se comparan byte a byte los 17 con
`experiments/results/tables_audit13/` (exportados por A13 y por B13.Q Q1). Las 6 figuras
`v15/figures/*_audit13q.pdf` se comparan con `paper/figures/*_audit13q.pdf` (B13.Q Q2). Como
extensión declarada, se comprueba además que todo `\input{tables/...}` y todo `\includegraphics` del
texto del v15 apuntan a un archivo presente en el zip, y que el zip ya no contiene figuras
`*_audit13.pdf` sin la q.

**3. B14.1: muestras y estadísticos.** Las muestras son
`experiments/results/checkpoints/audit10_cal/cal_n{100,200,500,1000}.npz`, con 500 000 filas cada
una (semilla de calibración 42, las que localizó B13.Q Q5). Las columnas usadas son
`c|msb`, `c|mzt`, `ct|msb` y `ct|mzt`. En ellas, `audit8_unitroot.np_statistics` calcula MSB-GLS y
MZ_t-GLS sobre residuos GLS (c̄ = −7 en el caso constante, −13.5 en el de tendencia) con el retardo
elegido por la MAIC de Ng–Perron. Se registra el sha256 de cada muestra y el número de NaN de cada
columna.

**4. B14.1: cuantil.** Es `numpy.nanquantile(x, α)` con el método por defecto (interpolación lineal
entre estadísticos de orden adyacentes), la misma llamada con la que `audit9_engine.rejector`
produjo los valores al 5 % que ya existen. Se usa la cola inferior: se rechaza cuando el estadístico
es menor que q_α. Los niveles son α ∈ {0.01, 0.025, 0.05, 0.10}. Salen 2 estadísticos × 2 casos ×
4 n × 4 niveles = 64 valores, de los que 48 son nuevos.

**5. B14.1: EE bootstrap sin aleatoriedad.** El EE de cada cuantil es el del bootstrap no paramétrico
ideal (B → ∞), calculado en forma cerrada y sin números aleatorios. Por eso la familia 150 no hace
falta. Con los estadísticos de orden x_(1) ≤ … ≤ x_(N) de la muestra y h = (N − 1)α, el cuantil
lineal es Q = (1 − g) x_(r) + g x_(r+1), con r = ⌊h⌋ + 1 y g = h − ⌊h⌋. Sea C_k el número de
extracciones bootstrap con índice ≤ k, que sigue una Bin(N, k/N).

- P(X*_(r) ≤ x_(k)) = P(C_k ≥ r). De ahí salen E*[X*_(r)] y E*[X*_(r)²], y lo mismo para r + 1.
- Para a < b, P(X*_(r) = x_(a), X*_(r+1) = x_(b)) = P(C_a = r) · (1 − (1 − 1/a)^r) ·
  [((N − b + 1)/(N − a))^(N−r) − ((N − b)/(N − a))^(N−r)].
- E*[(X*_(r+1) − X*_(r))²] es la suma de (x_(b) − x_(a))² ponderada por esas probabilidades.
- E*[X*_(r) X*_(r+1)] = ½(E*[X*_(r)²] + E*[X*_(r+1)²] − E*[(X*_(r+1) − X*_(r))²]).
- Var*(Q) resulta de los tres momentos. Los valores se centran en el cuantil muestral antes de
  sumar.

Las sumas se truncan donde los pesos omitidos suman menos de 1e-15, y se registra la masa total de
cada distribución marginal, que debe dar 1 dentro de 1e-12. Un test unitario valida las fórmulas por
enumeración exhaustiva de las N^N remuestras con N ≤ 6. Como control, se registra también el EE de
Maritz–Jarrett, es decir, el EE bootstrap exacto del estadístico de orden de índice round(Nα), y su
cociente con el anterior.

**6. B14.1: Paso 0.** En las columnas usadas, el cuantil al 5 % calculado debe ser igual (|Δ| = 0) a
los que ya existen:

- `b101_theta_audit10.json` `cells.<dm|ct>|<n>.sim_thresholds.<msb|mzt>`, con n ∈ {200, 500, 1000};
- `bA_ma_audit12.json` `config.iid_quantiles.<n>|<c|ct>.<msb|mzt>`, con n ∈ {100, 200, 500}.

En el resto de columnas comunes se recalculan con la misma llamada y las mismas muestras los demás
cuantiles al 5 % guardados en esas mismas entradas (dfgls, adf y pp). El criterio es ≤ 1e-12, con
declaración de los que difieran.

**7. B14.1: salidas.** `audit14_b1_critical.py` escribe `b1_critical_audit14.json`. Después,
`audit14_tables.py`, que sólo lee JSON y está bajo `tests/test_no_literals_audit14.py`, escribe:

- `tables_audit14/crit_msb_mzt_audit14.csv`: una fila por valor, con estadístico, caso, n, α, valor
  crítico, EE bootstrap, EE de Maritz–Jarrett, N_cal, NaN y archivo de muestra;
- `tables_audit14/tab_critMSB_audit14.tex`: con la disposición de tab:critB (filas n; columnas
  Constante y Tendencia × 4 niveles), en dos paneles, MSB-GLS a 4 decimales y MZ_t-GLS a 3, con
  redondeo binario;
- como extensión declarada, `tables_audit14/tab_critMSB_note_audit14.tex`: el fragmento de nota con
  N_cal y el EE máximo de cada estadístico.

**8. B14.2: búsqueda.** El alcance es todo archivo de texto del repositorio (.json, .csv, .md, .log,
.tex, .txt, .py, .bib), fuera de `.git` y `__pycache__`. Incluye `experiments/results/`, sus
checkpoints y `paper/`, que es la fuente del v11. Se buscan literalmente los tokens con fronteras de
dígito: `0.003` (sin otro dígito detrás), `0.0301`, `6.9`, `0.6` y `0.333`. Para 6.9 y 0.6 el
contexto debe llevar `%`. Se registran el recuento y los archivos con aciertos.

La exploración previa se hizo leyendo archivos, sin calcular nada. Localizó candidatos por contexto
semántico: el peso R̂ bajo H0, la aplicación con N_cal = 5e4 y el piloto α(1), las medianas de
σ̂²_HAC del AR(0.5) y la pendiente de B antes del redondeo. El script los registra, y para cada cifra
comprueba:

- que el archivo existe y el valor de la clave;
- que su redondeo a los decimales impresos (binario) da la cifra impresa;
- el script productor, con su sha256 y su estado en git;
- el commit que añadió el archivo de resultados.

«No recalcules» se aplica literalmente: no se recalcula ningún estadístico ni se combina aritméticamente
ningún valor almacenado para reconstruir una cifra. Si la cifra no está almacenada como tal, se dice,
y se listan los insumos almacenados que la acompañan.

**9. B14.3: Q3 sobre lo que cambió.** Se verifican las frases de la tabla «Cifras» de
`CHANGELOG_v15.md` (7 filas), con el registro, las plantillas y las convenciones de Q3 de B13.Q:
binaria, mitad hacia arriba y, en las cotas, desigualdad comprobada además del redondeo. Como
extensión declarada se añaden tres cosas:

- las frases de reemplazo de la tabla «Cifras retiradas» que llevan una cifra o una afirmación nueva
  (sec6: «left its 13 detections unchanged»; sec5 §5.12 sin la media; appA `rem:hacrate`, frase
  cualitativa);
- la completitud del changelog: cada bloque del diff v14 → v15 de los archivos de texto se asigna a
  una fila del changelog o a un `\includegraphics` de figura, y un bloque sin asignar se informa;
- la cobertura de las líneas cambiadas: todo número con decimales de una línea cambiada queda
  cubierto por una frase verificada o clasificado por el contexto de diseño de Q3.

La definición de sec4 se evalúa literalmente como «al menos uno de los dos (θ = 0, θ = 0.02) rechaza
con probabilidad estrictamente entre 0 y 0.99», y se compara el conjunto de celdas con el de la
definición de B13.Q (min < 0.99 y max > 0).

Las cifras retiradas se buscan en los archivos de texto del v15 (Q.TEXT_FILES):

- «mean $0.003$» y el token 0.003;
- 0.0301;
- 6.9;
- 0.6 seguido de `%`;
- 0.333.

Si aparece el token 0.6 en otro contexto, se informa con ese contexto.

**10. B14.3: Q4 con la regla corregida.** Los patrones y las zonas de Q4 de B13.Q se mantienen para
«collapses faster», «does not collapse as fast», «no cost in size», «no effect on size», «RM-GLS» y
«theta = 0.02». Para «rolling means» y «two-channel» (mismas expresiones regulares que Q4), cada
aparición se clasifica por la frase que la contiene en una de cuatro clases:

- (D) describe el diseño original o el estadístico registrado;
- (G) describe la prueba general en θ: la familia S_θ, la ecuación (eq:stat) y los teoremas y
  pruebas generales en θ;
- (N) describe los resultados negativos;
- (M) afirma algo sobre MSB-B, porque la frase tiene a \RMGLS{}, o a un pronombre cuyo antecedente
  es \RMGLS{}, como sujeto de un predicado.

Sólo se informan las de clase M. Una frase que es a la vez N y M se informa como M. La
clasificación vive en el script como un registro (archivo, fragmento distintivo de la frase → clase,
justificación), y toda aparición que el registro no clasifique se informa como «sin clasificar».

**11. Reporte.** `audit14_generate_report.py` sólo lee JSON y está bajo el test de literales.
Escribe `experiments/results/resultados_auditoria_14.md` con las siete secciones habituales (1
Resultados, 2 Compuertas, 3 Procedencia, 4 Desviaciones, 5 No ejecutado, 6 Conclusiones, 7 Anomalías
y contradicciones con el manuscrito) y la tabla maestra (clave | valor | IC/EE | N_sim | N_cal |
familia | JSON | ruta).

**12. Orden.** Se commitea este protocolo. Después se escribe y commitea el código. Por último, la
cadena `audit14_run_chain.sh` corre B14.0, B14.1, las tablas, B14.2, B14.3, la suite de tests y el
reporte, y se commitean los resultados.
