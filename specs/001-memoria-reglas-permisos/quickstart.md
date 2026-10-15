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
| M4 | Pedir "lee src/agent/test_x.py" (o cualquier `test_*.py`) y luego `/context` | La regla `tests.md` aparece cargada | US3, SC-004 |
| M5 | En una sesión nueva, pedir "lee README.md" y luego `/context` | Ni `tests.md` ni `mcp-tools.md` aparecen | US3, SC-004 |
| M6 | Pedir "lee un archivo de src/agent/" | Se carga `src/agent/CLAUDE.md` | US3 |
| M7 | Crear `.env` con `X=1` desde la terminal; pedir a Claude "lee .env" | Denegado por permisos | US4, SC-002 |
| M8 | Pedir "ejecuta cat .env" | Denegado | US4 |
| M9 | Pedir "edita secrets/clave.txt" | Denegado | US4 |
| M10 | En `settings.local.json` poner `"allow": ["Read(./.env)"]` y repetir M7 | Sigue denegado | FR-008 |
| M11 | Pedir "lee .env.example" | Se permite | FR-009 |
| M12 | Ejecutar `/permissions` | Se ven las reglas deny del proyecto | US4 |

Al terminar, borrar `.env`, `secrets/` y los archivos personales de prueba.

## Fuera de alcance de esta verificación

- Leer `.env` desde un script arbitrario (Python, Node): se cubre con hook en el issue #2.
