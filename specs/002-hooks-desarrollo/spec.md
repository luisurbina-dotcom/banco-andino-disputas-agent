# Feature Specification: Hooks de desarrollo (spec primero, datos ficticios, secretos y formateo)

**Feature Branch**: `002-hooks-desarrollo`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#2](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/2): "[Ecosistema] Hooks de desarrollo: spec primero, datos ficticios y formateo". Hacer cumplir de forma determinista los invariantes de desarrollo de la constitución (principios III, IV y VII). Necesidades del ecosistema: 4, 5, 6 y 7.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ningún dato con forma real entra al repositorio (Priority: P1)

Mientras el asistente escribe código, fixtures o documentación, intenta incluir un número de
tarjeta completo que parece real o un número de documento de identidad. La escritura se
bloquea antes de ocurrir y el asistente recibe un mensaje que explica qué detectó y cómo
expresarlo de forma ficticia (últimos 4 dígitos o formato ficticio).

**Why this priority**: un dato con apariencia real es falta grave de la prueba (principio III),
sin importar el resto de la entrega.

**Independent Test**: se le pide al asistente escribir en un archivo un número de 16 dígitos
que pasa la validación de Luhn; la escritura es rechazada. Se le pide escribir "tarjeta
terminada en 4821"; la escritura se permite.

**Acceptance Scenarios**:

1. **Given** un contenido con un número de 13 a 19 dígitos que pasa Luhn (con o sin espacios o
   guiones entre grupos), **When** el asistente intenta escribirlo o editarlo en cualquier
   archivo, **Then** la operación se bloquea con un mensaje que indica el tipo de dato y la
   alternativa ficticia.
2. **Given** un número de 13 a 19 dígitos que **no** pasa Luhn, **When** el asistente lo
   escribe, **Then** la operación se permite.
3. **Given** los últimos 4 dígitos de una tarjeta o un monto como `1.250.000`, **When** el
   asistente los escribe, **Then** la operación se permite.
4. **Given** un número de documento precedido por una etiqueta de documento (cédula, CC,
   documento, NIT, pasaporte) que no usa el formato ficticio del proyecto, **When** el
   asistente lo escribe, **Then** la operación se bloquea.
5. **Given** un documento con el formato ficticio del proyecto, **When** el asistente lo
   escribe, **Then** la operación se permite.

---

### User Story 2 - No se escribe código sin especificación (Priority: P1)

Un desarrollador le pide al asistente implementar algo directamente, sin haber pasado por
Spec Kit. El asistente no puede crear ni editar código de producción hasta que la feature
activa tenga su especificación, su plan y sus tareas.

**Why this priority**: es la necesidad 4 del ecosistema y el principio IV. Sin el bloqueo, el
ciclo Spec Kit depende de la disciplina de cada sesión.

**Independent Test**: en `main` (sin feature activa) se pide editar un archivo de `src/`; se
bloquea. En una rama de feature con `spec.md`, `plan.md` y `tasks.md`, la misma edición se
permite.

**Acceptance Scenarios**:

1. **Given** que la rama actual no corresponde a una feature (por ejemplo, `main`), **When** el
   asistente intenta crear o editar un archivo de código de producción, **Then** se bloquea
   con un mensaje que indica cómo iniciar la feature (`/speckit-specify`).
2. **Given** una rama de feature cuya carpeta en `specs/` no tiene `spec.md`, `plan.md` o
   `tasks.md`, **When** el asistente intenta editar código de producción, **Then** se bloquea
   indicando qué artefactos faltan.
3. **Given** una rama de feature con los tres artefactos, **When** el asistente edita código
   de producción, **Then** la operación se permite.
4. **Given** cualquier rama, **When** el asistente edita archivos que no son código de
   producción (especificaciones, documentación, configuración de Claude Code), **Then** la
   operación se permite.

---

### User Story 3 - Los secretos tampoco se alcanzan por la línea de comandos (Priority: P1)

