# Spec Delta

## Purpose

Define el envoltorio estandarizado de respuestas paginadas y sus reglas estrictas de validación de límites.

## ADDED Requirements

### Requirement: Formato estandarizado de paginación
The system SHALL respond with a uniform envelope containing items, total count, current page, page size, and total pages for all paginated listings.

#### Scenario: Respuesta paginada estándar
- **WHEN** un cliente solicita un listado paginado con parámetros válidos
- **THEN** la respuesta contiene `{items, total, page, size, pages}` con `size` por defecto de 20 si no fue especificado

### Requirement: Regla de colección vacía en paginación
The system SHALL return a single empty page with pages equal to 1 when a paginated query produces no results.

#### Scenario: Consulta sin registros
- **WHEN** se solicita un listado con `total == 0`
- **THEN** la respuesta retorna `total: 0`, `pages: 1` y una lista `items` vacía

### Requirement: Validación estricta de página excedida
The system SHALL reject with HTTP 422 Unprocessable Entity any paginated request where the requested page exceeds the total available pages.

#### Scenario: Solicitud de página inexistente
- **WHEN** un cliente envía un parámetro `page > pages` con `total > 0`
- **THEN** el sistema responde con HTTP 422 indicando el mensaje explicativo correspondiente
