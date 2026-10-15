# Feature Specification: Plugin reutilizable banca-guardrails

**Feature Branch**: `010-plugin-banca-guardrails`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#10](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/10): "[Ecosistema] Plugin reutilizable banca-guardrails". Que otro equipo del banco pueda instalar las piezas reutilizables en su propio repositorio: plugin con manifiesto y marketplace en el repo, que empaqueta al menos un subagente (`compliance-auditor`), una skill (`revisar-cumplimiento`) y un hook (escaneo de datos con forma real), con instrucciones de instalación. Necesidad del ecosistema 11.

## User Scenarios & Testing *(mandatory)*

El usuario es otro equipo de desarrollo del banco que trabaja con Claude Code en su propio
repositorio y quiere las mismas protecciones que este proyecto sin copiar archivos a mano.

### User Story 1 - Instalar el plugin desde el marketplace del repo (Priority: P1)

Un desarrollador de otro equipo agrega el marketplace de este repositorio y, con el
administrador de plugins, instala `banca-guardrails` en su propio proyecto.

**Why this priority**: es el criterio de aceptación del issue; sin instalación no hay reutilización.

**Independent Test**: desde un directorio distinto de este repo, agregar el marketplace, instalar
el plugin y ver sus piezas listadas como disponibles.

**Acceptance Scenarios**:

1. **Given** un directorio de otro proyecto, **When** el desarrollador agrega el marketplace y
   instala `banca-guardrails`, **Then** la instalación termina sin errores y el plugin aparece
   como habilitado.
2. **Given** el plugin instalado, **When** el desarrollador lista agentes, skills y hooks,
   **Then** aparecen el subagente de cumplimiento, la skill de revisión y el hook de datos.
3. **Given** el manifiesto y el marketplace, **When** se validan con la herramienta de
   validación de plugins, **Then** no hay errores.

---

### User Story 2 - El hook bloquea datos con forma real en otro repo (Priority: P1)

En el proyecto del otro equipo, Claude intenta escribir un archivo con un número de tarjeta que
pasa la validación de Luhn o un documento con forma real.

**Why this priority**: es la protección que más riesgo evita (principio III) y la más fácil de
comprobar.

**Independent Test**: en el otro directorio, pedir a Claude que escriba un archivo con un número
con forma de tarjeta real y comprobar que la escritura se bloquea con un mensaje accionable.

**Acceptance Scenarios**:

1. **Given** el plugin instalado, **When** Claude intenta escribir un número con forma de tarjeta
   real, **Then** la escritura se bloquea y el mensaje indica usar solo los últimos 4 dígitos.
2. **Given** el plugin instalado, **When** Claude escribe datos ficticios (últimos 4 dígitos,
   documento `FIC-<dígitos>`), **Then** la escritura procede.
3. **Given** que el hook falla internamente, **When** se evalúa una escritura, **Then** la
   escritura se bloquea (falla cerrada), igual que en este repo.

---

### User Story 3 - Revisión de cumplimiento en otro repo (Priority: P2)

En el proyecto del otro equipo, un desarrollador invoca la skill de revisión de cumplimiento
sobre su feature; un subagente de solo lectura audita el cambio contra los principios y reglas
del banco y emite un veredicto con evidencia.

**Why this priority**: lleva al otro equipo la revisión antes del PR; depende de US1.

**Independent Test**: en un repo de prueba con un cambio en una rama, invocar la skill y obtener
la tabla Principio/Regla | Resultado | Evidencia con un veredicto.

**Acceptance Scenarios**:

1. **Given** el plugin instalado y una rama con cambios, **When** se invoca la skill con la
   carpeta de la feature, **Then** el subagente devuelve la tabla y la línea de veredicto.
2. **Given** un proyecto que tiene su propia constitución o guía de reglas, **When** se audita,
   **Then** el auditor la usa como fuente de verdad junto con las reglas del banco.
3. **Given** el subagente de cumplimiento, **When** audita, **Then** no puede modificar archivos
   del proyecto.

---

### User Story 4 - Una sola fuente de verdad en este repo (Priority: P2)

Quien mantiene este repositorio sigue usando las mismas piezas (hook, subagente y skill) sin
tener dos copias que puedan divergir.

**Why this priority**: principio VII (simplicidad); dos copias divergen y la evidencia de la
prueba perdería coherencia.

**Independent Test**: comprobar que cada pieza existe una sola vez (o que una verificación
automática falla si las copias divergen) y que el flujo `/abrir-pr` sigue funcionando.

