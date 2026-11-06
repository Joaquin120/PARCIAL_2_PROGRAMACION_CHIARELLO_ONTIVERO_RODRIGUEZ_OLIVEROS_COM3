# Spec Delta

## Purpose

Gestiona el procesamiento atómico de órdenes de venta, la deducción transaccional de existencias, el despacho de notificaciones asíncronas en background, y el acceso protegido al historial y detalle de transacciones sin problemas de rendimiento N+1.

## ADDED Requirements

### Requirement: Registro atómico de ventas y mutación de stock
The system SHALL register sales transactions atomically under a single Unit of Work, decrementing physical stock and creating append-only negative stock movements, while enforcing complete rollback on failure.

#### Scenario: Venta exitosa con múltiples libros
- **WHEN** un usuario con rol `VENDEDOR` o `ADMIN` envía una orden de venta válida con uno o más libros con stock suficiente
- **THEN** el sistema persiste la cabecera de la venta, los renglones de detalle, decrementa el stock de cada libro y crea los correspondientes registros en `movimiento_stock` con motivo `'Venta'`, confirmando la transacción y respondiendo **HTTP 201 Created**

#### Scenario: Rollback completo por stock insuficiente
- **WHEN** se intenta registrar una venta donde al menos uno de los libros solicitados supera la cantidad de stock físico disponible
- **THEN** el sistema revierte todas las modificaciones en la base de datos (sin crear venta, renglones ni movimientos) y responde **HTTP 409 Conflict**

#### Scenario: Rechazo de venta sobre libro dado de baja
- **WHEN** una venta incluye un libro con marca de baja lógica (`borrado_en IS NOT NULL`)
- **THEN** el sistema aborta la transacción completa y responde **HTTP 409 Conflict**

#### Scenario: Fijación de precios y cálculo de total en el servidor
- **WHEN** se procesa la venta
- **THEN** el sistema toma los precios unitarios vigentes directamente del registro del libro en la base de datos, calcula el total de la venta en el servidor y descarta cualquier precio provisto por el cliente

#### Scenario: Control de acceso para registro de venta
- **WHEN** un usuario sin rol `VENDEDOR` ni `ADMIN` intenta crear una venta
- **THEN** el sistema responde **HTTP 403 Forbidden** si está autenticado o **HTTP 401 Unauthorized** si no posee sesión activa

### Requirement: Notificación asíncrona de comprobante en segundo plano
The system SHALL dispatch a non-blocking background task simulating receipt delivery only after the sales transaction has been successfully committed to the database.

#### Scenario: Disparo de tarea tras confirmación exitosa
- **WHEN** una venta se confirma exitosamente (`commit()`) en la base de datos
- **THEN** el sistema encola una tarea en segundo plano que ejecuta un retardo asíncrono no bloqueante (`await asyncio.sleep(0.5)`) y emite el mensaje de aviso en consola

#### Scenario: Supresión de tarea en segundo plano ante fallo o rollback
- **WHEN** la transacción de venta falla o se revierte
- **THEN** la tarea de envío de comprobante en segundo plano no se ejecuta

### Requirement: Listado administrativo de ventas paginado
The system SHALL expose a paginated list of all sales transactions with uniform pagination wrapper for administrative staff.

#### Scenario: Consulta de listado de ventas por personal
- **WHEN** un usuario con rol `VENDEDOR` o `ADMIN` solicita `GET /ventas` con parámetros de paginación
- **THEN** el sistema responde **HTTP 200 OK** con la estructura `{items, total, page, size, pages}` conteniendo el historial general de ventas

#### Scenario: Restricción de listado general para clientes
- **WHEN** un usuario con rol exclusivo `CLIENTE` intenta acceder al listado general `GET /ventas`
- **THEN** el sistema responde **HTTP 403 Forbidden**

### Requirement: Detalle de venta con autorización dinámica por pertenencia
The system SHALL authorize access to sale details dynamically based on user ownership or staff role without static router role guards, loading relations in a fixed number of SQL queries.

#### Scenario: Acceso de personal administrativo a detalle de venta
- **WHEN** un usuario con rol `ADMIN` o `VENDEDOR` solicita el detalle `GET /ventas/{id}` de cualquier venta existente
- **THEN** el sistema valida su rol y responde **HTTP 200 OK** con la venta, cliente, usuario y renglones de detalle completos

#### Scenario: Acceso de cliente titular a su propia venta
- **WHEN** un cliente autenticado cuyo `usuario_id` coincide con el cliente asociado a la venta solicita `GET /ventas/{id}`
- **THEN** el sistema comprueba la pertenencia y responde **HTTP 200 OK** con el detalle completo de la venta

#### Scenario: Rechazo de cliente ajeno a la venta
- **WHEN** un cliente autenticado intenta consultar `GET /ventas/{id}` de una venta que pertenece a otro cliente
- **THEN** el servicio rechaza el acceso respondiendo **HTTP 403 Forbidden**

#### Scenario: Consulta de detalle sin antipatrón N+1
- **WHEN** se solicita el detalle de una venta con múltiples renglones
- **THEN** el repositorio ejecuta una cantidad fija e invariable de consultas SQL mediante carga ansiosa (`joinedload` / `selectinload`), independientemente del número de renglones

### Requirement: Consulta de ventas propias del cliente
The system SHALL allow authenticated customers to view their own purchase history through a dedicated paginated endpoint.

#### Scenario: Listado exitoso de ventas del cliente autenticado
- **WHEN** un usuario autenticado con ficha de cliente asociada solicita `GET /mis-ventas`
- **THEN** el sistema responde **HTTP 200 OK** con el envoltorio de paginación conteniendo únicamente las compras realizadas por dicho cliente

#### Scenario: Rechazo de consulta si el usuario no tiene ficha de cliente
- **WHEN** un usuario sin registro asociado en la tabla de clientes invoca `GET /mis-ventas`
- **THEN** el sistema responde **HTTP 404 Not Found**
