# 06 — Funcionalidades e Historias de Usuario

Las funcionalidades de la etapa fundacional se organizan por épicas y se especifican en formato User Story (US-NNN).

---

## Épica 1: Configuración Tipada y Ciclo de Vida

### US-001 — Configuración centralizada con Pydantic Settings
**Como** desarrollador del sistema  
**Quiero** centralizar todas las variables y parámetros de entorno en una clase tipada con Pydantic  
**Para** asegurar que la aplicación valide en tiempo de booteo sus dependencias críticas y prevenga fallos en runtime.

**Criterios de Aceptación**:
- [ ] CA-1.1: Existe un modelo `Settings` en `src/core/config.py` que lee desde variables de entorno y archivo `.env`.
- [ ] CA-1.2: Contiene al menos las variables: `ENVIRONMENT`, `PROJECT_NAME`, `DEBUG`, `DATABASE_URL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`.
- [ ] CA-1.3: Si `DATABASE_URL` no está definida o no comienza con `postgresql+asyncpg://`, la inicialización falla con `ValidationError`.
- [ ] CA-1.4: La función `get_settings()` retorna la instancia cacheada como singleton.

**Reglas de negocio relacionadas**: RN-CFG-01, RN-CFG-02, RN-CFG-03, RN-CFG-04.

---

### US-002 — Ciclo de vida administrado por Lifespan
**Como** operador o desarrollador del backend  
**Quiero** gestionar el arranque y apagado del servidor con un gestor de contexto asíncrono  
**Para** garantizar que la conexión a la base de datos se verifique antes de aceptar tráfico y se libere limpiamente al terminar el proceso.

**Criterios de Aceptación**:
- [ ] CA-2.1: FastAPI se inicializa pasando un parámetro `lifespan` basado en `@asynccontextmanager`.
- [ ] CA-2.2: En el startup se ejecuta una prueba de conexión asíncrona hacia PostgreSQL (`ping`).
- [ ] CA-2.3: Si el ping falla en el arranque, se propaga la excepción o se loguea críticamente interrumpiendo el inicio del servicio.
- [ ] CA-2.4: En el shutdown se invoca `engine.dispose()` liberando todas las conexiones del pool sin emitir advertencias de recursos pendientes.

**Reglas de negocio relacionadas**: RN-LFS-01, RN-LFS-02, RN-LFS-03.

---

## Épica 2: Conexión Asíncrona a PostgreSQL

### US-003 — Pool de conexiones con SQLAlchemy 2.0 y asyncpg
**Como** desarrollador de la aplicación  
**Quiero** configurar un `AsyncEngine` y un `async_sessionmaker` optimizados  
**Para** permitir operaciones de base de datos no bloqueantes y reutilizar conexiones eficientemente.

**Criterios de Aceptación**:
- [ ] CA-3.1: Se crea `engine` usando `create_async_engine` configurado con `pool_size`, `max_overflow`, y `pool_pre_ping=True`.
- [ ] CA-3.2: Se define `async_sessionmaker` con `expire_on_commit=False` y `class_=AsyncSession`.
- [ ] CA-3.3: La dependencia `get_db()` inyecta una sesión asíncrona por request y garantiza su cierre al terminar.

**Reglas de negocio relacionadas**: RN-SES-01, RN-SES-02.

---

## Épica 3: Observabilidad y Healthchecks

### US-004 — Endpoint de Liveness (Salud de Proceso)
**Como** orquestador de contenedores o evaluador  
**Quiero** consultar un endpoint HTTP `/health/live` (o `/health`)  
**Para** certificar que el proceso del servidor web está en ejecución y puede responder peticiones HTTP.

**Criterios de Aceptación**:
- [ ] CA-4.1: Retorna código HTTP `200 OK` con payload JSON conteniendo `{"status": "alive", "service": "..."}`.
- [ ] CA-4.2: La respuesta es instantánea (< 5ms) y no realiza llamadas a la base de datos.

**Reglas de negocio relacionadas**: RN-HLT-01.

---

### US-005 — Endpoint de Readiness (Preparación del Servicio)
**Como** evaluador o balanceador de carga  
**Quiero** consultar el endpoint HTTP `/health/ready`  
**Para** conocer si la aplicación tiene conectividad operativa con PostgreSQL y está lista para atender consultas de datos.

**Criterios de Aceptación**:
- [ ] CA-5.1: Ejecuta `SELECT 1` asíncronamente con un timeout máximo de 2 segundos.
- [ ] CA-5.2: Si PostgreSQL responde, retorna HTTP `200 OK` y `{"status": "ready", "database": "connected"}`.
- [ ] CA-5.3: Si PostgreSQL está apagado o falla la conexión, retorna HTTP `503 Service Unavailable` y `{"status": "unhealthy", "database": "disconnected"}`.

**Reglas de negocio relacionadas**: RN-HLT-02.
