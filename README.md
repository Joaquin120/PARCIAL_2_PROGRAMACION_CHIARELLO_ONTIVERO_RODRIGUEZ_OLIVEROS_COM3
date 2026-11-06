# Backend Asíncrono - Parcial 2 Programación (TP Capítulos 1 a 4)

Backend asíncrono de alto rendimiento desarrollado con **FastAPI**, **SQLAlchemy 2.0 (Asyncio)**, **Alembic**, **asyncpg** y **PostgreSQL 16**.

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.11+
- **Framework Web:** FastAPI 0.115+
- **Servidor ASGI:** Uvicorn 0.30+
- **Configuración:** Pydantic Settings 2.5+
- **ORM / Persistencia:** SQLAlchemy 2.0+ (AsyncEngine, AsyncSession, async_sessionmaker)
- **Migraciones:** Alembic 1.13+ (Async mode con template async)
- **Driver DB:** asyncpg 0.30+
- **Base de Datos:** PostgreSQL 16 Alpine (vía Docker Compose)
- **Testing:** pytest 8.0+, pytest-asyncio, HTTPX (ASGITransport)

---

## 🚀 Inicio Rápido

### 1. Clonar el repositorio y configurar el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Linux/macOS
# o .venv\Scripts\activate en Windows
```

### 2. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar la plantilla de variables de entorno:

```bash
cp .env.example .env
```

Variables disponibles en `.env`:
```env
APP_NAME=TP_Cap1a4_Backend
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tp_cap1a4_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tp_cap1a4_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DB_ECHO=False
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_TIMEOUT=2.0

# Seguridad y Autenticación (Parcial)
SECRET_KEY=supersecretkey-parcial-2026-unbreakable-token
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BCRYPT_ROUNDS=12
BCRYPT_MAX_CONCURRENCY=4
COOKIE_SECURE=False
```

### 4. Iniciar base de datos local con Docker Compose

```bash
docker compose up -d
```

Verificar el estado del contenedor:
```bash
docker compose ps
```

### 5. Aplicar migraciones de base de datos

Ejecutar las migraciones pendientes con Alembic hacia PostgreSQL:

```bash
alembic upgrade head
```

Para revertir la última migración:
```bash
alembic downgrade -1
```

Para generar una nueva revisión a partir de cambios en los modelos declarativos:
```bash
alembic revision --autogenerate -m "descripcion_del_cambio"
```

### 6. Iniciar el servidor de desarrollo

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación interactiva estará disponible en:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📦 Modelos de Dominio y Persistencia

Las entidades de datos residen en `src/db/models/` e integran:
- `TimestampMixin`: Campos automáticos `created_at` y `updated_at` (timezone aware, delegados al motor con `func.now()`).
- `AuditMixin`: Hereda de `TimestampMixin` y agrega bandera de estado lógico `is_active` (`Boolean`, default `True`).
- `Item`: Modelo de dominio inicial con atributos `id`, `name`, `description`, `price`, `stock`, `is_active`, `created_at` y `updated_at`.
- Convención de nombres unificada (`POSTGRES_NAMING_CONVENTION`) para claves foráneas (`fk_*`), claves primarias (`pk_*`), checks (`ck_*`), índices (`ix_*`) y restricciones únicas (`uq_*`).

---

## 🩺 Endpoints de Salud (Health Probes)

| Endpoint | Método | Tipo | Descripción | Códigos HTTP |
|---|---|---|---|---|
| `/health` | `GET` | Liveness | Comprueba inmediatamente que el proceso web está activo | `200 OK` |
| `/health/live` | `GET` | Liveness | Alias de `/health` para orquestadores (K8s/Docker) | `200 OK` |
| `/health/ready` | `GET` | Readiness | Comprueba conexión activa a PostgreSQL (`SELECT 1`) con timeout de 2s | `200 OK` / `503 Service Unavailable` |

*Nota: También se encuentran disponibles bajo el prefijo `/api/v1` (ej. `/api/v1/health/ready`).*

---

## 🛍️ Catálogo de Endpoints de Ítems (`/api/v1/items`)

Endpoints REST asíncronos para la gestión de productos/ítems con validación estricta Pydantic v2:

| Endpoint | Método | Descripción | Códigos HTTP |
|---|---|---|---|
| `/api/v1/items/` | `POST` | Crea un nuevo ítem en la base de datos | `201 Created`, `422 Unprocessable Entity` |
| `/api/v1/items/` | `GET` | Lista ítems con paginación (`skip`, `limit`) y filtro opcional `is_active` | `200 OK` |
| `/api/v1/items/{id}` | `GET` | Obtiene el detalle de un ítem por ID | `200 OK`, `404 Not Found` |
| `/api/v1/items/{id}` | `PUT` | Actualización total de un ítem existente | `200 OK`, `404 Not Found`, `422 Unprocessable Entity` |
| `/api/v1/items/{id}` | `PATCH` | Actualización parcial de campos de un ítem | `200 OK`, `404 Not Found`, `422 Unprocessable Entity` |
| `/api/v1/items/{id}` | `DELETE` | Eliminación física del ítem en la base de datos | `204 No Content`, `404 Not Found` |

*Nota: Los endpoints también se encuentran accesibles bajo el prefijo `/items` para compatibilidad directa.*

### Parámetros de Consulta para Listado (`GET /api/v1/items/`):
- `skip` (int, default `0`, min `0`): Desplazamiento inicial de resultados.
- `limit` (int, default `10`, min `1`, max `100`): Límite máximo de elementos por página.
- `is_active` (bool, opcional): Filtrar exclusivamente por estado activo (`true`) o inactivo (`false`).

### Ejemplo de Creación (`POST /api/v1/items/`):
```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teclado Mecánico RGB",
    "description": "Switch Brown inalámbrico",
    "price": 89.99,
    "stock": 15,
    "is_active": true
  }'
