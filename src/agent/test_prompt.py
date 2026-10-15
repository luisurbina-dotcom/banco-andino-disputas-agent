import re

from agent.prompt import PROMPT_SISTEMA


def test_regla3_bloqueo_inmediato_sin_confirmacion():
    assert "bloquear_tarjeta" in PROMPT_SISTEMA
    assert "sin pedir confirmación" in PROMPT_SISTEMA


def test_regla4_persona_escala_sin_investigar():
    assert "CLIENTE_PIDE_PERSONA" in PROMPT_SISTEMA
    assert "sin buscar ni consultar" in PROMPT_SISTEMA


def test_regla5_y_umbral_escalan():
    for codigo in ("POLITICA_NO_CUBRE", "MONTO_SUPERA_UMBRAL"):
        assert codigo in PROMPT_SISTEMA
    assert "escalar_a_analista" in PROMPT_SISTEMA


def test_ambiguedad_pide_otro_identificador():
    assert "otro identificador" in PROMPT_SISTEMA
    assert "nunca elijas" in PROMPT_SISTEMA


def test_reintenta_errores_transitorios():
    assert "TRANSITORIO" in PROMPT_SISTEMA
    assert "reintenta" in PROMPT_SISTEMA


def test_respuesta_unificada():
    assert "una sola respuesta" in PROMPT_SISTEMA


def test_no_contiene_datos_con_forma_real():
    assert not re.search(r"\d{8,}", PROMPT_SISTEMA)


def test_regla5_general_y_fraude_sin_verificar():
    assert "si la política no cubre el caso" in PROMPT_SISTEMA.lower()
    assert "verifica primero" in PROMPT_SISTEMA
