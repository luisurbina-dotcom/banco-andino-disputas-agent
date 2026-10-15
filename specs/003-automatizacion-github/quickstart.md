# Quickstart: verificar la automatización

## Prerrequisitos

- `GITHUB_PAT` exportado en una terminal interactiva (`export GITHUB_PAT="$(gh auth token)"` en
  `~/.bashrc`) con scopes `repo` y `project`. Si tu sesión de `gh` no tiene `project`:
  `gh auth refresh -s project,read:org`.
- Reiniciar Claude Code desde esa terminal después de clonar o actualizar `.mcp.json`.

## 1. Verificación estática

```bash
bash scripts/verificar_ecosistema.sh
uv run pytest -q .claude/hooks/test_solo_lectura_git.py
```

Esperado: todo OK (archivos, frontmatter con `context: fork`, `allowed-tools` y `argument-hint`,
subagentes sin Write/Edit, `.mcp.json` con `${GITHUB_PAT}` y sin tokens).

## 2. Verificación en vivo

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| A1 | `claude mcp list` | `github` conectado | FR-001 |
| A2 | `/mcp` → herramientas de `github` | Aparecen las de projects, issues y PR; se confirman los nombres de R3 | FR-001, FR-007 |
| A3 | Pedir a `code-reviewer` que cree un archivo | No tiene la herramienta | FR-004, FR-010 |
| A4 | Pedir a `code-reviewer` `git checkout -b x` | Bloqueado por `[solo_lectura_git]` | FR-004 |
| A5 | `/revisar-cumplimiento specs/003-automatizacion-github` | Tabla I–IV con evidencia, sin ensuciar la conversación | FR-005, FR-006 |
| A6 | `/siguiente-ticket` | #4 pasa a In progress, rama `004-…`, spec iniciada, comentario en #4 | US1, SC-001 |
| A7 | (al terminar #4) `/abrir-pr` | Revisiones en `review.md`, PR con `Closes #4`, #4 en In review, comentario | US4, SC-002, SC-003 |
| A8 | Fusionar el PR del #4 | #4 cerrado y en Done | US5 |

A6–A8 se completan durante el ticket #4; este ticket se cierra con A1–A5 y A6 iniciado.

## Resultados (2026-10-15)

| # | Resultado | Cómo |
|---|---|---|
| Estática | ✅ `verificar_ecosistema.sh` todo OK (20 comprobaciones nuevas); 139 tests; ruff limpio | Sesión de implementación |
| A1 | ✅ `github: https://api.githubcopilot.com/mcp/ (HTTP) - ✔ Connected` | `claude mcp list` con `GITHUB_PAT` exportado |
| A2 | ✅ Existen `projects_list`, `projects_get`, `projects_write`, `issue_read`, `add_issue_comment`, `create_pull_request`: coinciden con research R3, sin ajustes a `allowed-tools` | Sesión nueva `claude -p` |
| A3 | ✅ `code-reviewer` no tiene herramienta de escritura; su intento por Bash (`echo hola > …`) fue bloqueado | Sesión nueva, subagente |
| A4 | ✅ `git checkout -b …` bloqueado por `[solo_lectura_git]`; `git status` permitido; el archivo y la rama no existen | Sesión nueva, subagente |
| A5 | ✅ `/revisar-cumplimiento specs/003-automatizacion-github` → tabla I–IV con evidencia, veredicto CUMPLE, en contexto aislado | Sesión nueva `claude -p` |
| Sin token | ✅ Sin `GITHUB_PAT`, el servidor rechaza el header literal (caso borde de la spec) | Sesión del revisor |
| A6–A8 | ⏳ Primer uso real: `/abrir-pr` cierra este ticket (T018) y `/siguiente-ticket` abre el #4 | Sesión interactiva |
