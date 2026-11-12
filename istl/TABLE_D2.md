# R17: reproducción completa de D2

Base: `f6035039618b6eec500a99bde633aedc1676053d` (`revision/istl`).
Se regeneran las 32 celdas (casos 2–9, cuatro métodos, mínimo dos años).
Los tres algoritmos originales no se ejecutan de nuevo: se recalculan sus
métricas desde las fronteras archivadas. Equal-K se calcula con la función publicada.
El módulo nuevo conserva las validaciones de R12, con ocho casos y quince
fronteras, sin modificar los módulos ni resultados históricos.

## Comandos desde la raíz

```sh
python -m istl.check_table_d2
python -m unittest istl.tests.test_table_d2 istl.tests.test_table_6 istl.tests.test_equal_k -v
```

Dependencias: las existentes en `istl/requirements.txt`.
`python -m istl.run_table_d2 --output-dir ruta` permite otra carpeta de salida.
`check_table_d2` compara automáticamente con las tablas nativas recuperadas el
12 de noviembre de 2026, cuya revisión queda registrada en
`istl/r17_manuscript_tables.json`. La comparación es con esa instantánea,
no con futuras versiones del documento.

## Resultados

| Método | MAE macro exacto | Coincidencias |
| --- | ---: | ---: |
| Derivative-K | 3.6875 | 3/15 |
| Linear-K | 3.1875 | 3/15 |
| Dynp L2-K | 4.3125 | 1/15 |
| Equal-K | 1.75 | 2/15 |

No se encontraron discrepancias en las 32 celdas. Se cotejan además las
24 particiones originales de Tabla 3 y los ocho resultados Equal-K de D1
que corresponden a D2. El caso 1 de D1 conserva la verificación previa de Equal-K.
Las pruebas comprueban cálculo independiente de errores, denominadores,
reordenamiento, rechazo de faltantes/duplicados y reproducción byte por byte.

`istl/table_d2_results/v1/` contiene la tabla D2 en CSV, detalles y agregados
en CSV/JSON, hashes de insumos/código/salidas y el cotejo con el manuscrito.
Son siete archivos reproducibles. El cotejo adicional no sustituye auditorías
de los datos bibliográficos originales ni una nueva ejecución de segmentación.
No se modificó el manuscrito ni se publicó este parche.
