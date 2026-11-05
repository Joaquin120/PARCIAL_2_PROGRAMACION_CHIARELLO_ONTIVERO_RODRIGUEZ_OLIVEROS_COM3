# parcial-catalog Specification

## Purpose

Gestiona el catálogo de libros, autores, editoriales y géneros con soft delete, filtros de búsqueda y paginación uniforme.

## Requirements

### Requirement: Consulta pública paginada y filtrada del catálogo de libros

The system SHALL provide a public paginated book listing excluding soft-deleted books, supporting optional filtering by title and genre.

#### Scenario: Listado paginado de libros activos

- **WHEN** un cliente consulta `GET /libros`
- **THEN** la respuesta devuelve el envoltorio paginado `{items, total, page, size, pages}` con `page` por defecto 1 y `size` por defecto 20, conteniendo únicamente libros activos

#### Scenario: Filtro por título

- **WHEN** un cliente consulta `GET /libros` con el parámetro `titulo`
- **THEN** la respuesta devuelve únicamente los libros cuyo título contiene la cadena especificada sin distinción de mayúsculas

#### Scenario: Filtro por género

- **WHEN** un cliente consulta `GET /libros` con el parámetro `genero_id`
- **THEN** la respuesta devuelve únicamente los libros pertenecientes a dicho género

#### Scenario: Exclusión de libros dados de baja

- **WHEN** existen libros con `borrado_en IS NOT NULL` en la base de datos
- **THEN** ninguno de ellos aparece en el listado devuelto por `GET /libros`

#### Scenario: Página inexistente

- **WHEN** un cliente solicita una página mayor al total calculado (`page > pages`)
- **THEN** el sistema responde **HTTP 422 Unprocessable Entity**

### Requirement: Consulta de catálogos auxiliares y libros asociados

The system SHALL expose read-only endpoints for authors, publishers, and genres, along with their associated active books.

#### Scenario: Listado de catálogos auxiliares

- **WHEN** se invoca `GET /autores`, `GET /editoriales` o `GET /generos`
- **THEN** el sistema devuelve la lista completa de entidades disponibles

#### Scenario: Consulta de libros por autor

- **WHEN** se invoca `GET /autores/{id}/libros` para un autor existente
- **THEN** el sistema devuelve la lista paginada de libros activos de dicho autor

#### Scenario: Consulta de libros por editorial

- **WHEN** se invoca `GET /editoriales/{id}/libros` para una editorial existente
- **THEN** el sistema devuelve la lista paginada de libros activos de dicha editorial

#### Scenario: Consulta de libros por género

- **WHEN** se invoca `GET /generos/{id}/libros` para un género existente
- **THEN** el sistema devuelve la lista paginada de libros activos de dicho género

### Requirement: Alta administrativa de libros

The system SHALL allow users with the `ADMIN` role to create new books with an initial stock, establishing the initial stock ledger entry atomically.

#### Scenario: Alta exitosa de libro por administrador

- **WHEN** un usuario con rol `ADMIN` invoca `POST /libros` con datos válidos y `stock_inicial`
- **THEN** el sistema persiste el libro, inicializa su stock y crea atómicamente el primer movimiento de stock con motivo `'Stock inicial'`, respondiendo **HTTP 201 Created**

#### Scenario: Rechazo de alta por usuario sin rol ADMIN

- **WHEN** un usuario sin rol `ADMIN` o sin sesión intenta invocar `POST /libros`
- **THEN** el sistema responde **HTTP 403 Forbidden** si está autenticado o **HTTP 401 Unauthorized** si no posee sesión

#### Scenario: Rechazo por campos inesperados en el cuerpo

- **WHEN** la petición `POST /libros` incluye un campo no definido en el esquema DTO
- **THEN** el sistema rechaza la petición con **HTTP 422 Unprocessable Entity**

#### Scenario: Conflicto por ISBN duplicado en libros activos

- **WHEN** se intenta crear un libro cuyo ISBN ya pertenece a otro libro activo (`borrado_en IS NULL`)
- **THEN** el sistema responde **HTTP 409 Conflict**

### Requirement: Modificación parcial de libros sin alteración directa de stock

The system SHALL allow administrators to update title and price via PATCH while strictly forbidding direct modification of the stock field.

#### Scenario: Modificación exitosa de título o precio

- **WHEN** un administrador invoca `PATCH /libros/{id}` enviando únicamente `titulo` o `precio`
- **THEN** los campos enviados son actualizados y el sistema responde **HTTP 200 OK** con los datos del libro

#### Scenario: Intento de modificación directa de stock rechazado

- **WHEN** se envía una petición `PATCH /libros/{id}` que incluye el campo `stock`
- **THEN** el sistema rechaza la petición con **HTTP 422 Unprocessable Entity** sin modificar el stock

#### Scenario: Modificación sobre libro dado de baja o inexistente

- **WHEN** un administrador invoca `PATCH /libros/{id}` sobre un libro inexistente o con `borrado_en IS NOT NULL`
- **THEN** el sistema responde **HTTP 404 Not Found**

### Requirement: Borrado lógico de libros

The system SHALL perform a soft delete on books, preserving historical relationships and freeing the ISBN for subsequent registrations.

#### Scenario: Borrado lógico exitoso

- **WHEN** un administrador invoca `DELETE /libros/{id}` para un libro activo
- **THEN** el sistema asigna la marca temporal actual en `borrado_en`, responde **HTTP 204 No Content** y el libro deja de ser visible en el catálogo

#### Scenario: Liberación de ISBN tras baja lógica

- **WHEN** un libro fue dado de baja y posteriormente se crea un nuevo libro con el mismo ISBN
- **THEN** la creación del nuevo libro es aceptada sin violar la unicidad de ISBN

#### Scenario: Intento de borrado sobre libro inexistente o ya borrado

- **WHEN** un administrador invoca `DELETE /libros/{id}` para un identificador inexistente o ya dado de baja
- **THEN** el sistema responde **HTTP 404 Not Found**

