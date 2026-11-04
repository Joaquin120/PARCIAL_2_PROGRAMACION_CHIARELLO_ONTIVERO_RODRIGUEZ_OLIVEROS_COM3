# 07 — Flujos Principales del Sistema

Este documento describe la secuencia paso a paso de los flujos de ejecución críticos de la etapa fundacional.

---

## Flujo 1: Arranque y Booteo de la Aplicación (Startup Lifespan)

**Disparador**: Ejecución del servidor ASGI (`uvicorn src.main:app`).  
**Actor**: Servidor de Aplicaciones / Runtime Python.

### Pasos:
1. Uvicorn inicializa el bucle de eventos (`asyncio`).
2. Se instancia la aplicación FastAPI referenciando el `lifespan`.
3. El `lifespan` entra en su fase inicial antes del `yield`:
   - Invoca `get_settings()` para validar variables de entorno desde `.env`.
   - Inicializa el `AsyncEngine` de SQLAlchemy con la URL de base de datos parseada.
   - Intenta abrir una conexión liviana y ejecutar `SELECT 1` para validar PostgreSQL.
   - Si la conexión es exitosa: emite un log informativo `[INFO] Database connection verified successfully.`
   - Si la conexión falla: emite un log crítico `[FATAL] Unable to connect to PostgreSQL.` y propaga la excepción o detiene el booteo.
4. El `lifespan` ejecuta `yield`, cediendo el control a FastAPI para comenzar a aceptar peticiones HTTP entrantes.

```
+-----------+            +---------------+             +-------------+            +------------+
|  Uvicorn  |            | FastAPI / App |             |  Lifespan   |            | PostgreSQL |
+-----------+            +---------------+             +-------------+            +------------+
      |                         |                             |                          |
      |--- 1. Iniciar ASGI ---->|                             |                          |
      |                         |--- 2. Iniciar Lifespan ---->|                          |
      |                         |                             |--- 3. get_settings() --->| (Local .env)
      |                         |                             |--- 4. SELECT 1 --------->|
      |                         |                             |<-- 5. OK (Conectado) ----|
      |                         |<-- 6. yield (Listo) --------|                          |
      |<-- 7. Aceptando HTTP ---|                             |                          |
```

---

## Flujo 2: Consulta del Endpoint de Readiness (`GET /health/ready`)

**Disparador**: Petición HTTP entrante a `/health/ready`.  
**Actor**: Monitor de salud, evaluador o script de pruebas.

### Pasos:
1. La petición llega al router de health en `src/api/v1/endpoints/health.py`.
2. El handler obtiene una sesión de base de datos a través de `Depends(get_db)`.
3. El handler ejecuta de forma asíncrona: `await db.execute(text("SELECT 1"))`.
4. **Camino Exitoso**:
   - PostgreSQL responde el valor `1`.
   - El endpoint retorna HTTP `200 OK` con metadata de tiempo y estado `ready`.
5. **Camino de Error (Excepción o Timeout)**:
   - Se captura `SQLAlchemyError` o `asyncio.TimeoutError`.
   - El handler loguea la falla y responde con HTTP `503 Service Unavailable` indicando `database: disconnected`.
6. La sesión de base de datos se cierra automáticamente en el bloque `finally` del generador `get_db()`.

---

## Flujo 3: Apagado Gracioso del Backend (Shutdown Lifespan)

**Disparador**: Señal del sistema operativo `SIGINT` (Ctrl+C) o `SIGTERM` (detención del contenedor Docker).  
**Actor**: Sistema Operativo / Docker Daemon.

### Pasos:
1. Uvicorn intercepta la señal de terminación y suspende la recepción de nuevas conexiones HTTP.
2. Espera a que las peticiones en vuelo terminen su ciclo.
3. El control retorna al `lifespan` inmediatamente después del `yield`.
4. El bloque de cleanup se ejecuta:
   - Invoca `await engine.dispose()`.
   - El pool de conexiones de `asyncpg` cierra todos los sockets TCP abiertos con PostgreSQL de manera limpia.
   - Emite un log `[INFO] Database connections successfully closed. Application shutdown complete.`
5. El proceso termina con código de salida `0`.
