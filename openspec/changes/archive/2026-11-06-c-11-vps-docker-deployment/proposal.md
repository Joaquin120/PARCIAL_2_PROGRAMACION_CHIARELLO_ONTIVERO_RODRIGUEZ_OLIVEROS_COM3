# Proposal: C-11 VPS Docker Deployment

## Why
El TP (Capítulos 1 a 4) requiere ser empaquetado y desplegado de forma independiente en un entorno de producción / VPS utilizando Docker. Es necesario garantizar que la aplicación corra de manera segura (usuario sin privilegios, sin secretos embebidos), eficiente (imagen ligera < 100 MB) y resiliente (healthchecks activos y ejecución automática de migraciones de base de datos) en una carpeta aislada `despliegue/`, documentando todas las evidencias requeridas (D-01 a D-08).

## What Changes
- Creación del directorio aislado `despliegue/` que contendrá el código fuente intacto del TP (Capítulos 1 a 4: `src/`, `alembic/`, `alembic.ini`, `requirements.txt`).
- `Dockerfile` multi-stage optimizado basado en `python:3.12-alpine` para lograr una imagen final inferior a 100 MB (**D-01**).
- Configuración de usuario no root (`appuser:appgroup`) para la ejecución del proceso en contenedor (**D-07**).
- Garantía de ausencia total de archivos `.env` o secretos embebidos en capas de imagen (**D-06**).
- Script de arranque `entrypoint.sh` ejecutable que aplica automáticamente migraciones (`alembic upgrade head`) y levanta el servidor ASGI Uvicorn (**D-03**).
- Configuración de directiva `HEALTHCHECK` nativa en Docker que evalúa periódicamente el endpoint `/health/ready` (**D-02**).
- Soporte para inyección de configuración exclusivamente vía variables de entorno (`docker run --env-file`) (**D-04**).
- Carpeta `despliegue/evidencia/` y documento `DEPLOY.md` conteniendo comandos, outputs y verificaciones de los criterios D-01 a D-08 (**D-01 a D-08**).

## Capabilities

### New Capabilities
- `vps-docker-deployment`: Despliegue contenerizado del backend TP (Capítulos 1 a 4) en Alpine Linux con multi-stage build, usuario sin privilegios, healthcheck nativo, script de arranque con migraciones y reporte de evidencia D-01 a D-08.

### Modified Capabilities
*(Ninguna; las capacidades funcionales previas del TP y Parcial permanecen intactas y sin modificaciones en sus requerimientos de software).*

## Impact
- **Código y Directorios**: Se crea la carpeta de nivel raíz `despliegue/` y sus subdirectorios (`despliegue/evidencia/`). No se alteran los archivos funcionales existentes en `src/` ni en `parcial/`.
- **APIs**: No se introducen cambios breaking ni modificaciones a las firmas de endpoints de `src/api/`.
- **Dependencias y Runtime**: Se utiliza Alpine Linux 3.12 con Python 3.12, dependencias de compilación en etapa builder y runtime minimal en etapa final.
