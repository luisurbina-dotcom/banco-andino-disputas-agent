# Quickstart: verificar el core bancario (parte 1)

## Prerrequisitos

`uv sync` en la raíz (instala `fastmcp` y el paquete `mcp_server`).

## 1. Tests

```bash
uv run pytest -q src/mcp_server
```

Esperado: todo en verde, sin red, en < 5 s (SC-006).

## 2. Servidor desde la terminal

```bash
uv run python -m mcp_server   # queda esperando por stdio; Ctrl+C para salir
```

## 3. Verificación en vivo (Claude Code)

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| B1 | `claude mcp list` | `banco` conectado | FR-001, R8 |
| B2 | Pedir: buscar el cliente con tarjeta terminada en 4821 | 1 coincidencia, sin fecha de nacimiento | US1, FR-005 |
| B3 | Pedir: buscar a "carlos ramirez" (sin tilde) | 2 coincidencias y `accion_sugerida` | US2, SC-001 |
| B4 | Pedir: buscar el documento `FIC-99999999` | Lista vacía, sin error | FR-002, SC-002 |
| B5 | Pedir: buscar por últimos dígitos "48" | Error `VALIDACION/ULTIMOS4_INVALIDO` | US4 |
| B6 | Verificar al titular de la 4821 con fecha errónea 3 veces y luego la correcta | `intentos_restantes` 2, 1, luego `IDENTIDAD_BLOQUEADA` | US3, FR-007 |
