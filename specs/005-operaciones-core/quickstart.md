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
| C6 | Escalar por `MONTO_SUPERA_UMBRAL` con la transacción de $1.250.000 | Caso en cola con `transacciones_incluidas: 1`; el resumen con monto y comercio queda en el core | US4 |
| C7 | Escalar `CLIENTE_PIDE_PERSONA` sin cliente | Caso aceptado | FR-007, regla 4 |
| C8 | Verificar `CLI-007` y disputar su cobro en US de hace 120 días | `NEGOCIO/POLITICA_NO_CUBRE` | regla 5 |
| C9 | Arrancar con `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1` y consultar dos veces | 1ª `TRANSITORIO` reintentable; 2ª normal | US5, SC-004 |

## Resultados (2026-10-15)

- 102 tests en `src/mcp_server` (244 en el repo), ruff limpio, `verificar_ecosistema.sh` OK.
- SC-006: los tests en sí duran < 1 s; la suite tardó 7–12 s porque **importar `fastmcp` tarda
  5–6,5 s** con la carga actual de la máquina WSL (antes ~4 s). Se registra como desviación por
  una dependencia, no por el código.

| # | Resultado (sesión nueva `claude -p`, solo `mcp__banco__*`) |
|---|---|
| C1 | ✅ Sin verificar → `PERMISOS/IDENTIDAD_NO_VERIFICADA`, no reintentable |
| C2 | ✅ Verificado; ayer → 2 transacciones ($180.000 y $1.250.000); por defecto → 3 |
| C3 | ✅ TX-0001 → `DSP-0001` abierta, monto 180000 |
| C4 | ✅ TX-0002 → `NEGOCIO/MONTO_SUPERA_UMBRAL` "Escala el caso" |
| C5 | ✅ Bloqueo y repetición → `ya_estaba_bloqueada` false / true, sin error |
| C6 | ✅ `CASO-0001` con fecha, monto, comercio y país completados por el core desde el id |
| C7 | ✅ `CLIENTE_PIDE_PERSONA` sin cliente → `CASO-0002` aceptado (regla 4) |
| C8 | ✅ CLI-007 verificado; TX-0010 (US, 120 días) → `NEGOCIO/POLITICA_NO_CUBRE` |
| C9 | ✅ Con `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1`: 1ª consulta `TRANSITORIO/CORE_NO_DISPONIBLE` reintentable; el reintento → total 3 |
| C6 (repetido tras `4e305ec`) | ✅ Salida reducida `{"id_caso":"CASO-0001","estado":"en_cola_analista","transacciones_incluidas":1}`; sin `id_cliente` con transacciones → `VALIDACION/RESUMEN_INCOMPLETO` "Indica el cliente al incluir transacciones en el caso." |
