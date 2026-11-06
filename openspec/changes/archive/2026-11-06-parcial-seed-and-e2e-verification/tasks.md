# Tasks: Parcial Seed and E2E Verification

## 1. Script de Datos Iniciales (`parcial/seed.py`)

- [x] 1.1 Implementar el módulo base y la estructura asíncrona de `parcial/seed.py` con verificación de idempotencia y hashing seguro de contraseñas, verificando que su ejecución inicial y subsiguiente se ejecute limpiamente sin excepciones de duplicidad.
- [x] 1.2 Implementar la creación de usuarios y roles del parcial (`admin@example.com`, `admin2@example.com`, `vendedor@example.com`, `ana@example.com`, `nuevo@example.com`), verificando que los 5 usuarios y sus asignaciones activas existan en la base de datos con `nuevo` teniendo `debe_cambiar_password = true`.
- [x] 1.3 Implementar la carga de autores, editoriales, géneros y los 5 libros canónicos (*Rayuela*, *Antología poética*, *Ficciones*, *Respiración artificial*, *Bestiario*) con movimientos iniciales de stock, verificando que `libro.stock == SUM(movimiento_stock.cantidad)` para cada libro.
- [x] 1.4 Implementar el alta de clientes iniciales (Lucía Fernández, Tomás Ríos, Ana Paz vinculada a `ana@example.com`), la Venta 1 inicial (Lucía compra 1 Rayuela y 2 Ficciones por $69.000,00 con deducción de stock y movimientos compensados) y el evento de auditoría del `'SISTEMA'`, verificando la persistencia y el invariante de stock mediante tests de integración dedicados para el seed.

## 2. Suite de Pruebas Automatizadas (.http y Pytest) para Casos C-01 a C-08

- [x] 2.1 Crear archivos `.http` para autenticación, sesiones y rate limiting (Casos C-01 a C-04) en `parcial/test/` y verificar su ejecución contra los endpoints con `parcial/tests/integration/test_e2e_casos_c01_c16.py`.
- [x] 2.2 Crear archivos `.http` para cambio de contraseña, roles dinámicos, autoprotección de admin y contratos estrictos (Casos C-05 a C-08) en `parcial/test/` y verificar su comportamiento en `parcial/tests/integration/test_e2e_casos_c01_c16.py`.

## 3. Suite de Pruebas Automatizadas (.http y Pytest) para Casos C-09 a C-16

- [x] 3.1 Crear archivos `.http` para paginación estándar, catálogo/reposición, soft-delete y ventas atómicas (Casos C-09 a C-13) en `parcial/test/` y verificar su respuesta en `parcial/tests/integration/test_e2e_casos_c01_c16.py`.
- [x] 3.2 Crear archivos `.http` para verificación de trigger append-only, lectura sin N+1 y control de visibilidad en ventas (Casos C-14 a C-16) en `parcial/test/` y verificar su resultado con `parcial/tests/integration/test_e2e_casos_c01_c16.py`.

## 4. Evidencia de Consultas Fijas sin N+1 (C-15), Trigger (C-14) y Documentación

- [x] 4.1 Generar informe técnico cuantitativo `parcial/evidencia/c15_nplusone_evidence.md` con script/test de captura de queries SQL de `GET /ventas/{id}` demostrando cantidad constante de consultas ante distintas cantidades de renglones.
- [x] 4.2 Documentar en `parcial/README.md` las instrucciones completas de ejecución del seed, suite de pruebas (.http y pytest), verificación de `solo_agregado.sql` e informe de evidencias, verificando que los comandos documentados sean reproducibles.
