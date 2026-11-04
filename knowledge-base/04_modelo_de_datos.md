# 04 — Modelo de Datos y Persistencia

## Dominios
Para la etapa fundacional (`SPEC-00-fundacion` / TP Capítulos 1 a 4), el dominio de persistencia se enfoca en la infraestructura de conexión, el ciclo de vida del pool y la clase base declarativa unificada para soportar futuras entidades.

1. **Dominio de Conectividad e Infraestructura**: Control de pool de conexiones (`asyncpg`), sesiones asíncronas (`AsyncSession`), y ejecución de pruebas de conexión (`text("SELECT 1")`).
2. **Dominio Base Declarativo**: Convención de nombrado unificada para constraints e índices en PostgreSQL.

## Arquitectura de Persistencia Asíncrona (SQLAlchemy 2.0)

```
+-------------------------------------------------------------------+
|                        FastAPI Request Context                    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                 FastAPI Dependency: get_db()                      |
|                  yields AsyncSession per request                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              async_sessionmaker[AsyncSession]                     |
|           expire_on_commit=False, autoflush=False                 |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                  SQLAlchemy AsyncEngine                           |
|       driver: postgresql+asyncpg://                               |
|       pool_size=10, max_overflow=20, pool_pre_ping=True           |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                  PostgreSQL 16 Connection Pool                    |
+-------------------------------------------------------------------+
```

## Base Declarativa y Convenciones

Se establece una clase `Base` unificada heredando de `DeclarativeBase` con convención estandarizada de nombres de metadatos (evitando colisiones en migraciones futuras):

```python
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
```

## Entidades de la Etapa de Fundación
En esta fase fundacional no se persisten tablas de negocio. La persistencia se valida mediante la ejecución de la consulta diagnóstica:

```sql
SELECT 1 AS alive;
```

Esta query se despacha de forma asíncrona dentro de una transacción de solo lectura con timeout controlado (ej. 2 segundos) para certificar la salud de la base de datos sin generar locks ni overhead.

## Seed data inicial
No se requiere seed data de negocio para esta fase. La inicialización del entorno se realiza levantando el contenedor de base de datos vía Docker Compose con la base de datos creada por defecto según variables de entorno.
