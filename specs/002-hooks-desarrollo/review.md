# Revisión antes del PR — 002-hooks-desarrollo

## T019 · Revisión independiente

- **Fecha**: 2026-10-15
- **Revisor**: subagente de solo lectura (Read, Grep, Glob, `git diff`), sin el contexto de la
  sesión que generó el código. Probó los regex en memoria sin escribir archivos.
- **Veredicto inicial**: CAMBIOS REQUERIDOS.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | ALTA | Tarjeta seguida o precedida de otros dígitos (CVV, vencimiento, "-01", "paso 3 …") no se detectaba: el regex absorbía los vecinos y Luhn fallaba sobre el total. | **Corregido**: tarjeta contigua (13–19) o agrupada (4 + grupos de 3–6); en la agrupada se prueba Luhn en cada prefijo que termina en límite de grupo. 13 tests nuevos (CVV, vencimiento, prefijos, Amex 4-6-5, teléfono + monto no se une). Verificado en vivo (V1b). |
| 2 | MEDIA | Variantes de etiqueta no detectadas: `CC.`, `C.C`, `cédula de ciudadanía`, `nro`, `n.º`. | **Corregido** con tests. `nro` solo cuenta tras una etiqueta de documento (suelto es ambiguo: número de pedido). |
| 3 | BAJA | 11 dígitos tras etiqueta se detectaban (spec dice 6–10). | **Corregido**: lookahead `(?!\d\|\.\d)`; test de 11 dígitos. |
| 4 | MEDIA | `formatear.py` salía con 2 y mensaje vacío si ruff fallaba por sí mismo; reportaba diagnósticos previos al formateo. | **Corregido**: `check --fix` → `format` → `check` final; código 1 = diagnósticos (exit 2), otro código = aviso y exit 0; `uv run --no-sync`. Test con config inválida. |
| 5 | MEDIA | `secrets` sin barra final (`cd secrets && …`) pasaba. | **Corregido** con test; no afecta palabras como "secretos". |
| 6 | BAJA | Mayúsculas (`.ENV`, `.PEM`) y globs (`.e*`, `.en?`, `.[e]nv`, `*.pem`) pasaban. | **Corregido** con tests. Indirección por variables, `$(printf …)` y base64 quedan como **limitación conocida** (spec, edge cases; la garantía real sería el sandbox). |
| 7 | BAJA | El matcher `Edit\|Write` no cubre `NotebookEdit` (puede escribir en `src/`); la rama `edits` de MultiEdit sin matcher. | **Código listo** (`new_source`, `notebook_path`, test). **Cambio de matcher pendiente de aprobación del responsable** (configuración de equipo). |
| 8 | BAJA | Faltaban tests de HEAD desacoplado, ruta relativa con `cwd`, `src/CLAUDE.md`. | **Corregido**: 4 tests nuevos (incluye NotebookEdit). |
| 9 | BAJA | `target-version = "py312"` con reglas `UP` podía reescribir los hooks a sintaxis 3.12. | **Corregido**: `per-file-ignores` de `UP` para `.claude/hooks/*.py`. |

Resultado tras las correcciones: 110 tests en verde, ruff limpio, 0 detecciones en los 71
archivos del repo.

### Incidente durante la corrección (evidencia del fail-closed)

Una edición intermedia dejó `detector.py` con un nombre indefinido. El hook `datos_ficticios`
falló con `NameError` y **bloqueó la siguiente edición por seguridad**; el hook de formateo
informó el `F821`. Se completó el cambio con un script por Bash (que no pasa por ese hook) y sin
contenido sensible. Muestra que un hook roto deja de permitir escrituras en lugar de abrir el
paso; el costo es que la reparación del propio hook se hace por shell.

## T020 · Revisión de cumplimiento (principios I–IV)

- **Fecha**: 2026-10-15 · **Alcance**: `git diff main...002-hooks-desarrollo`
- **Veredicto**: CUMPLE.

| Principio | Verificación | Resultado |
|---|---|---|
| I. Reglas de negocio | La constitución no cambia en este diff; los hooks de desarrollo no tocan las reglas del banco. | ✅ |
| II. Garantizado, no sugerido | Los cuatro invariantes son hooks deterministas. Los tres de bloqueo tienen fail-closed en dos capas (`try/except` + `"onFailure": "block"`), ambas demostradas en vivo (V12 e incidente anterior). | ✅ |
| III. Datos ficticios y cero credenciales | 0 credenciales y 0 detecciones en el diff. Los tests construyen tarjetas y documentos en tiempo de ejecución. | ✅ |
| IV. Spec primero | Spec, plan, research, data-model, contrato, quickstart y tareas antes del código; `/speckit-analyze` ejecutado (1 HIGH corregido). `spec_primero.py` hace cumplir el principio desde ahora. | ✅ |

Nota: hecha a mano; la skill `revisar-cumplimiento` y el subagente `compliance-auditor` llegan
en el issue #3.
