import subprocess

import pytest


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(
        tmp_path,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "i",
    )
    return tmp_path


def _editar(correr_hook, repo, ruta):
    evento = {"tool_name": "Write", "tool_input": {"file_path": str(repo / ruta), "content": ""}}
    return correr_hook("spec_primero", evento, env={"CLAUDE_PROJECT_DIR": str(repo)}, cwd=repo)


def _feature(repo, nombre, artefactos):
    _git(repo, "switch", "-q", "-c", nombre)
    carpeta = repo / "specs" / nombre
    carpeta.mkdir(parents=True)
    for a in artefactos:
        (carpeta / a).write_text("x")


def test_bloquea_en_main(correr_hook, repo):
    r = _editar(correr_hook, repo, "src/x.py")
    assert r.returncode == 2
    assert "no es una feature" in r.stderr
    assert "/speckit-specify" in r.stderr


def test_bloquea_feature_sin_carpeta(correr_hook, repo):
    _git(repo, "switch", "-q", "-c", "999-prueba")
    r = _editar(correr_hook, repo, "src/x.py")
    assert r.returncode == 2
    assert "spec.md, plan.md, tasks.md" in r.stderr


def test_bloquea_feature_incompleta(correr_hook, repo):
    _feature(repo, "998-parcial", ["spec.md"])
    r = _editar(correr_hook, repo, "src/x.py")
    assert r.returncode == 2
    assert "plan.md, tasks.md" in r.stderr
    assert "spec.md," not in r.stderr


def test_permite_feature_completa(correr_hook, repo):
    _feature(repo, "997-completa", ["spec.md", "plan.md", "tasks.md"])
    assert _editar(correr_hook, repo, "src/x.py").returncode == 0


def test_data_sigue_la_misma_regla(correr_hook, repo):
    assert _editar(correr_hook, repo, "data/clientes.json").returncode == 2


@pytest.mark.parametrize("ruta", ["src/agent/CLAUDE.md", "specs/001-x/spec.md", "README.md"])
def test_permite_lo_que_no_es_codigo_de_produccion(correr_hook, repo, ruta):
    assert _editar(correr_hook, repo, ruta).returncode == 0


def test_permite_rutas_fuera_del_repo(correr_hook, repo, tmp_path_factory):
    afuera = tmp_path_factory.mktemp("afuera") / "src" / "x.py"
    evento = {"tool_name": "Write", "tool_input": {"file_path": str(afuera), "content": ""}}
    r = correr_hook("spec_primero", evento, env={"CLAUDE_PROJECT_DIR": str(repo)}, cwd=repo)
    assert r.returncode == 0
