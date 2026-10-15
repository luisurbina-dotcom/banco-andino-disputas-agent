# Revisión antes del PR — 001-memoria-reglas-permisos

## T018 · Revisión independiente

- **Fecha**: 2026-10-15
- **Revisor**: subagente de solo lectura (Read, Grep, Glob, `git diff`), sin el contexto de la
  sesión que generó el código. El subagente `code-reviewer` del issue #3 todavía no existe, por
  eso se usó uno ad hoc con la misma restricción de herramientas.
- **Alcance**: `git diff main...001-memoria-reglas-permisos` contra spec.md, contrato, research
  R4 y constitución.
- **Veredicto**: APROBADO CON OBSERVACIONES.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | La negación `Read(!.env.example)` podría no estar soportada; si no, FR-009 falla. | **Resuelto por evidencia**: M11 en vivo permite leer `.env.example`, y `src/sub/.env.local` sigue denegado (quickstart § Resultados). |
| 2 | MEDIA | `./secrets/**` solo cubre `secrets/` en la raíz; `src/x/secrets/` quedaría expuesto (SC-002). | **Pendiente de aprobación del responsable**: agregar `Read(**/secrets/**)` y `Edit(**/secrets/**)` en `.claude/settings.json`. |
| 3 | BAJA | `.envrc`, `*.pem` y `*.key` no están cubiertos. | **Pendiente de decisión**: fuera del alcance de la spec; se evalúa junto con el #2. |
| 4 | BAJA | El script no comprobaba que el `@import` estuviera fuera de bloques de código. | **Corregido**: la comprobación usa `awk` y respeta los bloques. |
| 5 | BAJA | El script buscaba las reglas deny como texto suelto y solo 6 de 12. | **Corregido**: verifica las 12 dentro de `permissions.deny` y que `allow` no reabra secretos. |
| 6 | BAJA | El script solo buscaba `paths:` en las reglas. | **Corregido**: valida el frontmatter y los patrones exactos del contrato. |
| 7 | BAJA | `CLAUDE.md` repite el principio IV ("nada de código sin spec…"). | **Pendiente de aprobación del responsable**: reemplazar la línea por una remisión a la constitución. |
| 8 | BAJA | `uv run python -m chat` todavía no es verificable. | **Aceptado**: es un comando objetivo; se revisa en los issues #4 y #8. |

Los cambios a `.claude/settings.json` y a `CLAUDE.md` los aprueba una persona y no se aplican
solo porque los pida un revisor automático: son la política de permisos y la memoria del equipo.
