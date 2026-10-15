# Quickstart: plugin banca-guardrails

```bash
claude plugin validate plugins/banca-guardrails --strict
claude plugin validate . --strict              # marketplace
uv run pytest -q .claude/hooks/test_plugin.py
bash scripts/verificar_ecosistema.sh
```

Prueba de instalación aislada (directorio temporal ajeno al repo, caché de plugins temporal):
ver `research.md` R7.

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| Q1 | Validar plugin y marketplace con `--strict` | Sin errores ni avisos | FR-001, FR-002, SC-004 |
| Q2 | Tests y verificación del ecosistema | En verde; el test falla si se altera una copia | FR-007, FR-010, SC-005 |
| Q3 | Instalar desde un directorio temporal (`--scope local`) | Instalado y habilitado; piezas listadas | FR-008, US1, SC-001 |
| Q4 | En el temporal, `claude -p` pide escribir un número con forma de tarjeta real | Escritura bloqueada con el mensaje del hook; con datos ficticios procede | US2, SC-002 |
| Q5 | En el temporal (repo con una rama con cambios), invocar la skill | Tabla y veredicto del auditor del plugin | US3, SC-003 |
| Q6 | Seguir el README desde cero | Llega a Q3–Q5 sin leer el código | US5, FR-009 |
| Q7 | Limpieza | `marketplace remove`; temporal borrado; `~/.claude/plugins` intacto | R7 |
