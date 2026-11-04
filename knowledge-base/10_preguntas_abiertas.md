# 10 — Preguntas Abiertas e Inconsistencias

## Inconsistencias detectadas

### IN-01 — Nombre y convención de endpoint unificado de salud vs sondas granulares
- **Situación**: Algunos evaluadores prefieren un único endpoint `/health` que reporte el estado general, mientras que las mejores prácticas cloud-native separan `/health/live` y `/health/ready`.
- **Impacto**: Posible confusión durante la corrección si se espera una ruta específica.
- **Resolución propuesta**: Implementar `/health` como alias consolidado y además exponer `/health/live` y `/health/ready` de forma granular.

---

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor |
|---|---|---|---|
| **Alta** | ¿Cuál es la convención definitiva de logging requerida por la cátedra (`logging` estándar formateado o JSON estructurado con `structlog`)? | Implementación de middlewares y logs en lifespan | Equipo de Desarrollo / Cátedra |
| **Media** | ¿Se utilizará una base de datos SQLite en memoria (`sqlite+aiosqlite`) para los tests unitarios rápidos o se correrán siempre contra el PostgreSQL de Docker? | Fixtures de testing en `tests/conftest.py` | Equipo de Desarrollo |
| **Baja** | ¿Qué entidades de negocio específicas se incorporarán en el Capítulo 5 (siguiente etapa del TP)? | Modelos futuros de SQLAlchemy | Enunciado de cátedra (próximo hito) |
