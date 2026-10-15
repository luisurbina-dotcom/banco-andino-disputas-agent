# Implementation Plan: Operaciones del core

**Branch**: `005-operaciones-core` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-operaciones-core/spec.md`
(issue [#5](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/5))

## Summary

Se amplía el servidor `banco` del #4 con cuatro herramientas (`consultar_transacciones`,
`iniciar_disputa`, `bloquear_tarjeta`, `escalar_a_analista`) y un mecanismo de fallas
transitorias programables. La lógica nueva vive en `operaciones.py` (clase `Operaciones` que
comparte el estado del `Core`); `core.py` gana el registro de clientes verificados y las fallas
programadas. El servidor sigue siendo una capa delgada. Detalles en [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12 (uv). **Primary Dependencies**: `fastmcp` 4.x (ya instalado).

**Storage**: `data/*.json` (lectura); disputas, bloqueos, casos, verificados y fallas en memoria.

**Testing**: pytest; unitarios de `Operaciones` sin MCP y del servidor con el cliente en memoria.

**Target Platform**: proceso stdio (`python -m mcp_server`).

**Performance Goals**: suite de `src/mcp_server` < 5 s (SC-006).

**Constraints**: monto de la regla 2 leído del core (FR-004); solo `TRANSITORIO` reintentable;
datos ficticios; el agente no se conecta a estas herramientas hasta el #6.

**Scale/Scope**: 4 herramientas nuevas (6 en total), ~6 códigos de error nuevos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | Regla 2 (umbral con monto del core), regla 3 (bloqueo inmediato), regla 4 (escalar sin verificación), regla 5 (`POLITICA_NO_CUBRE`). Regla 1: defensa en profundidad con `PERMISOS`. | ✅ |
| II. Garantizado, no sugerido | El servidor rechaza por datos del core, no por argumentos del modelo. La garantía exigida (hooks del SDK) llega en el #6; hasta entonces el agente no usa estas herramientas. | ✅ |
| III. Datos ficticios | Solo usa los datos del #4; el resumen al analista se enriquece con montos del core. | ✅ |
| IV. Spec primero | Spec, plan y tareas antes del código (`spec_primero.py`). | ✅ |
| V. Contrato MCP | 4 categorías de error con el contrato del #4; descripciones con qué hacer ante cada error de negocio. | ✅ |
| VI. Agente confiable | Prepara el handoff autocontenido (causa, transacciones con monto, acciones, recomendación). | ✅ |
| VII. Calidad | Tests junto al código; ruff. | ✅ |

**Re-check post-diseño**: ✅ sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/005-operaciones-core/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/herramientas.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/mcp_server/
├── core.py               # + verificados, fallas programadas (programar_fallas, consumir_falla)
├── operaciones.py        # NUEVO: Operaciones(core): consultar, disputar, bloquear, escalar
├── servidor.py           # + 4 herramientas, BANCO_FALLAS_TRANSITORIAS al arrancar
├── test_operaciones.py   # NUEVO
├── test_core.py          # + verificados y fallas
└── test_servidor.py      # 6 herramientas, descripciones exactas de ambos contratos
```

**Structure Decision**: un módulo nuevo `operaciones.py` mantiene `core.py` enfocado en
identificación y estado compartido. El servidor solo registra herramientas y traduce errores.

## Complexity Tracking

No aplica.
