# Predicción registrada — DGP 5 (desviación mixta)

Escrita antes de ejecutar el experimento.

## Hipótesis
Un estadístico de dos canales no se justifica porque detecte dos clases de desviación
—dos contrastes separados también lo hacen—, sino porque no paga el coste de
multiplicidad de correr dos contrastes.

## Predicción
En la rejilla (rho, r) de DGP 5, a tamaño empírico igualado en 0.05:

1. En el INTERIOR (r en [2, 3], rho en [0.93, 0.95]) el test propuesto tiene mayor
   potencia que la unión Bonferroni de bootstrap DF-GLS y kappa_2.
2. En el EXTREMO DE MEDIA PURA (r = 1) el bootstrap DF-GLS solo tiene mayor potencia
   que el test propuesto.
3. En el EXTREMO DE VARIANZA (r = 4 con rho = 0.95) kappa_2 solo tiene mayor potencia
   que el test propuesto.

## Condición de falsación
Si (1) no se cumple en ninguna celda del interior, la conclusión es que el test
propuesto NO tiene ventaja comparativa operativa y el manuscrito debe reencuadrarse
como contribución sobre calibración. Este resultado se reporta con la misma
prominencia que el favorable.
