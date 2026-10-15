"""Garantías de las reglas 1 y 2 como hooks del Claude Agent SDK (principio II).

- `post_resultado` es la única fuente del estado "identidad verificada": lo fija solo cuando
  `verificar_identidad` responde `verificado: true` para el mismo `id_cliente`, y lo retira si la
  identidad queda bloqueada.
- `pre_reglas` niega antes de llegar al servidor: operar sobre productos sin esa verificación
  (regla 1) y disputar más de $500.000 con el monto leído de los datos del core (regla 2).

Las decisiones no dependen del SDK (reciben y devuelven dicts) y fallan de forma segura.
Formatos verificados en vivo: specs/006-agente-hooks-reglas/research.md (R3).
"""

import json
from dataclasses import dataclass, field
from datetime import date

from mcp_server.datos import cargar

PREFIJO = "mcp__banco__"
UMBRAL_DISPUTA = 500_000
PROTEGIDAS = {"consultar_transacciones", "iniciar_disputa", "bloquear_tarjeta"}

MOTIVO_REGLA_1 = (
    "Regla 1: verifica la identidad del cliente con verificar_identidad antes de operar sobre "
    "sus productos."
)
MOTIVO_REGLA_2 = (
    "Regla 2: la transacción supera $500.000; no se inicia automáticamente. Escala el caso con "
    "escalar_a_analista."
)
MOTIVO_TX_DESCONOCIDA = (
    "La transacción no existe en el core; consulta las transacciones del cliente antes de disputar."
)
MOTIVO_FALLO = "Garantía no disponible; la operación se niega por seguridad."
MOTIVO_DELEGACION = "Solo puedes delegar en el subagente analista-transacciones."
MOTIVO_SUBAGENTE = "El analista de transacciones solo puede consultar transacciones."
MOTIVO_HERRAMIENTA_AJENA = "Herramienta no permitida para el agente de disputas."
SUBAGENTE_ANALISTA = "analista-transacciones"
MOTIVO_PRODUCTO_AJENO = (
    "Regla 1: la tarjeta o la transacción no pertenece al cliente verificado en esta conversación."
)


@dataclass
class Evento:
    herramienta: str
    argumentos: dict
    resultado: str  # "ok" | "error" | "negado" | "delegado"
    detalle: object = None
    agente: str = "principal"  # o el agent_type del subagente que hizo la llamada


@dataclass
class EstadoSesion:
    transacciones: dict[str, dict]
    tarjetas: dict[str, dict] = field(default_factory=dict)  # id_tarjeta -> tarjeta del core
    verificado: str | None = None
    eventos: list[Evento] = field(default_factory=list)

    @classmethod
    def desde_core(cls, fecha_base: date | None = None) -> "EstadoSesion":
        """Lee los datos del core en solo lectura, con la misma fecha base que el servidor."""
        datos = cargar(fecha_base=fecha_base)
        return cls(
            transacciones={tx["id_transaccion"]: tx for tx in datos.transacciones},
            tarjetas={t["id_tarjeta"]: t for t in datos.tarjetas},
        )


def _nombre(entrada) -> str:
    if not isinstance(entrada, dict):
        return ""
    return str(entrada.get("tool_name", "")).removeprefix(PREFIJO)


def _agente(entrada) -> str:
    return (entrada.get("agent_type") if isinstance(entrada, dict) else None) or "principal"


def _negar(motivo: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": motivo,
        }
    }


def _interpretar(valor) -> dict | None:
    """Respuesta de herramienta MCP como dict: texto JSON, dict o lista de bloques de texto."""
    if isinstance(valor, dict):
        if isinstance(valor.get("content"), list):
            return _interpretar(valor["content"])
        return valor
    if isinstance(valor, list):
        for bloque in valor:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                return _interpretar(bloque.get("text"))
        return None
    if isinstance(valor, str):
        try:
            datos = json.loads(valor)
        except ValueError:
            return None
        return datos if isinstance(datos, dict) else None
    return None


def _motivo_de_negacion(estado: EstadoSesion, nombre: str, argumentos: dict) -> str | None:
    if nombre not in PROTEGIDAS:
        return None
    if estado.verificado is None or argumentos.get("id_cliente") != estado.verificado:
        return MOTIVO_REGLA_1
    # La pertenencia del producto se decide con los datos del core, no con el argumento.
    if nombre == "iniciar_disputa":
        transaccion = estado.transacciones.get(argumentos.get("id_transaccion"))
        if transaccion is None:
            return MOTIVO_TX_DESCONOCIDA
        tarjeta = estado.tarjetas.get(transaccion["id_tarjeta"])
        if tarjeta is None or tarjeta["id_cliente"] != estado.verificado:
            return MOTIVO_PRODUCTO_AJENO
        monto = transaccion["monto"]
        if not isinstance(monto, int) or isinstance(monto, bool):
            raise TypeError("monto no entero en el core")
        if monto > UMBRAL_DISPUTA:  # monto del core, nunca del modelo
            return MOTIVO_REGLA_2
        return None
    propias = {
        t["ultimos4"] for t in estado.tarjetas.values() if t["id_cliente"] == estado.verificado
    }
    if str(argumentos.get("ultimos4")) not in propias:  # 4821 o "4821": mismo producto
        return MOTIVO_PRODUCTO_AJENO
    return None


