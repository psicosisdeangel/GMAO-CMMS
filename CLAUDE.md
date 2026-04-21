# GMAO — Sistema de Gestión de Mantenimiento Asistido por Ordenador

---

## 1. Contexto del proyecto

**Qué es:** Sistema web para gestionar mantenimiento preventivo y correctivo de equipos industriales en una planta mediana.

**Usuarios:** Hasta **30 concurrentes** (REQ-14). Dos roles: `TECNICO` y `SUPERVISOR`.

**Datos clave:** Equipos, órdenes de trabajo (preventivas y correctivas), historial técnico de hasta 10 años (REQ-06), repuestos, bitácora de auditoría inmutable (REQ-13, retención ≥ 5 años).

**Documentos base del proyecto** (deben existir en `/docs` del repo):
- `REQUISITOS_GMAO.pdf` — 15 requisitos funcionales + normativas
- `GMAO_Arquitectura_Calidad.pdf` — arquitectura, atributos ISO/IEC 25010, escenarios ATAM

Si una decisión de implementación contradice estos documentos, **gana el documento**. Si hay ambigüedad, se pregunta al usuario; no se improvisa.

---

## 2. Stack tecnológico (fijo)

| Capa | Tecnología | Versión mínima | Notas |
|------|-----------|----------------|-------|
| Backend | Python + Django + Django REST Framework | Python 3.11+, Django 5.x, DRF 3.15+ | |
| Autenticación | `djangorestframework-simplejwt` | Última estable | JWT, TTL 30 min (REQ-08) |
| Hash passwords | `bcrypt` vía `django[bcrypt]` | cost factor ≥ 12 | REQ-08 |
| Base de datos | MySQL | 8.0+ | Motor InnoDB (transacciones ACID, REQ-12) |
| ORM driver | `mysqlclient` | Última estable | |
| Scheduler | Celery + Redis | 5.x / 7.x | Para REQ-03 (órdenes recurrentes). Alternativa: `django-q2` si se quiere evitar Redis |
| Frontend | React + TypeScript + Vite | React 18+, Vite 5+, TS 5+ | |
| Estilos | TailwindCSS | 3.x | |
| HTTP client | Axios | Última estable | Interceptor para JWT |
| Routing | React Router | 6.x | |
| State (servidor) | TanStack Query (React Query) | 5.x | Cachea y sincroniza datos de API |
| State (cliente) | Zustand | Solo si hace falta estado global no-servidor | No usar Redux salvo necesidad real |
| Forms | React Hook Form + Zod | Última estable | Validación tipada |
| Testing backend | pytest + pytest-django + factory-boy + coverage | | |
| Testing frontend | Vitest + React Testing Library | Vitest tiene API Jest-compatible | |
| CI/CD | GitHub Actions | | |

**No introducir otras librerías pesadas sin discutirlo primero.**

---

## 3. Estructura del monorepo

```
gmao/
├── README.md                    # Overview corto para humanos
├── CLAUDE.md                    # Este archivo (contexto para IA)
├── docker-compose.yml           # Opcional (dev con MySQL + Redis)
├── .github/
│   └── workflows/
│       ├── backend-ci.yml       # lint + pytest + coverage
│       └── frontend-ci.yml      # lint + typecheck + vitest
├── docs/
│   ├── REQUISITOS_GMAO.pdf
│   └── GMAO_Arquitectura_Calidad.pdf
├── backend/
│   ├── manage.py
│   ├── pyproject.toml           # ruff + black + pytest config
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   ├── gmao/                    # Django project config
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── authentication/      # login, JWT, middleware RBAC
│   │   ├── users/               # gestión usuarios (REQ-07)
│   │   ├── equipment/           # REQ-01
│   │   ├── work_orders/         # REQ-02, 03, 04, 05
│   │   ├── inventory/           # Repuestos (mínimo)
│   │   ├── audit/               # REQ-13 (bitácora inmutable)
│   │   └── reports/             # REQ-09, REQ-11 (dashboard)
│   └── scripts/                 # seed de datos, utilidades
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── .env.example
    └── src/
        ├── api/                 # axios instance + endpoints por recurso
        ├── components/ui/       # componentes genéricos reutilizables
        ├── features/            # feature-based (recomendado)
        │   ├── auth/
        │   ├── equipment/
        │   ├── work-orders/
        │   ├── dashboard/
        │   ├── reports/
        │   └── users/
        ├── hooks/
        ├── layouts/
        ├── pages/
        ├── router/
        ├── types/               # tipos compartidos (reflejo de serializers)
        └── utils/
```

