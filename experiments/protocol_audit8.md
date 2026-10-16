# Protocolo pre-declarado de la auditoría A8

Estadístico final, calibración corregida y comparadores de tamaño.

Este archivo se registra **antes** de cualquier bloque de cómputo. Su contenido
es la sección 1 del encargo de A8 y el texto literal de todas las compuertas de
su sección 3. Cualquier cambio posterior es una enmienda
(`protocol_audit8_amend{k}.md`, commit propio, fila en §4 del reporte con
motivo y con si se hizo antes o después de ver datos).

Commit de partida del repositorio al registrar: ver el mensaje del commit que
añade este archivo y el encabezado de `resultados_auditoria_8.md`.

---

## 1. Configuración primaria del test (fijada ahora)

R = 0, θ = 0.1, calibración `hac`, demeaned. Todas las tablas "principales"
usan esta configuración. θ ∈ {0.02, 0.05, 0.2} se reportan como sensibilidad y
**no** pueden sustituir a θ = 0.1 como primaria.

Definiciones:

- Calibración `one` (la publicada, Definición 1): ley nula por simulación de
  N_cal paseos aleatorios gaussianos usando σ̂_HAC = 1 en la calibración.
- Calibración `hac`: cada camino simulado de calibración calcula σ̂_HAC con la
  misma rutina que los datos.
- Desplazamiento pareado Δ = tasa bajo innovaciones mal especificadas − tasa
  bajo innovaciones gaussianas iid, del mismo test, mismo n, mismas
  innovaciones estandarizadas subyacentes cuando sea posible.
- Versiones de comparadores invariantes a escala: `asy` (valores críticos
  asintóticos) y `sim` (valores críticos simulados de muestra finita bajo paseo
  aleatorio gaussiano iid al mismo n, con la selección de retardos dentro del
  bucle).

## 2. Regla de adopción de la variante GLS (B4), fijada ahora

La variante anclada por GLS sustituye a la demeaned como estadístico primario
**si y solo si se cumplen las tres**:

- (G1) En potencia local asintótica (B4, caso demeaned, θ = 0.1), su brecha a
  la envolvente en c = 10 es al menos 10 pp menor que la de la versión
  demeaned.
- (G2) Su tamaño gaussiano con calibración `hac` está dentro de
  [0.0440, 0.0562] a n = 200, 500 y 1000.
- (G3) Su desplazamiento medio Δ bajo las 16 celdas GARCH a n ≤ 500 no supera
  en más de 0.30 pp al de la versión demeaned.

Si no se cumplen las tres, la primaria sigue siendo la demeaned y la GLS se
reporta como resultado secundario. Se aplica la regla mecánicamente y se
reporta cada criterio con su número. Si la regla adopta GLS, los bloques B5–B7
se corren con ambas versiones (primaria y demeaned).

## 3. Semillas

Familias nuevas 90–99, una por bloque (B0: 90, B1: 91, B2: 92, B3: 93, B4: 94,
B5: 95, B6: 96, B7: 97, B8: 98; 99 reservada para enmiendas). Se usa
`numpy.random.SeedSequence(family).spawn(...)` con un hijo por celda y, dentro
de la celda, un hijo por réplica; los procedimientos dentro de una celda
comparten las mismas trayectorias; celdas distintas usan streams
independientes. Se verifica contra el mapa de solape de A7 que ninguna semilla
efectiva coincide con familias previas y se reporta el resultado. Para
R/`bootUR`, la semilla de remuestreo se deriva del mismo `SeedSequence` y se
fija.

Excepción de pareo con lo publicado: donde un bloque diga "mismas trayectorias
que A5/A7", se regenera con las semillas originales y se hace Paso 0. Esas
celdas no usan la familia nueva.

## 4. Compuertas (texto literal del encargo)

### B1 — validaciones (todas DURA)

