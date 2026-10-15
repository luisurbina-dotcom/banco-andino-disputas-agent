---

description: "Tareas de implementación: hooks de desarrollo"
---

# Tasks: Hooks de desarrollo

**Input**: Design documents from `specs/002-hooks-desarrollo/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/hooks.md](./contracts/hooks.md),
[quickstart.md](./quickstart.md)

**Tests**: la spec los exige (FR-011). Para cada hook, el test se escribe antes que el hook y
debe fallar primero. Los tests MUST generar en tiempo de ejecución cualquier número que pase
Luhn (edge case de la spec): ningún literal válido en los archivos de test.

**Organization**: por historia de usuario. Todos los archivos de hooks viven en `.claude/hooks/`.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Crear `pyproject.toml` con uv: proyecto `banco-andino-disputas`, `requires-python = ">=3.12"`, grupo de desarrollo con `ruff` y `pytest`; `[tool.pytest.ini_options]` con `testpaths = ["src", ".claude/hooks"]` y marcador `e2e`; `[tool.ruff]` con `line-length = 100`, `target-version = "py312"` y reglas `E,F,I,UP,B`; ejecutar `uv sync` para generar `uv.lock`
- [X] T002 Confirmar que `uv run pytest --collect-only` recoge tests de `.claude/hooks/` (research R10) con un test trivial temporal; si no, ajustar la configuración

---

## Phase 2: Foundational

**⚠️ CRITICAL**: las historias dependen de esta fase.

- [X] T003 Crear `.claude/hooks/comun.py`: `leer_evento()` (JSON de stdin), `bloquear(hook, motivo)` (escribe `[<hook>] <motivo>` en stderr y sale con 2), `raiz_repo()` (`$CLAUDE_PROJECT_DIR` o `git rev-parse --show-toplevel`), `texto_nuevo(evento)` (`content` de Write, `new_string` de Edit, `edits[].new_string` de MultiEdit) y el decorador/función `ejecutar_seguro(hook, fn)` que ante cualquier excepción llama a `bloquear` con "Error interno: <tipo>. Se bloquea por seguridad." (research R4); solo biblioteca estándar, compatible con 3.10
- [X] T004 Crear `.claude/hooks/conftest.py` con la fixture `correr_hook(nombre, evento, env=None, cwd=None)` que ejecuta `python3 .claude/hooks/<nombre>.py` con el JSON en stdin y devuelve `returncode` y `stderr`; y el helper `tarjeta_valida(prefijo, largo)` que completa el dígito verificador de Luhn en tiempo de ejecución

**Checkpoint**: infraestructura de hooks y de tests lista.

---

## Phase 3: User Story 1 - Ningún dato con forma real entra al repositorio (P1) 🎯 MVP

**Goal**: bloquear tarjetas válidas por Luhn y documentos con etiqueta; permitir últimos 4 dígitos, montos y `FIC-`.

**Independent Test**: `uv run pytest .claude/hooks/test_detector.py .claude/hooks/test_datos_ficticios.py`; quickstart V1–V4.

- [X] T005 [P] [US1] Escribir `.claude/hooks/test_detector.py`: `luhn_valido` con números generados; detecta tarjetas de 13, 16 y 19 dígitos, también agrupadas con espacios o guiones; no detecta números que no pasan Luhn, "terminada en 4821", `$1.250.000`, `1250000`; detecta cada etiqueta (`cédula`, `cedula`, `CC:`, `c.c.`, `NIT`, `Pasaporte No.`, `documento`, en mayúsculas y minúsculas) seguida de un número de 6 a 10 dígitos **construido en tiempo de ejecución** (con y sin puntos de miles; ningún literal con forma de documento en el archivo); no detecta `FIC-` seguido de dígitos ni `documento FIC-…`; las detecciones no contienen el número
- [X] T006 [US1] Implementar `.claude/hooks/detector.py` según data-model § Deteccion y contrato § `detector.py`: `luhn_valido`, `detectar(texto) -> list[Deteccion]` con `Deteccion(tipo, inicio, sugerencia)`; tarjeta = "secuencia de 13 a 19 dígitos, admitiendo un espacio o guion entre grupos, no pegada a otros dígitos o letras, que pasa Luhn"; documento = etiqueta + "número de 6 a 10 dígitos (admite puntos de miles) que no esté precedido por FIC-"; hacer pasar T005
- [X] T007 [P] [US1] Escribir `.claude/hooks/test_datos_ficticios.py`: Write con tarjeta generada → exit 2 y stderr con `[datos_ficticios]` sin el número; Edit con documento → exit 2; contenido limpio → exit 0; JSON inválido en stdin → exit 2 (fail-closed)
- [X] T008 [US1] Implementar `.claude/hooks/datos_ficticios.py` (PreToolUse `Edit|Write`) con `comun.ejecutar_seguro`, `comun.texto_nuevo` y `detector.detectar`; mensajes exactos del contrato § `datos_ficticios.py`; hacer pasar T007

**Checkpoint**: US1 funcional y probada.

---

## Phase 4: User Story 2 - No se escribe código sin especificación (P1)

**Goal**: bloquear cambios en `src/` y `data/` sin feature activa completa.

**Independent Test**: `uv run pytest .claude/hooks/test_spec_primero.py`; quickstart V5–V7.

- [X] T009 [P] [US2] Escribir `.claude/hooks/test_spec_primero.py` usando un repo git temporal (`tmp_path`, `git init`, `CLAUDE_PROJECT_DIR` apuntando a él): en `main` editar `src/x.py` → exit 2 con "no es una feature"; rama `999-prueba` sin carpeta → exit 2 listando `spec.md, plan.md, tasks.md`; rama con solo `spec.md` → exit 2 listando `plan.md, tasks.md`; rama completa → exit 0; `data/y.json` sigue la misma regla; `src/agent/CLAUDE.md`, `specs/...`, `README.md` y rutas fuera del repo → exit 0
- [X] T010 [US2] Implementar `.claude/hooks/spec_primero.py` (PreToolUse `Edit|Write`) según data-model § FeatureActiva: rama por `git rev-parse --abbrev-ref HEAD`, patrón `^\d{3}-[a-z0-9-]+$`, código de producción = "ruta relativa al repo que empieza por src/ o data/, excepto archivos llamados CLAUDE.md"; mensajes del contrato § `spec_primero.py`; fail-closed; hacer pasar T009

**Checkpoint**: US2 funcional y probada.

---

## Phase 5: User Story 3 - Los secretos tampoco se alcanzan por la línea de comandos (P1)

**Goal**: bloquear comandos que nombran secretos; permitir `.env.example`.

**Independent Test**: `uv run pytest .claude/hooks/test_secretos_bash.py`; quickstart V8–V10.

- [X] T011 [P] [US3] Escribir `.claude/hooks/test_secretos_bash.py` parametrizado: bloquea `cat .env`, `python3 -c "open('.env')"`, `source .env`, `cp .env.local /tmp/x`, `cat src/x/.env`, `direnv allow .envrc`, `ls secrets/`, `cat config/secrets/a`, `openssl x509 -in cert.pem`, `cat id.key`, `cp .env.example .env.example.bak` (el destino es `.env.<sufijo>`), `git commit -m "actualiza .env"` (falso positivo aceptado, research R11); permite `cat .env.example`, `git status`, `uv run pytest`, `echo environment`, `grep -r envelope src/`
- [X] T012 [US3] Implementar `.claude/hooks/secretos_bash.py` (PreToolUse `Bash`) según contrato § `secretos_bash.py`: detectar menciones de `.env`, `.env.<sufijo>` (excepto exactamente `.env.example`), `.envrc`, segmento `secrets/`, archivos `*.pem` y `*.key`, como token o parte de ruta; mensaje con la categoría; fail-closed; hacer pasar T011

**Checkpoint**: US3 funcional y probada.

---

## Phase 6: User Story 4 - El código queda formateado después de cada edición (P2)

**Goal**: formatear y autocorregir archivos `.py` tras cada edición.

**Independent Test**: `uv run pytest .claude/hooks/test_formatear.py`; quickstart V11.

- [X] T013 [P] [US4] Escribir `.claude/hooks/test_formatear.py`: un `.py` temporal mal formateado con un import sin usar queda formateado y sin el import (exit 0); un `.py` con un problema no autocorregible (nombre indefinido) → exit 2 con la salida de ruff en stderr y el archivo conserva la edición; un `.md` → exit 0 sin cambios; ruta inexistente → exit 0; con `PATH` sin uv → exit 0 y aviso en stderr
- [X] T014 [US4] Implementar `.claude/hooks/formatear.py` (PostToolUse `Edit|Write`) según contrato § `formatear.py` y research R8: `uv run --quiet ruff format` y `uv run --quiet ruff check --fix` desde la raíz del repo; nunca bloquea por error interno (no usa fail-closed: sale 0 con aviso); hacer pasar T013

**Checkpoint**: las cuatro historias funcionan de forma aislada.

---

## Phase 7: Integración y Polish

- [X] T015 Agregar el bloque `hooks` a `.claude/settings.json` exactamente como contrato § Registro (con `timeout` y `"onFailure": "block"` en los de bloqueo), conservando `permissions` sin cambios; validar JSON (requiere aprobación del responsable: es la configuración de equipo)
- [X] T016 Actualizar `CLAUDE.md` (sección Stack y comandos) para indicar que `uv sync` y `uv run pytest` ya funcionan, manteniendo ≤ 60 líneas, y que `bash scripts/verificar_ecosistema.sh` siga en OK (requiere aprobación del responsable)
- [X] T017 Ejecutar `uv run pytest -q` y `uv run ruff check .` y `uv run ruff format --check .`; todo en verde y la suite en < 10 s (SC-005); medir el tiempo de cada hook de bloqueo con una entrada típica (`time python3 .claude/hooks/<hook>.py < evento.json`) y confirmar < 300 ms (SC-006, plan)
- [X] T018 Ejecutar la verificación en vivo V1–V12 de `specs/002-hooks-desarrollo/quickstart.md` en sesiones nuevas de Claude Code (incluida la confirmación de `onFailure`, research R4: si la versión instalada no la reconoce, quitar la clave de `.claude/settings.json` y documentar que el fail-closed queda solo en el `try/except`), registrar resultados en una tabla al final del quickstart y limpiar los artefactos de prueba
- [ ] T019 Revisión independiente con un subagente de solo lectura sin el contexto de esta sesión sobre `git diff main...HEAD` contra spec y contrato; registrar hallazgos y resolución en `specs/002-hooks-desarrollo/review.md`
- [ ] T020 Revisión de cumplimiento de los principios I–IV sobre el diff; agregar el resultado a `specs/002-hooks-desarrollo/review.md`
- [ ] T021 Cerrar el ciclo: PR de `002-hooks-desarrollo` hacia `main` con `Closes #2`, issue #2 a In review y comentario de avance (especificado, decidido, pendiente)

---

## Dependencies & Execution Order

- Setup (T001–T002) → Foundational (T003–T004) → historias.
- En cada historia: test → implementación (T005→T006, T007→T008, etc.). T008 depende de T006.
- US1, US2, US3 y US4 son independientes entre sí tras Foundational.
- T015 (registro) después de que los cuatro hooks pasen sus tests: registrar un hook roto
  bloquearía todas las ediciones de la sesión.
- T016–T021 en orden.

## Parallel Opportunities

```text
Tras Foundational, en paralelo (archivos distintos):
T005 test_detector.py   T009 test_spec_primero.py   T011 test_secretos_bash.py   T013 test_formatear.py
Luego:
T006 detector.py        T010 spec_primero.py        T012 secretos_bash.py        T014 formatear.py
```

## Implementation Strategy

1. **MVP**: Setup + Foundational + US1 (datos ficticios): es el riesgo de falta grave.
2. US3 (secretos) y US2 (spec primero), ambas P1.
3. US4 (formateo).
4. Registro en settings (T015) solo con todo en verde; luego verificación en vivo, revisiones y PR.
