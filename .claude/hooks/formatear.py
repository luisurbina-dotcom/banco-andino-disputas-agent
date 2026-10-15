"""PostToolUse (Edit|Write): formatea y autocorrige con ruff cada archivo Python editado.

Necesidad 7 del ecosistema. Nunca bloquea por un fallo propio: si uv o ruff no están, avisa y
sale con 0. Si quedan problemas no corregibles, los envía a Claude con exit 2 (en PostToolUse
no revierte la edición, solo informa).
"""

import shutil
import subprocess
import sys
from pathlib import Path

from comun import leer_evento, raiz_repo


def avisar(mensaje: str) -> None:
    print(f"[formatear] {mensaje}", file=sys.stderr)


def main() -> int:
    try:
        ruta = Path((leer_evento().get("tool_input") or {}).get("file_path", ""))
        if ruta.suffix != ".py" or not ruta.is_file():
            return 0
        if shutil.which("uv") is None:
            avisar("uv no está instalado; no se formateó el archivo.")
            return 0
        raiz = raiz_repo()
        config = raiz / "pyproject.toml"
        opciones = ["--config", str(config)] if config.is_file() else []
        # --no-sync: un hook no debe instalar dependencias ni depender de la red.
        ruff = ["uv", "run", "--no-sync", "--quiet", "ruff"]

        def correr(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [*ruff, *args, *opciones, str(ruta)], cwd=raiz, capture_output=True, text=True
            )

        # Primero las correcciones (pueden borrar líneas), luego el formato y al final un
        # check sin --fix para informar solo lo que de verdad quedó pendiente.
        correr("check", "--fix")
        correr("format")
        final = correr("check")
    except Exception as error:  # el formateo nunca bloquea
        avisar(f"No se pudo formatear: {type(error).__name__}.")
        return 0
    if final.returncode == 1:  # ruff: 1 = quedan diagnósticos
        avisar(f"Quedan problemas que ruff no corrige solo:\n{final.stdout.strip()}")
        return 2
    if final.returncode != 0:  # error de la herramienta (ruff ausente, config inválida…)
        avisar(f"ruff no pudo ejecutarse: {(final.stderr or final.stdout).strip()[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
