# Feature Specification: Memoria del equipo, reglas por ruta y permisos

**Feature Branch**: `001-memoria-reglas-permisos`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#1](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/1): "[Ecosistema] CLAUDE.md, reglas por ruta y permisos del equipo". Que todo desarrollador que clone el repo reciba las convenciones del equipo sin configurar nada, sin que las preferencias personales afecten al resto. Necesidades del ecosistema: 1, 2, 3 y 6.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convenciones del equipo al clonar (Priority: P1)

Un desarrollador nuevo clona el repositorio y abre su asistente de código. Sin configurar nada,
el asistente ya conoce las convenciones del equipo: los principios de la constitución (reglas
de negocio del banco, datos ficticios, spec primero), la estructura del proyecto y cómo se
corren los tests.

**Why this priority**: es la necesidad 1 del ecosistema y la base de las demás. Sin
convenciones compartidas, cada desarrollador obtiene un comportamiento distinto del asistente.

**Independent Test**: en un clon limpio, se le pregunta al asistente por el umbral de disputa
automática y por dónde viven los tests; responde con lo que establece el equipo sin que el
desarrollador haya configurado nada.

**Acceptance Scenarios**:

1. **Given** un clon limpio del repositorio, **When** el desarrollador abre el asistente en la
   raíz, **Then** el asistente carga las convenciones del equipo y la constitución.
2. **Given** que la constitución cambia en un PR, **When** otro desarrollador actualiza su
   clon, **Then** el asistente usa la versión nueva sin que nadie copie texto entre archivos.

---

### User Story 2 - Preferencias personales aisladas (Priority: P1)

Un desarrollador quiere que el asistente le responda de forma más breve y le permita algunos
comandos sin preguntar. Lo configura en sus archivos personales y sus compañeros no ven ni
heredan esas preferencias.

**Why this priority**: es la necesidad 2 del ecosistema. Mezclar lo personal con lo del equipo
contamina el historial y cambia el comportamiento para todos.

**Independent Test**: se crean los archivos de preferencias personales y se comprueba que el
control de versiones no los detecta como cambios para publicar.

**Acceptance Scenarios**:

1. **Given** un desarrollador con preferencias personales de instrucciones y de permisos,
   **When** revisa los cambios pendientes del repositorio, **Then** esos archivos no aparecen.
2. **Given** una preferencia personal que contradice una convención de estilo del equipo,
   **When** el desarrollador trabaja, **Then** su preferencia aplica solo en su máquina.

---

### User Story 3 - Guías que se cargan solo donde aplican (Priority: P2)

Cuando un desarrollador trabaja en archivos de tests, el asistente aplica las convenciones de
tests (ubicación junto al código, nombres, marcas de e2e). Cuando trabaja en el servidor de
herramientas del banco, aplica el contrato de herramientas (descripciones sin ambigüedad,
errores estructurados). Fuera de esas rutas, esas guías no ocupan contexto.

**Why this priority**: resuelve la necesidad 3 (tests en muchas carpetas con las mismas
convenciones) y mantiene el contexto enfocado.

**Independent Test**: se abre un archivo de test en una carpeta cualquiera y se verifica que
la guía de tests está activa; se abre un archivo de documentación y se verifica que no lo está.

**Acceptance Scenarios**:

1. **Given** un archivo de test en cualquier carpeta del proyecto, **When** el asistente lo
   lee o edita, **Then** aplica las convenciones de tests del equipo.
2. **Given** un archivo del servidor de herramientas del banco, **When** el asistente lo lee o
   edita, **Then** aplica el contrato de herramientas.
3. **Given** un archivo que no coincide con ninguna ruta de las guías, **When** el asistente
   trabaja en él, **Then** esas guías no se cargan.
4. **Given** el código del agente, **When** el asistente trabaja en esa carpeta, **Then**
   recibe las instrucciones específicas del agente (garantizar reglas de negocio con hooks).

---

### User Story 4 - Secretos fuera del alcance del asistente (Priority: P1)

Un desarrollador tiene su archivo de variables de entorno con claves de API en su máquina. El
asistente no puede leerlo ni modificarlo, aunque se le pida directamente.

**Why this priority**: es la necesidad 6 del ecosistema y el principio III de la constitución.
Una credencial expuesta es una falta grave.

