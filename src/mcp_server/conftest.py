from datetime import date

import pytest

from mcp_server.core import Core
from mcp_server.datos import cargar

FECHA_BASE = date(2026, 10, 15)


@pytest.fixture
def datos():
    return cargar(fecha_base=FECHA_BASE)


@pytest.fixture
def core(datos):
    return Core(datos)


@pytest.fixture
def titular_4821(datos):
    """Cliente titular de la tarjeta 4821, leído de los datos (no repetido a mano)."""
    tarjeta = next(t for t in datos.tarjetas if t["ultimos4"] == "4821")
    return next(c for c in datos.clientes if c["id_cliente"] == tarjeta["id_cliente"])
