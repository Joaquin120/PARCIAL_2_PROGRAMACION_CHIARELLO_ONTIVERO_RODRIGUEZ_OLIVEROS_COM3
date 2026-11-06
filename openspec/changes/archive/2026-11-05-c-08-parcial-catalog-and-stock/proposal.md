# Proposal

## Why

El sistema requiere exponer el catálogo de libros y entidades auxiliares (autores, editoriales y géneros) para consulta pública paginada y filtrada, así como la gestión administrativa de libros y stock restringida al rol `ADMIN`. Esto garantiza el borrado lógico de libros sin pérdida de historial y asegura que el stock sólo pueda mutar mediante movimientos auditables de tipo append-only.

## What Changes

- Exposición del catálogo público paginado en `GET /libros` con filtros opcionales por título y género, excluyendo libros dados de baja (`borrado_en IS NOT NULL`).
- Endpoints de consulta de catálogos auxiliares: `GET /autores`, `GET /editoriales`, `GET /generos`, junto con sus relaciones filtradas `GET /autores/{id}/libros`, `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros`.
- Endpoint administrativo `POST /libros` (`ADMIN`): alta de libro con validación estricta de DTO (`extra="forbid"`), unicidad condicional de ISBN y creación atómica del primer movimiento de stock con motivo `'Stock inicial'` en el mismo Unit of Work.
- Endpoint administrativo `PATCH /libros/{id}` (`ADMIN`): modificación parcial de título y precio (`model_dump(exclude_unset=True)`), con rechazo estricto (**HTTP 422 Unprocessable Entity**) si la petición intenta alterar el stock directamente.
- Endpoint administrativo `DELETE /libros/{id}` (`ADMIN`): soft delete (`borrado_en = func.now()`) con respuesta **HTTP 204 No Content**, liberando el ISBN para nuevas altas y preservando las relaciones históricas.
- Endpoint administrativo `POST /libros/{id}/reponer` (`ADMIN`): incremento de stock registrando atómicamente un `MovimientoStock` con motivo `'Reposicion'`, con rechazo (**HTTP 409 Conflict**) si el libro se encuentra dado de baja.
- Endpoint administrativo `GET /libros/{id}/movimientos` (`ADMIN`): histórico de movimientos de stock con paginación uniforme `{items, total, page, size, pages}`.
- Implementación de `LibroRepository` sobre `SoftDeleteRepository` y repositorios auxiliares integrados con `UnitOfWork`.

## Capabilities

### New Capabilities
- `parcial-catalog`: Catálogo público y administrativo de libros, autores, editoriales y géneros con soft delete, paginación uniforme y filtros.
- `parcial-stock-management`: Mutación de stock mediante reposición y auditoría de movimientos append-only para libros del catálogo.

### Modified Capabilities
<!-- None -->

## Impact

- Código nuevo en `parcial/app/modules/libros/`: esquemas (`schemas.py`), repositorios (`repository.py`), servicios (`service.py`) y endpoints (`router.py`).
- Integración en `parcial/app/main.py`: montaje de rutas públicas de catálogo en `open_router` y rutas administrativas de libros y reposición en `protected_router` custodiadas por `requiere_rol("ADMIN")`.
- Cobertura de pruebas en `parcial/tests/unit/` y `parcial/tests/integration/` con PostgreSQL de test.
- Sin cambios de esquema de base de datos ni migraciones (las tablas `libro`, `autor`, `editorial`, `genero` y `movimiento_stock` fueron creadas en C-06).

