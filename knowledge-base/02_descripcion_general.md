# 02 — Descripción General del Sistema

## Stack tecnológico

| Capa / Componente | Tecnología | Versión Mínima | Propósito / Justificación |
|---|---|---|---|
| **Lenguaje de Programación** | Python | 3.11+ | Soporte moderno para tipos nativos, TaskGroup y optimizaciones asíncronas de runtime. |
| **Framework Web** | FastAPI | 0.115+ | Framework asíncrono ASGI de alto rendimiento con validación automática y OpenAPI integrada. |
| **Servidor ASGI** | Uvicorn | 0.30+ | Servidor de producción para ejecutar aplicaciones ASGI basadas en uvloop. |
| **Configuración** | Pydantic Settings | 2.5+ | Tipado estricto, parsing automático de `.env` y validación de tipos en arranque. |
| **ORM / Acceso a Datos** | SQLAlchemy | 2.0+ | Estándar moderno de mapeo relacional en modo asíncrono con `AsyncEngine` y `async_sessionmaker`. |
| **Driver de Base de Datos** | asyncpg | 0.30+ | Driver de PostgreSQL en C nativo para máximo rendimiento asíncrono en asyncio. |
| **Motor de Base de Datos** | PostgreSQL | 16-alpine | Base de datos relacional robusta, transaccional y ACID. |
| **Testing** | pytest + pytest-asyncio | 8.0+ | Framework de pruebas unitarias y asíncronas con soporte para fixtures con scope async. |
| **Cliente HTTP de Pruebas** | HTTPX | 0.27+ | Cliente HTTP asíncrono utilizado con `ASGITransport` para pruebas directas sin levantar sockets de red. |
| **Infraestructura Local** | Docker & Docker Compose | v2+ | Aislamiento reproducible del servicio PostgreSQL para desarrollo y CI/CD. |

## Arquitectura general

El sistema sigue una arquitectura modular en capas desacopladas, diseñada para aislar el núcleo de la aplicación de los detalles de infraestructura:

```
                    +------------------------------------+
                    |        Peticiones HTTP / Red       |
                    +------------------------------------+
                                      |
                                      v
                    +------------------------------------+
                    |       Capa de Presentación         |
                    |    (FastAPI Routers / Endpoints)   |
                    |   - GET /health/live               |
                    |   - GET /health/ready              |
                    +------------------------------------+
                                      |
                         Dependencias | (Inyección FastAPI)
                                      v
                    +------------------------------------+
                    |        Capa Core / Config          |
                    |   - Settings (pydantic-settings)   |
                    |   - Lifespan Context Manager       |
                    +------------------------------------+
                                      |
                                      v
                    +------------------------------------+
                    |      Capa de Infraestructura       |
                    |   - SQLAlchemy 2.0 AsyncEngine     |
                    |   - Pool de conexiones asyncpg     |
                    |   - async_sessionmaker             |
                    +------------------------------------+
                                      |
                                      v
                    +------------------------------------+
                    |       PostgreSQL 16 (Docker)       |
                    +------------------------------------+
```

### Principios de diseño aplicados:
1. **Single Source of Truth para Configuración**: Toda variable proviene de `Settings` instanciada como singleton mediante `@lru_cache()`.
2. **Ciclo de vida desacoplado**: La inicialización de la conexión de DB y la verificación no se mezclan con la definición de rutas, sino que se gestionan en el `lifespan` de FastAPI.
3. **Fail-Fast**: Ante cualquier inconsistencia crítica de configuración o indisponibilidad insalvable de base de datos en el boot, el sistema previene el inicio de tráfico.

## Integraciones externas

| Servicio | Propósito | Tipo de Conexión | Protocolo |
|---|---|---|---|
| **PostgreSQL 16** | Persistencia transaccional de datos y validación de conectividad. | Asíncrona (Pool de sockets TCP) | `postgresql+asyncpg://` |

## API REST — Catálogo de Endpoints de Fundación

| Método | Ruta | Descripción | Códigos HTTP de Respuesta |
|---|---|---|---|
| `GET` | `/health` | Chequeo unificado de salud del servicio. | `200 OK` si el servicio está operativo. |
| `GET` | `/health/live` | Liveness probe: Comprueba que el proceso ASGI responde peticiones. | `200 OK` |
| `GET` | `/health/ready` | Readiness probe: Comprueba activamente la conectividad con PostgreSQL (`SELECT 1`). | `200 OK` (Operativo)<br>`503 Service Unavailable` (DB no disponible) |
| `GET` | `/docs` | Documentación interactiva Swagger UI generada automáticamente por OpenAPI. | `200 OK` |
