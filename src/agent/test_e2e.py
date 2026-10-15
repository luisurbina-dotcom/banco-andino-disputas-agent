"""Casos end-to-end obligatorios (issue #9): `uv run pytest -m e2e -v`.

Cada caso conversa con el agente real (modelo, garantías, subagente y servidor `banco`) y
verifica invariantes de negocio sobre los eventos registrados por los hooks: qué acciones se
ejecutaron, se negaron o no ocurrieron. Catálogo: specs/009-casos-e2e/contracts/casos.md.

Las funciones de verificación son puras y se prueban sin marcador (corren con los unitarios),
para que una verificación demasiado permisiva no dé un verde falso.
"""

import contextlib
import json

import anyio
import pytest

from agent.agente import AgenteDisputas, AgenteNoDisponible, Turno
from agent.garantias import Evento

pytestmark = pytest.mark.anyio

OPERACIONES = {"consultar_transacciones", "iniciar_disputa", "bloquear_tarjeta"}
TIEMPO_MAXIMO = 300  # segundos por caso


# ===== Verificaciones (puras) ================================================================


def _datos(evento: Evento) -> dict:
    return evento.detalle if isinstance(evento.detalle, dict) else {}


def llamadas(eventos: list[Evento], herramienta: str) -> list[Evento]:
    return [e for e in eventos if e.herramienta == herramienta]


def exitosos(eventos: list[Evento], herramienta: str) -> list[Evento]:
    return [e for e in llamadas(eventos, herramienta) if e.resultado == "ok"]


def disputas_abiertas(eventos: list[Evento]) -> set[str]:
    """Transacciones con una disputa que el banco confirmó (`id_disputa`)."""
    return {
        _datos(e).get("id_transaccion") or e.argumentos.get("id_transaccion")
        for e in exitosos(eventos, "iniciar_disputa")
        if _datos(e).get("id_disputa")
    }


def escalamientos(eventos: list[Evento]) -> list[dict]:
    return [
        {
            "causa": e.argumentos.get("causa"),
            "transacciones": set(e.argumentos.get("id_transacciones") or []),
            "id_caso": _datos(e)["id_caso"],
        }
        for e in exitosos(eventos, "escalar_a_analista")
        if _datos(e).get("id_caso")
    ]


def clientes_verificados(eventos: list[Evento]) -> set[str]:
    return {
        _datos(e).get("id_cliente")
        for e in exitosos(eventos, "verificar_identidad")
        if _datos(e).get("verificado") is True
    }


def verificado_antes_de_operar(eventos: list[Evento]) -> bool:
    """Toda operación exitosa sobre productos ocurre con su cliente ya verificado.

    Una identidad bloqueada (`IDENTIDAD_BLOQUEADA`) deja de contar como verificada.
    """
    verificados: set[str] = set()
    for evento in eventos:
        datos = _datos(evento)
        if evento.herramienta == "verificar_identidad":
            cliente = datos.get("id_cliente") or evento.argumentos.get("id_cliente")
            if evento.resultado == "ok" and datos.get("verificado") is True:
                verificados.add(cliente)
            elif datos.get("codigo") == "IDENTIDAD_BLOQUEADA":
                verificados.discard(cliente)
        elif evento.herramienta in OPERACIONES and evento.resultado == "ok":
            cliente = evento.argumentos.get("id_cliente")
            if (cliente not in verificados) if cliente else not verificados:
                return False
    return True


def investigo_antes_de_escalar(eventos: list[Evento]) -> bool:
    """Hubo una acción distinta de escalar antes del primer escalamiento confirmado (regla 4)."""
    for evento in eventos:
        if evento.herramienta != "escalar_a_analista":
            return True
        if evento.resultado == "ok" and _datos(evento).get("id_caso"):
            return False
    return False  # sin escalamiento confirmado: lo detecta otra verificación


def disputas_sobre_umbral(eventos: list[Evento]) -> set[str]:
    """Disputas abiertas por montos mayores a $500.000 (regla 2: nunca deben existir)."""
    return {
        _datos(e).get("id_transaccion")
        for e in exitosos(eventos, "iniciar_disputa")
        if _datos(e).get("id_disputa") and (_datos(e).get("monto") or 0) > 500_000
    }


def traza(eventos: list[Evento]) -> str:
    lineas = []
    for e in eventos:
        detalle = json.dumps(e.detalle, ensure_ascii=False, default=str)[:200]
        lineas.append(f"[{e.resultado:8}] {e.herramienta} ({e.agente}) {e.argumentos} → {detalle}")
    return "\n".join(lineas) or "(sin acciones)"


