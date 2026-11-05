# Spec Delta

## Purpose

Controla la mutación de stock físico de libros mediante reposición auditable y garantiza la trazabilidad histórica de movimientos.

## ADDED Requirements

### Requirement: Reposición de stock auditable

The system SHALL allow administrators to restock books by recording an append-only stock movement and updating book stock atomically, rejecting restock on soft-deleted books.

#### Scenario: Reposición exitosa de libro activo

- **WHEN** un administrador invoca `POST /libros/{id}/reponer` con una cantidad entera positiva
- **THEN** el sistema incrementa el stock del libro, persiste un registro en `movimiento_stock` con motivo `'Reposicion'` en la misma transacción y responde **HTTP 200 OK**

#### Scenario: Rechazo de reposición en libro dado de baja

- **WHEN** un administrador intenta reponer un libro que posee `borrado_en IS NOT NULL`
- **THEN** el sistema rechaza la operación con **HTTP 409 Conflict** sin alterar el stock ni generar movimientos

#### Scenario: Rechazo de reposición con cantidad no positiva

- **WHEN** se envía una petición de reposición con `cantidad <= 0`
- **THEN** el sistema rechaza la petición con **HTTP 422 Unprocessable Entity**

#### Scenario: Rechazo de reposición sobre libro inexistente

- **WHEN** un administrador intenta reponer un libro cuyo identificador no existe en la base de datos
- **THEN** el sistema responde **HTTP 404 Not Found**

### Requirement: Consulta de histórico de movimientos de stock

The system SHALL expose the chronological ledger of stock movements for a given book, restricted to administrators.

#### Scenario: Listado paginado de movimientos de un libro

- **WHEN** un administrador invoca `GET /libros/{id}/movimientos`
- **THEN** el sistema devuelve las entradas de stock del libro con el envoltorio `{items, total, page, size, pages}`

#### Scenario: Movimientos ordenados cronológicamente

- **WHEN** se consulta el histórico de movimientos de un libro
- **THEN** los movimientos se devuelven ordenados por fecha y hora de registro

#### Scenario: Consulta de movimientos sin privilegios de administrador

- **WHEN** un usuario sin rol `ADMIN` o sin sesión intenta consultar los movimientos de stock
- **THEN** el sistema responde **HTTP 403 Forbidden** si está autenticado o **HTTP 401 Unauthorized** si no posee sesión

### Requirement: Invariante de balance de stock

The system SHALL ensure that physical book stock always equals the sum of all its recorded stock movements.

#### Scenario: Consistencia de stock tras alta y reposición

- **WHEN** se consulta el stock de un libro tras operaciones de alta y reposición exitosas
- **THEN** el valor de `libro.stock` coincide exactamente con la suma de las cantidades registradas en sus movimientos

