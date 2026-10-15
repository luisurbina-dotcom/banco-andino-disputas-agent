# Quickstart: verificar el subagente y el handoff

```bash
uv run pytest -q src/agent src/mcp_server
```

| # | Conversación (`scripts/conversar.py`) | Esperado | Cubre |
|---|---|---|---|
| E1 | Mensaje de ejemplo + "Mi fecha de nacimiento es 1988-04-12" | Evento `delegado` a `analista-transacciones`; su consulta aparece con `agente=analista-transacciones`; luego bloqueo, disputa TX-0001, TX-0002 negada/escalada con cliente y transacción; una respuesta final con los 3 asuntos | US1, US2, US3, SC-001 |
| E2 | Revisar eventos del subagente en E1 | Solo `consultar_transacciones` | SC-002 |
| E3 | Cliente verificado reporta un cobro de $45.000 del café | Disputa abierta, sin escalamiento | FR-007, SC-004 |
| E4 | (prompt de prueba) pedir delegar en `general-purpose` | `Agent` negado por la garantía de delegación | R3 |

## Resultados (2026-10-15)

- 326 tests del repo, ruff limpio, `verificar_ecosistema.sh` OK.

| # | Resultado |
|---|---|
| E1 | ✅ Mensaje de ejemplo en 2 turnos: `[delegado] analista-transacciones` con encargo explícito (CLI-001, 4821, dos cobros de ayer); `consultar_transacciones (analista-transacciones)`; luego el principal bloquea, disputa TX-0001 (DSP-0001), TX-0002 `[negado]` por regla 2 y escala `MONTO_SUPERA_UMBRAL` con cliente, transacción, acciones y recomendación; una respuesta final con los 3 asuntos |
| E2 | ✅ El subagente solo llamó `consultar_transacciones` |
| E3 | ✅ Cobro de $45.000 "en un café": el analista lo emparejó con TX-0003 y el principal abrió la disputa sin escalar |
| E4 | ✅ Modelo de prueba pidiendo delegar en `general-purpose` → `[negado] Agent` "Solo puedes delegar en el subagente analista-transacciones." |
