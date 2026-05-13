<<<<<<< HEAD
# IncidentHub — Multi-Tenant Incident Response Platform

A production-ready MVP SaaS platform for managing incidents across isolated tenants. Built with Flask (backend) and Quasar/Vue 3 (frontend).

---

## Project Overview

IncidentHub lets organizations (tenants) track, assign, and resolve incidents with full audit trails. Each tenant's data is completely isolated. Role-based access control governs what each user can see and do.

---

## Architecture

```
incident-platform-backend/
├── backend/                  # Flask REST API
│   ├── app/
│   │   ├── config/           # Environment-based config
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routes/           # Blueprint route handlers
│   │   ├── schemas/          # Marshmallow validation/serialization
│   │   ├── services/         # Business logic (activity logging, etc.)
│   │   ├── middleware/        # JWT tenant/role decorators
│   │   └── utils/            # Pagination, error helpers
│   ├── run.py
│   └── requirements.txt
│
└── frontend/                 # Quasar (Vue 3) SPA
    └── src/
        ├── boot/             # Axios setup + interceptors
        ├── components/       # Reusable UI components
        ├── css/              # Global SCSS
        ├── layouts/          # MainLayout (sidebar + navbar)
        ├── pages/            # Route-level page components
        ├── router/           # Vue Router + auth guards
        ├── services/         # API service layer
        └── stores/           # Pinia state stores
```

---

## Database Schema

### tenants
| Column     | Type         | Notes              |
|------------|--------------|--------------------|
| id         | INT PK       |                    |
| name       | VARCHAR(255) | Unique             |
| created_at | DATETIME     |                    |

### users
| Column        | Type                        | Notes                    |
|---------------|-----------------------------|--------------------------|
| id            | INT PK                      |                          |
| tenant_id     | INT FK → tenants.id         | Indexed                  |
| name          | VARCHAR(255)                |                          |
| email         | VARCHAR(255)                | Unique per tenant        |
| password_hash | VARCHAR(255)                | bcrypt                   |
| role          | ENUM(admin, manager, user)  |                          |
| created_at    | DATETIME                    |                          |

### incidents
| Column      | Type                                    | Notes                        |
|-------------|-----------------------------------------|------------------------------|
| id          | INT PK                                  |                              |
| tenant_id   | INT FK → tenants.id                     | Indexed                      |
| title       | VARCHAR(500)                            |                              |
| description | TEXT                                    |                              |
| status      | ENUM(open, in_progress, resolved, closed) |                            |
| priority    | ENUM(low, medium, high, critical)       |                              |
| assigned_to | INT FK → users.id                       | Nullable                     |
| created_by  | INT FK → users.id                       |                              |
| version     | INT                                     | Optimistic concurrency lock  |
| created_at  | DATETIME                                |                              |
| updated_at  | DATETIME                                | Auto-updated on change       |

### incident_comments
| Column      | Type              | Notes   |
|-------------|-------------------|---------|
| id          | INT PK            |         |
| tenant_id   | INT FK            | Indexed |
| incident_id | INT FK            | Indexed |
| user_id     | INT FK            |         |
| comment     | TEXT              |         |
| created_at  | DATETIME          |         |

### activity_logs
| Column      | Type         | Notes                          |
|-------------|--------------|--------------------------------|
| id          | INT PK       |                                |
| tenant_id   | INT FK       | Indexed                        |
| incident_id | INT FK       | Indexed                        |
| action      | VARCHAR(100) | e.g. "status_changed"          |
| old_value   | TEXT         | Nullable                       |
| new_value   | TEXT         | Nullable                       |
| created_by  | INT FK       |                                |
| created_at  | DATETIME     |                                |

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8+
- `@quasar/cli` installed globally: `npm i -g @quasar/cli`

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DB credentials and JWT secret

# Create MySQL database
mysql -u root -p -e "CREATE DATABASE incident_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run (auto-creates tables on first start)
python run.py
```

The API will be available at `http://localhost:5000`.  
Swagger docs: `http://localhost:5000/api/docs/`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api to localhost:5000)
quasar dev
```

The app will open at `http://localhost:9000`.

### First-time Setup

1. Open the app and click **Register**
2. Enter your organization name, your name, email, and password
3. This creates a new tenant and an **admin** account
4. Log in and use **User Management** to add team members

---

## API Documentation

Full interactive docs available at `/api/docs/` (Swagger UI).

