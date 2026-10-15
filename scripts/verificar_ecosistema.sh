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

echo "003 · Automatización de tickets y revisiones"
fm() { awk 'NR==1 && $0!="---"{exit 1} NR>1 && $0=="---"{exit} NR>1' "$1"; }
fm_tiene() { local archivo=$1; shift; local f; f=$(fm "$archivo") || return 1; for clave in "$@"; do grep -qE "^$clave" <<<"$f" || return 1; done; }
for pieza in .claude/commands/siguiente-ticket.md .claude/commands/abrir-pr.md \
  .claude/skills/sincronizar-ticket/SKILL.md .claude/skills/revisar-cumplimiento/SKILL.md \
  .claude/agents/code-reviewer.md .claude/agents/compliance-auditor.md .mcp.json; do
  check "existe $pieza" test -f "$pieza"
done
for comando in .claude/commands/*.md; do
  check "$(basename "$comando") declara description" fm_tiene "$comando" 'description:'
done
for agente in .claude/agents/code-reviewer.md .claude/agents/compliance-auditor.md; do
  check "$(basename "$agente"): tools sin Write ni Edit" bash -c "grep -E '^tools:' '$agente' | grep -qvE 'Write|Edit'"
  check "$(basename "$agente"): hook solo_lectura_git" grep -q 'solo_lectura_git.py' "$agente"
done
skills_propias=(.claude/skills/sincronizar-ticket/SKILL.md .claude/skills/revisar-cumplimiento/SKILL.md)
for clave in 'context: fork' 'allowed-tools:' 'argument-hint:'; do
  check "skills propias usan '$clave'" bash -c "cat ${skills_propias[*]} | grep -qE '^$clave'"
done
check ".mcp.json es JSON válido" python3 -m json.tool .mcp.json
check ".mcp.json usa \${GITHUB_PAT}" grep -qF '${GITHUB_PAT}' .mcp.json
check ".mcp.json habilita el toolset projects" python3 -c 'import json,sys; t=json.load(open(".mcp.json"))["mcpServers"]["github"]["headers"]["X-MCP-Toolsets"]; sys.exit("projects" not in t.split(","))'
check ".mcp.json sin tokens literales" bash -c "! grep -qE 'gh[pousr]_|github_pat_' .mcp.json"

echo "010 · Plugin banca-guardrails"
check "marketplace.json es JSON válido" python3 -m json.tool .claude-plugin/marketplace.json
check "plugin.json es JSON válido" python3 -m json.tool plugins/banca-guardrails/.claude-plugin/plugin.json
check "hooks.json del plugin es JSON válido" python3 -m json.tool plugins/banca-guardrails/hooks/hooks.json
for pieza in agents/compliance-auditor.md skills/revisar-cumplimiento/SKILL.md README.md; do
  check "plugin: $pieza" test -f "plugins/banca-guardrails/$pieza"
done
if command -v claude >/dev/null 2>&1; then
  check "claude plugin validate --strict (plugin)" claude plugin validate plugins/banca-guardrails --strict
  check "claude plugin validate --strict (marketplace)" claude plugin validate . --strict
else
  ok "claude no disponible: se omite claude plugin validate"
fi

echo
if [ "$errores" -eq 0 ]; then echo "Todo OK"; else echo "$errores comprobación(es) fallaron"; exit 1; fi
