# 01 — Visión y Objetivos

## Propósito del sistema
El propósito de este proyecto es establecer una base arquitectónica asíncrona, robusta, tipada y de grado producción para el desarrollo del Trabajo Práctico (Capítulos 1 a 4) de la cátedra de Programación (Comisión 3). El sistema implementa un backend modular en FastAPI con validación centralizada de configuraciones, ciclo de vida administrado por lifespan, conexión asíncrona no bloqueante a PostgreSQL mediante SQLAlchemy 2.0 y asyncpg, y diagnóstico activo de operatividad mediante endpoints de healthcheck.

## Objetivos por actor

| Actor | Objetivo Principal | Objetivos Secundarios |
|---|---|---|
| **Estudiantes / Desarrolladores** (Chiarello, Ontivero, Rodriguez, Oliveros) | Contar con un andamiaje técnico sólido, modular y extensible para la implementación de las siguientes etapas del TP. | • Evitar acoplamientos innecesarios.<br>• Garantizar testing asíncrono reproducible.<br>• Centralizar configuración y variables sensibles. |
| **Cátedra / Evaluadores** | Evaluar la correcta aplicación de patrones de diseño asíncronos y buenas prácticas de ingeniería en Python. | • Verificar inicialización y desconexión limpia de recursos.<br>• Validar resiliencia y diagnóstico vía `/health`.<br>• Comprobar compliance de tipado estricto con Pydantic. |
| **Orquestadores / Monitores (SRE / Docker)** | Monitorear el estado operativo y la disponibilidad real de dependencias del contenedor backend. | • Obtener respuestas inmediatas de vitalidad (liveness).<br>• Diagnosticar conectividad efectiva a base de datos (readiness). |

## Alcance v0.1 (SPEC-00-fundacion / TP_Cap1a4)
El alcance de esta etapa fundacional comprende:
- **Estructura base del proyecto**: Organización modular siguiendo principios de Clean Architecture / capas desacopladas (`core`, `db`, `api`, `schemas`).
- **Configuración con `pydantic-settings`**: Carga jerárquica y validación en tiempo de arranque desde variables de entorno y archivos `.env`.
- **Persistencia asíncrona**: Configuración de `AsyncEngine`, pool de conexiones no bloqueante y factoría `async_sessionmaker` usando `SQLAlchemy 2.0` y `asyncpg` sobre PostgreSQL.
- **Ciclo de vida con Lifespan**: Implementación de gestor de contexto asíncrono (`@asynccontextmanager`) para inicialización controlada, verificación de ping a DB en arranque y liberación graciosa (`engine.dispose()`) en apagado.
- **Endpoints de Diagnóstico y Salud**:
  - `GET /health` (o `/health/live`): Comprobación inmediata de que el proceso FastAPI está activo.
  - `GET /health/ready`: Comprobación activa de la conexión a PostgreSQL (`SELECT 1`).
- **Entorno de Contenerización**: `docker-compose.yml` para levantar PostgreSQL local y testing de integración.
- **Suite de Pruebas Automatizadas**: Pruebas unitarias y de integración sobre ciclo de vida y endpoints de salud utilizando `pytest`, `pytest-asyncio` y `httpx.ASGITransport`.

## Fuera de alcance
- Modelos de datos de negocio avanzados o entidades de dominio de etapas posteriores (Capítulo 5+).
- Lógica de autenticación, autorización basada en JWT o manejo de sesiones de usuario.
- Interfaces gráficas de usuario, plantillas HTML o frontend web.
- Migraciones completas de esquemas de negocio con Alembic (solo se deja la inicialización y soporte técnico).

## Métricas de éxito
1. **Validación de arranque**: Si `DATABASE_URL` no está definida o es inválida, la aplicación aborta inmediatamente con mensajes claros antes de aceptar tráfico HTTP.
2. **Resiliencia de conexión**: El endpoint de readiness reporta `200 OK` únicamente cuando la conexión con PostgreSQL es exitosa y `503 Service Unavailable` si la base de datos se interrumpe.
3. **Liberación de recursos**: Al recibir señales `SIGINT` o `SIGTERM`, las conexiones en el pool se drenan y liberan sin dejar conexiones huérfanas en PostgreSQL.
4. **Cobertura de tests**: Cobertura del 100% en los módulos de configuración, lifespan y endpoints de salud.
