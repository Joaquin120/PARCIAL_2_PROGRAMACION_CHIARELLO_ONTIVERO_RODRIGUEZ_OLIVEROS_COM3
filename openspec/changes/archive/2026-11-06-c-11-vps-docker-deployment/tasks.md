# Tasks: C-11 VPS Docker Deployment

## 1. Estructura y Aislamiento del TP en despliegue/

- [x] 1.1 Crear carpeta `despliegue/` y replicar el código intacto del TP (Capítulos 1 a 4: `src/`, `alembic/`, `alembic.ini`, `requirements.txt`, `.env.example`).
- [x] 1.2 Crear archivo `.dockerignore` en `despliegue/` excluyendo `.env`, `.git`, `__pycache__`, `*.pyc` y archivos temporales para garantizar el aislamiento de credenciales (D-06).

## 2. Dockerfile Multi-Stage y Script de Entrada

- [x] 2.1 Crear el `Dockerfile` multi-stage basado en `python:3.12-alpine` con etapa `builder` para compilar dependencias C (`asyncpg`), etapa `runner` limpia, usuario no root `appuser` (UID 1000) y `HEALTHCHECK` nativo con `wget` sobre `http://127.0.0.1:8000/health/ready` (D-01, D-02, D-07).
- [x] 2.2 Crear el script ejecutable `entrypoint.sh` con espera de disponibilidad de PostgreSQL, ejecución de `alembic upgrade head` y delegación en Uvicorn (D-03).
- [x] 2.3 Compilar la imagen Docker localmente y verificar que el tamaño final sea menor a 100 MB (`docker images`) (D-01).

## 3. Pruebas de Ejecución y Verificaciones D-01 a D-08

- [x] 3.1 Probar ejecución con `docker run --env-file` conectado a la red de PostgreSQL y verificar la aplicación automática de migraciones (D-03, D-04).
- [x] 3.2 Verificar que el proceso corra bajo el usuario no root `appuser` (UID 1000) mediante `docker exec` / `whoami` (D-07).
- [x] 3.3 Validar que el `HEALTHCHECK` reporte estado `healthy` en `docker inspect` (D-02).
- [x] 3.4 Verificar la respuesta HTTP exitosa de los endpoints `/health/live`, `/health/ready` y `/api/v1/items` (D-05).
- [x] 3.5 Auditar las capas del contenedor e historial (`docker history`) confirmando la ausencia de `.env` y secretos embebidos (D-06).
- [x] 3.6 Probar apagado limpio (`docker stop`) confirmando el cierre controlado de conexiones y lifespan (D-08).

## 4. Documentación y Evidencias

- [x] 4.1 Generar el documento `despliegue/evidencia/DEPLOY.md` con los comandos ejecutados y capturas de salida de los criterios D-01 a D-08.
- [x] 4.2 Documentar las instrucciones de compilación y ejecución en `despliegue/README.md`.
