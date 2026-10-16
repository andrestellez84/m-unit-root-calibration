# Enmienda 1 al protocolo de A8

**Momento:** después de ver datos de B1, antes de cualquier dato de B2.

**Motivo (literal del autor):** "La tolerancia ±3% frente a Ng–Perron (2001,
Tabla 1) está mal especificada por el autor: las tablas publicadas de ERS (1996)
y Ng–Perron (2001) difieren entre sí en 2.6–2.8% para el mismo estadístico P_T,
de modo que la referencia no tiene la precisión que la compuerta exige. La
enmienda no depende de ningún resultado de tamaño o potencia."

## 1. Comparadores de la familia M

Se retiran MZ_α y MP_T de B3, B4 y B5. Quedan MZ_t-GLS y MSB-GLS, en versiones
`asy` (valores críticos publicados de Ng–Perron) y `sim`. La envolvente de B4
sigue usando P_T de ERS calibrado por simulación. No cambia nada más del
protocolo.

## 2. Nueva compuerta B1-NP (DURA)

Sustituye a la validación de Ng–Perron de la sección 4 del protocolo. Pasa si se
cumplen las cuatro:

- (a) MZ_t y MSB, demeaned y tendencia, a ±3% de Ng–Perron (2001) a n = 2000
  (N = 20 000, retardo fijo 0; ya medido en `b1_validation_audit8.json`).
- (b) Identidad MZ_t = MZ_α · MSB trayectoria a trayectoria, máx. |Δ| relativo
  ≤ 1e-12.
- (c) Convergencia interna: los cuantiles simulados al 5% de MZ_t y MSB a
  T = 2001 y T = 10001 difieren en ≤ 2 errores estándar combinados, en ambos
  casos.
- (d) Convención de índices: el código implementa exactamente
  MZ_α = (T⁻¹ ỹ_T² − s²_AR) / (2 T⁻² Σ_{t=1}^{T} ỹ_{t−1}²) y
  MSB = (T⁻² Σ_{t=1}^{T} ỹ_{t−1}² / s²_AR)^{1/2}, con ỹ el residuo GLS; se
  reportan las líneas de código y se recalculan los ocho cuantiles al 5% a
  n = 2000 con la convención alternativa (ỹ_{T−1} y suma hasta T−1). Si la
  alternativa es la del artículo de Ng–Perron y el código usa otra, se corrige
  el código, se repiten (a)–(c) y se declara en §4; si el código ya usa la
  convención del artículo, no se cambia nada.

Los tres fallos de la validación original (MP_T demeaned, MZ_α y MP_T con
tendencia) se reportan en §7(a) como anomalía de referencia: "atribuible a
precisión de las tablas publicadas; no afecta a ninguna comparación, porque
ambos estadísticos se retiraron y los contrastes de tamaño usan valores críticos
simulados".

## 3. Otras decisiones del autor registradas con esta enmienda

- MAIC: se mantiene la MAIC original de Ng–Perron (2001); no se implementa la
  modificación de Perron–Qu.
- Manuscrito: `paper_latex_v11.zip` se copia descomprimido a `paper/` en un
  commit propio; las citas de §7(b) remiten a `paper/<archivo>.tex:<línea>`; B8
  escribe en `paper/figures/`. No se edita ningún .tex.
- Tope por bloque: 4 h.
- Si B1-NP pasa, se continúa con B2 en adelante sin volver a preguntar,
  respetando las compuertas duras de B2a y B2b y la regla de presupuesto antes
  de B3 y B5. Si B1-NP no pasa, se detiene y se reporta.
