"""Agente de disputas sobre el Claude Agent SDK.

Cada turno: `query(mensaje)` y recorrer `receive_response()` hasta el `ResultMessage`. El SDK
ejecuta las herramientas mientras el modelo las pide y cierra el turno cuando el modelo termina
(`stop_reason`, p. ej. "end_turn"); no hay tope de iteraciones (comportamiento obligatorio 1).
Las reglas 1 y 2 las garantizan los hooks de `garantias.py`. Contrato:
specs/006-agente-hooks-reglas/contracts/agente.md.
"""

import os
import sys
import tempfile
from dataclasses import dataclass, field

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    CLIConnectionError,
    CLINotFoundError,
    HookMatcher,
    ProcessError,
    ResultMessage,
    TextBlock,
)

from agent import subagente
from agent.garantias import (
    EstadoSesion,
    Evento,
    post_resultado,
    pre_delegacion,
    pre_herramientas_permitidas,
    pre_reglas,
)
from agent.prompt import PROMPT_SISTEMA

HERRAMIENTAS = [
    f"mcp__banco__{nombre}"
    for nombre in (
        "buscar_cliente",
        "verificar_identidad",
        "consultar_transacciones",
        "iniciar_disputa",
        "bloquear_tarjeta",
        "escalar_a_analista",
    )
]
MATCHER_BANCO = "mcp__banco__.*"
# Herramientas internas de Claude Code que solo puede usar un subagente: la devolución de su
# resultado al agente principal (no ejecuta acciones del banco).
HERRAMIENTAS_INTERNAS_SUBAGENTE = {"SubagentHandback"}


class AgenteNoDisponible(RuntimeError):
    """El agente no pudo arrancar (CLI de Claude Code ausente o sin autenticación)."""


@dataclass
class Turno:
    texto: str
    eventos: list[Evento] = field(default_factory=list)
    stop_reason: str | None = None
    num_turns: int = 0
    error: bool = False  # el SDK informó un error en el turno (p. ej. autenticación)


def construir_opciones(
    estado: EstadoSesion,
    modelo: str | None = None,
    prompt_sistema: str | None = None,
    cwd: str | None = None,
) -> ClaudeAgentOptions:
    """`prompt_sistema` solo se reemplaza en pruebas (p. ej. un modelo que intenta saltarse las
    reglas): las garantías no dependen del prompt."""
    post = post_resultado(estado)
    return ClaudeAgentOptions(
        system_prompt=prompt_sistema or PROMPT_SISTEMA,
        # Un servidor banco por conversación, con el mismo intérprete del entorno.
        mcp_servers={
            "banco": {"type": "stdio", "command": sys.executable, "args": ["-m", "mcp_server"]}
        },
        # Solo el servidor banco: sin esto se heredan los conectores MCP de la cuenta del
        # desarrollador (p. ej. Drive), comprobado en vivo.
        strict_mcp_config=True,
        allowed_tools=[*HERRAMIENTAS, "Agent"],
        # Solo la herramienta de delegación: ninguna integrada de archivos ni shell.
        tools=["Agent"],
        agents={subagente.NOMBRE: subagente.definicion()},
        setting_sources=[],  # no hereda CLAUDE.md, reglas ni hooks de desarrollo del repo
        cwd=cwd or tempfile.gettempdir(),
        model=modelo or os.environ.get("BANCO_MODELO") or None,
        hooks={
            "PreToolUse": [
                HookMatcher(
                    matcher=None,
                    hooks=[
                        pre_herramientas_permitidas(
                            estado,
                            {*HERRAMIENTAS, "Agent", "Task"},
                            solo_subagentes=HERRAMIENTAS_INTERNAS_SUBAGENTE,
                        )
                    ],
                ),
                HookMatcher(matcher=MATCHER_BANCO, hooks=[pre_reglas(estado)]),
                HookMatcher(matcher="Agent|Task", hooks=[pre_delegacion(estado)]),
            ],
            "PostToolUse": [HookMatcher(matcher=MATCHER_BANCO, hooks=[post])],
            "PostToolUseFailure": [HookMatcher(matcher=MATCHER_BANCO, hooks=[post])],
        },
    )


class AgenteDisputas:
    def __init__(
        self,
        modelo: str | None = None,
        estado: EstadoSesion | None = None,
        fabrica_cliente=ClaudeSDKClient,
        prompt_sistema: str | None = None,
    ):
        self.estado = estado or EstadoSesion.desde_core()
        self._modelo = modelo
        self._prompt = prompt_sistema
        self._directorio = None
        self._fabrica = fabrica_cliente
        self._cliente = None

    async def __aenter__(self) -> "AgenteDisputas":
        # El servidor corre en un directorio temporal: los datos se resuelven con ruta absoluta.
        if os.environ.get("BANCO_DATOS_DIR"):
            os.environ["BANCO_DATOS_DIR"] = os.path.abspath(os.environ["BANCO_DATOS_DIR"])
        self._directorio = tempfile.TemporaryDirectory(prefix="agente-banco-")
        self._cliente = self._fabrica(
            options=construir_opciones(
                self.estado, self._modelo, self._prompt, cwd=self._directorio.name
            )
        )
        try:
            await self._cliente.connect()
        except BaseException as error:
            await self.__aexit__(None, None, None)
            if not isinstance(error, (CLINotFoundError, CLIConnectionError, ProcessError)):
                raise
            raise AgenteNoDisponible(
                "No se pudo iniciar el agente: instala Claude Code y autentícate (o define "
                f"ANTHROPIC_API_KEY en tu entorno). Detalle: {type(error).__name__}"
            ) from error
        return self

    async def __aexit__(self, *exc) -> None:
        try:
            if self._cliente is not None and hasattr(self._cliente, "disconnect"):
                await self._cliente.disconnect()
        finally:
            if self._directorio is not None:
                self._directorio.cleanup()
                self._directorio = None

    async def responder(self, texto: str) -> Turno:
        inicio = len(self.estado.eventos)
        await self._cliente.query(texto)
        ultimo_texto, turno = "", Turno(texto="")
        async for mensaje in self._cliente.receive_response():
            if isinstance(mensaje, AssistantMessage):
                partes = [b.text for b in mensaje.content if isinstance(b, TextBlock)]
                if partes:
                    ultimo_texto = "\n".join(partes)
            elif isinstance(mensaje, ResultMessage):
                turno.texto = mensaje.result or ultimo_texto
                turno.stop_reason = mensaje.stop_reason
                turno.num_turns = mensaje.num_turns
                turno.error = bool(mensaje.is_error)
        turno.texto = turno.texto or ultimo_texto
        turno.eventos = self.estado.eventos[inicio:]
        return turno
