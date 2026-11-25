# Propuesta de captura automática

Estado: diseño revisable; no implementado ni activado en esta publicación.

El objetivo es conservar conocimiento útil sin solicitar cada guardado. La unidad de selección propuesta es cada hallazgo: una conversación puede contener una decisión relevante, una preferencia breve y muchos mensajes sin valor de memoria.

| Destino | Criterio | Contenido |
| --- | --- | --- |
| 1 Con contexto | Decisión duradera, corrección importante, solución comprobada o aprendizaje reutilizable | Afirmación, motivo, evidencia y límites necesarios |
| 2 Breve | Idea pendiente, preferencia explícita o dato de continuidad útil | Nota pequeña con origen y contexto mínimo |
| 0 Omitir | Cortesía, repetición o información transitoria | Sin contenido nuevo en la bóveda |
| Revisión | Conflicto, procedencia insuficiente o contenido que requiere criterio | Pendiente separado del conocimiento consolidado |

La selección debe justificar utilidad futura, novedad, respaldo y contexto necesario. La importancia y la certeza se evalúan por separado: algo importante puede seguir siendo una hipótesis.

La ruta técnica propuesta registra un hito o cierre, lo encola, extrae candidatos, consulta duplicados y publica notas con fuentes. Un procesador necesita un modelo para evaluar significado; un script puede gestionar la cola y verificar archivos. Los eventos repetidos deben ser idempotentes y los errores deben conservar el trabajo pendiente.

Codex documenta hooks como `Stop` y `SessionEnd`, con distinta semántica: fin de turno y fin de sesión. La disponibilidad, los accesos y el comportamiento del cliente deben comprobarse antes de conectarlos. El cierre de una carpeta no demuestra que un proyecto esté terminado. [Hooks oficiales](https://learn.chatgpt.com/docs/hooks).

Las memorias nativas de Codex utilizan un almacenamiento propio; un puente hacia esta bóveda sería otro componente. Las tareas programadas pueden servir como ejecutor cuando el entorno lo permita. [Memorias](https://learn.chatgpt.com/docs/customization/memories), [tareas programadas](https://learn.chatgpt.com/docs/automations).

Un piloto debería comprobar omisiones, publicaciones innecesarias, duplicados, correcciones, reapertura de sesiones, fallos de permisos, consumo y recuperación. Los resultados servirían para ajustar los criterios antes de habilitar una publicación desatendida.

La primera fase prevista es Codex local. Incorporar todo el historial de una cuenta de ChatGPT requiere una integración y un alcance distintos.
