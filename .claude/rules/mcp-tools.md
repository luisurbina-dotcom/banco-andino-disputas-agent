---
paths:
  - "src/mcp_server/**"
---

# Contrato de herramientas del servidor MCP

El modelo decide con lo que dicen la descripción y la respuesta de cada herramienta. Escribe
ambas para que no tenga que adivinar.

## Descripciones

- `buscar_cliente` localiza candidatos por documento, nombre o últimos 4 dígitos de tarjeta.
  No confirma identidad. Puede devolver varias coincidencias: en ese caso el agente pide otro
  identificador y no elige.
- `verificar_identidad` confirma a un único cliente ya localizado con un dato adicional. Es
  requisito para cualquier operación sobre sus productos.
- Cada descripción dice cuándo usar la herramienta, cuándo no, y qué devuelve.

## Errores

Todo error tiene esta forma:

```json
{"error": {"tipo": "TRANSITORIO|VALIDACION|NEGOCIO|PERMISOS", "reintentable": true, "mensaje": "..."}}
```

- `TRANSITORIO`: falla temporal del core; `reintentable: true`.
- `VALIDACION`: argumentos mal formados; `reintentable: false` hasta corregirlos.
- `NEGOCIO`: la operación viola una regla o la política no la cubre (p. ej.
  `POLITICA_NO_CUBRE`); el mensaje indica la acción esperada (escalar).
- `PERMISOS`: falta identidad verificada u otra autorización.
- Una búsqueda sin resultados **no** es error: devuelve `{"coincidencias": []}`.

## Datos

Solo datos ficticios de `data/`. Las tarjetas se exponen por sus últimos 4 dígitos.
