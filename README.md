# RoomieHKU

## Run In 2 Minutes

### 1. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply database migrations

```bash
python manage.py migrate
```

### 4. Start the app

```bash
python manage.py runserver
```

Open:
- Student app: `http://127.0.0.1:8000/` (or `/app/`)
- Admin dashboard route: `http://127.0.0.1:8000/dashboard/` (staff-only)
- Django admin: `http://127.0.0.1:8000/admin/`

### 5. (Optional) Create admin user for dashboard access

```bash
python manage.py createsuperuser
```

Then log in via `/admin/` and revisit `/dashboard/`.

## Notes

- Tailwind is loaded via CDN in templates (no Node/Tailwind build step needed).
- Database is SQLite (`db.sqlite3`) for local development/demo.
