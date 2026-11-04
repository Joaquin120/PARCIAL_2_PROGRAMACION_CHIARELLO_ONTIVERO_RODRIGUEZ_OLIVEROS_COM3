# Tasks: C-03 Business API Endpoints

## 1. Esquemas de Validación (Pydantic v2)

- [x] 1.1 Implementar esquemas `ItemBase`, `ItemCreate`, `ItemUpdate`, `ItemResponse` e `ItemListResponse` en `src/schemas/item.py` con validaciones de campos no negativos (`price >= 0`, `stock >= 0`) y configuración `from_attributes=True`.
- [x] 1.2 Escribir pruebas unitarias en `tests/unit/test_item_schemas.py` verificando validación estricta de tipos, restricciones de valor y serialización de modelos.

## 2. Controladores REST y Rutas de Negocio

- [x] 2.1 Implementar router en `src/api/v1/endpoints/items.py` con endpoints asíncronos para operaciones CRUD (`POST /`, `GET /`, `GET /{item_id}`, `PUT /{item_id}`, `PATCH /{item_id}`, `DELETE /{item_id}`) utilizando `Depends(get_db)` y SQLAlchemy 2.0.
- [x] 2.2 Montar el router de ítems en `src/api/router.py` bajo el prefijo `/api/v1/items` y tags correspondientes.
- [x] 2.3 Escribir suite de pruebas de integración en `tests/integration/test_items_api.py` verificando creación (201), consultas paginadas (200), actualización (200), eliminación (204), y errores (404, 422) con `httpx.AsyncClient`.

## 3. Verificación Integral y Documentación

- [x] 3.1 Ejecutar la suite completa de pruebas con `pytest -v` verificando 100% de tests pasando en verde.
- [x] 3.2 Actualizar `README.md` documentando el catálogo de endpoints de ítems, parámetros de consulta y ejemplos de payloads.

## Workflow follow-up

- Ejecutar `/opsx-apply` para iniciar la implementación de las tareas.
- Al finalizar la implementación, archivar el change con `/opsx-archive c-03-business-api-endpoints`.
- Marcar como completado el checkbox de `C-03` en `CHANGES.md`.
