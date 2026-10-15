# Data Model: casos end-to-end

## Evento (existente, `agent.garantias.Evento`)

| Campo | Uso en las verificaciones |
|---|---|
| `herramienta` | nombre corto (`iniciar_disputa`, …) o el subagente en las delegaciones |
| `argumentos` | p. ej. `id_transaccion`, `causa`, `id_transacciones`, `id_cliente` |
| `resultado` | `ok`, `error`, `negado`, `delegado` |
| `detalle` | respuesta del banco (dict) o motivo de la negación |
| `agente` | `principal` o `analista-transacciones` |

## Caso end-to-end

| Campo | Descripción |
|---|---|
| nombre | identificador del test (`test_e2e_<caso>`) |
| mensajes | mensajes del cliente por turno (ver `contracts/casos.md`) |
| entorno | variables del core para el caso (solo US5: falla transitoria) |
| invariantes | funciones de verificación aplicadas a los eventos |

## Funciones de verificación (puras, sobre una lista de eventos)

| Función | Verdadero si… |
|---|---|
| `exitosos(eventos, herramienta)` | lista de eventos `ok` de esa herramienta |
| `llamadas(eventos, herramienta)` | todos los eventos de esa herramienta, con cualquier resultado |
| `disputas_abiertas(eventos)` | ids de transacción con `iniciar_disputa` ok y `id_disputa` |
| `escalamientos(eventos)` | escalamientos ok (causa, transacciones, id_caso) |
| `verificado_antes_de_operar(eventos)` | toda operación ok sobre productos va después de verificar a **su** cliente (una identidad bloqueada deja de contar) |
| `investigo_antes_de_escalar(eventos)` | hubo una acción distinta de escalar antes del primer escalamiento confirmado (regla 4) |
| `disputas_sobre_umbral(eventos)` | disputas abiertas por montos > $500.000 (regla 2) |
