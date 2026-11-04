# 08 — Arquitectura Propuesta y Estructura de Directorios

## Patrones aplicados

| Patrón | Dónde se aplica | Justificación |
|---|---|---|
| **Dependency Injection** | `FastAPI Depends()` en endpoints (`get_db`, `get_settings`) | Desacopla la lógica de las rutas de la creación y ciclo de vida de los clientes de DB y configuración. |
| **Lifespan Context Manager** | `src/core/lifespan.py` con `@asynccontextmanager` | Estándar ASGI moderno de FastAPI para inicialización y liberación atómica de recursos. |
| **Settings Singleton Cacheado** | `src/core/config.py` con `@lru_cache()` | Garantiza lectura única de variables de entorno y validación estricta inmutable. |
| **Session Per Request** | `src/db/session.py` (`get_db` generator) | Aísla las transacciones por petición HTTP, evitando fugas de memoria o transacciones colgadas. |
| **Declarative Base unificada** | `src/db/base.py` | Centraliza metadatos y convención de nombres de constraints para migraciones futuras. |

## Estructura de directorios recomendada

```
.
├── .env.example                     # Plantilla de variables de entorno (versionada)
├── .env                             # Variables locales reales (ignorado en git)
├── .gitignore                       # Ignorados (.env, __pycache__, .pytest_cache)
├── docker-compose.yml               # PostgreSQL 16 para desarrollo y tests
├── pyproject.toml / requirements.txt# Dependencias del proyecto
├── README.md                        # Guía de inicio rápido y comandos
├── knowledge-base/                  # Base de conocimiento (10 archivos canónicos)
├── openspec/                        # Especificaciones OpenSpec (specs, changes)
│
├── src/
│   ├── __init__.py
│   ├── main.py                      # Punto de entrada de FastAPI y registro de routers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Settings con pydantic-settings
│   │   └── lifespan.py              # Gestor de ciclo de vida con asynccontextmanager
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                  # DeclarativeBase y metadatos
│   │   └── session.py               # AsyncEngine, async_sessionmaker y get_db()
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py                # Agregador de routers v1
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py        # Endpoints /health, /health/live, /health/ready
│   └── schemas/
│       ├── __init__.py
│       └── health.py                # Pydantic models para respuestas de salud
│
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Fixtures pytest, cliente HTTPX asíncrono
    ├── unit/
    │   └── test_config.py           # Tests de Settings y validación de tipos
    └── integration/
        ├── test_health.py           # Tests de endpoints /health, /health/ready
        └── test_lifespan.py         # Tests de arranque y shutdown gracioso
```

## Seguridad y Gestión de Secretos

- **Aislamiento de Entorno**: Las credenciales de base de datos (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`) residen en `.env` y variables de entorno del sistema operativo.
- **Fail-Secure**: Si una contraseña contiene caracteres especiales, la URL de SQLAlchemy debe formatearse adecuadamente. Si falta un parámetro, la aplicación se rehúsa a iniciar.
- **Prevención de Data Leaks**: Los endpoints `/health` no exponen datos sensibles (contraseñas, hosts internos o stacktraces completos de fallas de base de datos) en las respuestas HTTP hacia el cliente.

## Variables de entorno requeridas

| Variable | Descripción | Valor por Defecto / Ejemplo | ¿Sensible? |
|---|---|---|:---:|
| `ENVIRONMENT` | Entorno de ejecución (`development`, `testing`, `production`) | `development` | No |
| `PROJECT_NAME` | Nombre de la aplicación | `TP_Cap1a4_API` | No |
| `DEBUG` | Activa modo depuración y documentación Swagger | `True` | No |
| `DATABASE_URL` | URL de conexión asíncrona a PostgreSQL | `postgresql+asyncpg://postgres:postgres@localhost:5432/tp_programacion` | **Sí** |
| `DB_POOL_SIZE` | Cantidad de conexiones mantenidas en el pool | `5` | No |
| `DB_MAX_OVERFLOW` | Conexiones adicionales permitidas sobre el pool | `10` | No |
| `DB_TIMEOUT` | Timeout en segundos para queries de diagnóstico | `2.0` | No |
