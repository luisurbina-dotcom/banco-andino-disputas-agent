---
description: Ejecuta la revisión independiente y la de cumplimiento, abre el PR con Closes #N, pasa el ticket a In review y comenta el avance en el issue.
argument-hint: "[número-de-issue]"
---

Abre el PR de la feature actual. El issue es `$ARGUMENTS` o, si no se indica, el que aparece en
el campo **Input** de `specs/<rama>/spec.md`.

1. **Precondiciones.** La rama actual es de feature (`NNN-nombre`); `specs/<rama>/tasks.md` no
   tiene tareas abiertas salvo las de revisión y cierre; `uv run pytest -q`,
   `uv run ruff check .` y `bash scripts/verificar_ecosistema.sh` pasan. Si algo falla,
   detente y muéstralo.
2. **Revisión independiente.** Delega en el subagente `code-reviewer` la revisión de
   `git diff main...HEAD` contra la especificación. Registra en `specs/<rama>/review.md` la tabla
   de hallazgos con una columna de resolución (Corregido / Aceptado con justificación /
   Pendiente). Corrige lo que corresponda y vuelve a pedir revisión si hubo cambios de fondo.
3. **Revisión de cumplimiento.** Ejecuta `/revisar-cumplimiento specs/<rama>` y agrega su tabla
   y veredicto a `review.md`.
4. **Compuerta.** Si queda un hallazgo ALTA en `Pendiente` o el veredicto es `NO CUMPLE`, **no
   abras el PR**: lista lo que falta. Aceptar un hallazgo es decisión de la persona y requiere
   justificación escrita en `review.md`.
5. **PR.** Haz commit de `review.md`, `git push` de la rama y crea el PR **por el servidor MCP**
   (`create_pull_request`, base `main`). El cuerpo incluye `Closes #<n>`, qué incluye, el proceso
   Spec Kit, la verificación y las limitaciones conocidas, y termina con
   `🤖 Generated with [Claude Code](https://claude.com/claude-code)`. Enviarlo por MCP evita que
   el hook `secretos_bash` bloquee textos que mencionan archivos de secretos.
6. **Sincronizar.** Usa la skill `sincronizar-ticket` con `<n> In review` y luego con
   `<n> comentar` y un comentario de avance (especificado, decidido, verificado, pendiente) con
   el enlace al PR.

Al final, recuerda que la fusión la hace una persona y que el workflow del Project pasará el
ticket a Done.
