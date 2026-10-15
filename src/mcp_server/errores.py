"""Contrato de errores del core (principio V de la constitución).

Todo error que decide el core tiene la forma
`{"error": {"tipo", "codigo", "reintentable", "mensaje"}}`. El servidor MCP lo envía como error
de herramienta para que el modelo sepa que la llamada falló, por qué y si puede reintentar.
"""

import json

TIPOS = ("TRANSITORIO", "VALIDACION", "NEGOCIO", "PERMISOS")


class ErrorCore(Exception):
    def __init__(self, tipo: str, codigo: str, mensaje: str, reintentable: bool = False):
        if tipo not in TIPOS:
            raise ValueError(f"tipo de error desconocido: {tipo}")
        super().__init__(mensaje)
        self.tipo = tipo
        self.codigo = codigo
        self.mensaje = mensaje
        self.reintentable = reintentable

    def a_dict(self) -> dict:
        return {
            "error": {
                "tipo": self.tipo,
                "codigo": self.codigo,
                "reintentable": self.reintentable,
                "mensaje": self.mensaje,
            }
        }

    def a_json(self) -> str:
        return json.dumps(self.a_dict(), ensure_ascii=False)
