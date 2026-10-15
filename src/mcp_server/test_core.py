import pytest

from mcp_server.errores import ErrorCore

# --- buscar_cliente: localizar (US1) ---


def test_buscar_por_ultimos4_devuelve_al_titular(core, titular_4821):
    r = core.buscar_cliente("4821", "ultimos4")
    assert r["total"] == 1
    assert r["coincidencias"][0]["id_cliente"] == titular_4821["id_cliente"]
    assert "accion_sugerida" not in r


def test_buscar_por_documento_devuelve_ese_cliente(core, titular_4821):
    r = core.buscar_cliente(titular_4821["documento"], "documento")
    assert [c["id_cliente"] for c in r["coincidencias"]] == [titular_4821["id_cliente"]]


def test_busqueda_sin_resultados_es_lista_vacia_y_no_error(core):
    assert core.buscar_cliente("FIC-99999999", "documento") == {"coincidencias": [], "total": 0}


def test_la_busqueda_no_expone_el_dato_de_verificacion(core, titular_4821):
    r = core.buscar_cliente("4821", "ultimos4")
    coincidencia = r["coincidencias"][0]
    assert set(coincidencia) == {"id_cliente", "nombre", "tarjetas"}
    assert titular_4821["fecha_nacimiento"] not in str(r)


def test_cliente_con_dos_tarjetas_aparece_una_vez(core):
    r = core.buscar_cliente("Sofía Herrera", "nombre")
    assert r["total"] == 1
    assert sorted(r["coincidencias"][0]["tarjetas"]) == ["5502", "9017"]


# --- buscar_cliente: varias coincidencias (US2) ---


@pytest.mark.parametrize("nombre", ["Carlos Ramírez", "carlos ramirez", "  CARLOS   RAMÍREZ "])
def test_nombre_compartido_devuelve_dos_y_pide_otro_identificador(core, nombre):
    r = core.buscar_cliente(nombre, "nombre")
    assert r["total"] == 2
    assert "pide otro identificador" in r["accion_sugerida"]
    assert "no elijas" in r["accion_sugerida"]


def test_ultimos4_compartidos_devuelven_dos(core):
    r = core.buscar_cliente("7310", "ultimos4")
    assert r["total"] == 2
    assert "accion_sugerida" in r


def test_buscar_por_una_palabra_devuelve_a_todos_los_que_la_contienen(core):
    r = core.buscar_cliente("carlos", "nombre")
    assert r["total"] == 2


# --- buscar_cliente: validación (US1/US4) ---


@pytest.mark.parametrize(
    ("criterio", "tipo", "codigo"),
    [
        ("   ", "nombre", "CRITERIO_VACIO"),
        ("48", "ultimos4", "ULTIMOS4_INVALIDO"),
        ("48a1", "ultimos4", "ULTIMOS4_INVALIDO"),
        ("10000001", "documento", "DOCUMENTO_INVALIDO"),
        ("Ana", "telefono", "TIPO_INVALIDO"),
    ],
)
def test_errores_de_validacion_de_busqueda(core, criterio, tipo, codigo):
    with pytest.raises(ErrorCore) as e:
        core.buscar_cliente(criterio, tipo)
    assert (e.value.tipo, e.value.codigo, e.value.reintentable) == ("VALIDACION", codigo, False)


# --- verificar_identidad (US3) ---


def test_fecha_correcta_verifica(core, titular_4821):
    r = core.verificar_identidad(titular_4821["id_cliente"], titular_4821["fecha_nacimiento"])
    assert r == {
        "verificado": True,
        "id_cliente": titular_4821["id_cliente"],
        "nombre": titular_4821["nombre"],
    }


def test_fecha_incorrecta_informa_intentos_sin_revelar_el_dato(core, titular_4821):
    id_cliente = titular_4821["id_cliente"]
    primero = core.verificar_identidad(id_cliente, "1900-01-01")
    segundo = core.verificar_identidad(id_cliente, "1900-01-02")
    assert (primero["verificado"], primero["intentos_restantes"]) == (False, 2)
    assert segundo["intentos_restantes"] == 1
    assert titular_4821["fecha_nacimiento"] not in str(primero) + str(segundo)


