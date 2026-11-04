# 03 — Actores y Roles

## Actores del sistema

| Actor | Tipo | Descripción | Canal de Interacción |
|---|---|---|---|
| **Desarrollador / Alumno** | Humano (Interno) | Integrante del equipo de desarrollo (Chiarello, Ontivero, Rodriguez, Oliveros) que implementa código, tests y configuraciones. | IDE, CLI (pytest, git, docker compose, openspec) |
| **Docente / Evaluador** | Humano (Externo) | Integrante del equipo docente de Programación Comisión 3 que evalúa el cumplimiento de pautas técnicas y arquitectura. | Repositorio git, CLI de pruebas, Swagger UI (`/docs`), endpoints HTTP |
| **Proceso / SRE Probe** | Máquina (Automatizado) | Agente de orquestación (Docker healthcheck, Kubernetes kubelet o script de monitoreo) que consulta periódicamente el estado. | Peticiones HTTP a `/health/live` y `/health/ready` |
| **Cliente de API / Consumidor** | Sistema / Aplicación | Aplicaciones cliente futuras que consumirán los servicios y endpoints de negocio en capítulos posteriores. | Peticiones HTTP REST |

## RBAC — Matriz de permisos

En esta etapa fundacional (SPEC-00-fundacion), la API no cuenta con mecanismos de autenticación por usuario ni roles administrativos de negocio. Todos los endpoints implementados corresponden a diagnóstico técnico y documentación pública.

| Rol | Recurso /health | Recurso /health/ready | Recurso /docs & /openapi.json | Configuración interna (.env) |
|---|---|---|---|---|
| **Público / Anónimo** | Lectura (`GET`) | Lectura (`GET`) | Lectura (`GET`) | Sin acceso |
| **Monitor / Probe** | Lectura (`GET`) | Lectura (`GET`) | Sin acceso (no requerido) | Sin acceso |
| **Desarrollador** | Lectura (`GET`) | Lectura (`GET`) | Lectura (`GET`) | Lectura / Escritura local |

## Rutas públicas

Las siguientes rutas son de acceso irrestricto y no requieren cabeceras de autorización (`Authorization: Bearer`):

- `GET /health` — Estado consolidado del backend.
- `GET /health/live` — Verificación de vida del proceso FastAPI.
- `GET /health/ready` — Verificación de preparación y conexión activa a PostgreSQL.
- `GET /docs` — Swagger UI interactivo.
- `GET /redoc` — Documentación ReDoc.
- `GET /openapi.json` — Esquema OpenAPI 3.1 en formato JSON.
