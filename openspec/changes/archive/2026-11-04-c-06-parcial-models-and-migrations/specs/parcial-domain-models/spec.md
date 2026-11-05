# Spec Delta

## Purpose

Define the relational domain models and constraints for users, security, catalog, customers, and sales in the Parcial system.

## ADDED Requirements

### Requirement: Modelos de usuario y asignación de roles
The system SHALL persist users and dynamic role assignments with partial unique constraints ensuring only active roles are unique per user.

#### Scenario: Asignación de rol activa única
- **WHEN** se asigna un rol a un usuario
- **THEN** la base de datos asegura unicidad en `(usuario_id, rol)` únicamente cuando `revocada_en IS NULL`

#### Scenario: Validación de valores de rol permitidos
- **WHEN** se intenta persistir una asignación de rol
- **THEN** la base de datos valida que el valor pertenezca a `ADMIN`, `VENDEDOR` o `CLIENTE`

### Requirement: Registro de intentos de acceso y eventos de seguridad
The system SHALL record authentication attempts and security audit events with indexed timestamps for efficient querying.

#### Scenario: Registro de intento de acceso
- **WHEN** un cliente intenta iniciar sesión
- **THEN** se almacena un registro en `intento_acceso` con `email`, `ip`, `cuando` y resultado `exito`

### Requirement: Catálogo de libros con unicidad condicional de ISBN
The system SHALL support soft deletion on books and enforce ISBN uniqueness only among active books with `borrado_en IS NULL`.

#### Scenario: Unicidad condicional de ISBN
- **WHEN** se da de alta un libro con un ISBN idéntico al de un libro previamente dado de baja (`borrado_en IS NOT NULL`)
- **THEN** la inserción es permitida exitosamente sin violar la restricción de clave única

### Requirement: Relación opcional uno a uno entre cliente y usuario
The system SHALL allow customers to exist without a user account while enforcing a unique one-to-one relationship when a user account is linked.

#### Scenario: Cliente vinculado a usuario
- **WHEN** se asigna un `usuario_id` a un registro de `cliente`
- **THEN** la base de datos asegura que ningún otro cliente posea el mismo `usuario_id`
