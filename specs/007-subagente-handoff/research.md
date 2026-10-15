# Research: Subagente de análisis y handoff

Verificado el 2026-10-15 con una sonda real (`claude-agent-sdk` 0.2.167).

## R1. Mecanismo de subagente

- **Decision**: `ClaudeAgentOptions(agents={"analista-transacciones": AgentDefinition(
  description, prompt=PROMPT_ANALISTA, tools=["mcp__banco__consultar_transacciones"])})`,
  `tools=["Agent"]` y `"Agent"` en `allowed_tools`.
- **Evidencia (sonda)**: el subagente solo llamó a `consultar_transacciones`; la herramienta de
  delegación aparece como `Task` en el mensaje `init` y como `Agent` en los hooks, con
  `tool_input = {description, prompt, subagent_type, run_in_background}`.
- **Contexto explícito**: el subagente no ve la conversación; recibe solo el `prompt` del encargo.
  El prompt principal exige incluir `id_cliente`, `ultimos4` y los cobros reportados.

## R2. Hooks sobre el subagente

- **Evidencia (sonda)**: el `PreToolUse` se dispara para las llamadas del subagente y la entrada
  trae `agent_id` y `agent_type = "analista-transacciones"`. Las garantías de las reglas 1 y 2 del
  #6 (matcher `mcp__banco__.*`) lo alcanzan sin cambios (FR-004).
- **Decision**: `Evento.agente` = `agent_type` o `"principal"` (FR-008).

## R3. Delegación limitada (garantía nueva)

- **Hallazgo (sonda)**: con `Agent` habilitado aparecen también los subagentes integrados
  (`general-purpose`, `Explore`, `Plan`, `claude`, `statusline-setup`).
- **Decision**: `pre_delegacion(estado)` como `PreToolUse` con matcher `Agent|Task`: niega
  cualquier `subagent_type` distinto de `analista-transacciones` y registra el evento
  `delegado`/`negado`. Además, `pre_reglas` niega a `analista-transacciones` cualquier herramienta
  que no sea `consultar_transacciones` (defensa si su definición cambia).
- **Rationale**: restringir por configuración (`AgentDefinition.tools`) y además por hook: el
  hook es determinista y no depende de cómo el SDK interprete la definición.

## R4. Formato del análisis

- **Decision**: el subagente responde con una línea por cobro reportado:
  `REPORTADO <descripción> → <id_transaccion|NO_ENCONTRADA> · <monto> · <fecha> · <país> ·
  <DISPUTA_AUTOMATICA|ESCALAR_UMBRAL|ESCALAR_POLITICA|PEDIR_DATOS> · <motivo>`.
- **Reglas de recomendación** (en su prompt): monto > 500 000 → `ESCALAR_UMBRAL`; país ≠ CO y > 90
  días → `ESCALAR_POLITICA` (prevalece); sin coincidencia o ambigua → `PEDIR_DATOS`; si no,
  `DISPUTA_AUTOMATICA`.
- **Rationale**: texto estructurado fácil de leer para el agente principal y para la interfaz; la
  recomendación es sugerencia y las acciones siguen protegidas por hooks y core.

## R5. Handoff completo (core)

- **Decision**: en `Operaciones.escalar_a_analista`, causa `MONTO_SUPERA_UMBRAL` o
  `POLITICA_NO_CUBRE` sin `id_cliente` o sin `id_transacciones` → `VALIDACION/RESUMEN_INCOMPLETO`
  ("indica el cliente y las transacciones del caso").
- **Rationale**: un analista no puede actuar sobre un monto o una política sin saber qué
  transacción es; la regla es determinista y vive donde se crea el caso.

## R6. Prompt principal

- **Decision**: agregar: delegar el análisis de cobros reportados en `analista-transacciones` con
  el encargo explícito; actuar según cada recomendación; separar asuntos (bloqueo, cada cobro) y
  una sola respuesta final; al escalar por umbral/política incluir cliente y transacciones.
