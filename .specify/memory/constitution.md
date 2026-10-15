# Constitución — Agente de Disputas de Banco Andino

Agente de disputas y contracargos para Banco Andino (banco ficticio), construido con el
Claude Agent SDK en Python 3.12. Consume un servidor MCP propio (FastMCP, stdio) que simula
el core bancario con datos ficticios en archivos JSON locales. El desarrollo se hace con
Claude Code siguiendo Spec Driven Development (Spec Kit), y el backlog vive en un GitHub
Project que se sincroniza de forma autónoma a través del MCP de GitHub. La documentación
del proyecto se escribe en español.

## Core Principles

### I. Reglas de negocio del banco (NO NEGOCIABLES)

Los montos están en pesos colombianos ficticios (COP). Los umbrales son fijos y no se
parametrizan para relajarlos.

1. **Identidad primero.** Ninguna operación sobre productos del cliente
   (`consultar_transacciones`, `iniciar_disputa`, `bloquear_tarjeta`) ocurre sin que
   `verificar_identidad` haya confirmado la identidad en la sesión actual.
2. **Umbral de disputa.** Una disputa por un monto **≤ $500.000** se inicia de forma
   automática. Por encima de ese monto MUST escalarse a un analista humano y MUST NOT
   iniciarse automáticamente.
3. **Bloqueo inmediato.** El bloqueo de tarjeta por sospecha de fraude es inmediato y no
   requiere aprobación. Sí requiere identidad verificada (regla 1).
4. **Persona a pedido.** Si el cliente pide explícitamente hablar con una persona, el agente
   escala de inmediato, sin investigar ni consultar transacciones antes.
5. **Fuera de política, se escala.** Si la política no cubre el caso (por ejemplo, un cobro
   de un comercio en el exterior con más de 90 días), el agente escala en lugar de
   improvisar.

Razón: son el contrato del banco con el regulador y con el cliente; una violación es una
falla grave independientemente del resto de la solución.

### II. Garantizado, no sugerido

- Las reglas 1 y 2 MUST hacerse cumplir con hooks `PreToolUse` del Agent SDK. Una
  instrucción en el prompt NO es suficiente.
- Los hooks MUST decidir con base en el estado de la sesión y en los datos del core (por
  ejemplo, el monto real de la transacción según su identificador). MUST NOT confiar en
  valores aportados por el modelo en los argumentos de la herramienta.
- El estado "identidad verificada" solo lo establece un `PostToolUse` sobre una respuesta
  exitosa de `verificar_identidad`.
- Las reglas 3, 4 y 5 se implementan con el prompt del sistema, las descripciones de las
  herramientas y errores de negocio del servidor MCP (por ejemplo, `POLITICA_NO_CUBRE` con
  la indicación de escalar).

Razón: un modelo puede ignorar instrucciones; un hook no.

### III. Solo datos ficticios y cero credenciales

- Ningún dato real de clientes, cuentas, tarjetas o documentos de identidad, ni en código,
  fixtures, logs, tests, configuración ni documentación.
- Las tarjetas se representan solo por sus últimos 4 dígitos o con números que **no pasan**
  la validación de Luhn. Los documentos usan un formato claramente ficticio.
- Ninguna credencial en el repositorio. Los archivos `.env` y de secretos nunca se versionan
  y Claude Code no los lee ni los modifica. Las credenciales llegan por variables de entorno
  (por ejemplo, `${GITHUB_PAT}` en `.mcp.json`).
- Se hace cumplir con hooks y reglas de permisos de Claude Code.

Razón: un dato con apariencia real o una credencial filtrada es una falta grave aunque el
resto sea correcto.

### IV. Especificación primero

- No se escribe código de producción sin `spec.md`, `plan.md` y `tasks.md` en
  `specs/<feature>/`, y cada feature MUST estar asociada a un issue de GitHub.
