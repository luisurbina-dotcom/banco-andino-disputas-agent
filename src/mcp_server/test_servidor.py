import json
import re
from pathlib import Path

import pytest
from fastmcp import Client

from mcp_server import servidor
from mcp_server.core import Core
from mcp_server.operaciones import Operaciones

SPECS = Path(__file__).resolve().parents[2] / "specs"
CONTRATOS = {
    "buscar_cliente": SPECS / "004-core-bancario-identidad/contracts/herramientas.md",
    "verificar_identidad": SPECS / "004-core-bancario-identidad/contracts/herramientas.md",
    "consultar_transacciones": SPECS / "005-operaciones-core/contracts/herramientas.md",
    "iniciar_disputa": SPECS / "005-operaciones-core/contracts/herramientas.md",
    "bloquear_tarjeta": SPECS / "005-operaciones-core/contracts/herramientas.md",
    "escalar_a_analista": SPECS / "005-operaciones-core/contracts/herramientas.md",
}

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def cliente(monkeypatch, datos):
    # Un Core nuevo por test: intentos, verificados, disputas y fallas no se comparten.
    core = Core(datos)
    monkeypatch.setattr(servidor, "core", core)
    monkeypatch.setattr(servidor, "ops", Operaciones(core))
    async with Client(servidor.mcp) as c:
        yield c


def _descripcion_del_contrato(herramienta: str) -> str:
    texto = CONTRATOS[herramienta].read_text(encoding="utf-8")
    seccion = texto.split(f"## `{herramienta}`", 1)[1]
    cita = re.search(r"\*\*Descripción\*\*[^\n]*\n\n((?:> [^\n]*\n)+)", seccion).group(1)
    return " ".join(linea[2:].strip() for linea in cita.splitlines())


async def _herramientas(cliente):
    return {t.name: t for t in await cliente.list_tools()}


async def test_expone_exactamente_las_seis_herramientas(cliente):
    assert set(await _herramientas(cliente)) == set(CONTRATOS)


@pytest.mark.parametrize("nombre", sorted(CONTRATOS))
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


async def test_causa_es_un_enum_de_cinco_valores(cliente):
    esquema = (await _herramientas(cliente))["escalar_a_analista"].input_schema
    assert set(esquema["properties"]["causa"]["enum"]) == {
        "CLIENTE_PIDE_PERSONA",
        "MONTO_SUPERA_UMBRAL",
        "POLITICA_NO_CUBRE",
        "IDENTIDAD_BLOQUEADA",
        "OTRO",
    }


async def _verificar_por_mcp(cliente, titular):
    await cliente.call_tool(
        "verificar_identidad",
        {"id_cliente": titular["id_cliente"], "fecha_nacimiento": titular["fecha_nacimiento"]},
    )


async def test_flujo_verificar_consultar_disputar_por_mcp(cliente, titular_4821):
    await _verificar_por_mcp(cliente, titular_4821)
    id_cliente = titular_4821["id_cliente"]
    consulta = await cliente.call_tool(
        "consultar_transacciones",
        {
            "id_cliente": id_cliente,
            "ultimos4": "4821",
            "desde": "2026-10-14",
            "hasta": "2026-10-14",
        },
    )
    assert consulta.structured_content["total"] == 2
    disputa = await cliente.call_tool(
        "iniciar_disputa",
        {"id_cliente": id_cliente, "id_transaccion": "TX-0001", "motivo": "No lo reconozco"},
    )
    assert disputa.structured_content["estado"] == "abierta"
    sobre_umbral = await cliente.call_tool(
        "iniciar_disputa",
        {"id_cliente": id_cliente, "id_transaccion": "TX-0002", "motivo": "No lo reconozco"},
        raise_on_error=False,
    )
    assert sobre_umbral.is_error is True
    error = json.loads(sobre_umbral.content[0].text)["error"]
    assert (error["tipo"], error["codigo"], error["reintentable"]) == (
        "NEGOCIO",
        "MONTO_SUPERA_UMBRAL",
        False,
    )


async def test_falla_transitoria_configurada_por_mcp(cliente, titular_4821):
    await _verificar_por_mcp(cliente, titular_4821)
    servidor.configurar_fallas("consultar_transacciones:1")
    argumentos = {"id_cliente": titular_4821["id_cliente"], "ultimos4": "4821"}
    falla = await cliente.call_tool("consultar_transacciones", argumentos, raise_on_error=False)
    assert falla.is_error is True
    error = json.loads(falla.content[0].text)["error"]
    assert (error["tipo"], error["reintentable"]) == ("TRANSITORIO", True)
    ok = await cliente.call_tool("consultar_transacciones", argumentos)
    assert ok.structured_content["total"] == 3


@pytest.mark.parametrize("texto", ["consultar_transacciones", "x:dos", ":1", "x:-1"])
def test_configuracion_de_fallas_invalida(texto):
    with pytest.raises(ValueError, match="BANCO_FALLAS_TRANSITORIAS"):
        servidor.configurar_fallas(texto)
