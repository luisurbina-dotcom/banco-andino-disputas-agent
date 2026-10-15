import subprocess
import zipfile

import empaquetar
import pytest

GIT = [
    "git",
    "-c",
    "user.name=Prueba",
    "-c",
    "user.email=prueba@example.invalid",
    "-c",
    "commit.gpgsign=false",
]


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


def test_secreto_borrado_que_sigue_en_el_historial_se_rechaza(tmp_path):
    entorno = ".e" + "nv"
    repo = _repo(tmp_path, {"README.md": "# P", entorno: "CLAVE=x"})
    subprocess.run([*GIT, "rm", "-q", entorno], cwd=repo, check=True)
    subprocess.run([*GIT, "commit", "-qm", "quita el archivo"], cwd=repo, check=True)
    with pytest.raises(empaquetar.PaqueteInvalido, match="historial"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_credencial_borrada_que_sigue_en_el_historial_se_rechaza(tmp_path):
    token = "gh" + "o_" + "A1b2C3d4E5" * 4
    repo = _repo(tmp_path, {"config.py": f'T = "{token}"\n'})
    (repo / "config.py").write_text("T = None\n", encoding="utf-8")
    subprocess.run([*GIT, "commit", "-qam", "quita el token"], cwd=repo, check=True)
    with pytest.raises(empaquetar.PaqueteInvalido, match=r"config.py \(historial\): posible"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")


@pytest.mark.parametrize(
    "contenido",
    ["-----BEGIN " + "RSA PRIVATE KEY-----", "AK" + "IA" + "ABCDEFGHIJKLMNOP"],
)
def test_otras_credenciales_se_rechazan(tmp_path, contenido):
    repo = _repo(tmp_path, {"notas.txt": contenido})
    with pytest.raises(empaquetar.PaqueteInvalido, match="credencial"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_url_del_remoto_con_token_se_limpia(tmp_path):
    repo = _repo(tmp_path, {"README.md": "# P"})
    token = "gh" + "p_" + "A1b2C3d4E5" * 4
    subprocess.run(
        [*GIT, "remote", "add", "origin", f"https://usuario:{token}@github.com/org/repo.git"],
        cwd=repo,
        check=True,
    )
    salida = tmp_path / "p.zip"
    empaquetar.empaquetar(repo, salida)
    config = zipfile.ZipFile(salida).read(f"{empaquetar.NOMBRE}/.git/config").decode()
    assert token not in config and "https://github.com/org/repo.git" in config


def test_enlace_simbolico_versionado_se_rechaza(tmp_path):
    repo = _repo(tmp_path, {"README.md": "# P"})
    (repo / "enlace").symlink_to("/etc/hostname")
    subprocess.run([*GIT, "add", "enlace"], cwd=repo, check=True)
    subprocess.run([*GIT, "commit", "-qm", "enlace"], cwd=repo, check=True)
    with pytest.raises(empaquetar.PaqueteInvalido, match="enlace simbólico"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_un_paquete_viejo_no_sobrevive_a_una_validacion_fallida(tmp_path):
    repo = _repo(tmp_path, {"certs/a" + ".pem": "x"})
    salida = tmp_path / "p.zip"
    salida.write_bytes(b"paquete anterior")
    with pytest.raises(empaquetar.PaqueteInvalido):
        empaquetar.empaquetar(repo, salida)
    assert not salida.exists()


def test_excepcion_historica_permite_solo_el_blob_exacto(tmp_path, monkeypatch):
    repo = _repo(tmp_path, {"datos.md": f"Tarjeta {_tarjeta_con_forma_real()}\n"})
    blob = subprocess.run(
        ["git", "rev-parse", "HEAD:datos.md"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    (repo / "datos.md").write_text("Tarjeta terminada en 4821.\n", encoding="utf-8")
    subprocess.run([*GIT, "commit", "-qam", "corrige el ejemplo"], cwd=repo, check=True)
    with pytest.raises(empaquetar.PaqueteInvalido, match="historial"):
        empaquetar.empaquetar(repo, tmp_path / "p.zip")
    monkeypatch.setattr(empaquetar, "EXCEPCIONES_HISTORIAL", {blob})
    empaquetar.empaquetar(repo, tmp_path / "p.zip")


def test_la_excepcion_del_repo_apunta_a_un_blob_que_existe():
    for blob in empaquetar.EXCEPCIONES_HISTORIAL:
        tipo = subprocess.run(
            ["git", "cat-file", "-t", blob],
            cwd=empaquetar.RAIZ_REPO,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert tipo == "blob", blob