- Ng–Perron: a n = 2000, paseo aleatorio gaussiano, N = 20 000, lag fijo en 0,
  los cuantiles empíricos al 5% deben estar a ±3% relativo de los valores
  críticos asintóticos de Ng–Perron (2001, Tabla 1): demeaned MZ_α −8.10,
  MZ_t −1.98, MSB 0.233, MP_T 3.17; tendencia MZ_α −17.3, MZ_t −2.91,
  MSB 0.168, MP_T 5.48. Si alguno no pasa, detente y reporta; no sigas con B2.
- Regresión pre/post con defaults: max|Δ| = 0 en estadístico y p-valor sobre
  100 series; suite en verde.
- RM con τ = 0 coincide con MSB-HAC implementado de forma independiente
  (fórmula directa n⁻²Σ(Y_t − Ȳ)²/σ̂² con el ajuste de divisor que
  corresponda) a 1e-12 relativo.
- RM-GLS: invariancia a Y ↦ aY + b (demeaned) y a Y ↦ aY + b + ct (tendencia)
  con peor diferencia relativa ≤ 1e-10; no dependencia de la deriva con
  números aleatorios comunes sobre μ ∈ {0, 0.05, 0.2}, estadísticos iguales a
  ≤ 1e-12.

### COMPUERTA B2a (DURA)

- PASA si |Δ| ≤ 0.30 pp en todas las celdas, ninguna McNemar p < 0.01, y
  |conteo(R=0) − conteo(R=0.5)| ≤ 2 en las 16 GARCH.
- FALLA si test de signo agregado p < 0.01 **y** media de Δ en GARCH
  ≥ +0.30 pp (R = 0 más liberal).
- En cualquier otro caso: INDETERMINADO.

Solo con PASA se continúa. Con FALLA o INDETERMINADO, se completa B2b, se
escribe el reporte y se detiene.

### COMPUERTA B2b (DURA)

Tamaño gaussiano de RM `hac` dentro de [0.0440, 0.0562] en n = 200, 500 y
1000. Si falla, detente: la calibración corregida no calibra y hay que
diagnosticar antes de seguir.

### COMPUERTA B3 (INFORMATIVA)

Clasifica el desenlace y se reportan los tres con su número:

- D1 "ventaja del estadístico": a n ∈ {200, 500}, la media de Δ de RM `hac`
  (primaria) es menor que la de cada uno de ADF-sim, DF-GLS-sim, MSB-GLS-sim,
  MZ_t-sim y MSB-HAC, en al menos 2 errores estándar de la diferencia.
- D2 "equivalente a MSB": |media Δ(RM hac) − media Δ(MSB-HAC)| ≤ 0.30 pp en
  todos los n.
- D3 "el bootstrap domina en tamaño": AWB está dentro de la región en al menos
  tantas celdas GARCH como RM `hac`, y su |media Δ| a n ≤ 500 es menor.

No se detiene por D1/D2/D3.

### B4 — compuerta previa (DURA)

En c = 0 todos los procedimientos rechazan dentro de [0.0440, 0.0562] con un
conjunto de prueba independiente de N = 5000.

### B4 — regla de adopción GLS

La de la sección 2 de este protocolo, con (G1) de B4, (G2) del tamaño
gaussiano de RM-GLS y (G3) de B3.

### Presupuestos (reglas de ejecución)

- Bloques de ≤ 4 h de reloj, con checkpoint en disco por lote, reanudables.
- Antes de cada bloque marcado CARO (B3 y B5, presupuesto 30 h cada uno), se
  ejecuta una sola celda completa, se extrapola el coste total y se escribe en
  el log. Si supera el presupuesto, se detiene y se reporta; no se recortan
  N_sim ni B.
- N_sim = 5000 para tamaño y potencia salvo indicación; N_sim = 2000 para
  columnas con bootstrap; N_cal = 50 000 salvo indicación.
- Región exacta de aceptación binomial bajo p = 0.05 calculada a partir de
  N_sim en cada tabla; para N_sim = 5000 debe dar [0.0440, 0.0562].
