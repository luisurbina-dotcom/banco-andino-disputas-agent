# Data Model: Automatización del ciclo de tickets

## Ticket (GitHub)

| Campo | Fuente | Notas |
|---|---|---|
| número, título, cuerpo | Issue | Insumo de `/speckit-specify` |
| estado | Campo "Status" del Project #1 (`luisurbina-dotcom`) | Todo → In progress → In review → Done |
| item del Project | `projects_get` / `projects_list` | Se agrega al Project si falta |

### Transiciones

| De | A | Quién | Cuándo |
|---|---|---|---|
| Todo | In progress | `/siguiente-ticket` vía `sincronizar-ticket` | Al tomar el ticket |
| In progress | In review | `/abrir-pr` vía `sincronizar-ticket` | Al crear el PR |
| In review | Done | Workflow del Project | Al fusionar el PR (persona) |

## Feature

`NNN-nombre`: `NNN` = siguiente número libre en `specs/`; `nombre` = 2–4 palabras del título del
issue en minúsculas con guiones. Rama y carpeta comparten nombre.

## Hallazgo (review.md)

| Campo | Valores |
|---|---|
| severidad | ALTA, MEDIA, BAJA |
| ubicación | `archivo:línea` |
| hallazgo, recomendación | texto |
| resolución | Corregido, Aceptado (con justificación), Pendiente |

## Veredicto de cumplimiento

| Campo | Valores |
|---|---|
| principio o regla | I–IV; reglas 1–5 cuando la feature las toca |
| resultado | CUMPLE, NO CUMPLE, N/A |
| evidencia | `archivo:línea` o comando |

Regla: regla 1 o 2 implementada sin hook `PreToolUse` del SDK → NO CUMPLE.
