# Protocolo de la auditoría A12: errores MA, variante Perron–Qu, condición inicial y θ = 0

Se registra antes de cualquier cómputo de A12, incluida la sonda de
presupuesto. La predicción va en su propio archivo
(`experiments/prediccion_ma_audit12.md`), commiteado aparte y antes que este.
Las enmiendas posteriores van en `protocol_audit12_amendN.md`, con commit propio
y fila en §4 del reporte.

El encargo se copia literalmente (sección 1). Las decisiones del autor tomadas
en el chat antes de registrar el protocolo están en la sección 2. Las lecturas
operativas, fijadas antes de ver datos, están en la sección 3.

## 1. Encargo (literal)

```
AUDITORÍA A12 — Errores MA, la variante Perron–Qu, la condición inicial y θ = 0
Sufijo _audit12. Familias de semillas 130–139 (A = 130, B = 131, C = 132,
D = 133, E = 134, F = 135, calibraciones nuevas = 136, sondas = 137).
Verifica colisión contra todas las familias previas (A8 90–99, A9 100–109,
A10 110–119, A11 120–129) y regístralo en B12.0.

REGLAS GENERALES (vigentes de A7–A11)
- protocol_audit12.md commiteado ANTES de cualquier cómputo. Incluye, copiados
  literalmente, los desenlaces A/B/Intermedio/C y la predicción registrada
  (abajo). Enmiendas: archivo y commit propios.
- prediccion_ma_audit12.md: archivo aparte con la predicción, commit propio,
  hash en el reporte, igual que en DGP 5.
- Paso 0 (máx. |Δ| = 0) al reutilizar trayectorias o checkpoints.
- No toques src/. Todo el código nuevo va en experiments/audit12_*.py. Si
  resultara imprescindible tocar producción, regresión pre/post sobre las
  celdas de control de A10 con |Δ| = 0.
- Generadores de tablas que sólo leen JSON, con test de literales
  (tests/test_no_literals_audit12.py).
- Reporte resultados_auditoria_12.md con las siete secciones (Resultados,
  Compuertas, Procedencia, Desviaciones, No ejecutado, Conclusiones,
  Anomalías y contradicciones con el manuscrito) y la tabla maestra
  (clave | valor | IC/EE | N_sim | N_cal | familia | JSON | ruta).
B12.0 — Inventario y protocolo (familia de verificación, sin cómputo pesado)
- Hashes de los JSON reutilizados: b101_theta_audit10.json,
  b103_equalized_audit10.json, b92_theta_audit9.json, b93_attribution_audit9.json,
  b97_critical_values_audit9.json, t3_anchor_audit11.json.
- Implementa en experiments/audit12_unitroot.py:
  (i) generador MA(1): v_t = e_t + psi e_{t-1}, e_0 = 0; generador AR(1):
      v_t = phi v_{t-1} + e_t, v_0 ~ N(0, 1/(1-phi^2)); y_t = y_{t-1} + v_t,
      y_0 = 0 bajo la nula; bajo la alternativa u_t = rho u_{t-1} + v_t, u_0 = 0.
  (ii) MAIC-MCO a la Perron–Qu (2007): se elige k con la MAIC de NP aplicada a
      datos detrendidos por MCO (constante o constante+tendencia); con ese k se
      calcula s2_AR, MSB, MZ_t y DF-GLS sobre datos detrendidos por GLS. Test
      unitario: con k fijo, coincide con np_statistics(k=k) a 1e-12.
  (iii) variante (b'): el estadístico RM-GLS con theta = 0 y s2_AR de (ii).
- Test de convención: con psi = 0 las funciones nuevas reproducen las filas de
  A10 (Paso 0) en 50 caminos de familia 110.

PREDICCIÓN REGISTRADA (copiar literal en prediccion_ma_audit12.md)
Derivación: el Bartlett con ancho de Andrews sobreestima omega^2 bajo MA(1)
psi < 0 por el factor 1 - 2 psi / [(B+1)(1+psi)^2]; a psi = -0.8, n = 200,
B = 8, el factor poblacional es 5.44 y S se multiplica por ~0.43.
Predicción: desenlace B. Tamaño de RM-GLS theta = 0 con valor crítico iid a
(psi = -0.8, n = 200, constante) > 0.30; a psi = -0.5 entre 0.08 y 0.20;
conservador (< 0.05) a phi = +0.5. Para C sólo se registra dirección:
(b') > (b) en DGP 1, n = 200.
Desenlaces (umbrales):
 A: a psi = -0.8, n en {100, 200}, ambos casos, tamaño(RM-GLS theta=0, cv iid)
    <= tamaño(MZ_t-GLS NP, cv asintótico) + 2 pp y <= 0.10; a psi = -0.5,
    <= MZ_t + 1 pp.
 B: tamaño(RM-GLS theta=0, cv iid) >= 0.15 a (psi = -0.8, n = 200) en algún
    caso, o >= MZ_t + 5 pp.
 Intermedio: ni A ni B.
 C: en DGP 1 constante n = 200, media sobre los 7 rho de (a) - (b') <= 1.0 pp
    con EE pareado <= 0.2 pp.

B12.A — Errores MA y AR (PRIMERO; familia 130)
Nulas: psi en {-0.8, -0.5, 0, 0.5}; phi en {-0.5, 0.5}; n en {100, 200, 500};
casos c y ct. 20 000 caminos por celda (36 celdas); casos con hijos distintos.
Procedimientos (todos sobre los mismos caminos de la celda):
 RM-GLS theta = 0.02; RM-GLS theta = 0; (b) theta=0 con s2_AR MAIC-GLS;
 (b') theta=0 con s2_AR MAIC-MCO; MSB-GLS y MZ_t-GLS (NP y PQ); DF-GLS
 (MAIC-GLS y MAIC-MCO); ADF (AIC); PP (Newey-West Bartlett).
Valores críticos: (1) simulados bajo la nula iid gaussiana, N_cal = 5e5 en
n = 100, 200, 500 (reutiliza A10 donde exista, con Paso 0; lo que falte, en
familia 136); (2) asintóticos publicados (NP 2001 Tabla 1; DF-GLS de ERS/Fuller;
ADF y PP de MacKinnon). RM-GLS no tiene asintótico publicado: usa el
calibrado a n = 20 000 de A10 como "límite".
Potencia: alternativas rho = 1 + cbar/n (cbar = -7 en c, -13.5 en ct) con la
misma estructura de error de cada nula, y rho en {0.90, 0.95} con n = 200 en c;
5000 caminos por celda. Dos lecturas: (i) al cv iid; (ii) ajustada al tamaño
con el cuantil 5 % de cada procedimiento en la celda de tamaño de la misma
estructura de error.
Diagnósticos por camino (guárdalos en checkpoint): sigma2_HAC, B de Andrews,
s2_AR (GLS y MCO), k MAIC-GLS y k MAIC-MCO. Reporta medianas y cuartiles de
sigma2_HAC/omega2 y s2_AR/omega2 bajo cada nula y bajo cada alternativa, y la
tabla poblacional del factor de sesgo del Bartlett (cálculo cerrado) al lado.
Compuertas:
 G-A1 (DURA): en las celdas psi = 0, tamaño de cada procedimiento con cv iid
   dentro de la región exacta de N = 20 000 [0.0470, 0.0531]. Si falla alguno,
   detente: es un error de calibración o de convención.
 G-A2 (INFORMATIVA): MZ_t-GLS NP con cv asintótico a psi = -0.8, n = 100
   dentro de ±0.03 de las cifras de NP (2000, Tablas 5.a y 6.a: 0.036 en c,
   0.059 en ct; son de MZ_alpha, "similares" según NP). Si no, reporta y sigue.
 Presupuesto: sonda de 14 x 50 caminos a n = 500, ct, psi = -0.8, todos los
   procedimientos; si la proyección del bloque completo supera 10 h en 14
   núcleos, detente y reporta antes de lanzar.
Clasificación: aplica A/B/Intermedio mecánicamente, cada término con su cifra.
B12.B — Atribución con Perron–Qu (familia 131; trayectorias de A8 familia 95)
Sobre las trayectorias DGP 1 (c, n = 200, 500, 1000; ct, n = 200, 500) de B5/A8
(Paso 0 contra los checkpoints de B9.3), calcula (b') y su calibración
(N_cal = 5e5 a 200, 500, 1000, familia 136). Reporta (a)-(b'), (b')-(b) y
(b')-(c), con EE pareado, por celda y en media por n, como tab:attrib. Más la
potencia local (n = 2000, c = 5, 10, 15) con (b'). Clasifica C.
Diagnóstico: mediana de k MAIC-GLS, k MAIC-MCO, s2_AR(GLS), s2_AR(MCO) y
sigma2_HAC por rho a n = 200.

B12.C — Condición inicial (familia 132)
DGP 1 constante, n = 200, rho en {0.90, 0.95, 0.97}; u_0 = alpha * sigma /
sqrt(1 - rho^2) con alpha en {0, 1, 2, 4} (signo positivo fijo) y una celda
con u_0 ~ N(0, 1/(1 - rho^2)). 5000 caminos pareados por celda.
Procedimientos: RM-GLS theta = 0 y 0.02, (b), (b'), DF-GLS, MZ_t-GLS, MSB-GLS,
ADF, PP, todos al cv iid (que es exacto: bajo la nula u_0 lo absorbe la
constante). Reporta potencia y McNemar frente a DF-GLS.

B12.F — Forma cerrada del sesgo del ancla (barato; familia 135)
Hipótesis a contrastar (no es resultado): E[S0^2] ≈ 1/2 - kappa/(n + cbar^2)
 + lambda/(n + cbar^2)^2, con kappa = 2|cbar|(1/2 + |cbar|/3) = 39.667 y
 lambda = cbar^2 (1 + |cbar| + cbar^2/3) = 1192.33, cbar = -7, sigma conocido.
(1) Calcula E[S0^2] EXACTA con sigma conocido por álgebra matricial
    (u = M Y, E[u'u] = tr(M Sigma M')) para n en {60, 100, 200, 500, 1000,
    2000, 5000, 20000}; no requiere simulación.
(2) Compárala con la fórmula y con t3_anchor_audit11.json (medias simuladas).
(3) Reporta si la media simulada a n = 20000 (0.49218) es compatible con el
    valor exacto; así se cierra la anomalía T3 de A11.
Compuerta INFORMATIVA: |fórmula - exacta| < 0.002 para n >= 200.

B12.E — Regeneración con theta = 0 (SÓLO si el autor lo confirma por escrito
antes de lanzar; familia 134)
(1) Tablas con theta = 0 desde JSON existentes, sin simular: tab:size
    (A10 para 200/500/1000; lo que falte a 60/100/150, nuevo con 5e4 caminos),
    tab:calib, tab:dgp1, tab:ctpower, tab:dgp2, tab:dgp3, tab:misspec,
    tab:localpower, tab:critB (de b97).
(2) Nuevo: AWB con theta = 0 (mismas trayectorias de B9.5, B = 399, presupuesto
    8 h con sonda); DGP 5 con theta = 0 (trayectorias de A7, Paso 0); aplicación
    con theta = 0 (hashes de datos congelados verificados).
(3) Figuras con sufijo _audit12.

B12.D — OPCIONAL, al final: ¿existe un régimen donde theta > 0 ayude? (familia 133)
Rejilla pre-declarada, n = 200, constante, 5000 caminos pareados, cv iid:
 outliers aditivos (proporción 0.02 y 0.05, tamaño 5 sigma) bajo la nula y bajo
 AR(0.95); quiebre de nivel de 1 y 2 desviaciones bajo AR(0.95).
theta en {0, 0.02, 0.05, 0.1}.
Regla de parada: theta > 0 "ayuda" sólo si supera a theta = 0 en >= 1 pp con
McNemar p < 0.01 en al menos 2 celdas de potencia sin empeorar tamaño en más
de 0.5 pp. Si no, se declara que no existe en la rejilla y se cierra.

ETIQUETAS: en el reporte, la columna que A8–A10 llaman "msbhac" (media anclada,
tau = 0, sqrt(n^-2 sum (Y_t - Ybar)^2 / s2_HAC)) se renombra en tablas nuevas
"MSB-OLS-HAC"; no uses "MSB-HAC" para ella.

ORDEN: B12.0 → A → B → C → F → (E si confirmado) → (D si se pide).
```

