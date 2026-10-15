import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _evento(ruta):
    return {"tool_name": "Write", "tool_input": {"file_path": str(ruta)}}


def _correr(correr_hook, ruta, env=None):
    return correr_hook(
        "formatear", _evento(ruta), env={"CLAUDE_PROJECT_DIR": str(RAIZ), **(env or {})}
    )


def test_formatea_y_quita_import_sin_usar(correr_hook, tmp_path):
    archivo = tmp_path / "feo.py"
    archivo.write_text("import os\nx=1\ndef f( a ):\n  return a\n")
    r = _correr(correr_hook, archivo)
    assert r.returncode == 0, r.stderr
    contenido = archivo.read_text()
    assert "import os" not in contenido
    assert "x = 1" in contenido
    assert "def f(a):" in contenido


def test_informa_problemas_no_corregibles_sin_revertir(correr_hook, tmp_path):
    archivo = tmp_path / "roto.py"
    archivo.write_text("def f():\n    return nombre_indefinido\n")
    r = _correr(correr_hook, archivo)
    assert r.returncode == 2
    assert "F821" in r.stderr
    assert "nombre_indefinido" in archivo.read_text()


def test_ignora_archivos_que_no_son_python(correr_hook, tmp_path):
    archivo = tmp_path / "notas.md"
    archivo.write_text("x=1\n")
    assert _correr(correr_hook, archivo).returncode == 0
    assert archivo.read_text() == "x=1\n"


def test_ignora_rutas_inexistentes(correr_hook, tmp_path):
    assert _correr(correr_hook, tmp_path / "no_existe.py").returncode == 0


def test_sin_uv_avisa_y_no_bloquea(correr_hook, tmp_path):
    archivo = tmp_path / "a.py"
    archivo.write_text("x=1\n")
    sin_uv = os.pathsep.join(
        p for p in os.environ["PATH"].split(os.pathsep) if not (Path(p) / "uv").exists()
    )
    r = _correr(correr_hook, archivo, env={"PATH": sin_uv})
    assert r.returncode == 0
    assert "uv" in r.stderr
