# Revisión antes del PR — 011-readme-decisiones-entregables

## Revisión independiente (`code-reviewer`, dentro de `/abrir-pr 11`)

- **Fecha**: 2026-10-15 · **Veredicto**: APROBADO CON OBSERVACIONES (4 MEDIA, 10 BAJA; sin ALTA).
- **Confirmado**: las afirmaciones de README y DECISIONES coinciden con el repo (hooks, reglas,
  subagentes, contrato de errores, comandos); los guiones son idénticos a los mensajes de los e2e;
  no hay credenciales ni datos con forma real en el árbol; el guion del video suma ~3 min 10 s.

| # | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| 1 | MEDIA | El empaquetado solo revisaba el árbol, no el historial que viaja en `.git`. | **Corregido**: revisa nombres (`git log --all --name-only`) y contenidos de todos los blobs (`rev-list --all --objects` + `cat-file --batch`). Tests con secreto y credencial borrados. **Hallazgo real**: un ejemplo con forma de cédula en `9f25fd6` (#2, escrito antes del hook, corregido en `be92bdc`). **Aceptado por el autor** como excepción fijada por el hash del blob (`EXCEPCIONES_HISTORIAL`), sin reescribir el historial (principio VII); test que exige que el blob exista y que la excepción no cubra otro contenido. |
| 2 | MEDIA | Una URL de `origin` con token entraría en `.git/config`. | **Corregido**: se quita usuario/token de la URL y se revisa `.git/config`; test. |
| 3 | MEDIA | Detector de credenciales estrecho. | **Corregido**: `gh[pousr]_`, `github_pat_`, `sk-ant-`, `AKIA…`, bloques `PRIVATE KEY`; nombres `id_rsa*`, `*.p12`, `*.pfx`; tests. |
| 4 | MEDIA | `SubagentHandback` negado por el guardia (⛔ espurios en C1 y C6; delegación degradada). | **Fuera de alcance**: el autor decidió un ticket aparte, después de este. El guion del video lo advierte. |
| 5 | BAJA | Enlaces simbólicos seguidos al comprimir. | **Corregido**: se rechazan; test. |
| 6 | BAJA | Archivos no UTF-8 sin revisar. | **Corregido**: se decodifican con reemplazo (los blobs del historial también). |
| 7 | BAJA | 50 MB binarios vs. decimales. | **Corregido**: `50_000_000`. |
| 8 | BAJA | Un `.zip` viejo sobrevivía a una validación fallida; sin aviso fuera de `main`. | **Corregido**: se borra antes de validar; aviso si la rama no es `main`; test. |
| 9 | BAJA | Faltaban carpetas de artefactos. | **Corregido**: `site-packages`, `.tox`, `dist`, `build`, `*.egg-info`. |
| 10 | BAJA | Tests sensibles a la firma de commits global. | **Corregido**: `commit.gpgsign=false`. |
| 11 | BAJA | "18 reglas deny" mezcla 16 negaciones y 2 excepciones. | **Corregido** en DECISIONES. |
| 12 | BAJA | La falla cerrada se atribuía solo a `onFailure`. | **Corregido**: `ejecutar_seguro` como garantía y `onFailure` para timeouts. |
| 13 | BAJA | Q1 no corrió sobre el árbol final y con caché caliente. | **Corregido**: Q1′ con caché vacía sobre la rama final (25 s). |
| 14 | BAJA | La comprobación del video pasa con "pendiente". | **Corregido**: aviso (sin fallar) mientras falte el enlace. |