### Estructura interna de cada app de Django (OBLIGATORIA — REQ-15)

Cada app en `backend/apps/<nombre>/` sigue **estrictamente** el patrón Controller-Service-Repository:

```
equipment/
├── __init__.py
├── apps.py
├── models.py               # modelos ORM (no lógica de negocio)
├── serializers.py          # DRF serializers (validación de shape)
├── urls.py                 # rutas -> controllers
├── controllers/            # (views en jerga Django) — SIN lógica de negocio
│   ├── __init__.py
│   └── equipment_controller.py
├── services/               # LÓGICA DE NEGOCIO VIVE AQUÍ
│   ├── __init__.py
│   └── equipment_service.py
├── repositories/           # acceso a ORM — sin reglas de negocio
│   ├── __init__.py
│   └── equipment_repository.py
├── exceptions.py           # excepciones de dominio propias
└── tests/
    ├── test_services.py
    ├── test_controllers.py
    └── test_repositories.py
```

---

## 4. Arquitectura (CRÍTICO — leer siempre antes de codear)

El sistema es un **monolito en capas** con patrón **Controller-Service-Repository (CSR)**. Esto es un requisito obligatorio (REQ-15), no una sugerencia.

### 4.1 Responsabilidades por capa

| Capa | Qué SÍ hace | Qué NO hace |
|------|-------------|-------------|
| **Controller** (`views` de DRF) | Recibir HTTP, validar JWT+RBAC, deserializar payload, llamar al service, serializar respuesta | Acceder a `Model.objects.*` directamente. Contener reglas de negocio. Cerrar transacciones. |
| **Service** | Toda la lógica de negocio: validaciones de dominio, cálculos (MTTR), orquestación de repositories, transacciones | Conocer HTTP, request, response, serializers. |
| **Repository** | Encapsular el ORM: `get`, `create`, `update`, `list`, queries complejas | Aplicar reglas de negocio. Validar permisos. |
| **Models** | Definir esquema, constraints, índices, FKs | Lógica compleja (usar services). |

### 4.2 Ejemplo canónico (seguir este patrón literalmente)

**controller** (`apps/equipment/controllers/equipment_controller.py`):
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.authentication.permissions import HasRole
from apps.equipment.serializers import EquipmentCreateSerializer, EquipmentReadSerializer
from apps.equipment.services.equipment_service import EquipmentService
from apps.equipment.exceptions import DuplicateEquipmentIdError

class EquipmentListCreateController(APIView):
    permission_classes = [HasRole("SUPERVISOR")]  # solo para POST; GET podría ser menos restrictivo

    def post(self, request):
        serializer = EquipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipment = EquipmentService.create_equipment(
                data=serializer.validated_data,
                actor=request.user,
            )
        except DuplicateEquipmentIdError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        return Response(EquipmentReadSerializer(equipment).data, status=status.HTTP_201_CREATED)
```

**service** (`apps/equipment/services/equipment_service.py`):
```python
from django.db import transaction
from apps.equipment.repositories.equipment_repository import EquipmentRepository
from apps.audit.services.audit_service import AuditService
from apps.equipment.exceptions import DuplicateEquipmentIdError

class EquipmentService:
    @staticmethod
    @transaction.atomic
    def create_equipment(data: dict, actor) -> "Equipment":
        if EquipmentRepository.exists_by_id_unico(data["id_unico"]):
            raise DuplicateEquipmentIdError(f"ID {data['id_unico']} ya existe")
        equipment = EquipmentRepository.create(data)
        AuditService.log(
            action="CREATE_EQUIPMENT",
            entity="Equipment",
            entity_id=equipment.id_unico,
            actor=actor,
            details=data,
        )
        return equipment
```

**repository** (`apps/equipment/repositories/equipment_repository.py`):
```python
from apps.equipment.models import Equipment

class EquipmentRepository:
    @staticmethod
    def exists_by_id_unico(id_unico: str) -> bool:
        return Equipment.objects.filter(id_unico=id_unico).exists()

    @staticmethod
    def create(data: dict) -> Equipment:
        return Equipment.objects.create(**data)

    @staticmethod
    def get_by_id(id_unico: str) -> Equipment | None:
        return Equipment.objects.filter(id_unico=id_unico).first()
