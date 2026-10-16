# Protocolo de la auditoría A13: regeneración con θ = 0 y cierre

Este protocolo se registra antes de cualquier cómputo de A13, incluidas la sonda
de presupuesto de la AWB y la lectura de checkpoints. El encargo no trae
predicción registrada porque no hay hipótesis nueva. Las enmiendas posteriores
irán en `protocol_audit13_amendN.md`, cada una con su commit, y tendrán fila en
§4 del reporte.

- Sección 1: el encargo, copiado literalmente.
- Sección 2: lo que el autor decidió antes del registro.
- Sección 3: las lecturas operativas, fijadas antes de ver ningún dato.

## 1. Encargo (literal)

```
AUDITORÍA A13 — Regeneración con theta = 0 y cierre
Sufijo _audit13. Familias 140-149 (E = 140, tablas nuevas = 141, AWB = 142,
aplicación = 143). Colisión contra 90-137. Protocolo commiteado antes de
cualquier cómputo. Sin predicción registrada: no hay hipótesis nueva.

B13.E (confirmado por el autor). Regenerar con theta = 0 todo lo que el
manuscrito reporta hoy con theta = 0.02:
 (1) Sin simular, desde JSON existentes y con Paso 0: tab:size (n = 200,
     500, 1000 de b101; n = 60, 100, 150 nuevos con 5e4 caminos, familia
     141), tab:calib, tab:dgp1, tab:ctpower, tab:dgp2, tab:dgp3,
     tab:misspec, tab:localpower, tab:critB (b97).
 (2) Nuevo cómputo: AWB con theta = 0 sobre las trayectorias de B9.5
     (B = 399, familia 142, presupuesto 8 h con sonda y regla de parada);
     DGP 5 con theta = 0 sobre las trayectorias de A7 (Paso 0);
     aplicación con theta = 0 sobre los datos congelados, con verificación
     de hashes (familia 143).
 (3) Figuras con sufijo _audit13.
 Compuerta INFORMATIVA: para cada tabla, la diferencia máxima entre la
 versión theta = 0 y la publicada con theta = 0.02, en pp.

B13.T. Tablas nuevas para el manuscrito, sólo desde JSON de A12:
 tab:serial (tamaño al cv iid por estructura de error, n y caso: las 36
 celdas, procedimientos RM-GLS theta=0, (b), (b'), MSB-GLS NP, MZ_t-GLS NP,
 DF-GLS, ADF, PP; columna adicional con el factor poblacional del Bartlett);
 tab:serialpower (potencia ajustada al tamaño en las mismas celdas);
 tab:initial (B12.C completa).
 Test de literales sobre el generador.

B13.Q. Pasada de coherencia final sobre el .tex de v14 cuando el autor lo
entregue: toda cifra del texto contra los JSON, con archivo:línea, como T5
de A11.

No ejecutar nada más. B12.D sigue cancelado.
```

## 2. Decisiones del autor antes del registro

- B13.E está confirmado por escrito en el propio encargo («confirmado por el
  autor»). Es la confirmación que A12 exigía para su B12.E.
- B12.D sigue cancelado y no se ejecuta.
- No hay predicción registrada, así que A13 no tiene
  `prediccion_*_audit13.md`.

## 3. Lecturas operativas (fijadas antes de ver datos)

1. **Familias.**
   - 140 (E) no tiene celdas. Toda la aleatoriedad nueva de B13.E va a las
     familias que el encargo asigna:
     - 141: `size_<dm|ct>_n<n>`, n ∈ {60, 100, 150}, 50 000 caminos cada una;
     - 142: `awb_<celda>`, las 16 celdas de B9.5;
     - 143: `awbapp_<índice>_D<D>` (16) y `awboos_D<D>` (4).
   - 144–149 quedan reservadas para enmiendas.
   - Semillas: `SeedSequence(familia, spawn_key = (celda, i))`.
   - B13.0 comprueba la equivalencia con `.spawn` y la ausencia de colisiones
     (palabra 0 de `generate_state`) contra las familias de A8–A12 (90–137),
     las semillas enteras de A5–A7 y la semilla 42 de producción. Es el método
     de A12.
