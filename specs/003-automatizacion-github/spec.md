# Feature Specification: Automatización del ciclo de tickets y revisiones antes del PR

**Feature Branch**: `003-automatizacion-github`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#3](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/3): "[Ecosistema] Automatización del ciclo de tickets con GitHub MCP y revisiones antes del PR". Que el estado de los tickets se mantenga sincronizado con el avance real sin intervención manual, y que cada PR pase por revisión independiente y de cumplimiento. Necesidades del ecosistema: 8, 9 y 10.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tomar el siguiente ticket (Priority: P1)

El desarrollador le pide al asistente que tome el siguiente ticket. El asistente consulta el
backlog en GitHub, elige el primer ticket pendiente, lo marca como "en progreso", prepara la
rama de la feature, inicia la especificación usando el contenido del issue y deja un
comentario en el issue. El desarrollador no mueve nada a mano.

**Why this priority**: es el punto de entrada del ciclo (necesidad 10). Sin él, el estado del
backlog depende de la memoria de cada persona.

**Independent Test**: con al menos un ticket en Todo, se invoca el comando y se verifica en
GitHub que el ticket pasó a In progress, que existe la rama, que `specs/<feature>/spec.md`
parte del contenido del issue y que el issue recibió un comentario.

**Acceptance Scenarios**:

1. **Given** varios tickets en Todo, **When** el desarrollador invoca "siguiente ticket",
   **Then** se toma el de menor número de issue, pasa a In progress y se crea la rama
   `NNN-nombre` con su carpeta en `specs/`.
2. **Given** el ticket tomado, **When** se inicia la especificación, **Then** el insumo es el
   título y el cuerpo del issue en GitHub, y el issue recibe un comentario con la rama y el
   enlace a la especificación.
3. **Given** que no hay tickets en Todo, **When** se invoca el comando, **Then** informa que el
   backlog está vacío y no cambia nada.
4. **Given** que ya hay un ticket en In progress, **When** se invoca el comando, **Then** avisa
   y pide confirmación antes de tomar otro.

---

### User Story 2 - Revisión independiente antes del PR (Priority: P1)

Antes de abrir un PR, el código pasa por un revisor que no comparte el contexto de la sesión
que lo escribió y que no puede modificar nada. El revisor compara el cambio contra la
especificación y el contrato, y entrega hallazgos con severidad.

**Why this priority**: es la necesidad 8. Los tickets #1 y #2 la hicieron con un revisor ad hoc;
este ticket la convierte en una pieza reutilizable y versionada.

**Independent Test**: se invoca el revisor sobre una rama con un defecto conocido y se
verifica que lo reporta, que no tiene herramientas de escritura y que el resultado queda en
`specs/<feature>/review.md`.

**Acceptance Scenarios**:

1. **Given** una rama de feature con cambios, **When** se pide la revisión independiente,
   **Then** el revisor analiza el diff contra `main` y entrega una tabla de hallazgos con
   severidad y un veredicto.
2. **Given** el revisor en ejecución, **When** intenta escribir, editar o ejecutar comandos que
   modifican, **Then** no tiene esas herramientas disponibles.
3. **Given** el resultado de la revisión, **When** termina, **Then** queda registrado en
   `review.md` con la resolución de cada hallazgo.

---

### User Story 3 - Revisión de cumplimiento de las reglas del banco (Priority: P1)

Un auditor verifica que las reglas de negocio del banco y los principios de la constitución
estén implementados como se especificaron: en particular, que las reglas 1 y 2 estén
garantizadas por hooks y no solo por instrucciones, y que no haya datos con forma real ni
credenciales.

**Why this priority**: es la necesidad 9 y protege los puntos que el enunciado califica como
faltas graves.

**Independent Test**: se invoca la revisión de cumplimiento sobre una feature y se obtiene una
tabla principio por principio (y regla por regla cuando aplica) con evidencia (archivo:línea)
y un veredicto CUMPLE / NO CUMPLE.

**Acceptance Scenarios**:

1. **Given** una feature, **When** se invoca la revisión de cumplimiento con su carpeta de
   especificación, **Then** se evalúan los principios I a IV y, si la feature toca reglas de
   negocio, cada una de las reglas 1 a 5 con evidencia.
2. **Given** que una regla 1 o 2 se aplica solo con instrucciones del prompt, **When** se
   revisa, **Then** el veredicto es NO CUMPLE.
3. **Given** la revisión, **When** corre, **Then** lo hace en un contexto aislado y con
   herramientas de solo lectura, sin ensuciar la conversación principal.

---

### User Story 4 - Abrir el PR y sincronizar el ticket (Priority: P1)

Al terminar la implementación, el desarrollador pide abrir el PR. El asistente ejecuta las dos
revisiones, se detiene si hay hallazgos graves sin resolver, abre el PR con referencia de
cierre al issue, pasa el ticket a In review y comenta en el issue lo especificado, lo decidido
y lo pendiente.

**Why this priority**: cierra el ciclo de sincronización (necesidad 10) y garantiza que ningún
PR salte las revisiones (necesidades 8 y 9).

**Independent Test**: sobre una rama lista, se invoca el comando y se verifica en GitHub el PR
con "Closes #N", el ticket en In review y el comentario de avance.

**Acceptance Scenarios**:

1. **Given** una rama de feature con tareas completas, **When** se invoca "abrir PR",
   **Then** se ejecutan la revisión independiente y la de cumplimiento antes de crear el PR.
