"""Genera el .zip de Code Defense: `uv run python scripts/empaquetar.py [--salida RUTA]`.

Parte de un clon del repositorio (solo lo versionado, con `.git` e historial intacto) y, antes de
comprimir, rechaza archivos de entorno, claves o secretos, dependencias instaladas, enlaces
simbólicos, credenciales y datos con forma real (mismo detector que el hook `datos_ficticios`),
tanto en el árbol como en **todo el historial** que viaja en `.git`. Límite: 50 MB.
Contrato: specs/011-readme-decisiones-entregables/contracts/entregables.md.
"""

import argparse
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, urlunsplit

RAIZ_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_REPO / ".claude" / "hooks"))
from detector import detectar, luhn_valido  # noqa: E402

NOMBRE = "banco-andino-disputas-agent"
LIMITE_BYTES = 50_000_000  # 50 MB decimales: criterio conservador
CARPETAS_PROHIBIDAS = {
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "site-packages",
    ".tox",
    "dist",
    "build",
    "secrets",
}
EXTENSIONES_CLAVE = (".pem", ".key", ".p12", ".pfx")
# Contenido histórico aceptado por el autor (no se reescribe el historial, principio VII). Se
# fija por el hash exacto del blob: cualquier otro contenido, aunque esté en la misma ruta, se
# sigue revisando. Justificación: DECISIONES.md y specs/011-readme-decisiones-entregables/
# review.md.
EXCEPCIONES_HISTORIAL = {
    # specs/002-hooks-desarrollo/quickstart.md en 9f25fd6 (#2): ejemplo de prueba con forma de
    # cédula escrito antes de que existiera el hook; reemplazado en el commit siguiente (be92bdc).
    "6744e37a2f9cf3787caca0ffbf2789ef2d291d15",
}
CREDENCIAL = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|sk-ant-[\w-]{10,}|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)

__all__ = ["NOMBRE", "PaqueteInvalido", "empaquetar", "luhn_valido", "main"]


class PaqueteInvalido(Exception):
    pass


def _motivo_por_nombre(relativa: PurePosixPath) -> str | None:
    if any(p in CARPETAS_PROHIBIDAS or p.endswith(".egg-info") for p in relativa.parts[:-1]):
        return "carpeta prohibida (dependencias, artefactos o secretos)"
    nombre = relativa.name
    entorno = ".e" + "nv"
    if nombre in (entorno, entorno + "rc") or (
        nombre.startswith(entorno + ".") and nombre != entorno + ".example"
    ):
        return "archivo de entorno"
    if nombre.endswith(EXTENSIONES_CLAVE) or nombre.startswith("id_rsa"):
        return "archivo de clave"
    return None


def _motivos_por_contenido(texto: str) -> list[str]:
    motivos = []
    if CREDENCIAL.search(texto):
        motivos.append("posible credencial")
    if detectar(texto):
        motivos.append("dato con forma real (tarjeta o documento)")
    return motivos


def _git(*argumentos: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *argumentos], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def _problemas_del_arbol(clon: Path) -> list[str]:
    problemas = []
    for ruta in sorted(clon.rglob("*")):
        relativa = ruta.relative_to(clon)
        if relativa.parts[0] == ".git":
            continue
        if ruta.is_symlink():
            problemas.append(f"{relativa}: enlace simbólico (podría arrastrar archivos externos)")
        elif ruta.is_file() and (motivo := _motivo_por_nombre(PurePosixPath(relativa))):
            problemas.append(f"{relativa}: {motivo}")
    return problemas


