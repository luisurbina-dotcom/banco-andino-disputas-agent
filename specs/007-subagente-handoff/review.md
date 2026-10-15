# Revisión antes del PR — 007-subagente-handoff

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 7`)

- **Fecha**: 2026-10-15 · **Veredicto**: APROBADO CON OBSERVACIONES (sin ALTA).
- **Confirmado**: las reglas 1 y 2 alcanzan al subagente; `pre_reglas` le niega todo salvo
  `consultar_transacciones`; `pre_delegacion` es fail-closed y solo admite `analista-transacciones`;
  FR-006 en el core; orden de recomendación coherente con las reglas 2 y 5; sin datos reales.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | El subagente no conocía la fecha base del core: `ESCALAR_POLITICA` (> 90 días) era frágil con una fecha base distinta de hoy. | **Corregido**: `consultar_transacciones` devuelve `fecha_base` y `antiguedad_dias` por transacción (contrato 005 ampliado); el prompt del analista los usa y consulta 120 días atrás para cobros antiguos. Tests del core y del prompt. |
| 2 | BAJA | La restricción "solo consultar" comparaba un único `agent_type`. | **Corregido**: lista permitida: cualquier subagente solo puede `consultar_transacciones`; test con otro `agent_type`. |
| 3 | BAJA | Herramientas integradas (si una definición las incluyera) no estaban vigiladas por hooks. | **Corregido**: nuevo `PreToolUse` sin matcher (`pre_herramientas_permitidas`) que niega cualquier herramienta fuera de las 6 del banco y la delegación, la llame quien la llame; tests con Bash, Read, WebFetch y otro MCP; verificado en vivo sin regresión. |
| 4 | BAJA | El evento de delegación registraba siempre `principal` y `Agent`. | **Corregido**: usa `agent_type` y el nombre real (`Task`/`Agent`); test. |
| 5 | BAJA | Contradicciones del prompt ("solo herramientas del banco"; disputar todo cobro). | **Corregido**: menciona la delegación y disputa según la recomendación del analista. |
| 6 | BAJA | Tests del prompt poco precisos. | **Corregido**: verifican el encargo, el mapeo recomendación → acción y la exigencia de umbral/política. |
| 7 | BAJA | Test de opciones debilitado. | **Corregido**: igualdad de `allowed_tools`, hooks concretos y conteo de matchers. |
| 8 | BAJA | Sin tests fail-closed de `pre_delegacion`. | **Corregido**: `None`, `tool_input` no dict, sin `subagent_type`, `Task`. El test con `None` detectó un fallo real (`_nombre` sin protección) que se corrigió. |

## Revisión de cumplimiento (`/revisar-cumplimiento`)

- **Estado revisado**: `c700ed9`. **Veredicto**: **CUMPLE** (I.1–I.5, II, III, IV).
- Reglas 1 y 2: hooks del #6 alcanzan al subagente; el subagente solo consulta; el servidor repite
  los controles; escalar por umbral exige cliente y transacciones.
- Reglas 3–5: prompt + core (`POLITICA_NO_CUBRE`); el analista usa `fecha_base` y
  `antiguedad_dias` del core.
- II: dos hooks nuevos (`pre_delegacion`, `pre_herramientas_permitidas`), fail-closed,
  justificados en research R3 y en esta revisión.

## Re-revisión del commit de correcciones (`code-reviewer`)

- **Alcance**: `c700ed9`. **Veredicto**: APROBADO CON OBSERVACIONES; los 8 hallazgos corregidos,
  sin regresiones; la guardia no niega nada del flujo normal.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 9 | BAJA | La guardia de herramientas negaba sin registrar evento. | **Corregido**: registra `negado` con herramienta y agente; test. |
| 10 | BAJA | El test no ejercitaba la guardia real sobre el flujo normal. | **Corregido**: la guardia de `construir_opciones` deja pasar las 6 herramientas, `Agent` y `Task`. |
| 11 | BAJA | data-model 005 § Caso sin `antiguedad_dias`. | **Corregido**. |
| 12 | BAJA | Un subagente con delegación podría delegar de nuevo. | **Corregido**: solo el agente principal delega; test. |

## Compuerta de `/abrir-pr`

Sin hallazgos ALTA pendientes y cumplimiento **CUMPLE** → se abre el PR.
