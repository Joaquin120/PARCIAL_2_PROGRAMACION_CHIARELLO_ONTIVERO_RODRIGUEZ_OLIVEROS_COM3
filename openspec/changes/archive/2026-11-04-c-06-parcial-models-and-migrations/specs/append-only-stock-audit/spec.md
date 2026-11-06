# Spec Delta

## Purpose

Enforces database-level append-only immutability on stock movements via PostgreSQL trigger.

## ADDED Requirements

### Requirement: Inmutabilidad estricta de movimientos de stock
The database SHALL abort and reject any UPDATE or DELETE statement executed against the `movimiento_stock` table.

#### Scenario: Rechazo de actualización de movimiento de stock
- **WHEN** se ejecuta una sentencia `UPDATE` sobre un registro de `movimiento_stock`
- **THEN** el disparador PL/pgSQL aborta la transacción lanzando una excepción

#### Scenario: Rechazo de eliminación de movimiento de stock
- **WHEN** se ejecuta una sentencia `DELETE` sobre un registro de `movimiento_stock`
- **THEN** el disparador PL/pgSQL aborta la transacción lanzando una excepción

### Requirement: Restricción de cantidad distinta de cero en movimientos
The database SHALL reject any stock movement whose quantity is zero via check constraint.

#### Scenario: Inserción de movimiento con cantidad cero
- **WHEN** se intenta insertar un movimiento con `cantidad = 0`
- **THEN** la base de datos rechaza la operación por violación de la restricción `CHECK (cantidad <> 0)`
