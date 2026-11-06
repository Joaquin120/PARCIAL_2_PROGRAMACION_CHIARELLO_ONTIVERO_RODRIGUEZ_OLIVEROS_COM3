# Spec Delta: parcial-e2e-verification

## Purpose

Define el marco de verificación de extremo a extremo de los 16 casos de prueba canónicos del Parcial (C-01 a C-16), la validación a nivel motor de la inmutabilidad de movimientos de stock y la evidencia de ausencia de consultas N+1 en la lectura de ventas.

## ADDED Requirements

### Requirement: Verificación E2E de autenticación y sesiones seguras (C-01 a C-04)
The system SHALL / El sistema DEBE validar de extremo a extremo los casos C-01 a C-04: login exitoso con cookie HttpOnly `access_token` sin token en body, rechazo con HTTP 401 de solicitudes con `Authorization: Bearer` o sin cookie, rate limiting de 5 intentos fallidos en 60s con HTTP 429 y `Retry-After: 60`, y mitigación de timing attacks mediante hash ficticio con tiempos consistentes ante emails inexistentes.

#### Scenario: Ciclo E2E de autenticación y seguridad
- **WHEN** se ejecutan las peticiones de los casos C-01 a C-04
- **THEN** se comprueba el seteo estricto de cookie HttpOnly, el rechazo a Bearer, la activación del rate limiting tras 5 fallos y la consistencia temporal de respuestas 401

### Requirement: Verificación E2E de control de acceso y autorizaciones dinámicas (C-05 a C-07)
The system SHALL / El sistema DEBE validar los casos C-05 a C-07: bloqueo con HTTP 403 a usuarios con `debe_cambiar_password = true` en rutas protegidas y desbloqueo tras cambio de contraseña, evaluación dinámica de roles vigentes con denegación inmediata ante revocación (HTTP 403), y protección del sistema contra la auto-revocación del último administrador activo (HTTP 409).

#### Scenario: Evaluación de RBAC dinámico y autoprotección
- **WHEN** se prueban las peticiones de los casos C-05 a C-07
- **THEN** se deniega el acceso a rutas protegidas ante contraseña pendiente, las revocaciones de roles surten efecto inmediato y se impide eliminar al último administrador

### Requirement: Verificación E2E de contratos de entrada y paginación uniforme (C-08 y C-09)
The system SHALL / El sistema DEBE verificar los casos C-08 y C-09: rechazo con HTTP 422 de cualquier petición con campos no declarados en el esquema (`extra="forbid"`), y formato estricto de paginación `{items, total, page, size, pages}` con validación HTTP 422 si se solicita `page > pages` y retorno de 1 página con 0 resultados.

#### Scenario: Cumplimiento de contratos y paginación estándar
- **WHEN** se envían payloads con campos adicionales o se consultan páginas fuera de rango
- **THEN** la API responde HTTP 422 Unprocessable Entity y todas las respuestas válidas contienen el envoltorio estándar de 5 campos

### Requirement: Verificación E2E de catálogo y punto único de mutación de stock (C-10 y C-11)
The system SHALL / El sistema DEBE verificar los casos C-10 y C-11: creación de libros y reposición de stock mediante endpoints dedicados con actualización del invariante físico, y borrado lógico con HTTP 204 No Content que excluye el libro del catálogo público y libera su ISBN para nuevas altas.

#### Scenario: Mutación de stock y ciclo de vida de libro
- **WHEN** se dan de alta libros, se reponen existencias o se efectúa un soft delete
- **THEN** el stock físico se mantiene sincronizado con los movimientos y los libros borrados no aparecen en el catálogo pero preservan la integridad referencial

### Requirement: Verificación E2E de transacciones atómicas de venta y permisos (C-12, C-13 y C-16)
The system SHALL / El sistema DEBE verificar los casos C-12, C-13 y C-16: registro atómico de ventas con deducción de stock y aviso asíncrono en segundo plano, rollback íntegro y HTTP 409 ante falta de stock o libros dados de baja, y control granular de acceso en `GET /ventas/{id}` permitiendo lectura a personal y cliente titular y respondiendo HTTP 403 a clientes ajenos.

#### Scenario: Transacciones de venta y control de visibilidad
- **WHEN** se procesan ventas válidas, ventas que exceden el stock y consultas de detalle con diversos roles
- **THEN** la venta exitosa persiste atómicamente, la venta inviable se revierte completamente con 409 y el detalle respeta la titularidad del cliente

### Requirement: Verificación de disparador append-only y consultas fijas (C-14 y C-15)
The system SHALL / El sistema DEBE verificar a nivel de motor PostgreSQL que el trigger PL/pgSQL aborta cualquier operación `UPDATE` o `DELETE` sobre `movimiento_stock` (Caso C-14), y constatar que el endpoint `GET /ventas/{id}` resuelve el detalle con una cantidad constante de consultas SQL sin importar el número de renglones (Caso C-15).

#### Scenario: Inmutabilidad física y eficiencia de consultas
- **WHEN** se ejecutan sentencias UPDATE/DELETE contra movimiento_stock o se audita el tráfico SQL de GET /ventas/{id}
- **THEN** PostgreSQL rechaza las mutaciones de movimientos con error de trigger y el detalle de venta se resuelve con cantidad fija de queries
