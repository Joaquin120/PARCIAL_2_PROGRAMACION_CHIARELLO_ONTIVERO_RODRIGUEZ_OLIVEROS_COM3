# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **PARCIAL_2_PROGRAMACION_CHIARELLO_ONTIVERO_RODRIGUEZ_OLIVEROS_COM3 (TP_Cap1a4)**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 domain-models-and-migrations
        └── C-03 business-api-endpoints
              └── C-04 integration-and-e2e-testing
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse según la disponibilidad de agentes y dependencias satisfechas.

```
GATE 0: ninguna
  → C-01 foundation-setup              [Agente A]

GATE 1: C-01 ✓
  → C-02 domain-models-and-migrations  [Agente A]

GATE 2: C-02 ✓
  → C-03 business-api-endpoints        [Agente A]

GATE 3: C-03 ✓
  → C-04 integration-and-e2e-testing   [Agente A]
```

### Camino crítico (4 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-04
```

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)              │ Agente B (Backend Aux) │ Agente C (Testing / QA)
─────┼──────────────────────────────────────┼────────────────────────┼─────────────────────────
  1  │ C-01 foundation-setup                │         —              │         —
  2  │ C-02 domain-models-and-migrations   │         —              │         —
  3  │ C-03 business-api-endpoints          │         —              │         —
  4  │ C-04 integration-and-e2e-testing    │         —              │         —
```

---

## FASE 1 — Fundación y Arquitectura Base

### [C-01] `foundation-setup`
- **Estado**: `[x]` completado
- **Scope**: Skeleton modular backend FastAPI + configuración tipada + persistencia asíncrona + lifespan + healthchecks
  - Estructura modular en `src/`: capas `core/`, `db/`, `api/v1/endpoints/`, `schemas/`
  - Configuración centralizada tipada en `src/core/config.py` con `pydantic-settings` (`Settings`, `get_settings()` con `@lru_cache()`), validación estricta de `DATABASE_URL` (`postgresql+asyncpg://`), pool sizing (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`), timeout y `.env.example`
  - Infraestructura de persistencia asíncrona en `src/db/session.py` (`AsyncEngine`, `async_sessionmaker`, generador inyectable `get_db()` con aislamiento por request) y `src/db/base.py` (`DeclarativeBase` con convención de nombres de constraints)
  - Ciclo de vida con ASGI Lifespan en `src/core/lifespan.py` (`@asynccontextmanager`), ping asíncrono a PostgreSQL (`SELECT 1`) en startup con fail-fast y disposición limpia del pool (`await engine.dispose()`) en shutdown
  - Endpoints de salud en `src/api/v1/endpoints/health.py`: `GET /health` y `GET /health/live` (liveness inmediato) y `GET /health/ready` (readiness con diagnóstico activo a PostgreSQL y respuesta HTTP 503 ante fallas)
  - Entorno de desarrollo contenerizado en `docker-compose.yml` para servicio PostgreSQL 16 Alpine
  - Tests automatizados en `tests/unit/test_config.py`, `tests/integration/test_health.py` y `tests/integration/test_lifespan.py` con `pytest-asyncio` y `httpx.ASGITransport`
  - Cubre Épicas 1, 2 y 3 (Historias de Usuario US-001 a US-005) correspondientes a `SPEC-00-fundacion`
- **Dependencias**: ninguna
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance v0.1
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico
  - `knowledge-base/04_modelo_de_datos.md` §Arquitectura de Persistencia Asíncrona
  - `knowledge-base/05_reglas_de_negocio.md` §RN-CFG, §RN-LFS, §RN-HLT, §RN-SES
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios recomendada

---

## FASE 2 — Capítulos Siguientes del TP (Extensión Modular)

### [C-02] `domain-models-and-migrations`
- **Estado**: `[x]` completado
- **Scope**: Definición de modelos de dominio base y configuración de migraciones con Alembic
  - Inicialización y configuración del entorno de migraciones con Alembic para async (`alembic init -t async alembic`, `env.py` vinculado a `src/db/base.py` y `Settings.DATABASE_URL`)
  - Definición de modelos de dominio base y mixins (`AuditMixin` con `created_at`, `updated_at`, `is_active`) heredando de `Base` (`DeclarativeBase`)
  - Mapeo de entidades de negocio del TP con tipado estricto SQLAlchemy 2.0 (`Mapped`, `mapped_column`, foreign keys con convención estandarizada)
  - Generación de migración inicial `001_initial_schema.py`
  - Tests unitarios de modelos y verificación de migraciones `upgrade head` / `downgrade base` sobre base de datos de prueba
- **Dependencias**: `C-01`
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Base Declarativa y Convenciones
  - `knowledge-base/05_reglas_de_negocio.md` §Dominio: Manejo de Sesiones de Base de Datos
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-01 Adopción de SQLAlchemy 2.0 Async

---

### [C-03] `business-api-endpoints`
- **Estado**: `[x]` completado
- **Scope**: Implementación de endpoints de negocio y validación de reglas
  - Definición de esquemas Pydantic v2 de entrada y salida (`schemas/`) para las operaciones del dominio con validación de datos
  - Implementación de routers y controladores REST en `src/api/v1/endpoints/` montados en `src/api/router.py`
  - Inyección de dependencias `Depends(get_db)` y manejo de transacciones de base de datos con manejo explícito de errores HTTP (`400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`)
  - Implementación de lógica de servicio y validación de reglas de negocio específicas del TP
  - Tests de integración de endpoints probando flujos de negocio exitosos y respuestas de error con `AsyncClient`
- **Dependencias**: `C-02`
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Arquitectura general
  - `knowledge-base/05_reglas_de_negocio.md` §Dominio: Manejo de Sesiones de Base de Datos
  - `knowledge-base/07_flujos_principales.md` §Flujo 2: Consulta del Endpoint de Readiness
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados (Dependency Injection)

---

### [C-04] `integration-and-e2e-testing`
- **Estado**: `[x]` completado
- **Scope**: Pruebas de integración E2E, fixtures y verificación de entrega final
  - Configuración de fixtures avanzados de testing en `tests/conftest.py` (aislamiento de transacciones, rollback automático por test, semillas de prueba)
  - Suite de pruebas E2E que valide el ciclo completo de vida de la aplicación, endpoints de salud (`/health/live`, `/health/ready`) y endpoints de negocio
  - Pruebas de resiliencia y tolerancia a fallos (comportamiento de `/health/ready` ante desconexión simulada de PostgreSQL, timeout de 2 segundos)
  - Configuración de script de verificación para evaluadores / entrega del TP (`pytest -v --cov=src`) y reporte de cobertura de código
  - Documentación de procedimientos de prueba y validación en `README.md`
- **Dependencias**: `C-03`
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Métricas de éxito
  - `knowledge-base/06_funcionalidades.md` §Criterios de Aceptación
  - `knowledge-base/07_flujos_principales.md` §Flujo 1, §Flujo 2, §Flujo 3
  - `knowledge-base/09_decisiones_y_supuestos.md` §SU-01, §SU-02
  - `knowledge-base/10_preguntas_abiertas.md` §Preguntas abiertas
