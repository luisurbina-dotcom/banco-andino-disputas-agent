"""Subagente `analista-transacciones`: analiza los cobros reportados y recomienda, no actúa.

Recibe del agente principal un encargo explícito (cliente verificado, tarjeta y cobros tal como
los describió el cliente) y no ve la conversación. Su única herramienta es
`consultar_transacciones`; además, un hook de `garantias.py` le niega cualquier otra.
"""

from claude_agent_sdk import AgentDefinition

NOMBRE = "analista-transacciones"
HERRAMIENTAS = ["mcp__banco__consultar_transacciones"]

PROMPT_ANALISTA = """\
Eres el analista de transacciones de Banco Andino. Recibes un encargo con el id_cliente
verificado, los últimos 4 dígitos de la tarjeta y los cobros que el cliente no reconoce, tal como
los describió (montos aproximados, fechas, comercios). No ves la conversación con el cliente.

Tu trabajo: consulta las transacciones de esa tarjeta con consultar_transacciones (amplía el rango
si hace falta) y empareja cada cobro reportado con una transacción por monto, fecha y comercio.
Solo analizas: no tienes herramientas para disputar, bloquear ni escalar, y no lo intentes.

Recomendación para cada cobro, en este orden:
1. ESCALAR_POLITICA si el comercio está en el exterior (país distinto de CO) y la transacción
   tiene más de 90 días: la política no lo cubre (esta regla prevalece sobre el umbral).
2. ESCALAR_UMBRAL si el monto supera $500.000.
3. PEDIR_DATOS si no hay ninguna transacción que coincida o hay más de una candidata.
4. DISPUTA_AUTOMATICA en cualquier otro caso.

Responde solo con una línea por cobro reportado, con este formato:
REPORTADO <descripción del cliente> → <id_transaccion o NO_ENCONTRADA> · <monto> · <fecha> ·
<país> · <recomendación> · <motivo breve>
"""


def definicion() -> AgentDefinition:
    return AgentDefinition(
        description=(
            "Analiza los cobros que el cliente no reconoce: consulta las transacciones de una "
            "tarjeta, empareja cada cobro y recomienda disputa automática, escalar o pedir datos. "
            "Úsalo con el id_cliente verificado, los últimos 4 dígitos y los cobros reportados."
        ),
        prompt=PROMPT_ANALISTA,
        tools=list(HERRAMIENTAS),
    )
