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
check "CLAUDE.md importa la constitución fuera de bloques de código" \
  awk '/^```/{f=!f} $0=="@.specify/memory/constitution.md" && !f {ok=1} END{exit !ok}' CLAUDE.md

echo "US2 · Preferencias personales aisladas"
check "CLAUDE.local.md ignorado por git" git check-ignore -q CLAUDE.local.md
check ".claude/settings.local.json ignorado por git" git check-ignore -q .claude/settings.local.json

echo "US4 · Secretos fuera del alcance"
check ".claude/settings.json es JSON válido" python3 -m json.tool .claude/settings.json
# Cada regla debe estar dentro de permissions.deny (no basta con que aparezca en el archivo).
while read -r regla; do
  check "deny contiene $regla" python3 -c 'import json,sys; sys.exit(sys.argv[1] not in json.load(open(".claude/settings.json"))["permissions"]["deny"])' "$regla"
done <<'REGLAS'
Read(./.env)
Read(./.env.*)
Read(**/.env)
Read(**/.env.*)
Read(!.env.example)
Read(!**/.env.example)
Read(**/.envrc)
Read(**/secrets/**)
Read(**/*.pem)
Read(**/*.key)
Edit(./.env)
Edit(./.env.*)
Edit(**/.env)
Edit(**/.env.*)
Edit(**/.envrc)
Edit(**/secrets/**)
Edit(**/*.pem)
Edit(**/*.key)
REGLAS
check "allow no reabre secretos" python3 -c 'import json,sys; a=json.load(open(".claude/settings.json"))["permissions"].get("allow",[]); sys.exit(any(".env" in r or "secrets" in r for r in a))'
check ".env ignorado por git" git check-ignore -q .env
check ".env.example versionable" bash -c '! git check-ignore -q .env.example'
check ".env.example existe" test -f .env.example
check ".env.example sin valores" bash -c "test -f .env.example && ! grep -vE '^\s*(#|$)' .env.example | grep -qE '=.+'"

echo "US3 · Guías por ruta"
# Frontmatter: primera línea '---', clave paths y los patrones exactos del contrato.
paths_ok() {
  local archivo=$1 fm; shift
  fm=$(awk 'NR==1 && $0!="---"{exit 1} NR>1 && $0=="---"{exit} NR>1' "$archivo") || return 1
  grep -q '^paths:' <<<"$fm" || return 1
  for patron in "$@"; do grep -qF "\"$patron\"" <<<"$fm" || return 1; done
}
check "tests.md: paths **/test_*.py y **/conftest.py" paths_ok .claude/rules/tests.md '**/test_*.py' '**/conftest.py'
check "mcp-tools.md: paths src/mcp_server/**" paths_ok .claude/rules/mcp-tools.md 'src/mcp_server/**'
check "src/agent/CLAUDE.md existe" test -f src/agent/CLAUDE.md

echo
if [ "$errores" -eq 0 ]; then echo "Todo OK"; else echo "$errores comprobación(es) fallaron"; exit 1; fi
