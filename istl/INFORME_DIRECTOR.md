# Entrega 01 · Datos, código y resultados

Fecha: 5 de noviembre de 2026. Rama exclusiva: `revision/istl`.
Commit de partida: `81da0fb072ed46ce0d64b6bea1eb55edc186873c`.
**Publicación bloqueada: no se creó commit final remoto.** Los intentos de
escritura mediante GitHub (git trees y contents) devolvieron 403:
`Resource not accessible by integration`. La carga de archivos por navegador
también quedó bloqueada por falta del permiso de acceso de la extensión a
archivos locales. No se cambió ese permiso. La entrega queda disponible en
un paquete ejecutable y un parche de adiciones para aplicar sobre la rama
de partida. Mensaje de commit propuesto:
`Validate common ten-case ISTL periodization pipeline`.

## Alcance y fuentes revisadas

Se leyó el manuscrito de Google Docs y se inspeccionaron todos los archivos de
código, cuaderno, CSV descriptivo y árbol de la rama antes de corregir las
implementaciones. Se leyeron las diez hojas del libro del repositorio y se
contrastaron sus 226 pares año/conteo con la lectura del libro homónimo de
Drive. El libro original no se modifica; su SHA256 está en provenance.json.

- Manuscrito: https://docs.google.com/document/d/15SW12tkCBToWAGib6KxzfrgbhoMoMrCXfPLuKnVsWqw/edit
- Carpeta: https://drive.google.com/drive/folders/1jRIitUaKsGW4FasvW8B2nBF4WmRa36CP
- Datos Drive: https://drive.google.com/file/d/1kANrRgQK-WNShF15JfChMDODrz1ymATv/view
- Rama: https://github.com/abritto2212/scientific-production-periodization/tree/revision/istl

Ninguna de esas fuentes quedó inaccesible. La clonación y pip fallaron por DNS
del entorno. Se accedió al repositorio con el conector GitHub; se incluyó un
subconjunto de fuentes oficiales de ruptures v1.1.10, con licencia, atribución
y huellas Git, para ejecutar Dynp/CostL2 sin alterar sus algoritmos. La suite
no valida el resto de ruptures. NumPy, SciPy y Matplotlib ya estaban disponibles.

El archivo auxiliar `data time series.xlsx` de Drive se leyó: presenta una
serie en orden descendente, con años omitidos, cuyos valores observados
coinciden con el caso 5. No se usa como entrada ni se convierten sus omisiones
en ceros. Los ceros explícitos del libro de diez casos se conservan, pero su
procedencia documental sigue pendiente. El archivo bibliográfico grande
`all_data_ai_data_engineering_1.xlsx` no se procesó: no forma parte de la
entrada anual común de esta entrega y no sustituye las referencias verificadas.

## Hallazgos y correcciones

| Hallazgo previo | Comprobación y resultado |
| --- | --- |
| PELT anunciado, K-means ejecutado | Confirmado en ArticuloEDO.ipynb. Se conserva como histórico, identificado en README. La implementación canónica del método 3 es Dynp L2. |
| Regresión con dos cortes y tramo interior sin mínimo | Confirmado. La función ya recibía n_breaks, aunque la ejecución lo fijaba en 2. Se filtran todas las particiones con algún tramo menor que min_len. |
| Gaussian recibe enteros | Confirmado. Se usa float64 antes del filtro; sigma=2 y criterio de picos se conservan. |
| Convenciones distintas | Confirmado: regresión years[i-1], Dynp years[i]. Salida común: primer año del período nuevo; intervalos inclusivos sin solapamiento. |
| Ejemplos activos diferentes | Confirmado: regresión usa el caso 5; derivadas/Dynp/cuaderno usan una serie personal distinta. La nueva ejecución usa las mismas diez hojas para los tres métodos. |
| Tabla 2 y cortes originales no trazables | No se encontraron procedimiento, límites originales ni correspondencia bibliográfica completa en los archivos revisados. No se recalculan esas métricas. |
| Separación de candidatos Dynp | El constructor de v1.1.10 usa jump=5 por defecto. Antes no se especificaba. Ahora jump=1 permite evaluar cada año admisible con mínimo 3. |

