# Planeación inicial — Agente de disputas de Banco Andino

Plan de desarrollo de la prueba técnica *Claude Code + Agent SDK — Escenario Banca: Disputas de
transacciones*. Fecha límite de los tres entregables: **domingo 18 de octubre de 2026**.
Esfuerzo estimado: 12–15 horas efectivas.

- Repositorio: https://github.com/luisurbina-dotcom/banco-andino-disputas-agent
- GitHub Project: https://github.com/users/luisurbina-dotcom/projects/1

## 1. Decisiones técnicas

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | **Python 3.12** | El `claude-agent-sdk` de Python tiene hooks (`PreToolUse`/`PostToolUse`) y subagentes (`AgentDefinition`). FastMCP arma el servidor en pocas líneas, y ruff y pytest resuelven el formateo y los tests. |
| Servidor MCP | FastMCP por stdio, con datos ficticios en `data/*.json` | No exige base de datos y se arranca con un solo comando. |
| Interfaz de chat | Terminal con **Rich**: paneles por turno y etiquetas 🔒 BLOQUEO / 📄 DISPUTA / 👤 ESCALADO | Se construye rápido, se entiende en el video y el diseño visual no se califica. Alternativa web: Streamlit. |
| Tests | pytest unitario y determinista para herramientas y hooks, sin API key. Tests e2e marcados `@pytest.mark.e2e` con los 6 casos obligatorios. | El README cumple con "correr los tests en menos de 5 minutos" aunque no haya API key. |
| Gestión de dependencias | uv | Fija la versión de Python del proyecto y también ejecuta Spec Kit. |

## 2. Arquitectura del agente

```
chat_ui (Rich) ──► agente (ClaudeSDKClient)
                     ├─ hooks SDK: PreToolUse  → regla 1 (identidad) y regla 2 (monto > 500.000)
                     │             PostToolUse → marca la sesión como verificada
                     ├─ subagente "analista-transacciones" (solo consultar_transacciones)
                     └─ MCP stdio ──► servidor core bancario (FastMCP + JSON ficticio)
```

Puntos clave para la sustentación:

- **Regla 1:** un `PreToolUse` sobre `consultar_transacciones`, `iniciar_disputa` y
  `bloquear_tarjeta` niega la llamada si el estado de la sesión no está verificado. Ese estado
  solo lo cambia el `PostToolUse` cuando `verificar_identidad` responde con éxito.
- **Regla 2:** el hook **busca el monto real en los datos** a partir del id de la transacción,
  en lugar de confiar en el monto que manda el modelo.
- **Reglas 3 a 5:** van en el prompt y en las descripciones de las herramientas. La regla 5 la
  refuerza el servidor devolviendo un error de negocio `POLITICA_NO_CUBRE` que indica que hay
  que escalar.
- **Errores estructurados:**
  `{"error": {"tipo": "TRANSITORIO|VALIDACION|NEGOCIO|PERMISOS", "reintentable": bool, "mensaje": ...}}`.
  Una búsqueda sin resultados devuelve `{"coincidencias": []}` y no un error. La falla
  transitoria se simula con una variable de entorno o un contador que inyecta fallos.
- **Ciclo agéntico:** el SDK continúa o termina según la razón de parada del modelo. Se
  consumen los mensajes hasta recibir `ResultMessage`, sin límite fijo de iteraciones ni
  búsqueda de palabras en el texto.
- **Datos ficticios:** tarjetas solo por sus últimos 4 dígitos o con números que **no pasan
  Luhn**, y cédulas con un formato claramente falso. Si no, el propio hook de PII bloquearía
  los fixtures.

## 3. Ecosistema de Claude Code: necesidad → mecanismo

| # | Necesidad | Mecanismo |
|---|---|---|
| 1 | Convenciones sin configurar nada | `CLAUDE.md` raíz, más `.claude/settings.json` y `.mcp.json` versionados. El CLAUDE.md raíz incluye `@.specify/memory/constitution.md` como única fuente de verdad. |
| 2 | Preferencias personales aisladas | `CLAUDE.local.md` y `.claude/settings.local.json`, ambos en `.gitignore`, más `~/.claude/CLAUDE.md`. |
| 3 | Tests junto al código | `.claude/rules/tests.md` con `paths: ["**/test_*.py"]`. |
| — | 2.ª regla por ruta y CLAUDE.md por subdirectorio | `.claude/rules/mcp-tools.md` con `paths: ["src/mcp_server/**"]` (contrato de errores y descripciones). `src/agent/CLAUDE.md` sobre los hooks del SDK. |
| 4 | No hay código sin spec | Hook `PreToolUse` (Edit\|Write sobre `src/**`) que comprueba que exista `specs/<rama>/spec.md` y, si no, sale con código 2. |
| 5 | Nada con forma de tarjeta o cédula real | Hook `PreToolUse` sobre Edit\|Write que escanea el contenido: números de 13–19 dígitos que pasan Luhn y patrones de documento. Pre-commit opcional. |
| 6 | No tocar secretos | `permissions.deny` con `Read(./.env*)`, `Edit(./.env*)` y `Read(./secrets/**)`, más un hook que bloquee `cat .env` por Bash. |
| 7 | Formateo tras cada edición | Hook `PostToolUse` que ejecuta `ruff format` y `ruff check --fix`. |
| 8 | Revisión independiente antes del PR | Subagente `code-reviewer` de solo lectura (Read, Grep, Glob, `Bash(git diff:*)`), invocado por el comando `/abrir-pr`. |
| 9 | Revisión de cumplimiento | Skill `revisar-cumplimiento` con `context: fork`, `allowed-tools: Read Grep Glob` y `argument-hint: [carpeta-spec]`, que delega en el subagente `compliance-auditor`. |
| 10 | Tickets sincronizados | Comando `/siguiente-ticket` (toma el ticket, lo pasa a In progress y alimenta `/speckit-specify`). Skill `gh-sync` para los comentarios de avance. `/abrir-pr` mueve a In review con "Closes #N". Al fusionar, el workflow integrado del Project pasa el ticket a Done. |
| 11 | Reutilizable por otro equipo | Plugin `banca-guardrails` con `marketplace.json` en el repo: subagente `compliance-auditor`, skill de cumplimiento y hook de PII. |

