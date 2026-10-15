"""Carga de los datos ficticios del core desde `data/`.

Las transacciones guardan `dias_atras` en lugar de una fecha fija: se resuelven contra la fecha
base (argumento, variable `BANCO_FECHA_BASE` o el día actual) para que "los cobros de ayer" del
escenario lo sigan siendo el día de la demo y los tests sean reproducibles.
"""

import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

DIRECTORIO_DATOS = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class Datos:
    fecha_base: date
    clientes: list[dict]
    tarjetas: list[dict]
    transacciones: list[dict]


def _fecha_base(fecha_base: date | None) -> date:
    if fecha_base is not None:
        return fecha_base
    desde_entorno = os.environ.get("BANCO_FECHA_BASE")
    return date.fromisoformat(desde_entorno) if desde_entorno else date.today()


def _leer(directorio: Path, nombre: str) -> list[dict]:
    return json.loads((directorio / nombre).read_text(encoding="utf-8"))


def cargar(directorio: Path | None = None, fecha_base: date | None = None) -> Datos:
    directorio = directorio or DIRECTORIO_DATOS
    base = _fecha_base(fecha_base)
    transacciones = [
        {**tx, "fecha": base - timedelta(days=tx["dias_atras"])}
        for tx in _leer(directorio, "transacciones.json")
    ]
    return Datos(
        fecha_base=base,
        clientes=_leer(directorio, "clientes.json"),
        tarjetas=_leer(directorio, "tarjetas.json"),
        transacciones=transacciones,
    )
