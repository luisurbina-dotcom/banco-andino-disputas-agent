# Quickstart: verificar memoria, reglas y permisos

## Prerrequisitos

- Claude Code ≥ 2.1 y el repositorio clonado.
- Estar en la rama de la feature o en `main` después del merge.

## 1. Verificación automática (estática)

```bash
bash scripts/verificar_ecosistema.sh
```

Resultado esperado: todas las comprobaciones en `OK` y código de salida 0. Comprueba:

- Existen los archivos del [contrato](./contracts/configuracion.md).
- `CLAUDE.md` tiene ≤ 60 líneas e importa la constitución (SC-005, FR-002).
- Las dos reglas tienen `paths` en el frontmatter (FR-006).
- `.claude/settings.json` es JSON válido y deniega `.env*` y `secrets/` (FR-007).
- `.gitignore` excluye lo personal y los secretos (FR-005).
- `.env.example` no tiene valores (FR-009).

## 2. Verificación manual en una sesión de Claude Code

| # | Paso | Resultado esperado | Cubre |
|---|---|---|---|
| M1 | Abrir `claude` en la raíz y ejecutar `/memory` | Aparecen `CLAUDE.md` y la constitución importada | US1, SC-001 |
| M2 | Preguntar "¿cuál es el umbral de disputa automática?" | Responde $500.000 sin leer archivos | US1 |
| M3 | Crear `CLAUDE.local.md` y `.claude/settings.local.json`; ejecutar `git status` | No aparecen como cambios | US2, SC-003 |
| M4 | Crear desde la terminal `src/agent/test_tmp.py` (vacío); en una sesión nueva pedir "lee src/agent/test_tmp.py" y luego `/context` | La regla `tests.md` aparece cargada | US3, SC-004 |
| M5 | En una sesión nueva, pedir "lee README.md" y luego `/context` | Ni `tests.md` ni `mcp-tools.md` aparecen | US3, SC-004 |
| M6 | En una sesión nueva, pedir "lee src/agent/test_tmp.py" y después preguntar "¿qué hook establece el estado de identidad verificada?" | Responde con lo de `src/agent/CLAUDE.md` (`PostToolUse` de `verificar_identidad`). El CLAUDE.md de subdirectorio no aparece en `/context`, por eso se verifica por comportamiento | US3 |
| M7 | Crear `.env` con `X=1` desde la terminal; pedir a Claude "lee .env" | Denegado por permisos | US4, SC-002 |
| M8 | Pedir "ejecuta cat .env" | Denegado | US4 |
| M9 | Pedir "edita secrets/clave.txt" | Denegado | US4 |
| M10 | En `settings.local.json` poner `"allow": ["Read(./.env)"]` y repetir M7 | Sigue denegado | FR-008 |
| M11 | Pedir "lee .env.example" | Se permite | FR-009 |
| M12 | Ejecutar `/permissions` | Se ven las reglas deny del proyecto | US4 |
| M13 | Crear desde la terminal `src/mcp_server/tmp.py` (vacío); en una sesión nueva pedir "lee src/mcp_server/tmp.py" y luego `/context` | La regla `mcp-tools.md` aparece cargada y `tests.md` no | US3, SC-004 |

Al terminar, borrar `.env`, `secrets/`, `src/agent/test_tmp.py`, `src/mcp_server/` y los archivos personales de prueba.

## Fuera de alcance de esta verificación

- Leer `.env` desde un script arbitrario (Python, Node): se cubre con hook en el issue #2.

## Resultados de la verificación (2026-10-15)

Script estático: `bash scripts/verificar_ecosistema.sh` → 19 comprobaciones en OK, código 0.

| # | Resultado | Cómo se ejecutó |
|---|---|---|
| M1 | ⏳ Pendiente (manual) | Requiere `/memory` en una sesión interactiva |
| M2 | ✅ Responde "$500.000 COP o menos se inician automáticamente" | Sesión nueva `claude -p` sin herramientas |
| M3 | ✅ `git check-ignore` confirma ambos archivos ignorados | Script estático |
| M4 | ✅ `tests.md` se carga al leer `src/agent/test_tmp.py`, no al inicio | Sesión nueva `claude -p` (autorreporte del modelo) |
| M5 | ✅ Tras leer un archivo fuera de las rutas, ninguna regla cargada | Sesión nueva `claude -p` (autorreporte del modelo) |
| M6 | ✅ Responde "PostToolUse sobre verificar_identidad" tras leer un archivo de `src/agent/` | Sesión nueva `claude -p` |
| M7 | ✅ `Read .env` → "denied by your permission settings" | Sesión de implementación |
| M8 | ✅ `cat .env` por Bash → denegado | Sesión de implementación |
| M9 | ✅ `Write secrets/clave.txt` → denegado | Sesión de implementación |
| M10 | ⏳ Pendiente (manual) | Requiere editar `settings.local.json`; no lo hace Claude |
| M11 | ✅ `Read .env.example` → permitido (la negación funciona) | Sesión de implementación |
| M12 | ⏳ Pendiente (manual) | Requiere `/permissions` en una sesión interactiva |
| M13 | ✅ `mcp-tools.md` se carga al leer `src/mcp_server/tmp.py` | Sesión nueva `claude -p` (autorreporte del modelo) |

Hallazgos adicionales:

- `Read` de un `.env.local` anidado (`src/sub/.env.local`) también es denegado (caso borde).
- Tras la enmienda: `src/x/secrets/token.txt` y `certs/server.key` también son denegados.
- `Write .env.example` es denegado para Claude: `Read(!.env.example)` solo exceptúa la lectura.
  Decisión: se mantiene así (la plantilla la crea o edita una persona); ver tarea T009.
