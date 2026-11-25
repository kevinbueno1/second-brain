# Implementación y verificación del piloto

Documentado el **25 de noviembre de 2026**, hora de Ciudad de México. Las pruebas con el runtime y la instalación de desarrollo se realizaron el **24 de noviembre de 2026**. Esta página conserva resultados y límites; no contiene transcripciones, notas, rutas de perfil ni identificadores privados de sesiones.

## Qué construimos

Se conservó la bóveda central y el helper. Se añadieron política de extracción, adaptador de eventos, cola SQLite e instalador de captura. Se adaptaron criterios de `teach`, `domain-modeling` y Remember de `chief-of-staff`; `loop-me` sirvió como referencia para concretar el flujo. La separación entre fuentes y conocimiento sigue el patrón de Karpathy. No se instalaron las betas de Matt ni se modificaron sus originales.

La copia pública conserva el instalador portable, la plantilla de la skill y una bóveda vacía. Los resultados de una instalación personal no se copian como configuración de otros usuarios.

## Comprobaciones realizadas

| Comprobación | Resultado observado | Límite |
| --- | --- | --- |
| Suite de la implementación personal | 34 pruebas correctas | Pruebas aisladas, sin instalar hooks en el perfil real |
| Suite pública | 35 pruebas locales correctas, incluida la plantilla portable | Ver también CI Ubuntu/Windows del commit publicado |
| Extracción con modelo real y texto ficticio | Una preferencia útil, despedida omitida; aceptación en bóveda aislada y lint correcto | Una muestra pequeña no mide calidad general |
| Programador de tareas de Windows | Tras corregir el bloqueo por batería: Ready, resultado 0 y panel actualizado | Verificación del ejecutor con cola vacía |
| API hooks/list del CLI local 0.162.0-alpha.17.2 | Stop y SessionEnd habilitados y trusted | Lectura de estado; no demuestra aprobación nueva |
| Turno nuevo real mediante app-server | Stop emitió inicio/fin correcto; sesión encolada sin inyección manual | Conversación independiente de la ya abierta en el IDE |
| Procesamiento de esa sesión técnica | Cursor completado, cero candidatos, sin errores | El mensaje no contenía conocimiento personal que conservar |
| SessionEnd | Definición encontrada y confiable | Su emisión independiente no se probó |

La prueba nativa utilizó historial paginado. El IDE ya abierto puede requerir conversación nueva o reinicio para leer la configuración. No se afirma haber verificado un evento de aquella sesión antigua.

## Problemas encontrados y correcciones

- **PATH:** tener el ejecutable en una extensión no hace que la terminal conozca `codex`. La guía exige un CLI disponible y explica la ruta absoluta.
- **Arranque incompleto:** `--version` no probaba la interfaz. Se documentó `--no-daemon`, sugerido por el error y las opciones oficiales; el recorrido se probó por API.
- **Confianza asumida pendiente:** la consulta directa mostró hooks ya confiables. Se corrigió la guía; no se fabricó ni omitió su aprobación.
- **Tarea en cola por batería:** se permitió ejecutarla con batería y se comprobó el resultado final y la actualización efectiva del panel.
- **Índice:** copiar un enlace relativo a la raíz cambiaba su destino. Ahora se convierte en texto antes de abreviar el resumen, con prueba de regresión.
- **Reanudar tras pausa:** se añadió el intervalo de exclusión para evitar incorporar retroactivamente mensajes de la pausa.

## Qué falta evaluar

Calidad con sesiones cotidianas, omisiones, duplicados semánticos, consumo y recuperación ante archivos movidos/eliminados. Hace falta una prueba independiente de SessionEnd en cada cliente de interés. La publicación automática seguirá desactivada mientras se evalúa el piloto.

CI usa datos ficticios y perfiles temporales. No necesita cuenta de Codex ni ejecuta el modelo real. Los resultados de integración se registran como evidencia local resumida, no como una prueba repetida por CI.

## Mejoras posibles

Medir decisiones de revisión, ampliar casos de aceptación, recuperar fuentes y adaptar otros clientes cuando exista una necesidad real. La búsqueda semántica y una integración con todos los chats son trabajos separados. Instalar más skills no sustituye probar el evento y el recorrido completo.
