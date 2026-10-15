# Tasks: devolución del subagente

- [X] T001 Intentar observar en vivo la llamada a `SubagentHandback` y su `agent_type`: no se
  reprodujo en 20 corridas, ni pidiéndosela al subagente (riesgo residual en spec y quickstart)
- [X] T002 Tests en `src/agent/test_garantias.py`: analista → `allow` explícito sin evento;
  principal, otro subagente, `agent_type` vacío o ausente → negado; herramienta ajena desde un
  subagente → negada; entrada malformada → negada
- [X] T003 `pre_herramientas_permitidas(..., solo_subagentes)` en `garantias.py` y configuración en
  `agente.py` (tests en `test_agente.py`: configuración real y ningún hook que niegue la devolución)
- [X] T004 Verificación en vivo sin regresiones (0 negaciones, delegación completa) y e2e;
  registrar en `quickstart.md`
- [X] T005 Cerrar el ticket con `/abrir-pr 23`
