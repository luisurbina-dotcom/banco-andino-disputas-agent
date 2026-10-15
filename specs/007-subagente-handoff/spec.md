# Feature Specification: Subagente de análisis, solicitudes con varios asuntos y handoff al analista

**Feature Branch**: `007-subagente-handoff`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#7](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/7): "[Agente] Subagente de análisis, solicitudes con varios asuntos y handoff al analista". Que el agente resuelva mensajes con varias preocupaciones, delegue el análisis de transacciones y escale con criterio.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delegar el análisis de los cobros reportados (Priority: P1)

Cuando el cliente reporta cobros que no reconoce, el agente principal delega en un subagente
especializado el análisis: le entrega de forma explícita el cliente verificado, la tarjeta y los
cobros tal como los describió el cliente (montos aproximados, fechas, comercios). El subagente
consulta las transacciones, empareja cada cobro reportado con una transacción del core y devuelve,
para cada uno, qué corresponde hacer según la política del banco. El subagente no puede disputar,
bloquear ni escalar: solo analiza.

**Why this priority**: es el comportamiento obligatorio 9 ("al menos un subagente… pasando el
contexto de forma explícita") y reduce errores al separar el análisis de la acción.

**Independent Test**: con el titular de la 4821 verificado, el subagente recibe "dos cobros de
ayer, $180.000 y $1.250.000" y devuelve TX-0001 → disputa automática y TX-0002 → escalar por
umbral, sin haber llamado a herramientas de acción.

**Acceptance Scenarios**:

1. **Given** un cliente verificado y cobros reportados, **When** el agente delega el análisis,
   **Then** el subagente recibe en su encargo el cliente, la tarjeta y los cobros, sin depender de
   la conversación.
2. **Given** el encargo, **When** el subagente trabaja, **Then** solo puede consultar
   transacciones; cualquier otra herramienta no está a su alcance.
3. **Given** cada cobro reportado, **When** el subagente responde, **Then** indica la transacción
   emparejada (o que no la encontró), su monto y fecha del core y una recomendación:
   disputa automática, escalar por umbral, escalar por política o pedir más datos.
4. **Given** el subagente, **When** consulta transacciones, **Then** las garantías de la regla 1
   también lo alcanzan (no puede consultar clientes no verificados).

---

### User Story 2 - Varias preocupaciones en un mensaje, una sola respuesta (Priority: P1)

El cliente mezcla en un mensaje varios asuntos (dos cobros y un bloqueo). El agente separa cada
asunto, resuelve los que puede, escala los que no, y responde una sola vez con el estado de cada
uno.

**Why this priority**: comportamiento obligatorio 5 y criterio de aceptación del issue con el
mensaje de ejemplo.

**Independent Test**: el mensaje de ejemplo produce disputa del cobro bajo, escalamiento del alto
y bloqueo de la tarjeta, informados en una sola respuesta final.

**Acceptance Scenarios**:

1. **Given** el mensaje de ejemplo y la identidad verificada, **When** el agente termina,
   **Then** existe una disputa abierta del cobro de $180.000, un caso de analista por el de
   $1.250.000 y la tarjeta 4821 bloqueada.
2. **Given** ese turno, **When** el agente responde, **Then** la respuesta final menciona cada
   asunto con lo que se hizo y lo que sigue.

---

### User Story 3 - Escalar con criterio y con un handoff útil (Priority: P1)

El agente escala cuando el cliente pide una persona, cuando el monto supera el umbral y cuando la
política no cubre el caso; no escala lo que puede resolver. Cuando escala por umbral o por
política, el caso incluye siempre al cliente y las transacciones involucradas, de modo que el
analista entienda el caso sin la conversación.

**Why this priority**: comportamientos obligatorios 7 y 8 y segundo criterio de aceptación del
issue.

**Independent Test**: un escalamiento por umbral sin cliente o sin transacciones es rechazado; uno
completo queda en cola con cliente, transacciones con monto, acciones, causa y recomendación.

**Acceptance Scenarios**:

1. **Given** una escalación por `MONTO_SUPERA_UMBRAL` o `POLITICA_NO_CUBRE`, **When** falta el
   cliente o las transacciones, **Then** el core la rechaza con un error de validación que indica
   qué falta.
2. **Given** un escalamiento completo, **When** se crea el caso, **Then** el resumen tiene cliente,
   transacciones con monto y fecha del core, acciones realizadas, causa y acción recomendada.
3. **Given** un cobro de $180.000 cubierto por la política, **When** el agente lo atiende,
   **Then** lo disputa y no lo escala.

### Edge Cases

- Un cobro reportado que no coincide con ninguna transacción: el subagente lo marca como no
  encontrado y el agente pide más datos al cliente, sin disputar a ciegas.
- Montos aproximados del cliente ("como un millón"): el subagente empareja por cercanía de monto y
  fecha y lo indica; si hay dos candidatas, pide más datos.
- El subagente recibe un encargo sin cliente verificado: su consulta es negada por las garantías y
  lo informa.
- Escalamiento por `CLIENTE_PIDE_PERSONA` o `IDENTIDAD_BLOQUEADA`: no exige transacciones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El agente MUST disponer de un subagente `analista-transacciones` cuyo único acceso a
  herramientas sea `consultar_transacciones`.
- **FR-002**: El agente MUST delegar el análisis de los cobros reportados en el subagente,
  pasándole en el encargo el `id_cliente` verificado, los últimos 4 dígitos de la tarjeta y los
  cobros reportados (monto, fecha, comercio si se conoce).
- **FR-003**: El subagente MUST devolver por cada cobro reportado: transacción emparejada o "no
  encontrada", monto y fecha del core, y una recomendación entre `DISPUTA_AUTOMATICA`,
  `ESCALAR_UMBRAL`, `ESCALAR_POLITICA` y `PEDIR_DATOS`.
- **FR-004**: Las garantías de las reglas 1 y 2 del #6 MUST aplicarse también a las llamadas del
  subagente.
- **FR-005**: El agente MUST separar los asuntos de un mensaje, resolverlos y responder una sola vez
  con el estado de cada uno.
- **FR-006**: Un escalamiento con causa `MONTO_SUPERA_UMBRAL` o `POLITICA_NO_CUBRE` MUST incluir
  `id_cliente` y al menos una transacción; si no, el core MUST rechazarlo con
  `VALIDACION/RESUMEN_INCOMPLETO`.
- **FR-007**: El agente MUST NOT escalar disputas que la política permite resolver
  automáticamente.
- **FR-008**: Los eventos del turno MUST permitir distinguir el trabajo del subagente (su consulta)
  del agente principal, para la interfaz del #8.

### Key Entities

- **Encargo de análisis**: cliente verificado, tarjeta, cobros reportados.
- **Análisis**: por cobro reportado: transacción emparejada, monto, fecha, país, recomendación y
  motivo.
- **Caso de analista**: el del #5, con la exigencia de cliente y transacciones para umbral y
  política.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el mensaje de ejemplo, el 100% de los asuntos (2 cobros + bloqueo) quedan
  resueltos o escalados en el turno en que se verifica la identidad, con una sola respuesta final.
- **SC-002**: El subagente realiza 0 llamadas a herramientas de acción (disputar, bloquear,
  escalar).
- **SC-003**: El 100% de los escalamientos por umbral o política tienen cliente y transacciones.
- **SC-004**: 0 escalamientos de cobros que se podían disputar automáticamente en las
  conversaciones de prueba.
- **SC-005**: Las pruebas automáticas de esta feature corren sin red ni credenciales.

## Assumptions

- El subagente se define con el mecanismo de subagentes del Agent SDK y recibe un prompt propio;
  no hereda la conversación.
- El emparejamiento es responsabilidad del subagente (criterio), no de una regla dura: las reglas
  duras siguen siendo los hooks del #6 y la validación del core.
- La recomendación del subagente es una sugerencia: las acciones las ejecuta el agente principal y
  las protegen las garantías.
- Interfaz de chat (#8) y casos e2e (#9) quedan fuera de este ticket.
