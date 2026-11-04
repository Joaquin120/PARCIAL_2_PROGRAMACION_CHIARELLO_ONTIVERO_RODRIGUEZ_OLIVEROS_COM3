# Design: C-03 Business API Endpoints

## Context
Ver motivación y problema en `proposal.md`. Con `C-01` y `C-02` completados, el proyecto cuenta con el modelo `Item` en `src/db/models/item.py`, la factoría de sesiones `get_db()` y las migraciones de base de datos listas. Se requiere implementar la capa de esquemas Pydantic y los controladores REST para exponer las operaciones del dominio sobre la entidad `Item`.

## Goals / Non-Goals

**Goals:**
- Definir esquemas Pydantic v2 en `src/schemas/item.py` (`ItemCreate`, `ItemUpdate`, `ItemResponse`, `ItemListResponse`) con validaciones de tipos y rangos (`price >= 0`, `stock >= 0`).
- Implementar controlador REST en `src/api/v1/endpoints/items.py` montado bajo el prefijo `/api/v1/items` en `src/api/router.py`.
- Inyectar sesiones asíncronas mediante `Depends(get_db)` y ejecutar consultas con SQLAlchemy 2.0 (`select`, `execute`, `commit`, `refresh`).
- Manejar respuestas HTTP canónicas: `201 Created` para inserciones, `200 OK` para consultas y modificaciones, `204 No Content` para eliminaciones, y `404 Not Found` ante recursos inexistentes.
- Implementar paginación (`skip: int = 0`, `limit: int = 100`) y filtrado opcional (`is_active: bool | None = None`).
- Desarrollar pruebas unitarias de esquemas y pruebas de integración de endpoints con `httpx.AsyncClient`.

**Non-Goals:**
- Autenticación y control de acceso RBAC.
- Interfaces de usuario gráficas o frontend web.
- Procesamiento en segundo plano con colas de tareas (Celery/Redis).

## Decisions

### Decisión 1: Serialización directa ORM con `from_attributes=True`
- **Elección**: Configurar `model_config = ConfigDict(from_attributes=True)` en los esquemas de respuesta Pydantic.
- **Alternativas consideradas**: Mapear manualmente cada campo de la entidad al modelo de datos en el endpoint.
- **Razón**: Aprovecha la compatibilidad nativa entre SQLAlchemy 2.0 y Pydantic v2, reduciendo código repetitivo y garantizando tipado consistente.

### Decisión 2: Consultas asíncronas nativas de SQLAlchemy 2.0
- **Elección**: Usar `select(Item).where(...)` con `await db.execute(...)` y `result.scalar_one_or_none()`.
- **Alternativas consideradas**: `db.query(Item)` sincrónico o métodos legacy de SQLAlchemy 1.x.
- **Razón**: Respeta estrictamente la regla RN-SES-01 y las pautas duras del proyecto para no bloquear el event loop.

### Decisión 3: Restricción de paginación por defecto
- **Elección**: Parámetros de consulta `skip: int = Query(0, ge=0)` y `limit: int = Query(10, ge=1, le=100)`.
- **Alternativas consideradas**: Devolver todos los registros sin límite.
- **Razón**: Protege la memoria del servidor y el ancho de banda ante colecciones extensas de registros.

## Risks / Trade-offs

- **[Riesgo] Actualizaciones parciales modifican campos no deseados**:
  - *Mitigación*: Utilizar `ItemUpdate` con todos los campos opcionales (`None`) y aplicar `item_data.model_dump(exclude_unset=True)` al actualizar la entidad ORM.
- **[Riesgo] Violación de constraints de unicidad o tipo en base de datos**:
  - *Mitigación*: Validación preventiva a nivel de esquema Pydantic antes de alcanzar la capa de persistencia y captura controlada de excepciones de integridad.