**Acceptance Scenarios**:

1. **Given** el repo con el plugin, **When** se edita el detector de datos, **Then** el cambio
   alcanza tanto a este proyecto como al plugin, o una verificación automática avisa la
   divergencia.
2. **Given** el plugin, **When** se corren los tests y la verificación del ecosistema, **Then**
   siguen en verde.

---

### User Story 5 - Instrucciones de instalación (Priority: P3)

El otro equipo encuentra en el repo instrucciones breves: cómo agregar el marketplace, instalar,
qué incluye, cómo comprobar que funciona y cómo desinstalar.

**Why this priority**: alcance del issue; sin instrucciones el plugin es difícil de adoptar.

**Independent Test**: seguir las instrucciones desde cero en otro directorio y llegar a US1–US3.

**Acceptance Scenarios**:

1. **Given** las instrucciones, **When** una persona las sigue, **Then** instala el plugin y
   comprueba el hook sin consultar el código.

### Edge Cases

- El proyecto destino no tiene una constitución de Spec Kit: el auditor usa la guía del proyecto
  (`CLAUDE.md`) y las reglas del banco, y lo dice en su informe.
- El proyecto destino no usa `main` como rama base: la skill acepta indicar la base o detectarla.
- El proyecto destino ya tiene su propio hook de datos: ambos corren; el plugin no reemplaza la
  configuración del equipo.
- El intérprete disponible en el destino: el hook no depende de dependencias externas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El repo MUST incluir un marketplace que publique el plugin `banca-guardrails`.
- **FR-002**: El plugin MUST tener un manifiesto válido con nombre, versión, descripción y autor.
- **FR-003**: El plugin MUST incluir el subagente `compliance-auditor`, la skill
  `revisar-cumplimiento` y un hook `PreToolUse` sobre ediciones que bloquee datos con forma de
  tarjeta o documento real.
- **FR-004**: El hook del plugin MUST tener el mismo comportamiento que el de este repo
  (detección, mensaje accionable y falla cerrada) y no depender de rutas de este proyecto.
- **FR-005**: El subagente MUST ser de solo lectura en el proyecto destino.
- **FR-006**: La skill y el subagente MUST funcionar en un proyecto distinto de este: fuente de
  verdad del proyecto destino si existe, reglas del banco como base y rama base configurable.
- **FR-007**: Cada pieza MUST tener una única fuente de verdad en el repo, o una verificación
  automática MUST detectar la divergencia.
- **FR-008**: El plugin MUST instalarse desde otro directorio con el administrador de plugins
  y sus piezas MUST funcionar allí (criterio de aceptación del issue).
- **FR-009**: El repo MUST incluir instrucciones de instalación, uso, verificación y
  desinstalación.
- **FR-010**: Los tests existentes y la verificación del ecosistema MUST seguir en verde, y la
  verificación del ecosistema MUST comprobar el plugin (manifiesto y piezas).
- **FR-011**: Ningún archivo del plugin MUST contener credenciales ni datos con forma real.

### Key Entities

- **Marketplace**: catálogo en el repo que lista el plugin y dónde encontrarlo.
- **Plugin `banca-guardrails`**: manifiesto y piezas (subagente, skill, hook).
- **Proyecto destino**: repositorio de otro equipo donde se instala el plugin.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Desde un directorio ajeno a este repo, el plugin se instala en menos de 2 minutos
  siguiendo las instrucciones.
- **SC-002**: En ese directorio, el 100 % de las escrituras de prueba con forma de tarjeta real
  se bloquean y el 100 % de las ficticias proceden.
- **SC-003**: La skill instalada devuelve un veredicto con evidencia en un repo de prueba.
- **SC-004**: La validación del plugin y del marketplace termina sin errores.
- **SC-005**: Cero copias divergentes de las piezas: una edición en un solo lugar basta.

## Assumptions

- "Otro equipo del banco" comparte las reglas de negocio del banco; las convenciones de datos
  ficticios (`FIC-<dígitos>`, últimos 4 dígitos) son las del banco.
- El marketplace se publica desde este mismo repositorio (público); el otro equipo puede
  agregarlo por ruta local o por el repositorio de GitHub.
- Los hooks y comandos propios de este proyecto que no pide el issue (spec primero, secretos,
  formateo, `/siguiente-ticket`, `/abrir-pr`) no entran en el plugin.
- La verificación de instalación "desde otro directorio" se hace en un directorio temporal con
  un repo de prueba.
