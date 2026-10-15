"""Dibujo de la conversación en la terminal con Rich."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from chat.indicadores import Indicador


def bienvenida(consola: Console) -> None:
    consola.print(
        Panel(
            "Asistente de disputas de [bold]Banco Andino[/bold].\n"
            "Todos los datos son [bold]ficticios[/bold]. Escribe como cliente; "
            "[bold]/salir[/bold] para terminar.\n"
            "Solo los recuadros de color muestran acciones reales en el banco.",
            title="Banco Andino · Chat",
            border_style="cyan",
        )
    )


def mensaje_cliente(consola: Console, texto: str) -> None:
    # Text() muestra lo escrito tal cual: corchetes como "[/b]" no se interpretan como marcado.
    consola.print(Panel(Text(texto), title="Cliente", title_align="right", border_style="white"))


def respuesta_agente(consola: Console, texto: str) -> None:
    # El modelo responde con Markdown (negritas, listas): se renderiza en lugar de mostrar `**`.
    consola.print(
        Panel(
            Markdown(texto, hyperlinks=False),
            title="Agente Banco Andino",
            title_align="left",
            border_style="cyan",
        )
    )


def indicadores(consola: Console, lista: list[Indicador]) -> None:
    for indicador in lista:
        if indicador.principal:
            consola.print(
                Panel(
                    Text(indicador.detalle),
                    title=f"{indicador.icono} {indicador.etiqueta}",
                    title_align="left",
                    border_style=indicador.estilo,
                    expand=False,
                )
            )
        else:
            linea = Text(f"  {indicador.icono} {indicador.etiqueta}: ", style=indicador.estilo)
            linea.append(indicador.detalle, style="dim")
            consola.print(linea)


def aviso(consola: Console, texto: str) -> None:
    consola.print(Panel(Text(texto), title="Aviso del sistema", border_style="red"))


def resumen(consola: Console, conteo: dict[str, int]) -> None:
    if not conteo:
        consola.print(Panel("Sin acciones en el banco.", title="Resumen de la sesión"))
        return
    tabla = Table(show_header=False, box=None)
    for etiqueta, cantidad in conteo.items():
        tabla.add_row(etiqueta, str(cantidad))
    consola.print(Panel(tabla, title="Resumen de la sesión", border_style="cyan", expand=False))
