# Design: C-11 VPS Docker Deployment

## Context
El TP (Capítulos 1 a 4) cuenta con arquitectura FastAPI asíncrona, SQLAlchemy 2.0 y migraciones con Alembic. Para su despliegue en un VPS, se requiere aislar la aplicación en una carpeta `despliegue/` y generar una imagen Docker multi-stage optimizada sobre Alpine Linux con un tamaño inferior a 100 MB, usuario no root, healthcheck nativo y arranque automatizado con migraciones.

## Goals / Non-Goals

**Goals:**
- Crear la estructura aislada en `despliegue/` con código del TP (`src/`, `alembic/`, `alembic.ini`, `requirements.txt`).
- Diseñar un `Dockerfile` multi-stage basado en `python:3.12-alpine` que logre una imagen final menor a 100 MB (**D-01**).
- Configurar el usuario no root `appuser` (UID/GID 1000) para la ejecución segura del proceso (**D-07**).
- Asegurar aislamiento estricto de secretos y exclusión de `.env` en la imagen mediante `.dockerignore` (**D-06**).
- Crear un script `entrypoint.sh` que ejecute `alembic upgrade head` y luego inicie Uvicorn (**D-03**).
- Incorporar directiva `HEALTHCHECK` usando `wget` nativo de Alpine sobre `http://127.0.0.1:8000/health/ready` (**D-02**).
- Permitir ejecución parametrizada con `docker run --env-file` (**D-04**).
- Generar el documento `DEPLOY.md` en `despliegue/evidencia/` con el registro de comandos y salidas de verificación para D-01 a D-08.

**Non-Goals:**
- No incluye el código del Parcial (Capítulos 5 y 6 que residen en `parcial/`).
- No configura un reverse proxy externo (Nginx/Traefik) ni certificados SSL en este hito (a menos que se requiera como complemento externo).

## Decisions

### 1. Construcción Multi-Stage en Alpine con Virtualenv Aislado
- **Decisión**: Utilizar dos etapas en el Dockerfile: `builder` (con `gcc`, `musl-dev`, `python3-dev`, `libpq-dev` para compilar dependencias C como `asyncpg`) y `runner` (imagen limpia `python:3.12-alpine` instalando únicamente la biblioteca de runtime `libpq`).
- **Razón**: Permite compilar paquetes nativos sin dejar herramientas de compilación en la imagen final, garantizando un tamaño menor a 100 MB (típicamente ~70-85 MB).
- **Alternativas consideradas**: Usar `python:3.12-slim` (Debian base), pero su tamaño suele rondar los 150-220 MB, superando el límite estricto de 100 MB de la consigna.

### 2. Arranque y Migraciones mediante `entrypoint.sh`
- **Decisión**: El script de entrada esperará disponibilidad de la base de datos, ejecutará `alembic upgrade head` para sincronizar el esquema y luego delegará en Uvicorn mediante `exec "$@"`.
- **Razón**: Garantiza que las tablas existan antes de que el ASGI Lifespan y el endpoint de readiness respondan tráfico HTTP.
- **Alternativas consideradas**: Ejecutar migraciones manuales antes del deploy, lo cual es propenso a errores y rompe la automatización del despliegue en VPS.

### 3. Healthcheck Nativo con `wget`
- **Decisión**: Usar `wget -qO- http://127.0.0.1:8000/health/ready || exit 1` en la directiva `HEALTHCHECK`.
- **Razón**: `wget` viene preinstalado en BusyBox/Alpine, evitando instalar `curl` y ahorrando espacio.
- **Alternativas consideradas**: Instalar `curl` vía apk (agrega dependencias y megabytes adicionales innecesarios).

### 4. Estructura de Evidencias D-01 a D-08 en `despliegue/evidencia/DEPLOY.md`
- **Decisión**: Estructurar el reporte con secciones explícitas:
  - **D-01**: Verificación de tamaño de imagen (`docker images`).
  - **D-02**: Verificación de HEALTHCHECK (`docker inspect` / `docker ps`).
  - **D-03**: Salida de ejecución automática de migraciones.
  - **D-04**: Ejecución con `--env-file`.
  - **D-05**: Respuestas de `/health/live`, `/health/ready` y endpoints de items.
  - **D-06**: Inspección de capas y confirmación de no inclusión de `.env` o credenciales.
  - **D-07**: Verificación de usuario `appuser` (no root).
  - **D-08**: Graceful shutdown y cleanup de conexiones.

## Risks / Trade-offs

- **[Riesgo] Compilación de `asyncpg` en musl libc (Alpine)**  
  → **Mitigación**: Añadir `musl-dev`, `gcc` y encabezados necesarios en la etapa `builder`, verificando que la rueda compilada sea compatible con la etapa `runner` en Alpine 3.12.
- **[Riesgo] Tamaño de imagen superior a 100 MB**  
  → **Mitigación**: Usar `pip install --no-cache-dir`, eliminar caches y temporales, y copiar únicamente el entorno virtual en la etapa final.
- **[Riesgo] Fallo de conectividad a PostgreSQL en el primer segundo de arranque**  
  → **Mitigación**: Incorporar reintentos en `entrypoint.sh` antes de invocar `alembic upgrade head`.
