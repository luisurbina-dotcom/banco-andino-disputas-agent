import json

import pytest

from mcp_server.errores import ErrorCore


def test_expone_los_campos_del_contrato():
    error = ErrorCore("VALIDACION", "CRITERIO_VACIO", "Indica un criterio de búsqueda.")
    assert (error.tipo, error.codigo, error.reintentable) == ("VALIDACION", "CRITERIO_VACIO", False)
    assert error.mensaje == "Indica un criterio de búsqueda."


def test_a_dict_tiene_exactamente_la_forma_del_contrato():
    error = ErrorCore("TRANSITORIO", "CORE_NO_DISPONIBLE", "Reintenta.", reintentable=True)
    assert error.a_dict() == {
        "error": {
            "tipo": "TRANSITORIO",
            "codigo": "CORE_NO_DISPONIBLE",
            "reintentable": True,
            "mensaje": "Reintenta.",
        }
    }


def test_a_json_es_el_mismo_contrato_serializado():
    error = ErrorCore("NEGOCIO", "IDENTIDAD_BLOQUEADA", "Escala a un analista.")
    assert json.loads(error.a_json()) == error.a_dict()


def test_tipo_desconocido_es_un_error_de_programacion():
    with pytest.raises(ValueError):
        ErrorCore("RARO", "X", "y")
