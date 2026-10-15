"""Utilidades compartidas por los hooks de Claude Code del proyecto.

Solo biblioteca estándar y compatible con Python 3.10+: los hooks se ejecutan con `python3`,
sin entorno virtual, para que arranquen rápido.

Contrato (specs/002-hooks-desarrollo/contracts/hooks.md):
- exit 0 → permitir; exit 2 + stderr → bloquear y explicar a Claude.
- Cualquier otro código de salida sería un error NO bloqueante, por eso los hooks de bloqueo
  usan `ejecutar_seguro`, que convierte toda excepción en un bloqueo (fail-closed).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn


def leer_evento() -> dict:
    """Lee el JSON del evento que Claude Code envía por stdin."""
    evento = json.load(sys.stdin)
    if not isinstance(evento, dict):
        raise ValueError("el evento no es un objeto JSON")
    return evento


def bloquear(hook: str, motivo: str) -> NoReturn:
    """Bloquea la herramienta: mensaje a Claude por stderr y exit 2."""
    print(f"[{hook}] {motivo}", file=sys.stderr)
    sys.exit(2)


def raiz_repo() -> Path:
    """Raíz del proyecto: $CLAUDE_PROJECT_DIR o, si no está, la raíz de git."""
    desde_env = os.environ.get("CLAUDE_PROJECT_DIR")
    if desde_env:
        return Path(desde_env).resolve()
    salida = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(salida.stdout.strip()).resolve()


def texto_nuevo(evento: dict) -> str:
    """Contenido nuevo que la herramienta va a escribir (Write, Edit o MultiEdit)."""
    entrada = evento.get("tool_input") or {}
    if "content" in entrada:
        return str(entrada["content"])
    if "new_string" in entrada:
        return str(entrada["new_string"])
    if "edits" in entrada:
        return "\n".join(str(e.get("new_string", "")) for e in entrada["edits"])
    return ""


def ejecutar_seguro(hook: str, fn: Callable[[dict], None]) -> None:
    """Ejecuta un hook de bloqueo; ante cualquier error interno, bloquea (fail-closed)."""
    try:
        fn(leer_evento())
    except SystemExit:
        raise
    except Exception as error:  # cualquier fallo debe bloquear
        bloquear(hook, f"Error interno: {type(error).__name__}. Se bloquea por seguridad.")
    sys.exit(0)
