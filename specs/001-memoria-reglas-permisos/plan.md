# Implementation Plan: Memoria del equipo, reglas por ruta y permisos

**Branch**: `001-memoria-reglas-permisos` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-memoria-reglas-permisos/spec.md`
(issue [#1](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/1))

## Summary

Configurar el ecosistema base de Claude Code para que el equipo comparta convenciones sin
configurar nada y lo personal quede aislado. Se resuelve con la jerarquía nativa de memoria
(CLAUDE.md raíz que importa la constitución, CLAUDE.md de subdirectorio en `src/agent/`),
dos reglas con alcance por ruta en `.claude/rules/` y una política de permisos versionada en
`.claude/settings.json` que deniega la lectura y edición de secretos. Las decisiones de
sintaxis y precedencia están en [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12 (proyecto gestionado con uv). Esta feature no escribe código
Python; solo configuración y documentación.

**Primary Dependencies**: Claude Code (memoria `CLAUDE.md`, `.claude/rules/`,
`.claude/settings.json`).

**Storage**: N/A (archivos versionados en el repositorio).

**Testing**: script de verificación `scripts/verificar_ecosistema.sh` (estructura, frontmatter,
JSON válido, `.gitignore`) más los escenarios manuales de [quickstart.md](./quickstart.md) para
lo que solo se observa dentro de una sesión de Claude Code.

**Target Platform**: Linux, macOS y WSL2 con Claude Code ≥ 2.1.

**Project Type**: configuración de herramientas de desarrollo para un proyecto CLI/agente.

**Performance Goals**: CLAUDE.md raíz ≤ 60 líneas (SC-005) para no gastar contexto en cada
sesión.

**Constraints**: ninguna credencial ni dato con forma real en estos archivos (principio III);
nada de lo personal versionado.

**Scale/Scope**: 1 CLAUDE.md raíz, 1 CLAUDE.md de subdirectorio, 2 reglas por ruta,
1 settings de equipo, 1 plantilla `.env.example`, 1 script de verificación.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo respeta esta feature | Estado |
|---|---|---|
| I. Reglas de negocio | El CLAUDE.md raíz importa la constitución; `src/agent/CLAUDE.md` recuerda que las reglas 1 y 2 van en hooks del SDK. No implementa reglas todavía. | ✅ |
| II. Garantizado, no sugerido | La protección de secretos usa `permissions.deny` (determinista), no una instrucción en CLAUDE.md. | ✅ |
| III. Datos ficticios y cero credenciales | `.env.example` sin valores; `.env*` y `secrets/` denegados y fuera de git. | ✅ |
| IV. Spec primero | Esta feature tiene spec, plan y tareas antes de implementar. El hook que lo hace cumplir es del issue #2. | ✅ |
| V. Contrato MCP | La regla `mcp-tools.md` codifica el contrato de descripciones y errores para quien edite el servidor. | ✅ |
| VI. Agente confiable | `src/agent/CLAUDE.md` fija ciclo por razón de parada, hooks y handoff. | ✅ |
| VII. Calidad y simplicidad | La regla `tests.md` fija tests junto al código. Solo se crean las piezas que pide el issue. | ✅ |

Sin violaciones; no aplica Complexity Tracking.

**Re-check post-diseño**: ✅ sin cambios. El diseño no introduce piezas adicionales a las del
alcance del issue.

## Project Structure

### Documentation (this feature)

```text
specs/001-memoria-reglas-permisos/
├── plan.md              # Este archivo
├── research.md          # Fase 0: sintaxis, carga y precedencia verificadas
├── data-model.md        # Fase 1: piezas de configuración y su alcance
├── quickstart.md        # Fase 1: verificación automática y manual
├── contracts/
│   └── configuracion.md # Fase 1: contrato de cada archivo (ubicación, formato, contenido)
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
CLAUDE.md                     # Convenciones de equipo + @import de la constitución
CLAUDE.local.md               # Personal, ignorado por git (no se versiona)
.env.example                  # Plantilla de variables, sin valores
.claude/
├── settings.json             # Permisos de equipo (deny de secretos)
├── settings.local.json       # Personal, ignorado por git (no se versiona)
└── rules/
    ├── tests.md              # paths: **/test_*.py, **/conftest.py
    └── mcp-tools.md          # paths: src/mcp_server/**
scripts/
└── verificar_ecosistema.sh   # Verificación estática de esta feature
src/
├── agent/
│   └── CLAUDE.md             # Guía de subdirectorio: hooks del SDK y reglas 1 y 2
├── mcp_server/               # (issue #4 y #5)
└── chat/                     # (issue #8)
data/                         # JSON ficticio (issue #4)
```

**Structure Decision**: proyecto único con paquetes por responsabilidad bajo `src/`
(`mcp_server`, `agent`, `chat`) y tests junto a cada módulo (`test_*.py` en la misma
carpeta). Esta feature solo crea `src/agent/CLAUDE.md`; los paquetes se crean en sus issues.
Los globs de las reglas apuntan a esta estructura.

**Por qué `src/agent/` y no otra carpeta para el CLAUDE.md de subdirectorio**: el agente es
donde un error de criterio rompe una regla de negocio (garantizar con hooks, no con prompt).
Esa guía solo hace falta cuando se trabaja ahí, así que no debe ocupar contexto en el resto
del repo. El servidor MCP usa una regla por ruta en vez de un CLAUDE.md porque su contrato
también aplica a los tests del servidor y se expresa mejor con un glob.

## Complexity Tracking

No aplica: el Constitution Check no tiene violaciones.
