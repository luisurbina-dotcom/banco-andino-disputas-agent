from dataclasses import replace
from datetime import timedelta

import pytest

from mcp_server.core import Core
from mcp_server.errores import ErrorCore
from mcp_server.operaciones import Operaciones


@pytest.fixture
def ops(core):
    return Operaciones(core)


def _verificar(core, datos, id_cliente):
    cliente = next(c for c in datos.clientes if c["id_cliente"] == id_cliente)
    core.verificar_identidad(id_cliente, cliente["fecha_nacimiento"])


@pytest.fixture
def verificado(core, datos):
    _verificar(core, datos, "CLI-001")
    return "CLI-001"


def _error(excinfo):
    e = excinfo.value
    return e.tipo, e.codigo, e.reintentable


# --- consultar_transacciones (US1) ---


def test_consultar_sin_verificar_es_permisos(ops):
    with pytest.raises(ErrorCore) as e:
        ops.consultar_transacciones("CLI-001", "4821")
    assert _error(e) == ("PERMISOS", "IDENTIDAD_NO_VERIFICADA", False)


def test_consultar_ayer_devuelve_los_dos_cobros(ops, verificado):
    r = ops.consultar_transacciones(verificado, "4821", desde="2026-10-14", hasta="2026-10-14")
    assert r["total"] == 2
    assert sorted(tx["monto"] for tx in r["transacciones"]) == [180_000, 1_250_000]
    assert {tx["fecha"] for tx in r["transacciones"]} == {"2026-10-14"}
    assert set(r["transacciones"][0]) == {"id_transaccion", "fecha", "monto", "comercio", "pais"}


def test_consultar_sin_rango_usa_los_ultimos_30_dias(ops, verificado):
    r = ops.consultar_transacciones(verificado, "4821")
    assert r["total"] == 3  # dos de ayer y una de hace 6 días


def test_rango_sin_datos_es_lista_vacia(ops, verificado):
    r = ops.consultar_transacciones(verificado, "4821", desde="2026-01-01", hasta="2026-01-31")
    assert r == {"transacciones": [], "total": 0}


@pytest.mark.parametrize(
    ("desde", "hasta"), [("2026-10-14", "2026-10-01"), ("14/10/2026", None), (None, "20261014")]
)
def test_rango_invalido(ops, verificado, desde, hasta):
    with pytest.raises(ErrorCore) as e:
        ops.consultar_transacciones(verificado, "4821", desde=desde, hasta=hasta)
    assert _error(e) == ("VALIDACION", "RANGO_INVALIDO", False)


def test_tarjeta_de_otro_cliente_no_se_encuentra(ops, verificado):
    with pytest.raises(ErrorCore) as e:
        ops.consultar_transacciones(verificado, "7310")
    assert _error(e) == ("VALIDACION", "TARJETA_NO_ENCONTRADA", False)


def test_falla_transitoria_y_luego_responde(ops, core, verificado):
    core.programar_fallas("consultar_transacciones", 1)
    with pytest.raises(ErrorCore) as e:
        ops.consultar_transacciones(verificado, "4821")
    assert _error(e) == ("TRANSITORIO", "CORE_NO_DISPONIBLE", True)
    assert ops.consultar_transacciones(verificado, "4821")["total"] == 3


# --- iniciar_disputa (US2) ---


def test_disputa_bajo_el_umbral_se_abre(ops, verificado):
    r = ops.iniciar_disputa(verificado, "TX-0001", "No reconozco el cobro")
    assert r["estado"] == "abierta"
    assert r["id_disputa"].startswith("DSP-")
    assert (r["id_transaccion"], r["monto"]) == ("TX-0001", 180_000)


def test_disputa_sobre_el_umbral_pide_escalar(ops, verificado):
    with pytest.raises(ErrorCore) as e:
        ops.iniciar_disputa(verificado, "TX-0002", "No reconozco el cobro")
    assert _error(e) == ("NEGOCIO", "MONTO_SUPERA_UMBRAL", False)
    assert "analista" in e.value.mensaje


def test_segunda_disputa_de_la_misma_transaccion(ops, verificado):
    ops.iniciar_disputa(verificado, "TX-0001", "No reconozco el cobro")
    with pytest.raises(ErrorCore) as e:
        ops.iniciar_disputa(verificado, "TX-0001", "Otra vez")
    assert _error(e) == ("NEGOCIO", "DISPUTA_EXISTENTE", False)


def test_extranjera_de_mas_de_90_dias_no_la_cubre_la_politica(ops, core, datos):
    _verificar(core, datos, "CLI-007")
    with pytest.raises(ErrorCore) as e:
        ops.iniciar_disputa("CLI-007", "TX-0010", "No reconozco el cobro")
    assert _error(e) == ("NEGOCIO", "POLITICA_NO_CUBRE", False)
    assert "analista" in e.value.mensaje


@pytest.mark.parametrize("id_transaccion", ["TX-0006", "TX-9999"])
def test_transaccion_ajena_o_inexistente(ops, verificado, id_transaccion):
    with pytest.raises(ErrorCore) as e:
        ops.iniciar_disputa(verificado, id_transaccion, "x")
    assert _error(e) == ("VALIDACION", "TRANSACCION_NO_ENCONTRADA", False)


def test_disputa_sin_verificar_es_permisos(ops):
    with pytest.raises(ErrorCore) as e:
        ops.iniciar_disputa("CLI-001", "TX-0001", "x")
    assert _error(e)[:2] == ("PERMISOS", "IDENTIDAD_NO_VERIFICADA")


