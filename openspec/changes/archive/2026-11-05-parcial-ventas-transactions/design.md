# Design

## Context

El proyecto implementa la arquitectura en capas `Router -> Service -> Unit of Work -> Repository -> Model` conforme a la especificación del Parcial (`CONSIGNA_PARCIAL.md` §1, §2 y §3).
Las entidades del modelo relacional (`Venta`, `DetalleVenta`, `Cliente`, `Libro`, `MovimientoStock`, `Usuario`) ya se encuentran definidas en `parcial/app/modules/*/models.py` y migradas a la base de datos PostgreSQL.
El componente `UnitOfWork` (`parcial/app/core/unit_of_work.py`) orquesta la demarcación transaccional (`commit()` / `rollback()`) sobre la sesión provista por FastAPI, garantizando que repositorios y dependencias compartan la misma conexión del pool sin fugas ni transacciones colgadas.

## Goals / Non-Goals

**Goals:**
- Implementar la creación atómica de ventas (`POST /ventas`) con deducción sincronizada de stock en `Libro` y creación de movimientos append-only en `MovimientoStock` (`cantidad = -renglon.cantidad`, `motivo = 'Venta'`), con rollback total ante stock insuficiente o libro borrado (HTTP 409).
- Despachar tareas asíncronas no bloqueantes con `BackgroundTasks` (`await asyncio.sleep(0.5)`) que emitan el aviso de venta únicamente tras la confirmación exitosa del UoW.
- Resolver la consulta detallada de ventas (`GET /ventas/{id}`) sin el antipatrón $N+1$, logrando un número fijo de consultas SQL mediante `joinedload` y `selectinload`.
- Aplicar autorización dinámica por pertenencia en `GET /ventas/{id}` a nivel de servicio: permitir acceso a personal administrativo (`ADMIN`/`VENDEDOR`) o al cliente dueño de la venta, y responder **HTTP 403 Forbidden** a clientes ajenos.
- Proveer la gestión completa de clientes (`POST /clientes`, `GET /clientes/{id}`, `PATCH /clientes/{id}`), vinculación unívoca de usuario-cliente (`POST /clientes/{id}/perfil`), compras por cliente (`GET /clientes/{id}/ventas`) y consulta de ventas propias (`GET /mis-ventas`).
- Respetar esquemas estrictos con `extra="forbid"`, paginación uniforme (`{items, total, page, size, pages}`) y rechazo de páginas inexistentes con **HTTP 422**.

**Non-Goals:**
- Generación de comprobantes fiscales PDF o integración con pasarelas de pago externas.
- Modificación del esquema de base de datos (las tablas e índices fueron creados en las fases previas).
- Carga de datos iniciales (`seed.py`) o ejecución de la suite de casos E2E C-01 a C-16 (reservado para C-10).

## Decisions

### 1. Orquestación Atómica de Ventas en `VentaService` y `UnitOfWork`
- **Decisión**: La operación completa de venta se ejecuta dentro de un único bloque `async with uow:`. Para cada renglón:
  1. Se verifica la existencia del libro y que no posea baja lógica (`borrado_en IS NULL`). Si está borrado o no existe -> aborta con **HTTP 409** (o 404).
  2. Se valida disponibilidad de stock (`libro.stock >= renglon.cantidad`). Si no alcanza -> aborta la venta completa con **HTTP 409 Conflict**.
  3. Se copia el precio unitario del catálogo (`libro.precio`) y se calcula el subtotal.
  4. Se actualiza el stock físico del libro (`libro.stock -= renglon.cantidad`).
  5. Se crea el registro `MovimientoStock(libro_id=libro.id, venta_id=venta.id, usuario_id=vendedor_o_admin_id, cantidad=-renglon.cantidad, motivo='Venta')`.
  6. Al salir del bloque, el UoW ejecuta `await session.commit()`. Si se produce cualquier error, se ejecuta `rollback()`.
- **Alternativas consideradas**:
  - Actualizar stock por trigger en la base de datos: Descartado porque la consigna explícitamente exige que el servicio de aplicación controle el flujo de negocio y mantenga el invariant `libro.stock = SUM(movimiento_stock.cantidad)`.

