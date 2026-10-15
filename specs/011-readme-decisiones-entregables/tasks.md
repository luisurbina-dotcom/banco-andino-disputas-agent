# Tasks: README, DECISIONES.md y entregables

**Input**: `specs/011-readme-decisiones-entregables/` (spec, plan, research, data-model, contracts, quickstart)

## Fase 1: Empaquetado (US3), tests primero

- [ ] T001 `scripts/test_empaquetar.py`: nombres prohibidos, credenciales y datos con forma real
  se rechazan; `.env.example` se permite; el `.zip` incluye `.git` y respeta el tamaño máximo
  (repos git de prueba en `tmp_path`); `scripts` en `testpaths`
- [ ] T002 `scripts/empaquetar.py` (R1, R2, contrato)

## Fase 2: Documentos y guiones (US1, US2, US4)

- [ ] T003 [US4] Guiones `demo/c1…c6` y `demo/GUION_VIDEO.md`
- [ ] T004 [US2] `DECISIONES.md` (11 necesidades, ≤ 1.000 palabras)
- [ ] T005 [US1] `README.md`
- [ ] T006 Sección README/DECISIONES en `scripts/verificar_ecosistema.sh`

## Fase 3: Verificación

- [ ] T007 Q1–Q7; registrar resultados en `quickstart.md`
- [ ] T008 Cerrar el ticket con `/abrir-pr 11`

## Dependencias

T001 → T002; T003–T006 independientes; todo → T007 → T008.
