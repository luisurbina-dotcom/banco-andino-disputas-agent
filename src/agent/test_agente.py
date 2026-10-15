import sys

import pytest
from claude_agent_sdk import AssistantMessage, CLINotFoundError, ResultMessage, TextBlock

from agent.agente import HERRAMIENTAS, AgenteDisputas, AgenteNoDisponible, construir_opciones
from agent.garantias import Evento
from agent.prompt import PROMPT_SISTEMA

pytestmark = pytest.mark.anyio


def test_opciones_aislan_al_agente_y_registran_las_garantias(estado):
    opciones = construir_opciones(estado)
    assert opciones.system_prompt == PROMPT_SISTEMA
    assert opciones.mcp_servers == {
        "banco": {"type": "stdio", "command": sys.executable, "args": ["-m", "mcp_server"]}
    }
    assert opciones.allowed_tools == HERRAMIENTAS
    assert len(HERRAMIENTAS) == 6
    assert all(h.startswith("mcp__banco__") for h in HERRAMIENTAS)
    assert opciones.tools == []
    assert opciones.strict_mcp_config is True  # sin conectores MCP heredados de la cuenta
    assert opciones.setting_sources == []
    assert opciones.max_turns is None  # el turno lo cierra la razón de parada, no un tope
    for evento in ("PreToolUse", "PostToolUse", "PostToolUseFailure"):
        (matcher,) = opciones.hooks[evento]
        assert matcher.matcher == "mcp__banco__.*"
        assert len(matcher.hooks) == 1


class ClienteFalso:
    """Emite los mensajes de un turno; los hooks se simulan agregando eventos."""

    def __init__(self, estado, mensajes, eventos_del_turno=()):
        self.estado = estado
        self.mensajes = mensajes
        self.eventos_del_turno = list(eventos_del_turno)
        self.consultas = []

    async def query(self, texto):
        self.consultas.append(texto)

    async def receive_response(self):
        self.estado.eventos.extend(self.eventos_del_turno)
        for mensaje in self.mensajes:
            yield mensaje


def _resultado(texto, stop_reason="end_turn", num_turns=3):
    return ResultMessage(
        subtype="success",
        duration_ms=1,
        duration_api_ms=1,
        is_error=False,
        num_turns=num_turns,
        session_id="s",
        stop_reason=stop_reason,
        result=texto,
    )


async def test_responder_devuelve_texto_razon_de_parada_y_eventos_del_turno(estado):
    viejo = Evento("buscar_cliente", {}, "ok", {})
    estado.eventos.append(viejo)
    nuevo = Evento("iniciar_disputa", {"id_transaccion": "TX-0002"}, "negado", "Regla 2")
    mensajes = [
        AssistantMessage(content=[TextBlock(text="Revisando…")], model="m"),
        _resultado("Listo: escalé el cobro alto."),
    ]
    agente = AgenteDisputas(estado=estado)
    agente._cliente = ClienteFalso(estado, mensajes, [nuevo])
    turno = await agente.responder("No reconozco un cobro")
    assert turno.texto == "Listo: escalé el cobro alto."
    assert (turno.stop_reason, turno.num_turns) == ("end_turn", 3)
    assert turno.eventos == [nuevo]  # solo los de este turno
    assert agente._cliente.consultas == ["No reconozco un cobro"]


async def test_sin_resultado_usa_el_ultimo_texto_del_asistente(estado):
    agente = AgenteDisputas(estado=estado)
    mensajes = [AssistantMessage(content=[TextBlock(text="Hola")], model="m")]
    agente._cliente = ClienteFalso(estado, mensajes)
    turno = await agente.responder("hola")
    assert (turno.texto, turno.stop_reason) == ("Hola", None)


async def test_sin_cli_el_agente_no_arranca_con_un_mensaje_claro(estado):
    class SinCli:
        def __init__(self, options):
            pass

        async def connect(self):
            raise CLINotFoundError("no está")

    with pytest.raises(AgenteNoDisponible, match="Claude Code"):
        async with AgenteDisputas(estado=estado, fabrica_cliente=SinCli):
            pass


def test_el_prompt_se_puede_reemplazar_sin_tocar_las_garantias(estado):
    opciones = construir_opciones(estado, prompt_sistema="Modelo de prueba desobediente")
    assert opciones.system_prompt == "Modelo de prueba desobediente"
    assert len(opciones.hooks["PreToolUse"][0].hooks) == 1
