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

## Resultados (2026-10-15)

- `uv run pytest -q src/mcp_server` → 39 tests en 4,75 s con Python 3.12 (SC-006 ✅); repo completo 181 tests; ruff limpio.
- Hallazgo de entorno: sin `.python-version`, uv eligió Python 3.15 (`requires-python >=3.12`); se fijó 3.12 como dice el plan. Con 3.15 la suite tardaba 6,8 s y emitía un warning de `beartype`.

| # | Resultado (sesión nueva `claude -p`, solo herramientas `mcp__banco__*`) |
|---|---|
| B1 | ✅ `banco: uv run python -m mcp_server - ✔ Connected` (junto a `github`) |
| B2 | ✅ `4821` → 1 coincidencia `CLI-001` con `tarjetas: ["4821"]`, sin documento ni fecha de nacimiento |
| B3 | ✅ `carlos ramirez` → 2 coincidencias (`CLI-002`, `CLI-003`) y `accion_sugerida` |
| B4 | ✅ `FIC-99999999` → `{"coincidencias": [], "total": 0}`, sin error |
| B5 | ✅ `48` → error `VALIDACION/ULTIMOS4_INVALIDO`, `reintentable: false` |
| B6 | ✅ fallos → `intentos_restantes` 2, 1; tercer fallo y siguiente → `NEGOCIO/IDENTIDAD_BLOQUEADA` con "Escala el caso a un analista" |
