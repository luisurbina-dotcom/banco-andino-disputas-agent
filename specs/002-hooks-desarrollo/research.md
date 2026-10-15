# Research: Hooks de desarrollo

Verificado contra la documentación oficial de hooks de Claude Code
([hooks](https://code.claude.com/docs/en/hooks)) el 2026-10-15. Los puntos marcados como
"a confirmar en vivo" se validan en el quickstart.

## R1. Lenguaje y ejecución de los hooks

- **Decision**: scripts Python solo con biblioteca estándar, compatibles con 3.10+, ejecutados
  con `python3`.
- **Rationale**: sin dependencias, arrancan en decenas de milisegundos y no requieren el entorno
  virtual (un `uv run` por cada edición añade latencia y falla si no se ha hecho `uv sync`). Al
  ser Python se prueban con pytest como el resto del proyecto. El detector queda como módulo
  puro, reutilizable por el plugin (#10).
- **Alternatives considered**: bash + grep (Luhn y normalización de tildes son frágiles en
  bash); `uv run` (más lento y acoplado al entorno); hooks de tipo `prompt` o `agent` (no
  deterministas, violan el principio II).

## R2. Contrato de entrada

- **Decision**: leer de stdin el JSON del evento y usar `tool_name` y `tool_input`.
- **Rationale**: campos documentados: `tool_input` de **Write** = `file_path`, `content`; de
  **Edit** = `file_path`, `old_string`, `new_string`, `replace_all`; de **Bash** = `command`
  (más `description`, `timeout`, `run_in_background`). PostToolUse recibe además
  `tool_response`. MultiEdit no aparece en la documentación vigente; si llega, se toma
  `edits[].new_string` por compatibilidad.
- **Texto a inspeccionar por el detector**: `content` (Write) o `new_string` (Edit). Solo el
  contenido nuevo (limitación aceptada en la spec).

## R3. Cómo bloquear

- **Decision**: código de salida 2 con el motivo en stderr.
- **Rationale**: en PreToolUse, exit 2 bloquea la herramienta y el stderr llega a Claude. La
  alternativa JSON (`hookSpecificOutput.permissionDecision: "deny"` +
  `permissionDecisionReason`) es equivalente; la documentación pide usar un solo enfoque por
  hook y exit 2 es más simple de probar (`returncode == 2`). En PostToolUse, exit 2 no puede
  bloquear (la herramienta ya corrió) pero muestra el stderr a Claude: es justo lo que necesita
  el formateo para informar problemas restantes.
- **Alternatives considered**: JSON de decisión (más verboso sin beneficio aquí).

## R4. Fail-closed

- **Decision**: cada hook de bloqueo envuelve su lógica en `try/except` y ante cualquier
  excepción sale con 2 y un mensaje. Además el registro usa `"onFailure": "block"` como segunda
  capa para fallos fuera del script (por ejemplo, `python3` ausente) — *a confirmar en vivo*,
  la opción figura para Claude Code ≥ 2.1.295 y el equipo usa 2.1.300.
- **Rationale**: un código de salida distinto de 0 y 2 (por ejemplo, una excepción no
  capturada que sale con 1) es un error **no bloqueante**: la herramienta se ejecutaría. Sin
  `try/except`, un bug del hook abriría el paso en silencio (FR-009).
- **Alternatives considered**: confiar solo en `onFailure` (no cubre una excepción capturada
  mal) o solo en `try/except` (no cubre que el intérprete no arranque).

## R5. Registro en settings.json

- **Decision**: forma shell con la ruta entre comillas dobles:
  `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/<hook>.py"`, matchers `Edit|Write` y `Bash`,
  `timeout` de 10 s para los de bloqueo y 60 s para el formateo.
- **Rationale**: `$CLAUDE_PROJECT_DIR` es la raíz del proyecto y hace que el hook funcione
  aunque Claude haya cambiado de directorio. Un matcher con solo letras y `|` es una lista
  exacta. El timeout por defecto (600 s) es excesivo para un bloqueo.
- **Alternatives considered**: forma exec (`command` + `args`) — la documentación la recomienda
  con placeholders, pero la expansión de variables en `args` no está confirmada; la forma shell
  con comillas es la documentada y probada.
- **Orden**: los hooks que coinciden corren en paralelo; por eso cada uno es independiente y no
  asume que otro ya corrió.

## R6. Feature activa

- **Decision**: rama actual con patrón `^\d{3}-[a-z0-9-]+$` → `specs/<rama>/` con `spec.md`,
  `plan.md` y `tasks.md`.
- **Rationale**: `.specify/feature.json` es estado local que queda apuntando a la última
  feature tras el merge; usarlo permitiría editar `src/` en `main`. La rama refleja lo que se
  está haciendo ahora y coincide con la convención de Spec Kit.
- **Alternatives considered**: `feature.json` (obsoleto tras merge); exigir solo `spec.md`
  (contradice el principio IV).

## R7. Detección de documentos sin falsos positivos

- **Decision**: solo se bloquea un número de 6–10 dígitos **precedido por una etiqueta de
  documento** y sin el prefijo `FIC-`.
- **Rationale**: un número suelto de 6–10 dígitos es indistinguible de un monto (`1250000`) o un
  id. La etiqueta da el contexto. El formato ficticio `FIC-<dígitos>` da una salida explícita.
- **Alternatives considered**: bloquear cualquier número de 6–10 dígitos (bloquearía montos del
  escenario).

## R8. Formateo

- **Decision**: `formatear.py` ejecuta `uv run --quiet ruff format <archivo>` y
  `uv run --quiet ruff check --fix <archivo>` solo si el archivo termina en `.py`; si queda
  salida de `ruff check`, la envía por stderr con exit 2; si uv/ruff no están, avisa y sale 0.
- **Rationale**: ruff es la herramienta del proyecto (`pyproject.toml`). Aquí sí se usa `uv run`
  porque ruff es una dependencia de desarrollo; la latencia es aceptable en PostToolUse.
- **Alternatives considered**: ruff global (no garantiza la versión del equipo); formatear todo
  el repo en cada edición (lento, toca archivos ajenos).

## R9. Desactivación

- `disableAllHooks: true` en un archivo de settings desactiva los hooks. Es una decisión
  explícita y visible del desarrollador; no se intenta impedir (requeriría managed settings).
  La revisión antes del PR compensa.

## R10. pytest y carpetas ocultas

- **Decision**: `testpaths = ["src", ".claude/hooks"]` en `pyproject.toml`.
- **Rationale**: pytest ignora por defecto los directorios que empiezan por `.` al recorrer;
  pasarlo como ruta explícita lo incluye — *a confirmar en vivo al implementar*.
