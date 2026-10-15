---

description: "Tareas de implementación: automatización del ciclo de tickets y revisiones"
---

# Tasks: Automatización del ciclo de tickets y revisiones antes del PR

**Input**: Design documents from `specs/003-automatizacion-github/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/piezas.md](./contracts/piezas.md),
[quickstart.md](./quickstart.md)

**Tests**: tests automáticos solo para el hook `solo_lectura_git.py` (código ejecutable). El resto
son piezas de configuración: se verifican con `scripts/verificar_ecosistema.sh` y en vivo
(quickstart A1–A8).

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Crear las carpetas `.claude/commands/`, `.claude/agents/`, `.claude/skills/sincronizar-ticket/` y `.claude/skills/revisar-cumplimiento/`

---

## Phase 2: Foundational (MCP de GitHub y hook de solo lectura)

**⚠️ CRITICAL**: las historias dependen de esta fase.

- [X] T002 Crear `.mcp.json` en la raíz exactamente como contrato § `.mcp.json` (`type: "http"`, URL remota oficial, `Authorization: "Bearer ${GITHUB_PAT}"`, `X-MCP-Toolsets: "context,repos,issues,pull_requests,projects"`), sin tokens literales
- [X] T003 Agregar `"enabledMcpjsonServers": ["github"]` a `.claude/settings.json` conservando `permissions` y `hooks` (requiere aprobación del responsable; research R2)
- [X] T004 [P] Escribir `.claude/hooks/test_solo_lectura_git.py`: permite `git diff main...HEAD`, `git log --oneline -5`, `git show HEAD:x`, `git status`, `git ls-files`, `git rev-parse HEAD`, `git merge-base main HEAD`, `git branch --show-current`; bloquea `git checkout -b x`, `git push`, `git commit`, `git diff > f`, `git diff; rm -rf x`, `git log | sh`, `git show $(cmd)`, `rm x`, `python3 x.py`, `git branch -D x`; evento sin comando → exit 2
- [X] T005 Implementar `.claude/hooks/solo_lectura_git.py` según contrato § Hook (subcomandos permitidos, sin metacaracteres `; | & > < $( \``, fail-closed con `comun.ejecutar_seguro`); hacer pasar T004

**Checkpoint**: MCP configurado y hook de solo lectura probado.

---

## Phase 3: User Story 2 - Revisión independiente (P1) 🎯

**Goal**: subagente revisor que no puede modificar nada.

**Independent Test**: quickstart A3–A4.

- [X] T006 [US2] Crear `.claude/agents/code-reviewer.md` según contrato § `code-reviewer`: `tools: Read, Grep, Glob, Bash`, `model: inherit`, `hooks.PreToolUse` con matcher `Bash` → `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/solo_lectura_git.py"` (`onFailure: block`); instrucciones: revisar `git diff main...HEAD` contra `specs/<feature>/spec.md` y `contracts/`, sin contexto previo, salida en tabla con severidad y veredicto

---

## Phase 4: User Story 3 - Revisión de cumplimiento (P1)

**Goal**: auditoría aislada de principios y reglas del banco.

**Independent Test**: quickstart A5.

- [X] T007 [P] [US3] Crear `.claude/agents/compliance-auditor.md` con la misma restricción de herramientas y hook que T006; instrucciones: principios I–IV y reglas 1–5 cuando apliquen, evidencia `archivo:línea`, "regla 1 o 2 implementada sin hook PreToolUse del SDK → NO CUMPLE", veredicto global
- [X] T008 [US3] Crear `.claude/skills/revisar-cumplimiento/SKILL.md` según contrato: `context: fork`, `agent: compliance-auditor`, `background: false`, `argument-hint: "<carpeta-spec>"`, `allowed-tools: Read Grep Glob Bash`; cuerpo con `$ARGUMENTS` como carpeta de la feature

---

## Phase 5: User Story 1 - Tomar el siguiente ticket (P1)