## 2. Decisiones del autor antes del registro (chat, 2026-09-21)

1. **G-A1 con corrección de Bonferroni.** El autor la eligió frente a la
   lectura literal.
   - El problema: G-A1 evalúa K tamaños, con K = número de procedimientos ×
     3 n × 2 casos en las celdas ψ = 0 (K = 72 con los 12 procedimientos de
     B12.A). Con calibración perfecta, la probabilidad de que los K caigan en
     la región al 95 % es ≈ 0.95^K, del orden de 3 %.
   - Regla registrada: **G-A1 pasa si cada uno de los K tamaños cae dentro de
     la región exacta binomial central de N = 20 000 al nivel 1 − 0.05/K**
     (error de familia 5 %). Se calcula como `exact_region(20000, level = 1 −
     0.05/K)`, con la misma función que la región al 95 %.
   - Si falla, me detengo y reporto, como dice el encargo.
   - Informativo, sin detener: cuántos de los K caen fuera de la región literal
     [0.0470, 0.0531] (exacta: [0.04700, 0.05305]), junto con el número
     esperado por azar, 0.05·K.
2. **B12.E no está confirmado.** No se ejecuta y se declara en §5.
3. **B12.D no se ha pedido.** No se ejecuta y se declara en §5.

## 3. Lecturas operativas (fijadas antes de ver datos)