MCP de GitHub en `.mcp.json`: servidor remoto con el header
`X-MCP-Toolsets: repos,issues,pull_requests,projects` y el token como `${GITHUB_PAT}`, expandido
desde el entorno. Ninguna credencial queda en el repositorio.

## 4. Backlog en GitHub

El bootstrap (repositorio, Spec Kit y constitución) se completó antes de crear el backlog, por
eso no tiene issue. Quedaron **11 issues** en el Project:

| # | Ticket | Etiquetas |
|---|---|---|
| [#1](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/1) | [Ecosistema] CLAUDE.md, reglas por ruta y permisos del equipo | ecosistema |
| [#2](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/2) | [Ecosistema] Hooks de desarrollo: spec primero, datos ficticios y formateo | ecosistema |
| [#3](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/3) | [Ecosistema] Automatización del ciclo de tickets con GitHub MCP y revisiones antes del PR | ecosistema |
| [#4](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/4) | [MCP] Core bancario simulado: datos ficticios, buscar_cliente y verificar_identidad | mcp, regla-negocio |
| [#5](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/5) | [MCP] Transacciones, disputas, bloqueo, escalamiento y fallas transitorias | mcp, regla-negocio |
| [#6](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/6) | [Agente] Ciclo agéntico con Agent SDK y hooks que garantizan las reglas 1 y 2 | agente, regla-negocio |
| [#7](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/7) | [Agente] Subagente de análisis, solicitudes con varios asuntos y handoff al analista | agente |
| [#8](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/8) | [Agente] Interfaz de chat que hace evidentes las acciones | agente |
| [#9](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/9) | [Agente] Casos de prueba obligatorios end-to-end | agente, regla-negocio |
| [#10](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/10) | [Ecosistema] Plugin reutilizable banca-guardrails | ecosistema |
| [#11](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/11) | [Docs] README, DECISIONES.md y entregables | docs |

Cada ticket recorre `/speckit-specify → /speckit-plan → /speckit-tasks → /speckit-analyze →
/speckit-implement` en su propia rama y PR (`/speckit-clarify` y `/speckit-converge` cuando
hagan falta).

Los tickets #1 a #3 construyen la propia automatización: mientras no exista
`/siguiente-ticket` (sale del #3), los estados se mueven con `gh`. Desde el #4 todo pasa por la
automatización.

## 5. Cronograma

| Día | Trabajo |
|---|---|
| **Mié 14** | Bootstrap: repositorio, GitHub Project, Spec Kit y constitución. *(Completado el 15.)* |
| **Jue 15** | Backlog en GitHub (#1–#11). Ecosistema base: tickets #1, #2 y #3. Conviene tenerlo antes que el código para que todo el historial pase por los hooks. |
| **Vie 16** | Servidor MCP completo con sus tests unitarios: tickets #4 y #5. Inicio del agente: ticket #6. |
| **Sáb 17** | Agente, subagente, interfaz de chat y tests e2e: tickets #6 a #9. Plugin: ticket #10. |
| **Dom 18** | Ticket #11: DECISIONES.md (máximo 2 páginas), README, video de funcionamiento, video de defensa y el .zip (con `.git`, sin `.venv` ni `.env`). |

Si se aprieta el tiempo, se recorta primero el plugin y los extras de la interfaz. Los
comportamientos obligatorios del agente no se recortan.

## 6. Riesgos que pueden anular la entrega

- **Revisión de autoría (35% del puntaje es la sustentación):** al cerrar cada ticket, recorrer
  el código y anotar cómo se explicaría. Un elemento que no se pueda defender vale cero.
- **Faltas graves:** que una regla dependa solo del prompt, que haya una credencial o un `.env`
  en el repo o en el zip, o que algún dato parezca real.
- **No reescribir el historial de git** antes de entregar.
