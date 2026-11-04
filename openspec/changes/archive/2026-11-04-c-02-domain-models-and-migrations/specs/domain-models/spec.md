# Spec Delta: Domain Models

## Purpose
Provee la definición de entidades de dominio fuertemente tipadas con soporte de auditoría temporal y convenciones relacionales unificadas.

## ADDED Requirements

### Requirement: Mapeo tipado y herencia declarativa
The system SHALL / El sistema DEBE definir entidades de negocio heredando de la base declarativa unificada con anotaciones de tipo nativas y validación de nulabilidad.

#### Scenario: Instanciación de entidad con atributos requeridos
- **WHEN** un servicio crea una instancia de una entidad de dominio con todos sus campos obligatorios provistos
- **THEN** la entidad expone atributos tipados y válidos listos para su persistencia

#### Scenario: Rechazo por omisión de clave o tipo incompatible
- **WHEN** se intenta persistir una entidad omitiendo restricciones requeridas o con tipos inválidos
- **THEN** la base de datos o la capa de mapeo rechaza la operación garantizando la integridad de los datos

### Requirement: Campos estándar de auditoría temporal
The system SHALL / El sistema DEBE incorporar en las entidades de dominio marcas temporales de creación y actualización gestionadas automáticamente.

#### Scenario: Registro automático de marcas de tiempo en inserción
- **WHEN** una entidad es creada y persistida en la base de datos
- **THEN** el sistema asigna automáticamente la marca de tiempo de creación y actualización al instante actual
