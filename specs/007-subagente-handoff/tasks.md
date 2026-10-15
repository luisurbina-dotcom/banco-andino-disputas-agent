---

description: "Tareas de implementación: subagente de análisis, varios asuntos y handoff"
---

# Tasks: Subagente de análisis, varios asuntos y handoff

**Input**: `specs/007-subagente-handoff/` ([plan](./plan.md), [spec](./spec.md),
[research](./research.md), [data-model](./data-model.md), [quickstart](./quickstart.md))

**Tests**: requeridos (FR y criterios del issue). TDD; sin red.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: User Story 3 - Handoff completo en el core (P1)

- [ ] T001 [US3] Agregar a `src/mcp_server/test_operaciones.py`: causa `MONTO_SUPERA_UMBRAL` o `POLITICA_NO_CUBRE` sin `id_cliente` o sin `id_transacciones` → `VALIDACION/RESUMEN_INCOMPLETO`; con ambos → caso creado; `CLIENTE_PIDE_PERSONA` e `IDENTIDAD_BLOQUEADA` siguen sin exigir transacciones
- [ ] T002 [US3] Implementar la regla en `Operaciones.escalar_a_analista` (`src/mcp_server/operaciones.py`) según research R5 y anotar la ampliación en `specs/005-operaciones-core/contracts/herramientas.md` (errores de `escalar_a_analista`); hacer pasar T001

---

## Phase 2: User Story 1 - Subagente de análisis (P1) 🎯

- [ ] T003 [P] [US1] Escribir `src/agent/test_subagente.py`: `definicion()` devuelve un `AgentDefinition` con `tools == ["mcp__banco__consultar_transacciones"]` y el prompt `PROMPT_ANALISTA`; el prompt contiene las 4 recomendaciones, el umbral de $500.000, la regla de exterior > 90 días que prevalece, "no tienes herramientas para disputar, bloquear ni escalar" y el formato de línea de research R4; sin datos con forma real
- [ ] T004 [US1] Implementar `src/agent/subagente.py` (`NOMBRE = "analista-transacciones"`, `PROMPT_ANALISTA`, `definicion()`); hacer pasar T003
- [ ] T005 [US1] Agregar a `src/agent/test_garantias.py`: `pre_delegacion` permite `subagent_type="analista-transacciones"` (evento `delegado` con el encargo) y niega `general-purpose`/`Explore` con motivo; `pre_reglas` niega a una llamada con `agent_type="analista-transacciones"` cualquier herramienta distinta de `consultar_transacciones`, y le aplica la regla 1 a su consulta (sin verificación → negado); los eventos registran `agente` (`principal` o el `agent_type`)
- [ ] T006 [US1] Implementar en `src/agent/garantias.py`: `Evento.agente`, `pre_delegacion(estado)`, la restricción del analista en `pre_reglas` y el registro de `agente` en pre/post según research R2–R3; hacer pasar T005
- [ ] T007 [US1] Actualizar `src/agent/test_agente.py`: `tools == ["Agent"]`, `"Agent"` en `allowed_tools`, `agents` con `analista-transacciones`, hook `PreToolUse` con matcher `Agent|Task` → `pre_delegacion`
- [ ] T008 [US1] Implementar en `src/agent/agente.py` las opciones de T007; hacer pasar T007

---

## Phase 3: User Story 2 + 3 - Prompt principal (P1)

- [ ] T009 [P] [US2] Agregar a `src/agent/test_prompt.py`: menciona delegar en `analista-transacciones` con `id_cliente`, `ultimos4` y cobros reportados; actuar según cada recomendación; incluir cliente y transacciones al escalar por umbral o política
- [ ] T010 [US2] Actualizar `src/agent/prompt.py` según research R6; hacer pasar T009
- [ ] T011 [US1] Mostrar `agente` en `scripts/conversar.py` (columna del evento) para distinguir al subagente

---

## Phase 4: Polish

- [ ] T012 Ejecutar `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .` y `bash scripts/verificar_ecosistema.sh`
- [ ] T013 Verificación en vivo E1–E4 de `quickstart.md`; registrar resultados
- [ ] T014 Cerrar el ticket con `/abrir-pr 7`

## Dependencies

T001→T002 · T003→T004 · T005→T006 · T007→T008 (tras T004, T006) · T009→T010 · T011 tras T006 · T012–T014 al final.
