---
name: revisar-cumplimiento
description: Revisión de cumplimiento de una feature contra la constitución o guía del proyecto y las reglas de negocio de Banco Andino. Úsala antes de abrir un PR o cuando pidan verificar que las reglas del banco estén implementadas como se especificaron.
argument-hint: "<carpeta-spec>"
context: fork
agent: banca-guardrails:compliance-auditor
allowed-tools: Bash(git diff:*) Read Grep Glob
---

Audita la feature cuya especificación está en `$ARGUMENTS` (si está vacío, audita el cambio
completo sin carpeta de especificación).

## Cambio a auditar (rama actual frente a `main`)

Archivos:

!`git diff --stat main...HEAD`

Diff:

!`git diff main...HEAD`

## Pasos

1. Lee la fuente de verdad del proyecto (constitución o `CLAUDE.md`) y, si hay carpeta,
   `$ARGUMENTS/spec.md` y `plan.md`.
2. Evalúa cada principio y cada regla del banco con evidencia `archivo:línea`.
3. Una regla 1 o 2 que no esté garantizada por un hook determinista (por ejemplo, `PreToolUse`
   del Agent SDK) es **NO CUMPLE**, aunque el prompt la mencione.
4. Devuelve la tabla Principio/Regla | Resultado | Evidencia y la línea
   `Veredicto: CUMPLE` o `Veredicto: NO CUMPLE`.
