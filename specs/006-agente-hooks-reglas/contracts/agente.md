# Contrato: agente de disputas

## API

```python
async with AgenteDisputas() as agente:  # lanza CLI + servidor banco
    turno = await agente.responder("Hola, no reconozco…")
    turno.texto  # respuesta al cliente
    turno.eventos  # list[Evento] de este turno
    turno.stop_reason  # p. ej. "end_turn"
```

`AgenteDisputas(modelo=None, estado=None, fabrica_cliente=ClaudeSDKClient, prompt_sistema=None)`;
`BANCO_MODELO` puede fijar el modelo. `estado` y `fabrica_cliente` existen para pruebas;
`prompt_sistema` solo se reemplaza en pruebas (modelo que intenta saltarse las reglas).
`Turno.error` refleja `ResultMessage.is_error`.

## Hooks (`garantias.py`)

| Hook | Matcher | Función | Decide |
|---|---|---|---|
| PreToolUse | `mcp__banco__.*` | `pre_reglas(estado)` | Reglas 1 y 2; registra evento `negado` |
| PostToolUse | `mcp__banco__.*` | `post_resultado(estado)` | Verificación de sesión; registra `ok` |
| PostToolUseFailure | `mcp__banco__.*` | `post_resultado(estado)` | Registra `error`; bloqueo retira verificación |

### Motivos de negación (texto exacto)

- Regla 1: `Regla 1: verifica la identidad del cliente con verificar_identidad antes de operar sobre sus productos.`
- Regla 2 (monto): `Regla 2: la transacción supera $500.000; no se inicia automáticamente. Escala el caso con escalar_a_analista.`
- Regla 2 (desconocida): `La transacción no existe en el core; consulta las transacciones del cliente antes de disputar.`
- Producto ajeno: `Regla 1: la tarjeta o la transacción no pertenece al cliente verificado en esta conversación.`
- Fallo interno: `Garantía no disponible; la operación se niega por seguridad.`

## Opciones del SDK

`system_prompt=PROMPT_SISTEMA`, `mcp_servers={"banco": stdio con sys.executable -m mcp_server}`,
`allowed_tools` = 6 herramientas `mcp__banco__*`, `tools=[]`, `strict_mcp_config=True` (sin
conectores MCP de la cuenta), `setting_sources=[]`, `cwd` en un directorio temporal que se borra
al salir, sin `max_turns`, hooks de arriba.