@pytest.fixture
def ops_limites(datos):
    """Core con transacciones de prueba en los límites exactos (sin tocar data/)."""
    base = datos.fecha_base

    def tx(id_tx, dias, monto, pais):
        return {
            "id_transaccion": id_tx,
            "id_tarjeta": "TAR-001",
            "dias_atras": dias,
            "fecha": base - timedelta(days=dias),
            "monto": monto,
            "comercio": "Comercio de prueba",
            "pais": pais,
        }

    datos_limite = replace(
        datos,
        transacciones=[
            tx("TX-L1", 1, 500_000, "CO"),
            tx("TX-L2", 90, 100_000, "US"),
            tx("TX-L3", 91, 900_000, "US"),
        ],
    )
    core = Core(datos_limite)
    _verificar(core, datos_limite, "CLI-001")
    return Operaciones(core)


def test_exactamente_500000_se_disputa(ops_limites):
    assert ops_limites.iniciar_disputa("CLI-001", "TX-L1", "x")["estado"] == "abierta"


def test_extranjera_de_exactamente_90_dias_se_disputa(ops_limites):
    assert ops_limites.iniciar_disputa("CLI-001", "TX-L2", "x")["estado"] == "abierta"


def test_fuera_de_politica_prevalece_sobre_el_umbral(ops_limites):
    with pytest.raises(ErrorCore) as e:
        ops_limites.iniciar_disputa("CLI-001", "TX-L3", "x")
    assert e.value.codigo == "POLITICA_NO_CUBRE"


# --- bloquear_tarjeta (US3) ---


def test_bloquear_y_repetir_es_idempotente(ops, core, verificado):
    primero = ops.bloquear_tarjeta(verificado, "4821", "Posible clonación")
    assert primero == {"bloqueada": True, "ultimos4": "4821", "ya_estaba_bloqueada": False}
    tarjeta = next(t for t in core.datos.tarjetas if t["ultimos4"] == "4821")
    assert tarjeta["estado"] == "bloqueada"
    assert ops.bloquear_tarjeta(verificado, "4821", "x")["ya_estaba_bloqueada"] is True


def test_bloquear_tarjeta_de_otro_cliente(ops, verificado):
    with pytest.raises(ErrorCore) as e:
        ops.bloquear_tarjeta(verificado, "7310", "x")
    assert _error(e) == ("VALIDACION", "TARJETA_NO_ENCONTRADA", False)


def test_bloquear_sin_verificar_es_permisos(ops):
    with pytest.raises(ErrorCore) as e:
        ops.bloquear_tarjeta("CLI-001", "4821", "x")
    assert _error(e)[:2] == ("PERMISOS", "IDENTIDAD_NO_VERIFICADA")


# --- escalar_a_analista (US4) ---


def test_escalar_completa_el_resumen_con_datos_del_core(ops, core):
    r = ops.escalar_a_analista(
        causa="MONTO_SUPERA_UMBRAL",
        descripcion="Cobro no reconocido sobre el umbral",
        accion_recomendada="Revisar y abrir disputa manual",
        id_cliente="CLI-001",
        id_transacciones=["TX-0002"],
        acciones_realizadas=["Identidad verificada", "Tarjeta bloqueada"],
    )
    assert r["estado"] == "en_cola_analista"
    resumen = r["resumen"]
    assert resumen["cliente"] == {"id_cliente": "CLI-001", "nombre": "Ana María Gómez"}
    assert resumen["transacciones"] == [
        {
            "id_transaccion": "TX-0002",
            "fecha": "2026-10-14",
            "monto": 1_250_000,
            "comercio": "Electro Ficticio SAS",
            "pais": "CO",
        }
    ]
    assert resumen["acciones_realizadas"] == ["Identidad verificada", "Tarjeta bloqueada"]
    assert core.casos[-1]["id_caso"] == r["id_caso"]


def test_escalar_a_pedido_no_exige_cliente_ni_verificacion(ops):
    r = ops.escalar_a_analista(
        causa="CLIENTE_PIDE_PERSONA",
        descripcion="El cliente pidió hablar con una persona",
        accion_recomendada="Contactar al cliente",
    )
    assert r["resumen"]["cliente"] is None
    assert r["estado"] == "en_cola_analista"


def test_casos_con_ids_correlativos(ops, core):
    for _ in range(2):
        ops.escalar_a_analista("OTRO", "d", "a")
    assert [c["id_caso"] for c in core.casos] == ["CASO-0001", "CASO-0002"]


@pytest.mark.parametrize(
    ("causa", "descripcion", "accion"),
    [("OTRO", "  ", "a"), ("OTRO", "d", ""), ("INVENTADA", "d", "a")],
)
def test_resumen_incompleto(ops, causa, descripcion, accion):
    with pytest.raises(ErrorCore) as e:
        ops.escalar_a_analista(causa, descripcion, accion)
    assert _error(e) == ("VALIDACION", "RESUMEN_INCOMPLETO", False)


def test_escalar_con_transaccion_o_cliente_desconocido(ops):
    with pytest.raises(ErrorCore) as e:
        ops.escalar_a_analista("OTRO", "d", "a", id_transacciones=["TX-9999"])
    assert e.value.codigo == "TRANSACCION_NO_ENCONTRADA"
    with pytest.raises(ErrorCore) as e:
        ops.escalar_a_analista("OTRO", "d", "a", id_cliente="CLI-999")
    assert e.value.codigo == "CLIENTE_NO_EXISTE"
