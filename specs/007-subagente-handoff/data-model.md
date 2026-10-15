# Data Model: Subagente y handoff

## Encargo (prompt de la herramienta `Agent`)

`id_cliente` verificado · `ultimos4` · cobros reportados (monto aproximado, fecha relativa o
exacta, comercio si se conoce).

## Línea de análisis (salida del subagente)

| Campo | Valores |
|---|---|
| reportado | descripción del cobro según el cliente |
| transacción | `TX-NNNN` o `NO_ENCONTRADA` |
| monto, fecha, país | del core |
| recomendación | `DISPUTA_AUTOMATICA` · `ESCALAR_UMBRAL` · `ESCALAR_POLITICA` · `PEDIR_DATOS` |
| motivo | texto breve |

## Evento (ampliado)

`agente`: `"principal"` o el `agent_type` del subagente. `resultado` admite además `"delegado"`.

## Caso de analista (regla nueva)

Causa `MONTO_SUPERA_UMBRAL` o `POLITICA_NO_CUBRE` ⇒ `id_cliente` y ≥ 1 `id_transaccion`.
