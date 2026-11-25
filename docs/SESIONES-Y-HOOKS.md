# Sesiones y hooks

Una conversación guardada puede retomarse; una sesión de trabajo puede contener muchos turnos. El proyecto puede continuar después de cerrar la sesión.

| Evento | Significado |
| --- | --- |
| SessionStart | Codex inicia o reanuda el hilo; contempla también orígenes como compactación |
| Stop | Termina un turno del asistente; la conversación puede seguir |
| SessionEnd | Codex da por terminada la sesión técnica |

SessionEnd se documenta para cierre normal de Codex, archivo/eliminación de una conversación todavía abierta o tras 30 minutos de inactividad sin estar abierta en ningún cliente. Cambiar de pestaña no lo produce inmediatamente. Interrumpir una respuesta genera Interrupt, distinto de Stop. [Hooks oficiales](https://learn.chatgpt.com/docs/hooks).

Ejemplo: preguntas por una automatización y recibes respuesta → Stop; pides otro requisito y recibes respuesta → otro Stop. Al terminar la sesión puede llegar SessionEnd. El piloto conecta Stop y SessionEnd para encolar trabajo; no instala un handler SessionStart.

## Conexión con el piloto

Los eventos no evalúan conocimiento ni publican notas directamente. Registran pendientes que procesa la tarea horaria. Los filtros, la espera de diez minutos y el control de duplicados pertenecen al adaptador, no a la definición de sesión de Codex.

## Confianza y comprobación

Las definiciones no administradas requieren confianza para ejecutarse. Consulta `/hooks` dentro del CLI para revisar las pendientes; no es una orden de PowerShell. Una integración programática puede usar `hooks/list` del [app-server](https://learn.chatgpt.com/docs/app-server), después de `initialize` e `initialized`, y revisar `enabled`, `currentHash` y `trustStatus`.

En la instalación de desarrollo ambos figuraban ya como `trusted`. Se consultó su estado y se probó Stop; no se modificó ni eludió la confianza. Es evidencia fechada de ese equipo, no una autorización que se transfiera al descargar el repositorio. Presencia del JSON, confianza y emisión del evento son comprobaciones diferentes. Ver [Verificación](VERIFICACION-PILOTO.md).
