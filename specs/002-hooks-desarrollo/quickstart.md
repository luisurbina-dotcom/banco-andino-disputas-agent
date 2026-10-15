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
