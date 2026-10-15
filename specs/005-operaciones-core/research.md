# Research: Operaciones del core

## R1. Identificar el producto

- **Decision**: tarjeta = `id_cliente` + `ultimos4`.
- **Rationale**: el cliente dice "mi tarjeta terminada en 4821"; el agente ya tiene el
  `id_cliente` de la verificación. Combinar ambos resuelve el caso `7310` compartido por dos
  clientes. Una tarjeta que no es del cliente → `VALIDACION/TARJETA_NO_ENCONTRADA`.

## R2. Defensa en profundidad de la regla 1

- **Decision**: el `Core` guarda en memoria los `id_cliente` verificados con éxito por
  `verificar_identidad`; consultar, disputar y bloquear exigen que el cliente esté en ese
  conjunto, si no → `PERMISOS/IDENTIDAD_NO_VERIFICADA` (no reintentable, "verifica la identidad
  antes de operar").
- **Rationale**: da uso real a la categoría `PERMISOS` y protege el core aunque otro cliente MCP
  (por ejemplo, Claude Code con `.mcp.json`) llame directo. **No** sustituye al hook del agente
  (#6), que es la garantía exigida por la constitución: el servidor es compartido entre sesiones,
  mientras que el hook decide por la sesión del agente.
- **Alternatives considered**: sin control en el servidor (deja `PERMISOS` sin uso y el core
  abierto a llamadas directas).

## R3. Reglas de disputa

- **Decision**: orden de evaluación en `iniciar_disputa`:
  1. falla transitoria programada → `TRANSITORIO`;
  2. verificado → si no, `PERMISOS`;
  3. transacción existe y es de una tarjeta del cliente → si no, `VALIDACION/TRANSACCION_NO_ENCONTRADA`;
  4. ya disputada → `NEGOCIO/DISPUTA_EXISTENTE`;
  5. `pais ≠ CO` y antigüedad > 90 días → `NEGOCIO/POLITICA_NO_CUBRE`;
  6. monto del core > 500 000 → `NEGOCIO/MONTO_SUPERA_UMBRAL`;
  7. abrir disputa.
- **Rationale**: los permisos antes que los datos evitan filtrar si una transacción existe; la
  política antes que el umbral porque un caso no cubierto no se "arregla" con un analista de
  montos. El monto sale del core por `id_transaccion` (FR-004): la herramienta ni siquiera recibe
  un monto.
- **Límites**: exactamente 500 000 se disputa; exactamente 90 días se disputa.

## R4. Escalamiento autocontenido

- **Decision**: `escalar_a_analista(causa, descripcion, accion_recomendada, id_cliente=None,
  id_transacciones=[], acciones_realizadas=[])`. El core enriquece cada `id_transaccion` con
  fecha, monto, comercio y país desde sus datos y el `id_cliente` con el nombre; un id
  desconocido → `VALIDACION`. Devuelve `{id_caso, estado: "en_cola_analista", resumen}` y guarda
  el caso.
- **Rationale**: el analista no ve la conversación; si el modelo enviara los montos podría
  equivocarse. Con ids, el resumen tiene los montos reales. No exige verificación (regla 4).
- **Alternatives considered**: texto libre (no estructurado, sin garantía de campos); montos
  enviados por el modelo (pueden ser incorrectos).

## R5. Fallas transitorias

- **Decision**: `Core.programar_fallas(herramienta, n)` y `Core.consumir_falla(herramienta)`, que
  lanza `TRANSITORIO/CORE_NO_DISPONIBLE` (`reintentable: true`) mientras queden fallas. Todas las
  herramientas operativas consumen primero. El servidor lee `BANCO_FALLAS_TRANSITORIAS`
  (`herramienta:N[,herramienta:N]`) al arrancar; un formato inválido detiene el arranque con un
  mensaje claro.
- **Rationale**: determinista y reproducible (no aleatorio), activable en tests y en la demo sin
  cambiar código. Para el caso obligatorio basta `consultar_transacciones:1`.

## R6. Serialización

- **Decision**: las fechas salen como `AAAA-MM-DD` (texto); montos como enteros COP.
- **Rationale**: el contenido estructurado de MCP es JSON.

## R7. Tests de contrato del servidor

- **Decision**: el test de descripciones exactas se generaliza para leer los dos contratos
  (`specs/004-…` y `specs/005-…`); el test de herramientas expuestas pasa a 6.
