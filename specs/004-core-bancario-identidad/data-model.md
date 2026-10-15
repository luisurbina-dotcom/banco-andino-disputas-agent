# Data Model: Core bancario simulado

## Cliente (`data/clientes.json`)

| Campo | Tipo | Regla |
|---|---|---|
| `id_cliente` | str | `CLI-NNN`, único |
| `nombre` | str | Nombre completo genérico |
| `documento` | str | `FIC-` + 8 dígitos, único |
| `fecha_nacimiento` | str | `AAAA-MM-DD`, ficticia. **Dato de verificación: nunca se expone en la búsqueda** |

## Tarjeta (`data/tarjetas.json`)

| Campo | Tipo | Regla |
|---|---|---|
| `id_tarjeta` | str | `TAR-NNN`, único |
| `id_cliente` | str | Referencia a Cliente |
| `ultimos4` | str | Exactamente 4 dígitos. **Nunca el número completo** |
| `estado` | str | `activa` \| `bloqueada` (la usa `bloquear_tarjeta` en #5) |

## Transacción (`data/transacciones.json`)

| Campo | Tipo | Regla |
|---|---|---|
| `id_transaccion` | str | `TX-NNNN`, único |
| `id_tarjeta` | str | Referencia a Tarjeta |
| `dias_atras` | int ≥ 0 | Se resuelve a `fecha` = fecha base − `dias_atras` |
| `monto` | int | COP ficticios, > 0 |
| `comercio` | str | Nombre ficticio |
| `pais` | str | Código ISO-3166 alfa-2 (`CO` = nacional) |

### Casos obligatorios en los datos

| Caso | Datos |
|---|---|
| Mensaje de ejemplo | Cliente titular de la tarjeta `4821` con dos transacciones `dias_atras = 1`: $180.000 y $1.250.000 |
| Homónimos | Dos clientes con nombre "Carlos Ramírez" y documentos distintos |
| Fuera de política | Transacción de comercio con `pais ≠ CO` y `dias_atras = 120` |
| Disputa automática | Transacciones ≤ $500.000 recientes |
| Varias tarjetas | Un cliente con dos tarjetas (aparece una vez en la búsqueda) |

## Coincidencia (salida de `buscar_cliente`)

`{id_cliente, nombre, tarjetas: ["4821", …]}` — sin documento completo ni fecha de nacimiento.

## Estado de verificación (memoria)

`intentos_fallidos[id_cliente] → int`. 3 → bloqueado. Un acierto lo reinicia a 0. Se pierde al
reiniciar el servidor.

## ErrorCore

| Campo | Valores |
|---|---|
| `tipo` | `TRANSITORIO`, `VALIDACION`, `NEGOCIO`, `PERMISOS` |
| `codigo` | `CRITERIO_VACIO`, `TIPO_INVALIDO`, `ULTIMOS4_INVALIDO`, `DOCUMENTO_INVALIDO`, `CLIENTE_NO_EXISTE`, `FECHA_INVALIDA`, `IDENTIDAD_BLOQUEADA` |
| `reintentable` | bool (todos `false` en esta feature; `TRANSITORIO` llega en #5) |
| `mensaje` | Texto accionable en español |
