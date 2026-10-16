# Implementation Plan: devolución del subagente

**Branch**: `012-subagent-handback` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

## Summary

`pre_herramientas_permitidas` (`src/agent/garantias.py`) recibe un segundo conjunto,
`solo_subagentes`, con las herramientas internas que solo puede usar un subagente. `agente.py` lo
configura con `{"SubagentHandback"}`. Una llamada a esas herramientas se autoriza (`allow`
explícito) solo si la entrada del hook trae `agent_type` = `analista-transacciones`; en cualquier
otro caso, o con una entrada malformada, se niega como hasta ahora.

## Technical Context

**Language/Version**: Python 3.12 · **Primary Dependencies**: `claude-agent-sdk` (sin cambios) ·
**Testing**: pytest (`src/agent/test_garantias.py`, `test_agente.py`), verificación en vivo con
`scripts/conversar.py` y e2e · **Constraints**: no abrir ninguna otra herramienta; falla cerrada.

## Constitution Check

| Principio | Evaluación |
|---|---|
| I–II | Las reglas 1 y 2 siguen en `pre_reglas`; el cambio solo afecta al guardia de herramientas ajenas y es más estrecho que una lista abierta. ✅ |
| III | Sin datos nuevos. ✅ |
| IV | spec, plan y tasks antes del código; issue #23. ✅ |
| VI | Restituye la devolución del subagente (delegación). ✅ |
| VII | Cambio mínimo con tests. ✅ |

## Project Structure

```text
src/agent/garantias.py      # pre_herramientas_permitidas(estado, permitidas, solo_subagentes)
src/agent/agente.py         # HERRAMIENTAS_INTERNAS_SUBAGENTE = {"SubagentHandback"}
src/agent/test_garantias.py # tests del guardia
src/agent/test_agente.py    # la configuración pasa el conjunto
```

## Research

- **Decision**: permitir solo al analista (`agent_type` = `analista-transacciones`), con `allow`
  explícito porque la herramienta no está en `allowed_tools` (ajuste tras la revisión).
- **Rationale**: es la herramienta con la que un subagente entrega su resultado; el principal no
  la necesita. Si la entrada no trae `agent_type`, se trata como principal (falla cerrada).
- **Verificación** (FR-004 enmendado): tests unitarios y verificación en vivo sin regresiones; la
  llamada no se pudo observar (no se ofrece al subagente) y queda como riesgo residual escrito.
- El `allow` cuenta con la regla documentada de Claude Code: entre varios hooks `PreToolUse`, gana
  la decisión más restrictiva (un `deny` de otro hook prevalece).

## Complexity Tracking

Sin violaciones.
