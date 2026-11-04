# health-probes Specification

## Purpose
Expone interfaces de diagnóstico HTTP para verificar de forma independiente la vitalidad inmediata del servidor web y la preparación operativa de sus dependencias críticas de base de datos.

## Requirements

### Requirement: Sonda de vitalidad (Liveness Probe)
The system SHALL / El sistema DEBE proveer un endpoint HTTP para verificar de manera inmediata que el proceso del servidor web está activo y respondiendo solicitudes, sin acoplamiento a dependencias externas.

#### Scenario: Consulta de vitalidad con proceso activo
- **WHEN** un cliente o monitor realiza una petición GET a la ruta de vitalidad (`/health` o `/health/live`)
- **THEN** el sistema responde con código HTTP 200 OK y confirmación de estado activo

### Requirement: Sonda de preparación (Readiness Probe)
The system SHALL / El sistema DEBE proveer un endpoint HTTP que compruebe activamente la conectividad con la base de datos PostgreSQL y reporte su estado con control de timeout.

#### Scenario: Base de datos disponible y operativa
- **WHEN** un cliente o balanceador realiza una petición GET a `/health/ready` y la base de datos responde dentro del timeout
- **THEN** el sistema responde con código HTTP 200 OK indicando estado de preparación satisfactorio

#### Scenario: Base de datos inaccesible o timeout
- **WHEN** un cliente o balanceador realiza una petición GET a `/health/ready` y la base de datos está caída o supera el timeout límite
- **THEN** el sistema responde con código HTTP 503 Service Unavailable detallando la indisponibilidad
