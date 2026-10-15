# Data Model: Memoria del equipo, reglas por ruta y permisos

Esta feature no maneja datos de negocio. Sus "entidades" son piezas de configuración de
Claude Code: dónde viven, a quién aplican y cuándo se cargan.

| Pieza | Archivo | Versionada | Alcance | Cuándo se carga | Requisitos |
|---|---|---|---|---|---|
| Instrucciones de equipo | `CLAUDE.md` | Sí | Todo el repo, todo el equipo | Al iniciar la sesión en el repo | FR-001, FR-003 |
| Constitución (importada) | `.specify/memory/constitution.md` vía `@import` | Sí | Todo el repo | Junto con `CLAUDE.md` | FR-002 |
| Guía de subdirectorio | `src/agent/CLAUDE.md` | Sí | `src/agent/` | Cuando Claude trabaja con archivos de esa carpeta | FR-004 |
| Regla de tests | `.claude/rules/tests.md` | Sí | `**/test_*.py`, `**/conftest.py` | Cuando Claude trabaja con archivos que coinciden | FR-006 |
| Regla de contrato MCP | `.claude/rules/mcp-tools.md` | Sí | `src/mcp_server/**` | Cuando Claude trabaja con archivos que coinciden | FR-006 |
| Política de permisos de equipo | `.claude/settings.json` | Sí | Todo el equipo | Siempre | FR-007, FR-008 |
| Plantilla de variables | `.env.example` | Sí | Todo el equipo | — (lectura permitida) | FR-009 |
| Instrucciones personales | `CLAUDE.local.md` | No (`.gitignore`) | Un desarrollador, este repo | Al iniciar la sesión | FR-005 |
| Permisos personales | `.claude/settings.local.json` | No (`.gitignore`) | Un desarrollador, este repo | Siempre | FR-005 |
| Preferencias globales | `~/.claude/CLAUDE.md` | Fuera del repo | Un desarrollador, todos sus repos | Al iniciar cualquier sesión | FR-005 |

## Reglas de validación

- Las reglas por ruta MUST declarar `paths` en el frontmatter; una regla sin `paths` se carga
  siempre y dejaría de ser "por ruta".
- `CLAUDE.md` raíz MUST tener ≤ 60 líneas y no duplicar texto de la constitución.
- `.claude/settings.json` MUST ser JSON válido y MUST NOT contener credenciales.
- `.env.example` MUST contener solo nombres de variables, sin valores.

## Precedencia

- **Instrucciones:** se suman. Las más específicas (subdirectorio, regla por ruta, local) se
  agregan a las de equipo; ante conflicto de estilo, la más específica prevalece para quien la
  tiene.
- **Permisos:** una denegación en cualquier nivel prevalece sobre un permiso en otro nivel
  (detalle en [research.md](./research.md)). Por eso la denegación de secretos vive en el
  nivel de equipo y ningún archivo personal puede revertirla (FR-008).
