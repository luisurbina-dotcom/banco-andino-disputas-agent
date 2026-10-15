"""Fixtures para probar los hooks como los ejecuta Claude Code: JSON por stdin."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).parent


def tarjeta_valida(prefijo: str, largo: int) -> str:
    """Completa `prefijo` hasta `largo` dígitos con un dígito verificador de Luhn válido.

    Los números que pasan Luhn se construyen en tiempo de ejecución: si fueran literales en
    este archivo, el hook datos_ficticios bloquearía su escritura.
    """
    cuerpo = (prefijo + "0" * largo)[: largo - 1]
    suma = 0
    for i, c in enumerate(reversed(cuerpo)):
        d = int(c)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        suma += d
    return cuerpo + str((10 - suma % 10) % 10)


@pytest.fixture
def correr_hook():
    def _correr(nombre: str, evento, env: dict | None = None, cwd: Path | None = None):
        entrada = evento if isinstance(evento, str) else json.dumps(evento)
        return subprocess.run(
            [sys.executable, str(HOOKS / f"{nombre}.py")],
            input=entrada,
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})},
            cwd=cwd,
        )

    return _correr
