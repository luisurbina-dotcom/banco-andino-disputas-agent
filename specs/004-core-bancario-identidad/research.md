# Research: Core bancario simulado e identificación

## R1. Biblioteca del servidor MCP

- **Decision**: paquete `fastmcp` 4.x (`from fastmcp import FastMCP`).
- **Rationale**: verificado el 2026-10-15: el SDK oficial `mcp` está en 2.3.0 y ahí `FastMCP` pasó
  a llamarse `MCPServer` (`mcp.server.fastmcp` ya no existe). `fastmcp` 4.1.0 mantiene la API
  FastMCP sobre `mcp` 2.x, convive con `claude-agent-sdk` 0.2.167 y trae un cliente en memoria
  (`fastmcp.Client(servidor)`) que permite probar las herramientas sin procesos ni red. Una
  herramienta que devuelve `dict` produce contenido estructurado (`structured_content`).
- **Alternatives considered**: `mcp<2` con `mcp.server.fastmcp` (fija una versión vieja del SDK);
  `mcp` 2.x con `MCPServer` (la constitución y el enunciado nombran FastMCP; API menos probada).

## R2. Forma de los errores

- **Decision**: el core lanza `ErrorCore(tipo, codigo, mensaje, reintentable)`; el servidor lo
  convierte en un error de herramienta (`ToolError`) cuyo texto es el JSON
  `{"error": {"tipo", "codigo", "reintentable", "mensaje"}}`. Resultados que no son errores
  (lista vacía, "no verificado") se devuelven como datos normales.
- **Rationale**: marcar la respuesta como error (`isError`) le dice al modelo que la llamada
  falló, y el JSON le da la categoría y si puede reintentar (principio V). Un "no verificado" no
  es un fallo de la herramienta: es la respuesta correcta a un dato equivocado.
- **Alternatives considered**: devolver `{"error": …}` como resultado exitoso (el modelo puede
  tomarlo como éxito); mensajes de texto libres (sin categoría ni reintentable).

## R3. Búsqueda con tipo explícito

- **Decision**: `buscar_cliente(criterio, tipo)` con `tipo ∈ {documento, nombre, ultimos4}`.
- **Rationale**: un "4821" puede ser últimos 4 dígitos o parte de un documento; adivinar el tipo
  introduce ambigüedad. Con `tipo` explícito, la descripción enseña al modelo qué enviar y la
  validación es simple (`ultimos4` = exactamente 4 dígitos; `documento` = `FIC-` + dígitos).
- **Normalización**: nombre sin tildes, minúsculas y espacios colapsados; coincidencia por
  igualdad del nombre completo normalizado o por contener todas las palabras buscadas.

## R4. Ambigüedad explícita en la respuesta

- **Decision**: la respuesta incluye `total` y, si `total > 1`, `accion_sugerida` con el texto
  "Hay varias coincidencias: pide otro identificador (documento o últimos 4 dígitos); no elijas
  un cliente."
- **Rationale**: refuerza en el dato lo que la descripción pide (principio V); el agente no
  tiene que inferirlo.

## R5. Verificación e intentos

- **Decision**: `verificar_identidad(id_cliente, fecha_nacimiento)`. Acierto →
  `{verificado: true, id_cliente, nombre}`. Fallo → `{verificado: false, intentos_restantes}`. Al
  tercer fallo del mismo cliente, esa y las siguientes llamadas → `ErrorCore(NEGOCIO,
  IDENTIDAD_BLOQUEADA, reintentable=false)` con la indicación de escalar. Contador en memoria
  por cliente; un acierto lo reinicia.
- **Rationale**: limitar intentos evita que el agente "adivine" la fecha; el estado en memoria
  basta para un core simulado (spec, Assumptions).
- **Validación**: `id_cliente` inexistente → `VALIDACION/CLIENTE_NO_EXISTE`; fecha que no es
  `AAAA-MM-DD` → `VALIDACION/FECHA_INVALIDA` (no consume intento).

## R6. Fechas relativas

- **Decision**: `transacciones.json` guarda `dias_atras`; `datos.py` calcula la fecha con la fecha
  base = `BANCO_FECHA_BASE` (si existe, `AAAA-MM-DD`) o el día actual.
- **Rationale**: los casos del enunciado hablan de "ayer" y de "más de 90 días"; con fechas fijas
  la demo se rompería con el paso de los días. Fijar la base hace los tests reproducibles.

## R7. Datos ficticios

- **Decision**: 8 clientes con nombres genéricos, documentos `FIC-1000000x`, fechas de nacimiento
  ficticias; tarjetas por `ultimos4`. Casos: titular de la tarjeta 4821 con dos cobros de ayer
  ($180.000 y $1.250.000); dos clientes "Carlos Ramírez"; un cobro de comercio en el exterior con
  `dias_atras` = 120; cobros pequeños disputables; un cliente con dos tarjetas.
- **Rationale**: cubre los casos obligatorios que dependen del core y deja datos para #5–#9. El
  hook `datos_ficticios` valida cada archivo al escribirlo.

## R8. Registro en Claude Code

- **Decision**: agregar a `.mcp.json` el servidor `banco` (`type: stdio`, `command: uv`,
  `args: ["run", "python", "-m", "mcp_server"]`) y `"banco"` a `enabledMcpjsonServers`
  (aprobación del responsable).
- **Rationale**: es el segundo servidor MCP que exige el enunciado y permite probar las
  herramientas desde Claude Code. El agente (#6) lanzará el mismo módulo desde el Agent SDK.

## R9. Empaquetado

- **Decision**: `[build-system]` hatchling y `[tool.hatch.build.targets.wheel] packages =
  ["src/mcp_server"]`; `uv sync` lo instala en modo editable.
- **Rationale**: `python -m mcp_server` funciona desde cualquier directorio y los tests importan
  `mcp_server` sin trucos de `sys.path`.
