import subprocess
import zipfile

import empaquetar
import pytest

GIT = ["git", "-c", "user.name=Prueba", "-c", "user.email=prueba@example.invalid"]


def _repo(tmp_path, archivos: dict[str, str], ignorados: dict[str, str] | None = None):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run([*GIT, "init", "-q", "-b", "main"], cwd=repo, check=True)
    for ruta, contenido in archivos.items():
        destino = repo / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")
    subprocess.run([*GIT, "add", "-A"], cwd=repo, check=True)
    subprocess.run([*GIT, "commit", "-qm", "inicial"], cwd=repo, check=True)
    for ruta, contenido in (ignorados or {}).items():
        (repo / ruta).write_text(contenido, encoding="utf-8")
    return repo


def _tarjeta_con_forma_real() -> str:
    # Se construye en tiempo de ejecución: un literal así no puede estar en el repo.
    cuerpo = "453201511283"
    for verificador in "0123456789":
        if empaquetar.luhn_valido(cuerpo + "000" + verificador):
            return cuerpo + "000" + verificador
    raise AssertionError


def test_paquete_incluye_git_y_solo_lo_versionado(tmp_path):
    entorno = ".e" + "nv"
    repo = _repo(
        tmp_path,
        {"README.md": "# Proyecto", f"{entorno}.example": "CLAVE=", ".gitignore": f"{entorno}\n"},
        ignorados={entorno: "CLAVE=secreta"},
    )
    salida = tmp_path / "paquete.zip"
    info = empaquetar.empaquetar(repo, salida)
    nombres = zipfile.ZipFile(salida).namelist()
    raiz = empaquetar.NOMBRE
    assert f"{raiz}/README.md" in nombres and f"{raiz}/.git/HEAD" in nombres
    assert f"{raiz}/{entorno}.example" in nombres
    assert f"{raiz}/{entorno}" not in nombres  # ignorado por git: el clon no lo trae
    assert info["bytes"] == salida.stat().st_size


@pytest.mark.parametrize(
    ("ruta", "motivo"),
    [
        (".e" + "nv", "entorno"),
        ("config/.e" + "nv.produccion", "entorno"),
        ("certs/servidor.pem", "clave"),
        ("se" + "crets/token.txt", "carpeta prohibida"),
        ("node_modules/x/index.js", "carpeta prohibida"),
        (".venv/bin/activate", "carpeta prohibida"),
    ],
)
def test_nombres_prohibidos_versionados_se_rechazan(tmp_path, ruta, motivo):
    repo = _repo(tmp_path, {"README.md": "# P", ruta: "x"})
    with pytest.raises(empaquetar.PaqueteInvalido, match=motivo):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")
    assert not (tmp_path / "p.zip").exists()


def test_credencial_versionada_se_rechaza(tmp_path):
    token = "gh" + "p_" + "A1b2C3d4E5" * 4
    repo = _repo(tmp_path, {"config.py": f'TOKEN = "{token}"\n'})
    with pytest.raises(empaquetar.PaqueteInvalido, match="credencial"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_dato_con_forma_real_se_rechaza(tmp_path):
    repo = _repo(tmp_path, {"datos.md": f"Tarjeta {_tarjeta_con_forma_real()}\n"})
    with pytest.raises(empaquetar.PaqueteInvalido, match="forma real"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_datos_ficticios_se_permiten(tmp_path):
    repo = _repo(tmp_path, {"datos.md": "Tarjeta terminada en 4821, documento FIC-10000001.\n"})
    empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_paquete_mayor_al_limite_se_rechaza_y_se_borra(tmp_path):
    repo = _repo(tmp_path, {"README.md": "# P"})
    salida = tmp_path / "p.zip"
    with pytest.raises(empaquetar.PaqueteInvalido, match="MB"):
        empaquetar.empaquetar(repo, salida, limite_bytes=10)
    assert not salida.exists()


def test_cambios_sin_commit_se_advierten(tmp_path, capsys):
    repo = _repo(tmp_path, {"README.md": "# P"})
    (repo / "README.md").write_text("# cambiado", encoding="utf-8")
    assert empaquetar.main([str(repo), "--salida", str(tmp_path / "p.zip")]) == 0
    assert "sin commit" in capsys.readouterr().err


def test_main_informa_el_error_con_codigo_1(tmp_path, capsys):
    repo = _repo(tmp_path, {"certs/a.key": "x"})
    assert empaquetar.main([str(repo), "--salida", str(tmp_path / "p.zip")]) == 1
    assert "clave" in capsys.readouterr().err
