# Implementation Plan: Agente de disputas — ciclo agéntico y garantías de las reglas 1 y 2

**Branch**: `006-agente-hooks-reglas` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/006-agente-hooks-reglas/spec.md`
(issue [#6](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/6))

## Summary

Paquete `agent` con el agente de disputas sobre el Claude Agent SDK (`ClaudeSDKClient`). Las
reglas 1 y 2 se garantizan con **hooks del SDK**: un `PostToolUse` sobre `verificar_identidad`
marca la sesión como verificada solo con `verificado: true`, y un `PreToolUse` sobre las
herramientas del banco niega operar sin esa verificación (regla 1) y disputar más de $500.000
con el monto leído de los datos del core (regla 2). La lógica de las garantías es pura
(`garantias.py`) y se prueba sin SDK ni red; `agente.py` solo arma las opciones y recorre los
mensajes del turno hasta el `ResultMessage`. Detalles en [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12 (uv).

**Primary Dependencies**: `claude-agent-sdk` 0.2.x (verificado en vivo: hooks, `stop_reason`,
autenticación con la sesión de Claude Code); servidor `banco` del #4/#5 (stdio).

**Storage**: estado de sesión en memoria (cliente verificado, eventos); datos del core en solo
lectura vía `mcp_server.datos.cargar` (misma fecha base que el servidor).

**Testing**: pytest. Unitarios de las garantías (funciones de hook con entradas simuladas) y de
la construcción de opciones y del recorrido de mensajes con un cliente falso. Sin red ni
credenciales. Las conversaciones reales son la verificación en vivo (y los e2e del #9).

**Target Platform**: proceso local que lanza la CLI de Claude Code (Agent SDK) y el servidor
`banco` por conversación.

**Performance Goals**: pruebas de garantías < 5 s sin contar importaciones (SC-004).

**Constraints**: garantías deterministas y fail-closed; el agente no carga la configuración de
desarrollo del repo (hooks de Claude Code, CLAUDE.md) ni tiene herramientas fuera del banco.

**Scale/Scope**: 1 paquete (`agent`), 4 módulos, ~3 archivos de test.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | Reglas 1 y 2 por hooks; 3, 4 y 5 por prompt + descripciones + errores del servidor. | ✅ |
| II. Garantizado, no sugerido | `PreToolUse` niega con estado de sesión y datos del core; `PostToolUse` es la única fuente de "verificado"; fail-closed. Cierra la condición del #5. | ✅ |
| III. Datos ficticios | Solo los datos del #4; credenciales del modelo por entorno o sesión de Claude Code. | ✅ |
| IV. Spec primero | Spec, plan y tareas antes de `src/agent/` (`spec_primero.py`). | ✅ |
| V. Contrato MCP | El agente consume las descripciones y errores del contrato; reintenta `TRANSITORIO`. | ✅ |
| VI. Agente confiable | Ciclo gobernado por `stop_reason` (sin `max_turns`); respuesta unificada; eventos para la interfaz. Subagente y handoff detallado: #7. | ✅ |
| VII. Calidad | Tests junto al código; ruff. | ✅ |

**Re-check post-diseño**: ✅.

## Project Structure

### Documentation (this feature)

```text
specs/006-agente-hooks-reglas/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/agente.md          # API del agente, hooks y motivos de negación
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml                   # + claude-agent-sdk; paquete src/agent en el wheel
src/agent/
├── CLAUDE.md                    # (existente, #1)
├── __init__.py
├── garantias.py                 # EstadoSesion + hooks puros: pre_reglas, post_resultado
├── prompt.py                    # PROMPT_SISTEMA (reglas 3–5, ambigüedad, reintentos)
├── agente.py                    # AgenteDisputas: opciones, turno, eventos
├── conftest.py
├── test_garantias.py
├── test_prompt.py
└── test_agente.py               # opciones y recorrido con cliente falso
```

**Structure Decision**: `garantias.py` no importa el SDK en tiempo de ejecución de las decisiones
(recibe dicts y devuelve dicts), así las reglas se prueban sin red. `agente.py` es la única pieza
que habla con el SDK.

## Complexity Tracking

No aplica.