El asistente intenta leer el archivo de variables de entorno a través de un intérprete
(`python -c "open('.env')"`), cargándolo en el shell (`source .env`) o con cualquier otro
comando que lo nombre. El comando se bloquea antes de ejecutarse.

**Why this priority**: es la necesidad 6 y cierra el límite conocido del issue #1: la política
de permisos bloquea las herramientas de archivos y los comandos de lectura comunes, pero no
otros comandos que nombran el archivo.

**Independent Test**: se pide ejecutar `python3 -c "print(open('.env').read())"` y se bloquea;
se pide `cat .env.example` y se permite.

**Acceptance Scenarios**:

1. **Given** un comando que menciona un archivo de entorno (`.env`, `.env.local`, `.envrc`,
   en cualquier ruta), **When** el asistente intenta ejecutarlo, **Then** se bloquea.
2. **Given** un comando que menciona una carpeta `secrets/` o un archivo `.pem` o `.key`,
   **When** el asistente intenta ejecutarlo, **Then** se bloquea.
3. **Given** un comando que solo menciona `.env.example`, **When** el asistente lo ejecuta,
   **Then** se permite.

---

### User Story 4 - El código queda formateado después de cada edición (Priority: P2)

Cada vez que el asistente crea o edita un archivo Python, el archivo queda formateado y con
las correcciones automáticas de estilo aplicadas, sin que nadie lo pida. Si quedan problemas
que no se pueden corregir solos, el asistente los recibe como retroalimentación.

**Why this priority**: es la necesidad 7. No afecta la seguridad, pero evita diffs ruidosos y
revisiones sobre estilo.

**Independent Test**: se le pide al asistente escribir un archivo Python mal formateado; al
terminar la escritura, el archivo en disco está formateado.

**Acceptance Scenarios**:

1. **Given** un archivo Python escrito con formato inconsistente, **When** el asistente
   termina de escribirlo o editarlo, **Then** el archivo queda formateado según la
   configuración del proyecto.
2. **Given** un problema de estilo corregible automáticamente (por ejemplo, un import sin
   usar), **When** el asistente termina la edición, **Then** queda corregido.
3. **Given** un problema que no se corrige solo, **When** el asistente termina la edición,
   **Then** recibe el detalle para corregirlo, sin que se deshaga su edición.
4. **Given** un archivo que no es Python, **When** el asistente lo edita, **Then** no se
   intenta formatear.

### Edge Cases

- Un número de tarjeta partido en grupos (`4xxx xxxx xxxx xxxx` o con guiones) se evalúa como
  un solo número.
- Los tests del propio detector necesitan números que pasan Luhn: MUST construirlos en tiempo
  de ejecución (no como literal en el archivo), o el propio bloqueo los rechazaría.
- Una edición parcial que no incluye el número completo, pero lo completa al combinarse con
  el resto del archivo: se evalúa el contenido nuevo que se escribe, no el archivo completo
  (limitación aceptada).
- Después de fusionar una feature, el puntero local de Spec Kit sigue apuntando a ella: la
  feature activa se determina por la rama actual, no por ese puntero.
- Un script que lee el archivo de entorno internamente sin nombrarlo en el comando no se puede
  detectar por texto: limitación documentada; la garantía a nivel de sistema operativo sería
  el sandbox.
- Si la herramienta de formateo no está instalada, la edición no se bloquea y el asistente
  recibe un aviso.
- Los hooks fallan de forma segura: un error interno del hook de bloqueo bloquea la operación
  con un mensaje, en lugar de permitirla en silencio.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Antes de cada escritura o edición de archivo, el sistema MUST rechazar el
  contenido nuevo que contenga un número de 13 a 19 dígitos (admitiendo espacios o guiones
  entre grupos) que pase la validación de Luhn.
