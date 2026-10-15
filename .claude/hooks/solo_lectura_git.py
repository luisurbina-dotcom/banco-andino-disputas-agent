"""PreToolUse (Bash) de los subagentes revisores: solo comandos git de lectura.

Se declara en el frontmatter de `code-reviewer` y `compliance-auditor`, no en settings.json:
restringe a esos subagentes sin afectar a la sesión principal. `tools` no permite limitar Bash
por comando, por eso la restricción es un hook (determinista, principio II).
"""

import shlex

from comun import bloquear, ejecutar_seguro

HOOK = "solo_lectura_git"
SUBCOMANDOS = {"diff", "log", "show", "status", "ls-files", "rev-parse", "merge-base"}
OPCIONES_GLOBALES = {"--no-pager"}
METACARACTERES = (";", "|", "&", ">", "<", "`", "$(", "\n")


def permitido(comando: str) -> bool:
    if any(m in comando for m in METACARACTERES):
        return False
    partes = shlex.split(comando)
    if not partes or partes[0] != "git":
        return False
    resto = partes[1:]
    while resto and resto[0] in OPCIONES_GLOBALES:
        resto.pop(0)
    if not resto:
        return False
    subcomando, argumentos = resto[0], resto[1:]
    if any(a == "--output" or a.startswith("--output=") for a in argumentos):  # escribe archivo
        return False
    if subcomando == "branch":
        return argumentos == ["--show-current"]
    return subcomando in SUBCOMANDOS


def revisar(evento: dict) -> None:
    comando = (evento.get("tool_input") or {})["command"]
    if not permitido(comando):
        bloquear(HOOK, "Este subagente solo puede leer el repositorio (git diff, log, show…).")


if __name__ == "__main__":
    ejecutar_seguro(HOOK, revisar)
