# Design: C-05 Parcial Core UoW

## Context

El proyecto finalizó los capítulos 1 a 4 del TP ubicados en `src/`. El Parcial introduce requisitos estrictos de negocio y arquitectura (Capítulos 1 a 6 de `CONSIGNA_PARCIAL.md`). Para garantizar que el TP permanezca inalterado para el posterior despliegue en VPS (`despliegue/`), se crea el nuevo espacio de trabajo en `parcial/app/core/`. Véase `proposal.md` para la motivación general.

## Goals / Non-Goals

**Goals:**
- Implementar la infraestructura central del Parcial en `parcial/app/core/`: `config.py`, `database.py`, `repository.py`, `unit_of_work.py`, `paginacion.py` y `main.py`.
- Diseñar el `UnitOfWork` asíncrono para delegar la creación y el cierre de la sesión física a FastAPI (`get_session`), administrando únicamente los límites de transacción (`commit` y `rollback`).
- Implementar `BaseRepository[T]` y `SoftDeleteRepository[T]` garantizando que las mutaciones usen exclusivamente `await session.flush()`, prohibiendo `commit()` dentro de los repositorios.
- Implementar paginación uniforme con DTO Pydantic `{items, total, page, size, pages}` y validación estricta de límites (default 20, 422 si `page > pages`).
- Configurar el lifespan con precálculo de hash ficticio bcrypt en `app.state.fictitious_password_hash` y estructurar los routers abiertos y protegidos.
- Validar todo el core con suite de pruebas unitarias en `parcial/tests/unit/`.

**Non-Goals:**
- Implementar modelos específicos de dominio de usuarios, libros o ventas (corresponden a C-06).
- Implementar endpoints de autenticación o endpoints de negocio (corresponden a C-07, C-08, C-09).
- Modificar archivos en `src/` o `tests/`.

## Decisions

### 1. Gestión de Sesión Compartida en Unit of Work
- **Decisión:** `UnitOfWork` recibe `session: AsyncSession` en su constructor, provista por la dependencia `get_session`. No invoca `session.close()` en `__aexit__`.
- **Razón:** La consigna exige que las dependencias de seguridad (`get_usuario_actual`, `requiere_rol`) y el UoW compartan la misma conexión física del pool por request, evitando agotar conexiones en peticiones concurrentes.
- **Alternativas consideradas:** Crear una sesión nueva dentro de `__aenter__` (descartada explícitamente por la regla no negociable 1.4 de la consigna).

### 2. Mutaciones en Repositorios Mediante `flush()` Exclusivo
- **Decisión:** En `BaseRepository`, los métodos `add` y `update` invocan `await self.session.flush()`.
- **Razón:** Asigna identificadores y dispara constraints de base de datos sin confirmar la transacción, delegando la atomicidad completa al `UnitOfWork`.
- **Alternativas consideradas:** `session.commit()` directo en repositorios (prohibido por arquitectura).

### 3. Paginación Uniforme con Manejo Estricto de Borde
- **Decisión:** Esquema genérico `PaginatedResponse[T]` con cálculo `pages = ceil(total / size)` si `total > 0`, sino `pages = 1`. Si `page > pages`, se levanta `HTTPException(422, detail=f"La página {page} no existe: hay {pages}")`.
- **Razón:** Cumplimiento textual de la regla 2 de la consigna.

### 4. Mitigación de Timing Attacks en Startup
- **Decisión:** Durante el lifespan en `parcial/app/main.py`, se calcula con bcrypt un hash de contraseña ficticia y se almacena en `app.state.fictitious_password_hash`.
- **Razón:** En el endpoint `/auth/login` (C-07), cuando un email no exista se comparará la contraseña contra este hash para que el tiempo de ejecución sea idéntico a un usuario existente.

## Risks / Trade-offs

- **[Risk: Sesiones no liberadas si un router no usa `get_session` de FastAPI]** → *Mitigación:* Se implementa `get_session` con bloque `async with` y `yield`, garantizando cierre automático al finalizar el ciclo de vida de la petición HTTP.
- **[Risk: Divergencia entre SQLAlchemy 2.0 async y drivers]** → *Mitigación:* Se valida la conexión con `asyncpg` y se configuran mocks tipados para pruebas unitarias sin dependencias externas.
