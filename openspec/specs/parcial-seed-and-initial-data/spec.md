# parcial-seed-and-initial-data Specification

## Purpose

Provee un mecanismo automatizado, repetible e idempotente para inicializar el estado del sistema con los usuarios canónicos, credenciales seguras, roles vigentes, libros de referencia, clientes de prueba, ventas iniciales y auditoría del sistema conforme a la consigna del Parcial.

## Requirements

### Requirement: Inicialización de usuarios del parcial y roles vigentes
The system SHALL / El sistema DEBE provisionar los usuarios canónicos requeridos (`admin@example.com`, `admin2@example.com`, `vendedor@example.com`, `ana@example.com`, `nuevo@example.com`) con contraseñas seguras generadas vía bcrypt, asociar los roles correspondientes (`ADMIN`, `VENDEDOR`, `CLIENTE`) sin fecha de vencimiento ni revocación, y marcar la bandera `debe_cambiar_password = true` exclusivamente en `nuevo@example.com`.

#### Scenario: Creación exitosa de usuarios y roles
- **WHEN** se ejecuta el script de seed sobre una base limpia o existente
- **THEN** los 5 usuarios quedan creados con sus roles vigentes y `nuevo@example.com` posee `debe_cambiar_password = true`

### Requirement: Carga de catálogo literario con balance de stock e historial de movimientos
The system SHALL / El sistema DEBE registrar las entidades maestras de autores, editoriales y géneros, dar de alta los 5 libros canónicos (*Rayuela*, *Antología poética*, *Ficciones*, *Respiración artificial*, *Bestiario*) y crear un registro de `MovimientoStock` de tipo `'Stock inicial'` por cada libro de modo que `libro.stock == SUM(movimientos.cantidad)`.

#### Scenario: Carga inicial balanceada de libros
- **WHEN** se ejecuta la inicialización de catálogo en el seed
- **THEN** los 5 libros quedan registrados y el stock de cada uno coincide exactamente con la suma de sus movimientos de stock iniciales

### Requirement: Registro de clientes iniciales y asociación opcional con usuarios
The system SHALL / El sistema DEBE registrar a los clientes Lucía Fernández y Tomás Ríos con `usuario_id = NULL`, y a la cliente Ana Paz vinculada mediante relación 1 a 1 al usuario `ana@example.com`.

#### Scenario: Clientes creados con y sin cuenta de usuario
- **WHEN** se ejecuta la siembra de clientes
- **THEN** existen tres clientes en el sistema y solo Ana Paz tiene su campo `usuario_id` apuntando a `ana@example.com`

### Requirement: Registro transaccional de venta inicial y compensación de stock
The system SHALL / El sistema DEBE registrar la Venta 1 a nombre de la cliente Lucía Fernández conteniendo 1 ejemplar de *Rayuela* y 2 de *Ficciones*, calcular el importe total exacto de 69000.00, descontar el stock de ambos libros y crear los registros correspondientes de `MovimientoStock` negativos (`motivo = 'Venta'`), preservando el invariante de stock.

#### Scenario: Registro exitoso de la venta inicial
- **WHEN** se procesa la venta inicial de Lucía Fernández en el seed
- **THEN** la venta queda registrada con total de 69000.00, el stock de Rayuela y Ficciones se decrementa y se crean los movimientos de stock negativos asociados

### Requirement: Registro inicial de evento de auditoría del sistema
The system SHALL / El sistema DEBE insertar un registro en `evento_seguridad` con actor `'SISTEMA'` dejando constancia de la ejecución exitosa de la inicialización de datos de semilla.

#### Scenario: Registro del evento de auditoría del seed
- **WHEN** finaliza la ejecución de todas las etapas del script de seed
- **THEN** se encuentra un registro en `evento_seguridad` con actor `'SISTEMA'` y descripción de la siembra
