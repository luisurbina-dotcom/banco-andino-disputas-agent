# Feature Specification: README, DECISIONES.md y entregables

**Feature Branch**: `011-readme-decisiones-entregables`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#11](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/11): "[Docs] README, DECISIONES.md y entregables". Dejar listos los entregables de la prueba: README para correr el agente y los tests en menos de 5 minutos con enlaces al Project y al video de funcionamiento; `DECISIONES.md` (máximo dos páginas) con el mecanismo elegido para cada necesidad del ecosistema y por qué; video de funcionamiento (≤ 5 min) con los casos obligatorios; `.zip` para Code Defense con `.git`, sin dependencias instaladas ni `.env` (≤ 50 MB). Criterio: un evaluador corre el agente siguiendo solo el README.

## User Scenarios & Testing *(mandatory)*

Los usuarios son el evaluador de la prueba (lee el README, mira el video, abre el Project y
recibe el `.zip`) y el autor, que graba los videos y sube el `.zip`.

### User Story 1 - Correr el agente y los tests solo con el README (Priority: P1)

Un evaluador clona el repositorio (o descomprime el `.zip`), sigue el README y en menos de 5
minutos tiene los tests en verde y una conversación con el agente en la interfaz de chat.

**Why this priority**: es el criterio de aceptación del issue y el primer contacto del evaluador.

**Independent Test**: en un clon limpio, seguir solo el README, medir el tiempo y comprobar que
los tests pasan y que el chat responde.

**Acceptance Scenarios**:

1. **Given** una máquina con los requisitos que lista el README, **When** el evaluador ejecuta los
   pasos en orden, **Then** los tests unitarios pasan y el chat arranca y responde en menos de 5
   minutos.
2. **Given** el README, **When** el evaluador busca cómo correr los casos end-to-end, el guion de
   demo o instalar el plugin, **Then** encuentra un comando para cada uno.
3. **Given** el README, **When** el evaluador busca el Project y el video de funcionamiento,
   **Then** encuentra ambos enlaces.
4. **Given** que falta un requisito (por ejemplo, Claude Code sin autenticar), **When** se sigue el
   README, **Then** el README dice qué hacer.

---

### User Story 2 - Entender las decisiones del ecosistema en dos páginas (Priority: P1)

Un evaluador lee `DECISIONES.md` y, para cada una de las 11 necesidades del ecosistema, sabe qué
mecanismo se eligió, dónde está y por qué (incluida la alternativa descartada cuando aporta).

**Why this priority**: entregable obligatorio y base de la sustentación (35 % de la nota).

**Independent Test**: comprobar que el documento cubre las 11 necesidades con mecanismo,
ubicación y razón, y que no supera dos páginas.

**Acceptance Scenarios**:

1. **Given** `DECISIONES.md`, **When** se buscan las necesidades 1 a 11, **Then** cada una tiene
   mecanismo, ubicación en el repo y justificación.
2. **Given** el documento, **When** se mide su extensión, **Then** cabe en dos páginas.
3. **Given** el documento, **When** se contrasta con el repositorio, **Then** cada pieza nombrada
   existe en la ubicación indicada.

---

### User Story 3 - Paquete para Code Defense (Priority: P1)

El autor genera con un comando el `.zip` para Code Defense: repositorio completo con `.git`,
README, `DECISIONES.md` y artefactos de Spec Kit; sin dependencias instaladas, sin `.env` ni
credenciales y con un tamaño ≤ 50 MB.

**Why this priority**: entregable obligatorio; un `.env` o credencial dentro es falta grave.

**Independent Test**: generar el `.zip`, inspeccionar su contenido y su tamaño.

**Acceptance Scenarios**:

1. **Given** el repositorio, **When** se ejecuta el comando de empaquetado, **Then** se obtiene un
   `.zip` que contiene `.git`, README, `DECISIONES.md` y `specs/`.
2. **Given** el `.zip`, **When** se inspecciona, **Then** no contiene entornos virtuales,
   cachés, archivos de entorno, archivos de secretos ni archivos personales ignorados por git.
3. **Given** el `.zip`, **When** se mide, **Then** pesa ≤ 50 MB.
4. **Given** el `.zip` descomprimido, **When** se sigue el README, **Then** funciona igual que el
   clon (historial de git intacto).

---

### User Story 4 - Grabar el video de funcionamiento (Priority: P2)

