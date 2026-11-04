# Tasks: C-02 Domain Models and Migrations

## 1. Configuración de Entorno de Migraciones (Alembic)

- [x] 1.1 Incorporar `alembic>=1.13.0` a `requirements.txt` y `pyproject.toml`, e instalar la dependencia en el entorno `.venv`.
- [x] 1.2 Inicializar el andamiaje de migraciones con Alembic en modo async (`alembic init -t async alembic`), adaptando `alembic.ini` y `alembic/env.py` para cargar dinámicamente `get_settings().DATABASE_URL` y vincular `target_metadata = Base.metadata`.
- [x] 1.3 Escribir prueba unitaria en `tests/unit/test_alembic_config.py` verificando que la configuración de Alembic resuelva la URL asíncrona de base de datos y cargue `target_metadata` correctamente.

## 2. Mixins y Modelos de Dominio Base

- [x] 2.1 Crear el directorio `src/db/models/` e implementar `TimestampMixin` y `AuditMixin` en `src/db/models/base.py` con atributos tipados `created_at: Mapped[datetime]`, `updated_at: Mapped[datetime]` y `is_active: Mapped[bool]`.
- [x] 2.2 Definir los modelos de dominio del Trabajo Práctico heredando de `Base` y de los mixins de auditoría, aplicando tipado estricto `Mapped`, `mapped_column` y restricciones relacionales.
- [x] 2.3 Centralizar la exportación de modelos en `src/db/models/__init__.py`, asegurando que `Base.metadata.tables` registre todas las entidades del dominio.
- [x] 2.4 Escribir suite de pruebas unitarias en `tests/unit/test_models.py` validando la instanciación de entidades, tipos de datos y valores por defecto de los mixins.

## 3. Generación y Validación de Migraciones

- [x] 3.1 Generar archivo de migración inicial `001_initial_schema.py` dentro de `alembic/versions/` reflejando el DDL de todas las tablas declaradas.
- [x] 3.2 Escribir pruebas de integración en `tests/integration/test_migrations.py` validando la ejecución programática de `alembic upgrade head` y `alembic downgrade base`.

## 4. Verificación Integral y Documentación

- [x] 4.1 Ejecutar la suite completa de pruebas con `pytest -v` verificando 100% de tests pasando en verde.
- [x] 4.2 Actualizar `README.md` documentando la gestión de migraciones con Alembic (`alembic upgrade head`, creación de revisiones) y comandos de prueba.

## Workflow follow-up

- Ejecutar `/opsx-apply` para iniciar la implementación de las tareas.
- Al finalizar la implementación, archivar el change con `/opsx-archive c-02-domain-models-and-migrations`.
- Marcar como completado el checkbox de `C-02` en `CHANGES.md`.
