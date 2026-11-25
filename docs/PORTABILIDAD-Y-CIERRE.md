# Replicar el Second Brain y preparar memoria a petición

Actualizado el 25 de noviembre de 2026.

## Qué obtienes al descargar GitHub

El [repositorio público](https://github.com/kevinbueno1/second-brain) contiene el programa, pruebas, documentación, plantillas, skill propia e instaladores. Distribuye una **bóveda vacía**. Tus notas personales, fuentes, candidatos, contraseñas, autenticación, configuración global, cola y copias de seguridad permanecen fuera de esa publicación. Las skills originales de Matt se referencian; no se distribuyen completas.

En otro ordenador, sigue el README del repositorio: instala Python 3.12+, crea el entorno, instala las dependencias y configura la skill con `install_global.py`. Para captura, instala y autentica Codex CLI y ejecuta por separado `install_capture.py`. Comprueba permisos, confianza de hooks y un evento real en ese cliente. Descargar archivos por sí solo no instala ni activa estas conexiones. Obsidian es opcional y se instala por separado.

La programación horaria incluida es de Windows. En macOS/Linux utiliza el intérprete del entorno y un programador propio, o ejecuta el procesador manualmente. El teléfono puede servir para consultar/editar Markdown con una solución de sincronización; no se comprobó como entorno del ejecutor local completo.

## Misma infraestructura frente a misma memoria

Una instalación nueva empieza sin tus recuerdos. Para conservar la **misma memoria** entre ordenadores necesitas además transferir una copia privada o configurar sincronización privada de notas y fuentes. Eso todavía no está automatizado por este repositorio.

Cada equipo debe mantener su configuración de captura y cola SQLite local, con sus propias rutas y transcripciones. Evita sincronizar en vivo `.brain/capture`, perfiles de Codex y entornos virtuales. La sincronización simultánea de una bóveda necesita resolver también conflictos de notas, historial e índice; el bloqueo local no coordina dos equipos. Como punto de partida, usa un equipo escritor a la vez y una copia privada de la bóveda. Reinstala la skill para que apunte a la ruta real del equipo receptor.

## Comando en la conversación

En una conversación de Codex local conectada a esta bóveda, escribe:

> Prepara la memoria de esta conversación.

El asistente ejecuta `capture.py checkpoint --process-now` sobre la **sesión exacta** y te informa si se encoló, si se procesó un bloque y si hay candidatos. Puedes continuar hablando después. La frase es una instrucción para el asistente, no un nuevo comando `/...` registrado en Codex.

El checkpoint reutiliza filtros, evidencia, deduplicación, cola y revisión. No emite un evento `SessionEnd`, no cierra ni archiva la conversación y no acepta candidatos por su cuenta. Los hooks naturales siguen funcionando como antes. El extractor consume uso de Codex cuando encuentra mensajes elegibles.

## Comando en PowerShell

Dentro de la carpeta del repositorio, **desde el entorno de herramientas de una conversación de Codex**:

```powershell
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\capture.py checkpoint --process-now
```

Sin `--process-now` solo encola el snapshot y lo deja para el procesador habitual.

Una terminal independiente puede no tener el ID de la conversación. En ese caso pasa su ID real y la carpeta de origen; no copies literalmente los marcadores:

```powershell
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\capture.py checkpoint --session-id ID_REAL --project 'RUTA_DEL_PROYECTO' --process-now
```

Desde otra carpeta, usa rutas absolutas al intérprete y al helper. El ID se toma de `CODEX_THREAD_ID` o `CODEX_SESSION_ID` si están disponibles y coinciden, o de `--session-id`. Se usa el transcript ya registrado o se busca el archivo de ese ID bajo las ubicaciones permitidas. Si hay varias coincidencias, pasa además `--transcript 'RUTA_EXACTA.jsonl'`. Se comprueban identidad y proyecto; nunca se elige la conversación más reciente como sustituta.

Si el proyecto está fuera del alcance, la captura está pausada o se trata de un subagente, se informa que no se encoló. Para un proyecto nuevo, primero hay que incorporarlo deliberadamente a `allowed_roots` de la configuración local; instalar la skill global y permitir captura automática son dos acciones distintas.

`--process-now` procesa como máximo **un bloque de esa sesión**, sin la espera por inactividad. Conserva el bloqueo de otro trabajador y la espera de reintento tras errores. Un resultado `processed: 0` no demuestra que la memoria esté lista: revisa `status` y el panel. Las conversaciones largas pueden necesitar más ejecuciones; un formato no soportado o un mensaje demasiado grande queda pendiente con error. El panel es `second-brain/CAPTURA-PILOTO.md`; pide «Revisa los candidatos de captura de mi Second Brain» para decidir qué conservar.

## ¿Conviene capturar toda mi cuenta de ChatGPT?

Recomendación: ampliar por ámbitos útiles y evaluar hallazgos selectivamente. Guardar conversaciones completas por defecto acumula duplicados, opiniones provisionales, información pasajera y posibles errores que después pueden confundirse con hechos.

El criterio es la utilidad futura del hallazgo, no que la conversación sea formal o larga:

| Resultado | Qué conservar |
| --- | --- |
| Categoría 1 | Decisiones con sus motivos, soluciones comprobadas, correcciones y aprendizajes reutilizables; contexto y evidencia suficientes |
| Categoría 2 | Ideas, preferencias estables y contexto breve para retomar algo; como propuesta cuando corresponda |
| Omitir | Cortesías, consultas pasajeras, repeticiones y contenido excluido por la persona |
| R | Contradicciones, incertidumbre o conflicto con una nota: revisión antes de consolidar |

Una charla informal puede aportar una buena idea; un proyecto puede producir muchos mensajes sin valor duradero. Importancia y certeza se evalúan por separado. Conserva la posibilidad de pausar y pedir no guardar, y revisa candidatos por lotes. El filtro automático de exclusión es parcial y no sustituye esa revisión.

La integración actual observa sesiones locales de Codex en las carpetas permitidas. **No hay una conexión activa con todo el historial de la cuenta de ChatGPT.** Incorporar otros chats requiere un adaptador o una importación deliberada; esta petición no los activa. La memoria nativa de ChatGPT y la memoria local nativa de Codex tienen sus propios almacenes y controles, separados de nuestra bóveda Markdown. Fuente: [documentación oficial de memorias](https://learn.chatgpt.com/docs/customization/memories).

Los eventos reales de cierre los determina el cliente. Fuente: [documentación oficial de hooks](https://learn.chatgpt.com/docs/hooks).
