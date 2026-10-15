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


@dataclass
class Evento:
    herramienta: str
    argumentos: dict
    resultado: str  # "ok" | "error" | "negado"
    detalle: object = None


@dataclass
class EstadoSesion:
    transacciones: dict[str, dict]
    verificado: str | None = None
    eventos: list[Evento] = field(default_factory=list)

    @classmethod
    def desde_core(cls, fecha_base: date | None = None) -> "EstadoSesion":
        """Lee los datos del core en solo lectura, con la misma fecha base que el servidor."""
        datos = cargar(fecha_base=fecha_base)
        return cls(transacciones={tx["id_transaccion"]: tx for tx in datos.transacciones})


def _nombre(entrada: dict) -> str:
    return str(entrada.get("tool_name", "")).removeprefix(PREFIJO)


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
    if nombre == "iniciar_disputa":
        transaccion = estado.transacciones.get(argumentos.get("id_transaccion"))
        if transaccion is None:
            return MOTIVO_TX_DESCONOCIDA
        if int(transaccion["monto"]) > UMBRAL_DISPUTA:  # monto del core, nunca del modelo
            return MOTIVO_REGLA_2
    return None


def pre_reglas(estado: EstadoSesion):
    async def hook(entrada: dict, tool_use_id, contexto) -> dict:
        nombre = _nombre(entrada)
        argumentos = entrada.get("tool_input") or {}
        try:
            motivo = _motivo_de_negacion(estado, nombre, argumentos)
        except Exception:  # fail-closed: un error interno nunca abre el paso
            motivo = MOTIVO_FALLO
        if motivo is None:
            return {}
        estado.eventos.append(Evento(nombre, argumentos, "negado", motivo))
        return _negar(motivo)

    return hook


def post_resultado(estado: EstadoSesion):
    async def hook(entrada: dict, tool_use_id, contexto) -> dict:
        nombre = _nombre(entrada)
        argumentos = entrada.get("tool_input") or {}
        try:
            if entrada.get("hook_event_name") == "PostToolUseFailure":
                error = (_interpretar(entrada.get("error")) or {}).get("error") or {}
                detalle = {"tipo": error.get("tipo"), "codigo": error.get("codigo")}
                estado.eventos.append(Evento(nombre, argumentos, "error", detalle))
                if detalle["codigo"] == "IDENTIDAD_BLOQUEADA":
                    estado.verificado = None
                return {}
            datos = _interpretar(entrada.get("tool_response"))
            estado.eventos.append(Evento(nombre, argumentos, "ok", datos))
            if (
                nombre == "verificar_identidad"
                and isinstance(datos, dict)
                and datos.get("verificado") is True
                and datos.get("id_cliente") == argumentos.get("id_cliente")
            ):
                estado.verificado = argumentos["id_cliente"]
        except Exception:  # fail-closed: ante la duda, no se marca la sesión como verificada
            pass
        return {}

    return hook
