# Contrato: hooks de desarrollo

## Entrada común (stdin)

```json
{
  "session_id": "…", "cwd": "/ruta/al/repo", "hook_event_name": "PreToolUse",
  "tool_name": "Write | Edit | Bash",
  "tool_input": { "file_path": "…", "content": "…" }
}
```

| `tool_name` | Campos usados de `tool_input` |
|---|---|
| `Write` | `file_path`, `content` |
| `Edit` | `file_path`, `new_string` |
| `MultiEdit` (compatibilidad) | `file_path`, `edits[].new_string` |
| `Bash` | `command` |

## Salida común

| Resultado | Exit | stderr |
|---|---|---|
| Permitir | 0 | vacío |
| Rechazar | 2 | `[<hook>] <motivo>. <cómo resolverlo>` |
| Error interno (hooks de bloqueo) | 2 | `[<hook>] Error interno: <tipo>. Se bloquea por seguridad.` |

Los mensajes MUST NOT incluir el número detectado completo.

## `datos_ficticios.py` — PreToolUse `Edit|Write`

- Inspecciona el contenido nuevo (`content` o `new_string`).
- Rechaza si `detector.detectar(texto)` devuelve al menos una detección.
- Mensaje (tarjeta): `[datos_ficticios] Se detectó un número con forma de tarjeta real (pasa
  Luhn). Usa solo los últimos 4 dígitos, p. ej. "terminada en 4821".`
- Mensaje (documento): `[datos_ficticios] Se detectó un número de documento con forma real.
  Usa el formato ficticio FIC-<dígitos>.`

## `spec_primero.py` — PreToolUse `Edit|Write`

- Solo actúa si `file_path`, relativo a la raíz del repo, empieza por `src/` o `data/` y su
  nombre no es `CLAUDE.md`.
- Rechaza si la rama no es de feature:
  `[spec_primero] La rama "<rama>" no es una feature. Crea la feature con /speckit-specify antes
  de escribir código en <ruta>.`
- Rechaza si faltan artefactos:
  `[spec_primero] Faltan <lista> en specs/<rama>/. Completa /speckit-plan y /speckit-tasks antes
  de implementar.`

## `secretos_bash.py` — PreToolUse `Bash`

- Rechaza si `command` contiene, como token o parte de ruta: `.env`, `.env.<sufijo>`, `.envrc`,
  un segmento `secrets/`, o un archivo terminado en `.pem` o `.key`.
- Excepción: `.env.example` no cuenta como mención.
- Mensaje: `[secretos_bash] El comando menciona un archivo de secretos (<categoría>). Claude
  Code no lee ni modifica secretos; pide a una persona que lo haga.`

## `formatear.py` — PostToolUse `Edit|Write`

- Ignora archivos que no terminan en `.py` o que no existen (exit 0).
- Ejecuta `ruff format` y `ruff check --fix` sobre el archivo.
- Si `ruff check` deja problemas: exit 2 con la salida de ruff en stderr (no revierte).
- Si uv o ruff no están disponibles: exit 0 con aviso en stderr.

## Registro en `.claude/settings.json`

```json
"hooks": {
  "PreToolUse": [
    { "matcher": "Edit|Write", "hooks": [
      { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/datos_ficticios.py\"", "timeout": 10, "onFailure": "block" },
      { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/spec_primero.py\"", "timeout": 10, "onFailure": "block" }
    ]},
    { "matcher": "Bash", "hooks": [
      { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/secretos_bash.py\"", "timeout": 10, "onFailure": "block" }
    ]}
  ],
  "PostToolUse": [
    { "matcher": "Edit|Write", "hooks": [
      { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/formatear.py\"", "timeout": 60 }
    ]}
  ]
}
```

`permissions` se conserva sin cambios.

## `detector.py` (API pura)

- `luhn_valido(digitos: str) -> bool`
- `detectar(texto: str) -> list[Deteccion]` con `Deteccion(tipo, inicio, sugerencia)`.
