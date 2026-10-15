# Quickstart: entregables

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| Q1 | Clon limpio en un temporal; seguir solo el README (cronometrado) | Tests en verde y primera respuesta del chat en < 5 min | US1, FR-002, SC-001 |
| Q2 | `bash scripts/verificar_ecosistema.sh` | README y DECISIONES presentes; 11 necesidades; ≤ 1.000 palabras | FR-009, SC-002 |
| Q3 | Rutas citadas en README y DECISIONES | Todas existen | FR-004, SC-005 |
| Q4 | `uv run python scripts/empaquetar.py --salida <tmp>/x.zip` | `.zip` con `.git`, sin archivos prohibidos, ≤ 50 MB | US3, FR-005, SC-003 |
| Q5 | Descomprimir el `.zip`, `git log` y tests | Historial intacto; tests en verde | US3 |
| Q6 | Correr los seis guiones de `demo/` en el chat | Indicadores esperados de cada caso | US4, SC-004 |
| Q7 | `uv run pytest -q` | En verde, incluidos los tests del empaquetado | FR-005 |
