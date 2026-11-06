# Design: C-06 Parcial Models and Migrations

## Context

El proyecto cuenta con la base técnica del Parcial en `parcial/app/core/` (configuración, base declarativa, repositorios con flush, unit of work y paginación). Se requiere mapear las entidades de negocio relacionales requeridas en los Capítulos 1 a 6 de `CONSIGNA_PARCIAL.md`, garantizando las restricciones clave:
- Roles dinámicos con `CHECK` e índice único condicional.
- Soft-delete en `Libro` con liberación de ISBN.
- Disparador PL/pgSQL append-only en `movimiento_stock` (Caso C-14).
- Estructura sin N+1 para ventas y clientes.

## Goals / Non-Goals

**Goals:**
- Mapear con SQLAlchemy 2.0 (`Mapped`, `mapped_column`, `relationship`, `ForeignKey`) todos los modelos del Parcial organizados por módulo en `parcial/app/modules/`:
  - `usuarios`: `Usuario`, `AsignacionRol`, `IntentoAcceso`, `EventoSeguridad`
  - `libros`: `Autor`, `Editorial`, `Genero`, `Libro`, `MovimientoStock`
  - `clientes`: `Cliente`
  - `ventas`: `Venta`, `DetalleVenta`
- Configurar índices únicos parciales mediante `Index(..., postgresql_where=...)`.
- Crear las migraciones de base de datos con Alembic en `parcial/migrations/`:
  - Migración con tablas, constraints e índices parciales.
  - Migración manual con función PL/pgSQL y disparador BEFORE UPDATE OR DELETE sobre `movimiento_stock`.
- Verificar los metadatos y modelos con pruebas unitarias en `parcial/tests/unit/test_models.py`.

**Non-Goals:**
- Implementar los endpoints REST ni servicios de autenticación (corresponden a C-07).
- Implementar la lógica transaccional de venta ni BackgroundTasks (corresponde a C-09).
- Modificar las tablas o modelos de `src/` correspondientes al TP original.

## Decisions

### 1. Organización Modular por Dominio
- **Decisión:** Agrupar modelos por dominio funcional dentro de `parcial/app/modules/<dominio>/models.py` (`usuarios`, `libros`, `clientes`, `ventas`).
- **Razón:** Sigue la arquitectura propuesta en `knowledge-base/08_arquitectura_propuesta.md` y permite que los routers y servicios de los changes subsiguientes coexistan limpiamente dentro de cada módulo.

### 2. Índices Únicos Parciales en PostgreSQL
- **Decisión:** Usar `postgresql_where=text("borrado_en IS NULL")` para `(isbn)` en `Libro`, y `postgresql_where=text("revocada_en IS NULL")` para `(usuario_id, rol)` en `AsignacionRol`.
- **Razón:** Cumplimiento textual de la consigna. Permite re-otorgar roles revocados históricamente y re-utilizar ISBNs de libros dados de baja.

### 3. Disparador Append-Only en `movimiento_stock`
- **Decisión:** Implementar función PL/pgSQL `rechazar_mutacion_movimiento_stock()` que ejecuta `RAISE EXCEPTION` y un trigger `BEFORE UPDATE OR DELETE ON movimiento_stock`.
- **Razón:** Garantiza inmutabilidad estricta a nivel de motor ACID, independientemente de la aplicación o clientes directos de BD (Caso C-14).

## Risks / Trade-offs

- **[Risk: Divergencia entre SQLite en memoria y PostgreSQL en índices parciales/triggers]** → *Mitigación:* Se configuran pruebas unitarias de metadatos de SQLAlchemy validando las propiedades `postgresql_where` y `CheckConstraint`, y se provee el script `solo_agregado.sql` para validación contra PostgreSQL.
