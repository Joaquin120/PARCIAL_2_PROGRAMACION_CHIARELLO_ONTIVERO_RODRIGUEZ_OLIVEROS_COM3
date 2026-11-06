# Proposal

## Why

El sistema de la librería requiere completar el flujo comercial transaccional central: permitir que vendedores y administradores registren ventas de libros de forma atómica garantizando la integridad de stock bajo Unit of Work, enviar avisos de comprobantes en segundo plano tras el commit exitoso, consultar ventas de manera eficiente sin problemas de rendimiento N+1, autorizar la visualización de comprobantes según la titularidad del cliente, y administrar el ciclo de vida de clientes vinculados o no a cuentas de usuario.

## What Changes

- **Ventas Transaccionales Atómicas (`POST /ventas`)**:
  - Endpoint restringido a roles `VENDEDOR` y `ADMIN`.
  - Ejecución atómica en un único Unit of Work (`async with uow:`).
  - Verificación de stock disponible para cada ítem del pedido; si algún libro no alcanza el stock requerido o tiene `borrado_en IS NOT NULL`, se aborta y revierte la transacción completa (`rollback()`), respondiendo **HTTP 409 Conflict**.
  - Deducción de stock físico en cada `Libro` y creación sincronizada de registros append-only `MovimientoStock` negativos (`cantidad = -renglon.cantidad`, `motivo = 'Venta'`).
  - Copia obligatoria de los precios unitarios actuales del catálogo (`libro.precio`) y cálculo del total en el servidor.
- **Notificación Asíncrona en Segundo Plano**:
  - Disparo de tarea simulada (`BackgroundTasks`) tras la confirmación exitosa (`commit()`) de la venta con retardo asíncrono no bloqueante (`await asyncio.sleep(0.5)`).
- **Consulta de Detalle y Reglas de Pertenencia (`GET /ventas/{id}`)**:
  - Endpoint sin dependencia de rol estático `requiere_rol` a nivel de router; la verificación de acceso se delega al servicio.
  - Usuarios del personal (`ADMIN` o `VENDEDOR`) o clientes dueños de la venta acceden con **HTTP 200 OK**.
  - Clientes ajenos a la venta son rechazados con **HTTP 403 Forbidden**.
  - Carga ansiosa estricta (`joinedload` y `selectinload`) en el repositorio para garantizar un número constante y fijo de consultas SQL ($O(1)$ consultas), eliminando el antipatrón $N+1$.
- **Consultas de Ventas Paginadas (`GET /ventas`, `GET /mis-ventas`)**:
  - Listado general para personal administrativo (`ADMIN`, `VENDEDOR`) con envoltorio de paginación uniforme `{items, total, page, size, pages}`.
  - Listado de ventas propias (`GET /mis-ventas`) para el cliente asociado al usuario autenticado.
- **Gestión Integral de Clientes (`/clientes`)**:
  - Alta (`POST /clientes`), consulta por ID (`GET /clientes/{id}`), actualización parcial (`PATCH /clientes/{id}`) para roles `ADMIN` y `VENDEDOR`.
  - Asociación de cuenta de usuario autenticada a ficha de cliente (`POST /clientes/{id}/perfil`).
  - Histórico de ventas por cliente (`GET /clientes/{id}/ventas`) restringido a personal o titular.

## Capabilities

### New Capabilities
- `parcial-sales-transactions`: Procesamiento transaccional atómico de ventas, validación estricta de stock con rollback integral, notificación asíncrona post-commit en background, control dinámico de permisos por titularidad y lecturas optimizadas sin N+1.
- `parcial-customer-management`: Ciclo de vida de clientes, vinculación unívoca con cuentas de usuario (`Usuario`), actualización parcial segura y consulta de historial de compras.

### Modified Capabilities

## Impact

- **Modelos y Persistencia**: Utiliza las entidades existentes `Venta`, `DetalleVenta`, `Cliente`, `Libro`, `MovimientoStock` y `Usuario`.
- **Servicios y Repositorios**:
  - Nuevos repositorios `VentaRepository` y `ClienteRepository` en `parcial/app/modules/ventas/repository.py` y `parcial/app/modules/clientes/repository.py`.
  - Nuevos servicios `VentaService` y `ClienteService` orquestados bajo `UnitOfWork`.
- **Routers y API**:
  - `parcial/app/modules/ventas/router.py` y `parcial/app/modules/clientes/router.py`.
  - Integración en `protected_router` de `main.py` para aplicar la verificación centralizada de `debe_cambiar_password == false`.
- **Testing y Calidad**: Tests de integración exhaustivos para concurrencia, atomicidad transaccional, rollback de stock, verificación de consultas fijas (sin N+1) y matriz de permisos por roles y titularidad.
