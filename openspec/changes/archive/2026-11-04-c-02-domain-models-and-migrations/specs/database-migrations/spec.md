# Spec Delta: Database Migrations

## Purpose
Provee la gestión evolutiva, versionado y ejecución asíncrona de cambios en el esquema relacional de la base de datos de forma idempotente y reproducible.

## ADDED Requirements

### Requirement: Inicialización y ejecución asíncrona de migraciones
The system SHALL / El sistema DEBE proveer herramientas de migración configuradas para ejecutar scripts de evolución de esquema de forma asíncrona sobre PostgreSQL.

#### Scenario: Aplicación exitosa de migraciones pendientes
- **WHEN** el operador ejecuta el comando de actualización a la última versión disponible
- **THEN** el sistema aplica secuencialmente todas las revisiones pendientes y actualiza el identificador de versión en la base de datos

#### Scenario: Reversión controlada de migración
- **WHEN** el operador solicita revertir una revisión previa
- **THEN** el sistema deshace los cambios estructurales correspondientes y restaura la versión anterior del esquema sin pérdida de consistencia

### Requirement: Sincronización automática de metadatos de modelos
The system SHALL / El sistema DEBE sincronizar el catálogo de metadatos declarativos de los modelos del dominio para la detección automática de diferencias de esquema.

#### Scenario: Detección de nuevas entidades declaradas
- **WHEN** se genera una nueva revisión de migración tras definir un modelo en el dominio
- **THEN** el sistema detecta las nuevas tablas y columnas reflejándolas en el archivo de migración resultante
