# Implementation Plan: README, DECISIONES.md y entregables

**Branch**: `011-readme-decisiones-entregables` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-readme-decisiones-entregables/spec.md`

## Summary

`README.md` y `DECISIONES.md` en la raíz; guiones de chat de los seis casos y guion de grabación
en `demo/`; `scripts/empaquetar.py` genera el `.zip` de Code Defense a partir de un clon del
repositorio (solo lo versionado, con `.git`) y lo verifica (nombres prohibidos, credenciales,
datos con forma real con el mismo detector del hook, tamaño ≤ 50 MB). La verificación del
ecosistema comprueba README y `DECISIONES.md`. Se valida desde un clon limpio y cronometrado.

## Technical Context

**Language/Version**: Markdown; Python 3.12 (biblioteca estándar) para el empaquetado.

**Primary Dependencies**: ninguna nueva (`zipfile`, `subprocess`, `git`).

**Storage**: N/A.

**Testing**: pytest (`scripts/test_empaquetar.py`; se agrega `scripts` a `testpaths`),
`verificar_ecosistema.sh`, prueba manual desde clon limpio y guiones en el chat.

**Target Platform**: máquina del evaluador (Linux/macOS/WSL con uv y Claude Code).

**Project Type**: documentación y herramienta de empaquetado.

**Constraints**: DECISIONES ≤ ~1.000 palabras; `.zip` ≤ 50 MB sin archivos de entorno, secretos ni
dependencias; sin datos con forma real.

**Scale/Scope**: 2 documentos, 6 guiones + 1 guion de grabación, 1 script con sus tests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| I–II | No toca el agente ni los hooks. ✅ |
| III. Datos ficticios y cero credenciales | El empaquetado parte de lo versionado y rechaza archivos de entorno, secretos, credenciales y datos con forma real (reutiliza `detector.py`). ✅ |
| IV. Spec primero | spec, plan y tasks antes del código; issue #11. ✅ |
| VII. Trazabilidad y simplicidad | Historial intacto en el `.zip` (clon con `.git`); un solo script con tests junto a él. ✅ |

Re-evaluación tras el diseño: sin cambios.

## Project Structure

### Documentation (this feature)

```text
specs/011-readme-decisiones-entregables/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── entregables.md
└── tasks.md
```

### Source Code (repository root)

```text
README.md                      # arranque del evaluador en < 5 min
DECISIONES.md                  # 11 necesidades → mecanismo, ubicación, razón
demo/
├── GUION_VIDEO.md             # orden, comandos y qué debe verse (≤ 5 min)
└── c1_mensaje_ejemplo.txt … c6_fuera_de_politica.txt
scripts/
├── empaquetar.py              # .zip de Code Defense + verificaciones
└── test_empaquetar.py
scripts/verificar_ecosistema.sh  # sección README/DECISIONES
pyproject.toml                 # testpaths += "scripts"
```

**Structure Decision**: `demo/` en la raíz porque lo usa el evaluador y el autor al grabar; el
guion del #8 (`specs/008-interfaz-chat/guiones/ejemplo.txt`) queda como evidencia de esa feature.

## Complexity Tracking

Sin violaciones.