2. **Manuscrito de referencia.**
   - «Publicada con θ = 0.02» se refiere a la cifra impresa en
     `paper_latex_v13.zip` (sha256 `fae1334b…9dac`), que es de sólo lectura.
   - La compuerta informativa compara la versión con θ = 0 contra el valor del
     JSON del que salió la cifra impresa.
   - Aparte, un Paso 0 de transcripción comprueba que ese JSON, redondeado a
     los decimales impresos, reproduce la tabla del v13 celda por celda.
3. **«Sin simular» en (1).** Ninguna tabla de (1) genera trayectorias nuevas,
   salvo las celdas de n ≤ 150 de tab:size, que el encargo pide explícitamente.
   Hay dos tipos de fuente:
   - **Tasas ya guardadas en los JSON.** Todas las columnas con θ = 0 se leen
     directamente de ahí: b101, b92, b103_equalized, b103_cv.
   - **Cifras que necesitan datos por camino** (McNemar de θ = 0 contra
     DF-GLS-sim; cuantiles y tamaños de tab:calib).
     - Se recalculan desde los checkpoints de las mismas trayectorias, sin
       generar ninguna nueva.
     - Paso 0 (máx. |Δ| = 0): el mismo código, corrido con θ = 0.02,
       reproduce exactamente los valores del JSON publicado.
     - Si el Paso 0 falla, la tabla correspondiente no se exporta y el fallo
       se reporta.
4. **tab:size.**
   - **n ∈ {200, 500, 1000}:** tasa agregada
     `b101.cells.<caso|n>.rates.gls_t0.pooled` (N = 100 000), con su Wilson.
   - **n ∈ {60, 100, 150}:** 50 000 caminos nuevos por (caso, n), familia 141,
     con hijos distintos por caso y el paseo gaussiano de A8 (Y₀ = 0,
     Y = cumsum ε).
     - Fila ligera por camino: s2, RM-GLS θ = 0 y θ = 0.02 en cada caso, con
       las rutinas de `audit9_engine`.
     - Paso 0 de la fila ligera: igual a las columnas de `audit9_engine.row`
       en los 50 primeros caminos de cada celda, con máx. |Δ| = 0.
     - Rechazo: regla RM-like (p = F_null(stat) < 0.05) con la calibración de
       A10 de N_cal = 500 000 (`audit10_cal/cal_n<n>.npz`).
     - Además, tamaño con el cuantil de n = 20 000 (B9.4, familia 104), para
       la figura de ganancia de calibración.
   - Se informan, sin que decidan nada:
     - la tasa con θ = 0 de B10.3.7 (`b103_lown`, familia 113, independiente)
       como contraste;
     - la diferencia pareada entre θ = 0 y θ = 0.02 sobre los caminos de
       B10.3.7.
5. **Columnas con θ = 0.**
   - En tab:dgp1, tab:ctpower, tab:dgp2, tab:dgp3 y tab:misspec, la columna
     RM-GLS pasa a θ = 0, y la McNemar se hace entre RM-GLS θ = 0 y
     DF-GLS-sim.
   - En tab:localpower, la columna RM-GLS pasa a θ = 0 y la columna «θ = 0»
     actual pasa a «θ = 0.02», para seguir mostrando la otra ventana.
   - El resto de columnas (RM con θ = 0.1, ADF, PP, DF-GLS, MZ_t, MSB, ZA,
     KPSS, envolvente) no depende de θ. Se vuelve a leer del mismo JSON y su
     Paso 0 de transcripción debe coincidir con el v13.
6. **tab:calib.**
   - Se repite `audit10_b103_finite` con θ = 0 sobre las mismas filas: las
     independientes de B9.2 (N = 20 000 por n, familia 102) y las de n = 20 000
     de B9.4.
   - La calibración de cada n es la de mayor N_cal disponible, igual que en
     A10: 500 000 para n ≤ 1000 y 50 000 de A9 para n ∈ {2000, 5000}.
   - Cambian q_0.05(n), el tamaño en q(n), el tamaño en q(20 000) y los KS
     del texto.
   - DF-GLS y MSB-GLS no dependen de θ y su Paso 0 exige |Δ| = 0.
