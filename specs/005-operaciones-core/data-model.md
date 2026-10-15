# Data Model: Operaciones del core

## Estado en memoria (Core)

| Estado | Estructura | Lo modifica |
|---|---|---|
| Verificados | `set[id_cliente]` | `verificar_identidad` exitosa |
| Fallas programadas | `dict[herramienta, int]` | `programar_fallas` / `BANCO_FALLAS_TRANSITORIAS` |
| Disputas | `dict[id_transaccion, Disputa]` | `iniciar_disputa` |
| Estado de tarjeta | `estado` de cada tarjeta (`activa`/`bloqueada`) | `bloquear_tarjeta` |
| Casos de analista | `list[Caso]` | `escalar_a_analista` |

## Disputa

`{id_disputa: "DSP-0001", id_transaccion, id_cliente, monto (del core), motivo, estado: "abierta"}`

## Caso de analista

```json
{"id_caso": "CASO-0001", "estado": "en_cola_analista",
 "resumen": {"causa": "MONTO_SUPERA_UMBRAL",
             "cliente": {"id_cliente": "CLI-001", "nombre": "…"} | null,
             "transacciones": [{"id_transaccion", "fecha", "monto", "comercio", "pais"}],
             "acciones_realizadas": ["…"], "descripcion": "…", "accion_recomendada": "…"}}
```

Causas: `CLIENTE_PIDE_PERSONA`, `MONTO_SUPERA_UMBRAL`, `POLITICA_NO_CUBRE`,
`IDENTIDAD_BLOQUEADA`, `OTRO`.

## Códigos de error nuevos

| Tipo | Código | Reintentable |
|---|---|---|
| TRANSITORIO | `CORE_NO_DISPONIBLE` | **sí** |
| PERMISOS | `IDENTIDAD_NO_VERIFICADA` | no |
| VALIDACION | `TARJETA_NO_ENCONTRADA`, `TRANSACCION_NO_ENCONTRADA`, `RANGO_INVALIDO`, `RESUMEN_INCOMPLETO` | no |
| NEGOCIO | `MONTO_SUPERA_UMBRAL`, `POLITICA_NO_CUBRE`, `DISPUTA_EXISTENTE` | no |

## Constantes

`UMBRAL_DISPUTA = 500_000`, `DIAS_POLITICA_EXTERIOR = 90`, `DIAS_CONSULTA_POR_DEFECTO = 30`,
`PAIS_LOCAL = "CO"`.
