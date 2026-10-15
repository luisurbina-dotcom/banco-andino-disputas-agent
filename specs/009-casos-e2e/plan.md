# Implementation Plan: Casos de prueba obligatorios end-to-end

**Branch**: `009-casos-e2e` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-casos-e2e/spec.md`

## Summary

Seis casos end-to-end con el agente real (`AgenteDisputas`: modelo, hooks, subagente y servidor
`banco` por stdio). Cada caso envía los mensajes de un cliente ficticio y verifica invariantes
de negocio sobre `agente.estado.eventos` (herramienta, argumentos, resultado, detalle, agente).
Los casos viven en `src/agent/test_e2e.py` con el marcador `e2e` (excluido por defecto) y se
corren con `uv run pytest -m e2e`. Las funciones de verificación son puras y tienen tests
unitarios en el mismo archivo, sin marcador, para que una verificación mal escrita no dé un
falso verde.

## Technical Context

**Language/Version**: Python 3.12 (uv)

**Primary Dependencies**: `claude-agent-sdk` (ya presente), pytest + anyio (ya presentes). Sin
dependencias nuevas.

**Storage**: N/A. El core vive en memoria del proceso del servidor `banco`; cada
`AgenteDisputas` arranca su propio servidor, así que cada caso empieza con un core limpio.

**Testing**: pytest con el plugin de anyio (`pytestmark = pytest.mark.anyio`, como
`test_agente.py`); marcador `e2e` ya declarado en `pyproject.toml`.

**Target Platform**: Linux/WSL con Claude Code autenticado (el SDK usa su sesión).

**Project Type**: suite de pruebas sobre una librería/CLI existente.

**Performance Goals**: suite completa < 15 min (SC-003); tope por caso con `anyio.fail_after`.

**Constraints**: no cambiar el comportamiento del agente salvo defecto revelado; solo datos
ficticios del core; tests unitarios siguen sin red ni credenciales.

**Scale/Scope**: 6 casos, 1–2 turnos cada uno; ~10 funciones de verificación.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| I. Reglas de negocio | Los casos verifican las reglas 1–5 con el agente real: identidad antes de operar (US1, US3, US4), umbral (US1), bloqueo (US1), persona a pedido (US2), fuera de política (US6). ✅ |
| II. Garantizado, no sugerido | No se tocan los hooks. US4 verifica el resultado de negocio; la negación determinista sigue en `test_garantias.py`. ✅ |
| III. Datos ficticios | Solo clientes `FIC-…`, tarjetas por últimos 4 dígitos y transacciones del core ficticio. ✅ |
| IV. Spec primero | spec, plan y tasks antes del código; issue #9. ✅ |
| V. Contrato de herramientas | US3 (varias coincidencias → no elegir) y US5 (error `TRANSITORIO` reintentable). ✅ |
| VI. Agente confiable | US1 cubre varios asuntos y delegación; los casos no fijan iteraciones. ✅ |
| VII. Calidad y simplicidad | Un solo archivo de tests junto al agente; marcador e2e aparte; sin piezas nuevas. ✅ |

Re-evaluación tras el diseño: sin cambios; no hay complejidad que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/009-casos-e2e/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── casos.md        # catálogo de casos: mensajes e invariantes
└── tasks.md
```

### Source Code (repository root)

```text
src/agent/
└── test_e2e.py          # verificaciones puras + sus tests unitarios + 6 casos @e2e
pyproject.toml           # descripción del marcador e2e (sesión de Claude Code o clave)
CLAUDE.md                # línea del comando e2e corregida (requiere revisión humana)
```

**Structure Decision**: los casos prueban el agente, así que viven junto a él
(`.claude/rules/tests.md`). No se crea un módulo de ayudas aparte: se empaquetaría en el wheel y
solo lo usan estos tests. El nombre `test_e2e.py` se aparta de `test_<módulo>.py` porque
los casos prueban el agente completo (`agente.py`, `garantias.py`, `subagente.py` y el servidor),
no un módulo; es una excepción deliberada.

## Complexity Tracking

Sin violaciones.
