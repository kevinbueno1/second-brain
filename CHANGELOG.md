# Registro de cambios

## 2026-11-25 — Captura a petición y portabilidad

- Nuevo `capture.py checkpoint`, con ID de sesión del entorno o explícito, resolución de transcript y validación de identidad/proyecto. Reutiliza la cola de los hooks sin emitir un evento SessionEnd ni cerrar el chat.
- `--process-now` procesa un bloque de esa sesión, conserva filtros y reintentos, y deja candidatos sujetos a revisión. El comando informa errores de procesamiento.
- Protocolo de uso con «Prepara la memoria de esta conversación», guía para otro equipo y criterios de selección al ampliar el alcance.
- Ocho pruebas nuevas: comando real en perfil aislado, identidad, ambigüedad, exclusiones, deduplicación entre checkpoint y hook, sesión objetivo, errores y reintento. Las pruebas locales de esta publicación suman 43.

## 2026-11-25 — Piloto de captura selectiva

- Se añadió `capture.py`: cola SQLite, lectura incremental de sesiones locales, extracción semántica, citas verificables, búsqueda de notas relacionadas y panel revisable.
- Se añadió `install_capture.py`: vista previa, hooks Stop/SessionEnd con respaldo y tarea horaria de Windows con usuario conectado, también en batería; pausa, reanudación y retiro de la integración.
- La publicación automática queda desactivada. Aceptar crea una nota y conserva sus evidencias mediante `brain.py`; se revisan conflictos y actualizaciones por separado.
- Pausar registra un intervalo de exclusión para que reanudar no recupere mensajes escritos durante la pausa. Descartar elimina el cuerpo y las citas del candidato conservando su identificador.
- Se documentaron alcance, criterios, privacidad, uso cotidiano, sesiones, diagnóstico y mejoras. Se registran las comprobaciones reales del 24 de noviembre sin publicar rutas, notas ni transcripciones personales.
- Se corrigieron los resúmenes del índice para convertir sus enlaces en texto antes de abreviarlos; así no se reinterpretan rutas relativas desde la raíz.
- Se añadieron pruebas de idempotencia, reapertura, carreras de eventos, fallos del modelo, procedencia de citas, exclusiones, cambios de formato, pausa y publicación revisada. Se preserva la prueba de portabilidad del instalador público.

Ver [instalación y uso](docs/AUTOMATIZACION.md), [sesiones](docs/SESIONES-Y-HOOKS.md) y [verificación con límites](docs/VERIFICACION-PILOTO.md).

## 2026-11-24 — Publicación inicial

Bóveda vacía, helper Python, skill personal, instalador portable, plantillas, documentación y pruebas con CI en Ubuntu/Windows. La captura automática se publicó inicialmente como propuesta.