### Auth
| Method | Endpoint             | Description                    |
|--------|----------------------|--------------------------------|
| POST   | /api/auth/register   | Create tenant + admin user     |
| POST   | /api/auth/login      | Authenticate, receive JWT      |

### Users (Admin only for POST)
| Method | Endpoint    | Description              |
|--------|-------------|--------------------------|
| GET    | /api/users  | List users in tenant     |
| POST   | /api/users  | Create user in tenant    |

### Incidents
| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| GET    | /api/incidents                  | List (filter/search/paginate)|
| POST   | /api/incidents                  | Create incident              |
| GET    | /api/incidents/:id              | Get detail                   |
| PUT    | /api/incidents/:id              | Update (version required)    |
| PATCH  | /api/incidents/:id/resolve      | Resolve incident             |
| PATCH  | /api/incidents/:id/assign       | Assign to user               |

### Comments & Activity
| Method | Endpoint                            | Description          |
|--------|-------------------------------------|----------------------|
| POST   | /api/incidents/:id/comments         | Add comment          |
| GET    | /api/incidents/:id/comments         | List comments        |
| GET    | /api/incidents/:id/activity         | Activity timeline    |

### Dashboard
| Method | Endpoint              | Description          |
|--------|-----------------------|----------------------|
| GET    | /api/dashboard/stats  | Stats + recent items |

---

## Tenant Isolation Strategy

Every database table includes a `tenant_id` column. The JWT token embeds `tenant_id` at login time — this value is extracted server-side from the verified token, never from the request body or query string.

Every query is scoped:
```python
Incident.query.filter_by(tenant_id=get_current_tenant_id())
```

The `tenant_required` middleware decorator verifies the JWT claim exists before any route handler runs. Cross-tenant access is structurally impossible — even if a user guesses another tenant's incident ID, the query returns 404.

---

## Concurrency Handling (Optimistic Locking)

Incidents have a `version` integer column. Every mutating request (PUT, PATCH) must include the current version. The server checks:

```python
if incident.version != data["version"]:
    return handle_conflict("Stale data: ...")
```

On success, `version` is incremented. This prevents two users from overwriting each other's changes silently. The frontend receives a 409 and can prompt the user to refresh.

---

## Role-Based Access Control

| Action                    | Admin | Manager | User |
|---------------------------|-------|---------|------|
| Register/Login            | ✓     | ✓       | ✓    |
| View assigned incidents   | ✓     | ✓       | ✓    |
| View all tenant incidents | ✓     | ✓       | ✗    |
| Create/update incidents   | ✓     | ✓       | ✗    |
| Assign/resolve incidents  | ✓     | ✓       | ✗    |
| Add comments              | ✓     | ✓       | ✓    |
| Manage users              | ✓     | ✗       | ✗    |

Roles are enforced via decorators (`@admin_required`, `@manager_or_admin_required`) applied at the route level.

---

## Scalability Considerations

- **Pagination**: All list endpoints are paginated (default 20/page, max 100)
- **DB Indexes**: Composite indexes on `(tenant_id, status)`, `(email, tenant_id)`, and all FK columns
- **Service layer**: Business logic is separated from route handlers for testability
- **Modular blueprints**: Each domain (auth, incidents, users, comments, dashboard) is a separate Flask Blueprint
- **Connection pooling**: SQLAlchemy engine configured with `pool_recycle` and `pool_pre_ping`
- **TODO**: Add Redis caching for dashboard stats, WebSocket support for real-time incident updates

---

## Tradeoffs

| Decision | Rationale |
|----------|-----------|
| Hash history vs HTML5 history | Hash mode avoids server-side routing config for MVP |
| Optimistic locking over pessimistic | Lower DB overhead; acceptable for incident management frequency |
| JWT-only auth (no refresh tokens) | Simpler for MVP; add refresh tokens before production |
| Single DB per platform | Simpler ops; row-level isolation is sufficient for MVP scale |
| Marshmallow over Pydantic | Consistent with Flask ecosystem; SQLAlchemy integration |

---

## AI Usage Disclosure

AI tools were used for boilerplate acceleration and documentation assistance.  
Core architecture, tenant isolation strategy, RBAC design, optimistic concurrency implementation, and backend flow decisions were manually reviewed and modified.
=======
# incident-response-platform
>>>>>>> 4bfdfda9b2e7cf78e50c0db1b8d3eb59947759be
