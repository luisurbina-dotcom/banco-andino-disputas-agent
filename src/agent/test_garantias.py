import json
from dataclasses import replace

import pytest

from agent.garantias import (
    MOTIVO_DELEGACION,
    MOTIVO_FALLO,
    MOTIVO_HERRAMIENTA_AJENA,
    MOTIVO_PRODUCTO_AJENO,
    MOTIVO_REGLA_1,
    MOTIVO_REGLA_2,
    MOTIVO_SUBAGENTE,
    MOTIVO_TX_DESCONOCIDA,
    post_resultado,
    pre_delegacion,
    pre_herramientas_permitidas,
    pre_reglas,
)

pytestmark = pytest.mark.anyio


def entrada_pre(nombre: str, argumentos: dict) -> dict:
    """Entrada de PreToolUse con el formato verificado en vivo (research R3)."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": f"mcp__banco__{nombre}",
        "tool_input": argumentos,
    }


def entrada_post(nombre: str, argumentos: dict, respuesta) -> dict:
    """PostToolUse: el resultado de una herramienta MCP llega como texto JSON."""
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": f"mcp__banco__{nombre}",
        "tool_input": argumentos,
        "tool_response": json.dumps(respuesta) if isinstance(respuesta, dict) else respuesta,
    }


def entrada_falla(nombre: str, argumentos: dict, tipo: str, codigo: str) -> dict:
    """PostToolUseFailure: el JSON del error llega en el campo `error` (sonda 2)."""
    error = {"error": {"tipo": tipo, "codigo": codigo, "reintentable": False, "mensaje": "x"}}
    return {
        "hook_event_name": "PostToolUseFailure",
        "tool_name": f"mcp__banco__{nombre}",
        "tool_input": argumentos,
        "error": json.dumps(error),
    }


VERIFICACION_OK = {"verificado": True, "id_cliente": "CLI-001", "nombre": "Ana María Gómez"}


def _decision(salida: dict) -> tuple[str | None, str | None]:
    especifica = salida.get("hookSpecificOutput", {})
    return especifica.get("permissionDecision"), especifica.get("permissionDecisionReason")


async def _verificar(estado, respuesta=VERIFICACION_OK, id_cliente="CLI-001"):
    args = {"id_cliente": id_cliente, "fecha_nacimiento": "1988-04-12"}
    await post_resultado(estado)(entrada_post("verificar_identidad", args, respuesta), "t", None)


# --- Regla 1 (US2) ---------------------------------------------------------------------------

OPERACIONES = [
    ("consultar_transacciones", {"id_cliente": "CLI-001", "ultimos4": "4821"}),
    ("iniciar_disputa", {"id_cliente": "CLI-001", "id_transaccion": "TX-0001", "motivo": "x"}),
    ("bloquear_tarjeta", {"id_cliente": "CLI-001", "ultimos4": "4821", "motivo": "x"}),
]


@pytest.mark.parametrize(("nombre", "args"), OPERACIONES)
async def test_regla1_sin_verificacion_niega_y_registra(estado, nombre, args):
    salida = await pre_reglas(estado)(entrada_pre(nombre, args), "t", None)
    assert _decision(salida) == ("deny", MOTIVO_REGLA_1)
    assert estado.eventos[-1].resultado == "negado"
    assert estado.eventos[-1].herramienta == nombre


@pytest.mark.parametrize(
    ("nombre", "args"),
    [
        ("buscar_cliente", {"criterio": "4821", "tipo": "ultimos4"}),
        ("verificar_identidad", {"id_cliente": "CLI-001", "fecha_nacimiento": "1988-04-12"}),
        (
            "escalar_a_analista",
            {"causa": "CLIENTE_PIDE_PERSONA", "descripcion": "d", "accion_recomendada": "a"},
        ),
    ],
)
async def test_regla1_no_aplica_a_herramientas_sin_productos(estado, nombre, args):
    salida = await pre_reglas(estado)(entrada_pre(nombre, args), "t", None)
    assert _decision(salida) == (None, None)


async def test_regla1_tras_verificar_permite_ese_cliente_y_niega_otro(estado):
    await _verificar(estado)
    assert estado.verificado == "CLI-001"
    pre = pre_reglas(estado)
    propio = {"id_cliente": "CLI-001", "ultimos4": "4821"}
    ajeno = {"id_cliente": "CLI-002", "ultimos4": "2290"}
    assert (
        _decision(await pre(entrada_pre("consultar_transacciones", propio), "t", None))[0] is None
    )
    assert (
        _decision(await pre(entrada_pre("consultar_transacciones", ajeno), "t", None))[0] == "deny"
    )


async def test_regla1_verificacion_fallida_no_marca(estado):
    await _verificar(
        estado, {"verificado": False, "id_cliente": "CLI-001", "intentos_restantes": 2}
    )
    assert estado.verificado is None


async def test_regla1_verificado_de_otro_cliente_no_marca(estado):
    await _verificar(estado, {**VERIFICACION_OK, "id_cliente": "CLI-002"})
    assert estado.verificado is None


async def test_regla1_bloqueo_por_intentos_retira_la_verificacion(estado):
    await _verificar(estado)
    args = {"id_cliente": "CLI-001", "fecha_nacimiento": "1900-01-01"}
    falla = entrada_falla("verificar_identidad", args, "NEGOCIO", "IDENTIDAD_BLOQUEADA")
    await post_resultado(estado)(falla, "t", None)
    assert estado.verificado is None
    assert estado.eventos[-1].resultado == "error"
    assert estado.eventos[-1].detalle == {"tipo": "NEGOCIO", "codigo": "IDENTIDAD_BLOQUEADA"}


@pytest.mark.parametrize(
    "respuesta",
    [
        VERIFICACION_OK,  # dict ya interpretado
        [{"type": "text", "text": '{"verificado": true, "id_cliente": "CLI-001"}'}],  # bloques
    ],
)
async def test_regla1_interpreta_otras_formas_de_respuesta(estado, respuesta):
    args = {"id_cliente": "CLI-001", "fecha_nacimiento": "1988-04-12"}
    entrada = entrada_post("verificar_identidad", args, "x")
    entrada["tool_response"] = respuesta
    await post_resultado(estado)(entrada, "t", None)
    assert estado.verificado == "CLI-001"


async def test_regla1_respuesta_ilegible_no_marca(estado):
    await _verificar(estado, "esto no es json")
    assert estado.verificado is None


async def test_registra_eventos_ok_con_los_datos(estado):
    await _verificar(estado)
    evento = estado.eventos[-1]
    assert (evento.herramienta, evento.resultado) == ("verificar_identidad", "ok")
    assert evento.detalle["verificado"] is True


# --- Regla 2 (US3) ---------------------------------------------------------------------------


async def _disputar(estado, id_transaccion, **extra):
    args = {"id_cliente": "CLI-001", "id_transaccion": id_transaccion, "motivo": "x", **extra}
    return _decision(await pre_reglas(estado)(entrada_pre("iniciar_disputa", args), "t", None))


async def test_regla2_niega_sobre_el_umbral_aunque_el_modelo_invente_un_monto(estado):
    await _verificar(estado)
    assert await _disputar(estado, "TX-0002", monto=100) == ("deny", MOTIVO_REGLA_2)


async def test_regla2_permite_bajo_el_umbral(estado):
    await _verificar(estado)
    assert (await _disputar(estado, "TX-0001"))[0] is None


async def test_regla2_exactamente_500000_se_permite(estado):
    await _verificar(estado)
    tx = {**estado.transacciones["TX-0001"], "id_transaccion": "TX-L1", "monto": 500_000}
    estado_limite = replace(estado, transacciones={**estado.transacciones, "TX-L1": tx})
    assert (await _disputar(estado_limite, "TX-L1"))[0] is None


async def test_regla2_transaccion_desconocida_se_niega(estado):
    await _verificar(estado)
    assert await _disputar(estado, "TX-9999") == ("deny", MOTIVO_TX_DESCONOCIDA)


async def test_fallo_interno_niega_por_seguridad(estado):
    await _verificar(estado)
    estado.transacciones["TX-0001"] = {"id_tarjeta": "TAR-001", "monto": "no-es-un-numero"}
    assert await _disputar(estado, "TX-0001") == ("deny", MOTIVO_FALLO)


# --- Hallazgos de la revisión independiente (review.md) ---


@pytest.mark.parametrize(
    "error", ["Error: algo salió mal", "<tool_use_error>x</tool_use_error>", None]
)
async def test_falla_ilegible_de_verificar_retira_la_verificacion(estado, error):
    await _verificar(estado)
    entrada = entrada_falla("verificar_identidad", {"id_cliente": "CLI-001"}, "X", "Y")
    entrada["error"] = error
    await post_resultado(estado)(entrada, "t", None)
    assert estado.verificado is None


async def test_error_que_llega_por_post_tool_use_se_trata_como_error(estado):
    await _verificar(estado)
    error = {"error": {"tipo": "NEGOCIO", "codigo": "IDENTIDAD_BLOQUEADA", "reintentable": False}}
    args = {"id_cliente": "CLI-001", "fecha_nacimiento": "1900-01-01"}
    await post_resultado(estado)(entrada_post("verificar_identidad", args, error), "t", None)
    assert estado.verificado is None
    assert estado.eventos[-1].resultado == "error"


async def test_regla1_disputa_de_transaccion_de_otro_cliente_se_niega(estado):
    await _verificar(estado)
    # TX-0006 es de una tarjeta de CLI-004, aunque el id_cliente diga CLI-001.
    assert await _disputar(estado, "TX-0006") == ("deny", MOTIVO_PRODUCTO_AJENO)


@pytest.mark.parametrize("nombre", ["consultar_transacciones", "bloquear_tarjeta"])
async def test_regla1_tarjeta_de_otro_cliente_se_niega(estado, nombre):
    await _verificar(estado)
    args = {"id_cliente": "CLI-001", "ultimos4": "7310", "motivo": "x"}
    salida = await pre_reglas(estado)(entrada_pre(nombre, args), "t", None)
    assert _decision(salida) == ("deny", MOTIVO_PRODUCTO_AJENO)


async def test_entrada_que_no_es_dict_niega_por_seguridad(estado):
    salida = await pre_reglas(estado)(None, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_FALLO)


async def test_monto_no_entero_niega_por_seguridad(estado):
    await _verificar(estado)
    estado.transacciones["TX-0001"] = {**estado.transacciones["TX-0001"], "monto": 500000.9}
    assert await _disputar(estado, "TX-0001") == ("deny", MOTIVO_FALLO)


async def test_bloquear_tarjeta_propia_se_permite(estado):
    await _verificar(estado)
    args = {"id_cliente": "CLI-001", "ultimos4": 4821, "motivo": "x"}  # también como número
    salida = await pre_reglas(estado)(entrada_pre("bloquear_tarjeta", args), "t", None)
    assert _decision(salida) == (None, None)


@pytest.mark.parametrize("id_cliente", ["CLI-004", "CLI-005"])
async def test_ultimos4_compartidos_se_permiten_a_cada_titular(estado, id_cliente):
    respuesta = {"verificado": True, "id_cliente": id_cliente, "nombre": "x"}
    await _verificar(estado, respuesta, id_cliente=id_cliente)
    args = {"id_cliente": id_cliente, "ultimos4": "7310"}
    salida = await pre_reglas(estado)(entrada_pre("consultar_transacciones", args), "t", None)
    assert _decision(salida) == (None, None)


async def test_post_con_entrada_invalida_retira_la_verificacion(estado):
    await _verificar(estado)
    await post_resultado(estado)(None, "t", None)
    assert estado.verificado is None


# --- #7: delegación y subagente ---


def _entrada_agente(subagent_type: str) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Agent",
        "tool_input": {"description": "d", "prompt": "encargo", "subagent_type": subagent_type},
    }


async def test_delegar_en_el_analista_se_permite_y_registra(estado):
    salida = await pre_delegacion(estado)(_entrada_agente("analista-transacciones"), "t", None)
    assert _decision(salida) == (None, None)
    assert estado.eventos[-1].resultado == "delegado"
    assert estado.eventos[-1].detalle == "encargo"


@pytest.mark.parametrize("tipo", ["general-purpose", "Explore", "claude"])
async def test_delegar_en_otro_subagente_se_niega(estado, tipo):
    salida = await pre_delegacion(estado)(_entrada_agente(tipo), "t", None)
    assert _decision(salida) == ("deny", MOTIVO_DELEGACION)


def _del_analista(entrada: dict) -> dict:
    return {**entrada, "agent_id": "a1", "agent_type": "analista-transacciones"}


@pytest.mark.parametrize(
    ("nombre", "args"),
    [
        ("iniciar_disputa", {"id_cliente": "CLI-001", "id_transaccion": "TX-0001", "motivo": "x"}),
        ("buscar_cliente", {"criterio": "4821", "tipo": "ultimos4"}),
        ("escalar_a_analista", {"causa": "OTRO", "descripcion": "d", "accion_recomendada": "a"}),
    ],
)
async def test_el_analista_solo_puede_consultar(estado, nombre, args):
    await _verificar(estado)
    entrada = _del_analista(entrada_pre(nombre, args))
    salida = await pre_reglas(estado)(entrada, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_SUBAGENTE)
    assert estado.eventos[-1].agente == "analista-transacciones"


async def test_la_regla1_alcanza_al_analista(estado):
    entrada = _del_analista(
        entrada_pre("consultar_transacciones", {"id_cliente": "CLI-001", "ultimos4": "4821"})
    )
    salida = await pre_reglas(estado)(entrada, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_REGLA_1)


async def test_eventos_distinguen_al_analista_del_principal(estado):
    await _verificar(estado)
    assert estado.eventos[-1].agente == "principal"
    args = {"id_cliente": "CLI-001", "ultimos4": "4821"}
    entrada = _del_analista(
        entrada_post("consultar_transacciones", args, {"transacciones": [], "total": 0})
    )
    await post_resultado(estado)(entrada, "t", None)
    assert estado.eventos[-1].agente == "analista-transacciones"


@pytest.mark.parametrize(
    "entrada",
    [None, {"tool_name": "Agent", "tool_input": "x"}, {"tool_name": "Task", "tool_input": {}}],
)
async def test_delegacion_fail_closed(estado, entrada):
    salida = await pre_delegacion(estado)(entrada, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_DELEGACION)


async def test_delegacion_negada_registra_herramienta_y_agente(estado):
    entrada = {**_entrada_agente("general-purpose"), "tool_name": "Task", "agent_type": "x"}
    await pre_delegacion(estado)(entrada, "t", None)
    assert (estado.eventos[-1].herramienta, estado.eventos[-1].agente) == ("Task", "x")


async def test_cualquier_subagente_solo_puede_consultar(estado):
    await _verificar(estado)
    args = {"id_cliente": "CLI-001", "id_transaccion": "TX-0001", "motivo": "x"}
    entrada = {**entrada_pre("iniciar_disputa", args), "agent_type": "otro-subagente"}
    salida = await pre_reglas(estado)(entrada, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_SUBAGENTE)


@pytest.mark.parametrize("herramienta", ["Bash", "Read", "WebFetch", "mcp__otro__x", None])
async def test_herramientas_fuera_de_la_lista_se_niegan_y_registran(estado, herramienta):
    hook = pre_herramientas_permitidas(estado, {"mcp__banco__buscar_cliente", "Agent"})
    salida = await hook({"tool_name": herramienta, "tool_input": {}}, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_HERRAMIENTA_AJENA)
    assert estado.eventos[-1].resultado == "negado"


async def test_herramientas_permitidas_pasan(estado):
    hook = pre_herramientas_permitidas(estado, {"mcp__banco__buscar_cliente", "Agent"})
    assert _decision(await hook({"tool_name": "Agent"}, "t", None)) == (None, None)


async def test_un_subagente_no_puede_delegar(estado):
    entrada = {**_entrada_agente("analista-transacciones"), "agent_type": "analista-transacciones"}
    salida = await pre_delegacion(estado)(entrada, "t", None)
    assert _decision(salida) == ("deny", MOTIVO_DELEGACION)
