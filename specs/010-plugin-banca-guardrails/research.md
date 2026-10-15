# Research: plugin banca-guardrails

Fuente: documentación de plugins de Claude Code (manifest-reference, marketplace-reference,
components, loading, cli-reference, sub-agents, skills, hooks), consultada el 2026-10-15, y
`claude plugin --help` en la versión instalada (2.1.301).

## R1. Estructura

- **Decision**: marketplace `banco-andino` en `.claude-plugin/marketplace.json` (raíz del repo) con
  una entrada `banca-guardrails` cuyo `source` es `./plugins/banca-guardrails`. Dentro del plugin:
  `.claude-plugin/plugin.json`, `agents/compliance-auditor.md`,
  `skills/revisar-cumplimiento/SKILL.md`, `hooks/hooks.json` y los scripts del hook, y un
  `README.md` con las instrucciones.
- **Rationale**: es el diseño documentado; las rutas relativas se resuelven desde la raíz del
  marketplace y el plugin se carga en sitio desde un marketplace local.
- Un `CLAUDE.md` en la raíz del plugin no se carga (y `validate` avisa): las instrucciones van en
  `README.md`.

## R2. Hook en el plugin

- **Decision**: `hooks/hooks.json` con `PreToolUse` sobre `Edit|Write|MultiEdit|NotebookEdit`,
  `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/datos_ficticios.py"`, `timeout: 10` y
  `onFailure: "block"` (soportado desde 2.1.295). Scripts `datos_ficticios.py`, `detector.py` y
  `comun.py` (solo biblioteca estándar).
- **Rationale**: mismo comportamiento que en este repo (exit 2 bloquea; cualquier falla bloquea).

## R3. Solo lectura del auditor en el plugin

- **Finding**: en agentes de plugin se ignoran `hooks`, `mcpServers` y `permissionMode`; por eso no
  se puede reutilizar el hook `solo_lectura_git` del agente de este repo.
- **Decision**: el agente del plugin tiene `tools: Read, Grep, Glob` (sin Bash ni herramientas de
  escritura): es de solo lectura **por construcción**. El diff lo aporta la skill con inyección de
  contexto (`` !`git …` ``) restringida por `allowed-tools: Bash(git diff:*)` y similares.
- **Alternatives considered**: permitir Bash con reglas de permisos de sesión (afecta a toda la
  sesión del otro equipo); hook de plugin sobre Bash (no es específico del agente).

## R4. Nombres en el plugin

- La skill se invoca como `/banca-guardrails:revisar-cumplimiento`; el agente es
  `banca-guardrails:compliance-auditor` y la skill lo referencia así en `agent:`. Esto último no
  está explícito en la documentación: se verifica en vivo (quickstart Q5).

## R5. Fuente única de verdad

- **Decision**: este repo sigue usando sus piezas en `.claude/` (no consume el plugin). El plugin
  contiene:
  - copias **idénticas** de `datos_ficticios.py`, `detector.py` y `comun.py`;
  - un agente y una skill **portables** (sin hook propio, sin rutas de este proyecto) que
    comparten con los de este repo el bloque de reglas del banco, delimitado por marcadores.
  - Un test (`.claude/hooks/test_plugin.py`) falla si las copias del hook divergen o si el bloque de
    reglas del banco difiere entre el auditor del repo y el del plugin.
- **Rationale**: FR-007 admite "fuente única o verificación de divergencia". Que este repo consuma
  su propio plugin exigiría cambiar `.claude/settings.json` (configuración de equipo), pasar por la
  confianza del workspace y renombrar las piezas con el espacio de nombres del plugin, rompiendo
  `/abrir-pr`; más piezas y riesgo para el mismo resultado.
- **Alternatives considered**: enlaces simbólicos (el plugin podría copiarse a la caché sin
  seguirlos); consumir el plugin desde `enabledPlugins` (ver arriba).

## R6. Portabilidad de la auditoría

- **Decision**: el auditor del plugin toma como fuente de verdad, en este orden, la constitución
  de Spec Kit del proyecto destino (`.specify/memory/constitution.md`), si existe, o su `CLAUDE.md`,
  y siempre las reglas del banco (bloque compartido).
- **Rama base**: `main`, documentada como limitación. Los argumentos de la skill se sustituyen
  como texto antes de ejecutar la inyección de contexto, así que un segundo argumento opcional
  no puede tener `main` por defecto sin comandos compuestos que `allowed-tools: Bash(git diff:*)`
  no autoriza.

## R7. Prueba de instalación aislada

- **Decision**: en un directorio temporal con un repo git de prueba:
  `CLAUDE_CODE_PLUGIN_CACHE_DIR=<tmp>` (no toca `~/.claude/plugins`),
  `claude plugin marketplace add <repo> --scope local` y
  `claude plugin install banca-guardrails@banco-andino --scope local`; luego `claude -p` en ese
  directorio para comprobar el hook y la skill. Limpieza: `marketplace remove` y borrar el temporal.
- `claude plugin validate <ruta> --strict` para el plugin y para el marketplace.
- Los números con forma de tarjeta real se generan en tiempo de ejecución en el temporal, nunca
  se escriben en el repo (principio III).
