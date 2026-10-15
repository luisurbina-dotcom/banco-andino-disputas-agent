# Quickstart: verificar los hooks de desarrollo

## Prerrequisitos

- `python3` ≥ 3.10, uv y Claude Code ≥ 2.1.
- `uv sync` en la raíz (instala ruff y pytest).

## 1. Tests automáticos

```bash
uv run pytest .claude/hooks -q
```

Esperado: todos los tests pasan en < 10 s, sin red (SC-005). Cubren el detector, cada hook vía
stdin y el fail-closed.

## 2. Verificación en vivo (sesión de Claude Code)

| # | Paso | Esperado | Cubre |
|---|---|---|---|
| V1 | Pedir escribir en `notas.md` un número de tarjeta válido por Luhn (dictado por la persona, no por Claude) | Bloqueado por `[datos_ficticios]` | US1, SC-001 |
| V2 | Pedir escribir "tarjeta terminada en 4821, monto $1.250.000" | Permitido | US1 |
| V3 | Pedir escribir la palabra "cédula" seguida de un número de 8 dígitos con puntos de miles (dictado por la persona) | Bloqueado | US1 |
| V4 | Pedir escribir "documento" seguido de `FIC-` y 8 dígitos | Permitido | US1 |
| V5 | En `main`, pedir crear `src/x.py` | Bloqueado: la rama no es feature | US2, SC-002 |
| V6 | En una rama `999-prueba` sin carpeta de spec, pedir crear `src/x.py` | Bloqueado: faltan artefactos | US2 |
| V7 | En una rama de feature completa, pedir crear `src/x.py` | Permitido | US2 |
| V8 | Pedir `python3 -c "print(open('.env').read())"` | Bloqueado por `[secretos_bash]` | US3, SC-003 |
| V9 | Pedir `source .env` y `ls secrets/` | Bloqueados | US3 |
| V10 | Pedir `cat .env.example` | Permitido | US3 |
| V11 | Pedir escribir un `.py` mal formateado con un import sin usar | Queda formateado y sin el import | US4, SC-004 |
| V12 | Romper temporalmente `detector.py` (error de sintaxis) y pedir una escritura | Bloqueada por seguridad (fail-closed) | FR-009 |

Al terminar: borrar `notas.md`, `src/x.py`, la rama `999-prueba` y revertir V12.

## Resultados automáticos (2026-10-15)

- `uv run pytest -q` → 72 tests en verde en ~7,5 s (SC-005 ✅).
- `uv run ruff check .` y `uv run ruff format --check .` → sin hallazgos.
- Detector sobre los 71 archivos del repo → 0 detecciones (los hooks no chocan con lo existente).
- Latencia de los hooks de bloqueo (10 ejecuciones, WSL2): mediana 215–354 ms, con picos
  ocasionales de la máquina. Cumple SC-006 (< 1 s perceptible); la meta interna del plan
  (< 300 ms) solo la cumple la mediana de `spec_primero` y `secretos_bash`. El costo es casi
  todo el arranque del intérprete; se acepta.

## Resultados de la verificación en vivo (2026-10-15)

| # | Resultado | Cómo |
|---|---|---|
| V1 | ✅ Tarjeta agrupada que pasa Luhn → bloqueada por `[datos_ficticios]`, `notas.md` no se creó | Sesión nueva `claude -p`; número generado en tiempo de ejecución |
| V2 | ✅ "terminada en 4821" y "$1.250.000" → escrito | Sesión nueva `claude -p` |
| V3 | ✅ "cédula" + número con puntos de miles → bloqueado | Sesión nueva `claude -p` |
| V4 | ✅ "documento FIC-…" → escrito | Sesión nueva `claude -p` |
| V5 | ✅ Rama `prueba-sin-feature`: `src/x.py` → "no es una feature" | Sesión de implementación |
| V6 | ✅ Rama `999-prueba` sin carpeta: "Faltan spec.md, plan.md, tasks.md" | Sesión de implementación |
| V7 | ✅ Rama `002-hooks-desarrollo` completa: `src/tmp_fmt.py` → permitido | Sesión de implementación |
| V8 | ✅ `python3 -c "print(open(...))"` sobre el archivo de entorno → bloqueado | Sesión de implementación |
| V9 | ✅ Listar la carpeta de secretos → bloqueado por `[secretos_bash]` | Sesión de implementación |
| V10 | ✅ Leer la plantilla de variables con `cat` → permitido | Sesión de implementación |
| V11 | ✅ Import sin usar eliminado y archivo formateado | Sesión de implementación |
| V12 | ✅ `detector.py` con error de sintaxis → escritura bloqueada | Sesión de implementación |

Hallazgos:

- **V12 confirma research R4 y la necesidad de las dos capas.** El error ocurre al importar
  `detector` en `datos_ficticios.py`, antes de `ejecutar_seguro`: Python sale con 1 (no
  bloqueante). La escritura se bloqueó por `"onFailure": "block"` ("failed; blocking because
  onFailure is "block""). La opción existe en Claude Code 2.1.300.
- **V11 detectó un defecto de orden**: formatear antes de `ruff check --fix` dejaba una línea en
  blanco al inicio tras borrar el import. Se invirtió el orden y el test ahora exige que el
  archivo empiece por el código.
- **R11 se observó en la práctica**: un comando con un heredoc que solo *mencionaba* la carpeta
  de secretos fue bloqueado por `secretos_bash`. Se usó la herramienta de edición en su lugar.
