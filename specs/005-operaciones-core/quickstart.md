# Quickstart: verificar las operaciones del core

## Tests

```bash
uv run pytest -q src/mcp_server
```

Esperado: verde, sin red, < 5 s.

## Verificación en vivo (sesión nueva `claude -p` con solo `mcp__banco__*`)

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| C1 | Consultar la 4821 de `CLI-001` **sin** verificar | `PERMISOS/IDENTIDAD_NO_VERIFICADA` | FR-008 |
| C2 | Verificar `CLI-001` y consultar su 4821 ayer | 2 transacciones ($180.000 y $1.250.000) | US1 |
| C3 | Disputar el cobro de $180.000 | Disputa abierta | US2 |
| C4 | Disputar el cobro de $1.250.000 | `NEGOCIO/MONTO_SUPERA_UMBRAL` | US2, regla 2 |
| C5 | Bloquear la 4821 dos veces | Bloqueada; la segunda `ya_estaba_bloqueada: true` | US3 |
| C6 | Escalar por `MONTO_SUPERA_UMBRAL` con la transacción de $1.250.000 | Caso en cola con monto y comercio completados por el core | US4 |
| C7 | Escalar `CLIENTE_PIDE_PERSONA` sin cliente | Caso aceptado | FR-007, regla 4 |
| C8 | Verificar `CLI-007` y disputar su cobro en US de hace 120 días | `NEGOCIO/POLITICA_NO_CUBRE` | regla 5 |
| C9 | Arrancar con `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1` y consultar dos veces | 1ª `TRANSITORIO` reintentable; 2ª normal | US5, SC-004 |