```

### 4.3 Reglas rojas de arquitectura (si aparecen en un PR, se rechaza)

1. **Nunca** llamar `Model.objects.*` desde un controller o serializer.
2. **Nunca** poner lógica de negocio en `models.py` más allá de `__str__`, `Meta` y validaciones triviales de campo.
3. **Nunca** abrir transacciones en el controller. Las transacciones viven en el service con `@transaction.atomic`.
4. **Nunca** usar `ModelViewSet` con `queryset` + `serializer_class` auto-generando todo el CRUD. Rompe el patrón CSR. Usar `APIView` o `GenericAPIView` + services explícitos.
5. **Nunca** exponer modelos de ORM al frontend. Siempre pasar por serializers.
6. El **frontend no contiene lógica de negocio**. Solo validación de forma (React Hook Form + Zod) y orquestación de UI.

---

## 5. Modelo de dominio

### Entidades principales

| Entidad | PK | Notas clave |
|---------|----|-------------|
| `Equipment` | `id_unico` (varchar, inmodificable) | REQ-01. PK de negocio, no autoincremental. |
| `WorkOrder` | `id_orden` (autoinc) | REQ-02/03/04/05. `tipo` ∈ {PREVENTIVO, CORRECTIVO}. `estado` ∈ {PROGRAMADO, EN_PROCESO, CERRADA}. Cuando `estado=CERRADA` → inmutable. |
| `User` | `id` (autoinc) | REQ-07. Usar `AbstractBaseUser` de Django extendido. Campo `rol` ∈ {TECNICO, SUPERVISOR}. `is_active` controla bloqueo de cuenta. |
| `SparePart` | `id_repuesto` (autoinc) | `cantidad_stock`, decrementado atómicamente al cerrar orden. |
| `WorkOrderSparePart` | compuesta | Join table entre `WorkOrder` y `SparePart` con `cantidad_usada`. |
| `AuditLog` | `id_log` (autoinc) | REQ-13. **Inmutable** a nivel de aplicación y BD (ver §7). |
| `MaintenanceChecklist` | `id_checklist` | Opcional fase 2. |

### Constraints no negociables en BD (MySQL DDL)

- FKs entre `WorkOrder.fk_equipo → Equipment.id_unico`, `WorkOrder.fk_tecnico → User.id`, etc.
- Índices compuestos en `WorkOrder (fk_equipo, fecha_inicio DESC)` para consultas de historial (REQ-06).
- Índice en `AuditLog (timestamp, entidad_afectada)`.
- `username` de `User` → UNIQUE.
- `Equipment.id_unico` → UNIQUE + NOT NULL.

---

## 6. Roles y permisos (RBAC — REQ-07, REQ-08, REQ-10, REQ-11)

### Matriz de permisos

| Acción | TECNICO | SUPERVISOR |
|--------|:-------:|:----------:|
| Login | ✅ | ✅ |
| Ver listado de equipos | ✅ | ✅ |
| Ver detalle de equipo | ✅ | ✅ |
| Crear / editar / eliminar equipo | ❌ | ✅ |
| Programar mantenimiento preventivo | ❌ | ✅ |
| Registrar falla correctiva | ✅ | ✅ |
| Ver órdenes asignadas a uno mismo | ✅ | ✅ |
| Ver todas las órdenes | ❌ | ✅ |
| Cerrar orden propia | ✅ | ✅ |
| Modificar orden en estado `CERRADA` | ❌ (REQ-05) | ❌ (REQ-05, REQ-11) |
| Consultar historial de equipo | ✅ | ✅ |
| Gestionar usuarios | ❌ | ✅ |
| Ver Dashboard de Supervisión | ❌ | ✅ |
| Generar reporte mensual (MTTR) | ❌ | ✅ |

### Implementación

- **Doble verificación** (defensa en profundidad):
  1. Clase de permiso DRF en el controller (rápida, barata).
  2. Verificación dentro del service para operaciones de dominio (última línea de defensa).
- Los claims de rol van **dentro del JWT** para evitar consultas a BD en cada request.
- JWT: TTL 30 min (REQ-08), refresh token opcional.

---

## 7. Reglas de negocio críticas (no romper)

### REQ-01 — ID de equipo inmodificable
- `id_unico` se fija al crear. Cualquier PATCH/PUT que intente cambiarlo → **HTTP 400**.
- Validación en service, no solo en serializer.

### REQ-02 — Fecha de mantenimiento no pasada
- `fecha_inicio >= now()` en la zona horaria del servidor, validado en service.

### REQ-03 — Órdenes recurrentes automáticas
- Al cerrar una orden preventiva con frecuencia ≠ `UNICA`, el service genera la siguiente orden:
  - Estado `PROGRAMADO`
  - `fecha_inicio = fecha_cierre + intervalo` (mensual/trimestral/anual)
  - Técnico **no asignado** (supervisor debe asignar manualmente)
- También ejecutar un job diario (Celery Beat / django-q) que revise órdenes atrasadas.

### REQ-04 — Registro de correctivo
- Técnico registra falla → orden en `EN_PROCESO` asignada a sí mismo.
- Si al cerrar se usa un repuesto, decrementar stock dentro de la misma transacción (ver REQ-12).

### REQ-05 — Inmutabilidad al cerrar (CRÍTICO)
- Cualquier operación de escritura sobre una orden con `estado=CERRADA` debe responder **HTTP 422** y **registrarse en auditoría** como intento denegado.
- Verificación **en el service** antes de cualquier repository call.
- No confiar solo en restricciones de UI: el endpoint debe rechazar a nivel de API.

### REQ-12 — Atomicidad ACID
- Toda operación multi-tabla → `@transaction.atomic` en el service.
- Uso obligatorio de MySQL InnoDB.
- Ante cualquier excepción dentro del bloque → rollback completo.

### REQ-13 — Auditoría inmutable
- Las operaciones críticas (crear equipo, editar equipo, crear orden, cerrar orden, crear/desactivar usuario, intento de operación denegada) se registran vía `AuditService.log(...)`.
- La tabla `AuditLog`:
  - No tiene endpoints de UPDATE ni DELETE en la API.
  - El `AuditRepository` **no expone** métodos de modificación ni borrado.
  - Ideal: revocar permisos de UPDATE/DELETE en el usuario de BD de la app para esta tabla.
- Retención: ≥ 5 años. No borrar aunque se elimine la entidad origen.
- Escritura **asíncrona** (fire-and-forget) para no bloquear el flujo principal, salvo cuando la auditoría sea parte del contrato transaccional (ej: cierre de orden).

---

## 8. Requisitos de calidad medibles (aceptación)

Estas metas deben cumplirse antes de considerar una feature "done":

| Atributo | Meta | Cómo se verifica |
|----------|------|------------------|
| Seguridad — Endpoints protegidos | 100% excepto `/auth/login` | Test automatizado que recorre `urls.py` |
| Seguridad — bcrypt cost factor | ≥ 12 | Test que inspecciona el hash generado |
| Seguridad — JWT TTL | 30 minutos | Config + test de expiración |
| Fiabilidad — Integridad transaccional | 100% rollback ante fallo | Test de inyección de fallo |
| Fiabilidad — Inmutabilidad de órdenes cerradas | 100% bloqueadas | Test que intenta PATCH sobre orden `CERRADA` |
| Desempeño — P95 tiempo de respuesta | ≤ 2000 ms con 30 concurrentes | Locust/JMeter en staging |
| Desempeño — Dashboard latencia | ≤ 5 s tras cierre de orden | Test E2E |
| Mantenibilidad — Cobertura unitaria | ≥ 70% backend | `pytest --cov` en CI |
| Mantenibilidad — Documentación endpoints | ≥ 80% | `drf-spectacular` (OpenAPI) |

---

## 9. Setup de desarrollo

### Prerrequisitos
- Python 3.11+
- Node.js 20+
- MySQL 8.0+ (local o en Docker)
- Redis 7+ (solo si se usa Celery)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env            # editar DB_*, JWT_SECRET, etc.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000/api
npm run dev                     # arranca en http://localhost:5173
```

