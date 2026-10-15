# Research: Automatización del ciclo de tickets y revisiones

Verificado el 2026-10-15 contra la documentación oficial de Claude Code
([mcp](https://code.claude.com/docs/en/mcp.md), [skills](https://code.claude.com/docs/en/skills.md),
[sub-agents](https://code.claude.com/docs/en/sub-agents.md),
[settings](https://code.claude.com/docs/en/settings-reference.md)) y del
[servidor MCP de GitHub](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md).
Lo marcado *a confirmar en vivo* se valida al conectar el servidor.

## R1. Servidor MCP de GitHub

- **Decision**: servidor remoto oficial en `.mcp.json`:
  `type: "http"`, `url: "https://api.githubcopilot.com/mcp/"`, headers
  `Authorization: "Bearer ${GITHUB_PAT}"` y
  `X-MCP-Toolsets: "context,repos,issues,pull_requests,projects"`.
- **Rationale**: el remoto no requiere Docker ni binarios. `${VAR}` se expande en `url` y
  `headers`, así el token vive solo en el entorno de cada desarrollador. El toolset `projects` no
  viene por defecto; el header `X-MCP-Toolsets` lo habilita junto con los demás (la forma de ruta
  `/x/projects` solo admite uno). Si `GITHUB_PAT` no está definido, la config carga pero el
  servidor no autentica y `claude mcp list` lo advierte: el comando se detiene (spec, edge case).
- **Alternatives considered**: servidor local en Docker con `GITHUB_TOOLSETS` (agrega Docker
  como requisito para clonar y trabajar); el conector de claude.ai (personal, no versionado).

## R2. Aprobación del servidor de proyecto

- **Decision**: agregar `"enabledMcpjsonServers": ["github"]` a `.claude/settings.json`
  (requiere aprobación del responsable: configuración de equipo).
- **Rationale**: sin esto, cada desarrollador debe aprobar el servidor en la primera sesión
  (contradice la necesidad 1). La clave se admite en el settings de proyecto y la documentación
  la ignora en carpetas no confiables, así que no abre una puerta en un clon no revisado.
  `claude -p` y el Agent SDK cargan los servidores de proyecto sin preguntar.
- **Alternatives considered**: `enableAllProjectMcpServers: true` (aprobaría también el servidor
  del banco del #4 sin nombrarlo; se prefiere la lista explícita).

## R3. Herramientas del toolset de projects

- **Decision**: la skill `sincronizar-ticket` usa las herramientas de projects
  (`projects_list`, `projects_get`, `projects_write` con método `update_project_item`) y
  `add_issue_comment`; `/abrir-pr` usa `create_pull_request`. *Nombres a confirmar en vivo con
  `/mcp`*; si difieren, se ajusta `allowed-tools`.
- **Rationale**: cambiar el campo Status requiere los ids del Project, del campo y de la opción;
  la skill los obtiene con `projects_get` en vez de fijarlos, salvo el número del Project (1) y
  el dueño, que no son secretos.

## R4. Comandos vs skills

- **Decision**: los dos flujos de usuario son **comandos** en `.claude/commands/`; la lógica
  reutilizable es **skills** en `.claude/skills/`.
- **Rationale**: los comandos son la entrada explícita del desarrollador (`/siguiente-ticket`,
  `/abrir-pr`) y el enunciado pide al menos uno propio. Las skills son piezas que otros flujos
  (y el plugin del #10) reutilizan. Ambos admiten `description`, `argument-hint` y
  `allowed-tools`; si un comando y una skill comparten nombre, gana la skill, por eso no se
  repiten nombres.

## R5. Revisión de cumplimiento aislada

- **Decision**: skill `revisar-cumplimiento` con `context: fork`, `agent: compliance-auditor`,
  `background: false`, `argument-hint: "<carpeta-spec>"` y `allowed-tools: Read Grep Glob Bash`.
- **Rationale**: `context: fork` ejecuta el cuerpo como tarea de un subagente que **no ve la
  conversación**: la auditoría no se contamina con el razonamiento de quien implementó y no
  llena el contexto principal con lecturas de archivos. `agent` elige el subagente, que define
  modelo y herramientas. `background: false` hace que `/abrir-pr` espere el veredicto.
- **Alternatives considered**: invocar el subagente directamente desde el comando (funciona,
  pero no es reutilizable como skill ni empaquetable en el plugin).

## R6. Solo lectura real para los revisores

- **Decision**: `code-reviewer` y `compliance-auditor` tienen `tools: Read, Grep, Glob, Bash`, y
  un hook `PreToolUse` **en su propio frontmatter** que solo deja pasar comandos git de lectura
  (`git diff|log|show|status|ls-files|rev-parse|branch --show-current|merge-base`) sin
  metacaracteres de shell (`; | & > < $( \``). Script: `.claude/hooks/solo_lectura_git.py`, con
  tests.
- **Rationale**: necesitan `git diff` para ver el cambio, pero `tools` no admite restringir Bash
  por comando (`Bash(git diff:*)` no está documentado ahí, y en `disallowedTools` quita Bash
  entero). Un hook acotado al subagente es determinista (principio II) y no afecta a la sesión
  principal. Sin Write ni Edit, no pueden tocar archivos.
- **Alternatives considered**: sin Bash y pasando el diff en el prompt (diffs grandes llenan el
  contexto y el revisor no puede mirar el historial); `permissions.deny` global (afectaría a la
  sesión principal).

## R7. Textos hacia GitHub

- **Decision**: cuerpos de PR y comentarios se envían por el servidor MCP.
- **Rationale**: viajan como argumentos de herramienta MCP y no pasan por `secretos_bash`, que
  bloquea comandos de shell que mencionan archivos de secretos aunque sea en un texto (R11 del
  #2). Además dejan evidencia de que la sincronización ocurre por el MCP oficial.

## R8. Bloqueo del PR

- **Decision**: `/abrir-pr` no crea el PR si `review.md` tiene hallazgos ALTA "Pendiente" o algún
  NO CUMPLE; un hallazgo "Aceptado" requiere justificación escrita.
- **Rationale**: decidir si un hallazgo se acepta es juicio humano, así que es instrucción del
  comando y no un hook (criterio de la matriz de la constitución).

## R9. Verificación

- **Decision**: comprobaciones estáticas en `scripts/verificar_ecosistema.sh` (archivos,
  frontmatter, `${GITHUB_PAT}` sin tokens literales), tests del hook `solo_lectura_git.py` y
  verificación en vivo con el ticket #4 como primer recorrido real del ciclo.
- **Rationale**: los flujos dependen de GitHub y de una sesión interactiva; el #4 es la prueba
  natural de SC-001 a SC-004.
