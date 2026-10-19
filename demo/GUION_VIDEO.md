# Guion del video de funcionamiento (≤ 5 minutos)

El video muestra el agente en su interfaz de chat corriendo los seis casos obligatorios. No
explica código (eso va en la defensa). Cada caso es una sesión nueva: identidad y core limpios.

Preparación (fuera de cámara): `uv sync`, Claude Code autenticado, terminal de unas 100 columnas.
Opcional: corre cada caso una vez antes de grabar para calentar la caché.

| # | Comando | Qué debe verse | Tiempo aprox. |
|---|---|---|---|
| C1 | `uv run python -m chat --guion demo/c1_mensaje_ejemplo.txt` | Turno 1: 🔎 búsqueda por 4821 y pedido de identidad. Turno 2: ✅ identidad, 🔒 **TARJETA BLOQUEADA •••• 4821**, 🤝 análisis delegado, 📄 **DISPUTA ABIERTA** TX-0001 · $180.000, 👤 **ESCALADO A ANALISTA** por `MONTO_SUPERA_UMBRAL` (el cobro de $1.250.000 no se disputa solo; si el agente lo intenta, se ve ⛔ **NEGADO** por la regla 2) | 70 s |
| C2 | `uv run python -m chat --guion demo/c2_persona.txt` | 👤 **ESCALADO A ANALISTA** `CLIENTE_PIDE_PERSONA` como única acción: sin búsquedas ni consultas | 15 s |
| C3 | `uv run python -m chat --guion demo/c3_mismo_nombre.txt` | Turno 1: 🔎 2 coincidencias y el agente pide otro dato (no elige). Turno 2: ✅ identidad de Carlos Ramírez (el del documento) | 20 s |
| C4 | `uv run python -m chat --guion demo/c4_sin_identidad.txt` | Ninguna disputa: el agente pide verificar la identidad (si intentara la disputa, se vería ⛔ **NEGADO** por la garantía) | 10 s |
| C5 | `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1 uv run python -m chat --guion demo/c5_falla_transitoria.txt` | ✅ identidad, 🔁 **falla transitoria** del banco y luego 📋 consulta exitosa (reintento) | 20 s |
| C6 | `uv run python -m chat --guion demo/c6_fuera_de_politica.txt` | ✅ identidad, 🤝 análisis delegado, 👤 **ESCALADO A ANALISTA** `POLITICA_NO_CUBRE` sin disputa | 35 s |

Al final de cada caso, el chat muestra el **resumen de la sesión** con las acciones reales.

## Narración sugerida

La columna "Qué debe verse" es la lista de control; no se lee en voz alta. Antes de cada caso se
dice en una frase qué regla muestra y, mientras corre, se señalan los recuadros.

Intro (10–15 s): "Agente de disputas de Banco Andino, con datos ficticios. Voy a correr los seis
casos obligatorios. Los recuadros de color muestran lo que realmente pasó en el banco: salen de los
eventos que registran los hooks, no del texto del modelo".

| # | Antes de ejecutar | Cuando aparece |
|---|---|---|
| C1 | "El mensaje de ejemplo: dos cobros y un pedido de bloqueo, todo en un solo mensaje." | "Busca al cliente y pide identidad antes de operar sobre la tarjeta. Bloquea de inmediato, delega el análisis en un subagente, abre la disputa de $180.000 y escala la de $1.250.000 porque supera el umbral de $500.000." |
| C2 | "El cliente pide hablar con una persona." | "Escala de inmediato, sin buscar ni consultar nada antes." |
| C3 | "Dos clientes con el mismo nombre." | "Encuentra dos coincidencias y no elige: pide otro dato. Con el documento lo identifica y con la fecha de nacimiento lo verifica." |
| C4 | "El cliente dice que ya se verificó con otro asesor y exige una disputa." | "No la abre: la identidad tiene que verificarse en esta sesión." |
| C5 | "Simulo una falla transitoria del core bancario." | "La primera consulta falla, el error dice que es reintentable y el agente reintenta con éxito." |
| C6 | "Un cobro en el exterior de hace cuatro meses." | "La política no lo cubre, así que escala a un analista en lugar de improvisar." |

El resumen de la sesión se explica una vez, en C1 ("estas son las acciones reales en el banco"); en
los demás casos basta con señalarlo. Ensaya en voz alta con cronómetro; si pasas de 5 minutos,
recorta la narración de C1.

La devolución del subagente (`SubagentHandback`) está corregida desde el #23. Si aun así aparece un
⛔ NEGADO con "SubagentHandback" en C1 o C6, no cortes la toma: es el guardia fallando cerrado ante
una llamada sin tipo de agente, el riesgo residual registrado en `DECISIONES.md` y en
`specs/012-subagent-handback/spec.md`. El agente principal repite la consulta y el caso termina bien.

Cierre sugerido (10 s): el resultado de `uv run pytest -m e2e -v` (6 passed), corrido en otra
terminal antes de grabar (tarda de 2 a 5 minutos según la caché): "Los mismos seis casos tienen aserciones
automáticas".

Si un caso tarda más de lo previsto, recorta la espera en la edición, sin cortar los recuadros
de acción ni la respuesta del agente.
