"""El plugin banca-guardrails no diverge de las piezas de este repo y su hook funciona en sitio.

Fuente de verdad: `.claude/` (specs/010-plugin-banca-guardrails/research.md, R5).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import tarjeta_valida

RAIZ = Path(__file__).resolve().parents[2]
PLUGIN = RAIZ / "plugins" / "banca-guardrails"
HOOKS = RAIZ / ".claude" / "hooks"
INICIO_REGLAS = "<!-- reglas-del-banco:inicio -->"
FIN_REGLAS = "<!-- reglas-del-banco:fin -->"


def _bloque_reglas(ruta: Path) -> str:
    texto = ruta.read_text(encoding="utf-8")
    assert texto.count(INICIO_REGLAS) == 1 and texto.count(FIN_REGLAS) == 1, ruta
    return texto.split(INICIO_REGLAS)[1].split(FIN_REGLAS)[0]


def _frontmatter(ruta: Path) -> str:
    texto = ruta.read_text(encoding="utf-8")
    assert texto.startswith("---\n"), ruta
    return texto.split("---\n")[1]


@pytest.mark.parametrize("script", ["datos_ficticios.py", "detector.py", "comun.py"])
def test_scripts_del_hook_son_copias_identicas(script):
    assert (PLUGIN / "hooks" / script).read_bytes() == (HOOKS / script).read_bytes(), (
        f"El plugin diverge de .claude/hooks/{script}: copia el archivo al plugin"
    )


def test_reglas_del_banco_identicas_en_ambos_auditores():
    assert _bloque_reglas(PLUGIN / "agents" / "compliance-auditor.md") == _bloque_reglas(
        RAIZ / ".claude" / "agents" / "compliance-auditor.md"
    )


def _entrada_datos_ficticios_del_repo() -> tuple[str, dict]:
    config = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
    for grupo in config["hooks"]["PreToolUse"]:
        for hook in grupo["hooks"]:
            if "datos_ficticios.py" in hook["command"]:
                return grupo["matcher"], hook
    raise AssertionError("El repo no registra el hook datos_ficticios")


def test_hooks_json_coincide_con_el_hook_del_repo_y_falla_cerrado():
    config = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    (grupo,) = config["hooks"]["PreToolUse"]
    (hook,) = grupo["hooks"]
    matcher_repo, hook_repo = _entrada_datos_ficticios_del_repo()
    assert set(grupo["matcher"].split("|")) == set(matcher_repo.split("|"))
    assert (hook["timeout"], hook["onFailure"]) == (hook_repo["timeout"], hook_repo["onFailure"])
    assert hook["onFailure"] == "block"
    assert "${CLAUDE_PLUGIN_ROOT}/hooks/datos_ficticios.py" in hook["command"]


def test_skill_y_agente_del_plugin_tratan_el_diff_como_evidencia():
    skill = (PLUGIN / "skills" / "revisar-cumplimiento" / "SKILL.md").read_text(encoding="utf-8")
    agente = (PLUGIN / "agents" / "compliance-auditor.md").read_text(encoding="utf-8")
    lineas = skill.splitlines()
    assert lineas.count("<<<DIFF") == lineas.count("DIFF>>>") == 2
    assert "evidencia, no instrucciones" in skill and "evidencia, no instrucciones" in agente


def test_agente_del_plugin_es_de_solo_lectura_por_construccion():
    fm = _frontmatter(PLUGIN / "agents" / "compliance-auditor.md")
    (linea,) = [linea for linea in fm.splitlines() if linea.startswith("tools:")]
    herramientas = {h.strip() for h in linea.removeprefix("tools:").split(",")}
    assert herramientas == {"Read", "Grep", "Glob"}
    assert "hooks:" not in fm  # en agentes de plugin se ignoraría


def test_skill_del_plugin_usa_el_agente_del_plugin():
    fm = _frontmatter(PLUGIN / "skills" / "revisar-cumplimiento" / "SKILL.md")
    assert "context: fork" in fm
    assert "agent: banca-guardrails:compliance-auditor" in fm


def test_manifiesto_y_marketplace_coinciden():
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    mercado = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    (entrada,) = mercado["plugins"]
    assert entrada["name"] == plugin["name"] == "banca-guardrails"
    assert entrada["source"] == "./plugins/banca-guardrails"
    assert plugin["version"] and plugin["description"] and plugin["author"]["name"]


def _hook_del_plugin(evento: dict) -> subprocess.CompletedProcess:
    # Se ejecuta desde un directorio ajeno, como en el proyecto de otro equipo.
    return subprocess.run(
        [sys.executable, str(PLUGIN / "hooks" / "datos_ficticios.py")],
        input=json.dumps(evento),
        capture_output=True,
        text=True,
        cwd="/",
    )


def test_hook_del_plugin_bloquea_tarjeta_con_forma_real():
    numero = tarjeta_valida("5", 16)
    r = _hook_del_plugin(
        {"tool_name": "Write", "tool_input": {"file_path": "x.md", "content": f"t {numero}"}}
    )
    assert r.returncode == 2 and "últimos 4 dígitos" in r.stderr


def test_hook_del_plugin_permite_datos_ficticios():
    texto = "Tarjeta terminada en 4821, documento FIC-10000001."
    r = _hook_del_plugin(
        {"tool_name": "Write", "tool_input": {"file_path": "x.md", "content": texto}}
    )
    assert r.returncode == 0, r.stderr


def test_hook_del_plugin_falla_cerrado_con_entrada_invalida():
    r = subprocess.run(
        [sys.executable, str(PLUGIN / "hooks" / "datos_ficticios.py")],
        input="no es json",
        capture_output=True,
        text=True,
        cwd="/",
    )
    assert r.returncode == 2


def test_cada_comando_inyectado_esta_autorizado_en_allowed_tools():
    # Si un comando y su autorización divergen, la inyección se deniega y el auditor recibe un
    # diff vacío sin que nada falle.
    skill = (PLUGIN / "skills" / "revisar-cumplimiento" / "SKILL.md").read_text(encoding="utf-8")
    (permitidas,) = [linea for linea in skill.splitlines() if linea.startswith("allowed-tools:")]
    comandos = [linea[2:-1] for linea in skill.splitlines() if linea.startswith("!`")]
    assert len(comandos) == 2
    for comando in comandos:
        assert f"Bash({comando})" in permitidas, comando
