# Feature Specification: El guardia de herramientas no debe negar la devolución del subagente

**Feature Branch**: `012-subagent-handback`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#23](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/23): "[Agente] El guardia de herramientas niega SubagentHandback y degrada la delegación". El subagente `analista-transacciones` intenta devolver su análisis con la herramienta interna de Claude Code `SubagentHandback`; el guardia `pre_herramientas_permitidas` la niega. El análisis no llega al agente principal (que vuelve a consultar) y la interfaz muestra negaciones espurias. Detectado por los guiones de demo del #11.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El análisis del subagente llega al agente principal (Priority: P1)

Cuando el agente delega el análisis de transacciones, el subagente puede devolver su resultado
al agente principal, que lo usa sin repetir la consulta.

**Why this priority**: principio VI (delegación con contexto explícito) y base de la defensa.

**Independent Test**: un caso que delega (mensaje de ejemplo o cobro fuera de política) no
registra negaciones de la devolución del subagente.

**Acceptance Scenarios**:

1. **Given** una delegación al analista, **When** el subagente devuelve su resultado con la
   herramienta interna de devolución, **Then** la devolución no se niega ni se registra como
   negación.
2. **Given** la misma sesión, **When** se muestra el resumen del chat, **Then** no cuenta
   negaciones espurias.

---

### User Story 2 - El guardia sigue cerrado para todo lo demás (Priority: P1)

El guardia de herramientas sigue negando cualquier herramienta que no sea del banco, la
delegación o la devolución del subagente.

**Why this priority**: es una defensa de seguridad; abrir la devolución no debe abrir nada más.

**Independent Test**: tests del guardia con herramientas ajenas (shell, archivos, web, otro MCP).

**Acceptance Scenarios**:

1. **Given** una herramienta ajena, **When** la pide el agente principal o un subagente,
   **Then** se niega como hasta ahora.
2. **Given** la herramienta de devolución, **When** la pide el agente principal (que no es un
   subagente), **Then** se niega.
3. **Given** una entrada malformada, **When** se evalúa, **Then** se niega (falla cerrada).

### Edge Cases

- La devolución es intermitente (el modelo no siempre la usa): la verificación en vivo repite
  los casos hasta observarla.
- La entrada del hook no informa qué agente hace la llamada: se trata como agente principal y se
  niega (falla cerrada).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El guardia MUST permitir la herramienta interna de devolución solo cuando la llama
  un subagente.
- **FR-002**: El guardia MUST seguir negando toda otra herramienta fuera de la lista permitida y
  toda entrada malformada.
- **FR-003**: Las reglas 1 y 2 y la restricción del subagente a `consultar_transacciones` sobre
  herramientas del banco MUST no cambiar.
- **FR-004**: MUST haber tests unitarios de FR-001 y FR-002, y verificación en vivo de que la
  devolución ya no se niega.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 negaciones de la devolución del subagente en las ejecuciones en vivo donde el
  subagente la usa.
- **SC-002**: Los tests unitarios y los seis casos end-to-end siguen en verde.

## Assumptions

- La herramienta de devolución es interna de Claude Code y no ejecuta acciones del banco: solo
  entrega el texto del subagente al agente principal.
- El hook recibe el tipo de agente (`agent_type`) cuando la llamada la hace un subagente; se
  verifica en vivo.
