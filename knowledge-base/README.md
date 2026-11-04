# Parcial 2 Programación — Base de Conocimiento (Knowledge Base)

Base de conocimiento canónica generada para el Trabajo Práctico (Capítulos 1 a 4) — Comisión 3 (Autores: Chiarello, Ontivero, Rodriguez, Oliveros).

## Resumen Ejecutivo
Este proyecto sienta las bases arquitectónicas de un backend moderno, modular y completamente asíncrono con **Python 3.11+** y **FastAPI**. Incorpora gestión de configuración centralizada y tipada mediante **pydantic-settings**, persistencia asíncrona no bloqueante con **SQLAlchemy 2.0** y **asyncpg** sobre **PostgreSQL 16**, ciclo de vida gestionado mediante **lifespan** (`@asynccontextmanager`) con verificación de conectividad en el startup y liberación graciosa en el shutdown, y observabilidad mediante sondas de salud (`/health`, `/health/live`, `/health/ready`).

---

## Índice de Archivos Canónicos

| # | Archivo | Contenido |
|---|---|---|
| 01 | [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito del sistema, objetivos por actor, alcance v0.1 y métricas de éxito. |
| 02 | [02_descripcion_general.md](02_descripcion_general.md) | Stack tecnológico, arquitectura en capas, integraciones y endpoints. |
| 03 | [03_actores_y_roles.md](03_actores_y_roles.md) | Actores (desarrolladores, evaluadores, sondas), matriz RBAC y rutas públicas. |
| 04 | [04_modelo_de_datos.md](04_modelo_de_datos.md) | Persistencia asíncrona, DeclarativeBase, pool de conexiones y validación con ping. |
| 05 | [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | Políticas técnicas codificadas: RN-CFG, RN-LFS, RN-HLT y RN-SES. |
| 06 | [06_funcionalidades.md](06_funcionalidades.md) | Épicas e Historias de Usuario (US-001 a US-005) con criterios de aceptación. |
| 07 | [07_flujos_principales.md](07_flujos_principales.md) | Flujos paso a paso: arranque de aplicación, consulta de readiness y shutdown. |
| 08 | [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Estructura de directorios `src/`, inyección de dependencias y variables de entorno. |
| 09 | [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | Registro de decisiones de arquitectura (ADRs) y supuestos de desarrollo. |
| 10 | [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Inconsistencias identificadas y preguntas abiertas priorizadas. |

---

## Quick Start para Desarrolladores

1. **Entender el alcance y visión**: Leer [01_vision_y_objetivos.md](01_vision_y_objetivos.md).
2. **Conocer las tecnologías y arquitectura**: Consultar [02_descripcion_general.md](02_descripcion_general.md) y [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md).
3. **Revisar las reglas técnicas indispensables**: Revisar [05_reglas_de_negocio.md](05_reglas_de_negocio.md).
4. **Implementar funcionalidades y tests**: Seguir los criterios de aceptación en [06_funcionalidades.md](06_funcionalidades.md) y los flujos en [07_flujos_principales.md](07_flujos_principales.md).
