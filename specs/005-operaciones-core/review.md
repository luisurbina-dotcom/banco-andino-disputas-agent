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
