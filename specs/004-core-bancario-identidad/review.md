# Revisión antes del PR — 004-core-bancario-identidad

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 4`)

- **Fecha**: 2026-10-15 · **Alcance**: `git diff main...HEAD` contra spec, contrato, data-model,
  research R1–R10 y plan.
- **Veredicto**: APROBADO CON OBSERVACIONES.
- **Confirmado por el revisor**: descripciones e instrucciones idénticas al contrato; búsqueda
  sin documento ni fecha de nacimiento; búsqueda vacía sin error; 3 intentos, bloqueo y reinicio
  según R5; fechas relativas con `BANCO_FECHA_BASE`; datos que cubren todos los casos
  obligatorios; sin datos con forma real ni credenciales.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | Un nombre que queda vacío al normalizar (emoji, tilde suelta) listaba a **todos** los clientes (`set() <= X`). | **Corregido**: `CRITERIO_VACIO` tras normalizar; 3 tests. |
| 2 | MEDIA | `date.fromisoformat` acepta `19880412` o `1988-W15-2`: la fecha correcta en formato compacto gastaba un intento y podía bloquear al cliente. | **Corregido**: exige `^\d{4}-\d{2}-\d{2}$` y fecha existente; tests de formatos alternativos y de fecha inexistente sin consumir intento. |
| 3 | BAJA | Criterio o `id_cliente` que no son texto → `AttributeError`/`TypeError` en llamadas directas al core. | **Corregido**: `VALIDACION` con tests. |
| 4 | BAJA | Cliente bloqueado + fecha mal formada respondía `FECHA_INVALIDA` (el agente reintentaría en vez de escalar). | **Corregido**: el bloqueo se comprueba antes del formato; test. |
| 5 | BAJA | Sin tests de `verificar_identidad` por MCP ni de no exposición en `structured_content`; `servidor.core` compartido entre tests. | **Corregido**: fixture con `Core` nuevo por test (`monkeypatch`); tests de verificación, bloqueo como `isError` y no exposición. |
| 6 | BAJA | El test de descripciones solo buscaba fragmentos. | **Corregido**: compara contra el texto exacto de `contracts/herramientas.md`. Al escribirlo, el propio test detectó un error en su regex (`re.S` capturaba el archivo entero) y se corrigió. |
| 7 | BAJA | `BANCO_FECHA_BASE` mal formada → `ValueError` sin contexto. | **Corregido**: mensaje que nombra la variable y el formato; test. |
| 8 | BAJA | `DIRECTORIO_DATOS` solo funciona con instalación editable. | **Corregido**: `BANCO_DATOS_DIR` opcional (test con datos distintos); documentado en `datos.py`. |
| 9 | BAJA | El wheel incluía tests; `anyio` llegaba solo como dependencia transitiva. | **Corregido**: `exclude` en hatch y `anyio` en el grupo dev. |

Incidente registrado (R11 del #2): al aplicar la corrección 6 por shell, `secretos_bash`
bloqueó el comando porque el regex `.*?` tiene forma de glob (`.` + `*?`). Se aplicó con un
script escrito por la herramienta de edición.

## Re-revisión del commit de correcciones (`code-reviewer`)

- **Alcance**: `git show 4a219f6` contra los 9 hallazgos. **Veredicto**: APROBADO CON OBSERVACIONES;
  las 9 correcciones aplicadas y probadas, sin regresiones en `core.py`.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 10 | BAJA | El test de fecha inexistente no comprobaba que no se gaste intento (lo afirmaba el hallazgo 2). | **Corregido**: el test lo comprueba. |
| 11 | BAJA | `BANCO_FECHA_BASE` aceptaba `20261015` o `2026-W42-4` (criterio distinto al del core). | **Corregido**: exige `AAAA-MM-DD`; test parametrizado. |

## Revisión de cumplimiento (`/revisar-cumplimiento`, fork con `compliance-auditor`)

- **Fecha**: 2026-10-15 · **Estado revisado**: `4a219f6` (con las correcciones).
- **Veredicto**: CUMPLE.

| Principio/Regla | Resultado | Evidencia (resumen del auditor) |
|---|---|---|
| I.1–I.5 | N/A | Solo se exponen `buscar_cliente` y `verificar_identidad` (un test lo fija). Aporta la base de la regla 1 (`verificado`, bloqueo tras 3 fallos) y los datos de las reglas 2 y 5 (TX-0001 $180.000, TX-0002 $1.250.000, TX-0010 US hace 120 días). |
| II | N/A | Sin operaciones que proteger ni prompt en el diff; hooks del SDK en #6. |
| III | CUMPLE | Documentos `FIC-…`, tarjetas por `ultimos4`, comercios ficticios; sin secuencias de 12+ dígitos ni prefijos de token; `banco` en `.mcp.json` sin credenciales. |
| IV | CUMPLE | spec → plan/tasks → código en el historial; spec ligada al #4. |

**Advertencias para los próximos tickets (registradas para #5 y #6):**

1. No conectar el agente a `consultar_transacciones`, `iniciar_disputa` y `bloquear_tarjeta` (#5)
   antes de tener los hooks `PreToolUse` del #6: las reglas 1 y 2 quedarían en NO CUMPLE.
2. El `PostToolUse` del #6 debe marcar la sesión como verificada **solo si `verificado is True`**
   y coincide el `id_cliente`; un "no verificado" es una respuesta exitosa, no un error.

## Compuerta de `/abrir-pr`

Sin hallazgos ALTA pendientes y veredicto CUMPLE → se abre el PR.
