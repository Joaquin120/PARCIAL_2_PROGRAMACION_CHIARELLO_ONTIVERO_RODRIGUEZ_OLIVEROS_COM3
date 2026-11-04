# PARCIAL_2_PROGRAMACION_CHIARELLO_ONTIVERO_RODRIGUEZ_OLIVEROS_COM3 (TP_Cap1a4) — Instrucciones para Agentes

> Este archivo (y su copia `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.  
> Generado a partir de `knowledge-base/`, `CHANGES.md` y `.atl/skill-registry.md`. No editar a mano sin re-sincronizar estos archivos.

---

## Stack Tecnológico

| Capa / Componente | Tecnología | Versión Mínima | Propósito / Justificación |
|---|---|---|---|
| **Lenguaje de Programación** | Python | 3.11+ | Tipado nativo moderno, TaskGroup y runtime asíncrono optimizado. |
| **Framework Web** | FastAPI | 0.115+ | Framework ASGI de alto rendimiento con validación y OpenAPI nativo. |
| **Servidor ASGI** | Uvicorn | 0.30+ | Servidor de aplicaciones ASGI basado en uvloop. |
| **Configuración** | Pydantic Settings | 2.5+ | Validación estricta en tiempo de booteo y parsing de `.env`. |
| **ORM / Acceso a Datos** | SQLAlchemy | 2.0+ | Acceso asíncrono tipado (`AsyncEngine`, `async_sessionmaker`, `Mapped`). |
| **Driver de Base de Datos** | asyncpg | 0.30+ | Driver PostgreSQL asíncrono nativo en C de alto rendimiento. |
| **Motor de Base de Datos** | PostgreSQL | 16-alpine | Motor relacional transaccional ACID ejecutado vía Docker Compose. |
| **Testing** | pytest + pytest-asyncio | 8.0+ | Framework de testing asíncrono con fixtures async. |
| **Cliente HTTP de Pruebas** | HTTPX | 0.27+ | Cliente asíncrono testeando la app con `ASGITransport`. |

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md)

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---|---|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito, actores, alcance v0.1 y métricas de éxito del TP. |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack técnico, arquitectura en capas y catálogo de endpoints. |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores, matriz de permisos y rutas públicas sin autenticación. |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Persistencia asíncrona, DeclarativeBase y validación con ping. |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas técnicas codificadas: RN-CFG, RN-LFS, RN-HLT y RN-SES. |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario (US-001 a US-005) y criterios de aceptación. |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E: startup lifespan, consulta de health y graceful shutdown. |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Estructura de directorios `src/`, inyección de dependencias y variables de entorno. |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Registro de decisiones arquitectónicas (DD-01 a DD-04) y supuestos. |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | Inconsistencias identificadas y preguntas abiertas priorizadas. |

---

## Skills Disponibles

| Agente | Rol | Skills que carga |
|---|---|---|
| **Backend Core** | FastAPI / SQLAlchemy 2.0 Async / Lifespan / Settings | `fastapi-python`, `async-python-patterns` |
| **Testing / QA** | Pruebas unitarias, asíncronas y de integración | `python-testing-patterns` |
| **Orquestación & Foundation** | SDD / OpenSpec / Foundation Flow / Rules | `active-orchestrator`, `kb-creator`, `roadmap-generator`, `agents-md-generator`, `find-skills` |

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo). Esta tabla solo mapea skill→rol.

---

## Roadmap de Changes

El plan de implementación completo está documentado en [CHANGES.md](CHANGES.md). Resumen ejecutivo:

- **Total de changes**: 4 organizados en 2 fases semánticas.
- **Camino crítico**: `C-01 → C-02 → C-03 → C-04`.
- **Primer change obligatorio**: `C-01` (`foundation-setup` / `SPEC-00-fundacion`).

**Antes de cualquier `/opsx:propose`**: leé [CHANGES.md](CHANGES.md), identificá las dependencias del change y los archivos de "Leer antes" de la Knowledge Base.

---

## Reglas Duras (Específicas del Proyecto)

Estas reglas son obligatorias y de cumplimiento estricto en cada iteración de desarrollo:

1. **NUNCA ejecutar operaciones de I/O de base de datos sincrónicas ni bloquear el event loop** → Usar siempre `await db.execute(...)` con SQLAlchemy 2.0 y sesiones obtenidas mediante `async_sessionmaker`.
2. **NUNCA usar los decoradores deprecados `@app.on_event("startup")` ni `@app.on_event("shutdown")`** → Gestionar el ciclo de vida exclusivamente mediante `@asynccontextmanager(app: FastAPI)` en conformidad con el estándar ASGI Lifespan.
3. **NUNCA hardcodear secretos, credenciales o URLs de conexión en código fuente** → Centralizar toda la configuración en `pydantic-settings` tipado con lectura de `.env` y caching como singleton vía `get_settings()` decorado con `@lru_cache()`.
4. **NUNCA acoplar comprobaciones de dependencias externas en el probe de liveness** → El endpoint `GET /health/live` responde únicamente la vitalidad del proceso HTTP; el endpoint `GET /health/ready` comprueba activamente PostgreSQL ejecutando `SELECT 1` con timeout de 2 segundos y retornando `HTTP 503 Service Unavailable` ante indisponibilidad.
5. **NUNCA utilizar clientes HTTP sincrónicos bloqueantes (`requests`, `urllib`) para probar la API** → Utilizar siempre `httpx.AsyncClient` con `ASGITransport(app=app)` y fixtures asíncronas de `pytest-asyncio`.
6. **NUNCA introducir código no tipado o campos no validados** → Usar anotaciones de tipo nativas completas (`typing`) en funciones y esquemas estrictos de Pydantic.

---

## Flujo de Trabajo Operativo

```
1. Leer la KB relevante (knowledge-base/)        → entender el dominio y arquitectura
2. Identificar el change en CHANGES.md           → verificar dependencias satisfechas
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks (cargando skills)       → respetando estrictamente las reglas duras
5. /opsx:archive C-NN-nombre + marcar [x]        → cerrar y auditar el change
```
