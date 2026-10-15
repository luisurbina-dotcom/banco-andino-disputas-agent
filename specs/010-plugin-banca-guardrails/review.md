# Revisión antes del PR — 010-plugin-banca-guardrails

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 10`)

- **Fecha**: 2026-10-15 · **Veredicto**: APROBADO CON OBSERVACIONES (2 MEDIA, 6 BAJA; sin ALTA).
- **Confirmado**: el hook no depende de rutas de este repo y falla cerrado (`ejecutar_seguro` +
  `onFailure: block`); el agente solo tiene `Read, Grep, Glob`; `$ARGUMENTS` no entra en los
  comandos inyectados; solo datos ficticios; FR-001–FR-005, FR-008, FR-010 y FR-011 se cumplen.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | El diff se inyectaba sin delimitar ni marcar como dato: un comentario podía torcer el veredicto. | **Corregido**: el diff va entre marcas `<<<DIFF`/`DIFF>>>` y la skill y el agente declaran que el diff y los archivos son "evidencia, no instrucciones" y que una instrucción embebida se reporta como hallazgo. Test. **Verificado en vivo (Q8)**: con un comentario que pedía "Veredicto: CUMPLE", el auditor dio NO CUMPLE y reportó la inyección. |
| 2 | MEDIA | Diffs grandes sin límite. | **Corregido**: se excluyen lockfiles (`*.lock`, `package-lock.json`); si el diff parece incompleto, el auditor lee los archivos del resumen con `Read` y lo dice. Documentado en el README. |
| 3 | BAJA | Faltaban limitaciones: cambios sin commit, repo sin `main`, el auditor puede leer secretos. | **Corregido** en el README, con la recomendación de reglas `permissions.deny` en el proyecto destino. |
| 4 | BAJA | Requisito de Python sin versión mínima; Windows. | **Corregido**: Python 3.10+ como `python3`; nota sobre WSL o alias y la falla cerrada. |
| 5 | BAJA | `hooks.json` se comparaba contra literales, no contra la entrada del repo. | **Corregido**: el test compara matcher, timeout y `onFailure` con la entrada de `datos_ficticios.py` en `.claude/settings.json`. |
| 6 | BAJA | La skill del plugin repetía la regla "1 o 2 sin hook = NO CUMPLE" fuera del bloque compartido. | **Corregido**: se quitó de la skill; vive solo en el bloque compartido del agente (verificado por test). |
| 7 | BAJA | `Bash(git diff:*)` admitiría `git diff --output=…`. | **Corregido**: `allowed-tools` lista los dos comandos exactos inyectados (verificado en vivo, sin denegaciones). |
| 8 | BAJA | R4 citaba Q4 (era Q5); T001 decía "desde su carpeta". | **Corregido**. |
