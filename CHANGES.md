# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **PARCIAL_2_PROGRAMACION_CHIARELLO_ONTIVERO_RODRIGUEZ_OLIVEROS_COM3 (TP_Cap1a4 + Parcial_Cap1a6)**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base y consignas canónicas (`CONSIGNA_PARCIAL.md`) indicadas en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
[TP Capítulos 1 a 4]
C-01 foundation-setup [x]
  └── C-02 domain-models-and-migrations [x]
        └── C-03 business-api-endpoints [x]
              └── C-04 integration-and-e2e-testing [x]
                    ├── C-11 vps-docker-deployment
                    └── [Parcial Capítulos 1 a 6]
                        C-05 parcial-core-uow [x]
                          └── C-06 parcial-models-and-migrations [x]
                                ├── C-07 parcial-auth-and-security
                                │     └── C-09 parcial-ventas-transactions [x]
                                └── C-08 parcial-catalog-and-stock
                                      └── C-09 parcial-ventas-transactions [x]
                                            └── C-10 parcial-seed-and-e2e-verification
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse según la disponibilidad de agentes y dependencias satisfechas.

```
GATE 0: ninguna
  → C-01 foundation-setup                      [Agente A] ✓

GATE 1: C-01 ✓
  → C-02 domain-models-and-migrations          [Agente A] ✓

GATE 2: C-02 ✓
  → C-03 business-api-endpoints                [Agente A] ✓

GATE 3: C-03 ✓
  → C-04 integration-and-e2e-testing           [Agente A] ✓

GATE 4: C-04 ✓                                 ← FORK (Parcial vs Despliegue VPS)
  → C-05 parcial-core-uow                      [Agente A] ✓
  → C-11 vps-docker-deployment                 [Agente C]

GATE 5: C-05 ✓
  → C-06 parcial-models-and-migrations          [Agente A] ✓

GATE 6: C-06 ✓                                 ← FORK (Auth vs Catálogo)
  → C-07 parcial-auth-and-security             [Agente A]
  → C-08 parcial-catalog-and-stock             [Agente B]

GATE 7: C-07 ✓, C-08 ✓
  → C-09 parcial-ventas-transactions           [Agente A] [x]

GATE 8: C-09 ✓
  → C-10 parcial-seed-and-e2e-verification     [Agente A]
```

### Camino crítico (9 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-04 → C-05 → C-06 → C-07 → C-09 → C-10
```
*(Nota: C-11 corre en paralelo sobre C-04 para el entregable del VPS).*

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)              │ Agente B (Backend Aux)       │ Agente C (DevOps / Testing)
─────┼──────────────────────────────────────┼──────────────────────────────┼─────────────────────────────
  1  │ C-01 foundation-setup [x]            │              —               │              —
  2  │ C-02 domain-models-and-migrations[x]│              —               │              —
  3  │ C-03 business-api-endpoints [x]      │              —               │              —
  4  │ C-04 integration-and-e2e-testing [x]│              —               │              —
  5  │ C-05 parcial-core-uow [x]            │              —               │ C-11 vps-docker-deployment
  6  │ C-06 parcial-models-and-migrations[x]│              —               │              —
  7  │ C-07 parcial-auth-and-security      │ C-08 parcial-catalog-stock   │              —
  8  │ C-09 parcial-ventas-transactions    │              —               │              — [x]
  9  │ C-10 parcial-seed-and-e2e           │              —               │              —
```

---

## FASE 1 — Fundación y Arquitectura Base (TP Capítulos 1 a 4)

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
  - Definición de esquemas Pydantic v2 de entrada y salida (`src/schemas/item.py`) para operaciones del dominio con validación de datos
  - Implementación de routers y controladores REST en `src/api/v1/endpoints/items.py` montados en `src/api/router.py`
  - Inyección de dependencias `Depends(get_db)` y manejo de transacciones con manejo explícito de errores HTTP (`400`, `404`, `422`)
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
  - Configuración de fixtures avanzados en `tests/conftest.py` (`isolated_db`, `FakeAsyncSession`, `async_client`)
  - Suite E2E en `tests/integration/test_e2e_workflow.py` validando el ciclo completo de la aplicación
  - Pruebas de resiliencia y tolerancia a fallos en `tests/integration/test_resilience.py` (degradación a HTTP 503 ante cortes o timeout > 2s)
  - Configuración de `pytest-cov` con cobertura del 100% en `src/` (49 tests pasando)
  - Documentación de procedimientos de prueba en `README.md`
