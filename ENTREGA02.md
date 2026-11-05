# Entrega 02 · Comparación provisional condicionada a fases publicadas

La entrega 01 conserva su código, once pruebas y resultados diagnósticos
en `istl/` y `istl/results/`. Su paquete y parche permanecen intactos.
La actualización añade exclusivamente `istl/v2/` y este índice.

La comparación nueva está en [istl/v2/README.md](istl/v2/README.md).
Véanse el [informe para Dirección](istl/v2/INFORME_DIRECTOR_v0.2.md)
y el [protocolo propuesto](istl/v2/PROTOCOLO_PROPUESTO_v0.2.md).

Desde la raíz:

```sh
python -m pip install -r istl/requirements.txt
python -m unittest discover -s istl -p test_periodization.py -v
python -m unittest discover -s istl/v2 -p test_conditioned.py -v
python istl/v2/run_conditioned.py
```

No se intentó publicar esta actualización. Dirección coordinará la aplicación
del parche en `revision/istl`. No se modificó el manuscrito ni se validó su
Tabla 2. Todos los indicadores nuevos son provisionales respecto de referencias
publicadas; no identifican un método ganador.
