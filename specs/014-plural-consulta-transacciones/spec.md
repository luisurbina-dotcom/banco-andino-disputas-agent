# Feature Specification: Concordancia de número en el indicador de consulta de transacciones

**Feature Branch**: `014-plural-consulta-transacciones`

**Created**: 2026-10-17

**Status**: Draft

**Input**: Issue de GitHub [#27](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/27): "Chat: concordancia de número en el indicador de consulta de transacciones". En el ensayo de la grabación, el caso C6 mostró "📋 Consulta de transacciones: 1 transacciones".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El indicador de consulta se lee bien con una sola transacción (Priority: P1)

Quien mira el chat (evaluador o video) ve "1 transacción" cuando la consulta devuelve una sola, y
"N transacciones" en los demás casos, igual que el indicador de búsqueda de cliente.

**Independent Test**: test unitario de `src/chat/indicadores.py` con totales 1 y 3.

**Acceptance Scenarios**:

1. **Given** una consulta con `total` 1, **When** se arma el indicador, **Then** el detalle dice
   "1 transacción · por <agente>".
2. **Given** una consulta con `total` 3, **When** se arma el indicador, **Then** el detalle dice
   "3 transacciones · por <agente>".

### Edge Cases

- `total` 0 o ausente: "0 transacciones", como hoy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El indicador de consulta de transacciones MUST concordar en número con el total.
- **FR-002**: El cambio MUST limitarse al texto del indicador; agente, hooks y servidor MCP no
  cambian.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % de los tests unitarios en verde y ruff limpio.

## Assumptions

- Es un ajuste cosmético previo a la grabación; los e2e no dependen de este texto.
