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
DB_ECHO=False
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_TIMEOUT=2.0
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

### 1. Ejecutar la suite completa con reporte de cobertura (100% Target)
```bash
pytest -v --cov=src --cov-report=term-missing
```

### 2. Ejecutar por categorías específicas
```bash
# Pruebas unitarias (configuración, modelos, session, alembic, schemas)
pytest tests/unit/ -v

# Pruebas de integración (health probes, lifespan, migraciones, items api)
pytest tests/integration/ -v

# Prueba de flujo End-to-End (E2E)
pytest tests/integration/test_e2e_workflow.py -v

# Pruebas de resiliencia y tolerancia a fallos
pytest tests/integration/test_resilience.py -v
```
