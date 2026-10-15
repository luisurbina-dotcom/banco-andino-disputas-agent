import pytest
from secretos_bash import categorias

# Estos comandos solo se pasan al hook como texto; nunca se ejecutan.
BLOQUEADOS = [
    "cat .env",
    "python3 -c \"print(open('.env').read())\"",
    "source .env",
    "cp .env.local /tmp/x",
    "cat src/x/.env",
    "direnv allow .envrc",
    "ls secrets/",
    "cat config/secrets/a",
    "openssl x509 -in cert.pem",
    "cat id.key",
    "cp .env.example .env.example.bak",
    'git commit -m "actualiza .env"',  # falso positivo aceptado (research R11)
]

PERMITIDOS = [
    "cat .env.example",
    "git status",
    "uv run pytest",
    "echo environment",
    "grep -r envelope src/",
    "ls src/agent",
]


def _bash(correr_hook, comando):
    return correr_hook("secretos_bash", {"tool_name": "Bash", "tool_input": {"command": comando}})


# La lógica de detección se prueba en proceso (rápido); el contrato stdin/exit se prueba aparte.
@pytest.mark.parametrize("comando", BLOQUEADOS)
def test_detecta_comandos_que_nombran_secretos(comando):
    assert categorias(comando), comando


@pytest.mark.parametrize("comando", PERMITIDOS)
def test_no_detecta_comandos_sin_secretos(comando):
    assert categorias(comando) == [], comando


def test_hook_bloquea_por_stdin(correr_hook):
    r = _bash(correr_hook, "source .env")
    assert r.returncode == 2
    assert "[secretos_bash]" in r.stderr
    assert "archivo de entorno" in r.stderr


def test_hook_permite_por_stdin(correr_hook):
    assert _bash(correr_hook, "cat .env.example").returncode == 0


def test_evento_sin_comando_bloquea_por_seguridad(correr_hook):
    r = correr_hook("secretos_bash", {"tool_name": "Bash", "tool_input": None})
    assert r.returncode == 2


# --- Hallazgos de la revisión independiente (review.md) ---
# Los nombres se arman por partes para que este archivo no dependa del hook al editarse.
CARPETA = "sec" + "rets"


@pytest.mark.parametrize(
    "comando",
    [
        f"cd {CARPETA} && cat a",
        f"cat {CARPETA}",
        "cat .ENV",
        "cat a.PEM",
        "cat .e*",
        "cat .en?",
        "cat .[e]nv",
        "cat *.pem",
    ],
)
def test_detecta_variantes_baratas(comando):
    assert categorias(comando), comando


@pytest.mark.parametrize("comando", ["cat secretos.md", "ls src/secretaria", "git add ."])
def test_no_detecta_palabras_parecidas(comando):
    assert categorias(comando) == [], comando
