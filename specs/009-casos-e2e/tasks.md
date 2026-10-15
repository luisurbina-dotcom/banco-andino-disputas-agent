# Tasks: Casos de prueba obligatorios end-to-end

**Input**: `specs/009-casos-e2e/` (spec, plan, research, data-model, contracts/casos.md, quickstart)

## Fase 1: Verificaciones (base para todos los casos)

- [X] T001 Tests unitarios (sin marcador) de las funciones de verificación con eventos
  sintéticos que deben pasar y que deben fallar, en `src/agent/test_e2e.py` (R8)
- [X] T002 Funciones de verificación puras (`exitosos`, `llamadas`, `disputas_abiertas`,
  `escalamientos`, `verificado_antes_de_operar`, `investigo_antes_de_escalar`, `disputas_sobre_umbral`) en `src/agent/test_e2e.py`
- [X] T003 Fixture del agente por caso (core aislado, `pytest.skip` si `AgenteNoDisponible`,
  `fail_after(300)`) y helper `conversar` que imprime los eventos por turno (R2–R5)

## Fase 2: Casos (US1–US6, contracts/casos.md)

- [X] T004 [US1] Caso C1, mensaje de ejemplo
- [X] T005 [US2] Caso C2, persona a pedido
- [X] T006 [US3] Caso C3, mismo nombre (invariantes del turno 1 y finales)
- [X] T007 [US4] Caso C4, disputa sin identidad
- [X] T008 [US5] Caso C5, falla transitoria (`monkeypatch.setenv`)
- [X] T009 [US6] Caso C6, fuera de política

## Fase 3: Comando, documentación y verificación (US7)

- [X] T010 Descripción del marcador `e2e` en `pyproject.toml` y línea del comando en
  `CLAUDE.md` (sesión de Claude Code o clave; señalar en el PR para revisión humana) (R7)
- [X] T011 Test unitario de FR-008: la fixture omite el caso si el agente no arranca
- [X] T012 Ejecución completa Q2 y repetición Q3; registrar resultados y tiempos en
  `quickstart.md`. Si un caso revela un defecto del agente, corregirlo con su test unitario
- [ ] T013 Cerrar el ticket con `/abrir-pr 9`

## Dependencias

T001 → T002 → T003 → T004–T009 (independientes entre sí) → T010–T011 → T012 → T013.
