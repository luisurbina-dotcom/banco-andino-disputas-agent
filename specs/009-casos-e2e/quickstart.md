# Quickstart: casos end-to-end

Requisito: Claude Code instalado y autenticado (el agente usa su sesión). Alternativa:
`ANTHROPIC_API_KEY` en el entorno.

```bash
uv run pytest -m e2e -v                       # los seis casos (C1–C6, contracts/casos.md)
uv run pytest -m e2e -v -k persona            # un caso
uv run pytest -q                              # unitarios: no corren los e2e
```

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| Q1 | `uv run pytest -q` | Unitarios en verde, incluidos los de las verificaciones; 0 casos e2e ejecutados | FR-007, SC-005 |
| Q2 | `uv run pytest -m e2e -v` | 6 casos en verde en < 15 min | SC-001, SC-003 |
| Q3 | Repetir Q2 | 6 casos en verde otra vez | SC-004 |
| Q4 | Caso que falla (forzado en local) | Se ve la secuencia de eventos del caso | FR-009 |
| Q5 | Sin Claude Code disponible (simulado) | Casos omitidos con motivo, sin traza | FR-008 |
