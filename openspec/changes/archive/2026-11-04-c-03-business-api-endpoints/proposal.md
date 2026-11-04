# Proposal: C-03 Business API Endpoints

## Why
Habiendo establecido la infraestructura de base de datos, los modelos declarativos y las migraciones con Alembic en C-01 y C-02, el sistema requiere exponer los endpoints de negocio para interactuar con las entidades del Trabajo Práctico. Sin controladores REST, esquemas de validación de entrada/salida con Pydantic y lógica de servicio con inyección de dependencias `get_db()`, el backend no cuenta con interfaces para que clientes externos gestionen los recursos del dominio.

## What Changes
- Definición de esquemas Pydantic v2 en `src/schemas/item.py` (`ItemBase`, `ItemCreate`, `ItemUpdate`, `ItemResponse`, `ItemListResponse`).
- Implementación de controladores REST en `src/api/v1/endpoints/items.py` montados en `src/api/router.py`:
  - `POST /api/v1/items`: Creación de un nuevo ítem con validación de precios y stock no negativos.
  - `GET /api/v1/items`: Listado de ítems con soporte de paginación (`skip`, `limit`) y filtrado por estado activo (`is_active`).
  - `GET /api/v1/items/{item_id}`: Consulta de un ítem por identificador con respuesta `404 Not Found` ante inexistencia.
  - `PUT /api/v1/items/{item_id}` / `PATCH /api/v1/items/{item_id}`: Actualización completa y parcial de un ítem.
  - `DELETE /api/v1/items/{item_id}`: Eliminación de un ítem con respuesta `204 No Content`.
- Inyección de dependencias asíncronas con `Depends(get_db)` y manejo transaccional explícito (`commit`, `rollback`, `refresh`).
- Manejo estructurado de errores y validaciones (`400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`).
- Suite de pruebas de integración con `httpx.AsyncClient` y `ASGITransport` probando casos de éxito y de error en `tests/integration/test_items_api.py`.

## Capabilities

### New Capabilities
- `item-management`: Endpoints REST para la creación, consulta paginada, actualización y eliminación de ítems con validación estricta y persistencia asíncrona.

### Modified Capabilities
*(Ninguna; las capacidades previas mantienen sus contratos intactos).*

## Impact
- **Código**: Nuevos esquemas en `src/schemas/item.py`, nuevo router en `src/api/v1/endpoints/items.py`, actualización de `src/api/router.py`.
- **Rutas de API**: Publica `/api/v1/items` y subrutas.
- **Testing**: Nuevas pruebas en `tests/integration/test_items_api.py` y `tests/unit/test_item_schemas.py`.
