# Enmienda 8 (auditoría A18): B18 — reempaquetado final

Se commitea antes de empezar. Productos con sufijo `_audit18`. Sin simulación ni generación de cifras.

## 1. Encargo (literal)

```
B18 — Reempaquetado final. Sin simulación ni generación de cifras.
Enmienda 8 commiteada antes de empezar.

1. Sustituye sec3_theory.tex por el de paper_latex_v18b.zip (escritorio).
   Único cambio respecto al v18: línea 176, l = round(1.75 T^{1/3}) and
   T = n + 1. Comprueba con diff que no hay otro.
2. Nota de la tabla S4.3: añade «The AWB p-value here is
   \#\{S^{*} \leq S\}/R, not the (1 + \#)/(R + 1) of Section 3.5 of the
   main text.» Registra la edición en el JSON.
3. Elimina CreationDate y ModDate (y cualquier zona horaria) de todos los
   PDF del paquete: figuras del cuerpo y del suplemento. Conserva el
   contenido y verifica con pdfinfo que no queda fecha.
4. Regenera MANIFEST.sha256. Compila el cuerpo y el suplemento juntos:
   0 errores, 0 referencias indefinidas. Repite la búsqueda de
   identificadores.
5. Genera submission_v18b.zip. Reporta su sha256 en
   resultados_auditoria_18.md. Commits por ruta explícita.
```

## 2. Entradas

**E8.0.** `paper_latex_v18b.zip` (escritorio), sha256 `31b4cda1c6427eb06a545981a2af16ca6ef0a9507f46167e5e2bb41eeebff221`. Frente a
`paper_latex_v18.zip` difieren `sec3_theory.tex` y `main.pdf`, que no entra en el paquete. No se edita ningún `.tex`: el paquete se
arma desde el zip del v18b.

## 3. Lecturas operativas

**E8.1 (1).** `audit18_diff.py` compara todos los miembros de los dos zips:
- archivos distintos, con los finales de línea normalizados;
- en `sec3_theory.tex`, las líneas cambiadas (difflib).

Criterio: el único archivo de texto distinto es `sec3_theory.tex`, y en él la única línea cambiada es la 176. Además se comprueba
que esa línea escribe `l = \mathrm{round}(1.75\,T^{1/3})` y `T = n + 1`, la regla del código registrada en
`boot35_v18_audit17.json`.

**E8.2 (2).** `audit18_supplement.py` reutiliza `audit17_supplement.py` sin modificarlo:
- **Remisiones.** Las remisiones al cuerpo se numeran con la compilación de control del v18b.
- **Edición.** Una sola, en el bloque transcrito que contiene tab:awb (S4.3): tras «for 2000 paths.» se añade la frase del
  encargo, con las fórmulas en modo matemático:

  «The AWB p-value here is $\#\{S^{*} \leq S\}/R$, not the $(1 + \#)/(R + 1)$ of Section~3.5 of the main text.»

  Se exige que el ancla aparezca una sola vez. Se comprueba además que `sec:bootdef` es la sección 3.5 en la compilación del v18b,
  y que `e_awb_audit13.json` registra el p-valor `#{stat* <= stat} / B` (con B = R = 399).
- **Registro.** La edición queda en el JSON.

**E8.3 (3). Fechas de los PDF.**
- **Qué se hace.** En cada PDF del paquete (la figura del cuerpo, desde el zip del v18b, y las cinco de `supplementary/figures/`) se
  eliminan del diccionario Info las claves `/CreationDate` y `/ModDate`, con PyMuPDF. Se comprueba que no hay metadatos XMP.
- **Contenido.** Se conserva: el flujo de contenido de cada página es idéntico byte a byte y la página rasterizada a 72 ppp es
  idéntica antes y después.
- **Verificación.** `pdfinfo` (MiKTeX) sobre cada PDF resultante no debe mostrar `CreationDate` ni `ModDate`, y el Info no debe
  contener ninguna fecha (patrón `D:\d{8}`).
- **Dónde se aplica.** Las figuras del suplemento se limpian en `supplementary/`, que se commitea, y la del cuerpo en el paquete.

**E8.4 (4).**
- **MANIFEST.** Se regenera `supplementary/MANIFEST.sha256` después de limpiar las figuras.
- **Compilación conjunta.** Con `audit18_package.py`, que sigue la lectura E7.5 sobre el v18b: v18b con pdflatex ×2 y el .bbl
  entregado, más la comprobación de que el .bbl coincide con el de bibtex; el suplemento con pdflatex, bibtex y pdflatex ×2.
  Criterio: 0 errores y 0 referencias o citas indefinidas en los dos.
- **Identificadores.** Se repite la búsqueda con los patrones de B15.5 sobre todos los archivos de texto, los nombres de archivo y
  los metadatos de los PDF, ahora también con el patrón de fecha.

**E8.5 (5).**
- **Zip.** `submission_v18b.zip` va al directorio temporal de la sesión, no se commitea y se entrega al autor.
- **Reporte.** Su sha256 va en `resultados_auditoria_18.md`, que genera `audit18_generate_report.py`. Este solo lee JSON y lo recorre
  `tests/test_no_literals_audit18.py`.
- Commits por ruta explícita.
