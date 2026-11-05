# Proposal: C-06 Parcial Models and Migrations

## Why

Habiendo establecido la infraestructura base y transaccional en `C-05`, es necesario estructurar el esquema relacional completo del Parcial (Capítulos 1 a 6) exigido por la consigna. Se requiere mapear las entidades de usuarios y seguridad (`Usuario`, `AsignacionRol`, `IntentoAcceso`, `EventoSeguridad`), catálogo y stock (`Autor`, `Editorial`, `Genero`, `Libro`, `MovimientoStock`), clientes y ventas (`Cliente`, `Venta`, `DetalleVenta`). Asimismo, se deben materializar las reglas de negocio en la capa de persistencia: índices únicos parciales para roles activos e ISBN de libros no borrados, relación 1 a 1 opcional cliente-usuario, y un disparador PL/pgSQL append-only que prohíba modificaciones o eliminaciones en `movimiento_stock` (Caso C-14).

## What Changes

- Implementación de modelos de seguridad en `parcial/app/modules/usuarios/models.py`:
  - `Usuario`: `id`, `email` (único), `nombre`, `password_hash`, `activo`, `debe_cambiar_password`.
  - `AsignacionRol`: `id`, `usuario_id`, `rol` con `CHECK (rol IN ('ADMIN', 'VENDEDOR', 'CLIENTE'))`, fechas de vigencia y revocación, e índice único parcial `(usuario_id, rol) WHERE revocada_en IS NULL`.
  - `IntentoAcceso`: `id`, `cuando`, `email`, `ip`, `exito`, con índice compuesto `(email, ip, cuando)`.
  - `EventoSeguridad`: `id`, `cuando`, `actor`, `accion`.
- Implementación de modelos de catálogo y stock en `parcial/app/modules/libros/models.py`:
  - `Autor`, `Editorial`, `Genero`.
  - `Libro`: `id`, `isbn`, `titulo`, `precio`, `stock`, claves foráneas, campo `borrado_en` e índice único parcial `(isbn) WHERE borrado_en IS NULL`.
  - `MovimientoStock`: `id`, `libro_id`, `venta_id`, `usuario_id`, `cantidad` con `CHECK (cantidad <> 0)`, `motivo`, `cuando`.
- Implementación de modelos de clientes y ventas:
  - `Cliente` en `parcial/app/modules/clientes/models.py`: agrega `usuario_id` (FK nullable, único con índice) con relación 1 a 1 opcional hacia `Usuario`.
  - `Venta` y `DetalleVenta` en `parcial/app/modules/ventas/models.py`: cabecera y renglones de venta estructurados para evitar consultas N+1.
- Configuración de migraciones con Alembic en `parcial/migrations/`:
  - Migración de esquema completa con tablas, claves foráneas, checks e índices parciales.
  - Migración manual PL/pgSQL que instala el disparador `trg_movimiento_stock_solo_agregado` que aborta sentencias `UPDATE` y `DELETE` sobre `movimiento_stock`.
- Tests unitarios en `parcial/tests/unit/test_models.py` verificando metadatos, constraints, índices parciales y relaciones.

## Capabilities

### New Capabilities
- `parcial-domain-models`: Modela las entidades de usuarios, roles, catálogo, clientes y transacciones de venta con constraints e índices parciales.
- `append-only-stock-audit`: Garantiza la inmutabilidad de movimientos de stock mediante un trigger PL/pgSQL de solo agregado que rechaza updates y deletes.

### Modified Capabilities
<!-- No se modifican contratos de specs existentes -->

## Impact

- **Modelos**: Nuevos submódulos en `parcial/app/modules/` (`usuarios`, `libros`, `clientes`, `ventas`).
- **Base de datos**: Nuevas tablas, índices parciales y función/trigger PL/pgSQL en PostgreSQL.
- **Tests**: Suite unitaria en `parcial/tests/unit/test_models.py`.
