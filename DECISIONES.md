# Decisiones

**Criterio**: un invariante de seguridad, cumplimiento o integridad se garantiza con un mecanismo
determinista (hook o regla de permisos). El juicio, el tono o las convenciones van en
instrucciones (CLAUDE.md, reglas por ruta, prompts). La matriz completa está en la
[constitución](.specify/memory/constitution.md).

## Necesidades del ecosistema

| # | Necesidad | Mecanismo y ubicación | Por qué |
|---|---|---|---|
| 1 | Convenciones al clonar | `CLAUDE.md` versionado (≤ 60 líneas) con `@.specify/memory/constitution.md`, `src/agent/CLAUDE.md` y `.claude/settings.json` | Se cargan sin configurar nada. El CLAUDE.md del agente solo entra al trabajar en `src/agent/`, y un archivo único habría cargado sus reglas en todas las sesiones |
| 2 | Preferencias personales aisladas | `CLAUDE.local.md` y `.claude/settings.local.json` ignorados por git; `~/.claude/CLAUDE.md` | Las capas personales de Claude Code no se versionan. `verificar_ecosistema.sh` comprueba que estén ignoradas |
| 3 | Tests junto al código con las mismas convenciones | `.claude/rules/tests.md` con `paths: **/test_*.py, **/conftest.py`; `testpaths` de pytest | La regla solo se carga al tocar tests, en cualquier carpeta. Si fuera global, costaría contexto en cada sesión |
| 4 | Nada de código sin spec | Hook `PreToolUse` `spec_primero.py` sobre Edit/Write en `src/` y `data/`: exige `spec.md`, `plan.md` y `tasks.md` de la feature de la rama actual; `onFailure: block` | Es un invariante del proceso. Una instrucción se puede ignorar. Toma la feature de la rama y no de `feature.json`, que queda obsoleto tras cada merge |
| 5 | Ningún dato con forma real | Hook `PreToolUse` `datos_ficticios.py` + `detector.py` (Luhn y patrones de documento). También lo reutilizan `scripts/empaquetar.py` y el plugin | El bloqueo es determinista y el mensaje accionable. Si el hook falla, la escritura se bloquea |
| 6 | Secretos fuera de Claude Code | 18 reglas `permissions.deny` (Read/Edit de `.env*`, `secrets/`, `*.pem`, `*.key`; se permite `.env.example`) + hook `secretos_bash.py` | `deny` no cubre comandos como `source .env`, y el hook cierra esa vía. Se acepta un falso positivo: también bloquea un comando que solo nombra el archivo |
| 7 | Código formateado tras cada edición | Hook `PostToolUse` `formatear.py` (`ruff format` + `ruff check --fix`) | Siempre corre. Los problemas que ruff no corrige se le informan a Claude |
| 8 | Revisión independiente antes del PR | Subagente `code-reviewer` (solo lectura: hook `solo_lectura_git.py` sobre Bash), invocado por `/abrir-pr` | No hereda la conversación que generó el código. Cada hallazgo y su resolución quedan en `specs/<feature>/review.md` |
| 9 | Cumplimiento de las reglas del banco | Skill `revisar-cumplimiento` (`context: fork`) con el subagente `compliance-auditor`. `/abrir-pr` no abre el PR con `NO CUMPLE` o con un ALTA pendiente | El auditor juzga con evidencia `archivo:línea`. Una regla 1 o 2 aplicada solo con el prompt es NO CUMPLE |
| 10 | Tickets sincronizados | MCP `github` (`.mcp.json`, `${GITHUB_PAT}`, toolset `projects`) + `/siguiente-ticket`, `/abrir-pr` y la skill `sincronizar-ticket`. Los workflows del Project pasan a Done al fusionar | Todo → In progress → In review → Done sin tocar la web. Se usa MCP y no la CLI `gh` para que el mecanismo sea uno solo y quede auditado |
| 11 | Piezas instalables por otro equipo | Marketplace `.claude-plugin/marketplace.json` + plugin `plugins/banca-guardrails` (hook, auditor, skill) | El auditor del plugin es de solo lectura por construcción (`Read, Grep, Glob`), porque los agentes de plugin ignoran `hooks`. Un test (`test_plugin.py`) impide que diverja de las piezas del repo |

## Agente (Agent SDK)

- **Ciclo**: cada turno termina con el `ResultMessage` y su `stop_reason`, sin tope de
  iteraciones (`src/agent/agente.py`).
- **Reglas 1 y 2**: los hooks `PreToolUse` `pre_reglas` y `PostToolUse` `post_resultado`
  (`src/agent/garantias.py`) deciden con el estado de la sesión y con el monto real leído del
  core, nunca con los argumentos del modelo. Las reglas 3, 4 y 5 van en el prompt, en las
  descripciones de las herramientas y en el error `NEGOCIO`/`POLITICA_NO_CUBRE`.
- **Herramientas MCP** (`src/mcp_server/`): las descripciones distinguen buscar de verificar.
  Los errores siguen el contrato `{tipo, codigo, reintentable, mensaje}`, y una búsqueda vacía
  no es error.
- **Subagente** `analista-transacciones`: solo puede `consultar_transacciones`, y recibe el
  contexto de forma explícita en el encargo. `pre_delegacion` solo admite esa delegación.
- **Interfaz**: los recuadros del chat salen de los eventos de los hooks, no del texto del modelo.
- **Verificación**: los seis casos obligatorios corren como e2e con aserciones sobre las
  herramientas (`src/agent/test_e2e.py`).
