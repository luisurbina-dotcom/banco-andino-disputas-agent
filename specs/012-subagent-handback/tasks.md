# Tasks: devolución del subagente

- [ ] T001 Confirmar en vivo qué `agent_type` trae la llamada a `SubagentHandback`
- [ ] T002 Tests en `src/agent/test_garantias.py`: subagente → permitido sin evento; principal →
  negado; sin `agent_type` → negado; herramienta ajena desde subagente → negada; entrada
  malformada → negada
- [ ] T003 `pre_herramientas_permitidas(..., solo_subagentes)` en `garantias.py` y configuración en
  `agente.py` (con su test en `test_agente.py`)
- [ ] T004 Verificación en vivo (repetir casos con delegación hasta observar la devolución: 0
  negaciones) y e2e; registrar en `quickstart.md`
- [ ] T005 Cerrar el ticket con `/abrir-pr 23`
