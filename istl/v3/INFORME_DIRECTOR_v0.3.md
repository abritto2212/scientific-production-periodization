> Adenda de Dirección, 7 de noviembre de 2026: el caso 3 tiene cotejo completo de sus 23 etiquetas (368 publicaciones). Las menciones de pendiente en el informe original quedan sustituidas por esta verificación. Véase `../../integration/REVIEW_ENTREGA03.md`.

# Entrega 03 — informe breve para Dirección

6 de noviembre de 2026. Base: `60ea426564f37622a8f7fc090ad3f9d8b63070ac`.
Se conservaron las entregas anteriores. No se modificó el manuscrito ni se
intentó publicar en GitHub. El parche solo modifica el Excel de trabajo y
añade `ENTREGA03.md` e `istl/v3/`.

## Cambios comprobados

| Caso | Cambio frente a entrega 02 | Comprobación |
| --- | --- | --- |
| 2 | Excel:2004=2→1; 2005 y años posteriores intactos | Total 1693; única diferencia con Drive antes de corregir |
| 6 | Ventana 2003–2023 pasa a ser la comparación aprobada, no sensibilidad alternativa | 21 años,712; fuente completa conserva 2004=7,2024=84, total 796 |
| 7 | Identidad y 23 conteos confirmados por Dirección/Sebastián; se incorpora K=3 | Total 273; texto 2000–2012/2013–2019/2020–2022; subtotales 62/109/102 |
| 8 | Se actualiza estado a 23 conteos cotejados con figura | Total 1004; fronteras textuales 2009/2017 |
| 9 | Se actualiza estado a 23 conteos cotejados con figura | Total 483;98/385; una frontera textual 2012 |

El Excel del commit base aún tenía 2004=2 en caso 2; Drive ya tenía 1. Tras corregir
esa celda, coinciden las 226 observaciones. Las otras 225 permanecen intactas;
solo cambia el miembro `xl/worksheets/sheet2.xml` del libro. Se conservaron
el Excel previo y los paquetes originales. El código de los métodos no cambia.

La integración de Dirección ya certificaba etiquetas de figuras en 1,4,5 y 10;
se retiene ese alcance. Caso 3 sigue sin cotejo anual completo. La fuente de
cada cambio de evidencia se registra: integración del commit base o instrucción
actual de Dirección/Sebastián, no una nueva auditoría del asistente.

## Cortes del escenario principal: mínimo dos años

| Caso | Referencia | Derivadas-K | Regresión-K | Dynp L 2-K |
| --- | --- | --- | --- | --- |
| 1 | 2007,2013,2019 | Inviable | 2009,2017,2021 | 2009,2017,2019 |
| 2 | 2014,2020 | 2014,2019 | 2014,2019 | 2014,2018 |
| 3 | 2009,2017 | 2017,2021 | 2012,2018 | 2018,2021 |
| 4 | 2011,2017 | 2009,2017 | 2012,2015 | 2007,2019 |
| 5 | 2012,2018 | 2017,2023 | 2017,2022 | 2018,2022 |
| 6 | 2011,2018 | 2017,2022 | 2016,2018 | 2016,2020 |
| 7 | 2013,2020 | 2015,2020 | 2013,2019 | 2009,2019 |
| 8 | 2009,2017 | 2016,2020 | 2017,2021 | 2015,2019 |
| 9 | 2012 | 2018 | 2020 | 2021 |

La corrección de una publicación en caso 2 cambia Dynp de 2015/2018 a 2014/2018,
sin mover regresión o derivadas. El caso 6 coincide con la sensibilidad recortada
de entrega 02; ahora su ventana es la aprobada para todos. El 7 añade resultados
antes no ejecutados. Los demás cortes no cambian; ver delta por caso/método/mínimo.
El 10 conserva diagnóstico separado, sin K publicado ni concordancia.

## Agregados sobre conjuntos comunes

MAE macro: media del MAE de cada caso. Exactos: aciertos/fronteras del conjunto.

