# Tasks: C-06 Parcial Models and Migrations

## 1. Modelos de Seguridad y Usuarios

- [x] 1.1 Implementar `parcial/app/modules/usuarios/models.py` (`Usuario`, `AsignacionRol`, `IntentoAcceso`, `EventoSeguridad`) con `CHECK` de rol e índice único parcial `(usuario_id, rol) WHERE revocada_en IS NULL`.

## 2. Modelos de Catálogo, Stock, Clientes y Ventas

- [x] 2.1 Implementar `parcial/app/modules/libros/models.py` (`Autor`, `Editorial`, `Genero`, `Libro`, `MovimientoStock`) con `borrado_en`, índice parcial único de `isbn` y `CHECK (cantidad <> 0)`.
- [x] 2.2 Implementar `parcial/app/modules/clientes/models.py` (`Cliente`) con clave foránea única opcional `usuario_id` y relación 1 a 1 `cliente.usuario`.
- [x] 2.3 Implementar `parcial/app/modules/ventas/models.py` (`Venta`, `DetalleVenta`) con relaciones hacia `Cliente`, `Usuario` y `Libro`.

## 3. Migraciones Alembic y Disparador Append-Only

- [x] 3.1 Crear script de migración estructurado con Alembic en `parcial/migrations/` conteniendo todas las tablas, relaciones, constraints e índices parciales del Parcial.
- [x] 3.2 Crear script de migración manual con la función PL/pgSQL y disparador BEFORE UPDATE OR DELETE sobre `movimiento_stock` (Caso C-14).

## 4. Verificación y Tests Unitarios

- [x] 4.1 Implementar suite de pruebas unitarias en `parcial/tests/unit/test_models.py` validando metadatos, checks de rol, cantidad, unicidad condicional y relaciones relacionales.
- [x] 4.2 Ejecutar la suite completa de pruebas unitarias verificando 100% de aserciones en verde y cero regresiones.

## Workflow follow-up

- Ejecutar validación OpenSpec con `openspec validate c-06-parcial-models-and-migrations`.
- Archivar el change con `openspec archive c-06-parcial-models-and-migrations`.
- Marcar como completado el checkbox de `C-06` en `CHANGES.md`.
