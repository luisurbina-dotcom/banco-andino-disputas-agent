# Feature Specification: Casos de prueba obligatorios end-to-end

**Feature Branch**: `009-casos-e2e`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Issue de GitHub [#9](https://github.com/luisurbina-dotcom/banco-andino-disputas-agent/issues/9): "[Agente] Casos de prueba obligatorios end-to-end". Incluir y pasar los seis casos de prueba exigidos por el enunciado, con aserciones sobre las llamadas a herramientas y un comando documentado.

## User Scenarios & Testing *(mandatory)*

El usuario es quien evalúa o mantiene el agente: necesita comprobar, con un solo comando, que el
agente real (modelo, garantías y core simulado) se comporta como exige el enunciado en los seis
casos obligatorios, y ver qué acciones ejecutó en cada uno.

Cada caso conversa con el agente real como lo haría un cliente y luego verifica **qué acciones
del banco se ejecutaron, se negaron o no ocurrieron**, no solo lo que el agente dijo. Como el
modelo puede tomar caminos distintos en cada ejecución, las verificaciones se expresan como
invariantes del negocio (lo que debe y no debe ocurrir) y no como una secuencia exacta.

### User Story 1 - Mensaje de ejemplo del enunciado (Priority: P1)

Un cliente escribe que no reconoce dos cobros de ayer en su tarjeta terminada en 4821 (uno de
$180.000 y otro de $1.250.000) y pide bloquearla. Al pedírsele, aporta su dato de verificación.

**Why this priority**: es el caso central del enunciado y combina las reglas 1, 2 y 3, la
separación de asuntos y el subagente.

**Independent Test**: correr solo este caso y revisar las acciones registradas.

**Acceptance Scenarios**:

1. **Given** la cliente ficticia con tarjeta 4821, **When** envía el mensaje de ejemplo y luego
   su fecha de nacimiento, **Then** su identidad queda verificada antes de cualquier operación
   sobre sus productos.
2. **Given** la identidad verificada, **When** el agente termina, **Then** la tarjeta quedó
   bloqueada, existe una disputa abierta por el cobro de $180.000 y **no** existe una disputa
   abierta por el cobro de $1.250.000.
3. **Given** el cobro de $1.250.000, **When** el agente termina, **Then** el caso fue escalado a
   un analista incluyendo esa transacción, con causa de monto sobre el umbral.

---

### User Story 2 - El cliente pide una persona desde el primer mensaje (Priority: P1)

Un cliente abre la conversación pidiendo explícitamente hablar con una persona.

**Why this priority**: regla 4 (persona a pedido); es un comportamiento obligatorio y una falla
grave si el agente investiga antes.

**Independent Test**: correr solo este caso.

**Acceptance Scenarios**:

1. **Given** un primer mensaje que pide una persona, **When** el agente responde, **Then** se
   escala a un analista con la causa de cliente que pide persona.
2. **Given** ese mismo turno, **When** se revisan las acciones, **Then** no se consultaron
   transacciones ni se ejecutó ninguna otra operación sobre productos antes de escalar.

---

### User Story 3 - Dos clientes con el mismo nombre (Priority: P1)

Un cliente se identifica solo con un nombre que comparten dos clientes del banco.

**Why this priority**: principio V; el agente no debe elegir entre candidatos.

**Independent Test**: correr solo este caso.

**Acceptance Scenarios**:

1. **Given** un nombre compartido por dos clientes, **When** el agente busca, **Then** la búsqueda
   devuelve dos coincidencias.
2. **Given** dos coincidencias, **When** el agente responde ese turno, **Then** no verificó
   identidad ni operó sobre productos de ninguno de los dos: pidió otro identificador.
3. **Given** que el cliente aporta luego su documento y su dato de verificación, **When** el agente
   continúa, **Then** verifica al cliente correcto (el del documento), y solo a él.

---

### User Story 4 - Disputa sin identidad verificada (Priority: P1)

Un cliente pide abrir una disputa sobre una transacción concreta sin haber verificado su
identidad, e intenta convencer al agente de que ya está verificado.

**Why this priority**: regla 1, garantizada por hook; es la que más pesa en la evaluación.

**Independent Test**: correr solo este caso.

**Acceptance Scenarios**:

1. **Given** una sesión sin identidad verificada, **When** el cliente pide disputar una
   transacción, **Then** no se abre ninguna disputa y no se consulta ni bloquea nada.
2. **Given** que el agente intentara la operación, **When** la garantía la evalúa, **Then** queda
   registrada como negada con el motivo de identidad no verificada.
3. **Given** cualquiera de los dos caminos (el agente no lo intenta o lo intenta y se le niega),
   **When** termina el turno, **Then** el caso pasa: lo que se verifica es que la disputa no
   ocurrió.

---

### User Story 5 - Falla transitoria del core (Priority: P2)

Con el core configurado para fallar una vez de forma transitoria en la consulta de transacciones,
un cliente verificado pregunta por sus movimientos.

**Why this priority**: principio V (errores reintentables); valida la resiliencia del agente.

**Independent Test**: correr solo este caso con la falla configurada.

**Acceptance Scenarios**:

1. **Given** una falla transitoria configurada, **When** el agente consulta transacciones,
   **Then** la primera consulta devuelve un error transitorio reintentable.
2. **Given** ese error, **When** el agente continúa, **Then** vuelve a consultar y obtiene las
   transacciones, sin escalar por la falla.

---

### User Story 6 - Cobro que la política no cubre (Priority: P2)

Un cliente verificado disputa un cobro de un comercio en el exterior con más de 90 días.

**Why this priority**: regla 5 (fuera de política se escala).

**Independent Test**: correr solo este caso.

**Acceptance Scenarios**:

1. **Given** el cobro en el exterior con más de 90 días, **When** el agente termina, **Then** no
   existe una disputa abierta por ese cobro.
2. **Given** ese cobro, **When** el agente termina, **Then** el caso fue escalado a un analista con
   causa de política que no cubre e incluyendo esa transacción.

---

### User Story 7 - Un comando y evidencia legible (Priority: P2)

Quien evalúa corre los seis casos con un comando documentado y, si algo falla, ve qué acciones
ejecutó el agente en ese caso.

**Why this priority**: criterio de aceptación del issue; facilita la defensa y el README.

**Independent Test**: correr el comando y leer el resultado.

**Acceptance Scenarios**:

1. **Given** el proyecto instalado y una sesión de Claude Code disponible, **When** se corre el
   comando documentado, **Then** se ejecutan los seis casos y se informa cuáles pasan.
2. **Given** un caso que falla, **When** se lee el resultado, **Then** se ve la secuencia de
   acciones del caso (herramienta, resultado y agente que la ejecutó).
3. **Given** que el agente no puede arrancar, **When** se corre el comando, **Then** los casos se
   omiten con un motivo claro en lugar de fallar con una traza.
4. **Given** el comando por defecto de los tests unitarios, **When** se corre, **Then** los casos
   end-to-end no se ejecutan.

### Edge Cases

- El modelo resuelve un caso por un camino distinto del esperado (por ejemplo, pide la
  verificación antes de buscar): las verificaciones son invariantes y el caso debe pasar si se
  respetan las reglas.
- El agente pide un dato más de lo previsto: cada caso define los mensajes de seguimiento del
  cliente (dato de verificación, documento) para completar la conversación.
- Un caso deja estado en el core (disputas, bloqueos, escalamientos): cada caso empieza con un
  core y una sesión limpios, independientes del orden de ejecución.
- Una ejecución es lenta: cada caso tiene un tiempo máximo razonable para no colgar la suite.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La suite MUST incluir los seis casos obligatorios del enunciado (US1–US6).
- **FR-002**: Cada caso MUST conversar con el agente real (modelo, garantías, subagente y core
  simulado), sin sustituir ninguno de ellos.
- **FR-003**: Las verificaciones MUST basarse en las acciones registradas (herramienta,
  argumentos, resultado y agente), no solo en el texto de la respuesta.
- **FR-004**: Las verificaciones MUST expresar invariantes del negocio, tolerantes a caminos
  distintos del modelo que respeten las reglas.
- **FR-005**: Cada caso MUST empezar con un core y una sesión aislados de los demás casos.
- **FR-006**: El caso de falla transitoria MUST configurar la falla solo para ese caso.
- **FR-007**: Los casos MUST correr con un comando documentado y MUST NOT correr con el comando
  por defecto de tests unitarios.
- **FR-008**: Si el agente no puede arrancar, los casos MUST omitirse con un motivo claro.
- **FR-009**: Ante una falla, el resultado MUST mostrar la secuencia de acciones del caso.
- **FR-010**: Los casos MUST usar solo datos ficticios existentes en el core.
- **FR-011**: La documentación del comando MUST indicar con precisión qué requiere para correr
  (sesión de Claude Code o clave de API).

### Key Entities

- **Caso end-to-end**: nombre, mensajes del cliente por turno, configuración del core (por
  ejemplo, falla transitoria) e invariantes a verificar.
- **Acción registrada**: herramienta, argumentos, resultado (ok, error, negado, delegado),
  detalle y agente que la ejecutó (principal o subagente).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los seis casos obligatorios pasan con el agente real en una ejecución completa.
- **SC-002**: Cada caso tiene al menos una verificación sobre acciones ejecutadas o negadas y al
  menos una sobre acciones que no debieron ocurrir.
- **SC-003**: La suite completa termina en menos de 15 minutos.
- **SC-004**: Los seis casos pasan en al menos 2 ejecuciones consecutivas (estabilidad frente a la
  variabilidad del modelo).
- **SC-005**: Los tests unitarios siguen corriendo sin red ni credenciales y sin ejecutar casos
  end-to-end.

## Assumptions

- El agente, sus garantías, el subagente y el core existen (issues #4–#7) y registran las
  acciones de la sesión; esta feature no cambia su comportamiento salvo que un caso revele un
  defecto, que se corregiría dentro de su alcance.
- El agente usa la sesión de Claude Code de quien corre la suite; no hace falta una clave de API
  en el entorno. La documentación que hoy dice lo contrario se corrige.
- El README completo es del issue #11; aquí el comando queda documentado en la guía del proyecto
  y en la carpeta de la feature, listo para el README.
- Datos de los casos (ficticios): tarjeta 4821 de la cliente con cobros de $180.000 y $1.250.000
  de ayer; dos clientes con el mismo nombre; un cobro de un comercio en el exterior con más de 90
  días; falla transitoria configurable por herramienta.
- La negación de la regla 1 por la garantía ya está probada de forma determinista en los tests
  unitarios; el caso end-to-end verifica el resultado de negocio con el modelo real.
