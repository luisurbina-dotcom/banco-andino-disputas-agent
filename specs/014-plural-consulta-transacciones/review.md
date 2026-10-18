# Revisión: concordancia de número en el indicador de consulta (#27)

## Revisión independiente (`code-reviewer`, 2026-10-17)

Veredicto: **APROBADO CON OBSERVACIONES**. Sin hallazgos ALTA ni MEDIA.

| # | Severidad | Archivo | Hallazgo | Resolución |
|---|---|---|---|---|
| 1 | BAJA | `src/chat/test_indicadores.py` | El caso borde "total 0 o ausente" de la spec no tenía test | Corregido: casos `{"total": 0}` y `{}` en `test_consulta_concuerda_en_numero` |
| 2 | BAJA | `src/chat/test_indicadores.py` | Los casos se agregaban a un test que ya mezcla comportamientos (`.claude/rules/tests.md`) | Corregido: test propio parametrizado con 1, 3, 0 y ausente |
| 3 | BAJA | `src/chat/indicadores.py` | `"transacci" + "ón"/"ones"` impide buscar la palabra completa | Corregido: `"transacción" if total == 1 else "transacciones"` |

Lo que el revisor no pudo comprobar se verificó en la sesión: el test nuevo falla con el código de
`main` (caso total 1) y pasa con la corrección; ningún otro archivo depende del texto anterior;
455 tests unitarios en verde y ruff limpio. Las correcciones son de forma; no se pidió una segunda
revisión.

## Revisión de cumplimiento (`/revisar-cumplimiento`, 2026-10-17)

| Principio/Regla | Resultado | Evidencia |
|---|---|---|
| I.1–I.5 Reglas de negocio | N/A | El diff no toca `src/agent/`, `src/mcp_server/`, hooks ni `data/`; FR-002 lo excluye |
| II. Garantizado, no sugerido | N/A | Hooks del Agent SDK sin cambios; ninguna garantía pasa al prompt |
| III. Datos ficticios y cero credenciales | CUMPLE | Solo totales (`0`, `1`, `3`) y el nombre de agente `principal` en el test |
| IV. Spec primero | CUMPLE | spec, plan y tasks en `2b41bb9`, antes del código (`6b7cbd3`, `8f2441f`); issue #27; test junto al código |

Veredicto: **CUMPLE**.
