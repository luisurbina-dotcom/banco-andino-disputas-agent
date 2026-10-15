# Quickstart: entregables

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| Q1 | Clon limpio en un temporal; seguir solo el README (cronometrado) | Tests en verde y primera respuesta del chat en < 5 min | US1, FR-002, SC-001 |
| Q2 | `bash scripts/verificar_ecosistema.sh` | README y DECISIONES presentes; 11 necesidades; ≤ 1.000 palabras | FR-009, SC-002 |
| Q3 | Rutas citadas en README y DECISIONES | Todas existen | FR-004, SC-005 |
| Q4 | `uv run python scripts/empaquetar.py --salida <tmp>/x.zip` | `.zip` con `.git`, sin archivos prohibidos, ≤ 50 MB | US3, FR-005, SC-003 |
| Q5 | Descomprimir el `.zip`, `git log` y tests | Historial intacto; tests en verde | US3 |
| Q6 | Correr los seis guiones de `demo/` en el chat | Indicadores esperados de cada caso | US4, SC-004 |
| Q7 | `uv run pytest -q` | En verde, incluidos los tests del empaquetado | FR-005 |

## Resultados (2026-10-15)

| # | Resultado |
|---|---|
| Q1 | ✅ Clon limpio, pasos del README: `uv sync` 2 s (caché de uv caliente), 411 tests en 11 s, primera respuesta del chat en 10 s; total 23 s. En una máquina sin caché se suma la descarga de dependencias, muy por debajo de 5 min |
| Q2 | ✅ `verificar_ecosistema.sh`: sección 011 en verde; `DECISIONES.md` cubre las 11 necesidades con 723 palabras |
| Q3 | ✅ Todas las rutas citadas en README, DECISIONES y el guion del video existen (salvo `.claude/settings.local.json`, personal e ignorado por diseño) |
| Q4 | ✅ `scripts/empaquetar.py`: 2,1 MB, 1182 archivos, `.git` incluido; sin entorno virtual, PDF del enunciado ni notas personales (ignorados por git) |
| Q5 | ✅ `.zip` descomprimido con `unzip`: 91 commits, `origin` en GitHub, árbol limpio, 424 tests en verde. (Con `python -m zipfile -e` se pierden los bits de ejecución de los `.sh`; `unzip` los conserva) |
| Q6 | ✅ Los seis guiones en el chat muestran los indicadores del caso: C1 bloqueo, delegación, disputa TX-0001, ⛔ regla 2 sobre TX-0002 y escalamiento; C2 solo escalamiento; C3 2 coincidencias y luego identidad de Carlos Ramírez; C4 sin acciones; C5 🔁 y 📋; C6 `POLITICA_NO_CUBRE` y escalamiento. **Hallazgo fuera de alcance**: en C1 y C6 el subagente intentó devolver su análisis con la herramienta interna `SubagentHandback` y el guardia `pre_herramientas_permitidas` la negó (⛔ espurios); el principal volvió a consultar por su cuenta. Queda para un ticket aparte |
| Q7 | ✅ `uv run pytest -q`: 424 en verde (13 nuevos del empaquetado) |

Tras la revisión independiente:

| # | Resultado |
|---|---|
| Q1′ | ✅ Clon limpio de la rama final con `UV_CACHE_DIR` vacío: clon + `uv sync` 4 s, 433 tests en 12 s, primera respuesta del chat en 9 s; total 25 s |
| Q4′ | ✅ El empaquetado revisa todo el historial: detectó un ejemplo con forma de cédula en `9f25fd6` (#2, previo al hook). El autor aceptó la excepción, fijada por hash del blob; el paquete se genera (2,1 MB, 1190 archivos) y cualquier otro hallazgo histórico se sigue rechazando |
| Q7′ | ✅ 433 tests (22 del empaquetado: historial, URL con token, enlaces simbólicos, credenciales, excepción por hash) |
| Q4″ | ✅ Tras la re-revisión (clon `--no-local`, revisión de todos los objetos, commits y tags): paquete de 1,1 MB y 240 archivos; descomprimido con `unzip`: 94 commits, `git fsck` limpio, árbol limpio, 14 ramas; 27 tests del empaquetado |
