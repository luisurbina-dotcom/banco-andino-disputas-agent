"""Servidor MCP `banco` (FastMCP, stdio): expone el core simulado como herramientas.

Solo traduce entre herramientas y `Core`: las descripciones guían al modelo y los `ErrorCore` se
envían como error de herramienta con el JSON del contrato. Contrato:
specs/004-core-bancario-identidad/contracts/herramientas.md.
"""

from typing import Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from mcp_server.core import Core
from mcp_server.datos import cargar
from mcp_server.errores import ErrorCore

INSTRUCCIONES = (
    "Core bancario simulado de Banco Andino con datos ficticios. Flujo: 1) buscar_cliente para "
    "localizar candidatos; 2) si hay más de uno, pide otro identificador; 3) verificar_identidad "
    "con un único cliente antes de cualquier operación sobre sus productos."
)

# Textos expuestos al modelo: deben coincidir con contracts/herramientas.md (lo comprueba un test).
DESCRIPCION_BUSCAR = (
    "Localiza clientes del banco por documento, nombre o últimos 4 dígitos de tarjeta. NO "
    "confirma la identidad: úsala solo para encontrar candidatos y luego llama a "
    "verificar_identidad con uno solo. Puede devolver varias coincidencias; en ese caso pide "
    "al cliente otro identificador (documento o últimos 4 dígitos) y no elijas tú. Una lista "
    "vacía significa que no hay coincidencias, no es un error."
)
DESCRIPCION_VERIFICAR = (
    "Confirma la identidad de UN cliente ya localizado con buscar_cliente, comparando su "
    "fecha de nacimiento (AAAA-MM-DD) que debe dar el propio cliente. Es obligatoria antes de "
    "consultar transacciones, iniciar disputas o bloquear tarjetas. No la uses para buscar "
    "clientes ni con datos que no haya dado el cliente. Si la respuesta es verificado=false, "
    "informa los intentos restantes; tras 3 fallos queda bloqueada y debes escalar a un "
    "analista."
)

mcp = FastMCP("banco", instructions=INSTRUCCIONES)
core = Core(cargar())


def _ejecutar(operacion, *args) -> dict:
    try:
        return operacion(*args)
    except ErrorCore as error:
        raise ToolError(error.a_json()) from None


@mcp.tool(description=DESCRIPCION_BUSCAR)
def buscar_cliente(criterio: str, tipo: Literal["documento", "nombre", "ultimos4"]) -> dict:
    return _ejecutar(core.buscar_cliente, criterio, tipo)


@mcp.tool(description=DESCRIPCION_VERIFICAR)
def verificar_identidad(id_cliente: str, fecha_nacimiento: str) -> dict:
    return _ejecutar(core.verificar_identidad, id_cliente, fecha_nacimiento)


def main() -> None:
    mcp.run()
