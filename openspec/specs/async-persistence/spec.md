# async-persistence Specification

## Purpose
Provee infraestructura de persistencia transaccional y pool de conexiones asíncronas no bloqueantes a PostgreSQL, asegurando aislamiento de sesiones por petición y convención unificada de metadatos.

## Requirements

### Requirement: Conexión asíncrona no bloqueante
The system SHALL / El sistema DEBE administrar un pool de conexiones asíncronas hacia PostgreSQL ejecutando operaciones de I/O sin bloquear el bucle de eventos principal.

#### Scenario: Operación de persistencia asíncrona
- **WHEN** un componente ejecuta una operación o consulta sobre la base de datos
- **THEN** la operación se despacha de forma asíncrona a través del pool sin interrumpir otras tareas concurrentes

### Requirement: Aislamiento y ciclo de vida de sesión por petición
The system SHALL / El sistema DEBE suministrar una sesión de base de datos aislada para cada petición y garantizar su cierre liberando recursos al finalizar la ejecución.

#### Scenario: Petición con acceso a base de datos finalizada
- **WHEN** un endpoint HTTP completa su procesamiento o genera una excepción no controlada
- **THEN** la sesión asociada se cierra automáticamente y la conexión subyacente retorna al pool

### Requirement: Convención estandarizada de metadatos relacionales
The system SHALL / El sistema DEBE proveer una base declarativa con convención estricta de nombres para índices, claves foráneas y restricciones primarias.

#### Scenario: Definición de metadatos de persistencia
- **WHEN** se definen entidades o tablas en el esquema de persistencia
- **THEN** los constraints e índices generados respetan automáticamente las convenciones de nombrado del proyecto
