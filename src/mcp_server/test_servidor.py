import json

import pytest
from fastmcp import Client

from mcp_server import servidor

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def cliente():
    async with Client(servidor.mcp) as c:
        yield c


async def _herramientas(cliente):
    return {t.name: t for t in await cliente.list_tools()}


async def test_expone_solo_las_herramientas_de_identificacion(cliente):
    assert set(await _herramientas(cliente)) == {"buscar_cliente", "verificar_identidad"}


async def test_descripciones_evitan_confundir_las_herramientas(cliente):
    herramientas = await _herramientas(cliente)
    buscar = herramientas["buscar_cliente"].description
    verificar = herramientas["verificar_identidad"].description
    for fragmento in ("NO confirma", "varias coincidencias", "lista vacía"):
        assert fragmento in buscar
    for fragmento in ("UN cliente", "obligatoria", "3 fallos"):
        assert fragmento in verificar


async def test_tipo_es_un_enum_de_tres_valores(cliente):
    esquema = (await _herramientas(cliente))["buscar_cliente"].input_schema
    assert set(esquema["properties"]["tipo"]["enum"]) == {"documento", "nombre", "ultimos4"}


async def test_llamada_valida_devuelve_contenido_estructurado(cliente):
    r = await cliente.call_tool("buscar_cliente", {"criterio": "4821", "tipo": "ultimos4"})
    assert r.is_error is False
    assert r.structured_content["total"] == 1


async def test_error_del_core_sigue_el_contrato(cliente):
    r = await cliente.call_tool(
        "buscar_cliente", {"criterio": "48", "tipo": "ultimos4"}, raise_on_error=False
    )
    assert r.is_error is True
    error = json.loads(r.content[0].text)["error"]
    assert error == {
        "tipo": "VALIDACION",
        "codigo": "ULTIMOS4_INVALIDO",
        "reintentable": False,
        "mensaje": "Los últimos dígitos de la tarjeta deben ser exactamente 4 números.",
    }


async def test_tipo_fuera_del_enum_lo_rechaza_el_esquema(cliente):
    # Fija el comportamiento del protocolo (research R10): no llega al core.
    r = await cliente.call_tool(
        "buscar_cliente", {"criterio": "Ana", "tipo": "telefono"}, raise_on_error=False
    )
    assert r.is_error is True
    assert "TIPO_INVALIDO" not in r.content[0].text
