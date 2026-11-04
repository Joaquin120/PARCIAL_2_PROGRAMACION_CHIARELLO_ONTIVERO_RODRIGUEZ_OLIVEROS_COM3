# Tasks: C-04 Integration and E2E Testing

## 1. Infraestructura de Pruebas y Fixtures Compartidos

- [x] 1.1 Configurar soporte de cobertura con `pytest-cov` en `requirements.txt` y `pyproject.toml` definiendo flags de cobertura sobre `src/`.
- [x] 1.2 Implementar fixtures compartidos en `tests/conftest.py` (`async_client`, `isolated_db_session`, `clean_storage`) garantizando aislamiento transaccional por test y verificar que las suites existentes continúen pasando.

## 2. Suites de Pruebas E2E y Resiliencia

- [x] 2.1 Implementar suite de pruebas End-to-End en `tests/integration/test_e2e_workflow.py` validando la secuencia completa de probes de salud (`/health/live`, `/health/ready`) y el ciclo de vida CRUD de artículos (`POST`, `GET`, `PATCH`, `DELETE`) con `httpx.AsyncClient`.
- [x] 2.2 Implementar suite de resiliencia en `tests/integration/test_resilience.py` validando el manejo de fallos operativos y timeouts de conexión (> 2.0s) en `/health/ready` retornando `HTTP 503 Service Unavailable`.

## 3. Verificación de Entrega y Cobertura

- [x] 3.1 Ejecutar la suite completa de pruebas con reporte de cobertura mediante `pytest --cov=src --cov-report=term-missing` verificando 100% de tests en verde.
- [x] 3.2 Actualizar `README.md` con los comandos de ejecución de pruebas E2E, verificación de resiliencia y reporte de cobertura de código para la entrega final.

## Workflow follow-up

- Ejecutar `/opsx:apply` para iniciar la implementación de las tareas.
- Ejecutar `/opsx:verify` para validar la integridad estricta del cambio.
- Archivar el change con `/opsx:archive c-04-integration-and-e2e-testing`.
- Marcar como completado el checkbox de `C-04` en `CHANGES.md`.