def pre_reglas(estado: EstadoSesion):
    async def hook(entrada: dict, tool_use_id, contexto) -> dict:
        agente = "principal"
        try:
            agente = _agente(entrada)
            nombre = _nombre(entrada)
            argumentos = entrada.get("tool_input") or {}
            if agente != "principal" and nombre != "consultar_transacciones":
                motivo = MOTIVO_SUBAGENTE  # un subagente solo consulta (lista permitida)
            else:
                motivo = _motivo_de_negacion(estado, nombre, argumentos)
        except Exception:  # fail-closed: un error interno nunca abre el paso
            nombre, argumentos, motivo = "desconocida", {}, MOTIVO_FALLO
        if motivo is None:
            return {}
        estado.eventos.append(Evento(nombre, argumentos, "negado", motivo, agente))
        return _negar(motivo)

    return hook


def post_resultado(estado: EstadoSesion):
    async def hook(entrada: dict, tool_use_id, contexto) -> dict:
        try:
            agente = _agente(entrada)
            nombre = _nombre(entrada)
            argumentos = entrada.get("tool_input") or {}
            if entrada.get("hook_event_name") == "PostToolUseFailure":
                datos = _interpretar(entrada.get("error"))
            else:
                datos = _interpretar(entrada.get("tool_response"))
            if entrada.get("hook_event_name") == "PostToolUseFailure" or (
                isinstance(datos, dict) and "error" in datos
            ):
                error = (datos or {}).get("error")
                error = error if isinstance(error, dict) else {}
                detalle = {"tipo": error.get("tipo"), "codigo": error.get("codigo")}
                estado.eventos.append(Evento(nombre, argumentos, "error", detalle, agente))
                # Fail-closed: un bloqueo, o un error ilegible de verificar_identidad, retira
                # la verificación (no se confía en interpretar bien el formato del error).
                if detalle["codigo"] == "IDENTIDAD_BLOQUEADA" or (
                    nombre == "verificar_identidad" and detalle["codigo"] is None
                ):
                    estado.verificado = None
                return {}
            estado.eventos.append(Evento(nombre, argumentos, "ok", datos, agente))
            if (
                nombre == "verificar_identidad"
                and isinstance(datos, dict)
                and datos.get("verificado") is True
                and datos.get("id_cliente") == argumentos.get("id_cliente")
            ):
                estado.verificado = argumentos["id_cliente"]
        except Exception:  # fail-closed: ante la duda, la sesión deja de estar verificada
            estado.verificado = None
        return {}

    return hook


def pre_delegacion(estado: EstadoSesion):
    """PreToolUse sobre la herramienta de delegación: solo el analista de transacciones."""

    async def hook(entrada: dict, tool_use_id, contexto) -> dict:
        try:
            argumentos = entrada.get("tool_input") or {}
            # Solo el agente principal delega, y solo en el analista (sin delegación anidada).
            permitido = (
                _agente(entrada) == "principal"
                and argumentos.get("subagent_type") == SUBAGENTE_ANALISTA
            )
        except Exception:  # fail-closed
            argumentos, permitido = {}, False
        agente = _agente(entrada)
        if permitido:
            estado.eventos.append(
                Evento(SUBAGENTE_ANALISTA, argumentos, "delegado", argumentos.get("prompt"), agente)
            )
            return {}
        estado.eventos.append(
            Evento(_nombre(entrada) or "Agent", argumentos, "negado", MOTIVO_DELEGACION, agente)
        )
        return _negar(MOTIVO_DELEGACION)

    return hook


def pre_herramientas_permitidas(
    estado: EstadoSesion, permitidas: set[str], solo_subagentes: set[str] = frozenset()
):
    """PreToolUse sin matcher: niega cualquier herramienta fuera de la lista permitida, la llame
    el agente principal o un subagente (defensa si cambia la configuración de herramientas).

    `solo_subagentes`: herramientas internas que solo pasan si las llama un subagente (por
    ejemplo, la devolución de su resultado al agente principal). Sin `agent_type`, se niegan.
    """

    async def hook(entrada: dict, tool_use_id, contexto) -> dict:
        try:
            nombre = entrada.get("tool_name")
            permitido = nombre in permitidas or (
                nombre in solo_subagentes and _agente(entrada) != "principal"
            )
        except Exception:  # fail-closed
            permitido = False
        if permitido:
            return {}
        argumentos = entrada.get("tool_input") if isinstance(entrada, dict) else None
        estado.eventos.append(
            Evento(
                _nombre(entrada) or "desconocida",
                argumentos if isinstance(argumentos, dict) else {},
                "negado",
                MOTIVO_HERRAMIENTA_AJENA,
                _agente(entrada),
            )
        )
        return _negar(MOTIVO_HERRAMIENTA_AJENA)

    return hook
