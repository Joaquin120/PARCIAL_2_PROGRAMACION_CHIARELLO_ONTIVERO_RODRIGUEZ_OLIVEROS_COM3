# Proposal: C-07 Parcial Auth and Security

## Why

C-06 ya materializó las tablas de seguridad (`usuario`, `asignacion_rol`, `intento_acceso`, `evento_seguridad`) y la infraestructura transaccional de C-05, pero la aplicación no autentica ni autoriza todavía: los grupos de rutas abierto/protegido de `parcial/app/main.py` existen pero son inertes. Sin esta capa no pueden cumplirse los casos de seguridad exigidos en `CONSIGNA_PARCIAL.md` §2 (cookies HttpOnly, límite de 72 bytes en contraseñas, rate limiting, mitigación de timing attacks, RBAC dinámico y autoprotección de administradores).

## What Changes

- **Contratos estrictos de seguridad**: DTOs de entrada con `ConfigDict(extra="forbid")` y validación de contraseñas por longitud en bytes UTF-8 (`<= 72`; exceder → **HTTP 422**, nunca 500).
- **Módulo de seguridad** `parcial/app/core/security.py`: hash/verificación bcrypt con costo desde `Settings`, ejecutado con `await asyncio.to_thread(...)` bajo un `asyncio.Semaphore` y **antes** de abrir transacciones; emisión/decodificación de JWT con PyJWT.
- **Endpoints de autenticación** en `parcial/app/modules/usuarios/router.py`:
  - `POST /auth/registro`: alta atómica de `Usuario` + rol `CLIENTE` + ficha `Cliente`; **HTTP 409** si el email ya existe.
  - `POST /auth/login`: rate limiting por `(email, ip)` sobre los últimos 60 s (≥ 5 fallos → **HTTP 429** con `Retry-After: 60`, sin bcrypt); mitigación de timing attack contra `app.state.fictitious_password_hash` cuando el email no existe (**HTTP 401** genérico); cookie `access_token` `HttpOnly`, `SameSite=Lax`, `Max-Age` y `Secure` configurable; el cuerpo **no** devuelve el token; cada intento se persiste en una **sesión y transacción aisladas** con commit forzado.
  - `POST /auth/logout`, `GET /auth/yo` (roles vigentes en BD y roles informativos del token) y `POST /auth/cambiar-password` (permitido con `debe_cambiar_password = true`).
  - Rechazo con **HTTP 401** cuando se envía `Authorization: Bearer ...` o cuando no hay cookie de sesión.
- **Dependencias de autorización** en `parcial/app/core/dependencies.py`:
  - `get_usuario_actual`: extracción exclusiva de la cookie `access_token`.
  - `requiere_rol`: consulta de roles vigentes en BD en cada petición (`revocada_en IS NULL` y `vence_en` nulo o futuro); **401** sin sesión, **403** sin rol. Revocar un rol surte efecto de inmediato.
  - Autoprotección de admin: prohibición de auto-revocar `ADMIN` y de dejar el sistema sin administradores vigentes (**HTTP 409**).
  - Validación de `vence_en`: obligatoriamente con zona horaria y futura (**HTTP 422**).
  - Registro de `evento_seguridad` en alta de personal, asignación/revocación de rol y cambio de contraseña.
- **Endpoints de administración** (grupo protegido + rol `ADMIN`): `POST /usuarios`, `GET /usuarios/{id}/roles`, `POST /usuarios/{id}/roles`, `DELETE /usuarios/{id}/roles/{rol}` y `GET /eventos`.
- **Grupos de rutas**: conectar los routers reales de autenticación al grupo abierto y los de administración de usuarios al grupo protegido, manteniendo el gate centralizado de `debe_cambiar_password`.
- **Tests de integración** de autenticación, rate limiting, timing mitigation, cookies HttpOnly, RBAC dinámico, autoprotección y contratos 422/401/403/409/429.

## Capabilities

### New Capabilities

- `parcial-authentication`: registro, login/logout con cookie HttpOnly, JWT, cambio de contraseña, rate limiting, mitigación de timing attacks y límite de 72 bytes.
- `parcial-authorization`: resolución del usuario desde cookie, RBAC dinámico contra `asignacion_rol`, autoprotección de administradores, validación de vigencia y auditoría de eventos de seguridad.

### Modified Capabilities

- `parcial-application-core`: se precisan los semánticas de acceso de los grupos abierto/protegido: una petición sin sesión válida al grupo protegido responde **401**, mientras que una sesión con `debe_cambiar_password = true` responde **403**, y el grupo abierto de autenticación queda operativo.

## Impact

- **Nuevos archivos**: `parcial/app/core/security.py`, `parcial/app/modules/usuarios/{schemas,repository,service,router}.py` y tests en `parcial/tests/integration/`.
- **Archivos modificados**: `parcial/app/core/dependencies.py`, `parcial/app/main.py`, posiblemente `parcial/app/core/config.py` (semáforo/concurrencia bcrypt si se parametriza).
- **API**: nuevos endpoints `/auth/*`, `/usuarios*` y `/eventos`; el contrato existente `/health*` no cambia.
- **Base de datos**: sin cambios de esquema; se usan las tablas y constraints creados en C-06.
- **Dependencias**: `bcrypt` y `pyjwt` ya declarados en `requirements.txt` y `pyproject.toml`.
- **Fuera de alcance**: catálogo de libros (C-08), ventas/clientes (C-09) y seed/E2E (C-10).