El código canónico se añadió en `istl/`; no se sobrescriben los scripts,
cuaderno, figuras ni datos históricos. La regresión usa mínimos cuadrados con
intercepto y pendiente independientes por tramo; no impone continuidad.
Dynp minimiza la SSE respecto a medias por bloque, sin suavizado previo.
Las diferencias entre estos objetivos son parte del diseño, no errores.

## Resultados ya verificables

La entrada contiene diez series consecutivas, 226 observaciones, duración
media 22,6 años y 9.591 publicaciones. Esos totales coinciden con la Tabla 1.
No se detectaron duplicados, desorden, años interiores ausentes ni conteos
faltantes, negativos o fraccionarios. La hoja 2 tiene seis filas finales
vacías (20–25), excluidas como formato sobrante y registradas en data_audit.json.
Esto valida la estructura del libro, no su exactitud frente a los artículos.

**Diagnóstico con dos cortes para regresión y Dynp; el método de derivadas
estima su número de cortes.** Años que inician un período nuevo:

| Caso | Derivadas con mínimo 3 | Regresión, 2 cortes | Dynp L2, 2 cortes |
| --- | --- | --- | --- |
| 1 | 2015, 2020 | 2017, 2021 | 2009, 2017 |
| 2 | 2014, 2019 | 2014, 2019 | 2015, 2018 |
| 3 | 2017 | 2012, 2018 | 2010, 2020 |
| 4 | 2009, 2017, 2021 | 2012, 2015 | 2007, 2019 |
| 5 | 2017 | 2017, 2022 | 2018, 2022 |
| 6 | 2017, 2022 | 2017, 2022 | 2016, 2020 |
| 7 | 2015, 2020 | 2013, 2019 | 2009, 2019 |
| 8 | 2016, 2020 | 2016, 2019 | 2015, 2019 |
| 9 | 2018 | 2015, 2020 | 2012, 2019 |
| 10 | 2018 | 2015, 2020 | 2018, 2021 |

Los 30 registros incluyen parámetros, índices, años, intervalos y longitudes.
Todos los segmentos corregidos tienen al menos tres observaciones y cubren
la serie completa una sola vez. No se interpreta esta tabla como precisión.

## Antes y después

- Solo convertir a float cambia los candidatos de derivadas en los casos
  **3, 4, 7 y 9**, conservando filtro, derivadas y umbral.
- En el caso 9, candidatos enteros: 2017; candidatos float: 2018 y 2021.
  El candidato 2021 deja solo dos años al final y se descarta bajo el mínimo
  común, quedando 2018. before_after.json separa ambos cambios.
- La regresión histórica del caso 9 permite índices 18 y 20: longitudes
  **18, 2, 3** y etiquetas antiguas 2017/2019. En convención común esos mismos
  cortes serían 2018/2020. La solución corregida es 2015/2020, longitudes
  **15, 5, 3**. La SSE aumenta de 184,238 a 275,525 porque se elimina una
  solución inadmisible; ese aumento no constituye peor concordancia.
- El mínimo interior cambia la partición de regresión solo en el caso 9;
  la corrección de etiquetas afecta también los restantes casos.
- Cambiar jump=5 a jump=1 modifica Dynp en **nueve casos**, todos salvo el 3.
  En el caso 9 pasa de 2010/2020 a 2012/2019, con SSE 2537,567 y 2281,274,
  respectivamente. Esa reducción corresponde a ampliar los candidatos,
  no a una mejora probada respecto de expertos.
- La reconstrucción histórica de regresión usa el mismo espacio de búsqueda
  y objetivo con np.linalg.lstsq, no el script completo de sklearn, paquete
  ausente en el entorno. Las pruebas independientes usan np.polyfit.

## Comprobaciones

