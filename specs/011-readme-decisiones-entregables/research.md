# Research: README, DECISIONES.md y entregables

## R1. Cómo se arma el `.zip`

- **Decision**: `scripts/empaquetar.py` clona el repositorio local (`git clone --no-hardlinks`) en
  un directorio temporal, apunta `origin` al repositorio de GitHub y comprime el clon con
  `zipfile` (incluye `.git`). Advierte si el árbol de trabajo tiene cambios sin commit.
- **Rationale**: un clon solo contiene lo versionado: los archivos ignorados (entorno virtual,
  cachés, archivos de entorno, el PDF del enunciado y las notas personales) quedan fuera por
  construcción, y el historial viaja intacto.
- **Alternatives considered**: `git archive` (no incluye `.git`); comprimir la carpeta de trabajo
  con exclusiones (riesgo de arrastrar archivos ignorados).

## R2. Verificaciones del paquete

- **Decision**: antes de escribir el `.zip`, el script recorre el clon y falla si encuentra:
  nombres prohibidos (archivos de entorno salvo `.env.example`, `*.pem`, `*.key`, `secrets/`,
  `.venv/`, `node_modules/`, `__pycache__/`), patrones de credenciales (`ghp_`, `github_pat_`,
  `sk-ant-`) o datos con forma real según `.claude/hooks/detector.py` en los archivos de texto
  versionados (fuera de `.git`). Después comprueba que el `.zip` pese ≤ 50 MB.
- **Rationale**: un archivo de entorno o una credencial en el `.zip` es falta grave; reutilizar el
  detector evita una segunda definición de "forma real".

## R3. DECISIONES.md

- **Decision**: una tabla por necesidad (1–11): mecanismo, ubicación y por qué (con la
  alternativa descartada cuando aporta), más una sección corta "criterio general" (invariante →
  mecanismo determinista; juicio → instrucciones) y las piezas del agente que la defensa pide.
  Límite: ≤ 1.000 palabras, verificado en `verificar_ecosistema.sh`.

## R4. Guiones del video

- **Decision**: un archivo por caso en `demo/`, un mensaje por línea (formato de `--guion`), y
  `demo/GUION_VIDEO.md` con el orden, el comando de cada caso (C5 con
  `BANCO_FALLAS_TRANSITORIAS=consultar_transacciones:1`) y los recuadros que deben verse.
  Mensajes iguales a los de los casos end-to-end (`specs/009-casos-e2e/contracts/casos.md`), que ya
  pasaron con el agente real.
- **Rationale**: cada caso necesita una sesión nueva (identidad y core limpios); los mismos
  mensajes que los e2e hacen la grabación predecible y cabe en 5 minutos (≈ 2,5–4 min de agente).

## R5. README

- **Decision**: secciones: qué es; requisitos; arranque en 5 minutos (`uv sync`, `uv run pytest`,
  `uv run python -m chat`); demo y casos e2e; plugin; estructura; flujo de trabajo y enlaces
  (Project, video); acciones del autor pendientes. Enlaces a `DECISIONES.md` y a la constitución.
