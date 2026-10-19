# Revisión: enlace del video y narración del guion (#29)

## Revisión independiente (`code-reviewer`, 2026-10-18)

Veredicto: **APROBADO CON OBSERVACIONES**. Sin hallazgos ALTA ni MEDIA.

| # | Severidad | Archivo | Hallazgo | Resolución |
|---|---|---|---|---|
| 1 | BAJA | `demo/GUION_VIDEO.md` | La intro llamaba "acciones reales en el core" a todos los recuadros; ⛔, 🤝 y 🔁 no lo son | Corregido (`9257783`): "muestran lo que realmente pasó en el banco", como el README |
| 2 | BAJA | `demo/GUION_VIDEO.md` | C1: "pide identidad antes de tocar nada", pero antes busca al cliente | Corregido (`9257783`): "busca al cliente y pide identidad antes de operar sobre la tarjeta" |
| 3 | BAJA | `demo/GUION_VIDEO.md` | C3: el documento identifica; la verificación es con la fecha de nacimiento | Corregido (`9257783`) |
| 4 | BAJA | `scripts/verificar_ecosistema.sh` | El AVISO de "pendiente; el autor" ya no puede dispararse y nada comprueba que el enlace siga | Aceptado: FR-004 limita este ticket a documentación; el enlace ya está y el AVISO no da falsos positivos. Reforzar el chequeo queda para un ticket aparte si hace falta |
| 5 | BAJA | `demo/GUION_VIDEO.md` / `README.md` | Duración de los e2e distinta (2–5 vs. 3–4 min) | Corregido (`9257783`): "entre 2 y 5 minutos" en ambos (medido: 1:56 y 5:06) |

Lo que el revisor no pudo comprobar se verificó en la sesión: el enlace responde sin sesión
(oEmbed de YouTube devuelve el título del video), `verificar_ecosistema.sh` termina en "Todo OK"
y la suite unitaria da 455 passed. Una corrida aislada dio 5 fallos que no se reprodujeron en
cuatro corridas posteriores (incluida la misma secuencia); el diff no toca código.
Las correcciones son de redacción; no se pidió una segunda revisión.

## Revisión de cumplimiento (`/revisar-cumplimiento`, 2026-10-18)

| Principio/Regla | Resultado | Evidencia |
|---|---|---|
| I.1–I.5 Reglas de negocio | N/A | Solo documentación; la narración es coherente con las reglas (`demo/GUION_VIDEO.md`) |
| II. Garantizado, no sugerido | N/A | Sin cambios en hooks ni prompt (FR-004) |
| III. Datos ficticios y cero credenciales | CUMPLE | Solo un enlace público de YouTube y montos ficticios |
| IV. Spec primero | CUMPLE | spec, plan y tasks en `8dbd355`, antes de los cambios de documentación; issue #29 |

Veredicto: **CUMPLE**.
