# Quickstart: documentación previa a la grabación

```bash
uv run python scripts/empaquetar.py --salida /ruta/rama.zip
docker run --rm -v /ruta/rama.zip:/paquete.zip:ro ghcr.io/astral-sh/uv:python3.12-bookworm-slim \
  bash -c 'cd /tmp && python -m zipfile -e /paquete.zip . && cd banco-andino-disputas-agent \
           && uv sync -q && uv run pytest -q'
```

## Resultados (2026-10-15)

| # | Resultado |
|---|---|
| Antes (`main` `6ac9611`, sin `git`) | ❌ Error de carga en `scripts/test_empaquetar.py` (`_es_superficial()` invoca `git` al cargarse) y 13 errores en `.claude/hooks/test_spec_primero.py` (fixture `repo`) |
| Sin `git` | ✅ 408 passed, 43 skipped ("git no está instalado"), 0 errores |
| Con `git` y `unzip` | ✅ 451 passed; `verificar_ecosistema.sh` conserva `rwx` y termina en "Todo OK" |
| Sin `git`, `verificar_ecosistema.sh` | 3 comprobaciones fallan (qué ignora git): esperado, `git` es requisito del README |
| Local | ✅ 451 passed, ruff limpio, "Todo OK" |
| `DECISIONES.md` | 839 palabras (≤ 1.000) |
