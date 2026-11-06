# Design: Parcial Seed and E2E Verification

## Context

Habiendo implementado la totalidad de los modelos de dominio, el Unit of Work transaccional, el módulo de seguridad dinámica con control de acceso por roles y los endpoints de negocio de catálogo, clientes y ventas (C-01 a C-09), el backend del Parcial cuenta con todas las capacidades funcionales requeridas. Véase `proposal.md` para la motivación.

El proyecto requiere ahora el script canónico de siembra de datos `parcial/seed.py`, la suite de verificación automatizada de los 16 casos de prueba (C-01 a C-16), la validación a nivel de motor de la inmutabilidad de movimientos de stock (C-14) y la evidencia documentada de consultas fijas sin $N+1$ en la consulta de ventas (C-15).

## Goals / Non-Goals

**Goals:**
- Implementar `parcial/seed.py` ejecutable directamente desde CLI (`python -m parcial.seed` o `python parcial/seed.py`), utilizando la factoría asíncrona de sesiones (`async_sessionmaker`), de forma atómica e idempotente.
- Sembrar los 5 usuarios canónicos (`admin@example.com`, `admin2@example.com`, `vendedor@example.com`, `ana@example.com`, `nuevo@example.com` con `debe_cambiar_password = True`) con sus respectivos roles vigentes (`ADMIN`, `VENDEDOR`, `CLIENTE`).
- Sembrar las entidades maestras de autor, editorial y género, y dar de alta los 5 libros canónicos (*Rayuela*, *Antología poética*, *Ficciones*, *Respiración artificial*, *Bestiario*) con sus movimientos de stock inicial balanceados.
- Sembrar a los clientes Lucía Fernández y Tomás Ríos (sin usuario), y Ana Paz (vinculada a `ana@example.com`).
- Registrar la Venta 1 a nombre de Lucía Fernández con 1 *Rayuela* y 2 *Ficciones* (Total: \$69.000,00), con deducción de stock y movimientos negativos asociados, preservando el invariante `libro.stock == SUM(movimientos.cantidad)`.
- Registrar el evento inicial en `evento_seguridad` con actor `'SISTEMA'`.
- Crear la suite de archivos `.http` en `parcial/test/` para los casos C-01 a C-16 en formato compatible con clientes REST (VS Code REST Client / IntelliJ).
- Implementar la suite de tests de integración automatizados con pytest en `parcial/tests/integration/test_e2e_casos_c01_c16.py` para garantizar ejecución determinística en entornos CI/CD.
- Documentar y validar el script SQL `parcial/test/solo_agregado.sql` para el caso C-14.
- Generar el informe de evidencia técnica en `parcial/evidencia/c15_nplusone_evidence.md` con captura de consultas SQL ejecutadas por `GET /ventas/{id}` demostrando ausencia de $N+1$.
- Redactar `parcial/README.md` con las instrucciones completas de puesta en marcha, ejecución del seed y verificación.

**Non-Goals:**
- Despliegue en contenedor Docker y configuración de VPS (reservado exclusivamente para el change C-11 en `despliegue/`).
- Modificación de contratos de datos o arquitectura de routers en `parcial/app/`.

## Decisions

### 1. Arquitectura Asíncrona e Idempotente para `parcial/seed.py`
- **Decisión:** `parcial/seed.py` se ejecutará en un loop asíncrono (`asyncio.run()`), abriendo una sesión asíncrona con el motor configurado en `parcial.app.core.session.async_session_maker`. Cada entidad se verificará por su identificador unívoco (`email` para usuarios, `isbn` para libros, `nombre` para entidades maestras y clientes) antes de crearse. Si la entidad ya existe, el script la reutiliza o actualiza sin duplicar registros ni romper restricciones únicas parciales.
- **Alternativas consideradas:**
  - *Borrar la base de datos completa antes de sembrar (`TRUNCATE`)*: Descartado porque impediría ejecutar el seed en entornos donde conviven datos preexistentes de pruebas o migraciones sin reiniciar la base.

### 2. Formato Dual de Verificación: Archivos `.http` y Suite Pytest Automatizada
- **Decisión:** Para cumplir con la consigna §4.2 ("Casos C-01 a C-16 en archivos `.http` dentro de `parcial/test/`") y las reglas de testing riguroso del orquestador, se proveerán ambas capas:
  1. Archivos `.http` en `parcial/test/` estructurados con variables, peticiones ordenadas y comentarios descriptivos para inspección manual y demostración.
  2. Suite de pruebas de integración en `parcial/tests/integration/test_e2e_casos_c01_c16.py` que ejecuta programáticamente los 16 casos con `httpx.AsyncClient`, verificando códigos de estado, cabeceras (ej. `Retry-After: 60`, `Set-Cookie`), cookies y payloads.
- **Alternativas consideradas:**
  - *Únicamente archivos `.http`*: No permitiría validación automatizada mediante `pytest`.
  - *Únicamente tests pytest*: Incumpliría el requerimiento explícito de la consigna de entregar archivos `.http`.

### 3. Evidencia Técnica Cuantitativa para C-15 ($N+1$)
- **Decisión:** La evidencia técnica de C-15 en `parcial/evidencia/c15_nplusone_evidence.md` se generará capturando los statements SQL mediante un listener de SQLAlchemy (`before_cursor_execute`) tanto para ventas con 1 renglón como para ventas con múltiples renglones (e.g., 5 o 10 renglones), demostrando cuantitativamente que la cantidad total de consultas SQL ejecutadas por `GET /ventas/{id}` permanece estrictamente constante e independiente de $N$.
- **Alternativas consideradas:**
  - *Inspección visual del código*: Insuficiente como evidencia técnica empírica requerida por la consigna.

## Risks / Trade-offs

- **[Riesgo] Costo de tiempo en el hashing de contraseñas de seed** → *Mitigación:* Se precalculan o generan los hashes mediante el servicio `PasswordService` con el costo configurado en `Settings`, ejecutándose concurrentemente o en lotes limpios.
- **[Riesgo] Invariante de stock inconsistente tras re-ejecución del seed** → *Mitigación:* Si la venta inicial 1 o los movimientos de stock ya existen, el seed detecta la existencia previa y no replica los descuentos ni movimientos, asegurando que `libro.stock == SUM(movimientos.cantidad)` se mantenga en todo momento.
- **[Riesgo] Dependencia de servicios externos o Docker en tests** → *Mitigación:* La suite automatizada de pytest utiliza los fixtures de sesión asíncrona existentes en `parcial/tests/integration/conftest.py`, aislando el estado de cada prueba.

## Migration Plan

- No requiere nuevas migraciones de base de datos.
- Requiere tener ejecutadas las migraciones de Alembic hasta `004_trigger_append_only`.
- Se ejecuta la siembra con `python -m parcial.seed` o directamente al levantar el entorno.
