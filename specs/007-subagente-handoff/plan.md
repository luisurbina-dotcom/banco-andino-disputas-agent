# Implementation Plan: Subagente de análisis, varios asuntos y handoff

**Branch**: `007-subagente-handoff` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/007-subagente-handoff/spec.md`
(issue [#7](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/7))

## Summary

Se agrega al agente del #6 el subagente `analista-transacciones` (mecanismo `agents` del Agent
SDK) con un prompt propio y una sola herramienta (`consultar_transacciones`). El agente principal
lo invoca con la herramienta `Agent`, pasándole un encargo explícito. Dos garantías nuevas en
`garantias.py`: solo se puede delegar en `analista-transacciones`, y el analista solo puede
consultar. El prompt principal incorpora la delegación, la separación de asuntos y el handoff. El
core exige cliente y transacciones al escalar por umbral o política. Detalles en
[research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12. **Primary Dependencies**: `claude-agent-sdk` 0.2.x
(`AgentDefinition`, verificado con una sonda), `fastmcp` (core del #5).

**Storage**: N/A (estado en memoria del #6). **Testing**: pytest sin red (hooks, opciones,
prompts, validación del core) + verificación en vivo con `scripts/conversar.py`.

**Constraints**: el subagente no actúa; las garantías del #6 lo alcanzan; los eventos distinguen
quién llamó.

**Scale/Scope**: 1 módulo nuevo (`subagente.py`), cambios en `garantias.py`, `agente.py`,
`prompt.py` y `mcp_server/operaciones.py`.

## Constitution Check

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | El subagente recomienda según reglas 2 y 5; las acciones siguen protegidas por el #6. | ✅ |
| II. Garantizado, no sugerido | Restricciones del subagente por `AgentDefinition.tools` **y** por hook; delegación limitada por hook; handoff completo por validación del core. | ✅ |
| III. Datos ficticios | Sin datos nuevos. | ✅ |
| IV. Spec primero | Spec, plan y tareas antes del código. | ✅ |
| V. Contrato MCP | Se amplía el contrato de `escalar_a_analista` (nuevo motivo de `RESUMEN_INCOMPLETO`). | ✅ |
| VI. Agente confiable | Subagente con contexto explícito; varios asuntos con respuesta unificada; handoff autocontenido. | ✅ |
| VII. Calidad | Tests junto al código. | ✅ |

## Project Structure

```text
src/agent/
├── subagente.py          # NUEVO: NOMBRE, PROMPT_ANALISTA, definicion() -> AgentDefinition
├── test_subagente.py     # NUEVO
├── garantias.py          # + pre_delegacion; analista solo consulta; Evento.agente
├── agente.py             # + tools=["Agent"], agents={…}, hook sobre Agent
├── prompt.py             # + delegación, encargo explícito, varios asuntos, handoff
└── test_*.py             # ampliados
src/mcp_server/
├── operaciones.py        # escalar: umbral/política exigen id_cliente y transacciones
└── test_operaciones.py
specs/005-operaciones-core/contracts/herramientas.md   # nota de la ampliación
```

## Complexity Tracking

No aplica.
