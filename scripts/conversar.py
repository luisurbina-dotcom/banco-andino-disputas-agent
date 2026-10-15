"""Conversación de prueba con el agente: uv run python scripts/conversar.py "msg 1" ["msg 2" …].

Muestra por turno la respuesta, los eventos (herramientas, errores, negaciones de las garantías)
y la razón de parada. La interfaz de chat completa llega en el issue #8.
"""

import asyncio
import json
import sys

from agent.agente import AgenteDisputas


async def main(mensajes: list[str]) -> None:
    async with AgenteDisputas() as agente:
        for numero, mensaje in enumerate(mensajes, start=1):
            turno = await agente.responder(mensaje)
            print(
                f"\n=== Turno {numero} · stop_reason={turno.stop_reason} · {turno.num_turns} pasos"
            )
            print(f"Cliente: {mensaje}")
            for evento in turno.eventos:
                detalle = json.dumps(evento.detalle, ensure_ascii=False, default=str)[:160]
                print(
                    f"  [{evento.resultado:8}] {evento.herramienta} ({evento.agente}) "
                    f"{evento.argumentos} → {detalle}"
                )
            print(f"Agente: {turno.texto}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Uso: uv run python scripts/conversar.py "mensaje" ["mensaje 2" …]')
    asyncio.run(main(sys.argv[1:]))
