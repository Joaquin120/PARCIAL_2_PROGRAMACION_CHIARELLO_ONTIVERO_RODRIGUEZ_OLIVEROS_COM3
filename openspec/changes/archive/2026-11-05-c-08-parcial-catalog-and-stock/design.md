# Design: C-08 Parcial Catalog and Stock

## Context

Ver `proposal.md` para la motivación. El estado actual relevante del proyecto:
- Los modelos SQLAlchemy `Libro`, `Autor`, `Editorial`, `Genero` y `MovimientoStock` ya fueron declarados en C-06 (`parcial/app/modules/libros/models.py`).
- `Libro` cuenta con índice condicional único `ix_libro_isbn_activo` sobre `isbn` donde `borrado_en IS NULL`.
- `MovimientoStock` posee restricción `CheckConstraint("cantidad <> 0")` y disparador PL/pgSQL append-only que aborta `UPDATE`/`DELETE`.
- `SoftDeleteRepository` ya existe en `parcial/app/core/repository.py` filtrando `borrado_en.is_(None)`.
- La infraestructura de seguridad de C-07 (`get_usuario_actual`, `requiere_rol`, cookies HttpOnly) ya está operativa en `main.py`.
- Convención arquitectónica estricta: `Router -> Service -> UnitOfWork -> Repository -> Model`. Ningún repositorio hace commit; los servicios reciben el UoW.

## Goals / Non-Goals

**Goals:**
- Implementar los servicios y repositorios para libros, catálogos auxiliares y movimientos de stock.
- Garantizar que el stock físico sólo mute a través de movimientos (`'Stock inicial'`, `'Reposicion'`).
- Exponer el catálogo público paginado en `open_router` y las mutaciones en `protected_router` custodiadas por rol `ADMIN`.
- Cumplir el soft delete liberando el ISBN para nuevas altas y rechazando reposición con 409 si el libro está borrado.
- Asegurar lecturas eficientes con `joinedload` para evitar el problema de $N+1$ en consultas del catálogo.

**Non-Goals:**
- Ventas y descuento de stock por compra (`POST /ventas` corresponde a C-09).
- Modificaciones sobre autores, editoriales o géneros (se proveen consultas de lectura y filtrado; las altas iniciales provienen del seed).
- Vistas o templates HTML (la API es exclusivamente REST JSON).

## Decisions

### 1. Composición de Capas y Especialización de Repositorios
- **Decisión:** `LibroRepository` hereda de `SoftDeleteRepository[Libro]`. Sus métodos `get_by_id`, `get_all`, `count` excluyen por defecto los libros con `borrado_en IS NOT NULL`. Para búsquedas específicas con relaciones se utiliza `joinedload(Libro.autor)`, `joinedload(Libro.editorial)` y `joinedload(Libro.genero)`.
- **Razón:** Encapsula la lógica de soft delete en el repositorio y evita duplicar cláusulas `WHERE borrado_en IS NULL` en los servicios.
- **Alternativa descartada:** Filtrar manualmente en cada servicio, propenso a omitir el filtro de bajas lógicas.

### 2. Punto Único de Mutación de Stock y Alta Atómica
- **Decisión:** El alta de libro (`POST /libros`) recibe `stock_inicial` en su DTO. Dentro de una única transacción UoW, se añade el `Libro` con `stock = stock_inicial` y se registra un `MovimientoStock` con `cantidad = stock_inicial`, `motivo = 'Stock inicial'` y `usuario_id = admin.id`.
- **Razón:** Cumple la invariante obligatoria: `libro.stock == SUM(movimiento_stock.cantidad)` desde el momento de creación.
- **Alternativa descartada:** Crear el libro con stock 0 y exigir una petición separada de reposición, lo cual requeriría dos peticiones HTTP y no sería atómico.

### 3. Prohibición de Alterar Stock por PATCH
- **Decisión:** El esquema `LibroUpdateRequest` declara exclusivamente campos mutables de metadatos: `titulo: str | None = None`, `precio: Decimal | None = None` con `model_config = ConfigDict(extra="forbid")`.
- **Razón:** Si un cliente envía `"stock": 10`, Pydantic rechaza la petición con **HTTP 422 Unprocessable Entity**. El stock no puede ser mutado arbitrariamente sin un movimiento contable.
- **Alternativa descartada:** Ignorar silenciosamente el campo de stock en el servicio, lo cual oculta el error del cliente.

