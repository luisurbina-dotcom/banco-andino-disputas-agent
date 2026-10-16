# Implementation Plan: documentación previa a la grabación

**Branch**: `013-docs-previas-grabacion` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

## Summary

`scripts/test_empaquetar.py` marca todo el módulo con `skipif` cuando `shutil.which("git")` es
`None`, y `_es_superficial()` deja de invocar `git` si no está (hoy lo invoca al cargarse y corta
la suite). Además se ajustan tres documentos: el guion del video, `DECISIONES.md` y el README.

## Technical Context

**Language/Version**: Python 3.12 · **Testing**: pytest; verificación en un contenedor
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim` con y sin `git`, a partir del `.zip` ·
**Constraints**: `DECISIONES.md` ≤ 1.000 palabras; ningún cambio en `src/` ni en la configuración
de equipo.

## Constitution Check

| Principio | Evaluación |
|---|---|
| I–II | Sin cambios en el agente ni en sus garantías. ✅ |
| III | Sin datos nuevos. ✅ |
| IV | spec, plan y tasks antes del cambio; issue #25. ✅ |
| VII | Cambio mínimo; tests junto al código. ✅ |

## Project Structure

```text
scripts/test_empaquetar.py  # pytestmark skipif sin git; _es_superficial sin git
README.md                   # cómo descomprimir el paquete
DECISIONES.md               # quién decidió cada excepción y riesgo residual
demo/GUION_VIDEO.md         # aviso de SubagentHandback actualizado
```

## Research

- **Decision**: `pytestmark` a nivel de módulo en lugar de capturar `FileNotFoundError` en cada
  test: un único motivo visible y ningún test intenta `git`.
- **Alternatives**: `pytest.importorskip` no aplica (falta un binario, no un módulo).
- Otros tests del repo que usan `git` se verifican en el mismo contenedor; si alguno falla sin
  `git`, se trata igual.

## Complexity Tracking

Sin violaciones.