### 2. Prevención del Antipatrón N+1 en Consultas de Venta
- **Decisión**: En `VentaRepository.obtener_por_id_con_detalles`, configurar una consulta SQLAlchemy con:
  ```python
  stmt = (
      select(Venta)
      .where(Venta.id == venta_id)
      .options(
          joinedload(Venta.cliente),
          joinedload(Venta.usuario),
          selectinload(Venta.detalles).joinedload(DetalleVenta.libro),
      )
  )
  ```
  Esto garantiza que la venta, el cliente asociado, el usuario vendedor, la lista de renglones y cada libro referenciado se obtengan en exactamente 2 consultas SQL fijas ($O(1)$) sin importar si la venta contiene 1 o 100 renglones.
- **Alternativas consideradas**:
  - Lazy loading: Descartado por generar consultas secuenciales $N+1$ y disparar excepciones de async I/O (`MissingGreenlet`) en SQLAlchemy 2.0.

### 3. Autorización Dinámica por Pertenencia en el Servicio
- **Decisión**: Para `GET /ventas/{id}`, el endpoint en `router.py` no utiliza `requiere_rol(...)`. En su lugar, inyecta `usuario_actual = Depends(get_usuario_actual)`. El servicio obtiene la venta con sus relaciones y verifica:
  ```python
  roles_usuario = {r.rol for r in usuario_actual.roles if r.es_vigente}
  es_personal = bool(roles_usuario & {"ADMIN", "VENDEDOR"})
  es_titular = (venta.cliente.usuario_id == usuario_actual.id)
  if not (es_personal or es_titular):
      raise HTTPException(status_code=403, detail="Acceso denegado a la venta solicitada")
  ```
- **Alternativas consideradas**:
  - Dependencia de FastAPI a nivel de ruta: Descartada porque se requiere consultar la base de datos para saber quién es el cliente titular de la venta antes de evaluar la autorización.

### 4. Notificación Asíncrona en Background Posterior al Commit
- **Decisión**: El endpoint `POST /ventas` recibe la dependencia estándar `BackgroundTasks` de FastAPI. La función de fondo:
  ```python
  async def simular_notificacion_comprobante(venta_id: int, total: float, email_destinatario: str) -> None:
      await asyncio.sleep(0.5)
      logger.info(f"Comprobante enviado para venta #{venta_id} por ${total:.2f} a {email_destinatario}")
  ```
  se encola con `background_tasks.add_task(...)` únicamente **después** de que el servicio haya retornado exitosamente de la transacción comiteada. Si la venta falla por stock o validación, se lanza una excepción HTTP antes de alcanzar esta línea y la tarea no se planifica.
- **Alternativas consideradas**:
  - Ejecutar la notificación dentro de la transacción: Descartado porque bloquearía la conexión y enviaría correos de ventas que podrían revertirse ante fallos de commit.

### 5. Contratos Estrictos y Paginación Uniforme
- **Decisión**:
  - Todos los DTOs de entrada y salida (`VentaCreateRequest`, `VentaItemRequest`, `ClienteCreateRequest`, `ClienteUpdateRequest`) heredan de esquemas con `model_config = ConfigDict(extra="forbid")`.
  - Los listados `GET /ventas`, `GET /clientes/{id}/ventas` y `GET /mis-ventas` emplean `armar_paginacion` devolviendo `{items, total, page, size, pages}` con validación de `page > pages` retornando **HTTP 422**.

## Risks / Trade-offs

- **[Condiciones de carrera en concurrencia de stock]** → *Mitigación*: SQLAlchemy opera bajo transacciones atómicas con aislamiento en PostgreSQL; ante inventario insuficiente el chequeo rechaza inmediatamente con HTTP 409 sin comprometer el balance contable.
- **[Disparo erróneo de tareas de fondo]** → *Mitigación*: `background_tasks.add_task` se ejecuta exclusivamente en el router tras el retorno limpio del servicio, asegurando que la transacción física ya fue comiteada.
- **[Fuga de datos de clientes ajenos]** → *Mitigación*: Verificación estricta de pertenencia en el servicio (`es_personal or es_titular`) para el detalle de venta y listado por cliente.
