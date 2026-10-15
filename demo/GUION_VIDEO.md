# Guion del video de funcionamiento (≤ 5 minutos)

El video muestra el agente en su interfaz de chat corriendo los seis casos obligatorios. No
explica código (eso va en la defensa). Cada caso es una sesión nueva: identidad y core limpios.

Preparación (fuera de cámara): `uv sync`, Claude Code autenticado, terminal de unas 100 columnas.
Opcional: corre cada caso una vez antes de grabar para calentar la caché.

| # | Comando | Qué debe verse | Tiempo aprox. |
|---|---|---|---|
| C1 | `uv run python -m chat --guion demo/c1_mensaje_ejemplo.txt` | Turno 1: 🔎 búsqueda por 4821 y pedido de identidad. Turno 2: ✅ identidad, 🔒 **TARJETA BLOQUEADA •••• 4821**, 🤝 análisis delegado, 📄 **DISPUTA ABIERTA** TX-0001 · $180.000, 👤 **ESCALADO** por `MONTO_SUPERA_UMBRAL` (el cobro de $1.250.000 no se disputa solo) | 70 s |
| C2 | `uv run python -m chat --guion demo/c2_persona.txt` | 👤 **ESCALADO** `CLIENTE_PIDE_PERSONA` como única acción: sin búsquedas ni consultas | 15 s |
| C3 | `uv run python -m chat --guion demo/c3_mismo_nombre.txt` | Turno 1: 🔎 2 coincidencias y el agente pide otro dato (no elige). Turno 2: ✅ identidad de Carlos Ramírez (el del documento) | 20 s |
| C4 | `uv run python -m chat --guion demo/c4_sin_identidad.txt` | Ninguna disputa: el agente pide verificar la identidad (si intentara la disputa, se vería ⛔ **NEGADO** por la garantía) | 10 s |
| C5 | `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1 uv run python -m chat --guion demo/c5_falla_transitoria.txt` | ✅ identidad, 🔁 **falla transitoria** del banco y luego 📋 consulta exitosa (reintento) | 20 s |
| C6 | `uv run python -m chat --guion demo/c6_fuera_de_politica.txt` | ✅ identidad, 🤝 análisis delegado, 👤 **ESCALADO** `POLITICA_NO_CUBRE` sin disputa | 35 s |

Al final de cada caso, el chat muestra el **resumen de la sesión** con las acciones reales.

Cierre sugerido (10 s): `uv run pytest -m e2e -v` ya corriendo o su resultado (6 passed), para
mostrar que los mismos casos tienen aserciones automáticas.

Si un caso tarda más de lo previsto, recorta la espera en la edición, sin cortar los recuadros
de acción ni la respuesta del agente.
