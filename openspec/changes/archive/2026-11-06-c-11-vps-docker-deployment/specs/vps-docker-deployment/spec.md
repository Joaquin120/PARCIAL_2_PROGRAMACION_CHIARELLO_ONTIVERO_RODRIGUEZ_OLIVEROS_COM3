# Spec Delta

## Purpose

Define el comportamiento verificable del empaquetado y despliegue del TP (Capítulos 1 a 4) en un contenedor Docker optimizado y seguro para VPS, incluyendo reportes de evidencia D-01 a D-08.

## ADDED Requirements

### Requirement: Multi-stage lightweight Alpine container image
El sistema SHALL compilar una imagen Docker basada en `python:3.12-alpine` utilizando multi-stage build, cuyo tamaño total final sea inferior a 100 megabytes (Criterio D-01).

#### Scenario: Image build size under threshold
- **WHEN** el operador ejecuta la compilación de la imagen Docker en `despliegue/`
- **THEN** la imagen resultante se construye exitosamente y `docker images` reporta un tamaño inferior a 100 MB

### Requirement: Non-root execution and credential isolation
El contenedor SHALL ejecutarse bajo un usuario sin privilegios `appuser` (Criterio D-07) y no SHALL contener archivos `.env` ni credenciales sensibles dentro de las capas de la imagen (Criterio D-06).

#### Scenario: Execution as unprivileged user
- **WHEN** se ejecuta el contenedor en runtime y se consulta el usuario activo con `whoami` o `id`
- **THEN** el sistema reporta `appuser` con UID distinto de cero (no root)

#### Scenario: Secrets and env file absence
- **WHEN** se inspecciona el sistema de archivos del contenedor o el historial de capas
- **THEN** no existe ningún archivo `.env` ni secretos embebidos en el contenedor

### Requirement: Automated database migrations on startup
El contenedor SHALL ejecutar automáticamente la aplicación de migraciones pendientes de base de datos (`alembic upgrade head`) a través del script de inicio antes de comenzar a servir tráfico HTTP (Criterio D-03).

#### Scenario: Automated migration execution
- **WHEN** el contenedor inicia conectado a una base de datos PostgreSQL
- **THEN** el script de inicio aplica las migraciones de Alembic y levanta Uvicorn sin errores

### Requirement: Native Docker health check monitoring
El contenedor SHALL definir una directiva `HEALTHCHECK` que consulte periódicamente el endpoint `/health/ready` utilizando herramientas nativas como `wget` (Criterio D-02).

#### Scenario: Container readiness healthcheck passes
- **WHEN** la aplicación y la base de datos se encuentran operativas tras el inicio
- **THEN** el comando `docker ps` o `docker inspect` reporta el estado del contenedor como `healthy`

### Requirement: External configuration via environment file
El contenedor SHALL ser configurable exclusivamente mediante variables de entorno inyectadas en tiempo de ejecución utilizando `docker run --env-file` (Criterio D-04).

#### Scenario: Runtime configuration injection
- **WHEN** el contenedor se inicia con `docker run --env-file <archivo-env>`
- **THEN** la aplicación lee la configuración sin requerir archivos dentro de la imagen

### Requirement: Structured deployment evidence documentation
El despliegue SHALL incluir un documento `DEPLOY.md` en `despliegue/evidencia/` que registre los comandos ejecutados y las salidas de terminal correspondientes a las verificaciones D-01 a D-08.

#### Scenario: Evidence document presence
- **WHEN** se audita el directorio `despliegue/evidencia/`
- **THEN** existe el archivo `DEPLOY.md` con los registros y salidas verificadas de D-01 a D-08
