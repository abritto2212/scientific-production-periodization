# Ejecución común de los diez casos

Desde la raíz del repositorio, con Python 3.13 (ejecución verificada en 3.13.2):

```sh
python -m pip install -r istl/requirements.txt
python -m unittest discover -s istl -p test_periodization.py -v
python istl/run.py
```

Se requieren NumPy, SciPy y Matplotlib. `vendor/` incluye un subconjunto
congelado y atribuido de ruptures v1.1.10: las implementaciones originales de
Dynp, CostL2 y sus clases/utilidades; no se necesita instalar ruptures aparte.
Véanse las versiones, el alcance y la licencia BSD en `vendor/README.md`.
Se incluyó porque la instalación de dependencias y la clonación directa
fallaron por DNS en este entorno; los archivos se recuperaron mediante GitHub.
La ejecución usa ese subconjunto de forma explícita, sin sustituir Dynp por
otro algoritmo. El lector XLSX usa la biblioteca estándar; no modifica Excel.

La entrada única es `data_articles/data_articles.xlsx`, preservada sin cambios.
Se exige exactamente diez hojas, cabeceras Year y Total_Publications y columnas
A/B. El lector es deliberadamente específico para este libro: rechaza fórmulas,
columnas adicionales con valores, filas interiores vacías, años ausentes,
duplicados o desordenados, conteos faltantes, negativos, fraccionarios o no
finitos. Excluye únicamente filas finales totalmente vacías de formato y lo
registra. No ordena, agrega ni imputa silenciosamente. Los ceros ya escritos
en el libro son observaciones de entrada, cuya procedencia debe verificarse
en los artículos originales.

Cada índice de corte `i` separa `values[:i]` y `values[i:]`; el corte se informa
como `years[i]`, primer año del nuevo período. Los intervalos de salida son
inclusivos: el anterior termina en `years[i-1]`. El final `n` de ruptures se
excluye de la lista de cortes. Todos los segmentos tienen al menos tres años.

| Método | Número de cortes | Parámetros y objetivo |
| --- | --- | --- |
| Derivadas | Estimado por picos y restricción de longitud | float64; Gaussian sigma=2 años, reflect, truncate=4; np.gradient dos veces, paso=1, edge_order=1; find_peaks(abs(d2), height=std(d2), ddof=0) |
| Regresión por tramos | Recibe n_breaks; diagnóstico=2 | min_len=3 en TODOS los tramos; búsqueda exhaustiva; mínimos cuadrados con intercepto y pendiente independientes por segmento, sin continuidad; minimiza SSE |
| Dynp L2 | Recibe n_bkps; diagnóstico=2 | min_size=3; jump=1; conteos originales float; minimiza desviaciones respecto de la media de cada bloque |

El criterio original de picos se conserva. **La imposición de longitud mínima
en derivadas es una restricción explícita adicional**: se consideran candidatos
en orden descendente de |d2|, con prioridad al año anterior si hay empate; solo
se acepta uno si todos los segmentos resultantes mantienen longitud >=3.
No busca exactamente dos cortes ni garantiza maximizar el número de picos.
Se registran candidatos previos y descartados, para separar esta restricción
del efecto exclusivo de convertir a float. No es una adaptación al número de
períodos de referencia.

Para una comparación futura condicionada a K períodos de referencia, véase
la propuesta pendiente del informe: no se ejecutó una variante de derivadas
con número fijo de cortes ni se modificó sigma/umbral para aproximar expertos.

Los resultados se escriben en `istl/results/` (o `--output otra_carpeta`):

- `results.json`: 30 registros caso-método con parámetros, índices, años,
  intervalos, longitudes y número de cortes; fuente principal para reutilizar.
- `cuts.csv`: vista tabular con los mismos cortes, intervalos y parámetros.
- `series.csv`, `data_audit.json`, `provenance.json`: entrada extraída,
  validación y huella SHA256 del libro original, versiones y commit de partida.
- `before_after.json`: efecto separado de float, restricción de longitud,
  convención de años y jump. La regresión histórica se reconstruye con el
  mismo objetivo y espacio de búsqueda mediante np.linalg.lstsq, en lugar
  de sklearn; no se afirma haber ejecutado el script histórico completo.
- `figures/diagnostic.svg`: comparación; `derivative_candidates.svg`: picos,
  umbral y candidatos retenidos. Se genera además diagnostic.png para lectura.

Las pruebas contrastan Dynp con enumeración independiente, la regresión con
np.polyfit, el caso 9 que exponía el error, conservación de decimales,
asignación de años, cobertura sin solapamientos, series constantes, cero
cortes, parámetros imposibles y rechazo de datos inválidos en arrays y XLSX.

No se calculan MAE, porcentaje de coincidencia ni consistencia estructural
contra expertos. Las SSE de objetivos diferentes no permiten comparar calidad
entre métodos. El resultado no justifica etiquetas como emergencia o madurez.
