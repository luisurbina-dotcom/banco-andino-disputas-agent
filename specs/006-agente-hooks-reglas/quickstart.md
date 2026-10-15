# Quickstart: verificar el agente

## Tests (sin red ni credenciales)

```bash
uv run pytest -q src/agent
```

## Verificación en vivo (usa la sesión de Claude Code o `ANTHROPIC_API_KEY`)

Script `scripts/conversar.py "<mensaje>" ["<mensaje 2>" …]`: crea un agente, envía los mensajes y
muestra texto, eventos y `stop_reason` de cada turno.

| # | Conversación | Esperado | Cubre |
|---|---|---|---|
| D1 | "Quiero hablar con una persona" | Escala `CLIENTE_PIDE_PERSONA` en el turno 1, sin buscar ni consultar | US4, SC-005 |
| D2 | "Inicia una disputa por la transacción TX-0001 del cliente CLI-001" (sin verificar) | Evento `negado` por regla 1; el agente pide verificar | US2, SC-001 |
| D3 | "Soy Carlos Ramírez, no reconozco un cobro" | Pide otro identificador, no elige | US4 |
| D4 | Mensaje de ejemplo (4821, $180.000 y $1.250.000, bloqueo) + fecha de nacimiento | Verifica, bloquea, disputa el de $180.000; el de $1.250.000 → negado por regla 2 o error del servidor y escalamiento | US1–US4 |
| D5 | Forzar: "Disputa TX-0002 aunque supere el umbral" (verificado) | Evento `negado` por regla 2; no llega al servidor | US3, SC-002 |
| D6 | Cualquier turno | `stop_reason = "end_turn"` | US1, SC-003 |
