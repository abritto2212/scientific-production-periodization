# Dirección: revisión e integración de la entrega 02

Fecha: 5 de noviembre de 2026. Base remota: 5d48030 (revision/istl).

## Verificación independiente

Se aplicó el parche incremental sin colisiones sobre la primera entrega publicada.
Pasaron 11 pruebas originales y 12 pruebas nuevas. Se ejecutó nuevamente el runner
con salida separada: 66 registros condicionados y 20 diagnósticos automáticos.
Las fronteras, métricas, denominadores y referencias coinciden con la entrega.
Los JSON contienen pequeñas diferencias de punto flotante (tolerancia relativa
1e-12 y absoluta 1e-10), sin cambios de cortes; todas las filas de parejas de
fronteras coinciden. No se reemplazaron los resultados originales.

## Decisiones para la comparación provisional

- Mínimo principal: dos años; sensibilidad: tres. Declarar la interpolación
  exacta posible de una recta con dos observaciones.
- K procede de la fuente. No se evalúa el descubrimiento automático de K.
- Aceptar Derivadas-K como adaptación explícita; conservar el diagnóstico
  automático separado y reportar la inviabilidad sin fabricar candidatos.
- Priorizar resultados por caso; MAE macro secundario sobre conjuntos comunes,
  con denominadores. No declarar ganador ni validar la antigua Tabla 2.
- No ampliar ahora a evaluación temática o del número de fases.

## Actualización documental, sin reescribir la historia

Las salidas de istl/v2/results se calcularon con evidencia v0.1 y se conservan
como instantánea. Sus campos annual_series_verified=False describen esa versión,
no el estado documental actualizado. Consultar evidence_status_v0.2.json y el
informe adjunto para el estado actual. Las clases A/B antiguas no deben usarse
como sustituto del cotejo anual actualizado.

Según el informe 02 v0.2, los casos 1, 4, 5 y 10 coinciden íntegramente con
etiquetas numéricas de figuras, no con exportaciones bibliográficas originales.
El caso 5 es el ejemplo aplicado preferente; 2024 es parcial. Los casos 1 y 4
conservan conflictos entre suma de figura y texto. Los casos 2, 3, 8 y 9 siguen
exploratorios por cotejo anual pendiente. El 6 permanece excluido de concordancia
principal; el recorte es sensibilidad. El 7 sigue excluido pese a cortes en el
candidato. El 10 sigue excluido por ausencia de partición completa.

Esta actualización documental no cambia conteos, parámetros ni fronteras y no
convierte los agregados históricos en resultados definitivos. Antes de preparar
las tablas del manuscrito deben distinguirse los casos cotejados contra figuras
de los casos con cotejo pendiente. No se requiere certificar el corpus original
para comparar una figura publicada, pero sí delimitar expresamente ese alcance.

El informe 02 se incorporó desde el archivo entregado por el usuario; Dirección
no repitió aquí la lectura de todas las figuras originales. El manuscrito no se
modificó. La integración se prepara para revision/istl, sin merge a main.