1. **Familias.**
   - B12.0 es de verificación: no tiene familia propia y no genera
     trayectorias.
   - A = 130, B = 131, C = 132, F = 135 (sin trayectorias: es un cálculo
     exacto), calibraciones nuevas = 136, sondas = 137.
   - D = 133 y E = 134 quedan reservadas y sin usar. 138–139 quedan para
     enmiendas.
   - Semillas: `SeedSequence(familia, spawn_key = (celda, i))`, con celdas en
     listas ordenadas (`audit12_design.py`) y casos, estructuras de error y
     remuestras en celdas distintas.
   - B12.0 comprueba la equivalencia con `SeedSequence(familia).spawn` y la
     ausencia de colisiones contra las familias 90–129, las semillas enteras de
     A5–A7 y la semilla 42 de producción.
2. **Test de convención.** La familia 110 no tiene trayectorias: B10.0 no
   generó ninguna. El test usa trayectorias equivalentes de A10:
   - las 50 primeras de `a1_dm_n200_s1` y `a1_ct_n200_s1` (familia 111,
     checkpoints de B10.1);
   - las 50 primeras filas de la calibración de A10 a n = 200 (semilla 42 de
     producción).

   Con ψ = 0, el generador MA nuevo, alimentado con el mismo `rng`, debe dar la
   misma trayectoria (máx. |Δ| = 0). Las columnas comunes de la fila nueva
   (s2, gls_t0, gls_t0.02, glsb_t0, dfgls, dfgls_p, mzt, msb, k, s2ar, adf,
   adf_p, pp, pp_p) deben coincidir con las de A10 con máx. |Δ| = 0.
