# Segunda versión: ejecución y alcance

Esta carpeta añade la comparación condicionada al número de fases publicado
en las fuentes reunidas por el chat 02. No modifica ninguna implementación,
prueba o salida de la entrega 01. Python y dependencias son los mismos de
`istl/requirements.txt`; se reutiliza Dynp/CostL2 congelado y atribuido en
`istl/vendor/`, sin dependencias nuevas.

```sh
python -m unittest discover -s istl -p test_periodization.py -v
python -m unittest discover -s istl/v2 -p test_conditioned.py -v
python istl/v2/run_conditioned.py
```

El último comando no ejecuta ni sobrescribe `istl/run.py` o `istl/results/`.
Escribe en `istl/v2/results/`; admite `--output otra_carpeta`.

| Familia | Ubicación | Número de cortes | Mínimo |
| --- | --- | --- | --- |
| Entrega 01: diagnóstico original | `istl/results/` | Regresión/Dynp reciben 2; derivadas estima | 3 años |
| Entrega 02: comparación provisional | `istl/v2/results/` | K−1, con K fases publicadas | 2 años; sensibilidad 3 |
| Entrega 02: derivadas automática | `native_derivative_diagnostic.json` | Lo estima; no se puntúa como fixed-K | 2 y 3 años |
| Entrega 02: caso 6, ventana recortada | escenario `case6_truncated_2023` | K−1 | 2 y 3; separado del agregado principal |

**Derivadas-K es una adaptación provisional explícita**, distinta del método
automático. Conserva los candidatos de sigma=2 y altura std(d2), enumera los
subconjuntos de K−1 picos que cumplen el mínimo y maximiza su suma de |d2|.
No inserta picos ni cambia sigma/umbral. Si no existe subconjunto, informa
inviabilidad y deja cortes/métricas en null. El mínimo 2 se implementa en el
módulo v2; no relaja el mínimo 3 del código congelado de la primera entrega.

Los archivos `references/` son instantáneas textuales de CSV, matriz e informe
v0.1 del chat 02, consultados el 5 de noviembre de 2026. No son una nueva
auditoría de los artículos. `sources.json` registra enlaces y fecha de
modificación de las fuentes; los SHA256 de las instantáneas se guardan en
`results/provenance.json`. Las terminaciones de línea se normalizaron al
guardar texto. Ninguna serie se declara cotejada anualmente con la fuente
original. No se corrigen conteos para hacerlos coincidir con los artículos.

Las referencias normalizadas tienen K=4 para el caso 1; K=2 para el 9; K=3
para 2–6 y 8; K desconocido para 7 y 10. Los diez casos permanecen en la
salida. Se excluyen 7/10 de métricas y de ejecución condicionada; se conserva
su diagnóstico original. El 6 se ejecuta sobre la ventana completa, sin
métrica de cercanía, porque la fuente no asigna 2024. Se añade por separado
el recorte explícito 2003–2023, que omite 84 publicaciones observadas.

Los tres estados son independientes:

- `algorithm_feasible`: se pudo obtener la partición con K y mínimo dados.
- `reference_satisfies_minimum`: los intervalos publicados cumplen el mínimo.
- `eligible_provisional_metrics`: la referencia cubre la ventana, cumple el
  mínimo y el algoritmo produjo K−1 cortes; la serie continúa sin cotejo
  anual externo. No equivale a elegibilidad para una validación definitiva.

Un ejemplo importante es el caso 2 con mínimo 3: los algoritmos pueden
segmentar, pero la fase publicada 2020–2021 no cumple ese mínimo. Se muestran
sus cortes, se explicita el conflicto y no se mezcla su puntuación en ese
agregado. El mínimo 2 se evalúa como escenario común predefinido, no elegido
por el valor obtenido de MAE.

Salidas:

- `conditioned_results.json` y `conditioned_cuts.csv`: 60 registros de ventana
  completa (incluyen estados no ejecutados), más 6 del recorte del caso 6;
  parámetros, fronteras, intervalos, razones de exclusión y métricas por caso.
- `paired_boundaries.csv`: parejas cronológicas y errores por frontera
  exclusivamente donde se permite puntuación provisional.
- `references_normalized.json`: identidad, evidencia, intervalos publicados
  sin completar 2024, K y cobertura; no contiene fronteras inventadas.
- `summary.json`/`.csv`: agregados por método disponible, conjunto común de
  los tres y estratos A/B de evidencia. Denominadores por casos y fronteras.
- `native_derivative_diagnostic.json`: 20 diagnósticos automáticos separados.
- `figures/conditioned_min2.svg` y `conditioned_min3.svg`: diez casos, con
  referencia publicada y cortes; los PNG se generan también para lectura.
- `provenance.json`, `verification.txt`: huellas, versiones y verificaciones.

Las métricas emparejan por orden cronológico, uno a uno, con K−1 igual.
MAE por caso = promedio de errores absolutos; agregado macro = promedio de
MAE de casos. También se exporta MAE agrupado por frontera, bajo otro nombre.
La tasa exacta agrupada conserva el denominador de fronteras. No se debe
comparar medias obtenidas de conjuntos distintos ni interpretar K impuesto
como éxito al estimar el número de fases. No se calcula «consistencia
estructural» o correspondencia temática, que requieren otra rúbrica.

Para decisiones y límites completos, consulte el protocolo y el informe
v0.2. La Tabla 2 histórica no es una referencia de ajuste ni un resultado
reproducido por esta actualización.
