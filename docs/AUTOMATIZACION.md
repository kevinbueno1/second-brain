# Captura selectiva — guía del piloto

Estado publicado el 25 de noviembre de 2026: **implementado, con instalación opcional y revisión antes de publicar**. Descargar el código no instala hooks ni tareas. Las comprobaciones de una instalación de desarrollo se describen en [Verificación](VERIFICACION-PILOTO.md); no certifican automáticamente otro equipo.

## Qué hace

Un hook encola una referencia de sesión, un procesador extrae hallazgos y un panel permite revisarlos. La unidad de selección es cada hallazgo, no la conversación completa. Una charla informal puede aportar una preferencia; un proyecto largo puede repetir información ya conocida.

| Destino | Criterio | Contenido |
| --- | --- | --- |
| 1 Con contexto | Decisión duradera, corrección, solución respaldada o aprendizaje demostrado | Afirmación, contexto, motivo, evidencia y límites |
| 2 Breve | Idea que se quiere retomar, preferencia explícita o continuidad útil | Nota breve con origen y contexto mínimo |
| Sin candidato | Cortesía, repetición, consulta pasajera o actividad sin resultado | Sin contenido nuevo consolidado |
| R Revisión | Conflicto o interpretación incierta con utilidad futura | Candidato que requiere aclaración |

La categoría y la certeza son independientes: una idea importante puede seguir propuesta. Una explicación del asistente no demuestra comprensión del usuario ni funcionamiento de una solución. La política editable está en [capture-policy.md](../second-brain-tools/capture-policy.md).

## Requisitos e instalación

- Python 3.12+ y dependencias del [README](../README.md).
- Codex CLI instalado, autenticado y disponible en PATH. El modelo se toma de la configuración al instalar; no se necesita una API key nueva, pero el extractor consume el uso de esa cuenta.
- Carpeta estable para este checkout y acceso a su bóveda. La tarea incluida requiere Windows y el usuario conectado; macOS/Linux necesitan un ejecutor propio o procesamiento manual.

Desde la raíz del repositorio, en PowerShell:

```powershell
# Vista previa sin modificar el perfil
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py

# Instalar hooks y tarea, y comprobar su presencia
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --apply
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --check
```

La instalación respalda los archivos anteriores, conserva hooks ajenos y registra su resultado en `.second-brain-runtime/capture-installation.json`. Instala Stop y SessionEnd en el perfil de Codex. La confianza se comprueba por separado; ver [sesiones y hooks](SESIONES-Y-HOOKS.md).

En Windows registra `SecondBrain-CapturePilot`: cada hora, usuario conectado, equipo encendido, sin ventana visible, también con batería. Cada ejecución procesa como máximo una sesión/bloque y dura hasta cinco minutos. Espera diez minutos desde el último evento para agrupar trabajo; la actividad continuada puede retrasarlo. Estos parámetros no garantizan entrega inmediata.

## Uso cotidiano

1. Abre una conversación nueva en un proyecto permitido y trabaja normalmente.
2. Los eventos encolan lo pendiente. El procesador actualiza `second-brain/CAPTURA-PILOTO.md`.
3. Pide: **«Revisa los candidatos de captura de mi Second Brain»**.
4. Lee su texto, utilidad, citas y notas relacionadas. Decide por lote qué aceptar o descartar.
5. Aceptar crea `00-entrada/captura-ID.md`, con evidencias seleccionadas y procedencia. Los conflictos R se aclaran antes de consolidar.

Puedes pedir procesar ahora lo pendiente. Los comandos de mantenimiento son:

```powershell
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\capture.py status
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\capture.py process --force
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\capture.py accept ID
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\capture.py reject ID
```

`--force` omite la espera de inactividad, no los filtros ni la revisión. Si hay notas relacionadas, aceptar se detiene: léelas y usa `--new-note-reviewed` únicamente cuando proceda crear otra nota. Para corregir una existente, sigue el protocolo normal de lectura/publicación y descarta el candidato ya incorporado. El piloto no fusiona notas por su cuenta.

