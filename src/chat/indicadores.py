"""Traduce los eventos de un turno a indicadores visibles (sin SDK ni Rich).

Lo que se muestra sale de lo que realmente ejecutaron el agente, el servidor y las garantías
(eventos), nunca del texto del modelo. Mapeo: specs/008-interfaz-chat/research.md (R2).
"""

from collections import Counter
from dataclasses import dataclass

from agent.garantias import Evento

PRINCIPALES = ("TARJETA BLOQUEADA", "DISPUTA ABIERTA", "ESCALADO A ANALISTA", "NEGADO")


@dataclass(frozen=True)
class Indicador:
    principal: bool
    icono: str
    etiqueta: str
    detalle: str
    estilo: str


def formato_monto(monto) -> str:
    try:
        return "$" + f"{int(monto):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(monto)


def _datos(evento: Evento) -> dict:
    return evento.detalle if isinstance(evento.detalle, dict) else {}


def _indicador(evento: Evento) -> Indicador:
    datos = _datos(evento)
    nombre = evento.herramienta

    if evento.resultado == "negado":
        return Indicador(True, "⛔", "NEGADO", f"{nombre} · {evento.detalle}", "bold red")
    if evento.resultado == "delegado":
        return Indicador(
            False, "🤝", "Análisis delegado", f"a {nombre} con el contexto del caso", "cyan"
        )
    if evento.resultado == "error":
        tipo, codigo = datos.get("tipo"), datos.get("codigo")
        if tipo == "TRANSITORIO":
            return Indicador(
                False, "🔁", "Falla transitoria del banco", f"{nombre} · se reintenta", "yellow"
            )
        return Indicador(False, "⚠", "El banco rechazó", f"{nombre} · {codigo or tipo}", "yellow")

    if nombre == "bloquear_tarjeta":
        detalle = f"•••• {datos.get('ultimos4', '?')}"
        if datos.get("ya_estaba_bloqueada"):
            detalle += " (ya estaba bloqueada)"
        return Indicador(True, "🔒", "TARJETA BLOQUEADA", detalle, "bold magenta")
    if nombre == "iniciar_disputa":
        detalle = (
            f"{datos.get('id_disputa', '?')} · {datos.get('id_transaccion', '?')} · "
            f"{formato_monto(datos.get('monto'))}"
        )
        return Indicador(True, "📄", "DISPUTA ABIERTA", detalle, "bold green")
    if nombre == "escalar_a_analista":
        causa = evento.argumentos.get("causa", "?") if isinstance(evento.argumentos, dict) else "?"
        detalle = f"{datos.get('id_caso', '?')} · causa {causa}"
        return Indicador(True, "👤", "ESCALADO A ANALISTA", detalle, "bold blue")
    if nombre == "buscar_cliente":
        total = datos.get("total", 0)
        detalle = f"{total} coincidencia" + ("" if total == 1 else "s")
        return Indicador(False, "🔎", "Búsqueda de cliente", detalle, "dim")
    if nombre == "verificar_identidad":
        if datos.get("verificado") is True:
            return Indicador(
                False, "✅", "Identidad verificada", str(datos.get("nombre", "")), "green"
            )
        restantes = datos.get("intentos_restantes", "?")
        return Indicador(
            False, "⚠", "Verificación fallida", f"intentos restantes: {restantes}", "yellow"
        )
    if nombre == "consultar_transacciones":
        detalle = f"{datos.get('total', 0)} transacciones · por {evento.agente}"
        return Indicador(False, "📋", "Consulta de transacciones", detalle, "dim")
    return Indicador(False, "•", nombre, evento.resultado, "dim")


def desde_eventos(eventos: list[Evento]) -> list[Indicador]:
    return [_indicador(evento) for evento in eventos]


def resumen(indicadores: list[Indicador]) -> dict[str, int]:
    conteo = Counter(i.etiqueta for i in indicadores if i.principal)
    return {etiqueta: conteo[etiqueta] for etiqueta in PRINCIPALES if conteo[etiqueta]}