**Independent Test**: se le pide al asistente que muestre o edite el archivo de entorno y la
operación es rechazada por configuración, no por decisión del modelo.

**Acceptance Scenarios**:

1. **Given** un archivo de entorno en la raíz, **When** se le pide al asistente que lo lea,
   **Then** la operación es denegada.
2. **Given** un archivo de entorno o un archivo dentro de la carpeta de secretos, **When** se
   le pide al asistente que lo modifique o lo cree, **Then** la operación es denegada.
3. **Given** la plantilla de variables de ejemplo sin valores reales, **When** el asistente la
   lee, **Then** la operación se permite.

### Edge Cases

- Variantes del archivo de entorno (`.env.local`, `.env.production`) también quedan protegidas.
- Archivos de entorno en subcarpetas también quedan protegidos.
- Un permiso personal que intente habilitar la lectura de secretos no prevalece sobre la
  denegación del equipo.
- La plantilla de ejemplo de variables (sin valores reales) sí puede leerse y versionarse.
- La guía de un subdirectorio no se carga si el desarrollador trabaja en otra parte del repo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El repositorio MUST incluir instrucciones de equipo versionadas que el asistente
  cargue automáticamente al abrirse en la raíz.
- **FR-002**: Las instrucciones de equipo MUST importar la constitución por referencia, sin
  duplicar su contenido.
- **FR-003**: Las instrucciones de equipo MUST ser breves y contener solo lo que el asistente
  no puede deducir del código: comandos, estructura, convenciones y flujo de trabajo.
- **FR-004**: El repositorio MUST incluir al menos una guía específica de subdirectorio,
  justificada, que se cargue solo al trabajar en esa carpeta (el código del agente).
- **FR-005**: Los archivos de preferencias personales (instrucciones y permisos locales) MUST
  quedar excluidos del control de versiones.
- **FR-006**: El repositorio MUST incluir al menos dos guías con alcance por ruta definidas con
  patrones glob: convenciones de tests y contrato de herramientas del servidor del banco.
- **FR-007**: La configuración de equipo versionada MUST denegar la lectura y la edición de
  archivos de entorno (en cualquier carpeta y con cualquier sufijo) y de la carpeta de secretos.
- **FR-008**: La denegación de secretos MUST prevalecer sobre cualquier permiso personal.
- **FR-009**: La plantilla de variables de ejemplo MUST poder leerse y versionarse.

### Key Entities

- **Instrucciones de equipo**: convenciones compartidas, versionadas, cargadas al abrir el
  repositorio. Importan la constitución.
- **Guía de subdirectorio**: instrucciones que aplican solo dentro de una carpeta concreta.
- **Guía por ruta**: instrucciones que aplican solo a archivos que coinciden con un patrón.
- **Preferencias personales**: instrucciones y permisos de un desarrollador, no versionados.
- **Política de permisos de equipo**: reglas versionadas de lo que el asistente puede y no
  puede hacer, que prevalecen sobre lo personal en las denegaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un desarrollador que clona el repositorio obtiene las convenciones del equipo
  con 0 pasos de configuración.
- **SC-002**: El 100% de los intentos del asistente de leer o editar archivos de entorno o de
  secretos son denegados.
- **SC-003**: Los archivos de preferencias personales aparecen como cambios para publicar en
  el 0% de los casos.
- **SC-004**: Cada guía por ruta se aplica en el 100% de los archivos que coinciden con su
  patrón y en ninguno de los que no coinciden.
- **SC-005**: Las instrucciones de equipo de la raíz caben en una pantalla (≤ 60 líneas),
  porque lo detallado vive en la constitución y en las guías por ruta.

## Assumptions

- El asistente de código del equipo es Claude Code, y su mecanismo nativo de memoria, reglas
  y permisos es el medio de configuración.
- El idioma de las instrucciones es el español, como el resto de la documentación.
- Las rutas definitivas del código (servidor de herramientas, agente) siguen la estructura que
  se fije en el plan; las guías por ruta usan esos patrones.
- Los hooks que bloquean contenido con forma de datos reales, el acceso a secretos por línea
  de comandos y el formateo pertenecen al issue #2, no a este.
- La configuración de servidores MCP y la automatización de tickets pertenecen al issue #3.
