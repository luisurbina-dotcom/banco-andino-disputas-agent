"""Genera el .zip de Code Defense: `uv run python scripts/empaquetar.py [--salida RUTA]`.

Parte de un clon del repositorio (solo lo versionado, con `.git` e historial intacto) y, antes de
comprimir, rechaza archivos de entorno o de secretos, dependencias instaladas, credenciales y
datos con forma real (mismo detector que el hook `datos_ficticios`). Límite: 50 MB.
Contrato: specs/011-readme-decisiones-entregables/contracts/entregables.md.
"""

import argparse
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_REPO / ".claude" / "hooks"))
from detector import detectar, luhn_valido  # noqa: E402

NOMBRE = "banco-andino-disputas-agent"
LIMITE_BYTES = 50 * 1024 * 1024
CARPETAS_PROHIBIDAS = {".venv", "venv", "node_modules", "__pycache__", "secrets"}
CREDENCIAL = re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_\w{20,}|sk-ant-[\w-]{10,}")

__all__ = ["NOMBRE", "PaqueteInvalido", "empaquetar", "luhn_valido", "main"]


class PaqueteInvalido(Exception):
    pass


def _motivo_por_nombre(relativa: Path) -> str | None:
    if any(parte in CARPETAS_PROHIBIDAS for parte in relativa.parts[:-1]):
        return "carpeta prohibida (dependencias, cachés o secretos)"
    nombre = relativa.name
    entorno = ".e" + "nv"
    if nombre in (entorno, entorno + "rc") or (
        nombre.startswith(entorno + ".") and nombre != entorno + ".example"
    ):
        return "archivo de entorno"
    if nombre.endswith((".pem", ".key")):
        return "archivo de clave"
    return None


def _problemas(clon: Path) -> list[str]:
    problemas = []
    for ruta in sorted(clon.rglob("*")):
        relativa = ruta.relative_to(clon)
        if relativa.parts[0] == ".git" or not ruta.is_file():
            continue
        if motivo := _motivo_por_nombre(relativa):
            problemas.append(f"{relativa}: {motivo}")
            continue
        try:
            texto = ruta.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binario
        if CREDENCIAL.search(texto):
            problemas.append(f"{relativa}: posible credencial")
        if detectar(texto):
            problemas.append(f"{relativa}: dato con forma real (tarjeta o documento)")
    return problemas


def _git(*argumentos: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *argumentos], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def empaquetar(repo: Path, salida: Path, limite_bytes: int = LIMITE_BYTES) -> dict:
    with tempfile.TemporaryDirectory(prefix="empaquetar-") as temporal:
        clon = Path(temporal) / NOMBRE
        _git("clone", "-q", "--no-hardlinks", str(repo), str(clon), cwd=Path(temporal))
        remoto = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        if remoto:  # el clon apunta a GitHub, no a la ruta local de quien empaqueta
            _git("remote", "set-url", "origin", remoto, cwd=clon)
        if problemas := _problemas(clon):
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
    try:
        info = empaquetar(repo, salida)
    except PaqueteInvalido as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Paquete: {info['ruta']} · {info['bytes'] / 1e6:.1f} MB · {info['archivos']} archivos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
