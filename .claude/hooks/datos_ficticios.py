"""PreToolUse (Edit|Write): bloquea contenido con forma de tarjeta o documento real.

Principio III de la constitución · necesidad 5 del ecosistema.
"""

from comun import bloquear, ejecutar_seguro, texto_nuevo
from detector import detectar

HOOK = "datos_ficticios"

MENSAJES = {
    "tarjeta": "Se detectó un número con forma de tarjeta real (pasa Luhn). "
    'Usa solo los últimos 4 dígitos, p. ej. "terminada en 4821".',
    "documento": "Se detectó un número de documento con forma real. "
    "Usa el formato ficticio FIC-<dígitos>.",
}


def revisar(evento: dict) -> None:
    tipos = {d.tipo for d in detectar(texto_nuevo(evento))}
    if tipos:
        bloquear(HOOK, " ".join(MENSAJES[t] for t in sorted(tipos, reverse=True)))


if __name__ == "__main__":
    ejecutar_seguro(HOOK, revisar)
