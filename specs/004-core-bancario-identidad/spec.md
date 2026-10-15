# Feature Specification: Core bancario simulado — datos ficticios e identificación del cliente

**Feature Branch**: `004-core-bancario-identidad`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#4](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/4): "[MCP] Core bancario simulado: datos ficticios, buscar_cliente y verificar_identidad". Servidor de herramientas que simula el core bancario y permite identificar al cliente.

## User Scenarios & Testing *(mandatory)*

Los "usuarios" de esta feature son el agente de disputas (que llama a las herramientas) y, a
través de él, el cliente del banco que escribe por el chat.

### User Story 1 - Localizar al cliente (Priority: P1)

El cliente escribe "no reconozco dos cobros en mi tarjeta terminada en 4821". El agente busca
al cliente con lo que tiene (últimos 4 dígitos de la tarjeta, nombre o documento) y recibe la
lista de candidatos, sin datos sensibles.

**Why this priority**: sin localizar al cliente no hay nada que verificar ni disputar.

**Independent Test**: buscar por "4821" devuelve exactamente un cliente; buscar por un
documento existente devuelve ese cliente; buscar por algo inexistente devuelve una lista vacía.

**Acceptance Scenarios**:

1. **Given** una tarjeta terminada en 4821 registrada, **When** se busca por "4821",
   **Then** se devuelve el cliente titular con su identificador y nombre.
2. **Given** un documento registrado, **When** se busca por ese documento, **Then** se devuelve
   exactamente ese cliente.
3. **Given** un criterio sin coincidencias, **When** se busca, **Then** la respuesta es una
   lista vacía y **no** un error.
4. **Given** cualquier búsqueda, **When** se devuelven candidatos, **Then** la respuesta no
   incluye el dato que se usa para verificar la identidad.

---

### User Story 2 - Varias coincidencias (Priority: P1)

El cliente da solo su nombre y en el banco hay dos clientes con ese nombre. La herramienta
devuelve ambos candidatos y deja claro que hay ambigüedad, para que el agente pida otro
identificador en lugar de elegir.

**Why this priority**: es un caso de prueba obligatorio y una regla de la constitución
(principio V: ante varias coincidencias, pedir otro identificador).

**Independent Test**: buscar por el nombre compartido devuelve dos coincidencias y una
indicación explícita de que hay que pedir otro identificador.

**Acceptance Scenarios**:

1. **Given** dos clientes con el mismo nombre, **When** se busca por ese nombre, **Then** se
   devuelven las dos coincidencias.
2. **Given** más de una coincidencia, **When** se devuelve la respuesta, **Then** incluye una
   indicación de que el agente debe pedir otro identificador (documento o últimos 4 dígitos) y
   no elegir.
3. **Given** un nombre escrito sin tildes o con otras mayúsculas, **When** se busca, **Then**
   las coincidencias son las mismas.

---

### User Story 3 - Verificar la identidad (Priority: P1)

Con un único cliente localizado, el agente pide al cliente un dato adicional y lo verifica.
Si coincide, la identidad queda confirmada; si no, se informa sin revelar el dato correcto y
con los intentos que quedan. Tras varios fallos, la verificación queda bloqueada.

