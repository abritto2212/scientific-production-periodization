> Adenda de Dirección, 7 de noviembre de 2026: el caso 3 tiene cotejo completo de sus 23 etiquetas (368 publicaciones). Las menciones de pendiente en el informe original quedan sustituidas por esta verificación. Véase `../../integration/REVIEW_ENTREGA03.md`.

# Ejecución de entrega 03

Desde la raíz del paquete o repositorio, con Python 3.13 y las dependencias
ya fijadas en `istl/requirements.txt`:

```sh
python -m unittest discover -s istl/v3 -p test_v3.py -v
python istl/v3/run.py
```

El Excel actualizado ya está incluido. Para reproducir exclusivamente la
corrección del libro desde su copia congelada: `python istl/v3/prepare_data.py`.
La preparación comprueba primero que no existan otros cambios de datos y se
niega a sobrescribirlos. Única celda modificada: hoja 2, B 2 (2004), de 2 a 1.
La comparación de las 226 observaciones con la copia de Drive coincide después
de esa corrección. Ningún archivo remoto se edita.

`run.py` reutiliza **sin cambios** `istl/v2/conditioned.py`, sus parámetros,
la implementación de derivadas de v 1 y las fuentes congeladas de Dynp/CostL 2.
No se añaden dependencias. El número de fases y ventanas procede de las
decisiones documentadas en `sources/approved_decisions.md`.

- Fuente: diez hojas completas; 226 valores, 9.590 publicaciones.
- Comparación: caso 6 se limita explícitamente a 2003–2023, con 712; fuente
  mantiene 2024=84 y total 796. Los otros casos conservan sus ventanas.
- Caso 7: fases textuales 2000–2012/2013–2019/2020–2022, cortes 2013/2020.
- Caso 10: K desconocido; no se ejecuta comparación condicionada ni se puntúa.
  `case10_separate_diagnostic.json` conserva derivadas automáticas y un
  diagnóstico de dos cortes para regresión y Dynp, sin referencia inventada.
- Mínimo principal 2 y sensibilidad 3. `reference_satisfies_minimum`,
  `algorithm_feasible` y `eligible` son campos independientes.
- Derivadas-K: sigma 2, reflect, truncate 4, gradiente anual dos veces,
  umbral std(d 2), candidatos originales; maximiza suma |d 2| sobre subconjuntos
  factibles de K−1 picos. No reduce umbral ni fuerza cortes si faltan picos.
- Regresión: rectas independientes, sin continuidad, mínimo en todos los
  tramos, mínimo global de SSE. Con dos observaciones la recta puede interpolar.
- Dynp L 2: medias por bloque, min_size=2/3, jump=1, K−1 cortes dados.

Salidas nuevas en `results/` (o `--output otra_carpeta`):

- `results.json`/`.csv`:60 registros caso×método×mínimo, incluidos estados
  no ejecutados del caso 10, con parámetros, cortes, intervalos, longitudes,
  elegibilidad y métricas por caso. Frontera=primer año del nuevo período.
- `common_set_summaries.json`/`.csv`: solo agregados sobre conjuntos comunes;
  intersección de tres métodos por mínimo, intersección entre ambos mínimos,
  subconjunto con figuras cotejadas y comparación común regresión/Dynp.
  No hay promedios sobre muestras distintas por método en un mismo conjunto.
- `paired_boundaries.csv`: emparejamiento cronológico uno a uno, error firmado
  y absoluto. Se conserva MAE macro por caso y agrupado por frontera con nombres
  distintos; coincidencias exactas tienen numerador y denominador explícitos.
- `references_and_evidence.json`: estado actualizado, fuente de la verificación,
  intervalos textuales, discrepancias de totales y alcance documental.
- `delta_vs_entrega02.json`: cambios de datos, ventanas, K, cortes y elegibilidad
  frente a la instantánea histórica. No combina versiones en una métrica.
- `case10_separate_diagnostic.json`, `figures/`: diagnóstico y tres paneles SVG
  reproducibles; se generan además PNG de lectura.
- `provenance.json`, `verification.txt`, `reproducibility_hashes.json`: versiones,
  huellas del código/datos, pruebas y repetición determinista de JSON/CSV/SVG.

En `data/` quedan la serie completa corregida, la serie analítica y auditoría.
En `sources/`: Excel de base, lectura textual de Drive, manifiesto del commit
base y decisiones de Dirección. Los encabezados gráficos discrepantes de 7/8/9
se registran como conflicto comunicado; no se inventan transcripciones literales
que no se entregaron. Esas transcripciones no son necesarias para ejecutar las
fronteras textuales aprobadas.

Verificación integral:

```sh
python istl/v3/verify.py
```

Usa `previous/ISTL_validacion_entrega02.zip` incluido en el paquete para ejecutar
las 23 pruebas antiguas con los datos originales en una carpeta temporal aislada.
En un clon del repositorio se puede proporcionar `--previous-package RUTA`.
Ejecutar las pruebas v 2 directamente sobre el Excel v 3 mezclaría una matriz
histórica de 1694 con el dato corregido 1693; no es una regresión del algoritmo.
Los archivos históricos y paquetes originales permanecen sin cambios.

Alcance: concordancia temporal con referencias publicadas. Los conteos cotejados
reproducen figuras; no auditan los registros bibliográficos originales.
Caso 3 conserva cotejo anual pendiente, y hay un agregado común que lo excluye.
No se validan interpretaciones históricas, superioridad ni la antigua Tabla 2.
