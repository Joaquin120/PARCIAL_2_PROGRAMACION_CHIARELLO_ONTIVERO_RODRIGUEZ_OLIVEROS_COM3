# Tasks: C-01 Foundation Setup

## 1. Setup e Infraestructura Base

- [x] 1.1 Crear estructura de directorios modular en `src/` (`core/`, `db/`, `api/v1/endpoints/`, `schemas/`) y `tests/` (`unit/`, `integration/`), verificando la existencia de archivos `__init__.py`.
- [x] 1.2 Configurar archivo de dependencias `pyproject.toml` o `requirements.txt` (`fastapi`, `uvicorn`, `pydantic-settings`, `sqlalchemy`, `asyncpg`, `pytest`, `pytest-asyncio`, `httpx`) y verificar exclusiones en `.gitignore` (`.env`, `__pycache__`, `.pytest_cache`).
- [x] 1.3 Crear plantilla `.env.example` y manifiesto `docker-compose.yml` para PostgreSQL 16 Alpine, verificando el inicio local del contenedor con `docker compose config`.

## 2. Configuración Tipada (Core Configuration)

- [x] 2.1 Implementar modelo `Settings` en `src/core/config.py` usando `pydantic-settings` (`SettingsConfigDict`) y función singleton `get_settings()` decorada con `@lru_cache()`.
- [x] 2.2 Escribir suite de pruebas unitarias en `tests/unit/test_config.py` y verificar que pasen los tests de carga exitosa y fallo rápido (`ValidationError`) ante `DATABASE_URL` ausente o inválida.

## 3. Capa de Persistencia Asíncrona (Async Persistence)

- [x] 3.1 Implementar `DeclarativeBase` con convención de nombrado estandarizada de constraints e índices en `src/db/base.py`.
- [x] 3.2 Implementar inicialización de `create_async_engine`, factoría `async_sessionmaker` y generador inyectable `get_db()` en `src/db/session.py`.
- [x] 3.3 Escribir tests unitarios en `tests/unit/test_session.py` y verificar el aislamiento de sesión y el cierre garantizado en bloque `finally`.

## 4. Ciclo de Vida Lifespan (Application Lifecycle)

- [x] 4.1 Implementar gestor de ciclo de vida `@asynccontextmanager` en `src/core/lifespan.py` ejecutando ping asíncrono (`SELECT 1`) en startup y `engine.dispose()` en shutdown.
- [x] 4.2 Inicializar la instancia principal de `FastAPI` en `src/main.py` vinculando el parámetro `lifespan`.
- [x] 4.3 Escribir tests de integración en `tests/integration/test_lifespan.py` verificando el arranque correcto y la captura de errores ante base de datos inaccesible.

## 5. Sondas de Diagnóstico (Health Probes)

- [x] 5.1 Definir modelos Pydantic de respuesta en `src/schemas/health.py` (`HealthStatusResponse`, `ReadinessResponse`).
- [x] 5.2 Implementar endpoints `GET /health`, `GET /health/live` y `GET /health/ready` (con consulta `SELECT 1` y timeout de 2 segundos) en `src/api/v1/endpoints/health.py` y agregador en `src/api/router.py`.
- [x] 5.3 Escribir tests de integración en `tests/integration/test_health.py` verificando código 200 en liveness, y respuestas 200 OK y 503 Service Unavailable en readiness.

## 6. Verificación Integral y Documentación

- [x] 6.1 Configurar `tests/conftest.py` con fixtures asíncronas utilizando `httpx.AsyncClient` con `ASGITransport(app=app)`.
- [x] 6.2 Ejecutar la suite completa de pruebas con `pytest -v` verificando 100% de tests pasando en verde.
- [x] 6.3 Actualizar `README.md` del proyecto con instrucciones de inicio rápido, arranque con Docker Compose y comandos de ejecución de tests.

## Workflow follow-up

- Ejecutar `/opsx-apply` para iniciar la implementación de las tareas.
- Al finalizar la implementación, archivar el change con `/opsx-archive c-01-foundation-setup`.
- Marcar como completado el checkbox de `C-01` en `CHANGES.md`.
