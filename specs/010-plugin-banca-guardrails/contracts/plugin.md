# Contrato: plugin banca-guardrails

## Instalación (proyecto destino)

```text
/plugin marketplace add luisurbina-dotcom/banco-andino-disputas-agent   # o una ruta local
/plugin install banca-guardrails@banco-andino
```

Equivalente por CLI: `claude plugin marketplace add <fuente> [--scope …]` y
`claude plugin install banca-guardrails@banco-andino [--scope …]`.

## Hook `datos_ficticios` (PreToolUse sobre Edit|Write|MultiEdit|NotebookEdit)

- Entrada: evento JSON por stdin (contrato de hooks de Claude Code).
- Bloquea (exit 2 + mensaje) si el contenido nuevo tiene un número con forma de tarjeta real
  (13–19 dígitos que pasan Luhn) o un documento con forma real; mensaje accionable (últimos 4
  dígitos / `FIC-<dígitos>`).
- Permite (exit 0) datos ficticios.
- Cualquier excepción o timeout bloquea (`ejecutar_seguro` + `onFailure: "block"`).
- Comportamiento idéntico al hook de este repo (mismos scripts).

## Skill `/banca-guardrails:revisar-cumplimiento <carpeta-spec>`

- `context: fork`, `agent: banca-guardrails:compliance-auditor`.
- Inyecta `git diff --stat <base>...HEAD` y `git diff <base>...HEAD` (base `main`).
- Salida: tabla Principio/Regla | Resultado (CUMPLE / NO CUMPLE / N/A) | Evidencia y la línea
  `Veredicto: CUMPLE` o `Veredicto: NO CUMPLE`.

## Agente `banca-guardrails:compliance-auditor`

- `tools: Read, Grep, Glob` (sin Bash ni escritura).
- Fuente de verdad: constitución del proyecto destino si existe, si no su `CLAUDE.md`; siempre
  las reglas del banco (bloque compartido con el auditor de este repo).
- Regla 1 o 2 aplicada solo con el prompt = NO CUMPLE.
