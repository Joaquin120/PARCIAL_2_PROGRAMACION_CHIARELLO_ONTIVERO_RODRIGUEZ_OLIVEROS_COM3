# parcial-application-core Specification

## Purpose
Define la configuración centralizada, ciclo de vida con mitigación de timing attacks y segregación de rutas del Parcial.

## Requirements

### Requirement: Configuración tipada y fail-fast
The system SHALL validate all required database and security configuration on startup, failing immediately if any required credential is missing.

#### Scenario: Booteo con configuración válida
- **WHEN** el sistema arranca con las variables de base de datos y seguridad provistas
- **THEN** la configuración es cargada y se compone la URL de conexión asíncrona de PostgreSQL

### Requirement: Mitigación de timing attack en inicio
The application lifecycle SHALL precalculate a fictitious password hash in application state during startup to ensure constant-time response behavior.

#### Scenario: Precomputación de hash en lifespan
- **WHEN** la aplicación ejecuta su rutina de inicio (lifespan)
- **THEN** se almacena en el estado de la aplicación un hash de contraseña ficticia precalculado con bcrypt

### Requirement: Segregación entre grupos de rutas abiertas y protegidas

The system SHALL organize two route groups such that protected routes centrally verify that the user does not have a pending password change requirement, responding 401 when no valid session exists and 403 when the session is authenticated but the pending-password flag is true.

#### Scenario: Acceso a ruta abierta

- **WHEN** un cliente accede a endpoints públicos o de autenticación
- **THEN** la petición es procesada sin exigir la verificación previa de cambio de contraseña

#### Scenario: Acceso bloqueado en ruta protegida

- **WHEN** un usuario con marca `debe_cambiar_password = true` intenta acceder a una ruta del grupo protegido
- **THEN** el sistema rechaza la petición inmediatamente con HTTP 403 Forbidden

#### Scenario: Acceso sin sesión al grupo protegido

- **WHEN** una petición sin cookie de sesión válida intenta acceder a una ruta del grupo protegido
- **THEN** el sistema responde HTTP 401 Unauthorized antes de evaluar la marca de cambio de contraseña

#### Scenario: Autenticación operativa en el grupo abierto

- **WHEN** la aplicación monta los endpoints `/auth/registro`, `/auth/login`, `/auth/logout`, `/auth/yo` y `/auth/cambiar-password`
- **THEN** esas rutas se resuelven en el grupo abierto y quedan disponibles sin el gate de cambio de contraseña
