# Tasks: C-07 Parcial Auth and Security

## 1. Seguridad base y contratos de entrada

- [x] 1.1 Escribir tests unitarios en `parcial/tests/unit/test_security.py` para hash/verificación bcrypt fuera del event loop, límite del semáforo, round-trip JWT y rechazo de tokens inválidos/expirados; ejecutar `pytest parcial/tests/unit/test_security.py` y confirmar que fallan (RED).
- [x] 1.2 Implementar `parcial/app/core/security.py` con `bcrypt` vía `asyncio.to_thread` bajo `asyncio.Semaphore`, helpers de hash/verify y emisión/decodificación JWT con PyJWT; verificar que los tests de 1.1 pasan (GREEN).
- [x] 1.3 Agregar `BCRYPT_MAX_CONCURRENCY` a `Settings` y a `.env.example`; escribir primero el test de configuración y verificar que falla, luego implementarlo y confirmar `pytest parcial/tests/unit/test_config.py` en verde.
- [x] 1.4 Escribir tests de DTOs que cubran `extra="forbid"` (HTTP 422), contraseña de 72 bytes aceptada y 73+ bytes rechazada con 422 (nunca 500); implementar `parcial/app/modules/usuarios/schemas.py` y verificar los tests en verde.
- [x] 1.5 Documentar en `.env.example` las variables de seguridad usadas (`COOKIE_SECURE`, `BCRYPT_MAX_CONCURRENCY`, `ACCESS_TOKEN_EXPIRE_MINUTES`) y verificar que el archivo conserva formato de entorno válido.

## 2. Repositorios y sesión aislada de intentos

- [x] 2.1 Escribir tests de repositorio contra PostgreSQL de test para `get_by_email`, roles vigentes (`revocada_en IS NULL` y `vence_en` nulo o futuro), bloqueo de administradores activos y listado de eventos; implementar `parcial/app/modules/usuarios/repository.py` y verificar los tests en verde.
- [x] 2.2 Escribir un test que fuerce el rollback del UoW del login y compruebe que el `intento_acceso` sigue persistido; implementar la dependencia `get_sessionmaker` y el helper de escritura aislada con commit forzado, incluyendo el comentario obligatorio de 3 puntos (qué hace distinto, por qué no comparte transacción y su costo), y verificar el test en verde.
- [x] 2.3 Implementar el repositorio/helper de `evento_seguridad` con actor y acción, y verificar con un test que un evento insertado en el mismo UoW de una mutación se revierte si la mutación falla.

## 3. Endpoints de autenticación

- [x] 3.1 Escribir tests de integración de `POST /auth/registro` (alta atómica de usuario + rol `CLIENTE` + `Cliente`, 409 por email duplicado, 422 por campo extra, 422 por contraseña > 72 bytes, respuesta sin `password_hash`); implementar el servicio y el router de registro y verificar los tests en verde.
- [x] 3.2 Escribir tests de `POST /auth/login` para el orden de evaluación: 5 fallos en 60 s → 429 con `Retry-After: 60` y sin bcrypt, email inexistente → 401 genérico con verificación contra el hash ficticio, credenciales válidas → 200; implementar el flujo y verificar los tests en verde.
- [x] 3.3 Escribir tests de cookie de sesión: login exitoso setea `access_token` `HttpOnly`, `SameSite=Lax`, `Max-Age` y `Secure` configurable; el cuerpo no incluye el token; `POST /auth/logout` elimina la cookie; `Authorization: Bearer` y ausencia de cookie responden 401; implementar y verificar los tests en verde.
- [x] 3.4 Escribir tests de `GET /auth/yo` (datos del usuario, roles vigentes de BD, roles informativos del token, sin `password_hash`) y de `POST /auth/cambiar-password` (permitido con `debe_cambiar_password=true`, limpia la marca, registra evento, 422 por contraseña > 72 bytes); implementar ambos endpoints y verificar los tests en verde.
- [x] 3.5 Montar el router de autenticación dentro del grupo abierto de `parcial/app/main.py` y verificar con un test que `/auth/registro`, `/auth/login`, `/auth/logout`, `/auth/yo` y `/auth/cambiar-password` son alcanzables sin el gate de cambio de contraseña.

