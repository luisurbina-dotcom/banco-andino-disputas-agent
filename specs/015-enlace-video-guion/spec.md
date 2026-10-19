# Feature Specification: Enlace del video de funcionamiento y narración del guion

**Feature Branch**: `015-enlace-video-guion`

**Created**: 2026-10-18

**Status**: Draft

**Input**: Issue de GitHub [#29](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/29): "[Docs] Enlace del video de funcionamiento y narración del guion". El README aún dice "pendiente" en el enlace del video, y la narración definida en el ensayo de la grabación (2026-10-17) no estaba versionada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El evaluador abre el video desde el README (Priority: P1)

El evaluador lee el README y encuentra el enlace al video de funcionamiento, que abre sin pedir
acceso.

**Independent Test**: abrir el enlace del README en una ventana privada.

**Acceptance Scenarios**:

1. **Given** el README en `main`, **When** el evaluador busca el video, **Then** encuentra un
   enlace en lugar del texto "pendiente".
2. **Given** la sección "Pendiente del autor", **When** se publica el video, **Then** ya no lista
   la publicación del video.

### User Story 2 - El autor graba con una narración acordada (Priority: P2)

El autor sigue `demo/GUION_VIDEO.md` y encuentra, además de lo que debe verse, qué decir antes y
durante cada caso.

**Independent Test**: leer el guion y comprobar que cada caso C1–C6 tiene sus dos frases.

**Acceptance Scenarios**:

1. **Given** el guion, **When** el autor prepara la grabación, **Then** encuentra la intro, una
   frase por caso antes de ejecutarlo y otra mientras corre, y el cierre con el resultado de los
   e2e.

### Edge Cases

- El enlace aún no existe al abrir la rama: la tarea del README queda abierta y el PR no se abre
  hasta tenerlo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `demo/GUION_VIDEO.md` MUST incluir una sección de narración con la intro, dos frases
  por caso (antes y durante) y el cierre.
- **FR-002**: El README MUST enlazar el video publicado en lugar del texto "pendiente".
- **FR-003**: La sección "Pendiente del autor" del README MUST dejar de listar la publicación del
  video.
- **FR-004**: El cambio MUST limitarse a documentación; no cambia código.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El enlace del README abre el video sin pedir acceso.
- **SC-002**: `bash scripts/verificar_ecosistema.sh` termina en "Todo OK" y los tests unitarios
  siguen en verde.

## Assumptions

- La plataforma del video la elige el autor; basta con que el enlace sea público o "cualquiera
  con el enlace".
