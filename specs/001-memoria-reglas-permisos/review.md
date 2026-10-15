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
| 2 | MEDIA | `./secrets/**` solo cubre `secrets/` en la raíz; `src/x/secrets/` quedaría expuesto (SC-002). | **Corregido con aprobación del responsable**: `Read(**/secrets/**)` y `Edit(**/secrets/**)` reemplazan a `./secrets/**`. |
| 3 | BAJA | `.envrc`, `*.pem` y `*.key` no están cubiertos. | **Corregido con aprobación del responsable**: se agregan `**/.envrc`, `**/*.pem` y `**/*.key` a Read y Edit. |
| 4 | BAJA | El script no comprobaba que el `@import` estuviera fuera de bloques de código. | **Corregido**: la comprobación usa `awk` y respeta los bloques. |
| 5 | BAJA | El script buscaba las reglas deny como texto suelto y solo 6 de 12. | **Corregido**: verifica las 12 dentro de `permissions.deny` y que `allow` no reabra secretos. |
| 6 | BAJA | El script solo buscaba `paths:` en las reglas. | **Corregido**: valida el frontmatter y los patrones exactos del contrato. |
| 7 | BAJA | `CLAUDE.md` repite el principio IV ("nada de código sin spec…"). | **Corregido con aprobación del responsable**: la línea remite al principio IV. |
| 8 | BAJA | `uv run python -m chat` todavía no es verificable. | **Aceptado**: es un comando objetivo; se revisa en los issues #4 y #8. |

Los cambios a `.claude/settings.json` y a `CLAUDE.md` los aprueba una persona y no se aplican
solo porque los pida un revisor automático: son la política de permisos y la memoria del equipo.

## T019 · Revisión de cumplimiento (principios I–IV)

- **Fecha**: 2026-10-15 · **Alcance**: `git diff main...001-memoria-reglas-permisos`
- **Veredicto**: CUMPLE.

| Principio | Verificación | Resultado |
|---|---|---|
| I. Reglas de negocio | La constitución no cambia en este diff. `CLAUDE.md` la importa sin reescribirla. La única mención del umbral (`src/agent/CLAUDE.md`) conserva $500.000 y exige hooks. | ✅ |
| II. Garantizado, no sugerido | La protección de secretos es `permissions.deny` (18 reglas, sin `allow`), no una instrucción. Probado en vivo: `.env`, `cat .env`, `secrets/` en raíz y anidado, `.env.local` anidado y `*.key` → denegados. | ✅ |
| III. Datos ficticios y cero credenciales | Sin tokens, claves ni números de 13–19 dígitos en el diff. `.env.example` solo trae nombres de variables. | ✅ |
| IV. Spec primero | `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `contracts/` y `quickstart.md` presentes antes del código. `/speckit-analyze` ejecutado y sus hallazgos corregidos. | ✅ |

Nota: esta revisión se hizo a mano porque la skill `revisar-cumplimiento` y el subagente
`compliance-auditor` se construyen en el issue #3.
