# Revisión antes del PR — 003-automatizacion-github

Primera feature revisada con las piezas que ella misma crea: `code-reviewer` (T016) y
`/revisar-cumplimiento` → `compliance-auditor` (T017), ejecutados en sesiones nuevas de Claude
Code sin el contexto de la sesión de implementación.

## T016 · Revisión independiente (`code-reviewer`)

- **Fecha**: 2026-10-15 · **Alcance**: `git diff main...HEAD` (20 archivos)
- **Veredicto**: APROBADO CON OBSERVACIONES.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | `/siguiente-ticket` calculaba siempre un `NNN` nuevo: un ticket retomado crearía una rama duplicada. | **Corregido**: antes de calcular `NNN` busca `specs/*/spec.md` cuyo **Input** mencione `#<n>` y reutiliza esa rama. |
| 2 | MEDIA | `/abrir-pr` pedía re-revisar tras corregir sin hacer commit: los revisores solo ven `main...HEAD`. | **Corregido**: precondición de árbol limpio y commit de correcciones antes de re-revisar y de la auditoría. |
| 3 | MEDIA | El plan trataba `allowed-tools` de las skills como restricción; en Claude Code preaprueba, no restringe. | **Corregido** en plan y contrato: la restricción real es `tools` del subagente + hook; "no usar `gh`" queda como instrucción. |
| 4 | BAJA | `plan.md` decía "sin código Python" y no listaba `solo_lectura_git.py`. | **Corregido**. |
| 5 | BAJA | `code-reviewer` no listaba `branch --show-current` ni avisaba que `git -C` y comandos compuestos se bloquean. | **Corregido** en ambos subagentes. |
| 6 | BAJA | `/abrir-pr` no comprobaba la conexión MCP al inicio (podía dejar una rama publicada sin PR). | **Corregido**: paso 0 de conexión. |
| 7 | BAJA | El quickstart no explicaba cómo obtener el scope `project`. | **Corregido**: `gh auth refresh -s project,read:org`. |
| 8 | BAJA | Comprobaciones débiles: `projects` buscado en todo el archivo; patrón de tokens sin `ghu_`, `ghs_`, `ghr_`. | **Corregido**: se valida `X-MCP-Toolsets` con JSON y patrón `gh[pousr]_`. |
| 9 | BAJA | `--output` bloqueaba también `--output-indicator-new` (falso positivo). | **Corregido**: solo `--output` y `--output=…`. |

Nota del revisor: el MCP `github` no conectó en su sesión ("authorization header is badly
formatted"). Esa sesión se lanzó sin `GITHUB_PAT`: confirma el caso borde de la spec (sin la
variable, el header viaja literal y el servidor lo rechaza).

## T018 · Segunda revisión independiente (dentro de `/abrir-pr 3`)

- **Fecha**: 2026-10-15 · **Ejecución**: subagente `code-reviewer` invocado por `/abrir-pr` en la
  sesión interactiva con el MCP `github` conectado.
- **Verificación de T016**: los 9 hallazgos "Corregido" están aplicados (comprobados archivo por
  archivo). El hook bloqueó en vivo un `git grep` del propio revisor.
- **Veredicto**: APROBADO CON OBSERVACIONES.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 10 | MEDIA | `/siguiente-ticket` llamaba a `/speckit-specify` aunque el ticket se retomara: la skill sobrescribe `spec.md` con la plantilla. | **Corregido**: si `spec.md` existe, no se regenera; se informa la fase y el siguiente comando. |
| 11 | MEDIA | Decía "la carpeta ya existe" sin crearla ni pasar `SPECIFY_FEATURE_DIRECTORY`: la skill podía elegir otro nombre que la rama. | **Corregido**: crea `specs/NNN-nombre/checklists/` y pasa `SPECIFY_FEATURE_DIRECTORY` explícito. |
| 12 | MEDIA | Comentaba el enlace a `spec.md` sin commit: el enlace apuntaba a un archivo inexistente en el remoto (SC-004). | **Corregido**: nuevo paso 7 de commit y push antes del comentario. |
| 13 | BAJA | La tabla de `review.md` no separa ubicación y recomendación (data-model). | **Corregido** en data-model: en `review.md` se resumen dentro del hallazgo y la resolución. |
| 14 | BAJA | Faltaban tests: `git -C ruta diff`, `--output archivo` separado y comilla sin cerrar. | **Corregido**: 3 casos nuevos (32 tests del hook). |
| 15 | BAJA | Mensaje del hook distinto entre contrato y código. | **Corregido** en el contrato. |
| 16 | BAJA | Quickstart A5 citaba `specs/002-…` pero se ejecutó sobre `specs/003-…`. | **Corregido**. |

## T017 · Revisión de cumplimiento (`/revisar-cumplimiento`)

- **Fecha**: 2026-10-15 · **Ejecución**: skill con `context: fork` y `agent: compliance-auditor`.
- **Veredicto**: CUMPLE.

| Principio/Regla | Resultado | Evidencia (resumen del auditor) |
|---|---|---|
| I.1–I.5 Reglas de negocio | N/A | El diff no toca `src/` ni `data/`; agente y servidor del banco llegan en #4–#7. |
| II. Garantizado, no sugerido | CUMPLE | Subagentes sin Write/Edit (`tools`), hook `solo_lectura_git.py` en su frontmatter con tests; el hook bloqueó en vivo `cd … && git diff` y `git -C …` del propio auditor. La compuerta del PR es instrucción por ser juicio humano (research R8). |
| III. Datos ficticios y cero credenciales | CUMPLE | `.mcp.json` usa `${GITHUB_PAT}`; control de tokens en `verificar_ecosistema.sh`; sin datos con forma real. |
| IV. Spec primero | CUMPLE | spec `4abd66f` → plan `7b0c683` → tasks `0acd87b` → implementación `88c1627`. |

Observaciones no bloqueantes del auditor: T015–T018 abiertas en ese momento (esperado) y la
aclaración sobre `git -C`, ya incorporada (hallazgo T016 #5).

## T018 · Revisión de cumplimiento final (dentro de `/abrir-pr 3`)

- **Fecha**: 2026-10-15 · **Ejecución**: `/revisar-cumplimiento specs/003-automatizacion-github`
  (fork con `compliance-auditor`) sobre el estado con las correcciones de la segunda revisión.
- **Veredicto**: CUMPLE (I.1–I.5 N/A; II, III y IV CUMPLE). El hook del auditor bloqueó en vivo
  un `ls` por Bash.
- **Observación aceptada para el futuro**: `solo_lectura_git.py` admite `--ext-diff` y
  `--textconv`, que podrían ejecutar drivers configurados en git; hoy el repo no tiene ninguno.
  Si se agregan, bloquear esas opciones.

## Compuerta de `/abrir-pr`

Sin hallazgos ALTA pendientes y veredicto CUMPLE → se abre el PR.