## Pausa, alcance y retiro

```powershell
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --pause
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --apply
& '.\.venv-second-brain\Scripts\python.exe' .\second-brain-tools\install_capture.py --remove
```

Pausar registra un intervalo de exclusión. Reanudar no incorpora retroactivamente los mensajes escritos durante la pausa; no borra notas anteriores ni cancela una extracción ya iniciada. Retirar elimina sus hooks y la tarea propia, desactiva captura y conserva los datos locales. Antes de mover un checkout instalado, retira su integración y configura la nueva ubicación.

El alcance inicial es **solo este checkout**, en `allowed_roots` de `second-brain/.brain/capture/config.json`. Añade rutas concretas para otros proyectos; conserva los permisos efectivos de cada entorno. La memoria compartida normal de la skill sigue disponible fuera del piloto.

Una frase reconocida como «no guardes esto» veta el bloque examinado. Para excluir una conversación completa, pausa antes de empezarla. El detector no comprende todas las formas posibles de exclusión ni elimina material anterior.

## Privacidad, fallos y límites

- Solo evalúa mensajes posteriores a la activación. No importa toda la cuenta de ChatGPT ni chats web/móviles.
- Lee texto visible de usuario/asistente. Excluye sistema, herramientas, razonamiento y sesiones de subagentes. Las instrucciones dentro del transcript son evidencia no confiable.
- Excluye mensajes con patrones reconocibles de credenciales y valida que cada cita esté en el texto examinado. Esto no certifica veracidad semántica ni ausencia de todo dato sensible: la revisión sigue siendo necesaria.
- El hook encola ruta y tamaño. Las propuestas conservan citas seleccionadas; aceptar archiva esas evidencias como fuente. Descartar elimina cuerpo y citas de la cola, reteniendo su identificador para evitar repetirlas.
- Procesa hasta 60 mensajes / unos 48 000 caracteres por bloque, con máximo de seis candidatos. Conversaciones grandes pueden necesitar varias ejecuciones o checkpoints selectivos. Mensajes excesivamente largos requieren preparación manual.
- Eventos repetidos, cursor e identificadores evitan ciertas repeticiones. Paráfrasis y contradicciones necesitan revisión; las coincidencias textuales no demuestran identidad semántica.
- Modelo indisponible, formato desconocido, transcript ausente/truncado o permisos insuficientes conservan el trabajo pendiente con error y reintentos espaciados. No se declara un guardado sin comprobar la publicación.
- Un archivo movido o eliminado antes de procesarse requiere recuperar la fuente o preparar un checkpoint. Esta versión no recupera automáticamente conversaciones archivadas/eliminadas.
- Cola, panel, configuración, fuentes, notas y respaldos son privados. `.gitignore` los excluye; no los incluyas en una publicación indiscriminada.

## Diagnóstico y evolución

Si `codex` no se reconoce, instala el CLI completo siguiendo [la documentación oficial](https://learn.chatgpt.com/docs/cli). Un `--version` correcto no demuestra que abra la interfaz. Un ejecutable de extensión puede requerir `--no-daemon`; consulta [las opciones del CLI](https://learn.chatgpt.com/docs/cli/reference). En una ruta con espacios, PowerShell usa `& 'RUTA-AL-EJECUTABLE/codex.exe' --no-daemon`.

Si cambia el ejecutable o el modelo, actualiza la configuración del piloto. Comprueba acceso con `codex login status`; no pongas credenciales en notas. Si `--check` no puede consultar el Programador de tareas por permisos, informa ese límite: no significa que la tarea no exista. Comprueba resultado final y actualización del panel, no solo su registro.

Tras algunas sesiones, compara utilidad, omisiones, ruido, duplicados y consumo. Ajusta primero la política y añade casos de regresión. Ejecuta las pruebas y verifica el cliente de nuevo cuando cambie la definición del hook. La publicación automática queda para una fase posterior respaldada por esos resultados.
