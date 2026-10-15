# Research: Memoria del equipo, reglas por ruta y permisos

Verificado contra la documentación oficial de Claude Code el 2026-10-15:
[memory](https://code.claude.com/docs/en/memory.md),
[permissions](https://code.claude.com/docs/en/permissions.md) y
[settings](https://code.claude.com/docs/en/settings-reference).

## R1. Importar la constitución en CLAUDE.md

- **Decision**: una línea `@.specify/memory/constitution.md` en el `CLAUDE.md` raíz.
- **Rationale**: la ruta se resuelve relativa al archivo que importa. El import se expande al
  cargar `CLAUDE.md`, así que hay una sola fuente de verdad y un cambio en la constitución
  llega a todos en el siguiente `git pull`. Admite hasta 4 niveles de imports recursivos. Un
  import dentro de un bloque de código o entre comillas se ignora, así que va en su propia
  línea y fuera de bloques.
- **Alternatives considered**: copiar los principios en `CLAUDE.md` (dos fuentes que se
  desincronizan); confiar en que Spec Kit lea la constitución (solo la leen sus comandos, no
  las sesiones normales).

## R2. Guía de subdirectorio

- **Decision**: `src/agent/CLAUDE.md`.
- **Rationale**: un CLAUDE.md de subdirectorio no se carga al iniciar. Claude lo carga cuando
  lee, escribe o edita un archivo de esa carpeta. Es el mecanismo adecuado para instrucciones
  que solo importan al trabajar en el agente (hooks del SDK, reglas 1 y 2, ciclo agéntico).
- **Alternatives considered**: ponerlo en el CLAUDE.md raíz (ocupa contexto en todo el repo);
  una regla por ruta `src/agent/**` (equivalente en carga, pero el requisito pide al menos un
  CLAUDE.md por subdirectorio o un `@import`, y la guía es propia de la carpeta, no de un tipo
  de archivo repartido por el repo).

## R3. Reglas con alcance por ruta

- **Decision**: `.claude/rules/tests.md` y `.claude/rules/mcp-tools.md`, con `paths` como
  lista YAML de globs en el frontmatter.
- **Rationale**: una regla con `paths` se carga cuando Claude usa Read, Write o Edit sobre un
  archivo que coincide (también con `cat`/`head` de un archivo por Bash). No se carga solo por
  resultados de Grep/Glob. Una regla sin `paths` se carga siempre, igual que CLAUDE.md, así que
  dejaría de ser por ruta. Los tests están repartidos en muchas carpetas (necesidad 3): un glob
  `**/test_*.py` los cubre a todos, cosa que un CLAUDE.md por carpeta no puede hacer.
- **Alternatives considered**: un CLAUDE.md en cada carpeta con tests (duplicado y frágil);
  poner las convenciones de tests en el CLAUDE.md raíz (ocupan contexto aunque no se toquen
  tests).

## R4. Sintaxis de denegación de secretos

- **Decision**: en `.claude/settings.json`:

  ```json
  "deny": [
    "Read(./.env)", "Read(./.env.*)", "Read(**/.env)", "Read(**/.env.*)",
    "Read(!.env.example)", "Read(!**/.env.example)",
    "Read(./secrets/**)",
    "Edit(./.env)", "Edit(./.env.*)", "Edit(**/.env)", "Edit(**/.env.*)",
    "Edit(./secrets/**)"
  ]
  ```

- **Rationale**:
  - Los patrones siguen el estilo gitignore: `./` es relativo al directorio de trabajo, `**/`
    coincide a cualquier profundidad.
  - Una regla `Edit(...)` cubre Edit y Write; una regla `Write(...)` específica nunca se
    consulta, por eso no se usa.
  - Un deny de `Read` ya bloquea Edit y Write sobre la misma ruta, y bloquea `cat`, `head`,
    `tail`, `sed` y `tee` por Bash. Aun así se declaran los `Edit(...)` de forma explícita para
    que la política se lea sin conocer esa regla implícita.
  - Una regla `allow` no puede abrir una excepción dentro de un deny. La excepción se expresa
    con negación (`!`) dentro de la misma lista `deny` y del mismo archivo.
- **Límite conocido**: el deny no impide que un subproceso arbitrario (un script de Python o
  Node) lea el archivo. Ese caso se cubre en el issue #2 con un hook sobre Bash; la garantía a
  nivel de sistema operativo sería el sandbox de Claude Code.
- **Alternatives considered**: instrucción en CLAUDE.md "no leas .env" (no es determinista,
  viola el principio II); solo `.gitignore` (evita versionar pero no evita que Claude lo lea).

## R5. Precedencia entre equipo y personal

- **Decision**: la denegación vive en `.claude/settings.json` (equipo, versionado).
- **Rationale**: Claude Code evalúa deny → ask → allow sobre todos los niveles. Un deny de
  proyecto gana sobre un allow en `settings.local.json`, lo que cumple FR-008 sin mecanismos
  adicionales.
- **Alternatives considered**: managed settings (requieren administración de la máquina;
  excesivo para un repo de equipo).

## R6. Preferencias personales

- **Decision**: `CLAUDE.local.md` y `.claude/settings.local.json` en `.gitignore` (ya
  configurado en el bootstrap); preferencias de todos los repos en `~/.claude/CLAUDE.md`.
- **Rationale**: `CLAUDE.local.md` sigue soportado y se carga junto a `CLAUDE.md`. Para
  compartir preferencias entre worktrees, la documentación sugiere importar un archivo del home
  (`@~/.claude/mis-prefs.md`) desde `CLAUDE.local.md`.
- **Alternatives considered**: una sección "personal" dentro del CLAUDE.md versionado (afecta
  a todos).

## R7. Verificación

- **Decision**: script `scripts/verificar_ecosistema.sh` para lo estático y escenarios manuales
  en `quickstart.md` para lo que solo se observa en una sesión.
- **Rationale**: la carga de reglas y la denegación de permisos ocurren dentro de Claude Code y
  no se pueden probar con pytest sin levantar una sesión. El script cubre lo verificable
  (archivos, frontmatter, JSON, `.gitignore`, longitud del CLAUDE.md); el quickstart cubre el
  resto con `/memory`, `/context` y `/permissions`.
- **Alternatives considered**: tests e2e con `claude -p` (lentos, requieren credenciales y no
  aportan más que la verificación manual para una feature de configuración).
