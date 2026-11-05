# 01 · Datos, código y resultados — entrega 02

Fecha: 5 de noviembre de 2026. Destino: 00 · Dirección e integración.
Estado: **comparación provisional y propuesta de protocolo**. No se modificó
el manuscrito ni se intentó publicar esta actualización en GitHub.

## 1. Continuidad y diferencias frente a la entrega inicial

Se partió del paquete `ISTL_validacion_entrega01.zip`, SHA256
`d64e43eee4ba4e6f922e9f2ef38e6907bd16588572bd12be2e13bc109c0fe96d`.
Los 35 miembros del ZIP, incluido su parche, código, pruebas y resultados,
se conservaron byte por byte. No se sustituyeron los resultados iniciales.

| Dimensión | Entrega 01, conservada | Entrega 02, añadida |
| --- | --- | --- |
| Propósito | Corregir implementaciones y ejecutar diagnóstico común | Incorporar fronteras de chat 02 y explorar comparación condicionada |
| K | Dos cortes para regresión/Dynp; derivadas estima | K fases de la fuente, sin inventar K en 7/10 |
| Restricción | Mínimo 3 en todos los segmentos | Escenario provisional mínimo 2; sensibilidad 3 |
| Derivadas | Automático, picos originales y filtro de longitud | Variante Derivadas-K explícita; automático separado |
| Referencias | No disponibles para puntuar | Fronteras documentadas de ocho casos, con límites de procedencia |
| Salida | `istl/results/`, 30 registros diagnósticos | `istl/v2/results/`, 66 registros de estado/resultado y 20 diagnósticos automáticos |
| Publicación | Bloqueada; paquete/parche disponibles | Sin nuevos intentos; dos parches para incorporación coordinada |

Solo se añaden `ENTREGA02.md` y `istl/v2/`. Las funciones originales de la
entrega 01 continúan exigiendo mínimo 3. Los parámetros nuevos viven en un
módulo separado; cuando K=3 y mínimo=3, regresión y Dynp reproducen los
cortes de la primera entrega, comprobado en los diez casos.

## 2. Insumos incorporados

Se leyeron y guardaron instantáneas de las tres fuentes del chat 02:

