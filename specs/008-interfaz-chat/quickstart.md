# Quickstart: interfaz de chat

```bash
uv run pytest -q src/chat
uv run python -m chat                                        # interactivo; /salir para terminar
uv run python -m chat --guion specs/008-interfaz-chat/guiones/ejemplo.txt
BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1 uv run python -m chat --guion <archivo>
```

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| F1 | `python -m chat` y `/salir` | Bienvenida (datos ficticios, cómo salir) y resumen vacío | US1 |
| F2 | Guion de ejemplo (mensaje + fecha) | Turnos diferenciados; 🔒, 📄, ⛔ (regla 2) y 👤 visibles en el turno 2; resumen con 3 acciones + 1 negación | US1, US2, SC-001 |
| F3 | Guion con falla transitoria | 🔁 seguido de 📋 | US3 |
| F4 | Sin Claude Code disponible (simulado en test) | Mensaje claro, sin traza | FR-008 |
