# Spec Delta

## Purpose

Resuelve la identidad desde la cookie de sesión y aplica control de acceso basado en roles vigentes consultados en base de datos, con autoprotección de administradores y auditoría.

## ADDED Requirements

### Requirement: Resolución de identidad desde la cookie de sesión

The system SHALL resolve the authenticated user exclusively from the `access_token` cookie and reject missing, invalid, expired, or inactive-user sessions with HTTP 401.

#### Scenario: Sesión válida resuelta

- **WHEN** una petición incluye una cookie `access_token` con un JWT válido de un usuario activo
- **THEN** la dependencia de identidad resuelve el usuario correspondiente para el resto del request

#### Scenario: JWT inválido o expirado

- **WHEN** la cookie contiene un token inválido, expirado o de un usuario inactivo
- **THEN** el sistema responde **HTTP 401 Unauthorized**

### Requirement: Autorización dinámica por roles vigentes

The system SHALL query active role assignments from the database on every authorized request instead of trusting token roles, so revocation takes effect immediately.

#### Scenario: Rol vigente habilita el acceso

- **WHEN** un usuario autenticado posee una asignación de rol activa requerida por el endpoint
- **THEN** la petición es autorizada y continúa su ejecución

#### Scenario: Rol revocado pierde acceso de inmediato

- **WHEN** un rol es revocado y el usuario intenta acceder en la petición siguiente a un endpoint que lo requiere
- **THEN** el sistema responde **HTTP 403 Forbidden** aunque el token aún contenga ese rol

#### Scenario: Usuario sin el rol requerido

- **WHEN** un usuario autenticado no posee ninguno de los roles requeridos
- **THEN** el sistema responde **HTTP 403 Forbidden**

### Requirement: Distinción entre falta de sesión y falta de permisos

The system SHALL respond HTTP 401 when there is no authenticated session and HTTP 403 when the session exists but lacks the required role.

#### Scenario: Acceso sin sesión a endpoint con rol

- **WHEN** una petición sin sesión válida invoca un endpoint que exige un rol
- **THEN** el sistema responde **HTTP 401 Unauthorized**

#### Scenario: Acceso con sesión pero sin rol

- **WHEN** una petición con sesión válida invoca un endpoint que exige un rol que el usuario no posee
- **THEN** el sistema responde **HTTP 403 Forbidden**

### Requirement: Validación de vigencia de roles

The system SHALL require a timezone-aware `vence_en` that is in the future when assigning a role, and SHALL reject timezone-naive or past values with HTTP 422.

#### Scenario: Vigencia válida

- **WHEN** se asigna un rol con `vence_en` con zona horaria y posterior al instante actual
- **THEN** la asignación es aceptada

#### Scenario: Vigencia sin zona horaria o en el pasado

- **WHEN** se asigna un rol con `vence_en` sin zona horaria o anterior al instante actual
- **THEN** el sistema responde **HTTP 422 Unprocessable Entity**

### Requirement: Autoprotección de administradores

The system SHALL prevent an administrator from revoking their own `ADMIN` role and from leaving the system with no active administrator, responding HTTP 409 in both cases.

#### Scenario: Auto-revocación de ADMIN

- **WHEN** un administrador intenta revocar su propia asignación de rol `ADMIN`
- **THEN** el sistema responde **HTTP 409 Conflict** y no modifica la asignación

#### Scenario: Último administrador vigente

- **WHEN** una revocación dejaría al sistema sin ningún administrador vigente
- **THEN** el sistema responde **HTTP 409 Conflict** y mantiene la asignación

### Requirement: Auditoría de eventos de seguridad

The system SHALL record a security event with actor and action for staff user creation, role assignment or revocation, and password changes.

#### Scenario: Alta de personal auditada

- **WHEN** un administrador crea un usuario de personal
- **THEN** se persiste un registro en `evento_seguridad` con el actor y la acción realizada

#### Scenario: Cambio de rol auditado

- **WHEN** se asigna o revoca un rol
- **THEN** se persiste un registro en `evento_seguridad` con el actor y la acción realizada

#### Scenario: Cambio de contraseña auditado

- **WHEN** un usuario cambia su contraseña
- **THEN** se persiste un registro en `evento_seguridad` con el actor y la acción realizada

### Requirement: Administración de usuarios y roles

The system SHALL expose administration endpoints for creating staff users, listing and mutating role assignments, and listing security events, restricted to users with an active `ADMIN` role.

#### Scenario: Administrador crea personal

- **WHEN** un administrador invoca `POST /usuarios` con datos válidos
- **THEN** el usuario es creado y la respuesta omite `password_hash`

#### Scenario: Consulta de roles de un usuario

- **WHEN** un administrador invoca `GET /usuarios/{id}/roles`
- **THEN** la respuesta devuelve las asignaciones de rol del usuario sin `password_hash`

#### Scenario: Asignación y revocación de rol

- **WHEN** un administrador asigna o revoca un rol válido sobre un usuario existente
- **THEN** la operación se persiste y se respeta la unicidad de asignaciones activas

#### Scenario: Usuario no administrador

- **WHEN** un usuario sin rol `ADMIN` invoca cualquiera de los endpoints de administración
- **THEN** el sistema responde **HTTP 403 Forbidden**

### Requirement: Listados administrativos paginados

The system SHALL return administrative listings, including security events and role assignments, using the standard pagination envelope.

#### Scenario: Listado de eventos de seguridad

- **WHEN** un administrador invoca `GET /eventos`
- **THEN** la respuesta usa el envoltorio `{items, total, page, size, pages}` con `page` por defecto 1 y `size` por defecto 20

#### Scenario: Página inexistente

- **WHEN** se solicita una página mayor a la última disponible en un listado administrativo
- **THEN** el sistema responde **HTTP 422 Unprocessable Entity**
