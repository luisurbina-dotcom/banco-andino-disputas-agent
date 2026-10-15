"""Servidor MCP `banco` (FastMCP, stdio): expone el core simulado como herramientas.

Solo traduce entre herramientas y el core: las descripciones guían al modelo y los `ErrorCore` se
envían como error de herramienta con el JSON del contrato. Contratos:
specs/004-core-bancario-identidad/contracts/herramientas.md (identificación) y
specs/005-operaciones-core/contracts/herramientas.md (operaciones).
"""

import os
import re
from typing import Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from mcp_server.core import Core
from mcp_server.datos import cargar
from mcp_server.errores import ErrorCore
from mcp_server.operaciones import Operaciones

INSTRUCCIONES = (
    "Core bancario simulado de Banco Andino con datos ficticios. Flujo: 1) buscar_cliente para "
    "localizar candidatos; 2) si hay más de uno, pide otro identificador; 3) verificar_identidad "
    "con un único cliente antes de cualquier operación sobre sus productos."
)

# Textos expuestos al modelo: deben coincidir con los contratos (lo comprueba un test).
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
DESCRIPCION_CONSULTAR = (
    "Lista las transacciones de una tarjeta del cliente en un rango de fechas (AAAA-MM-DD; "
    "por defecto los últimos 30 días). Requiere que el cliente haya pasado "
    "verificar_identidad; no la uses con clientes sin verificar ni si el cliente solo pidió "
    "hablar con una persona. Úsala para encontrar los cobros que el cliente no reconoce antes"
    " de disputarlos. Una lista vacía no es un error. Si recibes un error TRANSITORIO, "
    "reintenta la llamada."
)
DESCRIPCION_DISPUTAR = (
    "Abre una disputa sobre una transacción del cliente verificado. El core aplica la "
    "política: hasta $500.000 la disputa se abre; si responde MONTO_SUPERA_UMBRAL o "
    "POLITICA_NO_CUBRE, no la reintentes: escala el caso con escalar_a_analista. Si responde "
    "DISPUTA_EXISTENTE, informa al cliente que ya hay una disputa en curso. No la uses si el "
    "cliente pidió hablar con una persona."
)
DESCRIPCION_BLOQUEAR = (
    "Bloquea de inmediato una tarjeta del cliente verificado por sospecha de fraude; no "
    "requiere aprobación adicional. Si la tarjeta ya estaba bloqueada, lo indica sin error. "
    "Úsala cuando el cliente sospeche clonación, robo o pérdida; no la uses si el cliente no "
    "lo pidió ni expresó sospecha de fraude."
)
DESCRIPCION_ESCALAR = (
    "Pasa el caso a un analista humano, que NO ve la conversación. Úsala de inmediato si el "
    "cliente pide hablar con una persona (sin verificar ni investigar antes), y cuando una disputa "
    "responda MONTO_SUPERA_UMBRAL o POLITICA_NO_CUBRE, o la identidad quede bloqueada. Envía la "
    "causa, los ids de las transacciones involucradas, lo que ya hiciste y una acción recomendada; "
    "el core completa montos y fechas."
)

mcp = FastMCP("banco", instructions=INSTRUCCIONES)
core = Core(cargar())
ops = Operaciones(core)


HERRAMIENTAS_CON_FALLAS = (
    "consultar_transacciones",
    "iniciar_disputa",
    "bloquear_tarjeta",
    "escalar_a_analista",
)


def configurar_fallas(texto: str) -> None:
    """Programa fallas transitorias con el formato `herramienta:N[,herramienta:N]`.

    Valida todo antes de programar: un error de tipeo no debe dejar la demo sin falla.
    """
    programadas = []
    for parte in texto.split(","):
        coincidencia = re.fullmatch(r"\s*([a-z_]+):(\d+)\s*", parte)
        if not coincidencia or coincidencia.group(1) not in HERRAMIENTAS_CON_FALLAS:
            raise ValueError(
                "BANCO_FALLAS_TRANSITORIAS debe tener el formato herramienta:N[,herramienta:N] "
                f"con herramientas de {HERRAMIENTAS_CON_FALLAS} (recibido: {texto!r})"
            )
        programadas.append((coincidencia.group(1), int(coincidencia.group(2))))
    for herramienta, n in programadas:
        core.programar_fallas(herramienta, n)


def aplicar_configuracion_del_entorno() -> None:
    configuracion = os.environ.get("BANCO_FALLAS_TRANSITORIAS")
    if configuracion:
        configurar_fallas(configuracion)


def _ejecutar(operacion, *args, **kwargs) -> dict:
    try:
        return operacion(*args, **kwargs)
    except ErrorCore as error:
        raise ToolError(error.a_json()) from None


@mcp.tool(description=DESCRIPCION_BUSCAR)
def buscar_cliente(criterio: str, tipo: Literal["documento", "nombre", "ultimos4"]) -> dict:
    return _ejecutar(core.buscar_cliente, criterio, tipo)


@mcp.tool(description=DESCRIPCION_VERIFICAR)
def verificar_identidad(id_cliente: str, fecha_nacimiento: str) -> dict:
    return _ejecutar(core.verificar_identidad, id_cliente, fecha_nacimiento)


@mcp.tool(description=DESCRIPCION_CONSULTAR)
def consultar_transacciones(
    id_cliente: str, ultimos4: str, desde: str | None = None, hasta: str | None = None
) -> dict:
    return _ejecutar(ops.consultar_transacciones, id_cliente, ultimos4, desde, hasta)


@mcp.tool(description=DESCRIPCION_DISPUTAR)
def iniciar_disputa(id_cliente: str, id_transaccion: str, motivo: str) -> dict:
    return _ejecutar(ops.iniciar_disputa, id_cliente, id_transaccion, motivo)


@mcp.tool(description=DESCRIPCION_BLOQUEAR)
def bloquear_tarjeta(id_cliente: str, ultimos4: str, motivo: str) -> dict:
    return _ejecutar(ops.bloquear_tarjeta, id_cliente, ultimos4, motivo)


@mcp.tool(description=DESCRIPCION_ESCALAR)
def escalar_a_analista(
    causa: Literal[
        "CLIENTE_PIDE_PERSONA",
        "MONTO_SUPERA_UMBRAL",
        "POLITICA_NO_CUBRE",
        "IDENTIDAD_BLOQUEADA",
        "OTRO",
    ],
    descripcion: str,
    accion_recomendada: str,
    id_cliente: str | None = None,
    id_transacciones: list[str] | None = None,
    acciones_realizadas: list[str] | None = None,
) -> dict:
    return _ejecutar(
        ops.escalar_a_analista,
        causa,
        descripcion,
        accion_recomendada,
        id_cliente=id_cliente,
        id_transacciones=id_transacciones,
        acciones_realizadas=acciones_realizadas,
    )


def main() -> None:
    aplicar_configuracion_del_entorno()
    mcp.run()
