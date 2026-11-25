# Un día usando tu Second Brain

Guía práctica creada el 10 de noviembre de 2026. El proyecto y los resultados de abajo son ficticios: muestran cómo usar el sistema. Las rutas de notas del ejemplo todavía no representan proyectos, decisiones ni pruebas reales.

El caso combina dos de tus intereses: automatizar una tarea y aprender data engineering. Imagina que recibes archivos CSV cada semana y quieres consolidarlos sin repetir registros.

## 1. Por la mañana: aparece una idea

Abres una conversación de Codex con acceso a tu bóveda y escribes:

> Usa second-brain para guardar esta idea como propuesta: quiero automatizar la consolidación de los CSV que recibo cada semana. Me interesa resolver la tarea y aprender data engineering. Todavía no he decidido cómo implementarlo.

El asistente busca si existe una idea equivalente. Si corresponde crearla, guarda una nota de entrada con el objetivo y las dudas pendientes. No necesita decidir una tecnología para capturar la idea.

La nota podría quedar en `00-entrada/consolidar-csv.md`. Después del guardado real, el asistente debe mostrarte la ruta y qué conservó. Una idea guardada sigue siendo una propuesta; no implica haber iniciado el desarrollo.

## 2. Decides trabajar en ella

Creas y abres una carpeta de proyecto, por ejemplo `C:\Proyectos\consolidador-csv`, y comienzas una conversación nueva de Codex allí. Usas el mismo perfil local y el entorno debe permitir acceder a la bóveda central.

> Usa second-brain y recupera mi idea de consolidar CSV. Ayúdame a definir la primera versión. Primero aclaremos qué archivos recibo, qué resultado necesito y cómo sabremos que funciona.

El asistente recupera la idea y te ayuda a resolver las preguntas que cambian la solución: qué columnas existen, qué significa un duplicado, qué hacer ante un archivo inválido y qué resultado constituye una primera versión útil.

Cuando queda definido el proyecto, sus documentos detallados y tareas permanecen en la carpeta del proyecto. La bóveda conserva una ficha breve, por ejemplo `10-proyectos/consolidador-csv.md`, con objetivo, estado, decisiones principales y referencia a esa carpeta. La idea original puede enlazarse a la ficha.

No hay que copiar la bóveda dentro del proyecto. La skill personal apunta a la misma ubicación central desde ambas carpetas. Las demás skills de Matt solo estarán disponibles donde se hayan instalado.

## 3. Durante el trabajo: haces la tarea normal

Sigues conversando sobre la automatización:

> Ayúdame a implementar y comprobar la primera versión con estos archivos de ejemplo.

El asistente trabaja con el código y las pruebas del proyecto. No necesita publicar cada cambio en la memoria. Supongamos que descubrimos, mediante una prueba, que volver a procesar un archivo introduce registros repetidos, y después implementamos y comprobamos una solución.

Ese resultado sí puede aportar conocimiento reutilizable. Puedes pedir:

> Guarda en second-brain lo que acabamos de comprobar sobre el reprocesamiento. Explica el problema, la solución que funcionó, su contexto y la prueba que lo respalda. Conserva las dudas que queden abiertas.

El asistente buscaría una nota existente antes de crear otra. Una nueva podría quedar en `30-conocimiento/reprocesamiento-de-cargas.md`, con referencia al proyecto y a la evidencia. También puede hacer esta incorporación al detectar un hito pertinente siguiendo el protocolo actual; pedirlo explícitamente permite comprobar el resultado.

Una sugerencia sin probar se conserva como propuesta o hipótesis, no como una solución confirmada. Los resultados de esta escena son ficticios y no se han incorporado como aprendizaje real.

## 4. Al terminar el día: dejas un punto de retorno

> Actualiza la ficha del proyecto con el estado comprobado de hoy y el siguiente paso. Guarda solo las decisiones y aprendizajes que valga la pena recuperar. Dime qué archivos actualizaste.

El asistente revisa qué falta conservar y actualiza las páginas pertinentes. Si lo importante ya estaba guardado, debe decirlo sin crear duplicados. La lista detallada de tareas sigue en el proyecto.

La ficha podría indicar que la carga inicial funciona y que queda pendiente acordar el comportamiento ante archivos inválidos. Eso sería un estado fechado del proyecto, no una afirmación de que el código nunca volverá a cambiar.

Puedes cerrar la conversación. La memoria permanece en los archivos.

## 5. Al día siguiente: abres una conversación nueva

Desde la carpeta del proyecto escribes:

> Usa second-brain para recuperar el objetivo y las decisiones de consolidador-csv. Revisa también los archivos actuales del proyecto y ayúdame a continuar por el siguiente paso pendiente.

El asistente consulta la ficha y las notas relacionadas, y contrasta ese estado con los archivos actuales. No necesita recibir toda la conversación anterior para recuperar lo que quedó documentado.

Lo que nunca se guardó en las notas o en los documentos del proyecto puede necesitar una aclaración. El Second Brain no tiene acceso automático al contenido completo de todas tus conversaciones.

## 6. Otra semana: reutilizas lo aprendido en otro proyecto

Abres una carpeta distinta, por ejemplo `C:\Proyectos\importador-api`, e inicias una conversación nueva de Codex:

> Usa second-brain. Este proyecto importará datos desde una API. Consulta si tenemos aprendizajes sobre reintentos y reprocesamiento que puedan servir. Distingue lo aplicable de lo que necesita comprobarse aquí.

El asistente puede recuperar el aprendizaje del proyecto CSV. Examina su contexto antes de trasladarlo: una solución válida para archivos no determina por sí sola cómo funciona la API nueva.

Aquí se ve la utilidad de una memoria central: un resultado guardado en un proyecto puede ayudar a otro sin copiar las notas entre carpetas.

## También sirve para aprender sin desarrollar software

En una conversación local sobre computación cuántica podrías escribir:

> Ayúdame a estudiar este tema. Al terminar, guarda una explicación breve de lo que verificamos, las fuentes utilizadas y las dudas que quiero retomar. Busca antes si ya tenemos una nota relacionada.

La nota de aprendizaje quedaría en la misma bóveda. Los ejercicios y materiales pueden permanecer en su carpeta de aprendizaje, enlazados desde ella. Una conversación ordinaria de ChatGPT web requiere una incorporación adicional para pasar su contenido a esta bóveda; nuestra instalación no importa automáticamente todos los chats de la cuenta.

## Lo que puedes esperar de una operación real

| Lo que pides | Qué comprobar en la respuesta |
| --- | --- |
| Consultar conocimiento previo | Enlaces a las notas que se utilizaron y explicación de lo pertinente |
| Guardar una idea o aprendizaje | Ruta concreta de la nota creada o actualizada y estado del contenido |
| Retomar un proyecto | Objetivo, decisiones y pendientes recuperados, contrastados con el estado actual |
| Revisar la memoria | Alcance de la revisión, problemas encontrados y dudas que requieren criterio |

Puedes leer esas mismas notas en Obsidian o VS Code. Obsidian es opcional y abrirlo no es el disparador del guardado.

Para probar el flujo con contenido real, empieza por una idea tuya y pide su captura como propuesta. Comprueba el archivo que indique el asistente antes de continuar con la definición del proyecto.

## Referencias de esta guía

- [Inicio de la bóveda](INICIO.md).
- [Instructivo de uso, conexiones y mejoras](INSTRUCTIVO.md).
- [Protocolo de consulta, incorporación y revisión](AGENTS.md).

La guía es un ejemplo del asistente para explicar la instalación actual. No constituye evidencia de haber desarrollado los proyectos ficticios.