| Configuración | Casos comunes a los tres | Método | MAE macro, años | Exactos |
| --- | --- | --- | --- | --- |
| Mínimo 2 | 2,3,4,5,6,7,8,9 (8 casos,15 fronteras) | Derivadas-K | 3,6875 | 3/15 |
| Mínimo 2 | Mismo conjunto | Regresión-K | 3,1875 | 3/15 |
| Mínimo 2 | Mismo conjunto | Dynp L 2-K | 4,3125 | 1/15 |
| Mínimo 3 | 4,7,8,9 (4 casos,7 fronteras) | Derivadas-K | 3,2500 | 2/7 |
| Mínimo 3 | Mismo conjunto | Regresión-K | 3,6250 | 1/7 |
| Mínimo 3 | Mismo conjunto | Dynp L 2-K | 4,1250 | 0/7 |

Para comparar mínimos sobre **los mismos cuatro casos 4,7,8,9**, los MAE
macro con mínimo 2/3 son: derivadas 3,2500/3,2500; regresión 4,0000/3,6250;
Dynp 4,6250/4,1250. No se interpreta el cambio entre las muestras de 8 y 4 casos
como efecto puro de la longitud mínima. También se exportan intersecciones
de regresión/Dynp y conjuntos de figuras cotejadas, todos con denominadores.

Con mínimo 3, la referencia del caso 2 no es representable por su fase final
de dos años, aunque los tres algoritmos sí generan soluciones válidas. No se
puntúa ese caso en tal con figuración. Derivadas-K es inviable en 1,3,5,6 con
mínimo 3 y solo en 1 con mínimo 2. No se rellenan cortes ni se altera el umbral.

## Evidencia y límites para el artículo

Se usan las fases del texto en 7/8/9. El registro interno conserva el conflicto
con encabezados gráficos comunicado por Dirección. No se recibieron sus
literales ni constan en el registro de integración; quedan sin transcripción,
sin inventar años o reinterpretar las fronteras aprobadas.

Persisten diferencias entre sumas de las figuras y totales de artículos:
1:1787/1795;2:1693/1697;3:368/376;4:358/360;6:796/797 en fuente completa;
7:273/330;8:1004/1064;9:483/511;10:2165/2411. La diferencia se registra,
**no se atribuye a años excluidos por resta**. Caso 5 coincide en 663 y conserva
2024 parcial. Las verificaciones reproducen figuras, no auditan registros,
deduplicación o reglas de asignación del año bibliográfico.

Los valores apoyan una comparación aplicada de ubicación de cortes dado K,
no el descubrimiento de K, la validez histórica ni una superioridad general.
La flexibilidad de rectas con dos puntos y la cobertura desigual de derivadas
deben permanecer visibles. Caso 3 debe señalarse como exploratorio: el agregado
común que lo excluye contiene 7 casos/13 fronteras con mínimo 2. No se sustituye
la antigua Tabla 2 por una afirmación de ganador.

## Verificación y archivos

Las pruebas nuevas cubren celda única, ventanas, totales, subtotales, fronteras,
conjuntos comunes, inviabilidad y preservación de archivos del commit base.
Las suites anteriores se ejecutan con sus datos congelados en una copia
aislada; no se mezclan con el Excel corregido. Se repite la ejecución para
comprobar igualdad SHA 256 de JSON/CSV/SVG. Véase `results/verification.txt`.

Resultados completos:[JSON](results/results.json),[CSV](results/results.csv),
[agregados](results/common_set_summaries.csv),[cambios frente a 02](results/delta_vs_entrega02.json).
Evidencia:[registro](results/references_and_evidence.json),[datos](data/data_audit.json).
Ejecución:[README](README.md). Figuras:[mínimo 2](results/figures/comparison_min2.svg),
[mínimo 3](results/figures/comparison_min3.svg),[caso 10](results/figures/case10_diagnostic.svg).

El paquete incluye un parche binario/textual aplicable al commit base indicado,
con comprobación de aplicación y reproducción de los archivos entregados.
Dirección coordinará su revisión e incorporación exclusivamente en `revision/istl`.
