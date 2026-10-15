# Revisión antes del PR — 011-readme-decisiones-entregables

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 11`)

- **Fecha**: 2026-10-15 · **Veredicto**: APROBADO CON OBSERVACIONES (4 MEDIA, 10 BAJA; sin ALTA).
- **Confirmado**: las afirmaciones de README y DECISIONES coinciden con el repo (hooks, reglas,
  subagentes, contrato de errores, comandos); los guiones son idénticos a los mensajes de los e2e;
  no hay credenciales ni datos con forma real en el árbol; el guion del video suma ~3 min 10 s.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | El empaquetado solo revisaba el árbol, no el historial que viaja en `.git`. | **Corregido**: revisa nombres (`git log --all --name-only`) y contenidos de todos los blobs (`rev-list --all --objects` + `cat-file --batch`). Tests con secreto y credencial borrados. **Hallazgo real**: un ejemplo con forma de cédula en `9f25fd6` (#2, escrito antes del hook, corregido en `be92bdc`). **Aceptado por el autor** como excepción fijada por el hash del blob (`EXCEPCIONES_HISTORIAL`), sin reescribir el historial (principio VII); test que exige que el blob exista y que la excepción no cubra otro contenido. |
| 2 | MEDIA | Una URL de `origin` con token entraría en `.git/config`. | **Corregido**: se quita usuario/token de la URL y se revisa `.git/config`; test. |
| 3 | MEDIA | Detector de credenciales estrecho. | **Corregido**: `gh[pousr]_`, `github_pat_`, `sk-ant-`, `AKIA…`, bloques `PRIVATE KEY`; nombres `id_rsa*`, `*.p12`, `*.pfx`; tests. |
| 4 | MEDIA | `SubagentHandback` negado por el guardia (⛔ espurios en C1 y C6; delegación degradada). | **Fuera de alcance**: el autor decidió un ticket aparte, después de este. El guion del video lo advierte. |
| 5 | BAJA | Enlaces simbólicos seguidos al comprimir. | **Corregido**: se rechazan; test. |
| 6 | BAJA | Archivos no UTF-8 sin revisar. | **Corregido**: se decodifican con reemplazo (los blobs del historial también). |
| 7 | BAJA | 50 MB binarios vs. decimales. | **Corregido**: `50_000_000`. |
| 8 | BAJA | Un `.zip` viejo sobrevivía a una validación fallida; sin aviso fuera de `main`. | **Corregido**: se borra antes de validar; aviso si la rama no es `main`; test. |
| 9 | BAJA | Faltaban carpetas de artefactos. | **Corregido**: `site-packages`, `.tox`, `dist`, `build`, `*.egg-info`. |
| 10 | BAJA | Tests sensibles a la firma de commits global. | **Corregido**: `commit.gpgsign=false`. |
| 11 | BAJA | "18 reglas deny" mezcla 16 negaciones y 2 excepciones. | **Corregido** en DECISIONES. |
| 12 | BAJA | La falla cerrada se atribuía solo a `onFailure`. | **Corregido**: `ejecutar_seguro` como garantía y `onFailure` para timeouts. |
| 13 | BAJA | Q1 no corrió sobre el árbol final y con caché caliente. | **Corregido**: Q1′ con caché vacía sobre la rama final (25 s). |
| 14 | BAJA | La comprobación del video pasa con "pendiente". | **Corregido**: aviso (sin fallar) mientras falte el enlace. |

## Re-revisión (`code-reviewer`, estado `9900a9a`)

- **Veredicto**: CAMBIOS REQUERIDOS (1 ALTA, 6 BAJA). Confirmados: parseo del lote, excepción
  mínima (`be92bdc` es hijo directo de `9f25fd6` y solo cambia V3/V4), URL, enlaces, credenciales,
  50 MB, paquete viejo y las afirmaciones de DECISIONES (16 deny + 2 excepciones; `ejecutar_seguro`).

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| R1 | ALTA | `git clone` de una ruta local copia `objects/` entero (también lo descartado con `reset`/`stash`), y la revisión solo recorría lo alcanzable: esos blobs viajarían sin revisar. | **Corregido**: clon con `--no-local` (solo objetos alcanzables) y revisión de **todos** los objetos del clon (`cat-file --batch-all-objects`). Test: un blob agregado y luego descartado con `reset` no existe en el paquete. El paquete real bajó a 1,1 MB / 240 archivos; descomprimido: 94 commits, `git fsck` limpio, árbol limpio. |
| R2 | BAJA | Mensajes de commit y tags sin revisar. | **Corregido**: se revisan los objetos `commit` y `tag`; test con credencial en un mensaje. |
| R3 | BAJA | La excepción por hash apagaba todos los motivos del blob. | **Corregido**: la excepción guarda su único motivo aceptado (forma real); otro motivo en ese blob se reporta. Tests: el blob del repo produce exactamente ese motivo; otro motivo no queda tapado. |
| R4 | BAJA | El test de la excepción falla en clones superficiales. | **Corregido**: se omite si el repo es superficial. |
| R5 | BAJA | El aviso de rama no tenía test. | **Corregido**: test con una rama distinta de `main`. |
| R6 | BAJA | `.git/logs` llevaba la ruta local de quien empaqueta. | **Corregido**: se borra el reflog del clon; test. |
| R7 | BAJA | Una cabecera inesperada de `cat-file` lanzaría una traza. | **Corregido**: `PaqueteInvalido` con la respuesta recibida. |

## Revisión de cumplimiento (`/revisar-cumplimiento`)

- **Estado revisado**: `9900a9a` (las correcciones posteriores solo endurecen `scripts/empaquetar.py` y sus tests; no cambian el alcance auditado). **Veredicto**: **CUMPLE** (III, IV; I.1–I.5 y II N/A).
- No toca `src/` ni `data/`. Datos de demo ficticios (últimos 4 dígitos, `FIC-…`); tokens,
  claves y tarjetas de prueba construidos en tiempo de ejecución; el empaquetado rechaza
  credenciales y datos con forma real en árbol e historial.
- Observaciones: la excepción histórica (`9f25fd6`) está fijada por hash, justificada y respeta
  el principio VII; el `SubagentHandback` negado es una negación de más (no debilita las reglas 1
  y 2) y queda para un ticket aparte.
