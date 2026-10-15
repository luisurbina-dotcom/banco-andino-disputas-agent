# Feature Specification: Operaciones del core — transacciones, disputas, bloqueo, escalamiento y fallas transitorias

**Feature Branch**: `005-operaciones-core`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#5](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/5): "[MCP] Transacciones, disputas, bloqueo, escalamiento y fallas transitorias". Completar las herramientas operativas del core con errores estructurados.

## User Scenarios & Testing *(mandatory)*

Los usuarios son el agente de disputas (que llama a las herramientas) y el analista humano que
recibe los casos escalados.

### User Story 1 - Consultar las transacciones de una tarjeta (Priority: P1)

Con la identidad verificada, el agente consulta las transacciones de una tarjeta del cliente
en un rango de fechas para encontrar los cobros que el cliente no reconoce.

**Why this priority**: sin las transacciones no se puede decidir qué disputar.

**Independent Test**: con el titular de la 4821 verificado, consultar ayer devuelve los dos
cobros de $180.000 y $1.250.000.

**Acceptance Scenarios**:

1. **Given** un cliente verificado y su tarjeta, **When** consulta un rango de fechas, **Then**
   recibe las transacciones de esa tarjeta en ese rango, con identificador, fecha, monto,
   comercio y país.
2. **Given** un rango sin transacciones, **When** consulta, **Then** recibe una lista vacía, no un
   error.
3. **Given** una tarjeta que no pertenece al cliente, **When** consulta, **Then** recibe un error
   de validación.
4. **Given** un cliente no verificado, **When** consulta, **Then** recibe un error de permisos.

---

### User Story 2 - Iniciar una disputa dentro de la política (Priority: P1)

El agente inicia la disputa de un cobro no reconocido. El core la abre si el monto está dentro
del umbral y la política la cubre; si no, la rechaza con un error de negocio que indica escalar.

**Why this priority**: es el núcleo del escenario y aplica las reglas 2 y 5 del banco.

**Independent Test**: disputar el cobro de $180.000 abre la disputa; disputar el de $1.250.000
devuelve `MONTO_SUPERA_UMBRAL`; disputar el cobro en el exterior de hace 120 días devuelve
`POLITICA_NO_CUBRE`.

**Acceptance Scenarios**:

1. **Given** una transacción del cliente verificado de $500.000 o menos y cubierta por la
   política, **When** se inicia la disputa, **Then** queda abierta con un identificador.
2. **Given** una transacción de más de $500.000, **When** se inicia la disputa, **Then** se
   rechaza con error de negocio `MONTO_SUPERA_UMBRAL`, no reintentable, que indica escalar.
3. **Given** una transacción de comercio en el exterior con más de 90 días, **When** se inicia la
   disputa, **Then** se rechaza con error de negocio `POLITICA_NO_CUBRE`, que indica escalar.
4. **Given** una transacción que ya tiene una disputa, **When** se intenta de nuevo, **Then** se
   rechaza con error de negocio `DISPUTA_EXISTENTE`.
5. **Given** una transacción que no es del cliente o no existe, **When** se intenta, **Then** se
   rechaza con error de validación.
6. **Given** un cliente no verificado, **When** se intenta, **Then** se rechaza con error de
   permisos.

---

### User Story 3 - Bloquear la tarjeta por sospecha de fraude (Priority: P1)

El cliente cree que clonaron su tarjeta. El agente la bloquea de inmediato, sin aprobación
adicional, siempre que la identidad esté verificada.

**Why this priority**: regla 3 del banco y parte del mensaje de ejemplo.

**Independent Test**: bloquear la 4821 del titular verificado la deja bloqueada; repetir la
operación no falla y lo informa.

**Acceptance Scenarios**:

1. **Given** un cliente verificado y su tarjeta activa, **When** se bloquea, **Then** la tarjeta
   queda bloqueada de inmediato.
2. **Given** una tarjeta ya bloqueada, **When** se bloquea de nuevo, **Then** la respuesta lo
   indica sin error.