def _problemas_del_historial(clon: Path) -> list[str]:
    """Revisa cada archivo y cada contenido que alguna vez se versionó (viaja en `.git`)."""
    problemas = []
    nombres = set(
        filter(None, _git("log", "--all", "--name-only", "--format=", cwd=clon).split("\n"))
    )
    for nombre in sorted(nombres):
        if motivo := _motivo_por_nombre(PurePosixPath(nombre)):
            problemas.append(f"{nombre} (historial): {motivo}")
    rutas: dict[str, str] = {}
    for linea in _git("rev-list", "--all", "--objects", cwd=clon).split("\n"):
        sha, _, ruta = linea.partition(" ")
        if sha:
            rutas[sha] = ruta
    lote = subprocess.run(
        ["git", "cat-file", "--batch"],
        input="\n".join(rutas).encode() + b"\n",
        cwd=clon,
        check=True,
        capture_output=True,
    ).stdout
    posicion = 0
    while posicion < len(lote):
        fin = lote.index(b"\n", posicion)
        sha, tipo, tamano = lote[posicion:fin].decode().split()
        contenido = lote[fin + 1 : fin + 1 + int(tamano)]
        posicion = fin + 1 + int(tamano) + 1
        if tipo == "blob" and sha not in EXCEPCIONES_HISTORIAL:
            for motivo in _motivos_por_contenido(contenido.decode("utf-8", errors="replace")):
                problemas.append(f"{rutas[sha] or sha} (historial): {motivo}")
    return problemas


def _url_publica(url: str) -> str:
    """Quita usuario y token de una URL (p. ej. https://usuario:token@github.com/...)."""
    partes = urlsplit(url)
    if partes.scheme and "@" in partes.netloc:
        return urlunsplit(partes._replace(netloc=partes.netloc.rsplit("@", 1)[1]))
    return url


def empaquetar(repo: Path, salida: Path, limite_bytes: int = LIMITE_BYTES) -> dict:
    salida.unlink(missing_ok=True)  # un paquete viejo nunca debe quedar si este falla
    with tempfile.TemporaryDirectory(prefix="empaquetar-") as temporal:
        clon = Path(temporal) / NOMBRE
        _git("clone", "-q", "--no-hardlinks", str(repo), str(clon), cwd=Path(temporal))
        remoto = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        if remoto:  # el clon apunta al remoto público, no a la ruta local de quien empaqueta
            _git("remote", "set-url", "origin", _url_publica(remoto), cwd=clon)
        problemas = _problemas_del_arbol(clon) + _problemas_del_historial(clon)
        configuracion = (clon / ".git" / "config").read_text(encoding="utf-8", errors="replace")
        problemas += [f".git/config: {m}" for m in _motivos_por_contenido(configuracion)]
        if problemas:
            raise PaqueteInvalido("El paquete no se generó:\n- " + "\n- ".join(problemas))
        archivos = [r for r in sorted(clon.rglob("*")) if r.is_file()]
        salida.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as paquete:
            for ruta in archivos:
                paquete.write(ruta, Path(NOMBRE) / ruta.relative_to(clon))
    tamano = salida.stat().st_size
    if tamano > limite_bytes:
        salida.unlink()
        raise PaqueteInvalido(
            f"El paquete pesa {tamano / 1e6:.1f} MB y el máximo es {limite_bytes / 1e6:.0f} MB."
        )
    return {"ruta": salida, "bytes": tamano, "archivos": len(archivos)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera el .zip de Code Defense")
    parser.add_argument("repo", nargs="?", type=Path, default=RAIZ_REPO)
    parser.add_argument("--salida", type=Path, help="ruta del .zip (por defecto, junto al repo)")
    argumentos = parser.parse_args(argv)
    repo = argumentos.repo.resolve()
    salida = (argumentos.salida or repo.parent / f"{NOMBRE}.zip").resolve()
    if _git("status", "--porcelain", cwd=repo):
        print(
            "Aviso: hay cambios sin commit; el paquete solo incluye lo versionado.", file=sys.stderr
        )
    rama = _git("branch", "--show-current", cwd=repo)
    if rama != "main":
        print(
            f"Aviso: estás en la rama {rama or '(sin rama)'}; la entrega se genera desde main.",
            file=sys.stderr,
        )
    try:
        info = empaquetar(repo, salida)
    except PaqueteInvalido as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Paquete: {info['ruta']} · {info['bytes'] / 1e6:.1f} MB · {info['archivos']} archivos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
