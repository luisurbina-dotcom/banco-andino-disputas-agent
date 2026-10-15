# Banco Andino — Agente de disputas

Agente de disputas y contracargos para un banco ficticio, con Claude Agent SDK y un servidor
MCP propio que simula el core bancario. Los principios del proyecto son la constitución:

@.specify/memory/constitution.md

## Stack y comandos

Python 3.12 con uv. Comandos objetivo (se habilitan en los issues #4 y #8):

- `uv sync` instala dependencias.
- `uv run pytest` corre los tests unitarios (sin red ni API key).
- `uv run pytest -m e2e` corre los casos end-to-end (requiere `ANTHROPIC_API_KEY`).
- `uv run python -m chat` arranca la interfaz de chat.

## Estructura

- `src/mcp_server/` servidor MCP del core bancario (FastMCP, stdio).
- `src/agent/` agente, hooks del SDK y subagente. Tiene su propio `CLAUDE.md`.
- `src/chat/` interfaz de chat en terminal.
- `data/` datos ficticios en JSON.
- `specs/` artefactos de Spec Kit, una carpeta por feature.
- Los tests viven junto al código como `test_<módulo>.py` (ver `.claude/rules/tests.md`).

## Flujo de trabajo

1. Un ticket del GitHub Project → una rama `NNN-nombre` → una carpeta `specs/NNN-nombre/`.
2. `/speckit-specify` con el issue como insumo, luego `plan`, `tasks`, `analyze`, `implement`.
3. Spec primero: ver principio IV de la constitución.
4. Antes del PR: revisión independiente y revisión de cumplimiento.
5. El PR lleva `Closes #N`. Commits en español, estilo `tipo(alcance): descripción`.

## Lo personal

Tus preferencias van en `CLAUDE.local.md` o `.claude/settings.local.json` (ignorados por git)
o en `~/.claude/CLAUDE.md`. No las agregues a este archivo.
