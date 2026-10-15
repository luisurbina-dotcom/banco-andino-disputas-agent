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


def test_delega_el_analisis_con_encargo_explicito():
    texto = " ".join(PROMPT_SISTEMA.split())
    assert "delega en el subagente analista-transacciones" in texto
    assert "el encargo debe incluir el id_cliente verificado, los ultimos4" in texto


def test_actua_segun_la_recomendacion():
    texto = " ".join(PROMPT_SISTEMA.split())
    assert "DISPUTA_AUTOMATICA → iniciar_disputa" in texto
    assert "ESCALAR_UMBRAL o ESCALAR_POLITICA → escalar_a_analista" in texto
    assert "PEDIR_DATOS → pregunta al cliente" in texto


def test_escalar_por_umbral_o_politica_con_cliente_y_transacciones():
    texto = " ".join(PROMPT_SISTEMA.split())
    assert (
        "MONTO_SUPERA_UMBRAL o POLITICA_NO_CUBRE, el id_cliente y los id_transacciones son "
        "obligatorios" in texto
    )
