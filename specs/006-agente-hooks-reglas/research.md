# Research: Agente de disputas y garantías

Verificado el 2026-10-15 con `claude-agent-sdk` 0.2.167 y una sonda real (agente mínimo + servidor
`banco` + hooks).

## R1. Autenticación

- **Decision**: el Agent SDK lanza la CLI de Claude Code y reutiliza su autenticación (sesión del
  desarrollador o `ANTHROPIC_API_KEY` en el entorno). Nada se versiona.
- **Evidencia**: la sonda funcionó sin clave de API en el entorno.

## R2. Ciclo agéntico

- **Decision**: `ClaudeSDKClient.query(mensaje)` y recorrer `receive_response()` hasta el
  `ResultMessage`. No se fija `max_turns`.
- **Rationale**: el SDK ejecuta las herramientas mientras el modelo las pide y cierra el turno
  cuando el modelo termina; el `ResultMessage` trae `stop_reason` (en la sonda, `"end_turn"`) y
  `num_turns`. El agente registra ambos en la respuesta del turno: la terminación queda
  determinada por la razón de parada, no por un contador ni por el texto (comportamiento
  obligatorio 1). `AssistantMessage.stop_reason` llega como `None` en el flujo; no se usa.
- **Alternatives considered**: bucle manual con la API de mensajes (duplica lo que el SDK ya hace
  y el enunciado pide el Agent SDK); `max_turns` (tope fijo).

## R3. Hooks y su formato

- **Decision**: `hooks={"PreToolUse": [HookMatcher("mcp__banco__.*", [pre_reglas])],
  "PostToolUse": [HookMatcher("mcp__banco__.*", [post_resultado])],
  "PostToolUseFailure": [HookMatcher("mcp__banco__.*", [post_resultado])]}`.
- **Formato** (sonda): las herramientas llegan como `mcp__banco__<nombre>` con `tool_input` dict;
  el `tool_response` del `PostToolUse` de una herramienta MCP es el **texto JSON** del resultado
  (p. ej. `'{"verificado":true,"id_cliente":"CLI-001",…}'`). Negar = devolver
  `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
  "permissionDecisionReason": motivo}}`; el modelo recibe el motivo.
- **Confirmado en vivo (sonda 2)**: un error de herramienta MCP (`isError`) dispara
  `PostToolUseFailure` y el JSON del contrato llega en el campo `error` de la entrada (no en
  `tool_response`). `post_resultado` lee `tool_response` en `PostToolUse` y `error` en
  `PostToolUseFailure`.
- **Robustez**: `post_resultado` acepta texto JSON, dict o lista de bloques de contenido; si no
  puede interpretar la respuesta de `verificar_identidad`, **no** marca la sesión (fail-closed).

## R4. Regla 1 en el agente

- **Decision**: `EstadoSesion.verificado: str | None`. `post_resultado` lo fija a `id_cliente`
  solo si la herramienta es `verificar_identidad`, la respuesta tiene `verificado is True` y su
  `id_cliente` coincide con el pedido; lo borra si la respuesta es el error
  `IDENTIDAD_BLOQUEADA`. `pre_reglas` niega `consultar_transacciones`, `iniciar_disputa` y
  `bloquear_tarjeta` si `tool_input["id_cliente"] != estado.verificado`.
- **Motivo de negación**: "Regla 1: verifica la identidad del cliente con verificar_identidad
  antes de operar sobre sus productos."

## R5. Regla 2 en el agente

- **Decision**: `EstadoSesion` carga los datos del core con `mcp_server.datos.cargar()` (solo
  lectura, misma `BANCO_FECHA_BASE` que hereda el servidor). En `iniciar_disputa`, `pre_reglas`
  busca la transacción por `id_transaccion`: inexistente → niega ("consulta las transacciones");
  monto > 500 000 → niega ("Regla 2: supera $500.000; escala con escalar_a_analista"). El
  argumento del modelo nunca aporta el monto (la herramienta ni lo recibe).
- **Rationale**: decidir con los datos del core y no con el modelo (principio II). Leer los mismos
  archivos que el servidor evita una llamada extra y no depende del estado del servidor.
- **Alternatives considered**: consultar el monto llamando al servidor desde el hook (más
  piezas, y el hook quedaría a merced de fallas transitorias).

## R6. Fail-closed

- **Decision**: cada hook envuelve su lógica; una excepción en `pre_reglas` → `deny` con
  "Garantía no disponible; se niega por seguridad"; en `post_resultado` → no marca verificado.

## R7. Aislamiento del agente

- **Decision**: `setting_sources=[]` (no carga `CLAUDE.md`, reglas ni hooks de desarrollo del
  repo), `allowed_tools` = las 6 herramientas del banco, `tools=[]` para quitar las herramientas
  integradas (lectura de archivos, shell), `strict_mcp_config=True`, `cwd` = un directorio
  temporal. **Confirmado en vivo** (mensaje `init`): `tools=[]` quita las integradas, pero sin
  `strict_mcp_config` se heredaban los conectores MCP de la cuenta (Drive, Docs); con él solo
  quedan las 6 del banco.
- **Rationale**: el agente atiende clientes; no debe heredar la configuración de desarrollo ni
  poder leer archivos del repo.

## R8. Eventos del turno

- **Decision**: los hooks registran en `EstadoSesion.eventos` cada llamada: herramienta,
  argumentos, resultado (`ok` con datos, `error` con tipo/código, o `negado` con motivo).
  `responder()` devuelve `Turno(texto, eventos_del_turno, stop_reason, num_turns)`.
- **Rationale**: la interfaz del #8 necesita mostrar disputas, bloqueos, escalamientos y
  negaciones sin leer el texto del modelo.

## R9. Prompt del sistema

- **Decision**: `prompt.py` con reglas 3–5, ambigüedad (pedir otro identificador), reintento ante
  `TRANSITORIO` (una vez), respuesta unificada y estilo breve en español. No repite como única
  defensa las reglas 1 y 2 (las menciona, pero las garantizan los hooks).

## R10. Servidor por conversación

- **Decision**: `mcp_servers={"banco": {"type": "stdio", "command": sys.executable, "args":
  ["-m", "mcp_server"]}}`.
- **Rationale**: usa el mismo intérprete del entorno (sin depender de `uv` en el PATH) y da un
  core nuevo por conversación.
