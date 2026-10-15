"""Detector de datos con forma real (tarjetas y documentos de identidad).

Módulo puro, sin dependencias de Claude Code: lo usan el hook datos_ficticios y el plugin
banca-guardrails (issue #10). Reglas en specs/002-hooks-desarrollo/data-model.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SUGERENCIA_TARJETA = 'usa solo los últimos 4 dígitos, p. ej. "terminada en 4821"'
SUGERENCIA_DOCUMENTO = "usa el formato ficticio FIC-<dígitos>"

# 13 a 19 dígitos, con un espacio o guion opcional entre dígitos, no pegados a letras/dígitos.
_TARJETA = re.compile(r"(?<![\w])\d(?:[ -]?\d){12,18}(?![\w])")

# Etiqueta de documento + separadores opcionales + número de 6 a 10 dígitos (admite puntos de
# miles). Un número precedido por "FIC-" no coincide porque el patrón exige un dígito.
_DOCUMENTO = re.compile(
    r"(?<![\w])(?:c[eé]dula|c\.c\.|cc|documento|nit|pasaporte)(?![a-záéíóú])"
    r"[\s:#]*(?:no\.?|n[°º])?[\s:#]*"
    r"(\d{1,3}(?:\.\d{3}){1,3}|\d{6,10})(?![\d.]\d)",
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


def detectar(texto: str) -> list[Deteccion]:
    """Devuelve las detecciones en `texto`, sin guardar nunca el valor detectado."""
    detecciones: list[Deteccion] = []
    for m in _TARJETA.finditer(texto):
        digitos = re.sub(r"[ -]", "", m.group())
        if 13 <= len(digitos) <= 19 and luhn_valido(digitos):
            detecciones.append(Deteccion("tarjeta", m.start(), SUGERENCIA_TARJETA))
    for m in _DOCUMENTO.finditer(texto):
        if 6 <= len(m.group(1).replace(".", "")) <= 10:
            detecciones.append(Deteccion("documento", m.start(), SUGERENCIA_DOCUMENTO))
    return detecciones
