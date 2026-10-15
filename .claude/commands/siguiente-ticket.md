---
description: Toma el siguiente ticket del GitHub Project, lo pasa a In progress, crea su rama e inicia /speckit-specify con el contenido del issue.
argument-hint: "[número-de-issue]"
---

Inicia el siguiente ticket del backlog. Si se indicó un número (`$ARGUMENTS`), usa ese issue.

1. **Conexión.** Comprueba que el servidor MCP `github` responde (por ejemplo, leyendo el
   Project). Si no, detente con las instrucciones de la skill `sincronizar-ticket`.
2. **Trabajo en curso.** Si algún ticket del Project está en `In progress`, avisa cuál es y
   pide confirmación antes de seguir.
3. **Elegir.** Toma el issue abierto en `Todo` con el menor número (o el indicado). Si no hay
   ninguno, informa que el backlog está vacío y termina sin cambiar nada.
4. **Estado.** Usa la skill `sincronizar-ticket` con `<n> In progress`.
5. **Rama.** Primero busca si el ticket ya tiene feature: una carpeta `specs/*/spec.md` cuyo
   campo **Input** mencione `#<n>`. Si existe, reutiliza su nombre y cámbiate a esa rama
   (ticket retomado). Si no, desde `main` actualizado (`git switch main && git pull`) crea la
   rama `NNN-nombre`: `NNN` es el siguiente número libre en `specs/` y `nombre` son 2–4 palabras
   del título en minúsculas con guiones. Escribe `.specify/feature.json` con
   `{"feature_directory": "specs/NNN-nombre"}`.
6. **Especificar.** Invoca `/speckit-specify` pasándole el número, título y cuerpo completos del
   issue (leídos por MCP) e indicando que la rama y la carpeta ya existen.
7. **Avisar.** Usa `sincronizar-ticket` con `<n> comentar` y un comentario de avance con la
   rama, el enlace a `specs/NNN-nombre/spec.md`, lo especificado, lo decidido y lo pendiente.
   Publica la rama antes (`git push -u origin NNN-nombre`) para que el enlace funcione.

Al final, resume en pocas líneas: ticket, rama, estado en el Project y siguiente paso
(`/speckit-plan`).
