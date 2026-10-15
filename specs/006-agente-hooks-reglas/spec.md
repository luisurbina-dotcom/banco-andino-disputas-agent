# Feature Specification: Agente de disputas — ciclo agéntico y garantías de las reglas 1 y 2

**Feature Branch**: `006-agente-hooks-reglas`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#6](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/6): "[Agente] Ciclo agéntico con Agent SDK y hooks que garantizan las reglas 1 y 2". Agente que consume el servidor del banco y garantiza las reglas de negocio con hooks, no con el prompt.

## User Scenarios & Testing *(mandatory)*

El usuario final es el cliente del banco que escribe por el chat; el agente atiende la
conversación turno a turno usando las herramientas del servidor `banco`.

### User Story 1 - Conversación turno a turno (Priority: P1)

El cliente escribe un mensaje y el agente responde. Para hacerlo puede usar varias
herramientas seguidas (buscar, verificar, consultar…) y decide por sí mismo cuándo terminó de
trabajar en ese turno. La conversación conserva el contexto entre turnos.

**Why this priority**: es el comportamiento obligatorio 1 (ciclo agéntico correcto) y la base de
todo lo demás.

**Independent Test**: un turno que exige varias herramientas termina cuando el modelo indica que
terminó, sin un tope fijo de iteraciones; un segundo turno usa información del primero.

**Acceptance Scenarios**:

1. **Given** un mensaje que requiere varias herramientas, **When** el agente lo atiende,
   **Then** encadena las llamadas que necesite y termina el turno cuando el modelo deja de pedir
   herramientas.
2. **Given** un turno terminado, **When** el cliente envía otro mensaje, **Then** el agente
   recuerda lo ocurrido (cliente identificado, acciones hechas).
3. **Given** cualquier turno, **When** termina, **Then** el resultado incluye la respuesta al
   cliente y la lista de acciones ejecutadas o bloqueadas, para que la interfaz las muestre.

---

### User Story 2 - Ninguna operación sin identidad verificada (Priority: P1)

Si el agente intenta consultar transacciones, iniciar una disputa o bloquear una tarjeta de un
cliente que no ha verificado en esta conversación, la acción se impide antes de llegar al banco,
sin importar lo que diga el prompt o lo que decida el modelo.

