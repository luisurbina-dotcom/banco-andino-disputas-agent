---
paths:
  - "**/test_*.py"
  - "**/conftest.py"
---

# Convenciones de tests

- El test vive junto al módulo que prueba: `src/x/foo.py` → `src/x/test_foo.py`. No hay una
  carpeta `tests/` aparte.
- Se usa pytest. Fixtures compartidas en el `conftest.py` de la carpeta más cercana.
- Los tests unitarios no usan red ni API key: el servidor MCP y los hooks se prueban
  llamando a sus funciones directamente.
- Los casos que llaman al modelo se marcan con `@pytest.mark.e2e` y no corren por defecto.
- Solo datos ficticios: tarjetas por sus últimos 4 dígitos, documentos con formato
  claramente falso. Nunca un número completo que pase Luhn.
- En los tests del agente se afirma sobre qué herramientas se llamaron (o se bloquearon) y
  con qué argumentos, no solo sobre el texto de la respuesta.
- Un test por comportamiento, con nombre que lo describe:
  `test_disputa_sobre_umbral_es_bloqueada`.
