# Implementation Plan: concordancia de número en el indicador de consulta

**Branch**: `014-plural-consulta-transacciones` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

`_indicador` en `src/chat/indicadores.py` arma "N transacciones" sin mirar el total. Se aplica la
misma regla que ya usa el indicador de `buscar_cliente`: singular si el total es 1.

## Technical Context

**Language/Version**: Python 3.12 · **Testing**: pytest (unitario, sin red ni API key) ·
**Constraints**: ningún cambio fuera de `src/chat/indicadores.py` y su test.

## Constitution Check

| Principio | Evaluación |
|---|---|
| I–II | Sin cambios en el agente ni en sus garantías. ✅ |
| III | Sin datos nuevos. ✅ |
| IV | spec, plan y tasks antes del cambio; issue #27. ✅ |
| VII | Cambio mínimo; test junto al código. ✅ |

## Project Structure

```text
src/chat/indicadores.py       # singular con total 1
src/chat/test_indicadores.py  # casos 1 y 3
```

## Complexity Tracking

Sin violaciones.
