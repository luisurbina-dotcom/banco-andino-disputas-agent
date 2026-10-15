"""Detector de datos con forma real (tarjetas y documentos de identidad).

Módulo puro, sin dependencias de Claude Code: lo usan el hook datos_ficticios y el plugin
banca-guardrails (issue #10). Reglas en specs/002-hooks-desarrollo/data-model.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SUGERENCIA_TARJETA = 'usa solo los últimos 4 dígitos, p. ej. "terminada en 4821"'
SUGERENCIA_DOCUMENTO = "usa el formato ficticio FIC-<dígitos>"

# Tarjeta sin separadores: 13 a 19 dígitos seguidos, no pegados a letras ni dígitos.
_CONTIGUA = re.compile(r"(?<![\w])\d{13,19}(?![\w])")

# Tarjeta agrupada: un primer grupo de 4 dígitos y luego grupos de 3 a 6 separados por espacio o
# guion (4-4-4-4, 4-6-5, 4-4-4-4-3). Puede arrastrar dígitos vecinos (CVV, "-01"); por eso se
# prueba Luhn en cada prefijo que termina en un límite de grupo (ver `_tarjetas_agrupadas`).
_AGRUPADA = re.compile(r"(?<![\w])\d{4}(?:[ -]\d{3,6}){1,4}")

# Etiqueta de documento + separadores opcionales + número de 6 a 10 dígitos (admite puntos de
# miles). Un número precedido por "FIC-" no coincide porque el patrón exige un dígito.
_DOCUMENTO = re.compile(
    r"(?<![\w])(?:c[eé]dula(?:\s+de\s+ciudadan[ií]a)?|c\.?\s?c\.?|documento|nit|pasaporte)"
    r"(?![a-záéíóú])"
    r"[\s:#.]*(?:no\.?|nro\.?|n\.?\s?[°º])?[\s:#.]*"
    r"(\d{1,3}(?:\.\d{3}){1,3}|\d{6,10})(?!\d|\.\d)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Deteccion:
    tipo: str  # "tarjeta" | "documento"
    inicio: int
    sugerencia: str


def luhn_valido(digitos: str) -> bool:
    """True si la cadena de dígitos pasa el algoritmo de Luhn."""
    if not digitos.isdigit():
        return False
    suma = 0
    for i, c in enumerate(reversed(digitos)):
        d = int(c)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        suma += d
    return suma % 10 == 0


def _tarjetas_agrupadas(texto: str) -> list[int]:
    """Inicios de tarjetas agrupadas: algún prefijo de 13 a 19 dígitos que pasa Luhn."""
    inicios = []
    for m in _AGRUPADA.finditer(texto):
        acumulado = ""
        for grupo in re.split(r"[ -]", m.group()):
            acumulado += grupo
            if 13 <= len(acumulado) <= 19 and luhn_valido(acumulado):
                inicios.append(m.start())
                break
    return inicios


def detectar(texto: str) -> list[Deteccion]:
    """Devuelve las detecciones en `texto`, sin guardar nunca el valor detectado."""
    inicios = {m.start() for m in _CONTIGUA.finditer(texto) if luhn_valido(m.group())}
    inicios.update(_tarjetas_agrupadas(texto))
    detecciones = [Deteccion("tarjeta", i, SUGERENCIA_TARJETA) for i in sorted(inicios)]
    for m in _DOCUMENTO.finditer(texto):
        if 6 <= len(m.group(1).replace(".", "")) <= 10:
            detecciones.append(Deteccion("documento", m.start(), SUGERENCIA_DOCUMENTO))
    return detecciones
