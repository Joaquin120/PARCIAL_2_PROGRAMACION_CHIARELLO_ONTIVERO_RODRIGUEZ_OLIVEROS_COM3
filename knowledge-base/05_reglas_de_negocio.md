# 05 — Reglas de Negocio y Políticas Técnicas

Las reglas técnicas y operativas del sistema se codifican bajo el prefijo `RN-{DOMINIO}-{NN}` para garantizar trazabilidad con las pruebas y los criterios de aceptación.

## Dominio: Configuración Centralizada (RN-CFG)

- **RN-CFG-01 — Inmutabilidad y Carga en Arranque**: Las configuraciones deben cargarse al instanciar la aplicación desde variables de entorno y archivo `.env` mediante una clase que herede de `pydantic_settings.BaseSettings`.
- **RN-CFG-02 — Validación Estricta de Tipos**: Si una variable requerida (como `DATABASE_URL`) no está presente o contiene un formato inválido (ej. esquema distinto de `postgresql+asyncpg://`), la aplicación debe lanzar un error `ValidationError` durante el arranque y terminar inmediatamente la ejecución (Fail-Fast).
- **RN-CFG-03 — Secretos fuera del código**: Ninguna clave sensible, password de base de datos o token debe estar hardcodeado en el código fuente. El archivo `.env` debe estar excluido en `.gitignore`.
- **RN-CFG-04 — Singleton vía Cache**: La instancia de configuración debe exponerse a través de una función `get_settings()` decorada con `@lru_cache()` para evitar lecturas redundantes del entorno en cada petición.

## Dominio: Ciclo de Vida y Lifespan (RN-LFS)

- **RN-LFS-01 — Lifespan Moderno Asíncrono**: El ciclo de vida de FastAPI debe gestionarse exclusivamente mediante un gestor de contexto asíncrono con el decorador `@asynccontextmanager(app: FastAPI)` en conformidad con el estándar ASGI Lifespan. Se prohíbe el uso de los decoradores deprecados `@app.on_event("startup")` y `@app.on_event("shutdown")`.
- **RN-LFS-02 — Verificación de Conectividad en Startup**: En la fase de arranque del lifespan, la aplicación debe ejecutar una consulta de prueba asíncrona (`SELECT 1`) sobre PostgreSQL. Si la conexión falla, se debe registrar el error en los logs con nivel `CRITICAL` y abortar el inicio de la API.
- **RN-LFS-03 — Cierre Gracioso en Shutdown**: En la fase de cierre del lifespan (captura de señales `SIGINT` o `SIGTERM`), la aplicación debe invocar `await engine.dispose()` para cerrar ordenadamente todas las conexiones abiertas en el pool de `asyncpg`.

## Dominio: Diagnóstico y Salud del Servicio (RN-HLT)

- **RN-HLT-01 — Diagnóstico Liveness Aislado**: El endpoint `GET /health/live` (o `GET /health`) debe comprobar únicamente que el servidor web FastAPI está vivo y procesando peticiones. No debe verificar dependencias externas como bases de datos para evitar cascading failures. Debe responder con status HTTP `200 OK`.
- **RN-HLT-02 — Diagnóstico Readiness con Base de Datos**: El endpoint `GET /health/ready` debe comprobar activamente la disponibilidad de PostgreSQL ejecutando `SELECT 1` con un timeout máximo de 2 segundos.
  - Si la base responde exitosamente: Debe responder HTTP `200 OK` con payload `{"status": "ready", "database": "connected"}`.
  - Si la base falla o no responde dentro del timeout: Debe responder HTTP `503 Service Unavailable` con payload `{"status": "unhealthy", "database": "disconnected", "error": "<mensaje resumido>"}`.

## Dominio: Manejo de Sesiones de Base de Datos (RN-SES)

- **RN-SES-01 — Scope por Petición (Session per Request)**: Toda interacción con la base de datos dentro de un endpoint debe utilizar una sesión asíncrona obtenida mediante la dependencia inyectable `get_db()`.
- **RN-SES-02 — Cierre Obligatorio de Sesión**: La dependencia `get_db()` debe utilizar un bloque `try...finally` asegurando que la sesión siempre se cierre (`await session.close()`) al finalizar la petición, incluso en caso de excepciones no controladas.
