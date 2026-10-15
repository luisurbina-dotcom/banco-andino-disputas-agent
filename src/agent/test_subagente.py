import re

from agent.subagente import NOMBRE, PROMPT_ANALISTA, definicion


def test_definicion_solo_puede_consultar():
    agente = definicion()
    assert NOMBRE == "analista-transacciones"
    assert agente.tools == ["mcp__banco__consultar_transacciones"]
    assert agente.prompt == PROMPT_ANALISTA


def test_prompt_tiene_las_recomendaciones_y_las_reglas():
    for recomendacion in (
        "DISPUTA_AUTOMATICA",
        "ESCALAR_UMBRAL",
        "ESCALAR_POLITICA",
        "PEDIR_DATOS",
    ):
        assert recomendacion in PROMPT_ANALISTA
    assert "$500.000" in PROMPT_ANALISTA
    assert "90 días" in PROMPT_ANALISTA and "prevalece" in PROMPT_ANALISTA
    assert "no tienes herramientas para disputar, bloquear ni escalar" in PROMPT_ANALISTA
    assert "REPORTADO" in PROMPT_ANALISTA  # formato de línea (research R4)


def test_prompt_sin_datos_con_forma_real():
    assert not re.search(r"\d{8,}", PROMPT_ANALISTA)
