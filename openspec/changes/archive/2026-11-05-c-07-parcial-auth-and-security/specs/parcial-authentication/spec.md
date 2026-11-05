# Spec Delta

## Purpose

Gestiona el registro, el inicio y el cierre de sesión mediante cookies HttpOnly firmadas con JWT, aplicando límite de contraseña, rate limiting y mitigación de timing attacks.

## ADDED Requirements

### Requirement: Registro atómico de clientes

The system SHALL create a user, an active `CLIENTE` role assignment, and a linked customer record atomically during registration, rejecting duplicate emails.

#### Scenario: Registro exitoso de un cliente

- **WHEN** se envía `POST /auth/registro` con email no registrado, nombre y contraseña válida
- **THEN** se crean en una sola transacción el `Usuario`, su asignación de rol `CLIENTE` y su ficha `Cliente`, y la respuesta no incluye `password_hash`

#### Scenario: Email ya registrado

- **WHEN** se envía `POST /auth/registro` con un email que ya existe
- **THEN** el sistema responde **HTTP 409 Conflict** sin crear registros parciales

### Requirement: Límite de 72 bytes en contraseñas de entrada

The system SHALL reject any input password whose UTF-8 byte length exceeds 72 bytes with HTTP 422 and MUST never surface a server error for that case.

#### Scenario: Contraseña dentro del límite

- **WHEN** se envía una contraseña cuya longitud en bytes UTF-8 es menor o igual a 72
- **THEN** la validación del contrato continúa y la petición no es rechazada por longitud

#### Scenario: Contraseña que excede los 72 bytes

- **WHEN** se envía una contraseña cuya longitud en bytes UTF-8 es mayor a 72
- **THEN** el sistema responde **HTTP 422 Unprocessable Entity**, nunca **HTTP 500**

### Requirement: Contratos de entrada estrictos

The system SHALL reject any unexpected field in authentication request bodies with HTTP 422 and SHALL never include `password_hash` in any response.

#### Scenario: Campo inesperado en el cuerpo

- **WHEN** una petición de autenticación incluye un campo no declarado en su DTO
- **THEN** el sistema responde **HTTP 422 Unprocessable Entity**

#### Scenario: Respuesta sin hash de contraseña

- **WHEN** cualquier endpoint de autenticación devuelve datos de usuario
- **THEN** la respuesta omite el campo `password_hash`

### Requirement: Cálculo de hash fuera del event loop y antes de la transacción

The system SHALL compute and verify bcrypt hashes off the event loop under a concurrency limit and before opening database transactions.

#### Scenario: Hash de contraseña en registro y login

- **WHEN** se registra un usuario o se verifica una credencial
- **THEN** el cálculo bcrypt se ejecuta fuera del event loop, limitado por un semáforo de concurrencia y antes de iniciar la transacción de base de datos

### Requirement: Rate limiting de intentos de login

The system SHALL count failed login attempts per `(email, ip)` in the last 60 seconds and reject the request before hashing when the count reaches the threshold.

#### Scenario: Límite de intentos alcanzado

- **WHEN** existen 5 o más intentos fallidos para el par `(email, ip)` en los últimos 60 segundos
- **THEN** el sistema responde **HTTP 429 Too Many Requests** con encabezado `Retry-After: 60` sin calcular bcrypt

#### Scenario: Intentos por debajo del límite

- **WHEN** existen menos de 5 intentos fallidos en los últimos 60 segundos
- **THEN** la petición continúa con la verificación normal de credenciales

### Requirement: Mitigación de timing attack con email inexistente

The system SHALL verify the submitted password against a precomputed fictitious hash when the email does not exist, returning the same generic error and comparable timing as an invalid password.

#### Scenario: Login con email inexistente

- **WHEN** se intenta iniciar sesión con un email que no existe
- **THEN** el sistema calcula bcrypt contra el hash ficticio precomputado y responde **HTTP 401 Unauthorized** con el mismo mensaje genérico que una contraseña incorrecta

### Requirement: Sesión exclusiva en cookie HttpOnly

The system SHALL issue the JWT exclusively in an `access_token` cookie with `HttpOnly`, `SameSite=Lax`, `Max-Age` and configurable `Secure`, and SHALL reject bearer headers or absent cookies.

#### Scenario: Login exitoso emite cookie

- **WHEN** las credenciales son válidas y el usuario está activo
- **THEN** la respuesta establece la cookie `access_token` con las directivas requeridas y el cuerpo no contiene el token

#### Scenario: Intento de autenticación por encabezado Bearer

- **WHEN** una petición protegida envía `Authorization: Bearer ...` en lugar de la cookie de sesión
- **THEN** el sistema responde **HTTP 401 Unauthorized**

#### Scenario: Petición sin cookie de sesión

- **WHEN** una petición a un endpoint que requiere sesión no incluye la cookie `access_token`
- **THEN** el sistema responde **HTTP 401 Unauthorized**

#### Scenario: Cierre de sesión

- **WHEN** se invoca `POST /auth/logout`
- **THEN** la cookie de sesión es removida y el cliente queda sin credencial válida

### Requirement: Cambio de contraseña con marca pendiente

The system SHALL allow an authenticated user with `debe_cambiar_password = true` to change their password and clear the pending flag on success.

#### Scenario: Usuario obligado a cambiar contraseña

- **WHEN** un usuario autenticado con `debe_cambiar_password = true` invoca `POST /auth/cambiar-password` con una contraseña válida
- **THEN** la contraseña es actualizada, la marca `debe_cambiar_password` pasa a `false` y se registra el evento de seguridad correspondiente

### Requirement: Consulta del usuario autenticado

The system SHALL expose the authenticated user's identity together with their currently valid roles and the informational roles carried by the token.

#### Scenario: Consulta de identidad

- **WHEN** un usuario autenticado invoca `GET /auth/yo`
- **THEN** la respuesta incluye sus datos, sus roles vigentes consultados en base de datos y los roles informativos del token, sin `password_hash`

### Requirement: Persistencia aislada de intentos de acceso

The system SHALL persist every login attempt in an independent session and transaction with a forced commit so the record survives a failed login rollback.

#### Scenario: Intento fallido registrado

- **WHEN** un login falla y la transacción principal se revierte
- **THEN** el registro correspondiente en `intento_acceso` permanece persistido con el email, la IP, el instante y el resultado

#### Scenario: Intento exitoso registrado

- **WHEN** un login finaliza correctamente
- **THEN** se persiste un registro exitoso en `intento_acceso` asociado al mismo email e IP
