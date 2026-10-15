# Research: Interfaz de chat

## R1. Tecnología

- **Decision**: Rich (paneles, colores, `Console.status` como indicador de procesamiento) en la
  terminal.
- **Rationale**: ya está en el entorno (dependencia de `fastmcp`), se declara para no depender de
  una transitiva; la terminal se graba sin configurar nada y el enunciado no califica diseño.
- **Alternatives considered**: Streamlit o una web (más piezas y un servidor más para la demo);
  Textual (más complejo para el MVP).

## R2. Indicadores desde eventos

- **Decision**: función pura `desde_eventos(eventos) -> list[Indicador]` con el mapeo:

| Evento | Indicador | Tipo |
|---|---|---|
| `bloquear_tarjeta` ok | 🔒 TARJETA BLOQUEADA · •••• 4821 (o "ya estaba bloqueada") | principal |
| `iniciar_disputa` ok | 📄 DISPUTA ABIERTA · DSP-0001 · TX-0001 · $180.000 | principal |
| `escalar_a_analista` ok | 👤 ESCALADO A ANALISTA · CASO-0001 · causa | principal |
| cualquier `negado` | ⛔ NEGADO · herramienta · motivo de la garantía | principal |
| `buscar_cliente` ok | 🔎 Búsqueda · n coincidencias | secundario |
| `verificar_identidad` ok | ✅ Identidad verificada · nombre / ⚠ Verificación fallida · intentos | secundario |
| `delegado` | 🤝 Análisis delegado a analista-transacciones | secundario |
| `consultar_transacciones` ok | 📋 Consulta de transacciones · n (agente) | secundario |
| error `TRANSITORIO` | 🔁 Falla transitoria del banco · reintentable | secundario |
| otro error | ⚠ El banco rechazó · herramienta · código (sin código ni tipo: ⚠ Error sin detalle) | secundario |
| acción principal ok sin confirmación del banco (`bloqueada is True`, `id_disputa`, `id_caso`) | ❔ Resultado no confirmado · herramienta | secundario |

- **Rationale**: lo que se ve en pantalla sale de lo que realmente ejecutaron el agente, el
  servidor y las garantías; el texto del modelo podría contradecirlo. Una acción principal solo
  se afirma si la respuesta del banco la confirma.
- La **causa** del escalamiento se toma de los argumentos con que el modelo llamó a
  `escalar_a_analista` (el servidor no la devuelve). Es solo informativa: el caso y su
  identificador sí salen de la respuesta del banco.
- Montos en COP con separador de miles por punto (`$1.250.000`).

## R3. Bucle y guion

- **Decision**: `app.conversar(agente, entradas, consola)`, donde `entradas` es un iterador de
  mensajes (teclado o líneas del guion). `/salir` o fin del guion → resumen. `Ctrl+C` → resumen.
  `AgenteNoDisponible` → mensaje claro y código de salida 1.
- **Rationale**: inyectar el agente y las entradas permite probar el bucle sin red.

## R4. Falla transitoria en la demo

- **Decision**: se usa `BANCO_FALLAS_TRANSITORIAS` del #5 (el servidor lo hereda del entorno);
  la interfaz no necesita lógica propia, solo mostrar el indicador 🔁.
