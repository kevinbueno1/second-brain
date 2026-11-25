# Protocolo de la bóveda personal

Esta bóveda es común a los proyectos del usuario. Sus archivos Markdown son la memoria duradera; la conversación y los agentes son medios para consultarla y mantenerla. La skill personal `second-brain` apunta aquí desde otros proyectos.

## Ubicaciones

- `INICIO.md`: navegación para la persona.
- `index.md`: catálogo generado de notas de entrada, proyectos, areas, conocimiento y archivo.
- `log.md`: registro generado de operaciones, con fechas UTC.
- `00-entrada`: ideas y preguntas pendientes de clasificar.
- `10-proyectos`: fichas y enlaces a proyectos; el código y los tickets viven en sus repositorios.
- `20-areas`: responsabilidades y objetivos continuos.
- `30-conocimiento`: notas derivadas reutilizables, explicaciones, decisiones e investigaciones.
- `40-archivo`: contenido inactivo conservado.
- `80-fuentes`: copias originales con hash y metadatos de procedencia. Se leen; las revisiones se guardan como nuevas fuentes.
- `90-plantillas`: formatos de apoyo existentes.
- `.brain`: eventos estructurados, revisiones anteriores y bloqueo de escritura. Su contenido lo gestiona el helper.

## Consultar

1. Usa el índice y `brain.py search "consulta"` para seleccionar páginas. La búsqueda es textual y tolera diferencias de acentos; no es semántica.
2. Lee el contenido completo pertinente y, si la conclusión depende de un detalle, su fuente. Distingue fecha y contexto del proyecto de origen de la situacion actual.
3. Responde con enlaces a las notas y fuentes utilizadas. Si falta evidencia, explícita la duda; investiga cuando lo requiera la tarea.
4. En consultas explícitas a la memoria, registra brevemente la consulta y las páginas utilizadas con `journal --operation query`. Incorpora la respuesta como nota solo si aporta conocimiento duradero.

## Incorporar

1. Identifica lo que merece conservarse: idea, decisión, aprendizaje, evidencia o corrección. La fuente puede ser un documento, URL, resultado comprobado o una decisión explícita de la conversación con fecha.
2. Usa `capture-source` si necesitas conservar un archivo original. Guarda una URL y fecha si no dispones del original. Un archivo binario conservado no equivale a un documento leído: utiliza la herramienta de lectura apropiada y deja claro lo que realmente se examinó.
3. Busca antes de crear: actualiza una página pertinente o crea una cuando el tema sea distinto. Lee completa una página existente antes de proponer su revisión.
4. Redacta un cuerpo Markdown en un archivo temporal del proyecto actual y publica mediante `brain.py publish`. Declara título, proyecto, fuentes, tipo y estado. El cuerpo va sin frontmatter ni título H1: empieza por el texto o por subtítulos `##`. El helper agrega metadatos, el título y una sección de fuentes.
5. `confirmado` indica que el origen respalda la afirmacion en el contexto declarado. Las sugerencias del asistente permanecen `propuesto` y las conjeturas, `hipótesis`. Una afirmacion que pierde vigencia se marca o explica como obsoleta con fecha y reemplazo; no se presenta como vigente sin comprobarla.
6. Comprueba la salida, lee el archivo publicado y ejecuta `lint`. El helper actualiza índice y registro, conserva la versión previa y serializa escrituras concurrentes. Si se edita directamente desde Obsidian o un editor, ejecuta `reindex` después; esas ediciones directas no crean una revisión automática del helper.

## Revisar

- Ejecuta `lint`: detecta referencias rotas, índice desactualizado y fuentes registradas cuyo hash cambio.
- Para reparar solo un índice atrasado, ejecuta `reindex` y vuelve a comprobar.
- Revisa con criterio las contradicciones, afirmaciones antiguas y duplicados conceptuales. El script no interpreta su veracidad ni fusiona notas por su cuenta.
- Usa `backup` antes de cambios amplios, migraciones o actualizaciones de herramientas. No hace falta convertir cada cambio pequeño en una migracion.
- Registra una revisión semántica con `journal --operation review`, incluyendo lo examinado y lo pendiente.

## Mantenimiento entre proyectos

Consulta cuando el conocimiento previo pueda cambiar una decisión o explicación. Incorpora al completar un hito, al confirmar una decisión o cuando el usuario pida recordar algo. Evita llenar la memoria con transcripciones completas, resultados transitorios o cada pequeño cambio de código. Conserva secretos y credenciales en los mecanismos destinados a ellos, no en las notas.

El alcance de un proyecto ajeno sigue gobernado por sus propias instrucciones y accesos. Un segundo agente puede investigar una fuente o revisar una propuesta independiente; no se necesita mantener un equipo de agentes permanente.

## Herramienta y extensiones

Cuando el usuario pida «Prepara la memoria de esta conversación», resuelve `../second-brain-tools/capture.py` desde esta bóveda y ejecútalo con `checkpoint --process-now`, el Python instalado y directorio de trabajo del proyecto de esa sesión. Verifica el resultado y conserva la revisión antes de publicar. Usa el ID del entorno de Codex o uno comprobado; una identidad ausente o ambigua requiere resolverla, nunca elegir el chat más reciente. Lee `../docs/PORTABILIDAD-Y-CIERRE.md` para argumentos, rutas, alcance y bloqueos pendientes. Esto prepara memoria sin cerrar la conversación.

Para revisar candidatos o diagnosticar la captura, lee `../docs/AUTOMATIZACION.md` y consulta `../second-brain-tools/capture.py status`. El panel `CAPTURA-PILOTO.md` es generado; la cola y configuración locales están en `.brain/capture`. Los candidatos no son conocimiento consolidado. Publica solo tras aceptación explícita y lectura de las notas relacionadas; resuelve los conflictos R antes de consolidar. Mantén estado, panel, fuentes y notas personales fuera de GitHub.

El helper está en `../second-brain-tools/brain.py` y usa la biblioteca estándar de Python. `../second-brain-tools/install_global.py` instala la skill personal y las referencias globales con cambios acotados y copias previas. El manual de uso y evolución es `INSTRUCTIVO.md`.

Esta versión utiliza archivos nativos. La captura tiene un instalador separado y un ejecutor horario para Windows; comprueba su estado real antes de declararla activa. Basic Memory/MCP, búsqueda semántica y captura desde otras aplicaciones siguen como extensiones futuras.
