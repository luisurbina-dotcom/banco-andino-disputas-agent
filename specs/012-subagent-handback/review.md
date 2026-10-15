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
