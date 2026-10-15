# Research: casos end-to-end

## R1. Qué se verifica

- **Decision**: invariantes de negocio sobre `agente.estado.eventos` al terminar el caso (y por
  turno cuando el caso lo exige, p. ej. US3 turno 1), no una secuencia exacta de llamadas.
- **Rationale**: el modelo puede pedir datos en otro orden, delegar o no, o reintentar; lo que el
  banco exige es que ciertas acciones ocurran y otras no. Los eventos los registran los hooks y
  reflejan lo que realmente se ejecutó, se negó o falló.
- **Alternatives considered**: comparar contra una secuencia fija (frágil); evaluar el texto con
  otro modelo (no determinista y no valida acciones).

## R2. Aislamiento

- **Decision**: un `AgenteDisputas` nuevo por caso (fixture), con su propio servidor `banco` y
  su propio `EstadoSesion`. La falla transitoria se configura con `monkeypatch.setenv` antes de
  arrancar el agente del caso US5.
- **Rationale**: el core vive en memoria del servidor; el SDK pasa el entorno del proceso al CLI
  y este al servidor stdio (verificado en el #8, F3).

## R3. Agente no disponible

- **Decision**: la fixture captura `AgenteNoDisponible` y llama a `pytest.skip` con el motivo.
- **Rationale**: FR-008; sin sesión de Claude Code el resultado es "omitido", no una traza.

## R4. Evidencia ante una falla

- **Decision**: después de cada turno se imprime la secuencia de eventos (resultado,
  herramienta, agente, argumentos y detalle recortado). pytest muestra lo capturado solo cuando
  el caso falla; las aserciones incluyen un mensaje que dice qué invariante se rompió.
- **Alternatives considered**: hook `pytest_runtest_makereport` en `conftest.py` (más piezas
  para el mismo resultado).

## R5. Tiempo máximo

- **Decision**: `anyio.fail_after(300)` por caso.
- **Rationale**: un turno con delegación tarda ~30–60 s; 5 minutos evita colgar la suite sin
  cortar casos legítimos. SC-003 (< 15 min) se mide en la ejecución completa.

## R6. Guiones de los casos

- **Decision**: mensajes fijos por caso (ver `contracts/casos.md`). Cuando el cliente debe
  aportar datos, se dan completos (nombre, documento y fecha de nacimiento) en un solo mensaje
  de seguimiento para reducir turnos de ida y vuelta.
- **Rationale**: un cliente real suele dar los datos cuando se le piden; dárselos completos
  hace el caso estable sin cambiar lo que se verifica.

## R7. Comando y requisitos

- **Decision**: `uv run pytest -m e2e` (el último `-m` reemplaza al `-m 'not e2e'` de
  `addopts`). Se corrige la descripción del marcador y la línea de `CLAUDE.md`: el agente usa la
  sesión de Claude Code; `ANTHROPIC_API_KEY` es una alternativa, no un requisito.
- **Note**: `CLAUDE.md` es configuración de equipo; el cambio queda señalado en el PR para
  revisión humana.

## R8. Verificaciones confiables

- **Decision**: las funciones de verificación son puras (reciben eventos) y tienen tests
  unitarios con eventos sintéticos, que sí corren por defecto.
- **Rationale**: una verificación demasiado permisiva daría un verde falso en el caso más
  importante (p. ej. disputa sobre umbral); probarla con eventos que deben fallar lo evita.
