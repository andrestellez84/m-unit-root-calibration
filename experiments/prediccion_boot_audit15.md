# Predicción registrada de A15 (B15.1 y B15.3)

Se commitea antes de cualquier cómputo de B15.1 y B15.3 (incluidas sus sondas y el Paso 0 contra bootUR). Las lecturas
operativas están en `protocol_audit15.md` (1.6–1.10 y 3.7) y en `protocol_audit15_amend1.md` (E1.1, E1.3 y E1.4).

## B15.1 — Bootstrap de MZ_t-GLS bajo correlación serial

Brazos: (i) valor asintótico NP2001; (ii) valor iid de `b1_critical_audit14.json`; (iii) sieve basado en diferencias con
la nula impuesta; (iv) AWB de def:awb; (v′) «SWB (bootUR)»: el sieve wild bootstrap de bootUR 1.0.5, replicado desde su
código fuente y aplicado a MZ_t-GLS (enmienda 1, E1.3). El brazo (v) original (Cavaliere–Taylor 2009) queda «No
ejecutado: sin el PDF».

Definiciones (literales del encargo):

- D(arm) = media de |size − 0.05| sobre las celdas con ψ ≠ 0; M(arm) = máximo de esa desviación.
- «Domina en tamaño» si se cumplen las tres: D ≤ D(ii) − 0.005, M ≤ M(ii) − 0.010, y el brazo en la región exacta en
  las 6 celdas iid.
- «Sin costo» si, en toda celda de potencia, la potencia ajustada es ≥ la de (ii) − 1.0 pp, o McNemar exacto p ≥ 0.05.
- Se evalúa por separado para (iii) y (v′) «SWB (bootUR)».
- Desenlaces: A = algún brazo domina y sin costo; C = domina con costo; B = ninguno domina.

Precisiones operativas (protocolo, lecturas 1.8 y 1.10):

- «Celdas con ψ ≠ 0»: las 30 celdas cuyo error no es `ma_0` (o las que queden tras la reducción (2), declaradas).
- «Celdas iid»: las 6 celdas `ma_0`; región exacta binomial al 95 % para el N de la celda.
- Potencia ajustada: umbral = cuantil 5 % del p-valor del brazo en la celda nula del mismo error (n = 200, mismo caso);
  para (ii), cuantil 5 % de MZ_t-GLS en esa celda.
- McNemar exacto bilateral, pareado sobre los caminos, brazo frente a (ii), con decisiones ajustadas.
- Si (iii) y (v′) cumplen desenlaces distintos, el desenlace global es el mejor en el orden A > C > B, y se reportan los dos.

## B15.3 — Fixed-b sobre MSB-B

- «Fixed-b controla el tamaño» si, para algún b ∈ {0.1, 0.3, 1.0}, M(b) ≤ 0.02 sobre las 30 celdas con ψ ≠ 0.
- Costo de potencia medido frente a MSB-B con Andrews y frente a (b), en los 7 AR de DGP 1 (n = 200, caso constante),
  potencia ajustada, diferencia pareada y McNemar exacto. No hay umbral de costo registrado: se reporta.

## Pronóstico del autor

sin pronóstico del autor
