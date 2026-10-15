# Tasks: Plugin reutilizable banca-guardrails

**Input**: `specs/010-plugin-banca-guardrails/` (spec, plan, research, data-model, contracts, quickstart)

## Fase 1: Verificación primero

- [X] T001 `.claude/hooks/test_plugin.py`: copias del hook idénticas; bloque de reglas del banco
  idéntico entre auditores; el hook del plugin, ejecutado desde un directorio ajeno, bloquea una tarjeta
  con forma real y permite datos ficticios; `hooks.json` usa `${CLAUDE_PLUGIN_ROOT}` y
  `onFailure: block`; el agente del plugin no tiene Bash ni herramientas de escritura (R3, R5)

## Fase 2: Plugin (US1–US3)

- [X] T002 [US1] `.claude-plugin/marketplace.json` y `plugins/banca-guardrails/.claude-plugin/plugin.json`
- [X] T003 [US2] `plugins/banca-guardrails/hooks/` (`hooks.json` + copias de los scripts)
- [X] T004 [US3] Marcadores del bloque de reglas en `.claude/agents/compliance-auditor.md` y
  agente portable `plugins/banca-guardrails/agents/compliance-auditor.md`
- [X] T005 [US3] Skill portable `plugins/banca-guardrails/skills/revisar-cumplimiento/SKILL.md`

## Fase 3: Documentación y verificación (US4, US5)

- [X] T006 [US5] `plugins/banca-guardrails/README.md` (instalación, piezas, verificación, desinstalación)
- [X] T007 [US4] Sección del plugin en `scripts/verificar_ecosistema.sh` (archivos, JSON válido,
  `claude plugin validate --strict` si el CLI está disponible)
- [X] T008 Q1–Q2 y prueba de instalación aislada Q3–Q7; registrar en `quickstart.md`
- [X] T009 Cerrar el ticket con `/abrir-pr 10`

## Dependencias

T001 → T002–T005 → T006–T007 → T008 → T009.
