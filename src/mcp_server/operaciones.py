"""Operaciones del core sobre productos del cliente (issue #5).

Comparte el estado del `Core` (verificados, fallas programadas, disputas, casos). Las reglas del
banco se deciden con los datos del core, nunca con valores enviados por el modelo: la disputa no
recibe monto, lo lee por `id_transaccion`. Contrato: specs/005-operaciones-core/contracts/.
"""

import re
from datetime import date, timedelta

from mcp_server.core import Core
from mcp_server.errores import ErrorCore

UMBRAL_DISPUTA = 500_000
DIAS_POLITICA_EXTERIOR = 90
DIAS_CONSULTA_POR_DEFECTO = 30
PAIS_LOCAL = "CO"
CAUSAS_ESCALAMIENTO = (
    "CLIENTE_PIDE_PERSONA",
    "MONTO_SUPERA_UMBRAL",
    "POLITICA_NO_CUBRE",
    "IDENTIDAD_BLOQUEADA",
    "OTRO",
)


def _validacion(codigo: str, mensaje: str) -> ErrorCore:
    return ErrorCore("VALIDACION", codigo, mensaje)


def _negocio(codigo: str, mensaje: str) -> ErrorCore:
    return ErrorCore("NEGOCIO", codigo, mensaje)


def _fecha(texto: str | None, por_defecto: date) -> date:
    if texto is None:
        return por_defecto
    if not isinstance(texto, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        raise ValueError
    return date.fromisoformat(texto)


def _transaccion_publica(tx: dict, fecha_base: date) -> dict:
    return {
        "id_transaccion": tx["id_transaccion"],
        "fecha": tx["fecha"].isoformat(),
        "antiguedad_dias": (fecha_base - tx["fecha"]).days,
        "monto": tx["monto"],
        "comercio": tx["comercio"],
        "pais": tx["pais"],
    }


class Operaciones:
    def __init__(self, core: Core):
        self.core = core

    # --- utilidades ---------------------------------------------------------------------------

    def _exigir_verificado(self, id_cliente) -> None:
        """Defensa en profundidad de la regla 1; la garantía es el hook del agente (#6)."""
        if not (isinstance(id_cliente, str) and self.core.esta_verificado(id_cliente)):
            raise ErrorCore(
                "PERMISOS",
                "IDENTIDAD_NO_VERIFICADA",
                "El cliente no tiene la identidad verificada. Usa verificar_identidad antes de "
                "operar sobre sus productos.",
            )

    def _tarjeta(self, id_cliente: str, ultimos4) -> dict:
        for tarjeta in self.core.datos.tarjetas:
            if tarjeta["id_cliente"] == id_cliente and tarjeta["ultimos4"] == ultimos4:
                return tarjeta
        raise _validacion(
            "TARJETA_NO_ENCONTRADA", "El cliente no tiene una tarjeta con esos últimos 4 dígitos."
        )

    def _transaccion(self, id_transaccion) -> dict | None:
        return next(
            (t for t in self.core.datos.transacciones if t["id_transaccion"] == id_transaccion),
            None,
        )

    # --- herramientas -------------------------------------------------------------------------

    def consultar_transacciones(
        self, id_cliente: str, ultimos4: str, desde: str | None = None, hasta: str | None = None
    ) -> dict:
        self.core.consumir_falla("consultar_transacciones")
        self._exigir_verificado(id_cliente)
        tarjeta = self._tarjeta(id_cliente, ultimos4)
        base = self.core.datos.fecha_base
        try:
            hasta_f = _fecha(hasta, base)
            desde_f = _fecha(desde, hasta_f - timedelta(days=DIAS_CONSULTA_POR_DEFECTO))
        except ValueError:
            raise _validacion(
                "RANGO_INVALIDO", "Las fechas deben tener el formato AAAA-MM-DD."
            ) from None
        if desde_f > hasta_f:
            raise _validacion("RANGO_INVALIDO", "La fecha inicial es posterior a la final.")
        transacciones = [
            _transaccion_publica(tx, base)
            for tx in sorted(self.core.datos.transacciones, key=lambda t: t["fecha"])
            if tx["id_tarjeta"] == tarjeta["id_tarjeta"] and desde_f <= tx["fecha"] <= hasta_f
        ]
        return {
            "fecha_base": base.isoformat(),
            "transacciones": transacciones,
            "total": len(transacciones),
        }

    def iniciar_disputa(self, id_cliente: str, id_transaccion: str, motivo: str) -> dict:
        self.core.consumir_falla("iniciar_disputa")
        self._exigir_verificado(id_cliente)
        tx = self._transaccion(id_transaccion)
        tarjetas_del_cliente = {
            t["id_tarjeta"] for t in self.core.datos.tarjetas if t["id_cliente"] == id_cliente
        }
        if tx is None or tx["id_tarjeta"] not in tarjetas_del_cliente:
            raise _validacion(
                "TRANSACCION_NO_ENCONTRADA",
                "No existe esa transacción en las tarjetas del cliente. "
                "Consulta sus transacciones.",
            )
        if id_transaccion in self.core.disputas:
            raise _negocio("DISPUTA_EXISTENTE", "Esa transacción ya tiene una disputa abierta.")
        antiguedad = (self.core.datos.fecha_base - tx["fecha"]).days
        if tx["pais"] != PAIS_LOCAL and antiguedad > DIAS_POLITICA_EXTERIOR:
            raise _negocio(
                "POLITICA_NO_CUBRE",
                "La política no cubre cobros de comercios en el exterior con más de 90 días. "
                "No la reintentes: escala el caso a un analista.",
            )
        if tx["monto"] > UMBRAL_DISPUTA:  # regla 2 con el monto del core, no del modelo
            raise _negocio(
                "MONTO_SUPERA_UMBRAL",
                "El monto supera $500.000: la disputa requiere un analista. Escala el caso.",
            )
        disputa = {
            "id_disputa": f"DSP-{len(self.core.disputas) + 1:04d}",
            "estado": "abierta",
            "id_transaccion": id_transaccion,
            "monto": tx["monto"],
        }
        self.core.disputas[id_transaccion] = {**disputa, "id_cliente": id_cliente, "motivo": motivo}
        return disputa

    def bloquear_tarjeta(self, id_cliente: str, ultimos4: str, motivo: str) -> dict:
        self.core.consumir_falla("bloquear_tarjeta")
        self._exigir_verificado(id_cliente)
        tarjeta = self._tarjeta(id_cliente, ultimos4)
        ya_estaba = tarjeta["estado"] == "bloqueada"
        tarjeta["estado"] = "bloqueada"
        return {"bloqueada": True, "ultimos4": ultimos4, "ya_estaba_bloqueada": ya_estaba}

    def escalar_a_analista(
        self,
        causa: str,
        descripcion: str,
        accion_recomendada: str,
        id_cliente: str | None = None,
        id_transacciones: list[str] | None = None,
        acciones_realizadas: list[str] | None = None,
    ) -> dict:
        self.core.consumir_falla("escalar_a_analista")
        textos = (descripcion, accion_recomendada)
        if causa not in CAUSAS_ESCALAMIENTO or not all(
            isinstance(t, str) and t.strip() for t in textos
        ):
            raise _validacion(
                "RESUMEN_INCOMPLETO",
                "El caso necesita una causa válida, una descripción y una acción recomendada.",
            )
        if causa in ("MONTO_SUPERA_UMBRAL", "POLITICA_NO_CUBRE") and (
            id_cliente is None or not id_transacciones
        ):
            raise _validacion(
                "RESUMEN_INCOMPLETO",
                "Para escalar por umbral o política indica el cliente y las transacciones "
                "del caso.",
            )
        if id_transacciones and id_cliente is None:
            raise _validacion(
                "RESUMEN_INCOMPLETO", "Indica el cliente al incluir transacciones en el caso."
            )
        cliente = None
        tarjetas_del_cliente: set[str] = set()
        if id_cliente is not None:
            datos_cliente = self.core.cliente(id_cliente)
            if datos_cliente is None:
                raise _validacion(
                    "CLIENTE_NO_EXISTE", "No existe un cliente con ese identificador."
                )
            cliente = {"id_cliente": id_cliente, "nombre": datos_cliente["nombre"]}
            tarjetas_del_cliente = {
                t["id_tarjeta"] for t in self.core.datos.tarjetas if t["id_cliente"] == id_cliente
            }
        transacciones = []
        for id_tx in id_transacciones or []:
            tx = self._transaccion(id_tx)
            if tx is None or tx["id_tarjeta"] not in tarjetas_del_cliente:
                raise _validacion(
                    "TRANSACCION_NO_ENCONTRADA",
                    f"La transacción {id_tx} no pertenece a las tarjetas del cliente.",
                )
            transacciones.append(_transaccion_publica(tx, self.core.datos.fecha_base))
        caso = {
            "id_caso": f"CASO-{len(self.core.casos) + 1:04d}",
            "estado": "en_cola_analista",
            "resumen": {
                "causa": causa,
                "cliente": cliente,
                "transacciones": transacciones,
                "acciones_realizadas": list(acciones_realizadas or []),
                "descripcion": descripcion.strip(),
                "accion_recomendada": accion_recomendada.strip(),
            },
        }
        self.core.casos.append(caso)
        # Al modelo solo vuelve el acuse: el resumen enriquecido es para el analista (no es una
        # vía para leer datos de transacciones sin identidad verificada).
        return {
            "id_caso": caso["id_caso"],
            "estado": caso["estado"],
            "transacciones_incluidas": len(transacciones),
        }