## 4. Autorización dinámica y grupo protegido

- [x] 4.1 Escribir tests de `get_usuario_actual`: cookie válida resuelve el usuario, cookie ausente/inválida/expirada o usuario inactivo responde 401; implementar la dependencia en `parcial/app/core/dependencies.py` y verificar los tests en verde.
- [x] 4.2 Escribir tests de `requiere_rol`: sesión sin rol → 403, sin sesión → 401, revocación inmediata del rol → 403 en la petición siguiente; implementar `requiere_rol` consultando roles vigentes en BD y verificar los tests en verde.
- [x] 4.3 Actualizar `verificar_no_debe_cambiar_password` para depender de `get_usuario_actual`, responder 401 sin sesión y 403 con `debe_cambiar_password=true`; adaptar `parcial/tests/unit/test_lifespan.py` al nuevo contrato y confirmar que la suite de lifespan pasa en verde.
- [x] 4.4 Escribir un test de composición que verifique que el grupo protegido aplica el gate centralizado y que los endpoints reales de administración quedan custodiados; conectar el router protegido y verificar el test en verde.

## 5. Administración de usuarios, roles y eventos

- [x] 5.1 Escribir tests de `POST /usuarios` (ADMIN crea personal con rol `ADMIN`/`VENDEDOR`, contraseña temporal, `debe_cambiar_password` por defecto `true`, 409 por email duplicado, 422 por rol inválido y por contraseña > 72 bytes); implementar el endpoint y verificar los tests en verde.
- [x] 5.2 Escribir tests de `GET /usuarios/{id}/roles` y `POST /usuarios/{id}/roles` (listado paginado, asignación de rol, 404 por usuario inexistente, 422 por `vence_en` naive o pasado, 409 por asignación activa duplicada); implementar y verificar los tests en verde.
- [x] 5.3 Escribir tests de `DELETE /usuarios/{id}/roles/{rol}`: revocación exitosa, 404 sin asignación activa, 409 por auto-revocación de `ADMIN` y 409 si dejaría el sistema sin administradores vigentes; implementar con bloqueo `SELECT ... FOR UPDATE` y verificar los tests en verde.
- [x] 5.4 Escribir tests de `GET /eventos` (sólo ADMIN, envoltorio `{items,total,page,size,pages}`, default 20, 422 si `page > pages`) y verificar la implementación en verde.
- [x] 5.5 Escribir tests de auditoría que comprueben un evento por alta de personal, asignación de rol, revocación de rol y cambio de contraseña, con actor y acción; implementar los registros dentro del mismo UoW y verificar los tests en verde.
- [x] 5.6 Verificar con tests de integración que todos los endpoints de administración responden 403 a un usuario sin rol `ADMIN` y 401 sin sesión.

## 6. Integración, regresión y documentación

- [x] 6.1 Crear `parcial/tests/integration/conftest.py` con engine de PostgreSQL de test, creación de esquema con `Base.metadata.create_all`, truncado entre tests y overrides de `get_session`/`get_sessionmaker`; verificar que los tests de integración de este change corren con `docker compose up -d` y `pytest parcial/tests/integration`.
- [x] 6.2 Ejecutar la suite completa `pytest` y confirmar cero regresiones, incluyendo los tests de `tests/` y `parcial/tests/`; registrar la evidencia de RED/GREEN por tarea para el resumen de apply.
- [x] 6.3 Actualizar la documentación de ejecución y seguridad en `README.md` (variables nuevas, comando de tests de integración y comportamiento de cookies) y verificar que los comandos documentados se ejecutan tal como están escritos.

## Workflow follow-up

- Ejecutar `openspec validate c-07-parcial-auth-and-security --strict` y corregir cualquier observación.
- Archivar el change con `openspec archive c-07-parcial-auth-and-security` cuando la revisión esté aprobada.
- Marcar como completado el checkbox de `C-07` en `CHANGES.md`.
