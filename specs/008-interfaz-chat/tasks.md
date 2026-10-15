---

description: "Tareas de implementación: interfaz de chat"
---

# Tasks: Interfaz de chat que hace evidentes las acciones

**Input**: `specs/008-interfaz-chat/` ([plan](./plan.md), [spec](./spec.md),
[research](./research.md), [quickstart](./quickstart.md))

**Tests**: requeridos (FR-009). TDD; sin red.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Declarar `rich>=13` en `dependencies` y agregar `"src/chat"` a `packages` del wheel en `pyproject.toml`; `uv sync`; crear `src/chat/__init__.py` y `src/chat/__main__.py` (llama a `app.main()`)

## Phase 2: User Story 2 - Acciones evidentes (P1) 🎯

- [X] T002 [US2] Escribir `src/chat/test_indicadores.py`: cada fila del mapeo de research R2 produce su indicador (tipo, etiqueta, detalle con monto `$1.250.000`, `•••• 4821`, número de caso y causa, regla del `negado`); varios eventos conservan el orden; `resumen()` cuenta bloqueos, disputas, escalamientos y negaciones; un evento desconocido no rompe (indicador secundario genérico)
- [X] T003 [US2] Implementar `src/chat/indicadores.py` (`Indicador`, `desde_eventos`, `resumen`, `formato_monto`); hacer pasar T002

## Phase 3: User Story 1 - Conversar turno a turno (P1)

- [X] T004 [P] [US1] Escribir `src/chat/test_vista.py` con `Console(record=True)`: la bienvenida menciona datos ficticios y `/salir`; el mensaje del cliente y la respuesta del agente llevan etiquetas distintas ("Cliente", "Agente Banco Andino"); los indicadores principales aparecen con su etiqueta en mayúsculas y los secundarios también; el resumen lista las acciones
- [X] T005 [US1] Implementar `src/chat/vista.py`; hacer pasar T004
- [X] T006 [US1] Escribir `src/chat/test_app.py` con un agente falso (devuelve `Turno` con eventos): `conversar` muestra cada mensaje, la respuesta y los indicadores; ignora mensajes vacíos; termina con `/salir` o al acabar las entradas y muestra el resumen; `main()` con un agente que lanza `AgenteNoDisponible` muestra el mensaje y devuelve código 1 sin traza; `leer_guion` devuelve una línea por mensaje ignorando vacías
- [X] T007 [US1] Implementar `src/chat/app.py` (`conversar`, `leer_guion`, `main` con `argparse --guion`, `Console.status` mientras responde, `KeyboardInterrupt` → resumen) según research R3; hacer pasar T006

## Phase 4: User Story 3 - Demo reproducible (P2)

- [X] T008 [US3] Crear `specs/008-interfaz-chat/guiones/ejemplo.txt` (mensaje de ejemplo + fecha de nacimiento) y actualizar `CLAUDE.md` (comando del chat ya no es "objetivo")

## Phase 5: Polish

- [X] T009 Ejecutar `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, `bash scripts/verificar_ecosistema.sh`
- [ ] T010 Verificación en vivo F1–F3 (F2 y F3 con guion); registrar en `quickstart.md`
- [ ] T011 Cerrar el ticket con `/abrir-pr 8`

## Dependencies

T001 → T002→T003 → T004→T005 → T006→T007 → T008 → T009–T011.
