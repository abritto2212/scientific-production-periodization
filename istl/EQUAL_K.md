# Equal-K

`equal_k` recibe años consecutivos, un número entero de períodos `K ≥ 1` y una
duración mínima entera de al menos dos años. Para `N` años, reparte `q, r = divmod(N, K)`
asignando `q + 1` años a los primeros `r` períodos y `q` al resto. Cada frontera
es el primer año del período siguiente y los extremos de cada intervalo son inclusivos.

```python
from istl.equal_k import equal_k

result = equal_k(range(2000, 2023), n_periods=3, min_period_length=2)
print(result["cut_years"])  # [2008, 2016]
```

La función devuelve parámetros efectivos (`N`, `K`, mínimo, `q` y `r`),
viabilidad, índices, cortes e intervalos. Una entrada inválida genera una excepción
de validación. Si faltan años para cumplir simultáneamente `K` y la duración
mínima, el resultado conserva los parámetros y el motivo, con cortes e
intervalos nulos. La función pública `compare_periodizations` sigue devolviendo
sus tres métodos.

## Reproducción

Desde la raíz del repositorio y con las dependencias existentes de
`istl/requirements.txt`:

```sh
python -m istl.run_equal_k
python -m istl.examples.compare_with_equal_k
python -m unittest istl.tests.test_equal_k istl.tests.test_public_wrapper
```

Las salidas están en `istl/equal_k_results/v1/`. Usa `--output-dir` para reproducirlas
en otra carpeta. La base es el commit `b8bdb75f85a1155c2aedfa9788ea71ab831904d0`
de `revision/istl`. El cálculo usa los años de `istl/v3/data/analysis_series.csv` y
el `K` de `istl/v3/results/references_and_evidence.json`, vinculados por `case`.
Los cortes publicados se consultan para medir concordancia después de obtener la
partición. Las salidas históricas de la entrega 03 conservan su ubicación.

- `case_results.json` contiene las ventanas, parámetros, intervalos, cortes,
  viabilidad y concordancia por caso.
- `table_d1.csv` reproduce los nueve casos de la Tabla D1. El caso 1 figura como
  descriptivo por la inviabilidad del método de derivadas en la comparación principal.
- `table_d2_equal_k.csv` reproduce la columna Equal-K de la Tabla D2 para los
  casos 2–9.
- `aggregates.json` registra las tres comparaciones con un mínimo de dos años.
  El caso 10 carece de un `K` publicado para una partición completa y queda fuera
  de la concordancia.

## Contraste con el manuscrito

| Casos | N de casos | N de fronteras | MAE macro (años) | Coincidencias exactas |
| --- | ---: | ---: | ---: | ---: |
| 2–9 | 8 | 15 | 1,75 | 2/15 |
| 4, 7, 8, 9 | 4 | 7 | 1,875 (1,88 redondeado) | 1/7 |
| 4, 6, 7, 8, 9 | 5 | 9 | 1,70 | 1/9 |

El MAE macro es la media de los MAE por caso. Las fronteras se emparejan en orden
cronológico. Las coincidencias exactas del conjunto principal son 2018 en el
caso 5 y 2012 en el caso 9. Los cortes, errores por caso y agregados coinciden
con las secciones 3.4, 4.5, 4.6 y el Apéndice D. El subconjunto de cuatro casos
usa un mínimo de dos años, como indica la sección 4.5. Las cifras cuantifican
concordancia con las particiones publicadas.

[Manuscrito de referencia](https://docs.google.com/document/d/1rWaSltogAWgBzyF_G0ezuvH1gsx_1Xhl/edit)