### 4. Reposición de Stock con Bloqueo Pesimista y Validación de Baja Lógica
- **Decisión:** En `POST /libros/{id}/reponer`, el servicio consulta el libro con `SELECT ... FOR UPDATE` usando `get_by_id_including_deleted(id)`. Si el libro no existe, responde 404. Si `borrado_en is not None`, responde **HTTP 409 Conflict**. Si está activo, incrementa `libro.stock += cantidad` y añade `MovimientoStock(cantidad=cantidad, motivo='Reposicion', usuario_id=admin.id)`.
- **Razón:** El bloqueo pesimista evita carreras en reposiciones concurrentes y la consigna exige explícitamente responder 409 ante intentos de reposición en libros borrados.
- **Alternativa descartada:** Actualizar el stock sin bloqueo o ignorar la condición de borrado lógico.

### 5. Borrado Lógico y Liberación de ISBN
- **Decisión:** `DELETE /libros/{id}` invoca `soft_delete(libro)` estableciendo `borrado_en = func.now()` y responde **HTTP 204 No Content**.
- **Razón:** Respeta el índice parcial de PostgreSQL `CREATE UNIQUE INDEX ix_libro_isbn_activo ON libro (isbn) WHERE borrado_en IS NULL`. Una vez asignada la fecha de borrado, una nueva llamada a `POST /libros` con el mismo ISBN es aceptada sin violar la restricción de clave única.
- **Alternativa descartada:** Borrado físico `DELETE FROM libro`, que rompería la integridad referencial con movimientos de stock y ventas históricas.

### 6. Paginación Uniforme y Filtros en Catálogo
- **Decisión:** `GET /libros` recibe `PaginationParams(page=1, size=20)` y parámetros opcionales `titulo: str | None = None` y `genero_id: int | None = None`. Devuelve `PaginatedResponse[LibroResponse]` mediante `crear_respuesta_paginada`, que valida `page <= pages` (HTTP 422 si `page > pages`).
- **Razón:** Mantiene el formato estándar `{items, total, page, size, pages}` consistente con el resto de la aplicación.
- **Alternativa descartada:** Paginación por `limit/offset` expuesta directamente sin envoltorio de páginas.

### 7. Segregación de Rutas en Routers
- **Decisión:**
  - `open_router`: `GET /libros`, `GET /autores`, `GET /editoriales`, `GET /generos` y los endpoints de filtrado relacional `/autores/{id}/libros`, etc.
  - `protected_router`: `POST /libros`, `PATCH /libros/{id}`, `DELETE /libros/{id}`, `POST /libros/{id}/reponer`, `GET /libros/{id}/movimientos`, con dependencia `Depends(requiere_rol("ADMIN"))`.
- **Razón:** El catálogo de consulta es público (accesible por clientes anónimos y registrados), mientras que la mutación de catálogo y stock es una atribución exclusiva del administrador.

## Risks / Trade-offs

- **[Filtro por título con `ILIKE` en catálogos extensos]** → Puede degradar el rendimiento sin un índice trigram. *Mitigación:* Para el alcance del Parcial el volumen es moderado; la búsqueda usa `select(Libro).where(Libro.titulo.ilike(f"%{titulo}%"))`.
- **[Concurrencia en reposición de stock]** → Dos peticiones de reposición concurrentes podrían generar inconsistencias en `libro.stock`. *Mitigación:* Uso de `with_for_update()` en la consulta del libro dentro de la transacción UoW.
- **[Stock inicial no positivo]** → Podría crearse un libro con stock negativo o movimiento con cantidad 0 violando el check constraint de base de datos. *Mitigación:* El validador Pydantic exige `stock_inicial: int = Field(..., ge=0)` y para reposición `cantidad: int = Field(..., gt=0)`. Si `stock_inicial > 0`, se genera el movimiento `'Stock inicial'`; si `stock_inicial == 0`, no se genera movimiento de cantidad cero para no violar `ck_movimiento_stock_cantidad_no_cero`.

## Migration Plan

1. Crear esquemas DTOs en `parcial/app/modules/libros/schemas.py`.
2. Implementar repositorios en `parcial/app/modules/libros/repository.py`.
3. Implementar servicios en `parcial/app/modules/libros/service.py`.
4. Implementar routers en `parcial/app/modules/libros/router.py` y montarlos en `parcial/app/main.py`.
5. Validar con tests unitarios y tests de integración con PostgreSQL real.
6. Sin cambios de base de datos (rollback: revertir archivos de código).

