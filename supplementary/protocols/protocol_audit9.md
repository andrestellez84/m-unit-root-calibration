# Protocolo de la auditoría A9 — configuración final del estadístico primario

Registrado antes de cualquier cómputo de A9 (B9.0). Las reglas de decisión de
§B9.2, §B9.3 y §B9.5 se copian literalmente del encargo; también se copian las
clasificaciones de §B9.1. La sección "Lecturas operativas" fija, antes de ver
datos, cómo se aplica cada regla donde el encargo admite más de una lectura.
Enmiendas: archivo propio (`protocol_audit9_amendN.md`), commit propio y fila en
§4 del reporte.

## Reglas copiadas literalmente

### COMPUERTA B9.1 (INFORMATIVA)

Compuerta B9.1 (INFORMATIVA). Clasifica y reporta con su número:

* E1 "la ventaja en tendencia sobrevive": con valores críticos simulados, la primaria supera a DF-GLS-sim y a MZ_t-GLS-sim en al menos 8 de las 12 celdas del caso con tendencia, con McNemar p < 0.05 en al menos 6.
* E2 "la ventaja a persistencia moderada sobrevive": en DGP 1 a n = 200, la primaria supera a DF-GLS-sim en ρ ∈ {0.80, 0.85, 0.90, 0.93} con McNemar p < 0.05 en al menos 3 de las 4.

No detiene.

### REGLA B9.2 (DURA)

Regla de decisión del θ primario (DURA, pre-declarada; aplícala mecánicamente y reporta cada término):
Sea `P(θ)` la potencia local media en c ∈ {5, 10, 15} del caso demeaned. Son admisibles los θ que cumplen las dos:

* (A1) tamaño gaussiano dentro de la región exacta de N = 20 000 en n = 200, 500 y 1000, en ambos casos deterministas;
* (A2) media de Δ en las 16 celdas GARCH con n ≤ 500 no peor que la del mejor θ en más de 0.30 pp.

Entre los admisibles, el primario es el de mayor `P(θ)`; si dos quedan a menos de 1 pp de `P`, gana el θ mayor. Si el ganador es θ = 0, decláralo sin más: el primario es el estadístico sin suavizado.
Reporta además, para el θ ganador y para θ = 0, la tasa de DGP 3 a r = 4 y n = 200, porque es el coste conocido de la construcción.

### REGLA B9.3 (atribución)

Regla de atribución (pre-declarada): la diferencia (a) − (b) se atribuye al estimador de escala; la diferencia (b) − (c) a la calibración. Reporta ambas diferencias con su error estándar pareado, por celda y en media por n. No interpretes más allá de eso.

Variantes (literal):

* (a) escala σ̂_HAC (Bartlett, Andrews α(1)) + valores críticos simulados de muestra finita;
* (b) escala s²_AR con MAIC + valores críticos simulados de muestra finita;
* (c) escala s²_AR con MAIC + valores críticos asintóticos de Ng–Perron — es decir, MSB-GLS estándar.

### REGLA B9.5 (INFORMATIVA)

Regla de decisión (pre-declarada, INFORMATIVA): la calibración AWB se recomienda en el paper como variante para series con volatilidad no estacionaria si (i) en DGP 3 queda dentro de la región en al menos 4 de las 6 celdas, y (ii) pierde a lo sumo 3 pp de potencia frente a la calibración simulada en las cuatro celdas de DGP 1.

## Lecturas operativas (fijadas antes de ver datos)

1. **Familias.** Una por bloque: B9.0 = 100, B9.1 = 101, B9.2 = 102, B9.3 = 103,
   B9.4 = 104, B9.5 = 105, B9.6 = 106, B9.7 = 107; 108–109 para enmiendas. El
   texto de B9.2 dice "familia 101"; prevalece la asignación una-por-bloque
   (B9.2 = 102). Las familias 100, 101 y 103 no generan trayectorias: B9.1 y B9.3
   usan trayectorias existentes y la calibración de producción.
2. **Calibración bajo la Ec. (3).** Todos los procedimientos se calibran sobre los
   mismos caminos: los de producción (`build_null_cdf`, semilla 42, N_cal =
   50 000, un `standard_normal(n)` por camino), con la selección de retardos
   dentro del bucle. Así la columna RM-GLS (θ = 0.1, `hac`) es bit a bit la nula
   de producción de A8 (control en cada análisis) y las variantes (a) y (b) de
   B9.3 comparten la muestra de calibración. RM, RM-GLS, MSB-HAC y la variante
   (b) rechazan con p = F̂(stat) < 0.05 (ECDF de producción); los demás con
   stat < cuantil 5% (cola inferior).
3. **θ = 0.** τ₁ = 0 (`tau_mode = "zero"` de producción) con anclaje GLS: el
   estadístico sin suavizado rodante. θ ∈ {0.02, 0.05, 0.1, 0.2} usan τ₁ =
   round(θ n) acotado a [2, n/2].
