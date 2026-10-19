# Implementation Plan: enlace del video y narración del guion

**Branch**: `015-enlace-video-guion` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Se agrega a `demo/GUION_VIDEO.md` la narración ensayada (intro, frases por caso y cierre), y se
reemplaza en el README el texto "pendiente" por el enlace del video cuando el autor lo publique.

## Technical Context

**Language/Version**: Markdown · **Testing**: `verificar_ecosistema.sh` y suite unitaria ·
**Constraints**: sin cambios en `src/`, `data/` ni en la configuración de equipo.

## Constitution Check

| Principio | Evaluación |
|---|---|
| I–II | Sin cambios en el agente ni en sus garantías. ✅ |
| III | Sin datos nuevos; el guion usa los datos ficticios de `demo/`. ✅ |
| IV | spec, plan y tasks antes del cambio; issue #29. ✅ |
| VII | Cambio mínimo de documentación. ✅ |

## Project Structure

```text
demo/GUION_VIDEO.md  # sección "Narración sugerida" y cierre actualizado
README.md            # enlace del video; se quita el pendiente
```

## Complexity Tracking

Sin violaciones.
