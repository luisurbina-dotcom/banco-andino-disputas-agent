---
name: sincronizar-ticket
description: Cambia el estado de un ticket en el GitHub Project del equipo o comenta en su issue, siempre a través del servidor MCP de GitHub. La usan /siguiente-ticket y /abrir-pr; úsala también cuando haya que reflejar en GitHub el avance real de un ticket.
argument-hint: "<issue> <Todo|In progress|In review|Done|comentar> [texto del comentario]"
allowed-tools: mcp__github__projects_list mcp__github__projects_get mcp__github__projects_write mcp__github__issue_read mcp__github__add_issue_comment
---

Argumentos: `$ARGUMENTS` → número de issue, acción y, si la acción es `comentar`, el texto.

## Constantes del proyecto (no son secretos)

- Repositorio: `luisurbina-dotcom/banco-andino-disputas-agent`
- Project: número `1` del usuario `luisurbina-dotcom`
- Campo de estado: `Status`, con opciones `Todo`, `In progress`, `In review`, `Done`

## Cambiar estado

1. Busca el item del issue en el Project (`projects_list` / `projects_get`). Si el issue no está
   en el Project, agrégalo (`projects_write`).
2. Obtén el id del campo `Status` y el de la opción pedida **por nombre**; no los supongas.
3. Actualiza el campo con `projects_write` (método de actualización de item).
4. Confirma leyendo de nuevo el item y responde `#<issue> → <estado>`.

## Comentar

1. Publica el texto con `add_issue_comment` en el issue indicado.
2. El comentario de avance usa siempre esta estructura:
   `### Avance: <etapa>` · **Especificado** · **Decidido** · **Pendiente**.
3. Responde con el enlace al comentario.

## Reglas

- Todo cambio en GitHub pasa por el servidor MCP `github`; no uses la CLI `gh` ni la web.
- Si el servidor no responde o no está autenticado, detente y explica: exportar `GITHUB_PAT` en
  una terminal interactiva, reiniciar Claude Code y aprobar el servidor `github` si se pide.
- Nunca incluyas credenciales ni datos con forma real en los comentarios.
