# Protocolo propuesto para la comparación aplicada

Estado: **provisional, pendiente de cierre por Dirección**. La ejecución
incluida permite examinar sus consecuencias; no convierte la propuesta en
una validación definitiva. Fecha: 5 de noviembre de 2026.

## 1. Pregunta y unidad de comparación

¿Dónde sitúa cada método las fronteras cuando se le informa el número de
fases publicado para una misma serie anual? Se compara la ubicación temporal
condicionada a K, no la capacidad de descubrir automáticamente K ni la
veracidad histórica de las fases. Producción, citas y contenido temático
pueden haber intervenido en la periodización de los autores originales.

Se conservan diez casos. Cada registro identifica caso, hoja, fuente exacta,
ventana anual, versión de datos y versión del algoritmo. Los resultados de
la entrega 01 continúan identificados como diagnóstico con dos cortes para
regresión y Dynp. No se mezclan con las puntuaciones nuevas.

## 2. Congelación y validación de insumos

1. Conservar el libro original y su SHA256. Años ordenados, únicos,
   consecutivos, sin conteos ausentes/no finitos, negativos o fraccionarios.
   No imputar años omitidos como ceros. Conservar los ceros explícitos,
   marcando pendiente su procedencia cuando no se haya verificado.
2. Conservar el CSV de fronteras, la matriz y el informe del chat 02 como
   instantáneas con enlaces y huellas. No sobrescribirlos al llegar evidencia
   nueva: usar otra versión y registrar cambios de límites, cobertura o K.
3. Exigir para elegibilidad definitiva una identidad documental confirmada,
   cobertura completa y cotejo de la serie anual, distinguiendo datos/tablas
   originales de digitalización aproximada. Una coincidencia de total o
   subtotales no acredita cada año. No ajustar conteos a los cortes.
4. Resolver fuentes con ventanas diferentes o discrepancias antes de afirmar
   validación final. Las clases A/B/C indican fuerza del vínculo documental,
   no calidad científica del artículo ni exactitud numérica de la serie.

## 3. Referencias y casos no resueltos

La frontera es siempre el primer año del nuevo período. Un cierre 2011 y
apertura 2012 representan una sola frontera, 2012. Los intervalos son
inclusivos y no se solapan. Se conserva la formulación publicada y su página
o sección; no se desplaza un año para favorecer coincidencias.

| Situación | Tratamiento provisional |
| --- | --- |
| Casos 1–5, 8 y 9 | Puntuar provisionalmente donde la referencia cumple las restricciones; marcar cotejo anual pendiente y discrepancias en matriz. |
| Caso 6, ventana 2003–2024 | K=3 y fronteras conocidas; ejecutar algoritmos y retener resultados, sin puntuación principal porque 2024 no está asignado. |
| Caso 6, recorte 2003–2023 | Sensibilidad separada explícita: se omiten 2024 y sus 84 publicaciones; recalcular los tres métodos, incluido el filtro. No reparar la fuente ni mezclar con ventana completa. |
| Casos 7 y 10 | Conservar datos y diagnóstico inicial; no asignar K, no ejecutar comparación condicionada ni puntuar. «Alrededor de 2013» no se convierte en frontera exacta. |
| Referencia incompatible con mínimo | Mostrar conflicto como limitación de representación, separada de viabilidad del algoritmo. No cambiar los intervalos publicados. |

## 4. Restricciones comunes y escenarios

Evaluar **mínimo 2 años** como escenario provisional común y **mínimo 3 años**
como sensibilidad. Se ejecutan ambos de forma predefinida; no se elige el que
produzca una puntuación más favorable. K proviene exclusivamente de la
referencia: cuatro fases para el caso 1, dos para el 9, tres para 2–6/8.

El mínimo 2 permite representar la última fase publicada del caso 2; no
demuestra que esa restricción sea científicamente preferible. En regresión,
una recta con intercepto y pendiente puede interpolar exactamente dos
observaciones, reduciendo artificialmente la contribución residual de ese
segmento y aumentando flexibilidad. Esta es una razón para mostrar también
el escenario de 3 años, no para ocultar sus incompatibilidades.

El filtro conserva sigma=2 años, reflect y truncate=4; deriva dos veces con
np.gradient, paso anual 1 y edge_order=1; selecciona find_peaks(|d2|) con altura
std(d2), ddof=0. El tamaño de la ventana y su extremo influyen en el resultado;
no se interpreta el suavizado simétrico como un retardo causal fijo.

## 5. Métodos condicionados a K

**Regresión lineal por tramos:** enumerar combinaciones de K−1 índices de
frontera anuales; exigir mínimo común en todos los segmentos; ajustar rectas
independientes con intercepto y pendiente, sin continuidad; minimizar SSE
global. Desempate por primera combinación lexicográfica en igualdad numérica.