- **Dependencias**: `C-03`
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Métricas de éxito
  - `knowledge-base/06_funcionalidades.md` §Criterios de Aceptación
  - `knowledge-base/07_flujos_principales.md` §Flujo 1, §Flujo 2, §Flujo 3

---

## FASE 3 — Arquitectura del Parcial: Core, Repositorios y Unit of Work

### [C-05] `parcial-core-uow`
- **Estado**: `[x]` completado
- **Scope**: Estructura base de capas en `parcial/app/core/`, Unit of Work sin ser dueño de sesión, repositorios con flush, paginación con default 20 y grupos de rutas
  - Configuración en `parcial/app/core/config.py`: lectura de campos sueltos de PostgreSQL (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`), `@computed_field` que ensambla `DATABASE_URL` asíncrona (`postgresql+asyncpg://`), costo configurable de bcrypt en `Settings`, `SECRET_KEY` y passwords sin valores por defecto (fail-fast en arranque)
  - Motor y sesiones en `parcial/app/core/database.py`: `create_async_engine` con pool parametrizable, factoría `async_sessionmaker(expire_on_commit=False)`, y `get_session` como generador inyectable de dependencias
  - Lifespan y grupos de rutas en `parcial/app/main.py`:
    - Lifespan almacena `engine` y `sessionmaker` en `app.state`, precalcula en memoria `app.state.fictitious_password_hash` con bcrypt en startup (mitigación de timing attacks en login) y ejecuta `await engine.dispose()` al apagar
    - Estructuración de dos grupos de rutas:
      - **Grupo Abierto:** `/health/*`, `/auth/registro`, `/auth/login`, `/auth/logout`, `/auth/yo`, `/auth/cambiar-password` y catálogo público de libros
      - **Grupo Protegido:** Rutas de administración, ventas y clientes, custodiadas por verificación centralizada de `debe_cambiar_password == false` (rechazo inmediato con **HTTP 403 Forbidden** si es `true`)
  - Repositorios en `parcial/app/core/repository.py`:
    - `BaseRepository[T](session, model_cls)`: provee `get_by_id`, `get_all`, `count`, `add`, `update`, `delete`. Las operaciones `add` y `update` ejecutan exclusivamente `await session.flush()`, **nunca commit()**. Ningún repositorio confirma transacciones
    - `SoftDeleteRepository[T]`: filtra automáticamente por `borrado_en IS NULL`, y provee `get_by_id_including_deleted` y `soft_delete` (`UPDATE ... SET borrado_en = func.now()`)
  - Unit of Work en `parcial/app/core/unit_of_work.py`:
    - `UnitOfWork` base asincrónico que **recibe la sesión inyectada** (generada por `get_session`), **NO crea ni cierra la sesión física**. Esto garantiza que las dependencias de seguridad (`get_usuario_actual`, `requiere_rol`) y el UoW compartan la misma conexión del pool por request
    - Administra la delimitación transaccional: ejecuta `await session.commit()` al salir del bloque con éxito y `await session.rollback()` si ocurre una excepción no controlada
  - Paginación estándar en `parcial/app/core/paginacion.py`:
    - Envoltorio genérico `PaginatedResponse[T]` con `{items, total, page, size, pages}`
    - Parámetros: `page` (default 1, `>= 1`), `size` (default 20, entre 1 y 100)
    - Reglas de borde: si `total == 0` -> `pages = 1` y lista vacía; si se solicita `page > pages` -> levanta **HTTP 422 Unprocessable Entity** (ej. `"La página 4 no existe: hay 3"`)
  - Tests unitarios en `parcial/tests/unit/` verificando repositorios, UoW, lifespan y reglas de borde de paginación
- **Dependencias**: `C-04`
- **Governance**: CRITICO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §1 Reglas Arquitectónicas Obligatorias (Puntos 1 y 2)
  - `CONSIGNA_PARCIAL.md` §2 Seguridad y Control de Acceso (Punto 5: Grupos de Rutas)

---

## FASE 4 — Modelos de Dominio y Migraciones del Parcial

### [C-06] `parcial-models-and-migrations`
- **Estado**: `[x]` completado
- **Scope**: Modelos de dominio del Parcial, modificaciones a Cliente/Libro, y migraciones 3 (Alembic autogen) y 4 (manual SQL con trigger append-only)
  - Modelos de usuarios y seguridad en `parcial/app/modules/usuarios/models.py`:
    - `Usuario`: `id`, `email` (UNIQUE), `nombre`, `password_hash`, `activo`, `debe_cambiar_password`
    - `AsignacionRol`: `id`, `usuario_id` (FK), `rol` (`CHECK rol IN ('ADMIN', 'VENDEDOR', 'CLIENTE')`), `desde`, `vence_en`, `revocada_en`, `otorgada_por` (FK), índice único parcial `(usuario_id, rol) WHERE revocada_en IS NULL`
    - `IntentoAcceso`: `id`, `cuando`, `email`, `ip`, `exito`, índice compuesto `(email, ip, cuando)`
    - `EventoSeguridad`: `id`, `cuando`, `actor` (texto), `accion`
  - Modificación a `Cliente`: agrega `usuario_id` (FK nulo permitido, UNIQUE con índice) para relación 1 a 1 opcional con navegación `cliente.usuario`
  - Modificación a `Libro`: agrega `borrado_en` (timestamptz, nulo), elimina `UNIQUE(isbn)` global y crea índice único parcial `(isbn) WHERE borrado_en IS NULL`
  - Modelo `MovimientoStock` en `parcial/app/modules/libros/models.py`: `id`, `libro_id` (FK), `venta_id` (FK nulo), `usuario_id` (FK), `cantidad` (int, `CHECK cantidad <> 0`), `motivo` (str), `cuando` (timestamptz)
  - Migración 3 autogenerada con Alembic en `parcial/migrations/`: evolución de tablas, columnas nuevas e índices parciales
  - Migración 4 manual SQL en `parcial/migrations/`: trigger PL/pgSQL que aborta cualquier operación `UPDATE` o `DELETE` sobre `movimiento_stock` garantizando su naturaleza de sólo agregado (Caso C-14)
  - Tests unitarios de modelos y verificación de migraciones `upgrade head` / `downgrade`
- **Dependencias**: `C-05`
- **Governance**: CRITICO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §3 Dominio, Stock Transaccional y Ventas (Puntos 1 y 2)

---

## FASE 5 — Seguridad, Autenticación y Catálogo de Libros

### [C-07] `parcial-auth-and-security`
- **Estado**: `[x]` completado
- **Scope**: Autenticación con cookies HttpOnly, límite de 72 bytes en contraseñas, rate limiting con sesión aislada, mitigación de timing attacks y RBAC
  - Validación de DTOs con `model_config = ConfigDict(extra="forbid")` rechazando campos inesperados con **HTTP 422**; validación estricta de contraseñas de entrada `<= 72 bytes` (`len(v.encode('utf-8')) <= 72` -> **HTTP 422**, nunca 500)
  - Módulo de seguridad en `parcial/app/core/security.py`: `bcrypt` con costo desde `Settings`, ejecutado mediante `await asyncio.to_thread(...)` y bajo `asyncio.Semaphore` para limitar concurrencia antes de abrir transacciones de base de datos; tokens JWT con PyJWT
  - Endpoints de autenticación en `parcial/app/modules/usuarios/router.py`:
    - `POST /auth/registro`: creación atómica de `Usuario`, rol `CLIENTE` y ficha `Cliente` (409 si email existe)
    - `POST /auth/login`:
      1. Conteo de intentos fallidos en `intento_acceso` para `(email, ip)` en los últimos 60s. Si `>= 5` fallos -> responde **HTTP 429 Too Many Requests** con encabezado `Retry-After: 60`, sin calcular bcrypt
      2. Mitigación de timing attack: si email no existe, calcula bcrypt contra `app.state.fictitious_password_hash` precomputado -> respuesta idéntica y en tiempo constante con **HTTP 401 Unauthorized**
      3. Emisión de cookie `access_token` con `HttpOnly=True`, `SameSite="Lax"`, `Max-Age`. Cuerpo no devuelve token
      4. Rechazo con **HTTP 401** si se envía `Authorization: Bearer ...` o no hay cookie
      5. **Escritura aislada de `intento_acceso`:** persiste en sesión y transacción independientes con commit forzado para sobrevivir al rollback del login fallido. Incluye comentario obligatorio de 3 puntos en el código (qué hace distinto, por qué no comparte transacción y cuál es su costo)
    - `POST /auth/logout`: remoción de cookie de sesión
    - `GET /auth/yo`: retorno de usuario autenticado, roles vigentes en BD y roles en token
    - `POST /auth/cambiar-password`: permitido con `debe_cambiar_password = true`
  - Dependencias de autorización en `parcial/app/core/dependencies.py`:
    - `get_usuario_actual`: extracción de sesión desde cookie
    - Consulta de roles vigentes directamente en la base en cada petición (`revocada_en IS NULL` y `vence_en > now()`)
    - `requiere_rol`: control estricto de acceso (`401` sin sesión vs `403` sin rol)
    - Autoprotección de admin: prohibición de auto-revocación y garantía de al menos un admin activo (**HTTP 409 Conflict**)
    - Validación de `vence_en` con zona horaria y fecha futura (**HTTP 422**)
    - Registro de `evento_seguridad` en transacciones de personal, asignación de rol y cambio de clave
  - Endpoints de administración de usuarios en `parcial/app/modules/usuarios/router.py`: `POST /usuarios`, `GET /usuarios/{id}/roles`, `POST /usuarios/{id}/roles`, `DELETE /usuarios/{id}/roles/{rol}`, `GET /eventos`
  - Tests de integración de seguridad y control de acceso
- **Dependencias**: `C-06`
- **Governance**: CRITICO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §1 Reglas Arquitectónicas (Punto 3: DTOs), §2 Seguridad y Control de Acceso (Puntos 1 a 5)

---

### [C-08] `parcial-catalog-and-stock`
- **Estado**: `[x]` completado
- **Scope**: Catálogo de libros con soft delete, reposición append-only y consultas paginadas
  - Módulos `libros`, `editoriales`, `generos`, `autores` en `parcial/app/modules/`:
  - Repositorio `LibroRepository(SoftDeleteRepository)` y servicios integrados con `UnitOfWork`
  - Esquemas DTOs con `extra="forbid"`
  - `GET /libros`: listado paginado `{items, total, page, size, pages}` (default 20, 422 si `page > pages`), filtros por título y género, excluyendo libros dados de baja (`WHERE borrado_en IS NULL`)
  - `POST /libros` (`ADMIN`): alta de libro recibiendo `stock_inicial` y creando atómicamente el primer `MovimientoStock` (`Stock inicial`)
  - `PATCH /libros/{id}` (`ADMIN`): modificación de título y precio con `model_dump(exclude_unset=True)`; rechazo con **HTTP 422** si intenta alterar stock
  - `DELETE /libros/{id}` (`ADMIN`): soft delete (`borrado_en = func.now()`), retorno de **HTTP 204 No Content**, liberando el ISBN para nuevas altas y preservando historial de ventas
  - `POST /libros/{id}/reponer` (`ADMIN`): incremento de stock registrando `MovimientoStock` (`Reposicion`). Rechaza con **HTTP 409** si el libro tiene `borrado_en IS NOT NULL`
  - `GET /libros/{id}/movimientos` (`ADMIN`): histórico de movimientos de stock
  - Endpoints auxiliares de catálogos: `/editoriales`, `/generos`, `/autores`, `/editoriales/{id}/libros`, `/generos/{id}/libros`, `/autores/{id}/libros`
  - Tests de integración de catálogo, filtros y unicidad condicional de ISBN
- **Dependencias**: `C-06`
- **Governance**: ALTO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §1 Reglas Arquitectónicas (Puntos 2 y 3), §3 Dominio (Puntos 3 y 4)

---

## FASE 6 — Transacciones Atómicas de Ventas y Clientes

### [C-09] `parcial-ventas-transactions`
- **Estado**: [x] completado
- **Scope**: Registro atómico de ventas con descuento de stock bajo Unit of Work, consulta sin N+1 y aviso en segundo plano
  - Módulos `clientes` y `ventas` en `parcial/app/modules/`:
  - `POST /ventas` (`VENDEDOR`, `ADMIN`):
    - Operación atómica en un único UoW
    - Descuenta stock de cada libro y registra `MovimientoStock` negativo (`cantidad = -renglon.cantidad`, `motivo = 'Venta'`) por renglón
    - Precios unitarios copiados del libro en el servidor, total de venta calculado en servidor
    - Si algún libro tiene `borrado_en IS NOT NULL` -> rechazo con **HTTP 409 Conflict**
    - Si algún libro no posee stock suficiente: **rollback completo** de venta, renglones, descuentos y movimientos, devolviendo **HTTP 409 Conflict**
    - Tarea en segundo plano con `BackgroundTasks` simulando aviso de comprobante con `await asyncio.sleep(0.5)` que corre únicamente tras el commit exitoso de la venta
  - `GET /ventas` (`VENDEDOR`, `ADMIN`) paginado con `{items, total, page, size, pages}`
  - `GET /ventas/{id}`:
    - **Sin `requiere_rol` en el router**; el servicio valida pertenencia: personal (`ADMIN`/`VENDEDOR`) o cliente dueño responde `200`; cliente ajeno responde **HTTP 403 Forbidden**
    - Precarga estricta (`joinedload` y `selectinload`) para resolver el detalle de venta con cantidad fija de consultas SQL sin importar el número de renglones (sin $N+1$)
  - `GET /mis-ventas`: listado paginado de ventas del cliente asociado al usuario autenticado
  - Gestión de clientes: `POST /clientes`, `GET /clientes/{id}`, `PATCH /clientes/{id}`, `POST /clientes/{id}/perfil`, `GET /clientes/{id}/ventas`
  - Tests de integración de transacciones atómicas de venta, rollbacks y consultas fijas sin N+1
- **Dependencias**: `C-07`, `C-08`
- **Governance**: CRITICO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §2 Seguridad (Punto 6: Permisos en Detalle de Venta), §3 Dominio (Puntos 3 y 5)

---

## FASE 7 — Datos Iniciales, Casos de Prueba y Despliegue VPS

### [C-10] `parcial-seed-and-e2e-verification`
- **Estado**: `[ ]` pendiente
- **Scope**: Script de carga de datos iniciales (`seed.py`), suite de pruebas C-01 a C-16 y prueba del trigger de sólo agregado
  - Script `parcial/seed.py`:
    - Creación de usuarios: `admin@example.com` y `admin2@example.com` (`ADMIN`), `vendedor@example.com` (`VENDEDOR`), `ana@example.com` (`CLIENTE`), `nuevo@example.com` (`VENDEDOR` con `debe_cambiar_password = true`)
    - Carga de los 5 libros del TP con stock inicial balanceado (`libro.stock == SUM(movimientos)`): `Rayuela` (10), `Antología...` (5), `Ficciones` (8), `Respiración artificial` (3), `Bestiario` (1)
    - Clientes iniciales: Lucía Fernández y Tomás Ríos (sin usuario); Ana Paz (vinculada a `ana@example.com`)
    - Venta inicial 1: Lucía compra 1 Rayuela y 2 Ficciones (Total: 69000.00) con movimientos compensados
    - Registro de seguridad inicial con actor `'SISTEMA'`
  - Suite de pruebas de integración y casos automatizados:
    - Verificación completa de los 16 casos de prueba de la consigna (C-01 a C-16) en `parcial/test/*.http`
  - Archivo `parcial/test/solo_agregado.sql`: verificación del trigger PL/pgSQL que aborta sentencias `UPDATE` y `DELETE` sobre `movimiento_stock` (Caso C-14)
  - Evidencia de consultas fijas para C-15 en `parcial/evidencia/`
  - Documentación de ejecución y reporte en `parcial/README.md`
- **Dependencias**: `C-09`
- **Governance**: ALTO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §4 Casos de Prueba y Datos Iniciales (Puntos 1 y 2)

---

### [C-11] `vps-docker-deployment`
- **Estado**: `[ ]` pendiente
- **Scope**: Despliegue del TP (Capítulos 1 a 4) en carpeta independiente `despliegue/`
  - Carpeta independiente `despliegue/` con el código intacto del TP (Capítulos 1 a 4)
  - `Dockerfile` multi-stage optimizado para el TP (1 a 4) basado en `python:3.12-alpine` (< 100 MB, D-01)
  - Ejecución bajo usuario no root (`USER appuser`, D-07)
  - Sin secretos en la imagen ni archivos `.env` (D-06)
  - Script de arranque con aplicación automática de migraciones y verificación de salud (`HEALTHCHECK` sobre `http://127.0.0.1:8000/health/ready`, D-02)
  - Ejecución con `docker run --env-file`
  - Documento `DEPLOY.md` con comandos y salidas D-01 a D-08 en `despliegue/evidencia/`
- **Dependencias**: `C-04`
- **Governance**: MEDIO
- **Leer antes**:
  - `CONSIGNA_PARCIAL.md` §5 Despliegue en el VPS (`despliegue/`)