4. **KPSS y ZA "sim".** ZA: stat < cuantil 5% bajo la Ec. (3). KPSS contrasta la
   estacionariedad; su versión "sim" rechaza la raíz unitaria cuando el
   estadístico queda por debajo de su cuantil 5% bajo la Ec. (3). La columna
   asintótica de KPSS es la de A8 (rechazo de la estacionariedad, p < 0.05).
5. **E1.** Una celda cuenta como "supera" si la tasa de la primaria es
   estrictamente mayor que la de DF-GLS-sim y que la de MZ_t-GLS-sim; cuenta
   para "McNemar p < 0.05" si además los dos McNemar exactos (bilaterales) dan
   p < 0.05. E1 se cumple con ≥ 8 y ≥ 6.
6. **E2.** Se cumple si la primaria supera a DF-GLS-sim en las cuatro ρ y, en al
   menos 3 de ellas, con McNemar p < 0.05. Se reporta también la lectura "en al
   menos 3 de las 4 celdas la primaria supera con p < 0.05".
7. **A1.** Tamaño de RM-GLS(θ) `hac` sobre N = 20 000 trayectorias gaussianas
   independientes (familia 102; las mismas para los dos casos) dentro de la
   región exacta de N = 20 000 en n = 200, 500 y 1000, casos demeaned y con
   tendencia: seis condiciones.
8. **A2.** Hay 8 celdas GARCH con n ≤ 500; "las 16" se lee como esas 8 en los dos
   casos deterministas (16 celda-caso). Δ = tasa GARCH − tasa gaussiana
   independiente al mismo n y caso. "Peor" = media de Δ mayor (más liberal, como
   G3 de A8). Admisible si media Δ(θ) − min_θ' media Δ(θ') ≤ 0.30 pp. Se
   reportan también las lecturas alternativas (solo demeaned; |media Δ|) y si
   cambiarían el veredicto.
9. **Desempate.** Sea θ* el admisible de mayor P; los admisibles con P(θ) >
   P(θ*) − 1 pp forman el grupo de empate y gana el mayor θ del grupo. P(θ) es la
   media simple de las tres potencias en c = 5, 10 y 15 (n = 2000, N = 20 000).
10. **Envolvente.** Las trayectorias de potencia local de B9.2 son nuevas
    (familia 102), así que la envolvente de A8 (familia 94) no es reutilizable
    bit a bit: se recalcula (P_T de ERS con c̄ = −c, w² = s²_AR del caso, umbral
    en la muestra de calibración) y se reporta su diferencia con la de A8.
11. **B9.3.** (a) = RM-GLS con τ = 0 y σ̂_HAC, calibración `hac` simulada; (b) =
    el mismo estadístico con σ̂² sustituida por s²_AR(MAIC) del caso, en los datos
    y en cada camino de calibración; (c) = MSB-GLS de Ng–Perron con su valor
    crítico asintótico (0.233 / 0.168). (b) y (c) difieren además en la
    convención del estadístico (ᾱ = 1 + c̄/n frente a 1 + c̄/T, índices de la
    suma); se reporta MSB-GLS-sim como control de esa parte. Casos: tamaño y mala
    especificación en ambos casos; DGP 1 demeaned; caso con tendencia; potencia
    local en ambos casos. EE pareado = desviación típica de las diferencias de
    indicadores / √N; en Δ se combina en cuadratura con la parte gaussiana.
12. **B9.4.** La muestra de n = 20 000 (familia 104) se contrasta con las 20 000
    trayectorias independientes de cada n (familia 102); umbral KS al 5%:
    1.358·√(2/20 000). Tamaño en cada n (trayectorias independientes) con el
    cuantil 5% de n = 20 000 frente al cuantil de la calibración en n. DF-GLS y
    MSB-GLS: valores críticos asintóticos publicados (ERS 1996: −1.95 / −2.89;
    Ng–Perron 2001: 0.233 / 0.168) frente a los simulados en n.
13. **B9.5.** AWB de bootUR 1.0.5 con sus valores por defecto: l = round(1.75
    T^{1/3}), γ = 0.01^{1/l}, T = n + 1; residuos bajo la nula con intercepto y
    retardo 0 (como `boot_adf` en A6–A8); ξ₁ ~ N(0, 1) estacionario; Y*₀ = 0;
    p* = #{stat* ≤ stat}/B, rechazo si p* < 0.05. Semilla de cada serie:
    SeedSequence(105, spawn_key = (celda, i)). N_sim = 2000 (primeras 2000
    trayectorias de cada celda de origen). Región de (i): exacta binomial de
    N = 2000. (ii): potencia(sim) − potencia(AWB) ≤ 3 pp en cada una de las
    cuatro celdas de DGP 1, sobre las mismas 2000 trayectorias.
14. **Bloques CARO.** B9.2 (12 h) y B9.5 (8 h): sonda de 14 series por tipo de
    celda, extrapolación, y detención si la proyección excede el presupuesto.