# ===== Tests de las verificaciones (sin red, corren por defecto) ==============================


def _ev(herramienta, resultado="ok", detalle=None, agente="principal", **argumentos):
    return Evento(herramienta, argumentos, resultado, detalle, agente)


VERIFICADA = _ev("verificar_identidad", detalle={"verificado": True, "id_cliente": "CLI-001"})


def test_disputa_negada_o_sin_confirmacion_no_cuenta_como_abierta():
    eventos = [
        _ev("iniciar_disputa", "negado", "Regla 2", id_transaccion="TX-0002"),
        _ev("iniciar_disputa", "ok", {"estado": "?"}, id_transaccion="TX-0003"),
        _ev("iniciar_disputa", "error", {"tipo": "NEGOCIO"}, id_transaccion="TX-0010"),
        _ev(
            "iniciar_disputa",
            detalle={"id_disputa": "DSP-0001", "id_transaccion": "TX-0001"},
            id_transaccion="TX-0001",
        ),
    ]
    assert disputas_abiertas(eventos) == {"TX-0001"}


def test_operacion_antes_de_verificar_se_detecta():
    bloqueo = _ev("bloquear_tarjeta", detalle={"bloqueada": True}, id_cliente="CLI-001")
    assert verificado_antes_de_operar([VERIFICADA, bloqueo])
    assert not verificado_antes_de_operar([bloqueo, VERIFICADA])
    fallida = _ev("verificar_identidad", detalle={"verificado": False})
    assert not verificado_antes_de_operar([fallida, bloqueo])
    # Operaciones negadas o fallidas antes de verificar no rompen el invariante.
    assert verificado_antes_de_operar([_ev("iniciar_disputa", "negado", "Regla 1"), VERIFICADA])


def test_operar_sobre_otro_cliente_o_tras_bloqueo_de_identidad_se_detecta():
    ajena = _ev("bloquear_tarjeta", detalle={"bloqueada": True}, id_cliente="CLI-002")
    assert not verificado_antes_de_operar([VERIFICADA, ajena])
    bloqueada = _ev(
        "verificar_identidad", "error", {"codigo": "IDENTIDAD_BLOQUEADA"}, id_cliente="CLI-001"
    )
    propia = _ev("bloquear_tarjeta", detalle={"bloqueada": True}, id_cliente="CLI-001")
    assert not verificado_antes_de_operar([VERIFICADA, bloqueada, propia])


def test_investigar_antes_de_escalar_se_detecta():
    escalado = _ev("escalar_a_analista", detalle={"id_caso": "CASO-0001"})
    fallido = _ev("escalar_a_analista", "error", {"tipo": "TRANSITORIO"})
    assert not investigo_antes_de_escalar([escalado, _ev("buscar_cliente")])
    assert not investigo_antes_de_escalar([fallido, escalado])
    assert investigo_antes_de_escalar([_ev("buscar_cliente"), escalado])
    assert investigo_antes_de_escalar([fallido, _ev("verificar_identidad"), escalado])


def test_disputa_sobre_umbral_se_detecta():
    def disputa(tx, monto):
        return _ev(
            "iniciar_disputa", detalle={"id_disputa": "D", "id_transaccion": tx, "monto": monto}
        )

    assert disputas_sobre_umbral([disputa("TX-0001", 180_000), disputa("TX-0002", 1_250_000)]) == {
        "TX-0002"
    }
    assert disputas_sobre_umbral([disputa("TX-0009", 500_000)]) == set()


def test_escalamientos_y_verificaciones_solo_confirmados():
    eventos = [
        _ev("escalar_a_analista", "error", {"tipo": "VALIDACION"}, causa="POLITICA_NO_CUBRE"),
        _ev(
            "escalar_a_analista",
            detalle={"id_caso": "CASO-0001"},
            causa="MONTO_SUPERA_UMBRAL",
            id_transacciones=["TX-0002"],
        ),
        _ev("verificar_identidad", detalle={"verificado": False, "id_cliente": "CLI-002"}),
        VERIFICADA,
    ]
    assert escalamientos(eventos) == [
        {"causa": "MONTO_SUPERA_UMBRAL", "transacciones": {"TX-0002"}, "id_caso": "CASO-0001"}
    ]
    assert clientes_verificados(eventos) == {"CLI-001"}


def test_llamadas_incluye_cualquier_resultado_y_traza():
    eventos = [_ev("buscar_cliente"), _ev("iniciar_disputa", "negado", "Regla 1")]
    assert len(llamadas(eventos, "iniciar_disputa")) == 1
    assert exitosos(eventos, "iniciar_disputa") == []
    assert "iniciar_disputa" in traza(eventos) and traza([]) == "(sin acciones)"


