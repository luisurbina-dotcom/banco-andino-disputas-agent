# Implementation Plan: Plugin reutilizable banca-guardrails

**Branch**: `010-plugin-banca-guardrails` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-plugin-banca-guardrails/spec.md`

## Summary

Marketplace `banco-andino` en el repo que publica el plugin `banca-guardrails` con tres piezas:
el hook de datos con forma real (copias idénticas de los scripts de este repo, con falla
cerrada), el subagente `compliance-auditor` de solo lectura por construcción (`Read, Grep, Glob`)
y la skill `revisar-cumplimiento`, que le inyecta el diff de git y lo ejecuta en un contexto
aislado. Un test detecta divergencias entre las piezas del repo y las del plugin, y la
verificación del ecosistema valida el plugin. Se prueba la instalación real en un directorio
temporal ajeno al repo.

## Technical Context

**Language/Version**: Python 3 (biblioteca estándar) para el hook; Markdown y JSON para el resto.

**Primary Dependencies**: Claude Code ≥ 2.1.295 (`onFailure`), instalado 2.1.301. Sin
dependencias nuevas.

**Storage**: N/A.

**Testing**: pytest (`.claude/hooks/test_plugin.py`), `claude plugin validate --strict`,
`scripts/verificar_ecosistema.sh` y prueba de instalación en vivo (quickstart).

**Target Platform**: proyectos de otros equipos con Claude Code (Linux/macOS/WSL con `python3`).

**Project Type**: plugin de Claude Code distribuido por marketplace en el mismo repo.

**Constraints**: no cambiar `.claude/settings.json` ni las piezas de este repo salvo el bloque de
reglas compartido; agente sin Bash ni escritura; sin datos con forma real en el repo.

**Scale/Scope**: 1 marketplace, 1 plugin, 3 piezas, 1 README.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| I–II. Reglas de negocio y garantías | No toca el agente de disputas ni sus hooks. El auditor del plugin conserva el criterio "regla 1 o 2 solo en el prompt = NO CUMPLE". ✅ |
| III. Datos ficticios | El plugin lleva el hook que hace cumplir el principio en otros repos; los números de prueba con forma real se generan en tiempo de ejecución fuera del repo. ✅ |
| IV. Spec primero | spec, plan y tasks antes del código; issue #10. ✅ |
| VII. Calidad y simplicidad | Copias verificadas por test en lugar de un mecanismo de consumo del plugin (R5); sin piezas que no pida el issue. ✅ |

Re-evaluación tras el diseño: sin cambios.

## Project Structure

### Documentation (this feature)

```text
specs/010-plugin-banca-guardrails/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── plugin.md
└── tasks.md
```

### Source Code (repository root)

```text
.claude-plugin/
└── marketplace.json                  # marketplace "banco-andino"
plugins/banca-guardrails/
├── .claude-plugin/plugin.json
├── README.md                         # instalación, uso, verificación, desinstalación
├── agents/compliance-auditor.md      # portable, Read/Grep/Glob
├── skills/revisar-cumplimiento/SKILL.md
└── hooks/
    ├── hooks.json
    ├── datos_ficticios.py            # copia idéntica de .claude/hooks/
    ├── detector.py                   # copia idéntica
    └── comun.py                      # copia idéntica
.claude/agents/compliance-auditor.md  # solo se delimita el bloque de reglas del banco
.claude/hooks/test_plugin.py          # divergencias + hook del plugin funciona en sitio
scripts/verificar_ecosistema.sh       # nueva sección: plugin y marketplace válidos
```

**Structure Decision**: el plugin vive en `plugins/` para que el marketplace pueda crecer con más
plugins; el test de sincronización vive junto a la fuente de verdad (`.claude/hooks/`), que ya
está en `testpaths`.

## Complexity Tracking

Sin violaciones.
