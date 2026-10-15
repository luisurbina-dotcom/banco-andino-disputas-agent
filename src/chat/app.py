"""Bucle de conversación: `uv run python -m chat [--guion archivo]`.

Las entradas vienen del teclado o de un guion (un mensaje por línea, para grabar la demo).
Los indicadores se derivan de los eventos de cada turno (ver `indicadores.py`).
"""

import argparse
import asyncio
from collections.abc import Iterable, Iterator
from pathlib import Path

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


async def conversar(agente, entradas: Iterable[str], consola: Console) -> None:
    todos = []
    try:
        for mensaje in entradas:
            mensaje = mensaje.strip()
            if not mensaje:
                continue
            if mensaje == SALIR:
                break
            vista.mensaje_cliente(consola, mensaje)
            with consola.status("El agente está revisando tu caso…"):
                turno = await agente.responder(mensaje)
            indicadores = desde_eventos(turno.eventos)
            todos.extend(indicadores)
            vista.indicadores(consola, indicadores)
            vista.respuesta_agente(consola, turno.texto)
    except KeyboardInterrupt:
        consola.print("\n[dim]Conversación interrumpida.[/dim]")
    vista.resumen(consola, resumen(todos))


async def _correr(argumentos, consola: Console, fabrica_agente) -> int:
    entradas = (
        iter(leer_guion(argumentos.guion)) if argumentos.guion else entradas_de_teclado(consola)
    )
    try:
        async with fabrica_agente() as agente:
            await conversar(agente, entradas, consola)
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
    return asyncio.run(_correr(argumentos, consola, fabrica_agente))
