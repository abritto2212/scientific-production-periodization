# R12 · Reproducción de la Tabla 6

Base de `revision/istl` en el momento de la revisión
`0e789993bd2d40547b7492c8f7ef4daed1071f38`.

Para Derivative-K, Linear-K y Dynp L2-K, el script regenera los indicadores
desde las fronteras archivadas de la entrega 03. Equal-K se calcula con
`istl.equal_k.equal_k` del commit base. Los tres algoritmos de segmentación
se conservan y sus ejecuciones archivadas son el insumo de esta reproducción.

| Insumo versionado | Uso |
| --- | --- |
| `istl/v3/data/analysis_series.csv` | Años de la ventana analítica, agrupados por identificador de caso |
| `istl/v3/results/references_and_evidence.json` | Ventanas, K, intervalos y fronteras publicadas |
| `istl/v3/results/results.json` | Fronteras, intervalos y factibilidad archivados, por caso, método y duración mínima |

El script exige los casos 4, 6, 7, 8 y 9 con un mínimo de dos años. Verifica
que la ventana y K coincidan entre insumos, que cada partición sea factible
y que los intervalos publicados cumplan el mínimo. Las fronteras representan
el primer año del período siguiente y se emparejan cronológicamente.
Se calcula el MAE de cada caso a partir de las diferencias absolutas. El
MAE macro es el promedio no ponderado de los cinco MAE. El denominador de
coincidencias exactas es la suma de las fronteras de los cinco casos
(`2 + 2 + 2 + 2 + 1 = 9`), por método.

| Método | MAE macro (años) | Coincidencias exactas | Casos |
| --- | ---: | ---: | ---: |
| Derivative-K | 3,60 | 2/9 | 5 |
| Linear-K | 3,70 | 2/9 | 5 |
| Dynp L2-K | 4,40 | 0/9 | 5 |
| Equal-K | 1,70 | 1/9 | 5 |

Los cuatro valores de MAE, los cuatro numeradores y sus denominadores coinciden
con la Tabla 6. Las cifras de la tabla se usan como contraste en las pruebas.
[Manuscrito de referencia](https://docs.google.com/document/d/1_nLm1OJWoDa7ZdUyaapyqc8u1h8QA3gIYhCWivcoy04/edit)

## Reproducción

Desde la raíz del repositorio, con las dependencias existentes de
`istl/requirements.txt`, ejecuta:

```sh
python -m istl.run_table_6
python -m unittest istl.tests.test_table_6 istl.tests.test_equal_k -v
```

El comando escribe en `istl/table_6_results/v1/`. Para reproducir los archivos
en otro lugar, usa `python -m istl.run_table_6 --output-dir ruta/de/salida`.

- `case_results.csv` y `case_results.json` registran los 20 pares caso-método,
  sus fronteras, errores por frontera, MAE y coincidencias.
- `aggregates.csv` y `aggregates.json` registran el MAE macro y los
  denominadores de los cuatro métodos.
- `provenance.json` registra el commit base, el comando y los SHA-256 de los
  insumos, el código de cálculo y las cuatro salidas de resultados.

Los SHA-256 se calculan sobre los bytes de cada archivo. Para cotejarlos, usa
una copia de trabajo que preserve los finales de línea de Git
(`core.autocrlf=false`). Las pruebas reordenan los tres insumos, verifican que
las métricas archivadas no intervienen en el recálculo, contrastan los cortes
de Equal-K con su salida versionada y comprueban la reproducción byte a byte.
