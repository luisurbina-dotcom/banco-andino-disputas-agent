# Quickstart: devolución del subagente

```bash
uv run pytest -q src/agent          # tests del guardia y de la configuración
uv run pytest -m e2e -v             # seis casos con el agente real
```

## Resultados (2026-10-15)

| # | Resultado |
|---|---|
| Tests | ✅ 6 tests nuevos del guardia (subagente permitido sin evento; principal, `agent_type` vacío o ausente negados; herramienta ajena desde un subagente negada; entrada malformada negada) y 1 de la configuración real; 418 en total |
| En vivo, con la corrección | ✅ 6 corridas del chat (C1 y C6, tres veces cada una): 0 negaciones, la consulta la hace el subagente y el principal no la repite |
| Sonda | 4 corridas de C6 registrando toda herramienta ajena que llega al guardia: solo `Agent` (la delegación del principal). Desde el hallazgo, en 18 corridas el subagente no volvió a usar `SubagentHandback` (es intermitente), así que no se observó en vivo con la corrección puesta |
| Evidencia del `agent_type` | Las llamadas que hace el subagente dentro de su contexto llegan con `agent_type` (su `consultar_transacciones` se registra como `analista-transacciones`, y `pre_reglas` depende de eso). Si `SubagentHandback` llegara sin él, el guardia la niega (falla cerrada): nunca peor que antes |
| e2e | ✅ 6/6 en 2 min 05 s |
