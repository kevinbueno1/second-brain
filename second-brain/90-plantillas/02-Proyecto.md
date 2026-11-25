---
id: "POR-ASIGNAR"
tipo: proyecto
estado: borrador
dominios: []
actualizado: "AAAA-MM-DD"
version: 0.1
---

# [Nombre del proyecto]

Estados sugeridos: borrador → por revisar → definido → activo → cerrado. También puede estar en pausa o descartado. «Definido» significa que existe contexto suficiente para el siguiente paso acordado; no implica haber eliminado toda incertidumbre.

Cada dato relevante debe indicar si está **confirmado**, **propuesto**, **desconocido** o **no aplica**. Incluye la fuente cuando pueda haber dudas. No rellenes con números o decisiones inventados.

## Ficha breve

> Para [persona], que necesita [resolver una situación], queremos [resultado], dentro de [límites]. Lo consideraremos logrado cuando [evidencia observable].

- Problema o pregunta y por qué importa:
- Personas que lo usarán, se verán afectadas o decidirán si sirve:
- Resultado esperado y evidencia de éxito:
- Límites principales, incluido tiempo o presupuesto si existen:
- Primera entrega útil:

Para algo sencillo, estas cinco respuestas y la siguiente acción pueden bastar. Desarrolla las secciones que aporten claridad antes del siguiente compromiso.

## 1. Contexto y situación actual

- Cómo se hace hoy o qué sabemos del problema:
- Un ejemplo real de entrada y resultado deseado:
- Fuente del contexto:
- Qué se ha intentado y qué ocurrió, si aplica:

## 2. Alcance

- Incluye en esta versión:
- Queda fuera de esta versión:
- Entregables:
- Dependencias y responsables:

## 3. Entradas, salidas y comportamiento

- Qué inicia el proceso o el trabajo:
- Entradas, origen y disponibilidad:
- Salidas, destino y quién las utiliza:
- Flujo principal:
- Excepciones y comportamiento esperado si algo falla:

## 4. Requisitos verificables

Un requisito describe un resultado o comportamiento necesario. Una tarea describe trabajo para conseguirlo. Distingue ambos al planificar.

Forma útil: «Cuando [condición], [actor o sistema] debe [comportamiento observable], cumpliendo [límite relevante]».

| ID | Requisito | Motivo y fuente | Prioridad | Aceptación y cómo verificar | Estado de definición |
| --- | --- | --- | --- | --- | --- |
| R-001 | [Una obligación concreta] | [Necesidad de origen] | [Imprescindible / deseable / posterior] | [Evidencia, método y umbral si aplica] | [Confirmado / propuesto / desconocido] |

Evita «rápido», «intuitivo» o «confiable» sin explicar cómo observarás esa cualidad. Si desconoces el umbral, regístralo como pendiente y define cómo decidirlo. No inventes precisión.

Ejemplo ilustrativo, pendiente de adaptarse a un proyecto real:

- R-001: «Al volver a procesar un documento ya registrado, el flujo debe conservar una sola entrada asociada a su identificador».
- Aceptación: procesar dos veces el mismo identificador y comprobar que solo existe una entrada. Registrar cómo se reconoce el documento es una decisión pendiente si todavía no está definido.

## 5. Restricciones y calidad

- Tiempo disponible, fecha objetivo y presupuesto:
- Herramientas obligatorias y razón de la restricción:
- Acceso, datos personales o permisos relevantes:
- Volumen, rendimiento, fiabilidad o facilidad de uso que deba comprobarse:
- Quién lo mantendrá y cómo detectará errores, si aplica:

Separa una herramienta obligatoria de una posible solución técnica. La arquitectura se elige con el contexto disponible y puede cambiar.

## 6. Módulos adicionales

Usa todos los que apliquen. Marca como «no aplica» los demás, sin rellenarlos por obligación.

| Módulo | Preguntas adicionales |
| --- | --- |
| Automatización | ¿Qué la dispara? ¿Qué ocurre con duplicados, reintentos y fallos parciales? ¿Qué acciones requieren intervención? ¿Cómo se registra y recupera un error? |
| Software | ¿Cuáles son los recorridos principales? ¿Qué roles existen? ¿Dónde se usará? ¿Qué interfaces e integraciones necesita? ¿Cómo se entregará y mantendrá? |
| Data engineering | ¿Cuáles son las fuentes y el destino? ¿Qué representa cada registro? ¿Cuál es el esquema y la clave? ¿Qué frescura, calidad y volumen se requieren? ¿Cómo se recuperan cargas fallidas y cambios de esquema? |
| Aprendizaje | ¿Qué puedes hacer hoy? ¿Qué quieres demostrar al terminar? ¿Qué prerrequisitos faltan? ¿Cuánto tiempo tienes? ¿Qué ejercicio y explicación comprobarán lo aprendido? |
| Investigación o computación cuántica | ¿Qué pregunta o hipótesis explorarás? ¿Con qué método y referencia compararás, si aplica? ¿Qué supuestos, recursos y límites tiene el experimento? ¿Qué conservarás para repetirlo? ¿Qué conclusiones permitiría un resultado negativo? |
| Proyecto personal | ¿Qué cambio observable buscas? ¿Quién interviene? ¿Qué compromisos, recursos y fecha realista existen? ¿Cómo sabrás que terminó? |

En investigación, termina el proyecto al ejecutar y documentar la investigación acordada, aunque la hipótesis no se confirme. No prometas de antemano un descubrimiento ni una ventaja cuántica.

## 7. Dudas, supuestos y decisiones

| ID | Pregunta o supuesto | Impacto si es incorrecto | Cómo resolverlo | ¿Bloquea el siguiente paso? |
| --- | --- | --- | --- | --- |
| D-001 | [Por aclarar] | [Impacto] | [Persona, consulta o experimento] | [Sí / no, con motivo] |

| Fecha | Decisión y responsable | Motivo | Requisitos afectados |
| --- | --- | --- | --- |
| [AAAA-MM-DD] | [Decisión] | [Motivo] | [IDs] |

## 8. Primera entrega y plan

- Entrega mínima que permita comprobar utilidad o aprender algo decisivo:
- Acciones concretas, con requisito o duda de origen:
- Orden y dependencias:
- Qué se comprobará al terminar:
- Quién revisa y con qué evidencia:

## 9. Contexto para retomar

- Estado actual:
- Último resultado y enlace a la evidencia:
- Última decisión:
- Bloqueo actual, si existe:
- Siguiente acción concreta:
- Enlaces a código, notas y entregables:

## 10. Revisión y cierre

- ¿Se entiende la necesidad y quién decide si está resuelta?
- ¿La primera entrega y sus límites están claros?
- ¿Cada requisito imprescindible tiene una forma de comprobación?
- ¿Las dudas que bloquearían el siguiente paso están resueltas o tienen una investigación prevista?
- ¿Qué versión se revisó y qué cambió desde la anterior?
- Al cerrar: ¿qué evidencia se obtuvo, qué queda pendiente y qué aprendizaje reutilizable merece una nota propia?
