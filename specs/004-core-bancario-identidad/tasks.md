---

description: "Tareas de implementación: core bancario simulado e identificación"
---

# Tasks: Core bancario simulado — datos ficticios e identificación del cliente

**Input**: Design documents from `specs/004-core-bancario-identidad/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/herramientas.md](./contracts/herramientas.md),
[quickstart.md](./quickstart.md)

**Tests**: requeridos (criterio de aceptación del issue y FR-012). TDD: cada test antes de su
implementación. Todos sin red ni API key.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Agregar `fastmcp>=4,<5` a `dependencies` en `pyproject.toml`, `[build-system]` hatchling y `[tool.hatch.build.targets.wheel] packages = ["src/mcp_server"]`; ejecutar `uv sync` y confirmar `uv run python -c "import fastmcp, mcp_server"`
- [X] T002 Crear `src/mcp_server/__init__.py` (docstring del paquete) y `src/mcp_server/__main__.py` que llama a `servidor.main()`

---

## Phase 2: Foundational (errores y datos)

**⚠️ CRITICAL**: todas las historias dependen de esta fase.

- [X] T003 [P] Escribir `src/mcp_server/test_errores.py`: `ErrorCore` expone `tipo`, `codigo`, `reintentable`, `mensaje`; `a_dict()` devuelve exactamente `{"error": {"tipo", "codigo", "reintentable", "mensaje"}}`; un `tipo` fuera de `TRANSITORIO|VALIDACION|NEGOCIO|PERMISOS` lanza `ValueError`
- [X] T004 Implementar `src/mcp_server/errores.py` (`ErrorCore(Exception)` con `a_dict()` y `a_json()`); hacer pasar T003
- [X] T005 [P] Crear `data/clientes.json`, `data/tarjetas.json` y `data/transacciones.json` según data-model § Casos obligatorios: 8 clientes (`CLI-001…008`, documentos `FIC-` + 8 dígitos, fechas de nacimiento ficticias), dos "Carlos Ramírez", titular de la tarjeta `4821` con dos transacciones `dias_atras = 1` de $180.000 y $1.250.000, una transacción con `pais ≠ "CO"` y `dias_atras = 120`, transacciones ≤ $500.000 recientes, un cliente con dos tarjetas, y dos clientes distintos con una tarjeta de los mismos `ultimos4`; tarjetas solo con `ultimos4`
- [X] T006 [P] Escribir `src/mcp_server/test_datos.py`: con `BANCO_FECHA_BASE=2026-10-15` las transacciones de la 4821 tienen fecha `2026-10-14`; existe una transacción extranjera con más de 90 días; todos los documentos cumplen `^FIC-\d{8}$` y todas las tarjetas `^\d{4}$`; las referencias entre archivos son válidas; sin la variable, la fecha base es el día actual
- [X] T007 Implementar `src/mcp_server/datos.py`: `cargar(directorio=None, fecha_base=None)` lee los tres JSON de `data/` (ruta por defecto relativa al repo), resuelve `fecha = fecha_base − dias_atras` con `fecha_base` = argumento, `BANCO_FECHA_BASE` o hoy; hacer pasar T006

**Checkpoint**: errores y datos listos.

---

## Phase 3: User Story 1 + 2 - Localizar al cliente y varias coincidencias (P1) 🎯 MVP

**Goal**: búsqueda por documento, nombre y últimos 4 dígitos; ambigüedad explícita.

**Independent Test**: `uv run pytest -q src/mcp_server/test_core.py -k buscar`; quickstart B2–B5.

- [X] T008 [US1] Crear `src/mcp_server/conftest.py` con la fixture `core` (instancia de `Core` con fecha base fija `2026-10-15`; requiere un `Core` mínimo en `core.py` que se completa en T012) y un helper que lee de los datos la fecha de nacimiento correcta del titular de la 4821 (no repetida a mano)
- [X] T009 [US1] Escribir en `src/mcp_server/test_core.py` los tests de `buscar_cliente`: "4821"/`ultimos4` → 1 coincidencia del titular; documento existente → ese cliente; documento inexistente → `{"coincidencias": [], "total": 0}` sin error; ninguna coincidencia contiene `fecha_nacimiento` ni `documento`; cliente con dos tarjetas aparece una vez con ambas
- [X] T010 [US2] Agregar a `src/mcp_server/test_core.py`: "Carlos Ramírez", "carlos ramirez" y "  CARLOS   RAMÍREZ " → 2 coincidencias y `accion_sugerida` presente; con 1 coincidencia no hay `accion_sugerida`; los `ultimos4` compartidos por dos clientes devuelven 2 coincidencias con `accion_sugerida`; "Carlos" solo devuelve a todos los clientes cuyo nombre contiene esa palabra
- [X] T011 [US1] Agregar a `src/mcp_server/test_core.py` los errores: criterio vacío → `VALIDACION/CRITERIO_VACIO`; `ultimos4` "48" o "48a1" → `VALIDACION/ULTIMOS4_INVALIDO`; documento sin `FIC-` → `VALIDACION/DOCUMENTO_INVALIDO`; tipo fuera de los tres valores (llamada directa al core) → `VALIDACION/TIPO_INVALIDO`; todos `reintentable=False`
- [X] T012 [US1] Implementar en `src/mcp_server/core.py` la clase `Core(datos)` con `buscar_cliente(criterio, tipo)` según contrato § `buscar_cliente` y research R3–R4 (normalización de nombre: sin tildes, minúsculas, espacios colapsados; coincide por nombre completo o por contener todas las palabras); hacer pasar T009–T011

**Checkpoint**: búsqueda completa y probada.

---

## Phase 4: User Story 3 - Verificar la identidad (P1)

**Goal**: confirmar identidad con fecha de nacimiento, 3 intentos y bloqueo.

**Independent Test**: `uv run pytest -q src/mcp_server/test_core.py -k verificar`; quickstart B6.

- [X] T013 [US3] Agregar a `src/mcp_server/test_core.py`: fecha correcta → `verificado=True` con `id_cliente` y `nombre`; fecha incorrecta → `verificado=False`, `intentos_restantes` 2 y luego 1, y la respuesta no contiene la fecha correcta; tercer fallo y siguientes llamadas (aun con la fecha correcta) → `NEGOCIO/IDENTIDAD_BLOQUEADA` no reintentable con "analista" en el mensaje; un acierto antes del tercer fallo reinicia el contador; `CLI-999` → `VALIDACION/CLIENTE_NO_EXISTE`; fecha "15/10/1990" → `VALIDACION/FECHA_INVALIDA` sin consumir intento
- [X] T014 [US3] Implementar `Core.verificar_identidad(id_cliente, fecha_nacimiento)` según contrato y research R5 (contador en memoria por cliente); hacer pasar T013

---

## Phase 5: User Story 4 - Contrato de herramientas (P1)

**Goal**: servidor MCP con descripciones y errores del contrato.

**Independent Test**: `uv run pytest -q src/mcp_server/test_servidor.py`; quickstart B1.

- [X] T015 [US4] Escribir `src/mcp_server/test_servidor.py` con el cliente en memoria de FastMCP (`fastmcp.Client(servidor.mcp)`, tests async con anyio): el servidor lista exactamente `buscar_cliente` y `verificar_identidad`; sus descripciones contienen "NO confirma" / "varias coincidencias" / "lista vacía" y "UN cliente" / "obligatoria" / "3 fallos"; `tipo` es un enum de 3 valores; una llamada válida devuelve el `dict` del core como contenido estructurado; un error de validación del core responde con `is_error=True` y texto JSON con la forma del contrato; un `tipo` fuera del enum lo rechaza el propio esquema de FastMCP antes del core (test que fija ese comportamiento, research R10)
- [X] T016 [US4] Implementar `src/mcp_server/servidor.py`: `mcp = FastMCP("banco", instructions=…)` con las instrucciones del contrato; herramientas `buscar_cliente` y `verificar_identidad` con las descripciones exactas del contrato que delegan en un `Core` creado al importar (datos de `datos.cargar()`); `ErrorCore` → `ToolError(error.a_json())`; `main()` llama a `mcp.run()` (stdio); hacer pasar T015

---

## Phase 6: User Story 5 + Integración y Polish

- [X] T017 [US5] Agregar el servidor `banco` a `.mcp.json` según contrato § Registro, y `"banco"` a `enabledMcpjsonServers` en `.claude/settings.json` (requiere aprobación del responsable)
- [X] T018 Ejecutar `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .` y `bash scripts/verificar_ecosistema.sh`; todo en verde y la suite de `src/mcp_server` en < 5 s (SC-006)
- [X] T019 Verificación en vivo B1–B6 de `quickstart.md` (sesión nueva de Claude Code o `claude -p`); registrar resultados en `quickstart.md`
- [X] T020 Cerrar el ticket con `/abrir-pr 4` (revisión independiente, cumplimiento, PR con `Closes #4`, In review y comentario)

---

## Dependencies & Execution Order

- T001 → T002 → Foundational (T003–T007). T004 tras T003; T007 tras T005 y T006. T008 abre la Phase 3 (necesita un `Core` mínimo).
- US1+US2 (T009–T012) → US3 (T013–T014) → US4 (T015–T016) → T017–T020.

## Parallel Opportunities

```text
T003 test_errores.py   |   T005 data/*.json   |   T006 test_datos.py
```

## Implementation Strategy

1. Errores y datos (fundación). 2. Búsqueda (MVP del core). 3. Verificación.
4. Servidor MCP. 5. Registro, verificación en vivo y `/abrir-pr`.
