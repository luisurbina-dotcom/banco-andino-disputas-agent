from datetime import date

import pytest

from agent.garantias import EstadoSesion

FECHA_BASE = date(2026, 10, 15)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def estado():
    return EstadoSesion.desde_core(fecha_base=FECHA_BASE)