2. **Given** un hallazgo ALTA sin resolver o un NO CUMPLE, **When** se invoca el comando,
   **Then** no abre el PR y lista lo que falta resolver.
3. **Given** revisiones aprobadas, **When** se abre el PR, **Then** su descripción incluye
   `Closes #N`, el ticket pasa a In review y el issue recibe el comentario de avance.

---

### User Story 5 - Cierre automático al fusionar (Priority: P2)

Cuando una persona fusiona el PR, el issue se cierra y el ticket pasa a Done sin intervención.

**Why this priority**: ya funciona con los workflows del Project activados en #1; aquí solo se
documenta y se verifica como parte del ciclo completo.

**Independent Test**: se fusiona un PR creado por el comando y se verifica el issue cerrado y
el ticket en Done.

**Acceptance Scenarios**:

1. **Given** un PR con `Closes #N`, **When** se fusiona, **Then** el issue #N queda cerrado y
   el ticket en Done.

### Edge Cases

- El acceso a GitHub por el servidor MCP no está autenticado: el comando se detiene con
  instrucciones para configurarlo; no cambia estados por otra vía en silencio.
- El issue no está en el Project: el comando lo agrega antes de cambiar su estado.
- Textos de PR o comentarios que mencionan archivos de secretos: se envían por el servidor MCP
  (no por comandos de shell), así el hook de secretos no los bloquea.
- La rama ya existe (ticket retomado): se reutiliza en lugar de fallar.
- El revisor independiente encuentra hallazgos que el desarrollador decide aceptar: quedan
  registrados como "Aceptado" con su justificación en `review.md`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El repositorio MUST incluir la configuración versionada del servidor MCP oficial de
  GitHub con el toolset de projects habilitado, sin credenciales; el token MUST provenir de una
  variable de entorno del desarrollador.
- **FR-002**: El repositorio MUST incluir un comando versionado "siguiente ticket" que elija el
  ticket en Todo de menor número, lo pase a In progress, cree o reutilice la rama de feature,
  inicie la especificación con el contenido del issue y comente en el issue.
- **FR-003**: El repositorio MUST incluir un comando versionado "abrir PR" que ejecute la
  revisión independiente y la de cumplimiento, bloquee el PR ante hallazgos ALTA sin resolver o
  NO CUMPLE, abra el PR con `Closes #N`, pase el ticket a In review y comente en el issue.
- **FR-004**: El revisor independiente MUST ser un subagente sin herramientas de escritura ni de
  ejecución que modifique, y MUST revisar el diff contra la especificación y el contrato.
- **FR-005**: La revisión de cumplimiento MUST ser una skill que corre en contexto aislado, con
  herramientas restringidas, que recibe la carpeta de la feature como argumento y delega en un
  subagente auditor de solo lectura.
- **FR-006**: El auditor MUST evaluar los principios I a IV y, cuando aplique, las reglas de
  negocio 1 a 5, con evidencia por archivo y línea; una regla 1 o 2 sin hook MUST ser NO CUMPLE.
- **FR-007**: Los cambios de estado y los comentarios en GitHub MUST hacerse a través del
  servidor MCP de GitHub, encapsulados en una skill de sincronización reutilizable por ambos
  comandos.
- **FR-008**: Los resultados de ambas revisiones MUST quedar en `specs/<feature>/review.md`.
- **FR-009**: Entre las skills del proyecto (sin contar las de Spec Kit) MUST usarse
  `context: fork`, `allowed-tools` y `argument-hint`.
- **FR-010**: Cada subagente MUST tener herramientas restringidas a su rol.

### Key Entities

- **Ticket**: issue de GitHub con número, título, cuerpo y estado en el Project (Todo, In
  progress, In review, Done).
- **Feature**: rama `NNN-nombre` y carpeta `specs/NNN-nombre/` asociadas a un ticket.
- **Hallazgo**: severidad (ALTA, MEDIA, BAJA), ubicación, descripción, recomendación y
  resolución (Corregido, Aceptado, Pendiente).
- **Veredicto de cumplimiento**: por principio o regla: CUMPLE / NO CUMPLE / N/A con evidencia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Desde el ticket #4 en adelante, el 100% de los cambios de estado Todo → In
  progress → In review ocurren por los comandos y Done por el workflow, con 0 movimientos
  manuales.
- **SC-002**: El 100% de los PR desde #4 incluyen `Closes #N` y tienen `review.md` con revisión
  independiente y de cumplimiento.
- **SC-003**: Cada issue implementado recibe al menos 2 comentarios de avance (al iniciar y al
  abrir el PR).
- **SC-004**: Un evaluador puede reconstruir el avance de cada ticket solo mirando GitHub
  (estado en el Project, comentarios, PR y fechas).
- **SC-005**: 0 credenciales en el repositorio.

## Assumptions

- El servidor MCP de GitHub se usa en su modalidad remota oficial, autenticado con un token
  personal que cada desarrollador exporta en su entorno (por ejemplo, a partir de su sesión de
  la CLI de GitHub).
- El Project es el número 1 del usuario `luisurbina-dotcom` y su campo de estado se llama
  "Status"; estos identificadores no son secretos y pueden vivir en la configuración del
  comando.
- El orden del backlog es el número de issue: los issues se crearon en el orden de dependencia.
- La fusión del PR la hace una persona; el paso a Done lo hace el workflow del Project activado
  en el ticket #1.
- El segundo servidor MCP (core bancario) llega en el issue #4 y se agrega a la misma
  configuración.
