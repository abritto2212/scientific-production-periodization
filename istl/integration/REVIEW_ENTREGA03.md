# Revisión de Dirección — entrega 03

Fecha: 7 de noviembre de 2026. Base: `60ea426564f37622a8f7fc090ad3f9d8b63070ac`.

## Dictamen

Entrega aprobada técnicamente con corrección documental del caso 3. No se modificó el manuscrito ni se publicó en GitHub. La incorporación se prepara exclusivamente para `revision/istl`.

## Comprobaciones independientes

- El parche original aplica sobre el commit base sin conflictos.
- Se ejecutaron las 33 pruebas: 11 históricas de v1, 12 de v2 y 10 de v3. Las históricas utilizaron su paquete y datos congelados.
- Se reprodujeron los 60 registros de caso/método/configuración y el diagnóstico separado del caso 10. Cortes, viabilidad, elegibilidad, errores y denominadores coinciden con la entrega.
- La comparación estructural de los cinco JSON de resultados, referencias, agregados, cambios y diagnóstico no encontró diferencias materiales. Hubo 63 diferencias numéricas de redondeo dentro de tolerancia relativa 1e-12 o absoluta 1e-10. No se afirma identidad binaria entre entornos.
- Dos ejecuciones consecutivas en el entorno de Dirección produjeron 12 archivos JSON/CSV/SVG idénticos byte por byte.
- Se recalcularon independientemente los agregados desde las fronteras estimadas y publicadas: MAE macro y coincidencias exactas coinciden.
- El libro cambia únicamente caso 2, 2004: 2 a 1. Las otras 225 observaciones permanecen intactas. La coincidencia con Drive se comprobó contra la instantánea incluida; no se volvió a consultar la hoja en vivo.
- Caso 6 conserva 2024=84 en la fuente y usa 2003–2023, total 712, en los tres métodos. Caso 7 tiene total 273 y subtotales 62/109/102. Caso 10 no recibe concordancia.

## Correcciones de integración

1. Caso 3: cotejo anual completo. La imagen aportada por Sebastián el 7 de noviembre fue contrastada por Dirección con las 23 observaciones del Excel, 2000–2022, total 368. Se actualizó el generador de evidencia, las pruebas y las figuras. No cambia ningún conteo, frontera o resultado individual. La diferencia frente a 376 se conserva sin explicación supuesta.
2. El agregado de series con figuras verificadas incluye ahora al caso 3: ocho casos y quince fronteras con mínimo de dos años. Coincide con el agregado principal común. Se elimina la necesidad de excluirlo por falta de cotejo.
3. Se corrigió la ubicación de la Figura 1 del caso 7 a página 109; las fases textuales están en página 116.
4. Se conservó el informe original del chat 01 con una adenda visible. Las menciones históricas de cotejo pendiente quedan sustituidas por este dictamen y los resultados regenerados.

## Resultados principales confirmados

| Mínimo | Casos comunes | Fronteras | Derivadas MAE | Regresión MAE | Dynp L2 MAE |
|---|---|---:|---:|---:|---:|
| 2 años | 2,3,4,5,6,7,8,9 | 15 | 3.6875 | 3.1875 | 4.3125 |
| 3 años | 4,7,8,9 | 7 | 3.2500 | 3.6250 | 4.1250 |

Las coincidencias exactas son respectivamente 3/15, 3/15 y 1/15 en el análisis principal; 2/7, 1/7 y 0/7 en sensibilidad. No deben compararse los dos agregados como efecto puro de la restricción, pues cambian los casos.

## Alcance

La verificación respalda reproducción de figuras y comparación de fronteras dado K. No certifica registros bibliográficos primarios, deduplicación ni validez histórica de las fases. Se mantienen las diferencias entre totales fuente y declarados. No se alteraron los algoritmos para acercarlos a las referencias.

## Aplicación

El parche revisado se genera como correo de Git y se aplica con `git am`, sobre la base indicada. Sustituye al parche original de entrega 03; no aplicar ambos. No incluye merge a main.
