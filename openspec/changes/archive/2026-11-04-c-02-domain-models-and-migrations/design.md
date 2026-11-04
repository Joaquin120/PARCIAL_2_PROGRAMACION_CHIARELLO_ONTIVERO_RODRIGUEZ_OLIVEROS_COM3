# Design: C-02 Domain Models and Migrations

## Context
Ver motivación y problema en `proposal.md`. Tras la implementación de `C-01`, el backend dispone de una base declarativa (`Base = DeclarativeBase`) con convención de nombres para constraints en `src/db/base.py`, un pool asíncrono configurado con `asyncpg` en `src/db/session.py` y configuración centralizada tipada en `src/core/config.py`. Se requiere establecer el entorno de migraciones con Alembic configurado para operaciones asíncronas y definir los modelos de dominio fuertemente tipados.

## Goals / Non-Goals

**Goals:**
- Configurar Alembic en modo asíncrono nativo (`alembic init -t async alembic`, `alembic.ini`, `alembic/env.py`).
- Vincular `alembic/env.py` a la configuración centralizada `get_settings().DATABASE_URL` y a `Base.metadata` sin credenciales hardcodeadas.
- Definir mixins reutilizables de persistencia (`TimestampMixin`, `AuditMixin`) con `created_at`, `updated_at` e `is_active`.
- Definir las entidades de dominio en `src/db/models/` con tipado estricto de SQLAlchemy 2.0 (`Mapped`, `mapped_column`).
- Exponer y registrar todos los modelos en `src/db/models/__init__.py` para autogeneración de migraciones.
- Generar la primera migración de esquema (`001_initial_schema.py`).
- Desarrollar pruebas unitarias de modelos y pruebas de integración del ciclo de migración (`upgrade head` / `downgrade base`).

**Non-Goals:**
- Implementar endpoints REST de negocio o controladores (pertenecen a `C-03`).
- Implementar esquemas de negocio Pydantic para peticiones HTTP (pertenecen a `C-03`).
- Flujos de autenticación o autorización de usuarios.

## Decisions

### Decisión 1: Alembic Async nativo con asyncpg
- **Elección**: Utilizar la plantilla asíncrona de Alembic configurada con `async_engine_from_config` y `connection.run_sync`.
- **Alternativas consideradas**: Usar `psycopg2` sincrónico exclusivamente para migraciones o scripts manuales de SQL.
- **Razón**: Mantiene un único driver (`asyncpg`) y un único formato de cadena de conexión (`postgresql+asyncpg://`), eliminando dependencias binarias redundantes y garantizando consistencia en CI/CD y producción.

### Decisión 2: Inyección dinámica de configuración en `env.py`
- **Elección**: Modificar `alembic/env.py` para sobreescribir `sqlalchemy.url` usando `get_settings().DATABASE_URL`.
- **Alternativas consideradas**: Hardcodear `sqlalchemy.url` en `alembic.ini`.
- **Razón**: Cumple estrictamente con la regla RN-CFG-03 evitando credenciales expuestas en archivos de configuración estáticos y permitiendo variar entornos (`development`, `testing`, `production`) dinámicamente.

### Decisión 3: Estructura modular de modelos en `src/db/models/`
- **Elección**: Separar modelos en archivos dedicados dentro de `src/db/models/` y centralizar sus importaciones en `src/db/models/__init__.py`.
- **Alternativas consideradas**: Monolito de modelos en un único archivo `models.py`.
- **Razón**: Mejora la mantenibilidad, escalabilidad y permite que el autogenerador de Alembic descubra todas las tablas importando simplemente `src.db.models`.

## Risks / Trade-offs

- **[Riesgo] Migraciones automáticas no detectan metadatos si no son importados**:
  - *Mitigación*: En `alembic/env.py` se importa explícitamente `import src.db.models` y `from src.db.base import Base`, garantizando que todas las subclases estén en memoria al momento de inspeccionar `Base.metadata`.
- **[Riesgo] Inconsistencia en marcas temporales entre clientes y motor**:
  - *Mitigación*: Utilizar `DateTime(timezone=True)` junto con `server_default=func.now()` y `onupdate=func.now()` para delegar la generación del timestamp al motor de base de datos en UTC.
