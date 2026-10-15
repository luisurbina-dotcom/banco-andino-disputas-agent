# Banco Andino — Agente de disputas

Agente de disputas y contracargos para un banco ficticio, con Claude Agent SDK y un servidor
MCP propio que simula el core bancario. Los principios del proyecto son la constitución:

@.specify/memory/constitution.md

## Stack y comandos

Python 3.12 con uv.

- `uv sync` instala dependencias.
- `uv run pytest` corre los tests unitarios (sin red ni API key).
- `uv run pytest -m e2e` corre los casos end-to-end (objetivo, issue #9; requiere `ANTHROPIC_API_KEY`).
- `uv run python -m chat` arranca la interfaz de chat (objetivo, issue #8).
- Hooks de equipo en `.claude/hooks/` (datos ficticios, spec primero, secretos, formateo).

## Estructura

- `src/mcp_server/` servidor MCP del core bancario (FastMCP, stdio).
- `src/agent/` agente, hooks del SDK y subagente. Tiene su propio `CLAUDE.md`.
- `src/chat/` interfaz de chat en terminal.
- `data/` datos ficticios en JSON.
- `specs/` artefactos de Spec Kit, una carpeta por feature.
- Los tests viven junto al código como `test_<módulo>.py` (ver `.claude/rules/tests.md`).

## Flujo de trabajo

1. `/siguiente-ticket`: toma el ticket, lo pasa a In progress, crea la rama `NNN-nombre` y
   arranca `/speckit-specify` con el issue. Luego `plan`, `tasks`, `analyze`, `implement`.
2. Spec primero: ver principio IV de la constitución.
3. `/abrir-pr`: revisión independiente (`code-reviewer`), `/revisar-cumplimiento`, PR con
   `Closes #N` e In review. Una persona fusiona; el Project pasa el ticket a Done.
4. Estados y comentarios en GitHub solo por el MCP `github` (`GITHUB_PAT` en tu entorno).
5. Commits en español, estilo `tipo(alcance): descripción`.

## Lo personal

Tus preferencias van en `CLAUDE.local.md` o `.claude/settings.local.json` (ignorados por git)
o en `~/.claude/CLAUDE.md`. No las agregues a este archivo.
