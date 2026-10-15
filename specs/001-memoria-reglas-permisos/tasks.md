---

description: "Tareas de implementación: memoria del equipo, reglas por ruta y permisos"
---

# Tasks: Memoria del equipo, reglas por ruta y permisos

**Input**: Design documents from `specs/001-memoria-reglas-permisos/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/configuracion.md](./contracts/configuracion.md),
[quickstart.md](./quickstart.md)

**Tests**: la spec no pide TDD. La verificación es el script estático
`scripts/verificar_ecosistema.sh` (plan § Testing) y los escenarios manuales M1–M12 del
quickstart. Cada historia agrega sus comprobaciones al script.

**Organization**: tareas agrupadas por historia de usuario para implementar y verificar cada
una de forma independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario a la que pertenece (US1–US4)

---

## Phase 1: Setup

**Purpose**: estructura mínima que usan todas las historias.

- [ ] T001 Crear las carpetas `scripts/`, `src/agent/` y `.claude/rules/` en la raíz del repositorio
- [ ] T002 Crear `scripts/verificar_ecosistema.sh` (bash, `set -euo pipefail`, ejecutable) con funciones `ok`/`falla` que acumulan errores y terminan con código 1 si hubo alguno; sin comprobaciones todavía

---

## Phase 2: Foundational

**Purpose**: prerrequisitos compartidos.

- [ ] T003 Verificar que `.gitignore` incluya `.env`, `.env.*`, `!.env.example`, `secrets/`, `CLAUDE.local.md` y `.claude/settings.local.json` (contrato § `.gitignore`); completar lo que falte en `.gitignore`

**Checkpoint**: estructura y exclusiones listas; las historias pueden empezar.

---

## Phase 3: User Story 1 - Convenciones del equipo al clonar (Priority: P1) 🎯 MVP

**Goal**: un clon limpio entrega las convenciones del equipo y la constitución sin configurar nada.

**Independent Test**: quickstart M1 y M2; el script confirma el import y la longitud.

- [ ] T004 [US1] Escribir `CLAUDE.md` en la raíz según contrato § `CLAUDE.md`: "≤ 60 líneas", línea `@.specify/memory/constitution.md` en su propia línea y fuera de bloques de código, stack y comandos (`uv sync`, `uv run pytest`, `uv run pytest -m e2e`, arranque del chat), estructura (`src/mcp_server`, `src/agent`, `src/chat`, `data/`, `specs/`), flujo Spec Kit por ticket con rama por feature y PR con `Closes #N`, y dónde va lo personal; sin duplicar principios de la constitución
- [ ] T005 [US1] Agregar a `scripts/verificar_ecosistema.sh` las comprobaciones: existe `CLAUDE.md`, tiene ≤ 60 líneas y contiene una línea exacta `@.specify/memory/constitution.md`

**Checkpoint**: US1 verificable por sí sola.

---

## Phase 4: User Story 2 - Preferencias personales aisladas (Priority: P1)

**Goal**: lo personal no se versiona ni afecta al equipo.

**Independent Test**: quickstart M3.

- [ ] T006 [P] [US2] Agregar a `scripts/verificar_ecosistema.sh` una comprobación con `git check-ignore` de que `CLAUDE.local.md` y `.claude/settings.local.json` están ignorados
- [ ] T007 [US2] Documentar en `CLAUDE.md` (sección "Lo personal", una o dos líneas) que las preferencias van en `CLAUDE.local.md`, `.claude/settings.local.json` o `~/.claude/CLAUDE.md`, manteniendo el archivo en "≤ 60 líneas"

**Checkpoint**: US2 verificable por sí sola.

---

## Phase 5: User Story 4 - Secretos fuera del alcance del asistente (Priority: P1)

**Goal**: Claude Code no puede leer ni editar archivos de entorno ni secretos; `.env.example` sí.

**Independent Test**: quickstart M7–M12.

