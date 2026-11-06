# parcial-customer-management Specification

## Purpose
Permite administrar el ciclo de vida de los clientes de la librería, su vinculación opcional 1 a 1 con cuentas de usuario del sistema, y la consulta de su historial de compras con validación estricta de esquemas y permisos.

## Requirements

### Requirement: Gestión de entidades cliente
The system SHALL provide administrative endpoints to create, retrieve and partially update customer records with strict schema validation.

#### Scenario: Alta exitosa de cliente
- **WHEN** un usuario con rol `ADMIN` o `VENDEDOR` envía los datos de un nuevo cliente a `POST /clientes`
- **THEN** el sistema persiste la entidad en la base de datos y responde **HTTP 201 Created** con los datos del cliente generado

#### Scenario: Consulta de cliente por identificador
- **WHEN** un miembro del personal solicita `GET /clientes/{id}` de un cliente existente
- **THEN** el sistema responde **HTTP 200 OK** con los datos del cliente solicitado

#### Scenario: Actualización parcial de cliente con PATCH
- **WHEN** un usuario autorizado envía campos a modificar en `PATCH /clientes/{id}`
- **THEN** el sistema actualiza únicamente los campos provistos respetando `exclude_unset=True` y responde **HTTP 200 OK** con la entidad actualizada

#### Scenario: Rechazo de cliente inexistente
- **WHEN** se solicita o actualiza un cliente con un identificador inexistente
- **THEN** el sistema responde **HTTP 404 Not Found**

#### Scenario: Rechazo por campos inesperados en el cuerpo
- **WHEN** se envía una petición a endpoints de clientes con propiedades no definidas en el contrato
- **THEN** el sistema rechaza la petición con **HTTP 422 Unprocessable Entity**

### Requirement: Vinculación de perfil de usuario y cliente
The system SHALL allow binding an authenticated user account to an existing customer record ensuring a strict one-to-one relationship.

#### Scenario: Vinculación exitosa de cliente a usuario
- **WHEN** un usuario autenticado invoca `POST /clientes/{id}/perfil` para asociar su cuenta a una ficha de cliente sin asignar
- **THEN** el sistema actualiza el registro del cliente estableciendo `usuario_id` con el identificador del usuario autenticado y responde **HTTP 200 OK**

#### Scenario: Conflicto si el cliente ya tiene usuario asociado
- **WHEN** se intenta vincular una ficha de cliente que ya posee `usuario_id` asignado a otro usuario
- **THEN** el sistema rechaza la solicitud con **HTTP 409 Conflict**

#### Scenario: Conflicto si el usuario ya posee otra ficha vinculada
- **WHEN** un usuario que ya cuenta con una ficha de cliente asociada intenta vincularse a otro cliente
- **THEN** el sistema rechaza la operación con **HTTP 409 Conflict**

### Requirement: Consulta de ventas por cliente
The system SHALL expose the paginated sales history associated with a specific customer record, restricted to store staff or the owning customer.

#### Scenario: Personal consulta ventas de cualquier cliente
- **WHEN** un usuario con rol `ADMIN` o `VENDEDOR` solicita `GET /clientes/{id}/ventas`
- **THEN** el sistema responde **HTTP 200 OK** con el listado paginado de ventas de dicho cliente

#### Scenario: Cliente titular consulta sus propias ventas
- **WHEN** un usuario con rol `CLIENTE` consulta `GET /clientes/{id}/ventas` y su `usuario_id` coincide con el del cliente
- **THEN** el sistema responde **HTTP 200 OK** con sus ventas

#### Scenario: Rechazo para cliente ajeno
- **WHEN** un usuario con rol `CLIENTE` consulta `GET /clientes/{id}/ventas` de un cliente distinto al suyo
- **THEN** el sistema responde **HTTP 403 Forbidden**
