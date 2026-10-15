# Data Model: Agente de disputas

## EstadoSesion (memoria, una por conversación)

| Campo | Tipo | Regla |
|---|---|---|
| `verificado` | `str \| None` | `id_cliente` verificado; solo lo fija `post_resultado` con `verificado is True` |
| `transacciones` | `dict[id_transaccion, dict]` | Datos del core en solo lectura (monto, tarjeta) |
| `eventos` | `list[Evento]` | Todas las llamadas de la conversación |

## Evento

| Campo | Valores |
|---|---|
| `herramienta` | nombre corto (`iniciar_disputa`, …) |
| `argumentos` | `dict` del `tool_input` |
| `resultado` | `"ok"` \| `"error"` \| `"negado"` |
| `detalle` | datos (ok), `{tipo, codigo}` (error) o motivo (negado) |

## Turno (salida de `responder`)

`{texto: str, eventos: list[Evento], stop_reason: str | None, num_turns: int}`

## Herramientas protegidas

| Herramienta | Regla 1 | Regla 2 |
|---|---|---|
| `consultar_transacciones` | ✓ | |
| `iniciar_disputa` | ✓ | ✓ |
| `bloquear_tarjeta` | ✓ | |
| `buscar_cliente`, `verificar_identidad`, `escalar_a_analista` | — | — |
