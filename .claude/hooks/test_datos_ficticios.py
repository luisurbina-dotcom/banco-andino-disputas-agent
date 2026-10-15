from conftest import tarjeta_valida


def test_bloquea_write_con_tarjeta_valida(correr_hook):
    numero = tarjeta_valida("4", 16)
    r = correr_hook(
        "datos_ficticios",
        {"tool_name": "Write", "tool_input": {"file_path": "x.md", "content": f"t {numero}"}},
    )
    assert r.returncode == 2
    assert "[datos_ficticios]" in r.stderr
    assert "tarjeta" in r.stderr
    assert numero not in r.stderr


def test_bloquea_edit_con_documento(correr_hook):
    texto = "cliente con cédula " + "".join(str(i % 10) for i in range(3, 11))
    r = correr_hook(
        "datos_ficticios",
        {"tool_name": "Edit", "tool_input": {"file_path": "x.py", "new_string": texto}},
    )
    assert r.returncode == 2
    assert "FIC-" in r.stderr


def test_permite_contenido_limpio(correr_hook):
    r = correr_hook(
        "datos_ficticios",
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "x.md", "content": "tarjeta terminada en 4821"},
        },
    )
    assert r.returncode == 0
    assert r.stderr == ""


def test_json_invalido_bloquea_por_seguridad(correr_hook):
    r = correr_hook("datos_ficticios", "esto no es json")
    assert r.returncode == 2
    assert "Se bloquea por seguridad" in r.stderr