**Goal**: Todo → In progress, rama, spec desde el issue y comentario, sin pasos manuales.

**Independent Test**: quickstart A6.

- [X] T009 [US1] Crear `.claude/skills/sincronizar-ticket/SKILL.md` según contrato: `argument-hint: "<issue> <estado|comentar> [texto]"`, `allowed-tools` con solo las herramientas del MCP `github` de projects e issues (nombres de research R3), constantes del Project y pasos para cambiar estado (agregar el item si falta) y para comentar
- [X] T010 [US1] Crear `.claude/commands/siguiente-ticket.md` según contrato § `/siguiente-ticket` (pasos 1–7), con `description` y `argument-hint: "[número-de-issue]"`

---

## Phase 6: User Story 4 - Abrir el PR y sincronizar (P1)

**Goal**: revisiones obligatorias, PR con `Closes #N`, In review y comentario.

**Independent Test**: quickstart A7 (durante el ticket #4).

- [X] T011 [US4] Crear `.claude/commands/abrir-pr.md` según contrato § `/abrir-pr` (pasos 1–6), incluyendo la regla de bloqueo de research R8 y que el cuerpo del PR y los comentarios se envían por MCP (research R7)

---

## Phase 7: User Story 5 + Integración y Polish

- [X] T012 [US5] Documentar en `CLAUDE.md` (sección Flujo de trabajo) el uso de `/siguiente-ticket` y `/abrir-pr` y que la fusión la hace una persona (Done por workflow), manteniendo ≤ 60 líneas (requiere aprobación del responsable)
- [X] T013 Extender `scripts/verificar_ecosistema.sh` con una sección "003": existen las 7 piezas; los subagentes no declaran `Write` ni `Edit` en `tools` y declaran el hook `solo_lectura_git.py`; entre las skills propias aparecen `context: fork`, `allowed-tools` y `argument-hint`; los comandos tienen `description`; `.mcp.json` es JSON válido, usa `${GITHUB_PAT}` y no contiene `ghp_`, `github_pat_` ni `gho_`
- [X] T014 Ejecutar `bash scripts/verificar_ecosistema.sh`, `uv run pytest -q` y `uv run ruff check .`; todo en verde
- [X] T015 Verificación en vivo A1–A5 (tras reiniciar Claude Code con `GITHUB_PAT`): confirmar los nombres de herramientas de R3 y ajustar `allowed-tools` de `sincronizar-ticket` si difieren; registrar resultados en `quickstart.md`
- [X] T016 Revisión independiente con el nuevo `code-reviewer` sobre `git diff main...HEAD`; registrar en `specs/003-automatizacion-github/review.md`
- [X] T017 Revisión de cumplimiento con `/revisar-cumplimiento specs/003-automatizacion-github`; agregar a `review.md`
- [X] T018 Cerrar el ciclo con el propio `/abrir-pr` (primer uso real): PR con `Closes #3`, #3 a In review, comentario de avance

---

## Dependencies & Execution Order

- T001 → T002–T005. T005 después de T004 (TDD).
- T006 y T007 dependen de T005 (usan el hook). T008 depende de T007.
- T009 depende de T002–T003 (MCP). T010 depende de T009. T011 depende de T006, T008 y T009.
- T012–T014 al final; T015 requiere reiniciar Claude Code; T016–T018 en orden.

## Parallel Opportunities

```text
T004 test_solo_lectura_git.py  |  T002 .mcp.json
T006 code-reviewer.md          |  T007 compliance-auditor.md   (tras T005)
```

## Implementation Strategy

1. MCP + hook de solo lectura (fundación).
2. Revisores (US2, US3): se usan ya en este mismo ticket (T016–T017).
3. Sincronización y comandos (US1, US4).
4. Cerrar el #3 con `/abrir-pr` como primera prueba real; el #4 arranca con `/siguiente-ticket`.