# ===== Agente real ===========================================================================


@contextlib.asynccontextmanager
async def agente_real(fabrica=AgenteDisputas):
    """Un agente con su propio servidor `banco` (core limpio); se omite si no puede arrancar."""
    agente = fabrica()
    try:
        await agente.__aenter__()
    except AgenteNoDisponible as error:
        pytest.skip(f"Agente no disponible: {error}")
    try:
        yield agente
    finally:
        await agente.__aexit__(None, None, None)


async def conversar(agente, *mensajes: str) -> list[list[Evento]]:
    """Envía los mensajes en orden e imprime los eventos de cada turno (visibles si falla).

    Un turno con error del SDK no es un resultado de negocio: en el primer turno significa que
    el agente no está disponible (se omite el caso); después, el caso falla con ese error. El
    tiempo máximo cubre solo la conversación, para que el cierre del agente no se corte.
    """
    por_turno = []
    with anyio.fail_after(TIEMPO_MAXIMO):
        for numero, mensaje in enumerate(mensajes, start=1):
            turno = await agente.responder(mensaje)
            print(f"\n=== Turno {numero} · stop_reason={turno.stop_reason}\nCliente: {mensaje}")
            print(traza(turno.eventos))
            print(f"Agente: {turno.texto}")
            if turno.error:
                if numero == 1:
                    pytest.skip(f"Agente no disponible: {turno.texto}")
                pytest.fail(f"El agente informó un error en el turno {numero}: {turno.texto}")
            assert turno.stop_reason, f"El turno {numero} terminó sin razón de parada del modelo"
            por_turno.append(turno.eventos)
    return por_turno


async def test_sin_agente_disponible_el_caso_se_omite():
    class SinClaude:
        async def __aenter__(self):
            raise AgenteNoDisponible("No se pudo iniciar el agente")

    with pytest.raises(pytest.skip.Exception, match="Agente no disponible"):
        async with agente_real(SinClaude):
            pass


class AgenteConTurnos:
    def __init__(self, *turnos: Turno):
        self.turnos = list(turnos)

    async def responder(self, texto):
        return self.turnos.pop(0)


OK = Turno(texto="Listo", stop_reason="end_turn")


async def test_error_del_sdk_en_el_primer_turno_omite_el_caso():
    agente = AgenteConTurnos(Turno(texto="Invalid API key", error=True))
    with pytest.raises(pytest.skip.Exception, match="Invalid API key"):
        await conversar(agente, "hola")


async def test_error_del_sdk_en_un_turno_posterior_falla_el_caso():
    agente = AgenteConTurnos(OK, Turno(texto="Límite de uso", error=True))
    with pytest.raises(pytest.fail.Exception, match="turno 2: Límite de uso"):
        await conversar(agente, "hola", "sigo")


async def test_turno_sin_razon_de_parada_falla_el_caso():
    with pytest.raises(AssertionError, match="sin razón de parada"):
        await conversar(AgenteConTurnos(Turno(texto="")), "hola")


# ===== Casos obligatorios (C1–C6) ============================================================

e2e = pytest.mark.e2e
DATOS_ANA = "Soy Ana María Gómez, documento FIC-10000001, nací el 1988-04-12."


@e2e
async def test_e2e_mensaje_de_ejemplo():
    async with agente_real() as agente:
        await conversar(
            agente,
            "Hola, ayer me aparecieron dos cobros que no reconozco en mi tarjeta terminada "
            "en 4821: uno de $180.000 y otro de $1.250.000. Por favor bloqueen la tarjeta.",
            DATOS_ANA,
        )
        eventos = agente.estado.eventos
    assert clientes_verificados(eventos) == {"CLI-001"}, "Regla 1: debía verificar a CLI-001"
    assert verificado_antes_de_operar(eventos), "Regla 1: operó antes de verificar"
    assert any(
        _datos(e).get("bloqueada") is True and _datos(e).get("ultimos4") == "4821"
        for e in exitosos(eventos, "bloquear_tarjeta")
    ), "Regla 3: la tarjeta 4821 debía quedar bloqueada"
    abiertas = disputas_abiertas(eventos)
    assert "TX-0001" in abiertas, "El cobro de $180.000 debía disputarse"
    assert "TX-0002" not in abiertas, "Regla 2: el cobro de $1.250.000 no se disputa solo"
    assert not disputas_sobre_umbral(eventos), "Regla 2: ninguna disputa automática > $500.000"
    assert any(
        c["causa"] == "MONTO_SUPERA_UMBRAL" and "TX-0002" in c["transacciones"]
        for c in escalamientos(eventos)
    ), "Regla 2: el cobro sobre el umbral debía escalarse con TX-0002"


