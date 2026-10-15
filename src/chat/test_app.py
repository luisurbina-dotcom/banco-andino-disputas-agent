import pytest
from rich.console import Console

from agent.agente import AgenteNoDisponible, Turno
from agent.garantias import Evento
from chat import app

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


class AgenteFalso:
    def __init__(self):
        self.recibidos = []

    async def responder(self, texto):
        self.recibidos.append(texto)
        eventos = [
            Evento(
                "iniciar_disputa",
                {},
                "ok",
                {"id_disputa": "DSP-0001", "id_transaccion": "TX-0001", "monto": 180000},
            )
        ]
        return Turno(texto=f"Respuesta a: {texto}", eventos=eventos, stop_reason="end_turn")


def _consola():
    return Console(record=True, width=120, color_system=None)


async def test_conversar_muestra_turnos_indicadores_y_resumen():
    agente, consola = AgenteFalso(), _consola()
    await app.conversar(agente, iter(["hola", "  ", "otra cosa"]), consola)
    texto = consola.export_text()
    assert agente.recibidos == ["hola", "otra cosa"]  # el vacío no se envía
    assert "Respuesta a: hola" in texto and "DISPUTA ABIERTA" in texto
    assert "Resumen de la sesión" in texto and "DISPUTA ABIERTA" in texto.split("Resumen")[-1]


async def test_salir_termina_la_conversacion():
    agente, consola = AgenteFalso(), _consola()
    await app.conversar(agente, iter(["hola", "/salir", "no se envía"]), consola)
    assert agente.recibidos == ["hola"]


def test_leer_guion_ignora_vacias(tmp_path):
    guion = tmp_path / "g.txt"
    guion.write_text("primero\n\n  segundo  \n", encoding="utf-8")
    assert app.leer_guion(guion) == ["primero", "segundo"]


def test_main_sin_agente_disponible_muestra_mensaje(capsys):
    class SinAgente:
        async def __aenter__(self):
            raise AgenteNoDisponible("No se pudo iniciar el agente: instala Claude Code")

        async def __aexit__(self, *exc):
            pass

    codigo = app.main([], fabrica_agente=SinAgente)
    salida = capsys.readouterr().out
    assert codigo == 1
    assert "No se pudo iniciar el agente" in salida
    assert "Traceback" not in salida
