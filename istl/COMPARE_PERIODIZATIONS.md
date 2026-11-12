# Función pública para comparar periodizaciones

Base revisada: `12cf8cb213ec256bb202d35891b03b431d49f9c4`, rama
`revision/istl`. Incluye el cotejo completo del caso 3. Cambio propuesto
para revisión de Dirección; no publicado.

Desde la raíz del repositorio:

```python
from istl.compare_periodizations import compare_periodizations

results = compare_periodizations(
    years, counts, n_periods=3, min_period_length=2
)
for method, result in results.items():
    print(method, result['algorithm_feasible'], result['cut_years'])
```

Entradas: secuencias unidimensionales de años y conteos, número entero de
períodos >=1 y duración mínima entera >=2. Se reutilizan `validate_series`
y `validate_condition`: como en el código existente, se requieren al menos
tres observaciones en la serie, años consecutivos, ordenados y únicos,
conteos enteros no negativos y valores finitos. No se imputan ni ordenan datos.
Entradas inválidas generan el error de validación existente; no se presentan
como una inviabilidad del algoritmo ni se corrigen silenciosamente.

Cada clave de `results` identifica uno de los tres métodos existentes:
`derivative_k_provisional`, `piecewise_linear_k` o `dynamic_l2_k`.
Todos tienen los mismos campos externos:

| Campo | Contenido |
| --- | --- |
| `method` | Identificador del método |
| `n_periods`, `min_period_length` | Solicitud del usuario |
| `executed` | Si se llamó al método; False por longitud global insuficiente |
| `algorithm_feasible` | Si se obtuvo una solución admisible |
| `reason` | Motivo de inviabilidad; None si existe solución |
| `parameters` | Parámetros y diagnósticos devueltos por la implementación |
| `cut_indices`, `cut_years` | Índices de separación y primer año del período siguiente |
| `intervals` | Intervalos inclusivos sin solapamientos, con start/end/length |

Cuando faltan observaciones para K períodos, se devuelven tres registros
inviables, sin ejecutar algoritmos, con los parámetros solicitados. Cuando
derivadas no tiene un subconjunto factible de K−1 picos, se conservan sus
parámetros y motivo originales. En ambos casos cortes e intervalos son None.
No se ocultan errores inesperados de implementación mediante un catch general.

La función llama a `segment` de `istl/v2/conditioned.py`; no copia sus algoritmos.
Mantiene sigma=2, modo reflect, truncate=4, gradientes y umbral std(d2), selección
condicionada de picos, rectas independientes y Dynp L2 con jump=1. K lo proporciona
el usuario; no hay calibración, ranking, selección automática, exportación ni
escritura de archivos. Las SSE son de objetivos distintos y no seleccionan ganador.
La función desconoce referencias publicadas: viabilidad algorítmica no equivale
a elegibilidad para puntuar concordancia. Por ejemplo, caso 2 con mínimo 3 tiene
soluciones algorítmicas aunque su fase publicada de dos años sea incompatible.

Ejemplo sobre el caso 5, con el lector de datos que ya existe:

```sh
python -m istl.examples.compare_series
```

El ejemplo solo carga la serie existente y muestra la estructura con pprint.
No añade formatos de entrada ni sistema de informes.

Comprobación de equivalencia:

```sh
python -m unittest discover -s istl/tests -p test_public_wrapper.py -v
```

Se comparan las 54 combinaciones ya guardadas de casos 1–9, tres métodos y
mínimos 2/3 con `istl/v3/results/results.json`, utilizando las series analíticas
existentes. Se exigen idénticos cortes, intervalos, viabilidad y motivos;
parámetros numéricos con tolerancias de Dirección (rtol=1e-12, atol=1e-10).
El caso 6 usa la ventana analítica almacenada 2003–2023; el caso 10 no tiene K
publicado y no se le inventa uno. Se comprueba también la corrección integrada
de evidencia del caso 3, validación, longitud insuficiente y no mutación de arrays.
No se generan nuevos experimentos ni se reescriben resultados históricos.

Alcance de la revisión: cuatro archivos añadidos (función, ejemplo, documentación
y prueba). Sin cambios de datos, código algorítmico, dependencias, resultados o
manuscrito. El parche incluido es de adiciones y debe revisarse contra el commit
base antes de incorporarlo a `revision/istl`; no se realizó commit, push ni merge.
