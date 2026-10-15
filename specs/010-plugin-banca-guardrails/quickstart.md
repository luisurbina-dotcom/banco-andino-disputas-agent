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

## Resultados (2026-10-15)

| # | Resultado |
|---|---|
| Q1 | ✅ `claude plugin validate --strict` del plugin y del marketplace: "Validation passed", sin avisos |
| Q2 | ✅ 11 tests de `test_plugin.py` (copias idénticas, reglas compartidas, hook en sitio, solo lectura) y verificación del ecosistema con la nueva sección |
| Q3 | ✅ En un repo git temporal, con `CLAUDE_CODE_PLUGIN_CACHE_DIR` temporal: `marketplace add --scope local` + `install --scope local` → `enabled`; `plugin details`: 1 skill, 1 agente, 1 hook `PreToolUse` |
| Q4 | ✅ `claude -p` pidió escribir un número de 16 dígitos que pasa Luhn (generado al vuelo): archivo no creado, `PreToolUse:Write hook error … [datos_ficticios] Se detectó un número con forma de tarjeta real … This hook comes from the banca-guardrails@…`. Con "terminada en 4821, documento FIC-10000001" el archivo se creó |
| Q5 | ✅ Rama con un agente que aplica la regla 2 solo en el prompt: `/banca-guardrails:revisar-cumplimiento specs/001-disputas` (32 s) usó `banca-guardrails:compliance-auditor`, recibió el diff por inyección (sin denegaciones de permisos), dijo que no había constitución ni `CLAUDE.md` y dio NO CUMPLE en I.2 y II ("la regla solo está en el prompt") con evidencia `agente.py:línea` |
| Q6 | ✅ El README cubre los mismos pasos (instalación, comprobación, desinstalación) |
| Q7 | ✅ `marketplace remove` desinstaló el plugin; `~/.claude/plugins/*.json` sin cambios (md5 antes/después); temporal borrado |
