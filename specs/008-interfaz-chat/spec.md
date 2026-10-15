# Feature Specification: Interfaz de chat que hace evidentes las acciones

**Feature Branch**: `008-interfaz-chat`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#8](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/8): "[Agente] Interfaz de chat que hace evidentes las acciones". Interfaz que simula un chat, comprensible para alguien que no conoce el código.

## User Scenarios & Testing *(mandatory)*

El usuario es quien mira la demo (evaluador o analista del banco) y quien escribe como cliente.
No conoce el código: debe entender qué pasó solo mirando la pantalla.

### User Story 1 - Conversar turno a turno (Priority: P1)

Una persona arranca la interfaz con un solo comando, escribe como cliente y ve, turno a turno,
su mensaje y la respuesta del agente, claramente diferenciados. Mientras el agente trabaja, la
pantalla indica que está procesando.

**Why this priority**: es el comportamiento obligatorio 10 y la base del video de
funcionamiento.

**Independent Test**: arrancar con un comando, enviar "hola" y ver el mensaje del cliente y la
respuesta del agente en bloques distintos; salir con un comando de salida.

**Acceptance Scenarios**:

1. **Given** el proyecto instalado, **When** se ejecuta el comando de arranque, **Then** aparece
   una bienvenida que explica que los datos son ficticios y cómo salir.
2. **Given** la interfaz abierta, **When** el cliente escribe un mensaje, **Then** se ve su mensaje
   y luego la respuesta del agente, diferenciados por estilo y etiqueta.
3. **Given** que el agente está trabajando, **When** pasan segundos, **Then** se ve un indicador de
   que está procesando.
4. **Given** el comando de salida, **When** el cliente lo escribe, **Then** la interfaz muestra un
   resumen de las acciones de la sesión y termina.

---

### User Story 2 - Acciones evidentes (Priority: P1)

Cuando el agente bloquea una tarjeta, abre una disputa, escala a un analista o cuando una
garantía niega una acción, la interfaz lo muestra con un indicador visual inconfundible
(etiqueta, ícono y color), con los datos clave: tarjeta, número de disputa y monto, número de
caso y causa, o la regla que lo impidió.

**Why this priority**: es lo que el enunciado exige explícitamente ("cuando el agente bloquea,
inicia una disputa o escala, la interfaz lo hace evidente").

**Independent Test**: en el mensaje de ejemplo se ven, en el turno correspondiente, los
indicadores de tarjeta bloqueada, disputa abierta, acción negada por la regla 2 y escalamiento.

**Acceptance Scenarios**:

1. **Given** un bloqueo de tarjeta, **When** termina el turno, **Then** se ve "TARJETA BLOQUEADA"
   con los últimos 4 dígitos.
2. **Given** una disputa abierta, **When** termina el turno, **Then** se ve "DISPUTA ABIERTA" con su
   número, la transacción y el monto.
3. **Given** un escalamiento, **When** termina el turno, **Then** se ve "ESCALADO A ANALISTA" con el
   número de caso y la causa.
4. **Given** una acción negada por una garantía, **When** termina el turno, **Then** se ve "NEGADO"
   con la regla y el motivo.
5. **Given** pasos intermedios (búsqueda, verificación, análisis del subagente, error del banco y
   reintento), **When** termina el turno, **Then** se ven como indicadores secundarios, menos
   destacados que las cuatro acciones principales.

---

### User Story 3 - Demo reproducible (Priority: P2)

Para grabar el video, se puede arrancar la interfaz con una lista de mensajes preparada, que se
envían uno a uno, y con una falla transitoria activada, sin cambiar el código.

**Why this priority**: facilita grabar los seis casos obligatorios de forma consistente (#9 y
video de funcionamiento).

**Independent Test**: arrancar con un guion de dos mensajes muestra los dos turnos sin escribir;
con la falla transitoria activada se ve el indicador de error y el reintento.

**Acceptance Scenarios**:

1. **Given** un archivo con mensajes, **When** se arranca indicándolo, **Then** cada mensaje se
   muestra como si el cliente lo escribiera y se procesa en orden.
2. **Given** la falla transitoria configurada, **When** el agente consulta, **Then** se ve el
   indicador de error transitorio y luego el resultado del reintento.

### Edge Cases

- El agente no puede arrancar (sin credenciales o sin Claude Code): la interfaz muestra un mensaje
  claro y termina sin traza técnica.
- Mensaje vacío: no se envía.
- Un turno sin acciones: solo se ve la respuesta.
- Varias acciones en un turno: se muestran todas, en el orden en que ocurrieron.
- Interrupción con teclado: termina de forma ordenada mostrando el resumen.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La interfaz MUST arrancar con un único comando documentado.
- **FR-002**: MUST mostrar turno a turno el mensaje del cliente y la respuesta del agente,
  diferenciados visualmente.
- **FR-003**: MUST mostrar un indicador de procesamiento mientras el agente trabaja.
- **FR-004**: MUST mostrar, a partir de los eventos del turno, indicadores destacados para tarjeta
  bloqueada, disputa abierta, escalamiento y acción negada, con sus datos clave.
- **FR-005**: MUST mostrar indicadores secundarios para búsqueda, verificación (exitosa o fallida),
  delegación al subagente, consultas y errores del banco.
- **FR-006**: MUST aceptar un comando de salida y mostrar al salir el resumen de acciones de la
  sesión.
- **FR-007**: MUST aceptar un guion de mensajes para reproducir conversaciones sin teclear.
- **FR-008**: MUST mostrar un mensaje claro si el agente no puede arrancar.
- **FR-009**: La traducción de eventos a indicadores MUST poder probarse sin red ni credenciales.

### Key Entities

- **Indicador**: tipo (principal o secundario), etiqueta, ícono, color y detalle, derivado de un
  evento del turno.
- **Resumen de sesión**: conteo y lista de las acciones principales.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona que no conoce el código identifica correctamente en el mensaje de
  ejemplo las 4 acciones (bloqueo, disputa, negación, escalamiento) solo mirando la pantalla.
- **SC-002**: El 100% de los eventos de bloqueo, disputa, escalamiento y negación de los casos de
  prueba producen su indicador principal.
- **SC-003**: La interfaz arranca con 1 comando y no requiere configuración adicional a la del
  agente.
- **SC-004**: Las pruebas de la traducción de eventos corren sin red en menos de 5 segundos
  (excluida la importación).

## Assumptions

- Interfaz de terminal: el enunciado no califica el diseño visual sino la claridad; una terminal
  con colores es suficiente y se graba fácilmente.
- Los indicadores se derivan de los eventos del agente (#6, #7), no del texto del modelo.
- El guion es un archivo de texto con un mensaje por línea.
- La falla transitoria se activa con la configuración del servidor del #5.
