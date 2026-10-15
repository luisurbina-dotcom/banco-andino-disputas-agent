# Implementation Plan: Hooks de desarrollo

**Branch**: `002-hooks-desarrollo` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-hooks-desarrollo/spec.md`
(issue [#2](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/2))

## Summary

Cuatro hooks de Claude Code, versionados en `.claude/hooks/` y registrados en
`.claude/settings.json`, hacen cumplir los invariantes de desarrollo:

| Hook | Evento y matcher | Necesidad | Efecto |
|---|---|---|---|
| `datos_ficticios.py` | `PreToolUse` · `Edit\|Write` | 5 | Bloquea tarjetas válidas por Luhn y documentos con etiqueta |
| `spec_primero.py` | `PreToolUse` · `Edit\|Write` | 4 | Bloquea código de producción sin spec, plan y tareas |
| `secretos_bash.py` | `PreToolUse` · `Bash` | 6 | Bloquea comandos que nombran `.env*`, `secrets/`, `*.pem`, `*.key` |
| `formatear.py` | `PostToolUse` · `Edit\|Write` | 7 | `ruff format` + `ruff check --fix` sobre archivos `.py` |

La detección de datos ficticios vive en un módulo puro (`detector.py`) sin dependencias de
Claude Code, para probarla de forma aislada y reutilizarla en el plugin del issue #10. Se crea
además el proyecto Python (`pyproject.toml`) con ruff y pytest como dependencias de desarrollo.
Detalles y alternativas en [research.md](./research.md).

## Technical Context

**Language/Version**: Python. Hooks: solo biblioteca estándar, compatibles con 3.10+, ejecutados
con `python3`. Proyecto: Python 3.12 gestionado con uv.

**Primary Dependencies**: hooks de Claude Code (stdin JSON, códigos de salida). Desarrollo:
ruff, pytest.

**Storage**: N/A.

**Testing**: pytest. Tests unitarios del detector y de cada hook (invocando el script con un
JSON en stdin, como lo hace Claude Code). Sin red ni credenciales.

**Target Platform**: Linux, macOS y WSL2 con Claude Code ≥ 2.1, `python3` y uv.

**Project Type**: herramientas de desarrollo (scripts de hook) + configuración del proyecto Python.

**Performance Goals**: cada hook de bloqueo responde en < 300 ms (SC-006); suite de tests < 10 s
(SC-005).

**Constraints**: fail-closed en los hooks de bloqueo; el hook de formateo nunca bloquea; ningún
mensaje repite el dato completo detectado; los tests no contienen literales que pasen Luhn.

**Scale/Scope**: 4 hooks, 1 módulo común, ~5 archivos de test, `pyproject.toml`, ajuste de
`.claude/settings.json`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | No toca las reglas del banco (son hooks del SDK, issue #6). | ✅ N/A |
| II. Garantizado, no sugerido | Los cuatro invariantes se hacen cumplir con hooks deterministas, no con instrucciones. | ✅ |
| III. Datos ficticios y cero credenciales | `datos_ficticios.py` y `secretos_bash.py` lo hacen cumplir; los tests generan los números válidos en tiempo de ejecución. | ✅ |
| IV. Spec primero | `spec_primero.py` lo hace cumplir. Esta feature tiene spec, plan y tareas antes del código. | ✅ |
| V. Contrato MCP | N/A. | ✅ N/A |
| VI. Agente confiable | N/A. | ✅ N/A |
| VII. Calidad y simplicidad | Tests junto al código; formateo automático; solo biblioteca estándar en los hooks. | ✅ |

**Nota de arranque (huevo y gallina)**: `spec_primero.py` protege `src/` y `data/`; los hooks
viven en `.claude/hooks/`, fuera de esas rutas, así que esta feature se puede implementar con
sus propios hooks activos.

**Re-check post-diseño**: ✅ sin violaciones; no aplica Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/002-hooks-desarrollo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hooks.md          # Entrada (stdin), salida (exit code, stderr) y registro de cada hook
├── checklists/requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
pyproject.toml                    # Proyecto uv: Python 3.12, dev: ruff, pytest; config ruff y pytest
uv.lock
.claude/
├── settings.json                 # + bloque "hooks" (se conserva permissions)
└── hooks/
    ├── comun.py                  # Leer stdin, bloquear (exit 2), fail-closed, raíz del repo
    ├── detector.py               # Puro: Luhn, tarjetas, documentos con etiqueta, formato FIC-
    ├── test_detector.py
    ├── datos_ficticios.py        # PreToolUse Edit|Write
    ├── test_datos_ficticios.py
    ├── spec_primero.py           # PreToolUse Edit|Write
    ├── test_spec_primero.py
    ├── secretos_bash.py          # PreToolUse Bash
    ├── test_secretos_bash.py
    ├── formatear.py              # PostToolUse Edit|Write
    ├── test_formatear.py
    └── conftest.py               # Fixture: ejecutar un hook con un JSON en stdin
```

**Structure Decision**: los hooks viven en `.claude/hooks/` porque son configuración de Claude
Code del equipo, junto a `settings.json` que los registra, y no código del producto. Sus tests
van al lado (principio VII). `testpaths` de pytest incluye `.claude/hooks` explícitamente
porque pytest no recorre carpetas ocultas por defecto.

## Complexity Tracking

No aplica.
