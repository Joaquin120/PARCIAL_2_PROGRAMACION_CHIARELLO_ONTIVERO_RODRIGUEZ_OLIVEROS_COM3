# item-management Specification

## Purpose
Provee operaciones completas de creación, consulta, actualización y eliminación de artículos con validación estricta de esquemas y persistencia transaccional asíncrona.

## Requirements

### Requirement: Creación y validación de nuevos artículos
The system SHALL / El sistema DEBE recibir solicitudes de creación de artículos y validar que el precio y el inventario sean valores no negativos antes de persistirlos.

#### Scenario: Creación exitosa de artículo
- **WHEN** un cliente envía una solicitud POST con nombre, precio positivo y stock válido
- **THEN** el sistema persiste la entidad en la base de datos y responde con código HTTP 201 Created y los datos asignados

#### Scenario: Rechazo por precio negativo
- **WHEN** un cliente envía una solicitud POST con un precio inferior a cero
- **THEN** el sistema rechaza la solicitud retornando código HTTP 422 Unprocessable Entity con el detalle de la validación

### Requirement: Consulta paginada y filtrado de artículos
The system SHALL / El sistema DEBE proveer endpoints para listar artículos con soporte de paginación mediante parámetros de límite y desplazamiento, permitiendo filtrar por estado.

#### Scenario: Listado con paginación
- **WHEN** un cliente envía una petición GET especificando parámetros de paginación
- **THEN** el sistema retorna la colección de artículos paginada con código HTTP 200 OK

#### Scenario: Filtrado por estado activo
- **WHEN** un cliente envía una petición GET filtrando por artículos activos
- **THEN** el sistema responde únicamente con los artículos cuyo estado coincida con el filtro indicado

### Requirement: Actualización parcial y total de artículos
The system SHALL / El sistema DEBE permitir la actualización de campos específicos o completos de un artículo existente verificando su identificador.

#### Scenario: Actualización parcial de stock
- **WHEN** un cliente envía una petición PATCH con un nuevo valor de stock para un artículo existente
- **THEN** el sistema actualiza únicamente el campo indicado y retorna código HTTP 200 OK

#### Scenario: Actualización de artículo inexistente
- **WHEN** un cliente intenta actualizar un artículo cuyo identificador no existe en la persistencia
- **THEN** el sistema responde con código HTTP 404 Not Found

### Requirement: Eliminación de artículos y control de inexistencia
The system SHALL / El sistema DEBE procesar la eliminación de un artículo existente por su identificador y reportar error si el recurso no es encontrado.

#### Scenario: Eliminación exitosa
- **WHEN** un cliente envía una petición DELETE con el identificador de un artículo existente
- **THEN** el sistema remueve el artículo y responde con código HTTP 204 No Content

#### Scenario: Eliminación de artículo inexistente
- **WHEN** un cliente envía una petición DELETE para un identificador inexistente
- **THEN** el sistema responde con código HTTP 404 Not Found