- [CSV de fronteras v0.1](https://drive.google.com/file/d/1v-2_P4j9NNafCr-58GK-S-1EniCrTKVR/view).
- [Matriz editable de evidencia v0.1](https://docs.google.com/spreadsheets/d/1ZnkvtJpva-whNYGbtDGxZXvmpQvhXPE6M2cO5MpYjI0/edit).
- [Informe de literatura y evidencia v0.1](https://drive.google.com/file/d/1Qy5De2kSIVYZ6wTrvNXymrrF_IsgFgVe/view).

No se reauditaron los artículos ni se digitalizaron gráficas. Se conserva
la fuerza de vinculación A/B/C y la advertencia del chat 02: **ninguna serie
tiene todavía cotejo anual completo**. La matriz y el CSV concuerdan en las
fronteras; los totales de la matriz concuerdan internamente con el libro de
entrada. Esto no resuelve las diferencias con los artículos.

| Caso | K publicado | Fronteras: primer año del período nuevo | Uso provisional |
| --- | --- | --- | --- |
| 1 | 4 | 2007, 2013, 2019 | B; serie pendiente |
| 2 | 3 | 2014, 2020 | B; fase final 2020–2021 de 2 años |
| 3 | 3 | 2009, 2017 | B; serie pendiente |
| 4 | 3 | 2011, 2017 | B; serie pendiente |
| 5 | 3 | 2012, 2018 | A; vínculo fuerte, cotejo anual pendiente |
| 6 | 3 | 2011, 2018 | B; último intervalo textual termina en 2023 |
| 7 | Desconocido | No disponibles | C; sin ejecución condicionada ni puntuación |
| 8 | 3 | 2009, 2017 | B; serie pendiente |
| 9 | 2 | 2012 | A; no convertir 2020 en tercera fase |
| 10 | Desconocido | No partición completa | C; no convertir «alrededor de 2013» en corte exacto |

## 3. Implementación de la comparación provisional

Regresión y Dynp reciben K−1 cortes. Se mantienen objetivos distintos:
rectas independientes frente a medias por bloque. Dynp conserva jump=1.
Todos los algoritmos usan exactamente la misma serie y mínimo dentro de
cada escenario, con el corte como primer año del período nuevo.

**Derivadas-K se incorpora como adaptación provisional explícita.** Mantiene
float64, sigma=2, reflect, truncate=4, dos gradientes anuales y picos de |d2|
con altura mínima std(d2). Entre subconjuntos de K−1 picos que satisfacen el
mínimo común, elige la mayor suma de |d2|; desempata temporalmente. No recibe
los años de referencia para seleccionar picos. Si faltan candidatos, devuelve
inviabilidad, no picos fabricados ni un resultado de menor K puntuado como
equivalente. La formulación completa está en el protocolo propuesto.

El mínimo 2 permite representar la fase corta del caso 2; no se seleccionó
por obtener menor MAE. Tiene una limitación clara: una recta de dos puntos
puede tener residuo cero. El escenario de 3 años muestra la sensibilidad
y mantiene visible esa decisión. No se ajustó sigma, altura ni datos por caso.

## 4. Cortes obtenidos con mínimo 2

| Caso | Referencia | Derivadas-K provisional | Regresión-K | Dynp L2-K |
| --- | --- | --- | --- | --- |
| 1 | 2007, 2013, 2019 | Inviable: solo 2 picos candidatos para 3 cortes | 2009, 2017, 2021 | 2009, 2017, 2019 |
| 2 | 2014, 2020 | 2014, 2019 | 2014, 2019 | 2015, 2018 |
| 3 | 2009, 2017 | 2017, 2021 | 2012, 2018 | 2018, 2021 |
| 4 | 2011, 2017 | 2009, 2017 | 2012, 2015 | 2007, 2019 |
| 5 | 2012, 2018 | 2017, 2023 | 2017, 2022 | 2018, 2022 |
| 6 | 2011, 2018; cobertura hasta 2023 | 2017, 2022 | 2018, 2023 | 2016, 2020 |
| 7 | Desconocida | No ejecutado | No ejecutado | No ejecutado |
| 8 | 2009, 2017 | 2016, 2020 | 2017, 2021 | 2015, 2019 |
| 9 | 2012 | 2018 | 2020 | 2021 |
| 10 | Desconocida | No ejecutado | No ejecutado | No ejecutado |

El caso 6 de esta tabla usa la serie completa 2003–2024 para documentar el
comportamiento algorítmico; no contribuye a las métricas de ventana completa.
Los resultados no son una reproducción de la Tabla 2 histórica.

## 5. Viabilidad frente a cercanía temporal

Con K conocido, regresión y Dynp pueden segmentar los ocho casos con mínimo
2 o 3. Derivadas-K puede segmentar siete de ocho con mínimo 2, y cinco de
ocho con mínimo 3. La falta de picos del caso 1 es visible en ambos escenarios.
Los casos 7/10 tienen K desconocido: no cuentan como fallos algorítmicos.

La ventana completa aporta siete casos documentalmente utilizables de forma
provisional con mínimo 2 (1–5, 8, 9). En el escenario 3, el caso 2 se retira
de métricas porque su referencia viola el mínimo, **aunque los tres métodos
sí producen una partición algorítmica válida**. El caso 6 continúa fuera por
cobertura. Ninguna exclusión se codifica como error cero.

Las métricas emparejan las fronteras por orden cronológico, una a una. La
comparación no permite reutilizar 2017 como referencia de dos predicciones.
Se exportan error firmado y absoluto, MAE por caso y coincidencia exacta.

### Agregados sobre el mismo conjunto dentro de cada escenario

MAE macro = media de MAE de casos, cada caso con el mismo peso.
Coincidencia exacta = aciertos / fronteras del conjunto indicado.

| Mínimo | Casos comunes a los tres | Fronteras | Método | MAE macro, años | Coincidencias exactas |
| --- | --- | --- | --- | --- | --- |
| 2 | 2, 3, 4, 5, 8, 9 | 11 | Derivadas-K provisional | 3,917 | 2/11 |
| 2 | 2, 3, 4, 5, 8, 9 | 11 | Regresión-K | 3,750 | 1/11 |
| 2 | 2, 3, 4, 5, 8, 9 | 11 | Dynp L2-K | 4,833 | 0/11 |
| 3 | 4, 8, 9 | 5 | Derivadas-K provisional | 4,000 | 1/5 |
| 3 | 4, 8, 9 | 5 | Regresión-K | 4,667 | 0/5 |
| 3 | 4, 8, 9 | 5 | Dynp L2-K | 4,667 | 0/5 |

El cambio de conjunto entre mínimos impide atribuir directamente el cambio
de media a la restricción. Por eso también se exporta el conjunto fijo de
casos 4, 8 y 9 para ambos mínimos: MAE macro de derivadas 4,000/4,000;
regresión 5,167/4,667; Dynp 5,333/4,667 (mínimo 2/3). Son descripciones de
tres casos, no evidencia de superioridad general ni selección de parámetros.

`summary.csv` conserva además los disponibles por método: con mínimo 2,
regresión y Dynp tienen siete casos/14 fronteras; derivadas tiene seis/11.
Las medias de esos conjuntos distintos no deben ordenarse como un ranking.
También incluye agregados por frontera y estratos A/B, con nombres separados.

El ejemplo del caso 2 ilustra la convención común: 2014/2019 frente a
2014/2020 produce errores 0 y 1 años, MAE=0,5, sin desplazar etiquetas.
El caso 9, ahora con un solo corte publicado, produce diferencias de 6, 8
y 9 años con mínimo 2. No se cambia la referencia ni se añaden fases para
reducirlas. La semejanza de K no es mérito del método porque K fue impuesto.

## 6. Sensibilidad del caso 6

No se extendió 2018–2023 hasta 2024. La ejecución adicional recorta la serie
solo para explorar la ventana publicada: 2003–2023, 21 observaciones y 712
publicaciones, omitiendo expresamente 2024 con sus 84 publicaciones. Esto
no resuelve la ambigüedad de la fuente ni las diferencias de corpus 796/797.

| Mínimo | Método | Cortes con ventana recortada | MAE del caso |
| --- | --- | --- | --- |
| 2 | Derivadas-K provisional | 2017, 2022 | 5,0 |
| 2 | Regresión-K | 2016, 2018 | 2,5 |
| 2 | Dynp L2-K | 2016, 2020 | 3,5 |
| 3 | Derivadas-K provisional | Inviable | No calculado |
| 3 | Regresión-K | 2018, 2021 | 5,0 |
| 3 | Dynp L2-K | 2016, 2020 | 3,5 |

Los valores anteriores pertenecen exclusivamente al escenario de recorte,
no se suman a los siete casos de ventana completa. El filtro se recalcula
sobre el recorte; no se reutilizan derivadas de una ventana diferente.

## 7. Pruebas y reproducibilidad

Se conservaron y aprobaron las **11 pruebas iniciales**. Se añadieron y
aprobaron **12 pruebas nuevas**: K y convención, referencia corta frente
a viabilidad algorítmica, exclusión de 7/10, cobertura del 6 y recorte,
longitudes/cobertura para todos los casos admisibles, equivalencia con v1,
subconjuntos y objetivo de derivadas, óptimos SSE con mínimo 2, emparejamiento
cronológico, denominadores comunes, conjunto fijo entre mínimos y parámetros
inválidos. El registro completo está en `results/verification.txt`.

La verificación compara los 35 miembros de la entrega inicial con el ZIP
original antes y después de ejecutar pruebas y el runner nuevo. Comprueba
además igualdad SHA256 de JSON/CSV/SVG en dos ejecuciones de v2. Se revisaron
visualmente los dos paneles. La actualización no necesita instalar paquetes
adicionales y no toca el código ni las salidas anteriores.

## 8. Límites, decisiones y siguiente paso

Los nuevos resultados muestran cercanía a fronteras publicadas, no exactitud
histórica. Persisten discrepancias de totales y subtotales en la matriz, la
procedencia de los ceros y el cotejo anual. No se calcula «consistencia
estructural»: K coincide por diseño y la naturaleza temática de fases exige
otra evidencia y otra rúbrica. No se confirma la Tabla 2 ni se declara ganador.

Dirección debe cerrar: mínimo principal/sensibilidad; aceptación o revisión
de la adaptación Derivadas-K; elegibilidad definitiva de las series; 2024
del caso 6; identidad/versión de 7/10; agregado principal y eventual evaluación
independiente del número de fases. Véase el protocolo con criterios explícitos.

La tarea inmediata del chat 02 de cotejar el caso 5 y las series con fuentes
completas es complementaria: la comparación actual usa su evidencia v0.1
y debe actualizarse cuando llegue nueva evidencia, sin sobrescribir versiones.
La revisión del paquete inicial por Dirección permanece independiente.

## 9. Archivos y aplicación

- [Protocolo propuesto](PROTOCOLO_PROPUESTO_v0.2.md), [instrucciones](README.md).
- [Código condicionado](conditioned.py), [normalización](references.py),
  [ejecución](run_conditioned.py), [pruebas](test_conditioned.py).
- [Resultados](results/conditioned_results.json), [tabla CSV](results/conditioned_cuts.csv),
  [parejas de fronteras](results/paired_boundaries.csv), [agregados](results/summary.csv).
- [Referencias normalizadas](results/references_normalized.json),
  [procedencia](results/provenance.json), [verificación](results/verification.txt).
- [Panel mínimo 2](results/figures/conditioned_min2.svg),
  [panel mínimo 3](results/figures/conditioned_min3.svg).

El segundo paquete contiene un parche incremental aplicable después del
inicial y un parche acumulado aplicable sobre el commit de partida
`81da0fb072ed46ce0d64b6bea1eb55edc186873c`, sujeto a `git apply --check`
y revisión de colisiones por Dirección. El ZIP y parche iniciales permanecen
sin cambios. **No hay commit final ni intento de publicación de la entrega 02**;
la incorporación en `revision/istl` corresponde a la coordinación acordada.