- [ ] T008 [P] [US4] Crear `.claude/settings.json` con `"$schema": "https://json.schemastore.org/claude-code-settings.json"` y `permissions.deny` exactamente con las reglas de research.md § R4 (`Read(./.env)`, `Read(./.env.*)`, `Read(**/.env)`, `Read(**/.env.*)`, `Read(!.env.example)`, `Read(!**/.env.example)`, `Read(./secrets/**)`, `Edit(./.env)`, `Edit(./.env.*)`, `Edit(**/.env)`, `Edit(**/.env.*)`, `Edit(./secrets/**)`); sin credenciales, sin hooks ni MCP (issues #2 y #3)
- [ ] T009 [P] [US4] Crear `.env.example` en la raíz con "solo nombres de variables, sin valores": `ANTHROPIC_API_KEY=` y `GITHUB_PAT=`
- [ ] T010 [US4] Agregar a `scripts/verificar_ecosistema.sh`: `.claude/settings.json` es JSON válido (`python3 -m json.tool`), contiene las reglas deny de `.env`, `.env.*` y `secrets/**`, y `.env.example` no tiene valores después de `=`

**Checkpoint**: US4 verificable por sí sola.

---

## Phase 6: User Story 3 - Guías que se cargan solo donde aplican (Priority: P2)

**Goal**: reglas de tests y de contrato MCP por ruta, y guía de subdirectorio del agente.

**Independent Test**: quickstart M4–M6.

- [ ] T011 [P] [US3] Crear `.claude/rules/tests.md` con frontmatter `paths:` en lista YAML (`"**/test_*.py"`, `"**/conftest.py"`) y el contenido de contrato § `tests.md`: test junto al módulo como `test_<módulo>.py`, pytest, unitarios sin red ni API key, e2e con `@pytest.mark.e2e`, datos solo ficticios (tarjetas por últimos 4 dígitos), afirmar sobre llamadas a herramientas y no solo sobre texto
- [ ] T012 [P] [US3] Crear `.claude/rules/mcp-tools.md` con frontmatter `paths:` en lista YAML (`"src/mcp_server/**"`) y el contenido de contrato § `mcp-tools.md`: cuándo `buscar_cliente` vs `verificar_identidad`, qué hacer con varias coincidencias, formato de error `{"error": {"tipo": TRANSITORIO|VALIDACION|NEGOCIO|PERMISOS, "reintentable": bool, "mensaje": str}}`, búsqueda vacía no es error, datos solo ficticios
- [ ] T013 [P] [US3] Crear `src/agent/CLAUDE.md` según contrato § `src/agent/CLAUDE.md`: por qué existe; reglas 1 y 2 con hooks `PreToolUse` del SDK que leen el estado de sesión y los datos del core, nunca los argumentos del modelo; estado verificado solo por `PostToolUse` exitoso de `verificar_identidad`; ciclo por razón de parada; subagente con contexto explícito; handoff autocontenido
- [ ] T014 [US3] Agregar a `scripts/verificar_ecosistema.sh`: ambas reglas existen y su frontmatter declara `paths:`; existe `src/agent/CLAUDE.md`

**Checkpoint**: todas las historias verificables.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T015 Ejecutar `bash scripts/verificar_ecosistema.sh` y corregir hasta que todo esté en `OK` con código de salida 0
- [ ] T016 Ejecutar los escenarios manuales M1–M12 de `specs/001-memoria-reglas-permisos/quickstart.md`, registrar el resultado de cada uno en una tabla al final de ese archivo y limpiar los archivos de prueba (`.env`, `secrets/`, archivos personales)
- [ ] T017 Confirmar que ningún archivo nuevo contiene credenciales ni datos con forma real (`git diff main --stat` y revisión del contenido)

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003)** → historias.
- **US1 (T004–T005)** primero: crea `CLAUDE.md`, que US2 (T007) amplía.
- **US2** depende de T004 solo por T007; T006 es independiente.
- **US4** y **US3** son independientes de US1/US2 y entre sí.
- Las tareas que tocan `scripts/verificar_ecosistema.sh` (T005, T006, T010, T014) se hacen en
  secuencia porque editan el mismo archivo.
- **Polish (T015–T017)** al final.

## Parallel Opportunities

```text
# Tras el checkpoint de Foundational, en paralelo:
T004  CLAUDE.md                  (US1)
T008  .claude/settings.json      (US4)
T009  .env.example               (US4)
T011  .claude/rules/tests.md     (US3)
T012  .claude/rules/mcp-tools.md (US3)
T013  src/agent/CLAUDE.md        (US3)
```

## Implementation Strategy

1. **MVP**: Setup + Foundational + US1 → un clon ya recibe convenciones y constitución.
2. **Seguridad**: US4 inmediatamente después; es P1 y un riesgo de falta grave.
3. **US2** (aislamiento personal) y **US3** (guías por ruta) completan la feature.
4. Verificar con el script y el quickstart antes de abrir el PR.
