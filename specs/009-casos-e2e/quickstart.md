# Quickstart: casos end-to-end

Requisito: Claude Code instalado y autenticado (el agente usa su sesión). Alternativa:
`ANTHROPIC_API_KEY` en el entorno.

```bash
uv run pytest -m e2e -v                       # los seis casos (C1–C6, contracts/casos.md)
uv run pytest -m e2e -v -k persona            # un caso
uv run pytest -q                              # unitarios: no corren los e2e
```

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| Q1 | `uv run pytest -q` | Unitarios en verde, incluidos los de las verificaciones; 0 casos e2e ejecutados | FR-007, SC-005 |
| Q2 | `uv run pytest -m e2e -v` | 6 casos en verde en < 15 min | SC-001, SC-003 |
| Q3 | Repetir Q2 | 6 casos en verde otra vez | SC-004 |
| Q4 | Caso que falla (forzado en local) | Se ve la secuencia de eventos del caso | FR-009 |
| Q5 | Sin Claude Code disponible (simulado) | Casos omitidos con motivo, sin traza | FR-008 |

## Resultados (2026-10-15)

| # | Resultado |
|---|---|
| Q1 | ✅ `uv run pytest -q`: 391 en verde (incluye 5 tests de las verificaciones y la omisión), 6 e2e deseleccionados |
| Q2 | ✅ 6/6 en 2 min 40 s (C1 68 s, C6 32 s, C5 17 s, C3 17 s, C2 13 s, C4 9 s) |
| Q3 | ✅ 6/6 en 3 min 01 s |
| Q4 | ✅ Con `BANCO_FALLAS_TRANSITORIAS=escalar_a_analista:5`, C2 falla con "Regla 4: debía escalar con causa CLIENTE_PIDE_PERSONA" y la salida capturada muestra los dos intentos `[error] escalar_a_analista` |
| Q5 | ✅ Cubierto por `test_sin_agente_disponible_el_caso_se_omite` |

Caminos observados (primera ejecución):

- **C1:** busca por 4821 → verifica CLI-001 → bloquea → delega en el analista (consulta del subagente) → disputa TX-0001 → escala TX-0002 por `MONTO_SUPERA_UMBRAL`.
- **C2:** su única acción es `escalar_a_analista` (`CLIENTE_PIDE_PERSONA`).
- **C3:** turno 1 solo `buscar_cliente` (2 coincidencias) y pide otro dato. Turno 2: busca por documento → verifica CLI-003.
- **C4:** sin acciones del banco; pide verificar la identidad (no intentó la disputa).
- **C5:** verifica → consulta con error `TRANSITORIO` → reintenta con éxito.
- **C6:** verifica → delega → escala TX-0010 por `POLITICA_NO_CUBRE` sin intentar la disputa.
