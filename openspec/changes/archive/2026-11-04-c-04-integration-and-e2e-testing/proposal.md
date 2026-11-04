# Proposal: C-04 Integration and E2E Testing

## Why

El backend cuenta con los módulos fundamentales de configuración, ciclo de vida, persistencia asíncrona, migraciones con Alembic y controladores REST para la entidad Item. Sin embargo, se requiere una suite de validación integral End-to-End (E2E), fixtures centralizados con aislamiento transaccional y pruebas de resiliencia ante cortes o timeouts de PostgreSQL, garantizando la fiabilidad del sistema para su entrega y evaluación final.

## What Changes

- Creación de configuración centralizada de fixtures en `tests/conftest.py` para testing asíncrono con `pytest-asyncio` y clientes HTTP `httpx.AsyncClient(transport=ASGITransport(app=app))`.
- Implementación de suite de pruebas E2E en `tests/integration/test_e2e_workflow.py` validando el flujo completo de vida de la aplicación, endpoints de salud y ciclo CRUD de artículos.
- Implementación de pruebas de resiliencia y tolerancia a fallos en `tests/integration/test_resilience.py` validando el comportamiento de `/health/ready` ante caídas de conexión y timeouts forzados (> 2 segundos).
- Configuración de reporte de cobertura de código mediante `pytest-cov` en `pyproject.toml` para auditar `src/`.
- Actualización de `README.md` con instrucciones detalladas de ejecución de pruebas E2E, scripts de verificación para evaluadores y reporte de métricas de cobertura.

## Capabilities

### New Capabilities
- `system-verification`: Define los contratos de verificación integral E2E, resiliencia ante indisponibilidad de dependencias de persistencia y ejecución automatizada de pruebas con reporte de cobertura.

### Modified Capabilities
<!-- No se modifican contratos funcionales de las capacidades existentes -->

## Impact

- **Código y Tests**: Nuevas suites de pruebas en `tests/integration/test_e2e_workflow.py` y `tests/integration/test_resilience.py`. Fixtures compartidos en `tests/conftest.py`.
- **Configuración**: Adición de directivas de cobertura (`pytest-cov`) en `pyproject.toml` y dependencias de test en `requirements.txt`.
- **Documentación**: Sección de validación y evaluación final en `README.md`.
