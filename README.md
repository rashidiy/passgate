# skud

Access control system for managing employees, entry/exit devices, and work orders. Built for real deployments — tracks who goes in, who goes out, when, and through which device.

## Stack

- **Backend**: Django 5.1, Django REST Framework
- **Auth**: JWT (SimpleJWT)
- **DB**: PostgreSQL
- **Async**: Daphne, ASGI
- **Cache/Queue**: Redis
- **Infra**: Docker, nginx
- **Admin**: Jazzmin
- **Tests**: pytest
- **i18n**: Uzbek, Russian, English

## Features

- Employee directory with photo support and encrypted fields
- Device management — register and configure SKUD (access control) hardware
- Order/event logging — every entry and exit is recorded with timestamp and device
- Working hours calculation and Excel export (openpyxl)
- Webhook support for external integrations
- REST API with Swagger docs (drf-yasg)
- Nested routers for cleaner URL structure

## Project Structure

```
apps/
  devices/      — SKUD device models, serializers, views
  employees/    — employee profiles and management
  orders/       — entry/exit event records
  general/      — shared views
utils/
  orders_export.py
  working_hours_export.py
  redis_manager.py
  webhook.py
```

## Getting Started

```bash
cp .env.example .env
make build
make up
make migrate
make createsuperuser
```

Or without Docker:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Running Tests

```bash
pytest
```
