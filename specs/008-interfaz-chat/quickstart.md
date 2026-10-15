# Quickstart: interfaz de chat

```bash
uv run pytest -q src/chat
uv run python -m chat                                        # interactivo; /salir para terminar
uv run python -m chat --guion specs/008-interfaz-chat/guiones/ejemplo.txt
BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1 uv run python -m chat --guion <archivo>
```

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| F1 | `python -m chat` y `/salir` | Bienvenida (datos ficticios, cómo salir) y resumen vacío | US1 |
| F2 | Guion de ejemplo (mensaje + fecha) | Turnos diferenciados; 🔒, 📄, ⛔ (regla 2) y 👤 visibles en el turno 2; resumen con 3 acciones + 1 negación | US1, US2, SC-001 |
| F3 | Guion con falla transitoria | 🔁 seguido de 📋 | US3 |
| F4 | Sin Claude Code disponible (simulado en test) | Mensaje claro, sin traza | FR-008 |
| F5 | Ctrl+C en el prompt y a mitad de un turno (terminal real) | "Conversación interrumpida", resumen con lo hecho (incluido el turno cortado), sin traza | FR-006 |

## Resultados (2026-10-15)

- 45 tests en `src/chat` (386 en el repo) tras la revisión, ruff limpio, `verificar_ecosistema.sh` OK.

| # | Resultado |
|---|---|
| F1 | ✅ Bienvenida con "datos ficticios" y "/salir"; resumen al terminar (cubierto también por tests) |
| F2 | ✅ Guion de ejemplo: turno 1 `🔎 Búsqueda` + pedido de fecha; turno 2 `✅ Identidad verificada`, recuadros `🔒 TARJETA BLOQUEADA •••• 4821`, `🤝 Análisis delegado`, `📋 Consulta (analista-transacciones)`, `📄 DISPUTA ABIERTA DSP-0001 · TX-0001 · $180.000`, `👤 ESCALADO A ANALISTA CASO-0001 · MONTO_SUPERA_UMBRAL`; resumen con las 3 acciones. En esta corrida el agente siguió la recomendación `ESCALAR_UMBRAL` del analista y no intentó disputar el cobro alto (no hubo `⛔ NEGADO`; ese indicador se ve en los casos forzados y está cubierto por tests) |
| F3 | ✅ Con `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1`: `🔁 Falla transitoria del banco · reintentable` (texto actualizado tras la revisión) y luego `📋 Consulta de transacciones: 3` |
| F4 | ✅ Cubierto por test: sin agente disponible → mensaje claro y código 1, sin traza |
| F5 | ✅ Tras la revisión: Ctrl+C real (pseudo-terminal) en el prompt y a los 4 s de un turno → "Conversación interrumpida" y resumen, sin traza; con el guion cortado a los 15 s el resumen incluye `TARJETA BLOQUEADA` del turno interrumpido. Guion completo sin cambios; `--guion` inexistente → mensaje claro y código 2 |

Ajustes tras ver la demo: la respuesta del agente se renderiza como Markdown (antes se veían los
`**`) y "1 coincidencia" en singular.
