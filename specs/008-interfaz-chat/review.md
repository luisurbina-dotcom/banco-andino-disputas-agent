# Revisión antes del PR — 008-interfaz-chat

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 8`)

- **Fecha**: 2026-10-15 · **Veredicto**: CAMBIOS REQUERIDOS (1 ALTA, 3 MEDIA, 7 BAJA).
- **Confirmado**: los indicadores salen de los eventos y no del texto del modelo; la interfaz no
  toca las garantías del agente; tests sin red ni credenciales; sin datos reales.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | ALTA | Ctrl+C no era ordenado: en 3.12 `asyncio.run` lo convierte en `CancelledError` de la tarea principal, que no se capturaba; no salía el resumen y aparecía una traza. | **Corregido**: en el prompt, Ctrl+C lanza `KeyboardInterrupt` dentro de `input()`; durante un turno cancela solo la tarea del turno; durante el cierre del agente se ignora. Esto evita que el segundo SIGINT (con `uv run` la señal llega dos veces) corte la desconexión del SDK. El resumen suma los eventos del turno interrumpido desde `agente.estado.eventos`. Tests de ambos casos; verificado con Ctrl+C real en una pseudo-terminal (F5). |
| 2 | MEDIA | `mensaje_cliente` interpretaba el texto como marcado de Rich (`[/b]` rompía la app). | **Corregido**: `Text(texto)`; test con corchetes. |
| 3 | MEDIA | Se ignoraba `Turno.error` y las excepciones del SDK a mitad de sesión salían con traza. | **Corregido**: aviso del sistema y fin de la sesión con resumen; se capturan las excepciones `ClaudeSDKError` (incluye `ProcessError` y `CLIConnectionError`). Tests. |
| 4 | MEDIA | Los indicadores principales no comprobaban la confirmación del banco. | **Corregido**: exigen `bloqueada is True`, `id_disputa` o `id_caso`; si no, "❔ Resultado no confirmado" (secundario). Resultados distintos de `ok` no se afirman. Tests. |
| 5 | BAJA | "se reintenta" afirmaba un reintento que la interfaz no ve. | **Corregido**: "reintentable". |
| 6 | BAJA | Error sin código: "El banco rechazó · None". | **Corregido**: "Error sin detalle"; test. |
| 7 | BAJA | La causa del escalamiento sale de los argumentos del modelo. | **Aceptado y documentado** en `research.md` (R2): es informativa; el caso sale de la respuesta del banco. |
| 8 | BAJA | Markdown con hipervínculos; aclarar qué refleja acciones reales. | **Corregido**: `hyperlinks=False`; la bienvenida dice que solo los recuadros de color muestran acciones reales. |
| 9 | BAJA | `--guion` inexistente salía con traza. | **Corregido**: mensaje claro y código 2; test y verificación en vivo. |
| 10 | BAJA | Tests: stdout en lugar de stderr para la traza; faltaban EOF, Ctrl+C, monto no numérico y negaciones de `Agent`/desconocida. | **Corregido**: todos agregados (44 tests en `src/chat`). |
| 11 | BAJA | `rich` sin cota superior. | **Corregido**: `rich>=13,<16` (instalada 15.0.0). |
