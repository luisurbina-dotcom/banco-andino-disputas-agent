import json
import re
import shutil
from datetime import date

import pytest

from mcp_server.datos import DIRECTORIO_DATOS, cargar

BASE = date(2026, 10, 15)


def test_las_fechas_se_resuelven_contra_la_fecha_base():
    datos = cargar(fecha_base=BASE)
    tarjeta = next(t for t in datos.tarjetas if t["ultimos4"] == "4821")
    cobros = [tx for tx in datos.transacciones if tx["id_tarjeta"] == tarjeta["id_tarjeta"]]
    de_ayer = sorted(tx["monto"] for tx in cobros if tx["fecha"] == date(2026, 10, 14))
    assert de_ayer == [180_000, 1_250_000]


def test_la_fecha_base_puede_venir_del_entorno(monkeypatch):
    monkeypatch.setenv("BANCO_FECHA_BASE", "2026-01-31")
    datos = cargar()
    assert datos.fecha_base == date(2026, 1, 31)


def test_sin_fecha_base_se_usa_el_dia_actual(monkeypatch):
    monkeypatch.delenv("BANCO_FECHA_BASE", raising=False)
    assert cargar().fecha_base == date.today()


def test_hay_un_cobro_extranjero_de_mas_de_90_dias():
    datos = cargar(fecha_base=BASE)
    assert any(tx["pais"] != "CO" and (BASE - tx["fecha"]).days > 90 for tx in datos.transacciones)


def test_hay_cobros_disputables_de_bajo_monto():
    datos = cargar(fecha_base=BASE)
    assert sum(1 for tx in datos.transacciones if tx["monto"] <= 500_000) >= 3


def test_los_datos_son_ficticios():
    datos = cargar(fecha_base=BASE)
    assert all(re.fullmatch(r"FIC-\d{8}", c["documento"]) for c in datos.clientes)
    assert all(re.fullmatch(r"\d{4}", t["ultimos4"]) for t in datos.tarjetas)


def test_las_referencias_entre_archivos_son_validas():
    datos = cargar(fecha_base=BASE)
    clientes = {c["id_cliente"] for c in datos.clientes}
    tarjetas = {t["id_tarjeta"] for t in datos.tarjetas}
    assert all(t["id_cliente"] in clientes for t in datos.tarjetas)
    assert all(tx["id_tarjeta"] in tarjetas for tx in datos.transacciones)


def test_casos_de_ambiguedad_presentes():
    datos = cargar(fecha_base=BASE)
    nombres = [c["nombre"] for c in datos.clientes]
    assert nombres.count("Carlos Ramírez") == 2
    por_ultimos4: dict[str, set[str]] = {}
    for t in datos.tarjetas:
        por_ultimos4.setdefault(t["ultimos4"], set()).add(t["id_cliente"])
    assert any(len(titulares) > 1 for titulares in por_ultimos4.values())


@pytest.mark.parametrize("valor", ["15/10/2026", "20261015", "2026-W42-4"])
def test_fecha_base_mal_formada_da_un_mensaje_claro(monkeypatch, valor):
    monkeypatch.setenv("BANCO_FECHA_BASE", valor)
    with pytest.raises(ValueError, match="BANCO_FECHA_BASE"):
        cargar()


def test_el_directorio_de_datos_puede_venir_del_entorno(monkeypatch, tmp_path):
    for nombre in ("tarjetas.json", "transacciones.json"):
        shutil.copy(DIRECTORIO_DATOS / nombre, tmp_path / nombre)
    clientes = json.loads((DIRECTORIO_DATOS / "clientes.json").read_text(encoding="utf-8"))
    (tmp_path / "clientes.json").write_text(json.dumps(clientes[:1]), encoding="utf-8")
    monkeypatch.setenv("BANCO_DATOS_DIR", str(tmp_path))
    assert len(cargar(fecha_base=BASE).clientes) == 1
