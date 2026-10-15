# Contrato: piezas de la automatización

## `.mcp.json`

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}",
        "X-MCP-Toolsets": "context,repos,issues,pull_requests,projects"
      }
    }
  }
}
```

MUST NOT contener tokens literales. El servidor `banco` se agrega en el issue #4.

## `.claude/settings.json` (adición)

`"enabledMcpjsonServers": ["github"]` — se conservan `permissions` y `hooks`.

## Comando `/siguiente-ticket` (`.claude/commands/siguiente-ticket.md`)

- Frontmatter: `description`, `argument-hint: "[número-de-issue]"` (opcional: forzar un ticket).
- Pasos:
  1. Verificar que el MCP `github` responde; si no, detenerse con instrucciones (exportar
     `GITHUB_PAT`, reiniciar, aprobar el servidor).
  2. Si hay un ticket en In progress, avisar y pedir confirmación.
  3. Elegir el issue en Todo de menor número (o el indicado).
  4. `sincronizar-ticket <n> "In progress"`.
  5. Desde `main` actualizado, crear o reutilizar la rama `NNN-nombre` y escribir
     `.specify/feature.json`.
  6. Invocar `/speckit-specify` con el título y el cuerpo del issue.
  7. `sincronizar-ticket <n> comentar` con rama, enlace a la spec, lo especificado, lo decidido y
     lo pendiente.

## Comando `/abrir-pr` (`.claude/commands/abrir-pr.md`)

- Frontmatter: `description`, `argument-hint: "[número-de-issue]"` (por defecto, el del spec).
- Pasos:
  1. Confirmar rama de feature, `tasks.md` sin tareas abiertas, tests y ruff en verde.
  2. Delegar en `code-reviewer` el diff `main...HEAD`; registrar hallazgos en `review.md`.
  3. Ejecutar `/revisar-cumplimiento specs/<feature>`; agregar el veredicto a `review.md`.
  4. Si hay ALTA "Pendiente" o NO CUMPLE: detenerse y listar lo que falta.
  5. `git push` de la rama; crear el PR por MCP (`create_pull_request`) con `Closes #<n>`.
  6. `sincronizar-ticket <n> "In review"` y `sincronizar-ticket <n> comentar` con el resumen.

## Skill `sincronizar-ticket` (`.claude/skills/sincronizar-ticket/SKILL.md`)

- Frontmatter: `name`, `description`, `argument-hint: "<issue> <estado|comentar> [texto]"`,
  `allowed-tools`: herramientas del MCP `github` (projects, issues) **preaprobadas** para que la
  sincronización no pida confirmación. No es una restricción: no usar `gh` es una instrucción.
- Constantes: dueño `luisurbina-dotcom`, Project 1, campo `Status`, opciones `Todo`,
  `In progress`, `In review`, `Done`.
- Estado: obtener item (agregarlo si falta), id del campo y de la opción por nombre; actualizar.
- Comentar: `add_issue_comment` con el texto recibido.

## Skill `revisar-cumplimiento` (`.claude/skills/revisar-cumplimiento/SKILL.md`)

- Frontmatter: `name`, `description`, `argument-hint: "<carpeta-spec>"`, `context: fork`,
  `agent: compliance-auditor`, `background: false`, `allowed-tools: Read Grep Glob Bash`.
- Cuerpo: leer constitución y `$ARGUMENTS/spec.md`, revisar `git diff main...HEAD`, devolver la
  tabla de veredictos (data-model § Veredicto) y un veredicto global CUMPLE / NO CUMPLE.

## Subagente `code-reviewer` (`.claude/agents/code-reviewer.md`)

- Frontmatter: `name`, `description`, `tools: Read, Grep, Glob, Bash`, `model: inherit`,
  `hooks.PreToolUse` (matcher `Bash`) → `solo_lectura_git.py`.
- Salida: tabla Severidad | Archivo:línea | Hallazgo | Recomendación + veredicto
  (APROBADO / APROBADO CON OBSERVACIONES / CAMBIOS REQUERIDOS).

## Subagente `compliance-auditor` (`.claude/agents/compliance-auditor.md`)

- Igual restricción de herramientas y hook que `code-reviewer`.
- Evalúa principios I–IV y reglas 1–5 (cuando aplican) con evidencia; regla 1 o 2 sin hook del
  SDK → NO CUMPLE.

## Hook `solo_lectura_git.py` (`.claude/hooks/`)

- Entrada: evento PreToolUse de Bash. Permite (exit 0) solo `git diff|log|show|status|ls-files|
  rev-parse|merge-base|branch --show-current` con argumentos sin `; | & > < $( \``. Cualquier
  otro comando → exit 2 con `[solo_lectura_git] Este subagente solo puede leer el repositorio.`
- Fail-closed como los demás hooks de bloqueo.
