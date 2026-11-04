# Proposal: C-01 Foundation Setup

## Why
El proyecto requiere establecer los cimientos técnicos y arquitectónicos para un backend asíncrono robusto en FastAPI, garantizando que la configuración sea inmutable y validada en tiempo de arranque, que el acceso a PostgreSQL sea completamente asíncrono y no bloqueante mediante SQLAlchemy 2.0 y asyncpg, que los recursos se gestionen de forma atómica a través del ciclo de vida ASGI Lifespan, y que se expongan sondas de salud (liveness y readiness) para diagnóstico operativo continuo.

## What Changes
- Creación de la estructura base modular del backend bajo el directorio `src/` (`core/`, `db/`, `api/v1/endpoints/`, `schemas/`).
- Implementación de configuración centralizada con `pydantic-settings` (`Settings`, `get_settings()` decorado con `@lru_cache()`), validación estricta de `DATABASE_URL` y variables de entorno tipadas.
- Configuración de la capa de persistencia asíncrona con SQLAlchemy 2.0 (`create_async_engine`, `async_sessionmaker`, `DeclarativeBase` y generador inyectable `get_db()`).
- Implementación del ciclo de vida de la aplicación mediante gestor de contexto asíncrono `@asynccontextmanager` (ASGI Lifespan) en `src/core/lifespan.py`, con comprobación de conexión (`SELECT 1`) en el startup y liberación limpia del pool (`await engine.dispose()`) en el shutdown.
- Exposición de endpoints de salud en `src/api/v1/endpoints/health.py`:
  - `GET /health` y `GET /health/live`: Liveness probe inmediato que reporta la operatividad del servidor web.
  - `GET /health/ready`: Readiness probe que evalúa activamente la conectividad con PostgreSQL y responde `503 Service Unavailable` ante fallas o timeouts.
- Configuración de entorno de infraestructura local contenerizada mediante `docker-compose.yml` para PostgreSQL 16 Alpine.
- Suite de tests unitarios y de integración con `pytest`, `pytest-asyncio` y `httpx.AsyncClient` con `ASGITransport`.

## Capabilities

### New Capabilities
- `core-configuration`: Carga y validación tipada de configuraciones en tiempo de booteo desde variables de entorno y archivos `.env` mediante `pydantic-settings`.
- `async-persistence`: Gestión de pool de conexiones asíncronas a PostgreSQL mediante SQLAlchemy 2.0 y driver `asyncpg`, con sesiones aisladas por petición (`get_db`).
- `application-lifecycle`: Manejo del ciclo de vida del servidor ASGI con `@asynccontextmanager`, garantizando verificación de dependencias en el startup y liberación graciosa en el shutdown.
- `health-probes`: Sondas de diagnóstico HTTP independientes para vitalidad del proceso (liveness) y disponibilidad operativa de la base de datos (readiness).

### Modified Capabilities
*(Ninguna; este cambio inaugura las especificaciones del sistema).*

## Impact
- **Código**: Establece la base de código sobre `src/` y `tests/`.
- **Dependencias**: Incorpora `fastapi`, `uvicorn`, `pydantic-settings`, `sqlalchemy`, `asyncpg`, `pytest`, `pytest-asyncio`, `httpx`.
- **Infraestructura**: Define servicio PostgreSQL 16 en `docker-compose.yml` y archivo `.env.example`.
- **APIs**: Publica las rutas `/health`, `/health/live` y `/health/ready`.
