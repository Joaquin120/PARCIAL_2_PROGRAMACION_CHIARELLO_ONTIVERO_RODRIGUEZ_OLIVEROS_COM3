# Spec Delta: System Verification

## Purpose
Garantiza la confiabilidad, resiliencia y aislamiento del sistema mediante suites de verificación End-to-End (E2E), pruebas de tolerancia a fallos y fixtures compartidos de pruebas.

## ADDED Requirements

### Requirement: Flujo End-to-End integral de la aplicación
The system SHALL / El sistema DEBE validar de extremo a extremo el ciclo de vida del backend, incluyendo los probes de salud, la creación de recursos, su consulta paginada, actualización y eliminación.

#### Scenario: Ejecución de flujo E2E completo
- **WHEN** se ejecuta una secuencia E2E comenzando por `/health/live`, `/health/ready`, seguido de creación, consulta, actualización y eliminación de un ítem
- **THEN** todos los pasos responden con códigos de estado HTTP exitosos (200, 201, 204) reflejando las transformaciones de estado esperadas

### Requirement: Resiliencia y tolerancia a fallos en readiness
The system SHALL / El sistema DEBE diagnosticar la indisponibilidad de la base de datos y degradar el endpoint `/health/ready` a HTTP 503 ante fallas de conexión o tiempos de espera agotados.

#### Scenario: Degeneración a 503 ante interrupción de base de datos
- **WHEN** se consulta `/health/ready` y la conexión con PostgreSQL arroja un error de comunicación
- **THEN** el sistema responde con código HTTP 503 Service Unavailable reportando estado desconectado

#### Scenario: Degeneración a 503 ante timeout de consulta
- **WHEN** la consulta de verificación de PostgreSQL excede el tiempo límite de 2.0 segundos
- **THEN** el sistema aborta la espera y responde con código HTTP 503 Service Unavailable

### Requirement: Aislamiento transaccional en pruebas
The system SHALL / El sistema DEBE proveer fixtures asíncronos que aseguren aislamiento determinístico y prevengan efectos colaterales entre pruebas concurrentes o sucesivas.

#### Scenario: Reversión y aislamiento de estado entre pruebas
- **WHEN** un caso de prueba inserta, muta o elimina registros en la capa de datos
- **THEN** los tests subsecuentes inician con un contexto de datos limpio sin rastros de ejecuciones previas
