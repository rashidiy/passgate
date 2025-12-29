# passgate

Physical access control management system — tracks who enters which zone, enforces time-based access rules, integrates directly with Hikvision hardware, and logs every movement.

Built for enterprise deployments where security staff manage dozens of devices and hundreds of employees. The HR team operates through Django admin; access readers communicate through a DRF REST API.

## What it solves

In a facility with badge readers and face-recognition terminals, someone needs to:
- Maintain an employee roster and their assigned access zones
- Push access rules to physical hardware when employees join, transfer, or leave
- Log every entry/exit attempt (including failures)
- Track orders from a food-ordering terminal tied to the access control system
- Export payroll-relevant data (working hours, exceptions) to Excel

This system handles all of that.

---

## Architecture

```
HR / Security staff
        │
        ▼
  Django Admin (Jazzmin)
        │
        ├── employees, access points, devices, orders
        │
        ▼
  Django REST Framework
        │
        ├── /devices/  ← access hardware registers & polls events
        ├── /employees/ ← badge/face data pushed to devices
        └── /orders/    ← food-order terminal integration
        │
        ▼
  PostgreSQL + Redis
        │
        ├── Redis: async webhook broadcasting
        └── event_listener service: polls devices every 1.5s for new ACS events
```

Transport: Uvicorn (ASGI) behind Nginx. Swagger docs available at `/swagger/`.

---

## Key models

### Devices app
- **Device** — an access terminal (face reader, card reader, order kiosk). Stores encrypted credentials (`django-fernet-encrypted-fields`), hardware model, device type (`access_in` / `access_out` / `order`). Plugin-based: each hardware model has its own sync/event-polling logic.
- **Event** — every entry/exit attempt. Linked to employee + device, stores face image, card number, timestamp, success flag.
- **Webhook** — external endpoints to receive event notifications via Redis async broadcast.

### Employees app
- **Employee** — name, photo (200 KB max), gender, JSON snapshot for change detection.
- **Card** — up to 5 cards per employee. Tracks `old_card` to send ISAPI delete calls when a card changes.
- **AccessPoint** — join table between Employee and Device. Type: `normal` or `visitor`. Validity window (start/end dates), visit time constraint.
- **WorkingHourException** — labor leave, unpaid leave, working trip with start/end times. Used for payroll exports.

### Orders app
- **Order** — food order linked to an employee, tied to a single ORDER-type device. Portions mapped to Hikvision face codes (Complex 1 / Complex 2 / DP). Cancellable.

---

## Plugin system

Each hardware model ships as a plugin under `apps/devices/plugins/`. Current implementations:

- **DS-K1T671MF** — face recognition terminal. Creates/updates/deletes users via Hikvision ISAPI, manages card assignments, polls ACS events with pagination, downloads face images.
- **DS-K1T343MWX** — card reader variant.
- **OrderManager** — controls the order kiosk: enables/disables card reader, polls face/card events in real time with timeout loop.

The `event_listener` management command runs as a separate Docker service, polling all access devices every 1.5 s and saving new events.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1, DRF 3.15 |
| Async | Daphne, Uvicorn, ASGI |
| Auth | SessionAuth + DRF TokenAuth, SimpleJWT |
| DB | PostgreSQL 17 |
| Cache | Redis |
| Admin | Jazzmin |
| Docs | drf-yasg (Swagger) |
| Hardware | Hikvision ISAPI (digest auth, aiohttp) |
| Encryption | django-fernet-encrypted-fields |
| Export | openpyxl |
| i18n | Uzbek, Russian, English |
| Infra | Docker Compose, Nginx |
| Tests | pytest |

---

## Screenshots

> Screenshots are taken from a live deployment. Add your own by placing images in `docs/screenshots/`.

| Screen | File |
|---|---|
| Admin overview | `docs/screenshots/admin-overview.png` |
| Device list | `docs/screenshots/devices.png` |
| Employee + access points | `docs/screenshots/employees.png` |
| Event log | `docs/screenshots/events.png` |
| Order export UI | `docs/screenshots/order-export.png` |

---

## Getting started

```bash
cp .env.example .env
# fill in DB_USER, DB_PASSWORD, DB_NAME, REDIS_HOST, SECRET_KEY

docker compose up --build
# migrations run automatically via entrypoint.sh
```

Create a superuser after first boot:
```bash
docker compose exec web python manage.py createsuperuser
```

Admin is at `http://localhost:8000/admin/`. Swagger at `http://localhost:8000/swagger/`.

Sync access points to devices:
```bash
docker compose exec web python manage.py ap_sync
```

---

## Deployment

```
Nginx :8000 → Uvicorn (web) → PostgreSQL 17
                             → Redis
                    ↑
         event_listener (separate container, polls every 1.5s)
```

All services defined in `docker-compose.yml`. Makefile targets for migrations (`make mig`) and i18n (`make po` / `make mo`).
