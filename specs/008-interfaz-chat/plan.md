# Implementation Plan: Interfaz de chat que hace evidentes las acciones

**Branch**: `008-interfaz-chat` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: `specs/008-interfaz-chat/spec.md` (issue
[#8](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/8))

## Summary

Paquete `chat` con una interfaz de terminal sobre Rich: `indicadores.py` traduce los eventos del
turno (#6/#7) a indicadores principales y secundarios (puro, sin SDK); `vista.py` los dibuja junto
con los mensajes; `app.py` corre el bucle de conversación (teclado o guion) con `AgenteDisputas`.
Arranque: `uv run python -m chat [--guion archivo]`. Detalles en [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12. **Primary Dependencies**: `rich` 15 (ya presente vía
`fastmcp`; se declara explícitamente), `agent` del #6/#7.

**Testing**: pytest sin red: indicadores (puros), vista (consola Rich en memoria) y app con un
agente falso. Verificación en vivo con un guion.

**Constraints**: los indicadores salen de los eventos, nunca del texto del modelo; sin trazas
técnicas al usuario.

**Scale/Scope**: 1 paquete, 4 módulos, 3 archivos de test.

## Constitution Check

| Principio | Cómo lo respeta | Estado |
|---|---|---|
| I–II | No decide reglas: solo muestra lo que hicieron el agente y sus garantías (incluidas las negaciones). | ✅ |
| III | Muestra solo últimos 4 dígitos y datos ficticios; avisa en la bienvenida. | ✅ |
| IV | Spec, plan y tareas antes del código. | ✅ |
| VI | Hace visible la respuesta unificada y cada acción (comportamiento obligatorio 10). | ✅ |
| VII | Tests junto al código. | ✅ |

## Project Structure

```text
pyproject.toml          # + rich declarado; "src/chat" en el wheel
src/chat/
├── __init__.py
├── __main__.py         # python -m chat → app.main()
├── indicadores.py      # Indicador; desde_eventos(eventos); resumen(indicadores)
├── vista.py            # bienvenida, mensaje_cliente, respuesta_agente, indicadores, resumen
├── app.py              # bucle: teclado o --guion; spinner; /salir; AgenteNoDisponible
├── test_indicadores.py
├── test_vista.py
└── test_app.py
specs/008-interfaz-chat/guiones/ejemplo.txt   # guion de demo
```

## Complexity Tracking

No aplica.
