"""Bucle de conversación: `uv run python -m chat [--guion archivo]`.

Las entradas vienen del teclado o de un guion (un mensaje por línea, para grabar la demo).
Los indicadores se derivan de los eventos de cada turno (ver `indicadores.py`).
"""

import argparse
import asyncio
import contextlib
import signal
from collections.abc import Iterable, Iterator
from pathlib import Path

from claude_agent_sdk import ClaudeSDKError
from rich.console import Console

from agent.agente import AgenteDisputas, AgenteNoDisponible
from chat import vista
from chat.indicadores import desde_eventos, resumen

SALIR = "/salir"


def leer_guion(ruta: Path) -> list[str]:
    lineas = Path(ruta).read_text(encoding="utf-8").splitlines()
    return [linea.strip() for linea in lineas if linea.strip()]


def entradas_de_teclado(consola: Console) -> Iterator[str]:
    while True:
        try:
            yield consola.input("[bold]Tú › [/bold]")
        except EOFError:
            return


@contextlib.contextmanager
def _ctrl_c(accion):
    """Mientras dura el bloque, Ctrl+C ejecuta `accion` en el loop en lugar de interrumpir.

    Fuera del bloque, Ctrl+C lanza KeyboardInterrupt (por ejemplo, dentro de `input()`).
    Sin soporte de señales en el loop, se conserva el manejo por defecto.
    """
    loop = asyncio.get_running_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, accion)
    except (NotImplementedError, RuntimeError):
        yield
        return
    try:
        yield
    finally:
        loop.remove_signal_handler(signal.SIGINT)  # vuelve a default_int_handler


async def _responder(agente, mensaje: str):
    # Ctrl+C durante el turno cancela solo el turno; con `uv run` la señal llega dos veces,
    # por eso se cancela una sola vez.
    turno = asyncio.ensure_future(agente.responder(mensaje))
    with _ctrl_c(lambda: turno.done() or turno.cancelling() or turno.cancel()):
        return await turno


def _eventos_de_la_sesion(agente, inicio: int, vistos: list) -> list:
    # Los eventos del estado incluyen los de un turno interrumpido a mitad de camino.
    estado = getattr(agente, "estado", None)
    return estado.eventos[inicio:] if estado is not None else vistos


async def conversar(agente, entradas: Iterable[str], consola: Console) -> None:
    estado = getattr(agente, "estado", None)
    inicio = len(estado.eventos) if estado is not None else 0
    vistos = []
    try:
        for mensaje in entradas:
            mensaje = mensaje.strip()
            if not mensaje:
                continue
            if mensaje == SALIR:
                break
            vista.mensaje_cliente(consola, mensaje)
            with consola.status("El agente está revisando tu caso…"):
                turno = await _responder(agente, mensaje)
            vistos.extend(turno.eventos)
            vista.indicadores(consola, desde_eventos(turno.eventos))
            if turno.error:
                vista.aviso(
                    consola, f"El agente informó un error y la sesión termina: {turno.texto}"
                )
                break
            vista.respuesta_agente(consola, turno.texto)
    except (KeyboardInterrupt, asyncio.CancelledError):
        consola.print("\n[dim]Conversación interrumpida.[/dim]")
    except ClaudeSDKError as error:
        vista.aviso(consola, f"El agente dejó de responder ({type(error).__name__}).")
    vista.resumen(consola, resumen(desde_eventos(_eventos_de_la_sesion(agente, inicio, vistos))))


async def _correr(argumentos, consola: Console, fabrica_agente) -> int:
    try:
        entradas = (
            iter(leer_guion(argumentos.guion)) if argumentos.guion else entradas_de_teclado(consola)
        )
    except OSError as error:
        consola.print(f"[bold red]No se pudo leer el guion: {error.strerror}[/bold red]")
        return 2
    # asyncio.run instala un manejador que solo cancela la tarea principal y no interrumpe un
    # input() bloqueado; en el prompt, Ctrl+C debe lanzar KeyboardInterrupt.
    with contextlib.suppress(ValueError):  # fuera del hilo principal no se cambian señales
        signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        async with fabrica_agente() as agente:
            try:
                await conversar(agente, entradas, consola)
            finally:
                # Al cerrar, Ctrl+C se ignora: la desconexión del SDK tiene sus propios límites
                # de tiempo y, si se interrumpe, deja el subproceso sin recoger.
                with contextlib.suppress(NotImplementedError, RuntimeError):
                    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, lambda: None)
    except AgenteNoDisponible as error:
        consola.print(f"[bold red]{error}[/bold red]")
        return 1
    return 0


def main(argv: list[str] | None = None, fabrica_agente=AgenteDisputas) -> int:
    parser = argparse.ArgumentParser(description="Chat con el agente de disputas de Banco Andino")
    parser.add_argument("--guion", type=Path, help="archivo con un mensaje del cliente por línea")
    argumentos = parser.parse_args(argv)
    consola = Console()
    vista.bienvenida(consola)
    try:
        return asyncio.run(_correr(argumentos, consola, fabrica_agente))
    except KeyboardInterrupt:  # Ctrl+C antes de que arranque la conversación
        consola.print("\n[dim]Conversación interrumpida.[/dim]")
        return 130
