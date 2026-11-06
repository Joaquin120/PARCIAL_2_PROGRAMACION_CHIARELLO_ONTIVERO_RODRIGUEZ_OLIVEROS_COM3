# Proposal: C-05 Parcial Core UoW

## Why

El Trabajo Práctico (Capítulos 1 a 4) concluyó exitosamente proveyendo la arquitectura base en `src/`. Para abordar los requerimientos del Parcial (Capítulos 1 a 6) sin alterar el código que será desplegado en el VPS (`despliegue/`), es necesario asentar una nueva base modular en `parcial/app/core/`. Esta base debe introducir de forma estricta las reglas no negociables de la consigna: flujo `Router -> Service -> Unit of Work -> Repository -> Model`, un Unit of Work que no cree ni cierre sesiones físicas (compartiendo la conexión inyectada), repositorios que deleguen la confirmación mediante `flush()`, paginación uniforme con rechazo 422 en desbordes, mitigación de timing attacks en el ciclo de vida y división estructural de grupos de rutas abiertas y protegidas.

## What Changes

- Creación del árbol modular del Parcial en `parcial/app/core/` y `parcial/tests/unit/`.
- Configuración centralizada tipada en `parcial/app/core/config.py` con lectura de variables individuales de PostgreSQL (`POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.), propiedad `@computed_field` para `DATABASE_URL` asíncrona, costo configurable de bcrypt y fail-fast en arranque.
- Infraestructura de persistencia asíncrona en `parcial/app/core/database.py` con `AsyncEngine`, `async_sessionmaker(expire_on_commit=False)` y generador inyectable `get_session`.
- Implementación de patrones de acceso a datos en `parcial/app/core/repository.py`:
  - `BaseRepository[T]` con operaciones asíncronas (`get_by_id`, `get_all`, `count`, `add`, `update`, `delete`) donde `add` y `update` ejecutan exclusivamente `flush()`, nunca `commit()`.
  - `SoftDeleteRepository[T]` que filtra por defecto registros con `borrado_en IS NULL` y soporta borrado lógico.
- Implementación del patrón Unit of Work en `parcial/app/core/unit_of_work.py`:
  - Recibe la sesión inyectada por FastAPI sin crear ni cerrar la sesión física.
  - Context manager asíncrono que ejecuta `commit()` al completar el bloque y `rollback()` ante excepciones no controladas.
- Paginación uniforme en `parcial/app/core/paginacion.py`:
  - Envoltorio genérico `PaginatedResponse[T]` `{items, total, page, size, pages}` con tamaño default de 20.
  - Validación de bordes: `total == 0` retorna `pages = 1`, y si `page > pages` se rechaza con **HTTP 422 Unprocessable Entity**.
- Ciclo de vida y grupos de rutas en `parcial/app/main.py`:
  - Lifespan asíncrono con precálculo de `app.state.fictitious_password_hash` con bcrypt y disposición del pool en shutdown.
  - Estructuración de rutas: Grupo Abierto (health, auth, catálogo) y Grupo Protegido (custodiado por verificación de `debe_cambiar_password == false` con HTTP 403).
- Pruebas unitarias en `parcial/tests/unit/` para UoW, repositorios, paginación, lifespan y configuración.

## Capabilities

### New Capabilities
- `parcial-unit-of-work`: Define el patrón Unit of Work que no administra la vida física de la sesión y los repositorios base limitados a `flush()`, junto al soporte de soft-delete.
- `uniform-pagination`: Define el contrato estándar de paginación `{items, total, page, size, pages}` y las reglas de validación de desborde y colecciones vacías.
- `parcial-application-core`: Define la configuración tipada del Parcial, ciclo de vida con mitigación de timing attacks en login y división entre rutas abiertas y protegidas.

### Modified Capabilities
<!-- No se modifican capacidades existentes del TP -->

## Impact

- **Código nuevo**: Directorios `parcial/app/core/`, `parcial/app/main.py` y `parcial/tests/unit/`.
- **Compatibilidad**: Mantiene intacto el código de `src/` y `tests/` correspondiente al TP original.
- **Rutas de la API**: Configuración de routers abiertos y protegidos listos para los módulos subsiguientes (usuarios, libros, ventas).