def test_tercer_fallo_bloquea_aun_con_la_fecha_correcta(core, titular_4821):
    id_cliente, correcta = titular_4821["id_cliente"], titular_4821["fecha_nacimiento"]
    core.verificar_identidad(id_cliente, "1900-01-01")
    core.verificar_identidad(id_cliente, "1900-01-01")
    for fecha in ("1900-01-01", correcta):
        with pytest.raises(ErrorCore) as e:
            core.verificar_identidad(id_cliente, fecha)
        assert (e.value.tipo, e.value.codigo, e.value.reintentable) == (
            "NEGOCIO",
            "IDENTIDAD_BLOQUEADA",
            False,
        )
        assert "analista" in e.value.mensaje


def test_un_acierto_reinicia_el_contador(core, titular_4821):
    id_cliente, correcta = titular_4821["id_cliente"], titular_4821["fecha_nacimiento"]
    core.verificar_identidad(id_cliente, "1900-01-01")
    core.verificar_identidad(id_cliente, "1900-01-01")
    assert core.verificar_identidad(id_cliente, correcta)["verificado"] is True
    assert core.verificar_identidad(id_cliente, "1900-01-01")["intentos_restantes"] == 2


def test_cliente_inexistente_es_error_de_validacion(core):
    with pytest.raises(ErrorCore) as e:
        core.verificar_identidad("CLI-999", "1990-01-01")
    assert (e.value.tipo, e.value.codigo) == ("VALIDACION", "CLIENTE_NO_EXISTE")


def test_fecha_mal_formada_no_consume_intento(core, titular_4821):
    id_cliente = titular_4821["id_cliente"]
    with pytest.raises(ErrorCore) as e:
        core.verificar_identidad(id_cliente, "15/10/1990")
    assert (e.value.tipo, e.value.codigo) == ("VALIDACION", "FECHA_INVALIDA")
    assert core.verificar_identidad(id_cliente, "1900-01-01")["intentos_restantes"] == 2


# --- Hallazgos de la revisión independiente (review.md) ---


@pytest.mark.parametrize("criterio", ["😀", "´", "  ´ ¨ "])
def test_nombre_que_queda_vacio_al_normalizar_es_criterio_vacio(core, criterio):
    with pytest.raises(ErrorCore) as e:
        core.buscar_cliente(criterio, "nombre")
    assert e.value.codigo == "CRITERIO_VACIO"


@pytest.mark.parametrize("fecha", ["19880412", "1988-W15-2", "1988-4-12"])
def test_fecha_fuera_de_aaaa_mm_dd_es_invalida_y_no_consume_intento(core, titular_4821, fecha):
    id_cliente = titular_4821["id_cliente"]
    with pytest.raises(ErrorCore) as e:
        core.verificar_identidad(id_cliente, fecha)
    assert e.value.codigo == "FECHA_INVALIDA"
    assert core.verificar_identidad(id_cliente, "1900-01-01")["intentos_restantes"] == 2


def test_fecha_inexistente_en_el_calendario_es_invalida(core, titular_4821):
    with pytest.raises(ErrorCore) as e:
        core.verificar_identidad(titular_4821["id_cliente"], "1988-02-30")
    assert e.value.codigo == "FECHA_INVALIDA"


@pytest.mark.parametrize(("criterio", "tipo"), [(123, "nombre"), (None, "ultimos4")])
def test_criterio_que_no_es_texto_es_validacion(core, criterio, tipo):
    with pytest.raises(ErrorCore) as e:
        core.buscar_cliente(criterio, tipo)
    assert e.value.tipo == "VALIDACION"


@pytest.mark.parametrize("id_cliente", [123, ["CLI-001"], None])
def test_id_cliente_que_no_es_texto_es_validacion(core, id_cliente):
    with pytest.raises(ErrorCore) as e:
        core.verificar_identidad(id_cliente, "1990-01-01")
    assert e.value.codigo == "CLIENTE_NO_EXISTE"


def test_cliente_bloqueado_responde_bloqueo_aunque_la_fecha_este_mal_formada(core, titular_4821):
    id_cliente = titular_4821["id_cliente"]
    for _ in range(2):
        core.verificar_identidad(id_cliente, "1900-01-01")
    with pytest.raises(ErrorCore):
        core.verificar_identidad(id_cliente, "1900-01-01")
    with pytest.raises(ErrorCore) as e:
        core.verificar_identidad(id_cliente, "15/10/1990")
    assert e.value.codigo == "IDENTIDAD_BLOQUEADA"
