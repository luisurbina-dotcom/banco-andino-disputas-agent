# banca-guardrails

Plugin de Claude Code para los equipos de Banco Andino (banco ficticio). Lleva a tu repositorio
tres protecciones del proyecto de disputas:

| Pieza | Qué hace |
|---|---|
| Hook `datos_ficticios` (`PreToolUse` sobre ediciones) | Bloquea escrituras con números con forma de tarjeta real (pasan Luhn) o documentos con forma real, y explica cómo usar datos ficticios (últimos 4 dígitos, `FIC-<dígitos>`). Si el hook falla, la escritura se bloquea. |
| Subagente `banca-guardrails:compliance-auditor` | Audita un cambio contra la constitución o la guía de tu proyecto y las reglas de negocio del banco. Solo puede leer (`Read`, `Grep`, `Glob`). |
| Skill `/banca-guardrails:revisar-cumplimiento <carpeta-spec>` | Le pasa al auditor el diff de tu rama frente a `main` y devuelve una tabla con evidencia y un veredicto `CUMPLE` / `NO CUMPLE`. |

Requisitos: Claude Code 2.1.295 o superior y `python3` en el `PATH`.

## Instalación

Dentro de Claude Code, en tu proyecto:

```text
/plugin marketplace add luisurbina-dotcom/banco-andino-disputas-agent
/plugin install banca-guardrails@banco-andino
```

Si tienes el repositorio clonado, puedes usar su ruta en lugar de `owner/repo`. Por CLI:

```bash
claude plugin marketplace add <ruta-o-owner/repo> --scope project   # o user / local
claude plugin install banca-guardrails@banco-andino --scope project
```

Con `--scope project`, la declaración queda en `.claude/settings.json` y la comparte todo el equipo.

## Comprobar que funciona

1. `claude plugin details banca-guardrails@banco-andino` lista 1 skill, 1 agente y 1 hook.
2. Pide a Claude que escriba un archivo con un número de tarjeta de prueba de 16 dígitos: la
   escritura se bloquea con el mensaje `[datos_ficticios]`. Con "tarjeta terminada en 4821" la
   escritura procede.
3. En una rama con cambios: `/banca-guardrails:revisar-cumplimiento specs/<feature>` devuelve la
   tabla Principio/Regla | Resultado | Evidencia y la línea de veredicto.

## Desinstalación

```text
/plugin uninstall banca-guardrails@banco-andino
/plugin marketplace remove banco-andino
```

## Limitaciones

- La skill compara la rama actual con `main`.
- Si tu proyecto no tiene `.specify/memory/constitution.md`, el auditor usa tu `CLAUDE.md` y las
  reglas del banco, y lo indica en el informe.
- El hook convive con los hooks de tu proyecto; no reemplaza tu configuración.
