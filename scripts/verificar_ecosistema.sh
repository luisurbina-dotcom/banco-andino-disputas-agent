#!/usr/bin/env bash
# Verificación estática del ecosistema de Claude Code (feature 001).
# Uso: bash scripts/verificar_ecosistema.sh   — sale con 1 si alguna comprobación falla.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

errores=0
ok()    { printf '  OK     %s\n' "$1"; }
falla() { printf '  FALLA  %s\n' "$1"; errores=$((errores + 1)); }
check() { local desc=$1; shift; if "$@" >/dev/null 2>&1; then ok "$desc"; else falla "$desc"; fi; }

echo "US1 · Convenciones del equipo"
check "CLAUDE.md existe" test -f CLAUDE.md
lineas=$(wc -l < CLAUDE.md 2>/dev/null || echo 999)
check "CLAUDE.md tiene ≤ 60 líneas ($lineas)" test "$lineas" -le 60
check "CLAUDE.md importa la constitución" grep -qx '@.specify/memory/constitution.md' CLAUDE.md

echo "US2 · Preferencias personales aisladas"
check "CLAUDE.local.md ignorado por git" git check-ignore -q CLAUDE.local.md
check ".claude/settings.local.json ignorado por git" git check-ignore -q .claude/settings.local.json

echo "US4 · Secretos fuera del alcance"
check ".claude/settings.json es JSON válido" python3 -m json.tool .claude/settings.json
for regla in 'Read(./.env)' 'Read(**/.env.*)' 'Read(./secrets/**)' 'Edit(**/.env)' 'Edit(./secrets/**)' 'Read(!.env.example)'; do
  check "deny contiene $regla" grep -qF "\"$regla\"" .claude/settings.json
done
check ".env ignorado por git" git check-ignore -q .env
check ".env.example versionable" bash -c '! git check-ignore -q .env.example'
check ".env.example existe" test -f .env.example
check ".env.example sin valores" bash -c "test -f .env.example && ! grep -vE '^\s*(#|$)' .env.example | grep -qE '=.+'"

echo "US3 · Guías por ruta"
for regla in .claude/rules/tests.md .claude/rules/mcp-tools.md; do
  check "$regla declara paths en el frontmatter" bash -c "sed -n '1,/^---\$/{/^paths:/p}' <(tail -n +2 $regla) | grep -q paths"
done
check "src/agent/CLAUDE.md existe" test -f src/agent/CLAUDE.md

echo
if [ "$errores" -eq 0 ]; then echo "Todo OK"; else echo "$errores comprobación(es) fallaron"; exit 1; fi
