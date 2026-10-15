---
name: revisar-cumplimiento
description: Revisión de cumplimiento de una feature contra la constitución y las reglas de negocio de Banco Andino. Úsala antes de abrir un PR (la invoca /abrir-pr) o cuando pidan verificar que las reglas del banco estén implementadas como se especificaron.
argument-hint: "<carpeta-spec>"
context: fork
agent: compliance-auditor
background: false
allowed-tools: Read Grep Glob Bash
---

Audita la feature cuya especificación está en `$ARGUMENTS`.

1. Lee `.specify/memory/constitution.md` y `$ARGUMENTS/spec.md` (y `plan.md` si existe).
2. Revisa el cambio con `git diff --stat main...HEAD` y `git diff main...HEAD`.
3. Evalúa los principios I a IV y, si la feature toca el agente o el servidor MCP del banco,
   cada una de las reglas de negocio 1 a 5, con evidencia `archivo:línea`.
4. Una regla 1 o 2 que no esté garantizada por un hook `PreToolUse` del Agent SDK es
   **NO CUMPLE**, aunque el prompt la mencione.
5. Devuelve la tabla Principio/Regla | Resultado | Evidencia y la línea
   `Veredicto: CUMPLE` o `Veredicto: NO CUMPLE`.
