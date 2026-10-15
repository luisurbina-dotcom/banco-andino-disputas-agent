"""Lógica del core bancario simulado, sin dependencias de MCP.

`buscar_cliente` localiza candidatos y nunca expone el dato de verificación;
`verificar_identidad` confirma a un único cliente con su fecha de nacimiento y bloquea tras
tres fallos. Contrato: specs/004-core-bancario-identidad/contracts/herramientas.md.
"""

import re
import unicodedata
from datetime import date

from mcp_server.datos import Datos
from mcp_server.errores import ErrorCore

MAX_INTENTOS = 3
TIPOS_BUSQUEDA = ("documento", "nombre", "ultimos4")
ACCION_AMBIGUA = (
    "Hay varias coincidencias: pide otro identificador (documento o últimos 4 dígitos); "
    "no elijas un cliente."
)


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.lower().split())


def _validacion(codigo: str, mensaje: str) -> ErrorCore:
    return ErrorCore("VALIDACION", codigo, mensaje)


def _fecha_aaaa_mm_dd(texto) -> bool:
    """Exactamente AAAA-MM-DD y existente en el calendario (fromisoformat acepta más formatos)."""
    if not isinstance(texto, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return False
    try:
        date.fromisoformat(texto)
    except ValueError:
        return False
    return True


def _identidad_bloqueada() -> ErrorCore:
    return ErrorCore(
        "NEGOCIO",
        "IDENTIDAD_BLOQUEADA",
        "Se agotaron los intentos de verificación. Escala el caso a un analista.",
    )


class Core:
    def __init__(self, datos: Datos):
        self._clientes = {c["id_cliente"]: c for c in datos.clientes}
        self._tarjetas = datos.tarjetas
        self._intentos_fallidos: dict[str, int] = {}
        # Estado compartido con Operaciones (#5), en memoria durante la ejecución del servidor.
        self.datos = datos
        self._verificados: set[str] = set()
        self._fallas: dict[str, int] = {}
        self.disputas: dict[str, dict] = {}
        self.casos: list[dict] = []

    # --- estado compartido ------------------------------------------------------------------

    def cliente(self, id_cliente) -> dict | None:
        return self._clientes.get(id_cliente) if isinstance(id_cliente, str) else None

    def esta_verificado(self, id_cliente: str) -> bool:
        return id_cliente in self._verificados

    def programar_fallas(self, herramienta: str, n: int) -> None:
        """Las próximas `n` llamadas a `herramienta` responderán un error transitorio."""
        if n < 0:
            raise ValueError("el número de fallas no puede ser negativo")
        self._fallas[herramienta] = n

    def consumir_falla(self, herramienta: str) -> None:
        if self._fallas.get(herramienta, 0) > 0:
            self._fallas[herramienta] -= 1
            raise ErrorCore(
                "TRANSITORIO",
                "CORE_NO_DISPONIBLE",
                "El core no respondió a tiempo. Reintenta la operación.",
                reintentable=True,
            )

    # --- búsqueda ---------------------------------------------------------------------------

    def buscar_cliente(self, criterio: str, tipo: str) -> dict:
        criterio = criterio.strip() if isinstance(criterio, str) else ""
        if not criterio:
            raise _validacion("CRITERIO_VACIO", "Indica un documento, nombre o últimos 4 dígitos.")
        if tipo not in TIPOS_BUSQUEDA:
            raise _validacion("TIPO_INVALIDO", "El tipo debe ser documento, nombre o ultimos4.")

        if tipo == "ultimos4":
            if not re.fullmatch(r"\d{4}", criterio):
                raise _validacion(
                    "ULTIMOS4_INVALIDO",
                    "Los últimos dígitos de la tarjeta deben ser exactamente 4 números.",
                )
            ids = {t["id_cliente"] for t in self._tarjetas if t["ultimos4"] == criterio}
        elif tipo == "documento":
            if not re.fullmatch(r"FIC-\d+", criterio.upper()):
                raise _validacion(
                    "DOCUMENTO_INVALIDO", "El documento debe tener el formato FIC-<dígitos>."
                )
            ids = {i for i, c in self._clientes.items() if c["documento"] == criterio.upper()}
        else:
            buscado = _normalizar(criterio)
            if not buscado:  # p. ej. solo emojis o tildes sueltas: no lista a todos
                raise _validacion("CRITERIO_VACIO", "Indica un nombre con letras.")
            palabras = set(buscado.split())
            ids = {
                i
                for i, c in self._clientes.items()
                if _normalizar(c["nombre"]) == buscado
                or palabras <= set(_normalizar(c["nombre"]).split())
            }

        coincidencias = [self._coincidencia(i) for i in sorted(ids)]
        respuesta = {"coincidencias": coincidencias, "total": len(coincidencias)}
        if len(coincidencias) > 1:
            respuesta["accion_sugerida"] = ACCION_AMBIGUA
        return respuesta

    def _coincidencia(self, id_cliente: str) -> dict:
        cliente = self._clientes[id_cliente]
        tarjetas = [t["ultimos4"] for t in self._tarjetas if t["id_cliente"] == id_cliente]
        return {"id_cliente": id_cliente, "nombre": cliente["nombre"], "tarjetas": tarjetas}

    # --- verificación -----------------------------------------------------------------------

    def verificar_identidad(self, id_cliente: str, fecha_nacimiento: str) -> dict:
        cliente = self._clientes.get(id_cliente) if isinstance(id_cliente, str) else None
        if cliente is None:
            raise _validacion(
                "CLIENTE_NO_EXISTE",
                "No existe un cliente con ese identificador. Búscalo primero con buscar_cliente.",
            )
        # El bloqueo va primero: un cliente bloqueado debe escalar, no reintentar la fecha.
        if self._intentos_fallidos.get(id_cliente, 0) >= MAX_INTENTOS:
            raise _identidad_bloqueada()
        if not _fecha_aaaa_mm_dd(fecha_nacimiento):
            raise _validacion(
                "FECHA_INVALIDA", "La fecha de nacimiento debe tener el formato AAAA-MM-DD."
            )

        if fecha_nacimiento == cliente["fecha_nacimiento"]:
            self._intentos_fallidos[id_cliente] = 0
            self._verificados.add(id_cliente)
            return {"verificado": True, "id_cliente": id_cliente, "nombre": cliente["nombre"]}

        fallidos = self._intentos_fallidos.get(id_cliente, 0) + 1
        self._intentos_fallidos[id_cliente] = fallidos
        if fallidos >= MAX_INTENTOS:
            raise _identidad_bloqueada()
        return {
            "verificado": False,
            "id_cliente": id_cliente,
            "intentos_restantes": MAX_INTENTOS - fallidos,
        }