Se ejecutó `python -m unittest discover -s istl -p test_periodization.py -v`:
**11 pruebas aprobadas**. Incluyen mínimo en todos los tramos, reproducción
del defecto del caso 9, cobertura/índices/años, decimales del suavizado,
optimización de Dynp frente a enumeración, regresión frente a np.polyfit,
datos inválidos en arrays y copias XLSX en memoria, serie constante, cero
cortes y solicitud imposible. Se ejecutó el runner común y se revisó
visualmente el panel diagnóstico. Dependencias exactas y huella de entrada
están registradas; los originales permanecen intactos. Una segunda ejecución
produjo JSON, CSV y SVG con SHA256 idénticos. Se revisaron ambos paneles.

## Información faltante para reconstruir la Tabla 2

1. Identidad bibliográfica completa (DOI/título) de cada uno de los diez casos.
2. PDF/página/figura y cita verificable de cada periodización publicada;
   límites originales, número de períodos, convención de frontera y cualquier
   ambigüedad o hueco. La referencia publicada no debe asumirse verdad absoluta.
3. Procedimiento de reconstrucción de los conteos, ceros, ventanas y años
   potencialmente incompletos; contraste del libro con las fuentes.
4. Regla de emparejamiento de cortes, manejo de número desigual y límites
   ambiguos, denominadores y agregación por caso o por corte para MAE y
   coincidencia exacta. La Tabla 2 actual no aporta esa trazabilidad.
5. Rúbrica de consistencia estructural, quién la aplica y evidencia por caso.
   El número de períodos no verifica por sí solo la naturaleza temática de
   las fases. No puede derivarse esa naturaleza de la serie de conteos sola.
6. Código, versiones y parámetros de la ejecución que produjo la Tabla 2,
   si existe. Sus valores no se usan como objetivos ni se certifican aquí.

## Decisiones metodológicas pendientes

Para la comparación principal prevista, una vez verificados K períodos por
caso, regresión y Dynp recibirían **K-1 cortes**. El diagnóstico actual de dos
cortes no usa información de los expertos ni resuelve esa decisión.

**Propuesta para discutir, no implementada:** conservar sigma y el umbral
original; enumerar subconjuntos de K-1 picos candidatos que cumplan el mínimo
común y seleccionar el que maximice la suma de |d2|, con desempate temporal
predefinido. Si no existen suficientes picos admisibles, declarar el caso
inviable para esa variante. El caso 4 también muestra por qué debe definirse
una selección cuando sobran candidatos. Esta variante condicionada a K es
distinta del método automático actual y debe nombrarse y justificarse antes
de usarla. Quitar/reducir el umbral o agregar cortes fuera de picos para
forzar K requeriría otra adaptación explícita, no un ajuste silencioso.

También deben acordarse el tratamiento de inviabilidad (sin ocultar casos),
la sensibilidad a sigma/mínimo y una estrategia independiente para evaluar
el número de períodos si se desea estudiarlo. El filtro de longitud aplicado
a derivadas en esta entrega conserva y expone los picos originales, pero
es una regla adicional de selección que debe describirse en el manuscrito.

No se declara ganador. No se calcula concordancia con expertos. No se
modifica el manuscrito. Sus afirmaciones de superioridad, sobresegmentación
y desplazamiento inherente del filtro gaussiano quedan sin respaldo en esta
entrega; un filtro simétrico no demuestra por sí solo un rezago temporal fijo.

## Entregables

- [Instrucciones y parámetros](README.md)
- [Implementaciones](periodization.py), [lector](read_data.py), [ejecución](run.py)
- [Pruebas](test_periodization.py), [dependencias](requirements.txt)
- [Resultados completos](results/results.json), [tabla CSV](results/cuts.csv)
- [Antes/después](results/before_after.json)
- [Auditoría de datos](results/data_audit.json), [procedencia](results/provenance.json)
- [Diez series extraídas](results/series.csv)
- [Panel diagnóstico](results/figures/diagnostic.svg)
- [Candidatos de derivadas](results/figures/derivative_candidates.svg)
