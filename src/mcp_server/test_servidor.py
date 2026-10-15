import json
import re
from pathlib import Path

import pytest
from fastmcp import Client

from mcp_server import servidor
from mcp_server.core import Core

CONTRATO = (
    Path(__file__).resolve().parents[2]
    / "specs/004-core-bancario-identidad/contracts/herramientas.md"
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def cliente(monkeypatch, datos):
    # Un Core nuevo por test: el contador de intentos no se comparte entre tests.
    monkeypatch.setattr(servidor, "core", Core(datos))
    async with Client(servidor.mcp) as c:
        yield c


def _descripcion_del_contrato(herramienta: str) -> str:
    seccion = CONTRATO.read_text(encoding="utf-8").split(f"## `{herramienta}`", 1)[1]
    cita = re.search(r"\*\*Descripción\*\*[^\n]*\n\n((?:> [^\n]*\n)+)", seccion).group(1)
    return " ".join(linea[2:].strip() for linea in cita.splitlines())


async def _herramientas(cliente):
    return {t.name: t for t in await cliente.list_tools()}


async def test_expone_solo_las_herramientas_de_identificacion(cliente):
    assert set(await _herramientas(cliente)) == {"buscar_cliente", "verificar_identidad"}


@pytest.mark.parametrize("nombre", ["buscar_cliente", "verificar_identidad"])
async def test_descripciones_son_exactamente_las_del_contrato(cliente, nombre):
    herramientas = await _herramientas(cliente)
    assert herramientas[nombre].description == _descripcion_del_contrato(nombre)


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


async def test_busqueda_por_mcp_no_expone_datos_sensibles(cliente, titular_4821):
    r = await cliente.call_tool("buscar_cliente", {"criterio": "4821", "tipo": "ultimos4"})
    assert set(r.structured_content["coincidencias"][0]) == {"id_cliente", "nombre", "tarjetas"}
    assert titular_4821["fecha_nacimiento"] not in json.dumps(r.structured_content)


async def test_verificacion_por_mcp_y_bloqueo_como_error(cliente, titular_4821):
    id_cliente = titular_4821["id_cliente"]
    ok = await cliente.call_tool(
        "verificar_identidad",
        {"id_cliente": id_cliente, "fecha_nacimiento": titular_4821["fecha_nacimiento"]},
    )
    assert ok.structured_content["verificado"] is True
    for _ in range(2):
        await cliente.call_tool(
            "verificar_identidad", {"id_cliente": id_cliente, "fecha_nacimiento": "1900-01-01"}
        )
    bloqueo = await cliente.call_tool(
        "verificar_identidad",
        {"id_cliente": id_cliente, "fecha_nacimiento": "1900-01-01"},
        raise_on_error=False,
    )
    assert bloqueo.is_error is True
    assert json.loads(bloqueo.content[0].text)["error"]["codigo"] == "IDENTIDAD_BLOQUEADA"
