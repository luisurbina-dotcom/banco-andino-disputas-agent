# Quickstart: verificar la automatización

## Prerrequisitos

- `GITHUB_PAT` exportado en una terminal interactiva (`export GITHUB_PAT="$(gh auth token)"` en
  `~/.bashrc`) con scopes `repo` y `project`.
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
| A5 | `/revisar-cumplimiento specs/002-hooks-desarrollo` | Tabla I–IV con evidencia, sin ensuciar la conversación | FR-005, FR-006 |
| A6 | `/siguiente-ticket` | #4 pasa a In progress, rama `004-…`, spec iniciada, comentario en #4 | US1, SC-001 |
| A7 | (al terminar #4) `/abrir-pr` | Revisiones en `review.md`, PR con `Closes #4`, #4 en In review, comentario | US4, SC-002, SC-003 |
| A8 | Fusionar el PR del #4 | #4 cerrado y en Done | US5 |

A6–A8 se completan durante el ticket #4; este ticket se cierra con A1–A5 y A6 iniciado.
