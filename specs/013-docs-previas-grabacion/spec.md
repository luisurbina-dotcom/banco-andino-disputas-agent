# Feature Specification: Documentación previa a la grabación y robustez del paquete

**Feature Branch**: `013-docs-previas-grabacion`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#25](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/25): "[Docs] Documentación previa a la grabación y robustez del paquete". Al probar el `.zip` de `main` (`6ac9611`) en un contenedor limpio aparecieron dos limitaciones del paquete; además, parte de lo que el autor debe explicar en el video y la defensa solo estaba en specs internas o en la conversación.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El evaluador corre los tests del paquete en cualquier máquina (Priority: P1)

Un evaluador descomprime el paquete y corre los tests unitarios. Si su máquina no tiene `git`,
la suite igual termina: los tests que necesitan `git` se saltan con un motivo claro en lugar de
cortar todo.

**Why this priority**: un error de arranque haría parecer rota toda la entrega.

**Independent Test**: correr la suite en un entorno sin `git` y en uno con `git`.

**Acceptance Scenarios**:

1. **Given** una máquina sin `git`, **When** se corren los tests unitarios, **Then** terminan sin
   errores de carga y los que requieren `git` aparecen como saltados con su motivo.
2. **Given** una máquina con `git`, **When** se corren, **Then** pasan todos como antes.

---

### User Story 2 - El evaluador descomprime el paquete sin perder permisos (Priority: P2)

El README indica cómo descomprimir el paquete conservando los permisos de ejecución.

**Independent Test**: leer la sección del README.

**Acceptance Scenarios**:

1. **Given** el README, **When** el evaluador busca cómo abrir el paquete, **Then** encuentra la
   herramienta recomendada y la advertencia sobre la alternativa que pierde permisos.

---

### User Story 3 - Las decisiones y riesgos que se defienden están escritos (Priority: P1)

El autor graba el video y la defensa sin depender de la memoria: el guion refleja el estado
actual y `DECISIONES.md` registra quién tomó cada decisión aceptada y el riesgo residual abierto.

**Independent Test**: leer `demo/GUION_VIDEO.md` y `DECISIONES.md`.

**Acceptance Scenarios**:

1. **Given** el guion, **When** el autor prepara la grabación, **Then** no le pide verificar un
   ticket ya cerrado y le dice qué hacer si aparece una negación residual de la devolución del
   subagente.
2. **Given** `DECISIONES.md`, **When** un evaluador lo lee, **Then** encuentra que la excepción del
   historial, el ticket aparte de la devolución y la política estricta de `.env.example` fueron
   decisiones del autor, y el riesgo residual de la devolución del subagente.

### Edge Cases

- Un clon superficial con `git`: el salto existente del test del historial se mantiene.
- `DECISIONES.md` no puede pasar de dos páginas (≈ 1.000 palabras).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Los tests del empaquetado MUST saltarse con un motivo explícito cuando `git` no está
  disponible, sin errores de carga que corten la suite.
- **FR-002**: Con `git` disponible, la suite completa y la verificación del ecosistema MUST seguir
  en verde.
- **FR-003**: El README MUST indicar cómo descomprimir el paquete conservando los permisos.
- **FR-004**: El guion del video MUST reflejar que la devolución del subagente está corregida y qué
  hacer si aparece una negación residual.
- **FR-005**: `DECISIONES.md` MUST registrar quién tomó cada decisión aceptada y el riesgo residual,
  sin superar las dos páginas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En un entorno limpio sin `git`, 0 errores de carga en los tests unitarios.
- **SC-002**: En un entorno limpio con `git`, 100 % de los tests unitarios en verde y la
  verificación del ecosistema en "Todo OK".
- **SC-003**: `DECISIONES.md` ≤ 1.000 palabras.

## Assumptions

- El caso sin `git` es poco probable para un evaluador, pero el arreglo es pequeño y evita una
  primera impresión de suite rota.
- El enlace del video lo agrega el autor en un cambio posterior; no es parte de este ticket.
