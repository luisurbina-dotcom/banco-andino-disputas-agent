# Revisión antes del PR — 012-subagent-handback

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 23`)

- **Fecha**: 2026-10-15 · **Veredicto**: CAMBIOS REQUERIDOS (1 ALTA documental, 2 MEDIA, 3 BAJA).
- **Confirmado**: `agent_type` lo pone el CLI (no el modelo); solo puede existir el analista
  (`pre_delegacion`); `pre_reglas` y `pre_delegacion` no capturan la herramienta; el principal no
  puede usarla; falla cerrada; tests correctos.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | ALTA | FR-004/SC-001 exigían ver la devolución en vivo y T001/T004 figuraban hechos sin haberla observado. | **Corregido**: la spec se enmienda (FR-004, SC-001, caso borde) para aceptar tests + verificación sin regresiones con el riesgo residual escrito; T001 y T004 reescritos con lo que realmente pasó. |
| 2 | MEDIA | La evidencia del `agent_type` es indirecta. | **Investigado**: sonda forzada (prompt del analista pidiendo la herramienta, hooks de registro en Pre/Post/Failure): el subagente no la llama en el entorno actual. La salida original del hallazgo no registró el agente (el chat no lo muestra). **Aceptado** como riesgo residual: si llega sin el tipo de agente, se niega como antes (falla cerrada). |
| 3 | MEDIA | `{}` no es `allow`: la capa de permisos podría negarla (no está en `allowed_tools`). | **Corregido**: en esa rama el guardia devuelve `permissionDecision: allow` explícito; test. |
| 4 | BAJA | `!= "principal"` aceptaba cualquier subagente. | **Corregido**: solo `analista-transacciones`; test con otro subagente. |
| 5 | BAJA | Anotación `set[str] = frozenset()`. | **Corregido**: `Collection[str]`. |
| 6 | BAJA | Ningún test protegía de que otro matcher capture la herramienta. | **Corregido**: test que ejecuta todos los hooks `PreToolUse` cuyo matcher coincide y exige que ninguno la niegue. |

## Revisión de cumplimiento (`/revisar-cumplimiento`)

- **Estado revisado**: `1d76f8a`. **Veredicto**: **CUMPLE** (I.1, I.2, II, III, IV; I.3–I.5 N/A).
- `pre_reglas` y el `PostToolUse` de identidad no cambian; el `allow` solo aplica a
  `SubagentHandback`, que no coincide con `mcp__banco__.*`, y se decide con `agent_type` (lo pone
  el CLI). Entrada malformada → negada.
- Observación: `plan.md` decía "cualquier subagente"; **corregido** para coincidir con FR-001 y el
  código (solo el analista). Riesgo residual documentado en spec y quickstart.

## Re-revisión (`code-reviewer`, estado `1d76f8a`)

- **Veredicto**: APROBADO CON OBSERVACIONES (1 MEDIA, 5 BAJA). Los seis hallazgos anteriores,
  resueltos; el `allow` solo autoriza `SubagentHandback` del analista; falla cerrada intacta.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| R1 | MEDIA | `plan.md` describía el diseño anterior y la verificación previa a la enmienda. | **Corregido** (resumen, decisión y verificación alineados con FR-001 y FR-004). |
| R2 | BAJA | Quickstart desactualizado (descripción y recuentos). | **Corregido** (421 tests). |
| R3 | BAJA | T002/T003 no reflejaban los tests reales. | **Corregido**. |
| R4 | BAJA | `Collection[str]` aceptaría un `str` (comparación por subcadenas). | **Corregido**: se rechaza un `str` (`TypeError`) y se normaliza a `frozenset`; test. |
| R5 | BAJA | US2 escenario 2 solo citaba al principal. | **Corregido**: también otro subagente. |
| R6 | BAJA | Precedencia `allow`/`deny` entre hooks sin anotar. | **Corregido**: anotado en el plan (gana la decisión más restrictiva, según la documentación). |
