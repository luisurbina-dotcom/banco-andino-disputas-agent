import pytest
from conftest import tarjeta_valida
from detector import detectar, luhn_valido


def _invalida(numero: str) -> str:
    """Mismo número con el dígito verificador alterado: deja de pasar Luhn."""
    return numero[:-1] + str((int(numero[-1]) + 1) % 10)


def _documento(digitos: int, miles: bool = False) -> str:
    """Número con forma de documento construido en tiempo de ejecución."""
    numero = "".join(str((i * 7 + 3) % 10) for i in range(digitos))
    if miles:
        numero = f"{int(numero):,}".replace(",", ".")
    return numero


def test_luhn_valido_con_numeros_generados():
    for largo in (13, 16, 19):
        numero = tarjeta_valida("4", largo)
        assert luhn_valido(numero)
        assert not luhn_valido(_invalida(numero))


@pytest.mark.parametrize("largo", [13, 16, 19])
def test_detecta_tarjeta_valida(largo):
    texto = f"cobro con la tarjeta {tarjeta_valida('5', largo)} ayer"
    detecciones = detectar(texto)
    assert [d.tipo for d in detecciones] == ["tarjeta"]


@pytest.mark.parametrize("separador", [" ", "-"])
def test_detecta_tarjeta_agrupada(separador):
    n = tarjeta_valida("4", 16)
    agrupada = separador.join(n[i : i + 4] for i in range(0, 16, 4))
    assert [d.tipo for d in detectar(f"tarjeta {agrupada}")] == ["tarjeta"]


@pytest.mark.parametrize(
    "texto",
    [
        "tarjeta terminada en 4821",
        "un cobro de $1.250.000 y otro de $180.000",
        "monto 1250000",
        "id de transacción TX-000123",
    ],
)
def test_no_detecta_datos_permitidos(texto):
    assert detectar(texto) == []


def test_no_detecta_numero_que_no_pasa_luhn():
    assert detectar(f"referencia {_invalida(tarjeta_valida('4', 16))}") == []


def test_no_detecta_tarjeta_pegada_a_letras():
    assert detectar("ref" + tarjeta_valida("4", 16) + "x") == []


@pytest.mark.parametrize(
    "etiqueta", ["cédula", "cedula", "CÉDULA", "CC:", "c.c.", "NIT", "Pasaporte No.", "documento"]
)
@pytest.mark.parametrize("miles", [False, True])
def test_detecta_documento_con_etiqueta(etiqueta, miles):
    texto = f"cliente con {etiqueta} {_documento(8, miles)}"
    assert [d.tipo for d in detectar(texto)] == ["documento"]


@pytest.mark.parametrize("digitos", [6, 10])
def test_detecta_documento_en_los_limites(digitos):
    assert [d.tipo for d in detectar(f"NIT {_documento(digitos)}")] == ["documento"]


@pytest.mark.parametrize("texto", ["documento FIC-" + "1" * 8, "cédula: FIC-" + "2" * 8])
def test_no_detecta_formato_ficticio(texto):
    assert detectar(texto) == []


def test_las_detecciones_no_contienen_el_numero():
    numero = tarjeta_valida("4", 16)
    deteccion = detectar(f"tarjeta {numero}")[0]
    assert numero not in repr(deteccion)
    assert numero[-4:] not in deteccion.sugerencia
