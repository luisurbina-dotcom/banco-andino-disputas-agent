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

## Re-revisión (`code-reviewer`, estado `d3220e8`)

- **Veredicto**: APROBADO CON OBSERVACIONES (sin ALTA). Hallazgos 1–11 confirmados como resueltos
  (el #7, aceptado y documentado).

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| R1 | MEDIA | Ningún test ejercitaba el manejo de señales: quitar `_ctrl_c` dejaba los tests en verde. | **Corregido**: `test_sigint_real_a_mitad_de_turno` llama a `main()` con un agente falso que se envía dos SIGINT reales durante el turno y uno durante el cierre; afirma código 0, una sola cancelación, cierre completo, resumen con el bloqueo y SIGINT restaurado a `default_int_handler`. Prueba de mutación: sin `_ctrl_c` o sin ignorar en el cierre, el test falla. |
| R2 | BAJA | Ventana del segundo SIGINT entre el fin del turno y el resumen. | **Corregido**: Ctrl+C se ignora desde el fin de la sesión (antes del resumen) hasta el fin del cierre del agente. |
| R3 | BAJA | Se pisaba un SIGINT ignorado (`SIG_IGN`) del proceso. | **Corregido**: si SIGINT está ignorado, no se toca. Un manejador propio de quien llama no aplica: `python -m chat` es el punto de entrada del proceso. |
| R4 | BAJA | Cancelación del turno y cancelación externa de la tarea principal se tratan igual. | **Aceptado**: con el manejador propio, la tarea principal solo se cancela si el loop no soporta señales (fuera de la plataforma objetivo, Linux/WSL); el resultado sigue siendo un cierre con resumen. |
| R5 | BAJA | Con Ctrl+C ignorado en el cierre, un `disconnect()` colgado no se podría cortar. | **Aceptado y documentado** en `_ignorar_ctrl_c`: el cierre del SDK está acotado (espera con límites de 5 s, luego SIGTERM y SIGKILL; `subprocess_cli.py`). |
| R6 | BAJA | `yield` dentro del `except` encadenaba excepciones. | **Corregido**: la instalación devuelve una bandera y el `yield` queda fuera. |
| R7 | BAJA | El test de turno interrumpido no afirmaba que se corta la sesión. | **Corregido**: `recibidos == ["hola"]`. |

Verificado de nuevo en vivo (pseudo-terminal): Ctrl+C en el prompt y a mitad de turno, sin traza.
386 tests, ruff limpio, `verificar_ecosistema.sh` OK.

## Revisión de cumplimiento (`/revisar-cumplimiento`)

- **Estado revisado**: `d3220e8` (las correcciones de la re-revisión solo tocan el manejo de Ctrl+C en `src/chat/app.py` y sus tests; no cambian el alcance auditado). **Veredicto**: **CUMPLE** (II, III, IV; reglas I.1–I.5 N/A).
- El diff no toca `src/agent`, `src/mcp_server` ni `data`: las reglas 1–5 siguen garantizadas por
  los hooks del #6/#7. El chat usa `AgenteDisputas` real (sin camino alternativo) y sus
  indicadores salen de `estado.eventos`, no del texto del modelo.
- Indicadores principales solo con confirmación del banco; tarjetas solo por últimos 4 dígitos;
  guion de demo con datos ficticios; bienvenida aclara que los datos son ficticios.
- Observación sin efecto en las reglas: la causa mostrada del escalamiento viene de los
  argumentos del modelo (hallazgo #7, documentado).
- Spec primero: `9b26b37` (spec) y `95c7832` (plan/tareas) preceden al código (`60557f4`).