3. **Generadores.** El orden de los sorteos queda fijado así:
   - MA(1): `e = rng.standard_normal(n)` da e_1…e_n, con e_0 = 0, y
     v_t = e_t + ψ e_{t−1}.
   - AR(1): `z = rng.standard_normal(n + 1)` da v_0 = z_0/√(1−φ²) y
     v_t = φ v_{t−1} + z_t para t = 1…n.
   - Bajo la nula, y_0 = 0 e y_t = y_{t−1} + v_t (n + 1 puntos). Bajo la
     alternativa, y_t = u_t, con u_0 = 0 y u_t = ρ u_{t−1} + v_t.
   - No se añade componente determinista: todos los procedimientos son
     invariantes a la media, y a la tendencia en el caso ct.
   - ω² es (1+ψ)² en MA y 1/(1−φ)² en AR, con σ_e = 1.
4. **MAIC-MCO (PQ).**
   - Se regresa y sobre `deterministic_matrix(T, caso)` (constante, o constante
     y tendencia t = 1…T) y sobre el residuo MCO se corre la regresión ADF sin
     deterministas de `adf_gls_path`, con kmax = ⌊12(T/100)^{1/4}⌋ y muestra
     común t = kmax+1…T−1.
   - La MAIC es la de NP: ln σ̂²_k + 2(τ_T(k) + k)/(T−1−kmax), con τ_T calculado
     sobre los datos detrendidos por MCO. k_PQ es el argmin.
   - Paso GLS con k fijo: sobre el residuo GLS (c̄ = −7 o −13.5, a = 1 + c̄/T)
     se reestima la regresión ADF con k = k_PQ en la muestra t = k+1…T−1. Es la
     convención de `np_statistics(k=k)` y la de Perron–Qu (reestimar con el k
     elegido).
   - Salen s2_AR^PQ, MSB^PQ, MZ_t^PQ y DF-GLS^PQ (`arch.DFGLS`, lags = k_PQ).
   - El código del paso GLS es independiente de `np_statistics`. El test
     unitario exige coincidencia a 1e-12 con `np_statistics(y, caso, k=k)` para
     k fijo.
   - El lado NP es el de producción de A9–A10: `np_statistics` con MAIC-GLS
     sobre la muestra común de kmax, DF-GLS con ese k.
   - «s2_AR (GLS y MCO)» se lee como s2_AR con el k de MAIC-GLS y con el k de
     MAIC-MCO. Las dos se calculan sobre datos GLS.