7. **tab:misspec.** La columna RM-GLS θ = 0 y las filas de desplazamiento medio
   salen de `b92.misspec`.
   - Desplazamiento medio: media de `delta_vs_independent` sobre las celdas
     GARCH de cada n, con EE √(Σ se²)/k.
   - Paso 0 de la fórmula: aplicada a θ = 0.02, reproduce la fila impresa del
     v13.
8. **tab:critB.** `b103_cv_audit10.json`, entradas `dm|0|n` y `ct|0|n`, que
   son idénticas a la tabla de b97 (máx. |Δ| = 0 declarado por A10). Se
   informa el EE bootstrap máximo de cada θ, porque el texto dice «below
   0.001».
9. **AWB (familia 142).** Es B10.3.4 con θ = 0.
   - Trayectorias: las mismas 2000 primeras de cada celda de B9.5.
   - Paso 0: el estadístico observado recalculado coincide con la fila de
     B9.1/B9.2, con máx. |Δ| = 0.
   - Remuestreo: B = 399, AWB con los valores por defecto de bootUR 1.0.5,
     residuos dY − media(dY), semillas `SeedSequence(142, (awb_<celda>, i))`.
   - Columna simulada: calibración de A10 con θ = 0 (N_cal = 500 000).
   - Presupuesto de 8 h:
     - sonda de 14 series a n = 200 y a n = 500;
     - proyección = segundos por serie × 2000 × número de celdas de ese n;
     - si la proyección supera 8 h, no se lanza y se reporta;
     - durante la corrida, el tope es de 8 h con checkpoint por lote; al
       agotarse, se detiene y se reporta con el comando para reanudar.
   - La regla B9.5 (≥ 4 de 6 celdas de DGP 3 dentro de la región y pérdida
     ≤ 3 pp) se recalcula con fines informativos.
10. **DGP 5.** Es B10.3.2 con θ = 0 sobre las trayectorias de A7 (familia 60,
    regeneradas con sus semillas). No usa aleatoriedad nueva.
    - Paso 0 (a): componentes g1/g2 frente a los checkpoints de A7 en 50
      series por celda.
    - Paso 0 (b): RM-GLS θ = 0.02 recalculado en las 50 primeras series de
      cada celda frente a la caché de A10 (`audit10_b103/dgp5_gls_t0.02_*`).
    - Ambos pasos exigen máx. |Δ| = 0.
    - Umbral igualado: el cuantil 5 % de θ = 0 en la celda de calibración de
      A7 (N_cal = 5000), como en A10.
    - Columnas de A7 (dos canales, unión, bootstrap DF-GLS, cuota de g2): sin
      cambios.
11. **Aplicación (familia 143).** Es B10.3.5 con θ = 0.
    - Hashes de los datos congelados y de `experiments/protocol.md`
      verificados antes de calcular. Si no coinciden, no se calcula.
    - Nula: `build_null_cdf` de producción (semilla 42, N_cal = 50 000,
      `tau_mode = "zero"`, n = D − 1).
    - La fila AWB de tab:fp se calcula siempre, porque el manuscrito la
      reporta, cualquiera que sea la regla del punto 9. Su p-valor sale de
      `SeedSequence(143, (awbapp_<índice>_D<D>, j))`.
    - Tamaño fuera de muestra:
      - sobre los mismos paseos de B9.6 (familia 106, celdas `oos_D<D>`);
      - Paso 0: RM-GLS θ = 0.02 recalculado sobre esos paseos reproduce las
        tasas de A10 (|Δ| = 0);
      - la AWB fuera de muestra remuestrea con `awboos_D<D>` de la familia 143.
    - Comparadores: checkpoints de B6 de A8, sin cambios.
    - Tasa común: el mecanismo registrado no cambia (el objetivo es la tasa de
      FP agregada de la primaria, ahora con θ = 0). Con fines informativos se
      añade la fila con θ = 0 al objetivo publicado del v13 (el de A10).
    - Filas de tab:deviations: efecto de θ = 0 frente a θ = 0.02 y frente al
      estadístico registrado, con las mismas funciones que A10.
