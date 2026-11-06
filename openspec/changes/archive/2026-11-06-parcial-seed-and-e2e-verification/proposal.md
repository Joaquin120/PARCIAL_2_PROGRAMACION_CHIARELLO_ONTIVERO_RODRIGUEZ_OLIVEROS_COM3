# Proposal: Parcial Seed and E2E Verification

## Why

Una vez completada la implementación de la arquitectura transaccional, el modelo de datos, la seguridad dinámica y los módulos de ventas y clientes en C-09, el sistema requiere un mecanismo determinístico de inicialización de datos (`seed.py`) y una suite de verificación de extremo a extremo que valide integralmente los 16 casos de prueba canónicos de la consigna (C-01 a C-16). Sin esta etapa, la base de datos carece de la carga de datos inicial exigida para la evaluación y no se cuenta con evidencia formal de la ausencia de consultas $N+1$, la inmutabilidad de movimientos de stock y el cumplimiento de las restricciones de seguridad.

## What Changes

- **Script de Carga de Datos Iniciales (`parcial/seed.py`)**:
  - Creación idempotente de usuarios de prueba con contraseñas hasheadas con bcrypt: `admin@example.com`, `admin2@example.com` (`ADMIN`), `vendedor@example.com` (`VENDEDOR`), `ana@example.com` (`CLIENTE`), y `nuevo@example.com` (`VENDEDOR` con bandera `debe_cambiar_password = True`).
  - Creación de autores, editoriales y géneros literarios base para la catalogación de libros.
  - Carga de los 5 libros canónicos del TP con stock inicial y registro de `MovimientoStock` balanceado (`motivo = 'Stock inicial'`): *Rayuela* (10), *Antología poética* (5), *Ficciones* (8), *Respiración artificial* (3) y *Bestiario* (1).
  - Carga de clientes: Lucía Fernández y Tomás Ríos (sin usuario asociado), y Ana Paz (vinculada al usuario `ana@example.com`).
  - Registro de la Venta 1 inicial: Lucía adquiere 1 ejemplar de *Rayuela* y 2 de *Ficciones* (Total: \$69.000,00), con deducción de stock y movimientos negativos asociados (`motivo = 'Venta'`), preservando el invariante de stock `libro.stock == SUM(movimientos.cantidad)`.
  - Registro de auditoría inicial en `evento_seguridad` con actor `'SISTEMA'`.
- **Suite de Casos de Prueba C-01 a C-16 en `parcial/test/`**:
  - Colección de archivos `.http` estándar para clientes REST (VS Code REST Client / IntelliJ HTTP Client) cubriendo los casos C-01 a C-16.
  - Suite complementaria automatizada en pytest (`parcial/tests/integration/test_e2e_casos_c01_c16.py`) para ejecución automatizada en integración continua sin requerir disparos manuales.
- **Validación del Disparador de Inmutabilidad (Caso C-14)**:
  - Documentación y verificación automatizada del script SQL `parcial/test/solo_agregado.sql` demostrando que sentencias `UPDATE` y `DELETE` sobre `movimiento_stock` son abortadas por el trigger PL/pgSQL.
- **Evidencia de Consultas Fijas sin N+1 (Caso C-15)**:
  - Generación de informe y script de conteo de consultas SQL en `parcial/evidencia/c15_nplusone_evidence.md` demostrando que `GET /ventas/{id}` resuelve el detalle con una cantidad constante de queries SQL independientemente del número de renglones.
- **Documentación de Verificación y Uso (`parcial/README.md`)**:
  - Guía completa paso a paso para ejecutar el seed, correr las pruebas `.http` y `pytest`, verificar el trigger y consultar las evidencias.

## Capabilities

### New Capabilities
- `parcial-seed-and-initial-data`: Provisionamiento idempotente de datos iniciales del parcial (usuarios, credenciales seguras, roles vigentes, libros de referencia, balance de stock físico y auditoría del sistema).
- `parcial-e2e-verification`: Suite de verificación de extremo a extremo de los 16 casos canónicos (C-01 a C-16), trigger de sólo agregado en PostgreSQL y prueba de consultas fijas sin N+1 con evidencia.

### Modified Capabilities
<!-- Ninguna especificación previa altera sus requerimientos; las capacidades existentes continúan vigentes. -->

## Impact

- **Código afectado**:
  - Nuevo script `parcial/seed.py` ejecutable como módulo CLI (`python -m parcial.seed` o `python parcial/seed.py`).
  - Nuevos archivos `.http` en `parcial/test/`.
  - Nueva suite de verificación E2E `parcial/tests/integration/test_e2e_casos_c01_c16.py`.
  - Nueva carpeta de evidencia `parcial/evidencia/` con informe de queries fijas para C-15.
  - Nuevo documento explicativo `parcial/README.md`.
- **Dependencias**:
  - Requiere PostgreSQL 16 y extensiones/migraciones aplicadas hasta `004_trigger_append_only.py`.
- **Breaking Changes**: Ninguno. No altera endpoints ni contratos de API existentes.