5. **(b′)** = `audit9_engine.rmgls(y, n, 0.0, s2_AR^PQ, caso)`, con τ₁ = 0 y
   anclaje GLS.
6. **B de Andrews por camino.** Se replica la regla de
   `hac_estimator.hac_newey_west`: ρ̂₁ acotado a ±0.99, α̂ = 4ρ̂²/(1−ρ̂²)² y
   B = ⌈1.1447(α̂ n)^{1/3}⌉ acotado a [0, n−1], con n = len(Δy). Se comprueba
   que `hac_newey_west(Δy, bandwidth = B)` es igual a `hac_sigma_sq(y)` en
   cada camino de los tests.
7. **Rechazo.**
   - Con valor crítico simulado: RM-like (gls_t0.02, gls_t0, (b), (b′)) usa
     la regla de A9, F̂_null(stat) < 0.05 con `cdf_from_null_stats`; el resto,
     stat < cuantil 5 % (cola inferior).
   - Con valor crítico asintótico:
     - MZ_t y MSB (NP y PQ): NP 2001, Tabla 1 (c: −1.98 y 0.233; ct: −2.91 y
       0.168);
     - DF-GLS: ERS/Fuller (−1.95 y −2.89, convención de B9.4);
     - ADF y PP: p-valor MacKinnon < 0.05 (statsmodels / arch), convención de
       A8.
   - «Límite» de RM-GLS: cuantil 5 % de la muestra de n = 20 000 de B9.4
     (familia 104), la que usó A10 en `size_with_cv_n20000`. Solo existe para
     θ = 0 y 0.02; (b) y (b′) no tienen límite y figuran como «no disponible».
8. **Calibración (valor crítico iid).**
   - A10 tiene N_cal = 500 000 a n = 100, 200, 500 y 1000 (semilla 42) con
     todas las columnas del lado NP. Se reutiliza tras un Paso 0 de 50 filas
     recalculadas con el código de A12.
   - Las columnas PQ (kpq, s2ar_pq, glsbp_t0, mzt_pq, msb_pq, dfgls_pq) se
     calibran en la familia 136, celda `cal_n<n>`, con 500 000 paseos
     gaussianos (Y₀ = 0) y los dos casos en cada camino, en n ∈ {100, 200,
     500, 1000, 2000}.
   - n = 2000 se añade porque la potencia local de B12.B la necesita.
9. **Tamaño ajustado (lectura ii).** El umbral es el cuantil 5 % del
   procedimiento en la celda de tamaño del mismo (estructura de error, n,
   caso). Se rechaza si stat < umbral. Las alternativas ρ ∈ {0.90, 0.95} a
   n = 200 usan la celda (estructura, 200, c).
10. **Clasificación A/B/Intermedio.** Se aplica mecánicamente con el tamaño al
    valor crítico iid de gls_t0 y el tamaño de MZ_t-GLS NP al valor crítico
    asintótico:
    - A: a ψ = −0.8, en n ∈ {100, 200} y ambos casos, gls_t0 ≤ MZ_t + 0.02 y
      ≤ 0.10; y a ψ = −0.5, en n ∈ {100, 200} y ambos casos,
      gls_t0 ≤ MZ_t + 0.01.
    - B: a (ψ = −0.8, n = 200), en algún caso, gls_t0 ≥ 0.15 o
      gls_t0 ≥ MZ_t + 0.05.
    - Intermedio: ni A ni B.
