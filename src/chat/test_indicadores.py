import pytest

from agent.garantias import Evento
from chat.indicadores import desde_eventos, formato_monto, resumen


def _uno(evento):
    (indicador,) = desde_eventos([evento])
    return indicador


def test_formato_monto():
    assert formato_monto(1_250_000) == "$1.250.000"
    assert formato_monto(45000) == "$45.000"


def test_bloqueo():
    i = _uno(
        Evento(
            "bloquear_tarjeta",
            {"ultimos4": "4821"},
            "ok",
            {"bloqueada": True, "ultimos4": "4821", "ya_estaba_bloqueada": False},
        )
    )
    assert (i.principal, i.etiqueta) == (True, "TARJETA BLOQUEADA")
    assert "•••• 4821" in i.detalle


def test_bloqueo_que_ya_estaba():
    i = _uno(
        Evento(
            "bloquear_tarjeta",
            {},
            "ok",
            {"bloqueada": True, "ultimos4": "4821", "ya_estaba_bloqueada": True},
        )
    )
    assert "ya estaba bloqueada" in i.detalle


def test_disputa():
    datos = {
        "id_disputa": "DSP-0001",
        "estado": "abierta",
        "id_transaccion": "TX-0001",
        "monto": 180000,
    }
    i = _uno(Evento("iniciar_disputa", {}, "ok", datos))
    assert (i.principal, i.etiqueta) == (True, "DISPUTA ABIERTA")
    for parte in ("DSP-0001", "TX-0001", "$180.000"):
        assert parte in i.detalle


def test_escalamiento():
    args = {"causa": "MONTO_SUPERA_UMBRAL"}
    datos = {"id_caso": "CASO-0001", "estado": "en_cola_analista", "transacciones_incluidas": 1}
    i = _uno(Evento("escalar_a_analista", args, "ok", datos))
    assert (i.principal, i.etiqueta) == (True, "ESCALADO A ANALISTA")
    assert "CASO-0001" in i.detalle and "MONTO_SUPERA_UMBRAL" in i.detalle


def test_negado_muestra_herramienta_y_motivo():
    motivo = "Regla 2: la transacción supera $500.000; no se inicia automáticamente."
    i = _uno(Evento("iniciar_disputa", {"id_transaccion": "TX-0002"}, "negado", motivo))
    assert (i.principal, i.etiqueta) == (True, "NEGADO")
    assert "iniciar_disputa" in i.detalle and "Regla 2" in i.detalle


@pytest.mark.parametrize(
    ("evento", "etiqueta"),
    [
        (Evento("buscar_cliente", {}, "ok", {"coincidencias": [{}, {}], "total": 2}), "Búsqueda"),
        (
            Evento("verificar_identidad", {}, "ok", {"verificado": True, "nombre": "Ana"}),
            "Identidad verificada",
        ),
        (
            Evento("verificar_identidad", {}, "ok", {"verificado": False, "intentos_restantes": 2}),
            "Verificación fallida",
        ),
        (Evento("analista-transacciones", {}, "delegado", "encargo"), "Análisis delegado"),
        (
            Evento("consultar_transacciones", {}, "ok", {"total": 3}, "analista-transacciones"),
            "Consulta de transacciones",
        ),
        (
            Evento(
                "consultar_transacciones",
                {},
                "error",
                {"tipo": "TRANSITORIO", "codigo": "CORE_NO_DISPONIBLE"},
            ),
            "Falla transitoria",
        ),
        (
            Evento(
                "iniciar_disputa", {}, "error", {"tipo": "NEGOCIO", "codigo": "POLITICA_NO_CUBRE"}
            ),
            "El banco rechazó",
        ),
        (Evento("herramienta_rara", {}, "ok", {}), "herramienta_rara"),
    ],
)
def test_indicadores_secundarios(evento, etiqueta):
    i = _uno(evento)
    assert i.principal is False
    assert etiqueta in i.etiqueta


def test_detalles_de_secundarios():
    assert "2 coincidencias" in _uno(Evento("buscar_cliente", {}, "ok", {"total": 2})).detalle
    assert (
        "Ana"
        in _uno(
            Evento("verificar_identidad", {}, "ok", {"verificado": True, "nombre": "Ana"})
        ).detalle
    )
    consulta = _uno(
        Evento("consultar_transacciones", {}, "ok", {"total": 3}, "analista-transacciones")
    )
    assert "3" in consulta.detalle and "analista-transacciones" in consulta.detalle
    assert (
        "POLITICA_NO_CUBRE"
        in _uno(
            Evento(
                "iniciar_disputa", {}, "error", {"tipo": "NEGOCIO", "codigo": "POLITICA_NO_CUBRE"}
            )
        ).detalle
    )


def test_orden_y_resumen():
    eventos = [
        Evento("bloquear_tarjeta", {}, "ok", {"bloqueada": True, "ultimos4": "4821"}),
        Evento(
            "iniciar_disputa",
            {},
            "ok",
            {"id_disputa": "DSP-0001", "id_transaccion": "TX-0001", "monto": 1},
        ),
        Evento("iniciar_disputa", {}, "negado", "Regla 2"),
        Evento("escalar_a_analista", {"causa": "OTRO"}, "ok", {"id_caso": "CASO-0001"}),
    ]
    indicadores = desde_eventos(eventos)
    assert [i.etiqueta for i in indicadores] == [
        "TARJETA BLOQUEADA",
        "DISPUTA ABIERTA",
        "NEGADO",
        "ESCALADO A ANALISTA",
    ]
    assert resumen(indicadores) == {
        "TARJETA BLOQUEADA": 1,
        "DISPUTA ABIERTA": 1,
        "NEGADO": 1,
        "ESCALADO A ANALISTA": 1,
    }


@pytest.mark.parametrize("nombre", ["iniciar_disputa", "bloquear_tarjeta", "escalar_a_analista"])
def test_accion_sin_confirmacion_del_banco_no_se_afirma(nombre):
    (indicador,) = desde_eventos([Evento(nombre, {}, "ok", None)])
    assert indicador.principal is False
    assert indicador.etiqueta == "Resultado no confirmado"


@pytest.mark.parametrize("herramienta", ["Agent", "Task", "desconocida"])
def test_negaciones_de_las_garantias(herramienta):
    (indicador,) = desde_eventos([Evento(herramienta, {}, "negado", "motivo")])
    assert (indicador.etiqueta, indicador.principal) == ("NEGADO", True)


def test_error_sin_detalle_no_se_atribuye_al_banco():
    (indicador,) = desde_eventos([Evento("bloquear_tarjeta", {}, "error", {"tipo": None})])
    assert indicador.etiqueta == "Error sin detalle"


def test_formato_monto_con_valor_no_numerico():
    assert formato_monto(None) == "None"
    assert formato_monto("abc") == "abc"


def test_singular_y_plural_de_coincidencias():
    assert _uno(Evento("buscar_cliente", {}, "ok", {"total": 1})).detalle == "1 coincidencia"
    assert _uno(Evento("buscar_cliente", {}, "ok", {"total": 0})).detalle == "0 coincidencias"
