# Arquitectura y decisiones

La implementación mantiene una bóveda central de Markdown separada de los repositorios de cada proyecto. La memoria persiste en los archivos; Codex selecciona qué consultar o incorporar mediante una skill personal.

| Componente | Responsabilidad |
| --- | --- |
| `second-brain` | Notas, originales, índice, registro y revisiones locales |
| `brain.py` | Operaciones de archivos, búsqueda textual, integridad estructural y copias |
| Skill personal | Selección de conocimiento, procedencia, consulta y mantenimiento |
| `install_global.py` | Generar rutas del checkout, preservar configuración y conectar el perfil de Codex |
| Obsidian | Interfaz opcional sobre los mismos archivos |

Las fuentes incorporadas se identifican por SHA-256 y se conservan como originales. Las notas derivadas pueden evolucionar con versiones previas, fecha, estado y procedencia. La búsqueda tolera diferencias de acentos; no es semántica.

Las escrituras del helper se serializan con un bloqueo exclusivo. Los reemplazos de notas utilizan archivos temporales y `os.replace`; esto evita exponer un archivo parcialmente escrito, pero no equivale a una transacción de base de datos para todos los archivos de una operación. Un fallo requiere revisar el registro y el índice.

La versión inicial utiliza la biblioteca estándar de Python para sus operaciones. La configuración global se edita con `tomlkit` para conservar los otros ajustes. La instalación pública genera los valores de las rutas en lugar de distribuir una ruta personal fija.

La estructura se inspira en PARA/CODE y en las operaciones de LLM Wiki de Karpathy. Los procedimientos de Matt son referencias y herramientas complementarias; no se distribuye su repositorio como parte de este código. La selección automática por eventos sigue en fase de propuesta.
