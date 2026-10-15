# Implementation Plan: Core bancario simulado — datos ficticios e identificación del cliente

**Branch**: `004-core-bancario-identidad` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-core-bancario-identidad/spec.md`
(issue [#4](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/4))

## Summary

Servidor MCP `banco` (FastMCP, stdio) con dos herramientas, `buscar_cliente` y
`verificar_identidad`, sobre un core en memoria cargado desde JSON ficticio. La lógica de
negocio vive en un módulo puro (`core.py`) que se prueba sin MCP; el servidor (`servidor.py`)
solo traduce entre herramientas y core, y convierte los errores al contrato estructurado. Las
fechas de las transacciones se guardan como "días atrás" y se resuelven contra el día de
ejecución (o `BANCO_FECHA_BASE` en pruebas). Detalles en [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12 (uv).

**Primary Dependencies**: `fastmcp` 4.x (sobre `mcp` 2.x). Desarrollo: pytest (+ plugin anyio que
trae `mcp`), ruff.

**Storage**: archivos JSON en `data/` (clientes, tarjetas, transacciones); estado de intentos en
memoria.

**Testing**: pytest. Unitarios del core (puro) y del servidor con el cliente en memoria de
FastMCP (sin procesos ni red).

**Target Platform**: proceso stdio lanzado por Claude Code (`.mcp.json`) y por el agente (#6).

**Project Type**: servidor MCP (biblioteca + punto de entrada `python -m mcp_server`).

**Performance Goals**: cada herramienta responde en < 100 ms con los datos del MVP; suite < 5 s.

**Constraints**: datos 100% ficticios (hook `datos_ficticios` activo); la búsqueda nunca expone la
fecha de nacimiento; contrato de errores del principio V.

**Scale/Scope**: ~8 clientes, ~10 tarjetas, ~20 transacciones; 2 herramientas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | Prepara la regla 1: `verificar_identidad` es la única fuente de "identidad verificada". Los datos incluyen los casos de las reglas 2 y 5 para el #5. | ✅ |
| II. Garantizado, no sugerido | El bloqueo tras 3 intentos y la no exposición del dato de verificación los decide el core, no el modelo. La regla 1 se garantiza en el hook del agente (#6). | ✅ |
| III. Datos ficticios | Tarjetas por últimos 4 dígitos, documentos `FIC-…`, fechas de nacimiento ficticias; el hook de datos ficticios valida cada escritura. | ✅ |
| IV. Spec primero | Spec, plan y tareas antes de tocar `src/` y `data/` (lo exige `spec_primero.py`). | ✅ |
| V. Contrato MCP | Descripciones con cuándo usar/no usar; errores con tipo, código, reintentable y mensaje; búsqueda vacía = lista vacía. | ✅ |
| VII. Calidad | Tests junto al código (`src/mcp_server/test_*.py`); ruff. | ✅ |

**Re-check post-diseño**: ✅ sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/004-core-bancario-identidad/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/herramientas.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml                 # + fastmcp; build hatchling con paquete src/mcp_server
.mcp.json                      # + servidor "banco" (stdio)
.claude/settings.json          # + "banco" en enabledMcpjsonServers (aprobación)
data/
├── clientes.json
├── tarjetas.json
└── transacciones.json         # fechas como dias_atras
src/mcp_server/
├── __init__.py
├── __main__.py                # python -m mcp_server → servidor.main()
├── errores.py                 # ErrorCore + forma del contrato
├── datos.py                   # carga JSON, resuelve fechas contra la fecha base
├── core.py                    # Core: buscar_cliente, verificar_identidad (puro)
├── servidor.py                # FastMCP "banco": herramientas, descripciones, instrucciones
├── conftest.py                # core con fecha base fija
├── test_errores.py
├── test_datos.py
├── test_core.py
└── test_servidor.py           # cliente en memoria de FastMCP
```

**Structure Decision**: paquete `mcp_server` instalable (layout `src/`) para que el agente del #6
y Claude Code lo lancen con `python -m mcp_server`. Separar `core.py` de `servidor.py` permite
probar las reglas sin el protocolo y que el #5 agregue herramientas sin tocar la lógica de
identificación.

## Complexity Tracking

No aplica.
