---

description: "Tareas de implementación: agente de disputas y garantías de las reglas 1 y 2"
---

# Tasks: Agente de disputas — ciclo agéntico y garantías de las reglas 1 y 2

**Input**: Design documents from `specs/006-agente-hooks-reglas/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/agente.md](./contracts/agente.md),
[quickstart.md](./quickstart.md)

**Tests**: requeridos (criterio del issue: "tests de los hooks sin API key"). TDD.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Agregar `claude-agent-sdk>=0.2,<0.3` a `dependencies` y `"src/agent"` a `packages` del wheel (con el mismo `exclude` de tests) en `pyproject.toml`; `uv sync`; confirmar `uv run python -c "import claude_agent_sdk, agent"`
- [X] T002 Crear `src/agent/__init__.py` (docstring) y `src/agent/conftest.py` con la fixture `estado` (`EstadoSesion` con datos cargados con fecha base 2026-10-15) y, en `test_garantias.py` (no en conftest: hay varios `conftest.py` en el repo), helpers que arman entradas de hook (`entrada_pre(nombre, args)`, `entrada_post(nombre, args, respuesta)`) con el formato verificado en research R3 (`mcp__banco__<nombre>`, `tool_response` como texto JSON)

---

## Phase 2: User Story 2 - Ninguna operación sin identidad verificada (P1) 🎯

**Independent Test**: `uv run pytest -q src/agent/test_garantias.py -k regla1`.

- [X] T003 [US2] Escribir en `src/agent/test_garantias.py` (async con anyio): sin verificación, `pre_reglas` niega `consultar_transacciones`, `iniciar_disputa` y `bloquear_tarjeta` con el motivo exacto de la regla 1 (contrato) y registra un evento `negado`; permite `buscar_cliente`, `verificar_identidad` y `escalar_a_analista`; tras `post_resultado` con `'{"verificado":true,"id_cliente":"CLI-001",...}'` permite operar sobre `CLI-001` y niega sobre `CLI-002`; con `verificado:false` sigue negando; una respuesta con `verificado:true` pero otro `id_cliente` no marca; un error `IDENTIDAD_BLOQUEADA` retira la verificación tanto si llega como `PostToolUse` con el texto JSON del error como si llega como `PostToolUseFailure` (research R3: no confirmado cuál dispara el SDK; T013 lo confirma); respuestas en dict o lista de bloques también se interpretan; una respuesta ilegible no marca
- [X] T004 [US2] Implementar `src/agent/garantias.py`: `EstadoSesion` (data-model), `pre_reglas(estado)` y `post_resultado(estado)` que devuelven callbacks async `(entrada, tool_use_id, contexto) -> dict` según research R3, R4, R6, R8 (motivos exactos del contrato; fail-closed); hacer pasar T003

---

## Phase 3: User Story 3 - Ninguna disputa automática > $500.000 (P1)

**Independent Test**: `uv run pytest -q src/agent/test_garantias.py -k regla2`.

- [X] T005 [US3] Agregar a `src/agent/test_garantias.py`: verificado `CLI-001`, `iniciar_disputa` TX-0002 (1 250 000 en el core) → negado con el motivo exacto de la regla 2 aunque los argumentos traigan un campo `monto: 100` inventado; TX-0001 (180 000) → permitido; transacción de exactamente 500 000 (estado con datos de prueba) → permitido; `TX-9999` → negado con el motivo de transacción desconocida; una excepción interna (estado con datos corruptos) → negado con el motivo de fallo interno
- [X] T006 [US3] Completar `pre_reglas` con la regla 2 según research R5 (monto por `id_transaccion` desde `EstadoSesion.transacciones`); hacer pasar T005

---

## Phase 4: User Story 4 - Criterio del agente (P1)

**Independent Test**: `uv run pytest -q src/agent/test_prompt.py`; quickstart D1, D3.

- [X] T007 [P] [US4] Escribir `src/agent/test_prompt.py`: `PROMPT_SISTEMA` menciona regla 3 (bloqueo inmediato sin pedir confirmación), regla 4 (persona → `escalar_a_analista` con `CLIENTE_PIDE_PERSONA` sin buscar ni consultar antes), regla 5 (`POLITICA_NO_CUBRE`/`MONTO_SUPERA_UMBRAL` → escalar), ambigüedad (pedir otro identificador, no elegir), reintento ante `TRANSITORIO`, respuesta unificada; y no contiene datos con forma real
- [X] T008 [US4] Implementar `src/agent/prompt.py` con `PROMPT_SISTEMA` según research R9; hacer pasar T007

---

## Phase 5: User Story 1 - Conversación turno a turno (P1)

**Independent Test**: `uv run pytest -q src/agent/test_agente.py`; quickstart D2, D4–D6.

- [X] T009 [US1] Escribir `src/agent/test_agente.py`: `construir_opciones(estado)` usa `PROMPT_SISTEMA`, el servidor `banco` stdio con `sys.executable -m mcp_server`, `allowed_tools` = las 6 herramientas `mcp__banco__*`, `tools == []`, `setting_sources == []`, `max_turns` sin fijar, y hooks PreToolUse/PostToolUse/PostToolUseFailure con matcher `mcp__banco__.*`; `AgenteDisputas.responder` con un cliente falso que emite `AssistantMessage` y luego `ResultMessage(stop_reason="end_turn")` devuelve `Turno` con el texto del resultado, `stop_reason`, `num_turns` y solo los eventos de ese turno
- [X] T010 [US1] Implementar `src/agent/agente.py`: `Turno`, `construir_opciones(estado, modelo=None)`, `AgenteDisputas` (async context manager sobre `ClaudeSDKClient`, `responder(texto)`) según research R2, R7, R8, R10; si la CLI no está o falla la conexión/autenticación, relanzar `AgenteNoDisponible` con un mensaje accionable (caso borde de la spec, con test); hacer pasar T009
- [X] T011 [US1] Crear `scripts/conversar.py` (quickstart): recibe mensajes por argumentos, conversa con `AgenteDisputas` e imprime por turno el texto, los eventos y `stop_reason`

---

## Phase 6: Polish

- [X] T012 Ejecutar `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .` y `bash scripts/verificar_ecosistema.sh`
- [X] T013 Verificación en vivo D1–D6 con `scripts/conversar.py` (incluida la confirmación de `tools=[]`, research R7); registrar resultados en `quickstart.md`
- [X] T014 Cerrar el ticket con `/abrir-pr 6` (el cumplimiento debe dar CUMPLE en el principio II: condición del #5)

---

## Dependencies & Execution Order

- T001 → T002 → US2 (T003–T004) → US3 (T005–T006). US4 (T007–T008) es independiente.
- US1 (T009–T011) usa `garantias.py` y `prompt.py`. T012–T014 al final.

## Parallel Opportunities

```text
T007 test_prompt.py  |  T003 test_garantias.py   (tras T002)
```

## Implementation Strategy

Garantías primero (son la condición del #5 y lo que más pesa), luego prompt, luego el agente y la
conversación real.