**Programación dinámica L2:** Dynp sobre conteos float64 originales,
model=l2, min_size igual al mínimo común y jump=1. Pedir exactamente K−1
fronteras; descartar el índice terminal n al convertir a años. L2 minimiza
desviaciones respecto de una media por bloque. No se comparan sus SSE con
las de regresión como si fueran la misma medida de calidad.

**Derivadas-K, adaptación provisional:** mantener los picos originales y su
umbral; enumerar subconjuntos de exactamente K−1 candidatos con todos los
segmentos admisibles. Maximizar la suma de |d2| en los picos seleccionados;
desempatar lexicográficamente. La regla no consulta distancias a la referencia.
Si no existe subconjunto, declarar inviabilidad y no devolver cortes ni
puntuación. No completar con índices que no son picos, reducir el umbral,
cambiar sigma por caso ni seleccionar la variante por concordancia.

La derivada automática de número variable sigue disponible como diagnóstico
separado. La variante condicionada necesita aprobación metodológica final;
se implementó aquí de manera explícita para explorar viabilidad, conforme
al encargo de comparación provisional. Una alternativa distinta requeriría
otra versión, justificación previa y resultados separados.

## 6. Viabilidad, puntuación y denominadores

Registrar tres decisiones independientes: viabilidad algorítmica, admisibilidad
de la referencia bajo el mínimo y elegibilidad documental de ventana. Una
partición algorítmica admisible no garantiza que la referencia lo sea. No
confundir falta de picos con identificación documental pendiente.

Solo puntuar cuando exista referencia completa en la ventana, satisfaga el
mínimo y el método devuelva K−1 fronteras. En esta entrega las puntuaciones
siguen siendo provisionales por falta de cotejo anual externo.

Ordenar las fronteras predichas y publicadas cronológicamente y emparejarlas
uno a uno. Al haber igual número, este emparejamiento minimiza la suma de
distancias absolutas en la recta temporal. No reutilizar una frontera de
referencia para varios cortes predichos ni usar vecino más próximo por separado.
Exportar error firmado, absoluto, coincidencia exacta y denominadores.

Para cada caso i con b_i=K_i−1 fronteras:

- MAE_i = suma_j |predicho_ij − referencia_ij| / b_i.
- Coincidencia exacta_i = suma_j 1(predicho_ij=referencia_ij) / b_i.
- Agregado macro: media de métricas por caso, cada caso pesa igual.
- Agregado por frontera: sumar errores/aciertos y dividir por suma_i b_i;
  el caso 1 pesa más que el 9. Identificarlo como tal, no alternar ambos.

Publicar resultados por caso y agregados con los siguientes conjuntos:

1. Disponibles por método: informa cobertura, pero los denominadores pueden
   variar; no sirve para declarar superioridad entre métodos.
2. Intersección de casos puntuables de los tres métodos dentro de cada
   escenario: comparación descriptiva sobre el mismo conjunto, acompañada
   de tasas de viabilidad. Excluir casos puede sesgar hacia series favorables
   para el método con más restricciones; mostrar cuáles quedan fuera.
3. Estratos A/B de evidencia y escenario del caso 6 separados.

Para comparar efectos del mínimo 2 frente a 3, utilizar también la misma
intersección entre escenarios; no interpretar un cambio agregado con distinta
composición de casos como efecto puro del mínimo. No introducir pesos,
tolerancias ±1 año o reglas nuevas después de mirar qué método favorecen.

## 7. Qué no mide este protocolo

K correcto por construcción no es evidencia de detección del número de
fases. Coincidencia de años no acredita correspondencia temática, emergencia,
consolidación, liderazgo, calidad o causalidad. No se calcula la «consistencia
estructural» histórica de la Tabla 2 sin una rúbrica independiente y evidencia
interpretativa por caso. Tampoco se valida automáticamente el juicio publicado.

No se elige ganador ni se reproduce la Tabla 2 como objetivo. Evitar
inferencias generales con esta pequeña colección de conveniencia, sus
discrepancias de procedencia y la cobertura desigual de algoritmos.

## 8. Decisiones que debe cerrar Dirección

- Confirmar mínimo principal 2 y sensibilidad 3, incluyendo la limitación de
  rectas de dos observaciones, antes de presentar resultados definitivos.
- Aprobar o revisar la regla de selección Derivadas-K; cualquier revisión
  debe mantener trazabilidad y no ajustarse a los años publicados por caso.
- Resolver el año 2024 del caso 6, identidades de 7/10 y cotejo numérico anual
  de todos los casos, con tratamiento explícito de digitalización aproximada.
- Confirmar agregado principal (se propone macro por caso), conjuntos comunes
  y forma de comunicar inviabilidad, sin ocultarla como dato ausente ordinario.
- Definir si se añadirá una evaluación independiente del número de fases
  y/o correspondencia temática. No están resueltas por este experimento.

Después del cierre, congelar versiones e insumos, repetir pruebas y ejecutar
la comparación sin modificar parámetros con base en los resultados obtenidos.
