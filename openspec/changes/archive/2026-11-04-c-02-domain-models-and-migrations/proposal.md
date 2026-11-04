# Proposal: C-02 Domain Models and Migrations

## Why
Una vez establecida la fundación asíncrona del backend en C-01, el sistema requiere definir las entidades de dominio y el soporte de versionado de esquemas mediante migraciones de base de datos. Sin un mecanismo de migraciones estructurado (Alembic en modo async) y modelos fuertemente tipados con SQLAlchemy 2.0, la evolución del esquema relacional y el modelado de datos de las etapas posteriores del Trabajo Práctico no serían reproducibles ni auditables.

## What Changes
- Inicialización y configuración del entorno de migraciones asíncronas con Alembic (`alembic/`, `alembic.ini`, `env.py` adaptado a `asyncpg` y vinculado dinámicamente a `get_settings().DATABASE_URL` y `Base.metadata`).
- Definición de mixins de persistencia reutilizables en `src/db/models/base.py` (`AuditMixin` / `TimestampMixin` con `created_at`, `updated_at`, `is_active`).
- Definición de modelos de dominio base del Trabajo Práctico en `src/db/models/` utilizando tipado estricto de SQLAlchemy 2.0 (`Mapped`, `mapped_column`, tipos nativos).
- Exportación unificada de modelos en `src/db/models/__init__.py` asegurando visibilidad para el autogenerador de Alembic (`target_metadata = Base.metadata`).
- Generación de la migración inicial de esquema `001_initial_schema.py`.
- Suite de pruebas unitarias y de integración para validar la instanciación de modelos, constraints de integridad y la ejecución idempotente de migraciones `upgrade` y `downgrade`.

## Capabilities

### New Capabilities
- `database-migrations`: Versionado, generación y ejecución asíncrona de migraciones de esquema relacional utilizando Alembic.
- `domain-models`: Definición de entidades de dominio tipadas en SQLAlchemy 2.0 con mixins de auditoría temporal y restricciones de integridad.

### Modified Capabilities
*(Ninguna; las capacidades existentes no modifican sus requisitos funcionales).*

## Impact
- **Código**: Nuevos módulos en `src/db/models/`, configuración de `alembic/` y `alembic.ini`.
- **Dependencias**: Adición de `alembic>=1.13.0` a `requirements.txt` y `pyproject.toml`.
- **Base de Datos**: Creación de tabla de control `alembic_version` y tablas relacionales definidas en los modelos.
- **Testing**: Nuevas pruebas en `tests/unit/test_models.py` y `tests/integration/test_migrations.py`.
