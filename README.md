# Second Brain con Markdown y Codex

Infraestructura local para conservar ideas, proyectos, decisiones y aprendizaje en una bóveda central. Una skill personal permite que Codex consulte y actualice esa misma memoria desde distintas carpetas de trabajo. Obsidian es una interfaz opcional para los mismos archivos.

Esta publicación contiene código, pruebas, plantillas y documentación, incluido el primer piloto de captura selectiva. La bóveda se distribuye vacía: las notas personales y sus fuentes permanecen fuera de la publicación. Descargar este repositorio no activa hooks ni tareas en tu equipo.

## Estado del proyecto

| Componente | Estado |
| --- | --- |
| Bóveda Markdown y protocolo de consulta, incorporación y revisión | Implementado |
| Captura de fuentes con SHA-256, notas con procedencia y versiones anteriores | Implementado |
| Búsqueda textual, índice, registro, comprobaciones y copias ZIP | Implementado |
| Skill personal e instalador con vista previa y respaldo de configuración | Implementado |
| Pruebas de operaciones, concurrencia e instalación aislada | Incluidas |
| Plantillas para ideas, proyectos, aprendizaje y entrevista de requisitos | Incluidas |
| Cola de eventos Stop/SessionEnd, extracción con modelo y panel de candidatos | Piloto implementado; instalación opcional |
| Procesador horario en Windows, pausa/reanudación y publicación aceptada | Implementado; publicación automática desactivada |
| Búsqueda semántica y conexión con todos los chats de una cuenta | No implementadas |

## Empezar

Requiere Python 3.12 o posterior. Descarga el repositorio y abre una terminal en su carpeta. En PowerShell:

```powershell
python -m venv .venv-second-brain
& '.\.venv-second-brain\Scripts\python.exe' -m pip install -r .\second-brain-tools\requirements-setup.lock.txt
python .\second-brain-tools\brain.py reindex
python .\second-brain-tools\brain.py lint
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_global.py
```

El último comando solo muestra la propuesta de instalación. Revísala antes de aplicarla:

```powershell
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_global.py --apply
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_global.py --check
```

El instalador añade una skill a `~/.agents/skills/second-brain`, un bloque delimitado a las instrucciones globales de Codex y dos rutas de escritura: la bóveda y sus copias. Conserva una copia de los archivos previos y respeta el resto de la configuración. La skill se genera con las rutas de tu descarga. El entorno puede requerir autorización para modificar el perfil y aplicar sus propias restricciones de acceso.

En Linux o macOS, utiliza el intérprete `.venv-second-brain/bin/python` para los comandos del entorno virtual.

Abre una conversación nueva de Codex y escribe:

> Usa second-brain para guardar esta idea como propuesta: ...

> Consulta second-brain antes de ayudarme a definir este proyecto: ...

> Guarda los aprendizajes comprobados y las decisiones importantes de este hito, con sus fuentes.

## Documentación

- [Inicio de la bóveda](second-brain/INICIO.md).
- [Instructivo y conexiones](second-brain/INSTRUCTIVO.md).
- [Ejemplo cotidiano](second-brain/EJEMPLO-COTIDIANO.md).
- [Arquitectura](docs/ARQUITECTURA.md).
- [Captura automática: instalación, uso y límites del piloto](docs/AUTOMATIZACION.md).
- [Stop, SessionStart y SessionEnd](docs/SESIONES-Y-HOOKS.md).
- [Qué se implementó y qué se comprobó](docs/VERIFICACION-PILOTO.md).
- [Registro de cambios](CHANGELOG.md).
- [Referencias y atribución](NOTICE.md).

Para usar Obsidian, abre la carpeta `second-brain` como una bóveda existente y entra en `INICIO.md`. La aplicación se instala por separado.

## Comprobar el código

```powershell
& '.\.venv-second-brain\Scripts\python.exe' -m unittest discover -s second-brain-tools/tests -v
```

Las pruebas usan carpetas y perfiles temporales. No instalan la skill en el perfil real.

El helper de notas usa únicamente la biblioteca estándar de Python. `tomlkit` se utiliza para editar la configuración conservando sus otros ajustes; PyYAML sirve para validar skills durante el desarrollo.

## Memoria privada y publicación

El `.gitignore` excluye por defecto las notas personales, las fuentes, el historial, las copias y el estado de ejecución. Las plantillas y los documentos de uso sí pertenecen al repositorio. Si eliges versionar conocimiento real, revisa deliberadamente su audiencia y sus fuentes.

## Activar el piloto opcional

El piloto requiere Codex CLI instalado, autenticado y disponible como `codex` en PATH. El extractor usa la autenticación y el modelo configurado al instalar, y consume el uso de esa cuenta. Python gestiona la cola y los archivos; el modelo selecciona significado.

```powershell
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --apply
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --check
```

La primera orden muestra la propuesta. Aplicarla instala dos hooks personales y, en Windows, una tarea horaria oculta con tu usuario conectado. Inicialmente permite solo este checkout. Revisa su confianza en Codex y comprueba un evento real del cliente; los resultados de la instalación de desarrollo no se transfieren a tu equipo.

En chat: **«Revisa los candidatos de captura de mi Second Brain»**. El panel local `second-brain/CAPTURA-PILOTO.md` muestra las propuestas, citas y posibles notas relacionadas. Aceptar publica una nota; descartar elimina su cuerpo y citas de la cola. Los conflictos y las actualizaciones de notas existentes necesitan revisión.

Lee [la guía completa](docs/AUTOMATIZACION.md) para pausar, reanudar, añadir otro proyecto o retirar la integración. En macOS/Linux, el instalador no registra un programador de tareas: hace falta ejecutar `capture.py process` manualmente o integrar un ejecutor propio. El código y sus pruebas son portables; la programación incluida es de Windows.

Este piloto trabaja con eventos de Codex local. No sincroniza toda la cuenta de ChatGPT ni observa indiscriminadamente las carpetas del equipo.
