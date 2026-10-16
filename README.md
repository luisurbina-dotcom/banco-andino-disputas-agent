# Banco Andino · Agente de disputas

Agente de disputas y contracargos para **Banco Andino**, un banco ficticio. Está construido con el
**Claude Agent SDK** (Python 3.12) y un **servidor MCP propio** que simula el core bancario con
datos ficticios. Lo desarrollé con Claude Code siguiendo Spec Driven Development (Spec Kit), con
el backlog sincronizado en un GitHub Project.

- **GitHub Project:** https://github.com/users/luisurbina-dotcom/projects/1
- **Video de funcionamiento:** _pendiente; el autor lo agrega al publicarlo_
- **Decisiones del ecosistema:** [DECISIONES.md](DECISIONES.md) · **Principios:** [constitución](.specify/memory/constitution.md)

Todos los datos son ficticios: las tarjetas aparecen solo por sus últimos 4 dígitos y los
documentos usan el formato `FIC-<dígitos>`.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 si no lo tienes) y `git`.
- [Claude Code](https://docs.claude.com/en/docs/claude-code) instalado y autenticado. El agente
  usa esa sesión. Como alternativa, exporta `ANTHROPIC_API_KEY` en tu terminal; nunca la
  guardes en el repo.

## Arranque en 5 minutos

```bash
git clone https://github.com/luisurbina-dotcom/banco-andino-disputas-agent.git
cd banco-andino-disputas-agent
uv sync                       # dependencias
uv run pytest -q              # tests unitarios: sin red ni credenciales (~10 s)
uv run python -m chat         # chat con el agente; escribe /salir para terminar
```

Prueba en el chat: *"Hola, ayer me aparecieron dos cobros que no reconozco en mi tarjeta
terminada en 4821: uno de $180.000 y otro de $1.250.000. Por favor bloqueen la tarjeta."* Cuando
te pida identificarte: *"Soy Ana María Gómez, documento FIC-10000001, nací el 1988-04-12."*

Los recuadros de color muestran las acciones reales en el banco (tarjeta bloqueada, disputa
abierta, escalado, negado por una garantía). Salen de los eventos que registran los hooks, no
del texto del modelo.

Si el chat dice que no pudo iniciar el agente, autentica Claude Code (`claude` y luego `/login`)
o exporta `ANTHROPIC_API_KEY`.

## Casos de prueba obligatorios

| Caso | Demo en el chat | Qué se ve |
|---|---|---|
| Mensaje de ejemplo (dos cobros y bloqueo) | `uv run python -m chat --guion demo/c1_mensaje_ejemplo.txt` | Bloqueo, disputa de $180.000 y escalamiento de $1.250.000 |
| Persona a pedido | `uv run python -m chat --guion demo/c2_persona.txt` | Escala sin investigar |
| Dos clientes con el mismo nombre | `uv run python -m chat --guion demo/c3_mismo_nombre.txt` | Pide otro dato y no elige |
| Disputa sin identidad verificada | `uv run python -m chat --guion demo/c4_sin_identidad.txt` | No se abre ninguna disputa |
| Falla transitoria del servidor MCP | `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1 uv run python -m chat --guion demo/c5_falla_transitoria.txt` | Reintenta y consulta |
| Cobro fuera de política | `uv run python -m chat --guion demo/c6_fuera_de_politica.txt` | Escala sin disputar |

Los mismos casos tienen aserciones automáticas sobre las herramientas llamadas, negadas o no
llamadas. Toman entre 3 y 4 minutos y usan el modelo real:

```bash
uv run pytest -m e2e -v
```

El orden y los tiempos para grabar el video están en [demo/GUION_VIDEO.md](demo/GUION_VIDEO.md).

## Plugin reutilizable

Otro equipo puede instalar el hook de datos ficticios, el auditor de cumplimiento y la skill de
revisión en su repositorio:

```text
/plugin marketplace add luisurbina-dotcom/banco-andino-disputas-agent
/plugin install banca-guardrails@banco-andino
```

Detalles en [plugins/banca-guardrails/README.md](plugins/banca-guardrails/README.md).

## Estructura

| Ruta | Contenido |
|---|---|
| `src/mcp_server/` | Servidor MCP del core bancario (FastMCP, stdio): 6 herramientas y errores estructurados |
| `src/agent/` | Agente (Agent SDK), hooks que garantizan las reglas 1 y 2, subagente `analista-transacciones` y casos e2e |
| `src/chat/` | Interfaz de chat en terminal con indicadores de acciones |
| `data/` | Datos ficticios del core (JSON) |
| `specs/` | Artefactos de Spec Kit, una carpeta por ticket (spec, plan, tasks, revisión) |
| `.claude/` | Ecosistema de Claude Code: reglas, hooks, skills, subagentes y comandos |
| `plugins/`, `.claude-plugin/` | Plugin `banca-guardrails` y su marketplace |
| `demo/` | Guiones de los casos y del video |
| `scripts/` | Verificación del ecosistema, conversación de prueba y empaquetado del `.zip` |

## Flujo de trabajo

`/siguiente-ticket` pasa el ticket a In progress, crea la rama y la especificación. Siguen
`/speckit-plan`, las tareas, el análisis y la implementación con tests. `/abrir-pr` corre la
revisión independiente y la de cumplimiento, abre el PR con `Closes #N` y pasa el ticket a
In review. Al fusionar, el Project lo pasa a Done. Cada ticket deja su rastro en `specs/<feature>/`
y en GitHub.

Otras verificaciones:

```bash
bash scripts/verificar_ecosistema.sh                # configuración del ecosistema y del plugin
uv run python scripts/conversar.py "mensaje" …      # conversación con traza de eventos
uv run python scripts/empaquetar.py                 # .zip para Code Defense (con .git, ≤ 50 MB)
```

Para abrir el `.zip`, usa `unzip banco-andino-disputas-agent.zip`: conserva los permisos de
ejecución de los scripts. `python -m zipfile -e` los pierde: corre igual con `bash script.sh`, pero
`git status` marca esos scripts como modificados (`git config core.fileMode false` lo evita).
Sin `git` instalado, los tests que arman repositorios de prueba se saltan con su motivo;
`verificar_ecosistema.sh` sí necesita `git`.

## Pendiente del autor

- Publicar el video de funcionamiento y reemplazar el texto "pendiente" de arriba por el enlace.
- Generar el `.zip` desde `main` con `uv run python scripts/empaquetar.py` y subirlo a Code Defense.
