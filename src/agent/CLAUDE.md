# Agente (Claude Agent SDK)

Este archivo solo se carga cuando trabajas en `src/agent/`. Existe porque aquí un error de
criterio rompe una regla de negocio del banco, y estas instrucciones no hacen falta en el
resto del repo.

## Reglas de negocio garantizadas con hooks

- Las reglas 1 (identidad verificada) y 2 (umbral de $500.000) se hacen cumplir con hooks
  `PreToolUse` del SDK. Nunca solo con el prompt.
- El hook decide con el estado de la sesión y con los datos del core (por ejemplo, busca el
  monto real por el id de la transacción). Nunca confía en los argumentos que envía el modelo.
- El estado "identidad verificada" solo lo establece un `PostToolUse` sobre una respuesta
  exitosa de `verificar_identidad`.
- Las reglas 3 a 5 van en el prompt del sistema y en las descripciones de las herramientas.

## Ciclo y delegación

- El ciclo continúa o termina según la razón de parada del modelo. Nada de límites fijos de
  iteraciones ni de buscar palabras en el texto.
- El análisis de transacciones sospechosas se delega en un subagente con herramientas
  restringidas. El contexto se le pasa de forma explícita en el prompt; no hereda la
  conversación.
- Una solicitud con varios asuntos se separa, se resuelve cada uno y se responde una sola vez.

## Handoff al analista

El analista no ve la conversación. El resumen de `escalar_a_analista` incluye siempre:
cliente, transacciones, montos, acciones realizadas, causa del escalamiento y acción
recomendada.
