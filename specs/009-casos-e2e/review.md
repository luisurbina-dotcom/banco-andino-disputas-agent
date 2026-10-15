# Revisión antes del PR — 009-casos-e2e

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 9`)

- **Fecha**: 2026-10-15 · **Veredicto**: APROBADO CON OBSERVACIONES (2 MEDIA, 6 BAJA; sin ALTA).
- **Confirmado**: las verificaciones usan los mismos formatos que registran los hooks y que
  devuelve el servidor; las disputas solo cuentan con `id_disputa`; el aislamiento por caso, el
  tiempo máximo y la exclusión por defecto son correctos; solo datos ficticios.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | Falso verde en C4: `conversar` ignoraba `Turno.error`; un turno con error del SDK (sin agente) dejaba C4 en verde con cero eventos. | **Corregido**: un turno con error falla el caso (o lo omite si es el primero, ver #2) y cada turno exige `stop_reason`. Tests unitarios con turnos sintéticos. |
| 2 | MEDIA | FR-008 a medias: sin sesión válida el error llega por turno y los casos fallaban con aserciones engañosas. | **Corregido**: un error en el primer turno omite el caso con el texto del error ("Agente no disponible: …"). Test. |
| 3 | BAJA | C2: el primer evento podía ser un escalamiento fallido seguido de investigación. | **Corregido**: `investigo_antes_de_escalar` exige que antes del primer escalamiento confirmado solo haya intentos de escalar; tests. |
| 4 | BAJA | Regla 2 verificada solo para TX-0002. | **Corregido**: `disputas_sobre_umbral` (monto confirmado por el banco > $500.000) en C1 y C6; tests. |
| 5 | BAJA | `verificado_antes_de_operar` aceptaba la verificación de cualquier cliente y no se reiniciaba ante `IDENTIDAD_BLOQUEADA`. | **Corregido**: exige la verificación del cliente de la operación y descuenta identidades bloqueadas; tests. |
| 6 | BAJA | C3 exigía buscar por nombre en el turno 1 (posible falso rojo); spec y contrato no coincidían. | **Corregido**: si busca por el nombre, debe haber 2 coincidencias; lo duro es no verificar ni operar en el turno 1. Contrato alineado con la spec. |
| 7 | BAJA | `fail_after` envolvía el cierre del agente. | **Corregido**: el tiempo máximo cubre solo la conversación (`conversar`). |
| 8 | BAJA | `test_e2e.py` se aparta de `test_<módulo>.py`. | **Aceptado y documentado** en `plan.md`: los casos prueban el agente completo, no un módulo. |

Verificado tras las correcciones: 397 unitarios, ruff limpio y una tercera ejecución e2e 6/6
(4 min 01 s).
