# Design: C-07 Parcial Auth and Security

## Context

Ver `proposal.md` para la motivación. El estado actual relevante:

- `parcial/app/core/config.py` ya expone `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `BCRYPT_ROUNDS` y `COOKIE_SECURE`.
- `parcial/app/core/database.py` expone `engine`, `async_session_factory` y la dependencia `get_session()` (una sesión por request).
- `parcial/app/core/unit_of_work.py` recibe la sesión inyectada y hace `commit`/`rollback` sin cerrarla.
- `parcial/app/core/dependencies.py` sólo contiene un stub `verificar_no_debe_cambiar_password` que lee `request.state.user` y permite el paso si no existe usuario.
- `parcial/app/main.py` ya declara `open_router` y `protected_router`, con un endpoint de muestra `/protected/ping`.
- C-06 ya creó `Usuario`, `AsignacionRol`, `IntentoAcceso`, `EventoSeguridad` y la ficha `Cliente` con `usuario_id` único.
- Las dependencias `bcrypt>=4.0.0` y `pyjwt>=2.8.0` ya están declaradas.

Restricciones de la consigna: capas `Router -> Service -> Unit of Work -> Repository -> Model`; el UoW y las dependencias de seguridad deben compartir la sesión del request; bcrypt fuera del event loop y antes de abrir transacciones; ningún repositorio hace commit.

## Goals / Non-Goals

**Goals:**

- Implementar registro, login, logout, identidad y cambio de contraseña con JWT en cookie HttpOnly.
- Implementar RBAC dinámico contra `asignacion_rol`, autoprotección de administradores y auditoría en `evento_seguridad`.
- Exponer los endpoints administrativos de usuarios, roles y eventos.
- Cubrir con tests los contratos 422/401/403/409/429, el rate limiting, la mitigación de timing y la convivencia de sesiones.

**Non-Goals:**

- Cambios de esquema o migraciones: las tablas de C-06 son suficientes.
- Catálogo público, libros, ventas y clientes (C-08/C-09).
- Seed y suite E2E de los 16 casos (C-10).
- Un sistema distribuido de rate limiting (Redis): la consigna exige persistencia en `intento_acceso`.

## Decisions

### 1. Composición de capas y sesión compartida

- **Decisión:** Los routers inyectan `UnitOfWork` construido con la sesión de `get_session()`; los servicios reciben el UoW y nunca la sesión. `get_usuario_actual`, `requiere_rol` y el UoW declaran `Depends(get_session)`, y FastAPI reutiliza la misma instancia de sesión por request (cache de dependencias).
- **Razón:** Cumple la regla arquitectónica y evita agotar el pool. Alternativa descartada: que el UoW cree su propia sesión, lo que rompería la transacción compartida con las dependencias de seguridad.

### 2. Persistencia aislada de `intento_acceso`

- **Decisión:** Un helper dedicado abre una sesión nueva desde el `async_sessionmaker` (inyectable vía una dependencia `get_sessionmaker`), escribe el intento, hace `commit()` y cierra la sesión. No participa del UoW del login.
- **Razón:** El commit debe sobrevivir al rollback del login fallido. Alternativa descartada: usar el mismo UoW; el rollback borraría el intento y el rate limiting nunca acumularía fallos. **Costo asumido:** quedan filas aunque la petición falle y se consume una conexión extra por intento. El código incluirá el comentario obligatorio de 3 puntos exigido por la consigna.

### 3. Orden estricto del login

- **Decisión:** (1) contar fallos de `(email, ip)` en los últimos 60 s; si `>= 5`, persistir el intento rechazado y responder 429 con `Retry-After: 60` sin bcrypt; (2) verificar credenciales; si el email no existe, verificar contra `app.state.fictitious_password_hash`; (3) persistir el intento en sesión aislada; (4) emitir cookie sólo si el usuario existe, está activo y la contraseña es correcta.
- **Razón:** Reproduce el orden textual de la consigna y garantiza que el 429 sea barato. Alternativa descartada: contar después de bcrypt, que permitiría agotar CPU con intentos bloqueados.

### 4. Bcrypt fuera del event loop y con concurrencia acotada

- **Decisión:** `parcial/app/core/security.py` ejecuta `bcrypt.hashpw`/`bcrypt.checkpw` con `await asyncio.to_thread(...)` dentro de un `asyncio.Semaphore`. El tamaño del semáforo se toma de una nueva setting `BCRYPT_MAX_CONCURRENCY` (default 4). El hash se calcula antes de `async with uow:`.
- **Razón:** Cumple la consigna sin bloquear el event loop y limita el consumo de CPU. Alternativa descartada: `passlib` (no está en el proyecto) o ejecutar bcrypt en el loop (bloqueante).

### 5. Validación del límite de 72 bytes en el DTO

- **Decisión:** Los esquemas usan `field_validator` y comprueban `len(valor.encode("utf-8")) <= 72`; un exceso produce un error de validación de Pydantic (HTTP 422). Se valida también la contraseña actual en el cambio.
- **Razón:** Evita que bcrypt lance una excepción y se traduzca en 500. Alternativa descartada: recortar silenciosamente la contraseña, que cambia el secreto del usuario.

### 6. JWT en cookie y rechazo de Bearer

- **Decisión:** JWT HS256 con claims `sub` (id), `email`, `roles` (informativos), `iat` y `exp`. La cookie `access_token` se emite con `HttpOnly=True`, `SameSite="Lax"`, `Max-Age=ACCESS_TOKEN_EXPIRE_MINUTES*60`, `Secure=COOKIE_SECURE` y `path="/"`. La extracción de identidad lee únicamente la cookie; si hay `Authorization: Bearer` o no hay cookie, responde 401.
- **Razón:** La consigna prohíbe el token en el cuerpo y el uso de Bearer. Alternativa descartada: devolver el token en JSON o aceptar ambos mecanismos.

### 7. RBAC dinámico en cada request

- **Decisión:** `requiere_rol(*roles)` consulta `asignacion_rol` con `revocada_en IS NULL` y `(vence_en IS NULL OR vence_en > now())` en cada petición. Los roles del JWT sólo se devuelven en `/auth/yo` como información.
- **Razón:** La revocación debe surtir efecto en la petición inmediata. Alternativa descartada: confiar en los roles del token, que quedarían obsoletos hasta el próximo login.

### 8. Autoprotección de administradores con bloqueo

- **Decisión:** Antes de revocar `ADMIN`, el servicio bloquea con `SELECT ... FOR UPDATE` las asignaciones `ADMIN` activas. Si el objetivo es el propio actor o si el conteo quedaría en cero, responde 409 y revierte el UoW. Una asignación activa duplicada se traduce en 409.
- **Razón:** Evita la carrera entre dos revocaciones concurrentes que dejarían el sistema sin administradores. Alternativa descartada: contar sin bloqueo, que es vulnerable a concurrencia.

### 9. Validación de `vence_en`

- **Decisión:** El DTO exige un `datetime` con `tzinfo` no nulo y lo compara contra `datetime.now(timezone.utc)`; naive o pasado produce 422. El rol se restringe a `ADMIN`/`VENDEDOR` para alta de personal y a los tres valores para asignaciones administrativas.
- **Razón:** Cumple la consigna y evita fechas ambiguas. Alternativa descartada: asumir UTC para valores naive, que oculta errores del cliente.

### 10. Auditoría dentro de la misma transacción

- **Decisión:** `evento_seguridad` se inserta mediante el mismo UoW que la mutación auditada (alta de personal, asignación/revocación, cambio de contraseña). El actor es el email del usuario autenticado y la acción es un texto estable (`USUARIO_CREADO`, `ROL_ASIGNADO`, `ROL_REVOCADO`, `PASSWORD_CAMBIADO`).
- **Razón:** La auditoría no debe quedar si la mutación falla. Alternativa descartada: `BackgroundTasks`, que puede perder el evento.

### 11. Contratos de respuesta

- **Decisión:** `POST /auth/registro` → 201 con datos públicos del usuario y sus roles; `POST /auth/login` → 200 con datos públicos, sin token; `POST /auth/logout` → 204; `GET /auth/yo` → 200 con `roles_vigentes` (BD) y `roles_token`; `POST /auth/cambiar-password` → 200 con mensaje; administración → 201/200/204 según operación. Los listados usan `PaginatedResponse` de `parcial/app/core/paginacion.py`.
- **Razón:** Coherencia con el resto del proyecto y ausencia de `password_hash`. Alternativa descartada: respuestas ad-hoc por endpoint.

### 12. Estrategia de tests

- **Decisión:** Tests unitarios para validadores de 72 bytes, DTOs con `extra="forbid"`, JWT y bcrypt; tests de integración con PostgreSQL real (servicio de `docker-compose.yml`) usando un engine de test, `Base.metadata.create_all`, truncado entre tests y `app.dependency_overrides` para `get_session` y `get_sessionmaker`.
- **Razón:** El comportamiento depende de SQL real (índices parciales, `now()`, concurrencia). Alternativa descartada: un `FakeAsyncSession` manual, que ya demostró ser frágil con consultas SQLAlchemy complejas.

### 13. Impacto en los tests existentes del grupo protegido

- **Decisión:** Adaptar `parcial/tests/unit/test_lifespan.py`: el endpoint de muestra `/protected/ping` deja de ser público. Los tests que hoy esperan 200 sin cookie deben autenticarse (o sobrescribir `get_usuario_actual`) y el caso de `debe_cambiar_password = true` sigue esperando 403.
- **Razón:** El nuevo contrato exige 401 sin sesión; dejar el test intacto produciría una regresión falsa. Alternativa descartada: mantener `/protected/ping` fuera del gate, lo que contradice la consigna.

## Risks / Trade-offs

- **[Carrera en el conteo de rate limiting]** → El conteo y la inserción no son atómicos. *Mitigación:* aceptar la ventana deslizante aproximada; los tests usan intentos secuenciales deterministas. Si se requiere estrictez, se puede bloquear por `(email, ip)` en una iteración futura.
- **[El hash ficticio es fijo durante la vida del proceso]** → *Mitigación:* se sigue precomputando en el lifespan con el costo configurado, tal como ya existe; no se almacena ninguna contraseña real.
- **[Bcrypt con costo 12 hace lentos los tests]** → *Mitigación:* `BCRYPT_ROUNDS=4` en el entorno de test y semáforo configurable.
- **[IP detrás de un proxy]** → `request.client.host` puede ser la IP del proxy. *Mitigación:* se documenta como supuesto; no se confía en `X-Forwarded-For` sin un proxy confiable configurado.
- **[Compatibilidad de cookies en clientes de test]** → `httpx.AsyncClient` mantiene cookies automáticamente; los tests que necesiten simular ausencia de cookie usan un cliente nuevo. *Mitigación:* fixtures explícitas por escenario.
- **[Tests de integración requieren PostgreSQL]** → *Mitigación:* documentar `docker compose up -d` y usar una base de test dedicada; los tests unitarios no requieren motor.
- **[El grupo protegido ahora exige sesión]** → *Mitigación:* actualizar los tests existentes de `test_lifespan.py` y cualquier endpoint de muestra; los endpoints reales se montarán en C-08/C-09.

## Migration Plan

1. Implementar `security.py` y los DTOs; ejecutar los tests unitarios nuevos.
2. Extender `dependencies.py` y montar autenticación y administración en `main.py`.
3. Adaptar los tests existentes del grupo protegido.
4. Ejecutar la suite completa (`pytest`) con PostgreSQL de test levantado.
5. Sin migraciones de esquema; rollback = revertir los archivos nuevos y las modificaciones de `main.py`/`dependencies.py`.

## Open Questions

- Ninguna que bloquee el diseño. El formato exacto de los mensajes de error y el nombre de las acciones de auditoría se fijan en la implementación y quedan cubiertos por los tests de contrato.