**Why this priority**: la regla 1 del banco (identidad antes de cualquier operación) depende de
esta confirmación. El hook del agente (issue #6) se apoya en esta respuesta.

**Independent Test**: verificar con el dato correcto confirma la identidad; con un dato
incorrecto no la confirma y reduce los intentos; al agotar los intentos responde con un error de
negocio no reintentable.

**Acceptance Scenarios**:

1. **Given** un cliente localizado, **When** se verifica con el dato correcto, **Then** la
   respuesta confirma la identidad de ese cliente.
2. **Given** un dato incorrecto, **When** se verifica, **Then** la identidad no se confirma, la
   respuesta indica los intentos restantes y no revela el dato correcto.
3. **Given** que se agotaron los intentos, **When** se vuelve a verificar, **Then** la respuesta
   es un error de negocio no reintentable que indica escalar a un analista.
4. **Given** un identificador de cliente inexistente o mal formado, **When** se verifica,
   **Then** la respuesta es un error de validación.

---

### User Story 4 - Contrato de herramientas claro (Priority: P1)

Las herramientas describen cuándo usarse, cuándo no y qué devuelven, y todos sus errores tienen
la misma forma, con categoría e indicación de si se pueden reintentar.

**Why this priority**: es el principio V y un comportamiento obligatorio del enunciado
(descripciones que eviten confusiones; errores estructurados).

**Independent Test**: se leen las descripciones expuestas por el servidor y se provocan errores
de validación; todos siguen el contrato.

**Acceptance Scenarios**:

1. **Given** las descripciones de las herramientas, **When** se leen, **Then** queda explícito
   que la búsqueda no confirma identidad y que la verificación exige un único cliente ya
   localizado.
2. **Given** argumentos inválidos (criterio vacío, "últimos 4 dígitos" con otra longitud),
   **When** se llama a una herramienta, **Then** devuelve un error `VALIDACION` no reintentable
   con un mensaje accionable.

---

### User Story 5 - Datos ficticios que cubren los casos del enunciado (Priority: P1)

El core trae datos ficticios suficientes para todos los casos de prueba: el mensaje de ejemplo,
dos clientes homónimos, un cobro fuera de política y transacciones disputables, con fechas que
siguen siendo "de ayer" o "de hace más de 90 días" el día que se ejecute la demo.

**Why this priority**: sin estos datos no se pueden demostrar los casos obligatorios (#5–#9).

**Independent Test**: al cargar los datos en cualquier fecha, el cliente de la tarjeta 4821
tiene dos cobros de ayer por $180.000 y $1.250.000, y existe un cobro de comercio en el exterior
de hace más de 90 días.

**Acceptance Scenarios**:

1. **Given** el día de ejecución, **When** se cargan los datos, **Then** las fechas de las
   transacciones se calculan respecto de ese día.
2. **Given** los datos, **When** se revisan, **Then** ninguna tarjeta aparece completa (solo
   últimos 4 dígitos) y todos los documentos usan el formato ficticio `FIC-<dígitos>`.

### Edge Cases

- Búsqueda con espacios extra o mayúsculas: se normaliza.
- Búsqueda por número de 4 dígitos que coincide con tarjetas de dos clientes: devuelve ambos
  (misma regla de ambigüedad).
- Búsqueda por documento parcial: no coincide (el documento se compara completo).
- Un cliente con varias tarjetas: aparece una sola vez en los resultados.
- Verificación de un cliente bloqueado por intentos: sigue bloqueado durante la ejecución del
  servidor (el estado vive en memoria y se reinicia al reiniciar el servidor).
- Datos de entrada que no son texto o están ausentes: error `VALIDACION`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El servidor MUST exponer la herramienta `buscar_cliente` que acepte un criterio
  (documento, nombre o últimos 4 dígitos de tarjeta) y devuelva la lista de coincidencias con
  identificador de cliente, nombre y últimos 4 dígitos de sus tarjetas.
- **FR-002**: Una búsqueda sin resultados MUST devolver una lista vacía, no un error.
- **FR-003**: Con más de una coincidencia, la respuesta MUST incluir una indicación explícita de
  pedir otro identificador y no elegir.
- **FR-004**: La búsqueda por nombre MUST ignorar mayúsculas, tildes y espacios repetidos; la de
  documento y la de últimos 4 dígitos MUST ser exactas.
- **FR-005**: Ninguna respuesta de búsqueda MUST incluir el dato de verificación.
- **FR-006**: El servidor MUST exponer `verificar_identidad` que reciba el identificador de un
  cliente y un dato adicional (fecha de nacimiento ficticia) y confirme o rechace la identidad.
- **FR-007**: Un dato incorrecto MUST responder "no verificado" con los intentos restantes, sin
  revelar el dato correcto; al tercer fallo para el mismo cliente, las verificaciones siguientes
  MUST responder un error `NEGOCIO` no reintentable que indique escalar.
- **FR-008**: Todo error MUST tener la forma
  `{"error": {"tipo": TRANSITORIO|VALIDACION|NEGOCIO|PERMISOS, "codigo": str, "reintentable": bool, "mensaje": str}}`.
- **FR-009**: Las descripciones de las herramientas MUST indicar cuándo usarlas, cuándo no, qué
  devuelven y qué hacer con varias coincidencias.
- **FR-010**: Los datos MUST ser ficticios: tarjetas solo por últimos 4 dígitos, documentos
  `FIC-<dígitos>`, nombres genéricos; y MUST incluir: el cliente de la tarjeta 4821 con dos
  cobros de ayer ($180.000 y $1.250.000), dos clientes con el mismo nombre, un cobro de comercio
  en el exterior de hace más de 90 días y transacciones disputables de bajo monto.
- **FR-011**: Las fechas de las transacciones MUST expresarse relativas al día de ejecución y
  poder fijarse a un día concreto para pruebas reproducibles.
- **FR-012**: Las herramientas MUST poder probarse sin red ni credenciales.

### Key Entities

- **Cliente**: identificador, nombre, documento ficticio, fecha de nacimiento ficticia (dato de
  verificación, nunca expuesto por la búsqueda).
- **Tarjeta**: identificador, cliente titular, últimos 4 dígitos, estado.
- **Transacción**: identificador, tarjeta, fecha (relativa al día de ejecución), monto en COP,
  comercio, país del comercio. La consumen las herramientas del issue #5.
- **Coincidencia**: cliente candidato con identificador, nombre y últimos 4 dígitos de tarjetas.
- **Resultado de verificación**: verificado sí/no, identificador del cliente, intentos restantes.
- **Error estructurado**: tipo, código, reintentable, mensaje.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Buscar por el nombre compartido devuelve exactamente 2 coincidencias en el 100%
  de las ejecuciones.
- **SC-002**: El 100% de las búsquedas sin resultado devuelven lista vacía y 0 errores.
- **SC-003**: El 0% de las respuestas de búsqueda o de verificación revelan el dato de
  verificación.
- **SC-004**: El 100% de los errores provocados en las pruebas cumplen el contrato de errores.
- **SC-005**: Los datos cubren los 4 casos del enunciado que dependen del core, en cualquier
  fecha de ejecución.
- **SC-006**: Las pruebas de esta feature corren sin red y en menos de 5 segundos.

## Assumptions

- El dato adicional de verificación es la fecha de nacimiento ficticia (formato `AAAA-MM-DD`);
  es lo habitual en atención telefónica y basta para el MVP.
- Tres intentos fallidos bloquean la verificación del cliente mientras el servidor esté en
  ejecución; no hay persistencia (el core es simulado y en memoria).
- Los datos viven en archivos JSON locales; no hay base de datos.
- Las herramientas operativas (`consultar_transacciones`, `iniciar_disputa`, `bloquear_tarjeta`,
  `escalar_a_analista`) y la inyección de fallas transitorias pertenecen al issue #5; este ticket
  deja los datos de transacciones listos para ellas.
- El hook del agente que hace cumplir la regla 1 (issue #6) usará la respuesta de
  `verificar_identidad` para marcar la sesión como verificada.
