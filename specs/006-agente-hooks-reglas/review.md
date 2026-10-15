# Revisión antes del PR — 006-agente-hooks-reglas

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 6`)

- **Fecha**: 2026-10-15 · **Alcance**: `git diff main...HEAD` contra spec, contrato, data-model,
  research R1–R10 y constitución (principio II), con foco en buscar formas de saltarse las
  garantías.
- **Veredicto**: APROBADO CON OBSERVACIONES. "No encontré ninguna forma de operar sin verificar
  ni de disputar más de $500.000."
- **Confirmado**: `id_cliente`/`id_transaccion` manipulados → negado; monto siempre del core;
  verificar A y operar B → negado; otro prefijo de herramienta inalcanzable (`tools=[]` +
  `strict_mcp_config`); carreras entre hooks solo producen negaciones de más; ciclo por
  `ResultMessage` sin `max_turns`; aislamiento completo; sin datos reales.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | Retirar la verificación tras un bloqueo no era fail-closed: dependía de interpretar el JSON del error; con otro formato la sesión seguía verificada. | **Corregido**: un error ilegible de `verificar_identidad` también retira la verificación; tests con texto no JSON, envoltorio de error y `None`. |
| 2 | MEDIA | La regla 1 solo comparaba el argumento `id_cliente`; no comprobaba que la transacción o la tarjeta fueran del cliente verificado (lo frenaba solo el servidor). | **Corregido**: `EstadoSesion` carga las tarjetas del core; se niega con `MOTIVO_PRODUCTO_AJENO` si la transacción o los últimos 4 dígitos no son del cliente verificado; tests de disputa, consulta y bloqueo ajenos. |
| 3 | BAJA | `_nombre` y `tool_input` se leían fuera del `try` del `PreToolUse`. | **Corregido**: todo el cuerpo dentro del `try`; test con entrada `None` → negado. |
| 4 | BAJA | `int(monto)` truncaba (500000.9 pasaría). | **Corregido**: se exige entero; si no, fail-closed; test. |
| 5 | BAJA | Un error llegado por `PostToolUse` se registraba como `ok`. | **Corregido**: una respuesta con clave `error` se trata como error (y aplica el bloqueo); test. |
| 6 | BAJA | `mkdtemp` nunca se borraba; `BANCO_DATOS_DIR` relativo divergía entre agente y servidor. | **Corregido**: `TemporaryDirectory` limpiado en `__aexit__`; `BANCO_DATOS_DIR` a ruta absoluta; test de limpieza. |
| 7 | BAJA | Si `connect()` fallaba no se desconectaba; errores de autenticación del primer turno no se exponían. | **Corregido**: desconexión en el `except`; `Turno.error` refleja `ResultMessage.is_error`; tests. |
| 8 | BAJA | Faltaba la regla 5 general y qué hacer ante fraude sin verificar. | **Corregido** en el prompt con su test. |
| 9 | BAJA | Los tests del prompt solo buscan frases. | **Aceptado**: la cobertura de comportamiento es la verificación en vivo (D1–D6) y los e2e del #9. |
| 10 | BAJA | Contrato, R7 y T002 desactualizados. | **Corregido**. |

## Revisión de cumplimiento (`/revisar-cumplimiento`, fork con `compliance-auditor`)

- **Fecha**: 2026-10-15 · **Estado revisado**: `53f281b`. **Veredicto**: **CUMPLE**.

| Principio/Regla | Resultado | Evidencia (resumen del auditor) |
|---|---|---|
| I.1 Identidad primero | CUMPLE | Herramientas protegidas; niega sin verificado o con otro `id_cliente`; pertenencia de transacción/tarjeta con datos del core. |
| I.2 Umbral $500.000 | CUMPLE | Monto del core por `id_transaccion`; `monto` inventado ignorado; 500 000 exactos permitidos; transacción desconocida negada. |
| I.3 Bloqueo inmediato | CUMPLE | Prompt (sin confirmación, verificar primero) + descripción de la herramienta + hook de identidad. |
| I.4 Persona a pedido | CUMPLE | Prompt + verificación en vivo D1. |
| I.5 Fuera de política | CUMPLE | Prompt (código y caso general) + descripción. |
| **II. Garantizado, no sugerido** | **CUMPLE** | Hooks `PreToolUse`/`PostToolUse`/`PostToolUseFailure` registrados; verificado solo por `PostToolUse` exitoso del mismo cliente; bloqueo o error ilegible lo retiran; fail-closed; aislamiento (`tools=[]`, `strict_mcp_config`, `setting_sources=[]`). El prompt no es lo que impone las reglas. |
| III. Datos ficticios | CUMPLE | Sin secuencias de 6+ dígitos ni patrones de credenciales en el diff. |
| IV. Spec primero | CUMPLE | spec, plan, tasks y review presentes; ligada al #6. |

Observación menor (data-model sin `EstadoSesion.tarjetas`): **corregida**.

**Condición heredada del #5 (principio II en CUMPLE): satisfecha.**
