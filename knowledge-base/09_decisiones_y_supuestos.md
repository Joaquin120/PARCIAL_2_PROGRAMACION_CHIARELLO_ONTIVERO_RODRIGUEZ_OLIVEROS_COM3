# 09 — Registro de Decisiones de Diseño y Supuestos

## Decisiones documentadas (ADR / DD)

### DD-01 — Adopción de SQLAlchemy 2.0 Async con asyncpg
- **Decisión**: Utilizar `create_async_engine` de SQLAlchemy 2.0 junto con el driver nativo asíncrono `asyncpg`.
- **Contexto**: FastAPI es un framework completamente asíncrono basado en `asyncio`. Utilizar drivers sincrónicos tradicionales (`psycopg2`) bloquearía el event loop en cada llamada a base de datos.
- **Alternativas consideradas**:
  1. `psycopg2-binary` (sincrónico): Requiere ejecución en threadpool con `run_in_threadpool`, perdiendo rendimiento y escalabilidad.
  2. `asyncpg` directo sin ORM: Alto rendimiento, pero carece de la expresividad de metadatos, migraciones con Alembic y tipado de modelos para capítulos futuros.
  3. `Tortoise-ORM` o `Peewee-async`: Menor madurez y menor adopción comunitaria frente al ecosistema estándar de SQLAlchemy 2.0.
- **Justificación**: SQLAlchemy 2.0 ofrece soporte asíncrono nativo de primera clase, compatibilidad total con `Alembic` y tipado estricto con `Mapped` y `mapped_column`.
- **Trade-offs aceptados**: Mayor verbosidad en la configuración del `AsyncEngine` y obligatoriedad de usar `await db.execute(...)`.

---

### DD-02 — Migración de `@app.on_event` a `Lifespan Context Manager`
- **Decisión**: Implementar el ciclo de vida de la aplicación mediante `@asynccontextmanager` y el parámetro `lifespan` de FastAPI.
- **Contexto**: Los eventos `@app.on_event("startup")` y `@app.on_event("shutdown")` están oficialmente marcados como deprecados en FastAPI / Starlette.
- **Alternativas consideradas**: Mantener `@app.on_event`.
- **Justificación**: El gestor de contexto asíncrono garantiza que las variables inicializadas antes del `yield` se mantengan en el mismo scope y contexto que la limpieza posterior, permitiendo manejo de excepciones robusto y testeabilidad directa mediante `TestClient` o `AsyncClient`.
- **Trade-offs aceptados**: Requiere comprender la semántica de generadores asíncronos y contexto en Python.

---

### DD-03 — Configuración centralizada mediante `pydantic-settings` 2.x
- **Decisión**: Usar el paquete desacoplado `pydantic-settings` con `SettingsConfigDict` para leer y validar el entorno.
- **Contexto**: A partir de Pydantic v2, `BaseSettings` se separó del paquete core `pydantic`.
- **Alternativas consideradas**: `os.getenv()` o `python-decouple`.
- **Justificación**: Pydantic ofrece validación automática de tipos (int, bool, PostgresDsn), mensajes de error detallados al fallar y soporte transparente para `.env`.
- **Trade-offs aceptados**: Añadir una dependencia externa adicional en el entorno virtual.

---

### DD-04 — Desacoplamiento de Liveness y Readiness Probes
- **Decisión**: Separar `/health/live` (vitalidad del proceso) de `/health/ready` (operatividad con base de datos).
- **Contexto**: Si un endpoint único `/health` chequea la base de datos y ésta experimenta lentitud transitoria, orquestadores como Kubernetes o Docker podrían reiniciar agresivamente el contenedor del backend, empeorando el problema (cascading failure).
- **Justificación**: Permite al orquestador saber si debe reiniciar el proceso (liveness) o si debe pausar el envío de tráfico hasta que la base de datos se recupere (readiness).

---

## Supuestos inferidos

### SU-01 — Disponibilidad de PostgreSQL vía Docker en entorno de desarrollo
- **Supuesto**: Los desarrolladores y evaluadores tienen Docker instalado en su entorno local para levantar PostgreSQL con `docker compose up -d`.
- **Origen**: Prácticas estándar de la cátedra de Programación en entornos universitarios.
- **Riesgo si es falso**: Dificultad para ejecutar tests de integración localmente sin una base de datos instalada nativamente en el OS.
- **Cómo validar**: Proveer un archivo `docker-compose.yml` claro y scripts de verificación rápida.

### SU-02 — Python 3.11+ como runtime base
- **Supuesto**: El entorno virtual de desarrollo y evaluación utiliza Python 3.11 o superior.
- **Origen**: Uso de tipado moderno de Python y compatibilidad con `asyncio` optimizado.
- **Riesgo si es falso**: Incompatibilidad sintáctica en caso de usar versiones obsoletas como Python 3.9.
- **Cómo validar**: Declarar `requires-python = ">=3.11"` en `pyproject.toml`.
