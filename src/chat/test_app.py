import asyncio
import os
import signal

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
    salida = capsys.readouterr()
    assert codigo == 1
    assert "No se pudo iniciar el agente" in salida.out
    assert "Traceback" not in salida.err


class AgenteConEstado:
    """Agente falso con estado: el turno cancelado ya registró un bloqueo en la sesión."""

    def __init__(self):
        from agent.garantias import EstadoSesion

        self.estado = EstadoSesion(transacciones={})
        self.recibidos = []

    async def responder(self, texto):
        self.recibidos.append(texto)
        self.estado.eventos.append(
            Evento("bloquear_tarjeta", {}, "ok", {"bloqueada": True, "ultimos4": "4821"})
        )
        raise asyncio.CancelledError  # lo que produce Ctrl+C a mitad del turno


async def test_ctrl_c_durante_un_turno_muestra_el_resumen_con_lo_hecho():
    agente, consola = AgenteConEstado(), _consola()
    await app.conversar(agente, iter(["hola", "otro"]), consola)
    assert agente.recibidos == ["hola"]  # la interrupción cierra la sesión
    texto = consola.export_text()
    assert "interrumpida" in texto
    assert "TARJETA BLOQUEADA" in texto.split("Resumen")[-1]


async def test_ctrl_c_en_el_prompt_muestra_el_resumen():
    def entradas():
        yield "hola"
        raise KeyboardInterrupt  # Ctrl+C mientras se espera el siguiente mensaje

    agente, consola = AgenteFalso(), _consola()
    await app.conversar(agente, entradas(), consola)
    texto = consola.export_text()
    assert "interrumpida" in texto
    assert "DISPUTA ABIERTA" in texto.split("Resumen")[-1]


async def test_turno_con_error_avisa_y_termina():
    class ConError:
        async def responder(self, texto):
            return Turno(texto="Credenciales inválidas", eventos=[], error=True)

    consola = _consola()
    await app.conversar(ConError(), iter(["hola", "otro"]), consola)
    texto = consola.export_text()
    assert "Aviso del sistema" in texto and "Credenciales inválidas" in texto
    assert "Agente Banco Andino" not in texto


async def test_error_del_sdk_a_mitad_de_sesion():
    from claude_agent_sdk import CLIConnectionError

    class Caido:
        async def responder(self, texto):
            raise CLIConnectionError("se cayó")

    consola = _consola()
    await app.conversar(Caido(), iter(["hola"]), consola)
    texto = consola.export_text()
    assert "dejó de responder" in texto and "Resumen de la sesión" in texto


def test_guion_inexistente_da_mensaje_claro(tmp_path, capsys):
    codigo = app.main(["--guion", str(tmp_path / "no_existe.txt")], fabrica_agente=AgenteFalso)
    salida = capsys.readouterr()
    assert codigo == 2
    assert "No se pudo leer el guion" in salida.out
    assert "Traceback" not in salida.err


def test_eof_del_teclado_termina_las_entradas():
    class SinEntrada:
        def input(self, *a):
            raise EOFError

    assert list(app.entradas_de_teclado(SinEntrada())) == []


class AgenteInterrumpido:
    """Agente falso que recibe Ctrl+C real (dos SIGINT, como con `uv run`) a mitad del turno."""

    def __init__(self):
        from agent.garantias import EstadoSesion

        self.estado = EstadoSesion(transacciones={})
        self.cancelaciones = 0
        self.cerrado = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        os.kill(os.getpid(), signal.SIGINT)  # un Ctrl+C durante el cierre se ignora
        await asyncio.sleep(0.05)
        self.cerrado = True

    async def responder(self, texto):
        self.estado.eventos.append(
            Evento("bloquear_tarjeta", {}, "ok", {"bloqueada": True, "ultimos4": "4821"})
        )
        os.kill(os.getpid(), signal.SIGINT)
        os.kill(os.getpid(), signal.SIGINT)
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            self.cancelaciones += 1
            raise


def test_sigint_real_a_mitad_de_turno(tmp_path, capsys):
    guion = tmp_path / "guion.txt"
    guion.write_text("hola\notro\n", encoding="utf-8")
    agente = AgenteInterrumpido()
    codigo = app.main(["--guion", str(guion)], fabrica_agente=lambda: agente)
    salida = capsys.readouterr()
    assert codigo == 0
    assert agente.cancelaciones == 1 and agente.cerrado
    assert "interrumpida" in salida.out
    assert "TARJETA BLOQUEADA" in salida.out.split("Resumen")[-1]
    assert "Traceback" not in salida.err
    assert signal.getsignal(signal.SIGINT) is signal.default_int_handler
