# Design: C-01 Foundation Setup

## Context
Ver motivación y problema en `proposal.md`. El proyecto inicia desde un repositorio vacío sin código fuente existente, requiriendo definir la estructura modular `src/`, el empaquetado de dependencias, la infraestructura contenerizada local y la suite de testing asíncrono para soportar los Capítulos 1 a 4 del Trabajo Práctico.

## Goals / Non-Goals

**Goals:**
- Estructurar el proyecto bajo una arquitectura modular limpia en `src/` (`core/`, `db/`, `api/v1/endpoints/`, `schemas/`).
- Proveer configuración tipada inmutable mediante `pydantic-settings` con lectura de `.env` y caching como singleton vía `get_settings()` decorado con `@lru_cache()`.
- Implementar la factoría asíncrona de base de datos con SQLAlchemy 2.0 (`create_async_engine`, `async_sessionmaker`, `AsyncSession`) y driver `asyncpg`.
- Configurar el ciclo de vida del servidor ASGI con `@asynccontextmanager` (FastAPI lifespan), con ping diagnóstico en startup y `engine.dispose()` en shutdown.
- Implementar los endpoints `/health`, `/health/live` y `/health/ready` con separación estricta de responsabilidades entre liveness y readiness.
- Diseñar `docker-compose.yml` para levantar PostgreSQL 16 y tests asíncronos reproducibles con `pytest-asyncio` y `httpx.ASGITransport`.

**Non-Goals:**
- Implementar entidades de negocio complejas o migraciones de tablas de dominio (pertenecen a `C-02` y fases posteriores).
- Autenticación mediante JWT o control de acceso RBAC a nivel de usuario.
- Interfaz gráfica o frontend web.

## Decisions

### Decisión 1: SQLAlchemy 2.0 Async + asyncpg
- **Elección**: Usar `create_async_engine` de SQLAlchemy 2.0 con driver nativo `asyncpg`.
- **Alternativas consideradas**: `psycopg2` sincrónico con `run_in_threadpool`, o `asyncpg` crudo sin ORM.
- **Razón**: SQLAlchemy 2.0 provee tipado estricto nativo (`Mapped`, `mapped_column`), sesiones asíncronas de primera clase (`AsyncSession`), y compatibilidad directa con Alembic para las fases siguientes sin penalizar el rendimiento del bucle de eventos.

### Decisión 2: Ciclo de vida ASGI Lifespan (`@asynccontextmanager`)
- **Elección**: Gestionar el ciclo de vida de FastAPI exclusivamente mediante un gestor de contexto asíncrono (`src/core/lifespan.py`).
- **Alternativas consideradas**: Decoradores `@app.on_event("startup")` y `@app.on_event("shutdown")`.
- **Razón**: Los eventos `on_event` están oficialmente deprecados en FastAPI/Starlette. El gestor de contexto unifica el ámbito de setup y teardown, asegurando la captura de excepciones y el cierre limpio de recursos (`await engine.dispose()`) incluso ante terminaciones abruptas.

### Decisión 3: Desacoplamiento de Liveness y Readiness
- **Elección**: Separar `/health/live` (vitalidad del proceso) de `/health/ready` (operatividad con base de datos con timeout de 2 segundos).
- **Alternativas consideradas**: Endpoint único `/health` con verificación obligatoria de base de datos.
- **Razón**: Evita fallos en cascada en orquestadores de contenedores (Docker / Kubernetes); si la base de datos experimenta latencia temporal, el contenedor no se reinicia agresivamente, sino que simplemente deja de recibir tráfico de negocio hasta recuperarse.

### Decisión 4: Configuración tipada con `pydantic-settings`
- **Elección**: Clase `Settings` heredando de `BaseSettings` con validación de tipos estricta y `.env`.
- **Alternativas consideradas**: `os.environ` o librerías desacopladas como `python-decouple`.
- **Razón**: Falla rápido (Fail-Fast) en tiempo de arranque si `DATABASE_URL` no cumple con el esquema `postgresql+asyncpg://` o faltan parámetros obligatorios.

## Risks / Trade-offs

- **[Riesgo] Ausencia de PostgreSQL local durante ejecución de tests**:
  - *Mitigación*: Proveer servicio `db` en `docker-compose.yml` y soporte en fixtures de `pytest` para mockear o saltar condicionalmente si no hay base viva, o utilizar fallback controlado.
- **[Riesgo] Fuga de conexiones por excepciones no capturadas en endpoints**:
  - *Mitigación*: Implementar `get_db()` como generador con bloque `try ... finally: await session.close()`.
- **[Riesgo] Timeout indefinido en consulta de readiness**:
  - *Mitigación*: Ejecutar `SELECT 1` envuelto en `asyncio.wait_for(..., timeout=settings.DB_TIMEOUT)` garantizando corte en 2 segundos y respuesta `503 Service Unavailable`.
