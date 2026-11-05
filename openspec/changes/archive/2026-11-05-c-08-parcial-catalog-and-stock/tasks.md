# Tasks

## 1. DTOs and Schemas

- [x] 1.1 Implement Pydantic schemas for auxiliary catalogs (`AutorResponse`, `EditorialResponse`, `GeneroResponse`) with `model_config = ConfigDict(from_attributes=True, extra="forbid")` and verify schema unit tests
- [x] 1.2 Implement Pydantic schemas for Book operations (`LibroCreateRequest`, `LibroUpdateRequest`, `LibroResponse`, `LibroDetailResponse`) enforcing `extra="forbid"`, `stock_inicial >= 0`, and strictly omitting `stock` in `LibroUpdateRequest`, and verify schema validation unit tests
- [x] 1.3 Implement Pydantic schemas for stock operations (`ReponerStockRequest`, `MovimientoStockResponse`) enforcing `cantidad > 0` and `extra="forbid"`, and verify validation tests

## 2. Repositories and Data Access

- [x] 2.1 Implement `AutorRepository`, `EditorialRepository`, and `GeneroRepository` with listing and relation query methods, and verify repository unit tests
- [x] 2.2 Implement `LibroRepository` inheriting from `SoftDeleteRepository[Libro]` with eager loading (`joinedload`), title/genre filtering, `get_by_id_including_deleted`, and pessimistic locking (`with_for_update`), and verify repository tests
- [x] 2.3 Implement `MovimientoStockRepository` inheriting from `BaseRepository[MovimientoStock]` with paginated chronological ledger querying by book ID, and verify repository tests

## 3. Service Layer and Business Logic

- [x] 3.1 Implement catalog query services for authors, publishers, genres, and books with paginated envelope responses (`crear_respuesta_paginada`), and verify service unit tests
- [x] 3.2 Implement book creation service enforcing atomic creation of `Libro` and initial `MovimientoStock(motivo='Stock inicial')` within UoW, preventing duplicate active ISBN (409), and verify service tests
- [x] 3.3 Implement book update service applying `LibroUpdateRequest` metadata changes while strictly ignoring or failing on stock alterations, and verify service tests
- [x] 3.4 Implement soft delete service setting `borrado_en = func.now()` for active books, returning 404 if not found or already deleted, and verify soft delete and ISBN reactivation tests
- [x] 3.5 Implement restock service with pessimistic lock, rejecting deleted books with 409 Conflict, incrementing stock and recording `MovimientoStock(motivo='Reposicion')`, and verify restock tests

## 4. API Routers and Route Segregation

- [x] 4.1 Implement public open endpoints (`GET /libros`, `GET /autores`, `GET /editoriales`, `GET /generos`, `GET /autores/{id}/libros`, `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros`) on `open_router` and verify public API tests
- [x] 4.2 Implement protected administrative book endpoints (`POST /libros`, `PATCH /libros/{id}`, `DELETE /libros/{id}`) with `Depends(requiere_rol("ADMIN"))` and verify RBAC / forbidden / unauthorized tests
- [x] 4.3 Implement protected administrative stock endpoints (`POST /libros/{id}/reponer`, `GET /libros/{id}/movimientos`) with `Depends(requiere_rol("ADMIN"))` and verify stock API tests
- [x] 4.4 Mount routers in `parcial/app/main.py` and verify OpenAPI docs and endpoint accessibility

## 5. End-to-End & Invariant Integration Tests

- [x] 5.1 Implement integration tests for soft delete behavior and ISBN reuse (`test_catalog_soft_delete.py`) verifying active vs deleted book isolation and uniqueness constraints against PostgreSQL
- [x] 5.2 Implement integration tests for stock ledger balance invariant (`test_stock_invariant.py`) verifying `libro.stock == SUM(movimiento.cantidad)` across creation, multiple restocks, and rejected operations
- [x] 5.3 Run full test regression suite across all existing modules and new catalog/stock tests to ensure 100% pass rate

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result.

