# Contrato: archivos de configuración del ecosistema

Cada archivo define su ubicación, formato y contenido mínimo. Las tareas y el script de
verificación se apoyan en este contrato.

## `CLAUDE.md` (raíz)

- Formato: Markdown, ≤ 60 líneas.
- MUST contener, en su propia línea y fuera de bloques de código:
  `@.specify/memory/constitution.md`
- MUST contener solo lo que no se deduce del código:
  - Stack y comandos (`uv sync`, `uv run pytest`, `uv run pytest -m e2e`, cómo arrancar el chat).
  - Estructura (`src/mcp_server`, `src/agent`, `src/chat`, `data/`, `specs/`).
  - Flujo de trabajo: Spec Kit por ticket, rama por feature, PR con `Closes #N`.
  - Dónde va lo personal (`CLAUDE.local.md`, `settings.local.json`).
- MUST NOT duplicar los principios de la constitución ni contener credenciales.

## `src/agent/CLAUDE.md`

- Formato: Markdown breve.
- MUST explicar por qué existe (guía que solo aplica al código del agente).
- MUST fijar: reglas 1 y 2 con hooks `PreToolUse` del SDK leyendo el estado de la sesión y los
  datos del core, nunca los argumentos del modelo; el estado verificado solo lo pone un
  `PostToolUse` exitoso de `verificar_identidad`; ciclo gobernado por la razón de parada;
  subagente con contexto explícito; handoff autocontenido.

## `.claude/rules/tests.md`

```markdown
---
paths:
  - "**/test_*.py"
  - "**/conftest.py"
---
```

- MUST fijar: tests junto al módulo (`test_<módulo>.py` en la misma carpeta); pytest; tests
  unitarios sin red ni API key; e2e marcados con `@pytest.mark.e2e`; datos solo ficticios
  (tarjetas por últimos 4 dígitos); afirmar sobre llamadas a herramientas y no solo sobre texto.

## `.claude/rules/mcp-tools.md`

```markdown
---
paths:
  - "src/mcp_server/**"
---
```

- MUST fijar: descripciones que distingan `buscar_cliente` de `verificar_identidad` y digan qué
  hacer con varias coincidencias; formato de error
  `{"error": {"tipo": TRANSITORIO|VALIDACION|NEGOCIO|PERMISOS, "reintentable": bool, "mensaje": str}}`;
  búsqueda sin resultados = lista vacía, no error; datos solo ficticios.

## `.claude/settings.json`

- Formato: JSON válido, con `"$schema": "https://json.schemastore.org/claude-code-settings.json"`.
- `permissions.deny` MUST contener las reglas de [research.md § R4](../research.md#r4-sintaxis-de-denegación-de-secretos).
- MUST NOT contener credenciales. Hooks y MCP se agregan en los issues #2 y #3.

## `.env.example`

- Solo nombres de variables con valor vacío: `ANTHROPIC_API_KEY=` y `GITHUB_PAT=`.

## `.gitignore` (ya existente)

- MUST incluir `.env`, `.env.*`, `!.env.example`, `secrets/`, `CLAUDE.local.md` y
  `.claude/settings.local.json`.
