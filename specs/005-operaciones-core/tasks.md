---

description: "Tareas de implementación: operaciones del core"
---

# Tasks: Operaciones del core — transacciones, disputas, bloqueo, escalamiento y fallas

**Input**: Design documents from `specs/005-operaciones-core/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/herramientas.md](./contracts/herramientas.md),
[quickstart.md](./quickstart.md)

**Tests**: requeridos (criterios del issue y FR-012). TDD; sin red ni API key.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundational (estado compartido en el Core)

- [ ] T001 Agregar a `src/mcp_server/test_core.py`: tras una verificación exitosa `core.esta_verificado(id)` es `True` y tras una fallida `False`; `programar_fallas("x", 2)` hace que `consumir_falla("x")` lance `TRANSITORIO/CORE_NO_DISPONIBLE` con `reintentable=True` dos veces y luego no lance; otra herramienta no se ve afectada; `n` negativo → `ValueError`
- [ ] T002 Implementar en `src/mcp_server/core.py`: conjunto `_verificados` (lo llena `verificar_identidad` exitosa), `esta_verificado(id_cliente)`, `programar_fallas(herramienta, n)` y `consumir_falla(herramienta)` según research R2 y R5; hacer pasar T001

**Checkpoint**: estado compartido listo.

---

## Phase 2: User Story 1 - Consultar transacciones (P1) 🎯

**Independent Test**: `uv run pytest -q src/mcp_server/test_operaciones.py -k consultar`; quickstart C1–C2.

- [ ] T003 [US1] Crear `src/mcp_server/test_operaciones.py` con fixtures `ops` (`Operaciones(core)`) y `verificado` (verifica a `CLI-001` con su fecha leída de los datos); tests de `consultar_transacciones`: sin verificar → `PERMISOS/IDENTIDAD_NO_VERIFICADA`; `CLI-001`/`4821` con `desde=hasta=2026-10-14` → 2 transacciones de 180 000 y 1 250 000 con fecha `"2026-10-14"` (texto); sin rango → últimos 30 días; rango sin datos → lista vacía; `desde > hasta` o fecha mal formada → `VALIDACION/RANGO_INVALIDO`; tarjeta de otro cliente (`CLI-001`/`7310`) → `VALIDACION/TARJETA_NO_ENCONTRADA`; con una falla programada → `TRANSITORIO` y luego responde
- [ ] T004 [US1] Crear `src/mcp_server/operaciones.py` con `Operaciones(core)` y `consultar_transacciones(id_cliente, ultimos4, desde=None, hasta=None)` según contrato y research R1, R5, R6 (orden: falla → permisos → tarjeta → rango); hacer pasar T003

---

## Phase 3: User Story 2 - Iniciar disputa (P1)

**Independent Test**: `uv run pytest -q src/mcp_server/test_operaciones.py -k disputa`; quickstart C3, C4, C8.

- [ ] T005 [US2] Agregar tests de `iniciar_disputa` según research R3: $180 000 → disputa `abierta` con `id_disputa` y el monto del core; $1 250 000 → `NEGOCIO/MONTO_SUPERA_UMBRAL` no reintentable con "analista" en el mensaje; segunda disputa de la misma transacción → `NEGOCIO/DISPUTA_EXISTENTE`; transacción en US de 120 días (`CLI-007` verificado) → `NEGOCIO/POLITICA_NO_CUBRE`; transacción de otro cliente o inexistente → `VALIDACION/TRANSACCION_NO_ENCONTRADA`; sin verificar → `PERMISOS`; límites exactos: monto 500 000 se abre y extranjera de 90 días se abre (con datos de prueba construidos en el test vía `Datos`, sin tocar `data/`); extranjera > 90 días y > 500 000 → `POLITICA_NO_CUBRE`
- [ ] T006 [US2] Implementar `Operaciones.iniciar_disputa(id_cliente, id_transaccion, motivo)` con el orden de research R3, el monto leído del core (la firma no recibe monto) y las constantes de data-model; hacer pasar T005

---

## Phase 4: User Story 3 - Bloquear tarjeta (P1)

**Independent Test**: `uv run pytest -q src/mcp_server/test_operaciones.py -k bloquear`; quickstart C5.

- [ ] T007 [P] [US3] Agregar tests de `bloquear_tarjeta`: verificado → `{"bloqueada": True, "ultimos4": "4821", "ya_estaba_bloqueada": False}` y el estado de la tarjeta queda `bloqueada`; segunda vez → `ya_estaba_bloqueada: True` sin error; tarjeta de otro cliente → `VALIDACION/TARJETA_NO_ENCONTRADA`; sin verificar → `PERMISOS`
- [ ] T008 [US3] Implementar `Operaciones.bloquear_tarjeta(id_cliente, ultimos4, motivo)`; hacer pasar T007

---

## Phase 5: User Story 4 - Escalar a analista (P1)

**Independent Test**: `uv run pytest -q src/mcp_server/test_operaciones.py -k escalar`; quickstart C6–C7.

- [ ] T009 [P] [US4] Agregar tests de `escalar_a_analista`: con `id_cliente="CLI-001"`, `id_transacciones=["TX-0002"]` y causa `MONTO_SUPERA_UMBRAL` → caso `en_cola_analista` cuyo resumen trae nombre del cliente y la transacción con fecha, monto 1 250 000, comercio y país del core; `CLIENTE_PIDE_PERSONA` sin cliente ni verificación → aceptado con `cliente: None`; descripción o acción recomendada vacías → `VALIDACION/RESUMEN_INCOMPLETO`; causa fuera de las 5 (llamada directa al core) → `VALIDACION/RESUMEN_INCOMPLETO`; id de transacción desconocido → `VALIDACION/TRANSACCION_NO_ENCONTRADA`; cliente desconocido → `VALIDACION/CLIENTE_NO_EXISTE`; los casos quedan en `core.casos` con ids correlativos
- [ ] T010 [US4] Implementar `Operaciones.escalar_a_analista(causa, descripcion, accion_recomendada, id_cliente=None, id_transacciones=None, acciones_realizadas=None)` según research R4 y data-model § Caso; hacer pasar T009

---

## Phase 6: User Story 5 + Servidor

**Independent Test**: `uv run pytest -q src/mcp_server/test_servidor.py`; quickstart C9.

- [ ] T011 [US5] Actualizar `src/mcp_server/test_servidor.py`: el servidor expone exactamente las 6 herramientas; las descripciones son exactamente las de `specs/004-…/contracts/herramientas.md` y `specs/005-operaciones-core/contracts/herramientas.md` (helper generalizado); `causa` es un enum de 5 valores; flujo por MCP verificar → consultar → disputar devuelve contenido estructurado; `MONTO_SUPERA_UMBRAL` llega como `is_error=True` con el JSON del contrato; `configurar_fallas("consultar_transacciones:1")` produce `TRANSITORIO` con `reintentable: true` y la siguiente llamada funciona; un formato inválido de configuración lanza `ValueError` con el nombre de la variable
- [ ] T012 [US5] Implementar en `src/mcp_server/servidor.py`: `ops = Operaciones(core)`, las 4 herramientas con las descripciones exactas del contrato 005 (constantes) y tipos `Literal` para `causa`; `configurar_fallas(texto)` que parsea `herramienta:N[,…]` y llama a `core.programar_fallas`; aplicarla al arrancar con `BANCO_FALLAS_TRANSITORIAS`; hacer pasar T011 (actualizar el fixture para reemplazar `core` y `ops` por test)

---

## Phase 7: Polish

- [ ] T013 Ejecutar `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .` y `bash scripts/verificar_ecosistema.sh`; suite de `src/mcp_server` < 5 s
- [ ] T014 Verificación en vivo C1–C9 de `quickstart.md` con sesiones nuevas `claude -p` (C9 con la variable de entorno); registrar resultados
- [ ] T015 Cerrar el ticket con `/abrir-pr 5`

---

## Dependencies & Execution Order

- T001 → T002 → US1 (T003–T004) → US2 (T005–T006). US3 (T007–T008) y US4 (T009–T010)
  dependen de T004 (`operaciones.py`) pero no entre sí. T011–T012 después de US1–US4.

## Parallel Opportunities

```text
T007 tests de bloqueo   |   T009 tests de escalamiento   (tras T004)
```

## Implementation Strategy

Estado compartido → consulta → disputa (núcleo de las reglas 2 y 5) → bloqueo y escalamiento →
servidor y fallas → verificación en vivo → `/abrir-pr`.