11. **Predicción.** Se contrasta en el caso constante y n = 200:
    - gls_t0 a ψ = −0.8 > 0.30;
    - gls_t0 a ψ = −0.5 en [0.08, 0.20];
    - gls_t0 a φ = +0.5 < 0.05;
    - desenlace B;
    - dirección C: media sobre los 7 ρ de (b′) − (b) > 0 en DGP 1, c, n = 200.
12. **Presupuesto.**
    - La sonda (familia 137, celda `probe_ma_m0p8_n500_ct`) mide 14 × 50
      caminos a n = 500, ct, ψ = −0.8, con la fila completa, tras un
      calentamiento.
    - La proyección es (coste por camino a n = 500) × (caminos de B12.A a
      cualquier n ≤ 500 + caminos de la calibración PQ de la familia 136 a
      n ≤ 500) / 14. Es una cota superior: ningún caso de B12.A supera n = 500
      y la calibración solo calcula columnas PQ.
    - Si pasa de 10 h, me detengo. Cada bloque tiene un tope de 4 h y se puede
      reanudar.
13. **B12.B.**
    - Trayectorias: las de B9.1, que son las de B5 de A8, familia 95
      (`audit9_design.b5_path`):
      - celdas `dgp1_rho*_n{200,500,1000}` (7 ρ) en c;
      - celdas `ct_power_rho*_n{200,500}` en ct.
    - Potencia local: trayectorias de B9.2 (`lp_{dm,ct}_c{5,10,15}`, n = 2000,
      20 000 caminos).
    - Paso 0 frente a los checkpoints de B9.1/B9.2, que son los que leyó B9.3:
      las 50 primeras trayectorias de cada celda, todas las columnas comunes,
      máx. |Δ| = 0.
    - (a) = gls_t0 y (b) = glsb_t0 con la calibración de A10 (N_cal = 500 000,
      n = 200, 500, 1000); (b′) con la de la familia 136; (c) = MSB-GLS NP con
      valor crítico asintótico.
    - En la potencia local a n = 2000, (a) y (b) usan la calibración de A9
      (N_cal = 50 000), como B9.3, y (b′) la de la familia 136.
    - Diferencias pareadas: EE = sd(d_i)/√N. Medias por n con
      EE = √(Σ EE²)/k (convención de B9.3).
    - C: en DGP 1, c, n = 200, media de (a) − (b′) sobre los 7 ρ ≤ 0.010 y EE
      de esa media ≤ 0.002.
14. **B12.C.**
    - Una celda de innovaciones por ρ (`c_rho<ρ>`), con e_1…e_n comunes a los
      cinco valores de u₀ de ese ρ. Eso es el pareo.
    - u₀ = α/√(1−ρ²) con α ∈ {0, 1, 2, 4}. En la celda aleatoria,
      u₀ = z₀/√(1−ρ²), con z₀ de la celda `c_u0_rho<ρ>`.
    - y_t = u_t, t = 0…n.
    - Valor crítico iid de n = 200: A10 para el lado NP, familia 136 para (b′).
    - DF-GLS = el de MAIC-GLS (NP). La McNemar es exacta frente a DF-GLS.
15. **B12.F.**
    - E[S₀²] exacto con σ = 1: Y₀ = 0 y Σ_{st} = min(s, t) para s, t = 0…n.
    - β̂_GLS = w′Y, con w del mapa lineal de `rm_core.gls_mean` (se comprueba
      contra `gls_mean` en trayectorias aleatorias).
    - E[S₀²] = [tr Σ − 2·1′Σw + (n+1)·w′Σw] / (n(n+1)), con Σw calculado en
      O(n) por sumas acumuladas.
    - Se contrasta con tr(MΣM′) denso, con M = I − 1w′, en todos los n ≤ 5000.
      En n = 20 000 solo se usa la vía O(n).
    - Compatibilidad con la media simulada de A11: |media − exacta| < 3 EE.
16. **Etiquetas.** «msbhac» no forma parte de B12.A. Si aparece en una tabla
    nueva, se llama «MSB-OLS-HAC».
