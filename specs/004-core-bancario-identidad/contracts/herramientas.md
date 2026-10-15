# Contrato: herramientas del servidor MCP `banco` (parte 1)

## Servidor

- Nombre: `banco`. Transporte: stdio. Punto de entrada: `python -m mcp_server`.
- Instrucciones del servidor: "Core bancario simulado de Banco Andino con datos ficticios.
  Flujo: 1) buscar_cliente para localizar candidatos; 2) si hay más de uno, pide otro
  identificador; 3) verificar_identidad con un único cliente antes de cualquier operación sobre
  sus productos."

## `buscar_cliente`

**Descripción** (texto expuesto al modelo):

> Localiza clientes del banco por documento, nombre o últimos 4 dígitos de tarjeta. NO confirma
> la identidad: úsala solo para encontrar candidatos y luego llama a verificar_identidad con uno
> solo. Puede devolver varias coincidencias; en ese caso pide al cliente otro identificador
> (documento o últimos 4 dígitos) y no elijas tú. Una lista vacía significa que no hay
> coincidencias, no es un error.

**Entrada**

| Parámetro | Tipo | Regla |
|---|---|---|
| `criterio` | str | No vacío tras recortar espacios |
| `tipo` | `"documento"` \| `"nombre"` \| `"ultimos4"` | `ultimos4` = 4 dígitos; `documento` = `FIC-` + dígitos |

Con `tipo = "nombre"` coincide el nombre completo normalizado o todo cliente cuyo nombre contenga todas las palabras buscadas ("Carlos" devuelve a todos los Carlos).

**Salida**

```json
{"coincidencias": [{"id_cliente": "CLI-001", "nombre": "…", "tarjetas": ["4821"]}],
 "total": 1}
```

Con `total > 1` se agrega `"accion_sugerida": "Hay varias coincidencias: pide otro identificador (documento o últimos 4 dígitos); no elijas un cliente."`

**Errores**: `VALIDACION/CRITERIO_VACIO`, `VALIDACION/ULTIMOS4_INVALIDO`,
`VALIDACION/DOCUMENTO_INVALIDO`, `VALIDACION/TIPO_INVALIDO` (solo en llamadas directas al core;
por MCP el esquema ya restringe `tipo`), todos `reintentable: false`.

## `verificar_identidad`

**Descripción**:

> Confirma la identidad de UN cliente ya localizado con buscar_cliente, comparando su fecha de
> nacimiento (AAAA-MM-DD) que debe dar el propio cliente. Es obligatoria antes de consultar
> transacciones, iniciar disputas o bloquear tarjetas. No la uses para buscar clientes ni con
> datos que no haya dado el cliente. Si la respuesta es verificado=false, informa los intentos
> restantes; tras 3 fallos queda bloqueada y debes escalar a un analista.

**Entrada**: `id_cliente` (str, `CLI-NNN`), `fecha_nacimiento` (str, `AAAA-MM-DD`).

**Salida**

- Acierto: `{"verificado": true, "id_cliente": "CLI-001", "nombre": "…"}`
- Fallo: `{"verificado": false, "id_cliente": "CLI-001", "intentos_restantes": 2}`

**Errores**: `VALIDACION/CLIENTE_NO_EXISTE`, `VALIDACION/FECHA_INVALIDA` (no consume intento),
`NEGOCIO/IDENTIDAD_BLOQUEADA` ("Se agotaron los intentos de verificación. Escala el caso a un
analista."), todos `reintentable: false`.

## Formato de error (todas las herramientas)

El servidor responde con error de herramienta (`isError: true`) y como texto el JSON:

```json
{"error": {"tipo": "VALIDACION", "codigo": "ULTIMOS4_INVALIDO", "reintentable": false,
           "mensaje": "Los últimos dígitos de la tarjeta deben ser exactamente 4 números."}}
```

## Registro en `.mcp.json`

```json
"banco": {"type": "stdio", "command": "uv", "args": ["run", "python", "-m", "mcp_server"]}
```
