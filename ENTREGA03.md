# Entrega 03 — series verificadas y comparación actualizada

Base: `60ea426564f37622a8f7fc090ad3f9d8b63070ac`, rama `revision/istl`.
Consultar [instrucciones](istl/v3/README.md) e [informe breve](istl/v3/INFORME_DIRECTOR_v0.3.md).

```sh
python -m pip install -r istl/requirements.txt
python -m unittest discover -s istl/v3 -p test_v3.py -v
python istl/v3/run.py
```

El Excel de trabajo cambia únicamente caso 2, 2004: 2→1. El original está
congelado en `istl/v3/sources/base_data_articles.xlsx`. Los archivos de código
y resultados de las entregas anteriores no se modifican. Sus pruebas deben
usarse con sus datos históricos, no con el Excel corregido; `istl/v3/verify.py`
ejecuta ambas suites antiguas en una copia aislada de la entrega02.

El caso 6 conserva 2024=84 en fuente y usa 2003–2023 en comparación.
El caso 7 entra con las fases textuales aprobadas. El 10 sigue sin concordancia.
No se modificó el manuscrito ni se publicaron cambios.
