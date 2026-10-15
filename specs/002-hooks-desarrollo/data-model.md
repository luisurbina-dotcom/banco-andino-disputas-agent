# Data Model: Hooks de desarrollo

## Deteccion (detector.py)

| Campo | Tipo | Regla |
|---|---|---|
| `tipo` | `"tarjeta"` \| `"documento"` | — |
| `inicio` | int | Posición del hallazgo en el texto |
| `sugerencia` | str | Alternativa ficticia: "usa solo los últimos 4 dígitos" o "usa el formato FIC-<dígitos>" |

Nunca guarda el valor detectado (FR-003).

### Reglas de detección

- **Tarjeta**: secuencia de 13 a 19 dígitos, admitiendo un espacio o guion entre grupos, no
  pegada a otros dígitos o letras, que **pasa Luhn** (FR-001).
- **Documento**: etiqueta (`cedula`, `cédula`, `cc`, `c.c.`, `documento`, `nit`, `pasaporte`,
  sin distinguir mayúsculas ni tildes), separadores opcionales (`:`, `#`, `No.`, espacios) y un
  número de 6 a 10 dígitos (admite puntos de miles) que **no** esté precedido por `FIC-`
  (FR-002).
- **Permitido**: últimos 4 dígitos, montos (`1.250.000`, `$180.000`), números que no pasan Luhn,
  `FIC-<dígitos>`.

## FeatureActiva (spec_primero.py)

| Campo | Tipo | Regla |
|---|---|---|
| `rama` | str | `git rev-parse --abbrev-ref HEAD` |
| `carpeta` | str \| None | `specs/<rama>/` si la rama cumple `^\d{3}-[a-z0-9-]+$` |
| `faltantes` | list[str] | De `spec.md`, `plan.md`, `tasks.md`, los que no existen |

### Código de producción (FR-005)

Ruta relativa al repo que empieza por `src/` o `data/`, excepto archivos llamados `CLAUDE.md`.
Una ruta fuera del repo no se evalúa.

## DecisionDeBloqueo (comun.py)

| Resultado | Código de salida | Canal |
|---|---|---|
| Permitir | 0 | — |
| Rechazar | 2 | Motivo en stderr, dirigido a Claude |
| Error interno de un hook de bloqueo | 2 | "Hook <nombre> falló: <error>. Se bloquea por seguridad." |
| Aviso del hook de formateo | 2 (PostToolUse) | Problemas restantes en stderr; la edición no se revierte |
