# Tasks: devolución del subagente

- [X] T001 Intentar observar en vivo la llamada a `SubagentHandback` y su `agent_type`: no se
  reprodujo en 20 corridas, ni pidiéndosela al subagente (riesgo residual en spec y quickstart)
- [X] T002 Tests en `src/agent/test_garantias.py`: subagente → permitido sin evento; principal →
  negado; sin `agent_type` → negado; herramienta ajena desde subagente → negada; entrada
  malformada → negada
- [X] T003 `pre_herramientas_permitidas(..., solo_subagentes)` en `garantias.py` y configuración en
  `agente.py` (con su test en `test_agente.py`)
- [X] T004 Verificación en vivo sin regresiones (0 negaciones, delegación completa) y e2e;
  registrar en `quickstart.md`
- [ ] T005 Cerrar el ticket con `/abrir-pr 23`
