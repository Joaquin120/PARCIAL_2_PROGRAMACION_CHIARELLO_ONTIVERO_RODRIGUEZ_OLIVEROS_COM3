# Design: C-04 Integration and E2E Testing

## Context

El proyecto cuenta con la arquitectura completa en capas: configuración Pydantic, ciclo de vida ASGI Lifespan, persistencia SQLAlchemy 2.0 Async, migraciones Alembic y endpoints REST para `Item`. Véase `proposal.md` para la motivación. Se requiere centralizar los fixtures compartidos en `tests/conftest.py`, implementar un recorrido E2E completo, asegurar la tolerancia a fallos en readiness y configurar el reporte de cobertura de código para los evaluadores.

## Goals / Non-Goals

**Goals:**
- Centralizar fixtures asíncronos (`async_client`, `mock_db_session`, `clean_storage`) en `tests/conftest.py` para eliminar duplicación y garantizar aislamiento estricto por test.
- Implementar suite E2E en `tests/integration/test_e2e_workflow.py` que recorra: liveness (`/health/live`) -> readiness (`/health/ready`) -> creación de ítem (`POST`) -> verificación en listado paginado (`GET`) -> consulta por ID (`GET /{id}`) -> actualización parcial (`PATCH`) -> eliminación física (`DELETE`) -> verificación de 404.
- Implementar suite de resiliencia en `tests/integration/test_resilience.py` validando degradación controlada a HTTP 503 ante caída de conexión (`SQLAlchemyError`) y ante timeout (`asyncio.TimeoutError` > 2s).
- Configurar flags y opciones de cobertura en `pyproject.toml` con `pytest-cov` apuntando a `src/`.
- Actualizar `README.md` con comandos para ejecutar la suite completa y generar reportes de cobertura (`--cov-report=term-missing`).

**Non-Goals:**
- Modificar esquemas de datos o agregar nuevas rutas de negocio a la API.
- Forzar dependencias de red externas en la ejecución estándar de `pytest`.

## Decisions

### 1. Centralización de Fixtures en `tests/conftest.py`
- **Decisión:** Mover la creación de `FakeAsyncSession` y el cliente HTTP con `ASGITransport(app=app)` a `tests/conftest.py`.
- **Razón:** Reutilización limpia en pruebas de endpoints y suites E2E sin acoplar cada archivo de prueba a su propio harness de sesión.
- **Alternativas consideradas:** Mantener fixtures locales en cada archivo (descartado por redundancia y riesgo de desincronización).

### 2. Aislamiento Transaccional Determinístico en Memoria
- **Decisión:** Utilizar un fixture `isolated_items_db` con alcance de función (`scope="function"`) que provee un diccionario de almacenamiento limpio en cada caso de prueba.
- **Razón:** Permite ejecución concurrente y determinística con tiempo de ejecución menor a 1 segundo sin requerir un demonio PostgreSQL corriendo para la suite de integración básica.
- **Alternativas consideradas:** Conectar a base de datos real con rollback transaccional (requiere Docker Compose activo obligatoriamente en entornos CI mínimos).

### 3. Simulación de Falla y Timeout en Readiness
- **Decisión:** Sobrescribir `get_db` o simular retardo/excepción en la llamada a `db.execute(text("SELECT 1"))` para validar `HTTP 503 Service Unavailable`.
- **Razón:** Verifica que `src/api/v1/endpoints/health.py` maneja de forma determinística tanto `SQLAlchemyError` como `asyncio.TimeoutError` respetando el timeout configurado de 2 segundos.

## Risks / Trade-offs

- **[Risk: Divergencia entre in-memory session y PostgreSQL real]** → *Mitigación:* Se valida la compatibilidad estructural de modelos y migraciones en `test_models.py` y `test_migrations.py`.
- **[Risk: Paquetes de cobertura faltantes en entornos limpios]** → *Mitigación:* Se añade `pytest-cov>=5.0.0` en `requirements.txt` y `pyproject.toml`.
