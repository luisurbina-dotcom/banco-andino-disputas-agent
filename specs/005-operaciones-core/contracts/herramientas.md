# Contrato: herramientas del servidor MCP `banco` (parte 2)

Errores con el formato del contrato del #4 (`{"error": {tipo, codigo, reintentable, mensaje}}`
como error de herramienta). Las cuatro herramientas de esta parte (no `buscar_cliente` ni `verificar_identidad`) pueden
responder `TRANSITORIO/CORE_NO_DISPONIBLE` (`reintentable: true`) si hay fallas programadas.

## `consultar_transacciones`

**Descripción**:

> Lista las transacciones de una tarjeta del cliente en un rango de fechas (AAAA-MM-DD; por
> defecto los últimos 30 días). Requiere que el cliente haya pasado verificar_identidad; no la
> uses con clientes sin verificar ni si el cliente solo pidió hablar con una persona. Úsala para
> encontrar los cobros que el cliente no reconoce antes de disputarlos. Una lista vacía no es un
> error. Si recibes un error TRANSITORIO, reintenta la llamada.

**Entrada**: `id_cliente`, `ultimos4`, `desde` (opcional), `hasta` (opcional).

**Salida**: `{"fecha_base", "transacciones": [{"id_transaccion", "fecha", "antiguedad_dias",
"monto", "comercio", "pais"}], "total": n}`. `fecha_base` y `antiguedad_dias` se agregaron en el
#7 para que el analista evalúe la política de 90 días sin conocer la fecha del core.

**Errores**: `PERMISOS/IDENTIDAD_NO_VERIFICADA`, `VALIDACION/TARJETA_NO_ENCONTRADA`,
`VALIDACION/RANGO_INVALIDO`.

## `iniciar_disputa`

**Descripción**:

> Abre una disputa sobre una transacción del cliente verificado. El core aplica la política:
> hasta $500.000 la disputa se abre; si responde MONTO_SUPERA_UMBRAL o POLITICA_NO_CUBRE, no la
> reintentes: escala el caso con escalar_a_analista. Si responde DISPUTA_EXISTENTE, informa al
> cliente que ya hay una disputa en curso. No la uses si el cliente pidió hablar con una persona.

**Entrada**: `id_cliente`, `id_transaccion`, `motivo`.

**Salida**: `{"id_disputa", "estado": "abierta", "id_transaccion", "monto"}`

**Errores**: `PERMISOS/IDENTIDAD_NO_VERIFICADA`, `VALIDACION/TRANSACCION_NO_ENCONTRADA`,
`NEGOCIO/DISPUTA_EXISTENTE`, `NEGOCIO/POLITICA_NO_CUBRE`, `NEGOCIO/MONTO_SUPERA_UMBRAL`.

## `bloquear_tarjeta`

**Descripción**:

> Bloquea de inmediato una tarjeta del cliente verificado por sospecha de fraude; no requiere
> aprobación adicional. Si la tarjeta ya estaba bloqueada, lo indica sin error. Úsala cuando el
> cliente sospeche clonación, robo o pérdida; no la uses si el cliente no lo pidió ni expresó
> sospecha de fraude.

**Entrada**: `id_cliente`, `ultimos4`, `motivo`.

**Salida**: `{"bloqueada": true, "ultimos4", "ya_estaba_bloqueada": bool}`

**Errores**: `PERMISOS/IDENTIDAD_NO_VERIFICADA`, `VALIDACION/TARJETA_NO_ENCONTRADA`.

## `escalar_a_analista`

**Descripción**:

> Pasa el caso a un analista humano, que NO ve la conversación. Úsala de inmediato si el cliente
> pide hablar con una persona (sin verificar ni investigar antes), y cuando una disputa responda
> MONTO_SUPERA_UMBRAL o POLITICA_NO_CUBRE, o la identidad quede bloqueada. Envía la causa, los
> ids de las transacciones involucradas (si incluyes transacciones, indica también el
> id_cliente), lo que ya hiciste y una acción recomendada; el core completa montos y fechas.

**Entrada**: `causa` (`CLIENTE_PIDE_PERSONA` | `MONTO_SUPERA_UMBRAL` | `POLITICA_NO_CUBRE` |
`IDENTIDAD_BLOQUEADA` | `OTRO`), `descripcion`, `accion_recomendada`, `id_cliente` (opcional),
`id_transacciones` (lista, opcional), `acciones_realizadas` (lista, opcional).

**Salida**: `{"id_caso", "estado": "en_cola_analista", "transacciones_incluidas": n}`. El
resumen completo (data-model § Caso) queda en el core para el analista y no se devuelve al
modelo, para no abrir una vía de lectura de datos sin identidad verificada.

**Errores**: `VALIDACION/RESUMEN_INCOMPLETO` (descripción o acción recomendada vacías, o causa
fuera de las 5 en llamadas directas al core; por MCP la restringe el esquema),
`VALIDACION/TRANSACCION_NO_ENCONTRADA` (inexistente o de otro cliente),
`VALIDACION/CLIENTE_NO_EXISTE`. Incluir transacciones exige `id_cliente`. Ampliación del #7:
las causas `MONTO_SUPERA_UMBRAL` y `POLITICA_NO_CUBRE` exigen `id_cliente` y al menos una
transacción (si no, `RESUMEN_INCOMPLETO`).

## Configuración

`BANCO_FALLAS_TRANSITORIAS="consultar_transacciones:1"` al arrancar el servidor programa una falla
en la primera consulta.
