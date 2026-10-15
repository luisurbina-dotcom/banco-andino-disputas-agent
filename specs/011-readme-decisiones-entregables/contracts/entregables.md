# Contrato: entregables

## `uv run python scripts/empaquetar.py [--salida RUTA]`

- Salida por defecto: `../banco-andino-disputas-agent.zip` (fuera del repo, para no versionarlo).
- Contenido: clon del repositorio con `.git`, carpeta raíz `banco-andino-disputas-agent/`.
- Falla (código 1, mensaje claro) si hay nombres prohibidos, credenciales o datos con forma real
  en lo versionado, o si el `.zip` supera 50 MB. Advierte (sin fallar) si hay cambios sin commit.
- Imprime ruta, tamaño y número de archivos.

## Guiones (`demo/`)

| Archivo | Caso | Mensajes | Debe verse |
|---|---|---|---|
| `c1_mensaje_ejemplo.txt` | C1 | 2 | ✅ identidad, 🔒 tarjeta bloqueada, 🤝 delegación, 📄 disputa TX-0001, 👤 escalado por umbral |
| `c2_persona.txt` | C2 | 1 | 👤 escalado `CLIENTE_PIDE_PERSONA`, sin consultas |
| `c3_mismo_nombre.txt` | C3 | 2 | 🔎 2 coincidencias y pedido de otro dato; luego ✅ identidad de CLI-003 |
| `c4_sin_identidad.txt` | C4 | 1 | ninguna disputa (pide verificación o ⛔ negado) |
| `c5_falla_transitoria.txt` | C5 | 1 | 🔁 falla transitoria y luego 📋 consulta |
| `c6_fuera_de_politica.txt` | C6 | 1 | 👤 escalado `POLITICA_NO_CUBRE`, sin disputa |
