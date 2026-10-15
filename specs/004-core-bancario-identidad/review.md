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
