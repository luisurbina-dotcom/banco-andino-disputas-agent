# Data Model: plugin banca-guardrails

## Marketplace (`.claude-plugin/marketplace.json`)

| Campo | Valor |
|---|---|
| `name` | `banco-andino` |
| `owner.name` | autor del repo |
| `plugins[0].name` | `banca-guardrails` (igual que el manifiesto) |
| `plugins[0].source` | `./plugins/banca-guardrails` |
| `plugins[0].description` | resumen de las piezas |

## Plugin (`plugins/banca-guardrails/.claude-plugin/plugin.json`)

| Campo | Valor |
|---|---|
| `name` | `banca-guardrails` |
| `version` | `1.0.0` |
| `description` | guardrails de cumplimiento y datos ficticios para equipos del banco |
| `author.name` | autor del repo |
| `license`, `keywords` | opcionales |

## Piezas y su relación con este repo

| Pieza del plugin | Fuente en este repo | Relación verificada por test |
|---|---|---|
| `hooks/datos_ficticios.py`, `detector.py`, `comun.py` | `.claude/hooks/` | bytes idénticos |
| `agents/compliance-auditor.md` | `.claude/agents/compliance-auditor.md` | bloque "reglas del banco" idéntico (entre marcadores) |
| `skills/revisar-cumplimiento/SKILL.md` | `.claude/skills/revisar-cumplimiento/SKILL.md` | versión portable (sin relación textual) |