```

---

## 🧪 Ejecución de Pruebas y Cobertura

### 1. Ejecutar la suite completa del proyecto
```bash
pytest -v
```

### 2. Ejecutar pruebas unitarias (sin base de datos externa)
```bash
pytest parcial/tests/unit/ -v
pytest tests/unit/ -v
```

### 3. Ejecutar pruebas de integración (requiere PostgreSQL activo)
Asegurarse de tener la base de datos levantada con `docker compose up -d`:
```bash
# Pruebas de integración del módulo parcial (autenticación, roles, auditoría)
pytest parcial/tests/integration/ -v

# Pruebas de integración del backend base (health probes, items, resiliencia)
pytest tests/integration/ -v
```

---

## 🔒 Arquitectura de Seguridad y Autenticación (Parcial)

### 1. Mecanismo de Sesión y Cookies HttpOnly
- El token JWT (HS256) se transmite **exclusivamente** mediante una cookie segura `access_token`:
  - `HttpOnly=True`: Inaccesible desde JavaScript en el navegador.
  - `SameSite="Lax"`: Protección CSRF estándar.
  - `Secure`: Controlado por la variable de entorno `COOKIE_SECURE` (`True` en producción, `False` en desarrollo local).
  - `path="/"`: Válido en toda la aplicación.
- Se rechaza explícitamente el uso de tokens en el cuerpo JSON o vía cabecera `Authorization: Bearer` (responde `401 Unauthorized`).

### 2. Rate Limiting de Autenticación
- Se controlan los fallos de acceso por combinación `(email, ip)` en una ventana deslizante de 60 segundos.
- Al alcanzar 5 fallos en la ventana, se responde inmediatamente `429 Too Many Requests` con la cabecera `Retry-After: 60`, sin ejecutar hashing de contraseñas para proteger los recursos del servidor.
- Los intentos de acceso se persisten en una transacción aislada para no perder el conteo ante rollbacks.

### 3. Mitigación de Ataques de Temporización (Timing Attacks)
- Durante el lifespan del servidor se precomputa un hash bcrypt ficticio (`app.state.fictitious_password_hash`).
- Si se intenta autenticar con un correo inexistente, se ejecuta la verificación contra dicho hash para mantener tiempos de respuesta equivalentes y no revelar la existencia de la cuenta.

### 4. Control de Acceso Basado en Roles Dinámico (RBAC)
- Los roles asignados (`ADMIN`, `VENDEDOR`, `CLIENTE`) se consultan dinámicamente en la base de datos (`asignacion_rol`) en cada petición.
- Si un rol es revocado o expira (`vence_en`), la pérdida de privilegios tiene efecto inmediato en la siguiente petición.
- El sistema protege al último administrador activo: se rechaza la revocación del rol `ADMIN` que dejaría al sistema sin administradores, utilizando bloqueo pesimista `SELECT ... FOR UPDATE`.
- Los administradores no pueden auto-revocarse el rol `ADMIN`.

### 5. Auditoría de Seguridad Transaccional
- Toda mutación crítica (alta de personal, asignación de rol, revocación de rol y cambio de contraseña) registra un evento en la tabla `evento_seguridad` dentro de la misma transacción (Unit of Work).
- Los eventos pueden ser consultados por administradores en `GET /eventos` mediante el envoltorio de paginación estándar `{items, total, page, size, pages}`.
