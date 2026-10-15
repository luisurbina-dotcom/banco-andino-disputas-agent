# Implementation Plan: Automatización del ciclo de tickets y revisiones antes del PR

**Branch**: `003-automatizacion-github` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-automatizacion-github/spec.md`
(issue [#3](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/3))

## Summary

Piezas versionadas de Claude Code que automatizan el ciclo del ticket y las revisiones:

| Pieza | Tipo | Necesidad | Rol |
|---|---|---|---|
| `.mcp.json` → `github` | Servidor MCP (remoto oficial) | 10 | Issues, PR y Project (toolset `projects`) con token por variable de entorno |
| `/siguiente-ticket` | Comando | 10 | Todo → In progress, rama, `/speckit-specify` con el issue, comentario |
| `/abrir-pr` | Comando | 8, 9, 10 | Revisiones → PR `Closes #N` → In review → comentario |
| `sincronizar-ticket` | Skill (`allowed-tools` solo MCP de GitHub, `argument-hint`) | 10 | Cambiar estado en el Project y comentar en el issue |
| `revisar-cumplimiento` | Skill (`context: fork`, `allowed-tools`, `argument-hint`) | 9 | Corre aislada y delega en `compliance-auditor` |
| `code-reviewer` | Subagente de solo lectura | 8 | Revisa el diff contra spec y contrato |
| `compliance-auditor` | Subagente de solo lectura | 9 | Principios I–IV y reglas 1–5 con evidencia |

Los comandos orquestan; la skill de sincronización encapsula todo lo que toca GitHub; los
subagentes revisan sin poder modificar. Detalles en [research.md](./research.md).

## Technical Context

**Language/Version**: Markdown con frontmatter YAML (comandos, skills, subagentes) y JSON
(`.mcp.json`). Sin código Python de producción.

**Primary Dependencies**: Claude Code ≥ 2.1 (comandos, skills, subagentes, MCP); servidor MCP
remoto oficial de GitHub; Spec Kit (`/speckit-specify`).

**Storage**: GitHub (issues, PR, Project #1). Resultados de revisión en `specs/<feature>/review.md`.

**Testing**: extensión de `scripts/verificar_ecosistema.sh` (estructura, frontmatter, ausencia de
credenciales) + verificación en vivo del ciclo completo con el ticket #4 como caso real.

**Target Platform**: Claude Code en Linux/macOS/WSL2 con `GITHUB_PAT` exportado en el entorno.

**Project Type**: configuración de herramientas de desarrollo.

**Performance Goals**: N/A (flujos interactivos).

**Constraints**: ninguna credencial versionada; subagentes sin herramientas de escritura; los
textos hacia GitHub viajan por MCP (no por shell) para no chocar con `secretos_bash`.

**Scale/Scope**: 1 servidor MCP, 2 comandos, 2 skills, 2 subagentes, ajustes a
`verificar_ecosistema.sh` y `CLAUDE.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | `compliance-auditor` verifica las reglas 1–5 y marca NO CUMPLE si 1 o 2 no están en hooks. | ✅ |
| II. Garantizado, no sugerido | Las restricciones de los revisores son de configuración (`tools`/`allowed-tools`), no instrucciones. El bloqueo del PR ante ALTA/NO CUMPLE es una instrucción del comando: se acepta porque decide sobre juicio humano, no sobre un invariante de seguridad. | ✅ |
| III. Datos ficticios y cero credenciales | `.mcp.json` usa `${GITHUB_PAT}`; el script de verificación comprueba que no hay tokens. | ✅ |
| IV. Spec primero | `/siguiente-ticket` arranca siempre por `/speckit-specify`; `spec_primero.py` sigue protegiendo `src/` y `data/`. | ✅ |
| VII. Calidad y trazabilidad | Revisión independiente y de cumplimiento antes de cada PR; estados y comentarios automáticos. | ✅ |

**Re-check post-diseño**: ✅ sin violaciones; no aplica Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/003-automatizacion-github/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── piezas.md        # Frontmatter, entradas, salidas y pasos de cada pieza
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
.mcp.json                                   # github (este ticket); banco (issue #4)
.claude/
├── settings.json                           # + enabledMcpjsonServers (si aplica, R2)
├── commands/
│   ├── siguiente-ticket.md
│   └── abrir-pr.md
├── skills/
│   ├── sincronizar-ticket/SKILL.md
│   └── revisar-cumplimiento/SKILL.md
└── agents/
    ├── code-reviewer.md
    └── compliance-auditor.md
scripts/verificar_ecosistema.sh             # + comprobaciones de esta feature
CLAUDE.md                                   # + flujo con los comandos
```

**Structure Decision**: todo vive en `.claude/` y `.mcp.json` en la raíz porque es configuración
de equipo que llega con el clon (necesidad 1). `compliance-auditor`, `revisar-cumplimiento` y el
hook `datos_ficticios` son candidatos al plugin del issue #10, así que no dependen de rutas
específicas de este repo más allá de `specs/` y la constitución.

## Complexity Tracking

No aplica.
