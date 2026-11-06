# Tasks: C-05 Parcial Core UoW

## 1. Configuración, Base Declarativa y Persistencia Asíncrona

- [x] 1.1 Implementar `parcial/app/core/config.py` con tipado `pydantic-settings`, lectura de `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`, `@computed_field` para `DATABASE_URL` asíncrona, costo configurable de bcrypt, singleton con `@lru_cache()` y verificar con `parcial/tests/unit/test_config.py`.
- [x] 1.2 Implementar `parcial/app/core/database.py` (`create_async_engine`, `async_sessionmaker`, dependencia inyectable `get_session`) y `parcial/app/core/base.py` con `DeclarativeBase` y convención de nombres, verificando con `parcial/tests/unit/test_database.py`.

## 2. Repositorios y Unit of Work

- [x] 2.1 Implementar `BaseRepository[T]` y `SoftDeleteRepository[T]` en `parcial/app/core/repository.py` garantizando que `add()` y `update()` ejecuten exclusivamente `await session.flush()`, verificando con `parcial/tests/unit/test_repository.py`.
- [x] 2.2 Implementar `UnitOfWork` en `parcial/app/core/unit_of_work.py` recibiendo la sesión física inyectada sin cerrarla, controlando `commit()` al completar y `rollback()` ante errores, verificando con `parcial/tests/unit/test_unit_of_work.py`.

## 3. Paginación Uniforme y Lifespan con Grupos de Rutas

- [x] 3.1 Implementar `parcial/app/core/paginacion.py` con esquema `PaginatedResponse[T]` `{items, total, page, size, pages}`, default `size=20`, validación `total == 0 -> pages = 1` y rechazo con HTTP 422 si `page > pages`, verificando con `parcial/tests/unit/test_paginacion.py`.
- [x] 3.2 Implementar `parcial/app/main.py` con `@asynccontextmanager` para Lifespan (cálculo de `app.state.fictitious_password_hash` con bcrypt, disposición del pool) y partición entre Grupo Abierto y Grupo Protegido (`debe_cambiar_password == false` con HTTP 403), verificando con `parcial/tests/unit/test_lifespan.py`.

## 4. Verificación Integral del Core

- [x] 4.1 Ejecutar suite completa de tests de `parcial/tests/unit/` verificando 100% de aserciones en verde y ausencia de regresiones en `tests/`.

## Workflow follow-up

- Ejecutar validación OpenSpec con `openspec validate c-05-parcial-core-uow`.
- Archivar el change con `openspec archive c-05-parcial-core-uow`.
- Marcar como completado el checkbox de `C-05` en `CHANGES.md`.