- El ciclo por ticket es: `/speckit-specify` (con el issue como insumo) → `/speckit-clarify`
  si hay ambigüedad → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` →
  `/speckit-implement` → `/speckit-converge` si quedan brechas.
- Un hook de Claude Code bloquea la edición de código de producción cuando no existe la
  especificación de la feature activa.

Razón: el qué y el porqué se acuerdan antes del cómo, y quedan como evidencia versionada.

### V. Contrato de herramientas MCP

- Las descripciones de las herramientas MUST eliminar la ambigüedad: `buscar_cliente`
  localiza candidatos (por documento, nombre o últimos 4 dígitos) y puede devolver varias
  coincidencias; `verificar_identidad` confirma a un único cliente con un dato adicional.
  Ante varias coincidencias, el agente MUST pedir otro identificador y MUST NOT elegir.
- Los errores MUST ser estructurados, con una categoría (`TRANSITORIO`, `VALIDACION`,
  `NEGOCIO`, `PERMISOS`), un indicador `reintentable` y un mensaje accionable.
- Una búsqueda sin resultados NO es un error: devuelve una lista vacía.

Razón: el modelo decide con lo que la herramienta le dice; descripciones y errores
ambiguos producen decisiones erróneas.

### VI. Agente confiable

- El ciclo agéntico continúa o termina según la razón de parada del modelo, nunca por un
  número fijo de iteraciones ni por buscar palabras en el texto.
- Una solicitud con varios asuntos se separa en sus partes, cada una se resuelve y se
  responde al cliente de forma unificada.
- Al menos una parte del trabajo (el análisis de transacciones sospechosas) se delega en un
  subagente, al que se le pasa el contexto de forma explícita.
- El handoff al analista es autocontenido, porque el analista no ve la conversación:
  cliente, transacciones, montos, acciones realizadas, causa del escalamiento y acción
  recomendada.
- El agente escala cuando corresponde (reglas 2, 4 y 5) y no escala lo que puede resolver.

### VII. Calidad, trazabilidad y simplicidad

- Los tests viven junto al código que prueban (`test_<módulo>.py` en la misma carpeta) y se
  ejecutan con pytest. Los tests unitarios no requieren API key; los e2e se marcan aparte.
- El código se formatea con ruff después de cada edición.
- Antes de abrir un pull request, el código pasa por una revisión independiente de la sesión
  que lo generó y por una revisión de cumplimiento de las reglas de negocio.
- Cada pull request referencia y cierra su issue. El estado del ticket en el Project se
  sincroniza de forma automática: Todo → In progress → In review → Done.
- El historial de git no se reescribe.
- Es un MVP: se prefieren pocas piezas bien ubicadas y justificadas. Una pieza adicional
  MUST resolver una necesidad real.

## Matriz de cumplimiento: hooks vs. instrucciones

Criterio: lo que es un **invariante** de seguridad, cumplimiento o integridad se hace
cumplir con un mecanismo determinista (hook o regla de permisos). Lo que es **juicio**, tono
o estilo va en instrucciones (prompt, CLAUDE.md, reglas por ruta, descripciones).

| Asunto | Mecanismo | Tipo |
|---|---|---|
| Regla 1: identidad verificada | Hook `PreToolUse` y `PostToolUse` del Agent SDK | Garantizado |
| Regla 2: umbral de $500.000 | Hook `PreToolUse` del Agent SDK con el monto leído del core | Garantizado |
| Regla 3: bloqueo inmediato | Prompt y descripción de `bloquear_tarjeta` | Instrucción |
| Regla 4: escalar a pedido | Prompt del sistema | Instrucción |
| Regla 5: fuera de política | Error `NEGOCIO`/`POLITICA_NO_CUBRE` del servidor y prompt | Mixto |
| Datos con forma de tarjeta o documento real | Hook `PreToolUse` de Claude Code sobre ediciones | Garantizado |
| `.env` y secretos | `permissions.deny` y hook de Claude Code | Garantizado |
| Código sin spec | Hook `PreToolUse` de Claude Code | Garantizado |
| Formateo | Hook `PostToolUse` de Claude Code (ruff) | Garantizado |
| Convenciones de código y tests | CLAUDE.md y `.claude/rules/` por ruta | Instrucción |

## Flujo de desarrollo

1. Claude Code toma el siguiente ticket en Todo del Project, lo mueve a In progress y lo usa
   como insumo de `/speckit-specify`, en una rama propia de la feature.
2. Se completan el plan, las tareas y el análisis, y se implementa con tests.
3. Antes del PR: revisión independiente (subagente revisor) y revisión de cumplimiento.
4. Se abre el PR con `Closes #<issue>` y el ticket pasa a In review. El issue recibe un
   comentario con lo especificado, lo decidido y lo pendiente.
5. Al fusionar el PR, el ticket pasa a Done.

Un evaluador debe poder reconstruir el avance del proyecto solo mirando GitHub.

## Governance

- Esta constitución prevalece sobre cualquier otra práctica, instrucción o configuración del
  repositorio. `CLAUDE.md` la importa como fuente única de verdad.
- Enmiendas: se proponen en un PR que modifica este archivo, explica el motivo y actualiza
  la versión. Si una enmienda afecta especificaciones vigentes, se revisan con
  `/speckit-analyze`.
- Versionado semántico: MAJOR cuando se elimina o redefine un principio, MINOR cuando se
  añade o amplía uno, PATCH para aclaraciones de redacción.
- Cumplimiento: cada PR verifica los principios I a IV en la revisión de cumplimiento. Una
  complejidad adicional MUST justificarse en el `plan.md` de la feature.

**Version**: 1.0.0 | **Ratified**: 2026-10-15 | **Last Amended**: 2026-10-15
