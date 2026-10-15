import pytest
from solo_lectura_git import permitido

PERMITIDOS = [
    "git diff main...HEAD",
    "git diff --stat main...HEAD -- specs/",
    "git log --oneline -5",
    "git show HEAD:CLAUDE.md",
    "git status",
    "git ls-files",
    "git rev-parse HEAD",
    "git merge-base main HEAD",
    "git branch --show-current",
    "git --no-pager log -3",
]

BLOQUEADOS = [
    "git checkout -b x",
    "git push",
    "git commit -m x",
    "git diff > cambios.txt",
    "git diff; rm -rf x",
    "git log | sh",
    "git show $(whoami)",
    "git show `whoami`",
    "git diff && touch x",
    "git diff --output=cambios.txt",
    "git branch -D x",
    "git branch",
    "git -c alias.x=!sh x",
    "rm x",
    "python3 x.py",
    "git -C otra/ruta diff",
    "git diff --output cambios.txt",
    "",
]


@pytest.mark.parametrize("comando", PERMITIDOS)
def test_permite_lecturas_de_git(comando):
    assert permitido(comando), comando


@pytest.mark.parametrize("comando", BLOQUEADOS)
def test_bloquea_todo_lo_demas(comando):
    assert not permitido(comando), comando


def test_hook_bloquea_por_stdin(correr_hook):
    r = correr_hook(
        "solo_lectura_git", {"tool_name": "Bash", "tool_input": {"command": "git push"}}
    )
    assert r.returncode == 2
    assert "[solo_lectura_git]" in r.stderr


def test_hook_permite_por_stdin(correr_hook):
    r = correr_hook(
        "solo_lectura_git", {"tool_name": "Bash", "tool_input": {"command": "git status"}}
    )
    assert r.returncode == 0


def test_evento_sin_comando_bloquea_por_seguridad(correr_hook):
    r = correr_hook("solo_lectura_git", {"tool_name": "Bash", "tool_input": None})
    assert r.returncode == 2


def test_comilla_sin_cerrar_bloquea_por_seguridad(correr_hook):
    r = correr_hook(
        "solo_lectura_git", {"tool_name": "Bash", "tool_input": {"command": 'git log "x'}}
    )
    assert r.returncode == 2