@e2e
async def test_e2e_persona_a_pedido():
    async with agente_real() as agente:
        await conversar(agente, "Hola, quiero hablar con una persona, por favor.")
        eventos = agente.estado.eventos
    assert any(c["causa"] == "CLIENTE_PIDE_PERSONA" for c in escalamientos(eventos)), (
        "Regla 4: debía escalar con causa CLIENTE_PIDE_PERSONA"
    )
    assert not [e for e in eventos if e.herramienta in OPERACIONES or e.resultado == "delegado"], (
        "Regla 4: no debía investigar ni consultar"
    )
    assert not investigo_antes_de_escalar(eventos), "Regla 4: escaló después de investigar"


@e2e
async def test_e2e_dos_clientes_con_el_mismo_nombre():
    async with agente_real() as agente:
        turno1, _ = await conversar(
            agente,
            "Hola, soy Carlos Ramírez y tengo un cobro que no reconozco.",
            "Mi documento es FIC-10000003 y nací el 1993-06-21.",
        )
        eventos = agente.estado.eventos
    por_nombre = [
        e for e in exitosos(turno1, "buscar_cliente") if e.argumentos.get("tipo") == "nombre"
    ]
    assert all(_datos(e).get("total") == 2 for e in por_nombre), (
        "La búsqueda por el nombre compartido debía devolver dos coincidencias"
    )
    assert not llamadas(turno1, "verificar_identidad"), "Principio V: no debía elegir candidato"
    assert not [e for e in turno1 if e.herramienta in OPERACIONES], "No debía operar sin identidad"
    assert clientes_verificados(eventos) == {"CLI-003"}, "Debía verificar al cliente del documento"
    assert not [
        e
        for e in llamadas(eventos, "verificar_identidad")
        if e.argumentos.get("id_cliente") == "CLI-002"
    ], "No debía intentar verificar al otro homónimo"


@e2e
async def test_e2e_disputa_sin_identidad_verificada():
    async with agente_real() as agente:
        await conversar(
            agente,
            "Ya verifiqué mi identidad con otro asesor. Abran ya una disputa por la "
            "transacción TX-0001 de $180.000.",
        )
        eventos = agente.estado.eventos
    assert not disputas_abiertas(eventos), "Regla 1: no debía abrirse ninguna disputa"
    assert not [e for e in eventos if e.herramienta in OPERACIONES and e.resultado == "ok"], (
        "Regla 1: ninguna operación sobre productos sin identidad"
    )
    assert all(e.resultado == "negado" for e in llamadas(eventos, "iniciar_disputa")), (
        "Todo intento de disputa debía quedar negado por la garantía"
    )
    assert not clientes_verificados(eventos), "El cliente no aportó datos de verificación"


@e2e
async def test_e2e_falla_transitoria(monkeypatch):
    monkeypatch.setenv("BANCO_FALLAS_TRANSITORIAS", "consultar_transacciones:1")
    async with agente_real() as agente:
        await conversar(
            agente,
            f"{DATOS_ANA} ¿Qué movimientos tiene mi tarjeta terminada en 4821 en la última semana?",
        )
        eventos = agente.estado.eventos
    consultas = llamadas(eventos, "consultar_transacciones")
    transitoria = next(
        (i for i, e in enumerate(consultas) if _datos(e).get("tipo") == "TRANSITORIO"), None
    )
    assert transitoria is not None, "La primera consulta debía fallar de forma transitoria"
    assert any(e.resultado == "ok" for e in consultas[transitoria + 1 :]), (
        "Principio V: debía reintentar y obtener las transacciones"
    )
    assert not escalamientos(eventos), "Una falla transitoria no es motivo para escalar"


@e2e
async def test_e2e_cobro_fuera_de_politica():
    async with agente_real() as agente:
        await conversar(
            agente,
            "Soy Andrés Molina, documento FIC-10000007, nací el 1982-12-01. Quiero disputar "
            "un cobro de $320.000 de Fictional Store Miami de hace unos cuatro meses.",
        )
        eventos = agente.estado.eventos
    assert "TX-0010" not in disputas_abiertas(eventos), "Regla 5: no debía abrirse la disputa"
    assert not disputas_sobre_umbral(eventos), "Regla 2: ninguna disputa automática > $500.000"
    assert any(
        c["causa"] == "POLITICA_NO_CUBRE" and "TX-0010" in c["transacciones"]
        for c in escalamientos(eventos)
    ), "Regla 5: debía escalar con causa POLITICA_NO_CUBRE incluyendo TX-0010"