- **FR-002**: El sistema MUST rechazar números de 6 a 10 dígitos precedidos por una etiqueta de
  documento de identidad (cédula, CC, documento, NIT, pasaporte, sin distinguir mayúsculas ni
  tildes), salvo que usen el formato ficticio del proyecto.
- **FR-003**: Los mensajes de rechazo MUST indicar qué se detectó y la alternativa ficticia,
  sin repetir el número completo.
- **FR-004**: Antes de crear o editar un archivo de código de producción, el sistema MUST
  verificar que la rama actual corresponda a una feature y que su carpeta en `specs/` contenga
  `spec.md`, `plan.md` y `tasks.md`; si no, MUST rechazar la operación indicando qué falta.
- **FR-005**: Es código de producción todo archivo bajo `src/` y `data/`, excepto los archivos
  `CLAUDE.md` de subdirectorio.
- **FR-006**: Antes de ejecutar un comando de shell, el sistema MUST rechazarlo si menciona un
  archivo de entorno (`.env`, `.env.*`, `.envrc`), una carpeta `secrets/` o un archivo `.pem` o
  `.key`, salvo que la única mención sea `.env.example`.
- **FR-007**: Después de cada escritura o edición de un archivo Python, el sistema MUST
  aplicar el formateo y las correcciones automáticas de estilo del proyecto.
- **FR-008**: Si quedan problemas de estilo no corregibles, el sistema MUST informarlos al
  asistente sin revertir la edición.
- **FR-009**: Los mecanismos de bloqueo MUST ser deterministas (no dependen de que el modelo
  obedezca) y MUST fallar de forma segura (ante un error interno, rechazan).
- **FR-010**: Los mecanismos MUST estar en la configuración de equipo versionada, para que
  apliquen a todo el que clone el repositorio.
- **FR-011**: Cada mecanismo MUST tener pruebas automáticas que no requieran red ni
  credenciales.

### Key Entities

- **Detección**: tipo de dato detectado (tarjeta o documento), posición y alternativa
  sugerida. Nunca guarda el valor completo.
- **Feature activa**: identificador de la rama actual (`NNN-nombre`) y su carpeta de
  especificación con sus artefactos presentes o faltantes.
- **Decisión de bloqueo**: permitir o rechazar, con el motivo dirigido al asistente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los números de tarjeta válidos por Luhn de 13 a 19 dígitos del
  conjunto de pruebas es rechazado, y el 0% de los últimos 4 dígitos y montos del conjunto de
  pruebas lo es.
- **SC-002**: El 100% de los intentos de editar código de producción sin spec, plan y tareas
  es rechazado, con un mensaje que nombra los artefactos faltantes.
- **SC-003**: El 100% de los comandos de prueba que nombran archivos de entorno, secretos o
  claves es rechazado, y `.env.example` se puede consultar.
- **SC-004**: El 100% de los archivos Python editados por el asistente queda formateado al
  terminar la edición.
- **SC-005**: Las pruebas de los mecanismos corren en menos de 10 segundos sin conexión.
- **SC-006**: Ningún bloqueo agrega más de 1 segundo perceptible a una edición normal.

## Assumptions

- El formato ficticio de documentos del proyecto es el prefijo `FIC-` seguido de dígitos (por
  ejemplo `FIC-10000001`). Lo usarán los datos del issue #4.
- Las ramas de feature siguen el patrón `NNN-nombre` de Spec Kit y su carpeta es
  `specs/NNN-nombre/`.
- La herramienta de formateo y estilo del proyecto es ruff, instalada como dependencia de
  desarrollo; esta feature crea la configuración mínima del proyecto Python para tenerla.
- La detección por texto sobre el comando de shell es una defensa adicional a los permisos del
  issue #1, no un aislamiento completo.
- Las escrituras a archivos hechas por comandos de shell (por ejemplo, redirecciones) no pasan
  por el detector de datos ni por el guardián de spec; se acepta como limitación y se compensa
  con la revisión antes del PR.
