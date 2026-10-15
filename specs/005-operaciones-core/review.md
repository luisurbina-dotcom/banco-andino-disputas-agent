# Revisión antes del PR — 005-operaciones-core

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 5`)

- **Fecha**: 2026-10-15 · **Alcance**: `git diff main...HEAD` (14 archivos) contra spec, contrato,
  data-model, research R1–R7 y constitución.
- **Veredicto**: APROBADO CON OBSERVACIONES (sin ALTA).
- **Confirmado por el revisor**: orden de `iniciar_disputa` idéntico a R3; monto leído del core
  (la firma no lo recibe); límites exactos 500 000 y 90 días; `PERMISOS` antes de revelar
  existencia; bloqueo idempotente; escalamiento sin verificación; fallas consumidas primero;
  descripciones idénticas a los contratos; datos ficticios.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | La verificación nunca se revocaba: un cliente verificado que luego acumulaba 3 fallos (bloqueado) seguía pudiendo consultar, disputar y bloquear; y en un servidor compartido, una sesión habilitaba a otras. | **Corregido**: al bloquearse la identidad se retira de los verificados; test verificado → 3 fallos → no verificado. |
| 2 | MEDIA | `escalar_a_analista` (sin verificación, por regla 4) devolvía al modelo nombre del cliente y fecha/monto/comercio de cualquier transacción, y aceptaba transacciones de otro cliente: vía de lectura sin identidad. | **Corregido**: incluir transacciones exige `id_cliente` y que sean de sus tarjetas; al modelo solo vuelve `{id_caso, estado, transacciones_incluidas}`; el resumen enriquecido queda en el core para el analista. Contrato actualizado. |
| 3 | BAJA | Sin test de "PERMISOS antes de revelar existencia" con una transacción inexistente. | **Corregido**: test parametrizado con `TX-0001` y `TX-9999`. |
| 4 | BAJA | Fallas transitorias probadas solo en una herramienta y con cliente verificado. | **Corregido**: test parametrizado por las 4 herramientas sin verificar (TRANSITORIO primero; luego PERMISOS o éxito). |
| 5 | BAJA | `configurar_fallas` aceptaba nombres con error de tipeo o de herramientas que nunca fallan, y programaba parcialmente. | **Corregido**: valida contra las 4 herramientas operativas y parsea todo antes de programar; tests. |
| 6 | BAJA | Sin test de que el arranque aplique `BANCO_FALLAS_TRANSITORIAS`. | **Corregido**: `aplicar_configuracion_del_entorno()` con test por `monkeypatch.setenv`. |
| 7 | BAJA | FR-011: faltaba qué hacer ante `DISPUTA_EXISTENTE` y "cuándo no" en consultar y bloquear. | **Corregido** en contrato y servidor desde una sola fuente; el test de igualdad exacta lo confirma. |
| 8 | BAJA | SC-006 (< 5 s) no se cumple: 7–12 s. | **Aceptado con justificación**: los tests en sí duran < 1 s; el tiempo es la importación de `fastmcp` (5–6,5 s) bajo la carga de esta máquina WSL. Se informa en el PR; no hay acción en el código. |

Observación del proceso (para la defensa): al editar `test_servidor.py` en tres pasos, el hook de
formateo (`ruff check --fix`) borró entre ediciones un import que todavía no se usaba (F401), y la
edición siguiente quedó con un nombre indefinido que el mismo hook reportó. Se resolvió escribiendo
los cambios en una sola operación. Es el costo esperado de autocorregir después de cada edición.

## Re-revisión del commit de correcciones (`code-reviewer`)

- **Alcance**: `git show 4e305ec`. **Veredicto**: APROBADO CON OBSERVACIONES; los 8 hallazgos
  corregidos y probados, sin regresiones.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 9 | BAJA | El esperado y el resultado de C6 en el quickstart eran anteriores a la salida reducida. | **Corregido**: esperado actualizado y C6 repetido en vivo tras `4e305ec`. |
| 10 | BAJA | La descripción de `escalar_a_analista` no decía que incluir transacciones exige `id_cliente`. | **Corregido** en contrato y servidor con el mismo texto (test de igualdad exacta). |
| 11 | BAJA | Sin verificación, `TRANSACCION_NO_ENCONTRADA` frente al éxito revela si una transacción pertenece a un cliente (y crea casos). | **Aceptado**: impacto mínimo (el modelo no conoce ids de transacciones sin consultar, y consultar exige verificación). Se deja como nota para el hook del #6. |
| 12 | BAJA | Import de `ErrorCore` dentro de una función de test (rodeo del F401). | **Corregido**: import al encabezado. |

## Revisión de cumplimiento (`/revisar-cumplimiento`)

- **Fecha**: 2026-10-15 · **Veredicto**: **NO CUMPLE**.

| Principio/Regla | Resultado | Evidencia (resumen del auditor) |
|---|---|---|
| I.1 Identidad primero | CUMPLE (servidor) | `_exigir_verificado` antes de leer datos; verificado solo por `verificar_identidad` exitosa y revocado al bloquearse. |
| I.2 Umbral $500.000 | CUMPLE (servidor) | Monto del core; la firma no recibe monto; tests de límite. |
| I.3 Bloqueo inmediato | CUMPLE | Sin aprobación, idempotente, exige identidad. |
| I.4 Persona a pedido | CUMPLE (parte del servidor) | Escalar sin verificación; descripciones dicen cuándo no consultar/disputar. Prompt del agente en #6. |
| I.5 Fuera de política | CUMPLE (parte del servidor) | `POLITICA_NO_CUBRE` antes del umbral, mensaje de escalar. |
| **II. Garantizado (reglas 1 y 2)** | **NO CUMPLE** | No existen aún los hooks `PreToolUse`/`PostToolUse` del Agent SDK (`src/agent/` solo tiene `CLAUDE.md`). La constitución los exige; el control del servidor es defensa en profundidad. Atenuantes: ningún agente usa estas herramientas, nada depende del prompt y el servidor decide con datos del core. |
| III. Datos ficticios | CUMPLE | Sin credenciales ni datos con forma real. |
| IV. Spec primero | CUMPLE | spec → plan/tasks → código en el historial. |

## Compuerta de `/abrir-pr`

**Veredicto NO CUMPLE → el PR no se abrió** y se pidió una decisión humana.

### Aceptación explícita del responsable (2026-10-15)

El responsable (Luis F. Urbina Moreno) **acepta** fusionar el #5 con el principio II pendiente,
con esta justificación:

1. Ningún agente usa todavía estas herramientas: el agente se construye en el #6, el siguiente
   ticket, que agrega los hooks `PreToolUse`/`PostToolUse` del Agent SDK para las reglas 1 y 2.
2. Mientras tanto, el servidor ya protege las reglas 1 y 2 con datos del core (verificación en
   memoria, monto leído por `id_transaccion`); nada depende del prompt.
3. Esperar al #6 obligaría a mezclar dos tickets en un PR y degradaría la trazabilidad por ticket.

**Condición**: el PR del #6 debe pasar `/revisar-cumplimiento` con el principio II en CUMPLE; si no,
el #6 no se fusiona. Alternativa descartada: esperar al #6 con una rama apilada.