3. **Given** una tarjeta que no es del cliente, **When** se intenta, **Then** error de validación.
4. **Given** un cliente no verificado, **When** se intenta, **Then** error de permisos.

---

### User Story 4 - Escalar a un analista con un resumen útil (Priority: P1)

Cuando corresponde escalar (el cliente pide una persona, el monto supera el umbral, la política
no cubre el caso o la identidad quedó bloqueada), el agente crea un caso para un analista con un
resumen que se entiende sin la conversación.

**Why this priority**: reglas 2, 4 y 5 y el comportamiento obligatorio de handoff útil.

**Independent Test**: escalar con causa, cliente, transacciones, acciones y acción recomendada
crea un caso en cola; omitir la causa o la acción recomendada es un error de validación.

**Acceptance Scenarios**:

1. **Given** un resumen completo, **When** se escala, **Then** se crea un caso con identificador
   en la cola de analistas y se conserva el resumen tal como se envió.
2. **Given** que el cliente pidió una persona desde el primer mensaje, **When** se escala,
   **Then** el escalamiento se acepta aunque el cliente no esté identificado ni verificado.
3. **Given** un resumen sin causa válida, sin descripción o sin acción recomendada, **When** se
   escala, **Then** error de validación que indica qué falta.

---

### User Story 5 - Fallas transitorias simuladas (Priority: P1)

Para probar que el agente reintenta ante una caída temporal, el core puede configurarse para que
las próximas N llamadas a una herramienta fallen con un error transitorio reintentable.

**Why this priority**: es un caso de prueba obligatorio ("una falla transitoria del servidor MCP")
y un criterio de aceptación del issue.

**Independent Test**: con una falla programada en la consulta de transacciones, la primera
llamada devuelve `TRANSITORIO` reintentable y la siguiente funciona.

**Acceptance Scenarios**:

1. **Given** N fallas programadas para una herramienta, **When** se llama N veces, **Then** cada
   llamada devuelve `TRANSITORIO/CORE_NO_DISPONIBLE` con `reintentable: true`.
2. **Given** que se agotaron las fallas programadas, **When** se vuelve a llamar, **Then** la
   herramienta responde normalmente.
3. **Given** la demo, **When** se arranca el servidor con la configuración de fallas, **Then** se
   aplican sin cambiar el código.

### Edge Cases

- Rango de fechas invertido (desde > hasta) o mal formado: error de validación.
- Sin rango indicado: se usan los últimos 30 días hasta la fecha base.
- Una transacción en el exterior de exactamente 90 días sí está cubierta (el límite es "más de 90").
- Monto de exactamente $500.000: la disputa se inicia (regla 2: "hasta $500.000").
- Transacción extranjera de más de 90 días y además de más de $500.000: prevalece
  `POLITICA_NO_CUBRE` (el caso no está cubierto en absoluto); ambas indican escalar.
- La verificación de identidad que habilita las operaciones vive en memoria durante la ejecución
  del servidor.
- Las fallas transitorias se descuentan antes de cualquier otra validación (simulan que el core
  no respondió).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El servidor MUST exponer `consultar_transacciones` (cliente, últimos 4 dígitos de la
  tarjeta, rango opcional de fechas `AAAA-MM-DD`) que devuelva las transacciones de esa tarjeta en
  el rango, o lista vacía.
- **FR-002**: El servidor MUST exponer `iniciar_disputa` (cliente, transacción, motivo) que abra la
  disputa si el monto es ≤ $500.000 y la política la cubre.
- **FR-003**: Una disputa por más de $500.000 MUST rechazarse con `NEGOCIO/MONTO_SUPERA_UMBRAL`; una
  transacción de comercio en el exterior con más de 90 días MUST rechazarse con
  `NEGOCIO/POLITICA_NO_CUBRE`; ambos mensajes MUST indicar escalar a un analista.