12. **Figuras (3).**
    - Se regeneran las seis figuras de A11, en inglés, con θ = 0 como
      primaria y sufijo `_audit13`, desde los JSON de A13 y desde las fuentes
      que no dependen de θ.
    - Destinos: `figures/` y la copia en `paper/figures/`. Las `_audit10` no se
      tocan.
    - Los datos graficados se guardan en el JSON de figuras.
13. **Compuerta informativa.** Para cada tabla se da la diferencia máxima, en
    valor absoluto, entre θ = 0 y θ = 0.02 sobre las celdas de RM-GLS, con
    signo y celda. Las unidades son las de cada tabla:
    - tasas, en pp;
    - valores críticos de tab:critB y q(n) de tab:calib, en unidades del
      estadístico;
    - tab:fp: FP en pp, detecciones en número y latencias en días.

    La compuerta no detiene nada.
14. **B13.T.**
    - **Fuentes:** `bA_ma_audit12.json` y `bC_initial_audit12.json`, sin
      simular.
    - **Procedimientos:**

      | Procedimiento | Columna |
      |---|---|
      | RM-GLS θ = 0 | `gls_t0` |
      | (b) | `glsb_t0` |
      | (b′) | `glsbp_t0` |
      | MSB-GLS NP | `msb` (MAIC-GLS de Ng–Perron) |
      | MZ_t-GLS NP | `mzt` |
      | DF-GLS | `dfgls` (MAIC-GLS) |
      | ADF | `adf` (AIC) |
      | PP | `pp` |

    - **tab:serial:** bloque `iid` de las 36 celdas `sz_*`, es decir, cada
      procedimiento con su valor crítico simulado bajo errores iid en el mismo
      n y caso.
      - «NP» se lee como la selección MAIC-GLS de Ng–Perron (etiqueta de A12),
        no como el valor crítico asintótico.
      - Columna del factor poblacional del Bartlett:
        `bartlett_factor_at_median_B.factor`, con su B. Es
        [γ₀ + 2 Σ_{j≤B} (1 − j/(B+1)) γ_j] / ω², con B igual a la mediana del
        ancho de Andrews en la celda (`audit12_unitroot.bartlett_factor`).
    - **tab:serialpower:** bloque `adjusted` de las 36 celdas `pw_*`, con su ρ.
    - **tab:initial:** las 15 celdas de B12.C (3 ρ × 5 variantes de u₀) con la
      potencia de los 9 procedimientos. Se añaden la diferencia de RM-GLS
      θ = 0 frente a DF-GLS (EE pareado) y su McNemar exacto, que ya están en
      el JSON.
    - **Salidas:** Markdown en el reporte y fragmentos LaTeX de sólo el
      `tabular` (`tab_serial_audit13.tex`, `tab_serialpower_audit13.tex`,
      `tab_initial_audit13.tex`), como el T2 de A11.
15. **Exportación de (1)–(2).** Además del reporte se exporta cada tabla
    regenerada con θ = 0 como fragmento `tabular` (`tab_<nombre>_audit13.tex`),
    con las mismas columnas que el v13 y los cambios de la lectura 5. Todos
    los generadores sólo leen JSON. `tests/test_no_literals_audit13.py` los
    recorre, junto con el generador de B13.T y el del reporte.
16. **B13.Q.**
    - Se ejecutará cuando el autor entregue el `.tex` de v14.
    - Mientras tanto se declara pendiente en §5 y no se inventa ningún v14.
    - Al llegar el v14, cada cifra del texto se contrasta con su JSON, con
      archivo:línea, como en el T5 de A11. Si hace falta fijar reglas nuevas,
      irán en una enmienda.
17. **Etiquetas.** «msbhac» de A8–A10 se escribe «MSB-OLS-HAC» en las tablas
    nuevas, como en A12.
18. **Orden.** B13.0 (inventario y semillas) → E(1) → E(2) (DGP 5, AWB,
    aplicación) → E(3) → T → reporte. B13.Q queda fuera de esta cadena.
    `src/` no se toca.