El autor graba un video de máximo 5 minutos con el agente en la interfaz de chat corriendo los
seis casos obligatorios, apoyado en guiones listos para cada caso.

**Why this priority**: entregable obligatorio, pero lo graba una persona; aquí se deja todo
preparado para que la grabación sea reproducible y quepa en 5 minutos.

**Independent Test**: correr cada guion en el chat y comprobar que se ven los indicadores
esperados de cada caso.

**Acceptance Scenarios**:

1. **Given** los guiones de los seis casos, **When** se corre cada uno en el chat, **Then** se ven
   los recuadros de acción esperados (por ejemplo, tarjeta bloqueada, disputa abierta, escalado,
   negado, falla transitoria).
2. **Given** el guion de grabación, **When** el autor lo sigue, **Then** sabe qué comando correr
   en cada caso y en qué orden, para no pasar de 5 minutos.
3. **Given** el video publicado, **When** el autor lo enlaza, **Then** el README muestra el
   enlace (paso manual del autor).

### Edge Cases

- El video aún no está grabado al abrir el PR: el README deja un lugar claramente marcado para
  el enlace y el PR lo lista como pendiente del autor.
- El Project no es público: el README indica que debe ser visible para los evaluadores y el PR lo
  recuerda como acción del autor.
- Archivos ignorados por git con información personal (por ejemplo, notas del autor o el PDF
  del enunciado): no entran al `.zip`.
- El `.zip` se genera desde una rama con cambios sin commit: el paquete refleja solo lo
  versionado y el comando lo advierte.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El repo MUST tener un `README.md` con requisitos, instalación, tests, chat, guion de
  demo, casos end-to-end, plugin, estructura del repo, enlace al Project y enlace al video.
- **FR-002**: Siguiendo solo el README, los tests unitarios y el chat MUST quedar funcionando en
  menos de 5 minutos en una máquina con los requisitos listados.
- **FR-003**: El repo MUST tener `DECISIONES.md` que cubra las 11 necesidades del ecosistema con
  mecanismo, ubicación y justificación, en un máximo de dos páginas.
- **FR-004**: Toda pieza nombrada en `DECISIONES.md` y el README MUST existir en el repo.
- **FR-005**: El repo MUST incluir un comando que genere el `.zip` de Code Defense con `.git`,
  solo con lo versionado, y que verifique la ausencia de dependencias instaladas, archivos de
  entorno o secretos y el tamaño ≤ 50 MB.
- **FR-006**: El repo MUST incluir guiones de chat para los seis casos obligatorios y un guion de
  grabación del video de funcionamiento de máximo 5 minutos.
- **FR-007**: El README MUST indicar las acciones manuales del autor (enlazar el video, visibilidad
  del Project) sin dejarlas implícitas.
- **FR-008**: Ningún entregable MUST contener credenciales ni datos con forma real.
- **FR-009**: La verificación del ecosistema MUST comprobar que README y `DECISIONES.md` existen y
  que `DECISIONES.md` cubre las 11 necesidades.

### Key Entities

- **README**: guía de arranque para el evaluador.
- **DECISIONES.md**: necesidad → mecanismo, ubicación y razón.
- **Paquete de Code Defense**: `.zip` del repositorio versionado con `.git`.
- **Guiones de demo**: mensajes del cliente por caso, para el chat.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Desde un clon limpio, tests en verde y primera respuesta del chat en menos de 5
  minutos siguiendo solo el README.
- **SC-002**: `DECISIONES.md` cubre 11 de 11 necesidades y cabe en dos páginas (≤ 1.000 palabras
  aproximadamente).
- **SC-003**: El `.zip` pesa ≤ 50 MB y contiene 0 archivos de entorno, de secretos o de
  dependencias instaladas.
- **SC-004**: Los seis guiones producen en el chat los indicadores esperados de su caso.
- **SC-005**: El 100 % de las rutas y comandos citados en README y `DECISIONES.md` existen y
  funcionan.

## Assumptions

- La grabación y publicación de los videos (funcionamiento y defensa) y la subida del `.zip` a
  Edu Ranker son acciones del autor, fuera del alcance automatizable; aquí se dejan preparadas.
- Requisitos del evaluador: Python 3.12 con uv y Claude Code instalado y autenticado (el agente
  usa esa sesión) o `ANTHROPIC_API_KEY`.
- "Dos páginas" se aproxima a ≤ 1.000 palabras en Markdown renderizado.
- El `.zip` se genera desde el estado versionado de `main` tras fusionar este ticket.