**Why this priority**: regla 1 del banco y comportamiento obligatorio 2. Es un caso de prueba
obligatorio ("un intento de iniciar una disputa sin identidad verificada, que debe ser
bloqueado").

**Independent Test**: sin verificación previa en la conversación, una llamada a
`iniciar_disputa` es negada por la garantía del agente y el modelo recibe el motivo.

**Acceptance Scenarios**:

1. **Given** una conversación sin verificación exitosa, **When** el agente intenta consultar,
   disputar o bloquear, **Then** la acción se niega antes de ejecutarse y el modelo recibe un
   motivo que le indica verificar primero.
2. **Given** una verificación **fallida** (`verificado: false`), **When** el agente intenta
   operar, **Then** la acción sigue negada.
3. **Given** el cliente A verificado, **When** el agente intenta operar sobre el cliente B,
   **Then** la acción se niega.
4. **Given** el cliente verificado, **When** el agente opera sobre ese cliente, **Then** la acción
   se permite.

---

### User Story 3 - Ninguna disputa automática por encima de $500.000 (Priority: P1)

Si el agente intenta iniciar una disputa sobre una transacción de más de $500.000, la acción se
impide antes de llegar al banco, con el monto real registrado en el core (no el que el modelo
crea o diga), y el modelo recibe la indicación de escalar a un analista.

**Why this priority**: regla 2 del banco y comportamiento obligatorio 2.

**Independent Test**: con el cliente verificado, `iniciar_disputa` sobre el cobro de $1.250.000
es negada por la garantía del agente; sobre el de $180.000 se permite.

**Acceptance Scenarios**:

1. **Given** una transacción de más de $500.000 en el core, **When** el agente intenta
   disputarla, **Then** se niega con la indicación de escalar.
2. **Given** una transacción de exactamente $500.000, **When** el agente intenta disputarla,
   **Then** se permite.
3. **Given** que el modelo afirma un monto distinto en su razonamiento o en otros argumentos,
   **When** intenta disputar, **Then** la decisión usa solo el monto del core.
4. **Given** un identificador de transacción desconocido, **When** intenta disputar, **Then** la
   garantía no lo permite a ciegas: niega con un motivo que pide consultar las transacciones.

---

### User Story 4 - Criterio del agente en las demás reglas (Priority: P1)

El agente sigue las instrucciones del banco para lo que es criterio: bloquea de inmediato ante
sospecha de fraude (regla 3), escala de inmediato si el cliente pide una persona sin investigar
antes (regla 4), escala lo que la política no cubre (regla 5) y, ante varias coincidencias de
cliente, pide otro identificador en lugar de elegir.

**Why this priority**: reglas 3–5 y comportamientos obligatorios 6 y 7.

**Independent Test**: en conversaciones reales, "quiero hablar con una persona" produce un
escalamiento sin búsquedas previas; un nombre con dos coincidencias produce una pregunta por otro
identificador.

**Acceptance Scenarios**:

1. **Given** que el cliente pide una persona desde el primer mensaje, **When** el agente
   responde, **Then** escala de inmediato con causa `CLIENTE_PIDE_PERSONA` y no busca ni consulta
   antes.
2. **Given** dos clientes con el mismo nombre, **When** el agente busca, **Then** pide otro
   identificador y no elige.
3. **Given** sospecha de clonación con identidad verificada, **When** el cliente lo dice,
   **Then** el agente bloquea la tarjeta sin pedir confirmaciones adicionales.
4. **Given** un error `POLITICA_NO_CUBRE` o `MONTO_SUPERA_UMBRAL`, **When** el agente lo recibe,
   **Then** escala en lugar de improvisar.
5. **Given** un error `TRANSITORIO`, **When** el agente lo recibe, **Then** reintenta.

### Edge Cases

- La garantía falla internamente (error de lectura, dato inesperado): la acción se **niega**
  (fail-closed), igual que los hooks de desarrollo del #2.
- Una verificación exitosa seguida de un bloqueo por intentos en la misma conversación: el estado
  verificado se pierde.
- Herramientas que no operan sobre productos (`buscar_cliente`, `verificar_identidad`,
  `escalar_a_analista`) no requieren verificación.
- Sin credenciales de modelo, el agente no arranca y lo dice con un mensaje claro; las pruebas de
  las garantías no las necesitan.
- El servidor `banco` también protege las reglas 1 y 2 (defensa en profundidad del #5); la
  garantía de la constitución es la del agente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El agente MUST usar el servidor `banco` como única fuente de herramientas del banco y
  conservar la conversación entre turnos.
- **FR-002**: Cada turno MUST continuar mientras el modelo pida herramientas y terminar cuando el
  modelo indique que terminó; MUST NOT usar un tope fijo de iteraciones ni buscar palabras en el
  texto para decidirlo.
- **FR-003**: La sesión MUST marcarse como verificada para un cliente **solo** cuando
  `verificar_identidad` responde `verificado: true` para ese `id_cliente`; un bloqueo por intentos
  MUST retirar la verificación.
- **FR-004**: Antes de `consultar_transacciones`, `iniciar_disputa` o `bloquear_tarjeta`, una
  garantía determinista MUST negar la llamada si su `id_cliente` no es el cliente verificado en la
  sesión (regla 1).
- **FR-005**: Antes de `iniciar_disputa`, una garantía determinista MUST negar la llamada si el
  monto registrado en el core para `id_transaccion` supera $500.000, o si la transacción no existe
  (regla 2). El monto MUST leerse de los datos del core, nunca de los argumentos o del texto del
  modelo.
- **FR-006**: Las negaciones MUST llegar al modelo con un motivo accionable (verificar primero,
  escalar a un analista, consultar transacciones).
- **FR-007**: Las garantías MUST fallar de forma segura: ante un error interno, niegan.
- **FR-008**: Las instrucciones del sistema MUST cubrir las reglas 3, 4 y 5, la ambigüedad de
  clientes, el reintento ante errores transitorios y la respuesta unificada al cliente.
- **FR-009**: Cada turno MUST devolver la respuesta al cliente y los eventos del turno (herramienta
  llamada, resultado o error, negación por garantía) para la interfaz del #8.
- **FR-010**: Las garantías MUST poder probarse sin red ni credenciales de modelo.

### Key Entities

- **Sesión**: conversación con el modelo, cliente verificado (o ninguno) y eventos.
- **Evento**: herramienta, argumentos, resultado (éxito, error del servidor o negación por
  garantía con motivo).
- **Respuesta de turno**: texto al cliente + eventos del turno.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de operar sin identidad verificada se niegan antes de llegar
  al servidor, en pruebas automáticas y en conversaciones reales.
- **SC-002**: El 100% de los intentos de disputa por más de $500.000 se niegan antes de llegar al
  servidor, aunque el modelo afirme otro monto.
- **SC-003**: 0 turnos terminados por un tope de iteraciones.
- **SC-004**: Las pruebas de las garantías corren sin red ni credenciales en menos de 5 segundos
  (excluida la importación de dependencias).
- **SC-005**: En conversación real, "quiero hablar con una persona" escala en el primer turno sin
  llamadas previas a búsqueda o consulta.

## Assumptions

- Las credenciales del modelo llegan por el entorno del desarrollador (clave de API o la sesión de
  Claude Code que reutiliza el Agent SDK); nunca se versionan.
- El agente lanza el servidor `banco` como proceso propio por conversación, así el estado del core
  (verificaciones, disputas) es por conversación.
- La garantía de la regla 2 lee los datos del core desde los mismos archivos ficticios que el
  servidor (con la misma fecha base), en solo lectura.
- El subagente de análisis, la separación de varios asuntos y el handoff detallado son del #7; la
  interfaz de chat es del #8 y los casos end-to-end del #9.
- Condición heredada del #5: este ticket MUST pasar `/revisar-cumplimiento` con el principio II en
  CUMPLE.
