# Tasks

## 1. DTOs y Esquemas de Validación para Clientes y Ventas

- [x] 1.1 Implementar esquemas Pydantic para Clientes (`ClienteCreateRequest`, `ClienteUpdateRequest`, `ClienteResponse`) en `parcial/app/modules/clientes/schemas.py` con `extra="forbid"`, verificando rechazo de atributos no reconocidos con tests unitarios.
- [x] 1.2 Implementar esquemas Pydantic para Ventas (`VentaItemRequest`, `VentaCreateRequest`, `DetalleVentaResponse`, `VentaResponse`, `VentaDetailResponse`) en `parcial/app/modules/ventas/schemas.py` con `extra="forbid"`, verificando validaciones de cantidad positiva y tipos con tests unitarios.

## 2. Repositorios de Acceso a Datos y Carga Eager Anti N+1

- [x] 2.1 Implementar `ClienteRepository` en `parcial/app/modules/clientes/repository.py` heredando de `BaseRepository` con métodos para crear, actualizar, buscar por ID, buscar por `usuario_id` y listar paginado ejecutando exclusivamente `flush()`, verificado con tests unitarios de persistencia.
- [x] 2.2 Implementar `VentaRepository` en `parcial/app/modules/ventas/repository.py` heredando de `BaseRepository` con método `obtener_por_id_con_detalles` configurado con `joinedload` y `selectinload` para consulta en exactamente 2 sentencias SQL fijas sin importar la cantidad de renglones, verificado con tests de repositorio.

## 3. Servicios de Negocio y Transacciones Atómicas UoW

- [x] 3.1 Implementar `ClienteService` en `parcial/app/modules/clientes/service.py` con alta, consulta, actualización con `exclude_unset=True`, vinculación 1 a 1 de cuenta (`vincular_perfil`) con control de unicidad (HTTP 409) y consulta de ventas por cliente, verificado con tests de servicio.
- [x] 3.2 Implementar en `VentaService` (`parcial/app/modules/ventas/service.py`) la creación atómica de ventas dentro de `async with uow:`: validación de libro activo (`borrado_en IS NULL`), chequeo de inventario con rollback total (HTTP 409), cálculo de precios y total en servidor, decremento de stock y generación de `MovimientoStock` negativos (`motivo='Venta'`), verificado con tests de rollback y balance de inventario.
- [x] 3.3 Implementar en `VentaService` la consulta de ventas con autorización dinámica por pertenencia para `GET /ventas/{id}` (personal o titular -> 200, ajeno -> 403) y la consulta de ventas propias para clientes autenticados (`listar_mis_ventas`), verificado con tests de matriz de acceso.

## 4. Routers HTTP, Notificaciones en Background y Cableado de Rutas

- [x] 4.1 Implementar endpoints de Clientes en `parcial/app/modules/clientes/router.py`: `POST /clientes`, `GET /clientes/{id}`, `PATCH /clientes/{id}`, `POST /clientes/{id}/perfil` y `GET /clientes/{id}/ventas` con validación de roles y paginación uniforme `{items, total, page, size, pages}`, verificado con tests HTTP.
- [x] 4.2 Implementar endpoints de Ventas en `parcial/app/modules/ventas/router.py`: `POST /ventas` con encolado de notificación simulada (`BackgroundTasks` con `await asyncio.sleep(0.5)`) únicamente post-commit, `GET /ventas` paginado para personal, `GET /ventas/{id}` sin `requiere_rol` en router y `GET /mis-ventas` para clientes, verificado con tests HTTP.
- [x] 4.3 Registrar los routers de clientes y ventas en `protected_router` dentro de `parcial/app/main.py`, asegurando la verificación global de `debe_cambiar_password == false` y disponibilidad de endpoints en la aplicación, verificado con test de booteo e inspección de rutas.

## 5. Integración, Pruebas E2E y Verificación de Consultas Fijas (Sin N+1)

- [x] 5.1 Crear suite integral de pruebas para transacciones de venta en `parcial/tests/integration/test_ventas_transactions.py` validando flujo feliz multilínea, rollback total ante stock insuficiente, rollback ante libro borrado y ejecución de tareas de notificación tras commit, verificado mediante pytest.
- [x] 5.2 Crear suite de pruebas de seguridad y autorización por pertenencia en `parcial/tests/integration/test_ventas_permisos.py` validando respuestas 200/403/401 en `GET /ventas/{id}` y `GET /mis-ventas`, y control de vinculación de perfiles, verificado mediante pytest.
- [x] 5.3 Crear prueba de verificación anti N+1 en `parcial/tests/integration/test_ventas_nplusone.py` monitoreando eventos de consultas SQL de SQLAlchemy durante `GET /ventas/{id}` con 1, 5 y 10 renglones, demostrando que la cantidad de consultas SQL permanece fija e invariable ($O(1)$), verificado mediante pytest.
