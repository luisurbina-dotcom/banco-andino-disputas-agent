"""PreToolUse (Bash): bloquea comandos que nombran archivos de secretos.

Principio III · necesidad 6. Complementa permissions.deny del issue #1, que no cubre comandos
como `python -c "open('.env')"` o `source .env`. Evalúa el texto completo del comando: un
mensaje de commit que nombra el archivo también se bloquea (falso positivo aceptado, R11).
"""

import re

from comun import bloquear, ejecutar_seguro

HOOK = "secretos_bash"

_ENTORNO = re.compile(r"(?<![\w.-])\.env(?:rc|\.[\w.-]+)?(?![\w])")
_SECRETOS = re.compile(r"(?<![\w.-])secrets/")
_CLAVES = re.compile(r"[\w.-]+\.(?:pem|key)(?![\w])")


def categorias(comando: str) -> list[str]:
    encontradas = []
    if any(m.group() != ".env.example" for m in _ENTORNO.finditer(comando)):
        encontradas.append("archivo de entorno")
    if _SECRETOS.search(comando):
        encontradas.append("carpeta secrets/")
    if _CLAVES.search(comando):
        encontradas.append("clave o certificado")
    return encontradas


def revisar(evento: dict) -> None:
    comando = (evento.get("tool_input") or {})["command"]
    encontradas = categorias(comando)
    if encontradas:
        bloquear(
            HOOK,
            f"El comando menciona un archivo de secretos ({', '.join(encontradas)}). Claude Code "
            "no lee ni modifica secretos; pide a una persona que lo haga.",
        )


if __name__ == "__main__":
    ejecutar_seguro(HOOK, revisar)
