# Spec Delta

## Purpose

Define el patrón Unit of Work y repositorios para la gestión atómica de transacciones sin apropiarse de la sesión física.

## ADDED Requirements

### Requirement: Unit of Work transaction boundary
The system SHALL provide an asynchronous Unit of Work that delimits atomic transactions via commit on success and rollback on failure, without closing the underlying physical session.

#### Scenario: Transacción confirmada con éxito
- **WHEN** un bloque `async with uow:` finaliza sin excepciones
- **THEN** se invoca `commit()` en la sesión de base de datos compartida y la sesión física permanece abierta para el ciclo de vida del request

#### Scenario: Transacción revertida ante error
- **WHEN** ocurre una excepción dentro del bloque `async with uow:`
- **THEN** se invoca `rollback()` en la sesión de base de datos y la excepción es propagada

### Requirement: Repositorios desacoplados con flush exclusivo
The repositories SHALL execute asynchronous reads and writes, delegating transactional confirmation to the Unit of Work by using `flush()` exclusively on creation and updates.

#### Scenario: Inserción en repositorio
- **WHEN** se invoca `add()` sobre una entidad en un repositorio
- **THEN** se agrega a la sesión y se ejecuta `flush()`, sin invocar `commit()`

### Requirement: Soporte para borrado lógico en repositorios
The repositories with soft-delete support SHALL filter out soft-deleted entities by default and provide explicit methods for deletion marking and historical queries.

#### Scenario: Consulta por defecto en repositorio con soft delete
- **WHEN** se consulta un listado de entidades
- **THEN** se filtran automáticamente las entidades con `borrado_en` no nulo

#### Scenario: Marcado de borrado lógico
- **WHEN** se ejecuta `soft_delete()` sobre un registro activo
- **THEN** se actualiza su campo `borrado_en` con la marca temporal actual y se ejecuta `flush()`
