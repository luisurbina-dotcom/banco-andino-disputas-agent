"""PreToolUse (Edit|Write): no se escribe código de producción sin spec, plan y tareas.

Principio IV de la constitución · necesidad 4 del ecosistema. La feature activa se toma de la
rama actual y no de .specify/feature.json, que queda obsoleto después de cada merge.
"""

import re
import subprocess
from pathlib import Path

from comun import bloquear, ejecutar_seguro, raiz_repo

HOOK = "spec_primero"
CARPETAS_PRODUCCION = ("src", "data")
ARTEFACTOS = ("spec.md", "plan.md", "tasks.md")
RAMA_FEATURE = re.compile(r"^\d{3}-[a-z0-9-]+$")


def es_codigo_de_produccion(relativa: Path) -> bool:
    return (
        bool(relativa.parts)
        and relativa.parts[0] in CARPETAS_PRODUCCION
        and (relativa.name != "CLAUDE.md")
    )


def revisar(evento: dict) -> None:
    raiz = raiz_repo()
    entrada = evento.get("tool_input") or {}
    ruta = Path(entrada.get("file_path") or entrada["notebook_path"])  # NotebookEdit
    if not ruta.is_absolute():
        ruta = Path(evento.get("cwd") or raiz) / ruta
    try:
        relativa = ruta.resolve().relative_to(raiz)
    except ValueError:
        return  # fuera del repositorio
    if not es_codigo_de_produccion(relativa):
        return

    rama = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=raiz,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not RAMA_FEATURE.match(rama):
        bloquear(
            HOOK,
            f'La rama "{rama}" no es una feature. Crea la feature con /speckit-specify antes '
            f"de escribir código en {relativa}.",
        )

    faltantes = [a for a in ARTEFACTOS if not (raiz / "specs" / rama / a).is_file()]
    if faltantes:
        bloquear(
            HOOK,
            f"Faltan {', '.join(faltantes)} en specs/{rama}/. Completa /speckit-plan y "
            "/speckit-tasks antes de implementar.",
        )


if __name__ == "__main__":
    ejecutar_seguro(HOOK, revisar)