- **FR-004**: El monto que decide la regla 2 MUST ser el registrado en el core para esa
  transacción, nunca un monto recibido como argumento.
- **FR-005**: El servidor MUST exponer `bloquear_tarjeta` (cliente, últimos 4 dígitos, motivo) que
  bloquee de inmediato y sea idempotente.
- **FR-006**: El servidor MUST exponer `escalar_a_analista` con un resumen estructurado: cliente
  (opcional), causa (`CLIENTE_PIDE_PERSONA`, `MONTO_SUPERA_UMBRAL`, `POLITICA_NO_CUBRE`,
  `IDENTIDAD_BLOQUEADA`, `OTRO`), transacciones con monto, acciones realizadas, descripción y acción
  recomendada; MUST validar que causa, descripción y acción recomendada estén presentes.
- **FR-007**: `escalar_a_analista` MUST NOT exigir identidad verificada (regla 4: escalar sin
  investigar).
- **FR-008**: Consultar, disputar y bloquear MUST rechazar con `PERMISOS/IDENTIDAD_NO_VERIFICADA` a
  un cliente que no fue verificado en esta ejecución del servidor (defensa en profundidad; la
  garantía de la regla 1 es el hook del agente del issue #6).
- **FR-009**: El core MUST permitir programar N fallas transitorias por herramienta, desde los tests
  y desde la configuración del servidor, que respondan `TRANSITORIO/CORE_NO_DISPONIBLE` con
  `reintentable: true`.
- **FR-010**: Las cuatro categorías de error (`TRANSITORIO`, `VALIDACION`, `NEGOCIO`, `PERMISOS`)
  MUST aparecer en esta feature con el contrato del #4, y solo `TRANSITORIO` MUST ser reintentable.
- **FR-011**: Las descripciones de las herramientas MUST indicar cuándo usarlas, cuándo no y qué
  hacer con cada error de negocio.
- **FR-012**: Todo MUST poder probarse sin red ni credenciales.

### Key Entities

- **Disputa**: identificador, transacción, cliente, monto (del core), motivo, estado (`abierta`).
- **Tarjeta**: se agrega el cambio de estado `activa → bloqueada`.
- **Caso de analista**: identificador, causa, cliente (opcional), transacciones con monto,
  acciones realizadas, descripción, acción recomendada, estado (`en_cola_analista`).
- **Clientes verificados**: conjunto en memoria que alimenta `verificar_identidad`.
- **Fallas programadas**: herramienta → número de fallas pendientes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las disputas de ≤ $500.000 cubiertas se abren y el 100% de las de más de
  $500.000 o fuera de política se rechazan con el código correcto.
- **SC-002**: El 100% de las operaciones sobre productos de un cliente no verificado se rechazan
  con `PERMISOS`.
- **SC-003**: Las 4 categorías de error son distinguibles en las pruebas y solo `TRANSITORIO` es
  reintentable.
- **SC-004**: Una falla transitoria programada se observa en la primera llamada y desaparece en la
  siguiente, en tests y en una sesión real.
- **SC-005**: Un analista entiende el caso escalado sin la conversación: el 100% de los casos
  aceptados tienen causa, descripción, acción recomendada y, cuando aplica, transacciones con monto.
- **SC-006**: Las pruebas de esta feature corren sin red en menos de 5 segundos.

## Assumptions

- "Producto" = tarjeta, identificada por cliente + últimos 4 dígitos (lo que el cliente dice en el
  chat).
- La política del banco del MVP: se disputan transacciones nacionales sin límite de antigüedad y
  extranjeras de hasta 90 días; el resto no está cubierto.
- Disputas, bloqueos, casos y fallas viven en memoria; se reinician con el servidor.
- La configuración de fallas en el servidor es una variable de entorno con el formato
  `herramienta:N[,herramienta:N]`.
- Advertencia del auditor del #4: el agente no se conecta a estas herramientas hasta que el #6
  tenga los hooks que garantizan las reglas 1 y 2.