### Celery (opcional, solo si se usa scheduler via Celery)
```bash
cd backend
celery -A gmao worker -l info
celery -A gmao beat -l info
```

---

## 10. Scripts y comandos clave

### Backend
| Comando | Uso |
|---------|-----|
| `python manage.py runserver` | Dev server |
| `python manage.py makemigrations` | Generar migraciones |
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py test` | Tests con runner de Django (preferir pytest) |
| `pytest` | Ejecutar suite de tests |
| `pytest --cov=apps --cov-report=term-missing` | Cobertura |
| `ruff check .` | Lint |
| `black .` | Formateo |
| `python manage.py seed` | (custom) poblar BD con datos de ejemplo |

### Frontend
| Comando | Uso |
|---------|-----|
| `npm run dev` | Dev server con HMR |
| `npm run build` | Build de producción |
| `npm run preview` | Previsualizar build |
| `npm run test` | Vitest |
| `npm run test:coverage` | Cobertura |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |

---

## 11. Testing

### Backend (pytest)
- **Unit tests** por capa:
  - `test_services.py` — lógica de negocio pura, mock de repositories.
  - `test_repositories.py` — contra BD de test (sqlite in-memory o MySQL test DB).
  - `test_controllers.py` — `APIClient` de DRF, mock de services si es necesario.
- **Factory-boy** para fixtures de modelos.
- **Escenarios obligatorios** a cubrir (del doc de arquitectura):
  - EQ-01: técnico intenta POST a endpoint restringido → 403 + log.
  - EQ-02: token expirado → 401.
  - EQ-03: fallo en transacción multi-tabla → rollback completo, 0 residuos.
  - EQ-04: PATCH sobre orden `CERRADA` → 422.
  - EQ-05: test de carga (con Locust, fuera de CI).
  - EQ-07: test de regresión al agregar módulo.

### Frontend (Vitest + RTL)
- Tests de componentes críticos (formularios de cierre de orden, dashboard).
- Tests de hooks custom (autenticación, permisos).
- Tests de integración con MSW (Mock Service Worker) para mockear API.

---

## 12. CI/CD (GitHub Actions)

### `.github/workflows/backend-ci.yml` — esqueleto esperado
Pasos mínimos:
1. Setup Python 3.11
2. Instalar deps (`requirements-dev.txt`)
3. `ruff check .` — lint
4. `black --check .` — formato
5. `pytest --cov=apps --cov-fail-under=70` — tests + cobertura
6. (Opcional) subir cobertura a Codecov

### `.github/workflows/frontend-ci.yml` — esqueleto esperado
1. Setup Node 20
2. `npm ci`
3. `npm run lint`
4. `npm run typecheck`
5. `npm run test -- --coverage`
6. `npm run build` (smoke test de build)

**Regla:** ningún merge a `main` sin CI verde.

---

## 13. Convenciones de código

### Backend (Python)
- **Formateo:** Black (line length 100).
- **Linter:** Ruff (configurado en `pyproject.toml`).
- **Type hints obligatorios** en services y repositories.
- **Docstrings** estilo Google en funciones públicas.
- Nombres: `snake_case` para funciones/variables, `PascalCase` para clases.

### Frontend (TypeScript)
- **Formateo:** Prettier (config compartida en `frontend/.prettierrc`).
- **Linter:** ESLint con `typescript-eslint` recommended.
- **Sin `any`** salvo casos justificados (comentar el porqué).
- Componentes: `PascalCase.tsx`. Hooks: `useCamelCase.ts`.
- Tipos compartidos con el backend viven en `frontend/src/types/api.ts` (generarlos desde el OpenAPI de `drf-spectacular` cuando sea posible).

### Git
- **Branches:** `main` (protegida), `develop`, `feature/<req-id>-descripcion`, `fix/<descripcion>`.
- **Commits (Conventional Commits):**
  - `feat(work-orders): implementar cierre de orden (REQ-05)`
  - `fix(audit): corregir timestamp en zona horaria`
  - `test(equipment): agregar test de ID duplicado`
  - `refactor(services): extraer validacion de fecha`
- **PRs:** título = commit principal. Descripción = qué, por qué, REQ-IDs cubiertos, cómo se probó.

---

## 14. Trazabilidad requisitos ↔ código

| REQ | Módulo principal | Notas |
|-----|------------------|-------|
| REQ-01 | `apps/equipment` | ID inmodificable validado en service |
| REQ-02 | `apps/work_orders` | Validación temporal + RBAC supervisor |
| REQ-03 | `apps/work_orders` + Celery task | `generate_recurring_orders` |
| REQ-04 | `apps/work_orders` | Flujo de registro correctivo |
| REQ-05 | `apps/work_orders` | Guarda inmutabilidad |
| REQ-06 | `apps/work_orders` (endpoint de historial) | Índice `(fk_equipo, fecha_inicio DESC)` |
| REQ-07 | `apps/users` | Solo supervisor gestiona |
| REQ-08 | `apps/authentication` | JWT 30 min + bcrypt |
| REQ-09 | `apps/reports` | Cálculo MTTR + export PDF |
| REQ-10 | `apps/authentication/permissions.py` | Clase `HasRole("TECNICO")` y restricciones |
| REQ-11 | `apps/reports` (dashboard) + `apps/users` | Dashboard supervisor |
| REQ-12 | Transversal — `@transaction.atomic` en services | InnoDB |
| REQ-13 | `apps/audit` | Tabla solo-append |
| REQ-14 | Configuración + tests de carga | Índices, connection pool |
| REQ-15 | Estructura de carpetas + `drf-spectacular` | 80% endpoints documentados |

---

## 15. Asunciones y decisiones tomadas (validar con el usuario)

Estas decisiones se tomaron para resolver ambigüedades entre los dos documentos fuente. Si alguna es incorrecta, avisar y ajustar:

1. **Solo 2 roles (TECNICO, SUPERVISOR)**, no 3. El documento de arquitectura mencionaba `JEFE_PLANTA`, pero REQ-07 dice textualmente "estrictamente Técnico o Supervisor". Se elimina `JEFE_PLANTA` del MVP.
2. **OEE no se implementa en MVP.** El cálculo de OEE requiere datos de producción (disponibilidad + rendimiento + calidad) que no están capturados por ningún requisito funcional. Se mantiene **MTTR + frecuencia de fallas** (REQ-09, REQ-11), que sí son calculables con los datos del sistema.
3. **Repuestos en alcance mínimo.** Se implementa: CRUD de repuestos + decremento atómico de stock al cerrar orden correctiva. No se implementa: órdenes de compra, proveedores, alertas de stock mínimo (no están en requisitos).
4. **Frontend con TypeScript**, no JavaScript puro. Se alinea con los atributos de mantenibilidad/analizabilidad de REQ-15.
5. **Scheduler por defecto = Celery + Redis.** Si se quiere evitar Redis, usar `django-q2` (single-process, más simple, suficiente para 30 usuarios).
6. **Dashboard en tiempo real vía polling cada 3s** (más simple, cumple meta de ≤5 s). WebSockets se deja como mejora posterior si se escala.

---

## 16. Reglas de oro para Claude Code y Antigravity

Cuando la IA genere código en este repo, debe:

1. **Leer este archivo primero.** Si una instrucción del usuario lo contradice, preguntar antes de proceder.
2. **Respetar la separación de capas.** Si te piden "añade un endpoint", generar los 3 archivos: controller, service, repository. No atajos.
3. **Mapear cada cambio a uno o más REQ-IDs.** Si el cambio no mapea a ningún requisito, preguntar por qué se hace.
4. **Escribir el test junto con el código.** Una PR sin tests no es aceptable.
5. **Nunca** escribir lógica de negocio en:
   - `serializers.py` (solo validación de shape y tipos)
   - `models.py` (solo schema)
   - `views/controllers` (solo HTTP handling)
   - Componentes React (solo UI)
6. **Nunca** romper la inmutabilidad de órdenes cerradas ni de registros de auditoría, por ningún motivo.
7. **Nunca** devolver información sensible (hashes de password, JWTs de otros usuarios, stack traces en producción).
8. **Nunca** introducir dependencias pesadas (Redux, Lodash completo, Moment, etc.) sin justificarlo.
9. **Siempre** usar `transaction.atomic` para operaciones que tocan 2+ tablas.
10. **Siempre** registrar en `AuditService` las operaciones listadas en REQ-13.
11. **Siempre** preferir paginación en listados (DRF `PageNumberPagination`, page size 20 por defecto).
12. **Siempre** tipar los servicios y repositories (type hints en backend, tipos explícitos en frontend).

Si una sugerencia del IDE va contra estas reglas, la IA rechaza la sugerencia y explica por qué.

---

## 17. Contacto y propiedad

- **Autores:** Miguel Ángel Escobar Montoya, Simón Valderrama Mesa
- **Institución:** Institución Universitaria de Envigado — Ingeniería Informática
- **Asignatura:** Calidad de Software (docente: Martha Ligia Murillo Díaz)
- **Año:** 2026

---

*Última actualización: al inicializar el proyecto. Mantener este archivo sincronizado con cualquier cambio arquitectónico o de stack.*
