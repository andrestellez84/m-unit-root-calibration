# Predicción registrada de la auditoría A12 (errores MA)

Se registra y se commitea antes de cualquier cómputo de A12, en un commit
propio, como la predicción de DGP 5. Su sha256 se reporta en B12.0 y en el
reporte. Copia literal del encargo:

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
